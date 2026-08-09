
# -- SizingLoop -- #

'''

Closing a vehicle, and tracing one number from a feed line all the way to the payload.

Every other class in this domain takes the structural coefficient as an input. That is the number
the whole architecture turns on and it is the one nobody can supply, because it is an output of the
tank, which is an output of the tank pressure, which is an output of the feed system. So the sizing
is circular and it has to be iterated.

    guess a dry mass
        -> stage propellant from the rocket equation
        -> tank volume from the propellant
        -> tank wall from the pressure and the volume
        -> tank mass, plus the fixed masses
        -> a new dry mass

That loop either converges to a vehicle or it diverges, and a vehicle that diverges does not close.
**This class raises when it diverges rather than returning the last iterate**, because the last
iterate of a diverging loop looks exactly like a converged answer.

**The mass chain is the reason this class crosses domains.** It imports the pressure vessel model
from aerospaceStructures rather than reimplementing a tank, so that a change in the structures
allowables propagates into a payload without anyone reconciling two tank models. That is a
deliberate coupling and it is the only one in this repository that spans three domains.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os
import sys

import numpy as np

try:
    from vehicleUtils import (STANDARD_GRAVITY, structuralCoefficient,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, ClosureError)
    from StagedVehicle import StagedVehicle
except ImportError:
    from .vehicleUtils import (STANDARD_GRAVITY, structuralCoefficient,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, ClosureError)
    from .StagedVehicle import StagedVehicle

# The structures library owns the tank. Importing it here rather than reimplementing a shell mass
# is the whole point of the mass chain: one pressure vessel model, and a change in its allowables
# reaches the payload without anybody reconciling two of them.
_STRUCTURES = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'aerospaceStructures', 'aerospaceStructuresLibrary')

if _STRUCTURES not in sys.path:
    sys.path.insert(0, _STRUCTURES)

from PressureVessel import PressureVessel

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

MAXIMUM_ITERATIONS = 100
CONVERGENCE_TOLERANCE = 1.0e-6    # [-] relative change in dry mass

# A diverging loop is detected by the dry mass growing rather than settling. Two consecutive
# increases of more than this fraction is taken as divergence rather than slow convergence.
DIVERGENCE_GROWTH = 0.05    # [-]

# Ullage volume as a fraction of the propellant volume, which the tank has to enclose and does not
# hold propellant in.
ULLAGE_FRACTION = 0.03    # [-]

# Everything in a stage that is not tank: engines, thrust structure, avionics, feed lines,
# separation hardware, and the skirts. Carried as a fraction of propellant mass because that is how
# a conceptual estimate is made before any of it exists.
#
# Representative and registered as unvalidated. The sensitivity of the closed vehicle to this
# number is reported rather than hidden, because it is doing as much work as the tank model.
NON_TANK_DRY_FRACTION = 0.035    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- SizingLoop -- #
# ------------------------------------------------------------------------------------------------ #

class SizingLoop:

    '''

    Iterates tank, mass and performance to a closed vehicle, and traces the mass chain through it.

    '''

    def __init__(self):

        self.payloadMass    = np.nan
        self.targetDeltaV   = np.nan
        self.stages         = []
        self.tankRadius     = np.nan
        self.tankPressure   = np.nan
        self.tankMaterial   = ''
        self.propellantDensity = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `tankPressure` is the operating pressure the tank has to hold, and it is the input the mass
        chain starts from. It comes from the engine inlet requirement plus the feed system pressure
        drop, both of which belong to fluidSystems.

        `stages` needs a `specificImpulse` and a `deltaVFraction` per stage. The structural
        coefficient is deliberately NOT an input here, because computing it is what this class is
        for.

        '''

        requiredParams = {'payloadMass':   (int, float),
                          'targetDeltaV':  (int, float),
                          'stages':        list,
                          'tankRadius':    (int, float),
                          'tankPressure':  (int, float)}

        optionalParams = {'tankMaterial':      str,
                          'propellantDensity': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.tankMaterial:
            self.tankMaterial = '2219-T87'

        if not np.isfinite(self.propellantDensity):
            # bulk density of LOX/RP-1 at a mixture ratio of 2.56, from the propulsion hub
            self.propellantDensity = 1030.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def sizeTank(self, propellantMass: float) -> dict:

        '''

        A tank for a given propellant load, at the operating pressure, using the structures model.

        The length is solved for rather than assumed: the radius is a configuration choice and the
        volume follows from the propellant, so the barrel length is what is left.

        '''

        if propellantMass <= 0.0:
            raise InvalidInputError(
                f'The propellant mass must be positive to size a tank, got {propellantMass}.',
                context = createErrorContext(component = 'SizingLoop'))

        requiredVolume = propellantMass / self.propellantDensity * (1.0 + ULLAGE_FRACTION)

        vessel = PressureVessel()
        vessel.setInputs({'radius':            self.tankRadius,
                          'operatingPressure': self.tankPressure,
                          'cylindricalLength': 1.0,
                          'material':          self.tankMaterial})

        # the domes contribute a fixed volume, so the barrel makes up the difference
        domeVolume = vessel.calculateDomeGeometry()['domeVolumeBothEnds']

        barrelVolume = requiredVolume - domeVolume

        if barrelVolume <= 0.0:
            raise ClosureError(
                f'A tank of radius {self.tankRadius:.2f} m has {domeVolume:.2f} m^3 in its domes '
                f'alone, which already exceeds the {requiredVolume:.2f} m^3 this stage needs. The '
                f'tank is too fat for its propellant load and the radius is the thing to change.',
                context = createErrorContext(component = 'SizingLoop'))

        length = barrelVolume / (np.pi * self.tankRadius ** 2)

        vessel.setInputs({'radius':            self.tankRadius,
                          'operatingPressure': self.tankPressure,
                          'cylindricalLength': length,
                          'material':          self.tankMaterial})

        sized = vessel.calculateVolumeAndMass()

        return {'propellantMass':  propellantMass,
                'requiredVolume':  requiredVolume,
                'barrelLength':    length,
                'overallLength':   sized['overallLength'],
                'wallThickness':   sized['thickness'],
                'tankMass':        sized['shellMass'],
                'enclosedVolume':  sized['totalVolume'],
                'tankMassFraction': sized['shellMass'] / propellantMass}

    # -------------------------------------------------------------------------------------------- #

    def close(self) -> dict:

        '''

        Iterate to a closed vehicle, or raise.

        The loop starts from an optimistic structural coefficient and lets the tank model push it
        wherever it goes. Starting optimistic matters: a loop started pessimistic can converge to a
        heavier fixed point than one started optimistic when the tank model is nonlinear, and the
        optimistic start is the one that finds the lighter solution if one exists.

        '''

        findings = []

        coefficients = [0.05 for _ in self.stages]

        history = []

        previousDry = None
        growths     = 0

        for iteration in range(MAXIMUM_ITERATIONS):

            vehicle = StagedVehicle()
            vehicle.setInputs({
                'stages': [{'specificImpulse': stage['specificImpulse'],
                            'structuralCoefficient': coefficients[index]}
                           for index, stage in enumerate(self.stages)],
                'payloadMass':  self.payloadMass,
                'targetDeltaV': self.targetDeltaV})

            split = [stage['deltaVFraction'] * self.targetDeltaV for stage in self.stages]

            sized = vehicle.sizeToDeltaV(split)

            tanks    = []
            newCoefficients = []

            for index, entry in enumerate(sized['stages']):

                tank = self.sizeTank(entry['propellantMass'])

                nonTank = NON_TANK_DRY_FRACTION * entry['propellantMass']

                dry = tank['tankMass'] + nonTank

                tanks.append({**tank, 'nonTankMass': nonTank, 'dryMass': dry})

                newCoefficients.append(dry / (dry + entry['propellantMass']))

            totalDry = sum(entry['dryMass'] for entry in tanks)

            history.append({'iteration':    iteration,
                            'coefficients': list(coefficients),
                            'dryMass':      totalDry,
                            'liftoffMass':  sized['liftoffMass']})

            if previousDry is not None:

                change = (totalDry - previousDry) / previousDry

                if abs(change) < CONVERGENCE_TOLERANCE:

                    findings.append(
                        f'Converged in {iteration + 1} iterations to a structural coefficient of '
                        f'{", ".join(f"{value:.4f}" for value in newCoefficients)}.')

                    findings.append(
                        f'The tank is {tanks[0]["tankMassFraction"]:.1%} of the first stage '
                        f'propellant mass and its wall is '
                        f'{tanks[0]["wallThickness"] * 1000.0:.2f} mm at '
                        f'{self.tankPressure / 1.0e6:.2f} MPa.')

                    self.findings = findings

                    return {'converged':    True,
                            'iterations':   iteration + 1,
                            'coefficients': newCoefficients,
                            'stages':       sized['stages'],
                            'tanks':        tanks,
                            'liftoffMass':  sized['liftoffMass'],
                            'payloadMass':  self.payloadMass,
                            'payloadFraction': sized['payloadFraction'],
                            'dryMass':      totalDry,
                            'history':      history,
                            'findings':     findings}

                if change > DIVERGENCE_GROWTH:
                    growths += 1
                else:
                    growths = 0

                if growths >= 2:
                    raise ClosureError(
                        f'The sizing loop is diverging: the dry mass grew by {change:.1%} on two '
                        f'consecutive iterations and is now {totalDry:.0f} kg. **This vehicle does '
                        f'not close.** Each iteration makes the tanks heavier, which needs more '
                        f'propellant, which needs bigger tanks. The last iterate is not an answer '
                        f'and it is not returned, because a diverging loop\'s last iterate looks '
                        f'exactly like a converged one. Lower the tank pressure, raise the '
                        f'specific impulse, or accept a smaller payload.',
                        context = createErrorContext(component = 'SizingLoop'))

            previousDry  = totalDry
            coefficients = newCoefficients

        raise ClosureError(
            f'The sizing loop did not converge in {MAXIMUM_ITERATIONS} iterations. It is not '
            f'obviously diverging either, which usually means it is oscillating between two '
            f'states. The last dry mass was {totalDry:.0f} kg and it is not returned as a result.',
            context = createErrorContext(component = 'SizingLoop'))

    # -------------------------------------------------------------------------------------------- #

    def traceMassChain(self, pressureIncrement: float = 0.5e6) -> dict:

        '''

        The number this whole domain exists to produce: what a change in feed system pressure is
        worth in payload.

        A feed system pressure drop has to be made up somewhere, and it is made up in the tank. A
        higher tank pressure means a thicker wall, a heavier tank, a worse structural coefficient
        and less payload. That chain runs through three domains and no single one of them can see
        it.

        This method walks it by raising the tank pressure and re-closing the vehicle, holding the
        payload fixed and letting the liftoff mass absorb the difference. The liftoff mass penalty
        is what a pressure drop actually costs.

        '''

        findings = []

        baseline = self.close()

        original = self.tankPressure

        try:
            self.tankPressure = original + pressureIncrement
            raised = self.close()
        finally:
            self.tankPressure = original

        wallChange   = (raised['tanks'][0]['wallThickness']
                        - baseline['tanks'][0]['wallThickness'])
        tankChange   = raised['tanks'][0]['tankMass'] - baseline['tanks'][0]['tankMass']
        liftoffChange = raised['liftoffMass'] - baseline['liftoffMass']

        findings.append(
            f'Raising the tank pressure by {pressureIncrement / 1.0e6:.2f} MPa thickens the first '
            f'stage wall by {wallChange * 1000.0:.3f} mm.')

        findings.append(
            f'That adds {tankChange:.0f} kg to the tank, which worsens the structural coefficient '
            f'from {baseline["coefficients"][0]:.4f} to {raised["coefficients"][0]:.4f}.')

        findings.append(
            f'Holding the payload at {self.payloadMass / 1000.0:.1f} t, the liftoff mass rises by '
            f'{liftoffChange:.0f} kg, which is {liftoffChange / tankChange:.1f} kg of vehicle for '
            f'every kilogram added to the tank.')

        findings.append(
            'That multiplier is the mass chain. A kilogram added low in the vehicle is not a '
            'kilogram at liftoff, and the feed system engineer trading half a bar of pressure drop '
            'against a larger line is making a vehicle decision without a vehicle model.')

        self.findings = findings

        return {'baseline':       baseline,
                'raised':         raised,
                'pressureIncrement': pressureIncrement,
                'wallChange':     wallChange,
                'tankMassChange': tankChange,
                'liftoffChange':  liftoffChange,
                'amplification':  liftoffChange / tankChange if tankChange != 0.0 else np.nan,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full sizing report.
        '''

        result = self.close()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  SIZING LOOP: {self.payloadMass / 1000.0:.1f} t to '
                     f'{self.targetDeltaV:.0f} m/s')
        lines.append('=' * 96)
        lines.append('')

        rows = [[f'{index + 1}',
                 f'{entry["propellantMass"] / 1000.0:.2f}',
                 f'{tank["tankMass"] / 1000.0:.3f}',
                 f'{tank["nonTankMass"] / 1000.0:.3f}',
                 f'{tank["wallThickness"] * 1000.0:.2f}',
                 f'{tank["overallLength"]:.2f}',
                 f'{result["coefficients"][index]:.4f}']
                for index, (entry, tank) in enumerate(zip(result['stages'], result['tanks']))]

        lines.append(formatReportTable(
            rows, ['Stage', 'Propellant [t]', 'Tank [t]', 'Other [t]', 'Wall [mm]',
                   'Length [m]', 'Coefficient'],
            title = 'Closed vehicle'))

        lines.append('')
        lines.append(formatReportTable(
            [['Iterations',       f'{result["iterations"]}',                   ''],
             ['Liftoff mass',     f'{result["liftoffMass"] / 1000.0:.2f}',     't'],
             ['Payload',          f'{result["payloadMass"] / 1000.0:.3f}',     't'],
             ['Payload fraction', f'{result["payloadFraction"]:.3%}',          ''],
             ['Tank pressure',    f'{self.tankPressure / 1.0e6:.2f}',          'MPa']],
            ['Quantity', 'Value', 'Unit'], title = 'Closure'))

        lines.append('')
        for finding in result['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'sizing_loop.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('payload mass',  self.payloadMass),
                            ('target delta-V', self.targetDeltaV),
                            ('tank radius',   self.tankRadius),
                            ('tank pressure', self.tankPressure),
                            ('propellant density', self.propellantDensity)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'SizingLoop'))

        if not self.stages:
            raise InvalidInputError(
                'A vehicle needs at least one stage.',
                context = createErrorContext(component = 'SizingLoop'))

        for index, stage in enumerate(self.stages):

            for key in ('specificImpulse', 'deltaVFraction'):
                if key not in stage:
                    raise InvalidInputError(
                        f'Stage {index + 1} has no {key}.',
                        context = createErrorContext(component = 'SizingLoop'))

            if 'structuralCoefficient' in stage:
                raise InvalidInputError(
                    f'Stage {index + 1} was given a structural coefficient. This class computes '
                    f'it from the tank rather than taking it, and accepting one here would let a '
                    f'caller assert the answer the loop exists to find. Use StagedVehicle if the '
                    f'coefficient is known.',
                    context = createErrorContext(component = 'SizingLoop'))

        total = sum(stage['deltaVFraction'] for stage in self.stages)

        if abs(total - 1.0) > 1.0e-6:
            raise InvalidInputError(
                f'The delta-V fractions sum to {total:.4f} rather than one.',
                context = createErrorContext(component = 'SizingLoop'))
