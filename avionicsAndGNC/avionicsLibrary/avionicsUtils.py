# -- Domain-specific helpers [avionicsAndGNC] -- #

'''

Sensor error models, control authority and telemetry budgets.

Named avionicsUtils rather than utils. Every domain library in this repository has a helper module
re-exporting the shared foundation, and identically named ones resolve to a single entry in
sys.modules when more than one domain is imported in a single process. That works by accident for
the names every domain re-exports and fails for anything only one domain defines.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np

def _bootstrapCommon() -> None:

    '''
    Locate the orbitalRockets/common package and put it on sys.path.
    '''

    directory = os.path.dirname(os.path.abspath(__file__))

    while directory != os.path.dirname(directory):
        candidate = os.path.join(directory, 'common')
        if os.path.isdir(candidate):
            if candidate not in sys.path:
                sys.path.insert(0, candidate)
            return
        directory = os.path.dirname(directory)

    raise ImportError('Could not locate the orbitalRockets/common package.')

_bootstrapCommon()

# Re-export the shared foundation so the namespace inside this library stays flat.
from units import *
from fluidProperties import *
from materials import *
from structures import *
from solvers import *
from reporting import *
from errors import *

# Permissive numeric-input alias: these helpers accept arrays, lists, or scalars interchangeably.
ArrayLike = np.ndarray | list | float | int

#--------------------------------------------------------------------------------------------------------------------------#
# -- avionicsAndGNC Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause.
AvionicsError = EngineeringError

class NavigationError(AvionicsError):
    """
    A navigation solution whose error has grown past what the mission tolerates, or a sensor
    specification that cannot support the flight duration asked of it.
    """

class ControlAuthorityError(AvionicsError):
    """
    A control system that cannot produce the moment it needs, or cannot produce it fast enough.
    Raised rather than reported, because a vehicle that cannot hold attitude is not a vehicle with
    a small negative margin.
    """

class TelemetryError(AvionicsError):
    """
    A telemetry plan that does not fit its link, or a sample rate that cannot represent what it is
    measuring.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

STANDARD_GRAVITY = 9.80665       # [m/s^2]
EARTH_RATE = 7.2921159e-5        # [rad/s]

# Inertial measurement unit grades, with the error terms that matter for a launch vehicle.
#
# These are representative of each class rather than of any part number, and they are registered as
# unvalidated. The ORDERING between grades is the robust part and it spans four orders of magnitude,
# which is what makes the grade choice the decision rather than the specific unit.
#
#     gyroBias          [deg/h]         constant rate error, integrates into an attitude ramp
#     gyroRandomWalk    [deg/sqrt(h)]   noise, integrates into a random walk in attitude
#     accelBias         [micro g]       constant acceleration error, integrates twice into position
#     accelRandomWalk   [m/s/sqrt(h)]   noise, integrates into a random walk in velocity
IMU_GRADES = {
    'navigation': {
        'gyroBias':        0.01,      # [deg/h]
        'gyroRandomWalk':  0.002,     # [deg/sqrt(h)]
        'accelBias':       25.0,      # [micro g]
        'accelRandomWalk': 0.02,      # [m/s/sqrt(h)]
        'note': 'ring laser or fibre optic. What a launch vehicle flies unaided, and it is '
                'expensive and heavy enough that the decision is felt'},
    'tactical': {
        'gyroBias':        1.0,       # [deg/h]
        'gyroRandomWalk':  0.05,      # [deg/sqrt(h)]
        'accelBias':       300.0,     # [micro g]
        'accelRandomWalk': 0.1,       # [m/s/sqrt(h)]
        'note': 'fibre optic or high grade MEMS. Adequate for a short flight or with a good aiding '
                'source, and the usual choice on a small vehicle'},
    'industrial': {
        'gyroBias':        50.0,      # [deg/h]
        'gyroRandomWalk':  0.5,       # [deg/sqrt(h)]
        'accelBias':       2000.0,    # [micro g]
        'accelRandomWalk': 0.5,       # [m/s/sqrt(h)]
        'note': 'MEMS. Unusable unaided for anything but seconds, and entirely usable with a '
                'continuous aiding source'},
}

MICRO_G = 1.0e-6 * STANDARD_GRAVITY    # [m/s^2] per micro g

# Aiding sources and what each bounds. An aiding source does not reduce the IMU error, it stops it
# growing, which is a different and more useful thing.
AIDING_SOURCES = {
    'none': {
        'positionBound': None,
        'velocityBound': None,
        'availability':  1.0,
        'note': 'pure inertial. The error grows without limit and the only question is how fast'},
    'GPS': {
        'positionBound': 10.0,     # [m]
        'velocityBound': 0.1,      # [m/s]
        'availability':  0.98,
        'note': 'bounds the error rather than reducing it. Subject to jamming, to the launch '
                'dynamics limits in the receiver, and to a reacquisition time after any outage'},
    'star tracker': {
        'positionBound': None,
        'velocityBound': None,
        'availability':  0.95,
        'note': 'bounds ATTITUDE only, which is exactly the term that dominates the position error '
                'growth. Useless in atmosphere and during high rate manoeuvres'},
}

# Thrust vector control arrangements, with the gimbal range each typically provides.
TVC_ARRANGEMENTS = {
    'single gimballed engine': {
        'maximumAngle': 8.0,      # [degrees]
        'axes':         2,
        'note':         'pitch and yaw from the gimbal, roll from something else entirely'},
    'gimballed cluster': {
        'maximumAngle': 6.0,      # [degrees]
        'axes':         3,
        'note':         'differential gimbal gives roll, which is why a cluster does not need a '
                        'separate roll system'},
    'fixed engine with RCS': {
        'maximumAngle': 0.0,      # [degrees]
        'axes':         3,
        'note':         'all control authority from reaction control, which is adequate on an '
                        'upper stage in vacuum and nowhere near adequate in atmosphere'},
}

# Gain and phase margin conventions for a launch vehicle attitude loop. These are the classical
# aerospace values and they are conventions rather than a standard this repository has read.
GAIN_MARGIN_REQUIREMENT = 6.0     # [dB]
PHASE_MARGIN_REQUIREMENT = 30.0   # [degrees]

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def attitudeErrorFromGyroBias(bias: float, time: float) -> float:

    '''

    Attitude error from a constant gyro bias, which grows linearly with time.

        theta = b t

    Bias is supplied in degrees per hour and time in seconds; the result is in radians.

    '''

    if time < 0.0:
        raise InvalidInputError(
            f'The time cannot be negative, got {time}.',
            context = createErrorContext(component = 'avionicsUtils'))

    return np.radians(bias / 3600.0) * time

def attitudeErrorFromRandomWalk(walk: float, time: float) -> float:

    '''

    Attitude error from angle random walk, which grows with the square root of time.

        theta = w sqrt(t)

    Walk is supplied in degrees per root hour.

    '''

    if time < 0.0:
        raise InvalidInputError(
            f'The time cannot be negative, got {time}.',
            context = createErrorContext(component = 'avionicsUtils'))

    return np.radians(walk) * np.sqrt(time / 3600.0)

def positionErrorFromAccelBias(bias: float, time: float) -> float:

    '''

    Position error from a constant accelerometer bias, which grows with the SQUARE of time.

        x = 0.5 b t^2

    Bias is supplied in micro g. The square is the whole reason inertial navigation needs aiding:
    a bias that is negligible for a minute is not negligible for ten.

    '''

    if time < 0.0:
        raise InvalidInputError(
            f'The time cannot be negative, got {time}.',
            context = createErrorContext(component = 'avionicsUtils'))

    return 0.5 * bias * MICRO_G * time ** 2

def positionErrorFromTilt(attitudeError: float, time: float) -> float:

    '''

    Position error from an attitude error, through gravity misresolution.

    This is the term that dominates and it is the one that surprises people. An attitude error
    tilts the accelerometer triad, so a component of gravity appears as horizontal acceleration:

        a = g sin(theta) ~ g theta

    With the attitude error itself growing linearly from gyro bias, the position error from this
    path grows as the CUBE of time.

    '''

    if time < 0.0:
        raise InvalidInputError(
            f'The time cannot be negative, got {time}.',
            context = createErrorContext(component = 'avionicsUtils'))

    return 0.5 * STANDARD_GRAVITY * attitudeError * time ** 2

def nyquistRate(frequency: float, factor: float = 10.0) -> float:

    '''

    Sample rate needed to represent a frequency.

    The factor defaults to ten rather than two, because two is the theoretical floor for
    reconstructing a pure tone and is not enough to resolve the amplitude and shape of a transient.
    The same distinction appears in propulsionTesting for the same reason.

    '''

    if frequency <= 0.0:
        raise InvalidInputError(
            f'The frequency must be positive, got {frequency}.',
            context = createErrorContext(component = 'avionicsUtils'))

    return factor * frequency
