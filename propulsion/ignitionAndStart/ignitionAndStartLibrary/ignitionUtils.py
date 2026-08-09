# -- Domain-specific helpers [ignitionAndStart] -- #

'''

Igniters, the start sequence, chill-in, shutdown, and the transients that break engines.

Named ignitionUtils rather than utils. Every domain library in this repository has a utils.py
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
# -- ignitionAndStart Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
IgnitionError = EngineeringError

# IgnitionError above is the domain base, aliased to EngineeringError by the scaffold. These are the
# specific ones and they subclass it, so a caller can still catch the whole family with one except.

class SequenceError(IgnitionError):
    """
    A start or shutdown sequence whose events do not order correctly, or whose timing puts the
    engine somewhere it cannot recover from. Raised rather than reported, because a sequence that
    does not order is not a slow engine, it is a destroyed one.
    """

class ConditioningError(IgnitionError):
    """
    A chill-down that cannot reach the required state, or a propellant asked to condition hardware
    it has no phase change available for.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

_HUB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'propulsionLibrary')

if _HUB not in sys.path:
    sys.path.insert(0, _HUB)

from propulsionUtils import PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH

# ------------------------------------------------------------------------------------------------ #

# Igniter types, with what each needs and what each can and cannot do.
#
# The single axis that separates them in practice is restart. An engine that has to light more than
# once cannot use a pyrotechnic cartridge without carrying one per start, and that constraint has
# decided more igniter selections than energy or reliability ever has.
#
# 'restarts' is the number of starts one installation supports. None means unlimited within the
# hardware life. The energy figures are the order of magnitude the device delivers to the chamber
# and they are indicative rather than sourced; see the unvalidated register.
IGNITER_TYPES = {

    'augmented spark': {
        'restarts':       None,
        'energy':         50.0,          # [J] per start, order of magnitude
        'needsPower':     True,
        'needsConsumable': False,
        'propellants':    'gaseous or vaporised main propellants',
        'flightExample':  'RS-25, three augmented spark igniters, one per combustor',
        'note':           'a small chamber burning the main propellants, lit by a spark plug and '
                          'exhausting into the main chamber. Unlimited restarts and no consumable, '
                          'at the cost of a propellant tap and its own small feed system'},

    'torch': {
        'restarts':       None,
        'energy':         50.0,          # [J]
        'needsPower':     True,
        'needsConsumable': False,
        'propellants':    'gaseous main propellants, or a separate gas supply',
        'flightExample':  'RL10, spark torch',
        'note':           'the same idea as an augmented spark igniter and the names are often '
                          'used interchangeably. Where they are distinguished, a torch has its own '
                          'gas supply rather than tapping the main propellants'},

    'pyrotechnic': {
        'restarts':       1,
        'energy':         2.0e4,         # [J]
        'needsPower':     True,
        'needsConsumable': True,
        'propellants':    'any',
        'flightExample':  'Saturn V F-1 used a pyrotechnic igniter on the turbine exhaust',
        'note':           'a solid charge. The most energy for the least hardware and it works '
                          'with any propellant, but it is spent once. An engine needing four '
                          'starts carries four of them'},

    'hypergolic slug': {
        'restarts':       1,
        'energy':         None,
        'needsPower':     False,
        'needsConsumable': True,
        'propellants':    'any oxidiser that a hypergol will ignite against',
        'flightExample':  'Saturn V F-1, triethylaluminium/triethylborane cartridge; Merlin, TEA-TEB',
        'note':           'a cartridge of something that ignites on contact with the oxidiser, '
                          'burst into the fuel line. Needs no electrical power at all, which is '
                          'its real advantage, and it is spent once per cartridge'},

    'catalytic': {
        'restarts':       None,
        'energy':         None,
        'needsPower':     False,
        'needsConsumable': False,
        'propellants':    'monopropellants and peroxide systems',
        'flightExample':  'hydrazine monopropellant thrusters, Shell 405 catalyst bed',
        'note':           'no igniter at all in the usual sense. The bed decomposes the '
                          'propellant and the limit is bed life and cold-start performance rather '
                          'than ignition energy'},
}

# Hypergolic ignition delay, the time from first liquid contact to established combustion.
#
# These are drop-test and impinging-jet measurements at ambient conditions and they scatter widely
# between methods, which is why a range is carried rather than a value. The liquid-phase induction
# time is measured in tens of microseconds; everything above that is physical transport and heat
# transfer, which is what makes the delay depend on the injector rather than only on the chemistry.
#
# The number that matters is not the delay itself but the propellant it lets accumulate. See
# StartTransient.
#
# Keyed on the propulsion hub's combination names so a lookup crosses cleanly between the two.
IGNITION_DELAY = {
    'N2O4/MMH':  (1.0, 5.0),     # [ms]
    'N2O4/UDMH': (2.0, 8.0),     # [ms]
}

# The RS-25 start and shutdown sequence, from Biggs, 'SSME: The First Ten Years', part 3.
#
# This is the validation anchor for the whole sub-domain and it is the only fully published start
# sequence for a large liquid engine that states its times to the hundredth of a second. Every
# number here is quoted from that source; nothing is inferred.
#
# Written in chronological order, and a test asserts it stays that way. A sequence table out of
# order is a transcription error and it is the kind that survives review.
SSME_START_SEQUENCE = {
    'fuelPreburnerValveStart':  0.100,   # [s] delay before the FPOV ramps to 56 per cent
    'oxidiserPreburnerDelay':   0.120,   # [s] initial OPOV opening, seal retraction only
    'mainOxidiserValveDelay':   0.200,   # [s] before the MOV ramps to just under 60 per cent
    'mainFuelValveFullOpen':    0.667,   # [s] ramped to full open in two thirds of a second
    'fuelPreburnerNotch':       0.720,   # [s] the notch closure that rides the second pressure dip
    'oxidiserMainFlowPath':     0.840,   # [s] when the OPOV major flow path starts to open
    'speedCheck':               1.250,   # [s] HPFTP must exceed 4600 rpm or the engine is shut down
    'fuelPreburnerPrime':       1.400,   # [s]
    'mainChamberPrime':         1.500,   # [s]
    'oxidiserPreburnerPrime':   1.600,   # [s]
    'ignitionVerified':         1.700,   # [s] first of two ignition confirmation checks
    'ignitionVerifiedAgain':    2.300,   # [s]
    'closedLoopThrust':         2.400,   # [s]
    'closedLoopMixtureRatio':   3.800,   # [s]
    'ratedPower':               5.000,   # [s]
}

SSME_SHUTDOWN_LIMITS = {
    'oxidiserPreburnerCloseRate': 45.0,      # [per cent per second]
    'mainOxidiserCloseRate':      40.0,      # [per cent per second]
    'thrustDecayLimit':           700.0e3,   # [lbf per second], an orbiter structural limit
    'fuelValveHoldTime':          1.0,       # [s] held open to force a fuel-rich shutdown
    'boiloutSafeSpeed':           7000.0,    # [rpm] below which HPFTP boilout stops being damaging
    'boiloutSafeTime':            5.0,       # [s]
}

# The two facts from that source that decide how this sub-domain models sequencing at all.
SSME_SEQUENCE_TOLERANCE = {
    'timingError':        0.100,     # [s] can lead to significant damage
    'valvePositionError': 2.0,       # [per cent], and one per cent for the OPOV
    'primeSpacing':       0.100,     # [s] the three combustors prime about a tenth apart
    'pumpRunawayRate':    400.0e3,   # [rpm per second] HPOTP acceleration with no fluid load
}

# Cryogens, with the backend species name the property wrapper expects and the normal boiling
# point. Chill-down is an enthalpy balance and every number in it comes from the equation of state,
# so nothing is tabulated here that the backend can supply.
CRYOGENS = {
    'LOX':  {'species': 'O2',       'boilingPoint': 90.19},    # [K]
    'LH2':  {'species': 'H2',       'boilingPoint': 20.28},    # [K]
    'LCH4': {'species': 'Methane',  'boilingPoint': 111.67},   # [K]
    'LN2':  {'species': 'Nitrogen', 'boilingPoint': 77.36},    # [K]
}

# Mean specific heat of structural metals over a chill-down from room temperature to a cryogen
# boiling point.
#
# These are NOT the room-temperature values in common/materials.py and they must not be replaced by
# them. Specific heat falls steeply below about 100 K, and using a room-temperature value over the
# whole range overstates the metal's stored enthalpy and therefore the chill-down propellant, by
# roughly a third for stainless and more for aluminium.
MEAN_SPECIFIC_HEAT = {
    'stainless 304':  390.0,    # [J/(kg K)] mean over roughly 90 to 300 K
    'stainless 316':  390.0,    # [J/(kg K)]
    'inconel 718':    380.0,    # [J/(kg K)]
    'aluminium 6061': 700.0,    # [J/(kg K)]
    'aluminium 2219': 690.0,    # [J/(kg K)]
    'titanium 6-4':   440.0,    # [J/(kg K)]
}

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def accumulatedPropellant(massFlow: float, delay: float) -> float:

    '''

    Propellant delivered into the chamber before combustion is established.

    The whole of the hard start problem is in this one product. Nothing else about an igniter
    matters as much as how long it takes to work, because the feed system does not wait.

    '''

    if massFlow < 0.0 or delay < 0.0:
        raise InvalidInputError(
            f'Mass flow and delay must both be non-negative, got {massFlow} and {delay}.',
            context = createErrorContext(component = 'ignitionUtils'))

    return massFlow * delay

def residenceTime(chamberVolume: float, massFlow: float, gasDensity: float) -> float:

    '''

    Mean residence time of gas in the chamber, as chamber gas mass over mass flow.

    This is the yardstick the ignition delay is measured against, and the comparison is the point.
    A large engine holds its combustion gas for on the order of a millisecond; an igniter that
    takes fifty milliseconds to work has admitted fifty chamber-fulls in the meantime.

    '''

    if massFlow <= 0.0:
        raise InvalidInputError(
            f'Mass flow must be positive to define a residence time, got {massFlow}.',
            context = createErrorContext(component = 'ignitionUtils'))

    return chamberVolume * gasDensity / massFlow

def primingTime(volume: float, volumetricFlow: float) -> float:

    '''

    Time to fill a line or manifold with liquid, as volume over volumetric flow.

    Priming is filling the system with liquid such that the flow entering the injector equals the
    flow leaving it. Until that happens the injector is passing a two-phase mixture and the engine
    is not running on the propellants it was designed around.

    '''

    if volumetricFlow <= 0.0:
        raise InvalidInputError(
            f'The volumetric flow must be positive, got {volumetricFlow}.',
            context = createErrorContext(component = 'ignitionUtils'))

    return volume / volumetricFlow
