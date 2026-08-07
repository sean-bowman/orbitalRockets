
# -- Collection of commonly used functions [fluidSystems] -- #

'''

This utilities python file serves as the fluid-system function repository. Every component class in
this package pulls its fluid properties, unit conversions, friction factors, material data and error
types from here.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one flat
namespace and does not have to know whether a helper is fluid-specific or shared. What is defined
here is what is specific to fluid systems and belongs to no other domain.

Defined here:

--------------------------------------------------------------------------------------------------
Flow Functions
--------------------------------------------------------------------------------------------------
> reynoldsNumber
    >> Reynolds number from mass flow and hydraulic diameter
> frictionFactor
    >> Darcy friction factor by laminar, Colebrook, Churchill or Haaland
> criticalPressureRatio
    >> Pressure ratio at which a compressible flow chokes
> chokedMassFlux
    >> Choked (critical) mass flux for a compressible gas through a minimum area
> isentropicValues
    >> Static properties from stagnation properties and Mach number

--------------------------------------------------------------------------------------------------
Piping Code
--------------------------------------------------------------------------------------------------
> b31_3WallThickness
    >> ASME B31.3 straight-pipe pressure design thickness

--------------------------------------------------------------------------------------------------
Fluid System Errors
--------------------------------------------------------------------------------------------------
> FluidSystemError
    >> The domain base, an alias of the shared EngineeringError so the whole family stays catchable
> PressureDropError
    >> A pressure drop calculation produced a physically impossible result
> ChokedFlowError
    >> A flow choked where the calling analysis assumed it would not

Re-exported from orbitalRockets/common:

    units             every unit constant, convertPressureToAltitude, convertAltitudeToPressure
    fluidProperties   refWrap, coolWrap, hydrazineProps, fluidProps, speciesMolarMass,
                      leakRateConvert, convertToSCFM
    materials         materialProperties, roughnessTable
    structures        hoopStressCalculator
    solvers           secantSolve, solveForUnknown
    reporting         applyInputs, formatReportTable, writeFile, pickleObject
    errors            InvalidInputError, ConvergenceFailureError, CompatibilityError,
                      NumericalInstabilityError, createErrorContext

Author: Sean Bowman
Date:   01/24/2024

'''

import os
import sys
from typing import Any, Dict, Optional

import numpy as np

