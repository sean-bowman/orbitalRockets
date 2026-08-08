
# -- Tests for the environmentsAndLoads component classes -- #

'''

Tiered tests for the five environment classes.

Tier 1 covers the contract: malformed spectra, missing evidence for a derivation, and the guards
that stop a correlation being used where it does not apply.

Tier 2 validates against published values and closed forms: the NASA GEVS spectrum reproduces its
stated 14.1 Grms, decibel addition of two equal sources gives exactly +3.01 dB, the singular
-3.01 dB per octave PSD segment matches its analytic integral, and Miner duration scaling matches
its closed form.

Tier 3 covers self-consistency and the cross-domain agreement that keeps the same physical number
from drifting between domains.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'environmentsAndLoadsLibrary'))

from environmentsUtils import (overallRms, integrateSegment, segmentSlope, scaleSpectrum,
                               minerDurationScaling, decibelToRatio, ratioToDecibel,
                               toleranceLimit, NORMAL_TOLERANCE_FACTORS,
                               QUALIFICATION_MARGIN_RANDOM, QUALIFICATION_MARGIN_SHOCK,
                               MINER_FATIGUE_EXPONENT,
                               InvalidInputError, SpectrumError, DerivationError)
from RandomVibrationSpec import (RandomVibrationSpec, REFERENCE_SPECTRA, ZONE_SEVERITY,
                                 MINIMUM_BANDWIDTH_DECADES)
from ShockSpectrum import (ShockSpectrum, SHOCK_SOURCES, JOINT_ATTENUATION,
                           DISTANCE_ATTENUATION_PER_METRE, PYROSHOCK_VALID_FLOOR,
                           STANDARD_QUALITY_FACTOR)
from AcousticSpec import (AcousticSpec, REFERENCE_ENVIRONMENTS, OCTAVE_CENTRES,
                          REFERENCE_PRESSURE, ACOUSTIC_TEST_MASS_THRESHOLD)
from ThermalEnvironment import (ThermalEnvironment, SURFACE_FINISHES, STEFAN_BOLTZMANN,
                                SOLAR_CONSTANT_PERIHELION, SOLAR_CONSTANT_APHELION,
                                LOW_EARTH_ORBIT_PERIOD)
from LoadFactorSet import (LoadFactorSet, FLIGHT_EVENTS, COMBINATION_METHODS,
                           YIELD_FACTOR, ULTIMATE_FACTOR)

GEVS = [(20.0, 0.026), (50.0, 0.16), (800.0, 0.16), (2000.0, 0.026)]

def buildVibration(**overrides) -> RandomVibrationSpec:

    inputs = {'referenceSpectrum': 'GEVS qualification'}
    inputs.update(overrides)

    spec = RandomVibrationSpec()
    spec.setInputs(inputs)
    return spec

def buildShock(**overrides) -> ShockSpectrum:

    inputs = {'source': 'linear shaped charge', 'distance': 1.2,
              'jointPath': ['bolted', 'bolted']}
    inputs.update(overrides)

    shock = ShockSpectrum()
    shock.setInputs(inputs)
    return shock

def buildAcoustic(**overrides) -> AcousticSpec:

    inputs = {'referenceEnvironment': 'medium launcher fairing', 'surfaceMass': 4.0}
    inputs.update(overrides)

    acoustic = AcousticSpec()
    acoustic.setInputs(inputs)
    return acoustic

def buildThermal(**overrides) -> ThermalEnvironment:

    inputs = {'surfaceFinish': 'white paint', 'altitude': 500.0e3,
              'radiatingArea': 2.0, 'internalDissipation': 50.0, 'missionYears': 5.0}
    inputs.update(overrides)

    thermal = ThermalEnvironment()
    thermal.setInputs(inputs)
    return thermal

def buildFactors(**overrides) -> LoadFactorSet:

    inputs = {'mass': 500.0}
    inputs.update(overrides)

    factors = LoadFactorSet()
    factors.setInputs(inputs)
    factors.addStandardEvents()
    return factors

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testSpectrumNeedsIncreasingFrequencies():

    spec = RandomVibrationSpec()
    spec.setInputs({'breakpoints': [(20.0, 0.01), (2000.0, 0.05), (100.0, 0.02)]})

    with pytest.raises(SpectrumError):
        spec.calculateOverallLevel()

def testSpectrumRejectsNonPositiveDensity():

    spec = RandomVibrationSpec()
    spec.setInputs({'breakpoints': [(20.0, 0.01), (2000.0, 0.0)]})

    with pytest.raises(SpectrumError):
        spec.calculateOverallLevel()

def testNarrowBandIsNotARandomVibrationEnvironment():

    spec = RandomVibrationSpec()
    spec.setInputs({'breakpoints': [(100.0, 0.05), (150.0, 0.05)]})

    with pytest.raises(SpectrumError):
        spec.calculateOverallLevel()

def testDerivationWithoutMeasurementsRaises():

    '''
    A specification chosen rather than derived is legitimate and must be labelled as such, so the
    class refuses to present one as a derivation.
    '''

    with pytest.raises(DerivationError):
        buildVibration().deriveMaximumPredicted()

def testUnknownReferenceSpectrumRaises():

    spec = RandomVibrationSpec()
    with pytest.raises(InvalidInputError):
        spec.setInputs({'referenceSpectrum': 'made up'})

def testUnknownZoneRaises():

    with pytest.raises(InvalidInputError):
        buildVibration().applyZone('propellant')

def testShockBelowPyroshockFloorRaises():

    '''
    An SRS below 100 Hz is usually an artefact; the transient and random environments govern there.
    '''

    shock = buildShock(lowFrequency = 20.0)

    with pytest.raises(SpectrumError):
        shock.calculateAttenuatedSpectrum()

def testUnknownJointTypeRaises():

    shock = buildShock(jointPath = ['glued'])

    with pytest.raises(InvalidInputError):
        shock.calculateAttenuation()

def testAcousticNeedsMatchingBandCounts():

    acoustic = AcousticSpec()
    acoustic.setInputs({'bandCentres': [125.0, 250.0, 500.0], 'bandLevels': [140.0, 141.0]})

    with pytest.raises(SpectrumError):
        acoustic.calculateOverallLevel()

def testVibroacousticNeedsSurfaceMass():

    acoustic = AcousticSpec()
    acoustic.setInputs({'referenceEnvironment': 'medium launcher fairing'})

    with pytest.raises(InvalidInputError):
        acoustic.estimateVibrationResponse()

def testDynamicComponentCannotExceedAxialFactor():

    '''
    The dynamic part is included in the axial factor, so a table where it exceeds the axial value
    produces a negative steady acceleration and a dynamic share above 100 percent.
    '''

    factors = LoadFactorSet()
    factors.setInputs({'mass': 500.0})

    with pytest.raises(InvalidInputError):
        factors.addEvent('impossible', axial = 0.5, lateral = 0.5, dynamic = 1.5)

def testLoadFactorsNeedEventsBeforeAnalysis():

    factors = LoadFactorSet()
    factors.setInputs({'mass': 500.0})

    with pytest.raises(DerivationError):
        factors.identifyGoverning()

def testThermalNeedsRadiatingArea():

    thermal = ThermalEnvironment()
    thermal.setInputs({'surfaceFinish': 'white paint'})

    with pytest.raises(InvalidInputError):
        thermal.calculateOnOrbitCases()

def testDecibelQuantityMustBeNamed():

    with pytest.raises(InvalidInputError):
        decibelToRatio(3.0, quantity = 'energy')

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: against published values and closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testGevsSpectrumReproducesItsPublishedGrms():

    '''
    NASA GSFC-STD-7000 states 14.1 Grms for this breakpoint table. Reproducing it from the
    breakpoints validates the whole log-log integration chain against an external number.
    '''

    grms = overallRms(GEVS)

    assert grms == pytest.approx(REFERENCE_SPECTRA['GEVS qualification']['grms'], rel = 0.005), \
        f'{grms:.3f} against the published 14.1 Grms'

def testGevsSlopesMatchTheSpecification():

    '''
    GEVS is specified as +6, flat, -6 dB per octave. The slopes must come back out.
    '''

    assert segmentSlope(20.0, 0.026, 50.0, 0.16) == pytest.approx(6.0, abs = 0.05)
    assert segmentSlope(50.0, 0.16, 800.0, 0.16) == pytest.approx(0.0, abs = 1.0e-12)
    assert segmentSlope(800.0, 0.16, 2000.0, 0.026) == pytest.approx(-6.0, abs = 0.05)

def testSingularSegmentMatchesItsAnalyticIntegral():

    '''
    A -3.01 dB per octave slope makes the exponent exactly -1 and the integral degenerate to a
    logarithm. That is a real specification slope, not a contrived case, so the singular branch is
    exercised in practice.
    '''

    computed = integrateSegment(100.0, 0.10, 200.0, 0.05)
    analytic = 0.10 * 100.0 * np.log(2.0)

    assert computed == pytest.approx(analytic, rel = 1.0e-12)

def testFlatSegmentIntegratesToItsRectangle():

    assert integrateSegment(100.0, 0.05, 300.0, 0.05) == pytest.approx(0.05 * 200.0,
                                                                       rel = 1.0e-12)

def testThreeDecibelsDoublesPowerAndSixDoublesAmplitude():

    '''
    The distinction that decides whether a margin is a factor of two or of four.
    '''

    assert decibelToRatio(3.0, 'power') == pytest.approx(2.0, rel = 0.005)
    assert decibelToRatio(6.0, 'amplitude') == pytest.approx(2.0, rel = 0.005)
    assert decibelToRatio(6.0, 'power') == pytest.approx(4.0, rel = 0.01)

def testTwoEqualAcousticSourcesGiveExactlyThreeDecibelsMore():

    '''
    The canonical check on logarithmic addition. Two uncorrelated 140 dB sources give 143.01 dB,
    not 280 and not 140.
    '''

    acoustic = AcousticSpec()
    acoustic.setInputs({'bandCentres': [125.0, 250.0], 'bandLevels': [140.0, 140.0]})

    assert acoustic.calculateOverallLevel()['overallLevel'] == pytest.approx(143.0103,
                                                                             abs = 0.001)

def testOverallAcousticLevelExceedsEveryBand():

    result = buildAcoustic().calculateOverallLevel()

    assert result['overallLevel'] > result['loudestBandLevel']
    assert sum(entry['fraction'] for entry in result['contributions']) == pytest.approx(1.0)

def testMinerScalingMatchesItsClosedForm():

    '''
    dB = 10 log10((T1/T2)^(1/b)). Halving a test duration costs 0.753 dB at b = 4.
    '''

    for target, expected in ((30.0, 10.0 * np.log10(2.0 ** 0.25)),
                             (15.0, 10.0 * np.log10(4.0 ** 0.25)),
                             (6.0,  10.0 * np.log10(10.0 ** 0.25))):
        assert minerDurationScaling(60.0, target) == pytest.approx(expected, rel = 1.0e-12)

def testMinerScalingIsZeroForNoChange():

    assert minerDurationScaling(60.0, 60.0) == pytest.approx(0.0, abs = 1.0e-12)

def testQualificationMarginIsThreeDecibelsRandomAndSixShock():

    '''
    Shock carries a larger margin because its scatter is larger and its measurement is harder.
    '''

    assert QUALIFICATION_MARGIN_RANDOM == pytest.approx(3.0)
    assert QUALIFICATION_MARGIN_SHOCK == pytest.approx(6.0)
    assert QUALIFICATION_MARGIN_SHOCK > QUALIFICATION_MARGIN_RANDOM

def testThreeDecibelMarginIsRootTwoInGrms():

    '''
    A decibel margin on a power quantity is a square root in the amplitude everyone quotes, which
    is why a "+3 dB" qualification is only 1.41x in Grms.
    '''

    levels = buildVibration().deriveTestLevels()

    assert levels['densityRatio'] == pytest.approx(2.0, rel = 0.005)
    assert levels['grmsRatio'] == pytest.approx(np.sqrt(2.0), rel = 0.005)

def testShockAttenuatesWithDistanceAndJoints():

    near = buildShock(distance = 0.1, jointPath = []).calculateAttenuation()
    far  = buildShock(distance = 2.0, jointPath = ['bolted', 'bolted',
                                                   'bolted']).calculateAttenuation()

    assert far['totalAttenuation'] < near['totalAttenuation']
    assert near['distanceAttenuation'] == pytest.approx(DISTANCE_ATTENUATION_PER_METRE * 0.1)
    assert far['jointAttenuation'] == pytest.approx(3.0 * JOINT_ATTENUATION['bolted'])

def testIsolatorAttenuatesFarMoreThanAJoint():

    assert JOINT_ATTENUATION['isolated'] < JOINT_ATTENUATION['bolted'] * 5.0

def testStefanBoltzmannBalanceReproducesEquilibrium():

    '''
    The on-orbit hot case must satisfy its own radiation balance: emitted equals absorbed.
    '''

    thermal = buildThermal()
    result  = thermal.calculateOnOrbitCases()

    emitted = (thermal.emissivity * STEFAN_BOLTZMANN * thermal.radiatingArea
               * result['hotTemperature'] ** 4)

    assert emitted == pytest.approx(result['hotAbsorbed'], rel = 1.0e-9)

def testPerihelionIsHotterThanAphelion():

    assert SOLAR_CONSTANT_PERIHELION > SOLAR_CONSTANT_APHELION
    assert (SOLAR_CONSTANT_PERIHELION / SOLAR_CONSTANT_APHELION - 1.0) == pytest.approx(0.068,
                                                                                        abs = 0.01)

def testAeroheatingScalesWithVelocityCubed():

    '''
    Sutton-Graves goes as V^3, so a 20 percent velocity increase is a 73 percent heat flux
    increase. That is why peak heating is not at peak dynamic pressure.
    '''

    slow = buildThermal(velocity = 2000.0, atmosphericDensity = 1.0e-3,
                        noseRadius = 0.5).calculateAeroheating()
    fast = buildThermal(velocity = 2400.0, atmosphericDensity = 1.0e-3,
                        noseRadius = 0.5).calculateAeroheating()

    assert fast['heatFlux'] / slow['heatFlux'] == pytest.approx(1.2 ** 3, rel = 1.0e-9)

def testAeroheatingScalesWithRootDensity():

    thin  = buildThermal(velocity = 2000.0, atmosphericDensity = 1.0e-3,
                         noseRadius = 0.5).calculateAeroheating()
    dense = buildThermal(velocity = 2000.0, atmosphericDensity = 4.0e-3,
                         noseRadius = 0.5).calculateAeroheating()

    assert dense['heatFlux'] / thin['heatFlux'] == pytest.approx(2.0, rel = 1.0e-9)

def testFactorLadderMatchesNasaStandard():

    assert YIELD_FACTOR == pytest.approx(1.10)
    assert ULTIMATE_FACTOR == pytest.approx(1.40)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency and cross-domain agreement -- #
# ------------------------------------------------------------------------------------------------ #

def testFactorsAgreeWithTheStructuresDomain():

    '''
    The cross-domain drift guard. aerospaceStructures carries the same NASA-STD-5001 ladder, and
    the two must not diverge. They are stated independently rather than imported, because the
    domains must not depend on each other's internals.
    '''

    structuresLibrary = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'aerospaceStructures', 'aerospaceStructuresLibrary', 'LoadCase.py')

    assert os.path.exists(structuresLibrary), 'the structures domain must be present'

    import ast

    tree = ast.parse(open(structuresLibrary, encoding = 'utf-8').read())

    theirs = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in ('YIELD_FACTOR', 'ULTIMATE_FACTOR'):
                theirs[node.targets[0].id] = ast.literal_eval(node.value)

    assert theirs['YIELD_FACTOR'] == pytest.approx(YIELD_FACTOR)
    assert theirs['ULTIMATE_FACTOR'] == pytest.approx(ULTIMATE_FACTOR)

def testSpectrumEnergyFractionsSumToOne():

    result = buildVibration().calculateOverallLevel()

    assert sum(segment['energyFraction'] for segment in result['segments']) == \
        pytest.approx(1.0, rel = 1.0e-12)

def testSegmentMeanSquaresSumToTheTotal():

    result = buildVibration().calculateOverallLevel()

    total = sum(segment['meanSquare'] for segment in result['segments'])

    assert np.sqrt(total) == pytest.approx(result['grms'], rel = 1.0e-12)

def testScalingASpectrumTwiceEqualsScalingOnceBySum():

    once  = scaleSpectrum(GEVS, 6.0)
    twice = scaleSpectrum(scaleSpectrum(GEVS, 3.0), 3.0)

    for (frequencyA, densityA), (frequencyB, densityB) in zip(once, twice):
        assert frequencyA == pytest.approx(frequencyB)
        assert densityA == pytest.approx(densityB, rel = 1.0e-12)

def testDecibelRoundTrips():

    for value in (0.5, 1.0, 2.0, 10.0):
        assert decibelToRatio(ratioToDecibel(value, 'power'), 'power') == \
            pytest.approx(value, rel = 1.0e-12)
        assert decibelToRatio(ratioToDecibel(value, 'amplitude'), 'amplitude') == \
            pytest.approx(value, rel = 1.0e-12)

def testGevsAcceptanceIsThreeDecibelsBelowQualification():

    '''
    The two published GEVS spectra must be consistent with the stated margin policy.
    '''

    qualification = overallRms(REFERENCE_SPECTRA['GEVS qualification']['breakpoints'])
    acceptance    = overallRms(REFERENCE_SPECTRA['GEVS acceptance']['breakpoints'])

    assert qualification / acceptance == pytest.approx(np.sqrt(2.0), rel = 0.02)

def testHigherConfidenceGivesAHigherLimit():

    '''
    P95/90 must exceed P95/50, because the extra confidence is bought with a larger factor. That
    is what makes it the defensible choice when the sample is small.
    '''

    sample = [0.10, 0.13, 0.09, 0.15, 0.11, 0.12]

    relaxed = toleranceLimit(sample, basis = 'P95/50')
    strict  = toleranceLimit(sample, basis = 'P95/90')

    assert strict['limitValue'] > relaxed['limitValue']
    assert NORMAL_TOLERANCE_FACTORS['P95/90'] > NORMAL_TOLERANCE_FACTORS['P95/50']

def testMeanBasisAddsNoMargin():

    sample = [0.10, 0.13, 0.09, 0.15, 0.11, 0.12]

    assert toleranceLimit(sample, basis = 'P50/50')['marginOverMean'] == pytest.approx(0.0)

def testSmallSampleAtP9550IsFlagged():

    spec = buildVibration(flightMeasurements = [0.10, 0.14])

    result = spec.deriveMaximumPredicted()

    assert any('not defensible' in finding for finding in result['findings'])

def testZoneSeverityOrdersAsExpected():

    '''
    Zone definition dominates the answer, and the ordering must reflect distance from the source.
    '''

    assert (ZONE_SEVERITY['engine compartment']['factor']
            > ZONE_SEVERITY['aft skirt']['factor']
            > ZONE_SEVERITY['tank barrel']['factor']
            > ZONE_SEVERITY['payload bay']['factor']
            > ZONE_SEVERITY['isolated payload']['factor'])

    spec = buildVibration()

    engine = spec.applyZone('engine compartment')['grms']
    payload = spec.applyZone('isolated payload')['grms']

    assert engine / payload == pytest.approx(
        np.sqrt(ZONE_SEVERITY['engine compartment']['factor']
                / ZONE_SEVERITY['isolated payload']['factor']), rel = 1.0e-9)

def testDurationScalingRoundTrips():

    spec = buildVibration()

    compressed = spec.scaleForDuration(6.0)

    restored = RandomVibrationSpec()
    restored.setInputs({'breakpoints': compressed['scaledSpectrum'],
                        'acceptanceDuration': 6.0})
    expanded = restored.scaleForDuration(60.0)

    for (_, original), (_, returned) in zip(GEVS, expanded['scaledSpectrum']):
        assert returned == pytest.approx(original, rel = 1.0e-9)

def testLargeCompressionIsFlagged():

    result = buildVibration().scaleForDuration(2.0)

    assert result['compressionRatio'] > 10.0
    assert any('failure mode' in finding for finding in result['findings'])

def testShockQualificationIsAFactorOfTwoInAmplitude():

    levels = buildShock().deriveTestLevels()

    assert levels['amplitudeRatio'] == pytest.approx(2.0, rel = 0.005)
    assert levels['qualificationPeak'] == pytest.approx(
        levels['maximumPredictedPeak'] * 2.0, rel = 0.005)

def testShockSpectrumIsFlatAboveTheKnee():

    result = buildShock().calculateAttenuatedSpectrum(points = 20)

    aboveKnee = [level for frequency, level in zip(result['frequencies'], result['levels'])
                 if frequency >= result['kneeFrequency']]

    assert len(aboveKnee) > 1
    assert max(aboveKnee) == pytest.approx(min(aboveKnee), rel = 1.0e-12)

def testShockSpectrumRisesBelowTheKnee():

    result = buildShock().calculateAttenuatedSpectrum(points = 20)

    belowKnee = [level for frequency, level in zip(result['frequencies'], result['levels'])
                 if frequency < result['kneeFrequency']]

    assert all(np.diff(belowKnee) > 0.0), 'the SRS must rise toward the knee'

def testLighterPanelRespondsMoreAcoustically():

    '''
    Vibroacoustic response goes as the inverse square of surface mass, which is why adding mass
    reduces it and why that is usually the wrong trade.
    '''

    light = buildAcoustic(surfaceMass = 2.0).estimateVibrationResponse()
    heavy = buildAcoustic(surfaceMass = 8.0).estimateVibrationResponse()

    assert light['estimatedGrms'] > heavy['estimatedGrms']
    assert light['estimatedGrms'] / heavy['estimatedGrms'] == pytest.approx(4.0, rel = 0.01)

def testTestMethodFollowsSurfaceMass():

    light = buildAcoustic(surfaceMass = 2.0).recommendTestMethod()
    dense = buildAcoustic(surfaceMass = 40.0).recommendTestMethod()

    assert light['recommendation'] == 'acoustic chamber'
    assert dense['recommendation'] == 'shaker'
    assert ACOUSTIC_TEST_MASS_THRESHOLD > 0.0

def testHotCaseExceedsColdCase():

    result = buildThermal().calculateOnOrbitCases()

    assert result['hotTemperature'] > result['coldTemperature']
    assert result['swing'] == pytest.approx(
        result['hotTemperature'] - result['coldTemperature'], rel = 1.0e-12)

def testSurfaceFinishDominatesEquilibriumTemperature():

    '''
    The alpha over epsilon ratio sets a sunlit equilibrium temperature almost by itself, and the
    spread across finishes exceeds what most active thermal control achieves.
    '''

    comparison = buildThermal().compareFinishes()

    assert comparison['hottest'] == 'bare aluminium'
    assert comparison['coolest'] == 'optical solar reflector'
    assert comparison['spread'] > 100.0

    ratios = [entry['ratio'] for entry in comparison['finishes'].values()]
    temperatures = [entry['hot'] for entry in comparison['finishes'].values()]

    assert np.corrcoef(ratios, temperatures)[0, 1] > 0.9, \
        'temperature must track alpha over epsilon closely'

def testEndOfLifeIsHotterThanBeginningOfLife():

    beginning = buildThermal(endOfLife = False)
    end       = buildThermal(endOfLife = True)

    assert end.absorptivity > beginning.absorptivity

    cases = beginning.calculateOnOrbitCases()
    assert cases['endOfLifeRatio'] > cases['beginningOfLifeRatio']

def testThermalCycleCountMatchesTheOrbitPeriod():

    result = buildThermal(missionYears = 1.0).calculateThermalCycles()

    expected = 365.25 * 24.0 * 3600.0 / LOW_EARTH_ORBIT_PERIOD

    assert result['cycles'] == pytest.approx(expected, rel = 1.0e-12)
    assert result['cycles'] > 5000.0, 'a one year LEO mission accumulates thousands of cycles'

def testCombinedLoadFactorExceedsEitherComponent():

    factors = buildFactors()

    for name in factors.events:
        combined = factors.combineEvent(name)
        assert combined['combined'] >= combined['axial']
        assert combined['combined'] >= combined['lateral']

def testVectorCombinationMatchesPythagoras():

    factors = buildFactors()

    combined = factors.combineEvent('max-Q')

    assert combined['combined'] == pytest.approx(
        np.sqrt(combined['axial'] ** 2 + combined['lateral'] ** 2), rel = 1.0e-12)

def testAlgebraicCombinationIsMoreConservativeThanVector():

    vector    = buildFactors(combinationMethod = 'vector').combineEvent('max-Q')
    algebraic = buildFactors(combinationMethod = 'algebraic').combineEvent('max-Q')

    assert algebraic['combined'] > vector['combined']

def testEveryStandardEventHasAPositiveSteadyComponent():

    '''
    Regression on a real data error. The dynamic part is included in the axial factor, so a table
    entry where it exceeds the axial value gives a negative steady acceleration.
    '''

    factors = buildFactors()

    for name, event in factors.events.items():
        assert event['steadyAxial'] >= 0.0, f'{name} has a negative steady component'
        assert abs(event['dynamic']) <= abs(event['axial']) + 1.0e-12, name

def testStagingIsMostlyDynamic():

    factors = buildFactors()

    assert factors.combineEvent('staging')['dynamicShare'] > 0.8
    assert factors.combineEvent('max acceleration')['dynamicShare'] < 0.1

def testFactoredLoadsScaleTheForceNotTheGravityLevel():

    factors = buildFactors()

    limit    = factors.factoredFactors('limit')['events']['liftoff']
    ultimate = factors.factoredFactors('ultimate')['events']['liftoff']

    assert ultimate['axialForce'] == pytest.approx(limit['axialForce'] * ULTIMATE_FACTOR,
                                                   rel = 1.0e-12)

def testReportsRunForAllFiveClasses():

    assert 'RANDOM VIBRATION' in buildVibration().generateReport()
    assert 'SHOCK ENVIRONMENT' in buildShock().generateReport()
    assert 'ACOUSTIC ENVIRONMENT' in buildAcoustic().generateReport()
    assert 'THERMAL ENVIRONMENT' in buildThermal().generateReport()
    assert 'QUASI-STATIC LOAD FACTORS' in buildFactors().generateReport()
