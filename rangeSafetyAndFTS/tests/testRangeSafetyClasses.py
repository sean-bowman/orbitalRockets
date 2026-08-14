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
                              InvalidInputError, ImpactPointError, RiskError, TerminationError)

from validation.referenceCases import RANGE_SAFETY_CRITERIA, UNVALIDATED

from ImpactPoint import ImpactPoint
from PublicRisk import PublicRisk
from TerminationReliability import TerminationReliability

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
