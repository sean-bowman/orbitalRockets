# -- Tests for the rangeSafetyAndFTS library -- #

'''

Three tiers. Tier one is inputs and refusals, tier two is the orbital mechanics and the binomial
arithmetic, and tier three is 14 CFR Part 450, read from the regulation.

The regulation is reproduced rather than adjusted. Its criteria are limits rather than targets, and
every one of them is asserted against the register as well as against the library.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'rangeSafetyLibrary'))
sys.path.insert(0, ROOT)

from rangeSafetyUtils import (LAUNCH_SAFETY_CRITERIA, CASUALTY_AREA, POPULATION_DENSITY,
                              FLIGHT_SAFETY_RELIABILITY, FLIGHT_SAFETY_CONFIDENCE,
                              EARTH_RADIUS, EARTH_MU, EARTH_ROTATION_RATE,
                              freeFlightRangeAngle, zeroFailureTestCount,
                              SEA_LEVEL_DENSITY, ATMOSPHERIC_SCALE_HEIGHT, GRAVITY,
                              DEBRIS_CATALOGUE, ballisticCoefficient, terminalVelocity,
                              InvalidInputError, ImpactPointError, RiskError, TerminationError)

from validation.referenceCases import RANGE_SAFETY_CRITERIA, UNVALIDATED

from ImpactPoint import ImpactPoint
from PublicRisk import PublicRisk
from TerminationReliability import TerminationReliability
from DebrisDispersion import DebrisDispersion
import DebrisDispersion as DebrisDispersion_module

# ------------------------------------------------------------------------------------------------ #
# -- Fixtures -- #
# ------------------------------------------------------------------------------------------------ #

@pytest.fixture
def states():

    return [{'time': 20.0,  'altitude': 3000.0,   'speed': 200.0,  'flightPathAngle': 80.0},
            {'time': 60.0,  'altitude': 28000.0,  'speed': 1000.0, 'flightPathAngle': 45.0},
            {'time': 110.0, 'altitude': 78000.0,  'speed': 2600.0, 'flightPathAngle': 22.0},
            {'time': 200.0, 'altitude': 135000.0, 'speed': 5000.0, 'flightPathAngle': 7.0},
            {'time': 290.0, 'altitude': 175000.0, 'speed': 7300.0, 'flightPathAngle': 1.0},
            {'time': 320.0, 'altitude': 185000.0, 'speed': 7800.0, 'flightPathAngle': 0.3}]

@pytest.fixture
def impact(states):

    point = ImpactPoint()
    point.setInputs({'altitude': 78000.0, 'speed': 2600.0, 'flightPathAngle': 22.0,
                     'states': states, 'destructRange': 900000.0, 'reactionTime': 4.0})

    return point

@pytest.fixture
def risk():

    component = PublicRisk()
    component.setInputs({'failureProbability': 0.02,
                         'fragments': {'small': 180, 'medium': 60, 'large': 12, 'intact': 1},
                         'nearestPersonProbability': 3.0e-7,
                         'regions': [{'name': 'launch area', 'landUse': 'remoteLand',
                                      'impactProbability': 0.15},
                                     {'name': 'coastal town', 'landUse': 'suburban',
                                      'impactProbability': 0.0008},
                                     {'name': 'downrange ocean', 'landUse': 'shippingLane',
                                      'impactProbability': 0.82}]})

    return component

@pytest.fixture
def termination():

    component = TerminationReliability()
    component.setInputs({'elementReliability': 0.995,
                         'configuration':      'dualParallel',
                         'seriesElements':     {'command receiver': 0.9995,
                                                'FTS battery':      0.9998,
                                                'safe and arm':     0.9999},
                         'testsAvailable':     30})

    return component

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: inputs and refusals -- #
# ------------------------------------------------------------------------------------------------ #

def testAnOrbitalStateHasNoImpactPoint():

    '''
    The domain's most physically meaningful refusal. At insertion the free-flight perigee rises
    above the surface, the trajectory no longer intersects the Earth, and there is no impact point.
    That is the moment the flight termination system stops having a job.
    '''

    with pytest.raises(ImpactPointError):
        freeFlightRangeAngle(EARTH_RADIUS + 200000.0, 7800.0, 0.0)

def testACircularOrbitIsRefused():

    speed = np.sqrt(EARTH_MU / (EARTH_RADIUS + 400000.0))

    with pytest.raises(ImpactPointError):
        freeFlightRangeAngle(EARTH_RADIUS + 400000.0, speed, 0.0)

def testAVerticalFlightPathAngleIsRefused():

    point = ImpactPoint()

    with pytest.raises(InvalidInputError):
        point.setInputs({'altitude': 1000.0, 'speed': 100.0, 'flightPathAngle': 90.0})

def testATraceWithoutStatesIsRefused():

    point = ImpactPoint()
    point.setInputs({'altitude': 1000.0, 'speed': 100.0})

    with pytest.raises(ImpactPointError):
        point.traceAscent()

def testCollectiveRiskAboveTheLimitIsRefused(risk):

    '''
    14 CFR 450.101 is a limit rather than a target. Reporting a percentage over it invites somebody
    to accept the percentage, so the class raises.
    '''

    risk.failureProbability = 0.5

    with pytest.raises(RiskError):
        risk.calculateCollective()

def testIndividualRiskAboveTheLimitIsRefused(risk):

    risk.nearestPersonProbability = 5.0e-6

    with pytest.raises(RiskError):
        risk.calculateIndividual()

def testIndividualRiskWithoutAProbabilityIsRefused(risk):

    risk.nearestPersonProbability = np.nan

    with pytest.raises(RiskError):
        risk.calculateIndividual()

def testAnUnknownLandUseClassIsRefused():

    component = PublicRisk()

    with pytest.raises(InvalidInputError):
        component.setInputs({'failureProbability': 0.01,
                             'regions': [{'name': 'a', 'landUse': 'tundra',
                                          'impactProbability': 0.1}]})

def testAnUnknownFragmentClassIsRefused():

    component = PublicRisk()

    with pytest.raises(InvalidInputError):
        component.setInputs({'failureProbability': 0.01,
                             'regions': [{'name': 'a', 'landUse': 'ruralLand',
                                          'impactProbability': 0.1}],
                             'fragments': {'enormous': 1}})

def testAnElementReliabilityOfOneIsRefused():

    '''
    A reliability of exactly one is a claim rather than a number, and the arithmetic downstream of
    it stops meaning anything.
    '''

    component = TerminationReliability()

    with pytest.raises(InvalidInputError):
        component.setInputs({'elementReliability': 1.0})

def testASystemBelowTheRegulatoryReliabilityIsRefused(termination):

    termination.seriesElements = {'command receiver': 0.99}

    with pytest.raises(TerminationError):
        termination.checkRequirement()

def testAnUnknownConfigurationIsRefused():

    component = TerminationReliability()

    with pytest.raises(InvalidInputError):
        component.setInputs({'elementReliability': 0.99, 'configuration': 'quadRedundant'})

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: the orbital mechanics and the arithmetic -- #
# ------------------------------------------------------------------------------------------------ #

def testTheFreeFlightSolutionConservesEnergyAndMomentum():

    radius = EARTH_RADIUS + 100000.0
    speed = 4000.0
    angle = 20.0

    solution = freeFlightRangeAngle(radius, speed, angle)

    momentum = radius * speed * np.cos(np.radians(angle))
    energy = 0.5 * speed ** 2 - EARTH_MU / radius

    assert solution['parameter'] == pytest.approx(momentum ** 2 / EARTH_MU)
    assert -EARTH_MU / (2.0 * solution['semiMajorAxis']) == pytest.approx(energy)

def testDownrangeGrowsWithSpeed():

    downranges = [freeFlightRangeAngle(EARTH_RADIUS + 80000.0, speed, 20.0)['rangeAngle']
                  for speed in (1500.0, 2500.0, 3500.0, 4500.0)]

    assert all(downranges[index] < downranges[index + 1]
               for index in range(len(downranges) - 1))

def testDownrangeGrowsFasterThanLinearlyWithSpeed():

    '''
    The reason the impact point accelerates. At a fixed flight path angle the downrange distance
    grows faster than the speed does, so the drift rate grows through the ascent.
    '''

    slow = freeFlightRangeAngle(EARTH_RADIUS + 80000.0, 2000.0, 20.0)['rangeAngle']
    fast = freeFlightRangeAngle(EARTH_RADIUS + 80000.0, 4000.0, 20.0)['rangeAngle']

    assert fast / slow > 2.0

def testTheImpactPointAcceleratesThroughAnAscent(impact):

    trace = impact.traceAscent()

    assert trace['driftAcceleration'] > 10.0
    assert trace['lastDriftRate'] > trace['firstDriftRate']

def testTheImpactPointCeasesToExistAtInsertion(impact):

    trace = impact.traceAscent()

    assert trace['insertionTime'] is not None
    assert trace['trace'][-1]['hasImpactPoint'] is False
    assert trace['trace'][0]['hasImpactPoint'] is True

def testTheEarthRotationOffsetGrowsWithFlightTime(impact):

    near = impact.calculateImpactPoint(30000.0, 1000.0, 30.0)
    far = impact.calculateImpactPoint(120000.0, 5000.0, 10.0)

    assert far['timeOfFlight'] > near['timeOfFlight']
    assert far['rotationOffset'] > near['rotationOffset']

def testTheRotationOffsetMatchesItsDefinition(impact):

    point = impact.calculateImpactPoint(80000.0, 3000.0, 20.0)

    assert point['rotationOffset'] == pytest.approx(
        EARTH_ROTATION_RATE * point['timeOfFlight'] * EARTH_RADIUS)

def testCasualtyAreaSharesSumToOne(risk):

    area = risk.casualtyArea()

    assert sum(entry['share'] for entry in area['fragments']) == pytest.approx(1.0)

def testRiskFollowsPopulationRatherThanImpactProbability(risk):

    '''
    The domain's headline result. The ocean takes most of the debris and contributes almost none of
    the risk; one town takes almost none of the debris and contributes most of the risk.
    '''

    collective = risk.calculateCollective()

    byName = {entry['region']: entry for entry in collective['regions']}

    ocean = byName['downrange ocean']
    town = byName['coastal town']

    assert ocean['impactProbability'] > 100.0 * town['impactProbability']
    assert town['share'] > 10.0 * ocean['share']

def testCollectiveRiskIsLinearInFailureProbability(risk):

    sweep = risk.failureSensitivity([0.01, 0.02, 0.04])['results']

    assert sweep[1]['expectedCasualties'] == pytest.approx(2.0 * sweep[0]['expectedCasualties'])
    assert sweep[2]['expectedCasualties'] == pytest.approx(4.0 * sweep[0]['expectedCasualties'])

def testTheRiskSweepRestoresTheOriginalFailureProbability(risk):

    original = risk.failureProbability
    risk.failureSensitivity()

    assert risk.failureProbability == original

def testLandUseSpansOrdersOfMagnitude(risk):

    comparison = risk.compareLandUse()

    assert comparison['spread'] > 1.0e4
    assert 'openOcean' in comparison['clearing']
    assert 'denseUrban' not in comparison['clearing']

def testTheZeroFailureCountMatchesItsClosedForm():

    assert zeroFailureTestCount(0.999, 0.95) == pytest.approx(np.log(0.05) / np.log(0.999))
    assert zeroFailureTestCount(0.5, 0.5) == pytest.approx(1.0)

def testEachAdditionalNineCostsTenTimesTheTests():

    '''
    Because the count is ln(1-C)/ln(R) and ln(R) is nearly -(1-R) for R near one, the count scales
    inversely with the failure probability, which falls by ten with each nine.
    '''

    three = zeroFailureTestCount(0.999, 0.95)
    four = zeroFailureTestCount(0.9999, 0.95)

    assert four / three == pytest.approx(10.0, rel = 1.0e-2)

def testAShortTestProgrammeDemonstratesFarLess(termination):

    demonstration = termination.demonstrationSize()

    assert demonstration['demonstrable'] is False
    assert demonstration['demonstratedReliability'] < 0.95
    assert demonstration['testsRequired'] > 50.0 * demonstration['testsAvailable']

def testTwoOfTwoIsWorseThanASinglePath(termination):

    '''
    The wiring mistake the word redundant hides. An initiator pair that must both fire has doubled
    the number of things that can stop it.
    '''

    comparison = termination.compareConfigurations()

    byName = {entry['configuration']: entry for entry in comparison['results']}

    assert byName['dualSeries']['pathReliability'] < termination.elementReliability
    assert 'dualSeries' in comparison['worseThanSingle']
    assert byName['dualParallel']['pathReliability'] > termination.elementReliability

def testSeriesElementsMultiplyTheAnswerDown(termination):

    withSeries = termination.configurationReliability()['systemReliability']

    termination.seriesElements = {}
    withoutSeries = termination.configurationReliability()['systemReliability']

    assert withSeries < withoutSeries

def testASingleSeriesElementDominatesARedundantTrain(termination):

    '''
    A redundant ordnance train behind one command receiver is a single string system, and its
    reliability is the receiver's.
    '''

    termination.seriesElements = {'command receiver': 0.99}
    configuration = termination.configurationReliability()

    assert configuration['systemReliability'] == pytest.approx(
        0.99 * configuration['pathReliability'])
    assert configuration['systemReliability'] < 0.995

def testTheDualParallelPathBeatsItsElement(termination):

    configuration = termination.configurationReliability('dualParallel')

    assert configuration['redundancyGain'] > 1.0
    assert configuration['pathReliability'] == pytest.approx(
        1.0 - (1.0 - termination.elementReliability) ** 2)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: against the regulation -- #
# ------------------------------------------------------------------------------------------------ #

def testTheCriteriaTableCoversEveryLaunchCriterion():

    """
    Five criteria in 450.101 and all five carried, so a table edited later cannot silently drop
    one and leave a launch checked against four.
    """

    assert set(LAUNCH_SAFETY_CRITERIA) == {'publicCollective', 'neighbouringCollective',
                                           'publicIndividual', 'neighbouringIndividual',
                                           'aircraft'}

def testTheLaunchSafetyCriteriaMatchTheRegulation():

    '''
    14 CFR 450.101, read from the regulation. Collective risk to the public at 1e-4 expected
    casualties, neighbouring operations personnel at 2e-4; individual probability of casualty at
    1e-6 and 1e-5; aircraft at 1e-6 probability of impact.
    '''

    assert LAUNCH_SAFETY_CRITERIA['publicCollective']['limit'] == 1.0e-4
    assert LAUNCH_SAFETY_CRITERIA['neighbouringCollective']['limit'] == 2.0e-4
    assert LAUNCH_SAFETY_CRITERIA['publicIndividual']['limit'] == 1.0e-6
    assert LAUNCH_SAFETY_CRITERIA['neighbouringIndividual']['limit'] == 1.0e-5
    assert LAUNCH_SAFETY_CRITERIA['aircraft']['limit'] == 1.0e-6

def testTheNeighbouringCriteriaAreLooserThanThePublicOnes():

    '''
    Both by exactly a factor of two on the collective side and ten on the individual side, which is
    the regulation distinguishing people who chose to be there from people who did not.
    '''

    assert (LAUNCH_SAFETY_CRITERIA['neighbouringCollective']['limit']
            == 2.0 * LAUNCH_SAFETY_CRITERIA['publicCollective']['limit'])
    assert (LAUNCH_SAFETY_CRITERIA['neighbouringIndividual']['limit']
            == pytest.approx(10.0 * LAUNCH_SAFETY_CRITERIA['publicIndividual']['limit']))

def testTheFlightSafetyReliabilityMatchesTheRegulation():

    '''
    14 CFR 450.145: a design reliability of 0.999 at 95 per cent confidence, for the onboard and
    the off-vehicle portions both.
    '''

    assert FLIGHT_SAFETY_RELIABILITY == 0.999
    assert FLIGHT_SAFETY_CONFIDENCE == 0.95

def testTheLibraryCriteriaMatchTheValidationRegister():

    reference = RANGE_SAFETY_CRITERIA['14-CFR-450']

    for name, entry in reference['launchCriteria'].items():
        assert LAUNCH_SAFETY_CRITERIA[name]['limit'] == entry['limit']

    assert FLIGHT_SAFETY_RELIABILITY == reference['flightSafetyReliability']
    assert FLIGHT_SAFETY_CONFIDENCE == reference['flightSafetyConfidence']

def testTheRegisterRecordsTheDemonstrationArithmetic():

    reference = RANGE_SAFETY_CRITERIA['14-CFR-450']

    assert reference['zeroFailureTests'] == pytest.approx(
        zeroFailureTestCount(FLIGHT_SAFETY_RELIABILITY, FLIGHT_SAFETY_CONFIDENCE), rel = 1.0e-3)

    note = reference['demonstrationNote']

    assert 'argued' in note
    assert 'demonstrated' in note

def testTheDomainRegistersWhatItCannotValidate():

    registered = {name for name, entry in UNVALIDATED.items()
                  if entry['domain'] == 'rangeSafetyAndFTS'}

    assert registered == {'casualtyAreas', 'impactProbabilities'}

    for name in registered:
        entry = UNVALIDATED[name]
        assert entry['reason'] and entry['consequence'] and entry['nextStep']


# ------------------------------------------------------------------------------------------------ #
# -- Debris dispersion -- #
# ------------------------------------------------------------------------------------------------ #

@pytest.fixture(scope = 'module')
def dispersion():

    component = DebrisDispersion()
    component.setInputs({'breakupAltitude':        28000.0,
                         'breakupSpeed':           1000.0,
                         'breakupFlightPathAngle': 45.0,
                         'breakupDownrange':       30000.0,
                         'windSpeed':              15.0})
    return component

def testTerminalVelocityIsTheClosedForm():

    '''
    `v = sqrt( 2 g beta / rho )` from drag equal to weight. Exact, and the check that the whole
    propagation has not gone wrong: a fragment released high enough arrives at this speed and no
    other.
    '''

    for ballistic in (1.0, 10.0, 100.0, 1000.0):
        assert terminalVelocity(ballistic, SEA_LEVEL_DENSITY) == pytest.approx(
            np.sqrt(2.0 * GRAVITY * ballistic / SEA_LEVEL_DENSITY), rel = 1.0e-12)

def testAFragmentDroppedFromRestArrivesAtTerminalVelocity():

    '''
    The end to end check on the integration. Dropped from high enough with no initial velocity, a
    fragment has to arrive at the terminal velocity for the density it arrives in, and nothing
    about the integrator is asserted anywhere else.
    '''

    component = DebrisDispersion()
    component.setInputs({'breakupAltitude':        30000.0,
                         'breakupSpeed':           0.0,
                         'breakupFlightPathAngle': -90.0,
                         'catalogue': {'panel': {'count': 1, 'mass': 6.0, 'dragArea': 0.55,
                                                 'casualtyClass': 'medium'}}})

    fragment = component.propagate()['fragments'][0]

    assert fragment['impactSpeed'] == pytest.approx(fragment['terminal'], rel = 0.01), \
        f'{fragment["impactSpeed"]:.2f} m/s against a terminal velocity of ' \
        f'{fragment["terminal"]:.2f} m/s'

def testTheStepSizeHasConverged():

    '''
    An adaptive step is a claim about accuracy, so it gets checked. Halving both step criteria has
    to move the impacts by far less than anything the model is used for.
    '''

    def impacts(velocityFraction, heightFraction):

        original = (DebrisDispersion_module.STEP_VELOCITY_FRACTION,
                    DebrisDispersion_module.STEP_SCALE_HEIGHT_FRACTION)

        DebrisDispersion_module.STEP_VELOCITY_FRACTION = velocityFraction
        DebrisDispersion_module.STEP_SCALE_HEIGHT_FRACTION = heightFraction

        try:
            component = DebrisDispersion()
            component.setInputs({'breakupAltitude':        28000.0,
                                 'breakupSpeed':           1000.0,
                                 'breakupFlightPathAngle': 45.0,
                                 'windSpeed':              15.0})
            return {item['class']: item['impactRange']
                    for item in component.propagate()['fragments']}
        finally:
            (DebrisDispersion_module.STEP_VELOCITY_FRACTION,
             DebrisDispersion_module.STEP_SCALE_HEIGHT_FRACTION) = original

    coarse = impacts(0.01, 0.01)
    fine   = impacts(0.005, 0.005)

    for name in coarse:
        assert abs(coarse[name] - fine[name]) < 100.0, \
            f'{name} moves {abs(coarse[name] - fine[name]):.0f} m when the step is halved'

def testTheHeaviestFragmentLandsFurthestInStillAir():

    '''
    With no wind nothing but the fragment decides where it lands, so the impacts have to fall in
    ballistic coefficient order. A dense fragment keeps its downrange velocity and a light one
    loses it in the first few kilometres of fall.
    '''

    component = DebrisDispersion()
    component.setInputs({'breakupAltitude':        28000.0,
                         'breakupSpeed':           1000.0,
                         'breakupFlightPathAngle': 45.0,
                         'windSpeed':              0.0})

    propagation = component.propagate()

    assert propagation['orderingHolds']

    ranges = [item['impactRange'] for item in propagation['fragments']]

    assert ranges == sorted(ranges), 'fragments are returned in ballistic coefficient order'

def testWindBreaksTheBallisticOrdering(dispersion):

    '''
    The result worth having, and it is not obvious. In still air the lightest fragment lands
    nearest. With a wind on it, the lightest fragment falls slowly enough to be carried past a
    heavier one, so **the order of the pieces on the ground changes with the weather** and a
    footprint is not a property of the vehicle alone.
    '''

    propagation = dispersion.propagate()

    assert not propagation['orderingHolds']

    byClass = {item['class']: item for item in propagation['fragments']}

    assert byClass['insulation']['ballistic'] < byClass['skin']['ballistic']
    assert byClass['insulation']['impactRange'] > byClass['skin']['impactRange']

def testWindDriftFallsWithBallisticCoefficient(dispersion):

    '''
    Drift is the wind speed times the fall time, and the fall time falls as the fragment gets
    denser. The ordering is structural and holds for any wind.
    '''

    fragments = dispersion.propagate()['fragments']

    drifts = [abs(item['windDrift']) for item in fragments]

    assert drifts == sorted(drifts, reverse = True), \
        'drift has to fall monotonically as ballistic coefficient rises'

    assert max(drifts) / max(min(drifts), 1.0) > 10.0, \
        'the two ends of the catalogue should differ by an order of magnitude in drift'

def testTheScatterCauseFlipsAcrossTheCatalogue(dispersion):

    '''
    Two independent causes of scatter, dominant at opposite ends. A fragment that falls slowly
    loses the destruct throw in seconds and then spends the descent in a wind nobody measured; a
    fragment that falls fast keeps its throw and outruns the wind.

    Neither could be found from an average fragment, which is the argument for a catalogue.
    '''

    fragments = dispersion.propagate()['fragments']

    causes = {item['class']: item['spreadCause'] for item in fragments}

    assert causes['insulation'] == 'wind'
    assert causes['machinery'] == 'destruct'

    lightest = min(fragments, key = lambda item: item['ballistic'])
    heaviest = max(fragments, key = lambda item: item['ballistic'])

    assert lightest['throwSpread'] < heaviest['throwSpread'], \
        'a light fragment cannot hold on to a throw'

def testTheImpartedVelocityWidensTheFootprintThroughTheHeavyEnd(dispersion):

    '''
    The intuitive expectation is that a destruct charge scatters the light debris furthest. It does
    the opposite: the fragments a charge can throw hardest are exactly the ones that decelerate
    fastest, so the width of the footprint belongs to the dense fragments.
    '''

    fragments = dispersion.propagate()['fragments']

    crossRanges = [item['crossRange'] for item in fragments]

    assert crossRanges == sorted(crossRanges), \
        'cross-range displacement has to rise with ballistic coefficient'

def testTheFootprintIsLongAndNarrow(dispersion):

    '''
    A debris footprint is an ellipse tens of kilometres long and a few wide, and the aspect ratio
    is the result rather than the dimensions: the length comes from the ballistic coefficient
    spread and the width from a destruct charge, which are different in size by an order of
    magnitude.
    '''

    extent = dispersion.footprint()

    assert extent['length'] > 10.0 * extent['width']
    assert extent['aspectRatio'] > 10.0

def testImpactProbabilitiesSumToOne(dispersion):

    '''
    Every fragment lands somewhere. A set of bands covering the footprint has to account for the
    whole catalogue, and the dispersion tails are what stop it being exact.
    '''

    regions = [{'name': 'near',   'start': 0.0,       'end': 40000.0},
               {'name': 'middle', 'start': 40000.0,   'end': 50000.0},
               {'name': 'far',    'start': 50000.0,   'end': 400000.0}]

    result = dispersion.impactProbabilities(regions)

    total = sum(entry['impactProbability'] for entry in result['regions'])

    assert total == pytest.approx(1.0, abs = 0.002)

def testRegionsThatMissTheFootprintAreRefused(dispersion):

    '''
    The categorical refusal. A risk analysis that does not cover where the debris lands is
    incomplete rather than conservative, and returning a probability total of 0.3 would let the
    shortfall pass as rounding in a calculation everything else is multiplied into.
    '''

    with pytest.raises(RiskError):
        dispersion.impactProbabilities([{'name': 'launch area',
                                         'start': 0.0, 'end': 20000.0}])

def testAnEmptyRegionListIsRefused(dispersion):

    with pytest.raises(RiskError):
        dispersion.impactProbabilities([])

def testAReversedRegionIsRefused(dispersion):

    with pytest.raises(InvalidInputError):
        dispersion.impactProbabilities([{'name': 'backwards',
                                         'start': 50000.0, 'end': 10000.0}])

def testACatalogueEntryWithoutAMassIsRefused():

    '''
    The ballistic coefficient is the whole model, so an entry that cannot produce one is not a
    catalogue entry.
    '''

    component = DebrisDispersion()

    with pytest.raises(InvalidInputError):
        component.setInputs({'breakupAltitude':        28000.0,
                             'breakupSpeed':           1000.0,
                             'breakupFlightPathAngle': 45.0,
                             'catalogue': {'mystery': {'count': 10, 'dragArea': 0.5}}})

def testABreakupOnTheGroundIsRefused():

    component = DebrisDispersion()

    with pytest.raises(InvalidInputError):
        component.setInputs({'breakupAltitude':        0.0,
                             'breakupSpeed':           1000.0,
                             'breakupFlightPathAngle': 45.0})

def testWindMovesTheNearEndAndLeavesTheFarEnd(dispersion):

    '''
    A wind limit on launch day is usually justified by loads on the vehicle. This says what it does
    to the debris footprint, which is a separate effect and acts almost entirely on one end.
    '''

    sweep = dispersion.windSensitivity([0.0, 10.0, 20.0, 30.0])

    nearMoved = (max(entry['nearestRange'] for entry in sweep['results'])
                 - min(entry['nearestRange'] for entry in sweep['results']))

    farMoved = (max(entry['furthestRange'] for entry in sweep['results'])
                - min(entry['furthestRange'] for entry in sweep['results']))

    assert nearMoved > 5.0 * farMoved, \
        f'the near end moved {nearMoved / 1000.0:.1f} km and the far end ' \
        f'{farMoved / 1000.0:.1f} km'

def testTheDispersionAtmosphereMatchesTheRecoveryDomain():

    '''
    Two domains falling bodies through two different atmospheres is a drift waiting to happen.
    recoveryAndReusability propagates an entry through an exponential atmosphere and this domain
    propagates debris through one, so they are asserted equal rather than assumed.
    '''

    sys.path.insert(0, os.path.join(ROOT, 'recoveryAndReusability',
                                    'recoveryAndReusabilityLibrary'))

    from recoveryUtils import (SEA_LEVEL_DENSITY as recoveryDensity,
                               ATMOSPHERIC_SCALE_HEIGHT as recoveryScaleHeight)

    assert SEA_LEVEL_DENSITY == recoveryDensity
    assert ATMOSPHERIC_SCALE_HEIGHT == recoveryScaleHeight

def testTheDebrisCatalogueSpansThreeOrdersOfMagnitude(dispersion):

    '''
    The span is what makes a footprint rather than a point, so it is a property of the catalogue
    worth asserting. A catalogue that collapsed to one ballistic coefficient would put every
    fragment in one place and produce a risk analysis that is wrong in an obvious way.
    '''

    coefficients = dispersion.ballisticCoefficients()

    assert coefficients['ballisticSpan'] > 100.0
    assert coefficients['lightest'] == 'insulation'
    assert coefficients['heaviest'] == 'machinery'
