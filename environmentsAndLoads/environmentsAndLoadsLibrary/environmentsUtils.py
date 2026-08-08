
# -- Domain-specific helpers [environmentsAndLoads] -- #

'''

Spectral integration, decibel arithmetic and the margin policy constants this domain runs on.

Named environmentsUtils rather than utils deliberately. Every domain library in this repository
has a utils.py re-exporting the shared foundation, and they all resolve to the same 'utils' entry
in sys.modules when more than one domain is imported in a single process. That works by accident
for the names every domain re-exports and fails for anything only one domain defines.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np

def _bootstrapCommon() -> None:

    '''
    Locate orbitalRockets/common and put it on sys.path, independently of utils.py.
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

EnvironmentsAndLoadsError = EngineeringError

# ------------------------------------------------------------------------------------------------ #
# -- Margin Policy Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The margin ladder every environment specification climbs. Each step has a distinct reason, and
# the reasons are what make the numbers defensible rather than conventional.
#
#   flight limit level (MPE)  the maximum predicted environment, a statistical statement
#   acceptance level          = MPE. Screens workmanship on flight hardware
#   qualification level       = MPE + 3 dB (random) or + 6 dB (shock). Demonstrates design margin
#
# The 3 dB is not arbitrary: it is a factor of two in PSD, which is roughly one standard deviation
# of the lot-to-lot and unit-to-unit variability seen in practice.

QUALIFICATION_MARGIN_RANDOM   = 3.0    # [dB], over the maximum predicted environment
QUALIFICATION_MARGIN_SHOCK    = 6.0    # [dB], shock scatter is larger, so the margin is larger
QUALIFICATION_MARGIN_ACOUSTIC = 3.0    # [dB]

# Qualification runs longer as well as harder, to demonstrate life rather than survival.
QUALIFICATION_DURATION_FACTOR = 2.0    # [-], times the acceptance duration per axis
ACCEPTANCE_DURATION_DEFAULT   = 60.0   # [s], per axis, the common workmanship screen

# Miner's rule fatigue exponent for random vibration duration scaling. b = 4 is the NASA and MIL
# default for aluminium structure. It is an assumption, not a measurement, and it is the weakest
# link in any duration-scaled specification.
MINER_FATIGUE_EXPONENT = 4.0    # [-]

# The statistical basis of a maximum predicted environment. P95/50 is the common aerospace choice:
# the 95th percentile with 50 percent confidence.
NORMAL_TOLERANCE_FACTORS = {
    'P95/50': 1.645,   # [-], 95th percentile, 50 % confidence
    'P95/90': 2.145,   # [-], 95th percentile, 90 % confidence. Used where samples are few
    'P99/90': 3.000,   # [-], 99th percentile, 90 % confidence
    'P50/50': 0.000,   # [-], the mean. Not a maximum predicted environment
}

# ------------------------------------------------------------------------------------------------ #
# -- Decibel Arithmetic -- #
# ------------------------------------------------------------------------------------------------ #

def decibelToRatio(decibels: float, quantity: str = 'power') -> float:

    '''

    Convert a decibel change into a linear ratio.

    The distinction matters and it is the commonest error in this subject. A PSD is a power
    quantity, so +3 dB doubles it. An acceleration amplitude or an SRS level is an amplitude
    quantity, so +6 dB doubles it. Applying the wrong one is a factor of two on the test level.

    '''

    if quantity == 'power':
        return 10.0 ** (decibels / 10.0)
    if quantity == 'amplitude':
        return 10.0 ** (decibels / 20.0)

    raise InvalidInputError(
        f'quantity must be \'power\' or \'amplitude\', got \'{quantity}\'.',
        context = createErrorContext(component = 'environmentsAndLoads'))

