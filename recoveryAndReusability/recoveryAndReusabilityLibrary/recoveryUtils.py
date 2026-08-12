
# -- Collection of commonly used functions [recoveryAndReusability] -- #

'''

Shared function repository for the recoveryAndReusability library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one
flat namespace and does not have to know whether a helper is domain-specific or shared.

What is defined here is the entry environment closed forms, which are the only part of this domain
with a textbook derivation behind them, and the operational tables the reuse classes work from.

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
# -- recoveryAndReusability Errors -- #
# ------------------------------------------------------------------------------------------------ #

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause.
RecoveryError = EngineeringError

# Kept as an alias because the scaffold named it this and nothing gains from breaking it.
RecoveryAndReusabilityError = RecoveryError

class EntryError(RecoveryError):
    """
    An entry case outside what a closed form ballistic solution can describe: a flight path angle
    at or through the horizontal, a negative ballistic coefficient, or a body whose lift makes the
    ballistic assumption meaningless.
    """

class LandingError(RecoveryError):
    """
    A touchdown the vehicle does not survive: a load factor above the structural limit, a stroke
    that bottoms out, or a tipover margin at or below zero. Raised rather than reported, because a
    vehicle that tips over is not a vehicle with a small negative margin.
    """

class LifeError(RecoveryError):
    """
    An article flown past a life limit, or a life calculation with no measured environment behind
    it. Both are dispositions rather than numbers.
    """

class EconomicsError(RecoveryError):
    """
    A reuse case that cannot close: a refurbishment cost above the expendable unit cost, or a
    recovery success rate that makes the fleet shrink faster than it flies.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Entry environment: Allen-Eggers and Sutton-Graves -- #
# ------------------------------------------------------------------------------------------------ #

# Allen and Eggers solved ballistic entry into an exponential atmosphere in closed form in 1958,
# and the solution is still the first thing anybody should compute about an entry.
#
#     V(rho) = V_e * exp( -rho * H / (2 * beta * sin|gamma|) )
#
# with beta = m / (Cd * A) the ballistic coefficient, H the atmospheric scale height, and gamma the
# flight path angle, assumed constant. Everything below falls out of differentiating that.
#
# The two velocity fractions are pure numbers. They depend on nothing about the vehicle, the
# atmosphere or the trajectory, which is the single most useful fact in the whole subject.
PEAK_DECELERATION_VELOCITY_FRACTION = float(np.exp(-0.5))       # 0.6065, from d(rho V^2)/d(rho) = 0
PEAK_HEATING_VELOCITY_FRACTION      = float(np.exp(-1.0 / 6.0)) # 0.8465, from d(sqrt(rho) V^3)/d(rho) = 0

# Peak heating happens EARLIER and HIGHER than peak deceleration, at about 1.1 times the altitude.
# That ordering is fixed by the two fractions above and does not move.
PEAK_HEATING_ALTITUDE_RATIO = 1.1    # [-] approximate, h*_q / h*_g

# Sutton and Graves, NASA TR R-376, 1971. Stagnation point convective heating for a blunt body:
#
#     q = k * sqrt(rho / Rn) * V ** 3
#
# The constant for Earth air is 1.7415e-4. Its UNITS are quoted inconsistently: several sources
# state the expression returns W/cm2 with density in kg/m3, nose radius in metres and velocity in
# metres per second, and that is wrong by four orders of magnitude.
#
# Fixed here by reproducing published entry cases rather than by trusting the statement:
#
#     Stardust, V = 12.6 km/s, Rn = 0.23 m, rho = 2e-4     ->  1027 W/cm2 against ~1200 published
#     Apollo,   V = 11.1 km/s, Rn = 4.69 m, rho = 3.1e-4   ->   196 W/cm2 against ~200-250
#
# Both land where they should when the raw expression is read as W/m2, and are absurd by 1e4 when
# it is read as W/cm2. The library therefore works in W/m2 and converts for reporting.
SUTTON_GRAVES_CONSTANT = 1.7415e-4       # [W/m2 per (kg/m3/m)**0.5 (m/s)**3], Earth air
WATT_PER_M2_TO_WATT_PER_CM2 = 1.0e-4     # [-]

# Exponential atmosphere. A scale height of 7,200 m and a sea level density of 1.225 kg/m3 are the
# usual fit for the lower atmosphere, and the Allen-Eggers solution is only as good as the fit.
#
# The peak heating and deceleration altitudes for an orbital entry land between 40 and 70 km, where
# a single scale height is a coarse approximation and a two-layer fit would be better. What the
# solution gets right regardless is the SHAPE: which quantity peaks first, what each depends on,
# and which of them is independent of the vehicle.
ATMOSPHERIC_SCALE_HEIGHT = 7200.0        # [m]
SEA_LEVEL_DENSITY = 1.225                # [kg/m3]

# ------------------------------------------------------------------------------------------------ #
# -- Recovery architectures -- #
# ------------------------------------------------------------------------------------------------ #

# What a recovery mode costs, as fractions of the stage's own propellant load and dry mass.
#
# These are representative. What is NOT representative is the ordering and the shape: a return to
# the launch site costs more than a downrange landing because it has to cancel and reverse the
# downrange velocity, and both cost more than not recovering at all. That ordering holds for any
# values.
RECOVERY_MODES = {
    'expended': {
        'reservePropellantFraction': 0.00,
        'hardwareDryFraction':       0.00,
        'note':                      'the baseline everything else is measured against'},

    'downrangeLanding': {
        'reservePropellantFraction': 0.09,
        'hardwareDryFraction':       0.09,
        'note':                      'entry burn and landing burn, no boost-back'},

    'returnToLaunchSite': {
        'reservePropellantFraction': 0.17,
        'hardwareDryFraction':       0.09,
        'note':                      'boost-back as well, which is the largest single term'},

    'parachuteAndSplashdown': {
        'reservePropellantFraction': 0.00,
        'hardwareDryFraction':       0.06,
        'note':                      'no reserve propellant, and salt water is the refurbishment '
                                     'problem instead'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Life management and refurbishment -- #
# ------------------------------------------------------------------------------------------------ #

# What post-flight inspection can establish, and what it costs relative to a walkaround.
#
# The ordering is the point. Each level catches something the one below cannot, and the cost rises
# faster than the coverage does, which is why the disposition question is never "inspect more".
INSPECTION_LEVELS = {
    'walkaround':        {'relativeCost':  1.0, 'catches': 'visible damage and missing hardware'},
    'borescope':         {'relativeCost':  4.0, 'catches': 'internal surfaces without disassembly'},
    'proofPressure':     {'relativeCost': 12.0, 'catches': 'a flaw large enough to leak or burst'},
    'nonDestructive':    {'relativeCost': 25.0, 'catches': 'a flaw below the proof size, where access allows'},
    'teardown':          {'relativeCost': 90.0, 'catches': 'everything, and ends the article as flown'},
}

# Damage accumulated per flight, as a fraction of allowable life, for the items that usually set
# the refurbishment interval. Representative, and registered as such.
#
# The structural result they carry is that the limiting item is rarely the one that looks worst.
LIFE_LIMITED_ITEMS = {
    'engine turbopump':     {'damagePerFlight': 1.0 / 15.0, 'driver': 'low cycle fatigue on start and shutdown'},
    'thermal protection':   {'damagePerFlight': 1.0 / 25.0, 'driver': 'recession and cracking per entry'},
    'pressure vessel':      {'damagePerFlight': 1.0 / 60.0, 'driver': 'pressure cycles against a fracture life'},
    'landing leg':          {'damagePerFlight': 1.0 / 40.0, 'driver': 'crush core or damper, one shot per landing'},
    'primary structure':    {'damagePerFlight': 1.0 / 200.0,'driver': 'load cycles, and it is rarely the limit'},
}

def ballisticCoefficient(mass: float, dragCoefficient: float, referenceArea: float) -> float:

    '''

    beta = m / (Cd * A), in kg per square metre.

    A high ballistic coefficient body decelerates lower in the atmosphere, which raises both its
    peak heating rate and its total heat load. It does NOT raise its peak deceleration.

    '''

    if mass <= 0.0 or dragCoefficient <= 0.0 or referenceArea <= 0.0:
        raise EntryError('Mass, drag coefficient and reference area must all be positive.')

    return mass / (dragCoefficient * referenceArea)

def suttonGravesHeatFlux(density: float, noseRadius: float, velocity: float) -> float:

    '''

    Stagnation point convective heat flux in W/m2.

    '''

    if density < 0.0 or noseRadius <= 0.0:
        raise EntryError('Density cannot be negative and nose radius must be positive.')

    return SUTTON_GRAVES_CONSTANT * np.sqrt(density / noseRadius) * velocity ** 3

def exponentialDensity(altitude: float) -> float:

    '''
    Exponential atmosphere density, the model the Allen-Eggers solution assumes.
    '''

    return SEA_LEVEL_DENSITY * np.exp(-altitude / ATMOSPHERIC_SCALE_HEIGHT)

def altitudeFromDensity(density: float) -> float:

    '''
    The inverse, used to report where in the atmosphere each peak happens.
    '''

    if density <= 0.0:
        raise EntryError('Density must be positive to invert the exponential atmosphere.')

    return ATMOSPHERIC_SCALE_HEIGHT * np.log(SEA_LEVEL_DENSITY / density)
