# -- Domain-specific helpers [propulsion] -- #

'''

Performance relations, propellant property access and the engine-level helpers.

Named propulsionUtils rather than utils. Every domain library in this repository has a utils.py
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
# -- propulsion Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
PropulsionError = EngineeringError

class PropellantError(PropulsionError):
    '''
    An unknown propellant combination, or one asked to operate outside the range its tabulated
    performance was taken at.
    '''

class PerformanceError(PropulsionError):
    '''
    A performance calculation that cannot close: an expansion below ambient with no solution, a
    pressure ratio outside the isentropic relations, or an efficiency outside zero to one.
    '''

class SizingError(PropulsionError):
    '''
    A geometry that does not follow from the inputs, such as a contraction ratio below one or a
    chamber shorter than its own convergent section.
    '''

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Below roughly this exit-to-ambient pressure ratio the boundary layer separates from the nozzle
# wall and the flow no longer fills the exit. Summerfield's criterion is crude and it is the number
# everyone uses, because the alternatives need the wall boundary layer and are not better in the
# regime where the answer is 'do not do that'.
SUMMERFIELD_SEPARATION_RATIO = 0.4    # [-]

# Combustion efficiency expresses itself entirely in c*, and nozzle efficiency entirely in Cf. They
# multiply into Isp identically, which is exactly why an Isp shortfall on its own does not say which
# one is at fault. These are the values a well developed engine achieves.
TYPICAL_CSTAR_EFFICIENCY = 0.96    # [-]
TYPICAL_THRUST_COEFFICIENT_EFFICIENCY = 0.98    # [-]

# Characteristic length, L* = Vc / At, is the traditional chamber sizing parameter: it sets the
# residence time available for the propellant to finish burning. The values are propellant
# dependent because the thing being bought is reaction time, and hypergolics need less of it.
#
# The parameter is a floor rather than a design driver. Almost every real chamber is longer than its
# L* requires, because the wall area needed to carry the cooling load exceeds the wall area a
# minimum L* chamber has. See EngineSizing.sizeChamber, which reports which of the two governs.
CHARACTERISTIC_LENGTH = {
    'LOX/RP-1':     {'value': 1.10, 'note': 'kerosene needs the residence time, and soot does not help'},
    'LOX/LH2':      {'value': 0.90, 'note': 'fast kinetics, and the gas is moving quickly'},
    'LOX/LCH4':     {'value': 1.05, 'note': 'between hydrogen and kerosene, as it is in most things'},
    'N2O4/MMH':     {'value': 0.80, 'note': 'hypergolic, so ignition delay is not part of the budget'},
    'N2O4/UDMH':    {'value': 0.80, 'note': 'as MMH'},
    'H2O2/RP-1':    {'value': 1.50, 'note': 'decomposition then combustion, two steps in series'},
    'LOX/ethanol':  {'value': 1.00, 'note': 'well behaved, and forgiving of a short chamber'},
}    # [m]

# Representative bipropellant performance, at the reference chamber pressure each entry names and at
# the mixture ratio in 'mixtureRatio'. These are frozen-equilibrium textbook values and they exist so
# a first pass sizing runs without a CEA installation.
#
# CEA is the authority. Anything past a trade study should replace these with a CEA run at the actual
# chamber pressure and mixture ratio, because c* moves with both and the tabulated value is a single
# point on a surface. The class reports the reference condition alongside every number for that
# reason.
#
# 'mixtureRatio' is the operating point, not the stoichiometric one, and the two differ substantially.
# Peak specific impulse sits fuel rich of stoichiometric because the exhaust molecular weight falls
# faster than the flame temperature does, and c* goes as sqrt(Tc/M). LOX/LH2 is the extreme case:
# stoichiometric is 7.94 and engines run near 5.5.
#
# Two characteristic velocities are carried deliberately, and they do not agree.
#
# 'referenceCstar' is the literature value at the stated condition and is what the classes use.
# The ideal one-dimensional value that characteristicVelocity() computes from chamberTemperature,
# molarMass and gamma sits between 4.3 per cent below it and 1.6 per cent above it across this
# table. That spread is real physics rather than a table error: the ideal relation assumes a frozen
# composition at the chamber value, and a real expansion recombines on the way down, which adds
# energy the frozen calculation never sees. The sign of the discrepancy depends on how dissociated
# the chamber is.
#
# Carrying both and reporting the gap is the honest option. Tuning gamma until the ideal relation
# reproduced the literature number would hide a real effect behind a fitted constant, and would
# leave gamma wrong for every other place it is used, which includes the entire nozzle calculation.
PROPELLANT_COMBINATIONS = {
    'LOX/RP-1': {
        'oxidiser': 'LOX', 'fuel': 'RP-1',
        'mixtureRatio': 2.56, 'stoichiometricRatio': 3.41,
        'chamberTemperature': 3670.0, 'molarMass': 23.3, 'gamma': 1.24,
        'oxidiserDensity': 1141.0, 'fuelDensity': 810.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 1823.0,
        'hypergolic': False, 'storable': False,
        'note': 'the booster workhorse. Dense, cheap, and it cokes cooling passages'},
    'LOX/LH2': {
        'oxidiser': 'LOX', 'fuel': 'LH2',
        'mixtureRatio': 5.50, 'stoichiometricRatio': 7.94,
        'chamberTemperature': 3400.0, 'molarMass': 13.0, 'gamma': 1.20,
        'oxidiserDensity': 1141.0, 'fuelDensity': 71.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 2330.0,
        'hypergolic': False, 'storable': False,
        'note': 'the best specific impulse available, and the worst density impulse'},
    'LOX/LCH4': {
        'oxidiser': 'LOX', 'fuel': 'LCH4',
        'mixtureRatio': 3.45, 'stoichiometricRatio': 3.99,
        'chamberTemperature': 3533.0, 'molarMass': 20.3, 'gamma': 1.20,
        'oxidiserDensity': 1141.0, 'fuelDensity': 423.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 1857.0,
        'hypergolic': False, 'storable': False,
        'note': 'the reusability choice. Clean burning, and both fluids sit at similar temperatures'},
    'N2O4/MMH': {
        'oxidiser': 'N2O4', 'fuel': 'MMH',
        'mixtureRatio': 2.16, 'stoichiometricRatio': 2.50,
        'chamberTemperature': 3396.0, 'molarMass': 22.6, 'gamma': 1.24,
        'oxidiserDensity': 1443.0, 'fuelDensity': 878.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 1745.0,
        'hypergolic': True, 'storable': True,
        'note': 'hypergolic and storable, which buys restart and long coast. Toxic'},
    'N2O4/UDMH': {
        'oxidiser': 'N2O4', 'fuel': 'UDMH',
        'mixtureRatio': 2.61, 'stoichiometricRatio': 3.13,
        'chamberTemperature': 3415.0, 'molarMass': 23.1, 'gamma': 1.25,
        'oxidiserDensity': 1443.0, 'fuelDensity': 793.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 1734.0,
        'hypergolic': True, 'storable': True,
        'note': 'as MMH, and more widely used outside the United States'},
    'H2O2/RP-1': {
        'oxidiser': 'H2O2 98%', 'fuel': 'RP-1',
        'mixtureRatio': 7.30, 'stoichiometricRatio': 8.01,
        'chamberTemperature': 2953.0, 'molarMass': 21.7, 'gamma': 1.21,
        'oxidiserDensity': 1430.0, 'fuelDensity': 810.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 1610.0,
        'hypergolic': False, 'storable': True,
        'note': 'dense and non-toxic, at a real specific impulse cost. Catalyst bed or torch start'},
    'LOX/ethanol': {
        'oxidiser': 'LOX', 'fuel': 'ethanol 95%',
        'mixtureRatio': 1.60, 'stoichiometricRatio': 2.08,
        'chamberTemperature': 3100.0, 'molarMass': 22.0, 'gamma': 1.22,
        'oxidiserDensity': 1141.0, 'fuelDensity': 789.0,
        'referencePressure': 6.9e6,
        'referenceCstar': 1641.0,
        'hypergolic': False, 'storable': False,
        'note': 'low performance and low temperature, which makes it the teaching choice'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Isentropic relations -- #
# ------------------------------------------------------------------------------------------------ #

def vandenkerckhove(gamma: float) -> float:

    '''

    The Vandenkerckhove function, the choked mass flow group that appears in nearly every relation
    in this domain.

        Gamma = sqrt(gamma) (2 / (gamma + 1)) ^ ((gamma + 1) / (2 (gamma - 1)))

    It varies remarkably little: 0.6847 at gamma = 1.4 and 0.6346 at gamma = 1.13. That insensitivity
    is why order of magnitude engine numbers can be done in the head, and why an error in gamma is
    rarely the reason a performance prediction is wrong.

    '''

    if gamma <= 1.0:
        raise PerformanceError(
            f'The ratio of specific heats must exceed one, got {gamma}.',
            context = createErrorContext(component = 'propulsionUtils'))

    return np.sqrt(gamma) * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))

def characteristicVelocity(gamma: float, molarMass: float, chamberTemperature: float) -> float:

    '''

    Ideal characteristic velocity in m/s.

        c* = sqrt(R_specific Tc) / Gamma

    `molarMass` is in g/mol, which is how combustion codes report it.

    c* is a property of the propellant and the chamber alone. Nothing downstream of the throat can
    change it, which is the entire reason it is the diagnostic that separates a combustion problem
    from a nozzle problem.

    '''

    for name, value in (('molar mass', molarMass), ('chamber temperature', chamberTemperature)):
        if value <= 0.0:
            raise PerformanceError(
                f'The {name} must be positive, got {value}.',
                context = createErrorContext(component = 'propulsionUtils'))

    specificGasConstant = R_UNIVERSAL / (molarMass / 1000.0)

    return np.sqrt(specificGasConstant * chamberTemperature) / vandenkerckhove(gamma)

def areaRatioFromPressureRatio(gamma: float, pressureRatio: float) -> float:

    '''

    Expansion area ratio from the exit-to-chamber pressure ratio.

        eps = Gamma / [ (Pe/Pc)^(1/gamma) sqrt( 2 gamma / (gamma - 1) (1 - (Pe/Pc)^((gamma-1)/gamma)) ) ]

    '''

    if not 0.0 < pressureRatio < 1.0:
        raise PerformanceError(
            f'The exit-to-chamber pressure ratio must lie strictly between zero and one, got '
            f'{pressureRatio}. A ratio of one is a nozzle that does not expand.',
            context = createErrorContext(component = 'propulsionUtils'))

    exponent = (gamma - 1.0) / gamma

    return (vandenkerckhove(gamma)
            / (pressureRatio ** (1.0 / gamma)
               * np.sqrt(2.0 * gamma / (gamma - 1.0) * (1.0 - pressureRatio ** exponent))))

def pressureRatioFromAreaRatio(gamma: float, areaRatio: float) -> float:

    '''

    Exit-to-chamber pressure ratio from the expansion area ratio, by solve.

    The relation cannot be inverted in closed form and it has two roots: a subsonic one and a
    supersonic one. The supersonic branch is the one a rocket nozzle runs on, so the search is
    bracketed below the throat pressure ratio to select it. Returning the subsonic root would give a
    nozzle that decelerates the flow and a thrust coefficient near zero.

    '''

    if areaRatio <= 1.0:
        raise PerformanceError(
            f'The area ratio must exceed one, got {areaRatio}. An area ratio of one is the throat.',
            context = createErrorContext(component = 'propulsionUtils'))

    throatRatio = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))

    def residual(ratio: float) -> float:
        return areaRatioFromPressureRatio(gamma, ratio) - areaRatio

    lower = 1.0e-12
    upper = throatRatio * (1.0 - 1.0e-9)

    if residual(lower) * residual(upper) > 0.0:
        raise PerformanceError(
            f'No supersonic solution for an area ratio of {areaRatio} at gamma {gamma}.',
            context = createErrorContext(component = 'propulsionUtils'))

    # bisection: the residual is monotonic on the supersonic branch, and this cannot leave it
    for _ in range(200):
        middle = 0.5 * (lower + upper)
        if residual(lower) * residual(middle) <= 0.0:
            upper = middle
        else:
            lower = middle
        if upper - lower < 1.0e-15:
            break

    return 0.5 * (lower + upper)

def bulkDensity(mixtureRatio: float, oxidiserDensity: float, fuelDensity: float) -> float:

    '''

    Propellant bulk density in kg/m^3, the density the tanks actually see.

        rho_bulk = (1 + MR) / (MR / rho_ox + 1 / rho_f)

    This is a harmonic mean weighted by mass fraction, so it sits nearer the lower of the two
    densities than an arithmetic average would suggest. For LOX/LH2 that is the whole story.

    '''

    for name, value in (('mixture ratio', mixtureRatio), ('oxidiser density', oxidiserDensity),
                        ('fuel density', fuelDensity)):
        if value <= 0.0:
            raise PropellantError(
                f'The {name} must be positive, got {value}.',
                context = createErrorContext(component = 'propulsionUtils'))

    return (1.0 + mixtureRatio) / (mixtureRatio / oxidiserDensity + 1.0 / fuelDensity)
