
# -- Cryogenic Specific Heat [orbitalRockets common] -- #

'''

Specific heat of structural metals from liquid helium temperature to room temperature, from the
NIST cryogenic material properties curve fits.

Specific heat is the property that behaves least like its room-temperature value when a vehicle is
loaded. It falls steeply below about 100 K, so a chill-down computed with a handbook value
overstates the stored enthalpy of the hardware and therefore the propellant boiled off to remove
it. A single mean value does not fix that, because the mean depends on where the range ends: the
same stainless line has a mean of 400 J/(kg K) chilling to liquid oxygen and 331 chilling to liquid
hydrogen.

**So the enthalpy is integrated over the range that is actually being traversed**, and any mean
this module reports is the result of that integral rather than an input to it.

The fits are of the form

    log10(cp) = sum over n of a_n ( log10 T ) ** n

with cp in J/(kg K) and T in kelvin, evaluated over the range each fit states. Extrapolation is
refused rather than clamped: outside its range this functional form leaves the physical values
quickly, and a silently wrong specific heat produces a plausible chill-down mass.

Author: Sean Bowman
Date:   08/13/2026

'''

import numpy as np

try:
    from errors import InvalidInputError, createErrorContext
except ImportError:
    from .errors import InvalidInputError, createErrorContext

# ------------------------------------------------------------------------------------------------ #
# -- NIST curve fits -- #
# ------------------------------------------------------------------------------------------------ #

# Read from the NIST cryogenic material properties database, https://trc.nist.gov/cryogenics/
# materials/materialproperties.htm, accessed 13 August 2026. Coefficients are transcribed in the
# order a, b, c, ... i as published, and `fitError` is the percentage the database states the fit
# holds to against its own data.
#
# Two things about this table are worth knowing before using it.
#
# 316 stainless is published as TWO fits meeting at 50 K, and both are carried rather than only the
# upper one, because the joint is a free check on the transcription: an error in either set shows
# up as a step at 50 K that neither set can hide.
#
# The database has no specific heat fit for Ti-6Al-4V or for Inconel 718. Both pages carry thermal
# conductivity and linear expansion only. Those two materials keep a constant mean and stay in the
# unvalidated register, which is a narrower gap than the one this module closes and it is stated
# rather than papered over.

CRYOGENIC_SPECIFIC_HEAT_FITS = {

    'stainless 304': {
        'source':    'NIST cryogenic material properties, 304 Stainless (UNS S30400)',
        'fitError':  5.0,                       # [per cent] relative to the database's own data
        'segments': [{'range': (4.0, 300.0),    # [K]
                      'coefficients': [22.0061, -127.5528, 303.647, -381.0098, 274.0328,
                                       -112.9212, 24.7593, -2.239153, 0.0]}]},

    'stainless 316': {
        'source':    'NIST cryogenic material properties, 316 Stainless (UNS S31600)',
        'fitError':  2.0,                       # [per cent]
        'segments': [{'range': (4.0, 50.0),     # [K]
                      'coefficients': [12.2486, -80.6422, 218.743, -308.854, 239.5296,
                                       -89.9982, 3.15315, 8.44996, -1.91368]},
                     {'range': (50.0, 300.0),   # [K]
                      'coefficients': [-1879.464, 3643.198, 76.70125, -6176.028, 7437.6247,
                                       -4305.7217, 1382.4627, -237.22704, 17.05262]}]},

    'aluminium 6061': {
        'source':    'NIST cryogenic material properties, 6061-T6 Aluminum (UNS A96061)',
        'fitError':  5.0,                       # [per cent]
        'segments': [{'range': (4.0, 300.0),    # [K]
                      'coefficients': [46.6467, -314.292, 866.662, -1298.3, 1162.27,
                                       -637.795, 210.351, -38.3094, 2.96344]}]},
}

# Materials with no fit of their own, mapped onto one that applies.
#
# Specific heat per unit mass in a dilute substitutional alloy is set by the lattice of the base
# metal, and 2219 is 93 per cent aluminium against 6061's 97. The copper it carries is heavier per
# atom and lowers cp per kilogram slightly, so this substitution is expected to run a few per cent
# high rather than to be exact. That is a stated approximation and not a measurement, which is why
# it is a separate table from the fits above.
SPECIFIC_HEAT_SUBSTITUTIONS = {
    'stainless 316L':  'stainless 316',
    'stainless 304L':  'stainless 304',
    'aluminium 2219':  'aluminium 6061',
    'aluminium 2195':  'aluminium 6061',
    'aluminium 7075':  'aluminium 6061',
}

