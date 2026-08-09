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

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'nozzlesLibrary'))
sys.path.insert(0, ROOT)

from nozzleUtils import (NOZZLE_CONTOURS, ALTITUDE_COMPENSATION, SUMMERFIELD_SEPARATION_RATIO,
                         SCHMUCKER_COEFFICIENT, SCHMUCKER_EXPONENT,
                         TYPICAL_BOUNDARY_LAYER_LOSS, TYPICAL_KINETIC_LOSS,
                         divergenceEfficiency, schmuckerSeparationPressure,
                         idealCompensatingAreaRatio, convertAltitudeToPressure,
                         InvalidInputError, ContourError, SeparationError, NozzleError)
from NozzleLosses import NozzleLosses
from NozzleContour import NozzleContour
from AltitudeCompensation import AltitudeCompensation, RECOVERY_FRACTION, MASS_PENALTY

from validation.referenceCases import CORRELATION_ACCURACY, UNVALIDATED

# The integrated to frustum wetted area ratio on the reference booster, restated here so the
# registry entry and the class cannot drift apart silently.
UNVALIDATED_FRUSTUM_RATIO = 1.097

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

def buildContour(**overrides) -> NozzleContour:

    inputs = {'throatRadius': 0.0453, 'areaRatio': 20.35, 'lengthFraction': 0.80}
    inputs.update(overrides)

    contour = NozzleContour()
    contour.setInputs(inputs)

    return contour

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

def testDivergenceIsTheLargestLossUntilTheBellIsVeryLong():

    '''
    Regression guard on a finding this sub-domain published and then had to withdraw.

    The first version carried tabulated exit angles, with an 80 per cent bell fixed at 8 degrees
    regardless of area ratio, and concluded that the largest loss was the boundary layer rather
    than divergence. Rao's approximation gives 11.5 degrees at an area ratio of 20, which doubles
    the divergence loss and inverts the conclusion.

    Divergence is the largest loss on every contour here except the hundred per cent bell, where
    the wall has finally been turned far enough back that friction takes over.
    '''

    for contour in ('conical 15 degree', 'bell 60 per cent', 'bell 80 per cent'):
        assert buildLosses(contour = contour).decomposeEfficiency()['largestLoss'] == 'divergence'

    assert buildLosses(contour = 'bell 100 per cent'
                       ).decomposeEfficiency()['largestLoss'] == 'boundary layer'

def testAVeryShortBellIsBarelyBetterThanACone():

    '''
    The result the computed exit angle exposed and the lookup table hid.

    A 60 per cent bell has to turn the flow hard at the throat and cannot turn it back far by the
    exit, so it leaves at 15.4 degrees, which is STEEPER than the 15 degree cone it is competing
    with. Its divergence loss is therefore worse than the cone's, and the only reason it wins
    overall is its shorter wall and lower friction.

    A short bell is not a cheap way to buy divergence recovery. It is a way to buy wall area back.
    '''

    cone  = buildLosses(contour = 'conical 15 degree').decomposeEfficiency()
    short = buildLosses(contour = 'bell 60 per cent').decomposeEfficiency()

    assert short['exitAngle'] > cone['exitAngle']
    assert short['losses']['divergence'] > cone['losses']['divergence']

    assert short['losses']['boundary layer'] < cone['losses']['boundary layer']
    assert short['overall'] > cone['overall'], 'and it still wins, but only just'

    assert (short['overall'] - cone['overall']) < 0.005

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

def testReportsRunForEveryClass():

    assert 'NOZZLE LOSSES'         in buildLosses().generateReport()
    assert 'ALTITUDE COMPENSATION' in buildCompensation().generateReport()
    assert 'NOZZLE CONTOUR'        in buildContour().generateReport()

# ------------------------------------------------------------------------------------------------ #
# -- NozzleContour: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testAZeroThroatRadiusIsRejected():

    with pytest.raises(InvalidInputError, match = 'must be positive'):
        buildContour(throatRadius = 0.0)

def testAContourAreaRatioAtTheThroatIsRejected():

    with pytest.raises(InvalidInputError, match = 'must exceed one'):
        buildContour(areaRatio = 1.0)

