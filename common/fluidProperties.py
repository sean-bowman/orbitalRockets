
# -- Fluid Property Accessors [orbitalRockets common] -- #

'''

Unified fluid property access, shared by every domain that touches a fluid.

fluidProps is the function to call. It dispatches to the best available backend:

    1. A correlation table for species no equation of state models (currently hydrazine)
    2. REFPROP via refWrap, wherever a REFPROP installation is found
    3. CoolProp via coolWrap, as the automatic fallback

All three share one I/O contract and one unit system, mass-base SI, so a call site runs
unchanged on a machine with or without a REFPROP license.

Also carries the species molar mass table and the two conversions that need it: leak rates
between volumetric and mass units, and SCFM.

Author: Sean Bowman
Date:   08/06/2026

'''

import os
from typing import Any

import numpy as np

try:
    from units import *
except ImportError:
    from .units import *

# Permissive numeric-input alias: these helpers accept arrays, lists, or scalars
# interchangeably. Using this keeps static analysis from flagging valid array-like
# call sites while documenting intent.
ArrayLike = np.ndarray | list | float | int

# -- Weird imports that people might not have -- #

# ctREFPROP (This needs to be a global import instead of a nested local import because refWrap
# sometimes is called within a loop and re-importing this module each time refWrap is called
# makes it take FOREVER)
try:
    from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
except ImportError:
    print(f'Uh oh, ctREFPROP isn\'t found. You won\'t be able to call REFPROP. You can pip install that with \'pip install -U ctREFPROP\'')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Fluid Property Functions -- #
#--------------------------------------------------------------------------------------------------------------------------#

