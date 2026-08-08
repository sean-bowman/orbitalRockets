
# -- Domain-specific helpers [thermalManagement] -- #

'''

Resistance forms, dimensionless groups and the property tables this domain runs on.

Named thermalUtils rather than utils deliberately. Every domain library in this repository has a
utils.py re-exporting the shared foundation, and they all resolve to the same 'utils' entry in
sys.modules when more than one domain is imported in a single process. That works by accident for
the names every domain re-exports and fails for anything only one domain defines.

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

from units import *
from fluidProperties import *
from materials import *
from structures import *
from solvers import *
from reporting import *
from errors import *

ArrayLike = np.ndarray | list | float | int

ThermalManagementError = EngineeringError

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

STEFAN_BOLTZMANN = 5.670374419e-8    # [W/m^2/K^4]

# Lumped capacitance is valid below this Biot number. Above it the internal temperature gradient
# matters and a single-node representation understates the surface temperature.
LUMPED_CAPACITANCE_BIOT_LIMIT = 0.1    # [-]

# Contact conductance across a mechanical joint, which is almost always the dominant resistance in
# a bolted thermal path and almost always the least well known number in the model.
CONTACT_CONDUCTANCE = {
    'bolted, bare, vacuum':      {'value': 500.0,   'note': 'the common case, and very variable'},
    'bolted, bare, air':         {'value': 2000.0,  'note': 'trapped air conducts across the gap'},
    'bolted, with grease':       {'value': 8000.0,  'note': 'thermal grease fills the asperities'},
    'bolted, with indium foil':  {'value': 20000.0, 'note': 'soft metal foil, the good option'},
    'bonded, thermally filled':  {'value': 5000.0,  'note': 'filled adhesive'},
    'welded or integral':        {'value': 1.0e6,   'note': 'effectively no interface'},
    'deliberate isolator':       {'value': 50.0,    'note': 'a designed thermal break'},
}

# Surface optical properties, shared in intent with environmentsAndLoads. Stated independently
# rather than imported, because the two domains must not depend on each other's internals, and a
# drift test asserts the shared entries agree.
SURFACE_PROPERTIES = {
    'white paint':             {'absorptivity': 0.20, 'emissivity': 0.88},
    'black paint':             {'absorptivity': 0.95, 'emissivity': 0.88},
    'bare aluminium':          {'absorptivity': 0.15, 'emissivity': 0.05},
    'aluminised kapton':       {'absorptivity': 0.40, 'emissivity': 0.80},
    'optical solar reflector': {'absorptivity': 0.08, 'emissivity': 0.80},
    'gold':                    {'absorptivity': 0.30, 'emissivity': 0.03},
}

# Ablative materials. The effective heat of ablation lumps pyrolysis, char formation, blowing and
# surface removal into one number, which is a coarse but genuinely useful engineering treatment.
ABLATIVE_MATERIALS = {
    'silica phenolic':   {'heatOfAblation': 1.16e7, 'density': 1730.0, 'charDensity': 1200.0,
                          'charConductivity': 1.0, 'virginConductivity': 0.55,
                          'specificHeat': 1260.0, 'surfaceTemperature': 2800.0,
                          'note': 'the workhorse. Well characterised, moderate performance'},
    'carbon phenolic':   {'heatOfAblation': 2.10e7, 'density': 1450.0, 'charDensity': 1300.0,
                          'charConductivity': 4.0, 'virginConductivity': 0.60,
                          'specificHeat': 1300.0, 'surfaceTemperature': 3600.0,
                          'note': 'high performance, high conductivity char, expensive'},
    'PICA':              {'heatOfAblation': 2.60e7, 'density': 270.0, 'charDensity': 220.0,
                          'charConductivity': 0.30, 'virginConductivity': 0.13,
                          'specificHeat': 1600.0, 'surfaceTemperature': 3000.0,
                          'note': 'very low density, the modern entry choice'},
    'cork':              {'heatOfAblation': 6.50e6, 'density': 480.0, 'charDensity': 350.0,
                          'charConductivity': 0.12, 'virginConductivity': 0.07,
                          'specificHeat': 1900.0, 'surfaceTemperature': 1000.0,
                          'note': 'ascent heating only. Cheap, and it works'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Resistances -- #
# ------------------------------------------------------------------------------------------------ #

def conductionResistance(length: float, conductivity: float, area: float) -> float:

    '''

    Plane wall conduction resistance, L / (k A).

    '''

    if length < 0.0:
        raise InvalidInputError('Conduction path length cannot be negative.',
                                context = createErrorContext(component = 'thermalManagement'))

    if conductivity <= 0.0 or area <= 0.0:
        raise InvalidInputError('Conductivity and area must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    return length / (conductivity * area)

def contactResistance(area: float, jointType: str = 'bolted, bare, vacuum',
                      conductance: float = None) -> float:

    '''

    Interface resistance across a mechanical joint, 1 / (h_c A).

    Contact conductance is almost always the dominant resistance in a bolted thermal path and
    almost always the least well known number in the model. The spread across the table below is a
    factor of forty, which is larger than the uncertainty in anything else in a typical network.

    '''

    if area <= 0.0:
        raise InvalidInputError('Contact area must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    if conductance is None:
        if jointType not in CONTACT_CONDUCTANCE:
            raise InvalidInputError(
                f'Unknown joint type \'{jointType}\'. Known: {sorted(CONTACT_CONDUCTANCE)}.',
                context = createErrorContext(component = 'thermalManagement'))
        conductance = CONTACT_CONDUCTANCE[jointType]['value']

    if conductance <= 0.0:
        raise InvalidInputError('Contact conductance must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    return 1.0 / (conductance * area)

def convectionResistance(coefficient: float, area: float) -> float:

    '''

    Convective resistance, 1 / (h A).

    '''

    if coefficient <= 0.0 or area <= 0.0:
        raise InvalidInputError('Film coefficient and area must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    return 1.0 / (coefficient * area)

def radiationResistance(emissivity: float, area: float,
                        hotTemperature: float, coldTemperature: float) -> float:

    '''

    Linearised radiation resistance about the current temperature pair.

        h_r = eps sigma (T_h + T_c)(T_h^2 + T_c^2)

    Radiation is not linear, so this resistance is only valid near the temperatures it was
    evaluated at. In a transient solve it has to be re-evaluated as the temperatures move, which is
    why a radiation-dominated network needs iteration where a conduction one does not.

    '''

    if emissivity <= 0.0 or emissivity > 1.0:
        raise InvalidInputError(f'Emissivity must be in (0, 1], got {emissivity}.',
                                context = createErrorContext(component = 'thermalManagement'))

    if area <= 0.0:
        raise InvalidInputError('Radiating area must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    if hotTemperature <= 0.0 or coldTemperature <= 0.0:
        raise InvalidInputError('Temperatures must be absolute and positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    coefficient = (emissivity * STEFAN_BOLTZMANN
                   * (hotTemperature + coldTemperature)
                   * (hotTemperature ** 2 + coldTemperature ** 2))

    return 1.0 / (coefficient * area)

# ------------------------------------------------------------------------------------------------ #
# -- Dimensionless Groups -- #
# ------------------------------------------------------------------------------------------------ #

def biotNumber(coefficient: float, characteristicLength: float, conductivity: float) -> float:

    '''

    Bi = h L / k, the ratio of internal conduction resistance to surface resistance.

    Below 0.1 a body is close to isothermal internally and a lumped capacitance treatment is
    adequate. Above it there is a real internal gradient, and a single-node model understates the
    surface temperature, which is the direction that matters for a heat shield.

    '''

    if conductivity <= 0.0:
        raise InvalidInputError('Conductivity must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    return coefficient * characteristicLength / conductivity

def fourierNumber(diffusivity: float, time: float, characteristicLength: float) -> float:

    '''

    Fo = alpha t / L^2, dimensionless time for transient conduction.

    Fourier number of order one is the timescale on which a body responds. Below about 0.05 the
    thermal wave has not reached the far side and the body behaves as semi-infinite.

    '''

    if characteristicLength <= 0.0:
        raise InvalidInputError('Characteristic length must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    return diffusivity * time / characteristicLength ** 2

def thermalDiffusivity(conductivity: float, density: float, specificHeat: float) -> float:

    '''

    alpha = k / (rho cp), how fast a temperature disturbance propagates.

    '''

    if density <= 0.0 or specificHeat <= 0.0:
        raise InvalidInputError('Density and specific heat must be positive.',
                                context = createErrorContext(component = 'thermalManagement'))

    return conductivity / (density * specificHeat)

def thermalPenetrationDepth(diffusivity: float, time: float) -> float:

    '''

    An estimate of how far a thermal disturbance has propagated, roughly sqrt(alpha t).

    Useful for deciding whether a structure behaves as semi-infinite over the duration of an event.
    A short heat pulse into a thick wall never reaches the back face, which is why an ascent heat
    pulse and a soak at the same temperature are entirely different problems.

    '''

    if time < 0.0:
        raise InvalidInputError('Time cannot be negative.',
                                context = createErrorContext(component = 'thermalManagement'))

    return np.sqrt(max(diffusivity, 0.0) * time)

# ------------------------------------------------------------------------------------------------ #
# -- Domain Error Types -- #
# ------------------------------------------------------------------------------------------------ #

class ThermalNetworkError(ThermalManagementError):

    '''
    Raised when a thermal network is malformed, unsolvable or unconverged.
    '''

    pass

class AblationError(ThermalManagementError):

    '''
    Raised when an ablation calculation is asked for outside the range its correlation covers.
    '''

    pass
