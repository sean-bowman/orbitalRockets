
# -- Collection of commonly used functions [electricalPower] -- #

'''

Shared function repository for the electricalPower library.

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
# -- electricalPower Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
ElectricalPowerError = EngineeringError


# ElectricalPowerError above is the domain base, aliased to EngineeringError by the scaffold.
# These are the specific ones and they subclass it, so a caller can still catch the whole family
# with one except.

class HarnessError(ElectricalPowerError):
    """
    A wire that cannot carry its current after derating, or a run whose voltage drop leaves the
    load below its minimum operating voltage.
    """

class PowerBudgetError(ElectricalPowerError):
    """
    A battery that cannot deliver the mission, or an energy budget that does not close. Raised
    rather than reported, because a stage that runs out of power part way through is not a stage
    with a small negative margin.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Copper resistivity at 20 C, and its temperature coefficient. Both are standard values.
COPPER_RESISTIVITY = 1.724e-8        # [ohm m] at 20 C
COPPER_TEMPERATURE_COEFFICIENT = 0.00393   # [1/K]
REFERENCE_TEMPERATURE = 20.0         # [C]

# The AWG definition, which is exact rather than tabulated: 36 AWG is 0.005 inches and each step
# down multiplies the diameter by the 39th root of 92.
#
# That makes every wire resistance in this library a computed quantity rather than a table lookup,
# and it is one of the few exactly checkable numbers in the whole repository.
AWG_REFERENCE_GAUGE = 36
AWG_REFERENCE_DIAMETER = 0.127e-3    # [m], 0.005 inches
AWG_RATIO = 92.0
AWG_STEPS = 39.0

# Single copper wire in free air, current at which it reaches its insulation temperature limit.
#
# AS50881 gives these as curves rather than a table and the standard is not openly available, so
# these are representative values consistent with common practice. They are registered as
# unvalidated, and the conclusion this domain draws does not rest on them: see the voltage drop
# result, which is a resistance calculation and is exact.
SINGLE_WIRE_AMPACITY = {
    10: 55.0,    # [A]
    12: 41.0,
    14: 32.0,
    16: 22.0,
    18: 16.0,
    20: 11.0,
    22: 9.0,
    24: 7.0,
    26: 5.0,
    28: 4.0,
}

# Derating applied to the free-air rating. Both are stated as curves in AS50881 and both are
# representative here.
#
# Bundle derating is the larger effect and it is the one most often forgotten: a wire in the middle
# of a harness cannot shed heat, so the same wire carries far less current than its free-air rating.
BUNDLE_DERATING = {
    1:  1.00,    # [-] a single wire
    5:  0.60,
    15: 0.45,
    30: 0.38,
    60: 0.33,
}

# Altitude derating, because convective cooling falls with air density. Above the atmosphere the
# only path is conduction along the wire and radiation, and the value flattens.
ALTITUDE_DERATING = {
    0:      1.00,     # [-] sea level
    10000:  0.85,
    20000:  0.75,
    30000:  0.70,
    60000:  0.65,
}

# Maximum voltage drop over a run, as a fraction of bus voltage. Common practice for a continuous
# load; a transient load may be allowed more.
VOLTAGE_DROP_LIMIT = 0.03    # [-]

# Battery chemistries and what each is for. Specific energy is at the cell level; a pack is
# typically 60 to 75 per cent of it once the case, the interconnects and the management are counted.
BATTERY_CHEMISTRIES = {
    'lithium ion': {
        'specificEnergy':    200.0,   # [W h/kg] at cell level
        'nominalVoltage':    3.6,     # [V] per cell
        'minimumVoltage':    3.0,     # [V] per cell
        'maximumDischargeRate': 3.0,  # [C]
        'lowTemperatureLimit': -20.0, # [C]
        'note': 'the default for anything that has to be light. Needs a management system, needs '
                'thermal control, and its failure mode is thermal runaway rather than an open '
                'circuit'},
    'lithium polymer': {
        'specificEnergy':    180.0,   # [W h/kg]
        'nominalVoltage':    3.7,
        'minimumVoltage':    3.0,
        'maximumDischargeRate': 10.0, # [C]
        'lowTemperatureLimit': -10.0,
        'note': 'higher discharge rate and worse cold performance. Suits a short, high current '
                'profile such as an ascent'},
    'silver zinc': {
        'specificEnergy':    120.0,   # [W h/kg]
        'nominalVoltage':    1.5,
        'minimumVoltage':    1.2,
        'maximumDischargeRate': 20.0, # [C]
        'lowTemperatureLimit': -20.0,
        'note': 'very high discharge rate, short wet life measured in months, and extensive launch '
                'vehicle heritage for exactly that reason: a battery that only has to work once '
                'does not need a long life'},
    'lithium thionyl chloride': {
        'specificEnergy':    500.0,   # [W h/kg]
        'nominalVoltage':    3.6,
        'minimumVoltage':    3.0,
        'maximumDischargeRate': 0.1,  # [C]
        'lowTemperatureLimit': -55.0,
        'note': 'the highest specific energy available and a very low discharge rate. A primary '
                'cell for a long, low load, not for an ascent'},
}

# Usable fraction of nameplate capacity. Depth of discharge is a life and reliability limit rather
# than a physical one, and it is tighter on a rechargeable pack that has to survive many cycles
# than on a primary battery that is used once.
DEPTH_OF_DISCHARGE = {
    'single use':   0.90,   # [-]
    'few cycles':   0.80,
    'many cycles':  0.50,
}

# Capacity retained at temperature, as a fraction of the rating at 20 C. Cold is the case that
# matters on a launch vehicle: a battery cold-soaked on the pad delivers less than its nameplate.
TEMPERATURE_CAPACITY_FACTOR = {
    40.0:   1.00,   # [-]
    20.0:   1.00,
    0.0:    0.90,
    -20.0:  0.75,
    -40.0:  0.50,
}

# Connector mass and reliability. Connector count is the best available reliability proxy for a
# harness, which is the reason this table exists at all.
CONNECTOR_TYPES = {
    'circular, 8 way':  {'mass': 0.045, 'contacts': 8,  'note': 'the workhorse'},
    'circular, 19 way': {'mass': 0.075, 'contacts': 19, 'note': 'signal bundles'},
    'circular, 37 way': {'mass': 0.130, 'contacts': 37, 'note': 'avionics interfaces'},
    'power, 4 way':     {'mass': 0.090, 'contacts': 4,  'note': 'heavy contacts for bus feeds'},
}

# Wire mass per unit length including insulation, as a multiple of the bare copper mass. A thin
# wall PTFE insulation on a small gauge wire is a large fraction of the total.
INSULATION_MASS_FACTOR = {
    10: 1.35, 12: 1.40, 14: 1.45, 16: 1.55, 18: 1.65,
    20: 1.80, 22: 2.00, 24: 2.30, 26: 2.70, 28: 3.20,
}

COPPER_DENSITY = 8960.0    # [kg/m^3]

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def wireDiameter(gauge: float) -> float:

    '''

    Conductor diameter from AWG, by the definition rather than from a table.

        d = 0.127 mm * 92 ** ((36 - n) / 39)

    36 AWG is exactly 0.005 inches and each gauge step multiplies the diameter by the 39th root of
    92. Everything else about a wire follows from this.

    '''

    if gauge < 0 or gauge > 40:
        raise InvalidInputError(
            f'The wire gauge must lie between 0 and 40 AWG, got {gauge}. Outside that the '
            f'definition still evaluates and the wire does not exist.',
            context = createErrorContext(component = 'powerUtils'))

    return AWG_REFERENCE_DIAMETER * AWG_RATIO ** ((AWG_REFERENCE_GAUGE - gauge) / AWG_STEPS)

def wireArea(gauge: float) -> float:

    '''
    Conductor cross-sectional area.
    '''

    return np.pi / 4.0 * wireDiameter(gauge) ** 2

def wireResistance(gauge: float, length: float, temperature: float = REFERENCE_TEMPERATURE) -> float:

    '''

    Conductor resistance, with the copper temperature coefficient applied.

    A hot wire is a worse wire, and the temperature that matters is the conductor temperature under
    load rather than the ambient. That coupling is why a marginal harness gets worse as it warms.

    '''

    if length < 0.0:
        raise InvalidInputError(
            f'The length cannot be negative, got {length}.',
            context = createErrorContext(component = 'powerUtils'))

    resistivity = COPPER_RESISTIVITY * (1.0 + COPPER_TEMPERATURE_COEFFICIENT
                                        * (temperature - REFERENCE_TEMPERATURE))

    return resistivity * length / wireArea(gauge)

def voltageDrop(gauge: float, length: float, current: float,
                temperature: float = REFERENCE_TEMPERATURE) -> float:

    '''

    Voltage lost in a run, counting both conductors.

    The factor of two is the part that gets forgotten. Current goes out along one wire and returns
    along another, so the resistance in the loop is twice the one-way resistance unless the return
    is through structure.

    '''

    if current < 0.0:
        raise InvalidInputError(
            f'The current cannot be negative, got {current}.',
            context = createErrorContext(component = 'powerUtils'))

    return 2.0 * wireResistance(gauge, length, temperature) * current

def interpolateFactor(table: dict, value: float) -> float:

    '''
    Linear interpolation across a factor table, clamped at both ends rather than extrapolated.
    '''

    keys = sorted(table)

    if value <= keys[0]:
        return table[keys[0]]

    if value >= keys[-1]:
        return table[keys[-1]]

    return float(np.interp(value, keys, [table[key] for key in keys]))
