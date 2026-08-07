
# -- Numerical Solvers [orbitalRockets common] -- #

'''

The two root finders every sizing routine in this repository depends on.

secantSolve is the workhorse: superlinear convergence on the smooth, well-behaved relations most
sizing problems reduce to, with bounds clamping so a solver that overshoots into a nonphysical
region recovers instead of throwing. Its step-size convergence test matters because the residuals
here carry physical units, and a pure residual-magnitude test is meaningless at that scale.

solveForUnknown generalizes the solve-for-whichever-argument-is-None idiom, using bisection
because the relations it is handed are user-supplied and may be badly behaved at the bracket ends.

Author: Sean Bowman
Date:   08/06/2026

'''

from typing import Callable

import numpy as np

try:
    from errors import InvalidInputError, ConvergenceFailureError
except ImportError:
    from .errors import InvalidInputError, ConvergenceFailureError

#--------------------------------------------------------------------------------------------------------------------------#
# -- Root Finding -- #
#--------------------------------------------------------------------------------------------------------------------------#

def solveForUnknown(relation: Callable[..., float], arguments: dict, bracket: tuple = (1.0e-12, 1.0e12)) -> tuple:

    '''

    Generalized 'solve for whichever argument is None' helper.

    Several sizing relations in this library are single equations with N variables, any one of which
    might be the unknown: hoop stress and thickness, orifice diameter and pressure drop, valve Cv and
    flow rate. Rather than writing an if-tree per relation, this helper finds the single None-valued
    argument and solves the relation for it by bisection.

    ---------------------------------------------------------------------------
                                    INPUTS
    ---------------------------------------------------------------------------
    - relation     Callable taking all arguments by keyword and returning a residual that is zero
                   when the relation is satisfied
    - arguments    Dictionary of argument name to value; exactly one value must be None
    - bracket      (low, high) bracket for the unknown. The default spans twelve orders of magnitude
                   either side of unity, which covers every physical quantity in this library.

    ---------------------------------------------------------------------------
                                    OUTPUTS
    ---------------------------------------------------------------------------
    (unknownName, unknownValue)

    '''

    unknownNames = [name for name, value in arguments.items() if value is None]

    if len(unknownNames) != 1:
        raise InvalidInputError(
            message       = f'solveForUnknown needs exactly one argument set to None, found {len(unknownNames)}: {unknownNames}.',
            parameterName = 'arguments',
            value         = unknownNames,
            validRange    = 'Exactly one None-valued entry'
        )

    unknownName = unknownNames[0]

    def residual(trialValue: float) -> float:
        trialArguments              = dict(arguments)
        trialArguments[unknownName] = trialValue
        return relation(**trialArguments)

    low, high         = bracket
    residualLow       = residual(low)
    residualHigh      = residual(high)

    if residualLow * residualHigh > 0.0:
        raise ConvergenceFailureError(
            message = f'solveForUnknown could not bracket a root for \'{unknownName}\' over {bracket}. The relation may have no solution for these inputs.',
            context = {'unknown': unknownName, 'residualAtLow': residualLow, 'residualAtHigh': residualHigh}
        )

    # Bisection. Slower than a secant method but it cannot diverge, which matters here because the
    # relations being solved are user-supplied and may be badly behaved at the bracket ends.
    for _ in range(200):
        midpoint         = 0.5 * (low + high)
        residualMidpoint = residual(midpoint)
        if residualLow * residualMidpoint <= 0.0:
            high = midpoint
        else:
            low         = midpoint
            residualLow = residualMidpoint
        if abs(high - low) <= 1.0e-12 * max(1.0, abs(midpoint)):
            break

    return unknownName, 0.5 * (low + high)

def secantSolve(function: Callable[..., float], initialGuess: float, lowerBound: float = -np.inf, upperBound: float = np.inf, tolerance: float = 1.0e-10, maxIterations: int = 200, displayFlag: bool = False) -> float:

    '''

    Zero a function (linear or nonlinear) using the secant method, with bounds clamping.

    The secant method is used rather than Newton because none of the relations in this library have
    analytic derivatives worth writing, and rather than bisection because most of them are smooth
    and well behaved near the root so the superlinear convergence is worth having.

    Bounds are enforced by clamping rather than by rejecting the step, so a solver that overshoots
    into a nonphysical region (negative diameter, subatmospheric absolute pressure) recovers instead
    of throwing.

    '''

    currentGuess  = float(initialGuess)
    previousGuess = currentGuess * 1.01 if currentGuess != 0.0 else 1.0e-6

    currentValue  = function(currentGuess)
    previousValue = function(previousGuess)

    for iteration in range(maxIterations):

        if abs(currentValue) < tolerance:
            if displayFlag:
                print(f'secantSolve converged in {iteration} iterations, residual {currentValue:.3e}')
            return currentGuess

        denominator = currentValue - previousValue
        if abs(denominator) < 1.0e-300:
            break

        nextGuess = currentGuess - currentValue * (currentGuess - previousGuess) / denominator
        nextGuess = float(np.clip(nextGuess, lowerBound, upperBound))

        # Step-size convergence. The residual tolerance alone is not enough because the residuals in
        # this library carry physical units: a pressure residual of 1e-9 Pa is converged to machine
        # precision, while a Mach number residual of 1e-9 is not remotely tight. Stopping when the
        # independent variable stops moving is scale-free and catches both.
        if abs(nextGuess - currentGuess) <= 1.0e-12 * max(abs(nextGuess), 1.0e-12):
            if displayFlag:
                print(f'secantSolve converged on step size in {iteration} iterations, residual {currentValue:.3e}')
            return nextGuess

        previousGuess, currentGuess = currentGuess, nextGuess
        previousValue, currentValue = currentValue, function(currentGuess)

    raise ConvergenceFailureError(
        message    = 'secantSolve failed to converge.',
        context    = {'finalGuess': currentGuess, 'finalResidual': currentValue},
        iterations = maxIterations,
        tolerance  = tolerance,
        residual   = float(currentValue)
    )