def refWrap(species: str, inputTypes: str, outputTypes: str, inputTypeFirst: float, inputTypeSecond: float, mixtureRatio: list[float] = [1.0], units: bool = False) -> float | list[float] | str | list[str]:

    '''

    This function acts as a simple wrapper for REFPROP.

    ---------------------------------------------------------------------------
                                    INPUTS
    ---------------------------------------------------------------------------
    - Fluid Species                                   [case insensitive string]

    - Input Types         [case insensitive string of 2 values (no delimiters)]
        Supported Inputs:
        + 'T'                                    specifying fluid [Temperature]
        + 'P'                                       specifying fluid [Pressure]
        + 'D'                                        specifying fluid [Density]
        + 'E'                                specifying fluid [Internal Energy]
        + 'H'                                       specifying fluid [Enthalpy]
        + 'S'                                        specifying fluid [Entropy]
        + 'Q'                                        specifying fluid [Quality]
        i.e. 'TP' specifies [Temperature, Pressure] inputs

    - Output Types                    [space delimited case insensitive string]
        i.e. 'D Cp Cp/Cv' specifies [density, specific heat, gamma] outputs

    - First / Second Input Type                                  [Mass Base SI]

    ***NOTE:
    All input types are presented in [Mass Base SI] units i.e. [K, Pa, kg/m^3, etc]

    ---------------------------------------------------------------------------
                                    OUTPUTS
    ---------------------------------------------------------------------------
    refWrap can handle an arbitrary number of outputs, saved in the order that
    the outputs are specified.

    Example function call 1: Thermophysical Properties

    rho, mu, K, Cp = refWrap('O2', 'TP', 'D VIS TCX Cp', 350, 5e6)

    Example function call 2: Saturation Properties

    tSat = refWrap('O2', 'PQ', 'T', 101325, 0)

    To call the phase of a fluid, pass the string 'PHASE' as the output type. Do so separately from
    other thermophysical property calls, because the Python output structure stores the phase string
    in hUnits rather than in Output.

    ---------------------------------------------------------------------------
    LINK TO REFPROP DOCUMENTATION
    ---------------------------------------------------------------------------
    https://refprop-docs.readthedocs.io/en/latest/DLL/high_level.html#f/_/REFPROPdll

    *NOTE*:
    - A value of -9999990 is returned if no value is calculated for a given input.
    - A value of -9999970 is returned if an error occurs during calculation.
    - A value of -9999950 is returned if no value is stored in the Output structure but values
      exist in other fields (i.e. when calling the phase of a fluid).

    '''

    # Define location where REFPROP is stored and let the dll know
    rootUsers                = os.path.expanduser('~') + '\\REFPROP'
    rootProgramFilesx86      = 'C:\\Program Files (x86)\\REFPROP'
    REFPROPinUsers           = os.path.exists(rootUsers)
    REFPROPinProgramFilesx86 = os.path.exists(rootProgramFilesx86)

    if (REFPROPinUsers is False) and (REFPROPinProgramFilesx86 is False):
        raise Exception(f'Uh oh, REFPROP isn\'t found at Users\\%YOURUSERNAME%\\REFPROP or C:\\Program Files (x86)\\REFPROP')

    # Will default to User directory even if both are True because if statements check top-down
    if REFPROPinUsers is True:
        RP = REFPROPFunctionLibrary(rootUsers)
        RP.SETPATHdll(rootUsers)
    elif REFPROPinProgramFilesx86 is True:
        RP = REFPROPFunctionLibrary(rootProgramFilesx86)
        RP.SETPATHdll(rootProgramFilesx86)

    # Separate the outputs and count them
    outputTypesSplit = outputTypes.split(' ')
    numOutputs       = len(outputTypesSplit)

    iUnits = RP.GETENUMdll(0, 'MASS BASE SI').iEnum # Setting units to Mass Base SI
    iMass  = 1                                      # 0: molar fractions; 1: mass fractions (mixtures)
    iFlag  = 0                                      # 0: don't call SATSPLN; 1: call SATSPLN

    # Structure the call to REFPROP
    x = RP.REFPROPdll(species, inputTypes, outputTypes, iUnits, iMass, iFlag, inputTypeFirst, inputTypeSecond, mixtureRatio)

    # If only one value output is asked for, return it
    if (numOutputs == 1) and (outputTypesSplit[0] != 'PHASE') and (units is False):
        return x.Output[0]
    # If unit output is asked for, or if the only output is the fluid phase, return that instead
    elif ((numOutputs == 1) and (outputTypesSplit[0] != 'PHASE') and (units is True)) or (outputTypes == 'PHASE'):
        return x.hUnits
    # If multiple unit outputs are asked for, warn that only the unit of the first output is returned
    elif (numOutputs > 1) and (outputTypesSplit[0] != 'PHASE') and (units is True):
        print(f'Only first output can return units, sorry. If you want multiple units you have to make multiple calls.')
        return x.hUnits
    # Otherwise, make a list to hold all of the outputs and unpack each one into the subsequent output
    else:
        return list(outputValue for outputValue in x.Output[0:numOutputs])

