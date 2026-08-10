
# -- electricalPower worked example -- #

'''

An upper stage electrical system, and four results that are each the opposite of the obvious one.

**The load everyone worries about is not the load that dominates.** The propellant heaters get the
attention, and on this stage avionics running continuously at 35 W consumes twice their energy,
because a load at full duty for the whole mission beats a larger load that cycles. The heater is
still the number worth checking, for a different reason: it is the largest single *uncertainty* in
the budget, because its duty cycle is a thermal assumption rather than an electrical quantity.

**The energy driver and the peak driver are different loads.** Avionics sizes the battery and the
thrust vector actuators size the harness and the switching, so effort spent on one buys nothing on
the other.

**Voltage drop chooses the wire gauge, not current.** Ampacity says 20 AWG and voltage drop says
14, which is six gauge steps and four times the copper. A harness sized on current would not
function.

**Peak and hold gives three quarters of the valve energy back** for the cost of a resistor and a
transistor, because power goes as the square of current.

And underneath all of it: the nameplate battery is 1.85 times the energy actually delivered, before
any margin, because depth of discharge and cold multiply.

Run:
    python electricalPower/codeInterface.py

Author: Sean Bowman
Date:   10/08/2026

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

sys.path.insert(0, os.path.join(HERE, 'electricalPowerLibrary'))

from powerUtils import (BATTERY_CHEMISTRIES, wireArea, wireDiameter, HarnessError,
                        PowerBudgetError)
from PowerBudget import PowerBudget
from Battery import Battery
from HarnessSizing import HarnessSizing
from SolenoidDrive import SolenoidDrive

ASSET = os.path.join(HERE, 'electricalPowerLibrary', 'assets', 'upperStagePowerExample.json')

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

def buildBudget(case: dict) -> PowerBudget:

    budget = PowerBudget()
    budget.setInputs({'loads':  [dict(load) for load in case['loads']],
                      'phases': [dict(phase) for phase in case['phases']]})

    return budget

def buildHarness(case: dict, current: float = None) -> HarnessSizing:

    entry = case['harness']

    harness = HarnessSizing()
    harness.setInputs({'busVoltage': case['bus']['voltage'],
                       'current':    current if current is not None else entry['current'],
                       'length':     entry['length'],
                       'bundleSize': entry['bundleSize'],
                       'altitude':   entry['altitude']})

    return harness

def buildSolenoid(case: dict) -> SolenoidDrive:

    entry = case['solenoid']

    valve = SolenoidDrive()
    valve.setInputs({'busVoltage':      case['bus']['voltage'],
                     'coilResistance':  entry['coilResistance'],
                     'coilInductance':  entry['coilInductance'],
                     'coilTemperature': entry['coilTemperature'],
                     'holdFraction':    entry['holdFraction'],
                     'openDuration':    entry['openDuration']})

    return valve

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the load that is not an electrical load -- #
# ------------------------------------------------------------------------------------------------ #

def reportBudget(case: dict) -> dict:

    banner('1. THE LOAD THAT DOMINATES IS NOT THE ONE ANYBODY WORRIES ABOUT')

    budget = buildBudget(case)

    rollup  = budget.rollUp()
    drivers = budget.identifyDrivers()

    print(f'    {"load":28s} {"power [W]":>10s} {"energy [W h]":>14s} {"share":>8s}')
    for name, entry in sorted(rollup['byLoad'].items(), key = lambda item: -item[1]['energy']):
        print(f'    {name:28s} {entry["power"]:10.0f} {entry["energy"] / 3600.0:14.2f} '
              f'{entry["energy"] / rollup["deliveredEnergy"]:8.1%}')

    print()
    for finding in drivers['findings']:
        print(f'  - {finding}')

    heaterShare = (rollup['byLoad']['propellant line heaters']['energy']
                   / rollup['deliveredEnergy'])

    print()
    print(f'  The propellant heaters are the load that gets the attention, and they are '
          f'{heaterShare:.0%} of the')
    print('  energy rather than the largest. A continuous 35 W avionics load beats a 42 W heater')
    print('  that cycles, because duty cycle multiplies and power does not.')
    print()
    print('  **The heater is still the number worth checking, for a different reason.** It is a')
    print('  thermal requirement that arrives as an electrical one: its duty cycle depends on an')
    print('  attitude, an orbit and an insulation design, and none of those is under the control')
    print('  of the person sizing the battery. So it is the largest uncertainty even though it is')
    print('  not the largest load.')

    sensitivity = budget.dutyCycleSensitivity('propellant line heaters')

    print()
    print(f'    {"heater duty":>13s} {"mission energy [W h]":>22s}')
    for duty, energy in sensitivity['results'].items():
        print(f'    {duty:12.0%} {energy / 3600.0:22.1f}')

    print()
    print(f'  Sweeping that one assumption across its plausible range moves the mission energy by')
    print(f'  {sensitivity["spanFraction"]:.0%}, on a load that is only {heaterShare:.0%} of it. '
          f'**That swing is larger than the 25 per cent')
    print('  energy margin**, and it comes from an input this domain does not own.')
    print()
    print('  So the ranking by energy and the ranking by uncertainty are different lists, and the')
    print('  second one is the one worth acting on.')

    return {'budget': budget, 'rollup': rollup, 'drivers': drivers, 'sensitivity': sensitivity}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the nameplate is not the capacity -- #
# ------------------------------------------------------------------------------------------------ #

def reportBattery(case: dict, missionEnergy: float, peakPower: float) -> dict:

    banner('2. THE NAMEPLATE IS NOT THE CAPACITY')

    entry = case['battery']

    battery = Battery()
    battery.setInputs({'chemistry':     entry['chemistry'],
                       'busVoltage':    case['bus']['voltage'],
                       'missionEnergy': missionEnergy,
                       'peakPower':     peakPower,
                       'temperature':   entry['temperature'],
                       'cycleClass':    entry['cycleClass'],
                       'energyMargin':  entry['energyMargin']})

    sized = battery.sizePack()

    print(f'    {"step":34s} {"energy [W h]":>14s}')
    print(f'    {"delivered to the loads":34s} {missionEnergy / 3600.0:14.1f}')
    print(f'    {"plus margin":34s} {sized["withMargin"] / 3600.0:14.1f}')
    print(f'    {"divided by usable fraction":34s} {sized["nameplateEnergy"] / 3600.0:14.1f}')

    print()
    for finding in sized['findings']:
        print(f'  - {finding}')

    print()
    print(f'  **The nameplate is {sized["oversizeFactor"]:.2f} times the energy actually '
          f'delivered.** Neither deration is a')
    print('  margin: they are the difference between what the label says and what the battery')
    print('  does, and the margin sits on top of them.')

    rate = battery.checkDischargeRate()

    print()
    for finding in rate['findings']:
        print(f'  - {finding}')

    comparison = battery.compareChemistries()

    print()
    print(f'    {"chemistry":26s} {"pack [kg]":>11s} {"rate limit":>12s}   viable')
    for name, result in comparison['results'].items():
        print(f'    {name:26s} {result["packMass"]:11.2f} {result["rateLimit"]:11.1f} C   '
              f'{"yes" if result.get("rateAdequate", True) else "no"}')

    print()
    print('  Lithium thionyl chloride has two and a half times the specific energy and cannot')
    print('  supply the current. The chemistry choice is decided by the discharge rate, which is')
    print('  the only place in this stage where chemistry changes the answer at all.')

    return {'battery': battery, 'sized': sized, 'rate': rate, 'comparison': comparison}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: what actually chooses the wire -- #
# ------------------------------------------------------------------------------------------------ #

def reportHarness(case: dict) -> dict:

    banner('3. VOLTAGE DROP CHOOSES THE WIRE, NOT CURRENT')

    harness = buildHarness(case)

    sized = harness.sizeGauge()

    print(f'    {"AWG":>5s} {"derated [A]":>13s} {"drop [V]":>10s} {"fraction":>10s}')
    for gauge, entry in sorted(sized['detail'].items()):
        print(f'    {gauge:5d} {entry["derated"]:13.1f} {entry["drop"]:10.2f} '
              f'{entry["dropFraction"]:10.1%}')

    print()
    for finding in sized['findings']:
        print(f'  - {finding}')

    print()
    print('  The reason is geometry rather than electricity. A launch vehicle harness is long')
    print('  relative to its currents, so voltage drop scales with length and ampacity does not.')

    mass = harness.calculateMass(case['harness']['runs'], case['harness']['connectors'])

    print()
    print(f'    {"contribution":22s} {"mass [kg]":>11s} {"share":>8s}')
    print(f'    {"wire":22s} {mass["wireMass"]:11.2f} '
          f'{mass["wireMass"] / mass["totalMass"]:8.0%}')
    print(f'    {"connectors":22s} {mass["connectorMass"]:11.2f} '
          f'{mass["connectorMass"] / mass["totalMass"]:8.0%}')
    print(f'    {"total":22s} {mass["totalMass"]:11.2f}')

    print()
    for finding in mass['findings']:
        print(f'  - {finding}')

    voltages = harness.compareBusVoltage()

    print()
    print(f'    {"bus [V]":>9s} {"current [A]":>13s} {"governing AWG":>15s} {"copper area":>13s}')
    for voltage, result in voltages['results'].items():
        if result is None:
            print(f'    {voltage:9.0f} {"":>13s} {"does not close":>15s}')
            continue
        print(f'    {voltage:9.0f} {result["current"]:13.2f} {result["governing"]:15d} '
              f'{result["area"] * 1.0e6:12.2f} mm2')

    print()
    print('  Power is fixed, so current falls with bus voltage and the allowed drop rises with it.')
    print('  Both move the same way, so **the copper falls roughly with the square of bus')
    print('  voltage**. That is the cleanest argument for a higher bus and it is why anything with')
    print('  a long harness runs at more than 28 V.')

    return {'harness': harness, 'sized': sized, 'mass': mass, 'voltages': voltages}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: three quarters back for a resistor and a transistor -- #
# ------------------------------------------------------------------------------------------------ #

def reportSolenoid(case: dict) -> dict:

    banner('4. THREE QUARTERS OF THE VALVE ENERGY, BACK FOR ALMOST NOTHING')

    valve = buildSolenoid(case)

    drive = valve.calculateDrive()

    strategies = valve.compareDriveStrategies()

    count = case['solenoid']['valveCount']

    print(f'    {"quantity":30s} {"value":>12s}')
    print(f'    {"coil resistance at 20 C":30s} {drive["coldResistance"]:9.1f} ohm')
    print(f'    {"coil resistance hot":30s} {drive["hotResistance"]:9.1f} ohm')
    print(f'    {"pull-in current cold":30s} {drive["pullInCold"]:9.3f} A')
    print(f'    {"pull-in current hot":30s} {drive["pullInHot"]:9.3f} A')
    print(f'    {"force ratio hot to cold":30s} {drive["forceRatio"]:12.2f}')
    print(f'    {"continuous power per valve":30s} {drive["continuousPower"]:9.2f} W')
    print(f'    {"hold power per valve":30s} {drive["holdPower"]:9.2f} W')

    print()
    for finding in strategies['findings']:
        print(f'  - {finding}')

    print()
    print(f'  Across {count} valves that is '
          f'{(strategies["continuousPower"] - strategies["holdPower"]) * count:.0f} W off the peak '
          f'and')
    print(f'  {strategies["energySaved"] * count / 3600.0:.2f} W h off the burn, for the cost of a '
          f'resistor and a transistor per valve.')

    print()
    print('  And the hot coil is the design case, not the cold one:')
    print()
    print(f'  - A coil at {valve.coilTemperature:.0f} C has {drive["resistanceRise"]:.0%} more '
          f'resistance than at 20, pulls')
    print(f'    {drive["currentLoss"]:.0%} less current, and makes about '
          f'{1.0 - drive["forceRatio"]:.0%} less force. A valve that works cold and')
    print('    marginally hot is the classic version of this, and it is found on a hot day.')

    flyback = valve.calculateFlyback()

    print()
    for finding in flyback['findings']:
        print(f'  - {finding}')

    return {'valve': valve, 'drive': drive, 'strategies': strategies, 'flyback': flyback}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: what this domain does not own -- #
# ------------------------------------------------------------------------------------------------ #

def reportBoundaries(case: dict) -> None:

    banner('5. THE FIRING CIRCUIT, WHICH THIS DOMAIN DOES NOT OWN')

    print('  The pyro bus is on the load list at 120 W and it sizes nothing, because it draws that')
    print('  for milliseconds. What it does need is a no-fire and all-fire assessment, and that')
    print('  lives in mechanismsAndSeparation rather than here.')
    print()
    print('  `PyroCircuit` was planned for this library and deliberately not built.')
    print('  `PyrotechnicInitiator` in mechanismsAndSeparation already computes the firing current')
    print('  through the harness, the no-fire margin against stray energy, and the parallel-device')
    print('  arithmetic that catches a circuit sized for one initiator and flown with two.')
    print()
    print('  Two implementations of the same circuit with nothing enforcing agreement between them')
    print('  is the failure this repository has avoided in five other places, and the boundary is')
    print('  drawn the same way here: this domain supplies the bus voltage and the harness')
    print('  resistance, and that domain decides whether the device fires.')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(budget: dict, battery: dict, harness: dict, solenoid: dict) -> None:

    banner('SUMMARY: FOUR ANSWERS THAT ARE NOT THE OBVIOUS ONE')

    print()
    print(f'    {"question":46s} {"answer":>22s}')
    print(f'    {"what drives the mission energy":46s} '
          f'{budget["drivers"]["energyDriver"]:>22s}')
    print(f'    {"what drives the peak power":46s} '
          f'{budget["drivers"]["peakDriver"]:>22s}')
    print(f'    {"what drives the uncertainty":46s} '
          f'{"propellant heaters":>22s}')
    print(f'    {"heater duty cycle swing on mission energy":46s} '
          f'{budget["sensitivity"]["spanFraction"]:>21.0%}')
    print(f'    {"battery nameplate over energy delivered":46s} '
          f'{battery["sized"]["oversizeFactor"]:>21.2f}x')
    print(f'    {"gauge from ampacity":46s} '
          f'{harness["sized"]["ampacityGauge"]:>19d} AWG')
    print(f'    {"gauge from voltage drop":46s} '
          f'{harness["sized"]["dropGauge"]:>19d} AWG')
    print(f'    {"harness mass, counted":46s} '
          f'{harness["mass"]["totalMass"]:>20.2f} kg')
    print(f'    {"peak and hold saving per valve":46s} '
          f'{solenoid["strategies"]["powerSaving"]:>21.0%}')

    print()
    print('  Three of those nine are decided outside this domain. The heater duty cycle is a')
    print('  thermal design, the bus voltage is an architecture decision, and the firing circuit')
    print('  belongs to mechanisms. **The electrical system is the one that touches everything,')
    print('  which means most of its inputs are somebody else\'s outputs.**')
    print()
    print('  What this domain does not model, and says so rather than approximating:')
    print()
    print('    Grounding topology and EMI. Single point against multipoint is a topology decision')
    print('    with no scalar answer, and emissions and susceptibility are measured against')
    print('    MIL-STD-461 rather than computed. Both are documented and neither is modelled.')
    print()
    print('    Fault current and protection coordination. Fusing and current limiting need a')
    print('    source impedance model this domain does not carry.')
    print()
    print('    Battery thermal runaway. It is a safety analysis rather than an energy one.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    budget = reportBudget(case)

    battery = reportBattery(case,
                            budget['rollup']['sourceEnergy'],
                            budget['rollup']['peakPower'])

    harness  = reportHarness(case)
    solenoid = reportSolenoid(case)

    reportBoundaries(case)

    summarise(budget, battery, harness, solenoid)

if __name__ == '__main__':
    main()
