# -- Tests for the recoveryAndReusability worked example -- #

'''

The example argues that reuse is decided by the quantities nobody photographs. The tests pin the
five stage results, the two places where a published number is used honestly, and the scope
decisions the domain made about what not to build.

Author: Sean Bowman
Date:   10/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'recoveryAndReusabilityLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'recoveryCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['recoveryCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from recoveryUtils import LandingError, LifeError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The case itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheVehicleMassesComeFromTheValidationRegister(case):

    from validation.referenceCases import LAUNCH_VEHICLES

    vehicle = LAUNCH_VEHICLES['Falcon 9 Block 5']

    assert case['vehicle']['stageDryMass'] == vehicle['stageOneDryMass']
    assert case['vehicle']['baselinePayload'] == vehicle['payloadToLeoExpended']
    assert case['vehicle']['publishedReusablePayload'] == vehicle['payloadToLeoReusable']

def testABoosterReturnIsFarSlowerThanAnOrbitalOne(case):

    assert (case['entry']['entryVelocity']
            < 0.4 * case['orbitalComparison']['entryVelocity'])

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: entry -- #
# ------------------------------------------------------------------------------------------------ #

def testPeakDecelerationIsInvariantAcrossTheBallisticSweep(case):

    trajectory = codeInterface.buildEntry(case)
    comparison = trajectory.compareBallisticCoefficients()

    assert comparison['decelerationIsInvariant'] is True
    assert comparison['heatFluxSpread'] > 3.0

def testTheOrbitalCaseHeatsFarMoreThanTheBoosterCase(case):

    booster = codeInterface.buildEntry(case).calculatePeakHeating()
    orbital = codeInterface.buildEntry(case, 'orbitalComparison').calculatePeakHeating()

    assert orbital['peakHeatFlux'] > 10.0 * booster['peakHeatFlux']
    assert orbital['heatLoad'] > 10.0 * booster['heatLoad']

def testTheBoosterEntryIsSurvivableWithoutAHeatShield(case):

    '''
    Twenty odd watts per square centimetre is a paint and a metal skin problem. A few hundred is a
    heat shield. That single difference is why first stage reuse arrived long before upper stage
    reuse, and it comes from the cube of entry velocity.
    '''

    booster = codeInterface.buildEntry(case).calculatePeakHeating()

    assert booster['peakHeatFluxWattPerCm2'] < 50.0

def testTheCorridorTradeIsOpposedInTheCase(case):

    corridor = codeInterface.buildEntry(case).compareFlightPathAngles()

    assert corridor['tradeIsOpposed'] is True

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: what recovery costs -- #
# ------------------------------------------------------------------------------------------------ #

def testTheReserveCostsMorePayloadThanTheHardware(case):

    penalty = codeInterface.buildBudget(case).calculatePenalty()

    assert penalty['costliest'] == 'reserve propellant'

    hardware, reserve = penalty['contributions']

    assert reserve['payloadCost'] > 3.0 * hardware['payloadCost']

def testTheModelledPenaltyOverPredictsAndSaysSo(case):

    budget = codeInterface.buildBudget(case)
    vehicle = case['vehicle']

    published = ((vehicle['baselinePayload'] - vehicle['publishedReusablePayload'])
                 / vehicle['baselinePayload'])

    modelled = budget.calculatePenalty()['penaltyFraction']

    assert modelled > published
    assert modelled < 1.5 * published

def testTheInversionIsUsedRatherThanACalibration(case, capsys):

    '''
    Tuning the exchange ratios until the budget reproduced the published penalty and then
    reporting the agreement would be calibration. The example inverts instead and says so.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'calibration, not validation' in printed

def testTheRecoveryModeOrderingHoldsInTheCase(case):

    modes = codeInterface.buildBudget(case).compareModes()
    order = [entry['mode'] for entry in modes['results']]

    assert order.index('expended') < order.index('downrangeLanding')
    assert order.index('downrangeLanding') < order.index('returnToLaunchSite')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: touchdown -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTouchdownClearsItsStructuralLimit(case):

    touchdown = codeInterface.buildLanding(case).calculateLoadFactor()

    assert touchdown['loadFactor'] < case['landing']['limitLoadFactor']
    assert touchdown['margin'] > 1.0

def testTheChosenAbsorberIsAReusableOne(case):

    touchdown = codeInterface.buildLanding(case).calculateLoadFactor()

    assert touchdown['reusable'] is True

