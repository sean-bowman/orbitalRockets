
# -- StartTransient -- #

'''

The start sequence, what accumulates while it runs, and what that accumulation is worth in chamber
pressure.

The central result of this sub-domain is one ratio. If combustion is established a time `t` after
propellant first reaches the chamber, and the chamber's mean residence time is `t_res`, then the
propellant sitting in the chamber at the moment of ignition is `t / t_res` times the mass that
would be there at steady state. Burn all of it at constant volume and the pressure spike is that
same ratio times the design chamber pressure.

    P_spike / P_c  =  t_delay / t_residence

Everything else in a hard start is a detail of that ratio. It explains why residence time, which
looks like a combustion efficiency parameter, is really a transient safety parameter. It explains
why hypergolic ignition delays are specified in milliseconds rather than tens of milliseconds. And
it explains why the fix for a hard start is almost never a bigger igniter.

The ratio is an upper bound and it is a loose one. It assumes everything that entered is at the
right mixture ratio, is fully vaporised, burns to completion, and burns faster than the nozzle can
vent. None of those is true. What the bound is good for is deciding whether a sequence is in the
regime where a hard start is possible at all, and by how much.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from ignitionUtils import (PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH, IGNITION_DELAY,
                               SSME_START_SEQUENCE, SSME_SEQUENCE_TOLERANCE,
                               accumulatedPropellant, residenceTime, primingTime,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, SequenceError)
except ImportError:
    from .ignitionUtils import (PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH, IGNITION_DELAY,
                                SSME_START_SEQUENCE, SSME_SEQUENCE_TOLERANCE,
                                accumulatedPropellant, residenceTime, primingTime,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, SequenceError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Universal gas constant, used to get the chamber gas density from the combustion temperature and
# the products' molecular weight.
UNIVERSAL_GAS_CONSTANT = 8314.462618    # [J/(kmol K)]

# The overpressure ratio above which a start is called hard.
#
# There is no sharp threshold in the physics and this is a convention. Twice the design chamber
# pressure is where the chamber's own proof margin is being spent on a transient, which is a
# reasonable place to draw a line that is admittedly drawn.
HARD_START_RATIO = 2.0    # [-]

# The ratio below which the spike is not worth reporting as a spike at all, because it is inside
# the normal chamber pressure ripple.
BENIGN_START_RATIO = 1.2    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- StartTransient -- #
# ------------------------------------------------------------------------------------------------ #

class StartTransient:

    '''

    Priming, accumulation and the ignition overpressure bound for a start sequence.

    '''

    def __init__(self):

        self.combination     = ''
        self.chamberPressure = np.nan
        self.throatArea      = np.nan
        self.massFlow        = np.nan
        self.ignitionDelay   = np.nan
        self.feedVolume      = np.nan
        self.startFlowFraction = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `ignitionDelay` is the time from propellant first entering the chamber to combustion being
        established, in seconds. It is the igniter's delay for a spark or torch system and the
        chemical delay for a hypergolic one, and for a hypergolic combination it defaults to the
        upper end of the measured range.

        `feedVolume` is the liquid volume downstream of the main valves, which is what has to be
        primed and what continues to arrive after shutdown.

        '''

        requiredParams = {'combination':     str,
                          'chamberPressure': (int, float),
                          'throatArea':      (int, float),
                          'massFlow':        (int, float)}

        optionalParams = {'ignitionDelay':     (int, float),
                          'feedVolume':        (int, float),
                          'startFlowFraction': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.startFlowFraction):
            self.startFlowFraction = 1.0

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise InvalidInputError(
                f'Unknown propellant combination \'{self.combination}\'. Known combinations are '
                f'{sorted(PROPELLANT_COMBINATIONS)}.',
                context = createErrorContext(component = 'StartTransient'))

        if not np.isfinite(self.ignitionDelay):
            self.ignitionDelay = self._defaultIgnitionDelay()

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def chamberVolume(self) -> float:

        '''
        Chamber volume from the characteristic length and the throat area, which is how L* is
        defined and how the propulsion hub sizes a chamber.
        '''

        return CHARACTERISTIC_LENGTH[self.combination]['value'] * self.throatArea

    def chamberGasDensity(self) -> float:

        '''
        Density of the combustion gas at the design point, from the ideal gas law.
        '''

        entry = PROPELLANT_COMBINATIONS[self.combination]

        specificGasConstant = UNIVERSAL_GAS_CONSTANT / entry['molarMass']

        return self.chamberPressure / (specificGasConstant * entry['chamberTemperature'])

    def residenceTime(self) -> float:

        '''
        The yardstick. Chamber gas mass over mass flow.
        '''

        return residenceTime(self.chamberVolume(), self.massFlow, self.chamberGasDensity())

    # -------------------------------------------------------------------------------------------- #

    def calculateAccumulation(self) -> dict:

        '''

        Propellant in the chamber at the moment of ignition, and the pressure bound that follows.

        The pressure bound is the ratio of the accumulated mass to the steady-state chamber gas
        mass, which reduces to the ignition delay over the residence time, scaled by whatever
        fraction of mainstage flow is actually being admitted. Both forms are returned because
        seeing them agree is the point.

            massRatio  =  startFlowFraction * t_delay / t_residence

        **The flow fraction is where the whole design lives.** At mainstage flow essentially every
        ignition delay is many chamber-fulls, which is not a statement about igniters being bad; it
        is the reason no engine ignites at mainstage flow.

        '''

        findings = []

        gasDensity  = self.chamberGasDensity()
        volume      = self.chamberVolume()
        steadyMass  = volume * gasDensity
        residence   = self.residenceTime()

        startFlow = self.massFlow * self.startFlowFraction

        accumulated = accumulatedPropellant(startFlow, self.ignitionDelay)

        massRatio = accumulated / steadyMass
        timeRatio = self.startFlowFraction * self.ignitionDelay / residence

        spike = massRatio * self.chamberPressure

        findings.append(
            f'The chamber holds {steadyMass * 1000.0:.1f} g of gas at the design point and its '
            f'residence time is {residence * 1000.0:.2f} ms.')

        findings.append(
            f'An ignition delay of {self.ignitionDelay * 1000.0:.1f} ms at '
            f'{self.startFlowFraction:.0%} of mainstage flow admits {accumulated * 1000.0:.1f} g '
            f'before combustion is established, which is {massRatio:.1f} chamber-fulls.')

        if massRatio >= HARD_START_RATIO:
            findings.append(
                f'That bounds the ignition spike at {spike / 1.0e6:.1f} MPa against a design '
                f'chamber pressure of {self.chamberPressure / 1.0e6:.1f} MPa. The bound is loose, '
                f'but a sequence in this regime can produce a hard start and the fix is the delay, '
                f'not the igniter energy.')
        elif massRatio <= BENIGN_START_RATIO:
            findings.append(
                f'That bounds the spike at {massRatio:.2f} times the design pressure, which is '
                f'inside the normal chamber pressure ripple. This sequence cannot produce a hard '
                f'start by accumulation.')
        else:
            findings.append(
                f'That bounds the spike at {massRatio:.2f} times the design pressure. Not a hard '
                f'start, and not comfortable either.')

        self.findings = findings

        return {'chamberVolume':     volume,
                'steadyChamberMass': steadyMass,
                'residenceTime':     residence,
                'accumulatedMass':   accumulated,
                'massRatio':         massRatio,
                'timeRatio':         timeRatio,
                'spikePressure':     spike,
                'hardStart':         bool(massRatio >= HARD_START_RATIO),
                'findings':          findings}

    # -------------------------------------------------------------------------------------------- #

    def calculatePriming(self, volumetricFlow: float = None) -> dict:

        '''

        Time to fill the feed volume downstream of the main valves.

        Priming is the event the RS-25 sequence is built around: the three combustors are primed
        about a tenth of a second apart and the whole sequence exists to hit those times. An engine
        is not started when the igniter fires, it is started when the last combustor primes.

        '''

        if not np.isfinite(self.feedVolume):
            raise InvalidInputError(
                'A feed volume is needed to compute a priming time. Set feedVolume, the liquid '
                'volume downstream of the main valves.',
                context = createErrorContext(component = 'StartTransient'))

        entry = PROPELLANT_COMBINATIONS[self.combination]

        if volumetricFlow is None:
            # a bulk propellant density weighted by the mixture ratio, which is enough for a fill
            # time and avoids pretending to know the split between the two circuits
            mixtureRatio = entry['mixtureRatio']

            density = ((mixtureRatio * entry['oxidiserDensity'] + entry['fuelDensity'])
                       / (mixtureRatio + 1.0))

            volumetricFlow = self.massFlow / density

        fillTime = primingTime(self.feedVolume, volumetricFlow)

        return {'feedVolume':     self.feedVolume,
                'volumetricFlow': volumetricFlow,
                'primingTime':    fillTime,
                'primingTimeInResidenceTimes': fillTime / self.residenceTime()}

    # -------------------------------------------------------------------------------------------- #

    def compareIgnitionDelays(self, delays: dict = None) -> dict:

        '''

        The accumulation bound across a range of ignition delays, which is where the shape of the
        problem shows.

        The relationship is linear, so nothing about the ranking is surprising. What is surprising
        is the scale: on a large engine the residence time is on the order of a millisecond, so a
        delay measured in tens of milliseconds is already tens of chamber-fulls.

        '''

        if delays is None:
            delays = {'hypergolic, fast':     0.002,
                      'hypergolic, slow':     0.008,
                      'spark, prompt':        0.020,
                      'spark, marginal':      0.050,
                      'failed then relit':    0.200}

        residence = self.residenceTime()

        results = {}

        for name, delay in delays.items():

            ratio = self.startFlowFraction * delay / residence

            results[name] = {'delay':      delay,
                             'massRatio':  ratio,
                             'spike':      ratio * self.chamberPressure,
                             'hardStart':  bool(ratio >= HARD_START_RATIO)}

        firstHard = next((name for name, entry in results.items() if entry['hardStart']), None)

        return {'residenceTime': residence,
                'results':       results,
                'firstHardStart': firstHard}

    # -------------------------------------------------------------------------------------------- #

    def checkSequence(self, sequence: dict) -> dict:

        '''

        Check a start sequence for the two things that destroy engines, and report the margin.

        The first is ordering: an event out of order is not a slow start, it is a burned turbine.
        The RS-25 source is explicit that an oxidiser preburner prime early or a main chamber prime
        late leads to a rapid pump acceleration that can destroy it.

        The second is spacing. The RS-25 primes its three combustors about a tenth of a second
        apart, and the same source states that a timing error of a tenth of a second can cause
        significant damage. **The design spacing and the damaging error are the same number**, which
        is the honest measure of how little margin a start sequence has.

        '''

        if len(sequence) < 2:
            raise SequenceError(
                'A sequence needs at least two events to be checked for ordering.',
                context = createErrorContext(component = 'StartTransient'))

        times = list(sequence.values())
        names = list(sequence.keys())

        ordered = times == sorted(times)

        if not ordered:
            outOfOrder = [names[index] for index in range(1, len(times))
                          if times[index] < times[index - 1]]

            raise SequenceError(
                f'The sequence is not monotonic in time: {outOfOrder} occur before the event '
                f'preceding them. A start sequence out of order is not a slow start, it is a '
                f'destroyed engine, so this is refused rather than reported.',
                context = createErrorContext(component = 'StartTransient'))

        spacings = np.diff(times)

        tightest = float(np.min(spacings))
        tolerance = SSME_SEQUENCE_TOLERANCE['timingError']

        findings = []

        findings.append(
            f'The tightest spacing in the sequence is {tightest * 1000.0:.0f} ms, between '
            f'{names[int(np.argmin(spacings))]} and {names[int(np.argmin(spacings)) + 1]}.')

        findings.append(
            f'The RS-25 states that a timing error of {tolerance * 1000.0:.0f} ms can cause '
            f'significant damage, and it primes its three combustors '
            f'{SSME_SEQUENCE_TOLERANCE["primeSpacing"] * 1000.0:.0f} ms apart. The design spacing '
            f'and the damaging error are the same number.')

        if tightest < tolerance:
            findings.append(
                'This sequence is spaced more tightly than the error that damages an RS-25. That '
                'is not a verdict on this engine, which may be smaller and more forgiving, but it '
                'is the point at which the sequence needs a transient model rather than a table.')

        return {'ordered':      bool(ordered),
                'spacings':     spacings,
                'tightest':     tightest,
                'toleranceRef': tolerance,
                'insideReferenceTolerance': bool(tightest >= tolerance),
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full start transient report.
        '''

        accumulation = self.calculateAccumulation()
        comparison   = self.compareIgnitionDelays()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  START TRANSIENT: {self.combination} at '
                     f'{self.chamberPressure / 1.0e6:.1f} MPa')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Chamber volume',      f'{accumulation["chamberVolume"] * 1.0e3:.2f}',    'L'],
             ['Steady gas mass',     f'{accumulation["steadyChamberMass"] * 1000.0:.1f}', 'g'],
             ['Residence time',      f'{accumulation["residenceTime"] * 1000.0:.2f}',   'ms'],
             ['Ignition delay',      f'{self.ignitionDelay * 1000.0:.1f}',              'ms'],
             ['Accumulated mass',    f'{accumulation["accumulatedMass"] * 1000.0:.1f}', 'g'],
             ['Chamber-fulls',       f'{accumulation["massRatio"]:.2f}',                ''],
             ['Spike pressure bound', f'{accumulation["spikePressure"] / 1.0e6:.2f}',   'MPa'],
             ['Hard start',          f'{accumulation["hardStart"]}',                    '']],
            ['Quantity', 'Value', 'Unit'], title = 'Accumulation'))

        lines.append('')

        rows = [[name,
                 f'{entry["delay"] * 1000.0:.0f}',
                 f'{entry["massRatio"]:.1f}',
                 f'{entry["spike"] / 1.0e6:.1f}',
                 'yes' if entry['hardStart'] else 'no']
                for name, entry in comparison['results'].items()]

        lines.append(formatReportTable(
            rows, ['Case', 'Delay [ms]', 'Chamber-fulls', 'Spike [MPa]', 'Hard'],
            title = 'Ignition delay sensitivity'))

        lines.append('')
        for finding in accumulation['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'start_transient.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _defaultIgnitionDelay(self) -> float:

        '''
        The upper end of the measured hypergolic range where one exists, and nothing otherwise.
        '''

        if self.combination in IGNITION_DELAY:
            return IGNITION_DELAY[self.combination][1] / 1000.0

        raise InvalidInputError(
            f'\'{self.combination}\' is not hypergolic, so its ignition delay is a property of the '
            f'igniter rather than of the propellants and there is no default to fall back on. Set '
            f'ignitionDelay explicitly. Hypergolic combinations with a measured range are '
            f'{sorted(IGNITION_DELAY)}.',
            context = createErrorContext(component = 'StartTransient'))

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.chamberPressure <= 0.0:
            raise InvalidInputError(
                f'The chamber pressure must be positive, got {self.chamberPressure}.',
                context = createErrorContext(component = 'StartTransient'))

        if self.throatArea <= 0.0:
            raise InvalidInputError(
                f'The throat area must be positive, got {self.throatArea}.',
                context = createErrorContext(component = 'StartTransient'))

        if self.massFlow <= 0.0:
            raise InvalidInputError(
                f'The mass flow must be positive, got {self.massFlow}.',
                context = createErrorContext(component = 'StartTransient'))

        if self.ignitionDelay < 0.0:
            raise InvalidInputError(
                f'The ignition delay cannot be negative, got {self.ignitionDelay}.',
                context = createErrorContext(component = 'StartTransient'))

        if not 0.0 < self.startFlowFraction <= 1.0:
            raise InvalidInputError(
                f'The start flow fraction must lie in (0, 1], got {self.startFlowFraction}. It is '
                f'the fraction of mainstage flow being admitted while the engine lights, and it '
                f'scales the accumulation directly.',
                context = createErrorContext(component = 'StartTransient'))

        if self.ignitionDelay > 1.0:
            raise SequenceError(
                f'An ignition delay of {self.ignitionDelay:.2f} s is longer than most engines take '
                f'to reach mainstage. If combustion has not started by then the sequence has '
                f'failed and the correct action is to close the valves, not to compute an '
                f'overpressure. Set a detection window instead; see IgnitionSystem.',
                context = createErrorContext(component = 'StartTransient'))
