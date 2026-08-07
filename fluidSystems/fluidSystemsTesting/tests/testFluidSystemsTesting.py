
# -- Tests for the fluidSystemsTesting library -- #

'''

Tiered tests for the seven test-engineering classes.

Tier 1 covers pure constants and closed-form relations with no property backend.
Tier 2 validates against published references: MIL-STD-1540 qualification levels, the GUM method, the
success-run reliability formula, and Miner's rule fatigue equivalence.
Tier 3 covers self-consistency, round trips, and the cross-library coupling to fluidSystems.

Author: Sean Bowman
Date:   08/06/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'fluidSystemsTestingLibrary'))

from campaignUtils import (PRESSURE_TEST_FACTORS, QUALIFICATION_MARGINS, MINER_FATIGUE_EXPONENT,
                           LIFE_TEST_FACTOR, ACCEPTANCE_RANDOM_DURATION, BOLTZMANN_EV,
                           TestInfeasibleError, InvalidInputError, EngineeringError,
                           materialProperties, fluidProps)
from TestCampaign import TestCampaign, TEST_CATALOGUE
from PressureTest import PressureTest, TNT_ENERGY_PER_KG, SCALED_DISTANCE_CRITERIA
from LeakTest import LeakTest, DETECTION_MARGIN
from EnvironmentalTest import EnvironmentalTest
from LifeTest import LifeTest, LIFE_DEFINITIONS
from UncertaintyBudget import UncertaintyBudget, DISTRIBUTION_DIVISORS
from SampleSize import SampleSize

# -------------------------------------------------------------------------------------------------- #
# -- Tier 1: constants and closed-form relations -- #
# -------------------------------------------------------------------------------------------------- #

def testPressureFactorsMatchStandards():

    '''
    AIAA S-080 proof factor is 1.5 across every hardware class, and the hazardous fluid line burst
    factor is 4.0. A regression here would silently under-test flight hardware.
    '''

    for hardwareClass, factors in PRESSURE_TEST_FACTORS.items():
        assert factors['proof'] == pytest.approx(1.5), \
            f'Proof factor is 1.5 for every class; {hardwareClass} has {factors["proof"]}'

    assert PRESSURE_TEST_FACTORS['line hazardous fluid']['burst'] == pytest.approx(4.0), \
        'A hazardous fluid line carries a 4.0 burst factor, not the 2.0 of a pressure vessel'
    assert PRESSURE_TEST_FACTORS['pressure vessel metallic']['burst'] == pytest.approx(2.0)

def testQualificationMarginsMatchMilStd1540():

    '''
    MIL-STD-1540 qualification margins: +3 dB, 2x duration, 1.4x shock, 10 K thermal. These are the
    numbers that turn a flight environment into a test level.
    '''

    assert QUALIFICATION_MARGINS['randomVibrationDecibels'] == pytest.approx(3.0)
    assert QUALIFICATION_MARGINS['randomVibrationDuration'] == pytest.approx(2.0)
    assert QUALIFICATION_MARGINS['shockFactor'] == pytest.approx(1.4)
    assert QUALIFICATION_MARGINS['thermalMargin'] == pytest.approx(10.0)

def testMinerExponentAndTheThreeDecibelEquivalence():

    '''
    The standard Miner exponent of 4 is what makes +3 dB equivalent to 4x the exposure time. If the
    exponent changes, every duration-level trade in the library changes with it.
    '''

    assert MINER_FATIGUE_EXPONENT == pytest.approx(4.0)

    levelFactor = 10.0**(3.0 / 10.0)
    assert levelFactor == pytest.approx(2.0, rel = 0.005), '3 dB is a factor of two in PSD'

    timeEquivalent = levelFactor**(MINER_FATIGUE_EXPONENT / 2.0)
    assert timeEquivalent == pytest.approx(4.0, rel = 0.01), \
        '+3 dB with an exponent of 4 must be equivalent to 4x the exposure time'

def testDistributionDivisors():

    '''
    The rectangular divisor of sqrt(3) is the one most often got wrong, and getting it wrong is always
    unconservative: it overstates confidence by a factor of 1.73.
    '''

    assert DISTRIBUTION_DIVISORS['rectangular'] == pytest.approx(np.sqrt(3.0))
    assert DISTRIBUTION_DIVISORS['normal k=2'] == pytest.approx(2.0)
    assert DISTRIBUTION_DIVISORS['triangular'] == pytest.approx(np.sqrt(6.0))
    assert DISTRIBUTION_DIVISORS['normal k=1'] == pytest.approx(1.0)

def testLifeFactorAndTntEnergy():

    '''
    Basic constants that everything else scales from.
    '''

    assert LIFE_TEST_FACTOR == pytest.approx(4.0), 'Flight hardware life demonstration is 4x expected'
    assert TNT_ENERGY_PER_KG == pytest.approx(4.184e6), 'TNT energy is 4.184 MJ/kg by definition'
    assert ACCEPTANCE_RANDOM_DURATION == pytest.approx(60.0)

# -------------------------------------------------------------------------------------------------- #
# -- Tier 2: validation against published references -- #
# -------------------------------------------------------------------------------------------------- #

def testSuccessRunFormula():

    '''
    The success-run relation n = ln(1-C)/ln(R). The reference cases everyone quotes: 22 units for
    R = 0.90 at 90 percent confidence, and 230 for R = 0.99 at the same confidence.
    '''

    sample = SampleSize()
    sample.setInputs({'targetReliability': 0.90, 'confidenceLevel': 0.90})
    assert sample.calculateSuccessRun()['requiredSampleSize'] == 22, \
        'R = 0.90 at 90 percent confidence needs 22 units with zero failures'

    sample = SampleSize()
    sample.setInputs({'targetReliability': 0.99, 'confidenceLevel': 0.90})
    assert sample.calculateSuccessRun()['requiredSampleSize'] == 230

    sample = SampleSize()
    sample.setInputs({'targetReliability': 0.99, 'confidenceLevel': 0.95})
    expected = int(np.ceil(np.log(0.05) / np.log(0.99)))
    assert sample.calculateSuccessRun()['requiredSampleSize'] == expected

def testDemonstratedReliabilityInverse():

    '''
    The reverse calculation R = (1-C)^(1/n) must invert the success-run formula exactly. Three units
    at 90 percent confidence demonstrates 0.464, which is the number that makes the point about why
    reliability is not demonstrated by test alone.
    '''

    sample = SampleSize()
    sample.setInputs({'targetReliability': 0.99, 'confidenceLevel': 0.90, 'availableArticles': 3})
    demonstrated = sample.calculateDemonstrated()['demonstratedReliability']

    assert demonstrated == pytest.approx(0.10**(1.0 / 3.0), rel = 1e-9)
    assert demonstrated == pytest.approx(0.4642, abs = 1e-4), \
        'Three units passing demonstrates R = 0.464 at 90 percent confidence'

def testGumCombinationAndExpansion():

    '''
    The GUM method: standard uncertainties from the stated distributions, combined in quadrature,
    expanded by the coverage factor. Hand-checked against the same arithmetic done explicitly.
    '''

    budget = UncertaintyBudget()
    budget.setInputs({'measurand': 'test', 'measurandValue': 1.0, 'measurandUnit': '-'})
    budget.addContributor('calibration', 0.00025, 'normal k=2')
    budget.addContributor('temperature', 0.00040, 'rectangular')
    budget.addContributor('repeatability', 0.00015, 'normal k=1')

    result = budget.calculate()

    expected = np.sqrt((0.00025 / 2.0)**2 + (0.00040 / np.sqrt(3.0))**2 + 0.00015**2)

    assert result['combinedUncertainty'] == pytest.approx(expected, rel = 1e-9), \
        'The combined uncertainty must be the root-sum-square of the weighted standard uncertainties'
    assert result['expandedUncertainty'] == pytest.approx(2.0 * expected, rel = 1e-9), \
        'The expanded uncertainty must be k times the combined, with k = 2 by default'

def testGumDominantContributor():

    '''
    The dominant contributor is identified by share of variance, not of magnitude. Because the terms
    combine in quadrature, a term at half the magnitude contributes only a quarter of the variance,
    and that is what makes the identification actionable.
    '''

    budget = UncertaintyBudget()
    budget.setInputs({'measurand': 'test', 'measurandValue': 1.0})
    budget.addContributor('small', 0.001, 'normal k=1')
    budget.addContributor('large', 0.010, 'normal k=1')

    result = budget.calculate()

    assert result['dominantContributor'] == 'large'
    assert result['dominantShare'] == pytest.approx(0.010**2 / (0.001**2 + 0.010**2), rel = 1e-9)
    assert result['dominantShare'] > 0.98, \
        'A term ten times larger contributes a hundred times the variance'

def testGrmsFromFlatSpectrum():

    '''
    Grms from a flat PSD is the closed-form sqrt(PSD * bandwidth). This validates the log-log segment
    integration against a case that can be checked by hand.
    '''

    environmental = EnvironmentalTest()
    environmental.setInputs({'flightPowerSpectralDensity': [(20.0, 0.04), (2000.0, 0.04)]})
    result = environmental.calculateRandomVibration()

    expected = np.sqrt(0.04 * (2000.0 - 20.0))

    assert result['acceptanceGrms'] == pytest.approx(expected, rel = 1e-6), \
        f'Grms over a flat PSD must be sqrt(PSD * bandwidth) = {expected:.4f}'

def testGrmsOnAMinusOneSlopeSegment():

    '''
    A segment with slope exactly -1 on a log-log plot is the special case where the power law
    integral degenerates to a logarithm. A regression here would divide by zero or silently produce a
    wrong area.
    '''

    # S = k/f between 100 and 1000 Hz: S(100) = 0.01, S(1000) = 0.001
    environmental = EnvironmentalTest()
    environmental.setInputs({'flightPowerSpectralDensity': [(100.0, 0.01), (1000.0, 0.001)]})
    result = environmental.calculateRandomVibration()

    expectedArea = 0.01 * 100.0 * np.log(10.0)

    assert result['acceptanceGrms'] == pytest.approx(np.sqrt(expectedArea), rel = 1e-6), \
        'The slope = -1 segment must integrate to S1 * f1 * ln(f2/f1)'

def testQualificationIsThreeDecibelsAndDoubleDuration():

    '''
    Qualification random vibration is acceptance +3 dB for 2x duration. The Grms ratio must therefore
    be sqrt(2), because 3 dB is a factor of two in PSD and Grms is the square root of the integral.
    '''

    environmental = EnvironmentalTest()
    environmental.setInputs({'flightEnvironmentKey': 'launch vehicle component', 'flightDuration': 60.0})
    result = environmental.calculateRandomVibration()

    assert result['qualificationGrms'] / result['acceptanceGrms'] == pytest.approx(np.sqrt(2.0), rel = 0.005), \
        'A 3 dB level increase must raise Grms by sqrt(2)'
    assert result['qualificationDuration'] == pytest.approx(120.0), \
        'Qualification duration is twice acceptance'

def testArrheniusAccelerationFactor():

    '''
    Arrhenius acceleration, hand-checked. With Ea = 0.7 eV, 293.15 K service and 373.15 K test, the
    factor is about 380.
    '''

    life = LifeTest()
    life.setInputs({'articleType': 'seal', 'expectedLife': 1.0e6, 'accelerationModel': 'arrhenius',
                    'useTemperature': 293.15, 'testTemperature': 373.15, 'activationEnergy': 0.7})
    life.calculateRequiredLife()
    result = life.calculateAcceleration()

    expected = np.exp((0.7 / BOLTZMANN_EV) * (1.0 / 293.15 - 1.0 / 373.15))

    assert result['accelerationFactor'] == pytest.approx(expected, rel = 1e-9)
    assert result['accelerationFactor'] == pytest.approx(380.0, rel = 0.02), \
        'Arrhenius at 0.7 eV from 20 to 100 degC should give roughly 380x'

def testCoffinMansonAccelerationFactor():

    '''
    Coffin-Manson acceleration is a simple power law in the temperature range ratio. Doubling the
    cycle amplitude with an exponent of 2 gives a factor of four.
    '''

    life = LifeTest()
    life.setInputs({'articleType': 'bellows', 'expectedLife': 1000.0,
                    'accelerationModel': 'coffin-manson',
                    'useTemperatureRange': 40.0, 'testTemperatureRange': 80.0,
                    'coffinMansonExponent': 2.0})
    life.calculateRequiredLife()
    result = life.calculateAcceleration()

    assert result['accelerationFactor'] == pytest.approx(4.0, rel = 1e-9), \
        'Doubling the thermal cycle amplitude with an exponent of 2 gives 4x acceleration'

def testPneumaticStoresFarMoreEnergyThanHydrostatic():

    '''
    The calculation that justifies the rule to proof with a liquid. The same volume at the same
    pressure stores orders of magnitude more energy as a gas than as a liquid.
    '''

    common = {'maximumExpectedOperatingPressure': 20.0e6, 'hardwareClass': 'pressure vessel metallic',
              'testVolume': 0.010, 'testTemperature': 293.15}

    hydrostatic = PressureTest()
    hydrostatic.setInputs({**common, 'testMedium': 'liquid', 'testFluid': 'Water'})
    hydrostatic.calculateLevels()
    liquidEnergy = hydrostatic.calculateStoredEnergy()['storedEnergy']

    pneumatic = PressureTest()
    pneumatic.setInputs({**common, 'testMedium': 'gas', 'testFluid': 'Nitrogen'})
    pneumatic.calculateLevels()
    gasEnergy = pneumatic.calculateStoredEnergy()['storedEnergy']

    # The ratio is about 200 at this pressure. It is not larger because water's own compression
    # energy stops being negligible at 30 MPa: P^2 * V / (2 * K) is roughly 2 kJ. At the lower
    # pressures typical of a component proof test the ratio is far higher, which is the usual case.
    assert gasEnergy > 100.0 * liquidEnergy, \
        f'A pneumatic test must store orders of magnitude more energy: got {gasEnergy:.0f} J vs ' \
        f'{liquidEnergy:.1f} J, a factor of only {gasEnergy / liquidEnergy:.0f}'
    assert gasEnergy > 1.0e5, 'Ten litres at 30 MPa is a several hundred kJ hazard'

def testScaledDistanceStandoff():

    '''
    Hopkinson-Cranz scaling: R = Z * W^(1/3). Standoff must scale with the cube root of the TNT
    equivalent, which is what makes a scaled-distance criterion usable across charge sizes.
    '''

    test = PressureTest()
    test.setInputs({'maximumExpectedOperatingPressure': 20.0e6,
                    'hardwareClass': 'pressure vessel metallic',
                    'testMedium': 'gas', 'testFluid': 'Nitrogen', 'testVolume': 0.010})
    test.calculateLevels()
    result = test.calculateStoredEnergy()

    for criterion, scaledDistance in SCALED_DISTANCE_CRITERIA.items():
        expected = scaledDistance * result['tntEquivalent']**(1.0 / 3.0)
        assert result['safeStandoffDistance'][criterion] == pytest.approx(expected, rel = 1e-9), \
            f'Standoff for {criterion} must follow the cube root scaling law'

# -------------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency, sequencing and cross-library coupling -- #
# -------------------------------------------------------------------------------------------------- #

def testProofBeforeLeakInEverySequence():

    '''
    The ordering rule that exists because proof can open a marginal joint. If proof ever sorts after
    the post-proof leak test, the sequence has lost its meaning.
    '''

    campaign = TestCampaign()
    campaign.setInputs({'articleName': 'test', 'articleType': 'valve'})
    matrix = campaign.buildMatrix()

    for sequence in (matrix['qualificationSequence'], matrix['acceptanceSequence']):
        names = [entry['name'] for entry in sequence]
        assert names.index('proof pressure') < names.index('leak test, post proof'), \
            'Proof must precede the post-proof leak test'

def testBurstIsLastAndQualificationOnly():

    '''
    Burst destroys the article, so it must sort last and must never appear in an acceptance sequence,
    which is applied to every flight article.
    '''

    campaign = TestCampaign()
    campaign.setInputs({'articleName': 'test', 'articleType': 'pressure vessel'})
    matrix = campaign.buildMatrix()

    qualificationNames = [entry['name'] for entry in matrix['qualificationSequence']]
    assert qualificationNames[-1] == 'burst pressure', 'Burst must be the last qualification test'

    acceptanceNames = [entry['name'] for entry in matrix['acceptanceSequence']]
    assert 'burst pressure' not in acceptanceNames, \
        'A destructive test must never appear in the acceptance sequence'

def testNoAcceptanceTestIsDestructive():

    '''
    The general form of the rule. Acceptance is applied to every flight article and must leave it
    flyable.
    '''

    for articleType in ('valve', 'line', 'pressure vessel', 'filter', 'regulator'):
        campaign = TestCampaign()
        campaign.setInputs({'articleName': 'test', 'articleType': articleType})
        matrix = campaign.buildMatrix()
        for entry in matrix['acceptanceSequence']:
            assert not entry['destructive'], \
                f'{entry["name"]} is destructive and appears in the {articleType} acceptance sequence'

def testCryogenicAddsColdTesting():

    '''
    A cryogenic article must pick up the cold functional and cold leak tests, because ambient leak
    testing does not qualify a cryogenic joint.
    '''

    ambient = TestCampaign()
    ambient.setInputs({'articleName': 'test', 'articleType': 'valve', 'isCryogenic': False})
    ambientNames = [entry['name'] for entry in ambient.buildSequence('qualification')]

    cryogenic = TestCampaign()
    cryogenic.setInputs({'articleName': 'test', 'articleType': 'valve', 'isCryogenic': True})
    cryogenicNames = [entry['name'] for entry in cryogenic.buildSequence('qualification')]

    assert 'cryogenic functional' not in ambientNames
    assert 'cryogenic functional' in cryogenicNames
    assert 'leak test, at temperature' in cryogenicNames, \
        'A cryogenic article must be leak tested cold, not only at ambient'

def testTailoringIsRecordedNotSilent():

    '''
    Tailoring by omission is the failure mode. A removed test must disappear from the sequence AND
    appear in the tailoring record with its reason.
    '''

    campaign = TestCampaign()
    campaign.setInputs({'articleName': 'test', 'articleType': 'valve',
                        'tailoring': {'shock': 'No pyrotechnic events in this configuration'}})
    matrix = campaign.buildMatrix()

    names = [entry['name'] for entry in matrix['qualificationSequence']]
    assert 'shock' not in names, 'A tailored test must be removed from the sequence'

    assert len(matrix['tailoredOut']) == 1
    assert matrix['tailoredOut'][0]['name'] == 'shock'
    assert matrix['tailoredOut'][0]['reason'], 'A tailored test must carry a stated reason'

def testTailoringAnUnknownTestRaises():

    '''
    Tailoring out a test that is not in the catalogue is almost always a typo, and silently ignoring
    it would leave the real test in the sequence while everyone believes it was removed.
    '''

    campaign = TestCampaign()
    with pytest.raises(InvalidInputError):
        campaign.setInputs({'articleName': 'test', 'articleType': 'valve',
                            'tailoring': {'nonexistent test': 'reason'}})

def testMinerScalingRoundTrips():

    '''
    Scaling a duration to a level and back must return the original duration. Catches an inverted
    exponent, which would make every compressed test level wrong in the unconservative direction.
    '''

    environmental = EnvironmentalTest()
    environmental.setInputs({'flightEnvironmentKey': 'launch vehicle component', 'flightDuration': 60.0})
    environmental.calculateRandomVibration()

    forward   = environmental.scaleDurationToLevel(30.0)
    backward  = environmental.scaleLevelToDuration(forward['decibelIncrease'])

    assert backward['equivalentDuration'] == pytest.approx(30.0, rel = 1e-6), \
        'Duration to level and back must round trip'

def testUnmeasurableLeakRequirementRaises():

    '''
    A leak requirement below the floor of every method must raise at planning time, while the
    requirement can still be renegotiated, rather than being discovered in the test cell.
    '''

    leak = LeakTest()
    leak.setInputs({'allowableLeakRate': 1.0e-13, 'testPressure': 2.4e6})

    with pytest.raises(TestInfeasibleError):
        leak.selectMethod()

def testLeakAllocationAcrossJoints():

    '''
    Leak rates add, so the per-joint allowable is the system allowable divided by the joint count.
    This is the calculation that connects a hazard-derived requirement to a joint selection decision.
    '''

    leak = LeakTest()
    leak.setInputs({'allowableLeakRate': 1.2e-5, 'testPressure': 2.4e6,
                    'downstreamPressure': 101325.0, 'jointCount': 12})
    result = leak.allocateAcrossJoints()

    assert result['perJointAllowable'] == pytest.approx(1.0e-6, rel = 1e-9)
    assert 'AN flare' not in result['adequateJointTypes'], \
        'An AN flare at 1e-4 scc/s cannot meet a 1e-6 scc/s per-joint allowable'
    assert 'welded' in result['adequateJointTypes']

def testLeakTestDelegatesToTheDesignLibrary():

    '''
    The cross-library coupling. LeakTest must use the fluidSystems LeakPath physics rather than
    reimplementing it, so a design-side statement about achievable leak class and a test-side
    statement about measurability cannot drift apart.
    '''

    from LeakPath import LeakPath

    leak = LeakTest()
    leak.setInputs({'allowableLeakRate': 1.0e-5, 'testPressure': 2.5e6,
                    'downstreamPressure': 101325.0, 'temperature': 293.15})

    assert isinstance(leak.leakPath, LeakPath), 'LeakTest must build a real LeakPath'
    assert leak.flowRegime in ('viscous', 'transitional', 'molecular', 'choked')
    assert leak.equivalentDiameter > 0.0

    # And the equivalent diameter must match what LeakPath computes independently
    independent = LeakPath()
    independent.setInputs({'species': 'He', 'upstreamPressure': 2.5e6,
                           'downstreamPressure': 101325.0, 'temperature': 293.15,
                           'leakRate': 1.0e-5, 'leakRateUnit': 'sccs', 'length': 1.0e-3})
    assert leak.equivalentDiameter == pytest.approx(independent.calculateEquivalentDiameter(), rel = 1e-9)

def testPressureTestUsesSharedMaterialProperties():

    '''
    The cross-package coupling. PressureTest must use the same material allowables from common that
    the design library used, so the test level and the design margin are consistent.
    '''

    test = PressureTest()
    test.setInputs({'maximumExpectedOperatingPressure': 2.0e6, 'hardwareClass': 'component',
                    'material': '316L', 'outerDiameter': 0.0254, 'wallThickness': 0.0025})
    test.calculateLevels()
    result = test.checkArticleCapability()

    expected = materialProperties('316L', 293.15)
    assert result['yieldStrength'] == pytest.approx(expected['yieldStrength'], rel = 1e-12), \
        'PressureTest must use the shared material properties, not its own copy'

def testProofExceedingYieldRaises():

    '''
    A proof test that would yield the article is a design problem, not a test problem, and it must
    raise rather than quietly reporting a margin below one. Proof is applied to every flight article.
    '''

    test = PressureTest()
    test.setInputs({'maximumExpectedOperatingPressure': 50.0e6, 'hardwareClass': 'component',
                    'material': '6061-T6', 'outerDiameter': 0.0254, 'wallThickness': 0.0005})
    test.calculateLevels()

    with pytest.raises(TestInfeasibleError):
        test.checkArticleCapability()

def testLifeTestFactorAndInfeasibility():

    '''
    Life is 4x expected, and a test that does not fit the schedule must raise with the options in the
    message rather than silently reporting a duration nobody reads.
    '''

    life = LifeTest()
    life.setInputs({'articleType': 'valve', 'expectedLife': 5000.0, 'cycleRate': 2.0,
                    'availableDuration': 30.0 * 86400.0})
    result = life.calculateRequiredLife()

    assert result['requiredLife'] == pytest.approx(20000.0), 'Life demonstration is 4x expected'
    assert life.calculateDuration()['feasible'] is True

    impossible = LifeTest()
    impossible.setInputs({'articleType': 'valve', 'expectedLife': 1.0e8, 'cycleRate': 1.0,
                          'availableDuration': 86400.0})
    impossible.calculateRequiredLife()

    with pytest.raises(TestInfeasibleError):
        impossible.calculateDuration()

def testEveryLifeDefinitionCarriesItsCondition():

    '''
    The condition is the important half of a life definition. Cycling at the wrong condition
    demonstrates the wrong thing, and a definition without one is useless.
    '''

    for articleType, definition in LIFE_DEFINITIONS.items():
        assert definition['unit'], f'{articleType} has no life unit'
        assert definition['condition'], f'{articleType} has no test condition'
        assert definition['wearOut'], f'{articleType} has no wear-out mechanism listed'

def testErrorHierarchy():

    '''
    Every error in this library must be catchable as EngineeringError, so a caller can handle the
    whole family from any domain with one except clause.
    '''

    assert issubclass(TestInfeasibleError, EngineeringError)
    assert issubclass(InvalidInputError, EngineeringError)

    error = TestInfeasibleError('test', required = 1.0, achievable = 2.0, method = 'x')
    assert error.getContext()['required'] == 1.0
    assert error.getContext()['method'] == 'x'

def testEveryCatalogueEntryIsWellFormed():

    '''
    The catalogue drives the whole campaign, so a malformed entry would silently corrupt every
    sequence built from it.
    '''

    for name, data in TEST_CATALOGUE.items():
        assert isinstance(data['sequence'], int), f'{name} has a non-integer sequence number'
        assert data['levels'], f'{name} applies at no level'
        assert all(level in ('development', 'qualification', 'acceptance', 'preflight')
                   for level in data['levels']), f'{name} has an unknown level'
        assert data['purpose'], f'{name} has no stated purpose'
        assert isinstance(data['destructive'], bool)
