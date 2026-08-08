
# -- RandomVibrationSpec Class Definition -- #

'''

PSD breakpoint tables, Grms, and the derivation of a qualification level from flight data.

This is the class the domain is built around, because random vibration is where the phrase "the
test level" hides the most unexamined assumptions. A specification arrives as a table of
breakpoints and a Grms number, and almost nobody asks where it came from. This class makes every
step of the derivation explicit and reversible.

The chain, in order:

    flight measurements      several flights, several channels, one zone
    statistical limit        mean + k sigma on the decibel values, at a stated percentile
    maximum predicted        the MPE, which is what the hardware will actually see
    acceptance level         = MPE. Screens workmanship, does not demonstrate margin
    qualification level      = MPE + 3 dB, for twice the duration

Two things about that chain are worth stating because they are routinely lost:

**The statistics are done in decibels.** Vibration environments are log-normally distributed far
more often than normally, so a mean and standard deviation taken on the linear PSD values gives a
different and wrong answer.

**The percentile and confidence are part of the specification.** P95/50 and P95/90 are different
numbers, and the second is substantially higher when the sample is small. Quoting a level without
its basis is quoting half a number.

Grms itself deserves suspicion. It is the square root of the area under the PSD, so it is a single
number summarising a whole spectrum, and two spectra with identical Grms damage hardware
differently depending on where their energy sits relative to its resonances. Grms is useful for
comparing like with like and for sizing a shaker; it is not a specification.

See Also:
---------
AcousticSpec   : The acoustic field that induces most of this vibration
ShockSpectrum  : The other high frequency environment, with different statistics
LoadFactorSet  : The low frequency quasi-static end of the same problem

Theory: docs/RandomVibration.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from environmentsUtils import (applyInputs, formatReportTable, overallRms, segmentSlope,
                                   scaleSpectrum, minerDurationScaling, toleranceLimit,
                                   decibelToRatio, ratioToDecibel,
                                   QUALIFICATION_MARGIN_RANDOM, QUALIFICATION_DURATION_FACTOR,
                                   ACCEPTANCE_DURATION_DEFAULT, MINER_FATIGUE_EXPONENT,
                                   NORMAL_TOLERANCE_FACTORS,
                                   InvalidInputError, SpectrumError, DerivationError,
                                   createErrorContext)
except ImportError:
    from .environmentsUtils import (applyInputs, formatReportTable, overallRms, segmentSlope,
                                    scaleSpectrum, minerDurationScaling, toleranceLimit,
                                    decibelToRatio, ratioToDecibel,
                                    QUALIFICATION_MARGIN_RANDOM, QUALIFICATION_DURATION_FACTOR,
                                    ACCEPTANCE_DURATION_DEFAULT, MINER_FATIGUE_EXPONENT,
                                    NORMAL_TOLERANCE_FACTORS,
                                    InvalidInputError, SpectrumError, DerivationError,
                                    createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Reference Spectra -- #
# ------------------------------------------------------------------------------------------------ #

# Published general-purpose specifications, as (frequency [Hz], density [g^2/Hz]) breakpoints.
# These are starting points and comparison anchors, never a substitute for a derived environment.
REFERENCE_SPECTRA = {
    'GEVS qualification': {
        'breakpoints': [(20.0, 0.026), (50.0, 0.16), (800.0, 0.16), (2000.0, 0.026)],
        'grms': 14.1,
        'note': 'NASA GSFC-STD-7000 general environmental verification, 14.1 Grms'},
    'GEVS acceptance': {
        'breakpoints': [(20.0, 0.013), (50.0, 0.08), (800.0, 0.08), (2000.0, 0.013)],
        'grms': 10.0,
        'note': 'GEVS qualification less 3 dB'},
    'MIL-STD-1540 minimum': {
        'breakpoints': [(20.0, 0.0053), (150.0, 0.04), (600.0, 0.04), (2000.0, 0.0036)],
        'grms': 6.8,
        'note': 'The minimum workmanship screen, not a predicted environment'},
}

# Vibration zones on a launch vehicle, as a rough guide to where the energy is. The multipliers are
# relative to a mid-bay reference and exist to make the point that zone definition dominates the
# answer, not to substitute for a real zone analysis.
ZONE_SEVERITY = {
    'engine compartment':  {'factor': 4.0,  'note': 'closest to the source, worst by far'},
    'aft skirt':           {'factor': 2.5,  'note': 'structure-borne from the thrust structure'},
    'tank barrel':         {'factor': 1.0,  'note': 'the reference. Large, damped by propellant'},
    'forward skirt':       {'factor': 1.2,  'note': ''},
    'payload bay':         {'factor': 0.6,  'note': 'acoustically driven, isolated from the engines'},
    'isolated payload':    {'factor': 0.2,  'note': 'behind an isolation system'},
}

# Below this sample count the P95/50 basis is not defensible and a higher confidence factor is
# required, because the standard deviation itself is poorly known.
MINIMUM_FLIGHTS_FOR_P95_50 = 3    # [-]

# A spectrum spanning less than this is not a random vibration environment in the usual sense.
MINIMUM_BANDWIDTH_DECADES = 1.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- RandomVibrationSpec -- #
# ------------------------------------------------------------------------------------------------ #

class RandomVibrationSpec:

    '''

    Random vibration specification construction and derivation.

    Usage:
    ------
        spec = RandomVibrationSpec()
        spec.setInputs({'breakpoints': [(20.0, 0.026), (50.0, 0.16),
                                        (800.0, 0.16), (2000.0, 0.026)]})
        result = spec.calculateOverallLevel()

    '''

    def __init__(self):

        # -- Spectrum -- #

        self.breakpoints        = None    # [(Hz, g^2/Hz)], the maximum predicted environment
        self.referenceSpectrum  = ''      # key into REFERENCE_SPECTRA, an alternative to breakpoints

        # -- Derivation Inputs -- #

        self.flightMeasurements = None    # [g^2/Hz], one value per flight, at a reference band
        self.statisticalBasis   = 'P95/50'   # key into NORMAL_TOLERANCE_FACTORS
        self.zone               = 'tank barrel'   # key into ZONE_SEVERITY

        # -- Margin Policy -- #

        self.qualificationMargin = QUALIFICATION_MARGIN_RANDOM   # [dB]
        self.acceptanceDuration  = ACCEPTANCE_DURATION_DEFAULT   # [s], per axis
        self.durationFactor      = QUALIFICATION_DURATION_FACTOR # [-]
        self.fatigueExponent     = MINER_FATIGUE_EXPONENT        # [-]

        # -- Flight Exposure -- #

        self.flightDuration      = np.nan   # [s], the actual exposure being qualified for

        # -- Results -- #

        self.findings            = []       # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Either breakpoints or referenceSpectrum must be supplied.

        '''

        requiredParams = {}

        optionalParams = {'breakpoints':         (list, tuple),
                          'referenceSpectrum':   str,
                          'flightMeasurements':  (list, tuple, np.ndarray),
                          'statisticalBasis':    str,
                          'zone':                str,
                          'qualificationMargin': (int, float),
                          'acceptanceDuration':  (int, float),
                          'durationFactor':      (int, float),
                          'fatigueExponent':     (int, float),
                          'flightDuration':      (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.referenceSpectrum:
            if self.referenceSpectrum not in REFERENCE_SPECTRA:
                raise InvalidInputError(
                    f'Unknown reference spectrum \'{self.referenceSpectrum}\'. '
                    f'Known: {sorted(REFERENCE_SPECTRA)}.',
                    context = createErrorContext(component = 'RandomVibrationSpec'))
            if self.breakpoints is None:
                self.breakpoints = list(REFERENCE_SPECTRA[self.referenceSpectrum]['breakpoints'])

        if self.breakpoints is not None:
            self.breakpoints = [(float(frequency), float(density))
                                for frequency, density in self.breakpoints]

    # -------------------------------------------------------------------------------------------- #

    def calculateOverallLevel(self) -> dict:

        '''

        Grms and the per-segment breakdown, which is where the energy actually is.

        The breakdown matters more than the total. A spectrum whose energy is concentrated in one
        band excites hardware whose resonances fall in that band and does nothing to hardware whose
        do not, and the Grms is identical either way.

        '''

        self._validateSpectrum()

        segments  = []
        total     = 0.0

        for index in range(len(self.breakpoints) - 1):

            lowerFrequency, lowerDensity = self.breakpoints[index]
            upperFrequency, upperDensity = self.breakpoints[index + 1]

            partial = overallRms([(lowerFrequency, lowerDensity),
                                  (upperFrequency, upperDensity)]) ** 2
            total  += partial

            segments.append({'lowerFrequency': lowerFrequency,
                             'upperFrequency': upperFrequency,
                             'slope':          segmentSlope(lowerFrequency, lowerDensity,
                                                            upperFrequency, upperDensity),
                             'meanSquare':     partial})

        grms = np.sqrt(total)

        for segment in segments:
            segment['energyFraction'] = segment['meanSquare'] / total

        dominant = max(segments, key = lambda entry: entry['energyFraction'])

        self.findings = []
        self.findings.append(
            f'{dominant["energyFraction"] * 100.0:.0f} % of the energy is between '
            f'{dominant["lowerFrequency"]:.0f} and {dominant["upperFrequency"]:.0f} Hz. Hardware '
            f'with no resonance in that band sees far less than the Grms suggests.')

        return {'grms':            grms,
                'meanSquare':      total,
                'segments':        segments,
                'dominantBand':    (dominant['lowerFrequency'], dominant['upperFrequency']),
                'lowestFrequency': self.breakpoints[0][0],
                'highestFrequency': self.breakpoints[-1][0],
                'findings':        self.findings}

    # -------------------------------------------------------------------------------------------- #

    def deriveMaximumPredicted(self) -> dict:

        '''

        A maximum predicted environment from flight measurements, at a stated statistical basis.

        The statistics are taken on the decibel values, because vibration environments are
        log-normally distributed. Taking them on the linear values gives a different and wrong
        answer, and it is the commonest error in a derivation.

        '''

        if self.flightMeasurements is None:
            raise DerivationError(
                'A maximum predicted environment needs flight measurements. Without them this is '
                'a specification chosen rather than derived, which is a legitimate thing to do and '
                'should be labelled as such.',
                context = createErrorContext(component = 'RandomVibrationSpec'))

        result = toleranceLimit(self.flightMeasurements, basis = self.statisticalBasis)

        self.findings = []

        if result['sampleCount'] < MINIMUM_FLIGHTS_FOR_P95_50 and self.statisticalBasis == 'P95/50':
            self.findings.append(
                f'Only {result["sampleCount"]} measurements. The standard deviation is itself '
                f'poorly known at this sample size, so a P95/50 basis is not defensible. Use '
                f'P95/90, which carries a higher factor precisely to cover that uncertainty.')

        self.findings.append(
            f'The {self.statisticalBasis} limit sits {result["marginOverMean"]:+.2f} dB above the '
            f'sample mean, on a standard deviation of {result["standardDeviation"]:.2f} dB.')

        if result['standardDeviation'] > 5.0:
            self.findings.append(
                f'A {result["standardDeviation"]:.1f} dB standard deviation is large. Either the '
                f'zone is not homogeneous and should be split, or the flights are not comparable.')

        return {**result, 'findings': self.findings}

    # -------------------------------------------------------------------------------------------- #

    def deriveTestLevels(self) -> dict:

        '''

        Acceptance and qualification spectra from the maximum predicted environment.

        Acceptance equals the MPE and screens workmanship on flight hardware. Qualification is
        3 dB above for twice the duration and demonstrates that the design has margin. They answer
        different questions and neither substitutes for the other.

        '''

        self._validateSpectrum()

        acceptance    = list(self.breakpoints)
        qualification = scaleSpectrum(self.breakpoints, self.qualificationMargin)

        acceptanceGrms    = overallRms(acceptance)
        qualificationGrms = overallRms(qualification)

        qualificationDuration = self.acceptanceDuration * self.durationFactor

        self.findings = []
        self.findings.append(
            f'Qualification is {self.qualificationMargin:+.1f} dB on the PSD, which is '
            f'{decibelToRatio(self.qualificationMargin, "power"):.2f}x in density and only '
            f'{qualificationGrms / acceptanceGrms:.3f}x in Grms. A decibel margin on a power '
            f'quantity is a square root in the amplitude everyone quotes.')

        self.findings.append(
            f'Acceptance equals the maximum predicted environment, so it demonstrates no margin at '
            f'all. It screens workmanship. Qualification demonstrates the design.')

        return {'acceptanceSpectrum':    acceptance,
                'acceptanceGrms':        acceptanceGrms,
                'acceptanceDuration':    self.acceptanceDuration,
                'qualificationSpectrum': qualification,
                'qualificationGrms':     qualificationGrms,
                'qualificationDuration': qualificationDuration,
                'marginDecibels':        self.qualificationMargin,
                'grmsRatio':             qualificationGrms / acceptanceGrms,
                'densityRatio':          decibelToRatio(self.qualificationMargin, 'power'),
                'findings':              self.findings}

    # -------------------------------------------------------------------------------------------- #

    def scaleForDuration(self, targetDuration: float) -> dict:

        '''

        Compress or extend a test in time under Miner's rule, and report what was assumed.

        This is the most heavily leaned-on assumption in environmental testing. It presumes high
        cycle fatigue with a single S-N exponent, linear damage accumulation, and a failure mode
        that does not change with level. A large compression can raise the level enough to excite
        something flight never would.

        '''

        self._validateSpectrum()

        if not np.isfinite(self.acceptanceDuration) or self.acceptanceDuration <= 0.0:
            raise InvalidInputError('A reference duration is needed to scale from.',
                                    context = createErrorContext(component = 'RandomVibrationSpec'))

        offset = minerDurationScaling(self.acceptanceDuration, targetDuration,
                                      exponent = self.fatigueExponent)

        scaled = scaleSpectrum(self.breakpoints, offset)

        compression = self.acceptanceDuration / targetDuration

        self.findings = []
        self.findings.append(
            f'Compressing {self.acceptanceDuration:.0f} s to {targetDuration:.0f} s is a '
            f'{compression:.1f}x reduction and costs {offset:+.2f} dB, on an assumed fatigue '
            f'exponent of {self.fatigueExponent:.1f}.')

        if compression > 10.0:
            self.findings.append(
                f'A {compression:.0f}x compression is large. Miner scaling assumes the failure '
                f'mode does not change with level, and at this compression the test may excite '
                f'something flight never would.')

        if self.fatigueExponent != MINER_FATIGUE_EXPONENT:
            self.findings.append(
                f'A non-standard fatigue exponent of {self.fatigueExponent:.1f} was used against '
                f'the conventional {MINER_FATIGUE_EXPONENT:.1f}. That choice needs justifying, '
                f'because the scaling is sensitive to it.')

        return {'targetDuration':    targetDuration,
                'referenceDuration': self.acceptanceDuration,
                'compressionRatio':  compression,
                'offsetDecibels':    offset,
                'scaledSpectrum':    scaled,
                'scaledGrms':        overallRms(scaled),
                'fatigueExponent':   self.fatigueExponent,
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def applyZone(self, zone: str = None) -> dict:

        '''

        Scale a reference spectrum to a vibration zone.

        Zone definition dominates the answer. The difference between an engine compartment and an
        isolated payload is a factor of twenty in PSD, which is far larger than any margin policy
        argument, and it is decided by drawing boxes on a vehicle.

        '''

        self._validateSpectrum()

        target = zone if zone is not None else self.zone

        if target not in ZONE_SEVERITY:
            raise InvalidInputError(
                f'Unknown zone \'{target}\'. Known: {sorted(ZONE_SEVERITY)}.',
                context = createErrorContext(component = 'RandomVibrationSpec'))

        factor = ZONE_SEVERITY[target]['factor']
        offset = ratioToDecibel(factor, quantity = 'power')

        scaled = scaleSpectrum(self.breakpoints, offset)

        return {'zone':          target,
                'factor':        factor,
                'offsetDecibels': offset,
                'spectrum':      scaled,
                'grms':          overallRms(scaled),
                'note':          ZONE_SEVERITY[target]['note']}

    # -------------------------------------------------------------------------------------------- #

    def compareToReference(self, reference: str = 'GEVS qualification') -> dict:

        '''

        Against a published general-purpose specification, which is the sanity check.

        A derived environment far above GEVS is either a genuinely severe zone or a derivation
        error. Far below it and the hardware may still need the workmanship screen that the
        minimum specifications exist to provide.

        '''

        self._validateSpectrum()

        if reference not in REFERENCE_SPECTRA:
            raise InvalidInputError(
                f'Unknown reference \'{reference}\'. Known: {sorted(REFERENCE_SPECTRA)}.',
                context = createErrorContext(component = 'RandomVibrationSpec'))

        entry     = REFERENCE_SPECTRA[reference]
        ownGrms   = overallRms(self.breakpoints)
        theirGrms = overallRms(entry['breakpoints'])

        ratio = ownGrms / theirGrms

        findings = []
        if ratio > 2.0:
            findings.append(
                f'This environment is {ratio:.1f}x {reference} in Grms. That is either a genuinely '
                f'severe zone or a derivation error, and it is worth confirming which.')
        elif ratio < 0.5:
            findings.append(
                f'This environment is {ratio:.2f}x {reference}. Hardware may still need a '
                f'workmanship screen, which is what the minimum specifications exist for.')

        return {'reference':      reference,
                'referenceGrms':  theirGrms,
                'ownGrms':        ownGrms,
                'ratio':          ratio,
                'decibelDifference': ratioToDecibel(ratio ** 2, quantity = 'power'),
                'note':           entry['note'],
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the specification and its derivation.
        '''

        overall = self.calculateOverallLevel()
        levels  = self.deriveTestLevels()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  RANDOM VIBRATION SPECIFICATION: {overall["grms"]:.2f} Grms')
        lines.append('=' * 96)
        lines.append('')

        rows = [[f'{segment["lowerFrequency"]:.0f} - {segment["upperFrequency"]:.0f}',
                 f'{segment["slope"]:+.2f}',
                 f'{segment["energyFraction"] * 100.0:.1f}']
                for segment in overall['segments']]
        lines.append(formatReportTable(rows, ['Band [Hz]', 'Slope [dB/oct]', 'Energy [%]'],
                                       title = 'Spectrum'))
        lines.append('')

        levelRows = [['Acceptance', f'{levels["acceptanceGrms"]:.2f}',
                      f'{levels["acceptanceDuration"]:.0f}'],
                     ['Qualification', f'{levels["qualificationGrms"]:.2f}',
                      f'{levels["qualificationDuration"]:.0f}']]
        lines.append(formatReportTable(levelRows, ['Level', 'Grms', 'Duration [s/axis]'],
                                       title = f'Test levels, '
                                               f'{levels["marginDecibels"]:+.1f} dB margin'))

        allFindings = overall['findings'] + levels['findings']
        if allFindings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in allFindings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'randomVibration.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateSpectrum(self) -> None:

        '''
        Check the breakpoint table is a usable spectrum.
        '''

        context = createErrorContext(component = 'RandomVibrationSpec')

        if self.breakpoints is None or len(self.breakpoints) < 2:
            raise SpectrumError(
                'A spectrum needs at least two breakpoints. Supply breakpoints or a '
                'referenceSpectrum.', context = context)

        frequencies = [frequency for frequency, _ in self.breakpoints]

        if any(later <= earlier for earlier, later in zip(frequencies, frequencies[1:])):
            raise SpectrumError(
                f'Breakpoint frequencies must increase strictly. Got {frequencies}.',
                context = context)

        if any(density <= 0.0 for _, density in self.breakpoints):
            raise SpectrumError('Spectral densities must be positive.', context = context)

        decades = np.log10(frequencies[-1] / frequencies[0])

        if decades < MINIMUM_BANDWIDTH_DECADES:
            raise SpectrumError(
                f'The spectrum spans {decades:.2f} decades, below {MINIMUM_BANDWIDTH_DECADES:.1f}. '
                f'That is a narrow band excitation, not a random vibration environment.',
                context = context)