def coolWrap(species: str, inputTypes: str, outputTypes: str, inputTypeFirst: float, inputTypeSecond: float, mixtureRatio: list[float] = [1.0], units: bool = False) -> float | list[float] | str | list[str]:

    '''

    CoolProp implementation of refWrap, used as a fallback when REFPROP is not installed. The
    signature, unit system (mass-base SI), and return-value behavior mirror refWrap exactly, so the
    two are interchangeable behind the fluidProps dispatcher.

    See refWrap for the full description of inputs and outputs. Differences / limitations:

    - Single-component fluids only. CoolProp's high-level PropsSI cannot take mass-fraction mixtures
      without the REFPROP backend, so a ';'-delimited species (or a mixtureRatio with more than one
      entry) raises NotImplementedError. Install REFPROP if you need mixtures.
    - 'Cp/Cv' is returned as the computed ratio Cpmass / Cvmass.
    - 'PHASE' is returned as a REFPROP-style phase descriptor mapped from CoolProp's PhaseSI.
    - Trivial properties (TCRIT, PCRIT, ...) are evaluated from the fluid name alone.

    The REFPROP <-> CoolProp mapping tables live inside this function (rather than at module scope)
    so the top level of utils.py stays cleanly collapsible into function and class handles.

    '''

    # Lazy import so utils.py still loads on machines without CoolProp installed.
    try:
        import CoolProp.CoolProp as CP
    except ImportError:
        raise ImportError('CoolProp isn\'t installed, so coolWrap can\'t run. Install it with \'pip install CoolProp\'.')

    # -- REFPROP -> CoolProp mapping tables -- #

    # refWrap/REFPROP input-pair single-character codes -> CoolProp PropsSI input keys. CoolProp
    # PropsSI is mass-base SI by default (D [kg/m^3], H [J/kg], S [J/kg-K], U [J/kg]), matching the
    # 'MASS BASE SI' unit system refWrap requests from REFPROP, so values are directly interchangeable.
    inputKeys = {
        'T': 'T',   # Temperature        [K]
        'P': 'P',   # Pressure           [Pa]
        'D': 'D',   # Density            [kg/m^3]
        'H': 'H',   # Enthalpy           [J/kg]
        'S': 'S',   # Entropy            [J/kg-K]
        'Q': 'Q',   # Vapor quality      [-]
        'E': 'U',   # Internal energy    [J/kg]  (REFPROP 'E' -> CoolProp 'U')
        'U': 'U',
    }

    # refWrap/REFPROP output codes -> CoolProp PropsSI output key.
    outputKeys = {
        'T':       'T',         # Temperature                 [K]
        'P':       'P',         # Pressure                    [Pa]
        'D':       'D',         # Density                     [kg/m^3]
        'H':       'H',         # Enthalpy                    [J/kg]
        'S':       'S',         # Entropy                     [J/kg-K]
        'E':       'U',         # Internal energy             [J/kg]
        'U':       'U',
        'Cp':      'C',         # Isobaric specific heat      [J/kg-K]
        'Cv':      'O',         # Isochoric specific heat     [J/kg-K]
        'VIS':     'V',         # Dynamic viscosity           [Pa-s]
        'TCX':     'L',         # Thermal conductivity        [W/m-K]
        'W':       'A',         # Speed of sound              [m/s]
        'PRANDTL': 'PRANDTL',   # Prandtl number              [-]
        'STN':     'I',         # Surface tension             [N/m]
        'Q':       'Q',         # Vapor quality               [-]
    }

    # Trivial (state-independent) outputs that CoolProp evaluates from the fluid name alone.
    trivialKeys = {
        'TCRIT': 'Tcrit',     # Critical temperature  [K]
        'PCRIT': 'pcrit',     # Critical pressure     [Pa]
        'DCRIT': 'rhocrit',   # Critical density      [kg/m^3]
        'TMIN':  'Tmin',      # Minimum temperature   [K]
        'TMAX':  'Tmax',      # Maximum temperature   [K]
        'M':     'molar_mass' # Molar mass            [kg/mol]
    }

    # SI unit strings returned when units = True, keyed by refWrap output code.
    unitStrings = {
        'T': 'K', 'P': 'Pa', 'D': 'kg/m^3', 'H': 'J/kg', 'S': 'J/(kg.K)', 'E': 'J/kg', 'U': 'J/kg',
        'Cp': 'J/(kg.K)', 'Cv': 'J/(kg.K)', 'Cp/Cv': '', 'VIS': 'Pa.s', 'TCX': 'W/(m.K)', 'W': 'm/s',
        'PRANDTL': '', 'STN': 'N/m', 'Q': '', 'TCRIT': 'K', 'PCRIT': 'Pa', 'DCRIT': 'kg/m^3', 'M': 'kg/mol'
    }

    # REFPROP species names CoolProp does not resolve through its own alias table.
    refpropToCoolProp = {
        'NITROUS': 'NitrousOxide',
        'R740':    'Argon',
        'LOX':     'Oxygen',
        'GOX':     'Oxygen',
        'LN2':     'Nitrogen',
        'GN2':     'Nitrogen',
        'GHE':     'Helium',
        'LHE':     'Helium',
        'IPA':     'Isopropanol'
    }

    # CoolProp PhaseSI strings -> the phase descriptors refWrap/REFPROP returns.
    phaseMap = {
        'liquid':               'Subcooled liquid',
        'supercritical_liquid': 'Subcooled liquid',
        'gas':                  'Superheated gas',
        'supercritical_gas':    'Superheated gas',
        'supercritical':        'Supercritical',
        'twophase':             'Two-phase'
    }

    # Reject mixtures: the high-level CoolProp interface used here is single-component only.
    if (';' in species) or (len(mixtureRatio) > 1):
        raise NotImplementedError('coolWrap (CoolProp fallback) supports single-component fluids only. Install REFPROP to evaluate mixtures.')

    # Translate the REFPROP species name into a CoolProp-resolvable fluid name
    cleanName = species.strip()
    fluid     = refpropToCoolProp.get(cleanName.upper(), cleanName)

    # Separate the outputs and count them (identical convention to refWrap)
    outputTypesSplit = outputTypes.split(' ')
    numOutputs       = len(outputTypesSplit)

    # Translate the two input-pair codes into CoolProp keys up front
    in1Key = inputKeys.get(inputTypes[0], inputKeys.get(inputTypes[0].upper()))
    in2Key = inputKeys.get(inputTypes[1], inputKeys.get(inputTypes[1].upper()))
    if (in1Key is None) or (in2Key is None):
        raise KeyError(f'coolWrap has no CoolProp mapping for input types \'{inputTypes}\'.')

    # -- Units request short-circuit -- #
    if units and outputTypes != 'PHASE':
        if numOutputs > 1:
            print('Only first output can return units, sorry. If you want multiple units you have to make multiple calls.')
        firstCode = outputTypesSplit[0]
        return unitStrings.get(firstCode, unitStrings.get(firstCode.upper(), ''))

    # Evaluate a single output code at the requested thermodynamic state
    def evaluate(code: str):

        codeUpper = code.upper()

        # Phase: map CoolProp's descriptor onto the REFPROP-style string refWrap returns
        if codeUpper == 'PHASE':
            phase = CP.PhaseSI(in1Key, inputTypeFirst, in2Key, inputTypeSecond, fluid)
            return phaseMap.get(phase, phase)

        # Ratio of specific heats has no direct PropsSI key; compute it
        if codeUpper == 'CP/CV':
            cp = CP.PropsSI('C', in1Key, inputTypeFirst, in2Key, inputTypeSecond, fluid)
            cv = CP.PropsSI('O', in1Key, inputTypeFirst, in2Key, inputTypeSecond, fluid)
            return cp / cv

        # Trivial (state-independent) properties evaluate from the fluid name alone
        if codeUpper in trivialKeys:
            return CP.PropsSI(trivialKeys[codeUpper], fluid)

        # Standard state-dependent property
        cpKey = outputKeys.get(code, outputKeys.get(codeUpper))
        if cpKey is None:
            raise KeyError(f'coolWrap has no CoolProp mapping for output code \'{code}\'. Add it to the outputKeys table or use REFPROP.')
        return CP.PropsSI(cpKey, in1Key, inputTypeFirst, in2Key, inputTypeSecond, fluid)

    # -- Match refWrap's return-shape rules -- #
    if outputTypes == 'PHASE':
        return evaluate('PHASE')
    if numOutputs == 1:
        return evaluate(outputTypesSplit[0])
    return [evaluate(code) for code in outputTypesSplit]

