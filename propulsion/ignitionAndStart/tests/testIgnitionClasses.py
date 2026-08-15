# -- Tests for the ignitionAndStart classes -- #

'''

Tiered tests for the four transient classes.

Tier 1 covers the contract, and this sub-domain has more of it than most, because two of its
checks refuse rather than report: a start sequence out of order and an oxidiser-rich shutdown.
Both are destroyed engines rather than degraded ones and neither is modelled.

Tier 2 validates against closed forms and against the published RS-25 sequence.

Tier 3 covers the results the sub-domain exists to produce, chiefly that the accumulation bound
scales with start flow rather than with igniter quality, that ignition detection cannot act inside
the window on a large chamber, that the residual impulse is the plumbing rather than the ramp, and
that the hydrogen chill-down band is several times wider than the oxygen one.

Every tier 3 assertion is on a ranking, a ratio or the direction of a sensitivity. None is on a
magnitude, because the sources cannot support one. See docs/ValidationReferences.md.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'ignitionAndStartLibrary'))
sys.path.insert(0, ROOT)

from ignitionUtils import (CRYOGENIC_SPECIFIC_HEAT_FITS, UNFITTED_SPECIFIC_HEAT,
                           REFERENCE_CHILL_RANGE, specificHeat, meanSpecificHeat,
                           enthalpyChange, chillDownEnthalpy)
from ignitionUtils import (IGNITER_TYPES, IGNITION_DELAY, CRYOGENS, MEAN_SPECIFIC_HEAT,
                           SSME_START_SEQUENCE, SSME_SHUTDOWN_LIMITS, SSME_SEQUENCE_TOLERANCE,
                           accumulatedPropellant, residenceTime, primingTime,
                           InvalidInputError, IgnitionError, SequenceError, ConditioningError)
from StartTransient import StartTransient, HARD_START_RATIO
from IgnitionSystem import IgnitionSystem, PERMITTED_CHAMBER_FULLS, DETECTION_LATENCY
from ShutdownTransient import ShutdownTransient, NEWTON_PER_POUND_FORCE
from ChillDown import ChillDown

from validation.referenceCases import START_SEQUENCES, IGNITION_DELAYS, UNVALIDATED

# The reference booster, from the propulsion hub by way of combustionDevices.
THROAT_AREA  = np.pi / 4.0 * 0.0906 ** 2
BOOSTER_FLOW = 26.47 + 10.34

def buildStart(**overrides) -> StartTransient:

    inputs = {'combination':     'LOX/RP-1',
              'chamberPressure': 10.0e6,
              'throatArea':      THROAT_AREA,
              'massFlow':        BOOSTER_FLOW,
              'ignitionDelay':   0.020,
              'feedVolume':      0.008}
    inputs.update(overrides)

    start = StartTransient()
    start.setInputs(inputs)

    return start

def buildSystem(**overrides) -> IgnitionSystem:

    inputs = {'combination':    'LOX/RP-1',
              'startsRequired': 1,
              'residenceTime':  0.00147}
    inputs.update(overrides)

    system = IgnitionSystem()
    system.setInputs(inputs)

    return system

def buildShutdown(**overrides) -> ShutdownTransient:

    inputs = {'combination': 'LOX/RP-1',
              'thrust':      100.0e3,
              'massFlow':    BOOSTER_FLOW,
              'feedVolume':  0.008}
    inputs.update(overrides)

    shutdown = ShutdownTransient()
    shutdown.setInputs(inputs)

    return shutdown

def buildChill(**overrides) -> ChillDown:

    inputs = {'cryogen': 'LOX', 'material': 'stainless 304', 'metalMass': 45.0}
    inputs.update(overrides)

    chill = ChillDown()
    chill.setInputs(inputs)

    return chill

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSpecificErrorsSubclassTheDomainBase():

    '''
    The scaffold aliases IgnitionError to the shared EngineeringError, so a caller can catch the
    whole family with one except clause. The specific errors have to subclass it or that breaks.
    '''

    assert issubclass(SequenceError, IgnitionError)
    assert issubclass(ConditioningError, IgnitionError)

def testAnUnknownCombinationIsRejected():

    with pytest.raises(InvalidInputError, match = 'Unknown propellant combination'):
        buildStart(combination = 'LOX/unobtainium')

def testANonHypergolicCombinationHasNoDefaultIgnitionDelay():

    '''
    The delay of a spark ignited engine is a property of its igniter, not of its propellants, so
    there is nothing to fall back on. Guessing one would be inventing the input the whole
    accumulation bound turns on.
    '''

    with pytest.raises(InvalidInputError, match = 'not hypergolic'):
        StartTransient().setInputs({'combination':     'LOX/RP-1',
                                    'chamberPressure': 10.0e6,
                                    'throatArea':      THROAT_AREA,
                                    'massFlow':        BOOSTER_FLOW})

def testAHypergolicCombinationDefaultsToItsMeasuredRange():

    start = StartTransient()
    start.setInputs({'combination':     'N2O4/MMH',
                     'chamberPressure': 2.0e6,
                     'throatArea':      1.0e-4,
                     'massFlow':        0.5})

    assert start.ignitionDelay == pytest.approx(IGNITION_DELAY['N2O4/MMH'][1] / 1000.0)

def testAnIgnitionDelayLongerThanAStartIsRejected():

    '''
    If combustion has not started after a second the sequence has failed, and the correct action is
    to close the valves rather than to compute an overpressure for it.
    '''

    with pytest.raises(SequenceError, match = 'sequence has'):
        buildStart(ignitionDelay = 2.0)

def testAStartFlowFractionOutsideTheUnitIntervalIsRejected():

    with pytest.raises(InvalidInputError, match = r'\(0, 1\]'):
        buildStart(startFlowFraction = 1.5)

def testAnOutOfOrderStartSequenceIsRefusedRatherThanReported():

    '''
    The first of two refusals in this sub-domain. A sequence out of order is not a slow start, it
    is a destroyed engine, and nothing in this repository models what happens next.
    '''

    with pytest.raises(SequenceError, match = 'not monotonic'):
        buildStart().checkSequence({'fuelValve': 0.0, 'oxidiserValve': 0.5, 'igniter': 0.2})

def testASequenceWithOneEventCannotBeChecked():

    with pytest.raises(SequenceError, match = 'at least two events'):
        buildStart().checkSequence({'fuelValve': 0.0})

def testAnOxidiserRichShutdownIsRefusedRatherThanReported():

    '''
    The second refusal. An oxidiser-rich excursion at combustion temperature is how injector faces
    and turbines are destroyed.
    '''

    with pytest.raises(SequenceError, match = 'oxidiser-rich'):
        buildShutdown().checkShutdownOrder(oxidiserCloseTime = 1.0, fuelCloseTime = 0.5)

def testSimultaneousValveClosureIsAlsoRefused():

    '''
    Equal times are not fuel-rich, they are a coin toss on hardware. Refused on the same grounds.
    '''

    with pytest.raises(SequenceError, match = 'oxidiser-rich'):
        buildShutdown().checkShutdownOrder(oxidiserCloseTime = 1.0, fuelCloseTime = 1.0)

def testAnUnknownCryogenIsRejectedWithAUsefulReason():

    with pytest.raises(ConditioningError, match = 'not a cryogen'):
        buildChill(cryogen = 'RP-1')

def testAnUnknownMaterialIsRejected():

    with pytest.raises(InvalidInputError, match = 'No cryogenic specific heat'):
        buildChill(material = 'unobtainium')

def testATargetBelowTheBoilingPointIsRefused():

    '''
    Boiling liquid cannot cool metal below its own saturation temperature at the vent pressure, so
    the target is unreachable by that cryogen rather than merely expensive.
    '''

    with pytest.raises(ConditioningError, match = 'below the boiling point'):
        buildChill(targetTemperature = 80.0)

def testATargetAboveTheStartTemperatureIsRefused():

    with pytest.raises(ConditioningError, match = 'nothing to chill'):
        buildChill(targetTemperature = 300.0, startTemperature = 293.15)

def testAnArchitectureWithNoViableIgniterIsRefused():

    '''
    Three restarts with no electrical power at the engine is not a hard igniter problem, it is an
    architecture that has not been closed, and there is no partial answer to return.
    '''

    with pytest.raises(IgnitionError, match = 'No igniter type survives'):
        buildSystem(startsRequired = 3, powerAvailable = False).selectIgniter()

def testADetectionWindowNeedsAResidenceTime():

    system = IgnitionSystem()
    system.setInputs({'combination': 'LOX/RP-1', 'startsRequired': 1})

    with pytest.raises(InvalidInputError, match = 'residence time is needed'):
        system.calculateDetectionWindow()

def testHelperGuardsFire():

    with pytest.raises(InvalidInputError):
        accumulatedPropellant(-1.0, 0.01)

    with pytest.raises(InvalidInputError):
        residenceTime(1.0, 0.0, 1.0)

    with pytest.raises(InvalidInputError):
        primingTime(1.0, 0.0)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms and the published sequence -- #
# ------------------------------------------------------------------------------------------------ #

def testTheMassRatioAndTheTimeRatioAreTheSameNumber():

    '''
    The identity the whole model rests on. Accumulated mass over steady chamber gas mass reduces
    exactly to start flow fraction times ignition delay over residence time, and the class returns
    both so that seeing them agree is possible.
    '''

    result = buildStart().calculateAccumulation()

    assert result['massRatio'] == pytest.approx(result['timeRatio'])

def testTheAccumulationIsLinearInBothDelayAndFlow():

    base   = buildStart(ignitionDelay = 0.010, startFlowFraction = 1.0).calculateAccumulation()
    twice  = buildStart(ignitionDelay = 0.020, startFlowFraction = 1.0).calculateAccumulation()
    halved = buildStart(ignitionDelay = 0.020, startFlowFraction = 0.5).calculateAccumulation()

    assert twice['massRatio'] == pytest.approx(2.0 * base['massRatio'])
    assert halved['massRatio'] == pytest.approx(base['massRatio'])

def testTheChamberVolumeFollowsFromTheCharacteristicLength():

    from ignitionUtils import CHARACTERISTIC_LENGTH

    start = buildStart()

    assert start.chamberVolume() == pytest.approx(
        CHARACTERISTIC_LENGTH['LOX/RP-1']['value'] * THROAT_AREA)

def testTheChamberGasDensityIsTheIdealGasLaw():

    from ignitionUtils import PROPELLANT_COMBINATIONS
    from StartTransient import UNIVERSAL_GAS_CONSTANT

    entry = PROPELLANT_COMBINATIONS['LOX/RP-1']

    expected = 10.0e6 / ((UNIVERSAL_GAS_CONSTANT / entry['molarMass'])
                         * entry['chamberTemperature'])

    assert buildStart().chamberGasDensity() == pytest.approx(expected)

def testPrimingTimeIsVolumeOverVolumetricFlow():

    priming = buildStart().calculatePriming(volumetricFlow = 0.04)

    assert priming['primingTime'] == pytest.approx(0.008 / 0.04)

def testTheDetectionWindowIsThePermittedAccumulationOverTheFlow():

    window = buildSystem(startFlowFraction = 0.25).calculateDetectionWindow()

    assert window['window'] == pytest.approx(PERMITTED_CHAMBER_FULLS * 0.00147 / 0.25)

def testTheDecayLimitConvertsThePublishedImperialRate():

    decay = buildShutdown().calculateDecayLimit()

    assert decay['referenceRate'] == pytest.approx(
        SSME_SHUTDOWN_LIMITS['thrustDecayLimit'] * NEWTON_PER_POUND_FORCE)

    assert decay['minimumDecayTime'] == pytest.approx(100.0e3 / decay['referenceRate'])

def testTheSequencingConstantsAreThePublishedOnes():

    '''
    The one hardware-level validation this sub-domain has. Every sequencing constant in the library
    has to match the registered reference, or the sub-domain is quoting a source it is not using.
    '''

    reference = START_SEQUENCES['RS-25']

    assert reference['level'] == 'hardware'

    assert SSME_START_SEQUENCE['ratedPower']       == reference['timeToRatedPower']
    assert SSME_START_SEQUENCE['mainChamberPrime'] == reference['mainChamberPrime']
    assert SSME_START_SEQUENCE['speedCheck']       == reference['speedCheckTime']

    assert SSME_SEQUENCE_TOLERANCE['timingError']  == reference['damagingTimingError']
    assert SSME_SEQUENCE_TOLERANCE['primeSpacing'] == reference['primeSpacing']

    assert SSME_SHUTDOWN_LIMITS['thrustDecayLimit'] == reference['thrustDecayLimit']
    assert SSME_SHUTDOWN_LIMITS['boiloutSafeSpeed'] == reference['boiloutSafeSpeed']

def testThePublishedStartSequenceIsMonotonic():

    '''
    A check on the transcription rather than on the engine. If a published sequence came out of
    order it was typed wrong.
    '''

    times = list(SSME_START_SEQUENCE.values())

    assert times == sorted(times)

def testTheHypergolicDelayRangeMatchesTheRegisteredReference():

    reference = IGNITION_DELAYS['MMH/NTO']

    assert IGNITION_DELAY['N2O4/MMH'] == (reference['lower'], reference['upper'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testTheResidenceTimeMatchesWhatCombustionDevicesComputes():

    '''
    Cross-domain consistency, and it is a consistency check rather than a validation.

    combustionDevices computes 1.47 ms for this chamber from the same characteristic length and
    throat area. A transient calculation and a combustion efficiency calculation need the same
    quantity, and if the two ever disagreed one of them would be describing a different chamber.
    '''

    assert buildStart().residenceTime() == pytest.approx(0.00147, abs = 1.0e-5)

def testEveryIgnitionDelayIsAHardStartAtMainstageFlow():

    '''
    The result that reframes the sub-domain, and it is not a verdict on igniters.

    At full mainstage flow every delay in the comparison exceeds the hard start threshold,
    including a three millisecond hypergolic slug on a chamber designed for 10 MPa. That is the
    reason no engine lights at mainstage flow, and it means the fix for a hard start is the flow
    schedule rather than a faster igniter.
    '''

    comparison = buildStart(startFlowFraction = 1.0).compareIgnitionDelays(
        {'hypergolic': 0.003, 'spark prompt': 0.020, 'spark marginal': 0.050})

    for name, entry in comparison['results'].items():
        assert entry['hardStart'] is True, name

def testReducingTheStartFlowIsWhatMakesAStartSurvivable():

    '''
    The same 20 ms igniter, at mainstage flow and at a tenth of it. Nothing about the igniter
    changed and the answer did.
    '''

    full    = buildStart(ignitionDelay = 0.020, startFlowFraction = 1.00).calculateAccumulation()
    reduced = buildStart(ignitionDelay = 0.020, startFlowFraction = 0.10).calculateAccumulation()

    assert full['hardStart'] is True
    assert reduced['hardStart'] is False

    assert full['massRatio'] / reduced['massRatio'] == pytest.approx(10.0)

def testAHypergolicSlugBuysAnOrderOfMagnitudeMoreStartFlow():

    '''
    What a TEA-TEB cartridge is actually for: not reliability and not energy, but permission to
    admit flow while it works.
    '''

    residence = buildStart().residenceTime()

    hypergolic = PERMITTED_CHAMBER_FULLS * residence / 0.003
    spark      = PERMITTED_CHAMBER_FULLS * residence / 0.020

    assert hypergolic / spark > 5.0
    assert min(hypergolic, 1.0) > 0.9, 'a hypergolic slug can be lit on nearly the whole flow'
    assert spark < 0.2,                'a 20 ms torch cannot'

def testDetectionCannotActInsideTheWindowAtMainstageFlow():

    '''
    The ignition detection result, and it is not the one the words suggest. The window is a mass
    budget rather than an instrumentation specification, and on a large chamber it closes before
    any sensor loop can respond.
    '''

    window = buildSystem(startFlowFraction = 1.0).calculateDetectionWindow()

    assert window['window'] < window['detectionLatency']
    assert window['detectionCanAct'] is False

def testTheFlowScheduleCanOpenTheWindowWhereDetectionCannotBeMadeFaster():

    reduced = buildSystem(startFlowFraction = 0.05).calculateDetectionWindow()

    assert reduced['detectionCanAct'] is True
    assert reduced['window'] > DETECTION_LATENCY

def testRestartRemovesTheConsumableIgniters():

    '''
    The selection axis that decides igniters in practice, and it is not energy.
    '''

    once  = buildSystem(startsRequired = 1).selectIgniter()
    thrice = buildSystem(startsRequired = 3).selectIgniter()

    assert len(thrice['viable']) < len(once['viable'])

    for name in thrice['viable']:
        assert IGNITER_TYPES[name]['needsConsumable'] is False

def testLosingPowerAtTheEngineLeavesOnlyTheHypergolicCartridge():

    selection = buildSystem(powerAvailable = False).selectIgniter()

    assert selection['viable'] == ['hypergolic slug']

def testAHypergolicCombinationHasNoIgniterToSelect():

    system = IgnitionSystem()
    system.setInputs({'combination': 'N2O4/MMH', 'startsRequired': 20})

    selection = system.selectIgniter()

    assert selection['hypergolic'] is True
    assert selection['selected'] is None

def testTheResidualImpulseIsThePlumbingNotTheRamp():

    '''
    The shutdown result. The dribble volume dominates the thrust ramp, which means the design lever
    is where the valves sit rather than how fast they close.
    '''

    residual = buildShutdown().calculateResidualImpulse()

    assert residual['dribbleFraction'] > 0.7
    assert residual['dribbleImpulse'] > residual['rampImpulse']

def testAClosedCoupledValveCutsTheResidualImpulse():

    far   = buildShutdown(feedVolume = 0.016).calculateResidualImpulse()
    close = buildShutdown(feedVolume = 0.004).calculateResidualImpulse()

    assert close['totalImpulse'] < far['totalImpulse']
    assert close['scatter']      < far['scatter']

def testTheScatterIsSmallerThanTheImpulseAndItIsTheOneThatMatters():

    '''
    Recorded as a test because it is the claim the shutdown document makes, and because the scatter
    figure is unvalidated while the conclusion drawn from it is not sensitive to its value.
    '''

    residual = buildShutdown().calculateResidualImpulse()

    assert residual['scatter'] < residual['totalImpulse']
    assert residual['scatter'] > 0.0

def testTheDecayRateLimitBelongsToTheVehicle():

    '''
    A documentation test. The registered reference has to keep saying that the 700,000 lbf/s figure
    is an orbiter structural limit, because the whole point of carrying it is that it does not
    transfer to another vehicle.
    '''

    note = START_SEQUENCES['RS-25']['boundingUse']

    assert 'vehicle structural limit' in note
    assert 'no other vehicle' in note

def testTheHydrogenChillDownBandIsSeveralTimesWiderThanTheOxygenOne():

    '''
    The chill-down result. For oxygen the hardware mass decides the answer; for hydrogen the method
    does, and that is why the two literatures look completely different.
    '''

    comparison = buildChill().compareCryogens(['LOX', 'LCH4', 'LH2'])

    bands = comparison['bandRatio']

    assert bands['LH2'] > 4.0 * 1.0
    assert bands['LH2'] > 3.0 * bands['LOX']
    assert comparison['widestBand'] == 'LH2'

    assert comparison['results']['LOX']['methodDominated'] is False
    assert comparison['results']['LH2']['methodDominated'] is True

def testHydrogenVapourCarriesMostOfTheAvailableCooling():

    '''
    The mechanism behind the band. Hydrogen's latent heat is unremarkable and its vapour specific
    heat is enormous, so almost all of the cooling available is in the gas.
    '''

    hydrogen = buildChill(cryogen = 'LH2').calculateMass()
    oxygen   = buildChill(cryogen = 'LOX').calculateMass()

    assert hydrogen['sensibleFraction'] > 0.8
    assert oxygen['sensibleFraction']   < 0.6

def testCompareCryogensRestoresTheOriginalState():

    '''
    It mutates the instance to run each case. If it did not put it back, every call after a
    comparison would silently answer for the last cryogen in the list.
    '''

    chill = buildChill(cryogen = 'LOX')

    before = chill.calculateMass()['upperBound']

    chill.compareCryogens(['LOX', 'LH2'])

    assert chill.cryogen == 'LOX'
    assert chill.calculateMass()['upperBound'] == pytest.approx(before)

def testTheChillDownSpecificHeatsAreNotTheRoomTemperatureOnes():

    '''
    Regression guard on a correction that would be easy to undo while tidying up.

    Specific heat falls steeply below about 100 K. Using the room-temperature values from
    common/materials.py over the whole chill-down range overstates the stored enthalpy, and
    therefore the conditioning propellant, by roughly a third for stainless.
    '''

    from materials import materialProperties

    # 304L is the nearest entry in the shared table, and it carries no specific heat at all
    assert 'specificHeat' not in materialProperties('304L'), (
        'common/materials.py has gained a specific heat; check it is not being used over the '
        'cryogenic range before deleting this guard')

    # the mean over the chill-down range, well below the room-temperature value for stainless of
    # roughly 500 J/(kg K)
    assert MEAN_SPECIFIC_HEAT['stainless 304'] < 450.0

    # and the ordering between materials survives the correction
    assert MEAN_SPECIFIC_HEAT['aluminium 6061'] > MEAN_SPECIFIC_HEAT['stainless 304']
    assert MEAN_SPECIFIC_HEAT['titanium 6-4']   > MEAN_SPECIFIC_HEAT['inconel 718']

def testTheDesignSpacingAndTheDamagingErrorAreTheSameNumber():

    '''
    The sub-domain's central claim about how little margin a start sequence has, asserted against
    the published source rather than against itself.
    '''

    assert SSME_SEQUENCE_TOLERANCE['primeSpacing'] == SSME_SEQUENCE_TOLERANCE['timingError']

    primes = [SSME_START_SEQUENCE['fuelPreburnerPrime'],
              SSME_START_SEQUENCE['mainChamberPrime'],
              SSME_START_SEQUENCE['oxidiserPreburnerPrime']]

    spacings = np.diff(primes)

    assert np.allclose(spacings, SSME_SEQUENCE_TOLERANCE['primeSpacing'], atol = 1.0e-9)

def testASequenceTighterThanTheReferenceToleranceIsFlaggedNotRefused():

    '''
    A tight sequence is a warning, not an error. It may be a smaller and more forgiving engine, and
    the class says so rather than pretending to know.
    '''

    check = buildStart().checkSequence({'a': 0.0, 'b': 0.05, 'c': 0.5})

    assert check['ordered'] is True
    assert check['insideReferenceTolerance'] is False

def testTheUnvalidatedRegisterNamesWhatThisSubDomainCannotCheck():

    '''
    The register existing is more useful than it being short. Four entries, and each one names what
    depends on it.
    '''

    for key in ('ignitionOverpressureBound', 'igniterEnergy', 'shutdownImpulseScatter',
                'chillDownMeanSpecificHeat'):

        entry = UNVALIDATED[key]

        assert 'ignitionAndStart' in entry['domain']
        assert entry['consequence']
        assert entry['nextStep']

def testBooleanFlagsAreRealPythonBooleans():

    flags = [buildStart().calculateAccumulation()['hardStart'],
             buildSystem().calculateDetectionWindow()['detectionCanAct'],
             buildShutdown().calculateDecayLimit()['withinLimit'],
             buildChill().calculateMass()['methodDominated'],
             buildStart().checkSequence({'a': 0.0, 'b': 1.0})['ordered']]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testReportsRunForEveryClass():

    assert 'START TRANSIENT'    in buildStart().generateReport()
    assert 'IGNITION SYSTEM'    in buildSystem().generateReport()
    assert 'SHUTDOWN TRANSIENT' in buildShutdown().generateReport()
    assert 'CHILL DOWN'         in buildChill().generateReport()

# ------------------------------------------------------------------------------------------------ #
# -- Cryogenic specific heat, against the NIST curve fits -- #
# ------------------------------------------------------------------------------------------------ #

def testSpecificHeatReproducesRoomTemperatureHandbookValues():

    '''
    The NIST cryogenic fits run to 300 K, where the answer is a number everybody knows. 304
    stainless is about 477 J/(kg K) at room temperature and 6061 aluminium about 896, and the fits
    state 5 per cent errors against their own data, so agreement inside that band is the check
    available.
    '''

    assert specificHeat('stainless 304', 293.15) == pytest.approx(477.0, rel = 0.05)
    assert specificHeat('aluminium 6061', 293.15) == pytest.approx(896.0, rel = 0.06)

def testTheTwoStainlessSegmentsAgreeAtTheirJoint():

    '''
    316 is published as two fits meeting at 50 K. Neither set can hide a transcription error in the
    other, because a wrong coefficient anywhere shows up as a step at the joint. This is the only
    free check on nine transcribed numbers in the repository and it costs one assertion.
    '''

    entry = CRYOGENIC_SPECIFIC_HEAT_FITS['stainless 316']

    lower, upper = entry['segments']

    def evaluate(coefficients, temperature):
        exponent = np.log10(temperature)
        return 10.0 ** sum(value * exponent ** power
                           for power, value in enumerate(coefficients))

    below = evaluate(lower['coefficients'], 50.0)
    above = evaluate(upper['coefficients'], 50.0)

    assert below == pytest.approx(above, rel = 0.005), \
        f'the two 316 fits give {below:.2f} and {above:.2f} at their shared 50 K bound'

def testSpecificHeatFallsSteeplyBelowOneHundredKelvin():

    '''
    The reason the whole module exists. If specific heat were flat, a room-temperature value would
    be fine and the chill-down would be a one-line multiplication.
    '''

    for material in ('stainless 304', 'stainless 316', 'aluminium 6061'):

        warm = specificHeat(material, 293.15)
        cold = specificHeat(material, 90.19)

        assert cold < 0.6 * warm, \
            f'{material} at 90 K is {cold / warm:.2f} of its room temperature value'

def testExtrapolationIsRefusedRatherThanClamped():

    '''
    A polynomial in log10(T) leaves the physical values quickly outside its range, and a clamped
    specific heat produces a plausible chill-down mass rather than an error.
    '''

    with pytest.raises(InvalidInputError):
        specificHeat('stainless 304', 350.0)

    with pytest.raises(InvalidInputError):
        specificHeat('stainless 304', 2.0)

def testAMaterialWithNoNistCurveIsNamedRatherThanSubstituted():

    '''
    Ti-6Al-4V and Inconel 718 have thermal conductivity and linear expansion in the NIST database
    and no specific heat. Guessing one from a neighbouring alloy would be worse than saying so.
    '''

    for material in ('titanium 6-4', 'inconel 718'):

        assert material in UNFITTED_SPECIFIC_HEAT

        with pytest.raises(InvalidInputError):
            specificHeat(material, 150.0)

def testTheMeanIsTheIntegralAndNotTheMidpointValue():

    '''
    A mean specific heat has to reproduce the enthalpy when multiplied by the span, which the value
    at the midpoint does not. The curve is concave over this range, flattening as it approaches the
    Dulong-Petit plateau, so the midpoint value sits three per cent ABOVE the true mean and using
    it would overstate the chill-down.
    '''

    low, high = 90.19, 293.15

    mean     = meanSpecificHeat('stainless 304', low, high)
    midpoint = specificHeat('stainless 304', 0.5 * (low + high))

    assert enthalpyChange('stainless 304', 1.0, low, high) == pytest.approx(mean * (high - low),
                                                                           rel = 1.0e-9)
    assert midpoint > mean
    assert midpoint / mean == pytest.approx(1.031, rel = 0.01)

def testTheMeanTableIsDerivedFromTheCurves():

    '''
    MEAN_SPECIFIC_HEAT is computed at import over the reference range rather than written down, so
    there is nothing in it that can drift from the curves. This asserts that it was, which is what
    stops somebody replacing the derivation with the numbers it produced.
    '''

    for material in ('stainless 304', 'stainless 316', 'aluminium 6061', 'aluminium 2219'):

        assert MEAN_SPECIFIC_HEAT[material] == pytest.approx(
            meanSpecificHeat(material, *REFERENCE_CHILL_RANGE), rel = 1.0e-9)

def testNoMeanIsTheRoomTemperatureValue():

    '''
    The correction this table exists to make is that specific heat is not its room-temperature
    value over a chill-down. A tidy-up that replaced these with common/materials.py values would
    overstate every chill-down in the repository, so the difference is asserted rather than
    commented.
    '''

    for material in ('stainless 304', 'aluminium 6061'):
        assert MEAN_SPECIFIC_HEAT[material] < 0.9 * specificHeat(material, 293.15)

def testASingleMeanCannotCoverAllFourCryogens():

    '''
    The result that argues for integrating rather than tabulating. The same stainless line chilled
    for methane and for hydrogen has enthalpy-averaged specific heats a quarter apart, so the
    material alone does not determine the mean and the cryogen has to be in the calculation.
    '''

    means = {}

    for cryogen in CRYOGENS:

        component = ChillDown()
        component.setInputs({'cryogen': cryogen, 'material': 'stainless 304', 'metalMass': 50.0})

        means[cryogen] = component.effectiveSpecificHeat()

    assert max(means.values()) / min(means.values()) > 1.2, \
        f'the spread across cryogens is only {max(means.values()) / min(means.values()):.2f}'

    assert means['LCH4'] > means['LOX'] > means['LN2'] > means['LH2'], \
        'the mean has to fall as the range extends further down'

def testHydrogenChillDownWasOverstatedByAConstantMean():

    '''
    The direction of the error the old constant made. A mean quoted over the oxygen range applied
    to a hydrogen chill-down overstates the stored enthalpy, because it never sees the part of the
    curve below 90 K where specific heat collapses.
    '''

    component = ChillDown()
    component.setInputs({'cryogen': 'LH2', 'material': 'stainless 304', 'metalMass': 50.0})

    integrated = component.effectiveSpecificHeat()

    assert integrated < MEAN_SPECIFIC_HEAT['stainless 304']

    overstatement = MEAN_SPECIFIC_HEAT['stainless 304'] / integrated - 1.0

    assert 0.10 < overstatement < 0.25, \
        f'the constant mean overstates the hydrogen case by {overstatement:.1%}'
