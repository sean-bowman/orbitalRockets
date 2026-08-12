# -- Tests for the recoveryAndReusability library -- #

'''

Three tiers. Tier one is inputs and refusals, tier two is the closed forms, and tier three is the
published material: the Allen-Eggers solution, the Sutton-Graves constant reproduced against
published entry cases, and the Falcon 9 payload figures already in the validation register.

The Allen-Eggers relations are reproduced rather than fitted. Where a source states a rule of thumb
that does not generalise, the test asserts the general form and says why.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'recoveryAndReusabilityLibrary'))
sys.path.insert(0, ROOT)

from recoveryUtils import (RECOVERY_MODES, LIFE_LIMITED_ITEMS, INSPECTION_LEVELS,
                           ATMOSPHERIC_SCALE_HEIGHT, SEA_LEVEL_DENSITY,
                           PEAK_DECELERATION_VELOCITY_FRACTION, PEAK_HEATING_VELOCITY_FRACTION,
                           SUTTON_GRAVES_CONSTANT, WATT_PER_M2_TO_WATT_PER_CM2, GRAVITY,
                           ballisticCoefficient, suttonGravesHeatFlux,
                           exponentialDensity, altitudeFromDensity,
                           InvalidInputError, EntryError, LandingError, LifeError, EconomicsError)

from validation.referenceCases import LAUNCH_VEHICLES, UNVALIDATED

from EntryTrajectory import EntryTrajectory
from RecoveryBudget import RecoveryBudget
from LandingLoads import LandingLoads
from LifeTracking import LifeTracking
from ReuseEconomics import ReuseEconomics

# ------------------------------------------------------------------------------------------------ #
# -- Fixtures -- #
# ------------------------------------------------------------------------------------------------ #

@pytest.fixture
def entry():

    trajectory = EntryTrajectory()
    trajectory.setInputs({'entryVelocity':   7800.0,
                          'flightPathAngle': 6.0,
                          'mass':            26000.0,
                          'dragCoefficient': 1.1,
                          'referenceArea':   10.5,
                          'noseRadius':      1.8})

    return trajectory

@pytest.fixture
def budget():

    component = RecoveryBudget()
    component.setInputs({'stageDryMass':    22200.0,
                         'stagePropellant': 410900.0,
                         'baselinePayload': 22800.0,
                         'mode':            'downrangeLanding',
                         'hardwareItems':   {'landing legs': 2100.0,
                                             'grid fins':    450.0,
                                             'avionics':     160.0,
                                             'structure':    390.0}})

    return component

@pytest.fixture
def landing():

    loads = LandingLoads()
    loads.setInputs({'landedMass':      26000.0,
                     'sinkRate':        2.0,
                     'horizontalRate':  0.5,
                     'stroke':          0.45,
                     'absorber':        'hydraulicDamper',
                     'legCount':        4,
                     'footprintRadius': 9.0,
                     'centreOfGravity': 11.0,
                     'groundSlope':     2.0,
                     'limitLoadFactor': 4.5})

    return loads

@pytest.fixture
def life():

    tracker = LifeTracking()
    tracker.setInputs({'flightsFlown': 10.0, 'certifiedLife': 20.0})

    return tracker

@pytest.fixture
def economics():

    component = ReuseEconomics()
    component.setInputs({'refurbishmentCost':  0.08,
                         'recoveryCost':       0.04,
                         'expendableElements': 0.25,
                         'recoverySuccess':    0.97,
                         'flightsPerArticle':  20.0,
                         'payloadPenalty':     0.189})

    return component

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: inputs and refusals -- #
# ------------------------------------------------------------------------------------------------ #

def testANearlyHorizontalEntryIsRefused():

    '''
    A shallow entry is a glide, and the constant flight path angle the Allen-Eggers solution
    assumes is the first thing to go. Reporting a number for it would be reporting a number from a
    model that does not apply.
    '''

    trajectory = EntryTrajectory()

    with pytest.raises(EntryError):
        trajectory.setInputs({'entryVelocity': 7800.0, 'flightPathAngle': 0.2,
                              'mass': 1000.0, 'dragCoefficient': 1.0, 'referenceArea': 5.0})

def testAVerticalEntryIsRefused():

    trajectory = EntryTrajectory()

    with pytest.raises(EntryError):
        trajectory.setInputs({'entryVelocity': 7800.0, 'flightPathAngle': 90.0,
                              'mass': 1000.0, 'dragCoefficient': 1.0, 'referenceArea': 5.0})

def testHeatingWithoutANoseRadiusIsRefused():

    '''
    Nose radius does not appear in the trajectory at all, so it is optional there and required
    here. Defaulting it would put a made-up length into every heat flux.
    '''

    trajectory = EntryTrajectory()
    trajectory.setInputs({'entryVelocity': 7800.0, 'flightPathAngle': 6.0,
                          'mass': 1000.0, 'dragCoefficient': 1.0, 'referenceArea': 5.0})

    with pytest.raises(EntryError):
        trajectory.calculatePeakHeating()

def testARecoveryBudgetThatConsumesThePayloadIsRefused(budget):

    budget.baselinePayload = 500.0

    with pytest.raises(Exception):
        budget.calculatePenalty()

def testExchangeRatiosTheWrongWayRoundAreRefused():

    '''
    Dry mass costs more payload per kilogram than reserve propellant, because it is carried through
    the whole burn. A pair the other way round is a sign convention error rather than an unusual
    vehicle.
    '''

    component = RecoveryBudget()

    with pytest.raises(InvalidInputError):
        component.setInputs({'stageDryMass': 20000.0, 'stagePropellant': 400000.0,
                             'baselinePayload': 20000.0,
                             'dryMassExchangeRatio': 0.05, 'reserveExchangeRatio': 0.10})

def testALoadFactorAboveTheStructuralLimitIsRefused(landing):

    landing.sinkRate = 8.0

    with pytest.raises(LandingError):
        landing.calculateLoadFactor()

def testTipoverWithoutTheGeometryIsRefused(landing):

    landing.footprintRadius = np.nan

    with pytest.raises(LandingError):
        landing.calculateTipover()

def testATipoverMarginAtZeroIsRefused(landing):

    landing.groundSlope = 39.0

    with pytest.raises(LandingError):
        landing.calculateTipover()

def testFewerThanThreeLegsIsRefused():

    loads = LandingLoads()

    with pytest.raises(InvalidInputError):
        loads.setInputs({'landedMass': 1000.0, 'sinkRate': 2.0, 'stroke': 0.3, 'legCount': 2})

def testAnArticlePastItsLifeLimitIsRefused(life):

    life.flightsFlown = 40.0

    with pytest.raises(LifeError):
        life.calculateAccumulation()

def testADamagePerFlightAboveOneIsRefused():

    tracker = LifeTracking()

    with pytest.raises(InvalidInputError):
        tracker.setInputs({'flightsFlown': 1.0, 'items': {'thing': 1.4}})

def testAScatterFactorBelowOneIsRefused():

    tracker = LifeTracking()

    with pytest.raises(InvalidInputError):
        tracker.setInputs({'flightsFlown': 1.0, 'scatterFactor': 0.5})

def testReuseWithNoBreakEvenIsRefused(economics):

    '''
    Refurbishment plus recovery above one unit cost means a reusable flight is dearer than an
    expendable one at every flight count. Reporting a very large break-even would suggest that
    flying more fixes it, and it does not.
    '''

    economics.refurbishmentCost = 1.1

    with pytest.raises(EconomicsError):
        economics.breakEven()

def testARecoverySuccessOfZeroIsRefused():

    component = ReuseEconomics()

    with pytest.raises(InvalidInputError):
        component.setInputs({'refurbishmentCost': 0.1, 'flightsPerArticle': 10.0,
                             'recoverySuccess': 0.0})

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: the closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testPeakDecelerationDoesNotDependOnTheBallisticCoefficient(entry):

    '''
    The domain's headline result. a_max = V_e**2 sin|gamma| / (2 e H), and the vehicle does not
    appear in it at all.
    '''

    comparison = entry.compareBallisticCoefficients([0.1, 1.0, 10.0, 100.0])

    assert comparison['decelerationIsInvariant'] is True

    loadFactors = [item['peakLoadFactor'] for item in comparison['results']]

    assert max(loadFactors) == pytest.approx(min(loadFactors), rel = 1.0e-12)

def testPeakDecelerationMatchesTheClosedForm(entry):

    expected = (entry.entryVelocity ** 2 * np.sin(np.radians(entry.flightPathAngle))
                / (2.0 * np.e * entry.scaleHeight))

    assert entry.calculatePeakDeceleration()['peakDeceleration'] == pytest.approx(expected)

def testPeakDecelerationScalesWithTheSquareOfEntryVelocity(entry):

    slow = entry.calculatePeakDeceleration()['peakDeceleration']
    entry.entryVelocity *= 2.0
    fast = entry.calculatePeakDeceleration()['peakDeceleration']

    assert fast / slow == pytest.approx(4.0)

def testPeakHeatFluxScalesWithTheSquareRootOfBeta(entry):

    low = entry.calculatePeakHeating()['peakHeatFlux']
    entry.mass *= 4.0
    high = entry.calculatePeakHeating()['peakHeatFlux']

    assert high / low == pytest.approx(2.0)

def testPeakHeatFluxScalesWithTheCubeOfEntryVelocity(entry):

    slow = entry.calculatePeakHeating()['peakHeatFlux']
    entry.entryVelocity *= 2.0
    fast = entry.calculatePeakHeating()['peakHeatFlux']

    assert fast / slow == pytest.approx(8.0)

def testHeatLoadScalesWithTheSquareRootOfBetaAndInverselyWithSteepness(entry):

    base = entry.calculatePeakHeating()['heatLoad']

    entry.mass *= 4.0
    heavier = entry.calculatePeakHeating()['heatLoad']
    entry.mass /= 4.0

    assert heavier / base == pytest.approx(2.0)

    shallow = entry.calculatePeakHeating()['heatLoad']
    entry.flightPathAngle = 24.0
    steep = entry.calculatePeakHeating()['heatLoad']

    assert steep < shallow

def testTheCorridorTradeIsOpposed(entry):

    '''
    Steeper raises the peak rate and lowers the total load. There is no flight path angle that
    improves both, which is why the corridor is a choice rather than an optimum.
    '''

    corridor = entry.compareFlightPathAngles()

    assert corridor['tradeIsOpposed'] is True
    assert corridor['fluxRatio'] > 1.0
    assert corridor['loadRatio'] < 1.0

def testPeakHeatingHappensBeforePeakDeceleration(entry):

    heating = entry.calculatePeakHeating()
    deceleration = entry.calculatePeakDeceleration()

    assert heating['aheadOfDeceleration'] is True
    assert heating['atVelocity'] > deceleration['atVelocity']

def testTheAltitudeSeparationIsScaleHeightTimesLogThree(entry):

    '''
    The two peak densities differ by exactly a factor of three, and altitude is logarithmic in
    density, so the separation is H ln(3) for every entry of every vehicle.

    **The separation is the invariant and the ratio is not.** Sources quoting an altitude ratio of
    about 1.1 are quoting it for an orbital entry where the deceleration peak is high; on a
    booster returning from a lofted suborbital trajectory the same separation is half the altitude
    again.
    '''

    heating = entry.calculatePeakHeating()
    deceleration = entry.calculatePeakDeceleration()

    separation = heating['atAltitude'] - deceleration['atAltitude']

    assert separation == pytest.approx(ATMOSPHERIC_SCALE_HEIGHT * np.log(3.0))
    assert heating['altitudeSeparation'] == pytest.approx(separation)

def testTheVelocityFractionsArePureNumbers():

    assert PEAK_DECELERATION_VELOCITY_FRACTION == pytest.approx(np.exp(-0.5))
    assert PEAK_HEATING_VELOCITY_FRACTION == pytest.approx(np.exp(-1.0 / 6.0))
    assert PEAK_HEATING_VELOCITY_FRACTION > PEAK_DECELERATION_VELOCITY_FRACTION

def testTheAtmosphereInvertsExactly():

    for altitude in (0.0, 10000.0, 40000.0, 80000.0):
        assert altitudeFromDensity(exponentialDensity(altitude)) == pytest.approx(altitude)

def testCountedHardwareBeatsTheFractionalAllowance(budget):

    counted = budget.calculateHardwareMass()
    assert counted['method'] == 'counted'

    budget.hardwareItems = {}
    fractional = budget.calculateHardwareMass()

    assert fractional['method'] == 'fractional'
    assert len(counted['items']) > len(fractional['items'])

def testThePenaltySharesSumToOne(budget):

    penalty = budget.calculatePenalty()

    assert sum(entry['share'] for entry in penalty['contributions']) == pytest.approx(1.0)

def testThePenaltyMassIsFixedAcrossMissions(budget):

    '''
    The recovery cost is a nearly fixed number of kilograms. Expressed as a fraction of a payload
    that shrinks with mission energy it grows, which is the whole reason boosters are expended on
    the hardest missions of a reusable fleet.
    '''

    sensitivity = budget.missionSensitivity()

    assert sensitivity['penaltyMassIsFixed'] is True
    assert sensitivity['fractionSpread'] > 1.0

def testReturnToLaunchSiteCostsMoreThanADownrangeLanding(budget):

    modes = budget.compareModes()
    byMode = {entry['mode']: entry['penaltyFraction'] for entry in modes['results']}

    assert byMode['expended'] == 0.0
    assert byMode['parachuteAndSplashdown'] < byMode['downrangeLanding']
    assert byMode['downrangeLanding'] < byMode['returnToLaunchSite']

def testTheLoadFactorIsInverselyProportionalToStroke(landing):

    short = landing.calculateLoadFactor(stroke = 0.2)['loadFactor'] - 1.0
    long = landing.calculateLoadFactor(stroke = 0.4)['loadFactor'] - 1.0

    assert short / long == pytest.approx(2.0)

def testTheRequiredStrokeInvertsTheLoadFactor(landing):

    required = landing.requiredStroke(3.0)['requiredStroke']

    assert landing.calculateLoadFactor(stroke = required)['loadFactor'] == pytest.approx(3.0)

def testTheReusableAbsorbersAreTheInefficientOnes(landing):

    comparison = landing.compareAbsorbers()

    reusable = [entry for entry in comparison['results'] if entry['reusable']]
    singleUse = [entry for entry in comparison['results'] if not entry['reusable']]

    assert min(entry['efficiency'] for entry in singleUse) > \
           max(entry['efficiency'] for entry in reusable)

def testSlopeAndHorizontalRateBothReduceTheTipoverMargin(landing):

    base = landing.calculateTipover()['margin']

    landing.groundSlope += 5.0
    steeper = landing.calculateTipover()['margin']
    landing.groundSlope -= 5.0

    landing.horizontalRate += 1.0
    faster = landing.calculateTipover()['margin']

    assert steeper < base
    assert faster < base

def testTheLimitingItemHasTheLeastRemainingLife(life):

    accumulation = life.calculateAccumulation()

    assert accumulation['items'][0]['item'] == accumulation['limitingItem']
    assert all(accumulation['items'][index]['remainingFlights']
               <= accumulation['items'][index + 1]['remainingFlights']
               for index in range(len(accumulation['items']) - 1))

def testExtendingTheLimitingItemBuysOnlyTheGapToTheNext(life):

    accumulation = life.calculateAccumulation()

    byItem = {entry['item']: entry['allowableFlights'] for entry in accumulation['items']}

    assert accumulation['gainIfExtended'] == pytest.approx(
        byItem[accumulation['nextItem']] - byItem[accumulation['limitingItem']])

def testASeveritySweepRecordsWhereTheArticleRunsOut(life):

    '''
    Far enough up the range the article is past its limit. In a sensitivity study that is the
    answer rather than an error, so it is recorded rather than raised.
    '''

    severity = life.severitySensitivity()

    assert any(entry['pastLimit'] for entry in severity['results'])
    assert severity['exhaustsAtSeverity'] > 1.0

def testTheFleetLeaderLeadIsTheWarning(life):

    withLeader = life.fleetLeaderLead([36.0, 22.0, 18.0])
    evenFleet = life.fleetLeaderLead([20.0, 20.0, 20.0])

    assert withLeader['hasWarning'] is True
    assert evenFleet['hasWarning'] is False
    assert evenFleet['leadInFlights'] == 0.0

def testACertifiedLifeIsSmallerThanADemonstratedOne(life):

    certification = life.certifiedAgainstDemonstrated()

    assert certification['impliedCertified'] < certification['demonstratedLife']
    assert certification['impliedCertified'] == pytest.approx(
        certification['demonstratedLife'] / certification['scatterFactor'])

def testTheInspectionLadderCostsRiseFasterThanCoverage(life):

    ladder = life.inspectionLadder()

    costs = [entry['relativeCost'] for entry in ladder['levels']]

    assert costs == sorted(costs)
    assert ladder['costSpread'] > 50.0

def testTheAmortisedTermCollapsesAndTheRestDoesNot(economics):

    sweep = economics.flightCountSweep()

    first = sweep['sweep'][0]
    last = sweep['sweep'][-1]

    assert first['amortisedShare'] > last['amortisedShare']
    assert last['costPerFlight'] > sweep['floorCost']
    assert sweep['shareOfBenefitInThree'] > 0.5

def testTheMarginalSavingFallsWithFlightCount(economics):

    sweep = economics.flightCountSweep()['sweep'][1:]

    savings = [entry['marginalSaving'] for entry in sweep]

    assert all(savings[index] > savings[index + 1] for index in range(len(savings) - 1))

def testTheBreakEvenMatchesItsClosedForm(economics):

    breakEven = economics.breakEven()

    expected = 1.0 / (1.0 - economics.refurbishmentCost - economics.recoveryCost)

    assert breakEven['breakEvenFlights'] == pytest.approx(expected)

def testARecoveryLossRateCostsMoreFlightsThanItsRate(economics):

    '''
    A three per cent loss rate removes far more than three per cent of the flights, because the
    losses compound over the fleet life rather than applying once.
    '''

    effective = economics.effectiveFlights()

    assert effective['expected'] < effective['planned']
    assert effective['shortfall'] > 5.0 * (1.0 - economics.recoverySuccess)

def testPerfectRecoveryGivesThePlannedFlights(economics):

    economics.recoverySuccess = 1.0
    effective = economics.effectiveFlights()

    assert effective['expected'] == pytest.approx(effective['planned'])

def testThePayloadPenaltyErodesTheCostPerKilogramSaving(economics):

    perKilogram = economics.costPerKilogram()

    assert perKilogram['kilogramSaving'] < perKilogram['flightSaving']
    assert perKilogram['penaltyErodesSaving'] is True

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: against published material -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSuttonGravesConstantReproducesPublishedEntryCases():

    '''
    The units on this constant are quoted inconsistently: several sources state that the
    expression returns W/cm2 with SI inputs, and that is wrong by four orders of magnitude.

    Fixed here by reproducing published peak heating for two entries rather than by trusting the
    statement. Both land where they should when the raw expression is read as W/m2 and are absurd
    by 1e4 when it is read as W/cm2.

    Stardust returned from a comet sample mission at 12.6 km/s with a 0.23 m nose radius and a
    published peak convective heating around 1,200 W/cm2. Apollo returned from the Moon at
    11.1 km/s with a 4.69 m radius and a convective component around 200 to 250.
    '''

    stardust = suttonGravesHeatFlux(2.0e-4, 0.23, 12600.0) * WATT_PER_M2_TO_WATT_PER_CM2
    apollo = suttonGravesHeatFlux(3.1e-4, 4.69, 11140.0) * WATT_PER_M2_TO_WATT_PER_CM2

    assert 800.0 < stardust < 1500.0
    assert 150.0 < apollo < 300.0

def testTheSuttonGravesConstantIsTheEarthValue():

    assert SUTTON_GRAVES_CONSTANT == 1.7415e-4

def testTheBallisticCoefficientDefinition():

    assert ballisticCoefficient(1000.0, 1.0, 10.0) == pytest.approx(100.0)
    assert ballisticCoefficient(2000.0, 1.0, 10.0) == pytest.approx(200.0)
    assert ballisticCoefficient(1000.0, 2.0, 10.0) == pytest.approx(50.0)

def testTheFalconPenaltyRatiosComeFromTheRegister():

    '''
    The expendable and reusable payloads come from one source table, so their RATIO is a sourced
    quantity even though the model behind it is not. That is what makes it usable here.
    '''

    vehicle = LAUNCH_VEHICLES['Falcon 9 Block 5']

    leo = (1.0 - vehicle['payloadToLeoReusable'] / vehicle['payloadToLeoExpended'])
    gto = (1.0 - vehicle['payloadToGtoReusable'] / vehicle['payloadToGtoExpended'])

    assert leo == pytest.approx(0.1886, abs = 1.0e-3)
    assert gto == pytest.approx(0.3373, abs = 1.0e-3)

    # The transfer orbit penalty is the larger one, which is the structural result.
    assert gto > leo

def testTheModelledPenaltyIsTheRightSideOfThePublishedOne(budget):

    '''
    A bottom-up budget that lands nowhere near the published penalty is a budget with something
    missing. This one over-predicts, which is the safe direction and is reported rather than
    tuned away.

    **No coefficient is adjusted to make this pass.** The exchange ratios are representative and
    registered as unvalidated, and the class offers an inversion instead.
    '''

    vehicle = LAUNCH_VEHICLES['Falcon 9 Block 5']
    published = 1.0 - vehicle['payloadToLeoReusable'] / vehicle['payloadToLeoExpended']

    modelled = budget.calculatePenalty()['penaltyFraction']

    assert modelled > published
    assert modelled < 2.0 * published

def testTheInversionRecoversTheAssumedRatiosToWithinAThird(budget):

    vehicle = LAUNCH_VEHICLES['Falcon 9 Block 5']
    publishedMass = vehicle['payloadToLeoExpended'] - vehicle['payloadToLeoReusable']

    implied = budget.impliedExchangeRatios(publishedMass)

    assert 0.6 < implied['dryMassAgreement'] < 1.0
    assert implied['fixedRatio'] == pytest.approx(budget.dryMassExchangeRatio
                                                  / budget.reserveExchangeRatio)

def testTheRecoveryModeOrderingIsStructural():

    '''
    A return to the launch site costs more reserve than a downrange landing because it has to
    cancel and reverse the downrange velocity, and both cost more than expending. That holds for
    any values, which is why it is asserted on the table rather than on a result.
    '''

    assert RECOVERY_MODES['expended']['reservePropellantFraction'] == 0.0
    assert (RECOVERY_MODES['downrangeLanding']['reservePropellantFraction']
            < RECOVERY_MODES['returnToLaunchSite']['reservePropellantFraction'])
    assert RECOVERY_MODES['parachuteAndSplashdown']['reservePropellantFraction'] == 0.0

def testPrimaryStructureIsRarelyTheLifeLimit():

    '''
    The domain's life result in table form: the item that carries the loads is not the item that
    retires the article.
    '''

    limiting = min(LIFE_LIMITED_ITEMS, key = lambda name:
                   1.0 / LIFE_LIMITED_ITEMS[name]['damagePerFlight'])

    assert limiting != 'primary structure'
    assert (LIFE_LIMITED_ITEMS['primary structure']['damagePerFlight']
            == min(entry['damagePerFlight'] for entry in LIFE_LIMITED_ITEMS.values()))

def testTheDomainRegistersWhatItCannotValidate():

    registered = {name for name, entry in UNVALIDATED.items()
                  if entry['domain'] == 'recoveryAndReusability'}

    assert registered == {'exchangeRatios', 'lifeDamageRates', 'recoveryModeFractions'}

    for name in registered:
        entry = UNVALIDATED[name]
        assert entry['reason'] and entry['consequence'] and entry['nextStep']