def hydrazineProps(outputTypes: str, temperature: float, units: bool = False) -> float | list[float] | str | list[str]:

    '''

    Correlation-based liquid properties for anhydrous hydrazine (N2H4).

    Neither REFPROP nor CoolProp ships an equation of state for hydrazine, so the monopropellant
    side of this library would be dead in the water without a correlation table. These fits are
    built from the standard references (Schmidt, 'Hydrazine and its Derivatives'; NASA SP-8087;
    MIL-PRF-26536 property tables) and are accurate to roughly 1-2 % over the liquid range.

    Only saturated-liquid properties are returned. Hydrazine is a nearly incompressible liquid over
    any feed system pressure of interest, so pressure dependence is neglected. That is a real
    limitation and it is deliberate: the alternative is an EOS this library does not have.

    ---------------------------------------------------------------------------
                                    INPUTS
    ---------------------------------------------------------------------------
    - outputTypes                     [space delimited case insensitive string]
        Same output codes as refWrap. Supported here:
        'D'     density                     [kg/m^3]
        'VIS'   dynamic viscosity           [Pa-s]
        'TCX'   thermal conductivity        [W/m-K]
        'Cp'    isobaric specific heat      [J/kg-K]
        'STN'   surface tension             [N/m]
        'P'     saturation vapor pressure   [Pa]
        'H'     heat of vaporization        [J/kg]
        'M'     molar mass                  [kg/mol]
        'TCRIT' critical temperature        [K]
        'PCRIT' critical pressure           [Pa]
        'TMIN'  freezing point              [K]
        'TNBP'  normal boiling point        [K]

    - temperature                                                          [K]

    ---------------------------------------------------------------------------
                                VALIDITY RANGE
    ---------------------------------------------------------------------------
    275 K to 450 K. Below 274.69 K hydrazine freezes, which is itself a driving fluid system
    constraint: heater power and line routing on a hydrazine spacecraft exist almost entirely to
    keep the propellant above that point. A call below the freezing point returns values but prints
    a warning, because a frozen-line analysis is usually the thing you actually wanted to catch.

    Example:

    rho, mu, cp = hydrazineProps('D VIS Cp', 293.15)

    '''

    # -- Fixed-point properties -- #
    molarMass            = 32.0451e-3   # kg/mol
    criticalTemperature  = 653.0        # K
    criticalPressure     = 14.7e6       # Pa
    freezingTemperature  = 274.69       # K, 1.54 degC -- the design driver for heater sizing
    normalBoilingPoint   = 386.65       # K, 113.5 degC
    heatOfVaporizationRT = 1.395e6      # J/kg at 298.15 K (44.7 kJ/mol)

    # Clausius-Clapeyron coefficient, fit through the 25 degC vapor pressure (1.92 kPa) and the
    # normal boiling point (101.325 kPa). Equivalent to a latent heat of about 43 kJ/mol.
    clausiusCoefficient  = 5166.5       # K, dHvap / R

    if temperature < freezingTemperature:
        print(f'Warning: hydrazineProps called at {temperature:.2f} K, below the {freezingTemperature:.2f} K freezing point. Values are extrapolated.')

    temperatureCelsius = temperature - DEGC_OFFSET

    def evaluate(code: str):

        codeUpper = code.upper()

        # Density, Schmidt polynomial in degC, converted from g/cm^3 to kg/m^3
        if codeUpper == 'D':
            return 1.0e3 * (1.02540 - 8.4093e-4 * temperatureCelsius - 2.5217e-7 * temperatureCelsius**2)

        # Dynamic viscosity, Andrade fit anchored on 0.974 cP at 20 degC and 0.913 cP at 25 degC
        if codeUpper == 'VIS':
            return 2.0565e-5 * np.exp(1130.9 / temperature)

        # Thermal conductivity, linear fit anchored on 0.371 W/m-K at 25 degC
        if codeUpper == 'TCX':
            return 0.371 - 3.6e-4 * (temperature - 298.15)

        # Isobaric specific heat, linear fit anchored on 3084 J/kg-K at 25 degC
        if codeUpper == 'CP':
            return 3084.0 + 4.6 * (temperature - 298.15)

        # Surface tension, linear fit anchored on 66.7 mN/m at 25 degC
        if codeUpper == 'STN':
            return 66.7e-3 - 1.4e-4 * (temperature - 298.15)

        # Saturation vapor pressure, Clausius-Clapeyron anchored at the normal boiling point
        if codeUpper == 'P':
            return PA_PER_ATM * np.exp(-clausiusCoefficient * (1.0 / temperature - 1.0 / normalBoilingPoint))

        # Heat of vaporization, Watson correlation from the 25 degC reference value
        if codeUpper == 'H':
            reducedNow       = (1.0 - temperature / criticalTemperature)
            reducedReference = (1.0 - 298.15 / criticalTemperature)
            return heatOfVaporizationRT * (reducedNow / reducedReference)**0.38

        if codeUpper == 'M':
            return molarMass
        if codeUpper == 'TCRIT':
            return criticalTemperature
        if codeUpper == 'PCRIT':
            return criticalPressure
        if codeUpper == 'TMIN':
            return freezingTemperature
        if codeUpper == 'TNBP':
            return normalBoilingPoint

        raise KeyError(f'hydrazineProps has no correlation for output code \'{code}\'.')

    unitStrings = {
        'D': 'kg/m^3', 'VIS': 'Pa.s', 'TCX': 'W/(m.K)', 'CP': 'J/(kg.K)', 'STN': 'N/m',
        'P': 'Pa', 'H': 'J/kg', 'M': 'kg/mol', 'TCRIT': 'K', 'PCRIT': 'Pa', 'TMIN': 'K', 'TNBP': 'K'
    }

    outputTypesSplit = outputTypes.split(' ')
    numOutputs       = len(outputTypesSplit)

    if units:
        if numOutputs > 1:
            print('Only first output can return units, sorry. If you want multiple units you have to make multiple calls.')
        return unitStrings.get(outputTypesSplit[0].upper(), '')

    if numOutputs == 1:
        return evaluate(outputTypesSplit[0])
    return [evaluate(code) for code in outputTypesSplit]