def testALengthFractionFarOutsideTheFitIsRejected():

    '''
    Rao's fit covers roughly 0.6 to 1.0. A twenty per cent bell is not a short bell, it is an
    extrapolation that produces wall angles which are not physical, and the class says so rather
    than returning them.
    '''

    with pytest.raises(ContourError, match = 'between 0.3 and 1.2'):
        buildContour(lengthFraction = 0.2)

def testAnImpossiblyShortBellIsRejectedRatherThanApproximated():

    '''
    At an area ratio barely above one, the throat arc alone is longer than the whole bell. There is
    no parabola left to fit and the class refuses instead of producing one.
    '''

    with pytest.raises(ContourError, match = 'shorter than the throat arc'):
        buildContour(areaRatio = 1.05, lengthFraction = 0.3).coordinates()

# ------------------------------------------------------------------------------------------------ #
# -- NozzleContour: closed forms and the external reference -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExitRadiusFollowsFromTheAreaRatio():

    contour = buildContour(throatRadius = 0.05, areaRatio = 25.0)

    assert contour.exitRadius() == pytest.approx(0.05 * 5.0)

def testTheConicalLengthIsTheFifteenDegreeReference():

    contour = buildContour(throatRadius = 0.05, areaRatio = 25.0)

    assert contour.conicalLength() == pytest.approx(
        (0.25 - 0.05) / np.tan(np.radians(15.0)))

def testTheBellLengthIsTheQuotedFractionOfThatCone():

    contour = buildContour(lengthFraction = 0.60)

    assert contour.length() == pytest.approx(0.60 * contour.conicalLength())

def testTheWallAnglesMatchThePublishedRaoChart():

    '''
    The external check on this class. Rao's chart, reproduced as Huzel and Huang figure 4-16, gives
    an 80 per cent bell at an area ratio of 20 an initial wall angle of about 33 degrees and an exit
    angle of about 11.

    The registered band is a degree, which is what a fit to a chart is worth, and both angles land
    inside it. That band is not negligible: a degree of exit angle is worth about 0.1 per cent of
    divergence efficiency. It is a quarter of the error the lookup table this replaced was making.
    '''

    angles = buildContour(areaRatio = 20.0, lengthFraction = 0.80).wallAngles()

    band = CORRELATION_ACCURACY['raoWallAngles']['band']

    assert CORRELATION_ACCURACY['raoWallAngles']['bandUnit'] == 'degrees'

    assert angles['initialAngle'] == pytest.approx(33.0, abs = band)
    assert angles['exitAngle']    == pytest.approx(11.0, abs = band)

def testTheTwoAnglesMoveInOppositeDirectionsWithAreaRatio():

    '''
    The geometric heart of a bell. A larger expansion turns the flow harder at the throat and has
    further to turn it back by the exit, so the initial angle rises as the exit angle falls.

    A lookup table that gives one exit angle per contour family cannot represent this, which is why
    the table this class replaced was wrong.
    '''

    small = buildContour(areaRatio = 10.0).wallAngles()
    large = buildContour(areaRatio = 80.0).wallAngles()

    assert large['initialAngle'] > small['initialAngle']
    assert large['exitAngle']    < small['exitAngle']

def testAShorterBellLeavesAtASteeperAngle():

    '''
    The result that inverted a published finding. A 60 per cent bell has less length to turn the
    flow back, so it exits steeper, and at this area ratio it exits steeper than the 15 degree cone
    it competes with.
    '''

    short = buildContour(lengthFraction = 0.60).exitAngle()
    long_ = buildContour(lengthFraction = 1.00).exitAngle()

    assert short > long_
    assert short > 15.0, 'steeper than the cone, which is the whole point'

def testARunawayInitialWallAngleIsRefused():

    '''
    The length correction is multiplicative, so it cannot reverse the two angles and a guard on
    their ordering would never fire. The reachable failure is the initial angle running away: a very
    large area ratio at the shortest permitted length puts it past 90 degrees, which turns the wall
    past radial.

    The class raises there rather than returning a shape that is not a nozzle.
    '''

    with pytest.raises(ContourError, match = 'past radial'):
        buildContour(areaRatio = 400.0, lengthFraction = 0.3).wallAngles()

