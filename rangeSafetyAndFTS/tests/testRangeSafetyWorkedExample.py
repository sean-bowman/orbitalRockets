# -- Tests for the rangeSafetyAndFTS worked example -- #

'''

The example argues that range safety is decided by things outside the vehicle. The tests pin the
three stage results, the two refusals that matter, and the scope decisions.

Author: Sean Bowman
Date:   10/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'rangeSafetyLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'rangeSafetyCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['rangeSafetyCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from rangeSafetyUtils import (LAUNCH_SAFETY_CRITERIA, FLIGHT_SAFETY_RELIABILITY,
                              ImpactPointError, RiskError, TerminationError)

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the impact point -- #
# ------------------------------------------------------------------------------------------------ #

def testTheAscentReachesInsertionWithinTheStateHistory(case):

    '''
    The whole first result depends on the last state being at or past insertion. Without it the
    example would show an impact point accelerating and never disappearing.
    '''

    trace = codeInterface.buildImpactPoint(case).traceAscent()

    assert trace['insertionTime'] is not None
    assert trace['trace'][-1]['hasImpactPoint'] is False

def testTheImpactPointAcceleratesByOrdersOfMagnitude(case):

    trace = codeInterface.buildImpactPoint(case).traceAscent()

    assert trace['driftAcceleration'] > 20.0

def testTheImpactPointStartsSlowAndEndsFast(case):

    trace = codeInterface.buildImpactPoint(case).traceAscent()
    withPoint = trace['withImpactPoint']

    assert withPoint[0]['downrange'] < 50000.0
    assert withPoint[-1]['downrange'] > 1000000.0

def testTheDestructLineIsCrossedWithUsableWarning(case):

    check = codeInterface.buildImpactPoint(case).checkDestructLine()

    assert check['crossed'] is True
    assert check['margin'] > 1.0

def testALaterDestructLineGivesLessWarning(case):

    '''
    Because the impact point accelerates, a line further downrange is crossed faster. A line sized
    on an early drift rate is sized on the wrong number.
    '''

    point = codeInterface.buildImpactPoint(case)

    early = point.checkDestructLine()

    point.destructRange = 4000000.0
    point.reactionTime = 0.1
    late = point.checkDestructLine()

    assert late['driftRateAtLine'] > early['driftRateAtLine']
    assert late['warningTime'] < early['warningTime']

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: public risk -- #
# ------------------------------------------------------------------------------------------------ #

def testTheOceanTakesTheDebrisAndTheTownTakesTheRisk(case):

    '''
    The domain's headline result, in the worked case: risk follows population rather than impact
    probability.
    '''

    collective = codeInterface.buildRisk(case).calculateCollective()
    byName = {entry['region']: entry for entry in collective['regions']}

    ocean = byName['downrange ocean']
    town = byName['coastal town']

    assert ocean['impactProbability'] > 0.8
    assert ocean['share'] < 0.05
    assert town['impactProbability'] < 0.001
    assert town['share'] > 0.8

def testBothCriteriaAreMetAndTheIndividualOneIsTighter(case):

    risk = codeInterface.buildRisk(case)

    collective = risk.calculateCollective()
    individual = risk.calculateIndividual()

    assert collective['expectedCasualties'] < collective['limit']
    assert individual['probabilityOfCasualty'] < individual['limit']
    assert individual['margin'] < collective['margin']

def testTheAnalysisInheritsTheFailureProbability(case):

    sensitivity = codeInterface.buildRisk(case).failureSensitivity([0.02, 0.20, 0.50])

    assert sensitivity['results'][0]['clears'] is True
    assert sensitivity['results'][-1]['clears'] is False
    assert 0.05 < sensitivity['limitingProbability'] < 1.0

def testMostLandUseClassesDoNotClearTheCriterion(case):

    landUse = codeInterface.buildRisk(case).compareLandUse()

    assert 'openOcean' in landUse['clearing']
    assert 'suburban' not in landUse['clearing']
    assert 'denseUrban' not in landUse['clearing']
    assert landUse['spread'] > 1.0e5

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: termination reliability -- #
# ------------------------------------------------------------------------------------------------ #

def testTheRequirementNeedsThousandsOfTests(case):

    demonstration = codeInterface.buildTermination(case).demonstrationSize()

    assert demonstration['testsRequired'] == pytest.approx(2994.0, rel = 1.0e-3)
    assert demonstration['demonstrable'] is False

def testAThirtyTestProgrammeDemonstratesAboutNinetyPerCent(case):

    demonstration = codeInterface.buildTermination(case).demonstrationSize()

    assert 0.88 < demonstration['demonstratedReliability'] < 0.93

def testTheDualSeriesConfigurationIsWorseThanNoRedundancy(case):

    comparison = codeInterface.buildTermination(case).compareConfigurations()

    assert 'dualSeries' in comparison['worseThanSingle']
    assert comparison['best'] == 'dualParallel'

def testTheAsBuiltSystemMeetsTheRequirement(case):

    check = codeInterface.buildTermination(case).checkRequirement()

    assert check['systemReliability'] >= FLIGHT_SAFETY_RELIABILITY
    assert check['weakestSeries'] == 'command receiver'

def testASingleReceiverMakesItASingleStringSystem(case):

    '''
    The failure mode the word redundant hides. The same ordnance train behind one command receiver
    fails the requirement, and the reliability is the receiver's rather than the ordnance's.
    '''

    single = codeInterface.buildTermination(case, singleReceiver = True)

    with pytest.raises(TerminationError):
        single.checkRequirement()

    configuration = single.configurationReliability()

    assert configuration['systemReliability'] < FLIGHT_SAFETY_RELIABILITY
    assert configuration['weakestSeries'] == 'command receiver'

# ------------------------------------------------------------------------------------------------ #
# -- The whole example -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleRunsEndToEnd(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert len(printed.splitlines()) > 140

def testTheExampleStatesTheDemonstrationArithmetic(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert '2,994' in printed
    assert 'argued rather than demonstrated' in printed

def testTheExampleNamesWhatItDeliberatelyDidNotBuild(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    for absent in ('Debris catalogues and fragment ballistics',
                   'Blast overpressure and quantity-distance',
                   'Toxic dispersion',
                   'Ordnance initiation',
                   'Autonomous FTS rule sets',
                   'The licensing process'):
        assert absent in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
