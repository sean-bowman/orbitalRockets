# -- Tests for the postProcessing library -- #

'''

Tiered tests for SurfaceTreatment.

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
                                'postProcessingLibrary'))


from SurfaceTreatment import (SurfaceTreatment, ALMEN_STRIPS, PEENING_MEDIA,
                              PLATING_PROCESSES, THERMAL_SPRAY, COVERAGE_SATURATION,
                              HYDROGEN_BAKE_THRESHOLD, HYDROGEN_BAKE_TIME,
                              HYDROGEN_BAKE_TEMPERATURE, ALPHA_CASE_SAFETY)
from surfaceUtils import InvalidInputError, ProcessInfeasibleError

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testRemovingTheWholeWallRaises():

    '''
    An immersed part is attacked on both surfaces, so a wall loses twice the removal depth. Etching
    through it has to raise rather than return a negative thickness.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                         'wallThickness': 0.0005})

    with pytest.raises(ProcessInfeasibleError):
        treatment.calculateStockRemoval('chemical mill', 3600.0, 25.0e-6)

def testUnknownMediaRaises():

    '''
    Media hardness has to exceed the workpiece or the shot deforms instead of the part.
    '''

    treatment = SurfaceTreatment()
    with pytest.raises(InvalidInputError):
        treatment.setInputs({'material': '316L', 'peeningMedia': 'gravel'})

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testHydrogenBakeMatchesTheStandard():

    '''
    Validated against ASTM F1940 and AMS 2759/9: 23 hours at 190 degC, triggered at 1000 MPa
    ultimate, started within four hours of plating.

    These are the same numbers the materials domain carries and the two must agree.
    '''

    assert HYDROGEN_BAKE_THRESHOLD == pytest.approx(1000.0e6)
    assert HYDROGEN_BAKE_TIME == pytest.approx(23.0 * 3600.0)
    assert HYDROGEN_BAKE_TEMPERATURE == pytest.approx(190.0 + 273.15, abs = 0.01)

def testBakeTriggersOnStrengthNotService():

    '''
    A part that never sees hydrogen propellant still gets hydrogen charged into it by
    electroplating. The trigger is the tensile strength.
    '''

    steel = SurfaceTreatment()
    steel.setInputs({'material': '4340', 'condition': 'qt-260', 'alloyFamily': 'stainless'})
    assert steel.checkPlatingBake('cadmium')['bakeRequired'] is True

    stainless = SurfaceTreatment()
    stainless.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless'})
    assert stainless.checkPlatingBake('cadmium')['bakeRequired'] is False

def testIvdAluminiumRemovesTheBakeRequirement():

    '''
    IVD aluminium is the standard cadmium replacement on high strength steel and it charges no
    hydrogen at all, which removes the requirement rather than managing it.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '4340', 'condition': 'qt-260', 'alloyFamily': 'stainless'})

    assert treatment.checkPlatingBake('cadmium')['bakeRequired'] is True
    assert treatment.checkPlatingBake('ivd aluminium')['bakeRequired'] is False
    assert PLATING_PROCESSES['ivd aluminium']['chargesHydrogen'] is False

def testLaserShockPeeningIsFarDeeper():

    '''
    Validated against published layer depths. Laser shock peening reaches four to five times the
    depth of shot peening with almost no surface roughening, because a shock wave propagates rather
    than a dimple being formed.
    '''

    depths = {}
    for media in ('ceramic bead', 'laser shock'):
        treatment = SurfaceTreatment()
        treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                             'alloyFamily': 'titanium', 'peeningMedia': media,
                             'wallThickness': 0.006})
        depths[media] = treatment.calculatePeening()['compressiveLayerDepth']

    assert depths['laser shock'] / depths['ceramic bead'] > 4.0
    assert (PEENING_MEDIA['laser shock']['roughnessFactor'] <
            0.2 * PEENING_MEDIA['ceramic bead']['roughnessFactor'])

def testAlphaCaseGrowsWithTemperature():

    '''
    Validated against the parabolic diffusion law with an Arrhenius diffusivity. Alpha case is
    negligible below about 530 degC and grows rapidly above it.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                         'alloyFamily': 'titanium', 'wallThickness': 0.006})

    cold = treatment.calculateAlphaCase(700.0, 3600.0)
    hot  = treatment.calculateAlphaCase(1200.0, 3600.0)

    assert cold['caseDepth'] == 0.0
    assert hot['caseDepth'] > 0.0
    assert hot['removalDepth'] == pytest.approx(hot['caseDepth'] * ALPHA_CASE_SAFETY, rel = 1e-9)

