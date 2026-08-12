# -- Tests for the groundSystemsAndOperations worked example -- #

'''

The example argues that a launch campaign is limited by things that are counted rather than
designed: attempts, criteria, and loads in the storage tank. The tests pin that, the four stage
results, and the scope decision the domain made about what to build at all.

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

sys.path.insert(0, os.path.join(DOMAIN, 'groundSystemsLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'groundSystemsCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['groundSystemsCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from groundUtils import SitingError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The case itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheUpperStageSitsBelowTheHydrogenCrossover(case):

    '''
    The whole first result depends on this. Above the crossover the flat fourteen per cent governs
    and the stage would be an unremarkable siting input.
    '''

    siting = codeInterface.buildSiting(case)

    assert (case['vehicle']['secondStage']['propellantMass']
            < siting.hydrogenCrossover()['crossoverMass'])

def testTheFirstStageSitsAboveTheKeroseneBreakMass(case):

    '''
    Which puts it on the two-tier branch of the standard's RP-1 rule, so its effective fraction is
    below twenty per cent.
    '''

    siting = codeInterface.buildSiting(case)
    kerosene = siting.calculateEquivalent()['contributions'][0]

    assert kerosene['effectiveFraction'] < 0.20
    assert 'two tier' in kerosene['governing']

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: siting -- #
# ------------------------------------------------------------------------------------------------ #

def testTheHydrogenStageExceedsAFlatFourteenPerCentReading(case):

    siting = codeInterface.buildSiting(case)
    hydrogen = siting.calculateEquivalent()['contributions'][1]

    assert hydrogen['effectiveFraction'] > 0.14
    assert hydrogen['governing'].startswith('sublinear')

def testTheEffectiveFractionRisesAsTheHydrogenLoadFalls(case):

    siting = codeInterface.buildSiting(case)
    samples = siting.hydrogenCrossover()['samples']

    fractions = [entry['effectiveFraction'] for entry in samples]

    assert all(fractions[index] >= fractions[index + 1] for index in range(len(fractions) - 1))
    assert fractions[0] > 0.30

def testTheSmallestSampledStageIsMoreThanTwiceTheFlatFraction(case):

    siting = codeInterface.buildSiting(case)
    smallest = siting.hydrogenCrossover()['samples'][0]

    assert smallest['effectiveFraction'] > 2.0 * 0.14

def testAddingTheUpperStageMovesTheSitingDistance(case):

    withStage = codeInterface.buildSiting(case, withUpperStage = True)
    without   = codeInterface.buildSiting(case, withUpperStage = False)

    near = without.calculateDistances(['inhabitedBuilding'])['rings'][0]['distance']
    far  = withStage.calculateDistances(['inhabitedBuilding'])['rings'][0]['distance']

    assert far > near

def testTheBindingFacilityIsNotTheFurthestOne(case):

    '''
    The binding facility is the one whose criterion is strictest relative to where it sits, which
    is a different question from which is closest. On this layout the propellant farm binds.
    '''

    siting = codeInterface.buildSiting(case)
    check = siting.checkFacilities()

    closest = min(check['facilities'], key = lambda entry: entry['actual'])

    assert check['binding']['ratio'] < 3.0
    assert check['binding']['name'] == closest['name']
    assert check['binding']['ratio'] > 1.0

def testEveryFacilityInTheCaseClears(case):

    siting = codeInterface.buildSiting(case)

    assert all(entry['ratio'] > 1.0 for entry in siting.checkFacilities()['facilities'])

def testMovingTheBindingFacilityInsideItsRingIsRefused(case):

    siting = codeInterface.buildSiting(case)
    siting.facilities = [{'name': 'propellant farm', 'distance': 100.0,
                          'criterion': 'unbarricadedIntraline'}]

    with pytest.raises(SitingError):
        siting.checkFacilities()

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: loading -- #
# ------------------------------------------------------------------------------------------------ #

def testChillDownRatherThanFastFillDominatesTheTankingTime(case):

    '''
    The phase everybody pictures is not the phase that takes the time, because chill-down runs at a
    fraction of the transfer rate by necessity: the point of it is to boil.
    '''

    loading = codeInterface.buildLoading(case)
    sequence = loading.calculatePhases()

    assert sequence['longestPhase']['phase'] == 'chilldown'
    assert sequence['longestShare'] > 0.5

def testOneAttemptDrawsHalfAgainTheFlightLoad(case):

    loading = codeInterface.buildLoading(case)

    assert loading.calculateGroundDemand()['demandRatio'] > 1.4

def testAScrubCostsMostOfAFlightLoad(case):

    loading = codeInterface.buildLoading(case)

    assert loading.scrubCost()['lostFraction'] > 0.8

def testTheStorageIsTheBindingConstraintOnTheCampaign(case):

    '''
    The result the domain closes on. The schedule allows more attempts than the storage supports,
    so the campaign is propellant limited, and that is a resupply contract rather than an
    engineering change.
    '''

    loading = codeInterface.buildLoading(case)
    timeline = codeInterface.buildTimeline(case)

    supported = loading.scrubCost()['attemptsAffordable']
    allowed = timeline.attemptsPerCampaign(case['countdown']['campaignDuration'])['attempts']

    assert allowed > supported

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: countdown -- #
# ------------------------------------------------------------------------------------------------ #

def testTheCountIsShorterThanTheSumOfItsTasks(case):

    timeline = codeInterface.buildTimeline(case)
    path = timeline.calculateCriticalPath()

    assert path['parallelGain'] > 1.5

def testTheKeroseneChainRatherThanTheHydrogenChainIsCritical(case):

    timeline = codeInterface.buildTimeline(case)
    path = timeline.calculateCriticalPath()

    assert 'LO2 load stage 1' in path['criticalPath']
    assert 'LH2 load stage 2' not in path['criticalPath']

def testTheRecycleIsSeveralTimesTheHold(case):

    timeline = codeInterface.buildTimeline(case)
    hold = case['countdown']['hold']

    recycle = timeline.calculateRecycle(hold['holdAt'], hold['backUpTo'], hold['holdDuration'])

    assert recycle['multiplier'] > 2.0
    assert recycle['fitsWindow'] is True

def testOneDriverSetsTheTurnaroundAndFixingItBuysOnlyTheGap(case):

    timeline = codeInterface.buildTimeline(case)
    turnaround = timeline.calculateTurnaround()

    assert turnaround['governing'].startswith('LH2')
    assert turnaround['turnaround'] < turnaround['sumOfDrivers'] * 0.6
    assert turnaround['gainIfFixed'] < turnaround['turnaround']

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: availability -- #
# ------------------------------------------------------------------------------------------------ #

def testSixCriteriaCostFarMoreThanTheWorstOneAlone(case):

    availability = codeInterface.buildAvailability(case, 1)
    result = availability.calculatePerAttempt()

    assert result['perAttempt'] < 0.65
    assert result['combinedPenalty'] > 0.25

def testAttemptsBeatCriteriaAndByMostWhenThereAreFewest(case):

    ladder = [codeInterface.buildAvailability(case, count).compareLevers()
              for count in (1, 2, 3, 4)]

    assert all(entry['attemptsWin'] for entry in ladder)
    assert ladder[0]['ratio'] > ladder[-1]['ratio']
    assert ladder[0]['ratio'] > 5.0

def testCorrelationCostsTheCampaignAndTheGapIsReported(case):

    availability = codeInterface.buildAvailability(case, 8)
    campaign = availability.calculateCampaign()

    assert campaign['correlated'] < campaign['independent']
    assert campaign['conditionalAfterScrub'] < campaign['perAttempt']

# ------------------------------------------------------------------------------------------------ #
# -- The whole example -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleRunsEndToEnd(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert len(printed.splitlines()) > 150

def testTheExampleStatesTheStandardsMetricDiscrepancy(capsys):

    '''
    Found by reading the standard rather than a summary of it, and reported in the example rather
    than buried in a comment.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'not the same rule' in printed
    assert '4.13' in printed
    assert '6.147' in printed

def testTheExampleNamesWhatItDeliberatelyDidNotBuild(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    for absent in ('GSE fluid analysis', 'Chill-down mass', 'Boil-off from insulation',
                   'Umbilical retract dynamics', 'Weather forecasting'):
        assert absent in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
