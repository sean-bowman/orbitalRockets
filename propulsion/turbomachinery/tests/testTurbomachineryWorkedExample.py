# -- Tests for the turbomachinery worked example -- #

'''

The example makes one claim: the optimum turbopump shaft speed depends on the engine cycle, by a
factor of two, with nothing about the pumps changing between the two answers.

That claim is worth pinning because it rests on one term being present or absent rather than on its
size, which makes it robust to three mass models that are assumptions rather than data. The absolute
masses are not robust and the tests do not assert them.

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

sys.path.insert(0, os.path.join(DOMAIN, 'turbomachineryLibrary'))
sys.path.insert(0, ROOT)

# Loaded by path under a unique name, per the rule in BUILDOUT.md.

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'turbomachineryCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['turbomachineryCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from turbomachineryUtils import BEARING_DN_LIMIT
from Turbine import BLADE_TIP_SPEED_LIMIT

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

@pytest.fixture(scope = 'module')
def sweep(case):

    return codeInterface.sweepShaftSpeed(case)

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDutiesStillMatchTheHub(case):

    '''
    The example restates the hub's flow rates rather than importing them, so they can drift. This
    runs the hub sizing and checks they have not.
    '''

    sys.path.insert(0, os.path.join(ROOT, 'propulsion', 'propulsionLibrary'))

    from EngineSizing import EngineSizing

    sizing = EngineSizing()
    sizing.setInputs({'combination':      'LOX/RP-1',
                      'thrust':           100000.0,
                      'chamberPressure':  10.0e6,
                      'areaRatio':        20.35,
                      'contractionRatio': 2.5})

    throat = sizing.sizeThroat()

    duty = case['duty']

    assert throat['oxidiserFlow'] == pytest.approx(duty['oxidiser']['massFlow'], abs = 0.05)
    assert throat['fuelFlow']     == pytest.approx(duty['fuel']['massFlow'],     abs = 0.05)

def testTheDischargePressureMatchesTheHubInterfaceMargin(case):

    '''
    The hub states a 1.25 margin over a 10 MPa chamber. If either moves, this example is pumping to
    the wrong pressure.
    '''

    assert case['duty']['dischargePressure'] == pytest.approx(1.25 * 10.0e6)

# ------------------------------------------------------------------------------------------------ #
# -- The claim the example exists to make -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTwoCyclesWantDifferentShaftSpeeds(sweep):

    '''
    The point. An open cycle throws the turbine flow away so turbine efficiency is worth propellant;
    a closed cycle does not so tank mass wins. Nothing about the pumps differs between them.
    '''

    assert sweep['openBest']['shaftSpeed'] > sweep['closedBest']['shaftSpeed']

def testTheCycleMovesTheOptimumByAboutAFactorOfTwo(sweep):

    ratio = sweep['openBest']['shaftSpeed'] / sweep['closedBest']['shaftSpeed']

    assert 1.6 < ratio < 2.6, f'optimum speed ratio is {ratio:.2f}'

def testTheOpenCycleOptimumIsDominatedByDumpedPropellant(sweep):

    '''
    The mechanism behind the claim. If dumped propellant ever stops being the largest term at the
    open cycle optimum, the reason the two cycles differ has changed.
    '''

    best = sweep['openBest']

    assert best['dumpedMass'] > best['tankMass']
    assert best['dumpedMass'] > best['turbopumpMass']

def testTheClosedCycleOptimumIsATradeBetweenTankAndTurbopump(sweep):

    '''
    With the dumped term removed, the only two remaining move in opposite directions with speed,
    which is what produces an interior minimum rather than a boundary one.
    '''

    results = sweep['results']

    slowest = min(results, key = lambda entry: entry['shaftSpeed'])
    fastest = max(results, key = lambda entry: entry['shaftSpeed'])

    assert slowest['turbopumpMass'] > fastest['turbopumpMass']
    assert slowest['tankMass']      < fastest['tankMass']

    best = sweep['closedBest']

    assert slowest['shaftSpeed'] < best['shaftSpeed'] < fastest['shaftSpeed'], (
        'the closed cycle optimum must be interior, not at a sweep boundary')

def testTheOpenCycleOptimumIsBroadAndThePenaltyAsymmetric(sweep):

    '''
    The practical advice the example gives: err fast. Being half the optimum speed costs far more
    than being fast does, so a broad optimum is not an invitation to sit in the middle of it.
    '''

    results = sweep['results']
    minimum = sweep['openBest']['openTotal']

    within = [entry for entry in results if entry['openTotal'] < minimum * 1.05]

    assert max(entry['shaftSpeed'] for entry in within) \
        / min(entry['shaftSpeed'] for entry in within) > 1.3, 'the optimum should be broad'

    half = min(results, key = lambda entry:
               abs(entry['shaftSpeed'] - 0.5 * sweep['openBest']['shaftSpeed']))

    assert half['openTotal'] / minimum > 1.15, 'half speed should cost real mass'

# ------------------------------------------------------------------------------------------------ #
# -- What actually binds -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTurbineBladeSpeedIsTheBindingLimitAtTheOpenOptimum(sweep):

    '''
    The optimum is a soft minimum and the blade stress limit is not. On this engine they nearly
    coincide, so the open cycle answer is set by a materials limit rather than reached freely.
    '''

    blade = sweep['openBest']['bladeSpeed']

    assert blade > 0.85 * BLADE_TIP_SPEED_LIMIT
    assert blade <= BLADE_TIP_SPEED_LIMIT

def testTheBearingAndImpellerLimitsAreNotBinding(sweep, case):

    '''
    On a moderate chamber pressure engine the pump is not the hard part of a turbopump. If this
    ever inverts, the engine has moved somewhere the sub-domain's assumptions need revisiting.
    '''

    best = sweep['openBest']

    assert best['dnNumber'] < BEARING_DN_LIMIT

    for name in ('oxidiser', 'fuel'):
        assert best['sides'][name]['tipSpeed'] < 300.0

# ------------------------------------------------------------------------------------------------ #
# -- The tank chain -- #
# ------------------------------------------------------------------------------------------------ #

def testTheOxidiserTankCostsSubstantiallyMoreThanTheFuelTank(case):

    '''
    And the pump is barely responsible. LOX boils at 101 kPa against RP-1 at 2 kPa, so the LOX tank
    starts a hundred kilopascals in debt before any cavitation margin is added.
    '''

    result = codeInterface.evaluate(case, 30000.0)

    assert result['sides']['oxidiser']['tankMass'] > 3.0 * result['sides']['fuel']['tankMass']

def testMostOfTheCryogenicTankPressureIsNotCavitationMargin(case):

    '''
    The finding worth stating plainly. On the oxidiser side the vapour pressure alone is a large
    fraction of the required tank pressure, so the tank is mostly holding the propellant liquid
    rather than feeding the pump.
    '''

    result = codeInterface.evaluate(case, 30000.0)

    oxidiser = case['duty']['oxidiser']

    vapourShare = oxidiser['vapourPressure'] / result['sides']['oxidiser']['tankPressure']

    assert vapourShare > 0.30

def testTankPressureRisesWithShaftSpeed(case):

    slow = codeInterface.evaluate(case, 20000.0)
    fast = codeInterface.evaluate(case, 50000.0)

    assert fast['tankMass'] > slow['tankMass']

def testTurbineEfficiencyRisesWithShaftSpeed(case):

    slow = codeInterface.evaluate(case, 20000.0)
    fast = codeInterface.evaluate(case, 50000.0)

    assert fast['turbineEfficiency'] > slow['turbineEfficiency']
    assert fast['drivingFlow'] < slow['drivingFlow']

# ------------------------------------------------------------------------------------------------ #
# -- The assumptions stay labelled -- #
# ------------------------------------------------------------------------------------------------ #

def testTheMassModelsAreDeclaredInTheAsset(case):

    '''
    Three of them, all assumptions, and the conclusion moves with all three. They belong in the
    configuration where they can be seen and changed, not buried in the code.
    '''

    model = case['massModel']

    for field in ('tankShapeFactor', 'tankAllowable', 'turbopumpReferenceMass',
                  'turbopumpPowerExponent', 'gasGeneratorLostFraction'):
        assert field in model

    assert 'unvalidated' in model['_comment']

def testTheExampleSaysWhichModelsAreAssumptions(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'assumptions rather than data' in printed
    assert 'engineCycles' in printed, 'the cycle handover has to be named'

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
