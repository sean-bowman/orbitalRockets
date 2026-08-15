# -- Tests for the electricalPower classes -- #

'''

Tiered tests for the four power classes.

Tier 1 covers the contract. Two refusals matter here: a harness that cannot keep its load above
minimum voltage, and a battery that cannot deliver the current whatever its energy.

Tier 2 validates against the AWG definition, which is the tightest agreement in this repository:
computed conductor resistances reproduce published tables to four significant figures. That matters
because the domain's central result, that voltage drop rather than ampacity chooses the gauge, is a
pure resistance calculation.

Tier 3 covers the results the domain produces: the energy and peak drivers are different loads, the
battery nameplate is close to twice the energy delivered, copper falls with the square of bus
voltage, and peak-and-hold returns three quarters of the valve power.

Author: Sean Bowman
Date:   10/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'electricalPowerLibrary'))
sys.path.insert(0, ROOT)

from powerUtils import (BATTERY_CHEMISTRIES, DEPTH_OF_DISCHARGE, TEMPERATURE_CAPACITY_FACTOR,
                        SINGLE_WIRE_AMPACITY, BUNDLE_DERATING, ALTITUDE_DERATING,
                        COPPER_RESISTIVITY, COPPER_TEMPERATURE_COEFFICIENT,
                        AWG_REFERENCE_GAUGE, AWG_REFERENCE_DIAMETER, AWG_RATIO, AWG_STEPS,
                        wireDiameter, wireArea, wireResistance, voltageDrop, interpolateFactor,
                        InvalidInputError, ElectricalPowerError, HarnessError, PowerBudgetError)
from PowerBudget import PowerBudget, DISTRIBUTION_EFFICIENCY
from Battery import Battery, PACK_FRACTION
from HarnessSizing import HarnessSizing, ROUTING_ALLOWANCE
from SolenoidDrive import SolenoidDrive

from validation.referenceCases import (WIRE_GAUGE, UNVALIDATED, BATTERY_CELLS,
                                       REFERENCE_KINDS, VALIDATION_LEVELS)

PHASES = [{'name': 'pad hold', 'duration': 7200.0},
          {'name': 'ascent',   'duration': 540.0},
          {'name': 'burn',     'duration': 60.0}]

LOADS = [{'name': 'avionics', 'power': 35.0,
          'dutyCycle': {'pad hold': 1.0, 'ascent': 1.0, 'burn': 1.0}},
         {'name': 'heaters',  'power': 42.0,
          'dutyCycle': {'pad hold': 0.35, 'ascent': 0.40, 'burn': 0.20}},
         {'name': 'actuators', 'power': 180.0,
          'dutyCycle': {'pad hold': 0.0, 'ascent': 0.15, 'burn': 0.30}}]

def buildBudget(**overrides) -> PowerBudget:

    inputs = {'loads': [dict(load, dutyCycle = dict(load['dutyCycle'])) for load in LOADS],
              'phases': [dict(phase) for phase in PHASES]}
    inputs.update(overrides)

    budget = PowerBudget()
    budget.setInputs(inputs)

    return budget

def buildBattery(**overrides) -> Battery:

    inputs = {'chemistry': 'lithium ion', 'busVoltage': 28.0, 'missionEnergy': 900.0e3,
              'temperature': -20.0, 'cycleClass': 'single use', 'peakPower': 450.0}
    inputs.update(overrides)

    battery = Battery()
    battery.setInputs(inputs)

    return battery

def buildHarness(**overrides) -> HarnessSizing:

    inputs = {'busVoltage': 28.0, 'current': 3.0, 'length': 12.0,
              'bundleSize': 15, 'altitude': 30000.0}
    inputs.update(overrides)

    harness = HarnessSizing()
    harness.setInputs(inputs)

    return harness

def buildSolenoid(**overrides) -> SolenoidDrive:

    inputs = {'busVoltage': 28.0, 'coilResistance': 45.0, 'coilInductance': 0.12,
              'coilTemperature': 100.0, 'holdFraction': 0.50, 'openDuration': 60.0}
    inputs.update(overrides)

    valve = SolenoidDrive()
    valve.setInputs(inputs)

    return valve

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSpecificErrorsSubclassTheDomainBase():

    for error in (HarnessError, PowerBudgetError):
        assert issubclass(error, ElectricalPowerError)

def testAGaugeOutsideTheDefinitionIsRejected():

    with pytest.raises(InvalidInputError, match = 'between 0 and 40'):
        wireDiameter(50)

def testAHarnessThatCannotHoldItsVoltageIsRefused():

    '''
    Refused rather than reported, because a load below its minimum operating voltage is a load that
    does not work, and the message names the real fix: it is a run length problem rather than a
    wire problem.
    '''

    with pytest.raises(HarnessError, match = 'run length problem'):
        buildHarness(length = 400.0).sizeGauge()

def testAHarnessThatCannotCarryItsCurrentIsRefused():

    with pytest.raises(HarnessError, match = 'derating is doing the work'):
        buildHarness(current = 60.0, length = 0.5, bundleSize = 60).sizeGauge()

def testAHarnessMassNeedsRunsRatherThanAFraction():

    with pytest.raises(InvalidInputError, match = 'fraction of'):
        buildHarness().calculateMass([])

def testAnUnknownConnectorIsRejected():

    with pytest.raises(InvalidInputError, match = 'Unknown connector type'):
        buildHarness().calculateMass([{'gauge': 20, 'length': 1.0, 'count': 2}],
                                     {'edge connector': 4})

def testABatteryBelowItsTemperatureLimitIsRefused():

    '''
    Below the low temperature limit the capacity model does not apply and the cell may not deliver
    at all, so it is refused rather than extrapolated.
    '''

    with pytest.raises(PowerBudgetError, match = 'low temperature limit'):
        buildBattery(temperature = -40.0)

def testABatteryThatCannotDeliverTheCurrentIsRefused():

    '''
    A pack sized on energy alone can be unable to supply the current, and that is a different
    failure from being slightly small.
    '''

    with pytest.raises(PowerBudgetError, match = 'cannot supply'):
        buildBattery(chemistry = 'lithium thionyl chloride', peakPower = 450.0).checkDischargeRate()

def testADischargeCheckNeedsAPeakPower():

    with pytest.raises(InvalidInputError, match = 'peak power is needed'):
        buildBattery(peakPower = np.nan).checkDischargeRate()

def testADutyCycleAgainstAMissingPhaseIsRejected():

    '''
    A duty cycle against a phase that does not exist is silently ignored in most tools, and its
    energy disappears.
    '''

    loads = [dict(LOADS[0], dutyCycle = {'orbit': 1.0})]

    with pytest.raises(InvalidInputError, match = 'not in the phase list'):
        buildBudget(loads = loads)

def testADuplicateLoadNameIsRejected():

    loads = [dict(LOADS[0], dutyCycle = dict(LOADS[0]['dutyCycle'])),
             dict(LOADS[0], dutyCycle = dict(LOADS[0]['dutyCycle']))]

    with pytest.raises(InvalidInputError, match = 'Duplicate load name'):
        buildBudget(loads = loads)

def testABudgetWithNoPhasesIsRejected():

    with pytest.raises(InvalidInputError, match = 'at least one phase'):
        buildBudget(phases = [])

def testADutyCycleOutsideTheUnitIntervalIsRejected():

    loads = [dict(LOADS[0], dutyCycle = {'pad hold': 1.5, 'ascent': 1.0, 'burn': 1.0})]

    with pytest.raises(InvalidInputError, match = r'\[0, 1\]'):
        buildBudget(loads = loads)

def testAFlybackClampAtOrBelowTheBusIsRefused():

    '''
    A clamp at or below the supply conducts continuously while the valve is driven, which is a
    short across the drive rather than a suppression network.
    '''

    with pytest.raises(ElectricalPowerError, match = 'short across the drive'):
        buildSolenoid(clampVoltage = 20.0)

def testAnInrushCalculationNeedsAnInductance():

    with pytest.raises(InvalidInputError, match = 'coil inductance is needed'):
        buildSolenoid(coilInductance = np.nan).calculateInrush()

def testAStrategyComparisonNeedsAnOpenDuration():

    with pytest.raises(InvalidInputError, match = 'open duration is needed'):
        buildSolenoid(openDuration = np.nan).compareDriveStrategies()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: the AWG definition and closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testTheWireDiameterMatchesTheAwgDefinition():

    assert wireDiameter(AWG_REFERENCE_GAUGE) == pytest.approx(AWG_REFERENCE_DIAMETER)

    # each gauge step multiplies the diameter by the 39th root of 92
    step = AWG_RATIO ** (1.0 / AWG_STEPS)

    assert wireDiameter(19) / wireDiameter(20) == pytest.approx(step)

def testComputedResistanceReproducesPublishedTables():

    '''
    The tightest agreement anywhere in this repository, and it is the anchor the domain's central
    result rests on: voltage drop is a pure resistance calculation.
    '''

    published = WIRE_GAUGE['AWG definition']['publishedResistance']

    assert WIRE_GAUGE['AWG definition']['level'] == 'standard'

    for gauge, expected in published.items():
        assert wireResistance(gauge, 1000.0) == pytest.approx(expected, rel = 0.001), gauge

def testTheLibraryConstantsMatchTheRegisteredDefinition():

    reference = WIRE_GAUGE['AWG definition']

    assert AWG_REFERENCE_GAUGE == reference['referenceGauge']
    assert AWG_REFERENCE_DIAMETER == reference['referenceDiameter']
    assert AWG_RATIO == reference['ratio']
    assert AWG_STEPS == reference['steps']
    assert COPPER_RESISTIVITY == reference['copperResistivity']

def testResistanceRisesWithTemperature():

    hot = wireResistance(20, 1.0, 100.0)
    cold = wireResistance(20, 1.0, 20.0)

    assert hot / cold == pytest.approx(1.0 + COPPER_TEMPERATURE_COEFFICIENT * 80.0)

def testVoltageDropCountsBothConductors():

    '''
    The factor of two is the part that gets forgotten: current goes out along one wire and returns
    along another.
    '''

    assert voltageDrop(20, 10.0, 2.0) == pytest.approx(2.0 * wireResistance(20, 10.0) * 2.0)

def testAreaScalesWithTheSquareOfDiameter():

    assert wireArea(20) == pytest.approx(np.pi / 4.0 * wireDiameter(20) ** 2)

    # three gauge steps double the area
    assert wireArea(17) / wireArea(20) == pytest.approx(2.0, rel = 0.02)

def testInterpolationClampsRatherThanExtrapolates():

    keys = sorted(BUNDLE_DERATING)

    assert interpolateFactor(BUNDLE_DERATING, -5.0) == BUNDLE_DERATING[keys[0]]
    assert interpolateFactor(BUNDLE_DERATING, 500.0) == BUNDLE_DERATING[keys[-1]]

def testTheEnergyRollupIsTheSumOfItsParts():

    rollup = buildBudget().rollUp()

    byPhase = sum(entry['energy'] for entry in rollup['byPhase'].values())
    byLoad  = sum(entry['energy'] for entry in rollup['byLoad'].values())

    assert byPhase == pytest.approx(byLoad)
    assert rollup['deliveredEnergy'] == pytest.approx(byPhase)

def testSourceEnergyExceedsDeliveredByTheDistributionLoss():

    rollup = buildBudget().rollUp()

    assert rollup['sourceEnergy'] == pytest.approx(
        rollup['deliveredEnergy'] / DISTRIBUTION_EFFICIENCY)

def testTheBatteryDeratingIsTheProductOfItsFactors():

    derating = buildBattery().calculateDerating()

    assert derating['usableFraction'] == pytest.approx(
        DEPTH_OF_DISCHARGE['single use']
        * interpolateFactor(TEMPERATURE_CAPACITY_FACTOR, -20.0))

def testSolenoidPowerGoesAsTheSquareOfCurrent():

    drive = buildSolenoid(holdFraction = 0.5).calculateDrive()

    assert drive['holdPower'] / drive['continuousPower'] == pytest.approx(0.25)
    assert drive['powerSaving'] == pytest.approx(0.75)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testVoltageDropChoosesTheGaugeNotAmpacity():

    '''
    The domain's central result. On a launch vehicle harness the run is long relative to the
    current, so voltage drop scales with length and ampacity does not.
    '''

    sized = buildHarness().sizeGauge()

    assert sized['binding'] == 'voltage drop'
    assert sized['dropGauge'] < sized['ampacityGauge'], 'lower AWG is heavier wire'
    assert sized['governing'] == sized['dropGauge']

def testTheGaugeChosenOnAmpacityWouldNotFunction():

    sized = buildHarness()

    result = sized.sizeGauge()

    ampacityDrop = result['detail'][result['ampacityGauge']]['drop']

    assert ampacityDrop > result['allowedDrop']
    assert ampacityDrop / 28.0 > 0.05, 'the load would be several per cent low'

def testAShortRunIsAmpacityLimitedInstead():

    '''
    The other regime, and it confirms the result is about geometry rather than about the model
    always saying the same thing.
    '''

    sized = buildHarness(length = 0.5, current = 8.0).sizeGauge()

    assert sized['binding'] in ('ampacity', 'both')

def testBundleDeratingIsLargerThanAltitudeDerating():

    harness = buildHarness()

    derated = harness.deratedAmpacity(20)

    assert derated['bundleFactor'] < derated['altitudeFactor']

def testCopperFallsRoughlyWithTheSquareOfBusVoltage():

    '''
    Power is fixed, so current falls with voltage and the allowed drop rises with it. Both move the
    same way, which is the cleanest argument for a higher bus.
    '''

    comparison = buildHarness().compareBusVoltage([28.0, 56.0])

    low  = comparison['results'][28.0]
    high = comparison['results'][56.0]

    ratio = low['area'] / high['area']

    assert ratio > 2.0, 'doubling the bus should more than halve the copper'

def testHarnessMassIsCountedAndIncludesRouting():

    runs = [{'gauge': 20, 'length': 10.0, 'count': 4}]

    mass = buildHarness().calculateMass(runs)

    bare = wireArea(20) * 10.0 * 8960.0 * 4

    assert mass['wireMass'] > bare * (1.0 + ROUTING_ALLOWANCE), 'insulation adds to routing'

def testConnectorsAreASignificantShareOfHarnessMass():

    runs = [{'gauge': 14, 'length': 12.0, 'count': 2},
            {'gauge': 20, 'length': 9.0,  'count': 24},
            {'gauge': 24, 'length': 14.0, 'count': 48}]

    connectors = {'circular, 8 way': 12, 'circular, 19 way': 6,
                  'circular, 37 way': 4, 'power, 4 way': 3}

    mass = buildHarness().calculateMass(runs, connectors)

    assert mass['connectorCount'] == 25
    assert mass['connectorMass'] / mass['totalMass'] > 0.1

def testTheNameplateIsNearlyTwiceTheEnergyDelivered():

    '''
    Depth of discharge and cold multiply, and neither is a margin: they are the difference between
    what the label says and what the battery does.
    '''

    sized = buildBattery().sizePack()

    assert sized['oversizeFactor'] > 1.7
    assert sized['derating']['usableFraction'] < 0.7

def testWarmAndSingleUseIsTheBestCaseAndCycledAndColdTheWorst():

    best  = buildBattery(temperature = 20.0, cycleClass = 'single use').sizePack()
    worst = buildBattery(temperature = -20.0, cycleClass = 'many cycles').sizePack()

    assert worst['packMass'] / best['packMass'] > 2.0, (
        'the two derations together are worth more than a factor of two')

def testTheDischargeRateRatherThanEnergyDecidesTheChemistry():

    '''
    The only place in the battery calculation where the chemistry choice actually changes the
    answer, which is the opposite of how the trade is usually presented.
    '''

    comparison = buildBattery().compareChemistries()

    results = comparison['results']

    # the highest specific energy chemistry is the lightest and cannot supply the current
    assert results['lithium thionyl chloride']['packMass'] < results['lithium ion']['packMass']
    assert results['lithium thionyl chloride']['rateAdequate'] is False

    assert 'lithium thionyl chloride' not in comparison['viable']

def testTheEnergyAndPeakDriversAreDifferentLoads():

    '''
    The energy driver sizes the battery and the peak driver sizes the harness and the switching, so
    effort spent on one buys nothing on the other.
    '''

    drivers = buildBudget().identifyDrivers()

    assert drivers['sameLoad'] is False
    assert drivers['energyDriver'] == 'avionics'
    assert drivers['peakDriver'] == 'actuators'

def testAContinuousSmallLoadBeatsALargerCyclingOne():

    '''
    The result the worked example was corrected to. Duty cycle multiplies and power does not, so a
    35 W load at full duty consumes more than a 42 W load at a third.
    '''

    rollup = buildBudget().rollUp()

    assert rollup['byLoad']['avionics']['power'] < rollup['byLoad']['heaters']['power']
    assert rollup['byLoad']['avionics']['energy'] > rollup['byLoad']['heaters']['energy']

def testTheHeaterDutyCycleSwingExceedsATypicalEnergyMargin():

    '''
    The heater is not the largest load and it is the largest uncertainty, because its duty cycle is
    a thermal assumption rather than an electrical quantity.
    '''

    sensitivity = buildBudget().dutyCycleSensitivity('heaters')

    assert sensitivity['spanFraction'] > 0.25

def testAnUnknownLoadCannotBeSwept():

    with pytest.raises(InvalidInputError, match = 'No load named'):
        buildBudget().dutyCycleSensitivity('radiator')

def testTheHotCoilIsTheDesignCase():

    '''
    Copper gains about 0.4 per cent per kelvin, so a hot coil pulls less current and makes less
    force. A valve that works cold and marginally hot is found on a hot day.
    '''

    drive = buildSolenoid(coilTemperature = 100.0).calculateDrive()

    assert drive['hotResistance'] > drive['coldResistance']
    assert drive['pullInHot'] < drive['pullInCold']
    assert drive['forceRatio'] < 0.65

def testPeakAndHoldReturnsThreeQuartersOfTheValvePower():

    strategies = buildSolenoid(holdFraction = 0.5).compareDriveStrategies()

    assert strategies['powerSaving'] == pytest.approx(0.75)
    assert strategies['holdEnergy'] < strategies['continuousEnergy']

def testAHigherClampClosesTheValveFaster():

    '''
    The clamp voltage sets the valve closing time, so a suppression network chosen on component
    stress alone chooses a valve response time by accident.
    '''

    slow = buildSolenoid(clampVoltage = 35.0).calculateFlyback()
    fast = buildSolenoid(clampVoltage = 100.0).calculateFlyback()

    assert fast['clampTime'] < slow['clampTime']
    assert fast['speedFactor'] > slow['speedFactor']

def testTheDiodeOnlyDecayIsMuchSlowerThanAClamp():

    flyback = buildSolenoid().calculateFlyback()

    assert flyback['speedFactor'] > 5.0

def testBooleanFlagsAreRealPythonBooleans():

    flags = [buildBudget().identifyDrivers()['sameLoad'],
             buildBattery().checkDischargeRate()['adequate'],
             buildBattery().compareChemistries()['results']['lithium ion']['rateAdequate']]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testTheUnvalidatedRegisterNamesWhatThisDomainCannotCheck():

    for key in ('wireAmpacity', 'batteryDerating', 'harnessRoutingAllowance'):

        entry = UNVALIDATED[key]

        assert 'electricalPower' in entry['domain']
        assert entry['consequence']
        assert entry['nextStep']

def testReportsRunForEveryClass():

    assert 'POWER BUDGET'    in buildBudget().generateReport()
    assert 'BATTERY'         in buildBattery().generateReport()
    assert 'HARNESS'         in buildHarness().generateReport()
    assert 'SOLENOID DRIVE'  in buildSolenoid().generateReport()


# ------------------------------------------------------------------------------------------------ #
# -- A real cell, against the chemistry table -- #
# ------------------------------------------------------------------------------------------------ #

def testTheCellEnergyDensitiesReproduceFromTheRatedCapacity():

    '''
    Both published energy densities reproduce exactly from the rated capacity and the bare cell
    dimensions, and neither reproduces from the typical capacity.

    That is worth an assertion because it says which capacity a datasheet energy density is built
    from. The rated and typical figures differ by five per cent, and a nameplate density multiplied
    by a typical capacity counts that five per cent twice.
    '''

    cell = BATTERY_CELLS['Panasonic NCR18650BF']

    ratedEnergy = cell['ratedCapacity'] * cell['nominalVoltage']

    volume = np.pi * (cell['diameter'] / 2.0) ** 2 * cell['height'] * 1000.0     # [l]

    assert ratedEnergy / cell['maximumMass'] == pytest.approx(
        cell['gravimetricEnergyDensity'], rel = 0.002)

    assert ratedEnergy / volume == pytest.approx(cell['volumetricEnergyDensity'], rel = 0.002)

    typicalEnergy = cell['typicalCapacity'] * cell['nominalVoltage']

    assert typicalEnergy / cell['maximumMass'] > 1.04 * cell['gravimetricEnergyDensity'], \
        'the typical capacity is not what the published density is built from'

def testTheChemistryTableIsConservativeAgainstARealCell():

    '''
    The chemistry tables are representative of a class rather than of a part, which is the right
    shape for a sizing library and is also a claim nothing checked. One real cell cannot validate a
    class figure and it can say whether the class figure errs the right way, which is the only
    question a representative number has to answer.
    '''

    cell = BATTERY_CELLS['Panasonic NCR18650BF']

    classFigure = BATTERY_CHEMISTRIES['lithium ion']['specificEnergy']

    assert classFigure < cell['gravimetricEnergyDensity'], \
        'a class figure covering older and higher rate chemistries has to sit below a current cell'

    shortfall = 1.0 - classFigure / cell['gravimetricEnergyDensity']

    assert 0.10 < shortfall < 0.30, \
        f'the class figure is {shortfall:.0%} below the cell, which is outside the useful band'

def testTheDischargeTemperatureLimitMatchesTheCell():

    '''
    The one place the chemistry table and the datasheet state the same quantity, so it is the one
    place they can be checked against each other directly.
    '''

    cell = BATTERY_CELLS['Panasonic NCR18650BF']

    assert BATTERY_CHEMISTRIES['lithium ion']['lowTemperatureLimit'] == \
        cell['dischargeTemperatureRange'][0]

def testTheChargeLimitIsTighterThanAnythingTheLibraryCarries():

    '''
    The gap the datasheet exposed. A lithium ion cell discharges thirty degrees colder than it can
    be charged, and that is a hard limit rather than a derating curve, so no capacity factor
    expresses it.

    The consequence is operational rather than a sizing one: a vehicle cold soaked on the pad can
    run its battery and cannot top it up. This asserts the asymmetry so that it is recorded rather
    than remembered.
    '''

    cell = BATTERY_CELLS['Panasonic NCR18650BF']

    chargeFloor    = cell['chargeTemperatureRange'][0]
    dischargeFloor = cell['dischargeTemperatureRange'][0]

    assert chargeFloor > dischargeFloor
    assert chargeFloor - dischargeFloor == pytest.approx(30.0)

    # The library derates capacity down to -40 C and says nothing about charging at any of them.
    assert min(TEMPERATURE_CAPACITY_FACTOR) < chargeFloor

def testTheCellReferenceCarriesItsProvenanceAndLevel():

    for name, entry in BATTERY_CELLS.items():

        assert entry['source'], name
        assert entry['kind'] in REFERENCE_KINDS, name
        assert entry['level'] in VALIDATION_LEVELS, name
        assert entry['scopeNote'], name
