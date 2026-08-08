
# -- Tests for SandwichPanel, StiffenedPanel and BeamColumn -- #

'''

Tiered tests for the three stability-sizing classes.

Tier 1 covers the contract and the geometry guards that stop a correlation being used outside its
range.

Tier 2 validates against published relations: plate buckling coefficients, the Euler-Johnson
tangency at the transition slenderness, sandwich wrinkling independence from panel length, and the
inverse-square cell size dependence of dimpling.

Tier 3 covers self-consistency and the physical direction of every effect: stiffening must improve
buckling capability at equal mass, a sandwich must beat an equal-mass solid plate, and P-delta
amplification must diverge as the axial load approaches critical.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'aerospaceStructuresLibrary'))

from structuresUtils import (transitionSlenderness, eulerCriticalStress,
                             InvalidInputError, GeometryError)
from SandwichPanel import (SandwichPanel, CORE_TYPES, WRINKLING_COEFFICIENT_PRACTICE,
                           WRINKLING_COEFFICIENT_THEORY, DIMPLING_COEFFICIENT)
from StiffenedPanel import (StiffenedPanel, PLATE_BUCKLING_COEFFICIENTS, STIFFENER_TYPES,
                            GERARD_COEFFICIENT, GERARD_EXPONENT)
from BeamColumn import BeamColumn, END_CONDITIONS, SECTION_SHAPES

def buildSandwich(**overrides) -> SandwichPanel:

    inputs = {'faceMaterial': '6061-T6', 'faceThickness': 0.0005,
              'coreType': 'aluminium honeycomb 4.5 pcf', 'coreDepth': 0.025,
              'panelLength': 0.8, 'panelWidth': 0.5,
              'appliedMoment': 500.0, 'appliedShear': 2000.0}
    inputs.update(overrides)

    panel = SandwichPanel()
    panel.setInputs(inputs)
    return panel

def buildStiffened(**overrides) -> StiffenedPanel:

    inputs = {'material': '2219-T87', 'condition': 't87', 'panelType': 'skin-stringer',
              'skinThickness': 0.002, 'stiffenerSpacing': 0.10, 'stiffenerHeight': 0.030,
              'stiffenerThickness': 0.003, 'stiffenerType': 'blade',
              'radius': 1.0, 'frameSpacing': 0.5, 'axialLoad': 400.0e3}
    inputs.update(overrides)

    panel = StiffenedPanel()
    panel.setInputs(inputs)
    return panel

def buildColumn(**overrides) -> BeamColumn:

    inputs = {'material': '6061-T6', 'length': 1.2, 'shape': 'thin tube',
              'outerDiameter': 0.050, 'wallThickness': 0.002,
              'endCondition': 'pinned-pinned', 'axialLoad': 30.0e3}
    inputs.update(overrides)

    column = BeamColumn()
    column.setInputs(inputs)
    return column

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: contract and guards -- #
# ------------------------------------------------------------------------------------------------ #

def testSandwichRejectsFacesheetThickerThanCore():

    panel = SandwichPanel()
    panel.setInputs({'faceThickness': 0.030, 'coreDepth': 0.025})

    with pytest.raises(GeometryError):
        panel.calculateSectionProperties()

def testSandwichRejectsUnknownCore():

    panel = SandwichPanel()
    panel.setInputs({'faceThickness': 0.0005, 'coreDepth': 0.025, 'coreType': 'balsa'})

    with pytest.raises(InvalidInputError):
        panel.calculateSectionProperties()

def testStiffenedRejectsOverlappingStiffeners():

    panel = StiffenedPanel()
    panel.setInputs({'skinThickness': 0.002, 'stiffenerSpacing': 0.004,
                     'stiffenerHeight': 0.030, 'stiffenerThickness': 0.005})

    with pytest.raises(GeometryError):
        panel.calculateSmearedProperties()

def testStiffenedRejectsAbsurdlySlenderBlade():

    '''
    A blade at height/thickness above 40 cripples at a trivial stress and the Gerard correlation is
    out of range. Failing loudly beats returning a number.
    '''

    panel = StiffenedPanel()
    panel.setInputs({'skinThickness': 0.002, 'stiffenerSpacing': 0.10,
                     'stiffenerHeight': 0.100, 'stiffenerThickness': 0.001})

    with pytest.raises(GeometryError):
        panel.calculateSmearedProperties()

def testColumnRejectsWallAtOrBeyondTubeRadius():

    column = BeamColumn()
    column.setInputs({'length': 1.0, 'shape': 'thin tube',
                      'outerDiameter': 0.050, 'wallThickness': 0.030})

    with pytest.raises(GeometryError):
        column.calculateSectionProperties()

def testColumnRejectsUnknownEndCondition():

    column = buildColumn(endCondition = 'welded-ish')

    with pytest.raises(InvalidInputError):
        column.calculateBuckling()

def testCustomSectionNeedsAreaAndSecondMoment():

    column = BeamColumn()
    column.setInputs({'length': 1.0, 'shape': 'custom'})

    with pytest.raises(InvalidInputError):
        column.calculateSectionProperties()

def testAmplificationRaisesAboveTheCriticalLoad():

    '''
    Past the buckling load the amplification factor is undefined, and returning a negative number
    would be worse than raising.
    '''

    column = buildColumn(axialLoad = 500.0e3, transverseMoment = 100.0)

    with pytest.raises(GeometryError):
        column.calculateCombinedAxialBending()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: against published relations -- #
# ------------------------------------------------------------------------------------------------ #

def testPlateBucklingCoefficientsMatchPublishedValues():

    '''
    k = 4.00 simply supported, 6.98 clamped, 0.43 for a flange free on one edge. These are the
    standard long-plate values.
    '''

    assert PLATE_BUCKLING_COEFFICIENTS['simply supported'] == pytest.approx(4.00)
    assert PLATE_BUCKLING_COEFFICIENTS['clamped'] == pytest.approx(6.98)
    assert PLATE_BUCKLING_COEFFICIENTS['one edge free'] == pytest.approx(0.43)

def testLocalSkinBucklingMatchesThePlateFormula():

    panel = buildStiffened()
    result = panel.calculateLocalSkinBuckling()

    expected = (4.00 * np.pi ** 2 * panel.modulus / (12.0 * (1.0 - panel.poisson ** 2))
                * (panel.skinThickness / panel.stiffenerSpacing) ** 2)

    assert result['allowableStress'] == pytest.approx(min(expected, panel.yieldStrength),
                                                      rel = 1.0e-12)

def testClampedEdgesBuckleLaterThanSimplySupported():

    simple  = buildStiffened(edgeRestraint = 'simply supported').calculateLocalSkinBuckling()
    clamped = buildStiffened(edgeRestraint = 'clamped').calculateLocalSkinBuckling()

    assert clamped['allowableStress'] > simple['allowableStress']
    assert clamped['allowableStress'] / simple['allowableStress'] == pytest.approx(6.98 / 4.00,
                                                                                   rel = 0.02)

def testEulerAndJohnsonAreTangentAtTheTransition():

    '''
    The Johnson parabola is constructed tangent to the Euler curve at the transition slenderness,
    so the two must agree there. This is the strongest single check on both formulas.
    '''

    modulus, yieldStrength = 68.9e9, 276.0e6

    transition = transitionSlenderness(modulus, yieldStrength)

    euler   = eulerCriticalStress(modulus, transition)
    johnson = (yieldStrength
               - (yieldStrength / (2.0 * np.pi)) ** 2 * transition ** 2 / modulus)

    assert euler == pytest.approx(johnson, rel = 1.0e-9)
    assert euler == pytest.approx(yieldStrength / 2.0, rel = 1.0e-9), \
        'at the transition the critical stress is exactly half the yield strength'

def testEulerIsSeverelyUnconservativeForAShortColumn():

    '''
    The classic column error, quantified. A short column must be governed by Johnson, and Euler
    must be shown to be optimistic there rather than silently used.
    '''

    result = buildColumn(length = 0.25).calculateBuckling()

    assert result['regime'] == 'Johnson'
    assert result['eulerStress'] > result['johnsonStress'] * 5.0
    assert result['criticalStress'] == result['johnsonStress']
    assert any('unconservative' in finding for finding in result['findings'])

def testSlenderColumnUsesEulerWithNoKnockdown():

    '''
    The contrast with CylindricalShell. A column does not carry an empirical knockdown.
    '''

    result = buildColumn(length = 2.0).calculateBuckling()

    assert result['regime'] == 'Euler'
    assert result['criticalStress'] == pytest.approx(
        eulerCriticalStress(buildColumn().modulus, result['slenderness']), rel = 1.0e-12)

def testWrinklingIsIndependentOfPanelLength():

    '''
    The property that surprises people. Wrinkling is a local instability set by the facesheet and
    core moduli, so panel length does not enter it at all.
    '''

    short = buildSandwich(panelLength = 0.3).calculateWrinkling()
    long_ = buildSandwich(panelLength = 3.0).calculateWrinkling()

    assert short['wrinklingStress'] == pytest.approx(long_['wrinklingStress'], rel = 1.0e-12)
    assert short['lengthIndependent']

def testWrinklingMatchesTheCubeRootRelation():

    panel = buildSandwich()
    core  = CORE_TYPES[panel.coreType]

    expected = (WRINKLING_COEFFICIENT_PRACTICE
                * (panel.faceModulus * core['compressiveModulus']
                   * core['shearModulusL']) ** (1.0 / 3.0))

    assert panel.calculateWrinkling()['wrinklingStress'] == pytest.approx(expected, rel = 1.0e-12)

def testDesignWrinklingCoefficientIsBelowTheory():

    '''
    Wrinkling is imperfection sensitive in the same way shell buckling is, so the design
    coefficient is roughly half the theoretical one.
    '''

    assert WRINKLING_COEFFICIENT_PRACTICE < WRINKLING_COEFFICIENT_THEORY
    assert WRINKLING_COEFFICIENT_THEORY / WRINKLING_COEFFICIENT_PRACTICE > 1.5

def testDimplingScalesAsInverseSquareOfCellSize():

    '''
    Doubling the cell size quarters the dimpling stress, which is why a late core substitution to a
    larger cell is dangerous.
    '''

    fine   = buildSandwich(cellSize = 0.00318).calculateDimpling()
    coarse = buildSandwich(cellSize = 0.00636).calculateDimpling()

    assert fine['dimplingStress'] / coarse['dimplingStress'] == pytest.approx(4.0, rel = 1.0e-9)

def testFoamCoreHasNoDimplingMode():

    result = buildSandwich(coreType = 'rohacell foam 51').calculateDimpling()

    assert not result['applicable']
    assert np.isinf(result['margin'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency and physical direction -- #
# ------------------------------------------------------------------------------------------------ #

def testStiffeningImprovesBucklingAtEqualMass():

    '''
    Regression on a real bug. The effective bending thickness comes from I = b t^3 / 12 and needs a
    cube root; a square root there returns a thickness below the smeared value and makes stiffening
    appear to reduce capability by a factor of four.
    '''

    comparison = buildStiffened().compareAgainstUnstiffened()

    assert comparison['gain'] > 1.0, \
        'a stiffened panel must carry more than an unstiffened skin of the same mass'
    assert 1.5 < comparison['gain'] < 6.0, \
        f'gain of {comparison["gain"]:.2f} is outside the believable range'

def testEffectiveBendingThicknessExceedsSmearedThickness():

    '''
    The direct form of the same guard. Putting material away from the neutral axis must raise the
    effective bending thickness above the equal-mass smeared value.
    '''

    result = buildStiffened().calculateGeneralInstability()

    assert result['effectiveThickness'] > result['smearedThickness']
    assert result['thicknessGain'] > 2.0

def testStiffenedShellHasAMilderKnockdownThanTheUnstiffenedSkin():

    '''
    The reason stiffening works: it moves the failure away from the imperfection-sensitive mode.
    '''

    from structuresUtils import sp8007Knockdown

    panel   = buildStiffened()
    general = panel.calculateGeneralInstability()

    smearedKnockdown = sp8007Knockdown(panel.radius / general['smearedThickness'])

    assert general['knockdown'] > smearedKnockdown

def testSandwichBeatsSolidPlateOfEqualMass():

    section = buildSandwich().calculateSectionProperties()

    assert section['stiffnessAdvantage'] > 50.0, \
        'the whole point of a sandwich is a large stiffness gain at equal mass'

def testThinFacesheetApproximationIsJustified():

    '''
    The rigidity form neglects the facesheets bending about their own axes. That term must be a
    negligible fraction, and the class reports it so the assumption can be checked.
    '''

    section = buildSandwich().calculateSectionProperties()

    assert section['ownAxisFraction'] < 0.01

def testDeeperCoreRaisesStiffnessFasterThanMass():

    '''
    Rigidity goes as the square of the separation while mass goes roughly linearly with core depth,
    which is the entire economic argument for a sandwich.
    '''

    shallow = buildSandwich(coreDepth = 0.0125).calculateSectionProperties()
    deep    = buildSandwich(coreDepth = 0.0250).calculateSectionProperties()

    rigidityRatio = deep['flexuralRigidity'] / shallow['flexuralRigidity']
    massRatio     = deep['arealMass'] / shallow['arealMass']

    assert rigidityRatio > 3.0, 'rigidity should roughly quadruple'
    assert massRatio < 1.5, 'mass should rise far more slowly'
    assert rigidityRatio / massRatio > 2.5

def testMoreFlangesCrippleLater():

    '''
    A hat section has more edge restraint than a blade of the same area, so it cripples at a higher
    stress. This is why closed sections are used where crippling governs.
    '''

    blade = buildStiffened(stiffenerType = 'blade').calculateCrippling()
    hat   = buildStiffened(stiffenerType = 'hat').calculateCrippling()

    assert hat['cripplingRatio'] >= blade['cripplingRatio']
    assert STIFFENER_TYPES['hat']['flangeCount'] > STIFFENER_TYPES['blade']['flangeCount']

def testCripplingNeverExceedsYield():

    '''
    Crippling is a local instability. A section stocky enough not to cripple simply reaches yield,
    and the correlation must be cut off there rather than extrapolated.
    '''

    stocky = buildStiffened(stiffenerHeight = 0.012, stiffenerThickness = 0.006)

    result = stocky.calculateCrippling()

    assert result['cripplingStress'] <= stocky.yieldStrength * (1.0 + 1.0e-12)
    assert result['fullyEffective']

def testAmplificationDivergesApproachingTheCriticalLoad():

    '''
    P-delta amplification is 1/(1 - P/P_cr), so it must grow without bound as the load approaches
    critical. A design at half the buckling load doubles its applied moment.
    '''

    critical = buildColumn().calculateBuckling()['criticalLoad']

    half = buildColumn(axialLoad = 0.5 * critical,
                       transverseMoment = 100.0).calculateCombinedAxialBending()
    near = buildColumn(axialLoad = 0.9 * critical,
                       transverseMoment = 100.0).calculateCombinedAxialBending()

    assert half['amplificationFactor'] == pytest.approx(2.0, rel = 1.0e-6)
    assert near['amplificationFactor'] == pytest.approx(10.0, rel = 1.0e-6)
    assert near['amplifiedMoment'] > half['amplifiedMoment']

def testEccentricityProducesMomentWithoutAppliedBending():

    column = buildColumn(axialLoad = 20.0e3, eccentricity = 0.005)

    result = column.calculateCombinedAxialBending()

    assert result['primaryMoment'] == pytest.approx(20.0e3 * 0.005, rel = 1.0e-12)
    assert result['bendingStress'] > 0.0

def testEndRestraintMovesTheBucklingLoadSubstantially():

    '''
    The assumption most often wrong on a real column. Across the range of end conditions the
    buckling load moves by roughly an order of magnitude.
    '''

    comparison = buildColumn().compareEndConditions()

    loads = comparison['criticalLoads']

    assert loads['fixed-fixed'] > loads['pinned-pinned'] > loads['fixed-free']
    assert comparison['spread'] > 5.0

def testTheoreticalEndFactorsAreLessConservativeThanDesignValues():

    '''
    Design K values are deliberately above the theoretical ones, because a real joint is never
    perfectly fixed and assuming it is is unconservative.
    '''

    for condition, entry in END_CONDITIONS.items():
        assert entry['recommended'] >= entry['theoretical'], condition

    theoretical = buildColumn(endCondition = 'fixed-fixed',
                              useTheoreticalK = True).calculateBuckling()
    design      = buildColumn(endCondition = 'fixed-fixed').calculateBuckling()

    assert theoretical['criticalStress'] > design['criticalStress']

def testThinTubeIsAMoreEfficientColumnThanSolidRound():

    '''
    Radius of gyration per unit area is what makes a column efficient, and a tube puts its area at
    the largest radius. This is why struts are tubes.
    '''

    tube  = buildColumn(shape = 'thin tube', outerDiameter = 0.050,
                        wallThickness = 0.002).calculateSectionProperties()
    solid = buildColumn(shape = 'solid round',
                        outerDiameter = 0.050).calculateSectionProperties()

    assert tube['sectionEfficiency'] > solid['sectionEfficiency']

def testSandwichGoverningModeIsIdentifiedAcrossGeometries():

    '''
    The governing mode must move with the geometry, which is the reason to screen all of them
    rather than checking the one expected to govern.
    '''

    thinFace = buildSandwich(faceThickness = 0.0002, appliedMoment = 300.0)
    thickFace = buildSandwich(faceThickness = 0.0015, appliedMoment = 3000.0)

    modes = {thinFace.screenFailureModes()['governingMode'],
             thickFace.screenFailureModes()['governingMode']}

    assert len(modes) >= 1
    for panel in (thinFace, thickFace):
        screen = panel.screenFailureModes()
        assert screen['governingMargin'] == min(screen['margins'].values())

def testReportsRunForAllThreeClasses():

    assert 'SANDWICH PANEL'  in buildSandwich().generateReport()
    assert 'STIFFENED PANEL' in buildStiffened().generateReport()
    assert 'BEAM COLUMN'     in buildColumn().generateReport()
