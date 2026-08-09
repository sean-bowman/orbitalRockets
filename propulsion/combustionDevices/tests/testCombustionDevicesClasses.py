# -- Tests for the combustionDevices classes -- #

'''

Tiered tests for the three combustion device classes.

Tier 1 covers the contract: unknown elements and coolants, a stiffness or film fraction outside
the range it can physically take, a wall temperature above the chamber temperature, and an area
ratio below the throat.

Tier 2 validates against closed forms and physical law. Bartz against hand evaluation, the acoustic
mode frequencies against the Bessel eigenvalues, the momentum ratio against the closed form it
reduces to at equal pressure drop, and the orifice sizing against the flow it was derived from.

Tier 3 covers self-consistency and the physical direction of every effect, plus the cross-domain
check that matters most here: the heat load this sub-domain computes from Bartz against the
placeholder the propulsion hub assumes, which disagree by a factor of three.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'combustionDevicesLibrary'))

from combustionUtils import (INJECTOR_ELEMENTS, CHAMBER_ACOUSTIC_MODES, CHUG_STIFFNESS_FLOOR,
                             PROPELLANT_COMBINATIONS, R_UNIVERSAL,
                             bartzCoefficient, combustionGasProperties, combustionPrandtl,
                             combustionViscosity, _machFromAreaRatio,
                             InvalidInputError, InjectorError, StabilityError, CoolingError)
from Injector import Injector, INJECTION_DENSITIES, RECOMMENDED_MOMENTUM_RATIO
from CombustionStability import CombustionStability, BAFFLE_SUPPRESSION_ORDER
from RegenerativeCooling import (RegenerativeCooling, COOLANT_LIMITS, COOLANT_BY_COMBINATION,
                                 WALL_MATERIALS, THROAT_CURVATURE_RATIO)

# ------------------------------------------------------------------------------------------------ #
# -- Builders, all on the worked example engine -- #
# ------------------------------------------------------------------------------------------------ #

REFERENCE = {'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6, 'throatDiameter': 0.0906,
             'oxidiserFlow': 26.47, 'fuelFlow': 10.34, 'chamberDiameter': 0.1432,
             'barrelLength': 0.4091, 'convergentLength': 0.0456, 'divergentLength': 0.475,
             'contractionRatio': 2.5, 'areaRatio': 20.35}

def buildInjector(**overrides) -> Injector:

    inputs = {'combination':     REFERENCE['combination'],
              'chamberPressure': REFERENCE['chamberPressure'],
              'oxidiserFlow':    REFERENCE['oxidiserFlow'],
              'fuelFlow':        REFERENCE['fuelFlow'],
              'elementCount':    120}
    inputs.update(overrides)

    injector = Injector()
    injector.setInputs(inputs)

    return injector

def buildStability(**overrides) -> CombustionStability:

    inputs = {'combination':     REFERENCE['combination'],
              'chamberDiameter': REFERENCE['chamberDiameter'],
              'chamberLength':   REFERENCE['barrelLength'] + REFERENCE['convergentLength']}
    inputs.update(overrides)

    stability = CombustionStability()
    stability.setInputs(inputs)

    return stability

def buildCooling(**overrides) -> RegenerativeCooling:

    inputs = {'combination':      REFERENCE['combination'],
              'chamberPressure':  REFERENCE['chamberPressure'],
              'throatDiameter':   REFERENCE['throatDiameter'],
              'contractionRatio': REFERENCE['contractionRatio'],
              'areaRatio':        REFERENCE['areaRatio'],
              'barrelLength':     REFERENCE['barrelLength'],
              'convergentLength': REFERENCE['convergentLength'],
              'divergentLength':  REFERENCE['divergentLength'],
              'coolantFlow':      REFERENCE['fuelFlow']}
    inputs.update(overrides)

    cooling = RegenerativeCooling()
    cooling.setInputs(inputs)

    return cooling

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testUnknownElementIsRejected():

    with pytest.raises(InjectorError, match = 'Unknown element type'):
        buildInjector(elementType = 'magic')

def testStiffnessAtOrAboveOneIsRejected():

    '''
    A stiffness of one is an injector drop equal to the chamber pressure it feeds, which needs an
    infinite feed pressure to sustain.
    '''

    with pytest.raises(InjectorError, match = 'must lie in'):
        buildInjector(stiffness = 1.0)

def testAllFuelToTheWallIsRejected():

    with pytest.raises(InjectorError, match = 'nothing to burn in the core'):
        buildInjector(filmFraction = 1.0)

def testZeroElementsIsRejected():

    with pytest.raises(InjectorError, match = 'at least one'):
        buildInjector(elementCount = 0)

def testThrottleSettingOutsideRangeIsRejected():

    with pytest.raises(InjectorError, match = 'must lie in'):
        buildInjector().checkStiffness(throttleSetting = 1.5)

def testUnknownAcousticModeIsRejected():

    with pytest.raises(StabilityError, match = 'Unknown mode'):
        buildStability().sizeAcousticCavity(targetMode = '9T')

def testUnknownWallMaterialIsRejected():

    with pytest.raises(CoolingError, match = 'Unknown wall material'):
        buildCooling(wallMaterial = 'cheese').calculateWallTemperature()

def testWallTemperatureAboveChamberTemperatureIsRejected():

    '''
    No driving temperature difference means no heat transfer, and Bartz returns a negative flux
    rather than raising on its own.
    '''

    with pytest.raises(CoolingError, match = 'no driving temperature difference'):
        buildCooling(wallTemperature = 4000.0)

def testAreaRatioBelowTheThroatIsRejected():

    gas = combustionGasProperties('LOX/RP-1')

    with pytest.raises(CoolingError, match = 'at least one'):
        bartzCoefficient(0.09, 0.07, 10.0e6, 1750.0, 0.5, 800.0, gas)

def testUnknownCombinationHasNoGasProperties():

    with pytest.raises(CoolingError, match = 'Unknown propellant'):
        combustionGasProperties('LOX/unobtainium')

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms and physical law -- #
# ------------------------------------------------------------------------------------------------ #

def testPrandtlMatchesItsDefinition():

    for gamma in (1.15, 1.20, 1.24, 1.30):
        assert combustionPrandtl(gamma) == pytest.approx(4.0 * gamma / (9.0 * gamma - 5.0))

def testPrandtlIsNearThreeQuartersForEveryCombination():

    '''
    Combustion products sit near 0.8 regardless of propellant, which is why the correlation is
    tolerable. If one ever came out far from that, the gamma feeding it is wrong.
    '''

    for name, entry in PROPELLANT_COMBINATIONS.items():
        assert 0.7 < combustionPrandtl(entry['gamma']) < 0.9, name

def testViscosityFollowsItsCorrelation():

    assert combustionViscosity(23.3, 3670.0) == pytest.approx(
        1.184e-7 * np.sqrt(23.3) * 3670.0 ** 0.6)

def testGasPropertiesDeriveSpecificHeatFromGammaAndMolarMass():

    gas = combustionGasProperties('LOX/RP-1')

    expected = gas['gamma'] * gas['specificGasConstant'] / (gas['gamma'] - 1.0)

    assert gas['specificHeat'] == pytest.approx(expected)
    assert gas['specificGasConstant'] == pytest.approx(R_UNIVERSAL * 1000.0 / gas['molarMass'])

def testBartzMatchesHandEvaluationAtTheThroat():

    '''
    The full correlation evaluated by hand for the reference engine. If any exponent is mistyped
    this catches it, and nothing else would.
    '''

    gas = combustionGasProperties('LOX/RP-1')

    result = bartzCoefficient(0.0906, 1.5 * 0.0453, 10.0e6, 1750.1, 1.0, 800.0, gas)

    gamma = gas['gamma']
    stagnation = 1.0 + (gamma - 1.0) / 2.0

    correction = 1.0 / ((0.5 * (800.0 / 3670.0) * stagnation + 0.5) ** 0.68
                        * stagnation ** 0.12)

    expected = ((0.026 / 0.0906 ** 0.2)
                * (gas['viscosity'] ** 0.2 * gas['specificHeat'] / gas['prandtl'] ** 0.6)
                * (10.0e6 / 1750.1) ** 0.8
                * (0.0906 / (1.5 * 0.0453)) ** 0.1
                * correction)

    assert result['coefficient'] == pytest.approx(expected, rel = 1.0e-9)

def testBartzThroatMachNumberIsOne():

    gas = combustionGasProperties('LOX/RP-1')

    assert bartzCoefficient(0.09, 0.07, 10.0e6, 1750.0, 1.0, 800.0,
                            gas)['machNumber'] == pytest.approx(1.0)

def testAreaRatioToMachIsSubsonicByDefault():

    for areaRatio in (1.5, 2.5, 4.0, 10.0):
        assert _machFromAreaRatio(1.24, areaRatio) < 1.0

def testAcousticModeFrequenciesFollowTheEigenvalues():

    modes = buildStability().calculateAcousticModes()

    sound    = modes['speedOfSound']
    diameter = REFERENCE['chamberDiameter']

    for name, entry in CHAMBER_ACOUSTIC_MODES.items():
        expected = entry['eigenvalue'] * sound / (np.pi * diameter)
        assert modes['transverse'][name]['frequency'] == pytest.approx(expected)

def testSpeedOfSoundMatchesItsDefinition():

    stability = buildStability()
    gas       = stability.gasProperties

    expected = np.sqrt(gas['gamma'] * gas['specificGasConstant'] * gas['chamberTemperature'])

    assert stability.speedOfSound() == pytest.approx(expected)

def testLongitudinalModesAreHalfWavelengths():

    modes = buildStability().calculateAcousticModes()

    length = REFERENCE['barrelLength'] + REFERENCE['convergentLength']

    for order in (1, 2, 3):
        expected = order * modes['speedOfSound'] / (2.0 * length)
        assert modes['longitudinal'][f'{order}L']['frequency'] == pytest.approx(expected)

def testOrificeSizingReproducesTheFlow():

    '''
    The closing check on the orifice equation: mdot = Cd A sqrt(2 rho dP) has to return the flow
    the area was derived from.
    '''

    injector = buildInjector()
    result   = injector.sizeOrifices()

    discharge = injector.element['dischargeCoefficient']

    for name, flow in (('oxidiser', REFERENCE['oxidiserFlow']), ('fuel', REFERENCE['fuelFlow'])):

        entry = result['orifices'][name]

        recovered = (injector.elementCount * discharge * entry['area']
                     * np.sqrt(2.0 * entry['density'] * result['pressureDrop']))

        assert recovered == pytest.approx(flow, rel = 1.0e-9)

def testMomentumRatioReducesToTheClosedFormAtEqualPressureDrop():

    '''
    With one stiffness applied to both circuits, the momentum ratio is forced to
    MR sqrt(rho_fuel / rho_ox) and is not a design choice at all. That is the finding the class
    reports, and it is worth pinning because it is the reason real injectors run unequal drops.
    '''

    injector = buildInjector()
    result   = injector.calculateMomentumRatio()

    densities = INJECTION_DENSITIES[REFERENCE['combination']]

    expected = (REFERENCE['oxidiserFlow'] / REFERENCE['fuelFlow']
                * np.sqrt(densities['fuel'] / densities['oxidiser']))

    assert result['momentumRatio'] == pytest.approx(expected, rel = 1.0e-9)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency, direction and cross-domain -- #
# ------------------------------------------------------------------------------------------------ #

def testTheThroatCarriesThePeakFlux():

    '''
    Bartz carries (At/A)^0.9, so the throat is the peak by a wide margin and everything else falls
    away from it in both directions.
    '''

    cooling = buildCooling()

    throat = cooling.calculateHeatFlux(1.0)['heatFlux']

    for areaRatio in (1.5, 2.5, 5.0, 20.0):
        assert cooling.calculateHeatFlux(areaRatio)['heatFlux'] < throat

def testHeatLoadSectionsSumToTheTotal():

    heat = buildCooling().calculateHeatLoad()

    assert sum(entry['load'] for entry in heat['sections'].values()) == pytest.approx(
        heat['totalLoad'])
    assert sum(entry['area'] for entry in heat['sections'].values()) == pytest.approx(
        heat['totalArea'])

def testTheDivergentSectionIsMostOfTheAreaAndAThirdOfTheLoad():

    '''
    Low flux over a great deal of area. Neglecting it, which is the easy thing to do because the
    flux is low, understates the total by about a third.
    '''

    heat = buildCooling().calculateHeatLoad()

    divergent = heat['sections']['divergent']

    assert divergent['area'] / heat['totalArea'] > 0.5
    assert 0.25 < divergent['load'] / heat['totalLoad'] < 0.5

def testBartzDisagreesWithTheHubPlaceholderByAFactorOfThree():

    '''
    The cross-domain check that matters. The propulsion hub assumes the wall heat load is two per
    cent of jet power, which for this engine gives 2.72 MW. Bartz integrated over the real geometry
    gives about 8.1 MW.

    The hub value is a stated placeholder and it says so, and this is the calculation that replaces
    it. The test exists so that if either side moves, the disagreement is re-examined rather than
    quietly becoming agreement or becoming much worse.
    '''

    heat = buildCooling().calculateHeatLoad()

    hubPlaceholder = 0.02 * 100000.0 ** 2 / (2.0 * 36.81)

    ratio = heat['totalLoad'] / hubPlaceholder

    assert 2.5 < ratio < 4.0, (
        f'Bartz gives {heat["totalLoad"] / 1.0e6:.2f} MW against the hub placeholder '
        f'{hubPlaceholder / 1.0e6:.2f} MW, a ratio of {ratio:.2f}')

def testTheReferenceEngineCannotBeRegenerativelyCooled():

    '''
    The finding this sub-domain exists to produce. 10.34 kg/s of RP-1 cannot absorb the real heat
    load without going past its coking limit, and no channel geometry changes that.

    If this ever starts closing, either the heat load has fallen or the coolant limit has risen,
    and both are worth knowing about deliberately rather than by accident.
    '''

    capability = buildCooling().checkCoolantCapability()

    assert capability['feasible'] is False
    assert capability['outletTemperature'] > capability['limit']
    assert capability['requiredFlow'] > REFERENCE['fuelFlow']

def testHydrogenIsAFarBetterCoolantThanKerosene():

    '''
    Specific heat of 14300 against 2100. The same heat load into the same mass flow is a seventh of
    the temperature rise, which is most of why hydrogen engines run the chamber pressures they do.
    '''

    assert (COOLANT_LIMITS['LH2']['specificHeat']
            > 5.0 * COOLANT_LIMITS['RP-1']['specificHeat'])

def testEveryCombinationWithACoolantHasItsLimitDefined():

    for combination, coolant in COOLANT_BY_COMBINATION.items():
        assert coolant in COOLANT_LIMITS, combination
        assert combination in PROPELLANT_COMBINATIONS, combination

def testCopperDropsFarLessTemperatureThanInconel():

    '''
    The reason chamber liners are copper. An order of magnitude in conductivity is an order of
    magnitude in wall drop at the same flux and thickness.
    '''

    wall = buildCooling().calculateWallTemperature()

    copper  = wall['comparison']['GRCop-42']['wallDrop']
    inconel = wall['comparison']['Inconel 718']['wallDrop']

    assert inconel > 10.0 * copper

def testAThinnerWallDropsLessTemperature():

    thick = buildCooling(wallThickness = 0.002).calculateWallTemperature()
    thin  = buildCooling(wallThickness = 0.0005).calculateWallTemperature()

    assert thin['wallDrop'] < thick['wallDrop']

def testHigherChamberPressureRaisesTheFlux():

    '''
    Bartz carries Pc^0.8, so flux rises with chamber pressure while the wall area available to
    reject it falls. That is the whole reason high pressure engines are cooling limited.
    '''

    low  = buildCooling(chamberPressure = 5.0e6).calculateHeatFlux(1.0)['heatFlux']
    high = buildCooling(chamberPressure = 20.0e6).calculateHeatFlux(1.0)['heatFlux']

    assert high > low

def testStiffnessFallsLinearlyWithThrottle():

    injector = buildInjector(stiffness = 0.20)

    full = injector.checkStiffness(1.0)['stiffness']
    half = injector.checkStiffness(0.5)['stiffness']

    assert half == pytest.approx(0.5 * full)

def testTheThrottleFloorFollowsTheDesignStiffness():

    injector = buildInjector(stiffness = 0.20)

    result = injector.checkStiffness()

    assert result['deepestThrottle'] == pytest.approx(CHUG_STIFFNESS_FLOOR / 0.20)

def testFilmCoolingRaisesTheCoreMixtureRatio():

    none = buildInjector(filmFraction = 0.0).checkWallCompatibility()
    some = buildInjector(filmFraction = 0.10).checkWallCompatibility()

    assert some['coreMixtureRatio'] > none['coreMixtureRatio']
    assert none['coreMixtureRatio'] == pytest.approx(none['overallMixtureRatio'])

def testMixingQualityAndWallToleranceAreOpposed():

    '''
    The difficulty the injector document is built around. The best mixing element in the set is not
    wall tolerant, and the wall tolerant ones mix worse.
    '''

    best = max(INJECTOR_ELEMENTS, key = lambda name: INJECTOR_ELEMENTS[name]['mixingQuality'])

    assert INJECTOR_ELEMENTS[best]['wallCompatible'] is False

def testMoreElementsGiveSmallerOrifices():

    few  = buildInjector(elementCount = 50).sizeOrifices()
    many = buildInjector(elementCount = 200).sizeOrifices()

    assert (many['orifices']['fuel']['diameter']
            < few['orifices']['fuel']['diameter'])

def testBafflesSuppressTangentialModesAndNotRadialOnes():

    '''
    The point of the baffle section. Six blades suppress up to 3T and leave 1R untouched, which is
    why a baffled engine can still go unstable and why cavities are fitted as well.
    '''

    result = buildStability(baffleBlades = 6).sizeBaffles()

    assert result['suppressedOrder'] == int(6 * BAFFLE_SUPPRESSION_ORDER)
    assert '1T' in result['suppressed']
    assert '1R' in result['unsuppressed']

def testNoBaffleSuppressesNothing():

    result = buildStability(baffleBlades = 0).sizeBaffles()

    assert result['suppressed'] == []
    assert len(result['unsuppressed']) == len(CHAMBER_ACOUSTIC_MODES)

def testMoreBladesSuppressMoreModes():

    few  = buildStability(baffleBlades = 4).sizeBaffles()
    many = buildStability(baffleBlades = 12).sizeBaffles()

    assert many['suppressedOrder'] > few['suppressedOrder']

def testFirstTangentialScalesInverselyWithDiameter():

    small = buildStability(chamberDiameter = 0.10).calculateAcousticModes()
    large = buildStability(chamberDiameter = 0.40).calculateAcousticModes()

    assert (small['firstTangential'] / large['firstTangential']) == pytest.approx(4.0,
                                                                                  rel = 1.0e-9)

def testTheCavityDepthIsAQuarterWavelength():

    stability = buildStability()

    cavity = stability.sizeAcousticCavity('1T')

    assert cavity['quarterWaveDepth'] == pytest.approx(
        cavity['speedOfSound'] / (4.0 * cavity['frequency']))

def testChugCriterionIsDeclaredNecessaryRatherThanSufficient():

    '''
    A class that returned a stability verdict would be lying. This checks the output says so.
    '''

    result = buildStability().checkChugCriterion()

    assert result['necessaryOnly'] is True
    assert any('not sufficient' in finding or 'necessary' in finding
               for finding in result['findings'])

def testBooleanFlagsAreRealPythonBooleans():

    '''
    Guard on a defect found during the build. A comparison between numpy floats returns numpy.bool_,
    which is falsy and truthy in the right places but fails an `is True` or `is False` identity
    check. Callers write those checks and so do tests, and the failure looks like a wrong answer
    rather than a type problem.

    Every flag a class reports has to be a real bool.
    '''

    flags = [
        buildCooling().checkCoolantCapability()['feasible'],
        buildCooling().calculateWallTemperature()['withinLimit'],
        buildInjector().calculateMomentumRatio()['withinBand'],
        buildInjector().checkStiffness()['clearsFloor'],
        buildStability().checkChugCriterion()['clears'],
    ]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testReportsRunForAllThreeClasses():

    assert 'INJECTOR'             in buildInjector().generateReport()
    assert 'COMBUSTION STABILITY' in buildStability().generateReport()
    assert 'REGENERATIVE COOLING' in buildCooling().generateReport()
