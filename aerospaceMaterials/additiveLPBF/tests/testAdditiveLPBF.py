# -- Tests for the additiveLPBF library -- #

'''

Tiered tests for LpbfProcess, PowderLot and LpbfQualification.

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
                                'additiveLpbfLibrary'))


from LpbfProcess import (LpbfProcess, MELT_PROPERTIES, DFAM_LIMITS,
                         NORMALISED_ENTHALPY_LOWER, NORMALISED_ENTHALPY_UPPER,
                         MELT_POOL_DEPTH_COEFFICIENT)
from PowderLot import PowderLot, OXYGEN_LIMITS, HAUSNER_CLASSIFICATION, PSD_LIMITS
from LpbfQualification import (LpbfQualification, CONSEQUENCE_CLASSES, PROCESS_MATURITY,
                               QUALIFICATION_PILLARS, ORIENTATION_KNOCKDOWN)
from lpbfUtils import InvalidInputError, ProcessInfeasibleError, roughnessTable

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testUnknownMaterialRaises():

    '''
    The process model needs melting point, latent heat and absorptivity. None can be assumed, so an
    unlisted alloy must raise rather than fall back to a default.
    '''

    process = LpbfProcess()
    with pytest.raises(InvalidInputError):
        process.setInputs({'material': 'unobtainium'})

def testUnevacuablePassageRaises():

    '''
    Partially sintered powder in a closed passage cannot be seen, reached or removed, and in a
    propulsion system it migrates downstream into an injector or a valve seat. A passage that cannot
    be verified clear has to raise rather than warn.
    '''

    process = LpbfProcess()
    process.setInputs({'material': 'Inconel 718'})

    with pytest.raises(ProcessInfeasibleError):
        process.checkPowderEvacuation(0.002, 0.200, bends = 3)

def testOxygenLimitRaises():

    '''
    ELI titanium has a 0.03 percent oxygen window between virgin and the grade 5 limit. Past it the
    powder is no longer ELI, a third of the fracture toughness has gone, and nothing visible has
    changed. This must stop the lot rather than warn about it.
    '''

    lot = PowderLot()
    lot.setInputs({'material': 'Ti-6Al-4V ELI', 'reuseCycles': 20})

    with pytest.raises(ProcessInfeasibleError):
        lot.projectOxygenPickup()

def testTappedBelowApparentRaises():

    '''
    Tapping settles powder, so the tapped density is always the higher of the two. A reversed pair
    is a transposition and it would produce a Hausner ratio below one, which is impossible.
    '''

    lot = PowderLot()
    with pytest.raises(InvalidInputError):
        lot.setInputs({'material': '316L', 'apparentDensity': 2800.0, 'tappedDensity': 2500.0})

def testUncontrolledProcessCannotQualifyFlightHardware():

    '''
    No quantity of witness coupons substitutes for a frozen parameter set. Coupons monitor a process
    that is under control and they measure noise on one that is not.
    '''

    qualification = LpbfQualification()
    qualification.setInputs({'consequenceClass': 'AXM', 'processMaturity': 'uncontrolled'})

    with pytest.raises(ProcessInfeasibleError):
        qualification.classifyPart()

def testNonStructuralPartSurvivesAnUncontrolledProcess():

    '''
    The counterpart. A bracket built on an uncontrolled process is still a bracket, and the rule
    above has to be a consequence-class rule rather than a blanket prohibition.
    '''

    qualification = LpbfQualification()
    qualification.setInputs({'consequenceClass': 'CXC', 'processMaturity': 'uncontrolled'})
    result = qualification.classifyPart()

    assert result['rank'] == 1

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testEnergyDensityAgainstPublishedParameterSets():

    '''
    Validated against published production parameter sets. Volumetric energy density for the common
    alloys lands between 40 and 90 J/mm^3, and a value outside that means a unit error in one of the
    four parameters.
    '''

    for material, power, speed in (('Inconel 718', 285.0, 0.960),
                                   ('Ti-6Al-4V',   280.0, 1.200),
                                   ('316L',        195.0, 1.000)):
        process = LpbfProcess()
        process.setInputs({'material': material, 'laserPower': power, 'scanSpeed': speed})
        result = process.calculateEnergyDensity()

        density = result['energyDensityJoulePerCubicMillimetre']
        assert 30.0 < density < 100.0, \
            f'{material} energy density of {density:.1f} J/mm^3 is outside the published range'

def testMeltPoolReachesThePreviousLayer():

    '''
    Validated against published melt pool cross sections. A production Inconel 718 parameter set
    produces a pool about 2.3 layers deep, inside the 1.5 to 2.5 target band.

    Below one layer the fusion is incomplete and the result is flat, layer-aligned porosity that
    behaves like a crack. This is the single most important process check there is.
    '''

    process = LpbfProcess()
    process.setInputs({'material': 'Inconel 718', 'laserPower': 285.0, 'scanSpeed': 0.960})
    process.calculateEnergyDensity()
    result = process.calculateMeltPool()

    assert 1.5 <= result['depthToLayerRatio'] <= 2.5, \
        f'A production parameter set should give 1.5 to 2.5 layers of penetration, got ' \
        f'{result["depthToLayerRatio"]:.2f}. Below 1.0 means lack of fusion.'
    assert result['hatchOverlapFraction'] > 0.20

def testCopperIsHardToProcessBecauseOfAbsorptivity():

    '''
    Validated against the physical reason GRCop-42 exists in the form it does. Copper reflects the
    fibre laser wavelength, so its absorptivity is a fraction of the other alloys and a parameter
    set that works on nickel is deeply lack-of-fusion on copper.
    '''

    copper = MELT_PROPERTIES['GRCOP-42']['absorptivity']
    nickel = MELT_PROPERTIES['INCONEL 718']['absorptivity']

    assert copper < 0.5 * nickel, \
        'Copper absorptivity must be far below nickel at the fibre laser wavelength'

    process = LpbfProcess()
    process.setInputs({'material': 'GRCop-42', 'laserPower': 300.0, 'scanSpeed': 0.800})
    process.calculateEnergyDensity()
    result = process.classifyRegime()

    assert result['processRegime'] == 'lack of fusion', \
        'A nickel-class parameter set on GRCop-42 must come out lack of fusion, which is why the ' \
        'alloy needs far higher power'

def testAdditiveRoughnessMatchesTheSharedTable():

    '''
    The LPBF roughness values live in common/materials.py and this class predicts from them. A test
    on both sides stops the two drifting apart.
    '''

    process = LpbfProcess()
    process.setInputs({'material': 'Inconel 718'})
    result = process.predictSurfaceRoughness(90.0)

    assert result['roughness'] == pytest.approx(roughnessTable('lpbf as-built'), rel = 0.05), \
        'The predicted vertical wall roughness must match roughnessTable(\'lpbf as-built\')'
    assert result['ratioToDrawnTube'] > 10.0

def testHausnerClassificationAgainstCarrScale():

    '''
    Validated against the standard Carr and Hausner flowability scale. A ratio below 1.11 is
    excellent and above 1.34 is poor, and those bounds are what the recoater cares about.
    '''

    lot = PowderLot()
    lot.setInputs({'material': '316L', 'apparentDensity': 4000.0, 'tappedDensity': 4300.0})
    result = lot.calculateFlowability()

    assert result['hausnerRatio'] == pytest.approx(1.075, rel = 0.01)
    assert result['flowability'] == 'excellent'

    poor = PowderLot()
    poor.setInputs({'material': '316L', 'apparentDensity': 3000.0, 'tappedDensity': 4200.0})
    assert poor.calculateFlowability()['flowability'] in ('poor', 'very poor')

def testEliWindowIsNarrowerThanGradeFive():

    '''
    Validated against the AMS specifications. Grade 5 permits 0.20 percent oxygen and ELI permits
    0.13, so the ELI reuse window is a fraction of the grade 5 one. That narrow window is the whole
    reason ELI powder needs a tighter reuse policy.
    '''

    grade5 = OXYGEN_LIMITS['TI-6AL-4V']
    eli    = OXYGEN_LIMITS['TI-6AL-4V ELI']

    assert eli['limit'] < grade5['limit']
    assert (eli['limit'] - eli['virgin']) < (grade5['limit'] - grade5['virgin']), \
        'The ELI reuse window must be narrower than the grade 5 one'

def testCoreQualificationRequiresComputedTomography():

    '''
    An internal passage that a borescope cannot reach cannot be inspected by any method except CT.
    Radiography integrates through the thickness, so a lack of fusion defect in the build plane is
    presented edge-on and is close to invisible, which is exactly the orientation this process
    produces.
    '''

    qualification = LpbfQualification()
    qualification.setInputs({'consequenceClass': 'AXM', 'processMaturity': 'qualified',
                             'hasInternalPassages': True})
    plan = qualification.buildInspectionPlan()

    assert plan['computedTomographyRequired'] is True
    assert any('tomography' in method for method in plan['methods'])

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testEnergyDensityScalesInverselyWithSpeed():

    '''
    E_v = P / (v h t). Doubling the scan speed must halve the energy density exactly.
    '''

    slow = LpbfProcess(); slow.setInputs({'material': '316L', 'scanSpeed': 0.5})
    fast = LpbfProcess(); fast.setInputs({'material': '316L', 'scanSpeed': 1.0})

    assert (slow.calculateEnergyDensity()['energyDensity'] /
            fast.calculateEnergyDensity()['energyDensity']) == pytest.approx(2.0, rel = 1e-9)

def testProcessWindowOrderingIsMonotonic():

    '''
    Raising the power at fixed speed raises the normalised enthalpy monotonically, and the regime
    has to walk from lack of fusion through stable to keyhole in that order.
    '''

    enthalpies = []
    for power in (60.0, 150.0, 300.0, 700.0, 1500.0):
        process = LpbfProcess()
        process.setInputs({'material': '316L', 'laserPower': power, 'scanSpeed': 1.0})
        enthalpies.append(process.calculateEnergyDensity()['normalisedEnthalpy'])

    assert all(later > earlier for earlier, later in zip(enthalpies, enthalpies[1:]))
    assert enthalpies[0] < NORMALISED_ENTHALPY_LOWER
    assert enthalpies[-1] > NORMALISED_ENTHALPY_UPPER

def testRecoatDominatesTallThinBuilds():

    '''
    Recoat time depends on the layer count and not on how much is built per layer, so a tall build
    with a small part is recoat dominated. That is why nesting more parts into the same build height
    is close to free.
    '''

    process = LpbfProcess()
    process.setInputs({'material': '316L'})

    single = process.calculateBuildTime(1.0e-6, 0.20, partsPerBuild = 1)
    many   = process.calculateBuildTime(1.0e-6, 0.20, partsPerBuild = 20)

    assert single['dominantTerm'] == 'recoat'
    assert many['timePerPartHours'] < single['timePerPartHours'] / 5.0, \
        'Nesting twenty parts into a recoat dominated build must cut the per part time sharply'

def testHalvingLayerThicknessRoughlyDoublesBuildTime():

    '''
    Layer thickness has leverage on both terms and in the same direction: it doubles the layer count
    and it halves the volume deposited per pass. A 20 um build is roughly twice as slow as a 40 um
    one, which is the whole cost argument for coarse layers where the finish permits.
    '''

    coarse = LpbfProcess(); coarse.setInputs({'material': '316L', 'layerThickness': 40.0e-6})
    fine   = LpbfProcess(); fine.setInputs({'material': '316L', 'layerThickness': 20.0e-6})

    coarseTime = coarse.calculateBuildTime(1.0e-5, 0.10)['totalTime']
    fineTime   = fine.calculateBuildTime(1.0e-5, 0.10)['totalTime']

    assert 1.7 < fineTime / coarseTime < 2.3, \
        f'Halving the layer thickness should roughly double the build time, got ' \
        f'{fineTime / coarseTime:.2f}x'

def testDownskinIsRougherThanUpskin():

    '''
    A downskin melt pool sits on loose powder rather than solid material, so partially sintered
    particles adhere to the underside. The ordering has to hold at every layer thickness.
    '''

    process = LpbfProcess()
    process.setInputs({'material': 'Ti-6Al-4V'})

    downskin = process.predictSurfaceRoughness(20.0)['roughness']
    vertical = process.predictSurfaceRoughness(90.0)['roughness']
    upskin   = process.predictSurfaceRoughness(170.0)['roughness']

    assert downskin > vertical > upskin

def testBlendBackReachesTheTarget():

    '''
    The blend is a mass balance on the oxygen. Mixing the computed virgin fraction into the used lot
    has to land on the target, or the balance is wrong.
    '''

    lot = PowderLot()
    lot.setInputs({'material': 'Ti-6Al-4V', 'reuseCycles': 10})
    lot.projectOxygenPickup()

    target = 0.15
    result = lot.calculateBlendBack(target)

    blended = (result['virginFraction'] * result['virginOxygen'] +
               (1.0 - result['virginFraction']) * result['currentOxygen'])

    assert blended == pytest.approx(target, rel = 1e-9), \
        'The blended oxygen must equal the target, or the mass balance is wrong'

def testCouponCountRisesWithConsequenceAndFallsWithMaturity():

    '''
    Two independent axes. A higher consequence class needs more evidence; a better controlled
    process needs less of it for the same confidence.
    '''

    counts = {}
    for consequence in ('CXC', 'BXB', 'AXB', 'AXM'):
        qualification = LpbfQualification()
        qualification.setInputs({'consequenceClass': consequence, 'processMaturity': 'qualified'})
        counts[consequence] = qualification.calculateCouponRequirement()['couponsRequired']

    assert counts['CXC'] < counts['BXB'] < counts['AXB'] < counts['AXM']

    qualified = LpbfQualification()
    qualified.setInputs({'consequenceClass': 'AXB', 'processMaturity': 'qualified'})

    developmental = LpbfQualification()
    developmental.setInputs({'consequenceClass': 'AXB', 'processMaturity': 'developmental'})

    assert (developmental.calculateCouponRequirement()['couponsRequired'] >
            qualified.calculateCouponRequirement()['couponsRequired'])

def testUnknownOrientationIsPenalisedBelowZ():

    '''
    An unspecified build orientation carries a worse knockdown than the Z direction, and
    deliberately: if the orientation is not on the drawing then nothing stops a build being oriented
    badly, so the worst case has to be assumed.
    '''

    assert (ORIENTATION_KNOCKDOWN['unknown']['factor'] <
            ORIENTATION_KNOCKDOWN['Z']['factor'] <
            ORIENTATION_KNOCKDOWN['XY']['factor'])

def testEveryPillarHasADescription():

    '''
    The five pillars are a checklist, and a pillar without a description cannot be assessed.
    '''

    assert len(QUALIFICATION_PILLARS) == 5
    for key, description in QUALIFICATION_PILLARS:
        assert key and description

def testReportsRunForEveryClass():

    '''
    A smoke test. generateReport touches nearly every field.
    '''

    process = LpbfProcess(); process.setInputs({'material': 'Ti-6Al-4V'})
    assert 'LPBF PROCESS' in process.generateReport()

    lot = PowderLot(); lot.setInputs({'material': '316L'})
    assert 'POWDER LOT' in lot.generateReport()

    qualification = LpbfQualification()
    qualification.setInputs({'consequenceClass': 'AXB', 'hasInternalPassages': True})
    assert 'LPBF QUALIFICATION' in qualification.generateReport()
