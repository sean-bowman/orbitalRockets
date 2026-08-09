# -- Tests for the turbomachinery classes -- #

'''

Tiered tests for the three turbomachinery classes.

Tier 1 covers the contract: a tank below its own vapour pressure, a pressure ratio of one, a head
coefficient above one, and the geometries that extract no work.

Tier 2 validates against closed forms. The specific speed groups against their definitions, the US
customary conversion against a hand-computed case, the impulse turbine utilisation against its
classical optimum, and the spouting velocity against the isentropic drop.

Tier 3 covers self-consistency and the physical direction of every effect, and the three couplings
this sub-domain exists to expose: shaft speed against cavitation, shaft speed against blade speed
ratio, and the tank pressure that falls out of both.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'turbomachineryLibrary'))

from turbomachineryUtils import (PUMP_GEOMETRY, HEAD_COEFFICIENT, SUCTION_SPECIFIC_SPEED,
                                 BLADE_SPEED_RATIO_OPTIMUM, TURBINE_INLET_LIMITS,
                                 US_SPECIFIC_SPEED_PER_DIMENSIONLESS, BEARING_DN_LIMIT, GRAVITY,
                                 specificSpeed, suctionSpecificSpeed, toUsSpecificSpeed,
                                 headFromPressureRise, tipSpeedFromHead, geometryForSpecificSpeed,
                                 InvalidInputError, PumpError, CavitationError, TurbineError)
from Pump import Pump, IMPELLER_TIP_SPEED_LIMIT, PEAK_EFFICIENCY
from Inducer import Inducer, NPSH_MARGIN, THERMODYNAMIC_SUPPRESSION
from Turbine import Turbine, NOZZLE_ANGLE, MECHANICAL_LOSS_FACTOR, BLADE_TIP_SPEED_LIMIT

# ------------------------------------------------------------------------------------------------ #
# -- Builders, on the worked example engine's turbopump -- #
# ------------------------------------------------------------------------------------------------ #

def buildPump(**overrides) -> Pump:

    inputs = {'propellant': 'RP-1', 'density': 810.0, 'massFlow': 10.34,
              'pressureRise': 12.5e6, 'shaftSpeed': 30000.0}
    inputs.update(overrides)

    pump = Pump()
    pump.setInputs(inputs)

    return pump

def buildInducer(**overrides) -> Inducer:

    inputs = {'propellant': 'LOX', 'density': 1141.0, 'massFlow': 26.47,
              'shaftSpeed': 30000.0, 'vapourPressure': 101325.0,
              'staticHead': 3.0, 'lineLoss': 5.0}
    inputs.update(overrides)

    inducer = Inducer()
    inducer.setInputs(inputs)

    return inducer

def buildTurbine(**overrides) -> Turbine:

    inputs = {'requiredPower': 624000.0, 'inletTemperature': 1000.0, 'pressureRatio': 20.0,
              'shaftSpeed': 30000.0, 'meanDiameter': 0.15}
    inputs.update(overrides)

    turbine = Turbine()
    turbine.setInputs(inputs)

    return turbine

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testHeadCoefficientAboveOneIsRejected():

    '''
    psi is g H over the square of tip speed. Above one the impeller produces more head than its tip
    speed contains, which is not a demanding design, it is a wrong one.
    '''

    with pytest.raises(PumpError, match = 'must lie in'):
        buildPump(headCoefficient = 1.4)

def testUnknownImpellerMaterialIsRejected():

    with pytest.raises(PumpError, match = 'Unknown impeller material'):
        buildPump(impellerMaterial = 'cheese')

def testZeroStagesIsRejected():

    with pytest.raises(PumpError, match = 'at least one'):
        buildPump(stages = 0)

def testTankBelowVapourPressureIsRejected():

    '''
    The tank contains vapour rather than liquid and there is nothing for the pump to draw. This is
    a different failure from a small cavitation margin and it deserves a different message.
    '''

    with pytest.raises(CavitationError, match = 'at or below the vapour pressure'):
        buildInducer(tankPressure = 50000.0)

def testNonPositiveNpshIsRejected():

    with pytest.raises(CavitationError, match = 'must be positive'):
        suctionSpecificSpeed(1000.0, 0.01, -5.0)

def testAvailableNpshWithoutATankPressureIsRefused():

    '''
    The class can work the chain in either direction and it will not guess which. Asking for
    available NPSH without a tank pressure is an incomplete question.
    '''

    with pytest.raises(CavitationError, match = 'No tank pressure'):
        buildInducer().calculateAvailableNpsh()

def testPressureRatioOfOneIsRejected():

    with pytest.raises(TurbineError, match = 'must exceed one'):
        buildTurbine(pressureRatio = 1.0)

def testUnknownStageTypeIsRejected():

    with pytest.raises(TurbineError, match = 'Unknown stage type'):
        buildTurbine(stageType = 'magic')

def testUnknownBladeMaterialIsRejected():

    with pytest.raises(TurbineError, match = 'Unknown blade material'):
        buildTurbine(bladeMaterial = 'wood')

def testATurbineExtractingNoWorkIsRefusedRatherThanDividedBy():

    '''
    Above a blade speed ratio of cos(alpha) the blade moves as fast as the useful gas component and
    extracts nothing. Sizing a flow against zero specific work has to raise rather than return
    infinity.
    '''

    with pytest.raises(TurbineError, match = 'extracts no work'):
        buildTurbine(meanDiameter = 2.0, pressureRatio = 1.05).sizeFlow()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testSpecificSpeedMatchesItsDefinition():

    speed, flow, head = 1000.0, 0.02, 1500.0

    expected = speed * np.sqrt(flow) / (GRAVITY * head) ** 0.75

    assert specificSpeed(speed, flow, head) == pytest.approx(expected)

def testTheUsCustomaryConversionMatchesAHandComputedCase():

    '''
    Ns_US = N[rpm] sqrt(Q[gpm]) / H[ft]^0.75, computed independently in US units and compared
    against the dimensionless value scaled by the stored constant.
    '''

    rpm, cubicMetres, metres = 10000.0, 0.02, 2000.0

    angular = rpm * 2.0 * np.pi / 60.0

    dimensionless = specificSpeed(angular, cubicMetres, metres)

    gallonsPerMinute = cubicMetres * 15850.3
    feet             = metres * 3.28084

    customary = rpm * np.sqrt(gallonsPerMinute) / feet ** 0.75

    assert toUsSpecificSpeed(dimensionless) == pytest.approx(customary, rel = 1.0e-3)
    assert customary / dimensionless == pytest.approx(US_SPECIFIC_SPEED_PER_DIMENSIONLESS,
                                                      rel = 1.0e-3)

def testHeadFromPressureRiseMatchesItsDefinition():

    assert headFromPressureRise(12.5e6, 810.0) == pytest.approx(12.5e6 / (810.0 * GRAVITY))

def testTipSpeedInvertsTheHeadCoefficient():

    '''
    U = sqrt(g H / psi), so psi = g H / U^2 has to come back out.
    '''

    head, coefficient = 1574.0, 0.55

    tipSpeed = tipSpeedFromHead(head, coefficient)

    assert GRAVITY * head / tipSpeed ** 2 == pytest.approx(coefficient)

def testSuctionSpecificSpeedIsTheSameGroupAsSpecificSpeed():

    speed, flow, npsh = 3000.0, 0.02, 20.0

    assert suctionSpecificSpeed(speed, flow, npsh) == pytest.approx(
        specificSpeed(speed, flow, npsh))

def testSpoutingVelocityMatchesTheIsentropicDrop():

    turbine = buildTurbine()

    exponent = (turbine.gamma - 1.0) / turbine.gamma

    expected = np.sqrt(2.0 * turbine.specificHeat * turbine.inletTemperature
                       * (1.0 - turbine.pressureRatio ** (-exponent)))

    assert turbine.calculateSpoutingVelocity()['spoutingVelocity'] == pytest.approx(expected)

def testImpulseUtilisationPeaksAtTheClassicalOptimum():

    '''
    eta_u = 4 (U/C0)(cos alpha - U/C0) peaks at U/C0 = cos(alpha)/2 with a value of cos^2(alpha).
    At a 20 degree nozzle angle that is 0.470 and 0.883.
    '''

    cosine = np.cos(np.radians(NOZZLE_ANGLE))

    optimum = cosine / 2.0

    def utilisation(ratio):
        return 4.0 * ratio * (cosine - ratio)

    assert utilisation(optimum) == pytest.approx(cosine ** 2)

    for offset in (-0.10, -0.05, 0.05, 0.10):
        assert utilisation(optimum + offset) < utilisation(optimum)

def testTheReportedOptimumMatchesTheClassicalOne():

    result = buildTurbine().calculateEfficiency()

    cosine = np.cos(np.radians(NOZZLE_ANGLE))

    assert result['optimumRatio'] == pytest.approx(cosine / 2.0)
    assert result['peakUtilisation'] == pytest.approx(cosine ** 2)

def testPumpPowerIsHydraulicOverEfficiency():

    power = buildPump().calculatePower()

    assert power['shaftPower'] == pytest.approx(power['hydraulicPower'] / power['efficiency'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the couplings this sub-domain exists to expose -- #
# ------------------------------------------------------------------------------------------------ #

def testARocketPumpSitsBelowThePeakEfficiencySpecificSpeed():

    '''
    The structural reason rocket pump efficiencies look poor. The head is large and the flow is
    not, which puts specific speed far below where efficiency peaks.
    '''

    result = buildPump().calculateSpecificSpeed()
    power  = buildPump().calculatePower()

    assert result['specificSpeed'] < 1.0
    assert power['efficiency'] < PEAK_EFFICIENCY

def testThePumpEfficiencyModelLandsInTheRealisticBand():

    '''
    The correlation is a fit to the range rocket pumps operate in rather than to data, and it is
    registered as unvalidated. What it must do is land in the 60 to 75 per cent band those pumps
    actually achieve, or it is not even a useful ranking tool.
    '''

    efficiency = buildPump().calculatePower()['efficiency']

    assert 0.55 < efficiency < 0.80

def testNpshRequiredGoesAsShaftSpeedToTheFourThirds():

    '''
    The exponent that makes shaft speed expensive. Doubling the speed needs 2^(4/3) = 2.52 times
    the suction head.
    '''

    slow = buildInducer(shaftSpeed = 15000.0).calculateRequiredNpsh()['required']
    fast = buildInducer(shaftSpeed = 30000.0).calculateRequiredNpsh()['required']

    assert fast / slow == pytest.approx(2.0 ** (4.0 / 3.0), rel = 1.0e-6)

def testAnInducerBuysAFactorOfFourInShaftSpeed():

    '''
    The reason an inducer is fitted at all. It is a device for buying back shaft speed that would
    otherwise be paid for in tank pressure.
    '''

    result = buildInducer().maximumShaftSpeed(availableNpsh = 30.0)

    bare     = result['comparison']['no inducer']['maximumRpm']
    inducer  = result['comparison']['inducer']['maximumRpm']

    assert inducer / bare == pytest.approx(
        SUCTION_SPECIFIC_SPEED['inducer']['limit'] / SUCTION_SPECIFIC_SPEED['no inducer']['limit'])

    assert inducer / bare > 3.0

def testCryogensGetThermodynamicSuppressionAndStorablesDoNot():

    '''
    Vaporising a little cryogen at the blade cools the surrounding liquid and lowers its vapour
    pressure. A storable gets none of that, which is a real advantage for LOX that is easy to
    forget.
    '''

    assert THERMODYNAMIC_SUPPRESSION['LH2'] > THERMODYNAMIC_SUPPRESSION['LOX'] > 1.0
    assert THERMODYNAMIC_SUPPRESSION['RP-1'] == 1.0
    assert THERMODYNAMIC_SUPPRESSION['N2O4'] == 1.0

    cryogenic = buildInducer(propellant = 'LOX').calculateRequiredNpsh()['required']
    storable  = buildInducer(propellant = 'N2O4').calculateRequiredNpsh()['required']

    assert cryogenic < storable

def testAFasterShaftDemandsAHigherTankPressure():

    '''
    The chain this class exists for. Shaft speed sets NPSH required, which sets tank pressure,
    which sets tank mass. Four links and no single owner.
    '''

    slow = buildInducer(shaftSpeed = 20000.0).requiredTankPressure()['tankPressure']
    fast = buildInducer(shaftSpeed = 40000.0).requiredTankPressure()['tankPressure']

    assert fast > slow

def testTheTankPressureChainInvertsItself():

    '''
    Compute the tank pressure a speed demands, feed it back, and the margin should come out at
    exactly the design margin. If the two directions disagree, one of them is wrong.
    '''

    inducer = buildInducer()

    required = inducer.requiredTankPressure()['tankPressure']

    checked = buildInducer(tankPressure = required).checkMargin()

    assert checked['ratio'] == pytest.approx(NPSH_MARGIN, rel = 1.0e-6)
    assert checked['adequate'] is True

def testMaximumShaftSpeedInvertsTheRequiredNpsh():

    '''
    The other direction of the same relation.
    '''

    inducer = buildInducer()

    required = inducer.calculateRequiredNpsh()['withMargin']

    maximum = inducer.maximumShaftSpeed(availableNpsh = required)['maximumRpm']

    assert maximum == pytest.approx(inducer.shaftSpeed, rel = 1.0e-6)

def testARocketTurbineRunsWellBelowItsOptimumBladeSpeedRatio():

    '''
    The defining characteristic. The pump owns the shaft speed and the turbine accepts what it is
    given, so the blade speed ratio is far below the peak and the efficiency shows it.
    '''

    result = buildTurbine().calculateEfficiency()

    assert result['belowOptimum'] is True
    assert result['bladeSpeedRatio'] < 0.5 * result['optimumRatio']
    assert result['efficiency'] < 0.60

def testEfficiencyImprovesTowardTheOptimumRatio():

    '''
    Increasing the mean diameter raises blade speed toward the optimum, so efficiency has to rise.
    If it does not, the utilisation curve is the wrong way round.
    '''

    small = buildTurbine(meanDiameter = 0.15).calculateEfficiency()
    large = buildTurbine(meanDiameter = 0.35).calculateEfficiency()

    assert large['bladeSpeedRatio'] > small['bladeSpeedRatio']
    assert large['efficiency'] > small['efficiency']

def testALowerEfficiencyDemandsMoreDrivingFlow():

    small = buildTurbine(meanDiameter = 0.15).sizeFlow()
    large = buildTurbine(meanDiameter = 0.35).sizeFlow()

    assert small['drivingFlow'] > large['drivingFlow']

def testTheDrivingFlowIsASmallFractionOfPropellantFlow():

    '''
    A sanity bound with a real consequence. The gas generator flow on an open cycle engine is a few
    per cent of total propellant, and it is thrown overboard, which is the cycle loss that made the
    F-1 disagree with the propulsion library by eight per cent in validation.
    '''

    flow = buildTurbine().sizeFlow()['drivingFlow']

    totalPropellant = 36.81

    assert 0.01 < flow / totalPropellant < 0.10

def testMoreStagesReduceTipSpeed():

    single = buildPump(stages = 1).sizeImpeller()
    triple = buildPump(stages = 3).sizeImpeller()

    assert triple['tipSpeed'] < single['tipSpeed']
    assert triple['perStageHead'] == pytest.approx(single['perStageHead'] / 3.0)

def testTheRequiredStageCountFollowsTheSquareOfTheOverrun():

    '''
    Head goes as the square of tip speed, so a pump fifty per cent over the tip speed limit needs
    three stages rather than two. That is not obvious and it is the reason a hydrogen pump has the
    stage count it does.
    '''

    modest = buildPump(pressureRise = 12.5e6, impellerMaterial = 'aluminium')
    severe = buildPump(pressureRise = 60.0e6, impellerMaterial = 'aluminium')

    assert severe.sizeImpeller()['requiredStages'] > modest.sizeImpeller()['requiredStages']

def testASlowerShaftGivesALargerImpeller():

    fast = buildPump(shaftSpeed = 40000.0).sizeImpeller()
    slow = buildPump(shaftSpeed = 15000.0).sizeImpeller()

    assert slow['diameter'] > fast['diameter']

def testTheBearingDnLimitBoundsShaftSpeedIndependently():

    '''
    DN is bore diameter times rpm and it has nothing to do with cavitation, so it is a second and
    independent ceiling on shaft speed.
    '''

    modest  = buildPump(shaftSpeed = 20000.0).sizeImpeller()
    extreme = buildPump(shaftSpeed = 90000.0).sizeImpeller()

    assert modest['dnWithinLimit'] is True
    assert extreme['dnNumber'] > modest['dnNumber']

def testGeometryClassificationCoversTheWholeRange():

    for name, entry in PUMP_GEOMETRY.items():
        middle = 0.5 * (entry['lower'] + entry['upper'])
        assert geometryForSpecificSpeed(middle)['geometry'] == name

    assert geometryForSpecificSpeed(0.01)['inRange'] is False
    assert geometryForSpecificSpeed(50.0)['inRange'] is False

def testBooleanFlagsAreRealPythonBooleans():

    '''
    Guard on a defect found in combustionDevices. A comparison between numpy floats returns
    numpy.bool_, which fails an `is True` identity check that callers and tests both write.
    '''

    flags = [
        buildPump().sizeImpeller()['withinLimit'],
        buildPump().sizeImpeller()['dnWithinLimit'],
        buildInducer(tankPressure = 400000.0).checkMargin()['adequate'],
        buildTurbine().calculateEfficiency()['belowOptimum'],
        buildTurbine().checkLimits()['temperatureOk'],
    ]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testReportsRunForAllThreeClasses():

    assert 'PUMP'                   in buildPump().generateReport()
    assert 'INDUCER AND CAVITATION' in buildInducer().generateReport()
    assert 'TURBINE'                in buildTurbine().generateReport()
