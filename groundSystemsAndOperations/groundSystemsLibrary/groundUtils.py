
# -- Collection of commonly used functions [groundSystemsAndOperations] -- #

'''

Shared function repository for the groundSystemsAndOperations library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one
flat namespace and does not have to know whether a helper is domain-specific or shared.

What is defined here is the explosives siting data, which is the only part of this domain with a
published standard behind it, and the operational tables that the countdown and availability
classes work from.

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
# -- groundSystemsAndOperations Errors -- #
# ------------------------------------------------------------------------------------------------ #

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause.
GroundSystemsError = EngineeringError

class SitingError(GroundSystemsError):
    """
    A facility inside the separation distance its explosive equivalent requires. Raised rather
    than reported: a control room at intraline distance from an inhabited-building-distance
    hazard is not a small negative margin, it is a room full of people in the wrong place.
    """

class LoadingError(GroundSystemsError):
    """
    A tanking plan that cannot deliver the flight load: storage that runs dry, a transfer rate
    that cannot outrun the boil-off, or a topping flow below the vent rate.
    """

class TimelineError(GroundSystemsError):
    """
    A countdown that does not fit its window, or a recycle that cannot reach T-0 before the
    window closes.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Explosive siting: DESR 6055.09 and NASA-STD-8719.12A -- #
# ------------------------------------------------------------------------------------------------ #

# Hopkinson-Cranz cube-root scaling, in the form the standards write it:
#
#     d = K * W ** (1/3)      d in feet, W in pounds of TNT equivalent
#
# The scaling itself is a similarity law rather than a convention: two charges of the same
# explosive produce the same overpressure at the same scaled distance. What the standards supply
# is the table of K values, each one a chosen consequence.
#
# Read in full from NASA-STD-8719.12A Table E-1, which reproduces DESR 6055.09.
K_FACTORS = {
    'lungRupture':                {'k':  1.79, 'overpressure': 386.9, 'means': 'lethality due to lung rupture'},
    'lungRuptureThreshold':       {'k':  3.33, 'overpressure': 107.1, 'means': 'lethality due to lung rupture'},
    'eardrum99':                  {'k':  3.90, 'overpressure':  74.4, 'means': '99% chance of eardrum rupture'},
    'barricadedIntermagazine':    {'k':  6.00, 'overpressure':  27.0, 'means': 'barricaded aboveground intermagazine distance'},
    'eardrum50':                  {'k':  8.00, 'overpressure':  15.0, 'means': '50% chance of eardrum rupture'},
    'barricadedIntraline':        {'k':  9.00, 'overpressure':  12.0, 'means': 'intraline distance with barricading'},
    'unbarricadedIntermagazine':  {'k': 11.00, 'overpressure':   8.0, 'means': 'unbarricaded aboveground intermagazine distance'},
    'unbarricadedIntraline':      {'k': 18.00, 'overpressure':   3.5, 'means': 'intraline distance without barricades'},
    'publicTrafficRoute':         {'k': 24.00, 'overpressure':   2.3, 'means': 'public traffic route, below 100,000 lb HE'},
    'publicTrafficRouteLarge':    {'k': 30.00, 'overpressure':   1.7, 'means': 'public traffic route, above 250,000 lb HE'},
    'inhabitedBuilding':          {'k': 40.00, 'overpressure':   1.2, 'means': 'inhabited building distance'},
    'inhabitedBuildingRelaxed':   {'k': 50.00, 'overpressure':   0.9, 'means': 'inhabited building distance, relaxed criterion'},
}

# TNT equivalence of energetic liquid combinations at a range launch pad, as a fraction of the
# propellant mass. DESR 6055.09 Table V5.E4.T5, reproduced as NASA-STD-8719.12A Table 5-29.
#
# Two things about this table are worth knowing before using it.
#
# The percentages are for propellant aboveground and unconfined except by its own tankage, which
# is the pad case. Confinement raises them and the standard sends any other configuration to
# individual assessment.
#
# The static test stand column is lower than the range launch column for two of the entries,
# because a stand can be built to keep the propellants apart in a way a vehicle cannot.
TNT_EQUIVALENCE = {
    'LO2/RP-1':      {'rangeLaunch': 0.20, 'staticTest': 0.10,
                      'note': '20% up to 226,795 kg, 10% on the excess'},
    'LO2/LH2':       {'rangeLaunch': None, 'staticTest': None,
                      'note': 'the larger of 8 W**(2/3) and 14% of W, see explosiveEquivalent'},
    'IRFNA/UDMH':    {'rangeLaunch': 0.10, 'staticTest': 0.10, 'note': 'hypergolic'},
    'N2O4/UDMH+N2H4':{'rangeLaunch': 0.10, 'staticTest': 0.05,
                      'note': 'hypergolic; MMH substitutes for N2H4 or UDMH'},
    'N2O4/PBAN':     {'rangeLaunch': 0.15, 'staticTest': 0.15,
                      'note': 'hybrid; 15% donor, 5% high velocity impact'},
    'nitromethane':  {'rangeLaunch': 1.00, 'staticTest': 1.00, 'note': 'alone or in combination'},
}

# The LO2/LH2 rule, which is the interesting one. Equivalent weight is the larger of a sublinear
# term and a flat fraction, so which one governs depends on how much propellant there is.
#
# Below the crossover the sublinear term governs and the equivalent weight is a LARGER fraction of
# the propellant than 14%. A small hydrogen stage is disproportionately hazardous per kilogram,
# which is the opposite of the intuition that a small vehicle is a small problem.
HYDROGEN_SUBLINEAR_COEFFICIENT = 8.0     # [lb per lb**(2/3)], DESR 6055.09 Table V5.E4.T5 footnote f
HYDROGEN_SUBLINEAR_EXPONENT = 2.0 / 3.0
HYDROGEN_FLAT_FRACTION = 0.14

# The RP-1 break point, above which the standard drops the equivalence to 10 per cent on the
# excess. Stated in the standard in both units; the kilogram figure is the exact conversion of
# 500,000 lb.
RP1_BREAK_MASS = 226795.0                # [kg]
RP1_UPPER_FRACTION = 0.20
RP1_EXCESS_FRACTION = 0.10

# The standards are written in pounds and feet, so the library computes in those and converts.
#
# The bracketed metric coefficient the standard offers for the hydrogen rule, 4.13 Q**(2/3) for Q
# in kilograms, is NOT the unit conversion of 8 W**(2/3). Converting the English form exactly gives
# 6.147, and the two differ by a factor of 1.49 with the published metric form the smaller. An
# analyst working natively in SI from the bracketed coefficient therefore gets a shorter siting
# distance than the English form the table is built on.
#
# This library uses the English form and converts, which is the conservative reading and the one
# that reproduces the standard's own numbers. The discrepancy is asserted by a test rather than
# left as a comment, because it is the kind of thing that is quietly corrected in a later edition.
HYDROGEN_METRIC_COEFFICIENT_PUBLISHED = 4.13
HYDROGEN_METRIC_COEFFICIENT_EXACT = 8.0 * (0.45359237 ** (1.0 / 3.0))

# ------------------------------------------------------------------------------------------------ #
# -- Loading and countdown -- #
# ------------------------------------------------------------------------------------------------ #

# A cryogenic tanking sequence is not one flow rate. It is four, and the fast fill that everybody
# pictures is a minority of the elapsed time on most vehicles.
#
# Fractions are of the maximum transfer rate the ground system can deliver.
LOADING_PHASES = {
    'chilldown':  {'rateFraction': 0.15, 'ofLoad': 0.00,
                   'purpose': 'condition the transfer line and the vehicle tank'},
    'slowFill':   {'rateFraction': 0.30, 'ofLoad': 0.05,
                   'purpose': 'cover the tank bottom without shocking it or geysering the line'},
    'fastFill':   {'rateFraction': 1.00, 'ofLoad': 0.93,
                   'purpose': 'the bulk of the load'},
    'topping':    {'rateFraction': 0.10, 'ofLoad': 0.02,
                   'purpose': 'reach the flight level against the ullage sensor'},
}

# After topping the tank is full and still boiling, so the ground keeps feeding it. Replenish is
# not a phase with a duration of its own: it lasts as long as the hold does, which is why a long
# hold is a propellant cost and not just a schedule cost.
REPLENISH_RATE_MARGIN = 1.5              # [-], replenish capacity over the steady boil-off rate

# Representative causes of a launch scrub, as a fraction of scrubs rather than of attempts.
#
# The weather share is anchored: roughly half of scrubs at the Eastern Range over three decades
# were weather. The split of the remainder is representative.
SCRUB_CAUSES = {
    'weather':        0.48,
    'vehicle':        0.27,
    'groundSystem':   0.17,
    'range':          0.08,
}

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def explosiveEquivalent(combination: str, propellantMass: float,
                        setting: str = 'rangeLaunch') -> dict:

    '''

    TNT equivalent weight of a propellant load, per DESR 6055.09 Table V5.E4.T5.

    Parameters
    ----------
    combination : str
        A key of TNT_EQUIVALENCE.
    propellantMass : float
        Total mass of the combination present, oxidiser and fuel together [kg].
    setting : str
        'rangeLaunch' or 'staticTest'.

    Returns
    -------
    dict
        equivalentMass [kg], effectiveFraction [-], and which rule governed.

    '''

    if combination not in TNT_EQUIVALENCE:
        raise SitingError(f'{combination} is not in the standard table. Available: '
                          f'{sorted(TNT_EQUIVALENCE)}.')

    if propellantMass <= 0.0:
        raise SitingError('Propellant mass must be positive.')

    if setting not in ('rangeLaunch', 'staticTest'):
        raise SitingError("Setting must be 'rangeLaunch' or 'staticTest'.")

    if combination == 'LO2/LH2':

        # The standard is written in pounds, so the sublinear term is evaluated there and the
        # result converted back. Doing it the other way needs a metric coefficient, and the one
        # the standard prints does not agree with the conversion.
        massPounds = propellantMass / KG_PER_LBM

        sublinear = HYDROGEN_SUBLINEAR_COEFFICIENT * massPounds ** HYDROGEN_SUBLINEAR_EXPONENT
        flat = HYDROGEN_FLAT_FRACTION * massPounds

        governing = 'sublinear 8 W**(2/3)' if sublinear >= flat else 'flat 14 per cent'
        equivalentPounds = max(sublinear, flat)

        equivalent = equivalentPounds * KG_PER_LBM

    elif combination == 'LO2/RP-1' and setting == 'rangeLaunch':

        # Two-tier: the full fraction up to the break mass, the reduced one above it.
        upper = min(propellantMass, RP1_BREAK_MASS) * RP1_UPPER_FRACTION
        excess = max(0.0, propellantMass - RP1_BREAK_MASS) * RP1_EXCESS_FRACTION

        equivalent = upper + excess
        governing = 'two tier, 20 then 10 per cent' if excess > 0.0 else 'flat 20 per cent'

    else:

        fraction = TNT_EQUIVALENCE[combination][setting]
        equivalent = fraction * propellantMass
        governing = f'flat {fraction * 100.0:.0f} per cent'

    return {'equivalentMass':    equivalent,
            'effectiveFraction': equivalent / propellantMass,
            'propellantMass':    propellantMass,
            'governing':         governing,
            'combination':       combination,
            'setting':           setting}

def hopkinsonCranzDistance(kFactor: float, equivalentMass: float) -> float:

    '''

    Separation distance from a K factor and a TNT equivalent weight.

    The standard's form is d = K W**(1/3) with d in feet and W in pounds. This converts on both
    sides and returns metres, so a call site never handles the mixed units.

    '''

    if equivalentMass <= 0.0:
        raise SitingError('Equivalent mass must be positive.')

    massPounds = equivalentMass / KG_PER_LBM

    return kFactor * massPounds ** (1.0 / 3.0) * M_PER_FT

def cumulativeGoProbability(perAttempt: float, attempts: int) -> float:

    '''

    Probability of launching within a given number of independent attempts.

    Independence is the assumption doing the work here and it is optimistic for weather, which is
    correlated day to day. The class that uses this says so and offers a correlated case.

    '''

    if not 0.0 <= perAttempt <= 1.0:
        raise GroundSystemsError('Per-attempt probability must lie between zero and one.')

    if attempts < 0:
        raise GroundSystemsError('Attempt count cannot be negative.')

    return 1.0 - (1.0 - perAttempt) ** attempts
