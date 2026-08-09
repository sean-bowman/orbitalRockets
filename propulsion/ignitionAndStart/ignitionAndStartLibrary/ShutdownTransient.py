
# -- ShutdownTransient -- #

'''

Shutdown, which is the harder of the two transients and gets a fraction of the attention.

At start the engine is cold and empty and every event is commanded. At shutdown it is hot, full,
and spinning, and the propellant already downstream of the valves is going to arrive whatever the
controller does. The valves close; the engine does not stop.

Three results are worth taking away.

**The thrust decay rate is set by the vehicle, not by the engine.** The RS-25 limits its oxidiser
preburner valve to 45 per cent per second and its main oxidiser valve to 40, and the stated reason
is an interface control document limit of 700,000 pounds of thrust per second, which is an orbiter
structural limit. The engine could shut down faster. The airframe could not survive it.

**The residual impulse is not the problem. Its scatter is.** A cutoff impulse that is large but
repeatable is trimmed out in the guidance. One that varies from engine to engine and start to start
is a dispersion in the injection, and dispersion is what costs propellant margin.

**Shutdown runs fuel-rich on purpose.** The oxidiser is shut down faster than the fuel so the
mixture ratio falls through the transient, because an oxidiser-rich excursion at temperature is how
turbines and injector faces are destroyed. The RS-25 holds its main fuel valve open for more than a
second after the command for exactly this.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from ignitionUtils import (PROPELLANT_COMBINATIONS, SSME_SHUTDOWN_LIMITS,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, SequenceError)
except ImportError:
    from .ignitionUtils import (PROPELLANT_COMBINATIONS, SSME_SHUTDOWN_LIMITS,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, SequenceError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Effective specific impulse of the propellant that arrives after the valves close, as a fraction
# of the design value.
#
# It burns at a falling and badly controlled mixture ratio, in a chamber whose pressure is
# collapsing, through a nozzle that is separating. Half is a representative figure and it is
# registered as unvalidated; the conclusion this class draws does not depend on it, because the
# conclusion is about scatter rather than magnitude.
TAILOFF_IMPULSE_EFFICIENCY = 0.5    # [-]

# Run-to-run scatter in the residual impulse, as a fraction of the residual itself.
#
# Also unvalidated, and also not load-bearing: it is used to show that the scatter rather than the
# magnitude is what reaches the trajectory, which holds for any value that is not zero.
TAILOFF_SCATTER = 0.15    # [-]

# Newtons per pound force, for the RS-25 decay rate limit which is published in imperial units.
NEWTON_PER_POUND_FORCE = 4.4482216152605    # [N/lbf]

# ------------------------------------------------------------------------------------------------ #
# -- ShutdownTransient -- #
# ------------------------------------------------------------------------------------------------ #

class ShutdownTransient:

    '''

    Thrust decay limits, residual impulse and its scatter, and the mixture ratio excursion.

    '''

    def __init__(self):

        self.combination = ''
        self.thrust      = np.nan
        self.massFlow    = np.nan
        self.exhaustVelocity = np.nan
        self.feedVolume  = np.nan
        self.decayTime   = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `feedVolume` is the liquid volume downstream of the main valves, the dribble volume, which
        arrives in the chamber after the valves are commanded closed.

        `decayTime` is how long the thrust takes to fall to zero. Left unset, it is computed from
        the reference vehicle structural limit rather than assumed.

        '''

        requiredParams = {'combination': str,
                          'thrust':      (int, float),
                          'massFlow':    (int, float),
                          'feedVolume':  (int, float)}

        optionalParams = {'exhaustVelocity': (int, float),
                          'decayTime':       (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise InvalidInputError(
                f'Unknown propellant combination \'{self.combination}\'. Known combinations are '
                f'{sorted(PROPELLANT_COMBINATIONS)}.',
                context = createErrorContext(component = 'ShutdownTransient'))

        if not np.isfinite(self.exhaustVelocity):
            self.exhaustVelocity = self.thrust / self.massFlow

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateDecayLimit(self) -> dict:

        '''

        The minimum decay time the vehicle permits, and where that limit comes from.

        The RS-25 limit is a rate in pounds of thrust per second, set by the orbiter structure. Any
        vehicle has such a limit; what makes this one useful is that it is published, so a decay
        time can be computed rather than assumed.

        '''

        findings = []

        limitInNewtons = SSME_SHUTDOWN_LIMITS['thrustDecayLimit'] * NEWTON_PER_POUND_FORCE

        minimumTime = self.thrust / limitInNewtons

        findings.append(
            f'The reference structural limit is {SSME_SHUTDOWN_LIMITS["thrustDecayLimit"] / 1.0e3:.0f} '
            f'thousand pounds of thrust per second, which is {limitInNewtons / 1.0e6:.2f} MN/s.')

        findings.append(
            f'At {self.thrust / 1.0e3:.0f} kN that permits no faster than {minimumTime * 1000.0:.0f} '
            f'ms to zero thrust.')

        findings.append(
            'The engine is not the constraint. The RS-25 valve closing rates, 45 and 40 per cent '
            'per second, exist to satisfy an interface control document limit that belongs to the '
            'airframe. A shutdown specification that does not name the vehicle it was written '
            'against is not a specification.')

        commanded = self.decayTime if np.isfinite(self.decayTime) else minimumTime

        self.findings = findings

        return {'referenceRateImperial': SSME_SHUTDOWN_LIMITS['thrustDecayLimit'],
                'referenceRate':         limitInNewtons,
                'minimumDecayTime':      minimumTime,
                'decayTime':             commanded,
                'withinLimit':           bool(commanded >= minimumTime),
                'findings':              findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateResidualImpulse(self) -> dict:

        '''

        The impulse delivered after the shutdown command, and the part of it that reaches the
        trajectory as a dispersion.

        Two contributions. The thrust decaying through its ramp, which is roughly half the steady
        thrust over the decay time. And the dribble volume, the liquid already downstream of the
        valves, which burns badly and produces a fraction of its design impulse.

        '''

        findings = []

        decay = self.calculateDecayLimit()

        rampImpulse = 0.5 * self.thrust * decay['decayTime']

        entry = PROPELLANT_COMBINATIONS[self.combination]

        mixtureRatio = entry['mixtureRatio']

        bulkDensity = ((mixtureRatio * entry['oxidiserDensity'] + entry['fuelDensity'])
                       / (mixtureRatio + 1.0))

        dribbleMass = self.feedVolume * bulkDensity

        dribbleImpulse = (dribbleMass * self.exhaustVelocity * TAILOFF_IMPULSE_EFFICIENCY)

        total = rampImpulse + dribbleImpulse

        scatter = total * TAILOFF_SCATTER

        # what the scatter is worth as a velocity error on a representative upper stage mass
        findings.append(
            f'The thrust ramp contributes {rampImpulse / 1.0e3:.1f} kN s and the dribble volume '
            f'{dribbleImpulse / 1.0e3:.1f} kN s, for {total / 1.0e3:.1f} kN s after the command.')

        findings.append(
            f'{dribbleMass:.1f} kg of propellant is downstream of the valves when they close, and '
            f'it is going to arrive whatever the controller does.')

        findings.append(
            f'The magnitude is trimmed out in guidance. The **scatter**, about '
            f'{scatter / 1.0e3:.2f} kN s, is not, because guidance cannot trim what it cannot '
            f'predict. That is the number that reaches the injection accuracy.')

        return {'rampImpulse':    rampImpulse,
                'dribbleMass':    dribbleMass,
                'dribbleImpulse': dribbleImpulse,
                'totalImpulse':   total,
                'scatter':        scatter,
                'dribbleFraction': dribbleImpulse / total,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def checkShutdownOrder(self, oxidiserCloseTime: float, fuelCloseTime: float) -> dict:

        '''

        Check that the oxidiser leads the fuel closed, which is the one ordering rule shutdown has.

        An oxidiser-rich excursion at combustion temperature attacks everything it touches: the
        injector face, the throat, and on a staged combustion engine the turbine. Running fuel-rich
        through the transient costs a little unburned fuel and protects the hardware, and every
        large engine does it.

        This is refused rather than reported, on the same grounds as the start sequence ordering
        check. An engine that shuts down oxidiser-rich is not a slightly worse engine.

        '''

        if fuelCloseTime <= oxidiserCloseTime:
            raise SequenceError(
                f'The fuel valve closes at {fuelCloseTime:.2f} s and the oxidiser at '
                f'{oxidiserCloseTime:.2f} s, so the shutdown runs oxidiser-rich. That is how '
                f'injector faces and turbines are destroyed, and it is refused rather than '
                f'reported. The RS-25 holds its main fuel valve open for more than a second past '
                f'the command for exactly this reason.',
                context = createErrorContext(component = 'ShutdownTransient'))

        lead = fuelCloseTime - oxidiserCloseTime

        reference = SSME_SHUTDOWN_LIMITS['fuelValveHoldTime']

        return {'fuelLead':      lead,
                'referenceLead': reference,
                'fuelRich':      True,
                'meetsReference': bool(lead >= reference)}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full shutdown transient report.
        '''

        decay    = self.calculateDecayLimit()
        residual = self.calculateResidualImpulse()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  SHUTDOWN TRANSIENT: {self.combination} at {self.thrust / 1.0e3:.0f} kN')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Reference decay limit', f'{decay["referenceRate"] / 1.0e6:.2f}',        'MN/s'],
             ['Minimum decay time',    f'{decay["minimumDecayTime"] * 1000.0:.0f}',    'ms'],
             ['Ramp impulse',          f'{residual["rampImpulse"] / 1.0e3:.1f}',       'kN s'],
             ['Dribble mass',          f'{residual["dribbleMass"]:.1f}',               'kg'],
             ['Dribble impulse',       f'{residual["dribbleImpulse"] / 1.0e3:.1f}',    'kN s'],
             ['Total residual',        f'{residual["totalImpulse"] / 1.0e3:.1f}',      'kN s'],
             ['Scatter',               f'{residual["scatter"] / 1.0e3:.2f}',           'kN s']],
            ['Quantity', 'Value', 'Unit'], title = 'Shutdown'))

        lines.append('')
        for finding in decay['findings'] + residual['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'shutdown_transient.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('thrust', self.thrust), ('massFlow', self.massFlow),
                            ('exhaustVelocity', self.exhaustVelocity)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'ShutdownTransient'))

        if self.feedVolume < 0.0:
            raise InvalidInputError(
                f'The feed volume cannot be negative, got {self.feedVolume}.',
                context = createErrorContext(component = 'ShutdownTransient'))

        if np.isfinite(self.decayTime) and self.decayTime <= 0.0:
            raise InvalidInputError(
                f'The decay time must be positive, got {self.decayTime}.',
                context = createErrorContext(component = 'ShutdownTransient'))
