
# -- Collection of commonly used functions [manufacturingAndAssembly] -- #

'''

Shared function repository for the manufacturingAndAssembly library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one
flat namespace and does not have to know whether a helper is domain-specific or shared.

What is defined here is the inspection capability data, which is the only part of this domain with
a read standard behind it, and the rate and tolerance tables the other two classes work from.

The process physics is deliberately absent. It lives in the ten aerospaceMaterials sub-domains, and
what stays here is the cross-cutting view: what a stack of tolerances does, what a rate does to
cost, and what an inspection actually establishes.

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
# -- manufacturingAndAssembly Errors -- #
# ------------------------------------------------------------------------------------------------ #

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause.
ManufacturingError = EngineeringError

class ToleranceError(ManufacturingError):
    """
    A stack that does not close: a gap that goes negative at the worst case, or a shim demand
    outside what the joint can take. Raised rather than reported, because an interference at
    assembly is a part that does not go together rather than a small negative margin.
    """

class RateError(ManufacturingError):
    """
    A production plan that cannot meet its rate: a takt time below the bottleneck station, or a
    learning rate outside the range a learning curve describes.
    """

class InspectionError(ManufacturingError):
    """
    An inspection that establishes nothing: a reliably detectable flaw larger than the critical
    flaw size, or a demonstration too small to estimate a detection curve from.
    """

# ------------------------------------------------------------------------------------------------ #
# -- Inspection capability: MIL-HDBK-1823A -- #
# ------------------------------------------------------------------------------------------------ #

# The log-odds probability of detection model, which is the one the handbook uses for hit/miss data:
#
#     log( POD / (1 - POD) ) = ( log(a) - mu ) / sigma
#
# so POD(a) = 1 / (1 + (a50 / a) ** (1/sigma)) with a50 = exp(mu).
#
# Two sizes come off it and both are named in the standard. a50 is the size found half the time and
# a90 the size found nine times in ten, and their ratio is fixed by sigma alone:
#
#     a90 / a50 = 9 ** sigma
#
# **a90/95 is a different kind of number.** It is the 95 per cent confidence bound on the ESTIMATE
# of a90, so it depends on how many specimens the demonstration used as well as on the inspection.
# The handbook notes it has become a de facto design criterion, which means the size a programme
# designs to is partly a statement about how many specimens somebody paid for.
POD_LOGIT_AT_90 = float(np.log(9.0))     # [-], logit(0.9) = 2.1972

# Minimum demonstration sizes, MIL-HDBK-1823A section 4.5.2.2. These are minimums rather than
# targets: the handbook states that 120 binary inspection opportunities give a significantly more
# precise a50 and therefore a smaller a90/95.
MINIMUM_HIT_MISS_TARGETS = 60      # [-], binary hit/miss response
MINIMUM_SIGNAL_TARGETS = 40        # [-], quantitative response, the a-hat versus a case
UNFLAWED_SITE_RATIO = 3            # [-], unflawed sites per flawed site, for the false positive rate

# Representative inspection capability by method. a50 is in metres and sigma is dimensionless.
#
# These are representative of a method rather than of any qualified procedure: a real a90/95 comes
# from a demonstration on the actual geometry, material, surface finish and access, and the
# handbook is emphatic that all four move it.
#
# What is NOT representative is the ordering and the shape. Every method has a size below which it
# finds nothing useful, the curve rises over roughly a decade of size, and the methods that reach
# further inside a part find larger flaws than the ones that only see a surface.
NDE_METHODS = {
    'visual':            {'a50': 2.0e-3,  'sigma': 0.55, 'relativeCost': 1.0,
                          'finds':  'surface breaking, large, in accessible locations',
                          'misses': 'anything subsurface, and anything under a coating'},
    'penetrant':         {'a50': 0.6e-3,  'sigma': 0.40, 'relativeCost': 3.0,
                          'finds':  'surface breaking flaws in non-porous material',
                          'misses': 'subsurface flaws, and anything a smeared surface has closed'},
    'magneticParticle':  {'a50': 0.5e-3,  'sigma': 0.40, 'relativeCost': 3.0,
                          'finds':  'surface and near-surface flaws in ferromagnetic material',
                          'misses': 'everything in an austenitic or aluminium part'},
    'eddyCurrent':       {'a50': 0.4e-3,  'sigma': 0.35, 'relativeCost': 6.0,
                          'finds':  'surface and near-surface flaws, and it is fast',
                          'misses': 'flaws deeper than a few skin depths, and it needs a reference'},
    'ultrasonic':        {'a50': 0.8e-3,  'sigma': 0.45, 'relativeCost': 8.0,
                          'finds':  'internal flaws, with a couplant and a favourable orientation',
                          'misses': 'flaws parallel to the beam, and anything in the near field'},
    'radiography':       {'a50': 1.5e-3,  'sigma': 0.50, 'relativeCost': 12.0,
                          'finds':  'volumetric flaws, porosity and inclusions',
                          'misses': 'tight planar cracks not aligned with the beam'},
    'computedTomography':{'a50': 0.3e-3,  'sigma': 0.35, 'relativeCost': 40.0,
                          'finds':  'internal geometry and flaws without an orientation penalty',
                          'misses': 'nothing much, and it is limited by part size and cost'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Rate and learning -- #
# ------------------------------------------------------------------------------------------------ #

# Wright's learning curve. The cost of the nth unit is
#
#     C(n) = C(1) * n ** b        with  b = log2(learningRate)
#
# so a learning rate of 0.85 means every doubling of cumulative production costs 85 per cent of the
# previous doubling. The exponent is negative and small, which is what makes the curve log-linear.
#
# The rates below are representative by process class. The ordering is the useful part: the more
# labour a process carries, the more there is to learn, and a process that is mostly material cost
# barely learns at all.
LEARNING_RATES = {
    'manualAssembly':      {'rate': 0.80, 'note': 'the most labour and therefore the steepest curve'},
    'composites':          {'rate': 0.82, 'note': 'layup is labour, cure is not'},
    'welding':             {'rate': 0.85, 'note': 'operator skill and fixturing both improve'},
    'machining':           {'rate': 0.90, 'note': 'programme once, then it is cycle time'},
    'additive':            {'rate': 0.92, 'note': 'build time is build time'},
    'rawMaterial':         {'rate': 0.98, 'note': 'almost nothing to learn; it is a purchase'},
}

# A station whose utilisation exceeds this is treated as the bottleneck rather than as busy. Above
# it, queueing time grows faster than the utilisation does and the line stops behaving linearly.
BOTTLENECK_UTILISATION = 0.85    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- Tolerances -- #
# ------------------------------------------------------------------------------------------------ #

# Representative achievable tolerance by process, as a fraction of the nominal dimension, for a
# feature of the size a launch vehicle carries.
#
# The ordering is what matters and it spans three orders of magnitude, which is why process
# selection is a tolerance decision before it is a cost one.
PROCESS_TOLERANCES = {
    'sandCasting':      3.0e-3,
    'sheetForming':     1.5e-3,
    'welding':          1.0e-3,
    'additive':         5.0e-4,
    'turning':          1.0e-4,
    'milling':          1.0e-4,
    'grinding':         2.0e-5,
    'lapping':          5.0e-6,
}

# A worst case stack assumes every contributor sits at its limit simultaneously and in the same
# direction. A statistical stack assumes they are independent and normally distributed, and adds
# them in quadrature. The two differ by roughly the square root of the contributor count, which is
# the single most consequential fact in assembly tolerancing.
#
# The sigma level a statistical stack is quoted at decides how many assemblies fall outside it.
DEFAULT_STATISTICAL_SIGMA = 3.0    # [-]

def logOddsPod(flawSize: ArrayLike, a50: float, sigma: float) -> ArrayLike:

    '''

    Probability of detection from the log-odds model, MIL-HDBK-1823A appendix G.

    POD(a) = 1 / (1 + (a50 / a) ** (1 / sigma))

    '''

    size = np.asarray(flawSize, dtype = float)

    if a50 <= 0.0 or sigma <= 0.0:
        raise InspectionError('a50 and sigma must both be positive.')

    if np.any(size <= 0.0):
        raise InspectionError('Flaw size must be positive. The model is in log size.')

    return 1.0 / (1.0 + (a50 / size) ** (1.0 / sigma))

def podSize(probability: float, a50: float, sigma: float) -> float:

    '''

    The flaw size at a given probability of detection. Inverts logOddsPod.

    a(p) = a50 * ( p / (1 - p) ) ** sigma

    '''

    if not 0.0 < probability < 1.0:
        raise InspectionError('Probability must lie strictly between zero and one. The model '
                              'reaches zero and one only in the limit.')

    return a50 * (probability / (1.0 - probability)) ** sigma

def learningExponent(learningRate: float) -> float:

    '''

    Wright's learning curve exponent, b = log2(rate).

    '''

    if not 0.0 < learningRate <= 1.0:
        raise RateError('A learning rate is a fraction above zero and at or below one. A rate above '
                        'one is a process that gets worse with practice, which is a different '
                        'phenomenon and not a learning curve.')

    return np.log(learningRate) / np.log(2.0)