def ratioToDecibel(ratio: float, quantity: str = 'power') -> float:

    '''
    The inverse of decibelToRatio.
    '''

    if ratio <= 0.0:
        raise InvalidInputError('Ratio must be positive to take its logarithm.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    if quantity == 'power':
        return 10.0 * np.log10(ratio)
    if quantity == 'amplitude':
        return 20.0 * np.log10(ratio)

    raise InvalidInputError(
        f'quantity must be \'power\' or \'amplitude\', got \'{quantity}\'.',
        context = createErrorContext(component = 'environmentsAndLoads'))

# ------------------------------------------------------------------------------------------------ #
# -- Spectral Integration -- #
# ------------------------------------------------------------------------------------------------ #

def segmentSlope(lowerFrequency: float, lowerDensity: float,
                 upperFrequency: float, upperDensity: float) -> float:

    '''

    Slope of a PSD segment in dB per octave, the way breakpoint tables are always written.

        slope = 10 log10(W2/W1) / log2(f2/f1)

    '''

    if lowerFrequency <= 0.0 or upperFrequency <= 0.0:
        raise InvalidInputError('Frequencies must be positive on a log-log spectrum.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    if lowerDensity <= 0.0 or upperDensity <= 0.0:
        raise InvalidInputError('Spectral densities must be positive.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    return (10.0 * np.log10(upperDensity / lowerDensity)
            / np.log2(upperFrequency / lowerFrequency))

def integrateSegment(lowerFrequency: float, lowerDensity: float,
                     upperFrequency: float, upperDensity: float) -> float:

    '''

    Area under one log-log PSD segment, which is the mean square contribution of that band.

    A breakpoint table is straight lines on a log-log plot, so within a segment

        W(f) = W1 (f / f1)^n,    n = ln(W2/W1) / ln(f2/f1)

    and the integral has a closed form everywhere except n = -1, where it degenerates to a
    logarithm. That special case is a -3.01 dB/octave slope, which is not a contrived value: it is
    exactly the slope of many real specifications, so the singular branch gets exercised in
    practice rather than being a theoretical nicety.

    '''

    if lowerFrequency <= 0.0 or upperFrequency <= 0.0:
        raise InvalidInputError('Frequencies must be positive on a log-log spectrum.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    if upperFrequency <= lowerFrequency:
        raise InvalidInputError(
            f'Breakpoints must increase in frequency, got {lowerFrequency} then {upperFrequency}.',
            context = createErrorContext(component = 'environmentsAndLoads'))

    if lowerDensity <= 0.0 or upperDensity <= 0.0:
        raise InvalidInputError('Spectral densities must be positive.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    exponent = np.log(upperDensity / lowerDensity) / np.log(upperFrequency / lowerFrequency)

    if abs(exponent + 1.0) < 1.0e-9:
        # the -3.01 dB/octave case, where the integral is logarithmic
        return lowerDensity * lowerFrequency * np.log(upperFrequency / lowerFrequency)

    return (lowerDensity / lowerFrequency ** exponent
            * (upperFrequency ** (exponent + 1.0) - lowerFrequency ** (exponent + 1.0))
            / (exponent + 1.0))

def overallRms(breakpoints: list) -> float:

    '''

    Grms of a PSD breakpoint table, as a list of (frequency, density) pairs.

    Grms is the square root of the area under the PSD, and it is the single number everyone quotes.
    It is also nearly useless on its own: two spectra with the same Grms and different shapes damage
    hardware completely differently, because the damage depends on where the energy sits relative
    to the hardware's resonances.

    '''

    if len(breakpoints) < 2:
        raise InvalidInputError('A spectrum needs at least two breakpoints.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    meanSquare = 0.0
    for index in range(len(breakpoints) - 1):
        lowerFrequency, lowerDensity = breakpoints[index]
        upperFrequency, upperDensity = breakpoints[index + 1]
        meanSquare += integrateSegment(lowerFrequency, lowerDensity,
                                       upperFrequency, upperDensity)

    return np.sqrt(meanSquare)

def scaleSpectrum(breakpoints: list, decibels: float) -> list:

    '''

    Shift an entire spectrum by a decibel offset, treating the density as a power quantity.

    '''

    factor = decibelToRatio(decibels, quantity = 'power')

    return [(frequency, density * factor) for frequency, density in breakpoints]

def minerDurationScaling(originalDuration: float, targetDuration: float,
                         exponent: float = MINER_FATIGUE_EXPONENT) -> float:

    '''

    The decibel change equivalent to a change of test duration, under Miner's rule.

        W2 / W1 = (T1 / T2)^(1/b)

    Shortening a test raises the level to keep the accumulated damage equal. The exponent b is the
    slope of the S-N curve in log-log, taken as 4 for aluminium by convention.

    This is the most heavily leaned-on assumption in environmental testing and it deserves stating
    plainly: it presumes the damage mechanism is high cycle fatigue with a single exponent, that
    damage accumulates linearly, and that the failure mode does not change with level. A test
    shortened by a large factor can be raised to a level that excites a failure mode flight never
    would.

    '''

    if originalDuration <= 0.0 or targetDuration <= 0.0:
        raise InvalidInputError('Durations must be positive.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    if exponent <= 0.0:
        raise InvalidInputError('The fatigue exponent must be positive.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    ratio = (originalDuration / targetDuration) ** (1.0 / exponent)

    return ratioToDecibel(ratio, quantity = 'power')

def toleranceLimit(values: ArrayLike, basis: str = 'P95/50') -> dict:

    '''

    A maximum predicted environment from a sample, as mean plus k standard deviations.

    An environment specification is a statistical statement rather than a measurement, and the
    percentile and confidence are part of the specification. Quoting a level without them is
    quoting half a number.

    '''

    if basis not in NORMAL_TOLERANCE_FACTORS:
        raise InvalidInputError(
            f'Unknown basis \'{basis}\'. Known: {sorted(NORMAL_TOLERANCE_FACTORS)}.',
            context = createErrorContext(component = 'environmentsAndLoads'))

    sample = np.asarray(values, dtype = float)

    if sample.size < 2:
        raise InvalidInputError('A tolerance limit needs at least two samples.',
                                context = createErrorContext(component = 'environmentsAndLoads'))

    # environments are log-normally distributed far more often than normally, so the statistics
    # are taken on the decibel values rather than on the linear ones
    decibels = 10.0 * np.log10(sample)

    mean      = float(np.mean(decibels))
    deviation = float(np.std(decibels, ddof = 1))
    factor    = NORMAL_TOLERANCE_FACTORS[basis]

    limitDecibels = mean + factor * deviation

    return {'basis':             basis,
            'toleranceFactor':   factor,
            'sampleCount':       int(sample.size),
            'meanDecibels':      mean,
            'standardDeviation': deviation,
            'limitDecibels':     limitDecibels,
            'limitValue':        10.0 ** (limitDecibels / 10.0),
            'marginOverMean':    limitDecibels - mean}

# ------------------------------------------------------------------------------------------------ #
# -- Domain Error Types -- #
# ------------------------------------------------------------------------------------------------ #

class SpectrumError(EnvironmentsAndLoadsError):

    '''
    Raised when a spectrum is malformed or is evaluated outside the range it defines.
    '''

    pass

class DerivationError(EnvironmentsAndLoadsError):

    '''
    Raised when an environment derivation is asked for without the evidence it requires.
    '''

    pass
