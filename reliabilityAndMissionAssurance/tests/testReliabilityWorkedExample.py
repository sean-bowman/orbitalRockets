# -- Tests for the reliabilityAndMissionAssurance worked example -- #

'''

The example argues that reliability engineering keeps producing numbers whose form matters more
than their value. The tests pin the four stage results, the three refusals that carry them, and the
scope decisions.

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

sys.path.insert(0, os.path.join(DOMAIN, 'reliabilityAndMissionAssuranceLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'reliabilityCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['reliabilityCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from reliabilityUtils import FmecaError, FaultTreeError, AllocationError, RedundancyError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the FMECA -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTwoRankingsDisagreeInTheCase(case):

    table = codeInterface.buildFmeca(case).calculateTable()

    assert table['rankingsAgree'] is False

def testCatastrophicModesAreBuriedByTheDetectionColumn(case):

    disagreement = codeInterface.buildFmeca(case).rankingDisagreement()

    assert disagreement['anyBuried'] is True
    assert len(disagreement['buried']) >= 2

def testMostOfTheTableIsMandatoryReview(case):

    '''
    On a launch vehicle almost every mode is severe, which is exactly why a ranking that sorts by
    an ordinal product is the wrong instrument for finding the ones that matter.
    '''

    analysis = codeInterface.buildFmeca(case)
    review = analysis.mandatoryReview()

    assert review['share'] > 0.7

def testTheUnactionedFindingIsRefused(case):

    analysis = codeInterface.buildFmeca(case)

    with pytest.raises(FmecaError):
        analysis.checkActions()

def testActioningEverythingClearsTheCheck(case):

    complete = codeInterface.buildFmeca(case, actionAll = True)
    result = complete.checkActions()

    assert result['unactioned'] == []

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the fault tree -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSinglePointFailuresCarryTheWholeTree(case):

    analysis = codeInterface.buildFaultTree(case).analyseCutSets()

    assert analysis['singlePointCount'] >= 4
    assert analysis['singlePointShare'] > 0.99

def testTheRedundantPairsContributeAlmostNothing(case):

    analysis = codeInterface.buildFaultTree(case).analyseCutSets()

    pairs = [entry for entry in analysis['cutSets'] if entry['order'] == 2]

    assert pairs
    assert sum(entry['share'] for entry in pairs) < 0.01

def testTheRareEventSumOverstatesSlightly(case):

    analysis = codeInterface.buildFaultTree(case).analyseCutSets()

    assert analysis['rareEventSum'] > analysis['exactProbability']
    assert analysis['rareEventError'] < 0.01

def testImportanceAndProbabilityRankDifferently(case):

    '''
    The redundant avionics units sit orders of magnitude below the single valve on importance and
    above it on probability, which is the whole reason to compute importance at all.
    '''

    importance = codeInterface.buildFaultTree(case).importance()
    byName = {entry['event']: entry for entry in importance['results']}

    assert byName['mainValveFail']['importance'] > 100.0 * byName['avionicsA']['importance']
    assert byName['avionicsA']['probability'] > byName['mainValveFail']['probability']

def testUnacceptedSinglePointFailuresAreRefused(case):

    tree = codeInterface.buildFaultTree(case)
    accepted = case['faultTree']['acceptedSinglePoints']

    with pytest.raises(FaultTreeError):
        tree.checkSinglePoints(accepted)

def testAcceptingThemAllClearsTheCheck(case):

    tree = codeInterface.buildFaultTree(case)
    everything = tree.analyseCutSets()['singlePoints']

    result = tree.checkSinglePoints(everything)

    assert result['unaccepted'] == []

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the budget -- #
# ------------------------------------------------------------------------------------------------ #

def testTheBudgetClosesButOnlyJust(case):

    rollup = codeInterface.buildBudget(case).calculateRollup()

    assert rollup['meetsTarget'] is True
    assert rollup['margin'] < 1.5

def testOneSubsystemHoldsHalfTheFailureBudget(case):

    rollup = codeInterface.buildBudget(case).calculateRollup()

    assert rollup['isDominated'] is True
    assert rollup['dominantShare'] > 0.5

def testAThirdOfTheBudgetHasNoEvidenceBehindIt(case):

    audit = codeInterface.buildBudget(case).basisAudit()

    assert audit['assumedShare'] > 0.3
    assert audit['evidencedShare'] < 0.7

def testDemonstratingTheTargetWouldTakeManyFlights(case):

    demonstration = codeInterface.buildBudget(case).demonstrationCost()

    assert demonstration['flights'] > 50.0
    assert demonstration['perNine'] == pytest.approx(10.0, rel = 0.1)

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: redundancy -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDualSetFailsItsRequirementOnCommonCause(case):

    '''
    The result the stage exists to produce. The ideal arithmetic clears the requirement and the
    real one does not, which is exactly the error the beta factor exists to catch.
    '''

    analysis = codeInterface.buildRedundancy(case)

    with pytest.raises(RedundancyError):
        analysis.checkRequirement()

    configuration = analysis.calculateConfiguration()

    assert 1.0 - configuration['idealFailure'] > case['redundancy']['requiredReliability']
    assert configuration['systemReliability'] < case['redundancy']['requiredReliability']

def testCommonCauseDominatesTheDualSet(case):

    configuration = codeInterface.buildRedundancy(case).calculateConfiguration()

    assert configuration['commonCauseDominated'] is True
    assert configuration['commonCauseShare'] > 0.9

def testLoweringBetaClearsWhereAddingUnitsWouldNot(case):

    analysis = codeInterface.buildRedundancy(case)

    levers = analysis.compareLevers()

    assert levers['betaWins'] is True

    diverse = codeInterface.buildRedundancy(case, sharing = 'diverseDesign')
    check = diverse.checkRequirement()

    assert check['systemReliability'] >= case['redundancy']['requiredReliability']

def testSeparationAloneDoesNotCloseIt(case):

    separated = codeInterface.buildRedundancy(case, sharing = 'sameDesignSeparated')

    with pytest.raises(RedundancyError):
        separated.checkRequirement()

# ------------------------------------------------------------------------------------------------ #
# -- The whole example -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleRunsEndToEnd(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert len(printed.splitlines()) > 150

def testTheExampleStatesTheDomainEthos(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'A reliability number without a stated basis is a wish' in printed
    assert 'Redundancy that shares a failure cause is not redundancy' in printed
    assert 'An unactioned finding is' in printed

def testTheExampleNamesWhatItDeliberatelyDidNotBuild(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    for absent in ('Component failure rate prediction',
                   'Quality systems, configuration management and problem reporting',
                   'Human error probability',
                   'The FTS reliability case',
                   'Derating curves',
                   'Bayesian updating'):
        assert absent in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
