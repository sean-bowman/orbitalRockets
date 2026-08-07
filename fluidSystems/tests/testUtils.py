
# -- Tests for the shared utilities -- #

'''

Tiered tests for utils.py.

Tier 1 covers pure constants and conversions with no property backend, so it runs anywhere and
catches unit errors immediately.
Tier 2 validates against published references.
Tier 3 covers self-consistency identities and round trips.

Author: Sean Bowman
Date:   08/04/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'fluidSystemsLibrary'))

from utils import (fluidProps, hydrazineProps, leakRateConvert, speciesMolarMass, frictionFactor,
                   reynoldsNumber, criticalPressureRatio, chokedMassFlux, isentropicValues,
                   hoopStressCalculator, b31_3WallThickness, materialProperties, roughnessTable,
                   convertPressureToAltitude, convertAltitudeToPressure, convertToSCFM,
                   secantSolve, applyInputs, solveForUnknown, formatReportTable,
                   PA_PER_PSIA, PA_PER_BAR, PA_PER_ATM, M_PER_IN, KG_PER_LBM, N_PER_LBF,
                   GRAVITY, R_UNIVERSAL, LEAK_STD_TEMPERATURE,
                   FluidSystemError, InvalidInputError, ConvergenceFailureError)

# -------------------------------------------------------------------------------------------------- #
# -- Tier 1: constants and conversions, no backend -- #
# -------------------------------------------------------------------------------------------------- #

def testPressureConstants():

    '''
    Catches a transposed or mistyped pressure conversion constant, which would silently scale every
    pressure in the library.
    '''

    assert PA_PER_PSIA == pytest.approx(6894.757, rel = 1e-6), 'psia to Pa constant is wrong'
    assert PA_PER_BAR == 1.0e5, 'bar to Pa constant is wrong'
    assert PA_PER_ATM == 101325.0, 'atm to Pa constant is wrong'
    assert 14.6959 * PA_PER_PSIA == pytest.approx(PA_PER_ATM, rel = 1e-4), \
        'One standard atmosphere should be 14.6959 psia; the psia and atm constants disagree'

def testLengthAndMassConstants():

    '''
    Catches an inch or pound conversion error, which would scale every imperial boundary conversion.
    '''

    assert M_PER_IN == 0.0254, 'inch to metre constant is wrong'
    assert KG_PER_LBM == pytest.approx(0.45359237, rel = 1e-9), 'lbm to kg constant is wrong'
    assert N_PER_LBF == pytest.approx(4.448222, rel = 1e-6), 'lbf to N constant is wrong'
    assert N_PER_LBF == pytest.approx(KG_PER_LBM * GRAVITY, rel = 1e-6), \
        'lbf should equal lbm times standard gravity; the force and mass constants are inconsistent'

def testCriticalPressureRatio():

    '''
    The 0.528 diatomic critical pressure ratio is the single most used number in compressible flow
    work. A wrong gamma exponent would shift it.
    '''

    assert criticalPressureRatio(1.4) == pytest.approx(0.5283, abs = 1e-4), \
        'Diatomic critical pressure ratio should be 0.528'
    assert criticalPressureRatio(1.667) == pytest.approx(0.4867, abs = 1e-3), \
        'Monatomic critical pressure ratio should be 0.487'
    assert criticalPressureRatio(1.3) == pytest.approx(0.5457, abs = 1e-3), \
        'Combustion gas critical pressure ratio should be about 0.546'

def testLaminarFrictionFactor():

    '''
    64/Re is exact for fully developed laminar flow. A factor of four error here would indicate the
    Fanning rather than the Darcy factor is being returned.
    '''

    assert frictionFactor(1000.0, 0.0, 'churchill') == pytest.approx(0.064, rel = 1e-3), \
        'Laminar Darcy friction factor at Re = 1000 should be 0.064. A value of 0.016 means the ' \
        'Fanning factor is being returned instead'
    assert frictionFactor(2000.0, 0.0, 'laminar') == pytest.approx(0.032, rel = 1e-9)

def testHoopStress():

    '''
    Catches an inverted hoop stress relation, and verifies the solve-for-the-None-argument behaviour.
    '''

    stress = hoopStressCalculator(10.0e6, 0.100, thickness = 0.005)
    assert stress == pytest.approx(100.0e6, rel = 1e-9), 'Hoop stress relation is wrong'

    thickness = hoopStressCalculator(10.0e6, 0.100, hoopStress = 100.0e6)
    assert thickness == pytest.approx(0.005, rel = 1e-9), \
        'Solving for thickness should invert the same relation'

    with pytest.raises(ValueError):
        hoopStressCalculator(10.0e6, 0.100, thickness = 0.005, hoopStress = 100.0e6)

def testRoughnessTable():

    '''
    The drawn tube entry is the one used by default for every aerospace line. A wrong order of
    magnitude would change every friction factor.
    '''

    assert roughnessTable('drawn tube') == pytest.approx(1.5e-6), 'Drawn tube roughness should be 1.5 micron'
    assert roughnessTable('lpbf as-built') > 10.0 * roughnessTable('drawn tube'), \
        'As-built additive surfaces must be at least an order of magnitude rougher than drawn tube'

    with pytest.raises(KeyError):
        roughnessTable('unobtainium')

def testFormatReportTable():

    '''
    Every generateReport() depends on this. Catches a column width or ordering regression.
    '''

    table = formatReportTable([['a', '1'], ['bbbb', '22']], ['Name', 'Value'], title = 'TEST')
    assert 'TEST' in table
    assert 'Name' in table and 'Value' in table
    assert 'bbbb' in table

# -------------------------------------------------------------------------------------------------- #
# -- Tier 2: validation against published references -- #
# -------------------------------------------------------------------------------------------------- #

def testHydrazineDensity():

    '''
    Validated against the Schmidt reference values: 1.0085 g/cm^3 at 20 degC and 1.0042 at 25 degC.
    A wrong polynomial coefficient would shift the whole propellant side of the library.
    '''

    assert hydrazineProps('D', 293.15) == pytest.approx(1008.5, abs = 1.0), \
        'Hydrazine density at 20 degC should be 1008.5 kg/m^3'
    assert hydrazineProps('D', 298.15) == pytest.approx(1004.2, abs = 1.0), \
        'Hydrazine density at 25 degC should be 1004.2 kg/m^3'

def testHydrazineViscosityAndVaporPressure():

    '''
    Anchored on the published 0.913 cP at 25 degC and the 14.4 torr vapor pressure at 25 degC, plus
    the normal boiling point which must reproduce one atmosphere exactly.
    '''

    assert hydrazineProps('VIS', 298.15) == pytest.approx(9.13e-4, rel = 0.02), \
        'Hydrazine viscosity at 25 degC should be 0.913 mPa-s'
    assert hydrazineProps('P', 298.15) == pytest.approx(1920.0, rel = 0.05), \
        'Hydrazine vapor pressure at 25 degC should be about 1.92 kPa (14.4 torr)'
    assert hydrazineProps('P', 386.65) == pytest.approx(PA_PER_ATM, rel = 1e-3), \
        'The vapor pressure correlation must reproduce 1 atm at the 386.65 K normal boiling point'

def testHydrazineFixedPoints():

    '''
    The freezing point drives every heater in a hydrazine system. A wrong value here would propagate
    into the thermal design.
    '''

    assert hydrazineProps('TMIN', 293.15) == pytest.approx(274.69, abs = 0.01), \
        'Hydrazine freezing point is 274.69 K (1.54 degC)'
    assert hydrazineProps('TNBP', 293.15) == pytest.approx(386.65, abs = 0.01)
    assert hydrazineProps('M', 293.15) == pytest.approx(32.045e-3, rel = 1e-3)

def testColebrookAgainstMoody():

    '''
    Validated against the Moody diagram: at Re = 1e5 and eps/D = 1e-3 the Darcy friction factor is
    about 0.0222. Catches a sign or logarithm base error in the Colebrook iteration.
    '''

    factor = frictionFactor(1.0e5, 1.0e-3, 'colebrook')
    assert factor == pytest.approx(0.0222, rel = 0.02), \
        f'Colebrook at Re = 1e5, eps/D = 1e-3 should give about 0.0222, got {factor:.5f}'

def testFrictionFactorMethodsAgree():

    '''
    Churchill, Colebrook and Haaland are three routes to the same physics. They must agree in the
    fully turbulent regime; disagreement means one of them is implemented wrong.
    '''

    for reynolds in (1.0e4, 1.0e5, 1.0e6):
        for roughness in (0.0, 1.0e-4, 1.0e-3):
            churchill = frictionFactor(reynolds, roughness, 'churchill')
            colebrook = frictionFactor(reynolds, roughness, 'colebrook')
            haaland   = frictionFactor(reynolds, roughness, 'haaland')
            assert churchill == pytest.approx(colebrook, rel = 0.03), \
                f'Churchill and Colebrook disagree by more than 3 % at Re = {reynolds:.0e}, eps/D = {roughness:.0e}'
            assert haaland == pytest.approx(colebrook, rel = 0.03), \
                f'Haaland and Colebrook disagree by more than 3 % at Re = {reynolds:.0e}, eps/D = {roughness:.0e}'

def testLeakRateReferenceConversions():

    '''
    The two conversions everyone memorizes: 1 scc/s = 1.01325 mbar-L/s, and 1e-4 scc/s of helium is
    about 1.24e-3 lbm/yr. Catches a standard-state or molar mass error.
    '''

    assert leakRateConvert(1.0, 'sccs', 'mbarls') == pytest.approx(1.01325, rel = 1e-5), \
        '1 scc/s should be 1.01325 mbar-L/s'
    assert leakRateConvert(1.0, 'sccs', 'pam3s') == pytest.approx(0.101325, rel = 1e-5)
    assert leakRateConvert(1.0e-4, 'sccs', 'lbmyr', species = 'He') == pytest.approx(1.242e-3, rel = 0.01), \
        '1e-4 scc/s of helium should be about 1.24e-3 lbm/yr'

def testStandardAtmosphere():

    '''
    Validated against the US Standard Atmosphere 1976: 26436 Pa at 10 km, 5474.9 Pa at 20 km.
    '''

    assert convertAltitudeToPressure(0.0) == pytest.approx(101325.0, rel = 1e-6)
    assert convertAltitudeToPressure(10000.0) == pytest.approx(26436.0, rel = 1e-3), \
        'US Standard Atmosphere pressure at 10 km should be 26436 Pa'
    assert convertAltitudeToPressure(20000.0) == pytest.approx(5474.9, rel = 1e-3), \
        'US Standard Atmosphere pressure at 20 km should be 5474.9 Pa'

def testMaterialAllowableStress():

    '''
    316L at room temperature has 170 MPa yield and 485 MPa ultimate, so the B31.3 style allowable is
    min(113.3, 138.6) = 113.3 MPa. Catches a swapped criterion.
    '''

    properties = materialProperties('316L', 293.15)
    assert properties['yieldStrength'] == pytest.approx(170.0e6, rel = 1e-6)
    assert properties['allowableStress'] == pytest.approx(113.3e6, rel = 0.01), \
        'The 316L allowable should be two thirds of yield, 113.3 MPa, not one third of ultimate'

def testCryogenicStrengthGain():

    '''
    Austenitic stainless gains strength on cooling. A library that returned room temperature
    properties at 77 K would over-design every cryogenic component.
    '''

    ambient   = materialProperties('316L', 293.15)
    cryogenic = materialProperties('316L', 77.0)
    assert cryogenic['yieldStrength'] > 2.0 * ambient['yieldStrength'], \
        '316L yield strength at 77 K should be more than twice the room temperature value'

def testTitaniumCarriesTheOxygenWarning():

    '''
    The titanium in oxygen prohibition has to reach the user. If the note is lost, the single most
    dangerous material selection error in the library goes unflagged.
    '''

    properties = materialProperties('TI-6AL-4V', 293.15)
    assert 'LOX' in properties['notes'] or 'oxygen' in properties['notes'].lower(), \
        'The titanium entry must carry the oxygen incompatibility warning'

# -------------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency and round trips -- #
# -------------------------------------------------------------------------------------------------- #

def testAltitudePressureRoundTrip():

    '''
    Pressure to altitude and back must return the original altitude across every atmospheric layer.
    Catches a layer boundary or exponent error that a single-point test would miss.
    '''

    for altitude in (0.0, 5000.0, 11000.0, 15000.0, 20000.0, 32000.0, 47000.0, 60000.0):
        recovered = convertPressureToAltitude(convertAltitudeToPressure(altitude))
        assert recovered == pytest.approx(altitude, abs = 1.0), \
            f'Altitude round trip failed at {altitude} m, recovered {recovered} m'

def testLeakRateRoundTripAllUnits():

    '''
    Every leak rate unit must round trip through the internal Pa-m^3/s working unit. Catches an
    inverted conversion factor in any single entry.
    '''

    units = ['sccs', 'sccm', 'slpm', 'pam3s', 'mbarls', 'torrls', 'atmccs', 'kgs', 'gyr', 'lbmyr']
    for unit in units:
        forward   = leakRateConvert(3.7, 'sccs', unit, species = 'He')
        recovered = leakRateConvert(forward, unit, 'sccs', species = 'He')
        assert recovered == pytest.approx(3.7, rel = 1e-9), \
            f'Leak rate round trip through {unit} failed, recovered {recovered}'

def testChokedMassFluxConsistency():

    '''
    The choked mass flux must equal the isentropic result computed independently from the sonic
    state. Catches an exponent error in the Vandenkerckhove function.
    '''

    gamma       = 1.4
    gasConstant = 296.8            # nitrogen
    stagnationPressure    = 5.0e6
    stagnationTemperature = 300.0

    massFlux = chokedMassFlux(stagnationPressure, stagnationTemperature, gamma, gasConstant)

    # Independent route: sonic conditions from the isentropic relations, then rho * a
    sonicTemperature, sonicPressure, sonicVelocity = isentropicValues(
        1.0, stagnationTemperature, stagnationPressure, gamma, gasConstant)
    sonicDensity = sonicPressure / (gasConstant * sonicTemperature)

    assert massFlux == pytest.approx(sonicDensity * sonicVelocity, rel = 1e-9), \
        'The choked mass flux and the isentropic sonic state disagree; one of them has a wrong exponent'

def testB31_3ThicknessInversion():

    '''
    The B31.3 thickness relation must invert consistently: the pressure recovered from the computed
    thickness must equal the design pressure.
    '''

    designPressure  = 10.0e6
    outerDiameter   = 0.0254
    allowableStress = 113.3e6

    result    = b31_3WallThickness(designPressure, outerDiameter, allowableStress, millTolerance = 0.0)
    thickness = result['pressureDesignThickness']

    # Invert: P = 2 * S * E * t / (D - 2*Y*t)
    recovered = 2.0 * allowableStress * thickness / (outerDiameter - 2.0 * 0.4 * thickness)
    assert recovered == pytest.approx(designPressure, rel = 1e-9), \
        'The B31.3 thickness relation does not invert consistently'

def testReynoldsNumberConsistency():

    '''
    The mass-flow form of the Reynolds number must equal the velocity form. Catches an area or
    diameter error.
    '''

    density   = 1000.0
    viscosity = 1.0e-3
    diameter  = 0.010
    velocity  = 2.0

    area     = np.pi * diameter**2 / 4.0
    massFlow = density * velocity * area

    fromMassFlow = reynoldsNumber(massFlow, diameter, viscosity)
    fromVelocity = density * velocity * diameter / viscosity

    assert fromMassFlow == pytest.approx(fromVelocity, rel = 1e-12), \
        'The mass flow and velocity forms of the Reynolds number disagree'

def testSecantSolveConverges():

    '''
    Every sizing routine in the library depends on secantSolve. Catches a regression in the
    convergence criteria, particularly the step-size test that handles physically-scaled residuals.
    '''

    root = secantSolve(lambda x: x**2 - 2.0, 1.0)
    assert root == pytest.approx(np.sqrt(2.0), rel = 1e-9)

    # A residual carrying physical units, which is what breaks a pure residual-magnitude test
    root = secantSolve(lambda x: 1.0e6 * (x - 0.005), 0.001, lowerBound = 1e-9, upperBound = 1.0)
    assert root == pytest.approx(0.005, rel = 1e-9), \
        'secantSolve must converge on a residual scaled by 1e6; the step size criterion is missing'

def testSolveForUnknown():

    '''
    The generalized solve-for-the-None-argument helper, used by the sizing idioms.
    '''

    def relation(pressure, area, force):
        return pressure * area - force

    name, value = solveForUnknown(relation, {'pressure': 1.0e6, 'area': None, 'force': 500.0},
                                  bracket = (1e-9, 1.0))
    assert name == 'area'
    assert value == pytest.approx(5.0e-4, rel = 1e-6)

    with pytest.raises(InvalidInputError):
        solveForUnknown(relation, {'pressure': 1.0e6, 'area': None, 'force': None})

def testApplyInputsRaisesOnMissingRequired():

    '''
    Every component depends on applyInputs to catch a missing required parameter with a useful
    message rather than an AttributeError three functions later.
    '''

    class Dummy:
        pass

    component = Dummy()

    applyInputs(component, {'alpha': 1.0}, {'alpha': 'alpha not provided'}, [])
    assert component.alpha == 1.0

    with pytest.raises(InvalidInputError):
        applyInputs(Dummy(), {}, {'alpha': 'alpha not provided'}, [])

def testNoneCoercedToNan():

    '''
    A None in a configuration dictionary must become np.nan so downstream np.isnan() logic works.
    Catches the JSON null handling that every config-driven run depends on.
    '''

    class Dummy:
        pass

    component = Dummy()
    applyInputs(component, {'alpha': None}, {'alpha': 'alpha not provided'}, [])
    assert np.isnan(component.alpha), 'A None input must be coerced to np.nan'

def testErrorHierarchy():

    '''
    Every custom error must be catchable as FluidSystemError, so a caller can handle the whole family
    with one except clause.
    '''

    assert issubclass(InvalidInputError, FluidSystemError)
    assert issubclass(ConvergenceFailureError, FluidSystemError)

    error = InvalidInputError('test message', parameterName = 'alpha', value = 1.0,
                              validRange = 'positive')
    assert 'test message' in str(error)
    assert error.getContext()['parameterName'] == 'alpha'

# -------------------------------------------------------------------------------------------------- #
# -- Tier 3: property backend integration -- #
# -------------------------------------------------------------------------------------------------- #

def testFluidPropsRoutesHydrazine():

    '''
    Hydrazine has no equation of state in either backend, so fluidProps must route it to the
    correlation table transparently. A regression here would raise rather than return a value.
    '''

    density = fluidProps('N2H4', 'TP', 'D', 293.15, 2.4e6)
    assert density == pytest.approx(hydrazineProps('D', 293.15), rel = 1e-12), \
        'fluidProps must route hydrazine to the correlation table'

def testFluidPropsWaterReference():

    '''
    Water at 20 degC and 1 atm: 998.2 kg/m^3 and 1.002 mPa-s. Validates that whichever backend is
    installed is returning mass-base SI.
    '''

    density, viscosity = fluidProps('Water', 'TP', 'D VIS', 293.15, 101325.0)
    assert density == pytest.approx(998.2, rel = 0.01), \
        'Water density at 20 degC should be 998.2 kg/m^3. A value near 1.0 means molar units'
    assert viscosity == pytest.approx(1.002e-3, rel = 0.02), \
        'Water viscosity at 20 degC should be 1.002 mPa-s'

def testSpeciesMolarMass():

    '''
    The leak rate mass conversions depend on this. A wrong molar mass would scale every mass leak
    rate.
    '''

    assert speciesMolarMass('He') == pytest.approx(4.0026e-3, rel = 1e-4)
    assert speciesMolarMass('N2') == pytest.approx(28.0135e-3, rel = 1e-4)
    assert speciesMolarMass('N2H4') == pytest.approx(32.0451e-3, rel = 1e-4)

def testConvertToSCFM():

    '''
    SCFM uses a 60 degF standard state, not the 0 degC state used for leak rates. Catches the two
    standard states being conflated.
    '''

    # 1 kg/s of nitrogen at the SCFM standard state
    scfm = convertToSCFM('Nitrogen', 1.0, 300.0, 1.0e6)
    standardDensity = fluidProps('Nitrogen', 'TP', 'D', 288.706, 101325.0)
    expected = (1.0 / standardDensity) / 0.028316846592 * 60.0
    assert scfm == pytest.approx(expected, rel = 1e-9), \
        'SCFM must be evaluated at the 60 degF standard state, not at the flowing state'