def testTheReusableAbsorberIsBoughtBackWithStroke(case):

    comparison = codeInterface.buildLanding(case).compareAbsorbers()

    byName = {entry['absorber']: entry for entry in comparison['results']}

    assert (byName['hydraulicDamper']['strokeForBaseline']
            > byName['crushableHoneycomb']['strokeForBaseline'])

def testADroneshipDeckCostsTipoverMargin(case):

    pad = codeInterface.buildLanding(case).calculateTipover()
    deck = codeInterface.buildLanding(case, droneship = True).calculateTipover()

    assert deck['margin'] < pad['margin']
    assert deck['groundSlope'] > pad['groundSlope']

def testATallerVehicleOnTheSameFootprintIsRefused(case):

    '''
    Tipover margin falls as the arctangent of footprint over height, so a slender vehicle on the
    same footprint runs out of it quickly: 39 degrees at the case geometry, 9 at three times the
    height, and refused at ten times.
    '''

    loads = codeInterface.buildLanding(case, droneship = True)

    loads.centreOfGravity = 33.0
    assert loads.calculateTipover()['margin'] < 10.0

    loads.centreOfGravity = 120.0

    with pytest.raises(LandingError):
        loads.calculateTipover()

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: life -- #
# ------------------------------------------------------------------------------------------------ #

def testThePrimaryStructureIsNotTheLimit(case):

    accumulation = codeInterface.buildLife(case).calculateAccumulation()

    assert accumulation['limitingItem'] != 'primary structure'
    assert accumulation['items'][-1]['item'] == 'primary structure'

def testExtendingTheLimitMovesItRatherThanRemovingIt(case):

    accumulation = codeInterface.buildLife(case).calculateAccumulation()

    assert accumulation['nextItem'] is not None
    assert accumulation['gainIfExtended'] > 0.0

def testTheFleetLeaderCarriesTheWarning(case):

    fleet = codeInterface.buildLife(case).fleetLeaderLead(case['life']['fleetFlights'])

    assert fleet['hasWarning'] is True
    assert fleet['leadInFlights'] >= 10.0

def testTheStatedCertifiedLifeExceedsWhatTheScatterFactorSupports(case):

    '''
    A real and common position rather than an error: the stated life is held by inspection rather
    than by analysis, which is what the inspection ladder is for.
    '''

    certification = codeInterface.buildLife(case).certifiedAgainstDemonstrated()

    assert certification['coversScatter'] is False
    assert certification['impliedScatter'] < 1.0

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: economics -- #
# ------------------------------------------------------------------------------------------------ #

def testMostOfTheBenefitArrivesInTheFirstThreeFlights(case):

    economics = codeInterface.buildEconomics(case, 0.189)
    sweep = economics.flightCountSweep()

    assert sweep['shareOfBenefitInThree'] > 0.6

def testTheEconomicsUsesThePublishedPenaltyRatherThanTheModelled(case, capsys):

    '''
    A measured number is available for the penalty, so the example uses it rather than compounding
    its own over-prediction into the economics.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'carries 19% less' in printed

def testARecoveryLossRateCostsFarMoreThanItsRate(case):

    economics = codeInterface.buildEconomics(case, 0.189)
    effective = economics.effectiveFlights()

    lossRate = 1.0 - case['economics']['recoverySuccess']

    assert effective['shortfall'] > 5.0 * lossRate

# ------------------------------------------------------------------------------------------------ #
# -- Precedent and scope -- #
# ------------------------------------------------------------------------------------------------ #

def testTheFalconTurnaroundBeatsTheShuttleDesignGoal(case):

    '''
    The comparison the domain closes on. The difference is not landing technology, it is that the
    Shuttle had to be inspected in ways its design made expensive.
    '''

    precedent = case['precedent']

    assert precedent['shuttleShortestTurnaroundDays'] > 3.0 * precedent['shuttleDesignTurnaroundDays']
    assert precedent['falconShortestTurnaroundDays'] < precedent['shuttleDesignTurnaroundDays']

def testTheExampleNamesWhatItDeliberatelyDidNotBuild(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    for absent in ('Aeroheating into a structure', 'Fatigue and crack growth',
                   'Parachute sizing', 'Guidance to the landing point',
                   'Refurbishment scheduling', 'Sea state and droneship dynamics'):
        assert absent in printed

def testTheExampleRunsEndToEnd(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert len(printed.splitlines()) > 180

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
