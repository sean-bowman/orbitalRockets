
# -- Collection of commonly used functions [vehicleArchitecture] -- #

'''

Shared function repository for the vehicleArchitecture library.

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
# -- vehicleArchitecture Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
VehicleArchitectureError = EngineeringError

# VehicleArchitectureError above is the domain base, aliased to EngineeringError by the scaffold.
# These are the specific ones and they subclass it, so a caller can still catch the whole family
# with one except.

class ClosureError(VehicleArchitectureError):
    """
    A vehicle that does not close: a sizing loop that diverges, or a stage whose structure weighs
    more than its gross mass permits. Raised rather than reported, because an open design has no
    payload to optimise and reporting a negative one invites somebody to treat it as a small number.
    """

class StagingError(VehicleArchitectureError):
    """
    A staging arrangement that cannot deliver what is asked of it, or one whose stage definitions
    are inconsistent with each other.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

STANDARD_GRAVITY = 9.80665    # [m/s^2]

# Orbital velocity at low Earth orbit altitude, and the rotational assist from an easterly launch at
# Cape Canaveral. Both are geometry rather than vehicle design, and they set the delta-V target
# every architecture is measured against.
LEO_ORBITAL_VELOCITY = 7660.0     # [m/s] circular at about 400 km
EARTH_ROTATION_ASSIST = 408.0     # [m/s] at 28.5 degrees latitude, due east

# Typical ascent loss budget to low Earth orbit, as a band rather than a value.
#
# Gravity loss dominates and it scales with how long the vehicle spends fighting gravity, which is
# set by liftoff thrust to weight. Drag loss is small on a large vehicle and not on a small one.
# Steering loss is a trajectory design outcome and is the smallest of the three.
#
# These are representative and they are registered as unvalidated. What the sub-domain uses them
# for is the SHAPE of the loss against thrust to weight, which is robust to the values.
ASCENT_LOSSES = {
    'gravity':  (1000.0, 1500.0),   # [m/s]
    'drag':     (100.0, 500.0),     # [m/s]
    'steering': (0.0, 200.0),       # [m/s]
}

# Liftoff thrust to weight bounds. Below the floor the vehicle cannot leave the pad with any margin
# for an engine out; above the ceiling the gravity loss saving has stopped paying for the engine
# mass and the drag loss is rising.
LIFTOFF_THRUST_TO_WEIGHT_FLOOR = 1.2      # [-]
LIFTOFF_THRUST_TO_WEIGHT_TYPICAL = 1.35   # [-]
LIFTOFF_THRUST_TO_WEIGHT_CEILING = 1.8    # [-]

# Mass growth allowance by design maturity, as a fraction of the current best estimate.
#
# This follows the shape of the AIAA S-120 and ANSI/AIAA mass properties practice: an allowance
# applied to an estimate because estimates at that maturity have historically grown by that much.
#
# The critical point, and the one this domain makes loudly: growth allowance is NOT margin. The
# allowance covers what the estimate is expected to become; the margin covers what is not known at
# all. Applying one and calling it the other is how a programme discovers it has neither.
MASS_GROWTH_ALLOWANCE = {
    'estimated':    0.25,   # [-] a number from a scaling relationship or a guess
    'calculated':   0.15,   # [-] from an analysis of a defined configuration
    'preliminary':  0.10,   # [-] from a preliminary design with drawings
    'detailed':     0.05,   # [-] from a released drawing set
    'actual':       0.00,   # [-] weighed
}

# Structural coefficient, dry stage mass over gross stage mass, for real vehicles. This is the
# single number a vehicle architecture lives or dies by and it is the hardest one to estimate.
STRUCTURAL_COEFFICIENT_BAND = {
    'kerolox booster':  (0.045, 0.070),   # [-]
    'kerolox upper':    (0.030, 0.055),   # [-]
    'hydrolox upper':   (0.080, 0.120),   # [-] hydrogen is bulky and the tank pays for it
    'pressure fed':     (0.080, 0.150),   # [-] the tank is a pressure vessel, not a shell
}

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def exhaustVelocity(specificImpulse: float) -> float:

    '''
    Effective exhaust velocity from specific impulse. One line, and it is written down because it
    is the only place standard gravity enters a vehicle sizing calculation.
    '''

    if specificImpulse <= 0.0:
        raise InvalidInputError(
            f'The specific impulse must be positive, got {specificImpulse}.',
            context = createErrorContext(component = 'vehicleUtils'))

    return specificImpulse * STANDARD_GRAVITY

def deltaV(exhaust: float, massRatio: float) -> float:

    '''

    Tsiolkovsky. The easy part of vehicle design.

        dV = c ln(m0 / mf)

    '''

    if massRatio < 1.0:
        raise StagingError(
            f'The mass ratio must be at least one, got {massRatio}. A ratio below one means the '
            f'stage ends heavier than it started, which is a bookkeeping error rather than a '
            f'physical result.',
            context = createErrorContext(component = 'vehicleUtils'))

    return exhaust * np.log(massRatio)

def structuralCoefficient(dryMass: float, grossMass: float) -> float:

    '''

    Dry stage mass over gross stage mass, the number a vehicle architecture lives or dies by.

    Note the denominator. Some sources define it against propellant mass rather than gross mass,
    and the two differ by enough to change a design. This repository uses gross mass throughout and
    a test asserts the published reference cases are read the same way.

    '''

    if grossMass <= 0.0:
        raise InvalidInputError(
            f'The gross mass must be positive, got {grossMass}.',
            context = createErrorContext(component = 'vehicleUtils'))

    if dryMass >= grossMass:
        raise ClosureError(
            f'The dry mass {dryMass:.0f} kg is at or above the gross mass {grossMass:.0f} kg, so '
            f'the stage carries no propellant. That is not a heavy stage, it is a bookkeeping '
            f'error or a design that has already failed to close.',
            context = createErrorContext(component = 'vehicleUtils'))

    return dryMass / grossMass

def massGrowthAllowance(currentEstimate: float, maturity: str) -> float:

    '''

    The allowance to add to a current best estimate, from its design maturity.

    Not a margin. See MASS_GROWTH_ALLOWANCE.

    '''

    if maturity not in MASS_GROWTH_ALLOWANCE:
        raise InvalidInputError(
            f'Unknown design maturity \'{maturity}\'. Known levels are '
            f'{sorted(MASS_GROWTH_ALLOWANCE)}.',
            context = createErrorContext(component = 'vehicleUtils'))

    if currentEstimate < 0.0:
        raise InvalidInputError(
            f'The current estimate cannot be negative, got {currentEstimate}.',
            context = createErrorContext(component = 'vehicleUtils'))

    return currentEstimate * MASS_GROWTH_ALLOWANCE[maturity]
