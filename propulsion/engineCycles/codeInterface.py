
# -- engineCycles worked example -- #

'''

Which cycle the hub's 100 kN booster should use, and the pressure ceiling that rules one of them
out before any other consideration gets a say.

The cycle question looks like a preference and is not. Each candidate is eliminated or admitted by
a different constraint, and only one of the four is decided by anything resembling a trade.

    pressure fed        eliminated by tank mass. The tank has to hold what the pump would deliver
    expander            eliminated by a heat balance. There is not enough chamber wall
    staged combustion   admitted, and it costs pump discharge pressure
    gas generator       admitted, and it costs impulse

The expander case is the one worth the arithmetic. Its turbine runs on heat the chamber wall gave
up, and that heat is fixed by the wall area. Chamber pressure raises the pump power almost linearly
and lowers the wall area, so **the ratio of available to required power falls as roughly the
inverse 1.2 power of chamber pressure.** There is a ceiling, this engine is well above it, and the
ceiling for this propellant and scale falls between 4 and 5 MPa.

RL10, the best known expander cycle engine, runs at 4.4 MPa.

Run:
    python propulsion/engineCycles/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'engineCyclesLibrary'))
sys.path.insert(0, os.path.join(ROOT, 'propulsion', 'combustionDevices',
                                'combustionDevicesLibrary'))
sys.path.insert(0, os.path.join(ROOT, 'propulsion', 'turbomachinery', 'turbomachineryLibrary'))

from cycleUtils import ENGINE_CYCLES, pressureLadder
from EngineCycle import EngineCycle
from PowerBalance import PowerBalance

from RegenerativeCooling import RegenerativeCooling
from Pump import Pump

ASSET = os.path.join(HERE, 'engineCyclesLibrary', 'assets', 'cycleSelectionExample.json')

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

def pumpPowerFor(case: dict, dischargePressure: float) -> float:

    '''
    Total shaft power both pumps need to reach a given discharge pressure.
    '''

    engine = case['engine']

    total = 0.0

    for density, flow, material in ((1141.0, engine['oxidiserFlow'], 'Monel K-500'),
                                    (810.0,  engine['fuelFlow'],     'titanium')):

        pump = Pump()
        pump.setInputs({'density':          density,
                        'massFlow':         flow,
                        'pressureRise':     dischargePressure,
                        'shaftSpeed':       case['shaftSpeed'],
                        'impellerMaterial': material})

        total += pump.calculatePower()['shaftPower']

    return total

def jacketHeatAt(case: dict, chamberPressure: float) -> dict:

    '''

    The heat the chamber jacket gives up, at a chamber pressure the engine has been rescaled to.

    Holding thrust constant, the throat area goes as the inverse of chamber pressure, so every
    length scales as the inverse square root of it. That is what shrinks the jacket as the pressure
    rises, and it is half of why the expander has a ceiling.

    '''

    engine = case['engine']

    scale = np.sqrt(engine['chamberPressure'] / chamberPressure)

    cooling = RegenerativeCooling()
    cooling.setInputs({'combination':      engine['combination'],
                       'chamberPressure':  chamberPressure,
                       'throatDiameter':   engine['throatDiameter'] * scale,
                       'contractionRatio': engine['contractionRatio'],
                       'areaRatio':        engine['areaRatio'],
                       'barrelLength':     engine['barrelLength'] * scale,
                       'convergentLength': engine['convergentLength'] * scale,
                       'divergentLength':  engine['divergentLength'] * scale,
                       'coolantFlow':      engine['fuelFlow']})

    heat = cooling.calculateHeatLoad()

    return {'heat': heat['totalLoad'], 'area': heat['totalArea'],
            'throatDiameter': engine['throatDiameter'] * scale}

def tankMass(pressure: float, volume: float, model: dict) -> float:

    return model['shapeFactor'] * pressure * volume * model['materialDensity'] / model['allowable']

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the pressure ladder -- #
# ------------------------------------------------------------------------------------------------ #

def reportLadder(case: dict) -> dict:

    banner('1. WHERE THE TURBINE EXHAUST GOES DECIDES THE PUMP')

    engine = case['engine']

    print(f'  A {engine["thrust"] / 1000.0:.0f} kN engine at '
          f'{engine["chamberPressure"] / 1.0e6:.0f} MPa, {engine["combination"]}.')
    print()
    print(f'    {"cycle":24s} {"discharge":>10s} {"ratio":>7s} {"turbine in":>11s} '
          f'{"turbine out":>12s}')

    ladders = {}

    for name in case['candidates']:

        ladder = pressureLadder(engine['chamberPressure'], name)
        ladders[name] = ladder

        inlet = ('-' if ladder['turbineInlet'] is None
                 else f'{ladder["turbineInlet"] / 1.0e6:.1f}')
        exit_ = ('-' if ladder['turbineExit'] is None
                 else f'{ladder["turbineExit"] / 1.0e6:.1f}')

        print(f'    {name:24s} {ladder["dischargePressure"] / 1.0e6:10.1f} '
              f'{ladder["dischargeRatio"]:7.2f} {inlet:>11s} {exit_:>12s}')

    print()
    print('  An open cycle turbine exhausts overboard, so the pump only has to reach the chamber.')
    print('  A closed cycle turbine hands its exhaust to the main injector, so the pump has to')
    print('  reach above the turbine inlet instead. That is the whole reason a staged combustion')
    print('  pump runs at twice chamber pressure and a gas generator pump at a quarter above it.')

    return ladders

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: what each cycle costs -- #
# ------------------------------------------------------------------------------------------------ #

def reportCosts(case: dict, ladders: dict) -> dict:

    banner('2. WHAT EACH CYCLE COSTS')

    engine = case['engine']
    model  = case['tankModel']

    print(f'    {"cycle":24s} {"Isp [s]":>9s} {"penalty":>9s} {"pump MW":>9s} '
          f'{"drive %":>9s} {"tank kg":>9s}')

    results = {}

    for name in case['candidates']:

        ladder = ladders[name]

        cycle = EngineCycle()
        cycle.setInputs({'cycle':           name,
                         'chamberPressure': engine['chamberPressure'],
                         'idealImpulse':    engine['idealImpulse'],
                         'turbineFlowFraction':
                             0.0 if not ENGINE_CYCLES[name]['hasTurbomachinery'] else 0.035})

        impulse = cycle.calculateImpulseDelivered()

        entry = {'impulse': impulse['deliveredImpulse'], 'penalty': impulse['penalty']}

        if ENGINE_CYCLES[name]['hasTurbomachinery']:

            power = pumpPowerFor(case, ladder['dischargePressure'])

            balance = PowerBalance()
            balance.setInputs({'cycle':           name,
                               'chamberPressure': engine['chamberPressure'],
                               'totalFlow':       engine['totalFlow'],
                               'pumpPower':       power})

            driving = balance.calculateDrivingFlow()

            entry['pumpPower']    = power
            entry['driveFraction'] = driving['flowFraction']
            entry['tankMass']     = tankMass(0.3e6, model['oxidiserVolume'], model) \
                + tankMass(0.15e6, model['fuelVolume'], model)

        else:
            entry['pumpPower']     = 0.0
            entry['driveFraction'] = 0.0
            entry['tankMass']      = (tankMass(ladder['dischargePressure'],
                                               model['oxidiserVolume'], model)
                                      + tankMass(ladder['dischargePressure'],
                                                 model['fuelVolume'], model))

        results[name] = entry

        print(f'    {name:24s} {entry["impulse"]:9.1f} {entry["penalty"]:9.2%} '
              f'{entry["pumpPower"] / 1.0e6:9.3f} {entry["driveFraction"]:9.1%} '
              f'{entry["tankMass"]:9.1f}')

    pressureFed = results.get('pressure fed')
    pumped      = results['gas generator']

    if pressureFed:
        print()
        print(f'  The pressure fed tank is {pressureFed["tankMass"] / pumped["tankMass"]:.0f} '
              f'times the mass of a pumped one, because it has to hold what the pump would have')
        print('  delivered. That is the trade in one number and it is why pressure fed systems are')
        print('  upper stages, reaction control and nothing large.')

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the expander ceiling -- #
# ------------------------------------------------------------------------------------------------ #

def expanderCeiling(case: dict) -> dict:

    banner('3. THE EXPANDER CEILING')

    engine = case['engine']

    print('  An expander turbine runs on heat the chamber wall gave up. That heat is fixed by the')
    print('  wall area, and the wall shrinks as chamber pressure rises at constant thrust.')
    print()
    print(f'    {"Pc [MPa]":>9s} {"throat [mm]":>12s} {"jacket [MW]":>12s} {"pump [MW]":>10s} '
          f'{"avail [MW]":>11s} {"margin":>8s}  closes')

    rows = []

    for pressure in case['expanderSweep']['pressures']:

        jacket = jacketHeatAt(case, pressure)

        ladder = pressureLadder(pressure, 'expander')
        power  = pumpPowerFor(case, ladder['dischargePressure'])

        balance = PowerBalance()
        balance.setInputs({'cycle':           'expander',
                           'chamberPressure': pressure,
                           'totalFlow':       engine['totalFlow'],
                           'pumpPower':       power,
                           'availableHeat':   jacket['heat']})

        closure = balance.checkClosure()

        rows.append({'pressure': pressure, 'jacket': jacket['heat'], 'pumpPower': power,
                     'available': closure['availablePower'], 'margin': closure['margin'],
                     'closes': closure['closes'],
                     'throatDiameter': jacket['throatDiameter']})

        print(f'    {pressure / 1.0e6:9.1f} {jacket["throatDiameter"] * 1000.0:12.1f} '
              f'{jacket["heat"] / 1.0e6:12.2f} {power / 1.0e6:10.3f} '
              f'{closure["availablePower"] / 1.0e6:11.3f} {closure["margin"]:8.2f}  '
              f'{closure["closes"]}')

    closing = [row for row in rows if row['closes']]
    failing = [row for row in rows if not row['closes']]

    ceiling = (max(row['pressure'] for row in closing) if closing else None)
    firstFail = (min(row['pressure'] for row in failing) if failing else None)

    print()
    if ceiling and firstFail:
        print(f'  The ceiling is between {ceiling / 1.0e6:.1f} and {firstFail / 1.0e6:.1f} MPa.')
        print()
        print('  Read the columns rather than the verdict. The jacket heat barely moves across the')
        print(f'  whole sweep, {rows[0]["jacket"] / 1.0e6:.2f} MW down to '
              f'{rows[-1]["jacket"] / 1.0e6:.2f} MW, because the flux rises as the area falls and')
        print('  the two nearly cancel. The pump power rises almost linearly with pressure. So the')
        print('  margin collapses from one side only.')

        first, last = rows[0], rows[-1]
        pressureRatio = last['pressure'] / first['pressure']
        marginRatio   = first['margin'] / last['margin']

        print()
        print(f'  Over a {pressureRatio:.0f}x pressure increase the margin falls by '
              f'{marginRatio:.1f}x, which is close to the')
        print(f'  {np.log(marginRatio) / np.log(pressureRatio):.1f} power the scaling argument '
              f'predicts: heat goes as area times flux, roughly')
        print('  constant, and pump power goes as pressure.')

    print()
    print('  RL10, the best known expander cycle engine, runs at 4.4 MPa. That is not a')
    print('  coincidence and it is not a coincidence that expander cycles are upper stage engines.')

    return {'rows': rows, 'ceiling': ceiling, 'firstFailure': firstFail}

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, costs: dict, expander: dict) -> None:

    banner('SUMMARY: THREE ELIMINATIONS AND ONE TRADE')

    engine = case['engine']

    print()
    print(f'    {"cycle":24s} {"verdict":14s}  decided by')
    print(f'    {"pressure fed":24s} {"eliminated":14s}  tank mass, '
          f'{costs["pressure fed"]["tankMass"]:.0f} kg of pressure vessel')
    print(f'    {"expander":24s} {"eliminated":14s}  heat balance, ceiling near '
          f'{expander["ceiling"] / 1.0e6:.0f} MPa against a '
          f'{engine["chamberPressure"] / 1.0e6:.0f} MPa chamber')
    print(f'    {"staged combustion":24s} {"admitted":14s}  costs pump discharge, '
          f'{costs["staged combustion"]["pumpPower"] / 1.0e6:.2f} MW')
    print(f'    {"gas generator":24s} {"admitted":14s}  costs impulse, '
          f'{costs["gas generator"]["penalty"]:.1%}')

    print()
    print('  Only the last two are a trade. The other two were decided by a constraint that has')
    print('  nothing to do with preference, and both were decided before any performance number')
    print('  was compared.')
    print()
    print('  That is the useful shape of a cycle selection: most of the candidates are eliminated')
    print('  by arithmetic, and the remaining choice is between paying in pump pressure and paying')
    print('  in impulse.')
    print()
    print('  The turbomachinery sub-domain shows the other end of this. The same choice moves the')
    print('  optimum turbopump shaft speed by a factor of two, from 27 000 rpm closed to 55 000')
    print('  open, which is not usually thought of as a cycle consequence.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    ladders  = reportLadder(case)
    costs    = reportCosts(case, ladders)
    expander = expanderCeiling(case)

    summarise(case, costs, expander)

if __name__ == '__main__':
    main()