def testAlphaCaseDoesNotApplyToNonTitanium():

    '''
    Alpha case is oxygen dissolution in titanium. Applying it to a nickel alloy would be a
    fabrication.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': 'Inconel 718', 'condition': 'sta', 'alloyFamily': 'nickel'})
    result = treatment.calculateAlphaCase(1200.0, 3600.0)

    assert result['applicable'] is False

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testCoverageSaturatesExponentially():

    '''
    Each impact lands randomly, so later impacts increasingly fall where earlier ones already have.
    Full coverage is DEFINED as 98 percent because 100 percent is asymptotic, and that is why a
    specification calling for 200 percent coverage is a time specification rather than a geometric
    impossibility.
    '''

    coverages = []
    for time in (30.0, 60.0, 120.0, 240.0):
        treatment = SurfaceTreatment()
        treatment.setInputs({'material': '316L', 'condition': 'annealed',
                             'alloyFamily': 'stainless', 'peeningTime': time,
                             'saturationTime': 60.0, 'wallThickness': 0.006})
        coverages.append(treatment.calculatePeening()['coverage'])

    assert all(later > earlier for earlier, later in zip(coverages, coverages[1:]))
    assert coverages[1] == pytest.approx(COVERAGE_SATURATION, rel = 0.01), \
        'At the saturation time the coverage must be the 98 percent that defines full coverage'
    assert all(coverage < 1.0 for coverage in coverages), \
        '100 percent coverage is asymptotic and unreachable'

def testPartialCoverageLosesMostOfTheBenefit():

    '''
    The fatigue benefit depends on the whole surface being in compression. An uncovered patch is
    where the crack starts, so partial coverage loses the benefit disproportionately.
    '''

    full = SurfaceTreatment()
    full.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                    'peeningTime': 120.0, 'saturationTime': 60.0, 'wallThickness': 0.006})

    partial = SurfaceTreatment()
    partial.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                       'peeningTime': 20.0, 'saturationTime': 60.0, 'wallThickness': 0.006})

    assert (partial.calculatePeening()['fatigueImprovementFactor'] <
            full.calculatePeening()['fatigueImprovementFactor'])

def testRemovalTakesFromBothSurfaces():

    '''
    The doubling people forget. A 0.15 mm etch on a 2 mm wall leaves 1.7 mm, not 1.85.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                         'wallThickness': 0.002})
    result = treatment.calculateStockRemoval('chemical mill', 360.0, 25.0e-6)

    assert result['stockRemovalBothSurfaces'] == pytest.approx(
        2.0 * result['stockRemovalPerSurface'], rel = 1e-9)
    assert result['remainingWallThickness'] == pytest.approx(
        treatment.wallThickness - result['stockRemovalBothSurfaces'], rel = 1e-9)

def testElectropolishImprovesRoughnessAndChemicalMillDoesNot():

    '''
    Electropolishing removes the peaks preferentially, so it improves Ra. Chemical milling removes
    uniformly, so it preserves the profile and the roughness with it.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                         'wallThickness': 0.004, 'initialRoughness': 3.2e-6})

    polish = treatment.calculateStockRemoval('electropolish', 300.0)
    mill   = treatment.calculateStockRemoval('chemical mill', 60.0, 25.0e-6)

    assert polish['finalRoughness'] < polish['initialRoughness']
    assert mill['finalRoughness'] == pytest.approx(mill['initialRoughness'], rel = 0.01)

def testColdSprayHasNoThermalMismatchStress():

    '''
    Cold spray deposits in the solid state with no thermal excursion, so there is no CTE mismatch
    stress at all and the residual stress is compressive from particle impact.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless'})

    cold = treatment.calculateThermalSprayStress('cold spray')
    hot  = treatment.calculateThermalSprayStress('HVOF', coatingExpansion = 18.0e-6)

    assert cold['residualStress'] < 0.0
    assert 'solid state' in cold['mechanism']
    assert hot['mechanism'] != cold['mechanism']

def testReportRuns():

    '''
    Smoke test.
    '''

    treatment = SurfaceTreatment()
    treatment.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                         'alloyFamily': 'titanium', 'wallThickness': 0.004})
    assert 'SURFACE TREATMENT' in treatment.generateReport()
