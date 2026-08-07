
# -- Tests for the FluidView property viewer -- #

'''

Tiered tests for FluidView.

Tier 1 covers the contract: required inputs, the mode-specific validation, the grid guard, and the
property name resolution that stands between the caller and a silent backend failure.

Tier 2 validates against physics that does not depend on which backend answered: nitrogen density
against the ideal gas law where the gas is nearly ideal, the speed of sound against sqrt(gamma R T),
and the location of the critical point in the phase field.

Tier 3 covers self-consistency: a single point and the corresponding element of a sweep and of a
carpet plot must agree exactly, since they are the same lookup reached three ways.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'fluidSystemsLibrary'))

from utils import CompatibilityError, InvalidInputError
from FluidView import (FluidView, listAvailableFluids, resolveProperty, propertyUnit,
                       PROPERTY_LABELS, PHASE_CODES, PHASE_UNKNOWN, MAXIMUM_GRID_POINTS,
                       REFPROP_ERROR_SENTINEL)

UNIVERSAL_GAS_CONSTANT = 8.314462618    # [J/mol/K]
NITROGEN_MOLAR_MASS    = 0.0280134      # [kg/mol]
NITROGEN_CRITICAL_T    = 126.192        # [K]
NITROGEN_CRITICAL_P    = 3.3958e6       # [Pa]

def buildPoint(species: str = 'N2', temperature: float = 300.0, pressure: float = 1.0e5,
               outputs: list = None) -> FluidView:

    '''
    A configured single-point viewer, since almost every test needs one.
    '''

    view = FluidView()
    view.setInputs({'species': species, 'inputTypes': 'TP',
                    'outputTypes': outputs if outputs is not None else ['density'],
                    'firstValue': temperature, 'secondValue': pressure})
    return view

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testMissingSpeciesRaises():

    view = FluidView()
    with pytest.raises(InvalidInputError):
        view.setInputs({'inputTypes': 'TP', 'outputTypes': ['density']})

def testUnknownPropertyRaisesRatherThanReachingTheBackend():

    '''
    The backend answers an unknown label with the sentinel rather than an error, so an unknown name
    has to be caught here or it becomes a number.
    '''

    view = FluidView()
    with pytest.raises(InvalidInputError):
        view.setInputs({'species': 'N2', 'outputTypes': ['unobtainium density']})

def testPropertyNameResolvesFromEitherForm():

    assert resolveProperty('density') == 'D'
    assert resolveProperty('DENSITY') == 'D'
    assert resolveProperty('D')       == 'D'
    assert resolveProperty('VIS')     == 'VIS'

def testEveryReadableNameHasAUnitAndResolvesBack():

    for readable, entry in PROPERTY_LABELS.items():
        assert resolveProperty(readable) == entry['label']
        # phase is a string, so an empty unit would be wrong to demand of it alone
        assert propertyUnit(entry['label']) == entry['unit']

def testSinglePointWithoutStateValuesRaises():

    view = FluidView()
    view.setInputs({'species': 'N2', 'outputTypes': ['density']})
    with pytest.raises(InvalidInputError):
        view.calculateSinglePoint()

def testSweepWithoutConstantSecondValueRaises():

    view = FluidView()
    view.setInputs({'species': 'N2', 'outputTypes': ['density'],
                    'firstRange': np.linspace(200.0, 400.0, 5)})
    with pytest.raises(InvalidInputError):
        view.calculateRangeSweep()

def testCarpetPlotWithoutSecondRangeRaises():

    view = FluidView()
    view.setInputs({'species': 'N2', 'outputTypes': ['density'],
                    'firstRange': np.linspace(200.0, 400.0, 5)})
    with pytest.raises(InvalidInputError):
        view.calculateCarpetPlot()

def testGridGuardRaisesBeforeRunningForAnHour():

    '''
    A 600 by 600 carpet plot is 360000 backend calls. The guard exists so that is a fast error
    rather than a slow one.
    '''

    view = FluidView()
    view.setInputs({'species': 'N2', 'outputTypes': ['density'],
                    'firstRange': np.linspace(200.0, 400.0, 600),
                    'secondRange': np.linspace(1.0e6, 5.0e6, 600)})

    with pytest.raises(InvalidInputError):
        view.calculateCarpetPlot()

    assert 600 * 600 > MAXIMUM_GRID_POINTS, 'the guard must actually be exceeded by this case'

def testMixtureRatioMustMatchComponentCount():

    view = FluidView()
    view.setInputs({'species': 'N2;He', 'outputTypes': ['density'],
                    'mixtureRatio': [1.0],
                    'firstValue': 300.0, 'secondValue': 1.0e6})
    with pytest.raises(InvalidInputError):
        view.calculateSinglePoint()

def testUnmodelledSpeciesRaisesRatherThanReturningTheSentinel():

    '''
    The single most important behaviour in the class. REFPROP returns roughly -9999990.0 for a
    species it does not have, which is a float and propagates silently.
    '''

    view = buildPoint(species = 'NOTAFLUID')

    with pytest.raises(CompatibilityError):
        view.calculateSinglePoint()

def testPhaseDiagramRequiresTemperaturePressureCoordinates():

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'PH', 'outputTypes': ['phase'],
                    'firstRange': np.linspace(1.0e6, 5.0e6, 3),
                    'secondRange': np.linspace(1.0e5, 3.0e5, 3)})
    with pytest.raises(InvalidInputError):
        view.calculatePhaseDiagram()

def testBackendIsReported():

    available = listAvailableFluids()
    assert isinstance(available['refpropInstalled'], bool)
    assert 'hydrazine' in available['correlation']

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: against physics -- #
# ------------------------------------------------------------------------------------------------ #

def testNitrogenDensityMatchesIdealGasWhereItIsNearlyIdeal():

    '''
    At 300 K and 1 atm nitrogen is within a fraction of a percent of ideal, so the equation of
    state has to reproduce P M / (R T) closely. This catches a units error anywhere in the chain.
    '''

    temperature, pressure = 300.0, 101325.0

    result = buildPoint(temperature = temperature, pressure = pressure).calculateSinglePoint()
    density = result['properties']['D']

    idealDensity = pressure * NITROGEN_MOLAR_MASS / (UNIVERSAL_GAS_CONSTANT * temperature)

    assert density == pytest.approx(idealDensity, rel = 0.005), \
        f'{density:.4f} against ideal {idealDensity:.4f} kg/m^3'

def testNitrogenSpeedOfSoundMatchesTheIdealRelation():

    '''
    a = sqrt(gamma R T / M) at low pressure, which ties the speed of sound, gamma and the molar
    mass together. If any one of the three is wrong this fails.
    '''

    temperature, pressure = 300.0, 101325.0

    result = buildPoint(temperature = temperature, pressure = pressure,
                        outputs = ['speed of sound', 'gamma']).calculateSinglePoint()

    gamma      = result['properties']['CP/CV']
    speed      = result['properties']['W']
    idealSpeed = np.sqrt(gamma * UNIVERSAL_GAS_CONSTANT * temperature / NITROGEN_MOLAR_MASS)

    assert speed == pytest.approx(idealSpeed, rel = 0.01), \
        f'{speed:.2f} against ideal {idealSpeed:.2f} m/s'
    assert 1.39 < gamma < 1.41, f'diatomic gamma expected, got {gamma:.4f}'

def testDensityFallsWithTemperatureAtConstantPressure():

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['density'],
                    'firstRange': np.linspace(200.0, 500.0, 7), 'secondValue': 5.0e6})

    density = view.calculateRangeSweep()['properties']['D']

    assert np.all(np.diff(density) < 0.0), 'density must fall monotonically with temperature'

def testPhaseFieldPlacesSupercriticalAboveTheCriticalPoint():

    '''
    Nitrogen's critical point is 126.192 K and 3.3958 MPa. Above both, the fluid is supercritical;
    well below both it is not. This validates the phase coding against a published constant.
    '''

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['phase'],
                    'firstRange':  np.array([80.0, 1.5 * NITROGEN_CRITICAL_T]),
                    'secondRange': np.array([1.0e5, 2.0 * NITROGEN_CRITICAL_P])})

    field = view.calculatePhaseDiagram()
    codes = field['phaseCodes']

    assert codes[1, 1] == PHASE_CODES['Supercritical'], \
        'above both critical constants the fluid must be supercritical'
    assert codes[0, 0] != PHASE_CODES['Supercritical'], \
        'at 80 K and 1 bar nitrogen is not supercritical'

def testSubcooledLiquidAppearsBelowTheCriticalTemperatureAtHighPressure():

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['phase'],
                    'firstRange':  np.array([80.0]),
                    'secondRange': np.array([2.0 * NITROGEN_CRITICAL_P])})

    field = view.calculatePhaseDiagram()

    assert field['phaseCodes'][0, 0] == PHASE_CODES['Subcooled liquid']

def testHydrazineIsServedByTheCorrelationTableAndSaysSo():

    '''
    Hydrazine has no equation of state in either backend. The value must come back, and the finding
    must warn that it is a correlation rather than reference data.
    '''

    result = buildPoint(species = 'hydrazine', temperature = 293.15,
                        pressure = 1.0e6).calculateSinglePoint()

    density = result['properties']['D']

    # room temperature hydrazine is about 1004 kg/m^3
    assert 990.0 < density < 1020.0, f'{density:.1f} kg/m^3 is not hydrazine'
    assert any('correlation' in finding for finding in result['findings']), \
        'the correlation backend must be declared in the findings'

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency -- #
# ------------------------------------------------------------------------------------------------ #

def testSinglePointSweepAndCarpetAgreeExactly():

    '''
    The same state reached three ways is the same lookup, so the three must agree to the bit. Any
    disagreement means one of the paths is transposing or mis-indexing.
    '''

    temperature, pressure = 300.0, 5.0e6

    point = buildPoint(temperature = temperature, pressure = pressure,
                       outputs = ['density', 'viscosity']).calculateSinglePoint()

    sweepView = FluidView()
    sweepView.setInputs({'species': 'N2', 'inputTypes': 'TP',
                         'outputTypes': ['density', 'viscosity'],
                         'firstRange': np.array([250.0, temperature, 350.0]),
                         'secondValue': pressure})
    sweep = sweepView.calculateRangeSweep()

    carpetView = FluidView()
    carpetView.setInputs({'species': 'N2', 'inputTypes': 'TP',
                          'outputTypes': ['density', 'viscosity'],
                          'firstRange':  np.array([250.0, temperature, 350.0]),
                          'secondRange': np.array([1.0e6, pressure])})
    carpet = carpetView.calculateCarpetPlot()

    for label in ('D', 'VIS'):
        assert sweep['properties'][label][1] == point['properties'][label]
        assert carpet['properties'][label][1, 1] == point['properties'][label]

def testCarpetGridIsIndexedFirstRangeThenSecondRange():

    '''
    grid[i, j] must be the property at firstRange[i] and secondRange[j]. A transposed grid is the
    classic contour plotting bug and it produces a chart that looks plausible.
    '''

    firstRange  = np.array([200.0, 400.0])
    secondRange = np.array([1.0e6, 8.0e6])

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['density'],
                    'firstRange': firstRange, 'secondRange': secondRange})
    grid = view.calculateCarpetPlot()['properties']['D']

    assert grid.shape == (len(firstRange), len(secondRange))

    # cold and high pressure is the densest corner, hot and low pressure the least dense
    assert grid[0, 1] == grid.max(), 'densest must be at low temperature, high pressure'
    assert grid[1, 0] == grid.min(), 'least dense must be at high temperature, low pressure'

def testSpecificVolumeIsTheReciprocalOfDensity():

    result = buildPoint(temperature = 300.0, pressure = 5.0e6,
                        outputs = ['density', 'specific volume']).calculateSinglePoint()

    assert result['properties']['V'] == pytest.approx(1.0 / result['properties']['D'], rel = 1.0e-9)

def testGammaEqualsCpOverCv():

    result = buildPoint(temperature = 300.0, pressure = 1.0e6,
                        outputs = ['specific heat cp', 'specific heat cv',
                                   'gamma']).calculateSinglePoint()

    ratio = result['properties']['CP'] / result['properties']['CV']

    assert result['properties']['CP/CV'] == pytest.approx(ratio, rel = 1.0e-6)

def testUnitsAreReturnedForEveryRequestedProperty():

    result = buildPoint(outputs = ['density', 'viscosity',
                                   'thermal conductivity']).calculateSinglePoint()

    assert set(result['units']) == set(result['properties'])
    assert all(isinstance(unit, str) and unit for unit in result['units'].values())

def testSentinelConstantIsNegativeAndLarge():

    '''
    Guards the guard: if this constant were ever set positive or small, the sentinel check would
    start rejecting legitimate property values.
    '''

    assert REFPROP_ERROR_SENTINEL < -1.0e5

def testUnrecognisedPhaseCodeIsZeroAndDistinctFromEveryRealPhase():

    assert PHASE_UNKNOWN == 0
    assert PHASE_UNKNOWN not in PHASE_CODES.values()

def testReportRunsForEveryQueryMode():

    point = buildPoint(outputs = ['density', 'viscosity'])
    point.calculateSinglePoint()
    assert 'FLUID VIEW' in point.generateReport()

    sweepView = FluidView()
    sweepView.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['density'],
                         'firstRange': np.linspace(200.0, 400.0, 4), 'secondValue': 1.0e6})
    sweepView.calculateRangeSweep()
    assert 'Sweep over 4 points' in sweepView.generateReport()

    carpetView = FluidView()
    carpetView.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['density'],
                          'firstRange': np.linspace(200.0, 400.0, 3),
                          'secondRange': np.linspace(1.0e6, 5.0e6, 3)})
    carpetView.calculateCarpetPlot()
    assert '3 x 3 grid' in carpetView.generateReport()

def testUniformPhaseFieldIsReportedAsAFinding():

    '''
    A phase diagram whose bounds do not straddle a boundary is a chart of one colour, and it looks
    like a working chart. The class has to say so.
    '''

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'TP', 'outputTypes': ['phase'],
                    'firstRange':  np.array([400.0, 450.0]),
                    'secondRange': np.array([1.0e5, 2.0e5])})

    field = view.calculatePhaseDiagram()

    assert len(field['phasesPresent']) == 1
    assert any('shows nothing' in finding for finding in field['findings'])

def testExportPropertyTableWritesOneFilePerProperty(tmp_path):

    view = FluidView()
    view.setInputs({'species': 'N2', 'inputTypes': 'TP',
                    'outputTypes': ['density', 'viscosity'],
                    'firstRange': np.linspace(200.0, 400.0, 3),
                    'secondRange': np.linspace(1.0e6, 5.0e6, 3)})
    view.calculateCarpetPlot()

    written = view.exportPropertyTable(outputDir = str(tmp_path))

    assert len(written) == 2
    for path in written:
        assert os.path.exists(path)
        # the header row and column carry the input values, so the file is 4 x 4
        table = np.loadtxt(path, delimiter = ',')
        assert table.shape == (4, 4)
        assert np.allclose(table[0, 1:], np.linspace(1.0e6, 5.0e6, 3))
        assert np.allclose(table[1:, 0], np.linspace(200.0, 400.0, 3))
