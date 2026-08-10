
# -- DeploymentKinematics -- #

'''

A hinged deployable driven by a torsion spring, and the latch it arrives at.

The spring has to be strong enough to deploy against the worst-case resisting torque, which is a
[MechanismActuator](MechanismActuator.py) margin problem. This class is about what happens next:
the panel accelerates through its travel, arrives at the latch, and stops.

**The latch impact energy scales with the square of the arrival rate.** Halving the deployment time
quadruples the energy the latch and the hinge have to absorb, so a spring sized generously for
margin arrives violently, and the two requirements pull against each other directly.

A damper is what resolves that. It costs deployment time and it costs a component that has to work
after storage at temperature, and NASA-STD-5017B lists damper drag among the resisting torques a
margin calculation has to include, so **the damper that protects the latch also eats the margin
that justified the spring.**

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from mechanismUtils import (applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, MechanismsAndSeparationError)
except ImportError:
    from .mechanismUtils import (applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, MechanismsAndSeparationError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Integration steps across the deployment travel.
INTEGRATION_STEPS = 2000

# Damping ratio above which the deployment is treated as controlled rather than free.
CONTROLLED_DAMPING_RATIO = 0.3    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- DeploymentKinematics -- #
# ------------------------------------------------------------------------------------------------ #

class DeploymentKinematics:

    '''

    Deployment time, arrival rate and latch impact energy for a spring-driven hinged deployable.

    '''

    def __init__(self):

        self.springTorque   = np.nan
        self.springRate     = np.nan
        self.inertia        = np.nan
        self.travel         = np.nan
        self.resistingTorque = np.nan
        self.dampingCoefficient = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `springTorque` is the torque at the stowed position and `springRate` is how fast it falls
        off with angle, because a torsion spring unwinds as it deploys and arrives weakest.

        `travel` is the deployment angle in radians.

        '''

        requiredParams = {'springTorque': (int, float),
                          'inertia':      (int, float),
                          'travel':       (int, float)}

        optionalParams = {'springRate':          (int, float),
                          'resistingTorque':     (int, float),
                          'dampingCoefficient':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.springRate):
            self.springRate = 0.0

        if not np.isfinite(self.resistingTorque):
            self.resistingTorque = 0.0

        if not np.isfinite(self.dampingCoefficient):
            self.dampingCoefficient = 0.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def netTorque(self, angle: float, rate: float) -> float:

        '''
        Net accelerating torque at an angle and rate: the spring falling off with travel, less the
        constant resistance and the viscous damper.
        '''

        return (self.springTorque - self.springRate * angle
                - self.resistingTorque - self.dampingCoefficient * rate)

    # -------------------------------------------------------------------------------------------- #

    def deploy(self) -> dict:

        '''

        Integrate the deployment and report the arrival rate and time.

        A simple explicit integration is adequate here: the system is smooth, the step count is
        large, and the result is compared against an undamped closed form as a check.

        '''

        step = self.travel / INTEGRATION_STEPS

        angle = 0.0
        rate  = 0.0
        time  = 0.0

        stalled = False

        for _ in range(INTEGRATION_STEPS):

            torque = self.netTorque(angle, rate)

            if torque <= 0.0 and rate <= 0.0:
                stalled = True
                break

            acceleration = torque / self.inertia

            # advance in angle rather than time, which keeps the step size uniform across travel
            newRateSquared = rate ** 2 + 2.0 * acceleration * step

            if newRateSquared <= 0.0:
                stalled = True
                break

            newRate = np.sqrt(newRateSquared)

            time  += step / (0.5 * (rate + newRate)) if (rate + newRate) > 0.0 else 0.0
            rate   = newRate
            angle += step

        if stalled:
            raise MechanismsAndSeparationError(
                f'The deployable stalls at {np.degrees(angle):.1f} degrees of '
                f'{np.degrees(self.travel):.1f}. The spring torque has fallen to '
                f'{self.springTorque - self.springRate * angle:.2f} N m against a resistance of '
                f'{self.resistingTorque:.2f}. **A deployable that stops halfway is a failed '
                f'mission**, and a spring sized on its stowed torque rather than its torque at the '
                f'end of travel is the usual cause: a torsion spring arrives weakest.',
                context = createErrorContext(component = 'DeploymentKinematics'))

        # undamped, constant-torque closed form, as a check on the integration
        meanTorque = self.springTorque - 0.5 * self.springRate * self.travel - self.resistingTorque

        closedFormRate = (np.sqrt(2.0 * meanTorque * self.travel / self.inertia)
                          if meanTorque > 0.0 else np.nan)

        return {'arrivalRate':     rate,
                'arrivalRateDegrees': float(np.degrees(rate)),
                'deploymentTime':  time,
                'closedFormRate':  closedFormRate,
                'meanTorque':      meanTorque,
                'stalled':         False}

    # -------------------------------------------------------------------------------------------- #

    def latchImpact(self) -> dict:

        '''

        The energy the latch has to absorb, and how it scales.

        The panel arrives with kinetic energy one half I omega squared, and all of it goes into the
        latch, the hinge and the structure behind them in the time it takes to stop.

        **The scaling is the point.** Energy goes as the square of the arrival rate, so a spring
        chosen for a comfortable deployment margin arrives with far more energy than one chosen to
        just deploy, and the latch pays for the margin.

        '''

        findings = []

        deployment = self.deploy()

        energy = 0.5 * self.inertia * deployment['arrivalRate'] ** 2

        findings.append(
            f'The panel arrives at {deployment["arrivalRateDegrees"]:.1f} degrees per second after '
            f'{deployment["deploymentTime"]:.2f} s, carrying {energy:.1f} J.')

        findings.append(
            'That energy goes as the square of the arrival rate, so the latch pays quadratically '
            'for a spring chosen with generous deployment margin. The two requirements pull '
            'directly against each other and a damper is what resolves them.')

        if self.dampingCoefficient > 0.0:

            critical = 2.0 * np.sqrt(self.springRate * self.inertia) if self.springRate > 0.0 \
                       else np.nan

            ratio = (self.dampingCoefficient / critical if np.isfinite(critical) and critical > 0.0
                     else np.nan)

            findings.append(
                f'The damper takes {self.dampingCoefficient:.3f} N m s per radian, a damping ratio '
                f'of {ratio:.2f}.' if np.isfinite(ratio) else
                f'The damper takes {self.dampingCoefficient:.3f} N m s per radian.')

            findings.append(
                'NASA-STD-5017B lists damper drag among the resisting torques a margin calculation '
                'has to include, so the damper that protects the latch also eats the margin that '
                'justified the spring.')
        else:
            findings.append(
                'There is no damper, so the arrival rate is whatever the spring produces and the '
                'latch absorbs all of it.')

        self.findings = findings

        return {'arrivalRate':    deployment['arrivalRate'],
                'deploymentTime': deployment['deploymentTime'],
                'impactEnergy':   energy,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeDamper(self, energyLimit: float) -> dict:

        '''

        The damping coefficient that brings the latch impact energy under a limit.

        Solved by bisection on the coefficient, because the deployment integration has no closed
        form once damping is present.

        '''

        if energyLimit <= 0.0:
            raise InvalidInputError(
                f'The energy limit must be positive, got {energyLimit}.',
                context = createErrorContext(component = 'DeploymentKinematics'))

        original = self.dampingCoefficient

        try:
            self.dampingCoefficient = 0.0

            undamped = self.latchImpact()['impactEnergy']

            if undamped <= energyLimit:
                return {'required':      0.0,
                        'undampedEnergy': undamped,
                        'energyLimit':   energyLimit,
                        'damperNeeded':  False}

            low, high = 0.0, 1.0

            # grow the bracket until the damper is strong enough or the mechanism stalls
            for _ in range(60):

                self.dampingCoefficient = high

                try:
                    if self.latchImpact()['impactEnergy'] <= energyLimit:
                        break
                except MechanismsAndSeparationError:
                    break

                high *= 2.0

            else:
                raise MechanismsAndSeparationError(
                    'No damping coefficient brings the impact energy under the limit before the '
                    'mechanism stalls. The spring is too strong for the latch and the answer is a '
                    'weaker spring or a stronger latch rather than more damping.',
                    context = createErrorContext(component = 'DeploymentKinematics'))

            for _ in range(80):

                middle = 0.5 * (low + high)

                self.dampingCoefficient = middle

                try:
                    energy = self.latchImpact()['impactEnergy']
                except MechanismsAndSeparationError:
                    high = middle
                    continue

                if energy > energyLimit:
                    low = middle
                else:
                    high = middle

            required = high

        finally:
            self.dampingCoefficient = original

        return {'required':       required,
                'undampedEnergy': undamped,
                'energyLimit':    energyLimit,
                'damperNeeded':   True,
                'energyReduction': 1.0 - energyLimit / undamped}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full deployment report.
        '''

        impact = self.latchImpact()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  DEPLOYMENT: {np.degrees(self.travel):.0f} degrees of travel, '
                     f'{self.inertia:.2f} kg m^2')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Spring torque, stowed', f'{self.springTorque:.3f}',                    'N m'],
             ['Spring rate',           f'{self.springRate:.3f}',                      'N m/rad'],
             ['Resisting torque',      f'{self.resistingTorque:.3f}',                 'N m'],
             ['Damping',               f'{self.dampingCoefficient:.3f}',              'N m s/rad'],
             ['Deployment time',       f'{impact["deploymentTime"]:.2f}',             's'],
             ['Arrival rate',          f'{np.degrees(impact["arrivalRate"]):.1f}',    'deg/s'],
             ['Latch impact energy',   f'{impact["impactEnergy"]:.2f}',               'J']],
            ['Quantity', 'Value', 'Unit'], title = 'Deployment'))

        lines.append('')
        for finding in impact['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'deployment_kinematics.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('spring torque', self.springTorque),
                            ('inertia',       self.inertia),
                            ('travel',        self.travel)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'DeploymentKinematics'))

        if self.travel > 2.0 * np.pi:
            raise InvalidInputError(
                f'The travel is {np.degrees(self.travel):.0f} degrees, which is more than a full '
                f'turn. Travel is expected in radians and this looks like degrees.',
                context = createErrorContext(component = 'DeploymentKinematics'))

        for name, value in (('spring rate',        self.springRate),
                            ('resisting torque',   self.resistingTorque),
                            ('damping coefficient', self.dampingCoefficient)):
            if value < 0.0:
                raise InvalidInputError(
                    f'The {name} cannot be negative, got {value}.',
                    context = createErrorContext(component = 'DeploymentKinematics'))
