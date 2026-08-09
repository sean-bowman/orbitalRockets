# -- Tests for the propulsionTesting classes -- #

'''

Tiered tests for the two test-engineering classes.

Tier 1 covers the contract, including the one refusal this sub-domain makes: a test whose
acceptance band is inside its measurement uncertainty. Running such a test produces a verdict
decided by noise and signed by a person, which is worse than not running it.

Tier 2 validates against closed forms, and one of them is unusually strong for this repository:
the cancellation of chamber pressure and throat area in the c* times Cf product is an identity, so
it is asserted exactly rather than to a tolerance.

Tier 3 covers the results the sub-domain exists to produce, chiefly that combining c* and Cf
uncertainties as independent inflates the specific impulse uncertainty, that a one per cent effect
is unresolvable on this engine while a four per cent one is marginal, and that improving one
dominant channel of two buys almost nothing.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'propulsionTestingLibrary'))
sys.path.insert(0, ROOT)

from propulsionTestUtils import (INSTRUMENT_UNCERTAINTY, INSTABILITY_FLUX_MULTIPLIER,
                                 STABILITY_PULSE_FRACTION_MINIMUM, PULSE_GUN_DIAMETER_LIMIT,
                                 NYQUIST_FACTOR, RESOLUTION_FACTOR,
                                 rootSumSquare, characteristicVelocity, thrustCoefficient,
                                 firstTangentialFrequency,
                                 InvalidInputError, PropulsionTestingError,
                                 ReductionError, TestDesignError)
from PerformanceReduction import PerformanceReduction, STANDARD_GRAVITY
from HotFireTest import (HotFireTest, DISCRIMINATION_RATIO_FLOOR, DISCRIMINATION_RATIO_REFUSED,
                         CHAMBER_SETTLING_RESIDENCE_TIMES, WALL_SETTLING_TIME)

from validation.referenceCases import STABILITY_RATING, UNVALIDATED

# The reference booster, from the propulsion hub by way of combustionDevices.
THROAT_AREA  = np.pi / 4.0 * 0.0906 ** 2
BOOSTER_FLOW = 26.47 + 10.34

def buildReduction(**overrides) -> PerformanceReduction:

    inputs = {'chamberPressure': 10.0e6,
              'throatArea':      THROAT_AREA,
              'massFlow':        BOOSTER_FLOW,
              'thrust':          100.0e3}
    inputs.update(overrides)

    reduction = PerformanceReduction()
    reduction.setInputs(inputs)

    return reduction

def buildTest(**overrides) -> HotFireTest:

    inputs = {'objective':       'Establish c* efficiency at the design point',
              'chamberPressure': 10.0e6,
              'chamberDiameter': 0.1433,
              'residenceTime':   0.00147,
              'duration':        10.0,
              'sampleRate':      5000.0}
    inputs.update(overrides)

    test = HotFireTest()
    test.setInputs(inputs)

    return test

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSpecificErrorsSubclassTheDomainBase():

    assert issubclass(ReductionError, PropulsionTestingError)
    assert issubclass(TestDesignError, PropulsionTestingError)

def testAChannelThatReadZeroIsRejected():

    '''
    A reduction from a channel that read zero or negative is a data problem, not a performance
    result, and returning a number for it would launder the first into the second.
    '''

    with pytest.raises(InvalidInputError, match = 'must be positive'):
        buildReduction(chamberPressure = 0.0)

    with pytest.raises(InvalidInputError, match = 'must be positive'):
        buildReduction(massFlow = -1.0)

def testAZeroUncertaintyIsRejected():

    '''
    Zero claims a perfect instrument and one claims a measurement carrying no information. Both are
    statements nobody means to make.
    '''

    with pytest.raises(ReductionError, match = r'\(0, 1\)'):
        buildReduction(uncertainties = {'thrust': 0.0})

    with pytest.raises(ReductionError, match = r'\(0, 1\)'):
        buildReduction(uncertainties = {'thrust': 1.5})

def testAnIdealValueOfZeroIsRejectedWithTheReasonThatMatters():

    with pytest.raises(ReductionError, match = 'same chamber pressure and mixture ratio'):
        buildReduction().compareEfficiency(0.0, 1.5836)

def testATestWithoutAnObjectiveIsRefused():

    '''
    A test without a stated question is the failure this class exists to catch, and it is the one
    thing here that cannot be checked automatically, so it is required as an input instead.
    '''

    with pytest.raises(TestDesignError, match = 'stated objective'):
        buildTest(objective = '   ')

def testAnAcceptanceBandInsideTheMeasurementIsRefused():

    '''
    The refusal this sub-domain makes. A test that cannot distinguish a pass from a fail and is run
    anyway produces a verdict decided by noise and signed by a person.
    '''

    with pytest.raises(TestDesignError, match = 'cannot distinguish a pass from a fail'):
        buildTest().checkDiscrimination(0.004, channel = 'chamberPressure')

def testANonPositiveAcceptanceBandIsRejected():

    with pytest.raises(InvalidInputError, match = 'must be positive'):
        buildTest().checkDiscrimination(0.0)

def testAnUnknownChannelHasNoDefaultUncertainty():

    with pytest.raises(InvalidInputError, match = 'No default uncertainty'):
        buildTest().checkDiscrimination(0.05, channel = 'chamberColour')

def testANonPositivePulseIsRejected():

    with pytest.raises(InvalidInputError, match = 'must be positive'):
        buildTest().checkStabilityRating(0.0)

def testHelperGuardsFire():

    with pytest.raises(InvalidInputError):
        characteristicVelocity(1.0e6, 1.0e-3, 0.0)

    with pytest.raises(InvalidInputError):
        thrustCoefficient(1.0e3, 0.0, 1.0e-3)

    with pytest.raises(InvalidInputError):
        firstTangentialFrequency(1000.0, 0.0)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testTheReductionMatchesItsDefinitions():

    reduction = buildReduction()
    result    = reduction.reduce()

    assert result['characteristicVelocity'] == pytest.approx(
        10.0e6 * THROAT_AREA / BOOSTER_FLOW)

    assert result['thrustCoefficient'] == pytest.approx(
        100.0e3 / (10.0e6 * THROAT_AREA))

    assert result['specificImpulse'] == pytest.approx(
        100.0e3 / (BOOSTER_FLOW * STANDARD_GRAVITY))

def testTheProductIsAnIdentityAndIsAssertedExactly():

    '''
    c* times Cf is F over mdot, identically. Not to a tolerance: the chamber pressure and the
    throat area cancel algebraically, and this is the strongest single result in the sub-domain
    precisely because it needs no reference and no instrument figures.
    '''

    result = buildReduction().reduce()

    assert result['productCheck'] == pytest.approx(result['specificImpulse'], rel = 1.0e-12)

def testTheProductIdentityHoldsForAnyThroatAreaAndPressure():

    '''
    The identity is not a coincidence of the reference case. Change the two channels that are meant
    to cancel and the specific impulse must not move at all.
    '''

    base = buildReduction().reduce()

    for pressure, area in ((5.0e6, 2.0 * THROAT_AREA), (20.0e6, 0.5 * THROAT_AREA)):

        moved = buildReduction(chamberPressure = pressure, throatArea = area).reduce()

        assert moved['specificImpulse'] == pytest.approx(base['specificImpulse'])
        assert moved['productCheck']    == pytest.approx(base['productCheck'])

def testTheUncertaintiesMatchTheirPropagationRule():

    uncertainty = buildReduction().calculateUncertainty()

    pressure = INSTRUMENT_UNCERTAINTY['chamberPressure']['relative']
    area     = INSTRUMENT_UNCERTAINTY['throatArea']['relative']
    flow     = INSTRUMENT_UNCERTAINTY['massFlow']['relative']
    force    = INSTRUMENT_UNCERTAINTY['thrust']['relative']

    assert uncertainty['characteristicVelocity'] == pytest.approx(
        rootSumSquare(pressure, area, flow))

    assert uncertainty['thrustCoefficient'] == pytest.approx(
        rootSumSquare(force, pressure, area))

    assert uncertainty['specificImpulse'] == pytest.approx(rootSumSquare(force, flow))

def testTheSpecificImpulseUncertaintyIgnoresPressureAndArea():

    '''
    The consequence of the identity, asserted directly. Make the chamber pressure and throat area
    measurements ten times worse and the specific impulse uncertainty must not move.
    '''

    base  = buildReduction().calculateUncertainty()
    worse = buildReduction(uncertainties = {'chamberPressure': 0.05,
                                            'throatArea': 0.10}).calculateUncertainty()

    assert worse['specificImpulse'] == pytest.approx(base['specificImpulse'])

    assert worse['characteristicVelocity'] > base['characteristicVelocity']

def testTheDiscriminationRatioIsTheBandOverTheUncertainty():

    check = buildTest().checkDiscrimination(0.05, uncertainty = 0.01)

    assert check['ratio'] == pytest.approx(5.0)

def testTheSampleRateThresholdsAreTheStatedMultiples():

    sampling = buildTest().checkSampleRate()

    assert sampling['nyquistRate']    == pytest.approx(NYQUIST_FACTOR * sampling['frequency'])
    assert sampling['resolutionRate'] == pytest.approx(RESOLUTION_FACTOR * sampling['frequency'])

def testTheFirstTangentialFrequencyMatchesTheAcousticForm():

    assert firstTangentialFrequency(1000.0, 0.1433) == pytest.approx(
        1.8412 * 1000.0 / (np.pi * 0.1433))

def testTheStabilityFloorMatchesTheRegisteredReference():

    reference = STABILITY_RATING['MSFC pulse gun development']

    assert reference['level'] == 'hardware'

    assert STABILITY_PULSE_FRACTION_MINIMUM == reference['overpressureLower']
    assert PULSE_GUN_DIAMETER_LIMIT == reference['pulseGunDiameterLimit']

    assert INSTABILITY_FLUX_MULTIPLIER['injector face'] == (
        reference['instabilityFluxMultiplierInjector'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testCombiningTheTwoParametersInflatesTheImpulseUncertainty():

    '''
    The result this sub-domain exists to produce. The default thing to do when a reduction gives
    c* and Cf and somebody wants an Isp is wrong, and it is wrong by a large factor.
    '''

    uncertainty = buildReduction().calculateUncertainty()

    assert uncertainty['naiveSpecificImpulse'] > uncertainty['specificImpulse']
    assert uncertainty['inflationFactor'] > 1.5

def testTheInflationSurvivesAnyPlausibleInstrumentFigures():

    '''
    The claim that no instrument figures change the conclusion, only its size. Asserted across a
    wide sweep rather than argued for in a document.
    '''

    for pressure in (0.001, 0.005, 0.02):
        for area in (0.002, 0.01, 0.03):

            uncertainty = buildReduction(
                uncertainties = {'chamberPressure': pressure,
                                 'throatArea': area}).calculateUncertainty()

            assert uncertainty['inflationFactor'] > 1.0, (pressure, area)

def testTheReductionReproducesTheHubsDesignPoint():

    '''
    Cross-domain consistency, and it is circular by construction: the reduction is handed the hub's
    own design channels. It is asserted so that a change in either would surface, and it proves
    nothing about the outside world.
    '''

    result = buildReduction().reduce()

    assert result['specificImpulse'] == pytest.approx(277.0, abs = 0.1)

def testTheMeasuredEfficiencyReproducesTheHubsAssumedOne():

    comparison = buildReduction().compareEfficiency(1823.0, 1.5836)

    assert comparison['cstarEfficiency'] == pytest.approx(0.96, abs = 0.005)
    assert comparison['thrustCoefficientEfficiency'] == pytest.approx(0.98, abs = 0.005)

def testAFourPerCentEffectIsResolvableAndAOnePerCentEffectIsNot():

    '''
    The campaign result. The test can confirm that the injector performs roughly as designed and it
    cannot tell whether a modification took the efficiency from 0.96 to 0.97.
    '''

    test = buildTest()

    uncertainty = buildReduction().calculateUncertainty()['characteristicVelocity']

    validate = test.checkDiscrimination(0.04, uncertainty = uncertainty)

    assert validate['canDecide'] is True
    assert validate['comfortable'] is False, 'it decides, and only just'

    with pytest.raises(TestDesignError):
        test.checkDiscrimination(0.01, uncertainty = uncertainty)

def testImprovingOneOfTwoEqualChannelsBuysAlmostNothing():

    '''
    The budget result. The throat area and the mass flow carry equal weight, so improving either
    alone leaves the other in place and the combined figure barely moves.
    '''

    base = buildReduction().calculateUncertainty()['characteristicVelocity']

    one  = buildReduction(uncertainties = {'throatArea': 0.003}
                          ).calculateUncertainty()['characteristicVelocity']

    both = buildReduction(uncertainties = {'throatArea': 0.003, 'massFlow': 0.003}
                          ).calculateUncertainty()['characteristicVelocity']

    assert (base - one) < 0.5 * (base - both), 'one channel should buy less than half the gain'
    assert both < 0.5 * base

def testEvenBothChannelsImprovedCannotRankTwoInjectors():

    '''
    The conclusion that sends the campaign to a back to back comparison rather than to better
    instruments. If this ever stopped being true the recommendation would need revisiting.
    '''

    both = buildReduction(uncertainties = {'throatArea': 0.003, 'massFlow': 0.003}
                          ).calculateUncertainty()['characteristicVelocity']

    assert 0.01 / both < DISCRIMINATION_RATIO_FLOOR

def testAPerformanceSampleRateIsBelowNyquistForTheModeThatMatters():

    '''
    The instrumentation result, and it is worse than a missing measurement: below Nyquist the mode
    aliases into the performance band and appears as an oscillation that is not there.
    '''

    sampling = buildTest(sampleRate = 5000.0).checkSampleRate()

    assert sampling['detects'] is False
    assert sampling['resolves'] is False

def testResolvingTheModeTakesAnOrderOfMagnitudeMoreThanDetectingIt():

    sampling = buildTest().checkSampleRate()

    assert sampling['resolutionRate'] / sampling['nyquistRate'] == pytest.approx(5.0)

def testNoSampleRateAssertsNothingRatherThanAssumingOne():

    '''
    Returning None rather than a default. A data system that was not described has not been
    assessed, and saying so is better than guessing.
    '''

    sampling = buildTest(sampleRate = np.nan).checkSampleRate()

    assert sampling['detects'] is None
    assert sampling['resolves'] is None
    assert sampling['frequency'] > 0.0

def testTheTwoSettlingTimesDifferByOrdersOfMagnitude():

    '''
    The duration result. A short burn gives a valid performance number and an invalid wall
    temperature, and the wall temperature is usually what the short test was run to get.
    '''

    duration = buildTest().checkDuration()

    assert duration['wallSettling'] > 50.0 * duration['chamberSettling']

def testAShortBurnSettlesTheChamberAndNotTheWall():

    short = buildTest(duration = 1.0).checkDuration()

    assert short['settlesChamber'] is True
    assert short['settlesWall'] is False
    assert short['usableThermalWindow'] == 0.0

def testAnAdequatePulseIsAboveTheReferenceFloorAndATapIsNot():

    test = buildTest()

    assert test.checkStabilityRating(0.45 * 10.0e6)['adequate'] is True
    assert test.checkStabilityRating(0.10 * 10.0e6)['adequate'] is False

def testAPulseGunIsViableOnThisChamberAndNotOnALargeOne():

    assert buildTest().checkStabilityRating(4.5e6)['pulseGunViable'] is True

    large = buildTest(chamberDiameter = 0.5)

    assert large.checkStabilityRating(4.5e6)['pulseGunViable'] is False

def testTheInstabilityFluxMultiplierIsWhyTheTestExists():

    '''
    The cross-domain consequence, asserted so it does not get softened. combustionDevices computes
    a cooling circuit that does not close with comfortable margin at nominal flux. At five times
    nominal there is no circuit at all.
    '''

    lower, upper = INSTABILITY_FLUX_MULTIPLIER['injector face']

    assert lower >= 5.0
    assert upper >= lower

    reference = STABILITY_RATING['MSFC pulse gun development']

    assert 'no circuit at all' in reference['crossDomain']

def testTheDampCriterionIsRegisteredAsNotCarried():

    '''
    The gap this sub-domain refuses to fill from memory. checkStabilityRating deliberately returns
    no pass or fail, and the register says why.
    '''

    entry = UNVALIDATED['stabilityDampCriterion']

    assert 'has not been read' in entry['reason']

    result = buildTest().checkStabilityRating(4.5e6)

    assert 'passed' not in result
    assert 'stable' not in result

def testBooleanFlagsAreRealPythonBooleans():

    test = buildTest()

    flags = [test.checkDiscrimination(0.05)['comfortable'],
             test.checkStabilityRating(4.5e6)['adequate'],
             test.checkStabilityRating(4.5e6)['pulseGunViable'],
             test.checkDuration()['settlesWall'],
             buildReduction().compareEfficiency(1823.0, 1.5836)['cstarResolved']]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testTheUnvalidatedRegisterNamesWhatThisSubDomainCannotCheck():

    for key in ('instrumentUncertainty', 'stabilityDampCriterion', 'testSettlingTimes'):

        entry = UNVALIDATED[key]

        assert 'propulsionTesting' in entry['domain']
        assert entry['consequence']
        assert entry['nextStep']

def testReportsRunForBothClasses():

    assert 'PERFORMANCE REDUCTION' in buildReduction().generateReport()
    assert 'HOT FIRE TEST'         in buildTest().generateReport()
