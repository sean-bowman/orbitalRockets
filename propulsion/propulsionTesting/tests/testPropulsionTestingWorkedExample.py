# -- Tests for the propulsionTesting worked example -- #

'''

The example argues that a hot fire is limited by decisions made before the firing rather than by
the engine, and that the one arithmetic trap in the reduction is worth more than the rest of it.
The tests pin those arguments.

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

sys.path.insert(0, os.path.join(DOMAIN, 'propulsionTestingLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'propulsionTestingCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['propulsionTestingCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from propulsionTestUtils import TestDesignError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def testTheChannelsAreStillTheHubsDesignPoint(case):

    '''
    The example is handed the hub's design point as if it were recorded data, because inventing
    plausible stand data would be worse. If the hub moves, this example is reducing a firing of an
    engine that no longer exists.
    '''

    measured = case['measured']

    assert measured['chamberPressure'] == 10.0e6
    assert measured['throatDiameter']  == pytest.approx(0.0906)
    assert measured['massFlow']        == pytest.approx(36.81, abs = 0.01)
    assert measured['thrust']          == 100.0e3

def testTheReductionReproducesTheHubsImpulse(case):

    reduced = codeInterface.buildReduction(case).reduce()

    assert reduced['specificImpulse'] == pytest.approx(277.0, abs = 0.1)

def testTheIdealValuesAreIdealAndNotDelivered(case):

    '''
    Comparing a measured thrust coefficient against a delivered one rather than an ideal one is how
    an efficiency gets quoted as unity. The asset carries the ideal and says so.
    '''

    ideal = case['ideal']

    reduced = codeInterface.buildReduction(case).reduce()

    assert ideal['characteristicVelocity'] > reduced['characteristicVelocity']
    assert ideal['thrustCoefficient']      > reduced['thrustCoefficient']

# ------------------------------------------------------------------------------------------------ #
# -- The argument -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTwoRoutesToImpulseAgreeAndTheirUncertaintiesDoNot(case):

    '''
    The trap, and it is the strongest result in the sub-domain because it is an identity rather
    than a measurement.
    '''

    uncertainty = codeInterface.reportCorrelation(case)

    reduced = codeInterface.buildReduction(case).reduce()

    assert reduced['productCheck'] == pytest.approx(reduced['specificImpulse'], rel = 1.0e-12)

    assert uncertainty['naiveSpecificImpulse'] > uncertainty['specificImpulse']
    assert uncertainty['inflationFactor'] > 1.5

def testNoChannelDominatesTheCharacteristicVelocityBudget(case):

    '''
    The case where a budget is worth building rather than guessing, and the reason improving one
    channel alone does not help.
    '''

    stage = codeInterface.reportReduction(case)

    shares = stage['uncertainty']['cstarShares']

    assert max(shares.values()) < 0.5
    assert shares['throatArea'] == pytest.approx(shares['massFlow'], abs = 0.01)

def testTheCampaignCanValidateAndCannotRank(case):

    '''
    The result the example is built around. The four per cent criterion survives and the one per
    cent criterion is refused outright.
    '''

    stage = codeInterface.reportDiscrimination(case)

    assert stage['results']['validation'] is not None
    assert stage['results']['ranking'] is None, 'the one per cent band should have been refused'

    assert stage['results']['validation']['comfortable'] is False

def testImprovingBothChannelsStillCannotRank(case):

    '''
    Which is what sends the campaign to a back to back comparison rather than to a purchase order.
    '''

    results = codeInterface.reportImprovement(case)

    assert results['both'] < results['as tested']
    assert 0.01 / results['both'] < 3.0

def testTheDataSystemCannotSupportTheStabilityObjective(case):

    stage = codeInterface.reportInstrumentation(case)

    assert stage['sampling']['detects'] is False
    assert stage['stability']['adequate'] is True
    assert stage['stability']['pulseGunViable'] is True

def testTheBurnIsLongEnoughForBothSettlingTimes(case):

    stage = codeInterface.reportInstrumentation(case)

    assert stage['duration']['settlesWall'] is True
    assert stage['duration']['usableThermalWindow'] > 0.0

# ------------------------------------------------------------------------------------------------ #
# -- The example itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleNamesTheTacitHalfItDoesNotCover(capsys):

    '''
    The objectives for this sub-domain said the knowledge is largely tacit. The example has to say
    which half it captured, because claiming the rest by omission would be the worse outcome.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'tacit half' in printed

def testTheExampleShowsTheRefusalRatherThanDescribingIt(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'REFUSED' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
