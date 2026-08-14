# -- Tests for the reliabilityAndMissionAssurance library -- #

'''

Three tiers. Tier one is inputs and refusals, tier two is the probability arithmetic, and tier three
is the beta factor model and the cross-domain consistency the repository depends on.

There is no external standard here to reproduce. What can be asserted is that the arithmetic is
exact, that the structural results hold for every input, and that the tables agree with the register.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'reliabilityAndMissionAssuranceLibrary'))
sys.path.insert(0, ROOT)

from reliabilityUtils import (BETA_FACTORS, SEVERITY_CLASSES, DETECTION_CLASSES, FAILURE_RATES,
                              DEFAULT_COVERAGE,
                              seriesReliability, parallelReliability, betaFactorReliability,
                              zeroFailureDemonstration,
                              InvalidInputError, FmecaError, FaultTreeError,
                              AllocationError, RedundancyError)

from validation.referenceCases import RANGE_SAFETY_CRITERIA, UNVALIDATED

from FMECA import FMECA
from FaultTree import FaultTree
from ReliabilityBudget import ReliabilityBudget
from RedundancyAnalysis import RedundancyAnalysis

# ------------------------------------------------------------------------------------------------ #
# -- Fixtures -- #
# ------------------------------------------------------------------------------------------------ #

@pytest.fixture
def fmeca():

    analysis = FMECA()
    analysis.setInputs({'modes': [
        {'item': 'valve', 'mode': 'fails closed', 'effect': 'no start',
         'severity': 'catastrophic', 'probability': 2.0e-4, 'detection': 'certain'},
        {'item': 'regulator', 'mode': 'fails open', 'effect': 'overpressure',
         'severity': 'catastrophic', 'probability': 5.0e-4, 'detection': 'unlikely'},
        {'item': 'bolt', 'mode': 'fails to release', 'effect': 'stage retained',
         'severity': 'catastrophic', 'probability': 5.0e-4, 'detection': 'undetectable'},
        {'item': 'heater', 'mode': 'fails off', 'effect': 'freezes',
         'severity': 'critical', 'probability': 2.0e-3, 'detection': 'likely'},
        {'item': 'telemetry', 'mode': 'dropout', 'effect': 'lost data',
         'severity': 'negligible', 'probability': 1.0e-2, 'detection': 'certain'}],
        'actioned': ['fails closed', 'fails open', 'fails to release']})

    return analysis

@pytest.fixture
def tree():

    component = FaultTree()
    component.setInputs({'topEvent': 'missionLoss',
                         'gates': {
                             'missionLoss':  {'type': 'or',  'inputs': ['propulsion', 'control']},
                             'propulsion':   {'type': 'or',  'inputs': ['startFail', 'valveFail']},
                             'control':      {'type': 'and', 'inputs': ['avionicsA', 'avionicsB']}},
                         'basicEvents': {'startFail': 2.0e-3, 'valveFail': 2.0e-4,
                                         'avionicsA': 1.0e-3, 'avionicsB': 1.0e-3}})

    return component

@pytest.fixture
def budget():

    component = ReliabilityBudget()
    component.setInputs({'target': 0.97, 'itemReliability': 0.99995,
                         'subsystems': [
                             {'name': 'propulsion',    'reliability': 0.9850, 'basis': 'heritage'},
                             {'name': 'fluid systems', 'reliability': 0.9940, 'basis': 'assumed'},
                             {'name': 'separation',    'reliability': 0.9960, 'basis': 'allocated'},
                             {'name': 'avionics',      'reliability': 0.9970, 'basis': 'demonstrated'},
                             {'name': 'structures',    'reliability': 0.9995, 'basis': 'predicted'}]})

    return component

@pytest.fixture
def redundancy():

    component = RedundancyAnalysis()
    component.setInputs({'elementReliability': 0.99, 'units': 2,
                         'sharing': 'identicalDifferentLot',
                         'requiredReliability': 0.9995})

    return component

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: inputs and refusals -- #
# ------------------------------------------------------------------------------------------------ #

def testAModeWithoutABasisOfSeverityIsRefused():

    analysis = FMECA()

    with pytest.raises(InvalidInputError):
        analysis.setInputs({'modes': [{'item': 'a', 'mode': 'b', 'effect': 'c',
                                       'severity': 'apocalyptic', 'probability': 1.0e-4,
                                       'detection': 'certain'}]})

def testDuplicateModeNamesAreRefused():

    '''
    A mode listed twice under different names is a mode that will be actioned once and closed
    twice, which is a specific and common way a FMECA goes wrong.
    '''

    analysis = FMECA()

    with pytest.raises(FmecaError):
        analysis.setInputs({'modes': [
            {'item': 'a', 'mode': 'same', 'effect': 'c', 'severity': 'critical',
             'probability': 1.0e-4, 'detection': 'certain'},
            {'item': 'b', 'mode': 'same', 'effect': 'd', 'severity': 'critical',
             'probability': 1.0e-4, 'detection': 'certain'}]})

def testAnActionAgainstANonexistentModeIsRefused(fmeca):

    analysis = FMECA()

    with pytest.raises(FmecaError):
        analysis.setInputs({'modes': [{'item': 'a', 'mode': 'b', 'effect': 'c',
                                       'severity': 'critical', 'probability': 1.0e-4,
                                       'detection': 'certain'}],
                            'actioned': ['something else']})

def testAnUnactionedMandatoryReviewModeIsRefused(fmeca):

    '''
    The domain ethos in code. An unactioned finding converts a real hazard into a document saying
    the hazard was considered.
    '''

    with pytest.raises(FmecaError):
        fmeca.checkActions()

def testAGateWithNoInputsIsRefused():

    component = FaultTree()

    with pytest.raises(InvalidInputError):
        component.setInputs({'topEvent': 'top',
                             'gates': {'top': {'type': 'or', 'inputs': []}},
                             'basicEvents': {}})

def testACycleInTheTreeIsRefused():

    component = FaultTree()

    with pytest.raises(FaultTreeError):
        component.setInputs({'topEvent': 'a',
                             'gates': {'a': {'type': 'or', 'inputs': ['b']},
                                       'b': {'type': 'or', 'inputs': ['a']}},
                             'basicEvents': {}})

def testAnUndefinedGateInputIsRefused():

    component = FaultTree()

    with pytest.raises(InvalidInputError):
        component.setInputs({'topEvent': 'a',
                             'gates': {'a': {'type': 'or', 'inputs': ['ghost']}},
                             'basicEvents': {}})

def testAnUnacceptedSinglePointFailureIsRefused(tree):

    with pytest.raises(FaultTreeError):
        tree.checkSinglePoints(accepted = ['startFail'])

def testASubsystemWithoutABasisIsRefused():

    '''
    A reliability number without a stated basis is a wish, so the basis is required rather than
    optional.
    '''

    component = ReliabilityBudget()

    with pytest.raises(InvalidInputError):
        component.setInputs({'subsystems': [{'name': 'a', 'reliability': 0.99}]})

def testAnUnknownBasisIsRefused():

    component = ReliabilityBudget()

    with pytest.raises(InvalidInputError):
        component.setInputs({'subsystems': [{'name': 'a', 'reliability': 0.99,
                                             'basis': 'confident'}]})

def testABudgetThatDoesNotCloseIsRefused(budget):

    budget.target = 0.99

    with pytest.raises(AllocationError):
        budget.calculateRollup()

def testABetaOfOneIsRefused():

    component = RedundancyAnalysis()

    with pytest.raises(InvalidInputError):
        component.setInputs({'elementReliability': 0.99, 'units': 2, 'beta': 1.0})

def testARedundancyClaimBelowItsRequirementIsRefused(redundancy):

    with pytest.raises(RedundancyError):
        redundancy.checkRequirement()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: the arithmetic -- #
# ------------------------------------------------------------------------------------------------ #

def testSeriesReliabilityMultiplies():

    assert seriesReliability([0.9, 0.9]) == pytest.approx(0.81)
    assert seriesReliability([0.999] * 100) == pytest.approx(0.999 ** 100)
    assert seriesReliability([0.999] * 100) == pytest.approx(0.9048, abs = 1.0e-4)

def testParallelReliabilityMultipliesTheUnreliabilities():

    assert parallelReliability([0.9, 0.9]) == pytest.approx(0.99)
    assert parallelReliability([0.99] * 3) == pytest.approx(1.0 - 1.0e-6)

def testTheCommonCauseTermDoesNotFallWithUnitCount():

    '''
    The domain's headline result. The independent term falls as the nth power and the common cause
    term does not fall at all, so above a couple of units the second term is the answer.
    '''

    common = [betaFactorReliability(0.99, count, 0.10)['commonCauseTerm']
              for count in (2, 3, 4, 5)]

    assert all(value == pytest.approx(common[0]) for value in common)

def testCommonCauseDominatesADualRedundantSet():

    result = betaFactorReliability(0.99, 2, 0.10)

    assert result['commonCauseShare'] > 0.9
    assert result['systemFailure'] > 10.0 * result['idealFailure']

def testASingleUnitHasNoCommonCause():

    '''
    A single unit has nothing to share a cause with. Applying the beta split at n = 1 would report
    it as more reliable than its own element, which is the sort of quiet error a redundancy model
    should not contain.
    '''

    result = betaFactorReliability(0.99, 1, 0.10)

    assert result['systemFailure'] == pytest.approx(0.01)
    assert result['commonCauseTerm'] == 0.0
    assert result['penalty'] == pytest.approx(1.0)

def testABetaOfZeroReproducesTheIdealCase():

    for count in (1, 2, 3, 4):
        result = betaFactorReliability(0.99, count, 0.0)
        assert result['systemFailure'] == pytest.approx(result['idealFailure'])

def testTheThirdUnitBuysAlmostNothing(redundancy):

    sweep = redundancy.unitSweep()['sweep']

    assert sweep[1]['marginalGain'] > 0.5
    assert sweep[2]['marginalGain'] < 0.15
    assert sweep[3]['marginalGain'] < 0.02

def testLoweringBetaBeatsAddingAUnit(redundancy):

    levers = redundancy.compareLevers()

    assert levers['betaWins'] is True
    assert levers['ratio'] > 2.0

def testTheSharingLadderIsOrdered(redundancy):

    results = redundancy.betaSweep()['results']

    assert all(results[index]['beta'] <= results[index + 1]['beta']
               for index in range(len(results) - 1))
    assert results[0]['sharing'] == 'diverseAndSeparated'

def testAFaultTreeOrGateIsTheComplementProduct(tree):

    probability = tree.calculateProbability('propulsion')

    assert probability == pytest.approx(1.0 - (1.0 - 2.0e-3) * (1.0 - 2.0e-4))

def testAFaultTreeAndGateIsTheProduct(tree):

    assert tree.calculateProbability('control') == pytest.approx(1.0e-3 * 1.0e-3)

def testTheSinglePointFailuresAreTheOrderOneCutSets(tree):

    analysis = tree.analyseCutSets()

    assert set(analysis['singlePoints']) == {'startFail', 'valveFail'}
    assert analysis['singlePointShare'] > 0.99

def testTheRareEventSumOverstatesTheTopEvent(tree):

    analysis = tree.analyseCutSets()

    assert analysis['rareEventSum'] > analysis['exactProbability']
    assert analysis['rareEventError'] < 0.01

def testCutSetsAreMinimal(tree):

    cutSets = tree.minimalCutSets()

    for outer in cutSets:
        for inner in cutSets:
            if outer is not inner:
                assert not (inner < outer)

def testImportanceIsNotProbability(tree):

    '''
    An event in a single point cut set has an importance near one whatever its probability, and an
    event behind an AND gate has an importance of roughly its partner probability.
    '''

    importance = tree.importance()
    byName = {entry['event']: entry for entry in importance['results']}

    assert byName['valveFail']['importance'] > 0.9
    assert byName['avionicsA']['importance'] < 0.01
    assert byName['avionicsA']['probability'] > byName['valveFail']['probability']

def testTheBudgetSharesSumToOne(budget):

    rollup = budget.calculateRollup()

    assert sum(entry['share'] for entry in rollup['subsystems']) == pytest.approx(1.0)

def testFailureProbabilitiesAreNearlyAdditive(budget):

    rollup = budget.calculateRollup()

    assert rollup['additiveError'] < 0.02

def testTheDominantSubsystemHoldsMostOfTheBudget(budget):

    rollup = budget.calculateRollup()

    assert rollup['isDominated'] is True
    assert rollup['dominant'] == 'propulsion'

def testTheBasisAuditSeparatesEvidenceFromAssumption(budget):

    audit = budget.basisAudit()

    assert 0.0 < audit['evidencedShare'] < 1.0
    assert audit['assumedShare'] > 0.2
    assert audit['evidencedShare'] + audit['assumedShare'] <= 1.0 + 1.0e-9

def testItemCountIsAReliabilityParameter(budget):

    sweep = budget.itemCountEffect([10, 100, 1000])['sweep']

    assert sweep[0]['reliability'] > sweep[1]['reliability'] > sweep[2]['reliability']
    assert sweep[2]['failure'] > 50.0 * sweep[0]['failure']

def testAllocationDividesTheAllowedUnreliability(budget):

    allocation = budget.allocate()

    total = sum(entry['allocatedFailure'] for entry in allocation['allocations'])

    assert total == pytest.approx(allocation['allowed'])

def testTheCriticalityAndPriorityRankingsCanDisagree(fmeca):

    table = fmeca.calculateTable()

    assert table['rankingsAgree'] is False

def testADetectableCatastropheIsBuriedByTheRiskPriorityNumber(fmeca):

    '''
    A catastrophic mode that is detectable sorts below a less severe one that is not, which is
    exactly backwards for a launch vehicle.
    '''

    disagreement = fmeca.rankingDisagreement()

    assert disagreement['anyBuried'] is True
    assert 'fails closed' in disagreement['buried']

def testTheMandatoryReviewUsesNoOrdinalProduct(fmeca):

    review = fmeca.mandatoryReview()

    for mode in review['modes']:
        assert SEVERITY_CLASSES[mode['severity']]['rank'] >= 3

def testCriticalityIsSeverityTimesOccurrence(fmeca):

    for mode in fmeca.calculateTable()['modes']:
        assert mode['criticality'] == mode['severityRank'] * mode['occurrence']
        assert mode['riskPriority'] == mode['criticality'] * mode['detectionRank']

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the tables, and the cross-domain consistency -- #
# ------------------------------------------------------------------------------------------------ #

def testTheBetaFactorOrderingIsStructural():

    '''
    Units that share a design share its design errors, and units that share an environment share
    what the environment does to them. The ordering is a mechanism rather than a value.
    '''

    assert (BETA_FACTORS['identicalSameBatch']['beta']
            > BETA_FACTORS['identicalDifferentLot']['beta']
            > BETA_FACTORS['sameDesignSeparated']['beta']
            > BETA_FACTORS['diverseDesign']['beta']
            > BETA_FACTORS['diverseAndSeparated']['beta'])

def testTheSeverityAndDetectionScalesAreOrdinalAndOrdered():

    assert SEVERITY_CLASSES['catastrophic']['rank'] > SEVERITY_CLASSES['negligible']['rank']

    # A high detection rank is bad, which is the convention that catches people.
    assert DETECTION_CLASSES['undetectable']['rank'] > DETECTION_CLASSES['certain']['rank']

def testSingleShotDevicesDominateTheFailureRateTable():

    '''
    Single-shot devices are non-redundant by construction and are used exactly once at a moment
    that cannot be repeated, which is why they dominate a launch vehicle fault tree.
    '''

    perDemand = {name: entry['perDemand'] for name, entry in FAILURE_RATES.items()
                 if 'perDemand' in entry}

    assert perDemand['separationBolt'] > perDemand['structuralJoint'] * 100.0
    assert perDemand['engineStart'] == max(perDemand.values())

def testTheDemonstrationArithmeticAgreesWithRangeSafety():

    '''
    The same zero-failure binomial rangeSafetyAndFTS applies to a flight termination system. It is
    implemented in both because both need it, and this asserts the two agree rather than letting
    them drift.
    '''

    reference = RANGE_SAFETY_CRITERIA['14-CFR-450']

    here = zeroFailureDemonstration(reference['flightSafetyReliability'],
                                    reference['flightSafetyConfidence'])

    assert here == pytest.approx(reference['zeroFailureTests'], rel = 1.0e-3)

def testTheDomainRegistersWhatItCannotValidate():

    registered = {name for name, entry in UNVALIDATED.items()
                  if entry['domain'] == 'reliabilityAndMissionAssurance'}

    assert registered == {'betaFactors', 'componentFailureRates', 'ordinalScales'}

    for name in registered:
        entry = UNVALIDATED[name]
        assert entry['reason'] and entry['consequence'] and entry['nextStep']