def fluidProps(species: str, inputTypes: str, outputTypes: str, inputTypeFirst: ArrayLike, inputTypeSecond: ArrayLike, mixtureRatio: list[float] = [1.0], units: bool = False) -> Any:

    '''

    Unified fluid-property accessor, and the function every component class in this library calls.

    fluidProps is a thin dispatcher with the exact same I/O contract as refWrap (see refWrap for the
    full input/output description). It routes each call to the best available backend:

        1. Correlation table    -- species with no equation of state anywhere (currently hydrazine).
        2. REFPROP via refWrap  -- used whenever a REFPROP installation is found (highest fidelity,
                                   supports mixtures).
        3. CoolProp via coolWrap -- automatic fallback when REFPROP is not installed (single-
                                    component fluids only).

    This lets the same call site run on machines with or without a REFPROP license. To force a
    specific backend, call refWrap, coolWrap or hydrazineProps directly.

    The REFPROP-availability check is cached on the function object (fluidProps.refpropAvailable) so
    hot loops don't stat the filesystem on every call.

    ---------------------------------------------------------------------------
                                    EXAMPLE
    ---------------------------------------------------------------------------

    rho, mu, K, Cp = fluidProps('O2', 'TP', 'D VIS TCX Cp', 350, 5e6)

    returns density, dynamic viscosity, thermal conductivity, and isobaric specific heat for oxygen
    at 350 [K] and 5 [MPa], using REFPROP if present and CoolProp otherwise.

    rho = fluidProps('N2H4', 'TP', 'D', 293.15, 2.5e6)

    returns hydrazine density from the built-in correlation table, ignoring the pressure input.

    '''

    # -- Correlation-table species -- #
    # Hydrazine has no EOS in either backend. Route it before the backend check so the call site
    # never has to know which species are modeled by which tool.
    if species.strip().upper() in ('N2H4', 'HYDRAZINE'):
        temperatureIndex = inputTypes.upper().find('T')
        if temperatureIndex < 0:
            raise KeyError(f'Hydrazine properties are correlated against temperature only. Input types \'{inputTypes}\' contain no \'T\'.')
        temperature = inputTypeFirst if temperatureIndex == 0 else inputTypeSecond
        return hydrazineProps(outputTypes, temperature, units = units)

    # Cache the REFPROP-availability check on the function object on first call
    if not hasattr(fluidProps, 'refpropAvailable'):
        rootUsers           = os.path.expanduser('~') + '\\REFPROP'
        rootProgramFilesx86 = 'C:\\Program Files (x86)\\REFPROP'
        fluidProps.refpropAvailable = os.path.exists(rootUsers) or os.path.exists(rootProgramFilesx86)

    if fluidProps.refpropAvailable:
        return refWrap(species, inputTypes, outputTypes, inputTypeFirst, inputTypeSecond, mixtureRatio = mixtureRatio, units = units)

    return coolWrap(species, inputTypes, outputTypes, inputTypeFirst, inputTypeSecond, mixtureRatio = mixtureRatio, units = units)

