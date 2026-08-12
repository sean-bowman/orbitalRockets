
# -- avionicsAndGNC worked example -- #

'''

The avionics of one ascent: what the navigation knows, what the control can do, what gets recorded.

Three results, and the first is the one worth carrying out of this domain.

**The navigation error is dominated by the gyroscope, not the accelerometer.** An attitude error
tilts the accelerometer triad, so gravity leaks into the horizontal channel, and that path grows as
the cube of time while the accelerometer bias grows as the square. On a tactical grade unit the two
are within a few per cent at sixty seconds and a factor of nine apart at nine minutes. **A sensor
budget written from a short-flight intuition buys the wrong instrument.**

**The disturbance that sizes the gimbal changes through the flight.** Thrust misalignment is present
the whole burn; the aerodynamic term exists only in the atmosphere and dominates when it does. A
vehicle sized on one condition is sized on the wrong one for most of its flight.

**Twelve channels out of ninety-three are three quarters of the telemetry bandwidth.** The high-rate
structural measurements dominate everything else combined, which is where a bandwidth cut has to
come from and is exactly the group nobody wants to cut.

Run:
    python avionicsAndGNC/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'avionicsLibrary'))

from avionicsUtils import (IMU_GRADES, AIDING_SOURCES, TVC_ARRANGEMENTS,
                           NavigationError, ControlAuthorityError, TelemetryError)
from NavigationDrift import NavigationDrift
from ControlAuthority import ControlAuthority
from TelemetryBudget import TelemetryBudget

ASSET = os.path.join(HERE, 'avionicsLibrary', 'assets', 'ascentAvionicsExample.json')

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

def buildNavigation(case: dict, grade: str = None, aiding: str = None) -> NavigationDrift:

    entry = case['navigation']

    navigation = NavigationDrift()
    navigation.setInputs({'grade':               grade if grade else entry['grade'],
                          'flightTime':          case['flight']['duration'],
                          'aiding':              aiding if aiding else entry['aiding'],
                          'positionRequirement': entry['positionRequirement']})

    return navigation

def buildControl(case: dict, condition: dict = None) -> ControlAuthority:

    entry = case['control']

    inputs = {'thrust':           entry['thrust'],
              'gimbalArm':        entry['gimbalArm'],
              'arrangement':      entry['arrangement'],
              'referenceArea':    entry['referenceArea'],
              'staticMargin':     entry['staticMargin'],
              'vehicleLength':    entry['vehicleLength'],
              'vehicleDiameter':  entry['vehicleDiameter'],
              'bendingFrequency': entry['bendingFrequency']}

    if condition:
        inputs['dynamicPressure']   = condition['dynamicPressure']
        inputs['windAngleOfAttack'] = condition['windAngleOfAttack']

    control = ControlAuthority()
    control.setInputs(inputs)

    return control

def buildTelemetry(case: dict) -> TelemetryBudget:

    entry = case['telemetry']

    telemetry = TelemetryBudget()
    telemetry.setInputs({'measurements':     [dict(item) for item in entry['measurements']],
                         'linkCapacity':     entry['linkCapacity'],
                         'recorderCapacity': entry['recorderCapacity'],
                         'flightTime':       case['flight']['duration']})

    return telemetry

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the error that is not the one budgeted -- #
# ------------------------------------------------------------------------------------------------ #

def reportNavigation(case: dict) -> dict:

    banner('1. THE NAVIGATION ERROR IS THE GYROSCOPE, NOT THE ACCELEROMETER')

    navigation = buildNavigation(case)

    drift = navigation.calculateDrift()

    print(f'    {"term":30s} {"error [m]":>12s} {"share of variance":>19s}')
    for name, value in sorted(drift['terms'].items(), key = lambda item: -item[1]):
        print(f'    {name:30s} {value:12.1f} {drift["shares"][name]:19.1%}')

    print()
    print(f'  At {case["flight"]["duration"]:.0f} s the position error is '
          f'{drift["totalPosition"]:.0f} m and {drift["dominantShare"]:.0%} of the variance is')
    print(f'  {drift["dominant"]}.')

    print()
    print('  The mechanism is worth stating because it is not obvious. An attitude error tilts the')
    print('  accelerometer triad, so a component of gravity appears as horizontal acceleration.')
    print('  The attitude error grows linearly with gyro bias, and integrating that twice gives a')
    print('  position error growing as the **cube** of time, against the square for accelerometer')
    print('  bias.')

    print()
    print(f'    {"time [s]":>10s} {"accelerometer bias [m]":>24s} {"gyro through tilt [m]":>23s}')
    for time in (30.0, 60.0, 120.0, 300.0, case['flight']['duration']):
        entry = navigation.calculateDrift(time)
        print(f'    {time:10.0f} {entry["terms"]["accelerometer bias"]:24.1f} '
              f'{entry["terms"]["gyro bias through tilt"]:23.1f}')

    crossover = navigation.identifyCrossover()

    print()
    for finding in crossover['findings']:
        print(f'  - {finding}')

    grades = navigation.compareGrades()

    print()
    print(f'    {"grade":14s} {"attitude [deg]":>16s} {"position [m]":>16s}')
    for name, entry in grades['results'].items():
        print(f'    {name:14s} {entry["attitude"]:16.4f} {entry["position"]:16.1f}')

    print()
    print(f'  A spread of {grades["spread"]:.0f} times across three grades. **The grade is the')
    print('  decision and the specific unit is a detail**, which is not true of most components.')

    check = navigation.checkRequirement()

    print()
    for finding in check['findings']:
        print(f'  - {finding}')

    return {'navigation': navigation, 'drift': drift, 'crossover': crossover,
            'grades': grades, 'check': check}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the disturbance changes through the flight -- #
# ------------------------------------------------------------------------------------------------ #

def reportControl(case: dict) -> dict:

    banner('2. THE DISTURBANCE THAT SIZES THE GIMBAL CHANGES THROUGH THE FLIGHT')

    entry = case['control']

    print(f'    {"condition":22s} {"total [kN m]":>13s} {"governing":>32s} {"trim [deg]":>12s}')

    results = {}

    for condition in entry['conditions']:

        control = buildControl(case, condition)

        disturbances = control.calculateDisturbances()

        try:
            authority = control.checkAuthority()
            trim = f'{authority["trimAngle"]:12.2f}'
            results[condition['name']] = {'disturbances': disturbances,
                                          'authority':    authority}
        except ControlAuthorityError:
            trim = f'{"REFUSED":>12s}'
            results[condition['name']] = {'disturbances': disturbances, 'authority': None}

        print(f'    {condition["name"]:22s} {disturbances["total"] / 1000.0:13.1f} '
              f'{disturbances["governing"]:>32s} {trim}')

    print()
    print('  Away from the atmosphere the thrust misalignment governs, and it is present the whole')
    print('  burn and largest when the thrust is largest. Inside the atmosphere the aerodynamic')
    print('  term takes over, and it does so because the vehicle is **unstable**: the centre of')
    print(f'  pressure sits ahead of the centre of gravity by '
          f'{abs(entry["staticMargin"]):.1%} of the vehicle length,')
    print('  so any angle of attack produces a moment that increases the angle of attack.')

    print()
    print('  **A gimbal sized on one condition is sized on the wrong one for most of the flight.**')

    control = buildControl(case, entry['conditions'][1])

    rate = control.requiredActuatorRate(entry['controlFrequency'])

    print()
    for finding in rate['findings']:
        print(f'  - {finding}')

    print()
    print('  The angle is half the answer. The rate is the other half and it is the one that is')
    print('  usually short, because a rate-limited actuator is a nonlinearity that the gain and')
    print('  phase margins do not describe at all.')

    return {'results': results, 'rate': rate}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: twelve channels out of ninety-three -- #
# ------------------------------------------------------------------------------------------------ #

def reportTelemetry(case: dict) -> dict:

    banner('3. TWELVE CHANNELS OUT OF NINETY-THREE ARE THREE QUARTERS OF THE BANDWIDTH')

    telemetry = buildTelemetry(case)

    rate = telemetry.calculateBitRate()
    link = telemetry.checkLink()

    print(f'    {"group":28s} {"channels":>9s} {"rate [Hz]":>10s} {"kbit/s":>9s} {"share":>7s}')
    for item in sorted(rate['detail'], key = lambda entry: -entry['bitRate']):
        print(f'    {item["name"]:28s} {item["count"]:9d} {item["sampleRate"]:10.0f} '
              f'{item["bitRate"] / 1000.0:9.2f} {item["share"]:7.0%}')

    print()
    for finding in link['findings']:
        print(f'  - {finding}')

    print()
    print('  The high-rate structural channels dominate everything else combined. **That is where')
    print('  a bandwidth cut has to come from**, and it is exactly the group nobody wants to cut,')
    print('  because it is the group an investigation needs.')

    rates = telemetry.checkSampleRates()

    print()
    for finding in rates['findings']:
        print(f'  - {finding}')

    recorder = telemetry.checkRecorder()

    print()
    for finding in recorder['findings']:
        print(f'  - {finding}')

    allocations = telemetry.compareAllocations()

    print()
    print(f'    {"sample rate factor":>20s} {"payload [kbit/s]":>18s} {"channels affordable":>21s}')
    for factor, result in allocations['results'].items():
        print(f'    {factor:19.1f}x {result["payloadRate"] / 1000.0:18.1f} '
              f'{result["channelsAffordable"]:21.0f}')

    print()
    print('  Channel count and sample rate compete for the same bits. Doubling every rate halves')
    print('  the channels the link can carry, and the instinct to sample everything fast produces')
    print('  a list that gets cut by whoever is least attached to their channel rather than by')
    print('  what matters.')

    return {'telemetry': telemetry, 'rate': rate, 'link': link,
            'recorder': recorder, 'allocations': allocations}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: what this domain does not compute -- #
# ------------------------------------------------------------------------------------------------ #

def reportBoundaries() -> None:

    banner('4. WHAT THIS DOMAIN DOES NOT COMPUTE')

    print('  This domain was scaffolded documentation-first, on the grounds that the trajectory')
    print('  and control algorithm work overlaps material that already exists and a library here')
    print('  would duplicate rather than add. Three classes were built anyway, and the test')
    print('  applied was whether each computes something no other domain does.')
    print()
    print('  Built, because nothing else computes them:')
    print()
    print('    Sensor error propagation into a navigation solution. No other domain has a sensor.')
    print('    Control authority against disturbance moments. Structures has the loads and')
    print('    propulsion has the thrust; neither closes the attitude loop.')
    print('    Telemetry bandwidth. Nothing else allocates it.')
    print()
    print('  Not built, and each for a stated reason:')
    print()
    print('    **Guidance algorithms.** Closed-loop targeting and ascent guidance duplicate the')
    print('    conceptual vehicle design work, and vehicleArchitecture already owns the delta-V')
    print('    budget they would be optimising against.')
    print()
    print('    **Control law synthesis.** Gain scheduling and margin computation need a plant')
    print('    model: the rigid body, the bending modes, the slosh modes and the actuator, coupled.')
    print('    aerospaceStructures owns the modes and fluidSystems owns the slosh, and assembling')
    print('    a coupled model from them is a real piece of work rather than a class.')
    print()
    print('    **Kalman filtering and sensor fusion.** The error models here are what a filter')
    print('    would consume. Implementing the filter would be implementing an estimator whose')
    print('    tuning is the entire engineering content.')
    print()
    print('    **Radiation single event effects.** A parts and environment question.')
    print()
    print('    **Flight software assurance.** A process, documented and not modelled.')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(navigation: dict, control: dict, telemetry: dict) -> None:

    banner('SUMMARY: THREE THINGS WORTH KNOWING BEFORE TALKING TO AN AVIONICS TEAM')

    print()
    print(f'    {"question":48s} {"answer":>24s}')
    print(f'    {"what dominates the navigation error":48s} '
          f'{navigation["drift"]["dominant"]:>24s}')
    print(f'    {"when the gyro term overtakes the accelerometer":48s} '
          f'{navigation["crossover"]["crossover"]:>21.0f} s')
    print(f'    {"spread across IMU grades":48s} '
          f'{navigation["grades"]["spread"]:>23.0f}x')
    print(f'    {"what governs the gimbal at max-Q":48s} '
          f'{control["results"]["max-Q"]["disturbances"]["governing"]:>24s}')
    print(f'    {"what governs it above the atmosphere":48s} '
          f'{control["results"]["above the atmosphere"]["disturbances"]["governing"]:>24s}')
    print(f'    {"gimbal rate needed at 1 Hz":48s} '
          f'{control["rate"]["requiredRate"]:>20.0f} deg/s')
    print(f'    {"share of telemetry in 12 of 93 channels":48s} '
          f'{telemetry["rate"]["detail"][0]["share"]:>23.0%}')
    print(f'    {"recorder duration against a 9 minute flight":48s} '
          f'{telemetry["recorder"]["duration"] / 60.0:>20.0f} min')

    print()
    print('  The connecting theme is that in every one of the three, the quantity that dominates')
    print('  is not the quantity that gets specified. The accelerometer is specified and the')
    print('  gyroscope decides. The aerodynamic case is analysed and the thrust misalignment is')
    print('  present the whole burn. The channel count is negotiated and the sample rate is what')
    print('  spends the bandwidth.')
    print()
    print('  That is a useful thing for a domain built for architectural literacy rather than for')
    print('  design authority: **it says which question to ask, which is the thing somebody')
    print('  outside the discipline actually needs.**')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    navigation = reportNavigation(case)
    control    = reportControl(case)
    telemetry  = reportTelemetry(case)

    reportBoundaries()

    summarise(navigation, control, telemetry)

if __name__ == '__main__':
    main()
