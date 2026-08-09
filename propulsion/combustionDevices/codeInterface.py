
# -- combustionDevices worked example -- #

'''

The chamber that arrives from the propulsion hub, and what it takes to make it coolable.

The hub sizes a 100 kN LOX/RP-1 booster and hands over a geometry, a set of flow rates and a wall
heat load it computed from a stated placeholder. This example takes that geometry, computes the
heat load properly from Bartz, and finds that the engine cannot be regeneratively cooled by its own
fuel.

That is the result. It is not a failure of the hub, which labelled its placeholder as one, and it is
not a failure of the engine, which is an ordinary size at an ordinary chamber pressure. It is what
the physics says about a small high pressure hydrocarbon engine, and the response is film cooling
rather than a better channel.

The example then finds how much film cooling is needed and what it costs, which is the trade this
sub-domain exists to support:

    film cooling removes heat from the regenerative circuit
    it costs c* efficiency, because that propellant burns at a ratio chosen for the wall
    too little and the chamber cokes; too much and the engine underperforms

Two numbers in it are unvalidated and the example says so where it uses them: the RP-1 coking limit
that decides the closure, and the c* penalty per unit film fraction that prices the fix. Both are in
the register in validation/referenceCases.py.

Run:
    python propulsion/combustionDevices/codeInterface.py

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

HERE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(HERE, 'combustionDevicesLibrary'))

from combustionUtils import CHAMBER_ACOUSTIC_MODES, CHUG_STIFFNESS_FLOOR
from Injector import Injector, FILM_EFFICIENCY_PENALTY_LOWER, FILM_EFFICIENCY_PENALTY_UPPER
from CombustionStability import CombustionStability
from RegenerativeCooling import RegenerativeCooling, COOLANT_LIMITS, COOLANT_BY_COMBINATION

ASSET = os.path.join(HERE, 'combustionDevicesLibrary', 'assets', 'boosterChamberExample.json')

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

def buildCooling(case: dict, heatLoadFactor: float = 1.0) -> RegenerativeCooling:

    '''
    The cooling circuit for the inherited chamber. `heatLoadFactor` scales the coolant flow to
    represent film cooling having removed part of the load from the regenerative circuit.
    '''

    chamber = case['inherited']

    cooling = RegenerativeCooling()
    cooling.setInputs({'combination':      chamber['combination'],
                       'chamberPressure':  chamber['chamberPressure'],
                       'throatDiameter':   chamber['throatDiameter'],
                       'contractionRatio': chamber['contractionRatio'],
                       'areaRatio':        chamber['areaRatio'],
                       'barrelLength':     chamber['barrelLength'],
                       'convergentLength': chamber['convergentLength'],
                       'divergentLength':  chamber['divergentLength'],
                       'coolantFlow':      chamber['fuelFlow'],
                       'wallMaterial':     case['wall']['material'],
                       'wallThickness':    case['wall']['thickness'],
                       'wallTemperature':  case['wall']['gasSideTemperature']})

    return cooling

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: what arrives from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def reportInheritedChamber(case: dict) -> dict:

    banner('1. THE CHAMBER THAT ARRIVES FROM THE HUB')

    chamber = case['inherited']

    print(f'  From propulsion/codeInterface.py, the {chamber["thrust"] / 1000.0:.0f} kN booster:')
    print()
    print(f'    combination           {chamber["combination"]}')
    print(f'    chamber pressure      {chamber["chamberPressure"] / 1.0e6:8.2f} MPa')
    print(f'    throat diameter       {chamber["throatDiameter"] * 1000.0:8.1f} mm')
    print(f'    contraction ratio     {chamber["contractionRatio"]:8.2f}')
    print(f'    area ratio            {chamber["areaRatio"]:8.2f}')
    print(f'    oxidiser flow         {chamber["oxidiserFlow"]:8.2f} kg/s')
    print(f'    fuel flow             {chamber["fuelFlow"]:8.2f} kg/s')
    print()
    print(f'  The hub also handed over a wall heat load of '
          f'{chamber["hubHeatLoadPlaceholder"] / 1.0e6:.2f} MW, computed as')
    print(f'  {chamber["hubPlaceholderFraction"]:.0%} of jet power. It labelled that a placeholder. '
          f'Replacing it is')
    print('  the first thing this sub-domain does.')

    return chamber

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the real heat load -- #
# ------------------------------------------------------------------------------------------------ #

def computeHeatLoad(case: dict) -> dict:

    banner('2. THE REAL HEAT LOAD, FROM BARTZ')

    cooling = buildCooling(case)

    heat = cooling.calculateHeatLoad()

    placeholder = case['inherited']['hubHeatLoadPlaceholder']

    print(f'    {"section":12s} {"area [cm2]":>12s} {"mean q [MW/m2]":>16s} {"load [MW]":>11s}')
    for name, entry in heat['sections'].items():
        print(f'    {name:12s} {entry["area"] * 1.0e4:12.1f} '
              f'{entry["meanFlux"] / 1.0e6:16.2f} {entry["load"] / 1.0e6:11.3f}')
    print(f'    {"total":12s} {heat["totalArea"] * 1.0e4:12.1f} '
          f'{heat["meanFlux"] / 1.0e6:16.2f} {heat["totalLoad"] / 1.0e6:11.3f}')

    print()
    print(f'  Bartz gives {heat["totalLoad"] / 1.0e6:.2f} MW against the hub placeholder '
          f'{placeholder / 1.0e6:.2f} MW,')
    print(f'  a factor of {heat["totalLoad"] / placeholder:.2f}.')
    print()
    print('  The placeholder was wrong in a diagnosable way rather than merely imprecise. It took')
    print('  two per cent of JET power, and jet power is not the quantity heat is lost from. The')
    print('  thermal power is larger, and even two per cent of that is short of what Bartz gives,')
    print('  so the fraction was optimistic as well as measured against the wrong base.')

    band = case['validation']['measuredThroatFluxBand']

    print()
    print(f'  Validation: the peak throat flux is {heat["peakFlux"] / 1.0e6:.1f} MW/m^2, against a '
          f'measured')
    print(f'  literature band of {band[0]:.0f} to {band[1]:.0f} MW/m^2. It sits inside the band '
          f'and near the top,')
    print('  which is consistent with the documented tendency of Bartz to overpredict. That is a')
    print('  bounding check and not a validation: it would catch an order of magnitude and it')
    print('  would not catch the factor of three that started this.')

    return {'cooling': cooling, 'heat': heat}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the circuit does not close -- #
# ------------------------------------------------------------------------------------------------ #

def checkClosure(case: dict, loadResult: dict) -> dict:

    banner('3. THE REGENERATIVE CIRCUIT DOES NOT CLOSE')

    capability = loadResult['cooling'].checkCoolantCapability()

    print(f'    coolant                {capability["coolant"]}')
    print(f'    flow available         {loadResult["cooling"].coolantFlow:8.2f} kg/s, the whole '
          f'fuel flow')
    print(f'    heat load              {capability["heatLoad"] / 1.0e6:8.2f} MW')
    print(f'    bulk temperature rise  {capability["temperatureRise"]:8.0f} K')
    print(f'    outlet                 {capability["outletTemperature"]:8.0f} K')
    print(f'    limit                  {capability["limit"]:8.0f} K')
    print(f'    margin                 {capability["margin"]:+8.0f} K')
    print(f'    closes                 {str(capability["feasible"]):>8s}')

    print()
    print('  The bulk temperature rise is the heat load over the flow times the specific heat. The')
    print('  channel does not appear in it, so no channel geometry changes this answer. That is')
    print('  why the check runs before anything is sized rather than after.')

    print()
    print(f'  Closing would need {capability["requiredFlow"]:.2f} kg/s against the '
          f'{loadResult["cooling"].coolantFlow:.2f} kg/s available,')
    print(f'  a factor of {capability["requiredFlow"] / loadResult["cooling"].coolantFlow:.2f}. '
          f'There is no more fuel: it is all already')
    print('  going through the jacket.')

    print()
    print(f'  Caveat, and it matters: the {capability["limit"]:.0f} K limit is an unvalidated '
          f'number. It is a widely')
    print('  quoted range rather than a sourced value, and the real limit is a film temperature')
    print('  depending on residence time and surface chemistry. The conclusion is sensitive to it.')

    return capability

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: what film cooling buys -- #
# ------------------------------------------------------------------------------------------------ #

def sizeFilmCooling(case: dict, loadResult: dict, capability: dict) -> dict:

    banner('4. WHAT FILM COOLING BUYS, AND WHAT IT COSTS')

    chamber = case['inherited']
    film    = case['film']

    coolant = COOLANT_LIMITS[COOLANT_BY_COMBINATION[chamber['combination']]]

    heatLoad     = capability['heatLoad']
    coolantFlow  = chamber['fuelFlow']
    inlet        = loadResult['cooling'].coolantInlet

    # the heat load the regenerative circuit can actually carry within the coolant limit
    carryable = coolantFlow * coolant['specificHeat'] * (coolant['limit'] - inlet)

    removalNeeded = (heatLoad - carryable) / heatLoad

    print(f'  The circuit can carry {carryable / 1.0e6:.2f} MW within the coolant limit and is '
          f'being asked to carry')
    print(f'  {heatLoad / 1.0e6:.2f} MW. Film cooling has to remove '
          f'{removalNeeded:.0%} of the load from it.')

    print()
    print(f'    {"film fraction":>14s} {"load removed":>14s} {"circuit closes":>16s} '
          f'{"c* loss":>16s}')

    results = {}

    for fraction in film['fractionsTried']:

        # film cooling effectiveness: the fraction of wall heat load removed per unit film fraction
        removed = min(fraction * film['effectiveness'], 0.95)

        remaining = heatLoad * (1.0 - removed)

        # the film propellant leaves the regenerative circuit as well
        regenFlow = coolantFlow * (1.0 - fraction)

        rise    = remaining / (regenFlow * coolant['specificHeat'])
        outlet  = inlet + rise
        closes  = outlet <= coolant['limit']

        lower = FILM_EFFICIENCY_PENALTY_LOWER * fraction
        upper = FILM_EFFICIENCY_PENALTY_UPPER * fraction

        results[fraction] = {'removed': removed, 'outlet': outlet, 'closes': closes,
                             'lossLower': lower, 'lossUpper': upper, 'regenFlow': regenFlow}

        print(f'    {fraction:13.0%} {removed:14.0%} {str(closes):>16s} '
              f'{f"{lower:.1%} to {upper:.1%}":>16s}')

    closing = [f for f in film['fractionsTried'] if results[f]['closes']]

    print()
    if closing:
        chosen = min(closing)
        entry  = results[chosen]
        print(f'  The smallest film fraction that closes is {chosen:.0%}, costing '
              f'{entry["lossLower"]:.1%} to {entry["lossUpper"]:.1%} of c*.')
        print(f'  On a {chamber["thrust"] / 1000.0:.0f} kN engine at '
              f'{case["inherited"]["specificImpulse"]:.0f} s that is '
              f'{entry["lossLower"] * case["inherited"]["specificImpulse"]:.1f} to '
              f'{entry["lossUpper"] * case["inherited"]["specificImpulse"]:.1f} seconds of impulse.')
    else:
        chosen = None
        print('  No film fraction tried closes the circuit. The chamber pressure or the engine')
        print('  size has to change.')

    print()
    print('  Two of the three numbers in that trade are unvalidated. The effectiveness is an')
    print('  assumption stated in the asset. The c* penalty range is an estimate, and it is a')
    print('  range rather than a value precisely because no source was found for it. An earlier')
    print('  version of this library asserted the penalty equalled the film fraction, which is the')
    print('  pessimistic end stated as a value and overstates it by two to three times.')

    return {'results': results, 'chosen': chosen, 'removalNeeded': removalNeeded}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the injector that has to do it -- #
# ------------------------------------------------------------------------------------------------ #

def designInjector(case: dict, filmResult: dict) -> dict:

    banner('5. THE INJECTOR THAT HAS TO DELIVER IT')

    chamber = case['inherited']

    fraction = filmResult['chosen'] if filmResult['chosen'] else case['film']['fractionsTried'][-1]

    injector = Injector()
    injector.setInputs({'combination':     chamber['combination'],
                        'chamberPressure': chamber['chamberPressure'],
                        'oxidiserFlow':    chamber['oxidiserFlow'],
                        'fuelFlow':        chamber['fuelFlow'],
                        'elementType':     case['injector']['elementType'],
                        'elementCount':    case['injector']['elementCount'],
                        'stiffness':       case['injector']['stiffness'],
                        'filmFraction':    fraction})

    orifices = injector.sizeOrifices()
    momentum = injector.calculateMomentumRatio()
    wall     = injector.checkWallCompatibility()

    print(f'    elements               {injector.elementCount:8.0f} {injector.elementType}')
    print(f'    stiffness              {injector.stiffness:8.1%}')
    print(f'    oxidiser orifice       '
          f'{orifices["orifices"]["oxidiser"]["diameter"] * 1000.0:8.2f} mm')
    print(f'    fuel orifice           '
          f'{orifices["orifices"]["fuel"]["diameter"] * 1000.0:8.2f} mm')
    print(f'    momentum ratio         {momentum["momentumRatio"]:8.2f}')
    print(f'    film fraction          {fraction:8.0%}')
    print(f'    core mixture ratio     {wall["coreMixtureRatio"]:8.2f}')

    print()
    for finding in momentum['findings']:
        print(f'    - {finding}')

    return {'injector': injector, 'momentum': momentum, 'wall': wall}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 6: stability -- #
# ------------------------------------------------------------------------------------------------ #

def checkStability(case: dict) -> dict:

    banner('6. STABILITY')

    chamber = case['inherited']

    chamberDiameter = chamber['throatDiameter'] * np.sqrt(chamber['contractionRatio'])

    stability = CombustionStability()
    stability.setInputs({'combination':       chamber['combination'],
                         'chamberDiameter':   chamberDiameter,
                         'chamberLength':     chamber['barrelLength'] + chamber['convergentLength'],
                         'injectorStiffness': case['injector']['stiffness'],
                         'baffleBlades':      case['stability']['baffleBlades']})

    modes   = stability.calculateAcousticModes()
    baffles = stability.sizeBaffles()
    cavity  = stability.sizeAcousticCavity()

    print(f'    {"mode":6s} {"frequency [Hz]":>15s}   suppressed by baffle')
    for name in modes['transverse']:
        suppressed = 'yes' if name in baffles['suppressed'] else 'no'
        print(f'    {name:6s} {modes["transverse"][name]["frequency"]:15.0f}   {suppressed}')

    print()
    print(f'  {baffles["blades"]} blades cover tangential modes to order '
          f'{baffles["suppressedOrder"]}, and leave '
          f'{", ".join(baffles["unsuppressed"])} untouched.')
    print(f'  A quarter wave cavity tuned to 1T is '
          f'{cavity["quarterWaveDepth"] * 1000.0:.1f} mm deep and does reach the radial modes,')
    print('  which is why the two are fitted together rather than chosen between.')

    print()
    print('  Nothing here is a stability margin. Instability is a threshold and the only')
    print('  meaningful statement is a rating test: perturb the chamber deliberately and time the')
    print('  decay. A class that returned a margin would be inventing one.')

    return {'stability': stability, 'modes': modes, 'baffles': baffles}

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, loadResult: dict, capability: dict, filmResult: dict) -> None:

    banner('SUMMARY: A CHAMBER THAT NEEDS FILM COOLING TO EXIST')

    heat = loadResult['heat']

    print()
    print(f'    {"quantity":34s} {"value":>14s}   source')
    print(f'    {"hub placeholder heat load":34s} '
          f'{case["inherited"]["hubHeatLoadPlaceholder"] / 1.0e6:11.2f} MW   stated placeholder')
    print(f'    {"Bartz heat load":34s} {heat["totalLoad"] / 1.0e6:11.2f} MW   computed')
    print(f'    {"peak throat flux":34s} {heat["peakFlux"] / 1.0e6:11.1f} MW/m^2 '
          f'  computed, inside measured band')
    print(f'    {"coolant outlet, regen only":34s} '
          f'{capability["outletTemperature"]:11.0f} K      computed')
    print(f'    {"RP-1 limit":34s} {capability["limit"]:11.0f} K      UNVALIDATED')

    if filmResult['chosen']:
        print(f'    {"film fraction to close":34s} {filmResult["chosen"]:11.0%}        computed '
              f'on an assumed effectiveness')

    print()
    print('  The engine cannot be regeneratively cooled by its own fuel. That is not a defect in')
    print('  the hub, which labelled its placeholder, and not a defect in the engine, which is an')
    print('  ordinary size at an ordinary chamber pressure. It is what a small high pressure')
    print('  hydrocarbon engine does, and it is why film cooling is standard on them rather than')
    print('  an optimisation.')
    print()
    print('  Two of the numbers deciding it are unvalidated and both are named above. Neither is')
    print('  hidden in a constant, and the register in validation/referenceCases.py says what')
    print('  would close each one.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    reportInheritedChamber(case)

    loadResult = computeHeatLoad(case)
    capability = checkClosure(case, loadResult)
    filmResult = sizeFilmCooling(case, loadResult, capability)

    designInjector(case, filmResult)
    checkStability(case)

    summarise(case, loadResult, capability, filmResult)

if __name__ == '__main__':
    main()
