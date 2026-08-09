# -- Domain-specific helpers [propulsionTesting] -- #

'''

Hot fire campaign structure, test stands, instrumentation and data reduction.

Named propulsionTestUtils rather than utils. Every domain library in this repository has a utils.py
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
# -- propulsionTesting Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
PropulsionTestingError = EngineeringError

# PropulsionTestingError above is the domain base, aliased to EngineeringError by the scaffold.
# These are the specific ones and they subclass it, so a caller can still catch the whole family
# with one except.

class ReductionError(PropulsionTestingError):
    """
    A data reduction that cannot be performed from the channels supplied, or one whose result would
    be arithmetically valid and physically meaningless.
    """

class TestDesignError(PropulsionTestingError):
    """
    A test that cannot answer the question it was written to answer. Raised rather than reported,
    because running it and reporting a verdict is worse than not running it.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

_HUB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'propulsionLibrary')

if _HUB not in sys.path:
    sys.path.insert(0, _HUB)

from propulsionUtils import PROPELLANT_COMBINATIONS

# Typical instrument uncertainties for a development hot fire stand, as a fraction of reading unless
# noted. These are representative of good practice rather than of any particular installation, and
# they are registered as unvalidated: a real budget comes from the calibration certificates.
#
# The ordering is the useful part and it is stable across installations. Throat area is the worst
# measurement in the set and it is the one nobody calls a measurement.
INSTRUMENT_UNCERTAINTY = {
    'chamberPressure': {
        'relative': 0.0050,
        'note': 'a good transducer calibrated in place. Worse if the tap is short, unpurged or '
                'reading through a recirculation zone, and the tap is usually the larger error'},
    'thrust': {
        'relative': 0.0075,
        'note': 'load cell plus the load path. The cell is better than this; the plumbing '
                'crossing the load path is what makes it worse, and it is a bias not a scatter'},
    'massFlow': {
        'relative': 0.0100,
        'note': 'turbine or Coriolis meter, per propellant, and the total is the RSS of the two. '
                'Cryogenic service and two-phase flow both degrade it'},
    'throatArea': {
        'relative': 0.0100,
        'note': 'from a cold diameter measurement, doubled because area goes as diameter squared. '
                'It does not include throat erosion during the firing, which is not measured'},
}

# The chamber acoustic eigenvalues, restated from combustionDevices so a sample rate can be checked
# against the frequencies that have to be resolved. combustionDevices owns the stability model; this
# sub-domain owns whether the instrumentation could see it.
FIRST_TANGENTIAL_EIGENVALUE = 1.8412    # [-]

# Nyquist is the theoretical floor and it is not a usable engineering criterion for a transient
# waveform. Ten samples per cycle is the working rule for resolving an oscillation's amplitude and
# decay rather than merely detecting that it exists.
NYQUIST_FACTOR = 2.0       # [-]
RESOLUTION_FACTOR = 10.0   # [-]

# A pulse or bomb has to perturb the chamber hard enough that the response is a real dynamic
# response rather than noise. The NASA MSFC pulse gun development programme recorded zero-to-peak
# overpressures of 37 to 58 per cent of mean chamber pressure and called that adequate for typical
# stability rating.
STABILITY_PULSE_FRACTION_MINIMUM = 0.37    # [-]

# Above roughly this chamber diameter a pulse gun may be unable to produce an adequate response and
# a bomb is needed instead. From the same source.
PULSE_GUN_DIAMETER_LIMIT = 0.3048    # [m], 12 inches

# Heat flux multiplier under high frequency instability, from the same source. Near the injector
# face the flux can rise by five to ten times and it can double at the throat.
INSTABILITY_FLUX_MULTIPLIER = {
    'injector face': (5.0, 10.0),
    'throat':        (2.0, 2.0),
}

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def rootSumSquare(*terms: float) -> float:

    '''

    Root sum of squares, the combination rule for independent uncertainties.

    Independent is doing the work in that sentence. Applying it to terms that share a source is the
    most common error in a test uncertainty budget, and it is the error PerformanceReduction exists
    to avoid; see its docstring.

    '''

    return float(np.sqrt(sum(float(term) ** 2 for term in terms)))

def characteristicVelocity(chamberPressure: float, throatArea: float, massFlow: float) -> float:

    '''
    c* from the three measured channels. The definition, and the only one this repository uses.
    '''

    if massFlow <= 0.0:
        raise InvalidInputError(
            f'The mass flow must be positive to reduce a characteristic velocity, got {massFlow}.',
            context = createErrorContext(component = 'propulsionTestUtils'))

    return chamberPressure * throatArea / massFlow

def thrustCoefficient(thrust: float, chamberPressure: float, throatArea: float) -> float:

    '''
    Cf from the measured thrust and the same chamber pressure and throat area c* used.
    '''

    if chamberPressure <= 0.0 or throatArea <= 0.0:
        raise InvalidInputError(
            f'The chamber pressure and throat area must both be positive, got {chamberPressure} '
            f'and {throatArea}.',
            context = createErrorContext(component = 'propulsionTestUtils'))

    return thrust / (chamberPressure * throatArea)

def firstTangentialFrequency(speedOfSound: float, chamberDiameter: float) -> float:

    '''

    The first tangential mode frequency, which is the one that destroys engines and therefore the
    one the instrumentation has to resolve.

        f = alpha * a / (pi * D)

    combustionDevices owns the stability model. This is here so a sample rate can be checked against
    the frequency it has to see.

    '''

    if chamberDiameter <= 0.0:
        raise InvalidInputError(
            f'The chamber diameter must be positive, got {chamberDiameter}.',
            context = createErrorContext(component = 'propulsionTestUtils'))

    return FIRST_TANGENTIAL_EIGENVALUE * speedOfSound / (np.pi * chamberDiameter)