#--------------------------------------------------------------------------------------------------------------------------#
# -- Species Data and Derived Conversions -- #
#--------------------------------------------------------------------------------------------------------------------------#

def speciesMolarMass(species: str) -> float:

    '''

    Molar mass [kg/mol] for the gases that show up in leak testing and pressurization work.

    The lookup exists because the leak-rate conversions need a molar mass to move between volumetric
    (scc/s) and mass (lbm/yr) units, and because helium is almost never the service fluid: leak
    checks are run on helium and then scaled to the fluid the hardware actually sees.

    Falls back to a REFPROP/CoolProp query if the species is not in the table.

    '''

    molarMassTable = {
        'HE':        4.002602e-3,   # helium, the universal leak-check tracer
        'HELIUM':    4.002602e-3,
        'H2':        2.01588e-3,    # hydrogen, the worst-case leaker
        'HYDROGEN':  2.01588e-3,
        'N2':        28.01348e-3,   # nitrogen, the usual purge and pressurant gas
        'NITROGEN':  28.01348e-3,
        'GN2':       28.01348e-3,
        'O2':        31.9988e-3,    # oxygen
        'OXYGEN':    31.9988e-3,
        'GOX':       31.9988e-3,
        'AIR':       28.9647e-3,
        'AR':        39.948e-3,
        'ARGON':     39.948e-3,
        'CH4':       16.04246e-3,   # methane
        'METHANE':   16.04246e-3,
        'CO2':       44.0095e-3,
        'N2O':       44.0128e-3,    # nitrous oxide
        'NH3':       17.03052e-3,   # ammonia, the cat bed decomposition intermediate
        'N2H4':      32.0451e-3,    # hydrazine
        'HYDRAZINE': 32.0451e-3,
        'WATER':     18.01528e-3,
        'H2O':       18.01528e-3
    }

    key = species.strip().upper()
    if key in molarMassTable:
        return molarMassTable[key]

    # Not in the table: ask the property backend. REFPROP and CoolProp both return kg/mol for 'M'.
    return float(fluidProps(species, 'TP', 'M', 298.15, PA_PER_ATM))

