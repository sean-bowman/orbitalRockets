
# -- EnvironmentalTest Class Definition -- #

'''

Environmental test level derivation: random vibration, shock and thermal.

The job of this class is to turn a flight environment into a test specification, and to make every
decibel of the margin between them traceable rather than assumed.

Three derivations, each with a different underlying model:

**Random vibration.** Acceptance is the flight level; qualification is acceptance plus 3 dB for twice
the duration. Those two numbers are not arbitrary and they are not independent. Under Miner's rule
with the standard fatigue exponent of 4, a factor of 2 in PSD raises stress amplitude by sqrt(2), and
sqrt(2)^4 = 4, so 3 dB buys a factor of four in equivalent fatigue time. The 2x duration on top of it
is additional margin, not the same margin counted twice.

**Shock.** Qualification is 1.4x the flight SRS, applied three times per axis. There is no duration
concept: shock is a single transient and the damage model is peak response, not accumulated cycles.

**Thermal.** Qualification extends 10 K beyond each end of the flight range and doubles the cycle
count. The margin is in temperature and in cycles because the two damage mechanisms are different:
temperature extremes find material limits, cycles find fatigue.

The class also does the reverse calculation, which is the useful one in practice: given a test
duration you can actually afford, what level is equivalent to the required one? That is how a
six-hour test becomes a twenty-minute test, and it is a legitimate trade as long as the exponent is
defensible.

See Also:
---------
LifeTest      : Cycle-based life rather than environment-based fatigue
TestCampaign  : Where environmental testing sits in the sequence
environmentsAndLoads : Where the flight environments this class consumes come from

Theory: docs/EnvironmentalTesting.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (applyInputs, formatReportTable, QUALIFICATION_MARGINS,
                               ACCEPTANCE_RANDOM_DURATION, MINER_FATIGUE_EXPONENT,
                               InvalidInputError, TestInfeasibleError, createErrorContext)
except ImportError:
    from .campaignUtils import (applyInputs, formatReportTable, QUALIFICATION_MARGINS,
                                ACCEPTANCE_RANDOM_DURATION, MINER_FATIGUE_EXPONENT,
                                InvalidInputError, TestInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Representative flight random vibration environments as PSD breakpoint tables, each a list of
# (frequency [Hz], PSD [g^2/Hz]) pairs. Provided so a first-cut campaign can be built before the
# vehicle-specific environment exists, and clearly labelled as generic.
#
# A real program replaces these with measured or predicted zone-specific environments. Using a
# generic envelope is conservative in most bands and unconservative in a few, which is exactly the
# problem with enveloping.
GENERIC_VIBRATION_ENVIRONMENTS = {
    'launch vehicle component': [(20.0, 0.01), (80.0, 0.08), (500.0, 0.08), (2000.0, 0.005)],
    'launch vehicle severe':    [(20.0, 0.02), (80.0, 0.20), (500.0, 0.20), (2000.0, 0.013)],
    'spacecraft component':     [(20.0, 0.005), (80.0, 0.04), (500.0, 0.04), (2000.0, 0.0025)],
    'benign':                   [(20.0, 0.001), (100.0, 0.01), (1000.0, 0.01), (2000.0, 0.003)]
}

# Representative shock response spectra as (frequency [Hz], acceleration [g]) breakpoints.
GENERIC_SHOCK_ENVIRONMENTS = {
    'pyrotechnic near field': [(100.0, 100.0), (2000.0, 4000.0), (10000.0, 4000.0)],
    'pyrotechnic far field':  [(100.0, 30.0), (2000.0, 800.0), (10000.0, 800.0)],
    'separation':             [(100.0, 50.0), (1500.0, 1500.0), (10000.0, 1500.0)],
    'benign':                 [(100.0, 10.0), (2000.0, 200.0), (10000.0, 200.0)]
}

# Shock is applied as discrete events rather than for a duration.
SHOCK_APPLICATIONS_PER_AXIS = 3

class EnvironmentalTest:

    '''

    Environmental test level derivation for random vibration, shock and thermal.

    Primary Input Properties:
    -------------------------
    flightPowerSpectralDensity : list
        Flight random vibration as [(frequency [Hz], PSD [g^2/Hz])] breakpoints
    flightEnvironmentKey : str
        Alternatively, a key into GENERIC_VIBRATION_ENVIRONMENTS
    flightDuration : float
        Flight exposure duration per axis [s]. Defaults to ACCEPTANCE_RANDOM_DURATION.
    flightShockSpectrum : list
        Flight shock as [(frequency [Hz], acceleration [g])] breakpoints
    shockEnvironmentKey : str
        Alternatively, a key into GENERIC_SHOCK_ENVIRONMENTS
    flightTemperatureRange : tuple
        (minimum, maximum) flight temperature [K]
    flightThermalCycles : int
        Expected thermal cycles in service
    fatigueExponent : float
        Miner's rule exponent. Defaults to MINER_FATIGUE_EXPONENT.

    Key Output Properties:
    ----------------------
    acceptanceGrms / qualificationGrms : float
        Overall RMS acceleration at each level [g]
    qualificationPowerSpectralDensity : list
        Qualification PSD breakpoints [(Hz, g^2/Hz)]
    qualificationDuration : float
        Qualification duration per axis [s]
    qualificationShockSpectrum : list
        Qualification SRS breakpoints
    qualificationTemperatureRange : tuple
        Qualification temperature limits [K]
    qualificationThermalCycles : int
        Qualification cycle count

    Public Methods:
    ---------------
    setInputs(inputs)                      Load a configuration dictionary
    calculateRandomVibration()             Acceptance and qualification PSD, Grms, durations
    calculateShock()                       Qualification SRS and application count
    calculateThermal()                     Qualification temperature range and cycle count
    scaleDurationToLevel(duration)         Miner equivalence: what level matches a chosen duration
    scaleLevelToDuration(decibels)         Miner equivalence: what duration matches a chosen level
    generateReport(outputDir)              Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Random Vibration -- #

        self.flightPowerSpectralDensity = None    # [(Hz, g^2/Hz)] breakpoints
        self.flightEnvironmentKey       = ''      # key into GENERIC_VIBRATION_ENVIRONMENTS
        self.flightDuration             = np.nan  # [s] per axis

        # -- Shock -- #

        self.flightShockSpectrum        = None    # [(Hz, g)] breakpoints
        self.shockEnvironmentKey        = ''      # key into GENERIC_SHOCK_ENVIRONMENTS

        # -- Thermal -- #

        self.flightTemperatureRange     = None    # (minimum, maximum) [K]
        self.flightThermalCycles        = np.nan  # [-]

        # -- Model -- #

        # The Miner exponent is the assumption the whole duration-level equivalence rests on. Four is
        # the standard value; a material with a different S-N slope needs a different number, and if
        # the exponent is wrong every scaled test level is wrong with it.
        self.fatigueExponent            = np.nan  # [-], defaults to MINER_FATIGUE_EXPONENT

        # -- Results -- #

        self.acceptancePowerSpectralDensity    = None
        self.qualificationPowerSpectralDensity = None
        self.acceptanceGrms                    = np.nan  # [g]
        self.qualificationGrms                 = np.nan  # [g]
        self.acceptanceDuration                = np.nan  # [s] per axis
        self.qualificationDuration             = np.nan  # [s] per axis
        self.qualificationShockSpectrum        = None
        self.qualificationTemperatureRange     = None
        self.qualificationThermalCycles        = np.nan  # [-]
        self.designNotes                       = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object. Everything is optional; each calculate
        method checks for what it needs.

        '''

        optionalParams = ['flightPowerSpectralDensity', 'flightEnvironmentKey', 'flightDuration',
                          'flightShockSpectrum', 'shockEnvironmentKey', 'flightTemperatureRange',
                          'flightThermalCycles', 'fatigueExponent']

        applyInputs(self, inputs, {}, optionalParams)

    def calculateRandomVibration(self) -> dict:

        '''

        Acceptance and qualification random vibration levels.

        Acceptance is the flight environment. Qualification is acceptance plus 3 dB, for twice the
        duration, per axis.

        **Grms from a PSD breakpoint table** is the integral of the PSD over frequency, taken
        segment by segment. On a log-log plot the segments are straight lines, so each segment is a
        power law and integrates in closed form:

            for slope m != -1:   area = (f2 * S2 - f1 * S1) / (m + 1)
            for slope m == -1:   area = S1 * f1 * ln(f2 / f1)

        with m = ln(S2/S1) / ln(f2/f1). Grms is the square root of the total area.

        Doing this segment-wise on a log-log basis matters. Treating the breakpoints as linear on a
        linear scale, which is the obvious mistake, overestimates the area under a rolloff and
        underestimates it under a rise.

        A 3 dB increase is a factor of two in PSD, which is a factor of sqrt(2) in Grms.

        '''

        spectralDensity = self._resolveVibrationEnvironment()
        duration        = self.flightDuration if not np.isnan(self.flightDuration) else ACCEPTANCE_RANDOM_DURATION

        self.acceptancePowerSpectralDensity = list(spectralDensity)
        self.acceptanceDuration             = duration
        self.acceptanceGrms                 = self._grmsFromSpectralDensity(spectralDensity)

        # Qualification: +3 dB is a factor of two in PSD
        decibels    = QUALIFICATION_MARGINS['randomVibrationDecibels']
        levelFactor = 10.0**(decibels / 10.0)

        self.qualificationPowerSpectralDensity = [(frequency, density * levelFactor)
                                                  for frequency, density in spectralDensity]
        self.qualificationDuration = duration * QUALIFICATION_MARGINS['randomVibrationDuration']
        self.qualificationGrms     = self._grmsFromSpectralDensity(self.qualificationPowerSpectralDensity)

        # The equivalent fatigue margin the level increase alone represents
        exponent           = self._fatigueExponent()
        levelTimeEquivalent = levelFactor**(exponent / 2.0)

        self.designNotes.append(
            f'The {decibels:.0f} dB qualification increase is a factor of {levelFactor:.1f} in PSD, which under '
            f'Miner with an exponent of {exponent:.0f} is equivalent to {levelTimeEquivalent:.0f}x the exposure '
            f'time. The {QUALIFICATION_MARGINS["randomVibrationDuration"]:.0f}x duration is margin on top of that, '
            f'not the same margin counted twice.')

        return {
            'acceptancePowerSpectralDensity':    self.acceptancePowerSpectralDensity,
            'acceptanceGrms':                    self.acceptanceGrms,
            'acceptanceDuration':                self.acceptanceDuration,
            'qualificationPowerSpectralDensity': self.qualificationPowerSpectralDensity,
            'qualificationGrms':                 self.qualificationGrms,
            'qualificationDuration':             self.qualificationDuration,
            'levelFactor':                       levelFactor,
            'equivalentTimeFactorFromLevel':     levelTimeEquivalent
        }

    def calculateShock(self) -> dict:

        '''

        Qualification shock response spectrum.

        Qualification is 1.4x the flight SRS, applied three times per axis. There is no duration
        concept and no Miner scaling: shock is a single transient and the damage model is peak
        response rather than accumulated cycles.

        The three applications per axis exist to cover the variability of the shock machine rather
        than to accumulate damage, which is why the count does not scale with anything.

        '''

        spectrum = self._resolveShockEnvironment()
        factor   = QUALIFICATION_MARGINS['shockFactor']

        self.qualificationShockSpectrum = [(frequency, acceleration * factor)
                                           for frequency, acceleration in spectrum]

        peakFlight        = max(acceleration for _, acceleration in spectrum)
        peakQualification = peakFlight * factor

        return {
            'flightShockSpectrum':        list(spectrum),
            'qualificationShockSpectrum': self.qualificationShockSpectrum,
            'shockFactor':                factor,
            'peakFlight':                 peakFlight,
            'peakQualification':          peakQualification,
            'applicationsPerAxis':        SHOCK_APPLICATIONS_PER_AXIS
        }

    def calculateThermal(self) -> dict:

        '''

        Qualification thermal range and cycle count.

        Qualification extends the margin beyond each end of the flight range and multiplies the cycle
        count. The margin is applied in both temperature and cycles because the two damage mechanisms
        are different: temperature extremes find material limits and stack up tolerances, cycles find
        fatigue.

        The 10 K margin is the conventional value from MIL-STD-1540 and NASA-STD-7002. Programs with
        a well-characterized thermal model sometimes reduce it; programs with a poorly characterized
        one should not.

        '''

        if self.flightTemperatureRange is None:
            raise InvalidInputError(
                message       = 'calculateThermal needs the flight temperature range as (minimum, maximum) in K.',
                parameterName = 'flightTemperatureRange', value = None,
                validRange    = 'A (minimum, maximum) tuple'
            )

        minimumFlight, maximumFlight = self.flightTemperatureRange
        margin = QUALIFICATION_MARGINS['thermalMargin']

        self.qualificationTemperatureRange = (minimumFlight - margin, maximumFlight + margin)

        cycles = self.flightThermalCycles if not np.isnan(self.flightThermalCycles) else 4.0
        self.qualificationThermalCycles = int(np.ceil(cycles * QUALIFICATION_MARGINS['thermalCycleFactor']))

        return {
            'flightTemperatureRange':        self.flightTemperatureRange,
            'qualificationTemperatureRange': self.qualificationTemperatureRange,
            'thermalMargin':                 margin,
            'flightThermalCycles':           cycles,
            'qualificationThermalCycles':    self.qualificationThermalCycles
        }

    def scaleDurationToLevel(self, availableDuration: float) -> dict:

        '''

        Miner equivalence: the level increase needed to compress the qualification test into a
        duration you can actually afford.

        Under Miner's rule with fatigue exponent m, equal damage requires

            S1^m * t1 = S2^m * t2

        and since stress amplitude scales as the square root of PSD,

            (PSD2 / PSD1) = (t1 / t2)^(2/m)

        With m = 4 this is a square root relationship: halving the duration needs a factor of
        sqrt(2) = 1.41 in PSD, which is 1.5 dB.

        **This trade is legitimate and it has a limit.** Raising the level to compress the schedule
        eventually pushes the article into a failure mode it would never see in flight: a resonance
        that only responds at high amplitude, a nonlinearity, a joint that slips. The conventional
        limit is that a scaled test should not exceed the required level by more than about 6 dB, and
        the class flags that.

        '''

        if np.isnan(self.qualificationDuration):
            self.calculateRandomVibration()

        if availableDuration <= 0.0:
            raise InvalidInputError(
                message       = 'Available duration must be positive.',
                parameterName = 'availableDuration', value = availableDuration,
                validRange    = 'Greater than 0 s'
            )

        exponent      = self._fatigueExponent()
        densityFactor = (self.qualificationDuration / availableDuration)**(2.0 / exponent)
        decibels      = 10.0 * np.log10(densityFactor)

        scaledSpectrum = [(frequency, density * densityFactor)
                          for frequency, density in self.qualificationPowerSpectralDensity]
        scaledGrms     = self._grmsFromSpectralDensity(scaledSpectrum)

        if decibels > 6.0:
            self.designNotes.append(
                f'Compressing the qualification test to {availableDuration:.0f} s requires a {decibels:.1f} dB level '
                f'increase. Above about 6 dB a scaled test starts exciting failure modes the article would never '
                f'see in flight, and the equivalence stops being defensible.')

        return {
            'requiredDuration':      self.qualificationDuration,
            'availableDuration':     availableDuration,
            'fatigueExponent':       exponent,
            'densityFactor':         densityFactor,
            'decibelIncrease':       decibels,
            'scaledSpectrum':        scaledSpectrum,
            'scaledGrms':            scaledGrms,
            'defensible':            decibels <= 6.0
        }

    def scaleLevelToDuration(self, decibelIncrease: float) -> dict:

        '''

        The inverse: the duration equivalent to a chosen level increase.

            t2 = t1 * (PSD1 / PSD2)^(m/2)

        Useful when the shaker cannot reach the required level and the trade has to go the other way,
        buying equivalence with time instead of amplitude.

        '''

        if np.isnan(self.qualificationDuration):
            self.calculateRandomVibration()

        exponent      = self._fatigueExponent()
        densityFactor = 10.0**(decibelIncrease / 10.0)
        duration      = self.qualificationDuration * densityFactor**(-exponent / 2.0)

        return {
            'decibelIncrease':   decibelIncrease,
            'densityFactor':     densityFactor,
            'fatigueExponent':   exponent,
            'requiredDuration':  self.qualificationDuration,
            'equivalentDuration': duration
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        rows = []

        if not np.isnan(self.acceptanceGrms):
            rows.extend([
                ['Acceptance Grms',           f'{self.acceptanceGrms:.3f} g'],
                ['Acceptance duration',       f'{self.acceptanceDuration:.0f} s per axis'],
                ['Qualification Grms',        f'{self.qualificationGrms:.3f} g'],
                ['Qualification duration',    f'{self.qualificationDuration:.0f} s per axis'],
                ['Level margin',              f'+{QUALIFICATION_MARGINS["randomVibrationDecibels"]:.0f} dB'],
                ['Fatigue exponent',          f'{self._fatigueExponent():.1f}']
            ])

        if self.qualificationShockSpectrum is not None:
            peak = max(acceleration for _, acceleration in self.qualificationShockSpectrum)
            rows.extend([
                ['Shock factor',              f'{QUALIFICATION_MARGINS["shockFactor"]:.2f}'],
                ['Peak qualification SRS',    f'{peak:.0f} g'],
                ['Shock applications',        f'{SHOCK_APPLICATIONS_PER_AXIS} per axis']
            ])

        if self.qualificationTemperatureRange is not None:
            rows.extend([
                ['Flight temperature range',  f'{self.flightTemperatureRange[0]:.1f} to '
                                              f'{self.flightTemperatureRange[1]:.1f} K'],
                ['Qual temperature range',    f'{self.qualificationTemperatureRange[0]:.1f} to '
                                              f'{self.qualificationTemperatureRange[1]:.1f} K'],
                ['Qual thermal cycles',       f'{self.qualificationThermalCycles:d}']
            ])

        report = formatReportTable(rows, ['Quantity', 'Value'],
                                   title = 'ENVIRONMENTAL TEST LEVEL REPORT')

        if self.qualificationPowerSpectralDensity is not None:
            spectrumRows = []
            for (frequency, acceptance), (_, qualification) in zip(
                    self.acceptancePowerSpectralDensity, self.qualificationPowerSpectralDensity):
                spectrumRows.append([f'{frequency:.0f}', f'{acceptance:.5f}', f'{qualification:.5f}'])
            report += '\n\n' + formatReportTable(
                spectrumRows, ['Frequency [Hz]', 'Acceptance [g^2/Hz]', 'Qualification [g^2/Hz]'],
                title = 'RANDOM VIBRATION SPECTRUM')

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'environmentalTestReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _fatigueExponent(self) -> float:

        '''

        Miner's rule fatigue exponent, from the override or the module default.

        '''

        return self.fatigueExponent if not np.isnan(self.fatigueExponent) else MINER_FATIGUE_EXPONENT

    def _resolveVibrationEnvironment(self) -> list:

        '''

        The flight PSD, from the explicit breakpoints or the generic environment lookup.

        '''

        if self.flightPowerSpectralDensity is not None:
            return self.flightPowerSpectralDensity

        if self.flightEnvironmentKey:
            key = self.flightEnvironmentKey.strip().lower()
            if key not in GENERIC_VIBRATION_ENVIRONMENTS:
                raise InvalidInputError(
                    message       = f'Unknown generic vibration environment \'{self.flightEnvironmentKey}\'.',
                    parameterName = 'flightEnvironmentKey', value = self.flightEnvironmentKey,
                    validRange    = str(sorted(GENERIC_VIBRATION_ENVIRONMENTS.keys()))
                )
            self.designNotes.append(
                f'Using the generic \'{key}\' vibration environment. A real program replaces this with a measured '
                f'or predicted zone-specific environment; a generic envelope is conservative in most bands and '
                f'unconservative in a few.')
            return GENERIC_VIBRATION_ENVIRONMENTS[key]

        raise InvalidInputError(
            message       = 'calculateRandomVibration needs either flightPowerSpectralDensity breakpoints or a '
                            'flightEnvironmentKey.',
            parameterName = 'flightPowerSpectralDensity', value = None,
            validRange    = 'Breakpoint list or a generic environment key'
        )

    def _resolveShockEnvironment(self) -> list:

        '''

        The flight SRS, from the explicit breakpoints or the generic environment lookup.

        '''

        if self.flightShockSpectrum is not None:
            return self.flightShockSpectrum

        if self.shockEnvironmentKey:
            key = self.shockEnvironmentKey.strip().lower()
            if key not in GENERIC_SHOCK_ENVIRONMENTS:
                raise InvalidInputError(
                    message       = f'Unknown generic shock environment \'{self.shockEnvironmentKey}\'.',
                    parameterName = 'shockEnvironmentKey', value = self.shockEnvironmentKey,
                    validRange    = str(sorted(GENERIC_SHOCK_ENVIRONMENTS.keys()))
                )
            return GENERIC_SHOCK_ENVIRONMENTS[key]

        raise InvalidInputError(
            message       = 'calculateShock needs either flightShockSpectrum breakpoints or a shockEnvironmentKey.',
            parameterName = 'flightShockSpectrum', value = None,
            validRange    = 'Breakpoint list or a generic environment key'
        )

    def _grmsFromSpectralDensity(self, spectralDensity: list) -> float:

        '''

        Overall RMS acceleration from a PSD breakpoint table.

        Integrates segment by segment treating each segment as a straight line on a log-log plot,
        which is how a PSD specification is defined and how a shaker controller interprets it.

            m    = ln(S2/S1) / ln(f2/f1)
            area = (f2*S2 - f1*S1) / (m + 1)     for m != -1
            area = S1 * f1 * ln(f2/f1)           for m == -1

        Treating the breakpoints as linear on a linear scale is the obvious mistake and it
        overestimates the area under a rolloff.

        '''

        totalArea = 0.0

        for index in range(len(spectralDensity) - 1):

            frequencyLow,  densityLow  = spectralDensity[index]
            frequencyHigh, densityHigh = spectralDensity[index + 1]

            if frequencyHigh <= frequencyLow:
                raise InvalidInputError(
                    message       = 'PSD breakpoint frequencies must increase monotonically.',
                    parameterName = 'flightPowerSpectralDensity',
                    value         = (frequencyLow, frequencyHigh),
                    validRange    = 'Strictly increasing frequency'
                )

            if densityLow <= 0.0 or densityHigh <= 0.0:
                raise InvalidInputError(
                    message       = 'PSD values must be positive; a log-log segment is undefined at zero.',
                    parameterName = 'flightPowerSpectralDensity',
                    value         = (densityLow, densityHigh), validRange = 'Greater than 0 g^2/Hz'
                )

            slope = np.log(densityHigh / densityLow) / np.log(frequencyHigh / frequencyLow)

            if abs(slope + 1.0) < 1.0e-9:
                area = densityLow * frequencyLow * np.log(frequencyHigh / frequencyLow)
            else:
                area = (frequencyHigh * densityHigh - frequencyLow * densityLow) / (slope + 1.0)

            totalArea += area

        return float(np.sqrt(totalArea))
