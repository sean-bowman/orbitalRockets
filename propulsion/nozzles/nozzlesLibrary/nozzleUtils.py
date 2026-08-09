# -- Domain-specific helpers [nozzles] -- #

'''

Thrust coefficient, area ratio selection, flow separation and altitude compensation.

Named nozzleUtils rather than utils. Every domain library in this repository has a utils.py
re-exporting the shared foundation, and they all resolve to the same 'utils' entry in sys.modules
when more than one domain is imported in a single process. That works by accident for the names
every domain re-exports and fails for anything only one domain defines.

Domain-specific helpers are added here as the library is built out. Anything needed by a second
domain belongs in orbitalRockets/common instead.

Author: Sean Bowman
Date:   08/08/2026

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
# -- nozzles Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
NozzleError = EngineeringError

# NozzleError above is the domain base, aliased to EngineeringError by the scaffold. These are the
# specific ones and they subclass it, so a caller can still catch the whole family with one except.

class ContourError(NozzleError):
    """
    A nozzle geometry or contour that does not follow from its inputs.
    """

class SeparationError(NozzleError):
    """
    A flow condition where the boundary layer detaches, which is a structural event rather than a
    performance one and is refused rather than reported as a thrust coefficient.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

_HUB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'propulsionLibrary')

if _HUB not in sys.path:
    sys.path.insert(0, _HUB)

from propulsionUtils import (PROPELLANT_COMBINATIONS, SUMMERFIELD_SEPARATION_RATIO,
                             vandenkerckhove, areaRatioFromPressureRatio,
                             pressureRatioFromAreaRatio, convertAltitudeToPressure)

# Contour types, with the exit wall angle each produces and the length each takes as a fraction of
# a 15 degree cone of the same area ratio.
#
# The exit angle is what decides the divergence loss, and it is the whole reason a bell exists: a
# cone leaves the wall at its half angle and a bell turns the flow back toward axial before the exit.
NOZZLE_CONTOURS = {
    'conical 15 degree': {
        'exitAngle': 15.0, 'lengthFraction': 1.00,
        'note': 'the classical reference. Simple to make and it throws away 1.7 per cent'},
    'bell 60 per cent': {
        'exitAngle': 14.0, 'lengthFraction': 0.60,
        'note': 'very short. The divergence loss creeps back and the drag loss falls'},
    'bell 80 per cent': {
        'exitAngle': 8.0, 'lengthFraction': 0.80,
        'note': 'the common design point. Most of the recovery for four fifths of the length'},
    'bell 100 per cent': {
        'exitAngle': 5.0, 'lengthFraction': 1.00,
        'note': 'diminishing returns. The last of the divergence loss costs the whole length back'},
}

# Altitude compensating arrangements, and the honest reason each is rare.
ALTITUDE_COMPENSATION = {
    'fixed bell': {
        'compensating': False, 'flownOperationally': True,
        'note': 'optimum at exactly one altitude, and the reference every other option is judged '
                'against'},
    'extendible': {
        'compensating': True, 'flownOperationally': True,
        'note': 'two area ratios, deployed once. Flown on upper stages, where the transition is '
                'a single event in vacuum'},
    'dual bell': {
        'compensating': True, 'flownOperationally': False,
        'note': 'two area ratios with a passive transition. The transition is unsteady and it has '
                'not flown'},
    'aerospike': {
        'compensating': True, 'flownOperationally': False,
        'note': 'continuously compensating and never operational. The cooling problem is the reason'},
}

# The loss mechanisms that make up the thrust coefficient efficiency. The propulsion hub carries a
# single Cf efficiency of 0.98; this is what it decomposes into.
#
# They multiply rather than add, and the divergence term is the only one a contour designer
# controls directly.
TYPICAL_BOUNDARY_LAYER_LOSS = 0.010    # [-]
TYPICAL_KINETIC_LOSS = 0.005    # [-]

# Schmucker's separation criterion, a refinement on Summerfield that makes the separation pressure
# depend on the pressure ratio rather than being a fixed fraction of ambient.
#
#     Pe / Pa  =  0.667 (Pc / Pa)^-0.2
#
# It is less conservative than Summerfield at high pressure ratio, which is where a launch vehicle
# nozzle actually lives, and the two disagree by enough to change a design.
SCHMUCKER_COEFFICIENT = 0.667    # [-]
SCHMUCKER_EXPONENT = -0.2    # [-]

def divergenceEfficiency(exitAngle: float) -> float:

    """

    Divergence loss from the wall angle at the exit.

        eta = (1 + cos alpha) / 2

    The transverse component of the exit momentum produces no axial thrust. A 15 degree cone
    throws away 1.7 per cent; an 80 per cent bell leaving at 8 degrees throws away 0.5.

    """

    if not 0.0 <= exitAngle < 90.0:
        raise ContourError(
            f'The exit angle must lie in [0, 90) degrees, got {exitAngle}.',
            context = createErrorContext(component = 'nozzleUtils'))

    return (1.0 + np.cos(np.radians(exitAngle))) / 2.0

def schmuckerSeparationPressure(chamberPressure: float, ambientPressure: float) -> float:

    """

    The exit pressure at which the flow separates, by Schmucker's criterion.

    Summerfield puts it at a fixed 0.4 of ambient. Schmucker makes it depend on the pressure ratio,
    which matters because a launch vehicle nozzle runs at pressure ratios of a hundred and Summerfield
    was fitted at rather less.

    """

    if chamberPressure <= 0.0 or ambientPressure <= 0.0:
        raise SeparationError(
            'Both pressures must be positive to evaluate a separation criterion.',
            context = createErrorContext(component = 'nozzleUtils'))

    ratio = SCHMUCKER_COEFFICIENT * (chamberPressure / ambientPressure) ** SCHMUCKER_EXPONENT

    return ratio * ambientPressure

def idealCompensatingAreaRatio(gamma: float, chamberPressure: float,
                               ambientPressure: float) -> float:

    """

    The area ratio that expands exactly to ambient, which is what a perfectly compensating nozzle
    would present at every altitude.

    It is the upper bound on what altitude compensation can be worth, and it is not achievable by
    any real device.

    """

    ratio = ambientPressure / chamberPressure

    if ratio >= 1.0:
        raise ContourError(
            f'The ambient pressure is at or above the chamber pressure, so there is no expansion '
            f'to compute.',
            context = createErrorContext(component = 'nozzleUtils'))

    # a nozzle cannot expand to less than its throat
    return max(areaRatioFromPressureRatio(gamma, min(ratio, 0.5)), 1.01)
