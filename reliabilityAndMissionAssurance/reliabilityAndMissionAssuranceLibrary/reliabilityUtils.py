
# -- Collection of commonly used functions [reliabilityAndMissionAssurance] -- #

'''

Shared function repository for the reliabilityAndMissionAssurance library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one
flat namespace and does not have to know whether a helper is domain-specific or shared.

What is defined here is the reliability arithmetic that the four classes share, and the tables of
representative failure rates and beta factors they work from.

**None of the tables is the point.** The results this domain produces come from products, sums and
one beta-factor model, all of which survive every value in the tables being wrong.

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
# -- reliabilityAndMissionAssurance Errors -- #
# ------------------------------------------------------------------------------------------------ #

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause.
ReliabilityError = EngineeringError

# Kept as an alias because the scaffold named it this and nothing gains from breaking it.
ReliabilityAndMissionAssuranceError = ReliabilityError

class FmecaError(ReliabilityError):
    """
    A failure mode analysis that cannot be acted on: a criticality with no severity, a finding
    with no owner, or a table with a mode listed twice under different names.
    """

class FaultTreeError(ReliabilityError):
    """
    A tree that cannot be evaluated: a gate with no inputs, a cycle, or a basic event with a
    probability that is not one.
    """

class AllocationError(ReliabilityError):
    """
    A reliability budget that does not close, or one allocated to a target no series of
    subsystems can meet.
    """

class RedundancyError(ReliabilityError):
    """
    A redundancy claim that does not survive its own common cause. Raised rather than reported,
    because redundancy that shares a failure cause is not redundancy and reporting it as a small
    reduction invites somebody to keep calling it redundant.
    """


# ------------------------------------------------------------------------------------------------ #
# -- Common cause: the beta factor model -- #
# ------------------------------------------------------------------------------------------------ #

# The single most important idea in this domain, and the one the arithmetic of redundancy usually
# leaves out.
#
# A failure rate splits into an independent part and a common cause part:
#
#     lambda_independent = (1 - beta) * lambda
#     lambda_common      = beta * lambda
#
# The independent part is what redundancy defends against. **The common part defeats every
# redundant unit at once**, so for n parallel units the system failure probability is
#
#     Q = ((1 - beta) * q) ** n  +  beta * q
#
# The first term falls as the nth power and the second does not fall at all. Above a very small
# number of units the second term is the answer, which is why **adding a third unit to a system
# with a common cause almost never helps.**
#
# Representative beta factors by how much the redundant units share. The ordering is the point and
# it is structural: units that share a design share its design errors, and units that share an
# environment share what the environment does to them.
BETA_FACTORS = {
    'identicalSameBatch':    {'beta': 0.20, 'note': 'same design, same lot, same installation'},
    'identicalDifferentLot': {'beta': 0.10, 'note': 'same design, different lot'},
    'sameDesignSeparated':   {'beta': 0.05, 'note': 'same design, physically and thermally separated'},
    'diverseDesign':         {'beta': 0.02, 'note': 'different designs solving the same problem'},
    'diverseAndSeparated':   {'beta': 0.01, 'note': 'different designs, separated; the practical floor'},
}

# Fault detection coverage: the fraction of failures a monitoring system actually detects. An
# undetected failure in a standby unit means the redundancy is not there when it is called on, so
# coverage multiplies the benefit of standby redundancy and does nothing for active redundancy.
DEFAULT_COVERAGE = 0.95    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- FMECA -- #
# ------------------------------------------------------------------------------------------------ #

# Severity classes, from the usual system safety scale. The numbers are ranks rather than
# measurements, and multiplying them is a convention rather than an arithmetic.
SEVERITY_CLASSES = {
    'catastrophic': {'rank': 4, 'means': 'loss of vehicle, loss of life, or loss of the mission'},
    'critical':     {'rank': 3, 'means': 'major mission degradation or major damage'},
    'marginal':     {'rank': 2, 'means': 'minor mission degradation'},
    'negligible':   {'rank': 1, 'means': 'no mission effect'},
}

# Detection ranks. **A high rank is bad**, which is the convention that catches people: a mode that
# cannot be detected before it matters scores worst.
DETECTION_CLASSES = {
    'certain':      {'rank': 1, 'means': 'detected by instrumentation before it matters'},
    'likely':       {'rank': 2, 'means': 'detected by inspection or test'},
    'possible':     {'rank': 3, 'means': 'detected only by a specific check somebody has to run'},
    'unlikely':     {'rank': 4, 'means': 'detected only after the effect'},
    'undetectable': {'rank': 5, 'means': 'not detectable in service at all'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Representative failure rates -- #
# ------------------------------------------------------------------------------------------------ #

# Failures per demand for single-shot devices and per hour for continuous ones. Representative and
# registered as unvalidated.
#
# **The ordering is the useful part**: single-shot devices dominate a launch vehicle fault tree
# because they are non-redundant by construction and are used exactly once at a moment that cannot
# be repeated.
FAILURE_RATES = {
    'pyrotechnicInitiator': {'perDemand': 1.0e-4, 'note': 'single shot, lot acceptance tested'},
    'separationBolt':       {'perDemand': 5.0e-4, 'note': 'single shot, often non-redundant'},
    'solenoidValve':        {'perDemand': 2.0e-4, 'note': 'cycles, but the flight demand is one'},
    'pressureRegulator':    {'perDemand': 5.0e-4, 'note': 'a single point in most feed systems'},
    'engineStart':          {'perDemand': 2.0e-3, 'note': 'the transient, not the steady burn'},
    'avionicsUnit':         {'perHour':   1.0e-4, 'note': 'continuous, and redundant in practice'},
    'battery':              {'perHour':   5.0e-5, 'note': 'continuous over a short mission'},
    'structuralJoint':      {'perDemand': 1.0e-6, 'note': 'rarely the limiting term'},
}

def seriesReliability(reliabilities: ArrayLike) -> float:

    """

    Everything must work, so the reliabilities multiply.

    **This is where a launch vehicle loses its reliability**, and the arithmetic is unforgiving: a
    hundred items at 0.999 each give 0.905, and a thousand give 0.368.

    """

    values = np.atleast_1d(np.asarray(reliabilities, dtype = float))

    if np.any(values <= 0.0) or np.any(values > 1.0):
        raise ReliabilityError('Every reliability must lie above zero and at or below one.')

    return float(np.prod(values))

def parallelReliability(reliabilities: ArrayLike) -> float:

    """

    Any one must work, so the UNRELIABILITIES multiply.

    This is the ideal case with no common cause, which is what makes redundancy look better than it
    is. See betaFactorReliability for the honest version.

    """

    values = np.atleast_1d(np.asarray(reliabilities, dtype = float))

    if np.any(values < 0.0) or np.any(values > 1.0):
        raise ReliabilityError('Every reliability must lie between zero and one.')

    return float(1.0 - np.prod(1.0 - values))

def betaFactorReliability(elementReliability: float, units: int, beta: float) -> dict:

    """

    Parallel redundancy with a common cause fraction.

        Q = ((1 - beta) * q) ** n  +  beta * q

    The first term is the independent failures, which fall as the nth power of the unit count. The
    second is the common cause, which does not fall at all.

    """

    if not 0.0 < elementReliability <= 1.0:
        raise RedundancyError('Element reliability must lie above zero and at or below one.')

    if units < 1:
        raise RedundancyError('A redundant set has at least one unit.')

    if not 0.0 <= beta < 1.0:
        raise RedundancyError('Beta is a fraction of the failure rate at or above zero and below '
                              'one. A beta of one is a system with no independent failures at all.')

    failure = 1.0 - elementReliability

    # A single unit has nothing to share a cause with, so the split does not apply to it and the
    # whole failure rate is independent. Applying the beta split at n = 1 would report a single
    # unit as MORE reliable than its own element, which is the sort of quiet error a redundancy
    # model should not contain.
    if units == 1:
        independent = failure
        common = 0.0
    else:
        independent = ((1.0 - beta) * failure) ** units
        common = beta * failure

    total = independent + common

    return {'units':             units,
            'beta':              beta,
            'elementFailure':    failure,
            'independentTerm':   independent,
            'commonCauseTerm':   common,
            'systemFailure':     total,
            'systemReliability': 1.0 - total,
            'commonCauseShare':  common / total if total > 0.0 else 0.0,
            'idealFailure':      failure ** units,
            'penalty':           total / failure ** units if failure > 0.0 else 1.0}

def zeroFailureDemonstration(reliability: float, confidence: float) -> float:

    """

    Successful tests with zero failures needed to demonstrate a reliability at a confidence.

    The same arithmetic rangeSafetyAndFTS uses on a flight termination system, kept here because
    every reliability claim in this domain faces it.

    """

    if not 0.0 < reliability < 1.0 or not 0.0 < confidence < 1.0:
        raise ReliabilityError('Reliability and confidence must lie strictly between zero and one.')

    return float(np.log(1.0 - confidence) / np.log(reliability))