def testTheExitAngleIsAlwaysBelowTheInitialAngle():

    '''
    The invariant the removed guard was trying to protect, asserted where it belongs. A bell turns
    the flow away from the axis at the throat and back toward it at the exit, across the whole
    admissible range.
    '''

    for areaRatio in (2.0, 10.0, 20.35, 80.0, 200.0):
        for lengthFraction in (0.6, 0.8, 1.0):
            angles = buildContour(areaRatio = areaRatio,
                                  lengthFraction = lengthFraction).wallAngles()

            assert angles['exitAngle'] < angles['initialAngle'], (areaRatio, lengthFraction)
            assert angles['turning'] > 0.0

def testTheContourStartsAtTheThroatAndEndsAtTheExitRadius():

    contour = buildContour(throatRadius = 0.05, areaRatio = 25.0)

    coordinates = contour.coordinates()

    assert coordinates['radial'][0]  == pytest.approx(0.05)
    assert coordinates['radial'][-1] == pytest.approx(0.25)
    assert coordinates['axial'][-1]  == pytest.approx(contour.length())

def testTheContourExpandsMonotonically():

    coordinates = buildContour().coordinates()

    assert np.all(np.diff(coordinates['radial']) > 0.0)
    assert np.all(np.diff(coordinates['axial'])  > 0.0)

# ------------------------------------------------------------------------------------------------ #
# -- NozzleContour: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testTheIntegratedAreaExceedsTheFrustumApproximation():

    '''
    The finding that reaches another sub-domain. A bell bulges outward from the straight line
    between throat and exit, so it carries about a tenth more wetted area than the cone frustum
    that combustionDevices sizes its cooling circuit against.

    Registered as a limitation rather than propagated, because that circuit already fails to close
    and the correction makes it fail by more.
    '''

    area = buildContour(throatRadius = 0.0453, areaRatio = 20.35).surfaceArea()

    assert area['ratio'] > 1.0
    assert area['ratio'] == pytest.approx(UNVALIDATED_FRUSTUM_RATIO, abs = 0.01)

def testTheFrustumUnderstatementIsRegisteredAsALimitation():

    '''
    The registry is the point of the validation framework. A number a downstream sub-domain is
    getting wrong has to be findable by someone who wants to know whether to trust it.
    '''

    entry = UNVALIDATED['bellWettedArea']

    assert 'combustionDevices' in entry['domain']
    assert '1.097' in entry['consequence']

def testALongerBellHasMoreWettedAreaThanAShortOne():

    short = buildContour(lengthFraction = 0.60).surfaceArea()['area']
    long_ = buildContour(lengthFraction = 1.00).surfaceArea()['area']

    assert long_ > short

def testTheContourAgreesWithTheAngleTheLossesAreComputedFrom():

    '''
    The two classes have to be looking at the same nozzle. NozzleLosses builds a contour internally
    to get its exit angle, and if that ever stopped matching a directly built one the loss budget
    would be describing a different geometry from the report.
    '''

    fromLosses = buildLosses(contour = 'bell 80 per cent').decomposeEfficiency()['exitAngle']

    fromContour = buildContour(areaRatio = 20.35, lengthFraction = 0.80).exitAngle()

    assert fromLosses == pytest.approx(fromContour)

def testTheConeIsStillTakenFromTheTableRatherThanFromRao():

    '''
    A 15 degree cone has a 15 degree exit angle by definition and Rao has nothing to say about it.
    The table keeps the cone and computes the bells, which is the correct split rather than an
    inconsistency.
    '''

    assert NOZZLE_CONTOURS['conical 15 degree']['exitAngle'] == 15.0

    for name, entry in NOZZLE_CONTOURS.items():
        if name.startswith('bell'):
            assert entry['exitAngle'] is None, (
                f'{name} carries a tabulated exit angle again; that is the defect this '
                f'sub-domain published and withdrew')