def _bootstrapCommon() -> None:

    '''

    Locate the orbitalRockets/common package and put it on sys.path.

    Walks up from this file until it finds a sibling directory named 'common', so it works from any
    nesting depth. fluidSystemsLibrary sits two levels below orbitalRockets; a testing library nested
    inside a domain sits three. Both resolve to the same package.

    This is the same sys.path approach NOVA and propulsionDesign already use, rather than requiring
    the whole tree to be installed or run as a package.

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
                      f'{os.path.abspath(__file__)}. Is this file still inside the orbitalRockets tree?')

_bootstrapCommon()

# Re-export the shared foundation. Every name below was previously defined in this file; keeping the
# namespace flat means no call site in the sixteen component modules had to change.
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
# -- Flow Functions -- #
#--------------------------------------------------------------------------------------------------------------------------#

def reynoldsNumber(massFlow: float, hydraulicDiameter: float, viscosity: float, flowArea: float = None) -> float:

    '''

    Reynolds number from a mass flow rate rather than a velocity.

    Re = rho * V * D / mu = (mdot / A) * D / mu

    Written in the mass-flow form because that is what a feed system analysis actually carries
    around: mass flow is conserved through the line, velocity is not (it changes with every density
    change), so anchoring on mdot avoids a density lookup at every station.

    If flowArea is not given, a circular cross section of diameter hydraulicDiameter is assumed.

    '''

    if flowArea is None:
        flowArea = np.pi * hydraulicDiameter**2 / 4.0

    return (massFlow / flowArea) * hydraulicDiameter / viscosity

def frictionFactor(reynolds: float, relativeRoughness: float = 0.0, method: str = 'churchill') -> float:

    '''

    Darcy-Weisbach friction factor.

    Note that this returns the DARCY friction factor, four times the Fanning friction factor. Half
    of all published pressure drop discrepancies trace to that factor of four, so every call site in
    this library uses Darcy and says so.

    ---------------------------------------------------------------------------
                                    INPUTS
    ---------------------------------------------------------------------------
    - reynolds            Reynolds number                                    [-]
    - relativeRoughness   Absolute roughness / diameter, eps/D               [-]
    - method              'churchill', 'colebrook', 'haaland', or 'laminar'

    ---------------------------------------------------------------------------
                                    METHODS
    ---------------------------------------------------------------------------
    'churchill'  Churchill (1977). Single expression valid across laminar, transition and turbulent
                 regimes with no branching, which makes it the right default for any solver that
                 might march a line through the transition region. Matches Colebrook to within about
                 1 % in the fully turbulent regime.

    'colebrook'  Colebrook-White, solved iteratively by fixed-point iteration. The reference
                 turbulent correlation and the basis of the Moody diagram. Laminar below Re = 2300.

    'haaland'    Haaland (1983) explicit approximation to Colebrook, within about 2 %. Cheap, and
                 the right choice inside a hot loop where the extra accuracy does not matter.

    'laminar'    Force 64/Re regardless of Reynolds number. Useful for capillary and leak-path work
                 where the flow is laminar by construction.

    ---------------------------------------------------------------------------
                            A NOTE ON THE TRANSITION REGION
    ---------------------------------------------------------------------------
    Between Re = 2300 and Re = 4000 the friction factor is not a well-defined function of Reynolds
    number: it depends on inlet conditions, vibration and upstream disturbances. Any correlation
    here is a smooth interpolation through a physically unsteady region. Size hardware so that the
    operating point is not in it, and if it must be, carry the uncertainty explicitly.

    '''

    methodKey = method.strip().lower()

    # Guard against the zero-flow case that shows up when a solver initializes at rest
    if reynolds <= 0.0:
        return 0.0

    if methodKey == 'laminar':
        return 64.0 / reynolds

    if methodKey == 'churchill':
        # Churchill (1977), Chemical Engineering 84(24), pp. 91-92
        termA = (-2.457 * np.log((7.0 / reynolds)**0.9 + 0.27 * relativeRoughness))**16
        termB = (37530.0 / reynolds)**16
        return 8.0 * ((8.0 / reynolds)**12 + 1.0 / (termA + termB)**1.5)**(1.0 / 12.0)

    if methodKey == 'haaland':
        if reynolds < 2300.0:
            return 64.0 / reynolds
        return (-1.8 * np.log10((relativeRoughness / 3.7)**1.11 + 6.9 / reynolds))**-2.0

    if methodKey == 'colebrook':
        if reynolds < 2300.0:
            return 64.0 / reynolds
        # Fixed-point iteration on 1/sqrt(f). Converges in a handful of passes from the Haaland seed.
        inverseRootF = -1.8 * np.log10((relativeRoughness / 3.7)**1.11 + 6.9 / reynolds)
        for _ in range(50):
            previous     = inverseRootF
            inverseRootF = -2.0 * np.log10(relativeRoughness / 3.7 + 2.51 * inverseRootF / reynolds)
            if abs(inverseRootF - previous) < 1.0e-10:
                break
        return inverseRootF**-2.0

    raise KeyError(f'frictionFactor does not recognize method \'{method}\'. Use churchill, colebrook, haaland or laminar.')

def criticalPressureRatio(gamma: float) -> float:

    '''

    Ratio of downstream static pressure to upstream stagnation pressure at which a compressible flow
    chokes, P* / P0 = (2 / (gamma + 1))^(gamma / (gamma - 1)).

    For diatomic gases (gamma = 1.4) this is 0.528, which is the number to keep in your head: a GN2
    or GHe line vented to atmosphere is choked at anything above about 2 atm absolute upstream.

    '''

    return (2.0 / (gamma + 1.0))**(gamma / (gamma - 1.0))

def chokedMassFlux(stagnationPressure: float, stagnationTemperature: float, gamma: float, gasConstant: float) -> float:

    '''

    Choked (critical) mass flux [kg/s-m^2] through a minimum area.

    G* = P0 * sqrt(gamma / (R * T0)) * (2 / (gamma + 1))^((gamma + 1) / (2 * (gamma - 1)))

    Multiply by the minimum flow area and a discharge coefficient to get mass flow. This is the
    workhorse behind orifice, valve and relief device sizing on the gas side, and it is the reason
    choked components are such useful flow control elements: once choked, the mass flow depends only
    on upstream conditions and is completely insensitive to whatever happens downstream.

    gasConstant is the SPECIFIC gas constant [J/kg-K], R_universal / molarMass.

    '''

    return stagnationPressure * np.sqrt(gamma / (gasConstant * stagnationTemperature)) * (2.0 / (gamma + 1.0))**((gamma + 1.0) / (2.0 * (gamma - 1.0)))

def isentropicValues(machNumber: ArrayLike, stagnationTemperature: ArrayLike, stagnationPressure: ArrayLike, gamma: ArrayLike, gasConstant: ArrayLike) -> tuple:

    '''

    Returns (in this order):
    - Temperature
    - Pressure
    - Velocity

    Calculate resultant static values via isentropic relations given the flow Mach number and
    stagnation values of temperature and pressure as well as flow gamma and specific gas constant.

    '''

    temperature = stagnationTemperature / (1 + ((gamma - 1) / 2) * machNumber**2)
    pressure    = stagnationPressure    / (1 + ((gamma - 1) / 2) * machNumber**2)**(gamma / (gamma - 1))
    velocity    = np.sqrt(gamma * gasConstant * temperature) * machNumber

    return temperature, pressure, velocity

#--------------------------------------------------------------------------------------------------------------------------#
# -- Piping Code -- #
#--------------------------------------------------------------------------------------------------------------------------#

def b31_3WallThickness(designPressure: float, outerDiameter: float, allowableStress: float, jointEfficiency: float = 1.0, weldStrengthFactor: float = 1.0, coefficientY: float = 0.4, corrosionAllowance: float = 0.0, millTolerance: float = 0.125) -> dict:

    '''

    ASME B31.3 straight-pipe pressure design thickness.

    t = P * D / (2 * (S * E * W + P * Y))

    then the ordered thickness is t plus mechanical allowances, divided by (1 - millTolerance) to
    cover the wall thickness tolerance the mill is allowed to ship against.

    ---------------------------------------------------------------------------
                                    INPUTS
    ---------------------------------------------------------------------------
    - designPressure       Internal design gauge pressure                    [Pa]
    - outerDiameter        Pipe or tube OD                                    [m]
    - allowableStress      Basic allowable stress S at design temperature    [Pa]
    - jointEfficiency      Longitudinal weld joint quality factor E           [-]
                           1.00 seamless, 0.85 ERW, 0.80 furnace butt weld
    - weldStrengthFactor   Weld joint strength reduction factor W             [-]
                           1.00 below the creep range
    - coefficientY         Table 304.1.1 coefficient                          [-]
                           0.4 for ferritic and austenitic steels below 900 degF
    - corrosionAllowance   Mechanical, corrosion and erosion allowance        [m]
    - millTolerance        Fractional wall thickness under-tolerance          [-]
                           0.125 for seamless pipe, 0.10 for most tube

    ---------------------------------------------------------------------------
                                    OUTPUTS
    ---------------------------------------------------------------------------
    Dictionary with 'pressureDesignThickness', 'minimumThickness', 'orderedThickness' [m].

    Note what this does and does not cover. B31.3 pressure design thickness is a hoop stress check
    only. It says nothing about external pressure (vacuum jacket collapse), bending from thermal
    growth or support spacing, fatigue from pressure cycling, or the handling loads that actually
    set the minimum wall on small-bore tubing. On a flight vehicle, AIAA S-080 and S-081 factors of
    safety usually govern instead; B31.3 governs the ground half of the system.

    '''

    pressureDesignThickness = (designPressure * outerDiameter) / (2.0 * (allowableStress * jointEfficiency * weldStrengthFactor + designPressure * coefficientY))
    minimumThickness        = pressureDesignThickness + corrosionAllowance
    orderedThickness        = minimumThickness / (1.0 - millTolerance)

    return {
        'pressureDesignThickness': pressureDesignThickness,
        'minimumThickness':        minimumThickness,
        'orderedThickness':        orderedThickness
    }

#--------------------------------------------------------------------------------------------------------------------------#
# -- Fluid System Error Handling -- #
#--------------------------------------------------------------------------------------------------------------------------#

# FluidSystemError is an alias rather than a subclass so that the existing public name, and every
# existing `except FluidSystemError` and `issubclass(InvalidInputError, FluidSystemError)`, keep
# meaning exactly what they meant before the shared package existed.
#
# It is deliberately NOT given its own domainLabel. Setting one would mutate the shared
# EngineeringError class attribute, so whichever domain imported last would silently relabel every
# other domain's errors in the same process. The domain a failure came from is already carried in the
# error context (component, fluid, and the state values), which is where it belongs.
FluidSystemError = EngineeringError

class PressureDropError(EngineeringError):

    '''

    Exception raised when a pressure drop calculation produces a physically impossible result.

    Most often this means the requested mass flow cannot pass through the given geometry at the
    available pressure: the computed downstream pressure has gone below absolute zero, or below the
    vapor pressure by so much that the single-phase assumption is meaningless.

    '''

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 upstreamPressure: Optional[float] = None, downstreamPressure: Optional[float] = None,
                 pressureDrop: Optional[float] = None):

        if context is None:
            context = {}

        if upstreamPressure is not None:
            context['upstreamPressure'] = upstreamPressure
        if downstreamPressure is not None:
            context['downstreamPressure'] = downstreamPressure
        if pressureDrop is not None:
            context['pressureDrop'] = pressureDrop

        super().__init__(message, context)

class ChokedFlowError(EngineeringError):

    '''

    Exception raised when a flow chokes where the calling analysis assumed it would not, or when a
    choked-flow relation is applied to a flow that is not actually choked.

    This is its own error type rather than a generic input error because choking is the single most
    common way a fluid system model silently gives the wrong answer: an unchoked correlation applied
    past the critical pressure ratio will happily return a mass flow that the hardware cannot pass.

    '''

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 pressureRatio: Optional[float] = None, criticalRatio: Optional[float] = None):

        if context is None:
            context = {}

        if pressureRatio is not None:
            context['pressureRatio'] = pressureRatio
        if criticalRatio is not None:
            context['criticalPressureRatio'] = criticalRatio

        super().__init__(message, context)