# ------------------------------------------------------------------------------------------------ #
# -- Evaluation -- #
# ------------------------------------------------------------------------------------------------ #

def _resolveMaterial(material: str) -> str:

    '''
    Map a material onto the fit that covers it, or raise saying which materials are covered.
    '''

    if material in CRYOGENIC_SPECIFIC_HEAT_FITS:
        return material

    if material in SPECIFIC_HEAT_SUBSTITUTIONS:
        return SPECIFIC_HEAT_SUBSTITUTIONS[material]

    raise InvalidInputError(
        f'No cryogenic specific heat curve for \'{material}\'. Fits are available for '
        f'{sorted(CRYOGENIC_SPECIFIC_HEAT_FITS)}, and '
        f'{sorted(SPECIFIC_HEAT_SUBSTITUTIONS)} are mapped onto them. The NIST database carries no '
        f'specific heat fit for Ti-6Al-4V or Inconel 718, so a caller needing either has to supply '
        f'a mean value and record where it came from.',
        context = createErrorContext(component = 'cryogenicProperties'))

def specificHeat(material: str, temperature) -> float:

    '''

    Specific heat in J/(kg K) at a temperature in kelvin, from the NIST curve fit.

    Accepts a scalar or an array. Outside the fit range this raises rather than clamping, because
    the polynomial is in log10(T) and leaves the physical values quickly once it is extrapolated.

    '''

    entry = CRYOGENIC_SPECIFIC_HEAT_FITS[_resolveMaterial(material)]

    values = np.atleast_1d(np.asarray(temperature, dtype = float))

    low  = min(segment['range'][0] for segment in entry['segments'])
    high = max(segment['range'][1] for segment in entry['segments'])

    if np.any(values < low) or np.any(values > high):
        raise InvalidInputError(
            f'The {material} specific heat fit covers {low:.0f} to {high:.0f} K and was asked for '
            f'{np.min(values):.1f} to {np.max(values):.1f} K. This fit is a polynomial in '
            f'log10(T) and extrapolating it produces a confidently wrong number rather than an '
            f'error.',
            context = createErrorContext(component = 'cryogenicProperties'))

    result = np.empty_like(values)

    for index, value in enumerate(values):

        # The last segment whose lower bound the temperature clears. Segments are published in
        # ascending order and meet at their shared bound, where either is correct.
        segment = next(candidate for candidate in reversed(entry['segments'])
                       if value >= candidate['range'][0])

        exponent = np.log10(value)

        result[index] = 10.0 ** np.polyval(list(reversed(segment['coefficients'])), exponent)

    return float(result[0]) if np.isscalar(temperature) or np.ndim(temperature) == 0 else result

def meanSpecificHeat(material: str, lowTemperature: float, highTemperature: float,
                     points: int = 2001) -> float:

    '''

    Enthalpy-averaged specific heat over a temperature range, in J/(kg K).

    This is the integral divided by the span rather than the value at the midpoint, so multiplying
    it by the span returns the enthalpy exactly. **The result depends strongly on where the range
    ends**, which is the reason this is a function and not a table.

    '''

    if not np.isfinite(lowTemperature) or not np.isfinite(highTemperature):
        raise InvalidInputError(
            'A mean specific heat needs two finite temperatures.',
            context = createErrorContext(component = 'cryogenicProperties'))

    if highTemperature <= lowTemperature:
        raise InvalidInputError(
            f'The range {lowTemperature:.1f} to {highTemperature:.1f} K is empty or reversed. A '
            f'mean over no span is not a specific heat.',
            context = createErrorContext(component = 'cryogenicProperties'))

    grid = np.linspace(lowTemperature, highTemperature, points)

    return float(np.trapezoid(specificHeat(material, grid), grid)
                 / (highTemperature - lowTemperature))

def enthalpyChange(material: str, mass: float, lowTemperature: float,
                   highTemperature: float) -> float:

    '''

    Enthalpy a mass of metal gives up cooling from the high temperature to the low one, in joules.

    The quantity a chill-down actually needs. Reported separately from the mean so that a caller
    never has to multiply a mean by a span itself and get the span wrong.

    '''

    if mass < 0.0:
        raise InvalidInputError(
            f'A mass of {mass} kg has no enthalpy.',
            context = createErrorContext(component = 'cryogenicProperties'))

    return mass * meanSpecificHeat(material, lowTemperature,
                                   highTemperature) * (highTemperature - lowTemperature)
