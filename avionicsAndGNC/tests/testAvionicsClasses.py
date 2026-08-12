# -- Tests for the avionicsAndGNC classes -- #

'''

Tiered tests for the three avionics classes.

Tier 1 covers the contract, including a sign convention guard that catches the commonest error in
this domain: a positive static margin, which means a stable vehicle, which a launch vehicle is not.

Tier 2 validates against closed forms. Every error growth law here is an integration of a constant,
so the exponents are exact and asserted as such: t for attitude from gyro bias, t squared for
position from accelerometer bias, t cubed for position from gyro bias through tilt.

Tier 3 covers the results: the gyro term overtakes the accelerometer term early, the governing
disturbance changes through the flight, and a handful of high-rate channels dominate a telemetry
budget.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'avionicsLibrary'))
sys.path.insert(0, ROOT)

from avionicsUtils import (IMU_GRADES, AIDING_SOURCES, TVC_ARRANGEMENTS, MICRO_G,
                           STANDARD_GRAVITY, GAIN_MARGIN_REQUIREMENT, PHASE_MARGIN_REQUIREMENT,
                           attitudeErrorFromGyroBias, attitudeErrorFromRandomWalk,
                           positionErrorFromAccelBias, positionErrorFromTilt, nyquistRate,
                           InvalidInputError, AvionicsError,
                           NavigationError, ControlAuthorityError, TelemetryError)
from NavigationDrift import NavigationDrift
from ControlAuthority import ControlAuthority, TRIM_ALLOWANCE, THRUST_MISALIGNMENT
from TelemetryBudget import TelemetryBudget, FRAMING_OVERHEAD, LINK_MARGIN, RESOLUTION_FACTOR

from validation.referenceCases import UNVALIDATED

MEASUREMENTS = [
    {'name': 'accelerometers', 'count': 12, 'sampleRate': 2000.0, 'wordLength': 16,
     'signalFrequency': 150.0},
    {'name': 'pressures',      'count': 24, 'sampleRate': 200.0,  'wordLength': 14,
     'signalFrequency': 15.0},
    {'name': 'temperatures',   'count': 40, 'sampleRate': 5.0,    'wordLength': 12,
     'signalFrequency': 0.4}]

def buildNavigation(**overrides) -> NavigationDrift:

    inputs = {'grade': 'tactical', 'flightTime': 540.0, 'aiding': 'GPS',
              'positionRequirement': 500.0}
    inputs.update(overrides)

    navigation = NavigationDrift()
    navigation.setInputs(inputs)

    return navigation

def buildControl(**overrides) -> ControlAuthority:

    inputs = {'thrust': 100.0e3, 'gimbalArm': 6.0, 'arrangement': 'single gimballed engine',
              'dynamicPressure': 35000.0, 'referenceArea': 2.545, 'staticMargin': -0.06,
              'vehicleLength': 18.0, 'vehicleDiameter': 1.8, 'windAngleOfAttack': 4.0,
              'bendingFrequency': 6.0}
    inputs.update(overrides)

    control = ControlAuthority()
    control.setInputs(inputs)

    return control

def buildTelemetry(**overrides) -> TelemetryBudget:

    inputs = {'measurements': [dict(item) for item in MEASUREMENTS],
              'linkCapacity': 1.0e6, 'recorderCapacity': 4.0e9, 'flightTime': 540.0}
    inputs.update(overrides)

    telemetry = TelemetryBudget()
    telemetry.setInputs(inputs)

    return telemetry

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSpecificErrorsSubclassTheDomainBase():

    for error in (NavigationError, ControlAuthorityError, TelemetryError):
        assert issubclass(error, AvionicsError)

def testAnUnknownImuGradeIsRejected():

    with pytest.raises(InvalidInputError, match = 'Unknown IMU grade'):
        buildNavigation(grade = 'aspirational')

def testAnUnknownAidingSourceIsRejected():

    with pytest.raises(InvalidInputError, match = 'Unknown aiding source'):
        buildNavigation(aiding = 'dead reckoning')

def testANavigationSolutionThatMissesItsRequirementIsRefused():

    '''
    A vehicle that does not know where it is is not a vehicle with a small negative margin.
    '''

    with pytest.raises(NavigationError, match = 'does not know where it is'):
        buildNavigation(grade = 'industrial', aiding = 'none',
                        positionRequirement = 100.0).checkRequirement()

def testARequirementCheckNeedsARequirement():

    with pytest.raises(InvalidInputError, match = 'position requirement is needed'):
        buildNavigation(positionRequirement = np.nan).checkRequirement()

def testAPositiveStaticMarginIsRefusedAsASignConventionError():

    '''
    The commonest error in this domain. A launch vehicle is aerodynamically unstable, so a positive
    static margin is almost always a sign convention slip rather than a design.
    '''

    with pytest.raises(ControlAuthorityError, match = 'sign convention'):
        buildControl(staticMargin = 0.06)

def testAVehicleTrimmedNearItsStopIsRefused():

    '''
    A vehicle that needs its full gimbal range to hold steady disturbances cannot manoeuvre, so it
    is not marginal, it is uncontrolled.
    '''

    with pytest.raises(ControlAuthorityError, match = 'cannot manoeuvre'):
        buildControl(windAngleOfAttack = 8.0).checkAuthority()

def testAVehicleThatCannotBeControlledAtAllIsRefusedDifferently():

    with pytest.raises(ControlAuthorityError, match = 'cannot be controlled by thrust vectoring'):
        buildControl(thrust = 1.0e3, gimbalArm = 0.1,
                     windAngleOfAttack = 8.0).checkAuthority()

def testAnArrangementWithNoGimbalIsRefusedWithItsReason():

    with pytest.raises(ControlAuthorityError, match = 'reaction control'):
        buildControl(arrangement = 'fixed engine with RCS').checkAuthority()

def testATelemetryPlanThatExceedsItsLinkIsRefused():

    with pytest.raises(TelemetryError, match = 'does not\\s+degrade gracefully'):
        buildTelemetry(linkCapacity = 100.0e3).checkLink()

def testAnAliasingChannelIsRefused():

    '''
    A channel below Nyquist does not miss its signal, it aliases it into a frequency that is not
    there, and an investigation reading that data chases something that never happened.
    '''

    measurements = [dict(MEASUREMENTS[0], sampleRate = 100.0)]

    with pytest.raises(TelemetryError, match = 'aliases it'):
        buildTelemetry(measurements = measurements).checkSampleRates()

def testARecorderThatRunsOutBeforeTheEndIsRefused():

    with pytest.raises(TelemetryError, match = 'the end is the part'):
        buildTelemetry(recorderCapacity = 1.0e6).checkRecorder()

def testADuplicateMeasurementGroupIsRejected():

    with pytest.raises(InvalidInputError, match = 'Duplicate measurement group'):
        buildTelemetry(measurements = [dict(MEASUREMENTS[0]), dict(MEASUREMENTS[0])])

def testHelperGuardsFire():

    with pytest.raises(InvalidInputError):
        attitudeErrorFromGyroBias(1.0, -1.0)

    with pytest.raises(InvalidInputError):
        positionErrorFromAccelBias(1.0, -1.0)

    with pytest.raises(InvalidInputError):
        nyquistRate(0.0)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testAttitudeErrorFromBiasGrowsLinearly():

    one = attitudeErrorFromGyroBias(1.0, 100.0)
    two = attitudeErrorFromGyroBias(1.0, 200.0)

    assert two / one == pytest.approx(2.0)

    # one degree per hour for one hour is one degree
    assert attitudeErrorFromGyroBias(1.0, 3600.0) == pytest.approx(np.radians(1.0))

def testAttitudeErrorFromRandomWalkGrowsAsTheSquareRoot():

    one = attitudeErrorFromRandomWalk(1.0, 100.0)
    four = attitudeErrorFromRandomWalk(1.0, 400.0)

    assert four / one == pytest.approx(2.0)

def testPositionErrorFromAccelBiasGrowsAsTheSquare():

    one = positionErrorFromAccelBias(100.0, 100.0)
    two = positionErrorFromAccelBias(100.0, 200.0)

    assert two / one == pytest.approx(4.0)

    assert positionErrorFromAccelBias(1.0, 10.0) == pytest.approx(0.5 * MICRO_G * 100.0)

def testPositionErrorFromGyroBiasGrowsAsTheCube():

    '''
    The result the domain is built on. The attitude error grows linearly and the position error it
    causes integrates it twice, so the combined path is cubic.
    '''

    def combined(time):
        return positionErrorFromTilt(attitudeErrorFromGyroBias(1.0, time), time)

    assert combined(200.0) / combined(100.0) == pytest.approx(8.0)

def testTheTiltTermIsGravityTimesAttitude():

    assert positionErrorFromTilt(0.01, 10.0) == pytest.approx(
        0.5 * STANDARD_GRAVITY * 0.01 * 100.0)

def testTheControlMomentUsesTheFullSineNotASmallAngle():

    control = buildControl()

    angle = 8.0

    assert control.availableMoment(angle) == pytest.approx(
        100.0e3 * np.sin(np.radians(angle)) * 6.0)

    # and it differs measurably from the small angle form at the stop
    assert control.availableMoment(angle) < 100.0e3 * np.radians(angle) * 6.0

def testTheThrustMisalignmentTermMatchesItsDefinition():

    disturbances = buildControl().calculateDisturbances()

    assert disturbances['terms']['thrust misalignment'] == pytest.approx(
        100.0e3 * np.sin(np.radians(THRUST_MISALIGNMENT)) * 6.0)

def testTheAerodynamicTermScalesWithDynamicPressureAndAngle():

    low  = buildControl(dynamicPressure = 10000.0).calculateDisturbances()
    high = buildControl(dynamicPressure = 20000.0).calculateDisturbances()

    key = 'aerodynamic at angle of attack'

    assert high['terms'][key] / low['terms'][key] == pytest.approx(2.0)

    shallow = buildControl(windAngleOfAttack = 2.0).calculateDisturbances()
    steep   = buildControl(windAngleOfAttack = 4.0).calculateDisturbances()

    assert steep['terms'][key] / shallow['terms'][key] == pytest.approx(2.0)

def testTheBitRateIsChannelsTimesRateTimesWord():

    rate = buildTelemetry().calculateBitRate()

    expected = sum(entry['count'] * entry['sampleRate'] * entry['wordLength']
                   for entry in MEASUREMENTS)

    assert rate['payloadRate'] == pytest.approx(expected)
    assert rate['framedRate'] == pytest.approx(expected * (1.0 + FRAMING_OVERHEAD))

def testTheLinkRequirementIncludesFramingAndMargin():

    link = buildTelemetry().checkLink()

    assert link['requiredRate'] == pytest.approx(link['framedRate'] * (1.0 + LINK_MARGIN))

def testTheResolutionThresholdIsTenTimesTheSignal():

    rates = buildTelemetry().checkSampleRates()

    entry = rates['results']['accelerometers']

    assert entry['resolveRate'] == pytest.approx(RESOLUTION_FACTOR * entry['signalFrequency'])
    assert entry['detectRate'] == pytest.approx(2.0 * entry['signalFrequency'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testTheGyroTermDominatesOverAFlightDuration():

    '''
    The result this domain exists to produce. The accelerometer is what gets specified and the
    gyroscope is what decides.
    '''

    drift = buildNavigation().calculateDrift()

    assert drift['dominant'] == 'gyro bias through tilt'
    assert drift['dominantShare'] > 0.9

def testTheTermsCrossOverEarlyInTheFlight():

    crossover = buildNavigation().identifyCrossover()

    assert crossover['crossover'] is not None
    assert crossover['crossover'] < 120.0
    assert crossover['gyroDominatesAtFlightTime'] is True

def testTheAccelerometerDominatesOnAShortFlight():

    '''
    The other side of the crossover, and it is why a short-flight intuition transfers badly.
    '''

    drift = buildNavigation(flightTime = 30.0).calculateDrift()

    assert drift['dominant'] == 'accelerometer bias'

def testTheImuGradeSpreadIsOrdersOfMagnitude():

    comparison = buildNavigation().compareGrades()

    assert comparison['spread'] > 1000.0
    assert comparison['best'] == 'navigation'

    positions = [comparison['results'][grade]['position']
                 for grade in ('navigation', 'tactical', 'industrial')]

    assert positions == sorted(positions), 'better grade, smaller error'

def testAidingBoundsTheErrorRatherThanReducingIt():

    '''
    The distinction that matters operationally: the unaided case is what has to be survivable, not
    merely unlikely.
    '''

    unaided = buildNavigation(aiding = 'none', positionRequirement = 1.0e6).checkRequirement()
    aided   = buildNavigation(aiding = 'GPS').checkRequirement()

    assert aided['unaidedError'] == pytest.approx(unaided['unaidedError'])
    assert aided['effectiveError'] < aided['unaidedError']
    assert aided['bound'] == AIDING_SOURCES['GPS']['positionBound']
    assert aided['availability'] < 1.0

def testTheGoverningDisturbanceChangesWithDynamicPressure():

    '''
    A gimbal sized on one condition is sized on the wrong one for most of the flight.
    '''

    vacuum = buildControl(dynamicPressure = 50.0, windAngleOfAttack = 0.0)
    maxQ   = buildControl(dynamicPressure = 35000.0, windAngleOfAttack = 4.0)

    assert vacuum.calculateDisturbances()['governing'] == 'thrust misalignment'
    assert maxQ.calculateDisturbances()['governing'] == 'aerodynamic at angle of attack'

def testThrustMisalignmentIsPresentEvenWithNoAerodynamics():

    control = ControlAuthority()
    control.setInputs({'thrust': 100.0e3, 'gimbalArm': 6.0,
                       'arrangement': 'single gimballed engine'})

    disturbances = control.calculateDisturbances()

    assert 'thrust misalignment' in disturbances['terms']
    assert disturbances['total'] > 0.0

def testAGustCanTurnAnAdequateVehicleIntoARefusedOne():

    '''
    The margin between the design case and the gust case is where this domain's refusal fires, and
    it is the case a vehicle is actually lost in.
    '''

    assert buildControl(windAngleOfAttack = 4.0).checkAuthority()['adequate'] is True

    with pytest.raises(ControlAuthorityError):
        buildControl(windAngleOfAttack = 8.0).checkAuthority()

def testTheRequiredActuatorRateScalesWithControlFrequency():

    slow = buildControl().requiredActuatorRate(0.5)
    fast = buildControl().requiredActuatorRate(1.0)

    assert fast['requiredRate'] / slow['requiredRate'] == pytest.approx(2.0)

def testACloseBendingModeIsFlagged():

    control = buildControl(bendingFrequency = 3.0)

    result = control.requiredActuatorRate(1.0)

    assert result['bendingSeparation'] < 5.0

    assert any('notch filter' in finding for finding in result['findings'])

def testAHandfulOfHighRateChannelsDominateTheBudget():

    '''
    Twelve channels out of seventy-six carry three quarters of the bandwidth, which is where a cut
    has to come from and is the group nobody wants to cut.
    '''

    rate = buildTelemetry().calculateBitRate()

    largest = max(rate['detail'], key = lambda entry: entry['bitRate'])

    assert largest['name'] == 'accelerometers'
    assert largest['share'] > 0.7
    assert largest['count'] / rate['channelCount'] < 0.25

def testChannelCountAndSampleRateCompeteForTheSameBits():

    allocations = buildTelemetry().compareAllocations([1.0, 2.0])

    assert (allocations['results'][2.0]['channelsAffordable']
            == pytest.approx(0.5 * allocations['results'][1.0]['channelsAffordable']))

def testARecorderHoldsFarLongerThanTheFlight():

    recorder = buildTelemetry().checkRecorder()

    assert recorder['fits'] is True
    assert recorder['margin'] > 5.0

def testAChannelCanDetectWithoutResolving():

    measurements = [dict(MEASUREMENTS[0], sampleRate = 500.0)]

    rates = buildTelemetry(measurements = measurements).checkSampleRates()

    assert rates['results']['accelerometers']['status'] == 'detects'
    assert rates['allResolve'] is False

def testBooleanFlagsAreRealPythonBooleans():

    flags = [buildNavigation().checkRequirement()['meets'],
             buildNavigation().identifyCrossover()['gyroDominatesAtFlightTime'],
             buildControl().checkAuthority()['adequate'],
             buildTelemetry().checkLink()['fits'],
             buildTelemetry().checkRecorder()['fits'],
             buildTelemetry().checkSampleRates()['allResolve']]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testTheUnvalidatedRegisterNamesWhatThisDomainCannotCheck():

    for key in ('imuGrades', 'controlDisturbances', 'telemetryOverhead'):

        entry = UNVALIDATED[key]

        assert 'avionicsAndGNC' in entry['domain']
        assert entry['consequence']
        assert entry['nextStep']

def testReportsRunForEveryClass():

    assert 'NAVIGATION DRIFT'  in buildNavigation().generateReport()
    assert 'CONTROL AUTHORITY' in buildControl().generateReport()
    assert 'TELEMETRY BUDGET'  in buildTelemetry().generateReport()
