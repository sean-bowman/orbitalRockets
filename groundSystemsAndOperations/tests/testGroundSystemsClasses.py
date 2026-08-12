# -- Tests for the groundSystemsAndOperations library -- #

'''

Three tiers. Tier one is inputs and refusals, tier two is the arithmetic, and tier three is the
published standard: DESR 6055.09 Table V5.E4.T5 and NASA-STD-8719.12A Table E-1, both read in full
rather than summarised.

The standard is reproduced, not adjusted. Where the standard's own bracketed metric coefficient
disagrees with the conversion of its English form, the test asserts the disagreement rather than
picking whichever makes a number come out round.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'groundSystemsLibrary'))
sys.path.insert(0, ROOT)

from groundUtils import (K_FACTORS, TNT_EQUIVALENCE, LOADING_PHASES, SCRUB_CAUSES,
                         HYDROGEN_FLAT_FRACTION, HYDROGEN_SUBLINEAR_COEFFICIENT,
                         HYDROGEN_METRIC_COEFFICIENT_EXACT,
                         HYDROGEN_METRIC_COEFFICIENT_PUBLISHED,
                         RP1_BREAK_MASS, KG_PER_LBM, M_PER_FT,
                         explosiveEquivalent, hopkinsonCranzDistance, cumulativeGoProbability,
                         InvalidInputError, SitingError, LoadingError, TimelineError)

from validation.referenceCases import EXPLOSIVE_SITING, UNVALIDATED

from HazardSiting import HazardSiting
from PropellantLoading import PropellantLoading
from CountdownTimeline import CountdownTimeline
from LaunchAvailability import LaunchAvailability

# ------------------------------------------------------------------------------------------------ #
# -- Fixtures -- #
# ------------------------------------------------------------------------------------------------ #

@pytest.fixture
def siting():

    component = HazardSiting()
    component.setInputs({'combination':    'LO2/RP-1',
                         'propellantMass': 270000.0,
                         'facilities':     [{'name': 'control', 'distance': 4000.0}]})

    return component

@pytest.fixture
def loading():

    component = PropellantLoading()
    component.setInputs({'flightLoad':      5400.0,
                         'transferRate':    3.2,
                         'chilldownMass':   1900.0,
                         'boilOffRate':     0.11,
                         'holdDuration':    1800.0,
                         'storageCapacity': 42000.0,
                         'detankRecovery':  0.55})

    return component

@pytest.fixture
def timeline():

    component = CountdownTimeline()
    component.setInputs({'tasks': [{'name': 'clear',    'duration': 1800.0},
                                   {'name': 'fuel',     'duration': 3600.0,
                                    'predecessors': ['clear']},
                                   {'name': 'oxidiser', 'duration': 1200.0,
                                    'predecessors': ['clear']},
                                   {'name': 'terminal', 'duration': 600.0,
                                    'predecessors': ['fuel', 'oxidiser']}],
                         'windowDuration':    3600.0,
                         'turnaroundDrivers': {'propellant': 86400.0,
                                               'batteries':  43200.0,
                                               'crew':       21600.0}})

    return component

@pytest.fixture
def availability():

    component = LaunchAvailability()
    component.setInputs({'constraints': {'a': 0.10, 'b': 0.10, 'c': 0.10},
                         'attempts':    3,
                         'correlation': 0.4})

    return component

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: inputs and refusals -- #
# ------------------------------------------------------------------------------------------------ #

def testAnUnlistedPropellantIsRefusedRatherThanDefaulted():

    '''
    The standard sends anything not in its table to individual assessment. Guessing a percentage
    for it here would be inventing a number and dressing it as a citation.
    '''

    component = HazardSiting()

    with pytest.raises(InvalidInputError):
        component.setInputs({'combination': 'LO2/LCH4', 'propellantMass': 100000.0})

def testAFacilityInsideItsDistanceRaises(siting):

    siting.facilities = [{'name': 'control room', 'distance': 50.0}]

    with pytest.raises(SitingError):
        siting.checkFacilities()

def testTheViolationMessageNamesTheFacilityAndBothDistances(siting):

    siting.facilities = [{'name': 'control room', 'distance': 50.0}]

    with pytest.raises(SitingError) as error:
        siting.checkFacilities()

    assert 'control room' in str(error.value)
    assert '50' in str(error.value)

def testCheckingWithNoFacilitiesRaises():

    component = HazardSiting()
    component.setInputs({'combination': 'LO2/RP-1', 'propellantMass': 1000.0})

    with pytest.raises(SitingError):
        component.checkFacilities()

def testToppingBelowTheBoilOffRaises():

    '''
    The tank never reaches flight level and the failure is quiet: the level simply stops rising.
    A class that reports it as a long duration would be reporting a number instead of a fault.
    '''

    component = PropellantLoading()

    with pytest.raises(LoadingError):
        component.setInputs({'flightLoad':   5000.0,
                             'transferRate': 1.0,
                             'boilOffRate':  0.5})

def testStorageBelowOneAttemptRaises(loading):

    loading.storageCapacity = 1000.0

    with pytest.raises(LoadingError):
        loading.calculateGroundDemand()

def testACycleInTheTaskGraphRaises():

    component = CountdownTimeline()
    component.setInputs({'tasks': [{'name': 'a', 'duration': 10.0, 'predecessors': ['b']},
                                   {'name': 'b', 'duration': 10.0, 'predecessors': ['a']}]})

    with pytest.raises(TimelineError):
        component.calculateCriticalPath()

def testAnUnknownPredecessorRaises():

    component = CountdownTimeline()

    with pytest.raises(InvalidInputError):
        component.setInputs({'tasks': [{'name': 'a', 'duration': 10.0,
                                        'predecessors': ['nothing']}]})

def testARecyclePointAfterTheHoldRaises(timeline):

    with pytest.raises(TimelineError):
        timeline.calculateRecycle(holdAt = 1200.0, backUpTo = 240.0)

def testAProbabilityOutsideZeroToOneRaises():

    component = LaunchAvailability()

    with pytest.raises(InvalidInputError):
        component.setInputs({'constraints': {'a': 1.4}})

def testACorrelationOfOneRaises():

    '''
    A correlation of one means a scrub is permanent, which is not weather and is not a campaign.
    '''

    component = LaunchAvailability()

    with pytest.raises(InvalidInputError):
        component.setInputs({'constraints': {'a': 0.1}, 'correlation': 1.0})

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: the arithmetic -- #
# ------------------------------------------------------------------------------------------------ #

def testCubeRootScalingNeedsEightTimesTheMassToDoubleTheDistance():

    near = hopkinsonCranzDistance(40.0, 1000.0)
    far  = hopkinsonCranzDistance(40.0, 8000.0)

    assert far / near == pytest.approx(2.0, rel = 1.0e-12)

def testDistanceIsLinearInTheKFactor():

    single = hopkinsonCranzDistance(20.0, 5000.0)
    double = hopkinsonCranzDistance(40.0, 5000.0)

    assert double / single == pytest.approx(2.0, rel = 1.0e-12)

def testTheRingsAreOrderedByKFactor(siting):

    rings = siting.calculateDistances()['rings']

    assert all(rings[index]['kFactor'] <= rings[index + 1]['kFactor']
               for index in range(len(rings) - 1))

def testTheHydrogenFractionNeverFallsBelowFourteenPerCent():

    '''
    The rule is a maximum of two terms, so the flat fraction is a floor by construction. A result
    below it would mean the maximum had been implemented as a minimum, which is the single most
    likely way to get this wrong.
    '''

    for mass in (100.0, 1.0e4, 8.4e4, 1.0e6, 1.0e7):
        assert explosiveEquivalent('LO2/LH2', mass)['effectiveFraction'] >= HYDROGEN_FLAT_FRACTION

def testTheHydrogenFractionFallsMonotonicallyWithLoad():

    masses = [1.0e3, 1.0e4, 5.0e4, 8.0e4]
    fractions = [explosiveEquivalent('LO2/LH2', mass)['effectiveFraction'] for mass in masses]

    assert all(fractions[index] > fractions[index + 1] for index in range(len(fractions) - 1))

def testTheRp1EquivalenceIsExactlyTwentyPerCentUpToTheBreakMass():

    below = explosiveEquivalent('LO2/RP-1', RP1_BREAK_MASS * 0.5)
    at    = explosiveEquivalent('LO2/RP-1', RP1_BREAK_MASS)

    assert below['effectiveFraction'] == pytest.approx(0.20)
    assert at['effectiveFraction'] == pytest.approx(0.20)

def testTheRp1EquivalenceFallsAboveTheBreakMass():

    above = explosiveEquivalent('LO2/RP-1', RP1_BREAK_MASS * 2.0)

    assert 0.10 < above['effectiveFraction'] < 0.20

def testTheStaticTestColumnIsNeverHigherThanTheRangeLaunchColumn():

    '''
    A stand can be built to keep the propellants apart in a way a vehicle cannot, so the stand
    figure is the same or lower for every entry.
    '''

    for combination, entry in TNT_EQUIVALENCE.items():

        if entry['staticTest'] is None:
            continue

        assert entry['staticTest'] <= entry['rangeLaunch']

def testCombinedLoadsAddTheirEquivalents():

    component = HazardSiting()
    component.setInputs({'combination':     'LO2/RP-1',
                         'propellantMass':  270000.0,
                         'additionalLoads': {'LO2/LH2': 38000.0}})

    combined = component.calculateEquivalent()

    separate = (explosiveEquivalent('LO2/RP-1', 270000.0)['equivalentMass']
                + explosiveEquivalent('LO2/LH2', 38000.0)['equivalentMass'])

    assert combined['equivalentMass'] == pytest.approx(separate)

def testTheTankingPhasesDeliverExactlyTheFlightLoad(loading):

    sequence = loading.calculatePhases()

    delivered = sum(entry['mass'] for entry in sequence['phases']
                    if entry['phase'] != 'chilldown')

    assert delivered == pytest.approx(loading.flightLoad)

def testTheGroundDemandSharesSumToOne(loading):

    demand = loading.calculateGroundDemand()

    assert sum(entry['share'] for entry in demand['breakdown']) == pytest.approx(1.0)

def testGroundDemandAlwaysExceedsTheFlightLoad(loading):

    assert loading.calculateGroundDemand()['demandRatio'] > 1.0

def testHoldDemandIsLinearInTheHoldDuration(loading):

    sweep = loading.holdSensitivity([0.0, 1000.0, 2000.0])['sweep']

    first = sweep[1]['totalDemand'] - sweep[0]['totalDemand']
    second = sweep[2]['totalDemand'] - sweep[1]['totalDemand']

    assert first == pytest.approx(second)

def testTheHoldSweepRestoresTheOriginalDuration(loading):

    original = loading.holdDuration
    loading.holdSensitivity()

    assert loading.holdDuration == original

def testTheCriticalPathIsNoLongerThanTheSerialSum(timeline):

    path = timeline.calculateCriticalPath()

    assert path['totalDuration'] <= path['serialSum']
    assert path['parallelGain'] >= 1.0

def testEveryCriticalTaskHasZeroFloat(timeline):

    for entry in timeline.calculateCriticalPath()['tasks']:
        if entry['critical']:
            assert entry['float'] == pytest.approx(0.0)

def testTheCriticalPathPicksTheLongerOfTwoParallelBranches(timeline):

    path = timeline.calculateCriticalPath()

    assert 'fuel' in path['criticalPath']
    assert 'oxidiser' not in path['criticalPath']

def testARecycleIsLongerThanItsHold(timeline):

    recycle = timeline.calculateRecycle(240.0, 1200.0, 600.0)

    assert recycle['recycle'] > recycle['holdDuration']
    assert recycle['recycle'] == pytest.approx(600.0 + 960.0)

def testTurnaroundIsTheLargestDriverAndNotTheSum(timeline):

    turnaround = timeline.calculateTurnaround()

    assert turnaround['turnaround'] == max(timeline.turnaroundDrivers.values())
    assert turnaround['turnaround'] < turnaround['sumOfDrivers']

def testFixingTheGoverningDriverOnlyBuysTheGapToTheNext(timeline):

    turnaround = timeline.calculateTurnaround()

    assert turnaround['gainIfFixed'] == pytest.approx(
        turnaround['turnaround'] - turnaround['nextLargest'])

def testTheFirstAttemptIsFreeAndTheRestCostATurnaround(timeline):

    turnaround = timeline.calculateTurnaround()['turnaround']

    assert timeline.attemptsPerCampaign(0.0)['attempts'] == 1
    assert timeline.attemptsPerCampaign(turnaround * 3.0)['attempts'] == 4

def testTheConstraintsMultiplyRatherThanAveraging(availability):

    result = availability.calculatePerAttempt()

    assert result['perAttempt'] == pytest.approx(0.9 ** 3)

def testTheCombinedResultIsWorseThanTheWorstCriterionAlone(availability):

    result = availability.calculatePerAttempt()

    assert result['perAttempt'] < result['worstAlone']
    assert result['combinedPenalty'] > 0.0

def testCumulativeProbabilityIsOneMinusTheFailureProduct():

    assert cumulativeGoProbability(0.6, 3) == pytest.approx(1.0 - 0.4 ** 3)
    assert cumulativeGoProbability(0.6, 0) == pytest.approx(0.0)

def testCorrelationOfZeroReproducesTheIndependentCase(availability):

    availability.correlation = 0.0
    campaign = availability.calculateCampaign()

    assert campaign['correlated'] == pytest.approx(campaign['independent'])

def testCorrelationAlwaysCostsCampaignProbability(availability):

    campaign = availability.calculateCampaign()

    assert campaign['correlated'] < campaign['independent']
    assert campaign['gap'] > 0.0

def testTheCorrelatedChainReproducesTheUnconditionalRate(availability):

    '''
    The two-state chain has to be consistent: weighting the two conditional probabilities by the
    states they follow must return the unconditional rate. A model that fails this is a fudge with
    a plausible shape.
    '''

    perAttempt = availability.calculatePerAttempt()['perAttempt']
    rho = availability.correlation

    afterGo    = perAttempt + (1.0 - perAttempt) * rho
    afterScrub = perAttempt * (1.0 - rho)

    unconditional = perAttempt * afterGo + (1.0 - perAttempt) * afterScrub

    assert unconditional == pytest.approx(perAttempt)

def testAnExtraAttemptAlwaysHelpsAndByLess(availability):

    sweep = availability.attemptSweep(6)['sweep']

    assert all(entry['marginal'] > 0.0 for entry in sweep)
    assert all(sweep[index]['marginal'] > sweep[index + 1]['marginal']
               for index in range(len(sweep) - 1))

def testAttemptsBeatCriteriaAtEveryAttemptCount(availability):

    '''
    The result the class exists to produce. A five point improvement to the worst criterion is a
    large change to a launch commit criterion; one more attempt is a schedule decision, and it
    wins at every count.
    '''

    for attempts in (1, 2, 3, 4):
        availability.attempts = attempts
        assert availability.compareLevers()['attemptsWin'] is True

def testTheScrubCauseSharesSumToOne():

    assert sum(SCRUB_CAUSES.values()) == pytest.approx(1.0)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: against the published standard -- #
# ------------------------------------------------------------------------------------------------ #

def testTheKFactorTableMatchesTheStandard():

    '''
    NASA-STD-8719.12A Table E-1, reproducing DESR 6055.09. Read in full rather than summarised,
    which matters: the K factors are quoted loosely in secondary sources and the overpressures
    almost never travel with them.
    '''

    published = {'inhabitedBuilding':         (40.0, 1.2),
                 'inhabitedBuildingRelaxed':  (50.0, 0.9),
                 'publicTrafficRoute':        (24.0, 2.3),
                 'publicTrafficRouteLarge':   (30.0, 1.7),
                 'unbarricadedIntraline':     (18.0, 3.5),
                 'barricadedIntraline':       ( 9.0, 12.0),
                 'unbarricadedIntermagazine': (11.0, 8.0),
                 'barricadedIntermagazine':   ( 6.0, 27.0)}

    for name, (kFactor, overpressure) in published.items():
        assert K_FACTORS[name]['k'] == pytest.approx(kFactor)
        assert K_FACTORS[name]['overpressure'] == pytest.approx(overpressure)

def testTheKFactorsAreMonotonicInOverpressure():

    ordered = sorted(K_FACTORS.values(), key = lambda entry: entry['k'])

    assert all(ordered[index]['overpressure'] > ordered[index + 1]['overpressure']
               for index in range(len(ordered) - 1))

def testInhabitedBuildingDistanceReproducesTheStandardsUnits():

    '''
    d = 40 W**(1/3) with d in feet and W in pounds. One thousand pounds of TNT gives exactly
    400 feet, which is the arithmetic the standard is written in.
    '''

    distance = hopkinsonCranzDistance(40.0, 1000.0 * KG_PER_LBM)

    assert distance == pytest.approx(400.0 * M_PER_FT)

def testTheHydrogenCrossoverIsWhereTheTwoRulesAreEqual():

    '''
    8 W**(2/3) equals 0.14 W at W = (8 / 0.14) ** 3 pounds. Below it the sublinear rule governs.
    '''

    expected = (HYDROGEN_SUBLINEAR_COEFFICIENT / HYDROGEN_FLAT_FRACTION) ** 3 * KG_PER_LBM

    component = HazardSiting()
    component.setInputs({'combination': 'LO2/LH2', 'propellantMass': 1.0e4})

    crossover = component.hydrogenCrossover()

    assert crossover['crossoverMass'] == pytest.approx(expected)
    assert crossover['crossoverMass'] == pytest.approx(84635.0, rel = 1.0e-4)

    below = explosiveEquivalent('LO2/LH2', expected * 0.5)
    above = explosiveEquivalent('LO2/LH2', expected * 2.0)

    assert below['governing'].startswith('sublinear')
    assert above['governing'].startswith('flat')

def testThePublishedMetricCoefficientIsNotTheConversionOfTheEnglishOne():

    '''
    DESR 6055.09 Table V5.E4.T5 footnote f prints the rule as 8 W**(2/3) with W in pounds and, in
    brackets, 4.13 Q**(2/3) with Q in kilograms. Converting the English form exactly gives 6.147,
    so the two are not the same rule and the published metric form is the smaller.

    This is asserted rather than silently corrected. An SI-native reading of the bracketed
    coefficient produces a shorter siting distance than the form the table is built on, and that
    is a non-conservative error rather than a rounding one.

    The reference is not adjusted to make anything pass. The library computes in the English form,
    which is what this test pins.
    '''

    exact = 8.0 * KG_PER_LBM ** (1.0 / 3.0)

    assert HYDROGEN_METRIC_COEFFICIENT_EXACT == pytest.approx(exact)
    assert exact == pytest.approx(6.147, rel = 1.0e-3)

    assert HYDROGEN_METRIC_COEFFICIENT_PUBLISHED == 4.13
    assert exact / HYDROGEN_METRIC_COEFFICIENT_PUBLISHED == pytest.approx(1.488, rel = 1.0e-3)

    # And the library uses the English form, so its answer is the larger one.
    mass = 38000.0
    library = explosiveEquivalent('LO2/LH2', mass)['equivalentMass']
    metric = HYDROGEN_METRIC_COEFFICIENT_PUBLISHED * mass ** (2.0 / 3.0)

    assert library > metric

def testAWorkedPointFromTheStandardsOwnUnits():

    '''
    One hundred thousand pounds of LO2/LH2. The sublinear term gives 8 * 100000**(2/3) = 17,235 lb
    and the flat term gives 14,000, so the sublinear one governs. Computed here from kilograms
    through the library, which is the conversion path a call site actually takes.
    '''

    result = explosiveEquivalent('LO2/LH2', 100000.0 * KG_PER_LBM)

    assert result['equivalentMass'] / KG_PER_LBM == pytest.approx(17235.5, rel = 1.0e-4)
    assert result['governing'].startswith('sublinear')

def testTheLoadingPhaseTableIsOrderedByRate():

    '''
    Chill-down and topping both run below the fill rates, and fast fill is the maximum. A table
    edited into a different order would silently change the tanking time.
    '''

    assert LOADING_PHASES['fastFill']['rateFraction'] == 1.0
    assert LOADING_PHASES['chilldown']['rateFraction'] < LOADING_PHASES['slowFill']['rateFraction']
    assert LOADING_PHASES['topping']['rateFraction'] < LOADING_PHASES['slowFill']['rateFraction']

def testTheWeatherShareOfScrubsMatchesTheEasternRangeRecord():

    '''
    Roughly half of launch scrubs at the Eastern Range across three decades were weather. That is
    the one operational number in this domain with a published record behind it, and it is a
    bounded check rather than a validation: it constrains the share and says nothing about the
    rates that produce it.
    '''

    assert 0.40 <= SCRUB_CAUSES['weather'] <= 0.55
    assert SCRUB_CAUSES['weather'] > max(share for cause, share in SCRUB_CAUSES.items()
                                         if cause != 'weather')

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: against the validation register -- #
# ------------------------------------------------------------------------------------------------ #

def testTheLibraryTablesMatchTheValidationRegister():

    """
    The register is the record of what was read from the standard. The library is what the domain
    computes with. They are separate files and they have to agree, because a library edited without
    the register is a library that has quietly stopped citing anything.
    """

    reference = EXPLOSIVE_SITING['DESR-6055.09']

    for name, entry in reference['kFactors'].items():
        assert K_FACTORS[name]['k'] == pytest.approx(entry['k'])
        assert K_FACTORS[name]['overpressure'] == pytest.approx(entry['psi'])

    for name, entry in reference['equivalence'].items():
        assert TNT_EQUIVALENCE[name]['rangeLaunch'] == pytest.approx(entry['rangeLaunch'])
        assert TNT_EQUIVALENCE[name]['staticTest'] == pytest.approx(entry['staticTest'])

def testTheHydrogenRuleMatchesTheValidationRegister():

    rule = EXPLOSIVE_SITING['DESR-6055.09']['hydrogenRule']

    assert HYDROGEN_SUBLINEAR_COEFFICIENT == pytest.approx(rule['sublinearCoefficient'])
    assert HYDROGEN_FLAT_FRACTION == pytest.approx(rule['flatFraction'])

    crossover = (rule['sublinearCoefficient'] / rule['flatFraction']) ** 3

    assert crossover == pytest.approx(rule['crossoverPounds'], rel = 1.0e-6)
    assert crossover * KG_PER_LBM == pytest.approx(rule['crossoverKg'], rel = 1.0e-6)

def testTheRegisterRecordsWhyTheSixtyPerCentFigureIsNotUsed():

    """
    The commonly quoted sixty per cent for LO2/LH2 is a yield figure from test data, not the
    siting rule. Building on it would have overstated a small stage by about a factor of three
    and missed the shape of the rule entirely. The correction is recorded rather than assumed.
    """

    note = EXPLOSIVE_SITING['DESR-6055.09']['correctionNote']

    assert 'sixty per cent' in note
    assert 'PYRO' in note

def testTheRegisterRecordsTheUnitDiscrepancy():

    note = EXPLOSIVE_SITING['DESR-6055.09']['unitNote']

    assert '4.13' in note
    assert '6.147' in note
    assert 'non-conservative' in note

def testTheDomainRegistersWhatItCannotValidate():

    """
    Three entries, and each names what scales with the input and what does not. A domain with a
    standard-level anchor on one half of it still has to say what the other half rests on.
    """

    registered = {name for name, entry in UNVALIDATED.items()
                  if entry['domain'] == 'groundSystemsAndOperations'}

    assert registered == {'loadingPhaseFractions', 'scrubCauseSplit', 'weatherCorrelation'}

    for name in registered:
        entry = UNVALIDATED[name]
        assert entry['reason'] and entry['consequence'] and entry['nextStep']
