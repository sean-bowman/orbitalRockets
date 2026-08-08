
# -- Tests for the aerospaceStructures component classes -- #

'''

Tiered tests for CylindricalShell and PressureVessel.

Tier 1 covers the contract: thin-shell geometry limits, required inputs, and the guards that stop a
calculation being run outside the range its correlation covers.

Tier 2 validates against published relations: the classical shell buckling stress, the NASA SP-8007
knockdown curve, Bresse external pressure collapse, and membrane theory.

Tier 3 covers self-consistency and the cross-domain coupling: sizing must round trip against
checking, and the allowables must come from the aerospaceMaterials database rather than drifting to
a second copy of the same numbers.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'aerospaceStructuresLibrary'))

from structuresUtils import (structuralAllowables, classicalShellBucklingStress, sp8007Knockdown,
                   transitionSlenderness, marginOfSafety,
                   InvalidInputError, GeometryError)
from CylindricalShell import (CylindricalShell, THIN_SHELL_MINIMUM_RATIO,
                              THIN_SHELL_MAXIMUM_RATIO, BENDING_KNOCKDOWN_RELIEF)
from PressureVessel import (PressureVessel, DOME_TYPES, DOME_COMPRESSION_ASPECT_RATIO,
                            THIN_WALL_MINIMUM_RATIO)

def buildShell(**overrides) -> CylindricalShell:

    '''
    A 1 m radius, 2.5 mm 6061-T6 barrel, which is a representative vehicle section.
    '''

    inputs = {'material': '6061-T6', 'radius': 1.0, 'thickness': 0.0025,
              'length': 3.0, 'axialLoad': 200.0e3}
    inputs.update(overrides)

    shell = CylindricalShell()
    shell.setInputs(inputs)
    return shell

def buildTank(**overrides) -> PressureVessel:

    '''
    A 1 m radius 2219-T87 tank at 2.5 MPa, which is a representative stage tank.
    '''

    inputs = {'material': '2219-T87', 'condition': 't87', 'radius': 1.0,
              'cylindricalLength': 4.0, 'operatingPressure': 2.5e6}
    inputs.update(overrides)

    tank = PressureVessel()
    tank.setInputs(inputs)
    return tank

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testThickShellIsRejected():

    '''
    Thin-shell buckling theory does not describe a thick shell, and applying it silently would give
    a number that looks fine.
    '''

    shell = CylindricalShell()
    shell.setInputs({'radius': 0.1, 'thickness': 0.02})    # R/t = 5

    with pytest.raises(GeometryError):
        shell.calculateAxialBuckling()

def testExcessivelyThinShellIsRejected():

    shell = CylindricalShell()
    shell.setInputs({'radius': 10.0, 'thickness': 0.001})    # R/t = 10000

    with pytest.raises(GeometryError):
        shell.calculateAxialBuckling()

def testShellGeometryLimitsBracketTheUsefulRange():

    assert THIN_SHELL_MINIMUM_RATIO < 100.0 < THIN_SHELL_MAXIMUM_RATIO, \
        'a representative vehicle R/t must sit inside the validated band'

def testSimultaneousInternalAndExternalPressureIsRejected():

    shell = buildShell(internalPressure = 1.0e5, externalPressure = 1.0e5)

    with pytest.raises(InvalidInputError):
        shell.calculateAxialBuckling()

def testExternalPressureNeedsALength():

    shell = CylindricalShell()
    shell.setInputs({'radius': 1.0, 'thickness': 0.0025, 'externalPressure': 5.0e4})

    with pytest.raises(InvalidInputError):
        shell.calculateExternalPressureBuckling()

def testSizingNeedsACompressiveLoad():

    shell = buildShell(axialLoad = 0.0)

    with pytest.raises(InvalidInputError):
        shell.sizeThicknessForAxialLoad()

def testTankRejectsImpossibleJointEfficiency():

    tank = PressureVessel()
    with pytest.raises(InvalidInputError):
        tank.setInputs({'radius': 1.0, 'operatingPressure': 2.0e6, 'jointEfficiency': 1.4})
        tank.sizeWallThickness()

def testTankRejectsUnknownDomeType():

    tank = buildTank(domeType = 'parabolic')

    with pytest.raises(InvalidInputError):
        tank.calculateDomeGeometry()

def testMembraneStressesNeedAThickness():

    tank = buildTank()

    with pytest.raises(InvalidInputError):
        tank.calculateMembraneStresses()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: against published relations -- #
# ------------------------------------------------------------------------------------------------ #

def testClassicalBucklingStressMatchesTheClosedForm():

    '''
    sigma_cl = E t / (R sqrt(3 (1 - nu^2))). Computed independently here.
    '''

    modulus, thickness, radius, poisson = 68.9e9, 0.0025, 1.0, 0.33

    expected = modulus * thickness / (radius * np.sqrt(3.0 * (1.0 - poisson ** 2)))

    assert classicalShellBucklingStress(modulus, thickness, radius, poisson) == \
        pytest.approx(expected, rel = 1.0e-12)

def testSp8007KnockdownMatchesThePublishedCurve():

    '''
    gamma = 1 - 0.901 (1 - exp(-phi)) with phi = sqrt(R/t)/16, evaluated at three ratios.
    '''

    for ratio in (100.0, 400.0, 1500.0):
        phi      = np.sqrt(ratio) / 16.0
        expected = 1.0 - 0.901 * (1.0 - np.exp(-phi))
        assert sp8007Knockdown(ratio) == pytest.approx(expected, rel = 1.0e-12)

def testKnockdownFallsMonotonicallyWithSlenderness():

    '''
    A thinner shell is more imperfection sensitive, so the knockdown must get worse, never better.
    '''

    ratios     = np.array([50.0, 100.0, 200.0, 400.0, 800.0, 1600.0])
    knockdowns = np.array([sp8007Knockdown(ratio) for ratio in ratios])

    assert np.all(np.diff(knockdowns) < 0.0)
    assert np.all((knockdowns > 0.0) & (knockdowns < 1.0))

def testKnockdownAtRepresentativeGeometryIsAboutOneThird():

    '''
    The number the domain turns on. At R/t = 400 the classical solution is nearly three times
    optimistic, which is why a buckling analysis cannot be believed without a knockdown.
    '''

    knockdown = sp8007Knockdown(400.0)

    assert 0.34 < knockdown < 0.37, f'{knockdown:.4f} is outside the expected band'
    assert 2.7 < 1.0 / knockdown < 2.95

def testBucklingGovernsOverYieldForARepresentativeShell():

    '''
    The central claim of the domain, checked numerically rather than asserted in prose.
    '''

    result = buildShell().calculateAxialBuckling()

    assert result['bucklingGoverns']
    assert result['governingRatio'] > 5.0, \
        'a 1 m by 2.5 mm 6061 shell must buckle far below yield'
    assert result['allowableStress'] < result['yieldStrength']

def testExternalPressureCollapseMatchesBresse():

    '''
    Long-shell collapse is p = E/(4(1-nu^2)) (t/R)^3, independent of length.
    '''

    shell = buildShell(length = 100.0)    # long enough to be in the long-shell regime

    result = shell.calculateExternalPressureBuckling()

    expected = (shell.modulus / (4.0 * (1.0 - shell.poisson ** 2))
                * (shell.thickness / shell.radius) ** 3)

    assert result['longShellPressure'] == pytest.approx(expected, rel = 1.0e-12)
    assert result['isLongShell']

def testShortShellIsStrongerThanLongShellUnderExternalPressure():

    '''
    End restraint carries load, so a short shell collapses at a higher pressure. If this inverted,
    the transition logic would be backwards.
    '''

    short = buildShell(length = 0.5).calculateExternalPressureBuckling()
    long_ = buildShell(length = 100.0).calculateExternalPressureBuckling()

    assert not short['isLongShell']
    assert short['allowablePressure'] > long_['allowablePressure']

def testBendingKnockdownIsMoreGenerousThanAxial():

    '''
    Bending is less imperfection sensitive because the peak stress acts over a short arc.
    '''

    shell = buildShell()

    axial   = shell.calculateAxialBuckling()
    bending = shell.calculateBendingBuckling()

    assert bending['knockdown'] > axial['knockdown']
    assert bending['knockdown'] == pytest.approx(
        min(axial['knockdown'] * BENDING_KNOCKDOWN_RELIEF, 1.0), rel = 1.0e-12)

def testMembraneHoopIsTwiceLongitudinal():

    '''
    The reason cylindrical tanks split along a line parallel to the axis.
    '''

    tank = buildTank(thickness = 0.008)

    stresses = tank.calculateMembraneStresses()

    assert stresses['hoopToLongitudinal'] == pytest.approx(2.0, rel = 1.0e-12)
    assert stresses['hoopStress'] == pytest.approx(
        tank.operatingPressure * tank.radius / tank.thickness, rel = 1.0e-12)

def testDomeCompressionThresholdIsRootTwo():

    '''
    Above an aspect ratio of sqrt(2) the equatorial hoop stress goes compressive, which is a
    buckling problem rather than a burst problem.
    '''

    assert DOME_COMPRESSION_ASPECT_RATIO == pytest.approx(np.sqrt(2.0))

    hemisphere = buildTank(domeType = 'hemispherical').calculateDomeGeometry()
    rootTwo    = buildTank(domeType = 'sqrt2 ellipsoidal').calculateDomeGeometry()
    twoToOne   = buildTank(domeType = '2:1 ellipsoidal').calculateDomeGeometry()

    assert hemisphere['equatorialHoopFactor'] > 0.0
    assert rootTwo['equatorialHoopFactor'] == pytest.approx(0.0, abs = 1.0e-12)
    assert twoToOne['equatorialHoopFactor'] < 0.0
    assert twoToOne['equatorInCompression']

def testHemisphereIsTheLongestDome():

    heights = {name: buildTank(domeType = name).calculateDomeGeometry()['domeHeight']
               for name in DOME_TYPES}

    assert heights['hemispherical'] == max(heights.values())
    assert heights['2:1 ellipsoidal'] == min(heights.values())

def testInternalPressureRecoversKnockdown():

    '''
    Pressure stabilization is why a pressurized tank skin carries far more compression than an
    unpressurized one of the same gauge.
    '''

    dry       = buildShell().calculateKnockdown()
    pressured = buildShell(internalPressure = 2.0e5).calculateKnockdown()

    assert pressured['knockdown'] > dry['knockdown']
    assert pressured['pressureRecovery'] > 0.0
    assert pressured['knockdown'] <= 1.0

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency and cross-domain coupling -- #
# ------------------------------------------------------------------------------------------------ #

def testSizingRoundTripsAgainstChecking():

    '''
    A shell sized to zero margin must check out at zero margin. Any disagreement means the sizing
    loop and the check are using different relations.
    '''

    shell = buildShell()
    sized = shell.sizeThicknessForAxialLoad(targetMargin = 0.0)

    checked = buildShell(thickness = sized['thickness']).calculateAxialBuckling()

    assert checked['margin'] == pytest.approx(0.0, abs = 1.0e-6)

def testSizingToAPositiveMarginGivesAThickerWall():

    shell = buildShell()

    tight = shell.sizeThicknessForAxialLoad(targetMargin = 0.0)['thickness']
    loose = shell.sizeThicknessForAxialLoad(targetMargin = 0.5)['thickness']

    assert loose > tight

def testTankWallSizingRoundTripsAgainstTheGoverningMargin():

    '''
    Sizing picks the largest of three requirements, so at that thickness the governing margin must
    be zero and the others positive.
    '''

    tank   = buildTank()
    sizing = tank.sizeWallThickness()

    checked = buildTank(thickness = sizing['requiredThickness']).checkMargins()

    marginByName = {'burst': checked['burstMargin'],
                    'yield': checked['yieldMargin'],
                    'proof': checked['proofMargin']}

    governing = marginByName[sizing['bindingConstraint']]

    assert governing == pytest.approx(0.0, abs = 1.0e-9)
    assert all(value >= -1.0e-9 for value in marginByName.values()), \
        'no requirement may be violated at the sized thickness'

def testProofTestGovernsTheTankWall():

    '''
    The instructive result, and the same pattern as the fluidSystems helium bottle: a tank sized on
    burst alone yields during its own acceptance test.
    '''

    sizing = buildTank().sizeWallThickness()

    assert sizing['bindingConstraint'] == 'proof'
    assert sizing['candidates']['proof'] > sizing['candidates']['burst']
    assert any('acceptance test' in finding for finding in sizing['findings'])

def testCombinedLoadingCanFailWhereEveryLoadAlonePasses():

    '''
    The reason load cases are combined rather than enveloped. Loads are tuned so each ratio is
    below one and the interaction sum is above it.
    '''

    shell = buildShell(axialLoad = 180.0e3, bendingMoment = 130.0e3, torsion = 60.0e3)

    combined = shell.calculateCombinedLoading()

    assert combined['ratioAxial']   < 1.0
    assert combined['ratioBending'] < 1.0
    assert combined['ratioShear']   < 1.0
    assert combined['interaction']  > 1.0
    assert not combined['acceptable']

def testAllowablesComeFromTheMaterialsDomainNotASecondCopy():

    '''
    The cross-domain drift guard. aerospaceMaterials owns the allowables; if this domain ever grew
    its own table the two would diverge silently.
    '''

    properties = structuralAllowables('2219-T87', 't87')

    assert properties['source'] == 'aerospaceMaterials', \
        'the materials database must answer for an alloy outside the common seed table'

    shell = buildShell(material = '2219-T87', condition = 't87')
    shell.calculateAxialBuckling()

    assert shell.yieldStrength == pytest.approx(properties['yieldStrength'], rel = 1.0e-12)
    assert shell.modulus == pytest.approx(properties['elasticModulus'], rel = 1.0e-12)

def testSeedTableStillAnswersForItsOwnAlloys():

    '''
    6061-T6 is in both the seed table and the materials database, and they are enforced equal by
    the materials domain's own tests. Either source is therefore correct here.
    '''

    properties = structuralAllowables('6061-T6')

    assert properties['elasticModulus'] == pytest.approx(68.9e9, rel = 0.02)
    assert properties['yieldStrength'] == pytest.approx(276.0e6, rel = 0.02)

def testABasisIsMoreConservativeThanTypical():

    '''
    An A-basis allowable is a statistical lower bound and must never exceed the typical value.
    '''

    typical = structuralAllowables('2219-T87', 't87', basis = 'typical')
    aBasis  = structuralAllowables('2219-T87', 't87', basis = 'A')

    assert aBasis['yieldStrength'] < typical['yieldStrength']

def testTransitionSlendernessForAluminiumIsAboutSeventy():

    '''
    sqrt(2 pi^2 E / sigma_y) for 6061-T6, a number worth recognising on sight.
    '''

    slenderness = transitionSlenderness(68.9e9, 276.0e6)

    assert 65.0 < slenderness < 75.0

def testMarginOfSafetyDefinition():

    assert marginOfSafety(100.0, 50.0, 1.0) == pytest.approx(1.0)
    assert marginOfSafety(100.0, 50.0, 1.4) == pytest.approx(100.0 / 70.0 - 1.0)
    assert marginOfSafety(100.0, 100.0, 1.0) == pytest.approx(0.0)
    assert np.isinf(marginOfSafety(100.0, 0.0))

def testTankMassScalingSitsBetweenTheBarrelAndDomeLimits():

    '''
    Wall thickness goes as p R. At fixed barrel length the barrel area goes as R, so barrel mass
    goes as R^2, while dome area goes as R^2 so dome mass goes as R^3. Doubling the radius must
    therefore land the total between 4x and 8x, weighted by the area split.

    Getting this wrong in the obvious direction, by assuming a clean R^2, understates a wide tank.
    '''

    small = buildTank(radius = 1.0)
    small.thickness = small.sizeWallThickness()['requiredThickness']
    smallGeometry = small.calculateVolumeAndMass()

    large = buildTank(radius = 2.0)
    large.thickness = large.sizeWallThickness()['requiredThickness']
    largeGeometry = large.calculateVolumeAndMass()

    ratio = largeGeometry['shellMass'] / smallGeometry['shellMass']

    assert 4.0 < ratio < 8.0, f'mass ratio {ratio:.2f} must lie between the two limits'

    # the split moves toward the dome limit as the tank gets wider at fixed length
    smallDomeFraction = (smallGeometry['wettedArea']
                         - 2.0 * np.pi * small.radius * small.cylindricalLength)
    largeDomeFraction = (largeGeometry['wettedArea']
                         - 2.0 * np.pi * large.radius * large.cylindricalLength)

    assert (largeDomeFraction / largeGeometry['wettedArea']
            > smallDomeFraction / smallGeometry['wettedArea']), \
        'a wider tank at fixed length is proportionally more dome'

def testTankWallScalesLinearlyWithPressureAndRadius():

    '''
    The membrane relation itself: t = FS p R / sigma, so the wall is linear in both.
    '''

    base   = buildTank().sizeWallThickness()['requiredThickness']
    doubleP = buildTank(operatingPressure = 5.0e6).sizeWallThickness()['requiredThickness']
    doubleR = buildTank(radius = 2.0).sizeWallThickness()['requiredThickness']

    assert doubleP == pytest.approx(2.0 * base, rel = 1.0e-9)
    assert doubleR == pytest.approx(2.0 * base, rel = 1.0e-9)

def testReportsRunForBothClasses():

    assert 'CYLINDRICAL SHELL' in buildShell().generateReport()
    assert 'PRESSURE VESSEL' in buildTank().generateReport()
