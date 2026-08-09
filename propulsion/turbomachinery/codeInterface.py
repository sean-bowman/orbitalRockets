
# -- turbomachinery worked example -- #

'''

One shaft, four constraints that disagree about how fast it should turn, and a fifth thing nobody
in this sub-domain owns that decides the answer.

The pump wants speed, because specific speed and therefore efficiency rise with it and the machine
gets smaller. The turbine wants speed, because blade speed ratio rises toward its optimum. The
bearings want slowness, because DN is bore times rpm. Cavitation wants slowness hardest of all,
because NPSH required goes as speed to the four thirds, and NPSH is bought with tank pressure.

So shaft speed is not a turbopump decision. It trades turbopump mass against tank mass, and the
tank belongs to a different domain.

The fifth thing is the engine cycle, and it moves the answer by a factor of two.

    open cycle      the turbine flow is dumped overboard, so turbine efficiency is precious
                    and the optimum is 55 000 rpm

    closed cycle    the turbine flow goes to the main chamber and costs nothing, so tank mass
                    dominates and the optimum is 27 000 rpm

Nothing about the pumps changed between those two numbers. The cycle decided them, and the cycle
is chosen before any of this.

Three mass models in here are assumptions rather than data, and the conclusion moves with all
three. They are stated in the asset and named again in the output.

Run:
    python propulsion/turbomachinery/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'turbomachineryLibrary'))

from turbomachineryUtils import SUCTION_SPECIFIC_SPEED, BEARING_DN_LIMIT
from Pump import Pump, IMPELLER_TIP_SPEED_LIMIT
from Inducer import Inducer, NPSH_MARGIN
from Turbine import Turbine, BLADE_TIP_SPEED_LIMIT

ASSET = os.path.join(HERE, 'turbomachineryLibrary', 'assets', 'turbopumpShaftSpeedExample.json')

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Model helpers -- #
# ------------------------------------------------------------------------------------------------ #

def tankMass(pressure: float, volume: float, model: dict) -> float:

    '''
    Thin wall pressure vessel mass, with a shape factor covering domes, welds and non-optimum.
    '''

    return (model['tankShapeFactor'] * pressure * volume
            * model['tankMaterialDensity'] / model['tankAllowable'])

def turbopumpMass(power: float, shaftSpeed: float, model: dict) -> float:

    '''
    The common empirical scaling, mass proportional to power^0.6 over speed^0.6.
    '''

    reference = (model['turbopumpReferencePower'] ** model['turbopumpPowerExponent']
                 / model['turbopumpReferenceSpeed'] ** model['turbopumpSpeedExponent'])

    constant = model['turbopumpReferenceMass'] / reference

    return constant * power ** model['turbopumpPowerExponent'] \
        / shaftSpeed ** model['turbopumpSpeedExponent']

def buildInducer(side: dict, feed: dict, shaftSpeed: float) -> Inducer:

    inducer = Inducer()
    inducer.setInputs({'propellant':     side['propellant'],
                       'density':        side['density'],
                       'massFlow':       side['massFlow'],
                       'shaftSpeed':     shaftSpeed,
                       'vapourPressure': side['vapourPressure'],
                       'staticHead':     feed['staticHead'],
                       'lineLoss':       feed['lineLoss']})
    return inducer

def buildPump(side: dict, dischargePressure: float, shaftSpeed: float) -> Pump:

    pump = Pump()
    pump.setInputs({'propellant':       side['propellant'],
                    'density':          side['density'],
                    'massFlow':         side['massFlow'],
                    'pressureRise':     dischargePressure,
                    'shaftSpeed':       shaftSpeed,
                    'impellerMaterial': side['impellerMaterial']})
    return pump

def evaluate(case: dict, shaftSpeed: float) -> dict:

    '''
    Everything that depends on shaft speed, for both pumps and the turbine that drives them.
    '''

    duty  = case['duty']
    feed  = case['feed']
    model = case['massModel']

    tank  = 0.0
    power = 0.0
    dn    = 0.0
    sides = {}

    for name in ('oxidiser', 'fuel'):

        side = duty[name]

        inducer  = buildInducer(side, feed, shaftSpeed)
        pressure = inducer.requiredTankPressure()['tankPressure']

        pump     = buildPump(side, duty['dischargePressure'], shaftSpeed)
        impeller = pump.sizeImpeller()
        shaft    = pump.calculatePower()

        tank  += tankMass(pressure, side['tankVolume'], model)
        power += shaft['shaftPower']
        dn     = max(dn, impeller['dnNumber'])

        sides[name] = {'tankPressure': pressure,
                       'tankMass':     tankMass(pressure, side['tankVolume'], model),
                       'shaftPower':   shaft['shaftPower'],
                       'efficiency':   shaft['efficiency'],
                       'specificSpeed': pump.calculateSpecificSpeed()['specificSpeed'],
                       'diameter':     impeller['diameter'],
                       'tipSpeed':     impeller['tipSpeed'],
                       'dnNumber':     impeller['dnNumber']}

    turbine = Turbine()
    turbine.setInputs({'requiredPower':    power,
                       'inletTemperature': case['turbine']['inletTemperature'],
                       'pressureRatio':    case['turbine']['pressureRatio'],
                       'shaftSpeed':       shaftSpeed,
                       'meanDiameter':     case['turbine']['meanDiameter']})

    flow       = turbine.sizeFlow()
    efficiency = turbine.calculateEfficiency()

    dumped = flow['drivingFlow'] * duty['burnTime'] * model['gasGeneratorLostFraction']

    pumpMass = turbopumpMass(power, shaftSpeed, model)

    return {'shaftSpeed':      shaftSpeed,
            'sides':           sides,
            'tankMass':        tank,
            'turbopumpMass':   pumpMass,
            'dumpedMass':      dumped,
            'openTotal':       tank + pumpMass + dumped,
            'closedTotal':     tank + pumpMass,
            'shaftPower':      power,
            'turbineEfficiency': efficiency['efficiency'],
            'bladeSpeed':      efficiency['bladeSpeed'],
            'bladeSpeedRatio': efficiency['bladeSpeedRatio'],
            'drivingFlow':     flow['drivingFlow'],
            'dnNumber':        dn}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the duty -- #
# ------------------------------------------------------------------------------------------------ #

def reportDuty(case: dict) -> None:

    banner('1. TWO PUMPS, ONE SHAFT')

    duty = case['duty']

    print(f'  From propulsion/codeInterface.py, delivering to a '
          f'{duty["dischargePressure"] / 1.0e6:.1f} MPa engine inlet:')
    print()
    print(f'    {"":10s} {"flow [kg/s]":>12s} {"density":>9s} {"Q [l/s]":>9s} '
          f'{"p_vap [kPa]":>12s} {"tank [m3]":>10s}')

    for name in ('oxidiser', 'fuel'):
        side = duty[name]
        print(f'    {side["propellant"]:10s} {side["massFlow"]:12.2f} {side["density"]:9.0f} '
              f'{side["massFlow"] / side["density"] * 1000.0:9.2f} '
              f'{side["vapourPressure"] / 1000.0:12.0f} {side["tankVolume"]:10.2f}')

    print()
    print('  Both are driven by one turbine on one shaft, so they run at the same speed whether')
    print('  they want to or not.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: what each constraint wants -- #
# ------------------------------------------------------------------------------------------------ #

def reportConstraints(case: dict) -> dict:

    banner('2. FOUR CONSTRAINTS, PULLING TWO WAYS')

    duty = case['duty']
    feed = case['feed']

    reference = 30000.0

    print(f'    {"constraint":26s} {"wants":8s}  why')
    print(f'    {"pump specific speed":26s} {"faster":8s}  efficiency rises toward a peak it '
          f'never reaches')
    print(f'    {"turbine blade speed ratio":26s} {"faster":8s}  the optimum is 0.470 and a rocket '
          f'sits far below it')
    print(f'    {"bearing DN":26s} {"slower":8s}  bore times rpm, and it is a hard limit')
    print(f'    {"cavitation":26s} {"slower":8s}  NPSH goes as speed to the four thirds')

    print()
    print(f'  At {reference:.0f} rpm, what each pump can tolerate on 30 m of available NPSH:')
    print()
    print(f'    {"":10s} {"Nss":>7s} {"max rpm":>10s}   note')

    ceilings = {}

    for name in ('oxidiser', 'fuel'):

        side    = duty[name]
        inducer = buildInducer(side, feed, reference)

        ceiling = inducer.maximumShaftSpeed(availableNpsh = 30.0)

        ceilings[name] = ceiling['maximumRpm']

        note = ('cryogenic, so thermodynamic suppression helps'
                if inducer.suppressionFactor() > 1.0 else 'storable, no suppression')

        print(f'    {side["propellant"]:10s} {inducer.tolerableSuctionSpecificSpeed():7.1f} '
              f'{ceiling["maximumRpm"]:10.0f}   {note}')

    print()
    print(f'  The two land within {abs(ceilings["oxidiser"] - ceilings["fuel"]) / max(ceilings.values()) * 100.0:.0f} '
          f'per cent of each other, which is a coincidence of this engine rather')
    print('  than a rule. The oxidiser has more than twice the volumetric flow, which hurts, and it')
    print('  is cryogenic, which helps by almost exactly as much.')

    return ceilings

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the tank pays, and it is not the pump's fault -- #
# ------------------------------------------------------------------------------------------------ #

def reportTankChain(case: dict) -> None:

    banner('3. THE TANK PAYS FOR SHAFT SPEED, AND VAPOUR PRESSURE DECIDES HOW MUCH')

    duty  = case['duty']
    feed  = case['feed']
    model = case['massModel']

    print(f'    {"rpm":>7s} {"LOX tank [kPa]":>15s} {"RP-1 tank [kPa]":>16s} '
          f'{"LOX [kg]":>9s} {"RP-1 [kg]":>10s}')

    for speed in (15000.0, 30000.0, 45000.0, 60000.0):

        row = []
        for name in ('oxidiser', 'fuel'):
            side     = duty[name]
            pressure = buildInducer(side, feed, speed).requiredTankPressure()['tankPressure']
            row.append((pressure, tankMass(pressure, side['tankVolume'], model)))

        print(f'    {speed:7.0f} {row[0][0] / 1000.0:15.0f} {row[1][0] / 1000.0:16.0f} '
              f'{row[0][1]:9.1f} {row[1][1]:10.1f}')

    print()
    print('  The oxidiser tank costs roughly four times the fuel tank at every speed, and the pump')
    print('  is barely responsible. LOX boils at 101 kPa and RP-1 at 2 kPa, so the LOX tank starts')
    print('  a hundred kilopascals in debt before any cavitation margin is added.')
    print()
    print('  That is worth stating plainly: on a cryogenic stage, most of the tank pressure is not')
    print('  buying cavitation margin at all. It is holding the propellant liquid.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the optimum, and the cycle that moves it -- #
# ------------------------------------------------------------------------------------------------ #

def sweepShaftSpeed(case: dict) -> dict:

    banner('4. THE OPTIMUM SHAFT SPEED DEPENDS ON THE ENGINE CYCLE')

    sweep = case['sweep']

    speeds = np.arange(sweep['lower'], sweep['upper'] + 1.0, sweep['step'])

    results = [evaluate(case, float(speed)) for speed in speeds]

    openTotals   = [entry['openTotal'] for entry in results]
    closedTotals = [entry['closedTotal'] for entry in results]

    openBest   = results[int(np.argmin(openTotals))]
    closedBest = results[int(np.argmin(closedTotals))]

    print(f'    {"rpm":>7s} {"tank":>7s} {"tpump":>7s} {"dumped":>8s} {"OPEN":>8s} '
          f'{"CLOSED":>8s} {"turb eta":>9s} {"blade U":>8s}')

    for entry in results:
        if int(entry['shaftSpeed']) % 6000 != 4000:
            continue
        print(f'    {entry["shaftSpeed"]:7.0f} {entry["tankMass"]:7.1f} '
              f'{entry["turbopumpMass"]:7.1f} {entry["dumpedMass"]:8.1f} '
              f'{entry["openTotal"]:8.1f} {entry["closedTotal"]:8.1f} '
              f'{entry["turbineEfficiency"]:8.1%} {entry["bladeSpeed"]:8.0f}')

    print()
    print(f'  Open cycle optimum   {openBest["shaftSpeed"]:7.0f} rpm at '
          f'{openBest["openTotal"]:.1f} kg')
    print(f'  Closed cycle optimum {closedBest["shaftSpeed"]:7.0f} rpm at '
          f'{closedBest["closedTotal"]:.1f} kg')
    print(f'  Ratio of optimum speeds: '
          f'{openBest["shaftSpeed"] / closedBest["shaftSpeed"]:.2f}')

    print()
    print('  Nothing about the pumps changed between those two numbers.')
    print()
    print('  On an open cycle the turbine flow is thrown overboard, so turbine efficiency is worth')
    print('  real propellant and the answer is to spin fast and accept the tank pressure. On a')
    print('  closed cycle that flow goes to the main chamber and costs nothing, so there is no')
    print('  reason to chase turbine efficiency and the tank mass wins.')
    print()
    print('  The cycle is chosen before any of this, in engineCycles. It is not usually thought of')
    print('  as a turbopump decision and it sets the turbopump shaft speed to within a factor of')
    print('  two.')

    # how flat is the optimum
    openMinimum = openBest['openTotal']
    within      = [entry for entry in results if entry['openTotal'] < openMinimum * 1.05]

    print()
    print(f'  The open cycle optimum is broad: everything from '
          f'{min(entry["shaftSpeed"] for entry in within):.0f} to '
          f'{max(entry["shaftSpeed"] for entry in within):.0f} rpm')
    print('  is within five per cent of the minimum. The penalty is violently asymmetric, though.')

    slow = next(entry for entry in results if entry['shaftSpeed'] >= 0.5 * openBest['shaftSpeed'])

    print(f'  Half the optimum speed costs '
          f'{(slow["openTotal"] / openMinimum - 1.0) * 100.0:.0f} per cent, and being fast costs '
          f'almost nothing.')
    print('  Err fast, up to the hard limits.')

    return {'results': results, 'openBest': openBest, 'closedBest': closedBest}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the hard limits -- #
# ------------------------------------------------------------------------------------------------ #

def reportLimits(case: dict, sweep: dict) -> None:

    banner('5. WHAT ACTUALLY STOPS YOU')

    openBest = sweep['openBest']

    print('  The optimum is a soft minimum. These are not.')
    print()
    print(f'    {"limit":26s} {"value":>10s} {"at optimum":>12s}   binding')

    blade = openBest['bladeSpeed']
    dn    = openBest['dnNumber']

    print(f'    {"turbine blade speed":26s} {BLADE_TIP_SPEED_LIMIT:10.0f} {blade:12.0f}   '
          f'{"YES" if blade > 0.9 * BLADE_TIP_SPEED_LIMIT else "no"}')
    print(f'    {"bearing DN":26s} {BEARING_DN_LIMIT / 1.0e6:10.2f} {dn / 1.0e6:12.2f}   '
          f'{"YES" if dn > 0.9 * BEARING_DN_LIMIT else "no"}')

    for name in ('oxidiser', 'fuel'):
        side  = case['duty'][name]
        entry = openBest['sides'][name]
        limit = IMPELLER_TIP_SPEED_LIMIT[side['impellerMaterial']]['limit']
        print(f'    {side["propellant"] + " impeller tip":26s} {limit:10.0f} '
              f'{entry["tipSpeed"]:12.0f}   '
              f'{"YES" if entry["tipSpeed"] > 0.9 * limit else "no"}')

    print()
    print(f'  The turbine blade reaches its {BLADE_TIP_SPEED_LIMIT:.0f} m/s stress limit at')
    print(f'  {blade:.0f} m/s, essentially at the open cycle optimum. That is the constraint that')
    print('  actually decides an open cycle shaft speed, and the optimum happens to sit against')
    print('  it rather than being reached freely.')
    print()
    print('  The pump impellers are nowhere near their limits, which is the usual outcome: on a')
    print('  moderate pressure engine the pump is not the hard part of a turbopump. The turbine is.')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, sweep: dict) -> None:

    banner('SUMMARY: THE CYCLE SETS THE SHAFT SPEED')

    openBest   = sweep['openBest']
    closedBest = sweep['closedBest']

    print()
    print(f'    {"cycle":16s} {"optimum rpm":>12s} {"mass [kg]":>11s}   what dominates')
    print(f'    {"open":16s} {openBest["shaftSpeed"]:12.0f} {openBest["openTotal"]:11.1f}   '
          f'dumped turbine propellant')
    print(f'    {"closed":16s} {closedBest["shaftSpeed"]:12.0f} {closedBest["closedTotal"]:11.1f}'
          f'   tank pressure')

    print()
    print('  Shaft speed is not a turbopump decision. It trades turbopump mass against tank mass,')
    print('  and it is set by a cycle choice made in another sub-domain before this one starts.')
    print()
    print('  Three mass models in this example are assumptions rather than data: the tank pressure')
    print('  vessel scaling, the turbopump mass correlation, and the fraction of dumped propellant')
    print('  charged as lost. The factor of two between the two optima is robust to all three,')
    print('  because it comes from one term being present or absent rather than from its size. The')
    print('  absolute masses are not.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    reportDuty(case)
    reportConstraints(case)
    reportTankChain(case)

    sweep = sweepShaftSpeed(case)

    reportLimits(case, sweep)
    summarise(case, sweep)

if __name__ == '__main__':
    main()
