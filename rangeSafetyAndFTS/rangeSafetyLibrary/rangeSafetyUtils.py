
# -- Collection of commonly used functions [rangeSafetyAndFTS] -- #

'''

Shared function repository for the rangeSafetyAndFTS library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one
flat namespace and does not have to know whether a helper is domain-specific or shared.

What is defined here is the regulatory criteria, which are the substance of this domain and which
were read from the regulation rather than from a summary of it.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np

def _bootstrapCommon() -> None:

    '''

    Locate the orbitalRockets/common package and put it on sys.path.

    Walks up from this file until it finds a sibling directory named 'common', so it works
    from any nesting depth.

    '''

    directory = os.path.dirname(os.path.abspath(__file__))

    while directory != os.path.dirname(directory):
        candidate = os.path.join(directory, 'common')
        if os.path.isdir(candidate):
            if candidate not in sys.path:
                sys.path.insert(0, candidate)
            return
        directory = os.path.dirname(directory)

    raise ImportError('Could not locate the orbitalRockets/common package by walking up from '
                      f'{os.path.abspath(__file__)}.')

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

# ------------------------------------------------------------------------------------------------ #
# -- rangeSafetyAndFTS Errors -- #
# ------------------------------------------------------------------------------------------------ #

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause.
RangeSafetyError = EngineeringError

class ImpactPointError(RangeSafetyError):
    """
    A state vector with no instantaneous impact point, which happens at orbital insertion when the
    free-flight perigee rises above the Earth's surface. That is a physical fact rather than a
    numerical failure, and it is the moment the flight termination system stops having a job.
    """

class RiskError(RangeSafetyError):
    """
    A risk analysis that exceeds a regulatory criterion. Raised rather than reported, because
    14 CFR 450.101 is a limit rather than a target and a launch above it does not get a licence.
    """

class TerminationError(RangeSafetyError):
    """
    A flight termination system that cannot support its reliability claim, or a demonstration
    plan that cannot establish it.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Regulatory criteria: 14 CFR Part 450 -- #
# ------------------------------------------------------------------------------------------------ #

# 14 CFR 450.101, launch safety criteria, read from the regulation.
#
# Two things about this table are worth knowing before it is used.
#
# **These are limits rather than targets.** A launch above any of them does not get a licence, and
# there is no engineering argument that trades one against another.
#
# **Collective and individual risk are separate tests and both apply.** A launch can pass the
# collective criterion by spreading a small risk over a large population and still fail the
# individual one for the person nearest the trajectory, which is the case the individual limit
# exists to catch.
LAUNCH_SAFETY_CRITERIA = {
    'publicCollective': {
        'limit': 1.0e-4, 'measure': 'expected casualties, Ec',
        'applies': 'all members of the public, excluding persons in aircraft and neighbouring '
                   'operations personnel'},

    'neighbouringCollective': {
        'limit': 2.0e-4, 'measure': 'expected casualties, Ec',
        'applies': 'neighbouring operations personnel'},

    'publicIndividual': {
        'limit': 1.0e-6, 'measure': 'probability of casualty per launch, Pc',
        'applies': 'any individual member of the public'},

    'neighbouringIndividual': {
        'limit': 1.0e-5, 'measure': 'probability of casualty per launch, Pc',
        'applies': 'any individual neighbouring operations person'},

    'aircraft': {
        'limit': 1.0e-6, 'measure': 'probability of impact with debris capable of causing a casualty',
        'applies': 'aircraft, through the hazard areas established for them'},
}

# 14 CFR 450.145, highly reliable flight safety system.
#
# **A design reliability of 0.999 at 95 per cent confidence**, for the onboard and the off-vehicle
# portions both. That single pair of numbers is the reason the whole subject looks the way it does,
# and the arithmetic behind it is in TerminationReliability.
FLIGHT_SAFETY_RELIABILITY = 0.999      # [-]
FLIGHT_SAFETY_CONFIDENCE = 0.95        # [-]

# ------------------------------------------------------------------------------------------------ #
# -- Earth model -- #
# ------------------------------------------------------------------------------------------------ #

# A spherical non-rotating Earth for the free-flight solution, with the rotation applied afterwards
# as a correction to where the impact point lands rather than as a term in the trajectory.
#
# That is the standard treatment and it is accurate enough for an impact point: the free-flight time
# is minutes and the correction is a rotation of the ground beneath a trajectory that is itself
# computed in an inertial frame.
EARTH_RADIUS = 6371.0e3                # [m], mean
EARTH_MU = 3.986004418e14              # [m3/s2]
EARTH_ROTATION_RATE = 7.2921159e-5     # [rad/s]

# ------------------------------------------------------------------------------------------------ #
# -- Debris and casualty modelling -- #
# ------------------------------------------------------------------------------------------------ #

# Casualty area per fragment class, in square metres. This is the area within which a person is
# considered a casualty, and it is the fragment's own footprint plus an allowance for a standing
# person and for the fragment skipping or splashing.
#
# Representative. What is not representative is the ordering: a large fragment threatens a larger
# area than a small one, and both threaten far more than their own footprint.
CASUALTY_AREA = {
    'small':  {'area':  0.5, 'mass':    0.5, 'note': 'inert fragment, lethal by impact energy'},
    'medium': {'area':  3.0, 'mass':   10.0, 'note': 'the bulk of a debris catalogue by count'},
    'large':  {'area': 15.0, 'mass':  200.0, 'note': 'tankage and structure sections'},
    'intact': {'area': 90.0, 'mass': 5000.0, 'note': 'a stage that did not break up'},
}

# Population density by land use class, people per square kilometre. Representative and enormously
# variable, which is why a real analysis uses a gridded census product rather than a class.
POPULATION_DENSITY = {
    'openOcean':      0.0,
    'shippingLane':   0.02,
    'remoteLand':     1.0,
    'ruralLand':      50.0,
    'suburban':       1500.0,
    'urban':          6000.0,
    'denseUrban':     20000.0,
}


# ------------------------------------------------------------------------------------------------ #
# -- Break-up and debris dispersion -- #
# ------------------------------------------------------------------------------------------------ #

# Exponential atmosphere, matching the one recoveryAndReusability propagates an entry through. Two
# domains falling bodies through two different atmospheres would be a drift waiting to happen, and
# a test asserts these agree with the recovery library's constants.
SEA_LEVEL_DENSITY = 1.225                # [kg/m3]
ATMOSPHERIC_SCALE_HEIGHT = 7200.0        # [m]

GRAVITY = 9.80665                        # [m/s2]

# The debris catalogue produced by a commanded destruct.
#
# **The ballistic coefficient is the whole model.** m / (Cd A) decides how far downrange a fragment
# lands, how long it takes to get there, and therefore how far the wind carries it, and the four
# classes below span it by a factor of 660. That spread is what makes a debris footprint an
# ellipse tens of kilometres long rather than a point, and it is the reason a catalogue cannot be
# collapsed to an average fragment.
#
# The counts, masses and drag areas are REPRESENTATIVE of a small two stage vehicle and are
# registered as unvalidated. A real catalogue comes from a structural break-up analysis of a
# specific vehicle and is programme property. What is not representative is the ordering and the
# span, which follow from what the fragments are: a pressure vessel dome is dense and compact, an
# insulation panel is neither.
DEBRIS_CATALOGUE = {
    'insulation':  {'count': 400, 'mass':    0.4, 'dragArea': 0.30,
                    'casualtyClass': 'small',
                    'note': 'foam, cork and shroud panel. Stops in the upper air and then drifts'},
    'skin':        {'count': 180, 'mass':    6.0, 'dragArea': 0.55,
                    'casualtyClass': 'medium',
                    'note': 'tank wall and fairing sections, tumbling'},
    'structure':   {'count':  40, 'mass':  120.0, 'dragArea': 0.90,
                    'casualtyClass': 'large',
                    'note': 'thrust structure, interstage frames, ring segments'},
    'machinery':   {'count':   6, 'mass': 1400.0, 'dragArea': 1.60,
                    'casualtyClass': 'intact',
                    'note': 'engine and turbomachinery, the densest thing on the vehicle'},
}

# Velocity a destruct charge imparts to a fragment, spread roughly isotropically. A linear shaped
# charge opens a tank rather than shattering it, so this is small next to the vehicle velocity and
# it is not small next to the difference between fragment classes.
#
# Representative, and registered. What it controls is the WIDTH of the footprint; the length comes
# from the ballistic coefficient spread and is an order of magnitude larger.
DESTRUCT_IMPARTED_VELOCITY = 30.0        # [m/s]

def ballisticCoefficient(mass: float, dragArea: float) -> float:

    '''

    Ballistic coefficient m / (Cd A), in kg/m2.

    Drag area is Cd times the reference area, taken together because neither is separately knowable
    for a tumbling fragment. A tumbling plate has no single reference area and its drag coefficient
    is an average over attitude, so splitting the product implies a precision that is not there.

    '''

    if mass <= 0.0 or dragArea <= 0.0:
        raise InvalidInputError(
            f'A fragment with a mass of {mass} kg and a drag area of {dragArea} m2 has no '
            f'ballistic coefficient. Both have to be positive.',
            context = createErrorContext(component = 'rangeSafetyUtils'))

    return mass / dragArea

def terminalVelocity(ballistic: float, density: float = SEA_LEVEL_DENSITY) -> float:

    '''

    Terminal velocity of a fragment at a given air density, in m/s.

    From drag equal to weight: `rho v^2 / 2 * Cd A = m g`, so `v = sqrt( 2 g beta / rho )`. Exact,
    and the check that the propagation below has not gone wrong: a fragment released high enough
    arrives at the ground at this speed and no other.

    '''

    if ballistic <= 0.0 or density <= 0.0:
        raise InvalidInputError(
            f'A terminal velocity needs a positive ballistic coefficient and density, got '
            f'{ballistic} and {density}.',
            context = createErrorContext(component = 'rangeSafetyUtils'))

    return float(np.sqrt(2.0 * GRAVITY * ballistic / density))

def atmosphericDensity(altitude: float) -> float:

    '''
    Exponential atmosphere density in kg/m3. Clamped at the ground rather than extrapolated below
    it, because a fragment that has landed has stopped rather than entered a denser atmosphere.
    '''

    return float(SEA_LEVEL_DENSITY * np.exp(-max(altitude, 0.0) / ATMOSPHERIC_SCALE_HEIGHT))

def freeFlightRangeAngle(radius: float, speed: float, flightPathAngle: float,
                         impactRadius: float = None) -> dict:

    '''

    The Keplerian free-flight solution: where a vehicle would land if thrust stopped now.

    The state defines an orbit. Follow it forward to where it crosses the Earth's surface and that
    is the instantaneous impact point.

    Parameters
    ----------
    radius : float
        Distance from the Earth's centre [m].
    speed : float
        Inertial speed [m/s].
    flightPathAngle : float
        Angle above the local horizontal [deg].
    impactRadius : float
        The radius counted as impact, defaulting to the Earth's surface.

    Returns
    -------
    dict
        Range angle, eccentricity, semi-major axis, perigee radius and time of flight.

    '''

    if impactRadius is None:
        impactRadius = EARTH_RADIUS

    if radius <= 0.0 or speed < 0.0:
        raise ImpactPointError('Radius must be positive and speed cannot be negative.')

    angle = np.radians(flightPathAngle)

    # Specific angular momentum and energy define the orbit completely.
    momentum = radius * speed * np.cos(angle)
    energy = 0.5 * speed ** 2 - EARTH_MU / radius

    parameter = momentum ** 2 / EARTH_MU
    eccentricitySquared = 1.0 + 2.0 * energy * momentum ** 2 / EARTH_MU ** 2
    eccentricity = np.sqrt(max(0.0, eccentricitySquared))

    if eccentricity < 1.0e-9:
        raise ImpactPointError(
            'The state is a circular orbit, which never returns to the surface. There is no '
            'instantaneous impact point.')

    semiMajor = parameter / (1.0 - eccentricity ** 2) if abs(eccentricity - 1.0) > 1.0e-9 else np.inf
    perigee = parameter / (1.0 + eccentricity)

    if perigee >= impactRadius:
        raise ImpactPointError(
            f'The free-flight perigee is {(perigee - EARTH_RADIUS) / 1000.0:.1f} km above the '
            f'surface, so the trajectory does not intersect the Earth and there is no impact '
            f'point. **This is orbital insertion**, and it is the moment the flight termination '
            f'system stops having a job.',
            context = {'perigeeAltitude': perigee - EARTH_RADIUS,
                       'eccentricity':    float(eccentricity),
                       'speed':           speed})

    def trueAnomaly(atRadius: float) -> float:
        cosine = (parameter / atRadius - 1.0) / eccentricity
        return float(np.arccos(np.clip(cosine, -1.0, 1.0)))

    # The vehicle is ascending if the flight path angle is positive, which puts it before apogee.
    current = trueAnomaly(radius)
    if flightPathAngle < 0.0:
        current = -current

    # Impact is on the descending side, so the true anomaly there is the negative root.
    impact = -trueAnomaly(impactRadius)

    rangeAngle = (impact - current) % (2.0 * np.pi)

    return {'rangeAngle':      float(rangeAngle),
            'eccentricity':    float(eccentricity),
            'semiMajorAxis':   float(semiMajor),
            'perigeeRadius':   float(perigee),
            'perigeeAltitude': float(perigee - EARTH_RADIUS),
            'parameter':       float(parameter),
            'currentAnomaly':  current,
            'impactAnomaly':   impact,
            'timeOfFlight':    _timeOfFlight(semiMajor, eccentricity, current, impact)}

def _timeOfFlight(semiMajor: float, eccentricity: float,
                  fromAnomaly: float, toAnomaly: float) -> float:

    '''

    Kepler's equation, from true anomaly to time, for the elliptical case.

    A suborbital free-flight arc is an ellipse with the Earth's centre at a focus, so the eccentric
    anomaly and the mean anomaly both exist and the time follows directly.

    '''

    if not np.isfinite(semiMajor) or eccentricity >= 1.0:
        return float('nan')

    def meanAnomaly(trueValue: float) -> float:
        eccentric = 2.0 * np.arctan2(np.sqrt(1.0 - eccentricity) * np.sin(trueValue / 2.0),
                                     np.sqrt(1.0 + eccentricity) * np.cos(trueValue / 2.0))
        return eccentric - eccentricity * np.sin(eccentric)

    motion = np.sqrt(EARTH_MU / semiMajor ** 3)
    elapsed = (meanAnomaly(toAnomaly) - meanAnomaly(fromAnomaly)) % (2.0 * np.pi)

    return float(elapsed / motion)

def zeroFailureTestCount(reliability: float, confidence: float) -> float:

    '''

    The number of successful tests, with no failures, needed to demonstrate a reliability at a
    confidence level.

    From the binomial with zero failures, the lower confidence bound on reliability after n
    successes is (1 - C) ** (1/n), so

        n = ln(1 - C) / ln(R)

    **This is the arithmetic that shapes the whole subject.** Demonstrating 0.999 at 95 per cent
    confidence by test alone takes about three thousand successful tests of a single-use ordnance
    system, which nobody has ever done and nobody ever will.

    '''

    if not 0.0 < reliability < 1.0:
        raise TerminationError('Reliability must lie strictly between zero and one.')

    if not 0.0 < confidence < 1.0:
        raise TerminationError('Confidence must lie strictly between zero and one.')

    return float(np.log(1.0 - confidence) / np.log(reliability))
