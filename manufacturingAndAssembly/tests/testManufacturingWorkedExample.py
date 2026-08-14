# -- Tests for the manufacturingAndAssembly worked example -- #

'''

The example argues that manufacturing is full of quantities governed by one term and estimated as
though they were governed by all of them. The tests pin the three stage results and the scope
decisions, which matter here more than in most domains because the process physics lives in ten
sub-domains under aerospaceMaterials.

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

sys.path.insert(0, os.path.join(DOMAIN, 'manufacturingLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'manufacturingCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['manufacturingCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from manufacturingUtils import NDE_METHODS, ToleranceError, RateError, InspectionError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the stack -- #
# ------------------------------------------------------------------------------------------------ #

def testTheStackHasFewerContributorsThanThreeSigmaNeeds(case):

    '''
    The whole first result depends on this. Above nine contributors the statistical method would be
    a genuine saving and the stage would say something else.
    '''

    stack = codeInterface.buildStack(case).calculateStack()

    assert stack['count'] < 9
    assert stack['statisticalHelps'] is False

def testTheStatisticalStackAtThreeSigmaExceedsTheWorstCase(case):

    component = codeInterface.buildStack(case)
    stack = component.calculateStack()

    assert stack['statistical'] * component.sigmaLevel > stack['worstCase']

def testOneContributorHoldsHalfTheStatisticalStack(case):

    stack = codeInterface.buildStack(case).calculateStack()

    assert stack['isDominated'] is True
    assert stack['dominantShare'] >= 0.5

def testTheDominantContributorIsLargerInTheStatisticalRanking(case):

    stack = codeInterface.buildStack(case).calculateStack()
    dominant = stack['contributors'][0]

    assert dominant['statisticalShare'] > dominant['worstCaseShare'] * 1.3

def testTighteningTheDominantContributorMovesTheProblem(case):

    before = codeInterface.buildStack(case).calculateStack()
    after = codeInterface.buildStack(case, improved = True).calculateStack()

    assert after['dominant'] != before['dominant']
    assert after['worstCase'] < before['worstCase']
    assert after['isDominated'] is True

def testTheGapClearsAtBothMethodsAndNeedsAShim(case):

    stack = codeInterface.buildStack(case)

    for method in ('worstCase', 'statistical'):
        check = stack.checkGap(method)
        assert check['smallestGap'] > 0.0
        assert check['needsShim'] is True

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the inspection -- #
# ------------------------------------------------------------------------------------------------ #

def testTheFullWallCaseClearsAndTheThinWallCaseDoesNot(case):

    '''
    The result the stage exists to produce, and the pair is the point: the same weld and the same
    inspection, and the only thing that changed is the critical flaw size.
    '''

    full = codeInterface.buildInspection(case)
    check = full.checkAgainstCriticalFlaw()

    assert check['margin'] > 1.0

    thin = codeInterface.buildInspection(case, thinWall = True)

    with pytest.raises(InspectionError):
        thin.checkAgainstCriticalFlaw()

def testTheThinWallCaseMissesRealFlaws(case):

    from manufacturingUtils import logOddsPod

    thin = codeInterface.buildInspection(case, thinWall = True)
    missed = 1.0 - float(logOddsPod(case['inspection']['thinWallCriticalFlawSize'],
                                    thin.a50, thin.sigma))

    assert missed > 0.10

def testTheDemonstrationInTheCaseMeetsTheStandard(case):

    inspection = codeInterface.buildInspection(case)
    demonstration = inspection.demonstrationSize()

    assert demonstration['meetsMinimum'] is True
    assert demonstration['targets'] < demonstration['preciseTargets']

def testSomeMethodsEstablishNothingAtThisCriticalFlaw(case):

    methods = codeInterface.buildInspection(case).compareMethods()

    incapable = [entry for entry in methods['results']
                 if not entry.get('establishesSomething')]

    assert incapable
    assert 'visual' in [entry['method'] for entry in incapable]

def testTheCheapestCapableMethodIsNotApplicableToTheMaterial(case):

    '''
    The strongest thing in the stage. Magnetic particle clears the size requirement at a third of
    the cost of the alternatives and cannot be used on an aluminium tank at all, which is what the
    "what it misses" column exists to catch.
    '''

    methods = codeInterface.buildInspection(case).compareMethods()
    cheapest = methods['cheapestCapable']

    assert 'aluminium' in NDE_METHODS[cheapest]['misses']

def testTheMostSensitiveMethodIsNotTheCheapestCapableOne(case):

    methods = codeInterface.buildInspection(case).compareMethods()

    assert methods['best'] != methods['cheapestCapable']
    assert (NDE_METHODS[methods['best']]['relativeCost']
            > NDE_METHODS[methods['cheapestCapable']]['relativeCost'])

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the rate -- #
# ------------------------------------------------------------------------------------------------ #

def testTheLineMeetsItsDemandAndOnlyJust(case):

    takt = codeInterface.buildProduction(case).calculateTakt()

    assert takt['capacity'] >= takt['annualDemand']
    assert takt['overUtilised'] is True

def testCapacityIsFarBelowTheSumOfCycleTimesWouldSuggest(case):

    takt = codeInterface.buildProduction(case).calculateTakt()

    assert takt['bottleneckTime'] < 0.4 * takt['sumOfCycleTimes']

def testFixingTheBottleneckMovesItAndRaisesCapacity(case):

    before = codeInterface.buildProduction(case).calculateTakt()
    after = codeInterface.buildProduction(case, improved = True).calculateTakt()

    assert after['bottleneck'] != before['bottleneck']
    assert after['capacity'] > before['capacity']

def testAProgrammeOfTwentyHasBarelyLearned(case):

    cumulative = codeInterface.buildProduction(case).cumulativeCost(
        case['production']['runLength'])

    assert cumulative['lastUnitCost'] > 0.4
    assert cumulative['cumulativeAverage'] > cumulative['lastUnitCost']

def testTheLabourHeavyProcessesLearnFastest(case):

    classes = codeInterface.buildProduction(case).compareProcessClasses(20)
    results = classes['results']

    assert results[0]['processClass'] == 'manualAssembly'
    assert results[-1]['processClass'] == 'rawMaterial'

# ------------------------------------------------------------------------------------------------ #
# -- The whole example -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleRunsEndToEnd(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert len(printed.splitlines()) > 140

def testTheExampleStatesTheCrossoverResult(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'three sigma needs more than nine contributors' in printed

def testTheExampleNamesWhatItDeliberatelyDidNotBuild(capsys):

    '''
    This domain declines more than any other, because ten process sub-domains already carry the
    physics. The reasoning is written into the example rather than assumed.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    for absent in ('Machining, forming, casting and joining physics',
                   'Weld joint efficiency and HAZ knockdown',
                   'Buy-to-fly and process route comparison',
                   'Critical flaw size',
                   'Cost estimating relationships',
                   'Supplier qualification and counterfeit control'):
        assert absent in printed

def testTheExampleNamesTheSubDomainsThatCarryTheProcessPhysics(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    for subDomain in ('additiveLPBF', 'spinCasting', 'formingProcesses', 'machiningProcesses',
                      'joiningProcesses', 'postProcessing', 'extrusionHoning'):
        assert subDomain in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
