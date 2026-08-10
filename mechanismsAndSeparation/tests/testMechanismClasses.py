# -- Tests for the mechanismsAndSeparation classes -- #

'''

Tiered tests for the five mechanism classes.

Tier 1 covers the contract, and this domain refuses more than most: a separation that recontacts, a
clamp band that gaps, a firing circuit that will not fire, a circuit that could fire from stray
energy, a deployable that stalls, and a negative torque margin. Every one of them is a lost mission
rather than a degraded device, which is the whole argument for raising instead of reporting.

Tier 2 validates against NASA-STD-5017B, read directly rather than through a summary. That mattered:
a search summary of the same standard reported the required margin as 1.0 and the standard says
zero, because the reserve is inside the safety factors.

Tier 3 covers the results the domain produces, chiefly that preload relaxation compounds, that the
deterministic tipoff bound is flat in spring count while the statistical case falls as one over its
root, and that test evidence rather than design is what buys margin.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'mechanismsAndSeparationLibrary'))
sys.path.insert(0, ROOT)

from mechanismUtils import (TORQUE_MARGIN_FACTORS, REQUIRED_TORQUE_MARGIN,
                            BEARING_CONTACT_ALLOWABLE, INITIATOR_TYPES, PRELOAD_RELAXATION,
                            NO_FIRE_MARGIN, ALL_FIRE_MARGIN, TYPICAL_WEDGE_ANGLE,
                            springEnergy, separationVelocity, torqueMargin, clampBandPreload,
                            InvalidInputError, MechanismsAndSeparationError,
                            MarginError, SeparationError, InitiationError)
from SeparationSystem import SeparationSystem, CLEARANCE_FACTOR
from ClampBand import ClampBand, PRELOAD_MARGIN
from PyrotechnicInitiator import PyrotechnicInitiator
from MechanismActuator import MechanismActuator
from DeploymentKinematics import DeploymentKinematics

from validation.referenceCases import MECHANISM_STANDARDS, UNVALIDATED

def buildSeparation(**overrides) -> SeparationSystem:

    inputs = {'springCount': 4, 'springStiffness': 8000.0, 'springStroke': 0.10,
              'springRadius': 0.55, 'separatingMass': 1800.0, 'remainingMass': 6000.0,
              'inertia': 2653.0, 'clearanceLength': 0.30, 'radialGap': 0.020}
    inputs.update(overrides)

    system = SeparationSystem()
    system.setInputs(inputs)

    return system

def buildBand(**overrides) -> ClampBand:

    inputs = {'bandTension': 12000.0, 'interfaceRadius': 0.60, 'bandArea': 1.2e-4,
              'flightLoad': 95000.0, 'storageMonths': 9.0}
    inputs.update(overrides)

    band = ClampBand()
    band.setInputs(inputs)

    return band

def buildInitiator(**overrides) -> PyrotechnicInitiator:

    inputs = {'initiatorType': 'NSI', 'firingVoltage': 28.0, 'harnessResistance': 0.9,
              'parallelCount': 2, 'strayCurrent': 0.15}
    inputs.update(overrides)

    initiator = PyrotechnicInitiator()
    initiator.setInputs(inputs)

    return initiator

def buildActuator(**overrides) -> MechanismActuator:

    inputs = {'availableTorque': 4.5, 'fixedTorques': [0.80, 0.35],
              'variableTorques': [0.42, 0.25]}
    inputs.update(overrides)

    actuator = MechanismActuator()
    actuator.setInputs(inputs)

    return actuator

def buildDeployable(**overrides) -> DeploymentKinematics:

    inputs = {'springTorque': 4.0, 'springRate': 1.2, 'inertia': 2.5,
              'travel': np.radians(90.0), 'resistingTorque': 0.6}
    inputs.update(overrides)

    panel = DeploymentKinematics()
    panel.setInputs(inputs)

    return panel

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSpecificErrorsSubclassTheDomainBase():

    for error in (MarginError, SeparationError, InitiationError):
        assert issubclass(error, MechanismsAndSeparationError)

def testASingleSpringIsRefused():

    '''
    One spring is a moment about the centre of gravity rather than a separation system, and the
    tipoff calculation assumes a symmetric set.
    '''

    with pytest.raises(SeparationError, match = 'at least two springs'):
        buildSeparation(springCount = 1)

def testTheTransverseInertiaIsRequiredRatherThanGuessed():

    '''
    Regression guard on a defect that shipped. An earlier version defaulted the transverse inertia
    from the bolt circle radius, which is the wrong length entirely: a stage's transverse inertia
    is dominated by its length, and the estimate understated it by an order of magnitude and
    therefore overstated the tipoff rate by the same factor.
    '''

    system = SeparationSystem()

    with pytest.raises(Exception):
        system.setInputs({'springCount': 4, 'springStiffness': 8000.0, 'springStroke': 0.10,
                          'springRadius': 0.55, 'separatingMass': 1800.0,
                          'remainingMass': 6000.0})

def testARecontactingSeparationIsRefused():

    '''
    A separation that recontacts is a lost mission rather than a degraded separation, so it raises
    rather than reporting a negative clearance.
    '''

    with pytest.raises(SeparationError, match = 'recontacts'):
        buildSeparation(radialGap = 0.0005, springRadius = 1.2).checkRecontact()

def testRecontactNeedsGeometryToCheckAgainst():

    with pytest.raises(InvalidInputError, match = 'clearance length and a radial gap'):
        buildSeparation(clearanceLength = np.nan, radialGap = np.nan).checkRecontact()

def testAClampBandThatGapsInFlightIsRefused():

    with pytest.raises(MarginError, match = 'does not hold the joint'):
        buildBand(flightLoad = 200000.0).checkJoint()

def testAWedgeAngleOutsideTheQuadrantIsRejected():

    with pytest.raises(InvalidInputError, match = r'\(0, 90\)'):
        clampBandPreload(1000.0, 95.0)

def testAFiringCircuitThatCannotFireIsRefused():

    with pytest.raises(InitiationError, match = 'does not fire'):
        buildInitiator(harnessResistance = 40.0).checkAllFire()

def testAStrayCurrentAboveNoFireIsRefused():

    with pytest.raises(InitiationError, match = 'above the'):
        buildInitiator(strayCurrent = 0.8).checkNoFire()

def testANoFireCheckNeedsAStrayCurrent():

    '''
    Assuming zero stray current is the assumption that makes the check pointless, so it is required
    rather than defaulted.
    '''

    with pytest.raises(InvalidInputError, match = 'credible stray current'):
        buildInitiator(strayCurrent = np.nan).checkNoFire()

def testANegativeTorqueMarginIsRefused():

    with pytest.raises(MarginError, match = 'below the required'):
        buildActuator(availableTorque = 1.0).checkMargins()

def testAMechanismWithNoResistingTorquesIsRefused():

    '''
    A mechanism with no resistance has not been analysed rather than being infinitely good. The
    standard lists twenty conditions a margin calculation has to account for.
    '''

    with pytest.raises(InvalidInputError, match = 'has not been analysed'):
        buildActuator(fixedTorques = [], variableTorques = [])

def testAHelpingTorqueInTheResistingListIsRejected():

    '''
    A negative resisting torque silently gives the margin reserve it does not have.
    '''

    with pytest.raises(InvalidInputError, match = 'belongs in the available torque'):
        buildActuator(fixedTorques = [-0.5])

def testAStallingDeployableIsRefused():

    with pytest.raises(MechanismsAndSeparationError, match = 'stalls'):
        buildDeployable(springTorque = 2.0, springRate = 2.0, resistingTorque = 1.2).deploy()

def testTravelInDegreesIsCaught():

    '''
    Travel is expected in radians, and ninety passed as degrees is more than fourteen turns.
    '''

    with pytest.raises(InvalidInputError, match = 'looks like degrees'):
        buildDeployable(travel = 90.0)

def testHoldingMarginExcludesIncidentalFriction():

    '''
    The standard is explicit that incidental sources such as joint friction, harness bending and
    blanket rubbing are excluded from the holding torque because they are unreliable.
    '''

    with pytest.raises(InvalidInputError, match = 'does not count'):
        buildActuator().holdingMargin([0.2], holdingTorque = 0.0)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: NASA-STD-5017B and closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTorqueMarginEquationMatchesTheStandard():

    result = torqueMargin(10.0, [1.0], [1.0], [], source = 'theory or analysis')

    assert result['factoredResisting'] == pytest.approx(1.5 * 1.0 + 3.0 * 1.0)
    assert result['margin'] == pytest.approx(10.0 / 4.5 - 1.0)

def testTheSafetyFactorsAreTheStandardsOwn():

    reference = MECHANISM_STANDARDS['NASA-STD-5017B']

    assert reference['level'] == 'standard'

    for source, factors in reference['torqueMarginFactors'].items():
        assert TORQUE_MARGIN_FACTORS[source]['variable'] == factors['variable']
        assert TORQUE_MARGIN_FACTORS[source]['fixed'] == factors['fixed']
        assert TORQUE_MARGIN_FACTORS[source]['acceleration'] == factors['acceleration']

def testTheRequiredMarginIsZeroNotOne():

    '''
    The correction that reading the standard rather than a summary of it produced. A search summary
    of NASA-STD-5017B reported the threshold as 1.0; the standard says a margin greater than or
    equal to zero indicates the requirement is met, because the reserve is inside the factors.
    '''

    assert REQUIRED_TORQUE_MARGIN == 0.0

    reference = MECHANISM_STANDARDS['NASA-STD-5017B']

    assert reference['requiredMargin'] == 0.0
    assert 'summary' in reference['correctionNote']

def testTheOneSpringOutFactorsAreAllUnity():

    '''
    And they apply only to redundant springs in parallel with one failed, which the standard
    explicitly distinguishes from a single spring designed to tolerate partial failure.
    '''

    factors = TORQUE_MARGIN_FACTORS['one spring out']

    assert factors['variable'] == 1.0
    assert factors['fixed'] == 1.0
    assert factors['acceleration'] == 1.0

    assert 'ONLY' in factors['note']

def testTheFactorsTightenMonotonicallyWithEvidence():

    order = ['theory or analysis', 'development test', 'acceptance test, extremes']

    values = [TORQUE_MARGIN_FACTORS[name]['variable'] for name in order]

    assert values == sorted(values, reverse = True)

def testTheBearingAllowablesAreTheStandardsTableThree():

    reference = MECHANISM_STANDARDS['NASA-STD-5017B']['bearingContactAllowable']

    for material, values in reference.items():
        assert BEARING_CONTACT_ALLOWABLE[material]['quiet'] == values['quiet']
        assert BEARING_CONTACT_ALLOWABLE[material]['nonQuiet'] == values['nonQuiet']

def testSpringEnergyAndSeparationVelocityMatchTheirDefinitions():

    assert springEnergy(1000.0, 0.1) == pytest.approx(5.0)

    # equal masses share the energy equally, so the relative velocity is twice each body's
    assert separationVelocity(100.0, 10.0, 10.0) == pytest.approx(np.sqrt(2.0 * 100.0 * 0.2))

def testTheLighterBodyTakesMostOfTheVelocity():

    velocity = buildSeparation().calculateVelocity()

    assert velocity['separatingVelocity'] > velocity['remainingVelocity']

    assert (velocity['separatingVelocity'] / velocity['remainingVelocity']
            == pytest.approx(6000.0 / 1800.0))

def testMomentumIsConserved():

    velocity = buildSeparation().calculateVelocity()

    assert (1800.0 * velocity['separatingVelocity']
            == pytest.approx(6000.0 * velocity['remainingVelocity']))

def testTheWedgeAmplificationMatchesItsRelation():

    assert clampBandPreload(1000.0, 15.0) == pytest.approx(
        2.0 * np.pi * 1000.0 / np.tan(np.radians(15.0)))

    # a shallower wedge amplifies more
    assert clampBandPreload(1000.0, 10.0) > clampBandPreload(1000.0, 20.0)

def testTheInitiatorCircuitIsOhmsLaw():

    firing = buildInitiator(parallelCount = 1).calculateFiringCurrent()

    expected = 28.0 / (0.9 + 0.05 + INITIATOR_TYPES['NSI']['bridgewireResistance'])

    assert firing['busCurrent'] == pytest.approx(expected)
    assert firing['currentPerDevice'] == pytest.approx(expected)

def testTheDeploymentIntegrationAgreesWithTheUndampedClosedForm():

    result = buildDeployable(dampingCoefficient = 0.0).deploy()

    assert result['arrivalRate'] == pytest.approx(result['closedFormRate'], rel = 0.02)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testPreloadRelaxationCompoundsRatherThanAdding():

    relaxation = buildBand().calculateRelaxation()

    simpleSum = sum(relaxation['losses'].values())

    assert relaxation['totalLoss'] < simpleSum, 'compounding is less than adding'
    assert relaxation['totalLoss'] > 0.5 * simpleSum, 'and not much less'

def testStorageMakesTheJointWorseAndItIsNotVisible():

    fresh  = buildBand(storageMonths = 0.0).calculateRelaxation()
    stored = buildBand(storageMonths = 24.0).calculateRelaxation()

    assert stored['retainedPreload'] < fresh['retainedPreload']
    assert stored['totalLoss'] > fresh['totalLoss']

def testAJointCanPassFreshAndFailAfterStorage():

    '''
    The failure mode this domain's ethos names. The margin has to be carried against the relaxed
    preload, not the installed one.
    '''

    load = 120000.0

    fresh = buildBand(storageMonths = 0.0, flightLoad = load)

    assert fresh.checkJoint()['margin'] > 0.0

    # the same joint with a heavier flight load fails only because of relaxation
    marginal = buildBand(storageMonths = 0.0, flightLoad = 138000.0)

    assert marginal.checkJoint()['margin'] > 0.0

    with pytest.raises(MarginError):
        buildBand(storageMonths = 24.0, flightLoad = 138000.0).checkJoint()

def testTheDeterministicTipoffBoundIsFlatInSpringCount():

    '''
    The result this comparison was not written expecting, and the reason the narrative around it
    was corrected. Half the springs at the top of tolerance and half at the bottom produce the same
    net moment whether there are four of them or forty.
    '''

    comparison = buildSeparation().compareSpringCounts([2, 4, 6, 8, 12])

    assert comparison['worstCaseIsFlat'] is True

    rates = [entry['tipoff'] for entry in comparison['results'].values()]

    assert max(rates) == pytest.approx(min(rates))

def testTheStatisticalTipoffFallsAsOneOverRootCount():

    comparison = buildSeparation().compareSpringCounts([2, 4, 8, 16])

    results = comparison['results']

    # doubling the count should cut the statistical rate by root two
    for low, high in ((2, 4), (4, 8), (8, 16)):
        ratio = results[low]['statistical'] / results[high]['statistical']
        assert ratio == pytest.approx(np.sqrt(2.0), rel = 1.0e-6)

    assert comparison['lowestStatistical'] == 16

def testSpringCountDoesNotChangeTheSeparationVelocityAtFixedEnergy():

    comparison = buildSeparation().compareSpringCounts([2, 6, 12])

    velocities = [entry['velocity'] for entry in comparison['results'].values()]

    assert max(velocities) == pytest.approx(min(velocities))

def testAStrongerSpringBuysVelocityAndNoRecontactMargin():

    '''
    A claim this domain got wrong on the first pass and the tests caught.

    The original assertion was that a stronger spring leaves the tipoff rate unchanged. It does
    not: both the velocity and the tipoff rate scale with the square root of stiffness, because
    both come from the same impulse.

    What IS invariant is the rotation accumulated while clearing, because the extra rate is exactly
    cancelled by the shorter clearing time. **So a stronger spring buys separation velocity and no
    recontact margin at all**, which is a stronger and more useful statement than the one it
    replaced.
    '''

    base   = buildSeparation(springStiffness = 8000.0)
    strong = buildSeparation(springStiffness = 16000.0)

    ratio = np.sqrt(2.0)

    assert (strong.calculateVelocity()['relativeVelocity']
            == pytest.approx(ratio * base.calculateVelocity()['relativeVelocity'], rel = 1.0e-9))

    assert (strong.calculateTipoff()['rateDegrees']
            == pytest.approx(ratio * base.calculateTipoff()['rateDegrees'], rel = 1.0e-9))

    # and the thing that actually matters does not move
    assert (strong.checkRecontact()['rotationDegrees']
            == pytest.approx(base.checkRecontact()['rotationDegrees'], rel = 1.0e-6))

    assert (strong.checkRecontact()['clearanceFactor']
            == pytest.approx(base.checkRecontact()['clearanceFactor'], rel = 1.0e-6))

def testTighterSpringMatchingIsWhatAttacksTheBound():

    loose = buildSeparation(rateTolerance = 0.10).calculateTipoff()
    tight = buildSeparation(rateTolerance = 0.02).calculateTipoff()

    assert tight['rateDegrees'] < 0.3 * loose['rateDegrees']

def testTestEvidenceBuysMarginWithoutADesignChange():

    '''
    The result the domain is built around. The factors fall from 3.00 to 2.00 on variable torques
    as uncertainty is retired by measurement, and the same hardware gains margin.
    '''

    comparison = buildActuator().compareDataSources()

    analysis = comparison['results']['theory or analysis']['margin']
    tested   = comparison['results']['acceptance test, extremes']['margin']

    assert tested > analysis
    assert tested / analysis > 2.0

def testAMechanismCanFailOnAnalysisAndPassOnTest():

    marginal = buildActuator(availableTorque = 3.2)

    comparison = marginal.compareDataSources()

    assert comparison['results']['theory or analysis']['margin'] < REQUIRED_TORQUE_MARGIN
    assert comparison['results']['acceptance test, extremes']['margin'] > REQUIRED_TORQUE_MARGIN

    assert comparison['passesAtAnalysis'] is False

def testTheGearedOutputMarginIsCheckedSeparately():

    '''
    The standard requires margin at both the input and the output of a torque multiplier, because
    a gearbox is not a hundred per cent efficient.
    '''

    geared = buildActuator(gearRatio = 50.0, gearEfficiency = 0.80)

    result = geared.checkGearedMargins()

    assert result['outputIsWorse'] is True
    assert result['output']['margin'] < result['input']['margin']

def testLatchEnergyGoesAsTheSquareOfArrivalRate():

    slow = buildDeployable(springTorque = 2.0)
    fast = buildDeployable(springTorque = 8.0)

    slowImpact = slow.latchImpact()
    fastImpact = fast.latchImpact()

    rateRatio   = fastImpact['arrivalRate'] / slowImpact['arrivalRate']
    energyRatio = fastImpact['impactEnergy'] / slowImpact['impactEnergy']

    assert energyRatio == pytest.approx(rateRatio ** 2, rel = 1.0e-6)

def testADamperBuysLatchEnergyAndCostsTime():

    panel = buildDeployable()

    undamped = panel.latchImpact()

    sizing = panel.sizeDamper(energyLimit = 1.0)

    assert sizing['damperNeeded'] is True
    assert sizing['required'] > 0.0

    panel.dampingCoefficient = sizing['required']

    damped = panel.latchImpact()

    assert damped['impactEnergy'] < undamped['impactEnergy']
    assert damped['deploymentTime'] > undamped['deploymentTime']

def testADamperIsNotSizedWhenItIsNotNeeded():

    sizing = buildDeployable(springTorque = 2.0, springRate = 0.2,
                             resistingTorque = 0.3).sizeDamper(energyLimit = 100.0)

    assert sizing['damperNeeded'] is False
    assert sizing['required'] == 0.0

def testTheLowEnergyInitiatorTradesFiringEaseAgainstSafety():

    '''
    The initiator choice is an electromagnetic compatibility decision as much as an ordnance one.
    '''

    comparison = buildInitiator().compareInitiators()

    assert (comparison['results']['low energy']['noFireCurrent']
            < comparison['results']['NSI']['noFireCurrent'])

    assert INITIATOR_TYPES['low energy']['allFireCurrent'] < \
           INITIATOR_TYPES['NSI']['allFireCurrent']

def testParallelInitiatorsShareTheBus():

    '''
    A circuit sized for one device does not fire several, and this is the arithmetic that catches
    it before the pad does.
    '''

    single = buildInitiator(parallelCount = 1).calculateFiringCurrent()
    double = buildInitiator(parallelCount = 2).calculateFiringCurrent()

    assert double['busCurrent'] > single['busCurrent']
    assert double['currentPerDevice'] < single['currentPerDevice']

def testTheNoFireCurrentAndPowerRatingsAreIndependentLimits():

    '''
    A detail the tests surfaced. The NSI convention is stated as one amp AND one watt, and those
    are two separate limits rather than one derived from the other: at the nominal 1.05 ohm
    bridgewire, one amp dissipates 1.05 W, so the current limit is very slightly the binding one.

    The power margin therefore tracks the square of the current margin without equalling it, and a
    check written assuming they are the same relation fails by five per cent. Both have to be
    checked because a fault that delivers a fixed voltage and one that delivers a fixed current
    land on different limits.
    '''

    result = buildInitiator(strayCurrent = 0.1).checkNoFire()

    device = INITIATOR_TYPES['NSI']

    powerFactor = device['noFirePower'] / result['strayPower']

    # the square relation holds to the ratio between the two independently stated ratings
    ratingRatio = device['noFirePower'] / (device['noFireCurrent'] ** 2
                                           * device['bridgewireResistance'])

    assert powerFactor == pytest.approx(ratingRatio * result['currentFactor'] ** 2, rel = 1.0e-6)

    assert ratingRatio < 1.0, 'the current rating is the binding one at nominal bridgewire'

def testBooleanFlagsAreRealPythonBooleans():

    flags = [buildSeparation().checkRecontact()['meetsConvention'],
             buildBand().checkJoint()['holds'],
             buildInitiator().checkAllFire()['fires'],
             buildInitiator().checkNoFire()['safe'],
             buildActuator().checkMargins()['passes'],
             buildDeployable().deploy()['stalled']]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testTheUnvalidatedRegisterNamesWhatThisDomainCannotCheck():

    for key in ('pyroshockMagnitude', 'preloadRelaxation', 'springRateTolerance'):

        entry = UNVALIDATED[key]

        assert 'mechanismsAndSeparation' in entry['domain']
        assert entry['consequence']
        assert entry['nextStep']

def testReportsRunForEveryClass():

    assert 'SEPARATION SYSTEM'     in buildSeparation().generateReport()
    assert 'CLAMP BAND'            in buildBand().generateReport()
    assert 'PYROTECHNIC INITIATOR' in buildInitiator().generateReport()
    assert 'MECHANISM ACTUATOR'    in buildActuator().generateReport()
    assert 'DEPLOYMENT'            in buildDeployable().generateReport()
