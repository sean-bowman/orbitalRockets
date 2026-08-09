
# -- vehicleArchitecture worked example -- #

'''

One bar of feed system pressure drop, traced all the way to the payload.

The answer is 730 kg of liftoff mass on a 40 tonne vehicle, and the multiplier that produces it is
eleven: **every kilogram added to the first stage tank costs eleven kilograms at liftoff.** That
number is the reason this domain exists, and no single subsystem can see it, because the chain runs
from a fluid system pressure drop through a structures wall thickness into a rocket equation.

The example also settles two arguments that get had a lot and are worth less than they cost.

    The optimal staging split is flat. Ten per cent either way is worth a fifth of a per cent.
    The liftoff thrust to weight is not set by the loss budget, which wants 2.5 and gets 1.35.

And it corrects one of this domain's own stated design principles. "Payload is the residual of a
large subtraction, so small errors upstream are large errors in payload" is a claim about marginal
vehicles rather than about rockets. On a healthy design the elasticities are of order one. They
become large exactly when a design stops having margin, which is when it can least respond.

Run:
    python vehicleArchitecture/codeInterface.py

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

sys.path.insert(0, os.path.join(HERE, 'vehicleArchitectureLibrary'))

from vehicleUtils import STRUCTURAL_COEFFICIENT_BAND, structuralCoefficient, ClosureError
from StagedVehicle import StagedVehicle
from MassBudget import MassBudget
from AscentTrajectory import AscentTrajectory
from SizingLoop import SizingLoop

ASSET = os.path.join(HERE, 'vehicleArchitectureLibrary', 'assets',
                     'smallLaunchVehicleExample.json')

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def buildLoop(case: dict, pressure: float = None) -> SizingLoop:

    tank = case['tank']

    loop = SizingLoop()
    loop.setInputs({'payloadMass':       case['mission']['payloadMass'],
                    'targetDeltaV':      case['mission']['targetDeltaV'],
                    'stages':            [{'specificImpulse': stage['specificImpulse'],
                                           'deltaVFraction':  stage['deltaVFraction']}
                                          for stage in case['stages']],
                    'tankRadius':        tank['radius'],
                    'tankPressure':      pressure if pressure is not None else tank['pressure'],
                    'tankMaterial':      tank['material'],
                    'propellantDensity': tank['propellantDensity']})

    return loop

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: does the rocket equation reproduce a real vehicle -- #
# ------------------------------------------------------------------------------------------------ #

def reportReferenceCheck(case: dict) -> dict:

    banner('1. DOES THE ROCKET EQUATION REPRODUCE A REAL VEHICLE')

    reference = case['reference']

    epsilonOne = structuralCoefficient(reference['stageOneDryMass'],
                                       reference['stageOneGrossMass'])
    epsilonTwo = structuralCoefficient(reference['stageTwoDryMass'],
                                       reference['stageTwoGrossMass'])

    vehicle = StagedVehicle()
    vehicle.setInputs({
        'stages': [{'specificImpulse': 297.0, 'structuralCoefficient': epsilonOne,
                    'propellantMass': reference['stageOneGrossMass']
                                      - reference['stageOneDryMass']},
                   {'specificImpulse': 348.0, 'structuralCoefficient': epsilonTwo,
                    'propellantMass': reference['stageTwoGrossMass']
                                      - reference['stageTwoDryMass']}],
        'payloadMass': reference['payloadToLeoExpended']})

    performance = vehicle.calculatePerformance()

    print(f'  {reference["vehicle"]}, from published stage masses.')
    print()
    print(f'    {"stage":8s} {"eps":>8s} {"mass ratio":>12s} {"dV [m/s]":>10s}')
    for entry, epsilon in zip(performance['stages'], (epsilonOne, epsilonTwo)):
        print(f'    {entry["stage"]:<8d} {epsilon:8.4f} {entry["massRatio"]:12.3f} '
              f'{entry["deltaV"]:10.0f}')

    print()
    print(f'  Total {performance["totalDeltaV"]:.0f} m/s at a liftoff mass of '
          f'{performance["liftoffMass"] / 1000.0:.0f} t, carrying '
          f'{reference["payloadToLeoExpended"] / 1000.0:.1f} t.')
    print()
    print('  A low Earth orbit mission needs about 9300 m/s including losses. The published stage')
    print('  masses and engine performance close on that to within a couple of per cent, using')
    print('  nothing but the rocket equation.')
    print()
    print('  That is the check worth having. It does not validate any model in this domain beyond')
    print('  the bookkeeping, and the bookkeeping is what usually goes wrong: each stage lifts')
    print('  everything above it, and getting that wrong produces a plausible number.')

    print()
    print(f'  Structural coefficients of {epsilonOne:.4f} and {epsilonTwo:.4f} sit inside the '
          f'kerolox bands')
    print(f'  this library carries, {STRUCTURAL_COEFFICIENT_BAND["kerolox booster"]} and '
          f'{STRUCTURAL_COEFFICIENT_BAND["kerolox upper"]}.')

    return {'performance': performance,
            'coefficients': (epsilonOne, epsilonTwo)}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the two arguments that are not worth having -- #
# ------------------------------------------------------------------------------------------------ #

def reportFlatOptima(case: dict, coefficients: tuple) -> dict:

    banner('2. TWO ARGUMENTS THAT COST MORE THAN THEY ARE WORTH')

    vehicle = StagedVehicle()
    vehicle.setInputs({
        'stages': [{'specificImpulse': 297.0, 'structuralCoefficient': coefficients[0]},
                   {'specificImpulse': 348.0, 'structuralCoefficient': coefficients[1]}],
        'payloadMass':  case['reference']['payloadToLeoExpended'],
        'targetDeltaV': 9252.0})

    flatness = vehicle.checkStagingFlatness()

    print('  The staging split.')
    print()
    for finding in flatness['findings']:
        print(f'    - {finding}')

    print()
    print(f'  The real vehicle does not use the optimal split. It puts more on the first stage,')
    print(f'  and sizing it optimally would save under four per cent of liftoff mass. That gap')
    print(f'  buys engine commonality, booster recovery and a staging altitude the recovery needs,')
    print(f'  none of which the optimisation can see.')

    ascent = AscentTrajectory()
    ascent.setInputs({'thrustToWeight': case['ascent']['thrustToWeight'],
                      'latitude':       case['mission']['latitude'],
                      'launchAzimuth':  case['mission']['launchAzimuth']})

    budget = ascent.calculateBudget()
    sweep  = ascent.optimiseThrustToWeight()

    print()
    print('  The liftoff thrust to weight.')
    print()
    print(f'    {"term":22s} {"value [m/s]":>12s}')
    print(f'    {"orbital velocity":22s} {budget["orbitalVelocity"]:12.0f}')
    print(f'    {"rotation assist":22s} {-budget["rotationAssist"]:12.0f}')
    print(f'    {"gravity loss":22s} {budget["losses"]["gravity"]:12.0f}')
    print(f'    {"drag loss":22s} {budget["losses"]["drag"]:12.0f}')
    print(f'    {"steering loss":22s} {budget["losses"]["steering"]:12.0f}')
    print(f'    {"required":22s} {budget["requiredDeltaV"]:12.0f}')

    print()
    for finding in sweep['findings']:
        print(f'    - {finding}')

    return {'flatness': flatness, 'budget': budget, 'sweep': sweep}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the ethos this domain got wrong -- #
# ------------------------------------------------------------------------------------------------ #

def reportSensitivity(case: dict, coefficients: tuple) -> dict:

    banner('3. THE DESIGN PRINCIPLE THIS DOMAIN HAD BACKWARDS')

    print('  This domain\'s stated ethos says the payload is the residual of a large subtraction,')
    print('  so small errors upstream are large errors in payload. That is worth checking rather')
    print('  than repeating.')
    print()

    print(f'    {"vehicle":30s} {"payload %":>10s} {"fixed elasticity":>18s}')

    cases = (('the reference, good structure', coefficients[0], coefficients[1], 297.0, 348.0),
             ('mediocre structure',            0.070,           0.055,           297.0, 348.0),
             ('pressure fed upper stage',      0.070,           0.100,           297.0, 330.0),
             ('marginal, near closure',        0.090,           0.120,           285.0, 320.0))

    results = {}

    for name, first, second, impulseOne, impulseTwo in cases:

        vehicle = StagedVehicle()
        vehicle.setInputs({
            'stages': [{'specificImpulse': impulseOne, 'structuralCoefficient': first},
                       {'specificImpulse': impulseTwo, 'structuralCoefficient': second}],
            'payloadMass':  case['reference']['payloadToLeoExpended'],
            'targetDeltaV': 9252.0})

        sized       = vehicle.sizeToDeltaV()
        sensitivity = vehicle.payloadSensitivity()

        results[name] = {'payloadFraction': sized['payloadFraction'],
                         'elasticity': sensitivity['fixedVehicle']['dryMassElasticity']}

        print(f'    {name:30s} {sized["payloadFraction"]:9.3%} '
              f'{sensitivity["fixedVehicle"]["dryMassElasticity"]:18.2f}')

    print()
    print('  **The elasticity is not a property of the rocket equation. It is inversely')
    print('  proportional to how much payload fraction the design already has.**')
    print()
    print('  On a healthy vehicle a one per cent dry mass error costs a third of a per cent of')
    print('  payload. On a marginal one it costs one and a half. The claim that small upstream')
    print('  errors are large payload errors is therefore true of designs in trouble and not of')
    print('  designs in general, and it becomes true exactly when the design is least able to')
    print('  respond to it.')
    print()
    print('  That is a more useful statement than the original, because it tells you when to worry')
    print('  rather than telling you to worry always.')

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: growth allowance is not margin -- #
# ------------------------------------------------------------------------------------------------ #

def reportMassBudget(case: dict) -> dict:

    banner('4. GROWTH ALLOWANCE IS NOT MARGIN')

    budget = case['avionicsBudget']

    assembly = MassBudget()
    assembly.setInputs({'items':          [item for item in budget['items']],
                        'allocatedMass':  budget['allocatedMass'],
                        'programmePhase': budget['programmePhase']})

    rollup = assembly.rollUp()
    margin = assembly.checkMargin()

    print(f'    {"item":24s} {"maturity":14s} {"estimate":>10s} {"MGA":>6s} {"predicted":>11s}')
    for line in rollup['lines']:
        print(f'    {line["name"]:24s} {line["maturity"]:14s} {line["estimate"]:10.1f} '
              f'{line["allowanceRate"]:6.0%} {line["predicted"]:11.1f}')

    print(f'    {"TOTAL":24s} {"":14s} {rollup["estimate"]:10.1f} '
          f'{rollup["effectiveRate"]:6.1%} {rollup["predicted"]:11.1f}')

    print()
    for finding in margin['findings']:
        print(f'  - {finding}')

    print()
    print(f'  Note what happens if the two are confused. The estimate is '
          f'{rollup["estimate"]:.0f} kg against an')
    print(f'  allocation of {margin["allocated"]:.0f} kg, which looks like '
          f'{margin["allocated"] - rollup["estimate"]:.0f} kg of margin and is not margin at all.')
    print(f'  {rollup["growth"]:.0f} kg of it is growth allowance, which is what these estimates '
          f'are expected to')
    print('  become rather than a reserve against surprises. Spending it as margin leaves the')
    print('  programme with neither.')

    centre = assembly.calculateCentreOfGravity()

    print()
    print(f'  The centre of gravity moves {centre["shiftFromGrowth"] * 1000.0:.0f} mm between the '
          f'estimate and the prediction,')
    print('  because growth is not distributed evenly. That is small here and it is not always,')
    print('  and a control system sized on an estimate CG is sized on a number that will move.')

    return {'rollup': rollup, 'margin': margin, 'centre': centre}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the mass chain -- #
# ------------------------------------------------------------------------------------------------ #

def reportMassChain(case: dict) -> dict:

    banner('5. ONE BAR OF FEED PRESSURE, TRACED TO THE PAYLOAD')

    loop = buildLoop(case)

    closed = loop.close()

    print(f'  The vehicle closes in {closed["iterations"]} iterations.')
    print()
    print(f'    {"stage":8s} {"propellant [t]":>15s} {"tank [kg]":>11s} {"wall [mm]":>11s} '
          f'{"eps":>8s}')
    for index, (entry, tank) in enumerate(zip(closed['stages'], closed['tanks'])):
        print(f'    {index + 1:<8d} {entry["propellantMass"] / 1000.0:15.2f} '
              f'{tank["tankMass"]:11.0f} {tank["wallThickness"] * 1000.0:11.2f} '
              f'{closed["coefficients"][index]:8.4f}')

    print()
    print(f'  Liftoff {closed["liftoffMass"] / 1000.0:.1f} t for '
          f'{closed["payloadMass"] / 1000.0:.1f} t of payload, a payload fraction of '
          f'{closed["payloadFraction"]:.2%}.')

    trace = loop.traceMassChain(pressureIncrement = case['massChain']['pressureIncrement'])

    print()
    print('  Now add one bar to the tank pressure, which is what a smaller feed line, a tighter')
    print('  filter or an extra valve costs the pump inlet:')
    print()
    for finding in trace['findings']:
        print(f'    - {finding}')

    print()
    print('  **That is the mass chain, and it crosses three domains.** The pressure drop belongs')
    print('  to fluidSystems, the wall thickness to aerospaceStructures, and the payload to this')
    print('  one. The tank model here is imported from aerospaceStructures rather than')
    print('  reimplemented, so a change in its allowables reaches the payload without anybody')
    print('  reconciling two tank models.')

    return trace

# ------------------------------------------------------------------------------------------------ #
# -- Stage 6: where the chain becomes brutal -- #
# ------------------------------------------------------------------------------------------------ #

def reportPressureFed(case: dict) -> dict:

    banner('6. THE SAME VEHICLE, PRESSURE FED')

    pressures = [case['tank']['pressure'], 0.7e6, 1.5e6, 2.5e6,
                 case['massChain']['pressureFedComparison']]

    print(f'    {"tank [MPa]":>11s} {"wall [mm]":>11s} {"tank [kg]":>11s} {"eps":>8s} '
          f'{"liftoff [t]":>13s}')

    results = {}

    for pressure in pressures:

        try:
            closed = buildLoop(case, pressure).close()
        except ClosureError:
            print(f'    {pressure / 1.0e6:11.2f} {"":>11s} {"":>11s} {"":>8s} '
                  f'{"DOES NOT CLOSE":>13s}')
            results[pressure] = None
            continue

        results[pressure] = closed

        print(f'    {pressure / 1.0e6:11.2f} {closed["tanks"][0]["wallThickness"] * 1000.0:11.2f} '
              f'{closed["tanks"][0]["tankMass"]:11.0f} {closed["coefficients"][0]:8.4f} '
              f'{closed["liftoffMass"] / 1000.0:13.1f}')

    lowest  = results[pressures[0]]
    highest = results[pressures[-1]]

    if lowest and highest:
        print()
        print(f'  Going from pump fed to pressure fed takes the liftoff mass from '
              f'{lowest["liftoffMass"] / 1000.0:.1f} t to')
        print(f'  {highest["liftoffMass"] / 1000.0:.1f} t for the same payload, a factor of '
              f'{highest["liftoffMass"] / lowest["liftoffMass"]:.2f}.')
        print()
        print('  The structural coefficient goes from '
              f'{lowest["coefficients"][0]:.3f} to {highest["coefficients"][0]:.3f}, which is out '
              f'of the kerolox')
        print('  booster band entirely and into the pressure fed one. That is not a penalty being')
        print('  applied by a table. It is the tank wall getting thicker, computed by the')
        print('  structures library, and it is the whole reason turbopumps exist.')

    print()
    print('  One limitation, stated rather than buried. The pressure vessel model has no minimum')
    print('  manufacturing gauge, so the thin-wall end of this table is optimistic: a real 2219')
    print('  tank has a gauge floor of a millimetre or two regardless of pressure. That makes the')
    print('  low pressure rows better than they should be and it does not change the direction.')

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(chain: dict, sensitivity: dict, flat: dict) -> None:

    banner('SUMMARY: WHAT ACTUALLY MOVES A VEHICLE')

    print()
    print(f'    {"lever":44s} {"worth":>16s}')
    print(f'    {"one bar of feed system pressure drop":44s} '
          f'{chain["liftoffChange"]:12.0f} kg')
    print(f'    {"one kilogram in the first stage tank":44s} '
          f'{chain["amplification"]:12.1f} kg')
    print(f'    {"ten per cent off the optimal staging split":44s} '
          f'{flat["flatness"]["worstPenalty"]:12.2%}')
    print(f'    {"one per cent of dry mass, healthy vehicle":44s} '
          f'{abs(sensitivity["the reference, good structure"]["elasticity"]):12.2f} %')
    print(f'    {"one per cent of dry mass, marginal vehicle":44s} '
          f'{abs(sensitivity["marginal, near closure"]["elasticity"]):12.2f} %')

    print()
    print('  The largest lever on that list is the one furthest from anybody who calls themselves')
    print('  a vehicle designer. A feed system engineer choosing a line size is setting a tank')
    print('  pressure, which sets a wall thickness, which sets a structural coefficient, which')
    print('  sets the payload, and the amplification from tank kilogram to liftoff kilogram is')
    print(f'  {chain["amplification"]:.0f} to one.')
    print()
    print('  The smallest lever is the one that gets argued about most. The staging split is flat')
    print('  and the real reference vehicle does not even use its optimum.')
    print()
    print('  What this domain cannot do is choose between architectures on anything but mass.')
    print('  Cost, schedule, manufacturability and the recovery mode that pays for itself over a')
    print('  hundred flights are all outside it, and a vehicle chosen on mass alone is a vehicle')
    print('  chosen on one axis of several.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    reference   = reportReferenceCheck(case)
    flat        = reportFlatOptima(case, reference['coefficients'])
    sensitivity = reportSensitivity(case, reference['coefficients'])

    reportMassBudget(case)

    chain = reportMassChain(case)

    reportPressureFed(case)

    summarise(chain, sensitivity, flat)

if __name__ == '__main__':
    main()
