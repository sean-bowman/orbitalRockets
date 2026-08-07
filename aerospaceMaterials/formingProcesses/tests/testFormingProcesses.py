# -- Tests for the formingProcesses library -- #

'''

Tiered tests for FormingProcess.

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
                                'formingProcessesLibrary'))


from FormingProcess import (FormingProcess, WORK_HARDENING, FORMING_PROCESSES,
                            ANNEAL_STRAIN_THRESHOLD)
from formingUtils import InvalidInputError, ProcessInfeasibleError

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testTooTightABendRaises():

    '''
    The outer fibre of a bend is in tension and it cracks when the local strain exceeds the
    ductility. A radius below the minimum is a crack, not a marginal part.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '2219', 'condition': 't87', 'thickness': 0.0016,
                       'bendRadius': 0.0005})

    with pytest.raises(ProcessInfeasibleError):
        forming.calculateMinimumBendRadius()

def testUnknownMaterialRaises():

    '''
    The hardening exponent ranges from 0.08 to 0.45 across these alloys and it cannot be assumed.
    '''

    forming = FormingProcess()
    with pytest.raises(InvalidInputError):
        forming.setInputs({'material': 'unobtainium'})

def testExceedingTheFormingLimitRaises():

    '''
    Past the forming limit the sheet necks and tears. It is a hard stop.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '7075', 'condition': 't6', 'thickness': 0.0016,
                       'bendRadius': 0.0064})

    with pytest.raises(ProcessInfeasibleError):
        forming.checkFormingLimit(0.60, 0.0)

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testBendRadiusIsADuctilityLimitNotAStrengthLimit():

    '''
    Validated against the r_min/t = 50/RA - 1 relation. At RA = 50 percent the material folds flat
    on itself; at RA = 20 percent it needs 1.5 thicknesses.

    The relation contains no strength term at all, which is the point: a strong ductile alloy bends
    tighter than a weak brittle one.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '316L', 'condition': 'annealed', 'thickness': 0.0016,
                       'bendRadius': 0.0064})
    result = forming.calculateMinimumBendRadius()

    expected = max(0.0, 50.0 / (result['reductionOfArea'] * 100.0) - 1.0)
    assert result['minimumRatio'] == pytest.approx(expected, rel = 0.01)

def testGrainDirectionDoublesTheRequirement():

    '''
    Bending parallel to the grain puts the elongated grain boundaries directly in the tensile outer
    fibre. Rotating the blank is free and it halves the requirement, and it is the commonest
    omission on a formed part drawing.
    '''

    radii = {}
    for direction in ('transverse', 'parallel'):
        forming = FormingProcess()
        forming.setInputs({'material': '2219', 'condition': 't87', 'thickness': 0.0016,
                           'bendRadius': 0.010, 'grainDirection': direction})
        radii[direction] = forming.calculateMinimumBendRadius()['minimumBendRadius']

    assert radii['parallel'] == pytest.approx(2.0 * radii['transverse'], rel = 1e-9)

def testTitaniumSpringsBackMoreThanStainless():

    '''
    Validated against the governing group R F_ty / (E t). Titanium is doubly penalised: it is strong
    AND compliant, so its yield strain is far higher than stainless at the same geometry.
    '''

    springback = {}
    for material, condition in (('316L', 'annealed'), ('Ti-6Al-4V', 'annealed')):
        forming = FormingProcess()
        forming.setInputs({'material': material, 'condition': condition, 'thickness': 0.0016,
                           'bendRadius': 0.0064, 'bendAngle': 90.0})
        forming.calculateMinimumBendRadius()
        springback[material] = forming.calculateSpringback()['springbackAngle']

    assert springback['Ti-6Al-4V'] > 3.0 * springback['316L'], \
        'Titanium springs back far more than stainless because it is both strong and compliant'

def testAusteniticStainlessHasTheHighestHardeningExponent():

    '''
    Validated against published Hollomon parameters. n around 0.45 for austenitic stainless against
    0.08 for titanium, and that is why stainless deep draws and titanium does not.

    The exponent is also the uniform elongation, so a high n material both hardens more and stretches
    further before it necks.
    '''

    assert WORK_HARDENING['316L']['hardeningExponent'] > 0.40
    assert WORK_HARDENING['TI-6AL-4V']['hardeningExponent'] < 0.12
    assert (WORK_HARDENING['316L']['hardeningExponent'] >
            5.0 * WORK_HARDENING['TI-6AL-4V']['hardeningExponent'])

