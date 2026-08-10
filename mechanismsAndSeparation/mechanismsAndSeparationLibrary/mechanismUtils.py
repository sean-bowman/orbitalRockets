
# -- Collection of commonly used functions [mechanismsAndSeparation] -- #

'''

Shared function repository for the mechanismsAndSeparation library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one
flat namespace and does not have to know whether a helper is domain-specific or shared.

Domain-specific functions are added here as the library is built out. Anything that turns
out to be needed by a second domain should move to common instead.

Author: Sean Bowman
Date:   08/06/2026

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

#--------------------------------------------------------------------------------------------------------------------------#
# -- mechanismsAndSeparation Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
MechanismsAndSeparationError = EngineeringError


# MechanismsAndSeparationError above is the domain base, aliased to EngineeringError by the
# scaffold. These are the specific ones and they subclass it, so a caller can still catch the whole
# family with one except.

class MarginError(MechanismsAndSeparationError):
    """
    A mechanism whose torque or force margin is negative, or one whose margin is being computed in
    a case where NASA-STD-5017B says the concept does not apply. Raised rather than reported,
    because a mechanism operates once and a negative margin is not a degraded mechanism.
    """

class SeparationError(MechanismsAndSeparationError):
    """
    A separation that recontacts, or one whose geometry and energy cannot produce the clearance
    asked of it.
    """

class InitiationError(MechanismsAndSeparationError):
    """
    A firing circuit that cannot deliver all-fire current, or one that could deliver no-fire
    current under a credible fault. Both are refused rather than reported.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

STANDARD_GRAVITY = 9.80665    # [m/s^2]

# NASA-STD-5017B table 1, minimum safety factors for the torque margin equation.
#
# Read from the standard itself rather than from a summary of it, and that mattered: a search
# summary of this same standard reported a required margin of 1.0 or greater, and the standard says
# a margin greater than or equal to ZERO indicates the requirement is met. The reserve is inside
# these factors, not applied on top of the result.
#
#     variable      friction, viscous drag, harness torque from flexing and set
#     fixed         bearing drag, brush and windage drag, return springs, unbalanced pressure
#     acceleration  the torque required to achieve a specified acceleration
TORQUE_MARGIN_FACTORS = {
    'theory or analysis': {
        'variable': 3.00, 'fixed': 1.50, 'acceleration': 1.25,
        'note': 'initial sizing. The standard is explicit that these are NOT no-test design '
                'factors: verifying margin by test is required regardless'},
    'development test': {
        'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15,
        'note': 'at expected environmental extremes'},
    'qualification test': {
        'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15,
        'note': 'same factors as development test'},
    'lot acceptance test': {
        'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15,
        'note': 'at expected environmental extremes'},
    'acceptance test, ambient': {
        'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15,
        'note': 'flight hardware at ambient conditions'},
    'acceptance test, extremes': {
        'variable': 2.00, 'fixed': 1.25, 'acceleration': 1.10,
        'note': 'flight hardware at expected environmental extremes. The lowest factors available '
                'and they are earned by testing the flight article in its environment'},
    'one spring out': {
        'variable': 1.00, 'fixed': 1.00, 'acceleration': 1.00,
        'note': 'ONLY for redundant springs in parallel with one failed. The standard explicitly '
                'distinguishes this from a single spring designed to tolerate partial failure, '
                'where these factors do not apply'},
}

# The margin the standard requires. Zero, because the reserve is already in the factors above.
REQUIRED_TORQUE_MARGIN = 0.0    # [-]

# Bearing Hertzian contact stress allowables under non-operational yield design loads, from
# NASA-STD-5017B table 3. For non-rotating bearings, which is the launch vibration case.
BEARING_CONTACT_ALLOWABLE = {
    '440C':  {'quiet': 2310.0e6, 'nonQuiet': 2760.0e6, 'hardness': '58-62 HRC'},
    '52100': {'quiet': 2480.0e6, 'nonQuiet': 2960.0e6, 'hardness': '60-63 HRC'},
    'M50':   {'quiet': 2480.0e6, 'nonQuiet': 2960.0e6, 'hardness': '62-64 HRC'},
    'M62':   {'quiet': 3790.0e6, 'nonQuiet': 4070.0e6, 'hardness': '66-69 HRC'},
}

# Bridgewire initiator thresholds. The NASA Standard Initiator convention is a 1 A / 1 W no-fire:
# the device must not fire when 1 A or 1 W is applied for five minutes, and must fire reliably at
# its all-fire current.
#
# The 1 A / 1 W convention is well established. The all-fire currents and bridgewire resistances
# here are representative rather than any specific part number qualification data, and they are
# registered as unvalidated.
INITIATOR_TYPES = {
    'NSI': {
        'noFireCurrent':        1.0,    # [A]
        'noFirePower':          1.0,    # [W]
        'allFireCurrent':       5.0,    # [A]
        'bridgewireResistance': 1.05,   # [ohm]
        'note': 'NASA Standard Initiator. The 1 A / 1 W no-fire is the convention the whole '
                'ordnance safety practice is built around'},
    'low energy': {
        'noFireCurrent':        0.2,    # [A]
        'noFirePower':          0.05,   # [W]
        'allFireCurrent':       1.5,    # [A]
        'bridgewireResistance': 1.0,    # [ohm]
        'note': 'more sensitive, easier to fire and far harder to keep safe. Needs tighter stray '
                'energy control everywhere in the vehicle'},
}

# Applied current below this fraction of the no-fire rating is treated as safe. A factor of two on
# current is common practice, which is a factor of four on power.
NO_FIRE_MARGIN = 2.0    # [-]

# Delivered firing current has to exceed the all-fire current by this factor. Common practice, and
# a convention rather than a standard this repository has read.
ALL_FIRE_MARGIN = 1.5    # [-]

# Clamp band wedge half angle, measured from the plane of the interface. The wedge is what turns a
# modest band tension into a large axial preload, and it is the whole reason the device works.
TYPICAL_WEDGE_ANGLE = 15.0    # [degrees]

# Preload lost to short-term embedment and long-term relaxation, as a fraction of the installed
# preload. Embedment happens in hours as surface asperities flatten; relaxation continues for
# months. Representative and registered as unvalidated.
PRELOAD_RELAXATION = {
    'embedment':  0.05,    # [-] within hours of installation
    'shortTerm':  0.03,    # [-] first weeks
    'storage':    0.05,    # [-] months of storage before flight
}

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def springEnergy(stiffness: float, deflection: float) -> float:

    '''
    Energy stored in a linear spring, one half k x squared.
    '''

    if stiffness <= 0.0 or deflection < 0.0:
        raise InvalidInputError(
            f'The stiffness must be positive and the deflection non-negative, got {stiffness} and '
            f'{deflection}.',
            context = createErrorContext(component = 'mechanismUtils'))

    return 0.5 * stiffness * deflection ** 2

def separationVelocity(energy: float, massOne: float, massTwo: float) -> float:

    '''

    Relative separation velocity from stored energy and the two masses.

    Momentum is conserved and the energy splits between the bodies in inverse proportion to their
    masses, which gives the relative velocity through the reduced mass:

        v_rel = sqrt(2 E (1/m1 + 1/m2))

    The lighter body takes most of the velocity and most of the energy, which is why a small upper
    stage separating from a large booster moves and the booster barely does.

    '''

    if energy < 0.0 or massOne <= 0.0 or massTwo <= 0.0:
        raise InvalidInputError(
            f'The energy must be non-negative and both masses positive, got {energy}, {massOne} '
            f'and {massTwo}.',
            context = createErrorContext(component = 'mechanismUtils'))

    return float(np.sqrt(2.0 * energy * (1.0 / massOne + 1.0 / massTwo)))

def torqueMargin(available: float, fixed: list, variable: list, acceleration: list,
                 source: str = 'theory or analysis') -> dict:

    '''

    NASA-STD-5017B equation 4-1.

        margin = T_avail / (sum FSf Tf + sum FSv Tv + sum FSa Ta) - 1

    The requirement is a margin at or above zero, because the reserve is inside the safety factors
    rather than applied to the result. Setting all three factors to unity gives the torque at which
    no reserve is available at all, which is a different and much weaker statement.

    '''

    if source not in TORQUE_MARGIN_FACTORS:
        raise InvalidInputError(
            f"Unknown torque data source '{source}'. Known sources are "
            f'{sorted(TORQUE_MARGIN_FACTORS)}.',
            context = createErrorContext(component = 'mechanismUtils'))

    factors = TORQUE_MARGIN_FACTORS[source]

    if available <= 0.0:
        raise InvalidInputError(
            f'The available torque must be positive, got {available}.',
            context = createErrorContext(component = 'mechanismUtils'))

    resisting = (factors['fixed'] * sum(fixed)
                 + factors['variable'] * sum(variable)
                 + factors['acceleration'] * sum(acceleration))

    if resisting <= 0.0:
        raise InvalidInputError(
            'The factored resisting torque is zero, so the margin is unbounded. A mechanism with '
            'no resisting torque at all has not been analysed rather than being infinitely good.',
            context = createErrorContext(component = 'mechanismUtils'))

    return {'available':           available,
            'factoredResisting':   resisting,
            'margin':              available / resisting - 1.0,
            'factors':             factors,
            'source':              source,
            'unfactoredResisting': sum(fixed) + sum(variable) + sum(acceleration)}

def clampBandPreload(bandTension: float, wedgeAngle: float = TYPICAL_WEDGE_ANGLE) -> float:

    '''

    Axial preload across the joint from the band tension, through the wedge.

    A band under tension T produces a total inward radial force of 2 pi T on the ring, independent
    of radius. The V-section wedge turns that radial force into axial clamping:

        P = 2 pi T / tan(alpha)

    with alpha the wedge half angle measured from the interface plane. At 15 degrees the
    amplification is about 23, which is the entire reason a light band can hold a stage on.

    '''

    if bandTension <= 0.0:
        raise InvalidInputError(
            f'The band tension must be positive, got {bandTension}.',
            context = createErrorContext(component = 'mechanismUtils'))

    if not 0.0 < wedgeAngle < 90.0:
        raise InvalidInputError(
            f'The wedge half angle must lie in (0, 90) degrees, got {wedgeAngle}. At zero the '
            f'wedge is a cylinder and clamps nothing axially; at ninety it is a flat face and the '
            f'band does not clamp at all.',
            context = createErrorContext(component = 'mechanismUtils'))

    return float(2.0 * np.pi * bandTension / np.tan(np.radians(wedgeAngle)))