def leakRateConvert(value: float, fromUnit: str, toUnit: str, species: str = 'He', temperature: float = LEAK_STD_TEMPERATURE) -> float:

    '''

    Convert between every leak-rate unit a fluid system specification is ever written in.

    Leak specs are a minefield because three different families of unit are in use and they are not
    interchangeable without knowing the gas:

        Throughput (pressure x volume per time):  Pa-m^3/s, mbar-L/s, torr-L/s, atm-cc/s
        Standard volumetric:                      scc/s, sccm, sccs, slpm
        Mass:                                     kg/s, lbm/yr, g/yr

    Throughput and standard-volumetric units are interconvertible with nothing but the standard
    reference state. Converting either of them into a mass rate requires the molar mass, which is
    why species is an argument.

    ---------------------------------------------------------------------------
                                SUPPORTED UNITS
    ---------------------------------------------------------------------------
    'pam3s'    Pa-m^3/s        (SI throughput, the internal working unit)
    'mbarls'   mbar-L/s        (European vacuum industry standard)
    'torrls'   torr-L/s
    'atmccs'   atm-cm^3/s      (numerically identical to scc/s at 0 degC)
    'sccs'     std cm^3/s      (0 degC, 1 atm)
    'sccm'     std cm^3/min
    'slpm'     std L/min
    'kgs'      kg/s
    'gyr'      g/yr
    'lbmyr'    lbm/yr

    ---------------------------------------------------------------------------
                                    EXAMPLE
    ---------------------------------------------------------------------------

    A 1e-4 scc/s helium spec expressed as a mass loss per year:

    leakRateConvert(1e-4, 'sccs', 'lbmyr', species = 'He')   ->  approximately 1.24e-3 lbm/yr

    Note that scc/s is defined at 0 degC by the vacuum industry convention used here. Some specs
    define it at 20 degC or 70 degF instead, a 7 % difference; the temperature argument exists so
    that a spec written against a different reference state can be reproduced exactly.

    '''

    # Throughput equivalent of one standard cm^3, evaluated at the reference state. Working
    # everything through Pa-m^3/s keeps the conversion matrix to a single vector of factors.
    standardThroughput = LEAK_STD_PRESSURE * 1.0e-6   # Pa-m^3 per std cm^3 at the reference state

    # Molar flow per unit throughput at the reference temperature, from the ideal gas law.
    # Leak flows are always far below the pressures where real-gas corrections matter.
    molarPerThroughput = 1.0 / (R_UNIVERSAL * temperature)      # mol/(Pa-m^3)
    massPerThroughput  = molarPerThroughput * speciesMolarMass(species)  # kg/(Pa-m^3)

    # Conversion factors into the internal working unit, Pa-m^3/s
    toPaM3s = {
        'pam3s':  1.0,
        'mbarls': PA_PER_MBAR * M3_PER_L,                 # 0.1
        'torrls': PA_PER_TORR * M3_PER_L,                 # 0.1333
        'atmccs': standardThroughput,
        'sccs':   standardThroughput,
        'sccm':   standardThroughput / 60.0,
        'slpm':   standardThroughput * 1.0e3 / 60.0,
        'kgs':    1.0 / massPerThroughput,
        'gyr':    1.0e-3 / massPerThroughput / SECONDS_PER_YEAR,
        'lbmyr':  KG_PER_LBM / massPerThroughput / SECONDS_PER_YEAR
    }

    fromKey = fromUnit.strip().lower().replace('-', '').replace('/', '').replace('_', '')
    toKey   = toUnit.strip().lower().replace('-', '').replace('/', '').replace('_', '')

    if fromKey not in toPaM3s:
        raise KeyError(f'leakRateConvert does not recognize the source unit \'{fromUnit}\'. Supported: {sorted(toPaM3s.keys())}')
    if toKey not in toPaM3s:
        raise KeyError(f'leakRateConvert does not recognize the target unit \'{toUnit}\'. Supported: {sorted(toPaM3s.keys())}')

    return value * toPaM3s[fromKey] / toPaM3s[toKey]

def convertToSCFM(fluid: str, massFlowrate: float, temperature: float, pressure: float) -> float:

    '''

    Standard Cubic Feet per Minute flowrate conversion calculator.

    Input flowrate is in [kg/s]. The 'standard' state here is 60 degF and 1 atm, which is the US gas
    industry convention and is NOT the same as the 0 degC standard used for leak rates. Mixing the
    two is a 5 % error that hides very well inside a regulator sizing calculation.

    '''

    # Get fluid density at the standard state, not the flowing state. SCFM is a mass flow rate
    # wearing a volumetric costume; the density that matters is the one at the reference condition.
    standardDensity = fluidProps(fluid, 'TP', 'D', SCFM_STD_TEMPERATURE, SCFM_STD_PRESSURE)

    # Convert kg/s to standard m^3/s, then to ft^3/min
    standardVolumetricFlowrate = massFlowrate / standardDensity

    return standardVolumetricFlowrate / M3_PER_FT3 * 60.0
