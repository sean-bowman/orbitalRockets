
# -- propulsion worked example -- #

'''

A first stage booster engine, taken from a thrust requirement to a geometry, and the one decision
along the way that has three defensible answers which disagree.

The decision is the area ratio. Ask three reasonable questions and get three different numbers:

    what maximises thrust at liftoff        expand to ambient at sea level
    what maximises impulse over the burn    expand much further, because most of the burn is not
                                            at sea level
    what the flow will tolerate             stop before the exit pressure falls far enough below
                                            ambient for the boundary layer to separate

The first is the intuitive answer and it is wrong by 1.9 per cent of burn-averaged specific
impulse, which is 61 m/s of stage delta-V. The second is right and unreachable, because it
separates on the pad. The third is a constraint rather than an objective.

The design point is the third with margin held off it, because Summerfield's criterion is a
correlation with real scatter and designing exactly on it is designing on a coin toss. Five per
cent back from the limit lands 0.5 seconds short of the unreachable optimum, so the constraint and
the margin together are close to free.

That is why real first stage nozzles are deliberately over-expanded at sea level. It looks like a
compromise and it is within half a second of the best available.

The example then sizes the engine that results and states what it hands to the domains either side
of it: the flow rates fluidSystems has to deliver, the wall heat load thermalManagement has to
reject, and the thrust aerospaceStructures has to react.

Run:
    python propulsion/codeInterface.py

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'propulsionLibrary'))

from propulsionUtils import (GRAVITY, SUMMERFIELD_SEPARATION_RATIO, TYPICAL_CSTAR_EFFICIENCY,
                             areaRatioFromPressureRatio, convertAltitudeToPressure)
from PropellantCombination import PropellantCombination
from EnginePerformance import EnginePerformance
from EngineSizing import EngineSizing

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'propulsionLibrary', 'assets', 'firstStageEngineExample.json')

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the propellant -- #
# ------------------------------------------------------------------------------------------------ #

def selectPropellant(case: dict) -> dict:

    banner('1. THE PROPELLANT, CHOSEN ON DENSITY RATHER THAN IMPULSE')

    selection = case['selection']

    combination = PropellantCombination()
    combination.setInputs({'combination': selection['chosen'],
                           'areaRatio':   selection['comparisonAreaRatio']})

    comparison = combination.compareCombinations()

    print(f'  All at an area ratio of {selection["comparisonAreaRatio"]:.0f}, so the expansion is '
          f'not doing the ranking:')
    print()
    print(f'    {"combination":14s} {"Isp [s]":>9s} {"rho [kg/m3]":>13s} {"rho.Isp":>10s}   storable')

    for name in comparison['byDensityImpulse']:
        if name not in selection['candidates']:
            continue
        entry  = comparison['combinations'][name]
        marker = '  <-' if name == selection['chosen'] else ''
        print(f'    {name:14s} {entry["specificImpulse"]:9.1f} {entry["bulkDensity"]:13.0f} '
              f'{entry["densityImpulse"] / 1000.0:10.1f}   {str(entry["storable"]):5s}{marker}')

    hydrogen = comparison['combinations']['LOX/LH2']
    chosen   = comparison['combinations'][selection['chosen']]

    print()
    print(f'  LOX/LH2 wins on specific impulse by '
          f'{(hydrogen["specificImpulse"] / chosen["specificImpulse"] - 1.0) * 100.0:.0f} per cent '
          f'and loses on density impulse by a factor of '
          f'{chosen["densityImpulse"] / hydrogen["densityImpulse"]:.1f}.')
    print('  A first stage carries its tanks through the atmosphere, so it pays for volume in')
    print('  structure, drag and gravity losses. That is a density impulse problem, and it is the')
    print('  reason almost no first stage has ever flown on hydrogen without solid boosters beside')
    print('  it.')

    density = combination.calculateBulkDensity()

    print()
    print(f'  {selection["chosen"]} at a mixture ratio of {combination.mixtureRatio:.2f}:')
    print(f'    bulk density        {density["bulkDensity"]:8.1f} kg/m^3')
    print(f'    fuel volume share   {density["fuelVolumeFraction"] * 100.0:8.0f} %')
    print(f'    fuel mass share     {density["fuelMassFraction"] * 100.0:8.0f} %')

    return {'combination': combination, 'comparison': comparison, 'density': density}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the area ratio, which has three answers -- #
# ------------------------------------------------------------------------------------------------ #

def burnAveragedImpulse(performance: EnginePerformance, altitudes: list,
                        characteristicVelocity: float) -> float:

    '''
    Specific impulse averaged over the ascent samples, which are equally spaced in burn time.
    '''

    values = []

    for altitude in altitudes:
        ambient = float(convertAltitudeToPressure(altitude))
        thrustCoefficient = performance.calculateThrustCoefficient(ambient)
        values.append(characteristicVelocity * thrustCoefficient['delivered'] / GRAVITY)

    return float(np.mean(values))

def selectExpansion(case: dict, propellant: dict) -> dict:

    banner('2. THE AREA RATIO, AND WHY THE OBVIOUS ANSWER IS THE WRONG ONE')

    requirement = case['requirement']
    ascent      = case['ascent']
    expansion   = case['expansion']

    combination   = case['selection']['chosen']
    gamma         = propellant['combination'].properties['gamma']
    referenceCstar = propellant['combination'].properties['referenceCstar']
    deliveredCstar = referenceCstar * TYPICAL_CSTAR_EFFICIENCY

    chamberPressure = requirement['chamberPressure']
    seaLevel        = requirement['thrustAmbientPressure']

    def build(areaRatio: float) -> EnginePerformance:
        performance = EnginePerformance()
        performance.setInputs({'combination':     combination,
                               'chamberPressure': chamberPressure,
                               'areaRatio':       float(areaRatio)})
        return performance

    ratios = np.arange(expansion['sweepLower'], expansion['sweepUpper'], expansion['sweepStep'])

    seaLevelImpulse = []
    averageImpulse  = []

    for ratio in ratios:
        performance = build(ratio)
        thrustCoefficient = performance.calculateThrustCoefficient(seaLevel)
        seaLevelImpulse.append(deliveredCstar * thrustCoefficient['delivered'] / GRAVITY)
        averageImpulse.append(burnAveragedImpulse(performance, ascent['altitudeSamples'],
                                                  deliveredCstar))

    seaLevelOptimum = float(ratios[int(np.argmax(seaLevelImpulse))])
    averageOptimum  = float(ratios[int(np.argmax(averageImpulse))])

    separationLimit = areaRatioFromPressureRatio(
        gamma, SUMMERFIELD_SEPARATION_RATIO * seaLevel / chamberPressure)

    # Summerfield is a correlation with real scatter, so the design point is held back from the
    # limit rather than placed on it. Sitting exactly on a crude criterion is not a design.
    designPoint = separationLimit * expansion['separationMargin']

    # the pressure-matched expansion, which is what 'optimum at sea level' usually means
    pressureMatched = areaRatioFromPressureRatio(gamma, seaLevel / chamberPressure)

    answers = {}

    for label, ratio in (('sea level optimum',    seaLevelOptimum),
                         ('burn-average optimum', averageOptimum),
                         ('separation limit',     separationLimit),
                         ('design point',         designPoint)):

        performance = build(ratio)
        thrustCoefficient = performance.calculateThrustCoefficient(seaLevel)

        answers[label] = {
            'areaRatio':       ratio,
            'seaLevelImpulse': deliveredCstar * thrustCoefficient['delivered'] / GRAVITY,
            'averageImpulse':  burnAveragedImpulse(performance, ascent['altitudeSamples'],
                                                   deliveredCstar),
            'separated':       thrustCoefficient['separated']}

    print(f'  Expanding to exactly ambient at sea level gives an area ratio of '
          f'{pressureMatched:.2f}.')
    print(f'  The sweep finds the sea level impulse peak at {seaLevelOptimum:.2f}, which is the '
          f'same answer.')
    print()
    print(f'    {"answer":22s} {"eps":>7s} {"SL Isp [s]":>11s} {"burn avg [s]":>13s}   separated')
    for label, entry in answers.items():
        print(f'    {label:22s} {entry["areaRatio"]:7.2f} {entry["seaLevelImpulse"]:11.1f} '
              f'{entry["averageImpulse"]:13.1f}   {entry["separated"]}')

    naive     = answers['sea level optimum']
    reachable = answers['design point']
    ideal     = answers['burn-average optimum']

    penalty = reachable['averageImpulse'] - naive['averageImpulse']
    unreachable = ideal['averageImpulse'] - reachable['averageImpulse']

    deltaV = penalty * GRAVITY * np.log(ascent['massRatio'])

    print()
    print('  Three defensible questions, three different answers.')
    print()
    print(f'  Sizing at the sea level optimum costs {penalty:.1f} s of burn-averaged specific')
    print(f'  impulse, {penalty / naive["averageImpulse"] * 100.0:.2f} per cent, which at a mass '
          f'ratio of {ascent["massRatio"]:.1f} is {deltaV:.0f} m/s of stage delta-V.')
    print()
    print(f'  The true optimum at {ideal["areaRatio"]:.2f} separates on the pad, so it cannot be')
    print('  flown from a sea level start.')
    print()
    print(f'  The separation limit is {answers["separation limit"]["areaRatio"]:.2f}, and the '
          f'design point holds')
    print(f'  {(1.0 - expansion["separationMargin"]) * 100.0:.0f} per cent back from it at '
          f'{reachable["areaRatio"]:.2f}, because Summerfield is a correlation with real')
    print('  scatter and designing exactly on it is designing on a coin toss.')
    print()
    print(f'  That margin costs {unreachable:.1f} s against the unreachable optimum. The '
          f'constraint and the')
    print('  margin together are close to free, which is what makes this case pleasant rather')
    print('  than painful.')
    print()
    print('  So the answer is to expand until the flow is about to separate, back off, and accept')
    print('  being over-expanded at liftoff. That is what first stage nozzles do. It looks like a')
    print('  compromise and it is within half a second of the best available.')

    return {'answers':         answers,
            'chosen':          reachable,
            'pressureMatched': pressureMatched,
            'deltaVPenalty':   deltaV,
            'ratios':          ratios,
            'seaLevelImpulse': seaLevelImpulse,
            'averageImpulse':  averageImpulse,
            'deliveredCstar':  deliveredCstar}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the engine that results -- #
# ------------------------------------------------------------------------------------------------ #

def sizeEngine(case: dict, expansion: dict) -> dict:

    banner('3. THE ENGINE')

    requirement = case['requirement']

    areaRatio = expansion['chosen']['areaRatio']

    sizing = EngineSizing()
    sizing.setInputs({'combination':      case['selection']['chosen'],
                      'thrust':           requirement['thrust'],
                      'chamberPressure':  requirement['chamberPressure'],
                      'areaRatio':        areaRatio,
                      'ambientPressure':  requirement['thrustAmbientPressure'],
                      'contractionRatio': case['geometry']['contractionRatio']})

    throat  = sizing.sizeThroat()
    chamber = sizing.sizeChamber()
    nozzle  = sizing.sizeNozzle()
    mass    = sizing.estimateMass()

    print(f'  {requirement["thrust"] / 1000.0:.0f} kN at sea level, '
          f'{requirement["chamberPressure"] / 1.0e6:.1f} MPa chamber, area ratio '
          f'{areaRatio:.2f}')
    print()
    print(f'    specific impulse    {throat["specificImpulse"]:8.1f} s')
    print(f'    mass flow           {throat["massFlow"]:8.2f} kg/s')
    print(f'      oxidiser          {throat["oxidiserFlow"]:8.2f} kg/s')
    print(f'      fuel              {throat["fuelFlow"]:8.2f} kg/s')
    print()
    print(f'    throat diameter     {throat["throatDiameter"] * 1000.0:8.1f} mm')
    print(f'    exit diameter       {throat["exitDiameter"] * 1000.0:8.1f} mm')
    print(f'    chamber diameter    {chamber["chamberDiameter"] * 1000.0:8.1f} mm')
    print(f'    barrel length       {chamber["barrelLength"] * 1000.0:8.1f} mm')
    print(f'    bell length         {nozzle["bellLength"] * 1000.0:8.0f} mm')
    print(f'    residence time      {chamber["residenceTime"] * 1000.0:8.2f} ms')
    print(f'    engine mass         {mass["mass"]:8.1f} kg')

    print()
    for finding in chamber['findings']:
        print(f'    - {finding}')

    propellantMass = throat['massFlow'] * requirement['burnTime']

    print()
    print(f'  Over a {requirement["burnTime"]:.0f} s burn that is {propellantMass:.0f} kg of '
          f'propellant, which is the number the tanks are sized from.')

    return {'sizing': sizing, 'throat': throat, 'chamber': chamber,
            'nozzle': nozzle, 'mass': mass, 'propellantMass': propellantMass}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: what it hands to the domains either side -- #
# ------------------------------------------------------------------------------------------------ #

def reportInterfaces(case: dict, propellant: dict, engine: dict) -> None:

    banner('4. WHAT THIS ENGINE HANDS TO THE DOMAINS EITHER SIDE OF IT')

    interfaces = case['interfaces']
    throat     = engine['throat']
    chamber    = engine['chamber']

    density = propellant['density']

    propellantVolume = engine['propellantMass'] / density['bulkDensity']
    fuelVolume       = propellantVolume * density['fuelVolumeFraction']
    oxidiserVolume   = propellantVolume - fuelVolume

    feedPressure = case['requirement']['chamberPressure'] * interfaces['feedInletPressureMargin']

    print('  To fluidSystems, which owns everything upstream of the engine inlet:')
    print(f'    oxidiser flow          {throat["oxidiserFlow"]:9.2f} kg/s')
    print(f'    fuel flow              {throat["fuelFlow"]:9.2f} kg/s')
    print(f'    inlet pressure         {feedPressure / 1.0e6:9.2f} MPa at a '
          f'{interfaces["feedInletPressureMargin"]:.2f} margin over chamber')
    print(f'    oxidiser tank volume   {oxidiserVolume:9.2f} m^3')
    print(f'    fuel tank volume       {fuelVolume:9.2f} m^3')
    print('    The margin is what the injector, the cooling circuit and the valves consume. It is')
    print('    an assumption here and a pressure budget there, and the two have to agree.')

    print()
    print('  To thermalManagement, which owns the cooling:')
    print(f'    wall heat load         {chamber["wallHeatLoad"] / 1.0e6:9.2f} MW')
    print(f'    gas-side wall area     {chamber["availableWallArea"] * 1.0e4:9.0f} cm^2')
    print(f'    of which nozzle        {chamber["nozzleWallArea"] / chamber["availableWallArea"] * 100.0:9.0f} %')
    print(f'    wall limit             {interfaces["chamberWallLimit"]:9.0f} K '
          f'for {interfaces["chamberMaterial"]}')
    print(f'    The fuel flow of {throat["fuelFlow"]:.2f} kg/s is the entire coolant supply, so the')
    print('    cooling circuit and the feed system are one problem rather than two.')

    print()
    print('  To aerospaceStructures, which reacts the thrust:')
    print(f'    thrust                 {case["requirement"]["thrust"] / 1000.0:9.1f} kN')
    print(f'    design load            '
          f'{case["requirement"]["thrust"] * interfaces["thrustStructureFactorOfSafety"] / 1000.0:9.1f} kN '
          f'at a {interfaces["thrustStructureFactorOfSafety"]:.2f} factor')
    print(f'    engine mass            {engine["mass"]["mass"]:9.1f} kg')
    print(f'    exit diameter          {throat["exitDiameter"] * 1000.0:9.0f} mm, which sets the')
    print('    base diameter and therefore the gimbal envelope.')

    print()
    print('  To aerospaceMaterials, which owns the chamber liner:')
    print(f'    {interfaces["chamberMaterial"]} at a {interfaces["chamberWallLimit"]:.0f} K wall '
          f'limit, carrying {chamber["wallHeatLoad"] / 1.0e6:.2f} MW')
    print('    through a wall a millimetre or so thick. That combination is why the liner is a')
    print('    copper alloy and why it is additively manufactured.')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, expansion: dict, engine: dict) -> None:

    banner('SUMMARY: THREE ANSWERS TO ONE QUESTION')

    answers = expansion['answers']

    print()
    print(f'    {"question asked":38s} {"eps":>7s} {"burn avg [s]":>13s}   flyable')
    print(f'    {"what maximises liftoff thrust":38s} '
          f'{answers["sea level optimum"]["areaRatio"]:7.2f} '
          f'{answers["sea level optimum"]["averageImpulse"]:13.1f}   yes')
    print(f'    {"what maximises impulse over the burn":38s} '
          f'{answers["burn-average optimum"]["areaRatio"]:7.2f} '
          f'{answers["burn-average optimum"]["averageImpulse"]:13.1f}   no, separates')
    print(f'    {"what the flow will tolerate":38s} '
          f'{answers["separation limit"]["areaRatio"]:7.2f} '
          f'{answers["separation limit"]["averageImpulse"]:13.1f}   on the limit')
    print(f'    {"the design point, with margin":38s} '
          f'{answers["design point"]["areaRatio"]:7.2f} '
          f'{answers["design point"]["averageImpulse"]:13.1f}   yes')

    print()
    print(f'  The intuitive answer costs {expansion["deltaVPenalty"]:.0f} m/s of stage delta-V. The')
    print('  right answer is unreachable. The constraint that stops you reaching it happens to sit')
    print('  almost exactly where you wanted to be anyway.')
    print()
    print('  None of that is visible from a single point calculation at sea level, which is the')
    print('  condition the thrust requirement is written at and the condition the engine spends')
    print('  the least of its burn in.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    propellant = selectPropellant(case)
    expansion  = selectExpansion(case, propellant)
    engine     = sizeEngine(case, expansion)

    reportInterfaces(case, propellant, engine)
    summarise(case, expansion, engine)

if __name__ == '__main__':
    main()
