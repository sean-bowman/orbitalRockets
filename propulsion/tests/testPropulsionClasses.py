# -- Tests for the propulsion hub classes -- #

'''

Tiered tests for the three engine-level classes.

Tier 1 covers the contract: unknown propellants, mixture ratios outside the range the tabulated
properties apply to, efficiencies above one, and a nozzle asked to expand to less than its throat.

Tier 2 validates against closed forms and physical law. The Vandenkerckhove function against hand
evaluation, the area ratio relation against its own inverse, the thrust coefficient against the
vacuum limit, bulk density against the harmonic mean it is, and the sizing chain against the
thrust it was built from.

Tier 3 covers self-consistency and the physical direction of every effect, including three
regression guards on errors found during the build: residence time is a time rather than a length,
a cooling area check has to count the nozzle wall, and a method that calls another must not inherit
its findings.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'propulsionLibrary'))

from propulsionUtils import (PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH,
                             SUMMERFIELD_SEPARATION_RATIO, GRAVITY, R_UNIVERSAL,
                             vandenkerckhove, characteristicVelocity, bulkDensity,
                             areaRatioFromPressureRatio, pressureRatioFromAreaRatio,
                             InvalidInputError, PropellantError, PerformanceError, SizingError)
from PropellantCombination import PropellantCombination
from EnginePerformance import EnginePerformance, SEA_LEVEL_PRESSURE
from EngineSizing import EngineSizing, CONICAL_HALF_ANGLE, BELL_LENGTH_FRACTION

# ------------------------------------------------------------------------------------------------ #
# -- Builders -- #
# ------------------------------------------------------------------------------------------------ #

def buildPropellant(**overrides) -> PropellantCombination:

    inputs = {'combination': 'LOX/RP-1'}
    inputs.update(overrides)

    combination = PropellantCombination()
    combination.setInputs(inputs)

    return combination

def buildPerformance(**overrides) -> EnginePerformance:

    inputs = {'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6, 'areaRatio': 16.0}
    inputs.update(overrides)

    performance = EnginePerformance()
    performance.setInputs(inputs)

    return performance

def buildSizing(**overrides) -> EngineSizing:

    inputs = {'combination': 'LOX/RP-1', 'thrust': 100000.0,
              'chamberPressure': 10.0e6, 'areaRatio': 16.0}
    inputs.update(overrides)

    sizing = EngineSizing()
    sizing.setInputs(inputs)

    return sizing

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testUnknownCombinationIsRejected():

    with pytest.raises(PropellantError, match = 'Unknown propellant'):
        buildPropellant(combination = 'LOX/unobtainium')

def testOxidiserRichIsRejected():

    '''
    Above stoichiometric the tabulated chamber temperature and molar mass do not apply, and the
    physical behaviour changes: an oxidiser rich chamber attacks its wall rather than cooling it.
    '''

    with pytest.raises(PropellantError, match = 'above the stoichiometric'):
        buildPropellant(mixtureRatio = 4.0)

def testExtremelyFuelRichIsRejected():

    with pytest.raises(PropellantError, match = 'below'):
        buildPropellant(mixtureRatio = 0.5)

def testAreaRatioAtOrBelowUnityIsRejected():

    with pytest.raises(InvalidInputError, match = 'must exceed one'):
        buildPerformance(areaRatio = 1.0)

def testEfficiencyAboveOneIsRejected():

    with pytest.raises(PerformanceError, match = r'must lie in \(0, 1\]'):
        buildPerformance(cstarEfficiency = 1.05)

def testChamberPressureBelowAmbientIsRejected():

    '''
    An unchoked nozzle invalidates every relation in the class, so it has to be refused rather than
    producing a number.
    '''

    with pytest.raises(PerformanceError, match = 'not choked'):
        buildPerformance(chamberPressure = 50000.0, ambientPressure = SEA_LEVEL_PRESSURE)

def testContractionRatioBelowUnityIsRejected():

    with pytest.raises(SizingError, match = 'contraction ratio must exceed one'):
        buildSizing(contractionRatio = 0.8)

def testGammaAtOrBelowUnityIsRejected():

    with pytest.raises(PerformanceError, match = 'must exceed one'):
        vandenkerckhove(1.0)

def testSubsonicBranchIsNeverReturned():

    '''
    The area ratio relation has a subsonic and a supersonic root. A rocket nozzle runs on the
    supersonic one, and returning the other would give a nozzle that decelerates the flow.
    '''

    for gamma in (1.15, 1.20, 1.24, 1.30):
        throatRatio = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
        for areaRatio in (2.0, 10.0, 60.0):
            assert pressureRatioFromAreaRatio(gamma, areaRatio) < throatRatio

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms and physical law -- #
# ------------------------------------------------------------------------------------------------ #

def testVandenkerckhoveMatchesHandEvaluation():

    assert vandenkerckhove(1.4) == pytest.approx(0.68473, rel = 1.0e-4)
    assert vandenkerckhove(1.2) == pytest.approx(0.64847, rel = 1.0e-4)

def testVandenkerckhoveIsInsensitiveToGamma():

    '''
    Under six per cent across the whole range a rocket ever sees. That insensitivity is why an error
    in gamma is rarely the reason a performance prediction is wrong.
    '''

    values = [vandenkerckhove(gamma) for gamma in (1.13, 1.20, 1.30, 1.40)]

    assert (max(values) - min(values)) / min(values) < 0.09

def testAreaRatioRelationInvertsItself():

    for gamma in (1.15, 1.24, 1.30):
        for areaRatio in (2.0, 8.0, 40.0, 200.0):
            ratio = pressureRatioFromAreaRatio(gamma, areaRatio)
            assert areaRatioFromPressureRatio(gamma, ratio) == pytest.approx(areaRatio,
                                                                            rel = 1.0e-9)

def testCharacteristicVelocityMatchesItsDefinition():

    gamma, molarMass, temperature = 1.24, 23.3, 3670.0

    expected = (np.sqrt(R_UNIVERSAL / (molarMass / 1000.0) * temperature)
                / vandenkerckhove(gamma))

    assert characteristicVelocity(gamma, molarMass, temperature) == pytest.approx(expected)

def testCharacteristicVelocityRisesWithTemperatureAndFallsWithMolarMass():

    '''
    c* goes as sqrt(Tc / M). Both directions matter, and the molar mass one is why peak impulse sits
    fuel rich of stoichiometric.
    '''

    base = characteristicVelocity(1.24, 23.3, 3670.0)

    assert characteristicVelocity(1.24, 23.3, 4000.0) > base
    assert characteristicVelocity(1.24, 20.0, 3670.0) > base

def testBulkDensityIsTheHarmonicMeanItClaimsToBe():

    mixtureRatio, oxidiser, fuel = 2.56, 1141.0, 810.0

    expected = (1.0 + mixtureRatio) / (mixtureRatio / oxidiser + 1.0 / fuel)

    assert bulkDensity(mixtureRatio, oxidiser, fuel) == pytest.approx(expected)

def testBulkDensityLiesBetweenTheComponents():

    for name, entry in PROPELLANT_COMBINATIONS.items():
        density = bulkDensity(entry['mixtureRatio'], entry['oxidiserDensity'],
                              entry['fuelDensity'])
        assert min(entry['oxidiserDensity'], entry['fuelDensity']) <= density, name
        assert density <= max(entry['oxidiserDensity'], entry['fuelDensity']), name

def testVacuumThrustCoefficientExceedsSeaLevel():

    performance = buildPerformance()

    vacuum   = performance.calculateThrustCoefficient(0.0)
    seaLevel = performance.calculateThrustCoefficient(SEA_LEVEL_PRESSURE)

    assert vacuum['ideal'] > seaLevel['ideal']

def testThrustCoefficientPressureTermIsTheOnlyAltitudeDependence():

    '''
    The momentum term is a function of gamma and area ratio alone. If it ever moves with ambient
    pressure, the split between the two terms has been coded wrongly.
    '''

    performance = buildPerformance()

    momenta = [performance.calculateThrustCoefficient(ambient)['momentumTerm']
               for ambient in (0.0, 50000.0, SEA_LEVEL_PRESSURE)]

    assert momenta[0] == pytest.approx(momenta[1]) == pytest.approx(momenta[2])

def testSizingReproducesTheThrustItWasGiven():

    '''
    The closing check on the whole sizing chain: F = Cf Pc At has to return the thrust the geometry
    was derived from.
    '''

    sizing = buildSizing()

    throat            = sizing.sizeThroat()
    thrustCoefficient = sizing.performance.calculateThrustCoefficient()

    thrust = (thrustCoefficient['delivered'] * sizing.chamberPressure * throat['throatArea'])

    assert thrust == pytest.approx(sizing.thrust, rel = 1.0e-9)

def testMassFlowSplitSumsToTheTotal():

    throat = buildSizing().sizeThroat()

    assert throat['oxidiserFlow'] + throat['fuelFlow'] == pytest.approx(throat['massFlow'])

def testMixtureRatioIsRecoveredFromTheFlowSplit():

    throat = buildSizing().sizeThroat()

    ratio = throat['oxidiserFlow'] / throat['fuelFlow']

    assert ratio == pytest.approx(PROPELLANT_COMBINATIONS['LOX/RP-1']['mixtureRatio'])

def testDivergenceEfficiencyMatchesTheHalfAngle():

    nozzle = buildSizing().sizeNozzle()

    expected = (1.0 + np.cos(np.radians(CONICAL_HALF_ANGLE))) / 2.0

    assert nozzle['divergenceEfficiency'] == pytest.approx(expected)
    assert nozzle['bellLength'] == pytest.approx(BELL_LENGTH_FRACTION * nozzle['conicalLength'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency and regression -- #
# ------------------------------------------------------------------------------------------------ #

def testResidenceTimeIsATimeAndNotALength():

    '''
    Regression guard. Residence time was computed as chamber volume over `mdot c* / Pc`, which is a
    volume over an area and therefore a length. It returned 1100 for a chamber whose real residence
    time is 1.47 ms, and the number was plausible enough as milliseconds to pass a glance.

    A liquid engine chamber holds its propellant for single-digit milliseconds. Anything outside
    that band by orders of magnitude is a units error rather than an unusual engine.
    '''

    chamber = buildSizing().sizeChamber()

    assert 0.5e-3 < chamber['residenceTime'] < 10.0e-3

def testResidenceTimeMatchesTheChamberGasInventory():

    '''
    The definition it should satisfy: the mass resident in the chamber divided by the mass flow
    through it.
    '''

    sizing  = buildSizing()
    chamber = sizing.sizeChamber()
    throat  = sizing.sizeThroat()

    expected = chamber['chamberVolume'] * chamber['chamberDensity'] / throat['massFlow']

    assert chamber['residenceTime'] == pytest.approx(expected)

def testCoolingCheckCountsTheNozzleWall():

    '''
    Regression guard. The cooling area check originally compared the heat load against the barrel
    wall alone and concluded that cooling governed. The divergent section is the majority of the
    wetted area on any moderately expanded engine, and including it reverses the conclusion.
    '''

    chamber = buildSizing().sizeChamber()

    assert chamber['nozzleWallArea'] > chamber['barrelWallArea']

    total = (chamber['barrelWallArea'] + chamber['convergentWallArea']
             + chamber['nozzleWallArea'])

    assert chamber['availableWallArea'] == pytest.approx(total)

def testFindingsAreNotInheritedFromNestedCalls():

    '''
    Regression guard. Every sizing method calls sizeThroat, which used to write into self.findings,
    so each caller appended to the throat's findings and the report printed them four times.

    Each method now owns a local list. The check is that the chamber findings contain nothing the
    throat produced.
    '''

    sizing = buildSizing()

    throatFindings  = sizing.sizeThroat()['findings']
    chamberFindings = sizing.sizeChamber()['findings']

    assert not set(throatFindings) & set(chamberFindings)

def testTabulatedAndIdealCharacteristicVelocityAgreeToWithinFivePercent():

    '''
    The two are different calculations of the same quantity and they are allowed to disagree,
    because one is frozen at the chamber composition and the other is an equilibrium literature
    value. They are not allowed to disagree by a lot, which would mean a table entry is wrong
    rather than that the physics differs.
    '''

    for name, entry in PROPELLANT_COMBINATIONS.items():
        ideal = characteristicVelocity(entry['gamma'], entry['molarMass'],
                                       entry['chamberTemperature'])
        gap = abs(ideal - entry['referenceCstar']) / entry['referenceCstar']
        assert gap < 0.05, f'{name} differs by {gap:.1%}'

def testEveryCombinationHasACharacteristicLength():

    assert set(CHARACTERISTIC_LENGTH) == set(PROPELLANT_COMBINATIONS)

def testEveryOperatingRatioIsFuelRichOfStoichiometric():

    '''
    Peak impulse sits fuel rich, so every tabulated operating point should. A table entry above its
    own stoichiometric ratio would be rejected by the class that reads it.
    '''

    for name, entry in PROPELLANT_COMBINATIONS.items():
        assert entry['mixtureRatio'] < entry['stoichiometricRatio'], name

def testHydrogenHasTheBestImpulseAndTheWorstDensityImpulse():

    '''
    The inversion the PropellantCombination class exists to show. If it ever stops holding, either
    a density is wrong or the comparison has stopped fixing the area ratio.
    '''

    comparison = buildPropellant().compareCombinations()

    assert comparison['bySpecificImpulse'][0] == 'LOX/LH2'
    assert comparison['byDensityImpulse'][-1] == 'LOX/LH2'

def testDensityImpulseIsTheProductItClaimsToBe():

    combination = buildPropellant()

    impulse = combination.calculateDensityImpulse()

    assert impulse['densityImpulse'] == pytest.approx(impulse['bulkDensity']
                                                      * impulse['specificImpulse'])

def testFuelVolumeFractionExceedsFuelMassFractionForEveryCombination():

    '''
    True whenever the fuel is the less dense of the two, which it is for all of these. It is the
    reason a tank layout drawn from the mixture ratio alone comes out wrong.
    '''

    for name in PROPELLANT_COMBINATIONS:
        density = PropellantCombination()
        density.setInputs({'combination': name})
        result = density.calculateBulkDensity()
        assert result['fuelVolumeFraction'] > result['fuelMassFraction'], name

def testSeparationIsFlaggedForAVacuumNozzleAtSeaLevel():

    '''
    An upper stage expansion lit on the pad separates, and the class has to say so rather than
    returning a thrust coefficient that assumes attached flow.
    '''

    performance = buildPerformance(areaRatio = 120.0)

    result = performance.calculateThrustCoefficient(SEA_LEVEL_PRESSURE)

    assert result['separated'] is True
    assert result['exitPressure'] < SUMMERFIELD_SEPARATION_RATIO * SEA_LEVEL_PRESSURE

def testSeparationIsNotFlaggedInVacuum():

    performance = buildPerformance(areaRatio = 120.0)

    assert performance.calculateThrustCoefficient(0.0)['separated'] is False

def testSpecificImpulseRisesMonotonicallyWithAltitude():

    altitude = buildPerformance().calculateAltitudePerformance()

    impulses = [altitude['byAltitude'][value]['specificImpulse']
                for value in sorted(altitude['byAltitude'])]

    assert impulses == sorted(impulses)

def testVacuumImpulseRisesWithAreaRatio():

    expansion = buildPerformance().compareExpansion()

    ratios   = sorted(expansion['areaRatios'])
    impulses = [expansion['areaRatios'][ratio]['vacuumImpulse'] for ratio in ratios]

    assert impulses == sorted(impulses)

def testOptimumAltitudeRisesWithAreaRatio():

    '''
    A larger expansion has a lower exit pressure and therefore matches ambient higher up. This is
    the whole reason upper stages carry large nozzles.
    '''

    low  = buildPerformance(areaRatio = 8.0).calculateAltitudePerformance()
    high = buildPerformance(areaRatio = 60.0).calculateAltitudePerformance()

    assert high['optimumAltitude'] > low['optimumAltitude']
    assert high['exitPressure'] < low['exitPressure']

def testTheTwoEfficienciesMultiplyIntoTheCombinedOne():

    performance = buildPerformance(cstarEfficiency = 0.95,
                                   thrustCoefficientEfficiency = 0.97)

    impulse = performance.calculateSpecificImpulse()

    assert impulse['combinedEfficiency'] == pytest.approx(0.95 * 0.97)
    assert impulse['delivered'] == pytest.approx(impulse['ideal'] * 0.95 * 0.97)

def testSwappingTheEfficienciesGivesTheSameImpulseAndADifferentDiagnosis():

    '''
    The point the class exists to make. The same delivered impulse comes from two different engines
    with two different problems, which is why an Isp efficiency quoted alone says nothing.
    '''

    first  = buildPerformance(cstarEfficiency = 0.95, thrustCoefficientEfficiency = 0.99)
    second = buildPerformance(cstarEfficiency = 0.99, thrustCoefficientEfficiency = 0.95)

    assert (first.calculateSpecificImpulse()['delivered']
            == pytest.approx(second.calculateSpecificImpulse()['delivered']))

    assert (first.calculateCharacteristicVelocity()['delivered']
            != pytest.approx(second.calculateCharacteristicVelocity()['delivered']))

def testHigherChamberPressureShrinksTheThroat():

    low  = buildSizing(chamberPressure = 5.0e6).sizeThroat()
    high = buildSizing(chamberPressure = 15.0e6).sizeThroat()

    assert high['throatArea'] < low['throatArea']

def testChamberVolumeFollowsCharacteristicLength():

    short = buildSizing(characteristicLength = 0.8).sizeChamber()
    long  = buildSizing(characteristicLength = 1.6).sizeChamber()

    assert long['chamberVolume'] / short['chamberVolume'] == pytest.approx(2.0)

def testAnImpossibleContractionRatioIsRefusedRatherThanGivingANegativeBarrel():

    '''
    A large contraction ratio with a short characteristic length leaves the convergent section
    consuming more than the whole chamber volume. That has to raise rather than return a negative
    barrel length.
    '''

    with pytest.raises(SizingError, match = 'no barrel left'):
        buildSizing(contractionRatio = 12.0, characteristicLength = 0.3).sizeChamber()

def testReportsRunForAllThreeClasses():

    assert 'PROPELLANT COMBINATION' in buildPropellant().generateReport()
    assert 'ENGINE PERFORMANCE'     in buildPerformance().generateReport()
    assert 'ENGINE SIZING'          in buildSizing().generateReport()
