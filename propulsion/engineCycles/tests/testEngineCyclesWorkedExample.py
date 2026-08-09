# -- Tests for the engineCycles worked example and its validation -- #

'''

The example makes two claims.

The first is structural: most cycle candidates are eliminated by a constraint rather than chosen by
a trade, and only the last two are a genuine comparison.

The second is quantitative and it is the one with an external check. An expander cycle's turbine
runs on heat the chamber wall gave up, that heat is nearly independent of chamber pressure while
the pump power rises with it, so there is a ceiling. This engine's ceiling falls between 4.0 and
4.5 MPa, and RL10 runs at 4.4.

Two hardware comparisons sit at the bottom of this file: the pressure ladder against the published
RS-25 pump discharge, and the expander ceiling against RL10.

Author: Sean Bowman
Date:   09/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'engineCyclesLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'engineCyclesCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['engineCyclesCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from cycleUtils import pressureLadder, ENGINE_CYCLES
from validation.referenceCases import TURBOPUMPS, LIQUID_ENGINES, VALIDATION_LEVELS

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

@pytest.fixture(scope = 'module')
def expander(case):

    return codeInterface.expanderCeiling(case)

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def testTheEngineStillMatchesTheHub(case):

    sys.path.insert(0, os.path.join(ROOT, 'propulsion', 'propulsionLibrary'))

    from EngineSizing import EngineSizing

    engine = case['engine']

    sizing = EngineSizing()
    sizing.setInputs({'combination':      engine['combination'],
                      'thrust':           engine['thrust'],
                      'chamberPressure':  engine['chamberPressure'],
                      'areaRatio':        engine['areaRatio'],
                      'contractionRatio': engine['contractionRatio']})

    throat = sizing.sizeThroat()

    assert throat['throatDiameter'] == pytest.approx(engine['throatDiameter'], abs = 0.0005)
    assert throat['massFlow']       == pytest.approx(engine['totalFlow'],      abs = 0.05)

# ------------------------------------------------------------------------------------------------ #
# -- The expander ceiling -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExpanderCeilingExists(expander):

    '''
    There has to be a crossover inside the swept range, or the sweep does not demonstrate anything.
    '''

    assert expander['ceiling'] is not None
    assert expander['firstFailure'] is not None
    assert expander['firstFailure'] > expander['ceiling']

def testTheCeilingBracketsTheRL10ChamberPressure():

    '''
    The hardware check, and the reason this example is worth having. RL10 is the best known
    expander cycle engine and it runs at 4.4 MPa. A model that put the ceiling at 1 MPa or 40 MPa
    would be telling us nothing useful about expanders.

    The agreement is closer than the model deserves and should not be read as more than a sanity
    bracket: the propellant here is LOX/RP-1 and RL10 runs on hydrogen.
    '''

    case     = codeInterface.loadCase()
    expander = codeInterface.expanderCeiling(case)

    rl10ChamberPressure = 4.4e6

    assert expander['ceiling'] <= rl10ChamberPressure <= expander['firstFailure'] * 1.05, (
        f'ceiling brackets {expander["ceiling"] / 1.0e6:.1f} to '
        f'{expander["firstFailure"] / 1.0e6:.1f} MPa, RL10 is 4.4')

def testTheJacketHeatIsNearlyIndependentOfChamberPressure(expander):

    '''
    The mechanism behind the ceiling, and the half of it that is counterintuitive. Flux rises with
    chamber pressure and area falls, and the two nearly cancel.
    '''

    rows = expander['rows']

    first, last = rows[0], rows[-1]

    heatRatio     = first['jacket'] / last['jacket']
    pressureRatio = last['pressure'] / first['pressure']

    assert pressureRatio > 4.0
    assert heatRatio < 1.5, 'the jacket heat should barely move across the sweep'

def testThePumpPowerRisesRoughlyLinearlyWithChamberPressure(expander):

    rows = expander['rows']

    first, last = rows[0], rows[-1]

    powerRatio    = last['pumpPower'] / first['pumpPower']
    pressureRatio = last['pressure'] / first['pressure']

    assert powerRatio == pytest.approx(pressureRatio, rel = 0.35)

def testTheMarginFallsFasterThanChamberPressureRises(expander):

    '''
    The scaling argument: available over required goes as roughly the inverse 1.2 power of chamber
    pressure. If the exponent ever came out near zero the ceiling would not exist.
    '''

    rows = expander['rows']

    first, last = rows[0], rows[-1]

    exponent = (np.log(first['margin'] / last['margin'])
                / np.log(last['pressure'] / first['pressure']))

    assert 0.9 < exponent < 1.7, f'the scaling exponent came out at {exponent:.2f}'

def testTheMarginIsMonotonicInChamberPressure(expander):

    margins = [row['margin'] for row in expander['rows']]

    assert margins == sorted(margins, reverse = True)

# ------------------------------------------------------------------------------------------------ #
# -- The eliminations -- #
# ------------------------------------------------------------------------------------------------ #

def testThePressureFedTankIsAnOrderHeavier(case):

    '''
    The elimination that needs no subtlety. A pressure fed tank holds what the pump would have
    delivered, and that is a pressure vessel rather than a tank.
    '''

    ladders = codeInterface.reportLadder(case)
    costs   = codeInterface.reportCosts(case, ladders)

    assert costs['pressure fed']['tankMass'] > 10.0 * costs['gas generator']['tankMass']

def testTheOpenCycleLosesImpulseAndTheClosedOneLosesPumpPressure(case):

    ladders = codeInterface.reportLadder(case)
    costs   = codeInterface.reportCosts(case, ladders)

    assert costs['gas generator']['penalty'] > 0.0
    assert costs['staged combustion']['penalty'] == 0.0

    assert (costs['staged combustion']['pumpPower']
            > 1.4 * costs['gas generator']['pumpPower'])

# ------------------------------------------------------------------------------------------------ #
# -- Hardware validation of the pressure ladder -- #
# ------------------------------------------------------------------------------------------------ #

def testThePressureLadderMatchesTheRS25PumpDischarge():

    '''
    RS-25 is staged combustion at 20.64 MPa and its high pressure fuel turbopump discharges at
    roughly 41 MPa, a ratio of about two. The ladder predicts 45.4 MPa, which is 11 per cent high
    and conservative.

    Conservative is the right direction for a pressure ladder: it oversizes the pump rather than
    leaving it short.
    '''

    engine = LIQUID_ENGINES['RS-25']

    ladder = pressureLadder(engine['chamberPressure'], 'staged combustion')

    published = TURBOPUMPS['RS-25 HPFTP']['dischargePressure']

    error = (ladder['dischargePressure'] - published) / published

    assert 0.0 < error < 0.20, (
        f'predicted {ladder["dischargePressure"] / 1.0e6:.1f} MPa against a published '
        f'{published / 1.0e6:.1f} MPa, {error:+.1%}')

def testTheStagedCombustionRatioIsAboutTwoAsRS25Shows():

    '''
    The structural claim, checked against real hardware rather than against the library's own
    constants. RS-25 discharges at 41 MPa for a 20.64 MPa chamber, which is 1.99.
    '''

    engine    = LIQUID_ENGINES['RS-25']
    published = TURBOPUMPS['RS-25 HPFTP']['dischargePressure']

    realRatio = published / engine['chamberPressure']

    assert 1.8 < realRatio < 2.2

    modelRatio = pressureLadder(engine['chamberPressure'], 'staged combustion')['dischargeRatio']

    assert abs(modelRatio - realRatio) < 0.3

def testTheOpenCycleImpulsePenaltyExplainsTheF1Disagreement():

    '''
    The propulsion hub library models a thrust chamber and overpredicts the F-1's published vacuum
    impulse by 8.1 per cent while matching RS-25 to 1.7. F-1 is a gas generator engine.

    This checks that a cycle penalty of the size this sub-domain computes is the right order to
    account for a meaningful part of that gap. It does not close it entirely, and the test says so
    by bounding rather than asserting equality: the rest is chamber efficiency, which is a
    different thing.
    '''

    from EngineCycle import EngineCycle

    f1 = LIQUID_ENGINES['F-1']

    cycle = EngineCycle()
    cycle.setInputs({'cycle':               'gas generator',
                     'chamberPressure':     f1['chamberPressure'],
                     'idealImpulse':        328.7,
                     'turbineFlowFraction': 0.03})

    penalty = cycle.calculateImpulseDelivered()['penalty']

    hubDisagreement = (328.7 - f1['vacuumImpulse']) / f1['vacuumImpulse']

    assert 0.0 < penalty < hubDisagreement, (
        f'the cycle penalty is {penalty:.1%} against a hub disagreement of '
        f'{hubDisagreement:.1%}; it should account for part of it and not all')

    assert penalty > 0.25 * hubDisagreement, 'it should account for a meaningful part'

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
