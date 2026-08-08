
# -- AcousticSpec Class Definition -- #

'''

Octave band sound pressure levels, overall SPL, and the vibroacoustic response they induce.

Acoustics is the source of most of the random vibration a launch vehicle sees, which is why the
two documents belong together. At liftoff the engine exhaust radiates an enormous acoustic field,
the vehicle skin is a large lightweight panel immersed in it, and the panel responds. That
response is the random vibration environment for everything mounted to it.

Two flight phases dominate and they are different in character:

    liftoff        engine exhaust, reflected off the pad and the flame trench. Broadband
    transonic      aerodynamic, shock oscillation and separated flow. Concentrated, brief

Liftoff is usually the louder of the two and transonic is often the one that governs a particular
component, because its energy sits higher in frequency where small hardware resonates.

Decibel addition is the operation everyone gets wrong. Sound pressure levels do not add
arithmetically. Two uncorrelated 140 dB sources give 143 dB, not 280, because power adds and the
decibel is logarithmic. The overall SPL of a band-limited spectrum is the logarithmic sum of its
bands, and doing it any other way produces a number that is wrong by tens of decibels.

Acoustic testing beats shaker testing for large lightweight structure and loses for small dense
hardware. A reverberant chamber excites a panel the way flight does, over its whole area at once;
a shaker excites it through its mounting feet, which is not the same load path and gives a
different response. For a dense box the reverse is true: the acoustic field cannot get enough
energy into it and a shaker can.

See Also:
---------
RandomVibrationSpec : The vibration this acoustic field induces
ShockSpectrum       : The other high frequency environment

Theory: docs/AcousticEnvironment.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from environmentsUtils import (applyInputs, formatReportTable, decibelToRatio, ratioToDecibel,
                                   QUALIFICATION_MARGIN_ACOUSTIC,
                                   InvalidInputError, SpectrumError, createErrorContext)
except ImportError:
    from .environmentsUtils import (applyInputs, formatReportTable, decibelToRatio, ratioToDecibel,
                                    QUALIFICATION_MARGIN_ACOUSTIC,
                                    InvalidInputError, SpectrumError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The reference pressure for the decibel scale in air. Everything acoustic is relative to it.
REFERENCE_PRESSURE = 20.0e-6    # [Pa], 20 micropascals

# Standard one-third octave band centre frequencies over the range that matters for launch.
THIRD_OCTAVE_CENTRES = [31.5, 40.0, 50.0, 63.0, 80.0, 100.0, 125.0, 160.0, 200.0, 250.0,
                        315.0, 400.0, 500.0, 630.0, 800.0, 1000.0, 1250.0, 1600.0, 2000.0,
                        2500.0, 3150.0, 4000.0, 5000.0, 6300.0, 8000.0, 10000.0]

# Full octave band centres, which is how acoustic specifications are usually written.
OCTAVE_CENTRES = [31.5, 63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]

# Representative launch acoustic environments as octave band SPL in dB, at the payload fairing.
# These are anchors for comparison, not specifications.
REFERENCE_ENVIRONMENTS = {
    'small launcher fairing': {
        'levels': [124.0, 128.0, 131.0, 133.0, 132.0, 129.0, 125.0, 120.0, 114.0],
        'note': 'a representative small launch vehicle payload environment'},
    'medium launcher fairing': {
        'levels': [128.0, 132.0, 135.0, 137.0, 136.0, 133.0, 129.0, 124.0, 118.0],
        'note': 'representative of an EELV-class fairing'},
    'engine compartment': {
        'levels': [138.0, 143.0, 147.0, 149.0, 148.0, 145.0, 141.0, 136.0, 130.0],
        'note': 'close to the exhaust, the worst acoustic zone on the vehicle'},
}

# Above this overall SPL the acoustic environment is generally the dominant source of random
# vibration, and below it structure-borne paths usually are.
ACOUSTIC_DOMINANCE_THRESHOLD = 135.0    # [dB OASPL]

# Surface mass density below which acoustic testing is clearly the right method, and above which a
# shaker generally is. The crossover is not sharp and this is a guide.
ACOUSTIC_TEST_MASS_THRESHOLD = 10.0    # [kg/m^2]

# ------------------------------------------------------------------------------------------------ #
# -- AcousticSpec -- #
# ------------------------------------------------------------------------------------------------ #

class AcousticSpec:

    '''

    Acoustic environment definition and vibroacoustic response estimation.

    Usage:
    ------
        acoustic = AcousticSpec()
        acoustic.setInputs({'referenceEnvironment': 'medium launcher fairing'})
        result = acoustic.calculateOverallLevel()

    '''

    def __init__(self):

        # -- Spectrum -- #

        self.bandCentres        = list(OCTAVE_CENTRES)   # [Hz]
        self.bandLevels         = None    # [dB], one per band centre
        self.referenceEnvironment = ''    # key into REFERENCE_ENVIRONMENTS

        # -- Responding Structure -- #

        self.surfaceMass        = np.nan  # [kg/m^2], areal mass of the responding panel
        self.panelArea          = np.nan  # [m^2]
        self.criticalFrequency  = np.nan  # [Hz], coincidence frequency of the panel
        self.dampingRatio       = 0.02    # [-], typical for a stiffened panel

        # -- Margin Policy -- #

        self.qualificationMargin = QUALIFICATION_MARGIN_ACOUSTIC   # [dB]

        # -- Results -- #

        self.findings           = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Either bandLevels or referenceEnvironment must be supplied.

        '''

        requiredParams = {}

        optionalParams = {'bandCentres':          (list, tuple, np.ndarray),
                          'bandLevels':           (list, tuple, np.ndarray),
                          'referenceEnvironment': str,
                          'surfaceMass':          (int, float),
                          'panelArea':            (int, float),
                          'criticalFrequency':    (int, float),
                          'dampingRatio':         (int, float),
                          'qualificationMargin':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.referenceEnvironment:
            if self.referenceEnvironment not in REFERENCE_ENVIRONMENTS:
                raise InvalidInputError(
                    f'Unknown environment \'{self.referenceEnvironment}\'. '
                    f'Known: {sorted(REFERENCE_ENVIRONMENTS)}.',
                    context = createErrorContext(component = 'AcousticSpec'))
            if self.bandLevels is None:
                self.bandLevels  = list(REFERENCE_ENVIRONMENTS[self.referenceEnvironment]['levels'])
                self.bandCentres = list(OCTAVE_CENTRES)

        if self.bandLevels is not None:
            self.bandLevels = [float(level) for level in self.bandLevels]
        self.bandCentres = [float(centre) for centre in self.bandCentres]

    # -------------------------------------------------------------------------------------------- #

    def calculateOverallLevel(self) -> dict:

        '''

        Overall sound pressure level, by logarithmic summation of the bands.

            OASPL = 10 log10( sum of 10^(L_i / 10) )

        Decibels do not add arithmetically. Two uncorrelated 140 dB sources give 143 dB, and
        summing them any other way is wrong by an enormous margin. This is the single most common
        error in acoustic work.

        '''

        self._validateSpectrum()

        powers = [10.0 ** (level / 10.0) for level in self.bandLevels]
        total  = sum(powers)

        overall = 10.0 * np.log10(total)

        contributions = [{'centre':   centre,
                          'level':    level,
                          'fraction': power / total}
                         for centre, level, power in zip(self.bandCentres, self.bandLevels, powers)]

        dominant = max(contributions, key = lambda entry: entry['fraction'])

        # the equivalent rms pressure
        pressure = REFERENCE_PRESSURE * 10.0 ** (overall / 20.0)

        self.findings = []
        self.findings.append(
            f'The overall level is {overall:.1f} dB, which is {overall - max(self.bandLevels):.1f} '
            f'dB above the loudest single band at {max(self.bandLevels):.1f} dB. Decibels add '
            f'logarithmically, not arithmetically.')

        self.findings.append(
            f'The {dominant["centre"]:.0f} Hz band carries {dominant["fraction"] * 100.0:.0f} % of '
            f'the acoustic power.')

        if overall > ACOUSTIC_DOMINANCE_THRESHOLD:
            self.findings.append(
                f'At {overall:.0f} dB OASPL the acoustic field is likely the dominant source of '
                f'random vibration in this zone, rather than structure-borne paths.')

        return {'overallLevel':     overall,
                'rmsPressure':      pressure,
                'contributions':    contributions,
                'dominantBand':     dominant['centre'],
                'loudestBandLevel': max(self.bandLevels),
                'findings':         self.findings}

    # -------------------------------------------------------------------------------------------- #

    def estimateVibrationResponse(self) -> dict:

        '''

        A first-order estimate of the random vibration a panel develops in this acoustic field.

        Uses the Barrett relation, which correlates panel acceleration PSD against acoustic
        pressure and surface mass. It is a correlation rather than a derivation and it is accurate
        to a factor of two or three, which is enough to decide whether acoustics or a structural
        path dominates a zone.

            W_acceleration ~ (p^2 / m^2) x response terms

        The important content is the scaling: response goes as the inverse square of surface mass,
        so a light panel in a loud field is the severe case and a dense box is not.

        '''

        self._validateSpectrum()

        if not np.isfinite(self.surfaceMass) or self.surfaceMass <= 0.0:
            raise InvalidInputError(
                'A vibroacoustic estimate needs the responding panel surface mass.',
                context = createErrorContext(component = 'AcousticSpec'))

        overall  = self.calculateOverallLevel()
        pressure = overall['rmsPressure']

        # Barrett-style estimate: acceleration PSD proportional to p^2 / (m^2 f) with a damping term
        responses = []
        for centre, level in zip(self.bandCentres, self.bandLevels):

            bandPressure = REFERENCE_PRESSURE * 10.0 ** (level / 20.0)
            bandwidth    = centre * (2.0 ** 0.5 - 2.0 ** -0.5)    # full octave

            # acceleration spectral density in g^2/Hz
            density = ((bandPressure ** 2) / (self.surfaceMass ** 2)
                       / (self.dampingRatio * centre * bandwidth) / (9.80665 ** 2))

            responses.append({'centre': centre, 'density': density})

        totalMeanSquare = sum(entry['density'] * entry['centre']
                              * (2.0 ** 0.5 - 2.0 ** -0.5) for entry in responses)
        grms = np.sqrt(totalMeanSquare)

        findings = []
        findings.append(
            f'Estimated response is {grms:.1f} Grms for a {self.surfaceMass:.1f} kg/m^2 panel. '
            f'This is a correlation accurate to perhaps a factor of two, useful for deciding '
            f'which source dominates and not for setting a test level.')

        findings.append(
            'Response goes as the inverse square of surface mass, so a light panel in a loud field '
            'is the severe case. Adding mass to reduce vibroacoustic response works, and it is '
            'usually the wrong trade.')

        return {'responseSpectrum': responses,
                'estimatedGrms':    grms,
                'surfaceMass':      self.surfaceMass,
                'overallLevel':     overall['overallLevel'],
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def recommendTestMethod(self) -> dict:

        '''

        Acoustic chamber against shaker, decided by what the hardware actually is.

        A reverberant field loads a large light panel over its whole area, which is how flight
        loads it. A shaker loads it through its mounting feet, which is a different load path and
        gives a different response. For a small dense box the acoustic field cannot get enough
        energy in and the shaker is right.

        '''

        self._validateSpectrum()

        overall = self.calculateOverallLevel()['overallLevel']

        if not np.isfinite(self.surfaceMass):
            raise InvalidInputError('A test method recommendation needs the surface mass.',
                                    context = createErrorContext(component = 'AcousticSpec'))

        acousticPreferred = self.surfaceMass < ACOUSTIC_TEST_MASS_THRESHOLD

        findings = []

        if acousticPreferred:
            findings.append(
                f'At {self.surfaceMass:.1f} kg/m^2 this is a large light structure, so a '
                f'reverberant acoustic test loads it the way flight does. A shaker would excite it '
                f'through its feet, which is the wrong load path.')
        else:
            findings.append(
                f'At {self.surfaceMass:.1f} kg/m^2 this is dense enough that an acoustic field '
                f'cannot put much energy into it. A shaker random vibration test is the right '
                f'method, driven by the vibration this acoustic field induces in its mounting '
                f'structure.')

        if overall > ACOUSTIC_DOMINANCE_THRESHOLD and not acousticPreferred:
            findings.append(
                'The field is loud enough that both tests may be required: acoustic for the '
                'mounting structure, random vibration for the unit.')

        return {'recommendation':   'acoustic chamber' if acousticPreferred else 'shaker',
                'surfaceMass':      self.surfaceMass,
                'threshold':        ACOUSTIC_TEST_MASS_THRESHOLD,
                'overallLevel':     overall,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def deriveTestLevels(self) -> dict:

        '''

        Acceptance and qualification band levels.

        '''

        self._validateSpectrum()

        overall = self.calculateOverallLevel()

        qualification = [level + self.qualificationMargin for level in self.bandLevels]

        return {'acceptanceLevels':    list(self.bandLevels),
                'acceptanceOverall':   overall['overallLevel'],
                'qualificationLevels': qualification,
                'qualificationOverall': overall['overallLevel'] + self.qualificationMargin,
                'marginDecibels':      self.qualificationMargin,
                'bandCentres':         list(self.bandCentres)}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the acoustic environment.
        '''

        overall = self.calculateOverallLevel()
        levels  = self.deriveTestLevels()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ACOUSTIC ENVIRONMENT: {overall["overallLevel"]:.1f} dB OASPL')
        lines.append('=' * 96)
        lines.append('')

        rows = [[f'{entry["centre"]:.0f}', f'{entry["level"]:.1f}',
                 f'{entry["fraction"] * 100.0:.1f}',
                 f'{qualification:.1f}']
                for entry, qualification in zip(overall['contributions'],
                                                levels['qualificationLevels'])]
        lines.append(formatReportTable(
            rows, ['Band [Hz]', 'SPL [dB]', 'Power [%]', 'Qual [dB]'],
            title = f'Octave bands, {levels["marginDecibels"]:+.0f} dB qualification margin'))

        if self.findings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in self.findings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'acousticEnvironment.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateSpectrum(self) -> None:

        '''
        Check the band table is usable.
        '''

        context = createErrorContext(component = 'AcousticSpec')

        if self.bandLevels is None:
            raise SpectrumError(
                'No band levels. Supply bandLevels or a referenceEnvironment.', context = context)

        if len(self.bandLevels) != len(self.bandCentres):
            raise SpectrumError(
                f'{len(self.bandLevels)} levels against {len(self.bandCentres)} band centres.',
                context = context)

        if any(level <= 0.0 for level in self.bandLevels):
            raise SpectrumError(
                'Sound pressure levels are in decibels above 20 micropascals and are positive for '
                'any real environment. A non-positive level is almost certainly a unit error.',
                context = context)

        if any(later <= earlier for earlier, later in zip(self.bandCentres,
                                                          self.bandCentres[1:])):
            raise SpectrumError('Band centre frequencies must increase.', context = context)
