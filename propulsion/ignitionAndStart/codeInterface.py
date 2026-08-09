
# -- ignitionAndStart worked example -- #

'''

Why a start sequence takes seconds when the engine only needs milliseconds, and why the answer to a
hard start is never a bigger igniter.

The hub sized a 100 kN booster and combustionDevices gave it a chamber whose residence time is
1.47 ms. This example asks what that residence time means for the transients at each end of the
burn, and the answer reframes the whole sequence.

    Admitting mainstage flow while the engine lights gives a 2.9 ms window before two chamber-fulls
    have accumulated. No detection system acts in 2.9 ms. So the sequence cannot rely on detecting
    ignition; it has to make the accumulation small by admitting almost none of the flow.

That is the entire reason the RS-25 takes 1.5 seconds to prime its main chamber, and it is why the
igniter is the least interesting component in an ignition system.

Shutdown then produces the mirror result. The residual impulse is dominated by the propellant
already past the valves, its magnitude is trimmed out in guidance, and what reaches the trajectory
is its scatter.

Run:
    python propulsion/ignitionAndStart/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'ignitionAndStartLibrary'))

from ignitionUtils import (SSME_START_SEQUENCE, SSME_SEQUENCE_TOLERANCE, SSME_SHUTDOWN_LIMITS,
                           SequenceError, IgnitionError)
from StartTransient import StartTransient
from IgnitionSystem import IgnitionSystem
from ShutdownTransient import ShutdownTransient
from ChillDown import ChillDown

ASSET = os.path.join(HERE, 'ignitionAndStartLibrary', 'assets', 'startSequenceExample.json')

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

def buildStart(case: dict, delay: float = None, flowFraction: float = None) -> StartTransient:

    engine = case['engine']

    throatArea = np.pi / 4.0 * engine['throatDiameter'] ** 2

    inputs = {'combination':     engine['combination'],
              'chamberPressure': engine['chamberPressure'],
              'throatArea':      throatArea,
              'massFlow':        engine['oxidiserFlow'] + engine['fuelFlow'],
              'feedVolume':      case['feed']['volume']}

    if delay is not None:
        inputs['ignitionDelay'] = delay

    if flowFraction is not None:
        inputs['startFlowFraction'] = flowFraction

    start = StartTransient()
    start.setInputs(inputs)

    return start

def orderedSequence(case: dict) -> dict:

    '''
    The candidate sequence with its comment key stripped, in the order it was written.
    '''

    return {name: value for name, value in case['sequence'].items()
            if not name.startswith('_')}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the yardstick -- #
# ------------------------------------------------------------------------------------------------ #

def reportResidenceTime(case: dict) -> dict:

    banner('1. THE YARDSTICK, AND IT IS NOT THE IGNITER')

    start = buildStart(case, delay = 0.003)

    accumulation = start.calculateAccumulation()

    print(f'  The chamber holds {accumulation["steadyChamberMass"] * 1000.0:.1f} g of combustion '
          f'gas and passes it in')
    print(f'  {accumulation["residenceTime"] * 1000.0:.2f} ms. That is the clock every transient '
          f'in this sub-domain is measured against.')
    print()
    print('  It is the same residence time combustionDevices computed for this chamber, from the')
    print('  same characteristic length. A transient calculation and a combustion efficiency')
    print('  calculation turn out to need the same number, which is not obvious until it happens.')
    print()

    delays = {name: value for name, value in case['ignitionDelays'].items()
              if not name.startswith('_')}

    comparison = start.compareIgnitionDelays(delays)

    print('  Now suppose the engine tried to light at full mainstage flow:')
    print()
    print(f'    {"ignition delay":26s} {"[ms]":>6s} {"chamber-fulls":>15s} {"spike [MPa]":>13s}   hard')
    for name, entry in comparison['results'].items():
        print(f'    {name:26s} {entry["delay"] * 1000.0:6.0f} {entry["massRatio"]:15.1f} '
              f'{entry["spike"] / 1.0e6:13.1f}   {"yes" if entry["hardStart"] else "no"}')

    print()
    print('  Every one of them, including a three millisecond hypergolic slug. That is not a')
    print('  verdict on igniters. **It is the reason no engine lights at mainstage flow.**')
    print()
    print('  Reading the table the other way round is the useful direction. Take the delay as')
    print('  given and ask what flow the sequence may admit while it runs:')
    print()

    reduced = {}

    print(f'    {"ignition delay":26s} {"[ms]":>6s} {"flow permitted":>16s}')
    for name, delay in delays.items():

        # two chamber-fulls is the convention; invert it for the flow fraction
        permitted = 2.0 * accumulation['residenceTime'] / delay

        reduced[name] = min(permitted, 1.0)

        print(f'    {name:26s} {delay * 1000.0:6.0f} {min(permitted, 1.0):15.1%}')

    print()
    print('  A hypergolic slug can be lit on virtually the whole flow, and that is exactly what a')
    print('  TEA-TEB cartridge buys: not reliability, but permission to skip the slow part of the')
    print('  sequence. A torch at 20 ms may be given a fifteenth of the flow, and the sequence has')
    print('  to spend seconds getting from there to mainstage.')
    print()
    print('  The bound is loose. It assumes everything that entered is at the right mixture ratio,')
    print('  fully vaporised, burns to completion, and burns faster than the nozzle can vent it.')
    print('  None of that is true. It is still the right thing to look at, because the ranking it')
    print('  produces is robust to all of that and the ranking is what decides the sequence.')

    return {'start': start, 'accumulation': accumulation, 'comparison': comparison,
            'permittedFlow': reduced}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the window nobody can hit -- #
# ------------------------------------------------------------------------------------------------ #

def reportDetectionWindow(case: dict, residence: float) -> dict:

    banner('2. THE DETECTION WINDOW, AND WHY IT IS NOT AN INSTRUMENTATION PROBLEM')

    engine = case['engine']

    full = IgnitionSystem()
    full.setInputs({'combination':       engine['combination'],
                    'startsRequired':    engine['startsRequired'],
                    'residenceTime':     residence,
                    'startFlowFraction': 1.0})

    window = full.calculateDetectionWindow()

    print(f'  At full mainstage flow, two chamber-fulls accumulate in '
          f'{window["window"] * 1000.0:.1f} ms.')
    print(f'  A detection system needs about {window["detectionLatency"] * 1000.0:.0f} ms to sense '
          f'a pressure rise and move a valve.')
    print()
    print('  So detection cannot prevent this hard start. It can only record it.')
    print()

    print(f'    {"start flow":>12s} {"window [ms]":>13s}   detection can act')
    for fraction in (1.0, 0.5, 0.30, 0.10, 0.05):

        trial = IgnitionSystem()
        trial.setInputs({'combination':       engine['combination'],
                         'startsRequired':    engine['startsRequired'],
                         'residenceTime':     residence,
                         'startFlowFraction': fraction})

        entry = trial.calculateDetectionWindow()

        print(f'    {fraction:11.0%} {entry["window"] * 1000.0:13.1f}   '
              f'{"yes" if entry["detectionCanAct"] else "no"}')

    print()
    print(f'  The only lever with authority is the flow. Admitting '
          f'{window["requiredFlowFraction"]:.0%} of mainstage flow while the')
    print('  engine lights opens the window to the detection latency, and that is what a staged')
    print('  valve sequence is: a way of buying time by not delivering propellant.')
    print()
    print(f'  The RS-25 primes its main chamber at {SSME_START_SEQUENCE["mainChamberPrime"]:.1f} s '
          f'and reaches rated power at '
          f'{SSME_START_SEQUENCE["ratedPower"]:.0f} s. Those')
    print('  seconds are not the igniter being slow. They are the sequence keeping the')
    print('  accumulation small while the turbomachinery comes up.')

    return {'window': window, 'system': full}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the igniter, which is the easy part -- #
# ------------------------------------------------------------------------------------------------ #

def reportIgniterSelection(case: dict, residence: float) -> dict:

    banner('3. THE IGNITER, WHICH IS DECIDED BY RESTART AND NOT BY ENERGY')

    engine = case['engine']

    results = {}

    cases = (('booster, one start, powered',     engine['startsRequired'], True),
             ('upper stage, three starts',       3,                        True),
             ('booster, no power at the engine', engine['startsRequired'], False))

    print(f'    {"case":34s} {"viable":>7s}   options')

    for label, starts, powered in cases:

        system = IgnitionSystem()
        system.setInputs({'combination':    engine['combination'],
                          'startsRequired': starts,
                          'powerAvailable': powered,
                          'residenceTime':  residence})

        selection = system.selectIgniter()

        results[label] = selection

        print(f'    {label:34s} {len(selection["viable"]):7d}   {", ".join(selection["viable"])}')

    print()
    print('  Two constraints, and each removes a different half of the list.')
    print()
    print('  **Restart removes the consumables.** A cartridge is spent once, so three starts means')
    print('  three installations and the answer becomes a device with a propellant tap and its own')
    print('  small feed system.')
    print()
    print('  **No electrical power at the engine removes everything else.** A hypergolic cartridge')
    print('  needs no power at all, which is its real advantage and the reason the F-1 used one.')
    print()
    print('  Where both constraints are absent, more than one answer survives and the choice is')
    print('  made on grounds this class does not model: what the programme has flown before, and')
    print('  what the test stand already supports. The class reports the survivors and picks the')
    print('  one with no consumable, which is a stated convention rather than a derived result.')
    print()
    print('  Ask for both constraints at once and nothing survives, which the class refuses rather')
    print('  than returning an empty answer:')

    infeasible = IgnitionSystem()
    infeasible.setInputs({'combination':    engine['combination'],
                          'startsRequired': 3,
                          'powerAvailable': False,
                          'residenceTime':  residence})

    try:
        infeasible.selectIgniter()
        print('    the check did not fire, which is a defect')
    except IgnitionError as error:
        detail = [line for line in str(error).splitlines() if line.startswith('No igniter')]
        print(f'    IgnitionError: {detail[0]}')

    print()
    print('  Three restarts with no power at the engine is not a hard igniter problem, it is an')
    print('  architecture that has not been closed. The right response is to move the power or the')
    print('  start count, not to look for a cleverer igniter.')
    print()
    print('  Energy never entered any of it. Every device on the list delivers orders of magnitude')
    print('  more than the minimum ignition energy of the mixture, which is why an ignition')
    print('  problem is almost never solved by a bigger igniter.')

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the sequence, and how little margin it has -- #
# ------------------------------------------------------------------------------------------------ #

def reportSequence(case: dict) -> dict:

    banner('4. THE SEQUENCE, AND THE MARGIN IT DOES NOT HAVE')

    start = buildStart(case, delay = 0.003)

    sequence = orderedSequence(case)

    check = start.checkSequence(sequence)

    print(f'    {"event":22s} {"time [s]":>10s} {"gap [ms]":>10s}')

    times = list(sequence.values())
    for index, (name, time) in enumerate(sequence.items()):
        gap = '' if index == 0 else f'{(time - times[index - 1]) * 1000.0:10.0f}'
        print(f'    {name:22s} {time:10.2f} {gap:>10s}')

    print()
    for finding in check['findings']:
        print(f'  {finding}')

    print()
    priming = start.calculatePriming()

    print(f'  Priming the {priming["feedVolume"] * 1000.0:.0f} litres downstream of the main valves '
          f'takes {priming["primingTime"] * 1000.0:.0f} ms at')
    print(f'  full flow, which is {priming["primingTimeInResidenceTimes"]:.0f} residence times. The '
          f'engine is not started when the igniter')
    print('  fires. It is started when the last of that volume has arrived as liquid.')

    print()
    print('  What an out-of-order sequence does is not modelled here and it is not modelled')
    print('  anywhere in this repository. It is refused instead:')

    broken = dict(sequence)
    broken['oxidiserValveCrack'] = 0.10

    try:
        start.checkSequence(broken)
        print('    the check did not fire, which is a defect')
    except SequenceError as error:
        detail = [line for line in str(error).splitlines()
                  if line.startswith('The sequence is not monotonic')]
        print(f'    SequenceError: {detail[0]}')

    return {'check': check, 'priming': priming}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: shutdown, the harder one -- #
# ------------------------------------------------------------------------------------------------ #

def reportShutdown(case: dict) -> dict:

    banner('5. SHUTDOWN, WHICH IS HARDER AND GETS LESS ATTENTION')

    engine = case['engine']

    shutdown = ShutdownTransient()
    shutdown.setInputs({'combination': engine['combination'],
                        'thrust':      engine['thrust'],
                        'massFlow':    engine['oxidiserFlow'] + engine['fuelFlow'],
                        'feedVolume':  case['feed']['volume']})

    decay    = shutdown.calculateDecayLimit()
    residual = shutdown.calculateResidualImpulse()

    print(f'  The reference structural limit is {decay["referenceRate"] / 1.0e6:.2f} MN/s, which at '
          f'{engine["thrust"] / 1.0e3:.0f} kN permits no faster')
    print(f'  than {decay["minimumDecayTime"] * 1000.0:.0f} ms to zero thrust.')
    print()
    print('  That limit belongs to the airframe. The RS-25 rate limits on its oxidiser valves')
    print('  exist to satisfy an interface control document, not because the engine could not shut')
    print('  down faster. A shutdown specification that does not name its vehicle is not one.')
    print()

    print(f'    {"contribution":22s} {"impulse [kN s]":>16s} {"share":>8s}')
    print(f'    {"thrust ramp":22s} {residual["rampImpulse"] / 1.0e3:16.2f} '
          f'{1.0 - residual["dribbleFraction"]:8.0%}')
    print(f'    {"dribble volume":22s} {residual["dribbleImpulse"] / 1.0e3:16.2f} '
          f'{residual["dribbleFraction"]:8.0%}')
    print(f'    {"total":22s} {residual["totalImpulse"] / 1.0e3:16.2f}')

    print()
    print(f'  {residual["dribbleMass"]:.1f} kg is downstream of the valves when they close and it '
          f'is going to arrive.')
    print(f'  The ramp is {1.0 - residual["dribbleFraction"]:.0%} of the residual and the dribble '
          f'volume is {residual["dribbleFraction"]:.0%} of it.')
    print()
    print(f'  Guidance trims the magnitude. It cannot trim the scatter, about '
          f'{residual["scatter"] / 1.0e3:.2f} kN s, because it')
    print('  cannot predict it. **The scatter is what reaches the injection accuracy**, and it is')
    print('  the reason a shutdown that is repeatable beats a shutdown that is fast.')

    order = shutdown.checkShutdownOrder(case['shutdown']['oxidiserCloseTime'],
                                        case['shutdown']['fuelCloseTime'])

    print()
    print(f'  The fuel valve leads the oxidiser closed by {order["fuelLead"]:.2f} s, against the '
          f'RS-25\'s {order["referenceLead"]:.1f} s hold.')
    print('  The transient runs fuel-rich on purpose. An oxidiser-rich excursion at combustion')
    print('  temperature is how injector faces and turbines are destroyed, and this repository')
    print('  refuses a sequence that produces one rather than reporting it.')

    return {'shutdown': shutdown, 'decay': decay, 'residual': residual, 'order': order}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 6: chill-in, where the method is the answer -- #
# ------------------------------------------------------------------------------------------------ #

def reportChillDown(case: dict) -> dict:

    banner('6. CHILL-IN, WHERE THE METHOD DECIDES THE ANSWER')

    conditioning = case['conditioning']

    chill = ChillDown()
    chill.setInputs({'cryogen':   'LOX',
                     'material':  conditioning['material'],
                     'metalMass': conditioning['metalMass']})

    comparison = chill.compareCryogens(conditioning['cryogens'])

    print(f'  {conditioning["metalMass"]:.0f} kg of {conditioning["material"]} conditioned from '
          f'ambient, by each cryogen in turn.')
    print()
    print(f'    {"cryogen":10s} {"latent":>10s} {"vapour":>10s} {"lower [kg]":>12s} '
          f'{"upper [kg]":>12s} {"band":>7s}')

    for name, entry in comparison['results'].items():
        print(f'    {name:10s} {entry["latentHeat"] / 1.0e3:10.0f} '
              f'{entry["sensibleHeat"] / 1.0e3:10.0f} {entry["lowerBound"]:12.1f} '
              f'{entry["upperBound"]:12.1f} {entry["band"]:7.1f}')

    print()
    print('  The two bounds are the two chill-down methods. Fast flow sweeps the vapour out cold')
    print('  and only the latent heat is used; slow flow lets it warm and recovers the sensible')
    print('  heat as well. Real chill-down lies between them.')
    print()

    widest = comparison['widestBand']

    print(f'  For LOX the band is {comparison["bandRatio"]["LOX"]:.1f} to one and the hardware mass '
          f'decides the answer.')
    print(f'  For {widest} it is {comparison["bandRatio"][widest]:.1f} to one and the **method** '
          f'decides it.')
    print()
    print('  That single ratio is why the liquid hydrogen chill-down literature is entirely about')
    print('  trickle against pulse flow scheduling and the liquid oxygen literature is not.')
    print(f'  Hydrogen\'s latent heat is {comparison["results"][widest]["latentHeat"] / 1.0e3:.0f} '
          f'kJ/kg and its vapour will absorb '
          f'{comparison["results"][widest]["sensibleHeat"] / 1.0e3:.0f} more')
    print('  on the way back to ambient. Almost all of the cooling available is in the gas.')
    print()
    print('  This engine burns RP-1, which is stored at ambient and needs no conditioning at all.')
    print('  Half the operational simplicity of a kerosene booster is in that sentence.')

    return comparison

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(stage1: dict, stage2: dict, stage5: dict, stage6: dict) -> None:

    banner('SUMMARY: WHAT THE TRANSIENTS ACTUALLY DEPEND ON')

    residence = stage1['accumulation']['residenceTime']

    print()
    print(f'    {"question":42s} {"answer":>12s}   set by')
    print(f'    {"chamber residence time":42s} {residence * 1000.0:10.2f} ms   '
          f'chamber volume and flow')
    print(f'    {"window before two chamber-fulls":42s} '
          f'{stage2["window"]["window"] * 1000.0:10.1f} ms   the same, and the start flow')
    print(f'    {"detection latency needed to act":42s} '
          f'{stage2["window"]["detectionLatency"] * 1000.0:10.0f} ms   physics of the sensor loop')
    print(f'    {"start flow that makes detection work":42s} '
          f'{stage2["window"]["requiredFlowFraction"]:10.0%}      the valve schedule')
    print(f'    {"residual impulse after cutoff":42s} '
          f'{stage5["residual"]["totalImpulse"] / 1.0e3:10.1f} kNs  the dribble volume')
    print(f'    {"of which reaches the trajectory":42s} '
          f'{stage5["residual"]["scatter"] / 1.0e3:10.2f} kNs  its scatter, not its size')
    print(f'    {"LOX conditioning band":42s} '
          f'{stage6["bandRatio"]["LOX"]:10.1f} x     the hardware mass')
    print(f'    {"LH2 conditioning band":42s} '
          f'{stage6["bandRatio"]["LH2"]:10.1f} x     the chill-down method')

    print()
    print('  Three of those are set by things that are not the igniter, the controller or the')
    print('  sensor. They are set by the chamber volume, the valve schedule and the plumbing')
    print('  downstream of the valves, and none of the three is usually described as part of the')
    print('  ignition system.')
    print()
    print(f'  The RS-25 takes {SSME_START_SEQUENCE["ratedPower"]:.0f} seconds to reach rated power '
          f'and states that a '
          f'{SSME_SEQUENCE_TOLERANCE["timingError"] * 1000.0:.0f} ms timing error')
    print(f'  can cause significant damage, while priming its three combustors '
          f'{SSME_SEQUENCE_TOLERANCE["primeSpacing"] * 1000.0:.0f} ms apart. The')
    print('  design spacing and the damaging error are the same number. That is the honest')
    print('  measure of how much margin a start sequence has, and it is why they are developed on')
    print('  a test stand rather than on paper.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    stage1 = reportResidenceTime(case)

    residence = stage1['accumulation']['residenceTime']

    stage2 = reportDetectionWindow(case, residence)
    reportIgniterSelection(case, residence)
    reportSequence(case)
    stage5 = reportShutdown(case)
    stage6 = reportChillDown(case)

    summarise(stage1, stage2, stage5, stage6)

if __name__ == '__main__':
    main()
