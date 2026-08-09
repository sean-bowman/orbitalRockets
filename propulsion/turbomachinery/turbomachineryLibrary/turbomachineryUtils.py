# -- Domain-specific helpers [turbomachinery] -- #

'''

Pump and turbine sizing, cavitation, inducers, and the shaft that connects them.

Named turbomachineryUtils rather than utils. Every domain library in this repository has a utils.py
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
# -- turbomachinery Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
TurbomachineryError = EngineeringError

class PumpError(TurbomachineryError):
    """
    A pump duty that cannot be met, or one asked to operate outside the range the correlations
    apply to.
    """

class CavitationError(TurbomachineryError):
    """
    A suction condition that cavitates, or a suction specific speed beyond what an inducer can
    deliver.
    """

class TurbineError(TurbomachineryError):
    """
    A turbine that cannot deliver the power the pump needs, or one outside its blade speed or
    temperature limits.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The propellant table lives in the propulsion hub. Importing rather than duplicating keeps one
# definition of what LOX/RP-1 is, and the dependency direction is correct: a sub-domain may depend
# on its hub and the hub must not depend on a sub-domain.
_HUB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'propulsionLibrary')

if _HUB not in sys.path:
    sys.path.insert(0, _HUB)

from propulsionUtils import PROPELLANT_COMBINATIONS

# Specific speed sorts pump geometry, and it is the first number to compute because it decides what
# kind of machine you are building before any dimension exists.
#
# The dimensionless form is used throughout. The literature is overwhelmingly in US customary
# specific speed, N[rpm] sqrt(Q[gpm]) / H[ft]^0.75, so the conversion is provided and every reported
# value carries both.
US_SPECIFIC_SPEED_PER_DIMENSIONLESS = 2733.0    # [-]

# Pump geometry by dimensionless specific speed. Rocket pumps sit at the low end of this range and
# frequently below it, because the head is enormous and the flow is not.
PUMP_GEOMETRY = {
    'radial':       {'lower': 0.20, 'upper': 0.80,
                     'note': 'high head, low flow. Where nearly every rocket pump sits'},
    'mixed flow':   {'lower': 0.80, 'upper': 2.20,
                     'note': 'the middle ground'},
    'axial':        {'lower': 2.20, 'upper': 5.50,
                     'note': 'high flow, low head. Rare on a rocket except as an inducer'},
}

# Head coefficient, psi = g H / U^2, where U is the impeller tip speed. It is bounded above by the
# blade turning the flow can achieve and below by nothing useful, and it is what converts a required
# head into a required tip speed.
#
# A backswept centrifugal impeller reaches 0.45 to 0.60. Above that the blade loading is
# impractical, which is why a large head becomes multiple stages rather than one bigger wheel.
HEAD_COEFFICIENT = {'lower': 0.45, 'typical': 0.55, 'upper': 0.60}    # [-]

# Suction specific speed bounds cavitation performance. Without an inducer a centrifugal pump is
# limited to roughly 3 dimensionless, and an inducer buys a factor of four to eight.
#
# This is the number that decides shaft speed from above, and therefore the number that decides
# tank pressure, and therefore a real fraction of the vehicle's dry mass. It is the most
# consequential parameter in this sub-domain.
SUCTION_SPECIFIC_SPEED = {
    'no inducer':        {'limit': 3.0,  'note': 'a bare centrifugal impeller'},
    'inducer':           {'limit': 12.0, 'note': 'the standard arrangement'},
    'high performance inducer': {'limit': 20.0,
                                 'note': 'achievable and it accepts partial cavitation by design'},
}    # [-]

# Turbine blade speed ratio, U / C0, where C0 is the isentropic spouting velocity. Efficiency peaks
# at a value set by the stage type, and rocket turbines are usually forced well below the optimum
# because the shaft speed is set by the pump rather than by the turbine.
#
# That compromise is the defining characteristic of a rocket turbine and it is why their
# efficiencies look poor next to industrial practice.
BLADE_SPEED_RATIO_OPTIMUM = {
    'impulse':          {'optimum': 0.50, 'note': 'single stage impulse. The rocket default'},
    'two row velocity': {'optimum': 0.25, 'note': 'velocity compounded, for very high pressure ratio'},
    'reaction':         {'optimum': 0.70, 'note': 'fifty per cent reaction. Needs a fast shaft'},
}

# Turbine inlet temperature limits, which are a materials problem rather than an aerodynamic one.
# Uncooled superalloy blading is the norm on a rocket turbine because the run time is short.
TURBINE_INLET_LIMITS = {
    'uncooled superalloy': {'limit': 1150.0, 'note': 'the usual rocket case, short run time'},
    'cooled superalloy':   {'limit': 1500.0, 'note': 'cooling costs flow and complexity'},
    'expander cycle':      {'limit': 600.0,  'note': 'limited by what the coolant picked up'},
}    # [K]

# Bearing DN number, bore diameter in millimetres times shaft speed in rpm. It is the classical
# bearing limit and it bounds shaft speed from above alongside cavitation.
BEARING_DN_LIMIT = 2.0e6    # [mm rpm]

# ------------------------------------------------------------------------------------------------ #
# -- Similarity groups -- #
# ------------------------------------------------------------------------------------------------ #

def specificSpeed(shaftSpeed: float, volumetricFlow: float, head: float) -> float:

    """

    Dimensionless specific speed, omega sqrt(Q) / (g H)^0.75.

    `shaftSpeed` is in rad/s, `volumetricFlow` in m^3/s and `head` in metres.

    It is a shape parameter and not a performance one. Two pumps with the same specific speed have
    geometrically similar impellers regardless of size, fluid or speed, which is what makes it the
    first number to compute.

    """

    for name, value in (('shaft speed', shaftSpeed), ('volumetric flow', volumetricFlow),
                        ('head', head)):
        if value <= 0.0:
            raise PumpError(f'The {name} must be positive, got {value}.',
                            context = createErrorContext(component = 'turbomachineryUtils'))

    return shaftSpeed * np.sqrt(volumetricFlow) / (GRAVITY * head) ** 0.75

def suctionSpecificSpeed(shaftSpeed: float, volumetricFlow: float,
                         netPositiveSuctionHead: float) -> float:

    """

    Dimensionless suction specific speed, omega sqrt(Q) / (g NPSH)^0.75.

    The same group as specific speed with the available suction head in place of the developed
    head. It measures how hard the inlet is working rather than how hard the pump is, and it is
    what bounds shaft speed from above.

    """

    if netPositiveSuctionHead <= 0.0:
        raise CavitationError(
            f'The net positive suction head must be positive, got {netPositiveSuctionHead}. A '
            f'non-positive NPSH is a pump inlet below the vapour pressure, which is not a '
            f'cavitation margin, it is a vapour lock.',
            context = createErrorContext(component = 'turbomachineryUtils'))

    return specificSpeed(shaftSpeed, volumetricFlow, netPositiveSuctionHead)

def toUsSpecificSpeed(dimensionless: float) -> float:

    """
    Convert a dimensionless specific speed to the US customary form the literature uses.
    """

    return dimensionless * US_SPECIFIC_SPEED_PER_DIMENSIONLESS

def headFromPressureRise(pressureRise: float, density: float) -> float:

    """
    Head in metres from a pressure rise in Pa and a density in kg/m^3.
    """

    if density <= 0.0:
        raise PumpError(f'The density must be positive, got {density}.',
                        context = createErrorContext(component = 'turbomachineryUtils'))

    return pressureRise / (density * GRAVITY)

def tipSpeedFromHead(head: float, headCoefficient: float = None) -> float:

    """

    Impeller tip speed from the head it has to produce, U = sqrt(g H / psi).

    This is the relation that turns a pressure requirement into a mechanical one, and it is where
    a rocket pump becomes difficult: a large head needs a large tip speed, and tip speed is bounded
    by the impeller material rather than by anything hydraulic.

    """

    coefficient = HEAD_COEFFICIENT['typical'] if headCoefficient is None else headCoefficient

    if not 0.0 < coefficient <= 1.0:
        raise PumpError(
            f'The head coefficient must lie in (0, 1], got {coefficient}.',
            context = createErrorContext(component = 'turbomachineryUtils'))

    return np.sqrt(GRAVITY * head / coefficient)

def geometryForSpecificSpeed(dimensionless: float) -> dict:

    """
    Which impeller geometry a dimensionless specific speed corresponds to.
    """

    for name, entry in PUMP_GEOMETRY.items():
        if entry['lower'] <= dimensionless < entry['upper']:
            return {'geometry': name, 'note': entry['note'], 'inRange': True}

    lowest = min(PUMP_GEOMETRY.values(), key = lambda entry: entry['lower'])['lower']

    if dimensionless < lowest:
        return {'geometry': 'radial, below the usual range', 'inRange': False,
                'note': 'very high head for the flow. Multiple stages or a partial emission '
                        'impeller, and the efficiency will be poor'}

    return {'geometry': 'axial, above the usual range', 'inRange': False,
            'note': 'very high flow for the head. Unusual on a rocket outside an inducer'}
