# -- Tests for the spinCasting library -- #

'''

Tiered tests for CentrifugalCasting.

Tier 1 covers the guards: inputs that must raise, and outputs that must never be silently wrong.
Tier 2 validates against published process data and against the other tables in this repository.
Tier 3 covers self-consistency and the scaling laws that have to hold whatever the inputs.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'spinCastingLibrary'))


from CentrifugalCasting import (CentrifugalCasting, G_FACTOR_WINDOW, CASTING_ALLOYS,
                                INCLUSION_TYPES, GEOMETRY_LIMITS)
from spinCastingUtils import InvalidInputError, ProcessInfeasibleError, GRAVITY

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testSolidSectionRaises():

    '''
    Centrifugal casting produces a hollow section by definition. A wall equal to the radius leaves
    no bore and the request is a category error rather than a marginal geometry.
    '''

    casting = CentrifugalCasting()
    with pytest.raises(InvalidInputError):
        casting.setInputs({'alloy': '316L', 'outerDiameter': 0.100, 'wallThickness': 0.060})

def testUnknownAlloyRaises():

    '''
    Melt viscosity and the Chvorinov constant cannot be assumed.
    '''

    casting = CentrifugalCasting()
    with pytest.raises(InvalidInputError):
        casting.setInputs({'alloy': 'unobtainium'})

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testGFactorFormula():

    '''
    Validated against the definition. G = omega^2 r / g, and the speed selection has to invert it
    exactly.
    '''

    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': 0.020})
    casting.selectRotationalSpeed(targetGFactor = 80.0)
    result = casting.calculateGFactor()

    assert result['gFactor'] == pytest.approx(80.0, rel = 0.01)

    angular = casting.rotationalSpeed * np.pi / 30.0
    independent = angular ** 2 * 0.100 / GRAVITY
    assert independent == pytest.approx(80.0, rel = 0.01)

def testPreferredWindowIsFlagged():

    '''
    Below 40 the melt rains at top of arc; above 150 it cannot feed and bands. Both bounds have to
    be detected.
    '''

    for target, expected in ((20.0, 'too low'), (80.0, 'preferred'), (300.0, 'too high')):
        casting = CentrifugalCasting()
        casting.setInputs({'alloy': '316L'})
        casting.selectRotationalSpeed(targetGFactor = target)
        assert casting.calculateGFactor()['regime'] == expected

def testBoreGFactorIsBelowOuter():

    '''
    The field grows with radius, so the bore always sees less than the outer wall. On a thick walled
    casting that difference is large enough to matter.
    '''

    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': 0.040})
    casting.selectRotationalSpeed()
    result = casting.calculateGFactor()

    assert result['boreGFactor'] < result['gFactor']
    assert result['boreGFactor'] / result['gFactor'] == pytest.approx(0.6, rel = 0.02)

def testCentrifugalFieldOutrunsTheSolidificationFront():

    '''
    Validated against the reason the process exists. The Stokes velocity in the centrifugal field is
    orders of magnitude above the solidification front velocity, so essentially every inclusion
    reaches the bore before it is engulfed.

    That is what makes a centrifugal casting cleaner than a static one of the same alloy.
    '''

    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': 0.020})
    casting.selectRotationalSpeed()
    casting.calculateSolidification()
    result = casting.calculateInclusionMigration()

    assert result['captureNumber'] > 100.0, \
        'The centrifugal field must outrun the front by orders of magnitude'
    assert result['escapeFraction'] > 0.99

def testMachiningAllowanceIsPhysicallyReasonable():

    '''
    Real centrifugal casting bore allowances are a few millimetres, not the whole wall. An earlier
    version of this model integrated the Stokes velocity over the solidification time and produced a
    migration distance of metres, which saturated the allowance at the full wall thickness and made
    the calculation useless.
    '''

    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': 0.020})
    casting.selectRotationalSpeed()
    casting.calculateSolidification()
    casting.calculateInclusionMigration()
    result = casting.calculateMachiningAllowance()

    assert 0.0005 < result['boreMachiningAllowance'] < 0.006, \
        f'A bore allowance of {result["boreMachiningAllowance"] * 1000.0:.2f} mm is outside the ' \
        f'realistic range. Saturating at the wall thickness means the migration model is integrating ' \
        f'a free Stokes velocity rather than comparing it against the solidification front.'
    assert result['boreMachiningAllowance'] < casting.wallThickness

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testStokesVelocityScalesWithDiameterSquared():

    '''
    v goes as d^2, so a particle four times the diameter separates sixteen times faster. That is why
    fine oxides are the ones that set the requirement and coarse slag is never the problem.
    '''

    velocities = {}
    for inclusion in ('alumina', 'slag'):
        casting = CentrifugalCasting()
        casting.setInputs({'alloy': '316L', 'inclusionType': inclusion})
        casting.selectRotationalSpeed()
        casting.calculateSolidification()
        result = casting.calculateInclusionMigration()
        velocities[inclusion] = (result['stokesVelocity'], result['inclusionDiameter'])

    diameterRatio = velocities['slag'][1] / velocities['alumina'][1]
    velocityRatio = velocities['slag'][0] / velocities['alumina'][0]

    expected = diameterRatio ** 2 * (
        (7000.0 - INCLUSION_TYPES['slag']['density']) /
        (7000.0 - INCLUSION_TYPES['alumina']['density']))

    assert velocityRatio == pytest.approx(expected, rel = 0.02), \
        'Stokes velocity must scale with the square of the particle diameter'

def testSolidificationTimeScalesWithModulusSquared():

    '''
    Chvorinov with n = 2. Doubling the modulus must quadruple the freezing time.
    '''

    times = []
    moduli = []
    for wall in (0.010, 0.020):
        casting = CentrifugalCasting()
        casting.setInputs({'alloy': '316L', 'outerDiameter': 0.200, 'wallThickness': wall})
        casting.selectRotationalSpeed()
        result = casting.calculateSolidification()
        times.append(result['solidificationTime'])
        moduli.append(result['modulus'])

    modulusRatio = moduli[1] / moduli[0]
    timeRatio    = times[1] / times[0]

    assert timeRatio == pytest.approx(modulusRatio ** 2, rel = 0.01)

def testGeometryLimitsAreDetected():

    '''
    A wall below the minimum freezes before the melt distributes; a length to diameter above the
    limit tapers. Both have to be caught.
    '''

    casting = CentrifugalCasting()
    casting.setInputs({'alloy': '316L', 'outerDiameter': 0.100, 'wallThickness': 0.002,
                       'length': 1.200})
    result = casting.checkGeometry()

    assert not result['feasible']
    assert len(result['issues']) >= 2

def testReportRuns():

    '''
    Smoke test across the whole calculation chain.
    '''

    casting = CentrifugalCasting()
    casting.setInputs({'alloy': 'bronze', 'outerDiameter': 0.150, 'wallThickness': 0.015})
    assert 'CENTRIFUGAL CASTING' in casting.generateReport()
