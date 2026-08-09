
# -- HotFireTest -- #

'''

Whether a hot fire can answer the question it was written to answer.

fluidSystemsTesting states the principle: a test that cannot fail its own acceptance criterion has
not tested anything. This class is that principle made arithmetic for a hot fire, in three
independent ways, and each of them fails real tests.

**Can the measurement resolve the criterion.** An acceptance band narrower than the measurement
uncertainty is a band decided by noise. The ratio of the two is the only number that says whether a
pass means anything, and it is rarely computed before the test rather than after.

**Can the data system see what it is looking for.** A first tangential mode on a small chamber sits
in the kilohertz, and resolving its amplitude and decay needs an order of magnitude more sample
rate than detecting that it exists. A stability rating test recorded at a performance sample rate
has recorded nothing.

**Is the burn long enough for the thing being measured to have settled.** Chamber pressure settles
in milliseconds and wall temperature in seconds, and a test that reduces performance from a window
before the walls settled is reducing a transient.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from propulsionTestUtils import (INSTRUMENT_UNCERTAINTY, PROPELLANT_COMBINATIONS,
                                     NYQUIST_FACTOR, RESOLUTION_FACTOR,
                                     STABILITY_PULSE_FRACTION_MINIMUM, PULSE_GUN_DIAMETER_LIMIT,
                                     INSTABILITY_FLUX_MULTIPLIER,
                                     firstTangentialFrequency, rootSumSquare,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, TestDesignError)
except ImportError:
    from .propulsionTestUtils import (INSTRUMENT_UNCERTAINTY, PROPELLANT_COMBINATIONS,
                                      NYQUIST_FACTOR, RESOLUTION_FACTOR,
                                      STABILITY_PULSE_FRACTION_MINIMUM, PULSE_GUN_DIAMETER_LIMIT,
                                      INSTABILITY_FLUX_MULTIPLIER,
                                      firstTangentialFrequency, rootSumSquare,
                                      applyInputs, formatReportTable, createErrorContext,
                                      InvalidInputError, TestDesignError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The ratio of acceptance band to measurement uncertainty below which a test is deciding on noise.
#
# Three is a convention rather than a derivation, and it is chosen so that a result at the band edge
# is separated from the criterion by more than the coverage-factor-two uncertainty of the
# measurement. A test at a ratio of one is a coin toss and this repository refuses it.
DISCRIMINATION_RATIO_FLOOR = 3.0    # [-]

# Below this the test cannot distinguish a pass from a fail at all.
DISCRIMINATION_RATIO_REFUSED = 1.0    # [-]

# Representative speed of sound in the combustion gas, used only to place the acoustic mode when a
# real value is not supplied. It is an order of magnitude, and the conclusion drawn from it does not
# turn on the value.
DEFAULT_SPEED_OF_SOUND = 1000.0    # [m/s]

# Time constants for the two things that settle at different rates. The chamber settles in a few
# residence times; the wall settles on its own thermal time constant, which is seconds.
#
# Both are representative and both are registered as unvalidated. The ordering between them is the
# point and it is robust: the wall is always slower, by two to three orders of magnitude.
CHAMBER_SETTLING_RESIDENCE_TIMES = 20.0    # [-]
WALL_SETTLING_TIME = 3.0                   # [s]

# ------------------------------------------------------------------------------------------------ #
# -- HotFireTest -- #
# ------------------------------------------------------------------------------------------------ #

class HotFireTest:

    '''

    Discrimination, sample rate adequacy and duration for a hot fire test.

    '''

    def __init__(self):

        self.objective       = ''
        self.chamberPressure = np.nan
        self.chamberDiameter = np.nan
        self.residenceTime   = np.nan
        self.duration        = np.nan
        self.sampleRate      = np.nan
        self.speedOfSound    = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `objective` is free text and it is required, because a test without a stated question is
        the failure mode this class exists to catch and there is no way to check for it
        automatically.

        '''

        requiredParams = {'objective':       str,
                          'chamberPressure': (int, float),
                          'chamberDiameter': (int, float),
                          'duration':        (int, float)}

        optionalParams = {'residenceTime': (int, float),
                          'sampleRate':    (int, float),
                          'speedOfSound':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.speedOfSound):
            self.speedOfSound = DEFAULT_SPEED_OF_SOUND

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def checkDiscrimination(self, acceptanceBand: float, channel: str = 'chamberPressure',
                            uncertainty: float = None) -> dict:

        '''

        Whether the acceptance band is wide enough that the measurement can decide it.

        `acceptanceBand` is the half-width of the acceptance criterion as a fraction of the
        measured quantity: a requirement of plus or minus 2 per cent is 0.02.

        The class **raises** when the band is inside the measurement uncertainty, rather than
        reporting a low ratio. A test that cannot distinguish a pass from a fail and is run anyway
        produces a verdict with a signature on it, and that is worse than not running it.

        '''

        if acceptanceBand <= 0.0:
            raise InvalidInputError(
                f'The acceptance band must be positive, got {acceptanceBand}. It is a half-width '
                f'as a fraction of the measured quantity.',
                context = createErrorContext(component = 'HotFireTest'))

        if uncertainty is None:

            if channel not in INSTRUMENT_UNCERTAINTY:
                raise InvalidInputError(
                    f'No default uncertainty for channel \'{channel}\'. Known channels are '
                    f'{sorted(INSTRUMENT_UNCERTAINTY)}, or pass one explicitly.',
                    context = createErrorContext(component = 'HotFireTest'))

            uncertainty = INSTRUMENT_UNCERTAINTY[channel]['relative']
            label = channel

        else:
            # a supplied uncertainty is usually a reduced parameter rather than a raw channel, so
            # naming the default channel in the message would be actively misleading
            label = 'supplied'

        ratio = acceptanceBand / uncertainty

        findings = []

        findings.append(
            f'An acceptance band of {acceptanceBand:.1%} against a {label} uncertainty of '
            f'{uncertainty:.2%} gives a discrimination ratio of {ratio:.1f}.')

        if ratio <= DISCRIMINATION_RATIO_REFUSED:
            raise TestDesignError(
                f'The acceptance band of {acceptanceBand:.2%} is inside the {label} measurement '
                f'uncertainty of {uncertainty:.2%}, so this test cannot distinguish a pass from a '
                f'fail. Running it produces a verdict decided by noise and signed by a person, '
                f'which is worse than not running it. Either widen the band, improve the '
                f'measurement, or state the requirement against something else.',
                context = createErrorContext(component = 'HotFireTest'))

        if ratio < DISCRIMINATION_RATIO_FLOOR:
            findings.append(
                f'That is below the working floor of {DISCRIMINATION_RATIO_FLOOR:.0f}. The test '
                f'can decide, and a result near the band edge will be argued about, which in '
                f'practice means it will be decided by whoever is most senior in the room.')
        else:
            findings.append(
                'The band is comfortably wider than the measurement, so a result near the edge is '
                'still a result.')

        self.findings = findings

        return {'acceptanceBand': acceptanceBand,
                'uncertainty':    uncertainty,
                'ratio':          ratio,
                'canDecide':      True,
                'comfortable':    bool(ratio >= DISCRIMINATION_RATIO_FLOOR),
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def checkSampleRate(self) -> dict:

        '''

        Whether the data system can see the first tangential mode, detect it, and resolve it.

        Three thresholds rather than one, because they answer different questions. Nyquist says
        whether the frequency is representable at all. Ten samples per cycle is what it takes to
        recover an amplitude and a decay rate, which is what a stability rating needs.

        '''

        frequency = firstTangentialFrequency(self.speedOfSound, self.chamberDiameter)

        nyquist    = NYQUIST_FACTOR * frequency
        resolution = RESOLUTION_FACTOR * frequency

        findings = []

        findings.append(
            f'The first tangential mode sits at {frequency / 1000.0:.2f} kHz on a '
            f'{self.chamberDiameter * 1000.0:.0f} mm chamber.')

        findings.append(
            f'Detecting it needs {nyquist / 1000.0:.1f} kHz and resolving its amplitude and decay '
            f'needs {resolution / 1000.0:.0f} kHz.')

        if not np.isfinite(self.sampleRate):

            findings.append(
                'No sample rate was given, so nothing is being asserted about this data system. '
                'The two thresholds above are what it has to beat.')

            return {'frequency':    frequency,
                    'nyquistRate':  nyquist,
                    'resolutionRate': resolution,
                    'sampleRate':   None,
                    'detects':      None,
                    'resolves':     None,
                    'findings':     findings}

        detects  = bool(self.sampleRate >= nyquist)
        resolves = bool(self.sampleRate >= resolution)

        if not detects:
            findings.append(
                f'At {self.sampleRate / 1000.0:.1f} kHz the mode is below Nyquist and **will alias '
                f'into the performance band**, where it will look like a low frequency oscillation '
                f'that is not there. This is worse than not measuring it.')
        elif not resolves:
            findings.append(
                f'At {self.sampleRate / 1000.0:.1f} kHz the mode is detectable but not resolvable. '
                f'The test can say an instability happened and cannot say how large it was or how '
                f'fast it damped, which is what a stability rating is.')
        else:
            findings.append(
                f'At {self.sampleRate / 1000.0:.1f} kHz the mode is resolvable.')

        return {'frequency':      frequency,
                'nyquistRate':    nyquist,
                'resolutionRate': resolution,
                'sampleRate':     self.sampleRate,
                'detects':        detects,
                'resolves':       resolves,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def checkDuration(self) -> dict:

        '''

        Whether the burn is long enough for the quantity being measured to have settled.

        Two settling times, orders of magnitude apart. The chamber settles in a few tens of
        residence times, which is milliseconds. The wall settles on its own thermal time constant,
        which is seconds, and a performance reduction taken before it has is reducing a transient
        with a cooler nozzle than the engine will ever fly with.

        '''

        findings = []

        chamberSettling = (CHAMBER_SETTLING_RESIDENCE_TIMES * self.residenceTime
                           if np.isfinite(self.residenceTime) else np.nan)

        wallSettling = WALL_SETTLING_TIME

        if np.isfinite(chamberSettling):
            findings.append(
                f'The chamber settles in about {chamberSettling * 1000.0:.0f} ms, which is '
                f'{CHAMBER_SETTLING_RESIDENCE_TIMES:.0f} residence times.')

        findings.append(
            f'The wall settles on its own thermal time constant, of order {wallSettling:.0f} s. '
            f'The two differ by three orders of magnitude.')

        settlesChamber = bool(np.isfinite(chamberSettling) and self.duration > chamberSettling)
        settlesWall    = bool(self.duration > wallSettling)

        if not settlesWall:
            findings.append(
                f'This {self.duration:.1f} s burn does not reach wall thermal equilibrium. A '
                f'performance number from it is valid and a wall temperature from it is not, and '
                f'the second is usually what a short test was run to get.')
        else:
            findings.append(
                f'This {self.duration:.1f} s burn reaches both, so a steady window exists for '
                f'both performance and thermal reduction.')

        usableWindow = max(self.duration - wallSettling, 0.0)

        return {'chamberSettling': chamberSettling,
                'wallSettling':    wallSettling,
                'duration':        self.duration,
                'settlesChamber':  settlesChamber,
                'settlesWall':     settlesWall,
                'usableThermalWindow': usableWindow,
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def checkStabilityRating(self, pulseOverpressure: float) -> dict:

        '''

        Whether a stability rating perturbation is large enough to be worth calling one, and whether
        the device chosen can deliver it at this chamber size.

        The NASA MSFC pulse gun development programme recorded zero-to-peak overpressures of 37 to
        58 per cent of mean chamber pressure and called that adequate for typical stability rating.
        Below that the chamber has been tapped rather than perturbed, and a chamber that recovers
        from a tap has demonstrated nothing.

        '''

        if pulseOverpressure <= 0.0:
            raise InvalidInputError(
                f'The pulse overpressure must be positive, got {pulseOverpressure}. It is the '
                f'zero-to-peak amplitude in the same units as the chamber pressure.',
                context = createErrorContext(component = 'HotFireTest'))

        fraction = pulseOverpressure / self.chamberPressure

        adequate = bool(fraction >= STABILITY_PULSE_FRACTION_MINIMUM)

        pulseGunViable = bool(self.chamberDiameter <= PULSE_GUN_DIAMETER_LIMIT)

        findings = []

        findings.append(
            f'A zero-to-peak overpressure of {fraction:.0%} of chamber pressure, against a '
            f'reference minimum of {STABILITY_PULSE_FRACTION_MINIMUM:.0%}.')

        if not adequate:
            findings.append(
                'That is below what the reference programme called adequate. The chamber has been '
                'tapped rather than perturbed, and recovering from a tap demonstrates nothing '
                'about stability.')

        if pulseGunViable:
            findings.append(
                f'At {self.chamberDiameter * 1000.0:.0f} mm the chamber is within the range where '
                f'a pulse gun can produce an adequate response. That matters operationally: bombs '
                f'are expensive, hard to procure and demanding to transport and handle.')
        else:
            findings.append(
                f'At {self.chamberDiameter * 1000.0:.0f} mm the chamber is above the roughly '
                f'{PULSE_GUN_DIAMETER_LIMIT * 1000.0:.0f} mm where a pulse gun may be unable to '
                f'produce an adequate response, so a bomb is likely to be needed with everything '
                f'that implies for procurement and handling.')

        lower, upper = INSTABILITY_FLUX_MULTIPLIER['injector face']

        findings.append(
            f'Worth stating why this test is run at all: under high frequency instability the heat '
            f'flux near the injector face can rise by {lower:.0f} to {upper:.0f} times and can '
            f'double at the throat. No cooling design in this repository survives that, so '
            f'stability is a hardware survival requirement rather than a performance one.')

        return {'fraction':       fraction,
                'minimum':        STABILITY_PULSE_FRACTION_MINIMUM,
                'adequate':       adequate,
                'pulseGunViable': pulseGunViable,
                'fluxMultiplier': INSTABILITY_FLUX_MULTIPLIER,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full test design report.
        '''

        sampling = self.checkSampleRate()
        duration = self.checkDuration()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  HOT FIRE TEST: {self.objective}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Chamber pressure',   f'{self.chamberPressure / 1.0e6:.2f}',            'MPa'],
             ['Chamber diameter',   f'{self.chamberDiameter * 1000.0:.0f}',           'mm'],
             ['Duration',           f'{self.duration:.1f}',                           's'],
             ['First tangential',   f'{sampling["frequency"] / 1000.0:.2f}',          'kHz'],
             ['Rate to detect',     f'{sampling["nyquistRate"] / 1000.0:.1f}',        'kHz'],
             ['Rate to resolve',    f'{sampling["resolutionRate"] / 1000.0:.0f}',     'kHz'],
             ['Wall settling',      f'{duration["wallSettling"]:.1f}',                's'],
             ['Usable thermal window', f'{duration["usableThermalWindow"]:.1f}',      's']],
            ['Quantity', 'Value', 'Unit'], title = 'Test design'))

        lines.append('')
        for finding in sampling['findings'] + duration['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'hot_fire_test.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if not self.objective.strip():
            raise TestDesignError(
                'A hot fire needs a stated objective. A test without a question is the failure '
                'this class exists to catch, and it is the one thing here that cannot be checked '
                'automatically, so it is required as an input instead.',
                context = createErrorContext(component = 'HotFireTest'))

        for name, value in (('chamber pressure', self.chamberPressure),
                            ('chamber diameter', self.chamberDiameter),
                            ('duration',         self.duration)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'HotFireTest'))

        if np.isfinite(self.residenceTime) and self.residenceTime <= 0.0:
            raise InvalidInputError(
                f'The residence time must be positive, got {self.residenceTime}.',
                context = createErrorContext(component = 'HotFireTest'))

        if np.isfinite(self.sampleRate) and self.sampleRate <= 0.0:
            raise InvalidInputError(
                f'The sample rate must be positive, got {self.sampleRate}.',
                context = createErrorContext(component = 'HotFireTest'))
