
# -- Tests for the thermalManagement component classes -- #

'''

Tiered tests for the five thermal classes.

Tier 1 covers the contract: malformed networks, unphysical properties, and the guards that stop a
correlation being used where it does not apply.

Tier 2 validates against closed forms and physical law: the Stefan-Boltzmann balance must close,
resistances must combine in series, the fourth power law must show its fourth power, and the
lumped capacitance limit must sit where the textbook puts it.

Tier 3 covers self-consistency and the physical direction of every effect, including three
regression guards on bugs found during the build: a transient peak at the final time step is a
truncation artefact rather than a peak, an ablative surface temperature is an output of the energy
balance rather than an input, and the heat pipe boiling limit is driven by the nucleation radius
rather than the pore radius.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'thermalManagementLibrary'))

from thermalUtils import (conductionResistance, contactResistance, convectionResistance,
                          radiationResistance, biotNumber, fourierNumber, thermalDiffusivity,
                          thermalPenetrationDepth, STEFAN_BOLTZMANN, CONTACT_CONDUCTANCE,
                          SURFACE_PROPERTIES, ABLATIVE_MATERIALS,
                          LUMPED_CAPACITANCE_BIOT_LIMIT,
                          InvalidInputError, ThermalNetworkError, AblationError)
from ThermalNetwork import ThermalNetwork
from AblativeTPS import AblativeTPS, SURFACE_EMISSIVITY
from Radiator import Radiator, SINK_TEMPERATURES
from HeatPipe import HeatPipe, WORKING_FLUIDS, WICK_TYPES, NUCLEATION_RADIUS
from ThermalControl import ThermalControl, TEMPERATURE_LIMITS

def buildNetwork(endTime: float = 6000.0) -> ThermalNetwork:

    network = ThermalNetwork()
    network.setInputs({'timeStep': 2.0, 'endTime': endTime})
    network.addNodeFromMass('skin',     mass = 8.0,  specificHeat = 900.0, temperature = 293.15)
    network.addNodeFromMass('bracket',  mass = 45.0, specificHeat = 900.0, temperature = 293.15)
    network.addNodeFromMass('avionics', mass = 12.0, specificHeat = 800.0, temperature = 293.15)
    network.addNode('space', temperature = 200.0, boundary = True)
    network.addContact('skin', 'bracket', area = 0.02)
    network.addContact('bracket', 'avionics', area = 0.015, jointType = 'bolted, with grease')
    network.addRadiation('skin', 'space', emissivity = 0.85, area = 1.2)
    return network

def buildShield(**overrides) -> AblativeTPS:

    inputs = {'material': 'PICA', 'peakHeatFlux': 8.0e6, 'heatLoad': 1.4e9,
              'pulseDuration': 200.0, 'backfaceLimit': 450.0}
    inputs.update(overrides)

    shield = AblativeTPS()
    shield.setInputs(inputs)
    return shield

def buildRadiator(**overrides) -> Radiator:

    inputs = {'heatLoad': 500.0, 'radiatingTemperature': 320.0,
              'sinkEnvironment': 'low earth orbit',
              'surfaceFinish': 'optical solar reflector'}
    inputs.update(overrides)

    radiator = Radiator()
    radiator.setInputs(inputs)
    return radiator

def buildPipe(**overrides) -> HeatPipe:

    inputs = {'workingFluid': 'ammonia', 'wickType': 'axial groove', 'length': 1.0,
              'vapourRadius': 0.006, 'wickThickness': 0.001, 'operatingTemperature': 300.0}
    inputs.update(overrides)

    pipe = HeatPipe()
    pipe.setInputs(inputs)
    return pipe

def buildControl(**overrides) -> ThermalControl:

    inputs = {'component': 'battery', 'coldCaseLoss': 12.0, 'hotCaseTemperature': 300.0,
              'thermalMass': 4000.0, 'missionDuration': 3.15e7}
    inputs.update(overrides)

    control = ThermalControl()
    control.setInputs(inputs)
    return control

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testNetworkNeedsABoundaryNode():

    '''
    With no boundary the temperatures are all relative and the steady state solve is singular.
    '''

    network = ThermalNetwork()
    network.setInputs({})
    network.addNodeFromMass('a', mass = 1.0, specificHeat = 900.0)
    network.addNodeFromMass('b', mass = 1.0, specificHeat = 900.0)
    network.addResistance('a', 'b', 1.0)

    with pytest.raises(ThermalNetworkError):
        network.solveSteadyState()

def testNetworkRejectsOrphanNodes():

    network = ThermalNetwork()
    network.setInputs({})
    network.addNodeFromMass('a', mass = 1.0, specificHeat = 900.0)
    network.addNode('sink', temperature = 200.0, boundary = True)
    network.addNodeFromMass('orphan', mass = 1.0, specificHeat = 900.0)
    network.addResistance('a', 'sink', 1.0)

    with pytest.raises(ThermalNetworkError):
        network.solveSteadyState()

def testNetworkRejectsSelfConnection():

    network = ThermalNetwork()
    network.setInputs({})
    network.addNodeFromMass('a', mass = 1.0, specificHeat = 900.0)

    with pytest.raises(ThermalNetworkError):
        network.addResistance('a', 'a', 1.0)

def testTransientRejectsMasslessNodes():

    '''
    An arithmetic node has no thermal mass and cannot be marched in time.
    '''

    network = ThermalNetwork()
    network.setInputs({'timeStep': 1.0, 'endTime': 10.0})
    network.addNode('surface', capacitance = 0.0, temperature = 300.0)
    network.addNode('sink', temperature = 200.0, boundary = True)
    network.addResistance('surface', 'sink', 1.0)

    with pytest.raises(ThermalNetworkError):
        network.solveTransient()

def testUnknownJointTypeRaises():

    with pytest.raises(InvalidInputError):
        contactResistance(0.01, jointType = 'glued with hope')

def testAblativeRejectsMeanFluxAbovePeak():

    '''
    A heat load implying a mean flux above the stated peak means one of the two is wrong.
    '''

    with pytest.raises(AblationError):
        buildShield(peakHeatFlux = 1.0e6, heatLoad = 1.0e9, pulseDuration = 200.0).sizeThickness()

def testAblativeRejectsBackfaceAtInitialTemperature():

    shield = buildShield(backfaceLimit = 293.15, initialTemperature = 293.15)

    with pytest.raises(AblationError):
        shield.sizeThickness()

def testRadiatorRejectsSinkAboveRadiator():

    radiator = Radiator()
    radiator.setInputs({'heatLoad': 100.0, 'radiatingTemperature': 300.0,
                        'sinkTemperature': 350.0})

    with pytest.raises(InvalidInputError):
        radiator.sizeArea()

def testControlRejectsSurvivalNarrowerThanOperational():

    '''
    Survival limits are always the wider pair. An inverted table is a data error.
    '''

    control = ThermalControl()
    with pytest.raises(InvalidInputError):
        control.setInputs({'coldCaseLoss': 10.0,
                           'operationalLimits': (250.0, 340.0),
                           'survivalLimits': (260.0, 330.0)})
        control.sizeHeater()

def testHeatPipeRejectsExcessiveTilt():

    with pytest.raises(InvalidInputError):
        buildPipe(tiltAngle = 120.0).calculateLimits()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: against closed forms and physical law -- #
# ------------------------------------------------------------------------------------------------ #

def testConductionResistanceMatchesItsDefinition():

    assert conductionResistance(0.01, 200.0, 0.05) == pytest.approx(0.01 / (200.0 * 0.05))

def testResistancesCombineInSeries():

    '''
    Two resistances in series with a boundary at each end must give the arithmetic sum.
    '''

    network = ThermalNetwork()
    network.setInputs({})
    network.addNode('hot',  temperature = 400.0, boundary = True)
    network.addNodeFromMass('middle', mass = 1.0, specificHeat = 900.0)
    network.addNode('cold', temperature = 300.0, boundary = True)
    network.addResistance('hot', 'middle', 1.0)
    network.addResistance('middle', 'cold', 3.0)

    result = network.solveSteadyState()

    # the middle node sits at the resistance-weighted position between the two boundaries
    assert result['temperatures']['middle'] == pytest.approx(400.0 - 100.0 * (1.0 / 4.0))

def testLumpedCapacitanceLimitIsAtBiotZeroPointOne():

    assert LUMPED_CAPACITANCE_BIOT_LIMIT == pytest.approx(0.1)

    network = buildNetwork()

    thick = network.checkLumpedCapacitance('bracket', coefficient = 500.0,
                                           characteristicLength = 0.05, conductivity = 50.0)
    thin  = network.checkLumpedCapacitance('bracket', coefficient = 5.0,
                                           characteristicLength = 0.005, conductivity = 200.0)

    assert not thick['lumpedValid']
    assert thin['lumpedValid']
    assert thick['suggestedNodes'] > 1

def testBiotAndFourierMatchTheirDefinitions():

    assert biotNumber(100.0, 0.02, 50.0) == pytest.approx(100.0 * 0.02 / 50.0)
    assert fourierNumber(1.0e-5, 100.0, 0.05) == pytest.approx(1.0e-5 * 100.0 / 0.05 ** 2)
    assert thermalDiffusivity(200.0, 2700.0, 900.0) == pytest.approx(200.0 / (2700.0 * 900.0))

def testRadiationResistanceLinearisationMatchesTheFullLaw():

    '''
    The linearised coefficient must reproduce the exact fourth power flux at the temperatures it
    was taken at. That is what linearising about a point means.
    '''

    hot, cold, emissivity, area = 400.0, 300.0, 0.85, 2.0

    resistance = radiationResistance(emissivity, area, hot, cold)
    linearFlux = (hot - cold) / resistance

    exactFlux = emissivity * STEFAN_BOLTZMANN * area * (hot ** 4 - cold ** 4)

    assert linearFlux == pytest.approx(exactFlux, rel = 1.0e-12)

def testRadiatorObeysTheFourthPowerLaw():

    '''
    Halving the absolute radiating temperature must cut the rejection by sixteen.
    '''

    hot  = buildRadiator(radiatingTemperature = 400.0, sinkTemperature = 4.0,
                         solarFlux = 0.0).calculateNetFlux()
    cold = buildRadiator(radiatingTemperature = 200.0, sinkTemperature = 4.0,
                         solarFlux = 0.0).calculateNetFlux()

    assert hot['emitted'] / cold['emitted'] == pytest.approx(16.0, rel = 0.01)

def testStefanBoltzmannBalanceCloses():

    radiator = buildRadiator(solarFlux = 0.0)
    flux = radiator.calculateNetFlux()

    expected = (radiator.emissivity * STEFAN_BOLTZMANN * radiator.viewFactor
                * (radiator.radiatingTemperature ** 4 - radiator.sinkTemperature ** 4))

    assert flux['emitted'] == pytest.approx(expected, rel = 1.0e-12)

def testHeaterPowerIsLossLessDissipationTimesMargin():

    control = buildControl(coldCaseLoss = 20.0, internalDissipation = 5.0, heaterMargin = 1.5)
    sizing = control.sizeHeater()

    assert sizing['requiredPower'] == pytest.approx(15.0)
    assert sizing['sizedPower'] == pytest.approx(22.5)

def testSurvivalBandsAreWiderThanOperational():

    for name, entry in TEMPERATURE_LIMITS.items():
        operational = entry['operational']
        survival    = entry['survival']
        assert survival[0] <= operational[0], name
        assert survival[1] >= operational[1], name

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency and regression -- #
# ------------------------------------------------------------------------------------------------ #

def testSoakbackPeaksAfterTheEventEnds():

    '''
    The reason a transient solve exists. Interior nodes keep heating after the pulse stops.
    '''

    network = buildNetwork(endTime = 6000.0)
    network.solveTransient(heatLoadSchedule = {'skin': lambda t: 9000.0 if t <= 120.0 else 0.0})

    soakback = network.findSoakback(eventEndTime = 120.0)

    assert soakback['soakingNodes'], 'interior nodes must peak after the event'
    assert 'bracket' in soakback['soakingNodes']
    assert soakback['nodes']['bracket']['peakTime'] > 120.0
    assert soakback['nodes']['bracket']['soakbackRise'] > 0.0

def testTruncatedRunIsFlaggedRatherThanReportedAsAPeak():

    '''
    Regression on a real bug. A peak at the final time step means the node was still rising when
    the run stopped, so the reported maximum is a truncation artefact and the real one is higher.
    '''

    short = buildNetwork(endTime = 600.0)
    shortResult = short.solveTransient(
        heatLoadSchedule = {'skin': lambda t: 9000.0 if t <= 120.0 else 0.0})

    long_ = buildNetwork(endTime = 6000.0)
    longResult = long_.solveTransient(
        heatLoadSchedule = {'skin': lambda t: 9000.0 if t <= 120.0 else 0.0})

    assert shortResult['truncated'], 'the short run must be flagged'
    assert 'bracket' in shortResult['stillRising']
    assert not longResult['truncated'], 'the long run must not be'

    # and the truncated peak really was lower than the true one
    assert (longResult['peaks']['bracket']['peakTemperature']
            > shortResult['peaks']['bracket']['peakTemperature'])

def testAblativeSurfaceTemperatureIsAnOutputNotAnInput():

    '''
    Regression on a real bug. The tabulated temperature is what the material holds while ablating
    hard. Below the flux that sustains it the surface sits at radiative equilibrium and does not
    recede, and using the tabulated value regardless overstates re-radiation and oversizes the
    insulation.
    '''

    weak   = buildShield(peakHeatFlux = 1.2e6, heatLoad = 1.5e8, pulseDuration = 180.0)
    strong = buildShield(peakHeatFlux = 8.0e6, heatLoad = 1.4e9, pulseDuration = 200.0)

    weakFlux   = weak.calculateNetHeatFlux()
    strongFlux = strong.calculateNetHeatFlux()

    assert not weakFlux['isAblating']
    assert weakFlux['surfaceTemperature'] == pytest.approx(weakFlux['equilibriumTemperature'])
    assert weakFlux['surfaceTemperature'] < weakFlux['ablationTemperature']

    assert strongFlux['isAblating']
    assert strongFlux['surfaceTemperature'] == pytest.approx(strongFlux['ablationTemperature'])

    # and the energy balance closes at the actual surface temperature
    expected = (SURFACE_EMISSIVITY * STEFAN_BOLTZMANN
                * weakFlux['surfaceTemperature'] ** 4)
    assert weakFlux['reradiated'] == pytest.approx(expected, rel = 1.0e-12)

def testNonAblatingCaseRecedesNothing():

    weak = buildShield(peakHeatFlux = 1.2e6, heatLoad = 1.5e8, pulseDuration = 180.0)

    recession = weak.calculateRecession()
    sizing    = weak.sizeThickness()

    assert recession['recessionDepth'] == pytest.approx(0.0)
    assert sizing['limitedBy'] == 'insulation'

def testAblatingCaseRecedesAndIsSized():

    strong = buildShield()

    sizing = strong.sizeThickness()

    assert sizing['recessionDepth'] > 0.0
    assert sizing['totalThickness'] > sizing['recessionDepth']

def testLowDensityAblativeWinsOnArealMass():

    '''
    Areal mass rather than thickness is the comparison that matters, and it reorders the ranking.
    '''

    comparison = buildShield().compareMaterials()

    assert comparison['lightest'] == 'PICA'
    assert (comparison['materials']['PICA']['arealMass']
            < comparison['materials']['carbon phenolic']['arealMass'])

def testHeatPipeBoilingLimitUsesTheNucleationRadius():

    '''
    Regression on a real bug. The boiling driving term is dominated by the nucleation radius,
    three orders below the pore radius. Using the pore radius in its place understates the limit
    by roughly that ratio and makes boiling appear to govern when it does not.
    '''

    assert NUCLEATION_RADIUS < 1.0e-6

    pipe = buildPipe()
    limits = pipe.calculateLimits()['limits']

    assert limits['boiling'] > 50.0, \
        'the boiling limit must be a realistic magnitude, not a fraction of a watt'
    assert limits['capillary'] < limits['boiling'], \
        'capillary must govern a grooved ammonia pipe, not boiling'

def testCapillaryLimitGovernsForCommonWicks():

    for wick in ('axial groove', 'sintered metal', 'screen mesh'):
        result = buildPipe(wickType = wick).calculateLimits()
        assert result['governing'] == 'capillary', wick

def testAdverseTiltKillsAHeatPipeInOneGravity():

    '''
    The ground testability problem. A pipe that works on orbit can transport nothing on a bench
    with a few degrees of the wrong tilt, so a favourably tilted test was never a test.
    '''

    orbital = buildPipe(gravityLevel = 0.0).calculateCapillaryLimit()['limit']
    tilted  = buildPipe(gravityLevel = 1.0, tiltAngle = 5.0).calculateCapillaryLimit()['limit']

    assert orbital > 0.0
    assert tilted == pytest.approx(0.0)

    testability = buildPipe().checkGroundTestability()
    assert testability['deadAngles'], 'some adverse tilt must kill the pipe'

def testFinerWickPumpsHarderAndFlowsWorse():

    '''
    Pore radius and permeability pull in opposite directions, which is the whole wick trade.
    '''

    coarse = WICK_TYPES['axial groove']
    fine   = WICK_TYPES['sintered metal']

    assert fine['poreRadius'] < coarse['poreRadius']
    assert fine['permeability'] < coarse['permeability']

    coarseHead = buildPipe(wickType = 'axial groove').calculateCapillaryLimit()['capillaryHead']
    fineHead   = buildPipe(wickType = 'sintered metal').calculateCapillaryLimit()['capillaryHead']

    assert fineHead > coarseHead

def testRadiatorSinkComparisonHandlesAnUnusableSink():

    '''
    A sink above the radiator temperature is a legitimate comparison result saying the pointing
    does not work, not an error that should abort the whole table.
    '''

    comparison = buildRadiator().compareSinks()

    assert 'sun facing' in comparison['sinks']
    assert not comparison['sinks']['sun facing']['usable']
    assert np.isinf(comparison['sinks']['sun facing']['area'])
    assert comparison['sinks']['deep space']['usable']
    assert comparison['best'] == 'deep space'

def testColderRadiatorNeedsMoreArea():

    warm = buildRadiator(radiatingTemperature = 340.0).sizeArea()
    cool = buildRadiator(radiatingTemperature = 290.0).sizeArea()

    assert cool['area'] > warm['area']

def testFinEfficiencyFallsWithLength():

    short = buildRadiator(finLength = 0.05, finThickness = 0.002,
                          finConductivity = 180.0).calculateFinEfficiency()
    long_ = buildRadiator(finLength = 0.50, finThickness = 0.002,
                          finConductivity = 180.0).calculateFinEfficiency()

    assert long_['efficiency'] < short['efficiency']
    assert 0.0 < long_['efficiency'] <= 1.0

def testContactConductanceSpansAnOrderOfMagnitude():

    '''
    Contact conductance is the least well known number in most models and the spread is the reason.
    '''

    values = [entry['value'] for entry in CONTACT_CONDUCTANCE.values()
              if entry['value'] < 1.0e6]

    assert max(values) / min(values) > 100.0

    network = buildNetwork()
    sensitivity = network.resistanceSensitivity()

    assert sum(entry['fraction'] for entry in sensitivity['shares'].values()) == \
        pytest.approx(1.0, rel = 1.0e-9)

def testSurfacePropertiesAgreeWithTheEnvironmentsDomain():

    '''
    Cross-domain drift guard. environmentsAndLoads carries the same optical properties and the two
    must not diverge. They are stated independently rather than imported, because the domains must
    not depend on each other's internals.
    '''

    environmentsLibrary = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'environmentsAndLoads', 'environmentsAndLoadsLibrary', 'ThermalEnvironment.py')

    assert os.path.exists(environmentsLibrary), 'the environments domain must be present'

    import ast

    tree = ast.parse(open(environmentsLibrary, encoding = 'utf-8').read())

    theirs = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id == 'SURFACE_FINISHES':
                theirs = ast.literal_eval(node.value)

    assert theirs is not None, 'SURFACE_FINISHES not found in the environments domain'

    shared = set(SURFACE_PROPERTIES) & set(theirs)
    assert shared, 'the two tables must share entries for this guard to mean anything'

    for name in shared:
        assert SURFACE_PROPERTIES[name]['emissivity'] == \
            pytest.approx(theirs[name]['emissivity']), name
        assert SURFACE_PROPERTIES[name]['absorptivity'] == \
            pytest.approx(theirs[name]['absorptivity']), name

def testThermalPenetrationGrowsAsRootTime():

    diffusivity = thermalDiffusivity(0.13, 270.0, 1600.0)

    early = thermalPenetrationDepth(diffusivity, 100.0)
    late  = thermalPenetrationDepth(diffusivity, 400.0)

    assert late / early == pytest.approx(2.0, rel = 1.0e-9)

def testWiderDeadbandLengthensTheThermostatPeriod():

    tight = buildControl(deadband = 2.0).calculateDutyCycle()
    wide  = buildControl(deadband = 10.0).calculateDutyCycle()

    assert wide['period'] > tight['period']
    assert wide['cycles'] < tight['cycles']

def testReportsRunForAllFiveClasses():

    assert 'THERMAL NETWORK'  in buildNetwork().generateReport()
    assert 'ABLATIVE TPS'     in buildShield().generateReport()
    assert 'RADIATOR'         in buildRadiator().generateReport()
    assert 'HEAT PIPE'        in buildPipe().generateReport()
    assert 'THERMAL CONTROL'  in buildControl().generateReport()
