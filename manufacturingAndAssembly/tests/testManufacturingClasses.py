# -- Tests for the manufacturingAndAssembly library -- #

'''

Three tiers. Tier one is inputs and refusals, tier two is the closed forms, and tier three is
MIL-HDBK-1823A, read for the probability of detection model and the demonstration sizes.

The standard is reproduced rather than adjusted. Where a widely used method turns out not to help
in the regime it is applied in, the test asserts the crossover rather than the method.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'manufacturingLibrary'))
sys.path.insert(0, ROOT)

from manufacturingUtils import (NDE_METHODS, LEARNING_RATES, PROCESS_TOLERANCES,
                                MINIMUM_HIT_MISS_TARGETS, MINIMUM_SIGNAL_TARGETS,
                                UNFLAWED_SITE_RATIO, POD_LOGIT_AT_90,
                                DEFAULT_STATISTICAL_SIGMA, BOTTLENECK_UTILISATION,
                                logOddsPod, podSize, learningExponent,
                                InvalidInputError, ToleranceError, RateError, InspectionError)

from validation.referenceCases import INSPECTION_CAPABILITY, UNVALIDATED

from ToleranceStack import ToleranceStack
from InspectionCapability import InspectionCapability
from ProductionRate import ProductionRate

# ------------------------------------------------------------------------------------------------ #
# -- Fixtures -- #
# ------------------------------------------------------------------------------------------------ #

@pytest.fixture
def stack():

    component = ToleranceStack()
    component.setInputs({'nominalGap': 0.0040,
                         'minimumGap': 0.0002,
                         'maximumGap': 0.0055,
                         'sigmaLevel': 3.0,
                         'contributors': [{'name': 'roundness', 'tolerance': 0.00080},
                                          {'name': 'weld',      'tolerance': 0.00060},
                                          {'name': 'trim',      'tolerance': 0.00040},
                                          {'name': 'fixture',   'tolerance': 0.00025},
                                          {'name': 'thermal',   'tolerance': 0.00018},
                                          {'name': 'machining', 'tolerance': 0.00012}]})

    return component

@pytest.fixture
def equalStack():

    def build(count, sigmaLevel = 3.0):

        component = ToleranceStack()
        component.setInputs({'nominalGap': 0.004,
                             'sigmaLevel': sigmaLevel,
                             'contributors': [{'name': f'c{index}', 'tolerance': 3.0e-4}
                                              for index in range(count)]})
        return component

    return build

@pytest.fixture
def inspection():

    component = InspectionCapability()
    component.setInputs({'method':               'penetrant',
                         'responseType':         'hitMiss',
                         'demonstrationTargets': 80,
                         'criticalFlawSize':     0.0040,
                         'detectionMargin':      2.0})

    return component

@pytest.fixture
def production():

    component = ProductionRate()
    component.setInputs({'firstUnitCost': 1.0,
                         'processClass':  'welding',
                         'annualDemand':  24.0,
                         'shifts':        1.0,
                         'stations':      {'roll':      45.0,
                                           'longWeld':  60.0,
                                           'machining': 38.0,
                                           'circWeld':  75.0,
                                           'inspect':   50.0}})

    return component

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: inputs and refusals -- #
# ------------------------------------------------------------------------------------------------ #

def testAContributorWithNoToleranceIsRefused():

    component = ToleranceStack()

    with pytest.raises(InvalidInputError):
        component.setInputs({'nominalGap': 0.004,
                             'contributors': [{'name': 'a', 'tolerance': 0.0}]})

def testDuplicateContributorNamesAreRefused():

    component = ToleranceStack()

    with pytest.raises(InvalidInputError):
        component.setInputs({'nominalGap': 0.004,
                             'contributors': [{'name': 'a', 'tolerance': 1.0e-4},
                                              {'name': 'a', 'tolerance': 1.0e-4}]})

def testAGapThatClosesIsRefused(stack):

    stack.nominalGap = 0.0005

    with pytest.raises(ToleranceError):
        stack.checkGap('worstCase')

def testAGapBelowTheJointMinimumIsRefused(stack):

    stack.minimumGap = 0.0030

    with pytest.raises(ToleranceError):
        stack.checkGap('worstCase')

def testAnUnknownInspectionMethodIsRefused():

    component = InspectionCapability()

    with pytest.raises(InvalidInputError):
        component.setInputs({'method': 'thermography'})

def testADemonstrationBelowTheStandardMinimumIsRefused(inspection):

    '''
    a90/95 is a confidence bound, so a curve fitted to fewer targets than the standard asks for has
    bounds too wide to design against. Reporting a number from it would be reporting a number the
    standard says is not there.
    '''

    with pytest.raises(InspectionError):
        inspection.demonstrationSize(targets = 30)

def testACriticalFlawCheckWithoutACriticalFlawIsRefused():

    component = InspectionCapability()
    component.setInputs({'method': 'penetrant'})

    with pytest.raises(InspectionError):
        component.checkAgainstCriticalFlaw()

def testAnInspectionThatCannotSeeTheCriticalFlawIsRefused(inspection):

    inspection.criticalFlawSize = 0.0010

    with pytest.raises(InspectionError):
        inspection.checkAgainstCriticalFlaw()

def testADetectionMarginBelowOneIsRefused():

    component = InspectionCapability()

    with pytest.raises(InvalidInputError):
        component.setInputs({'method': 'penetrant', 'detectionMargin': 0.5})

def testALearningRateAboveOneIsRefused():

    component = ProductionRate()

    with pytest.raises(InvalidInputError):
        component.setInputs({'firstUnitCost': 1.0, 'learningRate': 1.4})

def testALineThatCannotMeetItsRateIsRefused(production):

    production.annualDemand = 40.0

    with pytest.raises(RateError):
        production.calculateTakt()

def testATaktWithoutStationsIsRefused():

    component = ProductionRate()
    component.setInputs({'firstUnitCost': 1.0, 'annualDemand': 10.0})

    with pytest.raises(RateError):
        component.calculateTakt()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: the closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testTheStatisticalStackIsTheQuadratureSum(stack):

    result = stack.calculateStack()

    tolerances = np.array([float(entry['tolerance']) for entry in stack.contributors])

    assert result['worstCase'] == pytest.approx(float(np.sum(tolerances)))
    assert result['statistical'] == pytest.approx(float(np.sqrt(np.sum(tolerances ** 2))))

def testTheStackSharesEachSumToOne(stack):

    result = stack.calculateStack()

    assert sum(entry['worstCaseShare'] for entry in result['contributors']) == pytest.approx(1.0)
    assert sum(entry['statisticalShare'] for entry in result['contributors']) == pytest.approx(1.0)

def testEqualContributorsGiveACrossoverOfExactlyRootN(equalStack):

    '''
    The domain's headline result. A k sigma statistical stack exceeds the arithmetic worst case
    whenever k is above sum(t) / sqrt(sum(t**2)), which for n equal contributors is exactly root n.
    '''

    for count in (2, 4, 6, 9, 16, 25):
        result = equalStack(count).calculateStack()
        assert result['sigmaCrossover'] == pytest.approx(np.sqrt(count))

def testThreeSigmaDoesNotHelpBelowNineContributors(equalStack):

    for count in (2, 4, 6, 9):
        assert equalStack(count).calculateStack()['statisticalHelps'] is False

    for count in (10, 16, 25):
        assert equalStack(count).calculateStack()['statisticalHelps'] is True

def testUnequalContributorsErodeTheStatisticalBenefit(stack, equalStack):

    unequal = stack.calculateStack()
    equal = equalStack(len(stack.contributors)).calculateStack()

    assert unequal['sigmaCrossover'] < equal['sigmaCrossover']
    assert unequal['unequalPenalty'] > 1.0

def testTheStatisticalSpreadIsCappedAtTheWorstCase(stack):

    '''
    The worst case is a hard bound: no combination of tolerances can exceed the arithmetic sum. A
    sigma level above the crossover produces a spread that cannot occur, so it is capped and the
    cap is reported rather than hidden.
    '''

    check = stack.checkGap('statistical')
    worstCase = stack.calculateStack()['worstCase']

    assert check['cappedAtWorstCase'] is True
    assert check['spread'] == pytest.approx(worstCase)

def testTheStatisticalRankingIsMoreConcentratedThanTheWorstCase(stack):

    result = stack.calculateStack()
    dominant = result['contributors'][0]

    assert dominant['statisticalShare'] > dominant['worstCaseShare']

def testTighteningTheDominantContributorMovesTheProblem(stack):

    before = stack.calculateStack()

    for entry in stack.contributors:
        if entry['name'] == before['dominant']:
            entry['tolerance'] = 0.00010

    after = stack.calculateStack()

    assert after['dominant'] != before['dominant']
    assert after['statistical'] < before['statistical']

def testTheRejectFractionMatchesTheNormalTail(stack):

    rejects = stack.rejectFraction()

    assert rejects['partsPerMillion'] == pytest.approx(2700.0, rel = 1.0e-3)
    assert rejects['assembliesPerReject'] == pytest.approx(370.0, rel = 1.0e-2)

def testTheProcessToleranceSpreadIsThreeOrdersOfMagnitude(stack):

    comparison = stack.compareProcesses(dimension = 3.7)

    assert comparison['spread'] > 100.0

def testThePodModelIsAHalfAtA50(inspection):

    assert logOddsPod(inspection.a50, inspection.a50, inspection.sigma) == pytest.approx(0.5)

def testPodSizeInvertsTheModel(inspection):

    for probability in (0.1, 0.5, 0.9, 0.99):
        size = podSize(probability, inspection.a50, inspection.sigma)
        assert logOddsPod(size, inspection.a50, inspection.sigma) == pytest.approx(probability)

def testTheRatioOfA90ToA50IsNineToTheSigma(inspection):

    '''
    Because logit(0.9) is log(9), the ratio depends on sigma alone and on nothing about the
    inspection or the material. The shape of a detection curve is one number.
    '''

    curve = inspection.detectionCurve()

    assert curve['a90OverA50'] == pytest.approx(9.0 ** inspection.sigma)
    assert curve['nineToTheSigma'] == pytest.approx(curve['a90OverA50'])

def testTheDetectionCurveIsMonotonic(inspection):

    curve = inspection.detectionCurve()
    probabilities = [entry['probability'] for entry in curve['curve']]

    assert all(probabilities[index] < probabilities[index + 1]
               for index in range(len(probabilities) - 1))

def testASmallerSigmaGivesASteeperCurve(inspection):

    wide = inspection.detectionCurve()['a90OverA50']
    inspection.sigma = 0.20
    steep = inspection.detectionCurve()['a90OverA50']

    assert steep < wide

def testMoreSensitiveMethodsCostMoreButNotProportionally(inspection):

    comparison = inspection.compareMethods()

    assert comparison['a90Spread'] > 5.0
    assert comparison['costSpread'] > comparison['a90Spread']

def testWrightsCurveHalvesTheExponentCorrectly():

    assert learningExponent(0.5) == pytest.approx(-1.0)
    assert learningExponent(1.0) == pytest.approx(0.0)
    assert learningExponent(0.85) == pytest.approx(np.log(0.85) / np.log(2.0))

def testEveryDoublingCostsTheSameFraction(production):

    sweep = production.doublingSweep()['sweep']

    ratios = [sweep[index + 1]['unitCost'] / sweep[index]['unitCost']
              for index in range(len(sweep) - 1)]

    assert all(ratio == pytest.approx(production.learningRate) for ratio in ratios)

def testTheAbsoluteSavingPerDoublingFalls(production):

    sweep = production.doublingSweep()['sweep'][1:]
    savings = [entry['savingFromPrevious'] for entry in sweep]

    assert all(savings[index] > savings[index + 1] for index in range(len(savings) - 1))

def testTheCumulativeAverageLagsTheUnitCost(production):

    cumulative = production.cumulativeCost(20)

    assert cumulative['cumulativeAverage'] > cumulative['lastUnitCost']
    assert cumulative['averageOverLast'] > 1.0

def testALowerLearningRateReachesALowerUnitCost(production):

    comparison = production.compareProcessClasses(20)
    results = comparison['results']

    assert results[0]['learningRate'] < results[-1]['learningRate']
    assert results[0]['lastUnitCost'] < results[-1]['lastUnitCost']

def testCapacityIsTheSlowestStationAndNotTheSum(production):

    takt = production.calculateTakt()

    assert takt['bottleneckTime'] == max(production.stations.values())
    assert takt['bottleneckTime'] < takt['sumOfCycleTimes']

def testFixingTheBottleneckBuysOnlyTheGapToTheNext(production):

    takt = production.calculateTakt()

    assert takt['gainIfFixed'] == pytest.approx(takt['bottleneckTime'] - takt['nextStationTime'])

def testTheBottleneckMovesWhenItIsFixed(production):

    before = production.calculateTakt()

    production.stations[before['bottleneck']] = before['nextStationTime'] - 1.0
    after = production.calculateTakt()

    assert after['bottleneck'] != before['bottleneck']
    assert after['capacity'] > before['capacity']

def testCapacityIsLinearInShifts(production):

    sweep = production.shiftSensitivity([1.0, 2.0, 4.0])['results']

    assert sweep[1]['capacity'] == pytest.approx(2.0 * sweep[0]['capacity'])
    assert sweep[2]['capacity'] == pytest.approx(4.0 * sweep[0]['capacity'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: against the published standard -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDemonstrationMinimumsMatchTheStandard():

    '''
    MIL-HDBK-1823A section 4.5.2.2: at least 60 targeted sites for a binary hit or miss response,
    at least 40 for a quantitative one, and at least three times as many unflawed sites as flawed
    ones so a false positive rate can be estimated.
    '''

    assert MINIMUM_HIT_MISS_TARGETS == 60
    assert MINIMUM_SIGNAL_TARGETS == 40
    assert UNFLAWED_SITE_RATIO == 3

def testTheLibraryMinimumsMatchTheValidationRegister():

    reference = INSPECTION_CAPABILITY['MIL-HDBK-1823A']

    assert MINIMUM_HIT_MISS_TARGETS == reference['minimumHitMissTargets']
    assert MINIMUM_SIGNAL_TARGETS == reference['minimumSignalTargets']
    assert UNFLAWED_SITE_RATIO == reference['unflawedSiteRatio']

def testTheDemonstrationSizeReportsTheStandardsFigures(inspection):

    demonstration = inspection.demonstrationSize()

    assert demonstration['minimumTargets'] == MINIMUM_HIT_MISS_TARGETS
    assert demonstration['unflawedSites'] == MINIMUM_HIT_MISS_TARGETS * UNFLAWED_SITE_RATIO
    assert demonstration['preciseTargets'] == 2 * MINIMUM_HIT_MISS_TARGETS

def testASignalResponseNeedsFewerTargetsThanHitMiss(inspection):

    binary = inspection.demonstrationSize()['minimumTargets']

    inspection.responseType = 'signal'
    quantitative = inspection.demonstrationSize()['minimumTargets']

    assert quantitative < binary

def testTheLogitAtNinetyIsLogNine():

    assert POD_LOGIT_AT_90 == pytest.approx(np.log(9.0))
    assert POD_LOGIT_AT_90 == pytest.approx(2.1972, rel = 1.0e-4)

def testTheRegisterRecordsWhatA9095ActuallyIs():

    '''
    a90 is a property of the inspection. a90/95 is a confidence bound on an estimate of it, so it
    depends on the demonstration size too. The handbook notes it has become a de facto design
    criterion, which is what makes the distinction worth recording rather than assuming.
    '''

    note = INSPECTION_CAPABILITY['MIL-HDBK-1823A']['confidenceNote']

    assert 'confidence bound' in note
    assert 'de facto design criterion' in note

def testTheDomainRegistersWhatItCannotValidate():

    registered = {name for name, entry in UNVALIDATED.items()
                  if entry['domain'] == 'manufacturingAndAssembly'}

    assert registered == {'inspectionCapability', 'learningRates', 'processTolerances'}

    for name in registered:
        entry = UNVALIDATED[name]
        assert entry['reason'] and entry['consequence'] and entry['nextStep']
