
# -- AscentTrajectory -- #

'''

The delta-V budget for reaching orbit, and the thrust to weight that minimises it.

Orbital velocity at low Earth orbit is about 7660 m/s and an easterly launch from Cape Canaveral is
handed about 408 of it by the Earth's rotation. Everything between that and the roughly 9300 m/s a
vehicle actually has to deliver is loss, and the losses are not independent of the design.

**Gravity loss falls with liftoff thrust to weight and drag loss rises with it**, which gives the
total a minimum. That minimum turns out to sit at a thrust to weight of about two and a half, which
nothing flies, because gravity loss falls faster than drag loss rises across the whole practical
range.

So the loss budget sets a floor rather than a target. Below about 1.2 the gravity loss becomes
unaffordable; above it the choice is decided by engine mass, engine count and engine-out
capability, and the loss budget has nothing to say about any of them. Flying at 1.35 rather than at
the loss optimum costs about 300 m/s and buying it back would take nearly twice the liftoff thrust.

This class computes the budget from a loss model rather than integrating a trajectory. That is a
deliberate limit: a real ascent is a trajectory optimisation with a steering law, atmospheric data
and a vehicle aerodynamic model, and none of those is in this repository. What is here is the
budget that such an optimisation would have to beat, and the shape of its dependence on the one
vehicle parameter that dominates it.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from vehicleUtils import (STANDARD_GRAVITY, LEO_ORBITAL_VELOCITY, EARTH_ROTATION_ASSIST,
                              ASCENT_LOSSES, LIFTOFF_THRUST_TO_WEIGHT_FLOOR,
                              LIFTOFF_THRUST_TO_WEIGHT_CEILING,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, VehicleArchitectureError)
except ImportError:
    from .vehicleUtils import (STANDARD_GRAVITY, LEO_ORBITAL_VELOCITY, EARTH_ROTATION_ASSIST,
                               ASCENT_LOSSES, LIFTOFF_THRUST_TO_WEIGHT_FLOOR,
                               LIFTOFF_THRUST_TO_WEIGHT_CEILING,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, VehicleArchitectureError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Reference thrust to weight the loss correlations are anchored at.
REFERENCE_THRUST_TO_WEIGHT = 1.35    # [-]

# Gravity loss scales roughly with the time spent climbing against gravity, which falls as the
# vehicle accelerates harder. A vehicle at twice the thrust to weight spends roughly half as long
# below orbital velocity, so the loss scales close to the inverse.
#
# This is a correlation shape rather than a derivation, and it is registered as unvalidated. What it
# is used for is the LOCATION of the minimum, which is robust to the exponent within reason.
GRAVITY_LOSS_EXPONENT = -1.0    # [-]

# Drag loss rises with thrust to weight, because a vehicle that accelerates harder is faster deeper
# in the atmosphere. It rises more gently than gravity loss falls, and from a base five times
# smaller, which is why the stationary point lands far above the practical range rather than inside
# it. That result is the point of optimiseThrustToWeight and it is not what was expected of it.
DRAG_LOSS_EXPONENT = 1.2    # [-]

# Reference losses at the reference thrust to weight, taken at the middle of the bands.
REFERENCE_GRAVITY_LOSS = 1250.0    # [m/s]
REFERENCE_DRAG_LOSS    = 250.0     # [m/s]
REFERENCE_STEERING_LOSS = 100.0    # [m/s]

# ------------------------------------------------------------------------------------------------ #
# -- AscentTrajectory -- #
# ------------------------------------------------------------------------------------------------ #

class AscentTrajectory:

    '''

    Delta-V budget to orbit, and its dependence on liftoff thrust to weight.

    '''

    def __init__(self):

        self.targetVelocity     = np.nan
        self.latitude           = np.nan
        self.launchAzimuth      = np.nan
        self.thrustToWeight     = np.nan
        self.residualVelocity   = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `targetVelocity` defaults to circular low Earth orbit. `latitude` and `launchAzimuth`
        together set the rotational assist, which is the only free delta-V in the budget.

        '''

        requiredParams = {'thrustToWeight': (int, float)}

        optionalParams = {'targetVelocity':   (int, float),
                          'latitude':         (int, float),
                          'launchAzimuth':    (int, float),
                          'residualVelocity': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.targetVelocity):
            self.targetVelocity = LEO_ORBITAL_VELOCITY

        if not np.isfinite(self.latitude):
            self.latitude = 28.5

        if not np.isfinite(self.launchAzimuth):
            self.launchAzimuth = 90.0

        if not np.isfinite(self.residualVelocity):
            self.residualVelocity = 0.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def rotationAssist(self) -> float:

        '''

        The velocity the Earth's rotation contributes, from the launch site latitude and the
        azimuth flown.

        The full equatorial surface speed is about 465 m/s. It is reduced by the cosine of the
        latitude, and only the easterly component of the azimuth counts.

        '''

        equatorial = EARTH_ROTATION_ASSIST / np.cos(np.radians(28.5))

        return float(equatorial * np.cos(np.radians(self.latitude))
                     * np.sin(np.radians(self.launchAzimuth)))

    # -------------------------------------------------------------------------------------------- #

    def calculateLosses(self, thrustToWeight: float = None) -> dict:

        '''

        The three ascent losses at a given liftoff thrust to weight.

        Gravity loss falls with thrust to weight and drag loss rises with it. Steering loss is
        treated as independent, which is a simplification: it is really a trajectory design outcome
        and it is the smallest of the three.

        '''

        if thrustToWeight is None:
            thrustToWeight = self.thrustToWeight

        ratio = thrustToWeight / REFERENCE_THRUST_TO_WEIGHT

        gravity = REFERENCE_GRAVITY_LOSS * ratio ** GRAVITY_LOSS_EXPONENT
        drag    = REFERENCE_DRAG_LOSS * ratio ** DRAG_LOSS_EXPONENT

        total = gravity + drag + REFERENCE_STEERING_LOSS

        return {'thrustToWeight': thrustToWeight,
                'gravity':        gravity,
                'drag':           drag,
                'steering':       REFERENCE_STEERING_LOSS,
                'total':          total}

    # -------------------------------------------------------------------------------------------- #

    def calculateBudget(self) -> dict:

        '''

        The full delta-V budget: what the orbit needs, what the Earth contributes, and what the
        losses take back.

        '''

        findings = []

        losses = self.calculateLosses()

        assist = self.rotationAssist()

        required = self.targetVelocity - assist + losses['total'] + self.residualVelocity

        findings.append(
            f'Circular orbit needs {self.targetVelocity:.0f} m/s and the Earth contributes '
            f'{assist:.0f} of it from {self.latitude:.1f} degrees at an azimuth of '
            f'{self.launchAzimuth:.0f}.')

        findings.append(
            f'Losses add {losses["total"]:.0f} m/s: {losses["gravity"]:.0f} gravity, '
            f'{losses["drag"]:.0f} drag, {losses["steering"]:.0f} steering.')

        findings.append(
            f'So the vehicle has to deliver {required:.0f} m/s, which is '
            f'{required / self.targetVelocity - 1.0:.1%} more than the orbit itself needs.')

        findings.append(
            'The rotational assist is the only free term in that budget and it is the reason '
            'launch sites are near the equator and launches go east.')

        self.findings = findings

        return {'orbitalVelocity':  self.targetVelocity,
                'rotationAssist':   assist,
                'losses':           losses,
                'residual':         self.residualVelocity,
                'requiredDeltaV':   required,
                'lossFraction':     losses['total'] / required,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def optimiseThrustToWeight(self, lower: float = None, upper: float = None,
                               points: int = 61) -> dict:

        '''

        The liftoff thrust to weight that minimises the loss total, and where real vehicles sit
        relative to it.

        **The loss-minimising thrust to weight is far above what anything flies**, and that is the
        result. With gravity loss falling as the inverse and drag rising as a fractional power from
        a much smaller base, the minimum of

            G (x/x0)^-1 + D (x/x0)^1.2

        sits where `x/x0 = (G / 1.2 D)^(1/2.2)`, which for a representative loss split is around a
        thrust to weight of two and a half. No launch vehicle flies there.

        So the loss budget does not choose the liftoff thrust to weight. It sets a floor, below
        which the gravity loss becomes unaffordable, and everything above that floor is decided by
        engine mass, engine count and engine-out capability. The penalty for flying at 1.35 rather
        than at the loss optimum is real and it is smaller than the engines that would buy it.

        '''

        if lower is None:
            lower = LIFTOFF_THRUST_TO_WEIGHT_FLOOR

        if upper is None:
            upper = LIFTOFF_THRUST_TO_WEIGHT_CEILING

        if not 0.0 < lower < upper:
            raise InvalidInputError(
                f'The thrust to weight sweep needs 0 < lower < upper, got {lower} and {upper}.',
                context = createErrorContext(component = 'AscentTrajectory'))

        findings = []

        sweep = np.linspace(lower, upper, points)

        totals = np.array([self.calculateLosses(value)['total'] for value in sweep])

        # the analytic stationary point, which is where the two loss derivatives balance
        exponentSpan = DRAG_LOSS_EXPONENT - GRAVITY_LOSS_EXPONENT

        optimalRatio = ((-GRAVITY_LOSS_EXPONENT * REFERENCE_GRAVITY_LOSS)
                        / (DRAG_LOSS_EXPONENT * REFERENCE_DRAG_LOSS)) ** (1.0 / exponentSpan)

        optimum = float(REFERENCE_THRUST_TO_WEIGHT * optimalRatio)

        minimum = self.calculateLosses(optimum)['total']

        atDesign = self.calculateLosses(self.thrustToWeight)['total']

        penalty = atDesign - minimum

        insideBand = bool(lower <= optimum <= upper)

        findings.append(
            f'The loss total is minimised at a thrust to weight of {optimum:.2f}, at '
            f'{minimum:.0f} m/s.')

        if not insideBand:
            findings.append(
                f'**That is outside the band real vehicles fly, {lower:.1f} to {upper:.1f}, and '
                f'nothing flies there.** Gravity loss falls faster with thrust to weight than drag '
                f'loss rises, so the loss budget alone always wants more thrust than anyone buys.')

        findings.append(
            f'At the design point of {self.thrustToWeight:.2f} the losses are {atDesign:.0f} m/s, '
            f'{penalty:.0f} m/s worse than the loss optimum. Closing that gap would take '
            f'{optimum / self.thrustToWeight:.1f} times the liftoff thrust.')

        findings.append(
            'So the loss budget sets a floor and not a target. Below about 1.2 the gravity loss '
            'becomes unaffordable; above it the choice is decided by engine mass, engine count and '
            'engine-out capability, and this budget has nothing to say about any of them.')

        self.findings = findings

        return {'sweep':          sweep,
                'totals':         totals,
                'optimum':        optimum,
                'minimum':        minimum,
                'lossAtDesign':   atDesign,
                'penalty':        penalty,
                'thrustMultipleToReachOptimum': optimum / self.thrustToWeight,
                'optimumInsidePracticalBand': insideBand,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full ascent budget report.
        '''

        budget = self.calculateBudget()
        sweep  = self.optimiseThrustToWeight()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ASCENT BUDGET: to {self.targetVelocity:.0f} m/s at a thrust to weight of '
                     f'{self.thrustToWeight:.2f}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Orbital velocity',  f'{budget["orbitalVelocity"]:.0f}',        'm/s'],
             ['Rotation assist',   f'-{budget["rotationAssist"]:.0f}',        'm/s'],
             ['Gravity loss',      f'+{budget["losses"]["gravity"]:.0f}',     'm/s'],
             ['Drag loss',         f'+{budget["losses"]["drag"]:.0f}',        'm/s'],
             ['Steering loss',     f'+{budget["losses"]["steering"]:.0f}',    'm/s'],
             ['Required',          f'{budget["requiredDeltaV"]:.0f}',         'm/s']],
            ['Term', 'Value', 'Unit'], title = 'Delta-V budget'))

        lines.append('')
        lines.append(formatReportTable(
            [['Loss optimum',      f'{sweep["optimum"]:.2f}',                 ''],
             ['Minimum loss',      f'{sweep["minimum"]:.0f}',                 'm/s'],
             ['Loss at design',    f'{sweep["lossAtDesign"]:.0f}',            'm/s'],
             ['Penalty vs optimum', f'{sweep["penalty"]:.0f}',                 'm/s'],
             ['Thrust multiple to reach it',
              f'{sweep["thrustMultipleToReachOptimum"]:.1f}',                  'x']],
            ['Quantity', 'Value', 'Unit'], title = 'Thrust to weight'))

        lines.append('')
        for finding in budget['findings'] + sweep['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'ascent_trajectory.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.thrustToWeight <= 1.0:
            raise VehicleArchitectureError(
                f'The liftoff thrust to weight is {self.thrustToWeight}, which is at or below one. '
                f'The vehicle does not leave the pad, and computing an ascent loss budget for it '
                f'would produce a number that looks like a result.',
                context = createErrorContext(component = 'AscentTrajectory'))

        if self.targetVelocity <= 0.0:
            raise InvalidInputError(
                f'The target velocity must be positive, got {self.targetVelocity}.',
                context = createErrorContext(component = 'AscentTrajectory'))

        if not -90.0 <= self.latitude <= 90.0:
            raise InvalidInputError(
                f'The latitude must lie between -90 and 90 degrees, got {self.latitude}.',
                context = createErrorContext(component = 'AscentTrajectory'))

        if not 0.0 <= self.launchAzimuth <= 360.0:
            raise InvalidInputError(
                f'The launch azimuth must lie between 0 and 360 degrees, got '
                f'{self.launchAzimuth}.',
                context = createErrorContext(component = 'AscentTrajectory'))

        if self.residualVelocity < 0.0:
            raise InvalidInputError(
                f'The residual velocity cannot be negative, got {self.residualVelocity}.',
                context = createErrorContext(component = 'AscentTrajectory'))
