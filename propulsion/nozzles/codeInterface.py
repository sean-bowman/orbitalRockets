
# -- nozzles worked example -- #

'''

Where the performance actually is in a nozzle, ranked, and it is not where the effort usually goes.

The propulsion hub sizes a nozzle and reports a thrust coefficient efficiency of 0.98. This example
takes that number apart, ranks the levers that could move it, and finds the ordering is nearly the
reverse of the attention each usually receives.

    altitude compensation   14.5 s available, and no flying device captures more than about
                            two thirds of it
    bell against cone        2.7 s, and the decision was made on every flying engine decades ago
    which bell               0.5 s between an eighty and a hundred per cent
    separation criterion     0.45 s, despite changing the permitted area ratio by 36 per cent

The last one is the surprise and it is the reason this example exists. Choosing Schmucker over
Summerfield permits an area ratio of 29.2 rather than 21.4, which **makes the hub's own
burn-average optimum reachable when the hub had concluded it was not.** It is worth less than half
a second, because the area ratio optimum is broad.

A 36 per cent change in a design variable that moves the answer by 0.15 per cent is worth knowing
about before anyone argues over which correlation to believe.

Run:
    python propulsion/nozzles/codeInterface.py

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
ROOT = os.path.dirname(os.path.dirname(HERE))

sys.path.insert(0, os.path.join(HERE, 'nozzlesLibrary'))
sys.path.insert(0, os.path.join(ROOT, 'propulsion', 'propulsionLibrary'))

from nozzleUtils import (NOZZLE_CONTOURS, SUMMERFIELD_SEPARATION_RATIO,
                         schmuckerSeparationPressure, areaRatioFromPressureRatio,
                         convertAltitudeToPressure)
from NozzleLosses import NozzleLosses
from NozzleContour import NozzleContour
from AltitudeCompensation import AltitudeCompensation

from EnginePerformance import EnginePerformance

ASSET = os.path.join(HERE, 'nozzlesLibrary', 'assets', 'nozzleLeverExample.json')

SEA_LEVEL = 101325.0

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

def burnAverageImpulse(case: dict, areaRatio: float) -> float:

    '''
    Burn-averaged specific impulse over the ascent profile, at a given area ratio.
    '''

    engine = case['engine']

    performance = EnginePerformance()
    performance.setInputs({'combination':     engine['combination'],
                           'chamberPressure': engine['chamberPressure'],
                           'areaRatio':       float(areaRatio)})

    values = []

    for altitude in case['ascent']['altitudes']:
        ambient = float(convertAltitudeToPressure(altitude))
        thrustCoefficient = performance.calculateThrustCoefficient(ambient)
        values.append(engine['characteristicVelocity'] * thrustCoefficient['delivered'] / 9.80665)

    return float(np.mean(values))

def buildLosses(case: dict, contour: str) -> NozzleLosses:

    engine = case['engine']

    losses = NozzleLosses()
    losses.setInputs({'combination':     engine['combination'],
                      'areaRatio':       engine['areaRatio'],
                      'chamberPressure': engine['chamberPressure'],
                      'contour':         contour})

    return losses

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the loss budget -- #
# ------------------------------------------------------------------------------------------------ #

def reportLossBudget(case: dict) -> dict:

    banner('1. WHAT THE HUB\'S 0.98 IS MADE OF')

    engine = case['engine']

    losses = buildLosses(case, engine['contour'])

    decomposition = losses.decomposeEfficiency()

    print(f'  {engine["contour"]} at an area ratio of {engine["areaRatio"]:.2f}:')
    print()
    print(f'    {"mechanism":18s} {"efficiency":>11s} {"loss":>9s}   what it is')
    print(f'    {"divergence":18s} {decomposition["divergence"]:11.4f} '
          f'{decomposition["losses"]["divergence"]:9.2%}   the exit flow is not axial')
    print(f'    {"boundary layer":18s} {decomposition["boundaryLayer"]:11.4f} '
          f'{decomposition["losses"]["boundary layer"]:9.2%}   friction on the wall')
    print(f'    {"kinetic":18s} {decomposition["kinetic"]:11.4f} '
          f'{decomposition["losses"]["kinetic"]:9.2%}   the chemistry lags the expansion')
    print(f'    {"overall":18s} {decomposition["overall"]:11.4f}')

    print()
    print(f'  The hub carries 0.98 as a single number. This is what it decomposes into, and the')
    print(f'  largest single loss is {decomposition["largestLoss"]}.')
    print()
    print('  This example said the opposite until the exit angle was computed rather than looked')
    print('  up. A table gave an eighty per cent bell 8 degrees regardless of area ratio; Rao gives')
    print(f'  {decomposition["exitAngle"]:.1f} at this one, which doubles the divergence loss and inverts the ranking.')
    print('  Divergence is also the only one of the three a contour designer controls directly, so')
    print('  the correction moves the largest loss back into the designer\'s hands.')

    return decomposition

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the contour lever -- #
# ------------------------------------------------------------------------------------------------ #

def reportContourLever(case: dict) -> dict:

    banner('2. THE CONTOUR LEVER, AND WHERE IT STOPPED MATTERING')

    engine    = case['engine']
    reference = burnAverageImpulse(case, engine['areaRatio'])

    results = {}

    print(f'    {"contour":22s} {"exit [deg]":>11s} {"eta_Cf":>8s} {"Isp [s]":>9s} '
          f'{"vs 80% bell":>13s}')

    baseline = buildLosses(case, 'bell 80 per cent').decomposeEfficiency()['overall']

    for contour in case['contours']:

        decomposition = buildLosses(case, contour).decomposeEfficiency()

        efficiency = decomposition['overall']

        impulse = reference * efficiency / baseline

        results[contour] = {'efficiency': efficiency, 'impulse': impulse,
                            'exitAngle': decomposition['exitAngle'],
                            'delta': impulse - reference}

        print(f'    {contour:22s} {decomposition["exitAngle"]:11.1f} {efficiency:8.4f} '
              f'{impulse:9.2f} {impulse - reference:+13.2f}')

    cone = results['conical 15 degree']['impulse']
    bell = results['bell 80 per cent']['impulse']
    full = results['bell 100 per cent']['impulse']

    print()
    print(f'  Cone to an eighty per cent bell is worth {bell - cone:.2f} s.')
    print(f'  Eighty per cent to a hundred is worth {full - bell:.2f} s.')
    print()
    print('  The first decision is worth having and it was made on every flying engine decades')
    print('  ago. The second is half a second and it costs a quarter of the nozzle length back,')
    print('  which is why nobody flies a hundred per cent bell.')
    print()
    print('  Read the exit angle column before believing the usual story about short bells. The')
    print(f'  sixty per cent bell leaves at {results["bell 60 per cent"]["exitAngle"]:.1f} degrees, which is STEEPER than the fifteen degree')
    print('  cone it competes with, because a short bell turns the flow hard at the throat and has')
    print('  no length left to turn it back. Its divergence loss is worse than the cone\'s. It wins')
    print('  overall only on wall area. A short bell buys friction back, not divergence.')

    return {'results': results, 'reference': reference,
            'coneToBell': bell - cone, 'bellToFull': full - bell}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2b: the geometry the losses were computed from -- #
# ------------------------------------------------------------------------------------------------ #

def reportContourGeometry(case: dict) -> dict:

    '''
    The Rao contour itself, at conceptual fidelity, and the one number it changes downstream.
    '''

    banner('2b. THE GEOMETRY BEHIND THOSE NUMBERS')

    engine = case['engine']

    geometry = NozzleContour()
    geometry.setInputs({'throatRadius':   engine['throatRadius'],
                        'areaRatio':      engine['areaRatio'],
                        'lengthFraction': 0.80})

    angles = geometry.wallAngles()
    area   = geometry.surfaceArea()

    print(f'    {"quantity":26s} {"value":>10s}')
    print(f'    {"throat radius [mm]":26s} {engine["throatRadius"] * 1000.0:10.1f}')
    print(f'    {"exit radius [mm]":26s} {geometry.exitRadius() * 1000.0:10.1f}')
    print(f'    {"cone length [mm]":26s} {geometry.conicalLength() * 1000.0:10.1f}')
    print(f'    {"bell length [mm]":26s} {geometry.length() * 1000.0:10.1f}')
    print(f'    {"initial wall angle [deg]":26s} {angles["initialAngle"]:10.1f}')
    print(f'    {"exit wall angle [deg]":26s} {angles["exitAngle"]:10.1f}')
    print(f'    {"wetted area [cm^2]":26s} {area["area"] * 1.0e4:10.0f}')
    print(f'    {"frustum estimate [cm^2]":26s} {area["frustumArea"] * 1.0e4:10.0f}')

    print()
    print(f'  A bell bulges outward from the straight line between throat and exit, so it carries')
    print(f'  {area["ratio"]:.3f} times the wetted area of the cone frustum that combustionDevices uses to size')
    print('  the cooling circuit. That circuit already fails to close on this engine, so the')
    print('  direction is safe and the magnitude is recorded rather than propagated.')
    print()
    print('  This is Rao\'s parabolic approximation, which is a fit to published design data. It is')
    print('  a conceptual answer to "roughly what shape and how much area". The coordinates for')
    print('  manufacture come from NOVA and this does not attempt to compete with them.')

    return {'angles': angles, 'area': area, 'geometry': geometry}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the separation criterion -- #
# ------------------------------------------------------------------------------------------------ #

def reportSeparationLever(case: dict) -> dict:

    banner('3. THE SEPARATION CRITERION, AND WHY IT MATTERS LESS THAN IT LOOKS')

    engine = case['engine']
    hub    = case['hubResult']

    gamma = 1.24

    summerfieldLimit = areaRatioFromPressureRatio(
        gamma, SUMMERFIELD_SEPARATION_RATIO * SEA_LEVEL / engine['chamberPressure'])

    schmuckerLimit = areaRatioFromPressureRatio(
        gamma, schmuckerSeparationPressure(engine['chamberPressure'], SEA_LEVEL)
        / engine['chamberPressure'])

    margin = hub['separationMargin']

    summerfieldPoint = summerfieldLimit * margin
    schmuckerPoint   = schmuckerLimit * margin

    summerfieldImpulse = burnAverageImpulse(case, summerfieldPoint)
    schmuckerImpulse   = burnAverageImpulse(case, schmuckerPoint)

    print(f'    {"criterion":16s} {"limit":>8s} {"design point":>14s} {"burn-avg Isp":>14s}')
    print(f'    {"Summerfield":16s} {summerfieldLimit:8.2f} {summerfieldPoint:14.2f} '
          f'{summerfieldImpulse:14.2f}')
    print(f'    {"Schmucker":16s} {schmuckerLimit:8.2f} {schmuckerPoint:14.2f} '
          f'{schmuckerImpulse:14.2f}')

    print()
    print(f'  The criterion changes the permitted area ratio by '
          f'{(schmuckerLimit / summerfieldLimit - 1.0) * 100.0:.0f} per cent and the delivered')
    print(f'  impulse by {schmuckerImpulse - summerfieldImpulse:.2f} s, which is '
          f'{(schmuckerImpulse / summerfieldImpulse - 1.0) * 100.0:.2f} per cent.')

    optimum = hub['burnAverageOptimum']

    print()
    print(f'  It does change one conclusion. The hub found its burn-average optimum at an area')
    print(f'  ratio of {optimum:.2f} and rejected it, because Summerfield said it separates. Under')
    print(f'  Schmucker it does not: the limit is {schmuckerLimit:.2f}.')
    print()
    print(f'  So the hub\'s unreachable optimum is reachable, and reaching it is worth')
    print(f'  {burnAverageImpulse(case, optimum) - summerfieldImpulse:.2f} s.')
    print()
    print('  A 36 per cent change in a design variable that moves the answer by a seventh of a')
    print('  per cent is worth knowing before anyone argues over which correlation to believe.')
    print('  The area ratio optimum is broad, and that is why.')

    return {'summerfieldLimit': summerfieldLimit, 'schmuckerLimit': schmuckerLimit,
            'summerfieldImpulse': summerfieldImpulse, 'schmuckerImpulse': schmuckerImpulse,
            'gain': schmuckerImpulse - summerfieldImpulse,
            'optimumReachable': bool(optimum <= schmuckerLimit)}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the lever nobody has captured -- #
# ------------------------------------------------------------------------------------------------ #

def reportCompensationLever(case: dict) -> dict:

    banner('4. THE ONE LARGE LEVER, AND WHY IT IS STILL THERE')

    engine = case['engine']

    compensation = AltitudeCompensation()
    compensation.setInputs({'combination':            engine['combination'],
                            'chamberPressure':        engine['chamberPressure'],
                            'areaRatio':              engine['areaRatio'],
                            'characteristicVelocity': engine['characteristicVelocity'],
                            'altitudes':              case['ascent']['altitudes']})

    bound        = compensation.calculateIdealBenefit()
    arrangements = compensation.compareArrangements()

    print(f'  A perfectly compensating nozzle is worth {bound["benefit"]:.2f} s, '
          f'{bound["benefitFraction"]:.1%}.')
    print()
    print(f'    {"altitude [km]":>14s} {"fixed [s]":>11s} {"ideal [s]":>11s} {"gap [s]":>9s}')
    for index, altitude in enumerate(case['ascent']['altitudes']):
        print(f'    {altitude / 1000.0:14.0f} {bound["fixedProfile"][index]:11.2f} '
              f'{bound["idealProfile"][index]:11.2f} '
              f'{bound["idealProfile"][index] - bound["fixedProfile"][index]:9.2f}')

    gaps = [ideal - fixed for ideal, fixed
            in zip(bound['idealProfile'], bound['fixedProfile'])]

    print()
    print(f'  The gap is {gaps[0]:.2f} s at sea level and {gaps[-1]:.2f} s at the top, a factor of '
          f'{gaps[-1] / gaps[0]:.0f}.')
    print()
    print('  That is the opposite of the intuition. A fixed nozzle\'s visible problem at sea level')
    print('  is over-expansion, which is what causes separation and gets the attention. Its')
    print('  performance loss is dominated by under-expansion high up, where nothing dramatic')
    print('  happens and the nozzle is simply too small.')

    print()
    print(f'    {"arrangement":16s} {"recovers":>9s} {"gain [s]":>10s} {"mass":>7s}  flown')
    for name, entry in arrangements['arrangements'].items():
        print(f'    {name:16s} {entry["recovery"]:9.0%} {entry["impulseGain"]:10.2f} '
              f'{entry["massPenalty"]:7.0%}  {entry["flown"]}')

    print()
    print('  The best performing arrangement has never flown operationally, and the only')
    print('  compensating one that has works by solving an easier problem: a single deployment in')
    print('  vacuum on an upper stage, not continuous compensation through the atmosphere.')

    return {'bound': bound, 'arrangements': arrangements, 'gaps': gaps}

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, contour: dict, separation: dict, compensation: dict) -> None:

    banner('SUMMARY: THE LEVERS, RANKED')

    print()
    print(f'    {"lever":34s} {"worth [s]":>10s}   status')
    print(f'    {"altitude compensation, ideal":34s} '
          f'{compensation["bound"]["benefit"]:10.2f}   unreachable')
    print(f'    {"altitude compensation, aerospike":34s} '
          f'{compensation["arrangements"]["arrangements"]["aerospike"]["impulseGain"]:10.2f}   '
          f'never flown operationally')
    print(f'    {"bell instead of a cone":34s} {contour["coneToBell"]:10.2f}   '
          f'done on every flying engine')
    print(f'    {"a fuller bell":34s} {contour["bellToFull"]:10.2f}   '
          f'costs the length back')
    print(f'    {"Schmucker instead of Summerfield":34s} {separation["gain"]:10.2f}   '
          f'a 36 per cent change in area ratio')

    print()
    print('  The ordering is nearly the reverse of the attention each receives.')
    print()
    print('  The one large lever is altitude compensation, it has been known since the 1950s, and')
    print('  no operational vehicle has captured it. Everything a contour designer controls is')
    print('  worth a few seconds at most, and the argument most likely to be had, over which')
    print('  separation correlation to believe, is worth less than half a second.')
    print()
    print('  The contour here is Rao\'s parabolic approximation at conceptual fidelity, which is')
    print('  what the loss budget, the cooling area and the mass estimate need. The method of')
    print('  characteristics contour and the cooling channel geometry that follows it belong to')
    print('  the NOVA suite, and this does not reimplement them. The two answer different')
    print('  questions: this one is roughly what shape and how much area, that one is what are')
    print('  the coordinates.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    reportLossBudget(case)

    contour      = reportContourLever(case)
    geometry     = reportContourGeometry(case)
    separation   = reportSeparationLever(case)
    compensation = reportCompensationLever(case)

    summarise(case, contour, separation, compensation)

if __name__ == '__main__':
    main()
