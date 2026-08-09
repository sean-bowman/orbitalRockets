# -- Domain-specific helpers [combustionDevices] -- #

'''

Injector element sizing, chamber volume, combustion stability and regenerative cooling.

Named combustionUtils rather than utils. Every domain library in this repository has a utils.py
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
# -- combustionDevices Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
CombustionDevicesError = EngineeringError

class InjectorError(CombustionDevicesError):
    """
    An injector geometry that cannot deliver the flow, or a stiffness outside the range the
    correlations and the stability experience apply to.
    """

class StabilityError(CombustionDevicesError):
    """
    A stability calculation asked for something outside its basis: a mode index that is not
    tabulated, or a chamber whose geometry puts it outside the acoustic model.
    """

class CoolingError(CombustionDevicesError):
    """
    A cooling circuit that cannot close. A wall temperature above the material limit, a coolant
    that boils, or a channel whose pressure drop exceeds the available head.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The propellant combination table lives in the propulsion hub. Importing it here rather than
# duplicating it keeps one definition of what LOX/RP-1 is, and the direction of the dependency is
# correct: a sub-domain may depend on its hub, and the hub must not depend on a sub-domain.
_HUB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'propulsionLibrary')

if _HUB not in sys.path:
    sys.path.insert(0, _HUB)

from propulsionUtils import (PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH,
                             vandenkerckhove, characteristicVelocity)

# Injector element types, with the pressure drop coefficient and the character each one has. The
# discharge coefficient is the orifice one; the mixing quality is a relative figure on a scale where
# 1.0 is a well developed unlike-impinging doublet, and it exists to rank rather than to predict.
#
# The wall compatibility column is the one that gets people. An element that mixes well produces a
# hot core, and an element that mixes well NEXT TO THE WALL produces a hot wall. Nearly every engine
# runs a deliberately different element pattern in the outer row for this reason, and the c*
# efficiency lost there is the price of not burning through.
INJECTOR_ELEMENTS = {
    'like-on-like doublet': {
        'dischargeCoefficient': 0.75, 'mixingQuality': 0.85, 'wallCompatible': True,
        'note': 'each propellant impinges on itself. Poor mixing, very forgiving of the wall'},
    'unlike impinging doublet': {
        'dischargeCoefficient': 0.80, 'mixingQuality': 1.00, 'wallCompatible': False,
        'note': 'the workhorse. Good mixing, and it will find the wall if you let it'},
    'unlike impinging triplet': {
        'dischargeCoefficient': 0.78, 'mixingQuality': 1.10, 'wallCompatible': False,
        'note': 'two oxidiser on one fuel. Better mixing again, and less tolerant still'},
    'coaxial shear': {
        'dischargeCoefficient': 0.85, 'mixingQuality': 0.90, 'wallCompatible': True,
        'note': 'the cryogenic standard. Needs a large velocity ratio to atomise'},
    'coaxial swirl': {
        'dischargeCoefficient': 0.70, 'mixingQuality': 1.05, 'wallCompatible': True,
        'note': 'swirl atomises at lower velocity ratio. More pressure drop for it'},
    'pintle': {
        'dischargeCoefficient': 0.80, 'mixingQuality': 0.95, 'wallCompatible': True,
        'note': 'one element, variable area, inherently deep throttling and inherently stable'},
}

# Transverse and radial acoustic mode eigenvalues for a cylinder: the roots of the derivative of
# the Bessel function of the first kind. The mode frequency is alpha c / (pi D).
#
# The first tangential mode is the one that destroys engines. It is the lowest transverse mode, it
# couples readily with the injection process, and it produces a pressure wave sweeping around the
# chamber circumference at a frequency in the low thousands of hertz for a typical chamber.
CHAMBER_ACOUSTIC_MODES = {
    '1T':   {'eigenvalue': 1.8412, 'note': 'first tangential. The one that destroys engines'},
    '2T':   {'eigenvalue': 3.0542, 'note': 'second tangential'},
    '1R':   {'eigenvalue': 3.8317, 'note': 'first radial. Baffles do not suppress it'},
    '1T1R': {'eigenvalue': 5.3314, 'note': 'combined first tangential and first radial'},
    '3T':   {'eigenvalue': 4.2012, 'note': 'third tangential'},
}

# Injector stiffness, the ratio of injector pressure drop to chamber pressure. Below the lower bound
# the feed system and the chamber couple strongly enough to sustain a chug oscillation; above the
# upper bound the pressure drop is being paid for with pump work that buys nothing.
#
# The band is experience rather than theory. Chug is a system instability involving the feed line
# inertance and the chamber volume as well as the injector, so no single ratio is a sufficient
# criterion, and this one is the necessary part of it that is easy to check.
CHUG_STIFFNESS_FLOOR = 0.05    # [-]
RECOMMENDED_STIFFNESS_LOWER = 0.15    # [-]
RECOMMENDED_STIFFNESS_UPPER = 0.25    # [-]

# Prandtl number for combustion products, from the specific heat ratio. An algebraic estimate that
# is adequate for a heat transfer correlation whose own scatter is larger than its error.
def combustionPrandtl(gamma: float) -> float:

    """
    Prandtl number of the combustion products, 4 gamma / (9 gamma - 5).
    """

    return 4.0 * gamma / (9.0 * gamma - 5.0)

def combustionViscosity(molarMass: float, temperature: float) -> float:

    """

    Dynamic viscosity of the combustion products in Pa s.

    The standard rocket correlation, mu = 1.184e-7 M^0.5 T^0.6, with molar mass in g/mol. It is a
    curve fit across the species a hydrocarbon or hydrogen flame produces and it is good to
    perhaps ten per cent, which is well inside the scatter of the Bartz correlation it feeds.

    """

    if molarMass <= 0.0 or temperature <= 0.0:
        raise CoolingError(
            f'Molar mass and temperature must be positive, got {molarMass} and {temperature}.',
            context = createErrorContext(component = 'combustionUtils'))

    return 1.184e-7 * np.sqrt(molarMass) * temperature ** 0.6

def combustionGasProperties(combination: str) -> dict:

    """

    The gas-side properties the Bartz correlation needs, derived from the propellant table.

    Everything here follows from gamma, molar mass and chamber temperature, so there is one source
    for what a propellant is and no opportunity for this sub-domain to disagree with its hub.

    """

    if combination not in PROPELLANT_COMBINATIONS:
        raise CoolingError(
            f'Unknown propellant combination \'{combination}\'. '
            f'Known: {sorted(PROPELLANT_COMBINATIONS)}.',
            context = createErrorContext(component = 'combustionUtils'))

    entry = PROPELLANT_COMBINATIONS[combination]

    gamma       = entry['gamma']
    molarMass   = entry['molarMass']
    temperature = entry['chamberTemperature']

    specificGasConstant = R_UNIVERSAL * 1000.0 / molarMass
    specificHeat        = gamma * specificGasConstant / (gamma - 1.0)

    return {'gamma':               gamma,
            'molarMass':           molarMass,
            'chamberTemperature':  temperature,
            'specificGasConstant': specificGasConstant,
            'specificHeat':        specificHeat,
            'viscosity':           combustionViscosity(molarMass, temperature),
            'prandtl':             combustionPrandtl(gamma),
            'characteristicVelocity': entry['referenceCstar']}

def bartzCoefficient(throatDiameter: float, curvatureRadius: float, chamberPressure: float,
                     characteristicVelocity: float, areaRatioToThroat: float,
                     wallTemperature: float, gasProperties: dict) -> dict:

    """

    Gas-side heat transfer coefficient from the Bartz correlation.

        h_g = (0.026 / Dt^0.2) (mu^0.2 cp / Pr^0.6) (Pc / c*)^0.8 (Dt / Rc)^0.1 (At / A)^0.9 sigma

    `areaRatioToThroat` is the local area over the throat area, so it is 1 at the throat and larger
    everywhere else. The 0.9 exponent on its reciprocal is why the throat carries the peak flux by
    such a margin: at an area ratio of 4 the coefficient has already fallen by a factor of 3.5.

    `sigma` is the property variation correction, which accounts for the boundary layer being far
    colder than the free stream. It depends on the wall temperature, so the correlation is
    implicit in wall temperature and has to be iterated if the wall is not known.

    Bartz is a 1957 correlation with real scatter, quoted at plus or minus twenty per cent and
    worse in the convergent section. It is used because nothing appreciably better exists that
    needs no more information, and because engines designed with it work.

    """

    for name, value in (('throat diameter', throatDiameter),
                        ('curvature radius', curvatureRadius),
                        ('chamber pressure', chamberPressure),
                        ('characteristic velocity', characteristicVelocity),
                        ('wall temperature', wallTemperature)):
        if value <= 0.0:
            raise CoolingError(f'The {name} must be positive, got {value}.',
                               context = createErrorContext(component = 'combustionUtils'))

    if areaRatioToThroat < 1.0:
        raise CoolingError(
            f'The local area ratio must be at least one, got {areaRatioToThroat}. It is the local '
            f'area over the throat area, so the throat is one and everywhere else is larger.',
            context = createErrorContext(component = 'combustionUtils'))

    gamma     = gasProperties['gamma']
    viscosity = gasProperties['viscosity']
    heat      = gasProperties['specificHeat']
    prandtl   = gasProperties['prandtl']
    chamber   = gasProperties['chamberTemperature']

    machNumber = _machFromAreaRatio(gamma, areaRatioToThroat)

    stagnationRatio = 1.0 + (gamma - 1.0) / 2.0 * machNumber ** 2

    correction = 1.0 / ((0.5 * (wallTemperature / chamber) * stagnationRatio + 0.5) ** 0.68
                        * stagnationRatio ** 0.12)

    coefficient = ((0.026 / throatDiameter ** 0.2)
                   * (viscosity ** 0.2 * heat / prandtl ** 0.6)
                   * (chamberPressure / characteristicVelocity) ** 0.8
                   * (throatDiameter / curvatureRadius) ** 0.1
                   * (1.0 / areaRatioToThroat) ** 0.9
                   * correction)

    # adiabatic wall temperature, with the recovery factor for a turbulent boundary layer
    recovery      = prandtl ** (1.0 / 3.0)
    staticRatio   = 1.0 + recovery * (gamma - 1.0) / 2.0 * machNumber ** 2
    adiabaticWall = chamber * staticRatio / stagnationRatio

    return {'coefficient':             coefficient,
            'machNumber':              machNumber,
            'adiabaticWallTemperature': adiabaticWall,
            'correction':              correction,
            'heatFlux':                coefficient * (adiabaticWall - wallTemperature)}

def _machFromAreaRatio(gamma: float, areaRatio: float, supersonic: bool = False) -> float:

    """

    Mach number from the local area ratio, on the requested branch.

    The chamber and convergent section are subsonic and the divergent section is supersonic, and
    the same area ratio corresponds to one of each. The default is the subsonic branch, because the
    peak heat flux is at the throat and the chamber side is where the cooling circuit is sized.

    """

    if areaRatio <= 1.0 + 1.0e-12:
        return 1.0

    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))

    def relation(mach: float) -> float:
        return (1.0 / mach
                * ((2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * mach ** 2)) ** exponent
                - areaRatio)

    lower, upper = (1.0, 50.0) if supersonic else (1.0e-6, 1.0)

    for _ in range(200):
        middle = 0.5 * (lower + upper)
        if relation(lower) * relation(middle) <= 0.0:
            upper = middle
        else:
            lower = middle
        if upper - lower < 1.0e-12:
            break

    return 0.5 * (lower + upper)
