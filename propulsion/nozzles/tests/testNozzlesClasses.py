# -- Tests for the nozzles classes -- #

'''

Tiered tests for the two nozzle classes.

Tier 1 covers the contract: unknown contours, an area ratio at or below the throat, a zero ambient
pressure handed to a separation criterion that has no meaning in vacuum, and an empty ascent
profile.

Tier 2 validates against closed forms: the divergence efficiency against its definition, the
Schmucker criterion against its correlation, and the loss decomposition against the product it
claims to be.

Tier 3 covers the results this sub-domain exists to produce, chiefly that the thrust coefficient
efficiency the propulsion hub carries as a single number decomposes into three mechanisms, and that
most of the altitude compensation prize is at altitude rather than at sea level.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'nozzlesLibrary'))

from nozzleUtils import (NOZZLE_CONTOURS, ALTITUDE_COMPENSATION, SUMMERFIELD_SEPARATION_RATIO,
                         SCHMUCKER_COEFFICIENT, SCHMUCKER_EXPONENT,
                         TYPICAL_BOUNDARY_LAYER_LOSS, TYPICAL_KINETIC_LOSS,
                         divergenceEfficiency, schmuckerSeparationPressure,
                         idealCompensatingAreaRatio, convertAltitudeToPressure,
                         InvalidInputError, ContourError, SeparationError, NozzleError)
from NozzleLosses import NozzleLosses
from AltitudeCompensation import AltitudeCompensation, RECOVERY_FRACTION, MASS_PENALTY

def buildLosses(**overrides) -> NozzleLosses:

    inputs = {'combination': 'LOX/RP-1', 'areaRatio': 20.35, 'chamberPressure': 10.0e6}
    inputs.update(overrides)

    losses = NozzleLosses()
    losses.setInputs(inputs)

    return losses

def buildCompensation(**overrides) -> AltitudeCompensation:

    inputs = {'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6, 'areaRatio': 20.35}
    inputs.update(overrides)

    compensation = AltitudeCompensation()
    compensation.setInputs(inputs)

    return compensation

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testUnknownContourIsRejected():

    with pytest.raises(ContourError, match = 'Unknown contour'):
        buildLosses(contour = 'trumpet')

def testAreaRatioAtTheThroatIsRejected():

    with pytest.raises(InvalidInputError, match = 'must exceed one'):
        buildLosses(areaRatio = 1.0)

def testAZeroAmbientPressureIsRejectedWithAUsefulReason():

    '''
    A separation criterion divides by ambient pressure and has no meaning in vacuum. The message
    points at the class that does handle vacuum rather than merely refusing.
    '''

    with pytest.raises(InvalidInputError, match = 'no meaning in vacuum'):
        buildLosses(ambientPressure = 0.0)

def testAnExitAngleOutsideTheQuadrantIsRejected():

    with pytest.raises(ContourError, match = r'\[0, 90\)'):
        divergenceEfficiency(95.0)

def testAnEmptyAscentProfileIsRejected():

    with pytest.raises(ContourError, match = 'at least one altitude'):
        buildCompensation(altitudes = [])

def testNegativeAltitudesAreRejected():

    with pytest.raises(InvalidInputError, match = 'cannot be negative'):
        buildCompensation(altitudes = [0.0, -100.0])

def testTheSpecificErrorsSubclassTheDomainBase():

    '''
    The scaffold aliases NozzleError to the shared EngineeringError, so a caller can catch the
    whole family with one except clause. The specific errors have to subclass it or that breaks.
    '''

    assert issubclass(ContourError, NozzleError)
    assert issubclass(SeparationError, NozzleError)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testDivergenceEfficiencyMatchesItsDefinition():

    for angle in (0.0, 5.0, 8.0, 15.0, 25.0):
        assert divergenceEfficiency(angle) == pytest.approx(
            (1.0 + np.cos(np.radians(angle))) / 2.0)

def testAnAxialExitHasNoDivergenceLoss():

    assert divergenceEfficiency(0.0) == pytest.approx(1.0)

def testTheFifteenDegreeConeLosesTheClassicalOnePointSevenPerCent():

    assert divergenceEfficiency(15.0) == pytest.approx(0.9830, abs = 1.0e-4)

def testSchmuckerMatchesItsCorrelation():

    chamber, ambient = 10.0e6, 101325.0

    expected = (SCHMUCKER_COEFFICIENT * (chamber / ambient) ** SCHMUCKER_EXPONENT) * ambient

    assert schmuckerSeparationPressure(chamber, ambient) == pytest.approx(expected)

def testTheLossDecompositionIsTheProductItClaimsToBe():

    result = buildLosses().decomposeEfficiency()

    assert result['overall'] == pytest.approx(
        result['divergence'] * result['boundaryLayer'] * result['kinetic'])

def testTheIdealCompensatingAreaRatioExpandsToAmbient():

    '''
    At the matched condition the exit pressure equals ambient, which is the definition of the
    ideal compensating expansion.
    '''

    from nozzleUtils import pressureRatioFromAreaRatio

    gamma, chamber, ambient = 1.24, 10.0e6, 26436.0

    areaRatio = idealCompensatingAreaRatio(gamma, chamber, ambient)

    exit_ = pressureRatioFromAreaRatio(gamma, areaRatio) * chamber

    assert exit_ == pytest.approx(ambient, rel = 1.0e-6)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDecompositionReproducesTheHubsSingleEfficiency():

    '''
    The propulsion hub carries a thrust coefficient efficiency of 0.98. Three unrelated mechanisms
    multiplying to that number is the point of this class, and if they stopped doing so one of the
    two would need revisiting.
    '''

    overall = buildLosses(contour = 'bell 80 per cent').decomposeEfficiency()['overall']

    assert overall == pytest.approx(0.98, abs = 0.01)

def testTheLargestLossIsNotAlwaysDivergence():

    '''
    The useful finding. On a well shaped bell the contour is not where the loss is, which is worth
    knowing before spending a programme on contour shape.
    '''

    result = buildLosses(contour = 'bell 80 per cent').decomposeEfficiency()

    assert result['largestLoss'] != 'divergence'

def testAConeLosesMostlyToDivergenceAndABellDoesNot():

    cone = buildLosses(contour = 'conical 15 degree').decomposeEfficiency()
    bell = buildLosses(contour = 'bell 80 per cent').decomposeEfficiency()

    assert cone['largestLoss'] == 'divergence'
    assert cone['losses']['divergence'] > 3.0 * bell['losses']['divergence']

def testAShorterBellTradesDivergenceAgainstBoundaryLayer():

    '''
    The two move in opposite directions, which is what gives the sum a broad minimum rather than a
    sharp optimum.
    '''

    short = buildLosses(contour = 'bell 60 per cent').decomposeEfficiency()
    long_ = buildLosses(contour = 'bell 100 per cent').decomposeEfficiency()

    assert short['losses']['divergence']     > long_['losses']['divergence']
    assert short['losses']['boundary layer'] < long_['losses']['boundary layer']

def testTheContourSpreadIsSmall():

    '''
    Every contour in the set lands within about one and a half points of every other. That is
    smaller than the difference between a good and a poor injector, and it is the honest scale of
    what contour shaping is worth.
    '''

    comparison = buildLosses().compareContours()

    assert comparison['spread'] < 0.03

def testSchmuckerPermitsALargerAreaRatioThanSummerfield():

    '''
    At launch vehicle pressure ratios Schmucker is the less conservative of the two, and the
    difference is large enough to change a design rather than to refine one.
    '''

    separation = buildLosses().checkSeparation()

    assert separation['schmuckerLimit'] > separation['summerfieldLimit']
    assert separation['schmuckerLimit'] / separation['summerfieldLimit'] > 1.2

def testTheTwoSeparationCriteriaCanDisagreeAboutTheSameNozzle():

    '''
    And when they do, the design rests on which correlation is believed. Both are curve fits and
    neither is a physical limit, which is why the class reports both rather than picking one.
    '''

    disagreeing = buildLosses(areaRatio = 25.0).checkSeparation()

    assert disagreeing['separatedBySummerfield'] is True
    assert disagreeing['separatedBySchmucker'] is False
    assert disagreeing['criteriaAgree'] is False

def testTheCompensationPrizeIsSeveralPerCent():

    '''
    Large enough to be worth chasing and small enough that every scheme for capturing it has so far
    lost more than it gained. That is the whole subject in one number.
    '''

    bound = buildCompensation().calculateIdealBenefit()

    assert 0.02 < bound['benefitFraction'] < 0.08

def testMostOfThePrizeIsAtAltitudeNotAtSeaLevel():

    '''
    The result worth carrying away, and it is the opposite of the intuition. A fixed nozzle's
    visible problem at sea level is over-expansion, which is what causes separation. Its
    performance loss is dominated by under-expansion high up, where the gap is six times larger.
    '''

    bound = buildCompensation().calculateIdealBenefit()

    gaps = [ideal - fixed for ideal, fixed
            in zip(bound['idealProfile'], bound['fixedProfile'])]

    assert gaps[-1] > 4.0 * gaps[0], (
        f'sea level gap {gaps[0]:.1f} s, top of ascent gap {gaps[-1]:.1f} s')

def testTheFixedBellRecoversNothingByDefinition():

    arrangements = buildCompensation().compareArrangements()['arrangements']

    assert arrangements['fixed bell']['impulseGain'] == 0.0
    assert arrangements['fixed bell']['massPenalty'] == 0.0

def testNoArrangementRecoversTheWholePrize():

    '''
    The bound is a bound. An arrangement claiming to reach it would be claiming perfect
    compensation with no base flow loss and no truncation, which no real device does.
    '''

    for name, recovery in RECOVERY_FRACTION.items():
        assert recovery < 1.0, name

def testTheBestPerformingArrangementIsNotOneThatHasFlown():

    '''
    The honest shape of the subject. The aerospike recovers most of the prize and has never flown
    operationally, and the reason is cooling and mass rather than aerodynamics.
    '''

    comparison = buildCompensation().compareArrangements()

    assert comparison['best'] not in comparison['flown']
    assert ALTITUDE_COMPENSATION[comparison['best']]['flownOperationally'] is False

def testTheFlownCompensatingArrangementIsTheExtendibleOne():

    comparison = buildCompensation().compareArrangements()

    compensating = [name for name in comparison['flown']
                    if ALTITUDE_COMPENSATION[name]['compensating']]

    assert compensating == ['extendible']

def testTheAerospikeCostsTheMostMass():

    assert MASS_PENALTY['aerospike'] == max(MASS_PENALTY.values())

def testBooleanFlagsAreRealPythonBooleans():

    flags = [
        buildLosses().checkSeparation()['separatedBySummerfield'],
        buildLosses().checkSeparation()['criteriaAgree'],
    ]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testReportsRunForBothClasses():

    assert 'NOZZLE LOSSES'         in buildLosses().generateReport()
    assert 'ALTITUDE COMPENSATION' in buildCompensation().generateReport()
