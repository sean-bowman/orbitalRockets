
# -- ShockSpectrum Class Definition -- #

'''

Shock response spectra, pyroshock attenuation with distance and across joints, and test levels.

Shock is the environment with the worst signal-to-noise ratio in the whole discipline. The event
lasts a few milliseconds, the peak accelerations are thousands of g, the measurement is difficult
and frequently wrong, and the flight-to-flight scatter is large enough that a 6 dB qualification
margin is used rather than the 3 dB that random vibration gets.

It is also the environment that breaks things nothing else breaks: relays chatter, crystals crack,
solder joints fail, and brittle parts fracture, all without the structure noticing anything
happened. Shock damages small stiff things, and the structure it passes through is usually fine.

The shock response spectrum is not a spectrum in the Fourier sense. It is the peak response of a
family of single degree of freedom oscillators, one per frequency, all driven by the same base
transient:

    SRS(f) = max over time of the response of an oscillator at frequency f with Q = 10

That definition matters because it is not invertible. Many different transients produce the same
SRS, and two of them can damage hardware differently. An SRS is a damage-potential summary, not a
description of the event.

Attenuation is what makes shock tractable. It falls off steeply with distance from the source and
across every joint it crosses, so a component a metre away behind three joints sees a small
fraction of what the pyrotechnic device produced.

See Also:
---------
RandomVibrationSpec : The other high frequency environment, with better statistics
AcousticSpec        : Liftoff acoustics, a different kind of transient

Theory: docs/ShockEnvironment.md

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
                                   QUALIFICATION_MARGIN_SHOCK,
                                   InvalidInputError, SpectrumError, createErrorContext)
except ImportError:
    from .environmentsUtils import (applyInputs, formatReportTable, decibelToRatio, ratioToDecibel,
                                    QUALIFICATION_MARGIN_SHOCK,
                                    InvalidInputError, SpectrumError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The standard amplification factor for an SRS. Q = 10 is 5 percent critical damping and it is the
# near-universal convention. An SRS quoted at a different Q is a different number and comparing
# them without conversion is meaningless.
STANDARD_QUALITY_FACTOR = 10.0    # [-]

# Pyroshock sources, with a representative peak SRS at the source and the knee frequency above
# which the spectrum flattens. These are order-of-magnitude anchors, not specifications.
SHOCK_SOURCES = {
    'linear shaped charge': {'peakSrs': 10000.0, 'kneeFrequency': 2000.0,
                             'note': 'the most severe common source, stage separation'},
    'frangible joint':      {'peakSrs': 6000.0,  'kneeFrequency': 2000.0,
                             'note': 'contained, cleaner than shaped charge'},
    'explosive bolt':       {'peakSrs': 3000.0,  'kneeFrequency': 1500.0,
                             'note': 'local, and there are usually several'},
    'separation nut':       {'peakSrs': 2000.0,  'kneeFrequency': 1500.0,
                             'note': 'lower shock, heavier hardware'},
    'pin puller':           {'peakSrs': 1000.0,  'kneeFrequency': 1000.0,
                             'note': 'low shock release device'},
    'clamp band release':   {'peakSrs': 1500.0,  'kneeFrequency': 1000.0,
                             'note': 'payload separation, distributed source'},
}

# Attenuation with distance from the source. Pyroshock falls off far faster than vibration because
# the high frequency content is dissipated by material damping over a short path.
DISTANCE_ATTENUATION_PER_METRE = -13.0    # [dB/m], a widely used engineering rule

# Every structural joint the shock crosses dissipates energy. Bolted joints are the worst because
# they have interfaces that slip.
JOINT_ATTENUATION = {
    'monolithic':   0.0,    # [dB], no joint
    'welded':      -1.0,    # [dB], continuous, little dissipation
    'bonded':      -2.0,    # [dB]
    'bolted':      -3.0,    # [dB], per joint. The common case
    'riveted':     -3.0,    # [dB], per joint
    'isolated':   -20.0,    # [dB], a designed shock isolator
}

# Below this frequency pyroshock is not the governing environment; the transient and random
# vibration environments are. An SRS quoted below it is usually an artefact.
PYROSHOCK_VALID_FLOOR = 100.0    # [Hz]

# The SRS rises at roughly 9 to 12 dB per octave below the knee, which corresponds to a
# constant-velocity spectrum, and flattens above it.
SRS_LOW_FREQUENCY_SLOPE = 9.0    # [dB/octave]

# ------------------------------------------------------------------------------------------------ #
# -- ShockSpectrum -- #
# ------------------------------------------------------------------------------------------------ #

class ShockSpectrum:

    '''

    Shock response spectrum construction, attenuation and test level derivation.

    Usage:
    ------
        shock = ShockSpectrum()
        shock.setInputs({'source': 'linear shaped charge', 'distance': 1.2,
                         'jointPath': ['bolted', 'bolted']})
        result = shock.calculateAttenuatedSpectrum()

    '''

    def __init__(self):

        # -- Source -- #

        self.source          = 'frangible joint'   # key into SHOCK_SOURCES
        self.peakSrs         = np.nan   # [g], overrides the source table
        self.kneeFrequency   = np.nan   # [Hz], overrides the source table

        # -- Path -- #

        self.distance        = 0.0      # [m], from the source to the component
        self.jointPath       = []       # [-], joint types crossed, keys into JOINT_ATTENUATION

        # -- Spectrum Definition -- #

        self.lowFrequency    = 100.0    # [Hz], the lowest frequency of interest
        self.highFrequency   = 10000.0  # [Hz]
        self.qualityFactor   = STANDARD_QUALITY_FACTOR   # [-]

        # -- Margin Policy -- #

        self.qualificationMargin = QUALIFICATION_MARGIN_SHOCK   # [dB]

        # -- Results -- #

        self.findings        = []       # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        '''

        requiredParams = {}

        optionalParams = {'source':              str,
                          'peakSrs':             (int, float),
                          'kneeFrequency':       (int, float),
                          'distance':            (int, float),
                          'jointPath':           (list, tuple),
                          'lowFrequency':        (int, float),
                          'highFrequency':       (int, float),
                          'qualityFactor':       (int, float),
                          'qualificationMargin': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.source not in SHOCK_SOURCES:
            raise InvalidInputError(
                f'Unknown shock source \'{self.source}\'. Known: {sorted(SHOCK_SOURCES)}.',
                context = createErrorContext(component = 'ShockSpectrum'))

        entry = SHOCK_SOURCES[self.source]

        if not np.isfinite(self.peakSrs):
            self.peakSrs = entry['peakSrs']
        if not np.isfinite(self.kneeFrequency):
            self.kneeFrequency = entry['kneeFrequency']

        self.jointPath = list(self.jointPath)

    # -------------------------------------------------------------------------------------------- #

    def calculateAttenuation(self) -> dict:

        '''

        Total attenuation from distance and from every joint crossed.

        Attenuation is what makes pyroshock survivable. A component a metre away behind two bolted
        joints sees a small fraction of the source level, and moving a sensitive part further away
        or adding a joint is far cheaper than qualifying it to the source environment.

        '''

        self._validateInputs()

        distanceLoss = DISTANCE_ATTENUATION_PER_METRE * self.distance

        jointLoss = 0.0
        for joint in self.jointPath:
            if joint not in JOINT_ATTENUATION:
                raise InvalidInputError(
                    f'Unknown joint type \'{joint}\'. Known: {sorted(JOINT_ATTENUATION)}.',
                    context = createErrorContext(component = 'ShockSpectrum'))
            jointLoss += JOINT_ATTENUATION[joint]

        total = distanceLoss + jointLoss

        self.findings = []

        self.findings.append(
            f'{self.distance:.2f} m of structure and {len(self.jointPath)} joint(s) attenuate the '
            f'source by {total:.1f} dB, a factor of '
            f'{1.0 / decibelToRatio(total, "amplitude"):.1f} in level.')

        if not self.jointPath and self.distance < 0.1:
            self.findings.append(
                'The component is essentially at the source with no joints in the path. This is '
                'the worst case in the vehicle and it is where shock isolation earns its mass.')

        return {'distanceAttenuation': distanceLoss,
                'jointAttenuation':    jointLoss,
                'totalAttenuation':    total,
                'amplitudeFactor':     decibelToRatio(total, quantity = 'amplitude'),
                'jointCount':          len(self.jointPath),
                'findings':            self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateAttenuatedSpectrum(self, points: int = 12) -> dict:

        '''

        The SRS at the component, after attenuation, as a table across the frequency range.

        The spectrum rises at roughly 9 dB per octave below the knee and is flat above it. That
        low frequency slope corresponds to a constant velocity change, which is the physical
        content: a shock event delivers a velocity increment, and an oscillator's peak response to
        a velocity step rises linearly with its frequency.

        '''

        self._validateInputs()

        attenuation = self.calculateAttenuation()
        peak        = self.peakSrs * attenuation['amplitudeFactor']

        frequencies = np.logspace(np.log10(self.lowFrequency),
                                  np.log10(self.highFrequency), points)

        levels = []
        for frequency in frequencies:
            if frequency >= self.kneeFrequency:
                levels.append(peak)
            else:
                octaves = np.log2(frequency / self.kneeFrequency)
                levels.append(peak * decibelToRatio(SRS_LOW_FREQUENCY_SLOPE * octaves,
                                                    quantity = 'amplitude'))

        return {'frequencies':      frequencies,
                'levels':           np.array(levels),
                'peakLevel':        peak,
                'sourcePeak':       self.peakSrs,
                'kneeFrequency':    self.kneeFrequency,
                'totalAttenuation': attenuation['totalAttenuation'],
                'qualityFactor':    self.qualityFactor,
                'findings':         attenuation['findings']}

    # -------------------------------------------------------------------------------------------- #

    def deriveTestLevels(self) -> dict:

        '''

        Qualification level, which carries a 6 dB margin rather than the 3 dB random vibration gets.

        The larger margin exists because shock scatter is larger. Flight-to-flight variation of a
        pyrotechnic event is substantial, the measurement is difficult, and the SRS is a lossy
        summary of the transient. Six decibels is a factor of two in level, not in energy.

        '''

        self._validateInputs()

        spectrum = self.calculateAttenuatedSpectrum()

        qualificationPeak = spectrum['peakLevel'] * decibelToRatio(self.qualificationMargin,
                                                                  quantity = 'amplitude')

        findings = list(spectrum['findings'])
        findings.append(
            f'Shock qualification carries {self.qualificationMargin:+.0f} dB against random '
            f'vibration\'s +3 dB, because the scatter is larger and the measurement is harder. '
            f'On an amplitude quantity that is a factor of '
            f'{decibelToRatio(self.qualificationMargin, "amplitude"):.2f}.')

        findings.append(
            'Shock is not usually a structural problem. It breaks relays, crystals, solder joints '
            'and brittle parts, and the structure it travelled through is generally unharmed.')

        return {'maximumPredictedPeak': spectrum['peakLevel'],
                'qualificationPeak':    qualificationPeak,
                'marginDecibels':       self.qualificationMargin,
                'amplitudeRatio':       decibelToRatio(self.qualificationMargin, 'amplitude'),
                'kneeFrequency':        self.kneeFrequency,
                'findings':             findings}

    # -------------------------------------------------------------------------------------------- #

    def compareTestMethods(self) -> dict:

        '''

        The available shock test methods and what each one actually reproduces.

        Fidelity to the real event varies enormously, and the cheapest method is the least like
        flight. That trade is worth making deliberately rather than by default.

        '''

        methods = {
            'pyrotechnic, flight article': {
                'fidelity': 'highest', 'cost': 'highest',
                'note': 'the actual device on the actual structure. Destructive and definitive'},
            'mechanical impact': {
                'fidelity': 'good above 1 kHz', 'cost': 'moderate',
                'note': 'resonant plate or bar struck by a projectile. The common choice'},
            'electrodynamic shaker': {
                'fidelity': 'poor above 2 kHz', 'cost': 'low',
                'note': 'a synthesised transient. Limited by shaker stroke and frequency'},
            'drop table': {
                'fidelity': 'low frequency only', 'cost': 'low',
                'note': 'classical pulses. Not representative of pyroshock at all'},
        }

        findings = [
            'A shaker cannot reproduce pyroshock above roughly 2 kHz, which is where most of the '
            'damage potential is. A shaker shock test that passes proves less than it appears to.',
            'Many transients share one SRS, so matching the SRS does not match the event. Two '
            'tests that both meet the specification can damage hardware differently.']

        return {'methods': methods, 'findings': findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the shock environment.
        '''

        attenuation = self.calculateAttenuation()
        levels      = self.deriveTestLevels()
        spectrum    = self.calculateAttenuatedSpectrum(points = 6)

        lines = []
        lines.append('=' * 96)
        lines.append(f'  SHOCK ENVIRONMENT: {self.source}, {self.distance:.2f} m, '
                     f'{len(self.jointPath)} joint(s)')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Source peak SRS',   f'{self.peakSrs:.0f}', 'g'],
                ['Distance loss',     f'{attenuation["distanceAttenuation"]:.1f}', 'dB'],
                ['Joint loss',        f'{attenuation["jointAttenuation"]:.1f}', 'dB'],
                ['Total attenuation', f'{attenuation["totalAttenuation"]:.1f}', 'dB'],
                ['At the component',  f'{levels["maximumPredictedPeak"]:.0f}', 'g'],
                ['Qualification',     f'{levels["qualificationPeak"]:.0f}', 'g']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'],
                                       title = 'Attenuation and levels'))
        lines.append('')

        spectrumRows = [[f'{frequency:.0f}', f'{level:.0f}']
                        for frequency, level in zip(spectrum['frequencies'], spectrum['levels'])]
        lines.append(formatReportTable(spectrumRows, ['Frequency [Hz]', 'SRS [g]'],
                                       title = f'Spectrum at Q = {self.qualityFactor:.0f}'))

        if levels['findings']:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in levels['findings']:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'shockEnvironment.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the source, path and frequency range are physical.
        '''

        context = createErrorContext(component = 'ShockSpectrum')

        if not np.isfinite(self.peakSrs) or self.peakSrs <= 0.0:
            raise InvalidInputError('Peak SRS must be positive.', context = context)

        if self.distance < 0.0:
            raise InvalidInputError('Distance cannot be negative.', context = context)

        if self.qualityFactor <= 0.0:
            raise InvalidInputError('Quality factor must be positive.', context = context)

        if self.lowFrequency <= 0.0 or self.highFrequency <= self.lowFrequency:
            raise SpectrumError(
                f'Frequency range must increase and be positive, got {self.lowFrequency} to '
                f'{self.highFrequency}.', context = context)

        if self.lowFrequency < PYROSHOCK_VALID_FLOOR:
            raise SpectrumError(
                f'A pyroshock SRS below {PYROSHOCK_VALID_FLOOR:.0f} Hz is usually an artefact. '
                f'Below that the transient and random vibration environments govern, not shock.',
                context = context)