def testPlaneStrainIsTheCriticalCondition():

    '''
    The forming limit diagram has its minimum at plane strain, and the limit rises either side. That
    is why a long straight-sided feature necks before more severely deformed corners do.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '316L', 'condition': 'annealed', 'thickness': 0.0016,
                       'bendRadius': 0.0064})

    planeStrain = forming.checkFormingLimit(0.10,  0.00)['limitStrain']
    drawing     = forming.checkFormingLimit(0.10, -0.15)['limitStrain']
    stretching  = forming.checkFormingLimit(0.10,  0.15)['limitStrain']

    assert planeStrain < drawing
    assert planeStrain < stretching

def testDrawingLimitRisesFasterThanStretching():

    '''
    The FLD is asymmetric. In the drawing quadrant material flows in from the side to feed the
    deformation, so the section thins less and the limit rises steeply. Biaxial stretching thins
    everywhere at once with nowhere to draw from, so it rises slowly.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '6061', 'condition': 't6', 'thickness': 0.0016,
                       'bendRadius': 0.010})

    drawing    = forming.checkFormingLimit(0.05, -0.10)['limitStrain']
    stretching = forming.checkFormingLimit(0.05,  0.10)['limitStrain']

    assert drawing > stretching

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testSpringbackFallsWithATighterBend():

    '''
    The governing group scales with the radius, so a tight bend yields the section thoroughly and
    springs back less. A gentle bend barely yields it and springs back most.
    '''

    angles = []
    for radius in (0.002, 0.006, 0.020):
        forming = FormingProcess()
        forming.setInputs({'material': '316L', 'condition': 'annealed', 'thickness': 0.0016,
                           'bendRadius': radius, 'bendAngle': 90.0})
        forming.calculateMinimumBendRadius()
        angles.append(forming.calculateSpringback()['springbackAngle'])

    assert angles[0] < angles[1] < angles[2]

def testStretchFormingReducesSpringbackAgainstAirBending():

    '''
    Stretching past yield across the whole section nearly eliminates springback, which is why it is
    used for contoured skins.
    '''

    angles = {}
    for process in ('air bend', 'stretch form'):
        forming = FormingProcess()
        forming.setInputs({'material': '2219', 'condition': 't87', 'process': process,
                           'thickness': 0.0016, 'bendRadius': 0.010, 'bendAngle': 90.0})
        forming.calculateMinimumBendRadius()
        angles[process] = forming.calculateSpringback()['springbackAngle']

    assert angles['stretch form'] < 0.5 * angles['air bend']

def testKFactorStaysBelowOneHalf():

    '''
    The neutral axis migrates towards the inside of the bend because the inner fibre thickens in
    compression while the outer thins in tension. It never reaches the mid-thickness.
    '''

    for ratio in (0.5, 1.0, 2.0, 4.0, 10.0):
        forming = FormingProcess()
        forming.setInputs({'material': '316L', 'condition': 'annealed', 'thickness': 0.0016,
                           'bendRadius': 0.0016 * ratio})
        kFactor = forming.calculateBendAllowance()['kFactor']
        assert 0.30 <= kFactor <= 0.50, f'k-factor of {kFactor:.3f} at r/t = {ratio} is unphysical'

def testWorkHardeningSpendsDuctilityAsItGainsStrength():

    '''
    Both halves of the trade, and only the first is usually claimed. The material necks when the
    strain reaches n, so accumulated strain approaching n means the material is at the end of its
    uniform deformation.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '6061', 'condition': 't6', 'thickness': 0.0016,
                       'bendRadius': 0.0064})

    light = forming.calculateWorkHardening(0.05)
    heavy = forming.calculateWorkHardening(0.18)

    assert heavy['flowStress'] > light['flowStress']
    assert heavy['remainingUniformElongation'] < light['remainingUniformElongation']
    assert heavy['ductilitySpentFraction'] > light['ductilitySpentFraction']

def testAnnealThresholdIsFlagged():

    '''
    Above the threshold most alloys have consumed their formability and need a recrystallisation
    anneal before further work.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '316L', 'condition': 'annealed', 'thickness': 0.0016,
                       'bendRadius': 0.0064})

    assert forming.calculateWorkHardening(ANNEAL_STRAIN_THRESHOLD + 0.1)['annealRequired'] is True
    assert forming.calculateWorkHardening(ANNEAL_STRAIN_THRESHOLD - 0.1)['annealRequired'] is False

def testHydroformPressureScalesWithThickness():

    '''
    P = 2 F_ty t / D. Doubling the thickness doubles the pressure needed.
    '''

    pressures = []
    for thickness in (0.0010, 0.0020):
        forming = FormingProcess()
        forming.setInputs({'material': '316L', 'condition': 'annealed', 'process': 'hydroform',
                           'thickness': thickness, 'bendRadius': 0.050, 'partDiameter': 0.200})
        pressures.append(forming.calculateHydroformPressure()['formingPressure'])

    assert pressures[1] / pressures[0] == pytest.approx(2.0, rel = 1e-9)

def testReportRuns():

    '''
    Smoke test.
    '''

    forming = FormingProcess()
    forming.setInputs({'material': '316L', 'condition': 'annealed', 'thickness': 0.0016,
                       'bendRadius': 0.0064})
    assert 'FORMING PROCESS' in forming.generateReport()
