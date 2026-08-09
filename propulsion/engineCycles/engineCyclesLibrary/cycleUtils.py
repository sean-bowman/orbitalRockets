# -- Domain-specific helpers [engineCycles] -- #

'''

Gas generator, staged combustion, expander and pressure-fed cycles, and what closes them.

Named cycleUtils rather than utils. Every domain library in this repository has a utils.py
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
# -- engineCycles Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
EngineCyclesError = EngineeringError

class CycleError(EngineCyclesError):
    """
    A cycle that cannot close: a turbine that cannot deliver the pump power, a pressure ladder that
    does not reach the chamber, or a heat balance that runs out of heat.
    """

class PressureLadderError(EngineCyclesError):
    """
    A pressure schedule that is not monotonic, or one that asks a pump for a discharge pressure
    below the chamber it feeds.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

_HUB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'propulsionLibrary')

if _HUB not in sys.path:
    sys.path.insert(0, _HUB)

from propulsionUtils import PROPELLANT_COMBINATIONS

# The cycles, and the one structural fact about each that decides everything else.
#
# 'closed' is the field that matters most. A closed cycle puts every kilogram of propellant through
# the main chamber, so its turbine exhaust is not a loss. An open cycle dumps the turbine flow
# overboard at a fraction of main chamber impulse, and that penalty is the reason the whole
# staged combustion family exists.
#
# 'turbinePressureRatio' follows directly from 'closed'. An open cycle exhausts to ambient and can
# take a pressure ratio of twenty or more. A closed cycle has to hand its exhaust to the main
# injector, so the turbine gets whatever is left above chamber pressure, which is very little. That
# single constraint is why staged combustion pumps run at twice the chamber pressure.
ENGINE_CYCLES = {

    'pressure fed': {
        'hasPreburner': False,
        'closed': True, 'hasTurbomachinery': False,
        'turbinePressureRatio': None,
        'dischargeRatio': 1.0,
        'note': 'no pumps. The tank is the pump, and it pays in wall thickness'},

    'gas generator': {
        'hasPreburner': True,
        'closed': False, 'hasTurbomachinery': True,
        'turbinePressureRatio': 20.0,
        'dischargeRatio': 1.25,
        'note': 'the open cycle workhorse. Simple, and it throws propellant away'},

    'staged combustion': {
        'hasPreburner': True,
        'closed': True, 'hasTurbomachinery': True,
        'turbinePressureRatio': 1.5,
        'dischargeRatio': 2.0,
        'note': 'everything through the chamber. The pumps pay for it in discharge pressure'},

    'full flow staged combustion': {
        'hasPreburner': True,
        'closed': True, 'hasTurbomachinery': True,
        'turbinePressureRatio': 1.5,
        'dischargeRatio': 2.0,
        'note': 'two preburners, one per propellant. No interpropellant seal problem'},

    'expander': {
        'hasPreburner': False,
        'closed': True, 'hasTurbomachinery': True,
        'turbinePressureRatio': 1.6,
        'dischargeRatio': 1.7,
        'note': 'the turbine runs on jacket heat. Elegant, and it has a hard pressure ceiling'},

    'expander bleed': {
        'hasPreburner': False,
        'closed': False, 'hasTurbomachinery': True,
        'turbinePressureRatio': 15.0,
        'dischargeRatio': 1.3,
        'note': 'jacket heat, and the turbine flow is dumped. Escapes the pressure ceiling'},
}

# The specific impulse a dumped turbine exhaust delivers, as a fraction of the main chamber value.
# It is low because the exhaust is cool, fuel rich, and expanded through a short nozzle that is
# there to avoid a side force rather than to produce thrust.
DUMPED_EXHAUST_IMPULSE_FRACTION = 0.30    # [-]

# Pressure drops in the ladder from pump discharge to chamber, as fractions of chamber pressure.
# These are the consumers the pump is really working against, and the sum of them is why a pump
# discharge is never merely the chamber pressure.
PRESSURE_LADDER = {
    'injector':       {'fraction': 0.20, 'note': 'stability. See combustionDevices'},
    'cooling jacket': {'fraction': 0.15, 'note': 'the regenerative circuit'},
    'lines and valves': {'fraction': 0.05, 'note': 'plumbing'},
    'preburner injector': {'fraction': 0.20, 'note': 'closed cycles only, and it is on top'},
}

# Turbine inlet temperature by cycle. The gas generator and preburner cases are set by what the
# blade tolerates uncooled; the expander case is set by what the coolant picked up, which is a
# completely different and much lower limit.
CYCLE_TURBINE_TEMPERATURE = {
    'gas generator':               900.0,
    'staged combustion':           1000.0,
    'full flow staged combustion': 1000.0,
    'expander':                    500.0,
    'expander bleed':              500.0,
}    # [K]

def cycleDefinition(cycle: str) -> dict:

    """
    The definition for a named cycle, raising rather than defaulting on an unknown name.
    """

    if cycle not in ENGINE_CYCLES:
        raise CycleError(f"Unknown engine cycle '{cycle}'. Known: {sorted(ENGINE_CYCLES)}.",
                         context = createErrorContext(component = 'cycleUtils'))

    return dict(ENGINE_CYCLES[cycle])

def pressureLadder(chamberPressure: float, cycle: str) -> dict:

    """

    The pressure schedule from pump discharge down to the chamber.

    An open cycle pump has to overcome the injector, the cooling jacket and the plumbing. A closed
    cycle pump has to overcome all of that **and** push the whole flow through a turbine first,
    which means its discharge has to sit above the turbine inlet rather than above the chamber.

    That is the structural reason a staged combustion pump runs at roughly twice the chamber
    pressure while a gas generator pump runs at about a quarter above it.

    """

    definition = cycleDefinition(cycle)

    consumers = {}

    for name in ('injector', 'cooling jacket', 'lines and valves'):
        consumers[name] = PRESSURE_LADDER[name]['fraction'] * chamberPressure

    if not definition['hasTurbomachinery']:
        discharge = chamberPressure + sum(consumers.values())
        return {'dischargePressure': discharge, 'consumers': consumers,
                'turbineInlet': None, 'turbineExit': None,
                'dischargeRatio': discharge / chamberPressure}

    if definition['closed']:

        # the turbine exhaust has to enter the main injector, so it sits above chamber plus injector
        turbineExit  = chamberPressure + consumers['injector']
        turbineInlet = turbineExit * definition['turbinePressureRatio']

        # an expander cycle has no preburner: the fuel goes jacket, turbine, injector. Charging
        # it a preburner injector drop would overstate its pump discharge by a fifth of chamber
        # pressure, and it is the cycle least able to afford one.
        if definition['hasPreburner']:
            consumers['preburner injector'] = (PRESSURE_LADDER['preburner injector']['fraction']
                                               * chamberPressure)

        discharge = (turbineInlet + consumers.get('preburner injector', 0.0)
                     + consumers['cooling jacket'] + consumers['lines and valves'])

    else:

        # the turbine exhausts overboard, so the pump only has to reach the chamber
        discharge    = chamberPressure + sum(consumers.values())
        turbineInlet = discharge
        turbineExit  = turbineInlet / definition['turbinePressureRatio']

    return {'dischargePressure': discharge,
            'consumers':         consumers,
            'turbineInlet':      turbineInlet,
            'turbineExit':       turbineExit,
            'dischargeRatio':    discharge / chamberPressure}
