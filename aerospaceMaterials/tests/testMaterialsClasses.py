
# -- Tests for the aerospaceMaterials domain classes -- #

'''

Tiered tests for Allowables, MaterialSelector, DamageTolerance, CorrosionAssessment, HeatTreatment
and ProcessComparison.

Tier 1 covers the guards: the inputs that must raise, and the outputs that must never silently be
wrong in the unconservative direction.
Tier 2 validates against published values -- MMPDS k-factors, the PREN and CPT correlations, the
7075 through-hardening limit, and the ASTM F1940 bake trigger.
Tier 3 covers self-consistency: three independent k-factor routes against each other, and the
physical invariants that have to hold whatever the inputs.

Two of these tests exist because writing them found a real bug. testParisCoefficientUnits catches a
Pa versus MPa error in the crack growth integration that returned zero life, and
testQuenchSeverityUnits catches an inverse-inch versus inverse-metre error that reported every
quench as perfect.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'aerospaceMaterialsLibrary'))
sys.path.insert(0, ROOT)

from Allowables import (Allowables, toleranceFactorExact, toleranceFactorNatrella,
                        toleranceFactorMmpds, STANDARD_KNOCKDOWNS, SCIPY_AVAILABLE,
                        MINIMUM_SAMPLE_SIZE, Z_QUANTILE_B)
from MaterialSelector import MaterialSelector, ASHBY_INDICES, ENVIRONMENT_SEVERITY
from DamageTolerance import DamageTolerance, GEOMETRY_FACTORS, NDE_FLAW_SIZES
from CorrosionAssessment import (CorrosionAssessment, GALVANIC_POTENTIAL_LIMIT,
                                 HYDROGEN_BAKE_THRESHOLD, CPT_SLOPE, CPT_INTERCEPT)
from HeatTreatment import HeatTreatment, QUENCH_SEVERITY, LARSON_MILLER_CONSTANT
from ProcessComparison import ProcessComparison, PROCESS_ROUTES
from MaterialDatabase import queryMaterial
from materialData import MATERIAL_DATABASE
from utils import InvalidInputError, CompatibilityError

from validation.referenceCases import TOLERANCE_FACTORS

# ---------------------------------------------------------------------------------------------- #
# -- Fixtures -- #
# ---------------------------------------------------------------------------------------------- #

@pytest.fixture(scope = 'module')
def titaniumSample():
    '''Thirty specimens of Ti-6Al-4V ultimate strength, mean 950 MPa, CV about 3 percent.'''
    generator = np.random.default_rng(42)
    return generator.normal(950.0e6, 30.0e6, 30)

@pytest.fixture(scope = 'module')
def multiBatchSample():
    '''Sixty specimens across six lots, with real between-lot variation.'''
    generator   = np.random.default_rng(7)
    values      = []
    identifiers = []
    for lot in range(6):
        lotMean = 950.0e6 + generator.normal(0.0, 25.0e6)
        values.extend(generator.normal(lotMean, 15.0e6, 10))
        identifiers.extend([f'lot{lot}'] * 10)
    return np.array(values), np.array(identifiers)

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testSmallSampleRaisesRatherThanReturningANumber():

    '''
    The single most dangerous thing this domain could do is return an A-basis from five specimens.
    The number would carry the authority of a statistical allowable and the content of a guess.
    '''

    allowables = Allowables()
    allowables.setInputs({'sampleData': np.array([950.0e6, 930.0e6, 970.0e6, 940.0e6, 960.0e6]),
                          'basis': 'A'})

    with pytest.raises(InvalidInputError):
        allowables.calculateBasisValue()

def testKnockdownAboveUnityRaises():

    '''
    A knockdown must reduce the value. A factor above 1.0 is either a sign error or somebody trying
    to take credit for a process improvement in the wrong place.
    '''

    allowables = Allowables()
    allowables.setInputs({'sampleData': np.full(20, 950.0e6) + np.arange(20) * 1.0e6,
                          'knockdowns': {'wishful thinking': 1.15}})
    allowables.calculateBasisValue()

    with pytest.raises(InvalidInputError):
        allowables.applyKnockdowns()

def testEveryStandardKnockdownReducesTheValue():

    '''
    A completeness check on the table itself. Every factor must lie in (0, 1] and carry a written
    basis, so a new entry cannot be added without a justification.
    '''

    for name, entry in STANDARD_KNOCKDOWNS.items():
        assert 0.0 < entry['factor'] <= 1.0, \
            f'Knockdown \'{name}\' has factor {entry["factor"]}, outside (0, 1]'
        assert entry.get('basis'), f'Knockdown \'{name}\' has no written basis'

def testProofStressBelowOperatingRaises():

    '''
    A proof test at or below the operating stress screens nothing that service would not already
    have found, so accepting it would credit a test that does nothing.
    '''

    damage = DamageTolerance()
    with pytest.raises(InvalidInputError):
        damage.setInputs({'material': 'Ti-6Al-4V', 'operatingStress': 500.0e6,
                          'proofStress': 450.0e6})

def testMissingFractureDataRaisesRatherThanAssuming():

    '''
    A fracture critical part cannot be analysed without toughness data, and assuming a value would
    be worse than refusing. AlSi10Mg stress relieved has no fracture block.
    '''

    damage = DamageTolerance()
    damage.setInputs({'material': 'AlSi10Mg', 'condition': 'lpbf stress relieved',
                      'operatingStress': 100.0e6})

    with pytest.raises(InvalidInputError):
        damage.calculateCriticalFlaw()

def testShortTransverseSccRaisesForSusceptibleAlloy():

    '''
    Fifty MPa of sustained short transverse tension in 7075-T6 in marine air will crack. That is a
    stress nobody would think twice about, which is exactly why this raises rather than warns.
    '''

    corrosion = CorrosionAssessment()
    corrosion.setInputs({'anodeMaterial': '7075', 'anodeCondition': 't6',
                         'appliedStress': 120.0e6, 'orientation': 'ST',
                         'environment': 'launch site marine', 'sccEnvironmentKey': 'salt fog'})

    with pytest.raises(CompatibilityError):
        corrosion.assessStressCorrosion()

def testT73DoesNotRaiseWhereT6Does():

    '''
    The whole purpose of the T73 overage is to raise the SCC threshold from 50 to 240 MPa. If both
    tempers behaved the same the test above would be catching a blanket rule rather than a real
    material difference.
    '''

    corrosion = CorrosionAssessment()
    corrosion.setInputs({'anodeMaterial': '7075', 'anodeCondition': 't73',
                         'appliedStress': 120.0e6, 'orientation': 'ST',
                         'environment': 'launch site marine', 'sccEnvironmentKey': 'salt fog'})

    result = corrosion.assessStressCorrosion()
    assert result['exceedsThreshold'] is False, \
        'T73 exists to survive this stress. If it does not, the overage has bought nothing.'

def testWeightsMustSumToOne():

    '''
    A score built from weights that do not sum to one is not comparable between runs, which makes
    the whole ranking meaningless in a trade study.
    '''

    selector = MaterialSelector()
    with pytest.raises(InvalidInputError):
        selector.setInputs({'requirements': {}, 'weights': {'mass': 0.9, 'cost': 0.9,
                                                            'leadTime': 0.1, 'risk': 0.1}})

def testMachiningTheWholeSectionRaises():

    '''
    A degenerate input that would otherwise divide by zero in the second moment of area.
    '''

    treatment = HeatTreatment()
    with pytest.raises(InvalidInputError):
        treatment.setInputs({'material': '7075', 'machinedFraction': 1.0})

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation against published values -- #
# ---------------------------------------------------------------------------------------------- #

@pytest.mark.skipif(not SCIPY_AVAILABLE, reason = 'exact k-factor needs scipy')
def testToleranceFactorsAgainstPublishedTables():

    '''
    Validated against the published MMPDS Chapter 9 tolerance factor tables. These four values are
    the ones quoted in every textbook treatment and a transcription error in the quantiles would
    move them all.
    '''

    assert toleranceFactorExact(10, 'B') == pytest.approx(2.355, rel = 0.005), \
        'k_B at n = 10 is 2.355 in every published table'
    assert toleranceFactorExact(10, 'A') == pytest.approx(3.981, rel = 0.005), \
        'k_A at n = 10 is 3.981'
    assert toleranceFactorExact(30, 'B') == pytest.approx(1.777, rel = 0.005)
    assert toleranceFactorExact(30, 'A') == pytest.approx(3.064, rel = 0.005)

@pytest.mark.skipif(not SCIPY_AVAILABLE, reason = 'exact k-factor needs scipy')
def testNistWorkedExampleReproducedExactly():

    '''
    The published anchor for this domain, and the one it went longest without.

    NIST/SEMATECH works a one-sided tolerance limit end to end for 43 wafers at 90 per cent
    coverage and 99 per cent confidence, printing every intermediate. Both library routes land on
    the published k to four decimal places.

    Ninety-nine per cent confidence is deliberately not the library default of ninety-five, so
    neither function can reproduce this by happening to have been written around it.
    '''

    reference = TOLERANCE_FACTORS['NIST-SEMATECH-1.3.5.2']

    sampleSize = reference['sampleSize']
    confidence = reference['confidence']

    # Coverage of 0.90 is what the B-basis quantile means, so B-basis is the right argument here
    # and the fact that this example is about wafers rather than metal changes nothing.
    exact    = toleranceFactorExact(sampleSize, 'B', confidence)
    natrella = toleranceFactorNatrella(sampleSize, 'B', confidence)

    assert exact == pytest.approx(reference['exactFactor'], abs = 5.0e-5), \
        f"noncentral t route gives {exact:.4f} against the published " \
        f"{reference['exactFactor']:.4f}"
    assert natrella == pytest.approx(reference['natrellaFactor'], abs = 5.0e-5), \
        f"Natrella route gives {natrella:.4f} against the published " \
        f"{reference['natrellaFactor']:.4f}"

@pytest.mark.skipif(not SCIPY_AVAILABLE, reason = 'exact k-factor needs scipy')
def testNistIntermediatesReproducedNotJustTheAnswer():

    '''
    k is a ratio, so reproducing it does not prove that either half of the ratio is right. A
    noncentrality parameter too large by some factor and a quantile too small by the same one
    return the published k while getting both wrong.

    The handbook prints a, b, the noncentrality and the noncentral t quantile, so all four are
    asserted rather than the answer alone.
    '''

    from scipy import stats

    reference  = TOLERANCE_FACTORS['NIST-SEMATECH-1.3.5.2']
    sampleSize = reference['sampleSize']

    coverageQuantile   = Z_QUANTILE_B
    confidenceQuantile = stats.norm.ppf(reference['confidence'])

    # The handbook prints its quantiles to four figures, which is the precision available here.
    assert coverageQuantile == pytest.approx(reference['coverageQuantile'], abs = 5.0e-5)
    assert confidenceQuantile == pytest.approx(reference['confidenceQuantile'], abs = 5.0e-5)

    a = 1.0 - confidenceQuantile ** 2 / (2.0 * (sampleSize - 1))
    b = coverageQuantile ** 2 - confidenceQuantile ** 2 / sampleSize

    assert a == pytest.approx(reference['natrellaA'], abs = 5.0e-5)
    assert b == pytest.approx(reference['natrellaB'], abs = 5.0e-5)

    noncentrality = coverageQuantile * np.sqrt(sampleSize)
    quantile      = stats.nct.ppf(reference['confidence'], sampleSize - 1, noncentrality)

    assert noncentrality == pytest.approx(reference['noncentrality'], abs = 5.0e-5)
    assert quantile == pytest.approx(reference['noncentralTQuantile'], abs = 5.0e-6)

@pytest.mark.skipif(not SCIPY_AVAILABLE, reason = 'exact k-factor needs scipy')
def testNatrellaErrsInTheUnconservativeDirection():

    '''
    The direction of an approximation's error matters more than its size. Natrella returns a
    smaller k than the exact route at every sample size, and a smaller k is a larger allowable, so
    the approximation reports material as stronger than the statistics support.

    It is worst at n = 10, which is the smallest sample the library will accept, and that is the
    reason the exact route is the default rather than the fast one.
    '''

    for basis in ('A', 'B'):
        for sampleSize in (10, 20, 30, 50, 100, 300):
            assert toleranceFactorNatrella(sampleSize, basis) < toleranceFactorExact(sampleSize,
                                                                                     basis), \
                f'Natrella is expected below exact for {basis}-basis at n = {sampleSize}'

    for basis, bound in (('A', 0.011), ('B', 0.015)):
        exact = toleranceFactorExact(MINIMUM_SAMPLE_SIZE, basis)
        error = abs(toleranceFactorNatrella(MINIMUM_SAMPLE_SIZE, basis) - exact) / exact
        assert error < bound, \
            f'Natrella is {error * 100:.2f} % low for {basis}-basis at the minimum sample size'

def testToleranceFactorApproachesTheNormalQuantile():

    '''
    As the sample grows the tolerance factor must converge on the standard normal quantile, because
    with infinite data there is no confidence penalty left to pay. A factor that converged on
    anything else would mean the quantiles are wrong.
    '''

    assert toleranceFactorNatrella(100000, 'B') == pytest.approx(1.2816, rel = 0.01)
    assert toleranceFactorNatrella(100000, 'A') == pytest.approx(2.3263, rel = 0.01)

def testPittingResistanceAgainstPublishedCorrelation():

    '''
    Validated against the standard PREN definition and the widely used CPT correlation. 316L comes
    out at PREN 26 and a critical pitting temperature near minus 6 C, which is the number that says
    plainly that 316L pits at ambient temperature in a chloride environment.

    This one calculation carries more of the corrosion story than any compatibility table.
    '''

    corrosion = CorrosionAssessment()
    corrosion.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed'})
    result = corrosion.calculatePittingResistance()

    assert result['pren'] == pytest.approx(26.1, abs = 0.3), \
        'PREN for 316L (17 Cr, 2.5 Mo, 0.05 N) is 17 + 8.25 + 0.8 = 26.05'
    assert result['criticalPittingCelsius'] == pytest.approx(-6.0, abs = 2.0)
    assert result['pitsAtServiceTemperature'] is True, \
        'A critical pitting temperature below ambient means 316L pits at a coastal launch site'

def testInconel625FarOutperforms316LOnPitting():

    '''
    Validated against the reason 625 bellows are specified at coastal sites. PREN 51 against 26 is
    a critical pitting temperature of +57 C against -6 C, and that gap is the justification for a
    seven times cost multiplier.
    '''

    stainless = CorrosionAssessment()
    stainless.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed'})

    nickel = CorrosionAssessment()
    nickel.setInputs({'anodeMaterial': 'Inconel 625', 'anodeCondition': 'annealed'})

    stainlessResult = stainless.calculatePittingResistance()
    nickelResult    = nickel.calculatePittingResistance()

    assert nickelResult['pren'] > 1.9 * stainlessResult['pren']

    # The PREN ratio understates the difference. What matters is which side of ambient the critical
    # pitting temperature falls on, and the two land 63 degrees apart across that line.
    assert nickelResult['criticalPittingCelsius'] > 40.0
    assert stainlessResult['criticalPittingCelsius'] < 10.0
    assert nickelResult['pitsAtServiceTemperature'] is False
    assert stainlessResult['pitsAtServiceTemperature'] is True

def testHydrogenBakeTriggersOnTensileStrength():

    '''
    Validated against ASTM F1940 and AMS 2759/9: a plated part above 1000 MPa ultimate requires a
    bake of at least 23 hours at 190 C. 4340 at 1790 MPa triggers it and 316L at 485 MPa does not.
    '''

    steel = CorrosionAssessment()
    steel.setInputs({'anodeMaterial': '4340', 'anodeCondition': 'qt-260'})
    steelResult = steel.assessHydrogenEmbrittlement()

    stainless = CorrosionAssessment()
    stainless.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed'})
    stainlessResult = stainless.assessHydrogenEmbrittlement()

    assert steelResult['bakeRequired'] is True
    assert steelResult['bakeTime'] == pytest.approx(82800.0)
    assert stainlessResult['bakeRequired'] is False
    assert steelResult['susceptibilityIndex'] > stainlessResult['susceptibilityIndex'] * 3.0, \
        'A BCC martensitic steel at 1790 MPa must score far worse than an austenitic stainless'

def testHydrogenSusceptibilityPeaksNearTwoHundredKelvin():

    '''
    The counterintuitive part, and the reason a room temperature hydrogen test understates the
    problem: embrittlement is worst near 200 to 250 K, not at either extreme. Cold slows the
    diffusion that feeds the crack tip and heat lets hydrogen escape faster than it accumulates.
    '''

    factors = {}
    for temperature in (77.0, 225.0, 293.15, 500.0):
        corrosion = CorrosionAssessment()
        corrosion.setInputs({'anodeMaterial': '4340', 'anodeCondition': 'qt-260',
                             'temperature': temperature})
        factors[temperature] = corrosion.assessHydrogenEmbrittlement()['temperatureFactor']

    assert factors[225.0] > factors[77.0]
    assert factors[225.0] > factors[293.15]
    assert factors[225.0] > factors[500.0]
    assert factors[225.0] == pytest.approx(1.0, abs = 0.01)

def testQuenchSeverityUnits():

    '''
    Grossmann H is tabulated in inverse INCHES and this repository is base SI, so the stored values
    are the tabulated numbers times 39.37. Using the inverse-inch numbers directly gives a Biot
    number two orders of magnitude too small, which reports every quench as perfectly uniform and
    every part as fully hardened.

    This test exists because writing it found exactly that bug.
    '''

    # Agitated water is 1.5 1/in, so 59 1/m
    assert QUENCH_SEVERITY['agitated water'] == pytest.approx(59.0, rel = 0.05), \
        'Agitated water is H = 1.5 1/in = 59 1/m. A value near 1.5 means inverse inches were ' \
        'stored as inverse metres.'
    assert QUENCH_SEVERITY['still water'] == pytest.approx(39.4, rel = 0.05)

    # And the physical consequence: a 25 mm section in agitated water must have a Biot number of
    # order one, not of order 0.01.
    treatment = HeatTreatment()
    treatment.setInputs({'material': '7075', 'condition': 't73', 'sectionThickness': 0.025})
    result = treatment.modelCoolingCurve()

    assert 0.2 < result['biotNumber'] < 5.0, \
        f'A 25 mm section in agitated water should have a Biot number of order one, got ' \
        f'{result["biotNumber"]:.4f}. Two orders of magnitude low means the H units are wrong.'

def testSevenThousandSeriesThroughHardeningLimit():

    '''
    Validated against the reason 7050 exists. 7075 retains nearly all of its strength in a thin
    section and loses a real fraction in a thick one, because the core cannot outrun the nose of
    the C-curve. The published limit is around 75 mm and this reproduces that shape.
    '''

    retained = {}
    for thickness in (0.010, 0.050, 0.150):
        treatment = HeatTreatment()
        treatment.setInputs({'material': '7075', 'condition': 't73',
                             'sectionThickness': thickness, 'quenchant': 'agitated water'})
        treatment.modelCoolingCurve()
        retained[thickness] = treatment.calculateQuenchFactor()['retainedStrengthFraction']

    assert retained[0.010] > 0.95, \
        'A 10 mm section in agitated water should be essentially fully hardened'
    assert retained[0.150] < 0.85, \
        'A 150 mm section cannot be through-hardened in 7075, which is why 7050 exists'
    assert retained[0.010] > retained[0.050] > retained[0.150], \
        'Retained strength must fall monotonically with section thickness'

def testSlowQuenchCostsMoreThanFastQuench():

    '''
    Still air is not a quench. A part solution treated and air cooled has not been heat treated in
    any useful sense, and the model has to say so.
    '''

    results = {}
    for quenchant in ('agitated water', 'still oil', 'still air'):
        treatment = HeatTreatment()
        treatment.setInputs({'material': '7075', 'condition': 't73',
                             'sectionThickness': 0.025, 'quenchant': quenchant})
        treatment.modelCoolingCurve()
        results[quenchant] = treatment.calculateQuenchFactor()['retainedStrengthFraction']

    assert results['agitated water'] > results['still oil'] > results['still air']
    assert results['still air'] < 0.5, \
        'Air cooling a 7xxx alloy leaves it substantially unhardened'

def testLowCarbonGradeResistsSensitization():

    '''
    Validated against the reason the L grades exist. 316L at 0.025 carbon tolerates well over ten
    times the time at the sensitization nose that a 0.08 carbon standard grade would, which is the
    difference between a weld that is at risk and one that is not.
    '''

    treatment = HeatTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed'})
    result = treatment.calculateSensitization(exposureTemperature = 948.0)

    assert result['applicable'] is True
    assert result['carbonAdvantage'] > 10.0, \
        f'316L should tolerate more than ten times the exposure of a 0.08 carbon grade, got ' \
        f'{result["carbonAdvantage"]:.1f}x'
    assert result['timeToSensitize'] > result['standardGradeTime']

def testStabilisedGradeBeatsLowCarbonGrade():

    '''
    321 is titanium stabilised rather than merely low carbon, which pushes the sensitization nose
    out by another order of magnitude. That is why a welded hot gas line is 321 and not 316L.
    '''

    lowCarbon = HeatTreatment()
    lowCarbon.setInputs({'material': '316L', 'condition': 'annealed'})

    stabilised = HeatTreatment()
    stabilised.setInputs({'material': '321', 'condition': 'annealed'})

    lowCarbonTime  = lowCarbon.calculateSensitization()['timeToSensitize']
    stabilisedTime = stabilised.calculateSensitization()['timeToSensitize']

    assert stabilisedTime > lowCarbonTime * 5.0, \
        'Titanium stabilisation must buy substantially more than the low carbon grade alone'

def testTitaniumBottleLeaksBeforeItBursts():

    '''
    Validated against the worked example. A 175 mm Ti-6Al-4V sphere at 30 MPa has a critical flaw
    of about 4.7 mm against a 2.4 mm wall, so a growing crack penetrates and vents rather than
    running unstably. That is a detectable, survivable failure rather than a fragmentation event.
    '''

    damage = DamageTolerance()
    damage.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                      'operatingStress': 552.0e6, 'proofStress': 828.0e6,
                      'wallThickness': 0.00238})

    damage.calculateCriticalFlaw()
    result = damage.checkLeakBeforeBurst()

    assert damage.criticalFlawSize == pytest.approx(0.0047, rel = 0.10), \
        f'Critical flaw should be about 4.7 mm, got {damage.criticalFlawSize * 1000.0:.2f} mm'
    assert result['leakBeforeBurst'] is True

def testStaTitaniumIsTheWrongTradeForAPressureVessel():

    '''
    The toughness trade, quantified. STA titanium buys 25 percent yield strength and gives back
    35 percent of the fracture toughness. Because the critical flaw goes as toughness squared, the
    net effect on a fracture critical vessel is strongly negative even though the strength table
    looks better.
    '''

    annealed = queryMaterial('Ti-6Al-4V', 'annealed', 293.15)
    aged     = queryMaterial('Ti-6Al-4V', 'sta',      293.15)

    assert aged['yieldStrength'] > annealed['yieldStrength'], 'STA must be stronger'

    annealedToughness = min(annealed['fracture']['planeStrainToughness'].values())
    agedToughness     = min(aged['fracture']['planeStrainToughness'].values())

    assert agedToughness < annealedToughness, 'and less tough'

    # At the same stress, critical flaw goes as toughness squared
    flawRatio = (agedToughness / annealedToughness) ** 2
    assert flawRatio < 0.5, \
        f'STA cuts the critical flaw size to {flawRatio:.2f} of the annealed value at equal ' \
        f'stress. On a fracture critical vessel that is a worse trade than the strength gain.'

def testParisCoefficientUnits():

    '''
    The Paris coefficient is quoted for dK in MPa-sqrt(m) in every published da/dN table, while
    this repository is base SI throughout. Feeding Pa-sqrt(m) into a power law with an exponent
    near 3.3 overstates the growth rate by twenty orders of magnitude and returns zero life.

    This test exists because writing it found exactly that bug. A real Ti pressure vessel gets
    thousands of cycles from a penetrant-detectable flaw, not zero.
    '''

    damage = DamageTolerance()
    damage.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                      'operatingStress': 552.0e6, 'proofStress': 828.0e6,
                      'wallThickness': 0.00238, 'designCycles': 500,
                      'inspectionMethod': 'penetrant, standard'})

    result = damage.calculateCrackGrowth()

    assert result['cyclesToFailure'] > 100.0, \
        f'A Ti bottle from a 0.64 mm flaw should survive well over a hundred cycles, got ' \
        f'{result["cyclesToFailure"]:.1f}. A value of zero means the Paris law is being fed ' \
        f'Pa-sqrt(m) where it expects MPa-sqrt(m).'
    assert result['cyclesToFailure'] < 1.0e7, \
        'and not an absurdly large number, which would mean the conversion went the other way'

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

@pytest.mark.skipif(not SCIPY_AVAILABLE, reason = 'needs scipy for the exact route')
def testThreeToleranceFactorRoutesAgree():

    '''
    Three independent implementations of the same quantity: the exact non-central t, the Natrella
    closed form, and the published MMPDS curve fits. They agree to within 2 percent at n = 10 and
    better than 1 percent above n = 20.

    This is a cross-check and not a validation. Three routes agreeing establishes that one formula
    was typed the same way three times, which catches a transcription error and nothing else. What
    makes it useful is that the exact route is separately anchored to the NIST worked example, so
    agreement with it now carries that anchor across to the other two.
    '''

    for basis in ('A', 'B'):
        for sampleSize in (10, 20, 30, 50, 100, 200, 300):
            exact    = toleranceFactorExact(sampleSize, basis)
            natrella = toleranceFactorNatrella(sampleSize, basis)
            mmpds    = toleranceFactorMmpds(sampleSize, basis)

            tolerance = 0.02 if sampleSize < 20 else 0.01

            assert natrella == pytest.approx(exact, rel = tolerance), \
                f'Natrella and exact disagree by more than {tolerance * 100:.0f} % for ' \
                f'{basis}-basis at n = {sampleSize}'
            assert mmpds == pytest.approx(exact, rel = tolerance), \
                f'MMPDS fit and exact disagree by more than {tolerance * 100:.0f} % for ' \
                f'{basis}-basis at n = {sampleSize}'

def testABasisIsAlwaysBelowBBasis(titaniumSample):

    '''
    A-basis is a 99 percent exceedance and B-basis is 90 percent, so A is always the lower number.
    An inversion here would hand out an unconservative allowable labelled as the conservative one.
    '''

    allowables = Allowables()
    allowables.setInputs({'sampleData': titaniumSample})
    values = allowables.calculateBasisValue()

    assert values['A']['value'] < values['B']['value']
    assert values['A']['kFactor'] > values['B']['kFactor']
    assert values['B']['value'] < allowables.mean

def testToleranceFactorFallsMonotonicallyWithSampleSize():

    '''
    More data can only reduce the confidence penalty. A factor that rose anywhere would mean the
    approximation has broken down in that range.
    '''

    for basis in ('A', 'B'):
        factors = [toleranceFactorNatrella(size, basis)
                   for size in (10, 15, 20, 30, 50, 100, 300, 1000)]
        assert all(later < earlier for earlier, later in zip(factors, factors[1:])), \
            f'{basis}-basis tolerance factor must fall monotonically with sample size'

def testKnockdownChainIsOrderedAndCompounds(titaniumSample):

    '''
    The chain has to be reproducible and auditable. Each step records its factor, and the product of
    every factor must equal the ratio of the design value to the mean.
    '''

    allowables = Allowables()
    allowables.setInputs({'sampleData': titaniumSample, 'basis': 'A',
                          'knockdowns': {'EB girth weld': 'weld, electron beam',
                                         'thick section': 'thickness, heavy section'}})
    allowables.calculateBasisValue()
    result = allowables.applyKnockdowns()

    chain = result['chain']
    assert chain[0]['step'] == 'Sample mean (typical)'
    assert chain[-1]['step'] == 'Design value'

    product = 1.0
    for entry in chain[1:-1]:
        product *= entry['factor']

    assert product == pytest.approx(result['totalFactor'], rel = 1.0e-9), \
        'The chain factors must compound to the total, or the audit trail does not describe the ' \
        'number it claims to explain'
    assert allowables.designValue < allowables.toleranceLimit < allowables.mean

def testAnovaBasisIsBelowThePooledBasis(multiBatchSample):

    '''
    Pooling every specimen as though they came from one population understates the spread whenever
    between-lot variation is real. The ANOVA route must therefore produce the lower, more
    defensible number.
    '''

    values, identifiers = multiBatchSample

    allowables = Allowables()
    allowables.setInputs({'sampleData': values, 'batchIdentifiers': identifiers, 'basis': 'B'})
    allowables.calculateBasisValue()

    result = allowables.calculateAnovaBasis()

    assert result['anovaBasisValue'] < result['pooledBasisValue'], \
        'Accounting for between-lot variation must reduce the allowable, not raise it'
    assert result['totalDeviation'] >= result['withinLotDeviation']

def testRequiredSampleSizeIsUnreachableWhenScatterIsTooHigh():

    '''
    With infinite data the tolerance factor converges on the normal quantile, so there is a ceiling
    on the basis ratio set by the coefficient of variation alone. Asking for a ratio above that
    ceiling must report it as unreachable rather than returning an enormous sample size.
    '''

    generator = np.random.default_rng(3)
    allowables = Allowables()
    allowables.setInputs({'sampleData': generator.normal(950.0e6, 150.0e6, 40), 'basis': 'A'})
    allowables.calculateBasisValue()

    result = allowables.calculateRequiredSampleSize(0.95)

    assert result['achievable'] is False
    assert 'Unreachable' in result['note']
    assert result['limitingRatio'] < 0.95

def testAshbyIndexOrderingReversesWithLoadingMode():

    '''
    The reason the index matters rather than raw strength: the ordering genuinely reverses between
    loading modes.

    Titanium beats 7075-T6 on sigma/rho for a tension tie. On a plate in bending the index is
    sigma^(1/2)/rho, and the half power flattens titanium's strength advantage while leaving its
    64 percent density penalty untouched. The aluminium wins by 22 percent.

    A trade study run on strength to weight alone would pick titanium for both, and be wrong for
    one of them.
    '''

    titanium  = queryMaterial('Ti-6Al-4V', 'annealed', 293.15)
    aluminium = queryMaterial('7075', 't6', 293.15)

    tieTitanium  = titanium['ultimateStrength'] / titanium['density']
    tieAluminium = aluminium['ultimateStrength'] / aluminium['density']

    plateTitanium  = titanium['ultimateStrength'] ** 0.5 / titanium['density']
    plateAluminium = aluminium['ultimateStrength'] ** 0.5 / aluminium['density']

    assert tieTitanium > tieAluminium, \
        'Titanium wins a tension tie on strength to weight'
    assert plateAluminium > plateTitanium, \
        'and loses a plate in bending, because the half power flattens the strength advantage ' \
        'while the density penalty stays. This is why selecting on strength alone gets it wrong.'
    assert plateAluminium / plateTitanium > 1.15, \
        'and the reversal is not marginal'

def testHalfPowerCollapsesTheTitaniumAdvantage():

    '''
    The same effect against 6061, where the ordering does not quite reverse but the margin
    collapses from 87 percent to under 7 percent. At that point the decision stops being about
    the index at all and moves to cost, lead time and weldability, where aluminium wins easily.
    '''

    titanium  = queryMaterial('Ti-6Al-4V', 'annealed', 293.15)
    aluminium = queryMaterial('6061', 't6', 293.15)

    tieMargin   = (titanium['ultimateStrength'] / titanium['density']) / \
                  (aluminium['ultimateStrength'] / aluminium['density'])
    plateMargin = (titanium['ultimateStrength'] ** 0.5 / titanium['density']) / \
                  (aluminium['ultimateStrength'] ** 0.5 / aluminium['density'])

    assert tieMargin > 1.8, 'Titanium wins a tie against 6061 by a wide margin'
    assert plateMargin < 1.10, \
        f'and only by {(plateMargin - 1.0) * 100.0:.1f} percent on a bending plate, which is ' \
        f'inside the noise of any real design'

def testSelectorRejectsTitaniumFromAnOxidiserSystem():

    '''
    The compatibility screen has to fire during selection, not after. A trade study that ranks
    titanium first for a LOX vessel has failed at the first hurdle.
    '''

    selector = MaterialSelector()
    selector.setInputs({'requirements': {'fluids': ['LOX'], 'serviceTemperature': 90.0},
                        'loadingMode': 'pressure vessel'})
    result = selector.screen()

    titaniumEntries = [label for label in result['rejected'] if 'TI-6AL-4V' in label.upper()]
    assert titaniumEntries, 'Titanium must be rejected outright from a LOX system'

    for label in titaniumEntries:
        assert any('PROHIBITED' in reason for reason in result['rejected'][label])

    passedNames = [name for name, _ in result['passed']]
    assert not any('TI-6AL-4V' == name for name in passedNames)

def testSelectorRejectionsAlwaysCarryAReason():

    '''
    A screen that returns survivors and no explanation cannot answer the question a design review
    always asks. Every rejection must name the requirement it failed.
    '''

    selector = MaterialSelector()
    selector.setInputs({'requirements': {'minimumUltimateStrength': 800.0e6,
                                         'serviceTemperature': 293.15},
                        'loadingMode': 'tie'})
    result = selector.screen()

    assert result['rejected'], 'This screen should reject most of the database'
    for label, reasons in result['rejected'].items():
        assert reasons, f'{label} was rejected with no reason recorded'
        assert all(isinstance(reason, str) and reason for reason in reasons)

def testGalvanicPenetrationScalesWithAreaRatio():

    '''
    The area ratio effect, which is the rule people get backwards. A small anode against a large
    cathode concentrates the whole couple current onto a small area, so the penetration rate scales
    directly with the ratio. This is why a steel fastener in an aluminium plate is fine and an
    aluminium fastener in a steel plate is destroyed.
    '''

    rates = {}
    for anodeArea, label in ((0.001, 'small anode'), (0.100, 'large anode')):
        corrosion = CorrosionAssessment()
        corrosion.setInputs({'anodeMaterial': '6061', 'anodeCondition': 't6',
                             'cathodeMaterial': '316L', 'cathodeCondition': 'annealed',
                             'anodeArea': anodeArea, 'cathodeArea': 0.010,
                             'environment': 'launch site marine'})
        rates[label] = corrosion.calculateGalvanicCouple()['penetrationRate']

    assert rates['small anode'] > rates['large anode'] * 50.0, \
        'A hundred times smaller anode must give a hundred times the penetration rate'

def testCoatTheCathodeRuleIsEnforced():

    '''
    Coating only the anode concentrates the entire couple current onto the inevitable holidays in
    the coating and accelerates the failure it was meant to prevent. The recommendation has to say
    so explicitly rather than leaving it to the reader.
    '''

    corrosion = CorrosionAssessment()
    corrosion.setInputs({'anodeMaterial': '6061', 'anodeCondition': 't6',
                         'cathodeMaterial': 'Ti-6Al-4V', 'cathodeCondition': 'annealed',
                         'environment': 'launch site marine'})
    recommendations = corrosion.recommendProtection()

    joined = ' '.join(recommendations).lower()
    assert 'cathode' in joined
    assert 'never coat only the anode' in joined, \
        'The rule has to be stated, because getting it backwards is worse than doing nothing'

def testAcceptableCoupleReturnsNoMitigations():

    '''
    A couple within the permitted potential difference should not generate a list of fixes for a
    problem it does not have.
    '''

    corrosion = CorrosionAssessment()
    corrosion.setInputs({'anodeMaterial': '304L', 'anodeCondition': 'annealed',
                         'cathodeMaterial': '316L', 'cathodeCondition': 'annealed',
                         'environment': 'launch site marine'})
    result = corrosion.calculateGalvanicCouple()

    assert result['acceptable'] is True
    assert len(corrosion.recommendProtection()) == 1

def testStainlessToNickelExceedsTheMarineLimit():

    '''
    A result worth having visible, because it surprises people. 316L against Inconel 625 is a
    0.20 V couple, which passes the 0.25 V limit for a normal environment and FAILS the 0.15 V
    limit for a coastal launch site.

    A 316L manifold bolted to a 625 bellows is a common and unremarkable-looking joint, and at a
    coastal site it needs isolation.
    '''

    marine = CorrosionAssessment()
    marine.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed',
                      'cathodeMaterial': 'Inconel 625', 'cathodeCondition': 'annealed',
                      'environment': 'launch site marine'})
    marineResult = marine.calculateGalvanicCouple()

    normal = CorrosionAssessment()
    normal.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed',
                      'cathodeMaterial': 'Inconel 625', 'cathodeCondition': 'annealed',
                      'environment': 'normal'})
    normalResult = normal.calculateGalvanicCouple()

    assert marineResult['potentialDifference'] == pytest.approx(0.20, abs = 0.01)
    assert marineResult['acceptable'] is False, \
        'A 0.20 V couple exceeds the 0.15 V limit for a coastal launch site'
    assert normalResult['acceptable'] is True, \
        'and passes the 0.25 V limit for a sheltered environment. The environment is what decides.'

def testLarsonMillerEquivalenceIsReversible():

    '''
    Two aging cycles with the same parameter are equivalent, and converting from one to the other
    and back must return the original. A one-way conversion that does not round trip has a sign or
    a base error in the logarithm.
    '''

    treatment = HeatTreatment()
    treatment.setInputs({'material': '7075', 'condition': 't73',
                         'agingTemperature': 393.0, 'agingTime': 86400.0})

    forward = treatment.calculateAgingResponse(comparisonTemperature = 413.0)
    equivalentTime = forward['equivalentTime']

    reverse = HeatTreatment()
    reverse.setInputs({'material': '7075', 'condition': 't73',
                       'agingTemperature': 413.0, 'agingTime': equivalentTime})
    back = reverse.calculateAgingResponse(comparisonTemperature = 393.0)

    assert back['equivalentTime'] == pytest.approx(86400.0, rel = 0.01), \
        'The Larson-Miller conversion must round trip'
    assert equivalentTime < 86400.0, \
        'A hotter age reaches the same parameter in less time'

def testAsymmetricMachiningProducesBow():

    '''
    A quenched plate carries balanced residual stress. Machine one side away and the balance is
    destroyed, the remaining section carries an unbalanced moment, and the part bows. Machining
    symmetrically removes the effect entirely, which is the practical fix.
    '''

    asymmetric = HeatTreatment()
    asymmetric.setInputs({'material': '7075', 'condition': 't73', 'sectionThickness': 0.050,
                          'partLength': 0.500, 'machinedFraction': 0.50})
    asymmetric.modelCoolingCurve()
    asymmetricResult = asymmetric.calculateDistortion()

    symmetric = HeatTreatment()
    symmetric.setInputs({'material': '7075', 'condition': 't73', 'sectionThickness': 0.050,
                         'partLength': 0.500, 'machinedFraction': 0.0})
    symmetric.modelCoolingCurve()
    symmetricResult = symmetric.calculateDistortion()

    assert asymmetricResult['predictedBow'] > symmetricResult['predictedBow']
    assert symmetricResult['predictedBow'] == pytest.approx(0.0, abs = 1.0e-12), \
        'Removing nothing must release nothing'
    assert asymmetricResult['residualStress'] > 0.0

def testResidualStressProfileIsSelfEquilibrating():

    '''
    A quenched plate sits flat, which means the residual stress through its thickness has zero net
    force and zero net moment. Any profile that does not satisfy both would have the plate bowed
    before a cutter touched it.

    This test exists because the first implementation treated the removed layer as carrying a
    uniform stress and multiplied by an arm length, which ignores that the layer contains both the
    compressive surface and part of the tensile core. That overstated the released moment by a
    factor of four.
    '''

    treatment = HeatTreatment()
    treatment.setInputs({'material': '7075', 'condition': 't73', 'sectionThickness': 0.050,
                         'partLength': 0.500, 'partWidth': 0.200, 'machinedFraction': 0.001})
    treatment.modelCoolingCurve()
    result = treatment.calculateDistortion()

    # Removing a negligible sliver leaves an essentially intact section, which must still be
    # balanced: the net force and moment both have to be near zero.
    fullSectionForce = result['unbalancedForce']
    sectionArea      = treatment.sectionThickness * treatment.partWidth

    assert abs(fullSectionForce) < 0.02 * abs(result['surfaceStress']) * sectionArea, \
        'The intact section must carry essentially zero net force, or the plate would not sit flat'

    # And the mid-plane stress must oppose the surface stress, which is what balance requires.
    assert result['midPlaneStress'] * result['surfaceStress'] < 0.0, \
        'Surface and mid-plane residual stress must have opposite signs'

def testDistortionScalesWithPartLengthSquared():

    '''
    Bow from a released curvature goes as L^2 / 8, so doubling the part length quadruples the bow.
    That is why a long thin machined part distorts and a short stubby one does not, and it is worth
    a test because a linear scaling would look plausible in a single result.
    '''

    bows = {}
    for length in (0.250, 0.500):
        treatment = HeatTreatment()
        treatment.setInputs({'material': '7075', 'condition': 't73', 'sectionThickness': 0.050,
                             'partLength': length, 'partWidth': 0.200, 'machinedFraction': 0.40})
        treatment.modelCoolingCurve()
        bows[length] = treatment.calculateDistortion()['predictedBow']

    assert bows[0.500] / bows[0.250] == pytest.approx(4.0, rel = 0.01), \
        'Bow must scale with the square of the part length'

def testProcessRoutesAllCarryConsistentDefinitions():

    '''
    Structural integrity of the route table. Every route needs a buy-to-fly at or above one (you
    cannot finish with more material than you started), a positive cost multiplier, and knockdown
    keys that resolve in the Allowables table.
    '''

    from Allowables import STANDARD_KNOCKDOWNS as knockdownTable

    for name, route in PROCESS_ROUTES.items():
        assert route['buyToFly'] >= 1.0, \
            f'{name} has a buy-to-fly below 1.0, which would mean creating material'
        assert route['costMultiplier'] > 0.0
        assert route['minimumWall'] > 0.0
        assert route['note'], f'{name} has no explanatory note'
        for knockdownKey in route['knockdowns']:
            assert knockdownKey in knockdownTable, \
                f'{name} names knockdown \'{knockdownKey}\' which is not in ' \
                f'Allowables.STANDARD_KNOCKDOWNS'

def testAdditiveHasTheBestBuyToFlyAndMachiningTheWorst():

    '''
    The defining economic property of additive manufacturing, and the reason it wins on expensive
    alloys despite a high process cost. Machining from plate throws away most of the stock.
    '''

    additive  = PROCESS_ROUTES['lpbf as-built']['buyToFly']
    machined  = PROCESS_ROUTES['machined from plate']['buyToFly']
    forged    = PROCESS_ROUTES['closed die forged and machined']['buyToFly']

    assert additive < forged < machined
    assert machined / additive > 5.0

def testCastingFactorDominatesTheRouteTrade():

    '''
    The finding that makes ProcessComparison worth running. An un-qualified casting carries a
    factor of 2.0, which halves the allowable and doubles the material needed to carry the same
    load. No alloy substitution recovers that, and qualifying the process is usually cheaper.
    '''

    # The tolerance has to be loose enough for a sand casting to be a candidate at all. IT14 holds
    # 870 um on 100 mm, so a 500 um requirement screens it out on dimensions before the allowable
    # ever enters the argument.
    comparison = ProcessComparison()
    comparison.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'finishedMass': 1.0,
                          'minimumWallThickness': 0.006, 'characteristicSize': 0.30,
                          'requiredTolerance': 1.00e-3})
    routes = comparison.compareRoutes()

    byName = {entry['route']: entry for entry in routes}

    assert 'sand cast' in byName, 'A 6 mm wall, 300 mm part at 1 mm tolerance is sand castable'
    assert byName['sand cast']['allowableFactor'] == pytest.approx(0.5, rel = 0.01)
    assert byName['sand cast']['massPenalty'] == pytest.approx(2.0, rel = 0.01), \
        'A factor of 2.0 casting knockdown means twice the material for the same load'

def testInfeasibleRoutesAreRejectedNotRanked():

    '''
    A route that cannot hold the wall thickness is not a cheap option, it is not an option. It has
    to leave the comparison entirely rather than appearing at the top of a cost ranking.
    '''

    comparison = ProcessComparison()
    comparison.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'finishedMass': 0.2,
                          'minimumWallThickness': 0.0005, 'characteristicSize': 0.10,
                          'requiredTolerance': 0.10e-3})
    result = comparison.screenRoutes()

    assert 'sand cast' in result['infeasible'], \
        'Sand casting cannot hold a 0.5 mm wall and must be screened out'
    assert 'sand cast' not in result['feasible']
    assert result['infeasible']['sand cast'], 'and it must say why'

def testEveryClassGeneratesAReport():

    '''
    A smoke test across all six classes. generateReport touches nearly every field, so a formatting
    error or a missing value surfaces here rather than in the worked example.
    '''

    generator  = np.random.default_rng(11)

    allowables = Allowables()
    allowables.setInputs({'sampleData': generator.normal(950.0e6, 30.0e6, 30)})
    assert 'DESIGN ALLOWABLE REPORT' in allowables.generateReport()

    selector = MaterialSelector()
    selector.setInputs({'requirements': {'serviceTemperature': 293.15, 'fluids': ['GHE']},
                        'loadingMode': 'pressure vessel'})
    assert 'MATERIAL SELECTION' in selector.generateReport()

    damage = DamageTolerance()
    damage.setInputs({'material': 'Ti-6Al-4V', 'operatingStress': 552.0e6,
                      'proofStress': 828.0e6, 'wallThickness': 0.00238})
    damage.calculateCriticalFlaw()
    damage.checkLeakBeforeBurst()
    assert 'DAMAGE TOLERANCE' in damage.generateReport()

    corrosion = CorrosionAssessment()
    corrosion.setInputs({'anodeMaterial': '6061', 'anodeCondition': 't6',
                         'cathodeMaterial': '316L', 'anodeArea': 0.002, 'cathodeArea': 0.010})
    assert 'CORROSION ASSESSMENT' in corrosion.generateReport()

    treatment = HeatTreatment()
    treatment.setInputs({'material': '7075', 'condition': 't73'})
    treatment.modelCoolingCurve()
    treatment.calculateQuenchFactor()
    treatment.calculateDistortion()
    assert 'HEAT TREATMENT' in treatment.generateReport()

    comparison = ProcessComparison()
    comparison.setInputs({'material': 'Ti-6Al-4V', 'finishedMass': 1.0,
                          'minimumWallThickness': 0.003, 'characteristicSize': 0.20,
                          'requiredTolerance': 0.30e-3})
    assert 'PROCESS ROUTE COMPARISON' in comparison.generateReport()


# ------------------------------------------------------------------------------------------------ #
# -- What the assumptions behind a basis value are worth -- #
# ------------------------------------------------------------------------------------------------ #

def testPoolingLotsIsUnconservativeWhenBetweenLotVariationIsReal(multiBatchSample):

    '''
    A basis value rests on two things the tolerance factor cannot see, and this is the second of
    them. Pooling every specimen as one population counts lot scatter as if it were specimen
    scatter, which understates the spread and raises the number.

    The direction is structural: total variance is the sum of the two components, so a pooled
    estimate that ignores the split can only be optimistic.
    '''

    values, identifiers = multiBatchSample

    allowables = Allowables()
    allowables.setInputs({'sampleData': values, 'batchIdentifiers': identifiers, 'basis': 'B'})

    comparison = allowables.compareBasisRoutes()

    assert comparison['lotCount'] == 6
    assert comparison['poolingCost'] > 0.0, 'pooling has to be the higher of the two'
    assert 0.0 < comparison['poolingCost'] < 0.10

    assert comparison['anovaValue'] < comparison['normalTheoryValue']

def testTheNormalityAssumptionIsBoundedRatherThanNamed(multiBatchSample):

    '''
    The first assumption. The order statistic route uses no distribution at all, so the difference
    between it and the normal-theory value bounds what normality is worth on this sample.

    **It is not an error measurement.** The distribution-free route pays for its generality: it
    needs 29 specimens before it can use its lowest observation for B-basis, so on a small sample
    it is low for reasons unconnected to normality.
    '''

    values, identifiers = multiBatchSample

    allowables = Allowables()
    allowables.setInputs({'sampleData': values, 'batchIdentifiers': identifiers, 'basis': 'B'})

    comparison = allowables.compareBasisRoutes()

    assert comparison['distributionFreeValue'] is not None
    assert np.isfinite(comparison['normalityCost'])
    assert abs(comparison['normalityCost']) < 0.10

    # The wording has to carry the caveat, because the number alone invites the wrong reading.
    assert any('bounds the assumption' in finding for finding in comparison['findings'])

def testASampleTooSmallForADistributionFreeBoundSaysSo():

    '''
    B-basis needs 29 specimens before the lowest observation is a 95 per cent bound at all, and
    A-basis needs 299. Below that the normality assumption is doing all the work, and the honest
    output is to say so rather than to report a comparison that cannot be made.
    '''

    generator = np.random.default_rng(3)

    allowables = Allowables()
    allowables.setInputs({'sampleData': generator.normal(950.0e6, 30.0e6, 15), 'basis': 'B'})

    comparison = allowables.compareBasisRoutes()

    assert comparison['distributionFreeValue'] is None
    assert not np.isfinite(comparison['normalityCost'])

    assert any('doing all of the work' in finding for finding in comparison['findings'])

def testASingleLotSampleCannotCheckPoolingAtAll():

    '''
    The quieter of the two gaps. A sample from one lot supports a basis value for that lot and says
    nothing about the next one, and no arithmetic on it can reveal that.
    '''

    generator = np.random.default_rng(5)

    allowables = Allowables()
    allowables.setInputs({'sampleData': generator.normal(950.0e6, 30.0e6, 40), 'basis': 'B'})

    comparison = allowables.compareBasisRoutes()

    assert comparison['lotCount'] == 0
    assert not np.isfinite(comparison['poolingCost'])

    assert any('cannot be checked at all' in finding for finding in comparison['findings'])

def testASkewedSampleIsFlaggedRatherThanFitted():

    '''
    Anderson-Darling is already run; this asserts the comparison surfaces it. A rejected normal fit
    on metallic strength data usually means the sample mixes product forms, heats or temperatures,
    and the fix is to split the sample rather than to change the distribution.
    '''

    generator = np.random.default_rng(9)

    # Two populations 120 MPa apart, which is what mixing two tempers looks like.
    mixed = np.concatenate([generator.normal(950.0e6, 20.0e6, 30),
                            generator.normal(830.0e6, 20.0e6, 30)])

    allowables = Allowables()
    allowables.setInputs({'sampleData': mixed, 'basis': 'B'})

    comparison = allowables.compareBasisRoutes()

    assert comparison['normalityRejected']
    assert any('mixes product forms' in finding for finding in comparison['findings'])

def testTheRegisterRecordsThisAsACrossCheckAndNotAValidation():

    '''
    The distinction this repository exists to keep. Two routes disagreeing by one per cent
    establishes what an assumption is worth and not that either is right, and the register has to
    say so where somebody reading the number will see it.
    '''

    note = TOLERANCE_FACTORS['NIST-SEMATECH-1.3.5.2']['assumptionNote']

    assert 'internal cross-check and not a validation' in note
    assert 'knockdown chain remains unbounded' in note
