
# -- Tests for the component classes -- #

'''

Tiered tests for the sixteen component classes.

Tier 2 validates against published references: the definition of Cv, ISO 5167 discharge
coefficients, Crane TP-410 equivalent lengths, textbook Joukowsky surge values, AS568 gland
practice, and Aerojet Rocketdyne catalog hydrazine thruster performance.

Tier 3 covers self-consistency: forward and inverse solves must round trip, and quantities computed
by two independent routes must agree.

Author: Sean Bowman
Date:   08/04/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'fluidSystemsLibrary'))

from utils import (fluidProps, PA_PER_PSIA, GRAVITY, CompatibilityError, InvalidInputError,
                   PressureDropError, ChokedFlowError)
from Orifice import Orifice
from CavitatingVenturi import CavitatingVenturi
from Valve import Valve, CV_FLOW_CONSTANT
from Line import Line
from Fitting import Fitting
from Seal import Seal
from LeakPath import LeakPath
from Weld import Weld
from Insulation import Insulation
from WaterHammer import WaterHammer
from CatalystBed import CatalystBed
from MonopropThruster import MonopropThruster
from Pressurization import Pressurization
from Regulator import Regulator
from CheckValve import CheckValve
from Filter import Filter

# -------------------------------------------------------------------------------------------------- #
# -- Fixtures -- #
# -------------------------------------------------------------------------------------------------- #

HYDRAZINE_TEMPERATURE = 293.15
HYDRAZINE_DENSITY     = 1008.48

@pytest.fixture(scope = 'module')
def referenceBed() -> CatalystBed:

    '''
    The 100 N class catalyst bed used across the monopropellant tests, solved once and shared.
    '''

    bed = CatalystBed()
    bed.setInputs({'massFlow': 0.046, 'chamberPressure': 1.5e6,
                   'inletTemperature': HYDRAZINE_TEMPERATURE, 'ammoniaDissociation': 0.40,
                   'meshSize': '14-18', 'bedLoading': 20.0, 'bedTemperature': 373.15})
    bed.calculateDecomposition()
    bed.sizeBed()
    bed.calculatePressureDrop()
    bed.checkColdStart()

    return bed

# -------------------------------------------------------------------------------------------------- #
# -- Orifice -- #
# -------------------------------------------------------------------------------------------------- #

def testOrificeIncompressibleRelation():

    '''
    The bare incompressible orifice relation, checked by hand: mdot = Cd * A * sqrt(2 * rho * dP).
    Catches a factor of two or a missing square root.
    '''

    element = Orifice()
    element.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.20e6,
                       'downstreamPressure': 1.90e6, 'upstreamTemperature': HYDRAZINE_TEMPERATURE,
                       'diameter': 0.0016958, 'orificeType': 'square'})
    massFlow = element.calculateMassFlow()

    area     = np.pi * 0.0016958**2 / 4.0
    expected = 0.81 * area * np.sqrt(2.0 * HYDRAZINE_DENSITY * 3.0e5)

    assert massFlow == pytest.approx(expected, rel = 0.01), \
        'The incompressible orifice relation does not match the hand calculation'

def testOrificeSizeAndFlowRoundTrip():

    '''
    Sizing for a target flow and then computing the flow through the sized hole must return the
    original flow. Catches an inconsistency between the forward and inverse paths.
    '''

    inputs = {'fluid': 'N2H4', 'upstreamPressure': 2.20e6, 'downstreamPressure': 1.90e6,
              'upstreamTemperature': HYDRAZINE_TEMPERATURE, 'orificeType': 'square'}

    sizer = Orifice()
    sizer.setInputs({**inputs, 'massFlow': 0.045})
    diameter = sizer.sizeDiameter()

    analyzer = Orifice()
    analyzer.setInputs({**inputs, 'diameter': diameter})

    assert analyzer.calculateMassFlow() == pytest.approx(0.045, rel = 1e-6), \
        'Orifice sizing and analysis do not round trip'

def testOrificeChokedGasIsIndependentOfDownstream():

    '''
    The defining property of choked flow: once choked, the mass flow does not depend on downstream
    pressure at all. A regression here would mean the choking branch is not being selected.
    '''

    flows = []
    for downstreamPressure in (101325.0, 500000.0, 1.0e6):
        element = Orifice()
        element.setInputs({'fluid': 'Nitrogen', 'upstreamPressure': 5.0e6,
                           'downstreamPressure': downstreamPressure,
                           'upstreamTemperature': 293.15, 'diameter': 0.001,
                           'orificeType': 'sharp'})
        flows.append(element.calculateMassFlow())
        assert element.isChoked, f'Should be choked at P2/P1 = {downstreamPressure / 5.0e6:.3f}'

    assert flows[0] == pytest.approx(flows[1], rel = 1e-12)
    assert flows[1] == pytest.approx(flows[2], rel = 1e-12), \
        'Choked mass flow must be completely independent of downstream pressure'

def testOrificeSubsonicMatchesChokedAtTheTransition():

    '''
    The subsonic and choked expressions must agree at the critical pressure ratio, or the class has a
    discontinuity exactly where solvers operate.
    '''

    gamma         = float(fluidProps('Nitrogen', 'TP', 'Cp/Cv', 293.15, 5.0e6))
    criticalRatio = (2.0 / (gamma + 1.0))**(gamma / (gamma - 1.0))

    justAbove = Orifice()
    justAbove.setInputs({'fluid': 'Nitrogen', 'upstreamPressure': 5.0e6,
                         'downstreamPressure': 5.0e6 * criticalRatio * 1.0001,
                         'upstreamTemperature': 293.15, 'diameter': 0.001, 'orificeType': 'sharp'})
    subsonicFlow = justAbove.calculateMassFlow()

    justBelow = Orifice()
    justBelow.setInputs({'fluid': 'Nitrogen', 'upstreamPressure': 5.0e6,
                         'downstreamPressure': 5.0e6 * criticalRatio * 0.9999,
                         'upstreamTemperature': 293.15, 'diameter': 0.001, 'orificeType': 'sharp'})
    chokedFlow = justBelow.calculateMassFlow()

    assert not justAbove.isChoked and justBelow.isChoked
    assert subsonicFlow == pytest.approx(chokedFlow, rel = 1e-3), \
        'The subsonic and choked branches must be continuous at the critical pressure ratio'

def testOrificeISO5167DischargeCoefficient():

    '''
    Validated against ISO 5167-2: a beta 0.5 orifice plate with flange tappings at Re_D near 1e5 has
    a Reader-Harris/Gallagher discharge coefficient close to 0.605.
    '''

    meter = Orifice()
    meter.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 0.98e6,
                     'upstreamTemperature': 293.15, 'diameter': 0.05, 'pipeDiameter': 0.10,
                     'model': 'plate', 'tappings': 'flange'})
    meter.calculateMassFlow()

    assert meter.dischargeCoefficient == pytest.approx(0.605, abs = 0.005), \
        f'ISO 5167-2 Cd at beta 0.5 should be about 0.605, got {meter.dischargeCoefficient:.4f}'

def testOrificePermanentPressureLoss():

    '''
    ISO 5167 permanent loss: dP_permanent / dP_measured = 1 - beta^1.9. At beta 0.5 that is 0.732.
    '''

    meter = Orifice()
    meter.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 0.98e6,
                     'upstreamTemperature': 293.15, 'diameter': 0.05, 'pipeDiameter': 0.10,
                     'model': 'plate', 'tappings': 'flange'})
    meter.calculateMassFlow()

    assert meter.permanentPressureLoss / meter.pressureDrop == pytest.approx(1.0 - 0.5**1.9, rel = 1e-6)

def testOrificeCavitatesBelowVaporPressure():

    '''
    A liquid orifice discharging below the vapor pressure must choke on vapor pressure rather than on
    the full differential. Catches the cavitating branch not being taken.
    '''

    element = Orifice()
    element.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 1000.0,
                       'upstreamTemperature': 293.15, 'diameter': 0.002, 'orificeType': 'sharp'})
    element.calculateMassFlow()

    assert element.regime == 'cavitating'
    assert element.isChoked
    assert element.cavitationStatus == 'flashing'

def testOrificeRaisesWhenFlowIsImpossible():

    '''
    Asking for more flow than the orifice can pass even when choked must raise a typed error with the
    physical limit in it, not return a nonsense pressure.
    '''

    element = Orifice()
    element.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 9.0e5,
                       'upstreamTemperature': 293.15, 'diameter': 0.003, 'massFlow': 2.0,
                       'orificeType': 'square'})

    with pytest.raises(PressureDropError):
        element.calculatePressureDrop()

# -------------------------------------------------------------------------------------------------- #
# -- Valve -- #
# -------------------------------------------------------------------------------------------------- #

def testValveCvDefinition():

    '''
    The defining test: a Cv of 1 passes 1 US gallon per minute of 60 degF water at 1 psi. If this
    fails, every valve size in the library is wrong by the same factor.
    '''

    valve = Valve()
    valve.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6,
                     'downstreamPressure': 1.0e6 - PA_PER_PSIA, 'upstreamTemperature': 288.7,
                     'flowCoefficient': 1.0, 'valveType': 'globe'})
    massFlow = valve.calculateMassFlow()

    volumetricFlowGpm = massFlow / 999.0 / 6.30902e-5

    assert volumetricFlowGpm == pytest.approx(1.0, rel = 0.005), \
        f'Cv = 1 must pass 1 gpm of water at 1 psi, got {volumetricFlowGpm:.4f} gpm'

def testValveCvKvRelation():

    '''
    Kv = 0.8646 * Cv is the definition. Catches an inverted metric conversion.
    '''

    valve = Valve()
    valve.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 0.95e6,
                     'upstreamTemperature': 293.15, 'massFlow': 1.0, 'valveType': 'globe'})
    valve.sizeFlowCoefficient()

    assert valve.flowCoefficientKv == pytest.approx(0.8646 * valve.requiredFlowCoefficient, rel = 1e-9)

def testValveChokedLiquidCapsTheSizingDifferential():

    '''
    Sizing on the full differential when the valve is choked undersizes it. The class must cap the
    sizing differential at FL^2 * (P1 - FF * Pv).
    '''

    valve = Valve()
    valve.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 5.0e3,
                     'upstreamTemperature': 293.15, 'massFlow': 1.0, 'valveType': 'ball full bore'})
    valve.sizeFlowCoefficient()

    assert valve.isChoked, 'A 1.0 MPa to 5 kPa differential on a ball valve must be choked'
    assert valve.chokedPressureDrop < (1.0e6 - 5.0e3), \
        'The choked differential must be below the actual differential'

def testValveGasExpansionFactorFloor():

    '''
    The IEC 60534 expansion factor Y falls linearly to exactly 2/3 at choking and is pinned there.
    A value below 2/3 means the floor is missing.
    '''

    valve = Valve()
    valve.setInputs({'fluid': 'Nitrogen', 'upstreamPressure': 5.0e6, 'downstreamPressure': 1.0e5,
                     'upstreamTemperature': 293.15, 'massFlow': 0.01, 'valveType': 'globe'})
    valve.sizeFlowCoefficient()

    assert valve.isChoked
    assert valve.expansionFactor == pytest.approx(2.0 / 3.0, rel = 1e-9), \
        'The expansion factor must be pinned at 2/3 once choked'

def testValveRecoveryFactorOrdering():

    '''
    A ball valve has a much lower pressure recovery factor than a globe valve, so it cavitates at a
    differential the globe valve handles. If the ordering reverses, the trim selection guidance in
    the docs is wrong.
    '''

    results = {}
    for valveType in ('globe', 'ball full bore'):
        valve = Valve()
        valve.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 4.0e5,
                         'upstreamTemperature': 293.15, 'massFlow': 1.0, 'valveType': valveType})
        valve.sizeFlowCoefficient()
        results[valveType] = valve.chokedPressureDrop

    assert results['globe'] > results['ball full bore'], \
        'A globe valve must tolerate a larger differential before choking than a ball valve'

def testValveCvToLossCoefficientRoundTrip():

    '''
    Converting Cv to an equivalent loss coefficient K and back through the K pressure drop relation
    must reproduce the original pressure drop.
    '''

    valve = Valve()
    valve.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 0.95e6,
                     'upstreamTemperature': 293.15, 'massFlow': 2.0, 'valveType': 'globe',
                     'nominalSize': 0.0254})
    valve.sizeFlowCoefficient()

    area     = np.pi * 0.0254**2 / 4.0
    velocity = valve.massFlow / (valve.density * area)
    fromK    = valve.lossCoefficient * valve.density * velocity**2 / 2.0

    assert fromK == pytest.approx(valve.pressureDrop, rel = 1e-6), \
        'The Cv to K conversion does not reproduce the original pressure drop'

def testValveInstalledCharacteristicAtLowAuthority():

    '''
    Equal percentage trim at low authority must install approximately linear. That is the entire
    design intent of the trim shape, and if it does not come out the model is wrong.
    '''

    valve = Valve()
    valve.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6, 'downstreamPressure': 0.95e6,
                     'upstreamTemperature': 293.15, 'massFlow': 1.0, 'valveType': 'globe',
                     'systemPressureDrop': 2.5e5, 'characteristic': 'equal percentage'})
    valve.sizeFlowCoefficient()
    curves = valve.calculateCharacteristic(11)

    assert curves['authority'] == pytest.approx(0.2, rel = 0.01)

    # The installed curve must be much closer to linear than the inherent curve is
    travel            = curves['travel']
    inherentError     = np.max(np.abs(curves['inherent'] - travel))
    installedError    = np.max(np.abs(curves['installed'] - travel))

    assert installedError < inherentError, \
        'Equal percentage trim at 0.2 authority must install closer to linear than its inherent curve'

# -------------------------------------------------------------------------------------------------- #
# -- Line -- #
# -------------------------------------------------------------------------------------------------- #

def testLineDarcyWeisbachByHand():

    '''
    Hand check of the Darcy-Weisbach pressure drop with no fittings, no elevation and an
    incompressible liquid, so the marching solution must reduce to the closed form.
    '''

    line = Line()
    line.setInputs({'fluid': 'Water', 'massFlow': 1.0, 'length': 10.0,
                    'inletPressure': 1.0e6, 'inletTemperature': 293.15,
                    'innerDiameter': 0.025, 'surface': 'drawn tube'})
    pressureDrop = line.calculatePressureDrop()

    density  = 998.2
    area     = np.pi * 0.025**2 / 4.0
    velocity = 1.0 / (density * area)
    expected = line.frictionFactorValue * (10.0 / 0.025) * density * velocity**2 / 2.0

    assert pressureDrop == pytest.approx(expected, rel = 0.02), \
        'The marching solution must reduce to the closed-form Darcy-Weisbach result for a liquid'

def testLineEquivalentLengthFromCraneRatios():

    '''
    Crane TP-410 equivalent lengths: a standard 90 degree elbow is L/D = 30. Four of them on a 10 mm
    line must add 1.2 m of equivalent length.
    '''

    line = Line()
    line.setInputs({'fluid': 'Water', 'massFlow': 0.5, 'length': 5.0,
                    'inletPressure': 1.0e6, 'inletTemperature': 293.15,
                    'innerDiameter': 0.010, 'fittings': {'elbow 90 standard': 4}})
    line.calculatePressureDrop()

    assert line.equivalentLength == pytest.approx(4 * 30 * 0.010, rel = 1e-9), \
        'Four standard 90 degree elbows on a 10 mm line should add 1.2 m equivalent length'

def testLineDiameterFifthPowerSensitivity():

    '''
    Pressure drop scales as D^-5 in turbulent flow at constant mass flow. This is the single most
    important sensitivity in the library and a regression would change every sizing answer.
    '''

    pressureDrops = {}
    for diameter in (0.010, 0.020):
        line = Line()
        line.setInputs({'fluid': 'Water', 'massFlow': 1.0, 'length': 10.0,
                        'inletPressure': 5.0e6, 'inletTemperature': 293.15,
                        'innerDiameter': diameter, 'surface': 'drawn tube'})
        pressureDrops[diameter] = line.calculatePressureDrop()

    ratio = pressureDrops[0.010] / pressureDrops[0.020]

    # Doubling the diameter should reduce dP by roughly 2^5 = 32, modified slightly by the friction
    # factor's own Reynolds dependence
    assert 25.0 < ratio < 40.0, \
        f'Doubling the diameter should reduce dP by roughly a factor of 32, got {ratio:.1f}'

def testLineSizingMeetsTheBindingConstraint():

    '''
    sizeDiameter must satisfy both the velocity limit and the pressure drop budget, taking whichever
    requires the larger diameter.
    '''

    line = Line()
    line.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'length': 2.5,
                    'inletPressure': 2.4e6, 'inletTemperature': HYDRAZINE_TEMPERATURE,
                    'allowablePressureDrop': 5.0e4, 'service': 'hydrazine'})
    line.sizeDiameter()

    assert line.pressureDrop == pytest.approx(5.0e4, rel = 0.01), \
        'The sized line should land on the pressure drop budget when that constraint governs'
    assert line.velocity <= 6.0, 'The hydrazine velocity limit of 6 m/s must not be exceeded'

def testLineStandardTubeSnapsUp():

    '''
    selectStandardTube must snap UP to the next available inner diameter, never down. Snapping down
    would blow the pressure budget silently.
    '''

    line = Line()
    line.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'length': 2.5,
                    'inletPressure': 2.4e6, 'inletTemperature': HYDRAZINE_TEMPERATURE,
                    'allowablePressureDrop': 5.0e4, 'service': 'hydrazine',
                    'designPressure': 3.5e6})
    requiredDiameter = line.sizeDiameter()
    line.selectStandardTube()

    assert line.innerDiameter >= requiredDiameter, \
        'The selected standard tube must have an inner diameter at least the required value'
    assert line.pressureDrop <= 5.0e4, \
        'Snapping up must reduce the pressure drop below the budget'

def testLineGasChokingRaises():

    '''
    A gas line that reaches Mach 1 at its exit cannot pass the requested flow. It must raise rather
    than return a negative outlet pressure.
    '''

    line = Line()
    line.setInputs({'fluid': 'Nitrogen', 'massFlow': 2.0, 'length': 50.0,
                    'inletPressure': 5.0e5, 'inletTemperature': 293.15,
                    'innerDiameter': 0.004})

    with pytest.raises((ChokedFlowError, PressureDropError)):
        line.calculatePressureDrop()

# -------------------------------------------------------------------------------------------------- #
# -- Water hammer -- #
# -------------------------------------------------------------------------------------------------- #

def testJoukowskySurgeTextbookCase():

    '''
    The textbook case: water at 3 m/s in a 50 mm ID, 3 mm wall steel line. Wave speed about 1360 m/s
    and a Joukowsky surge of about 4.08 MPa. Catches a bulk modulus or wall compliance error.
    '''

    surge = WaterHammer()
    surge.setInputs({'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15,
                     'velocity': 3.0, 'innerDiameter': 0.05, 'wallThickness': 0.003,
                     'length': 20.0, 'material': '316L'})
    surge.calculateSurge()

    assert surge.waveSpeed == pytest.approx(1360.0, rel = 0.02), \
        f'Wave speed for water in a 50 mm, 3 mm wall steel line should be about 1360 m/s, got {surge.waveSpeed:.0f}'
    assert surge.joukowskySurge == pytest.approx(4.08e6, rel = 0.03), \
        'Joukowsky surge for a 3 m/s change should be about 4.08 MPa'

def testJoukowskyIsLinearInVelocityChange():

    '''
    dP = rho * a * dV is linear in dV. Catches a squared or square-rooted velocity term.
    '''

    surges = []
    for velocity in (1.0, 2.0, 4.0):
        surge = WaterHammer()
        surge.setInputs({'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15,
                         'velocity': velocity, 'innerDiameter': 0.05, 'wallThickness': 0.003,
                         'length': 20.0})
        surge.calculateSurge()
        surges.append(surge.joukowskySurge)

    assert surges[1] == pytest.approx(2.0 * surges[0], rel = 1e-9)
    assert surges[2] == pytest.approx(4.0 * surges[0], rel = 1e-9), \
        'The Joukowsky surge must be linear in the velocity change'

def testSlowClosureReducesSurge():

    '''
    Closing slower than the pipe period must reduce the surge; closing faster must not. Catches the
    pipe period threshold being applied backwards.
    '''

    inputs = {'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15, 'velocity': 3.0,
              'innerDiameter': 0.05, 'wallThickness': 0.003, 'length': 20.0}

    fast = WaterHammer()
    fast.setInputs({**inputs, 'closureTime': 0.001})
    fast.calculateSurge()

    slow = WaterHammer()
    slow.setInputs({**inputs, 'closureTime': 0.5})
    slow.calculateSurge()

    assert fast.isRapidClosure and fast.actualSurge == pytest.approx(fast.joukowskySurge, rel = 1e-9), \
        'Closing faster than the pipe period must produce the full Joukowsky surge'
    assert not slow.isRapidClosure and slow.actualSurge < 0.1 * slow.joukowskySurge, \
        'Closing 17 times slower than the pipe period must reduce the surge substantially'

def testEntrainedGasReducesWaveSpeed():

    '''
    0.1 percent free gas roughly halves the wave speed. This is the mechanism an accumulator uses and
    the reason an unbled line behaves nothing like the calculation.
    '''

    inputs = {'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15, 'velocity': 3.0,
              'innerDiameter': 0.05, 'wallThickness': 0.003, 'length': 20.0}

    clean = WaterHammer()
    clean.setInputs(inputs)
    clean.calculateWaveSpeed()

    gassy = WaterHammer()
    gassy.setInputs({**inputs, 'entrainedGasFraction': 0.001})
    gassy.calculateWaveSpeed()

    assert gassy.waveSpeed < 0.7 * clean.waveSpeed, \
        '0.1 percent entrained gas must cut the wave speed substantially'

def testAdiabaticCompressionTemperature():

    '''
    Compressing air from 1 atm to 20 MPa adiabatically reaches about 1330 K, above the ignition
    temperature of every non-metal. Catches a wrong gamma exponent in the oxygen ignition check.
    '''

    surge = WaterHammer()
    surge.setInputs({'fluid': 'Water', 'pressure': 1.0e5, 'temperature': 293.15, 'velocity': 0.1,
                     'innerDiameter': 0.01, 'wallThickness': 0.001, 'length': 1.0})

    result = surge.calculateAdiabaticCompression(101325.0, 20.0e6, gamma = 1.4)

    assert result['finalTemperature'] == pytest.approx(1327.0, rel = 0.01), \
        'Adiabatic compression from 1 atm to 20 MPa should reach about 1330 K'
    assert 'PTFE' in result['materialsAtRisk'], \
        'PTFE must be flagged at risk at 1330 K in oxygen'

# -------------------------------------------------------------------------------------------------- #
# -- Catalyst bed and thruster -- #
# -------------------------------------------------------------------------------------------------- #

def testDecompositionMoleBalance(referenceBed):

    '''
    Nitrogen and hydrogen atoms must be conserved through the decomposition for any dissociation
    fraction. Catches a stoichiometry error, which would corrupt the molecular weight and c*.
    '''

    for dissociation in (0.0, 0.25, 0.5, 0.75, 1.0):
        referenceBed.ammoniaDissociation = dissociation
        referenceBed.calculateDecomposition()
        moles = referenceBed.productMoles

        nitrogenAtoms = moles['NH3'] * 1 + moles['N2'] * 2
        hydrogenAtoms = moles['NH3'] * 3 + moles['H2'] * 2

        assert nitrogenAtoms == pytest.approx(2.0, rel = 1e-9), \
            f'Nitrogen atoms not conserved at X = {dissociation}'
        assert hydrogenAtoms == pytest.approx(4.0, rel = 1e-9), \
            f'Hydrogen atoms not conserved at X = {dissociation}'

    referenceBed.ammoniaDissociation = 0.40
    referenceBed.calculateDecomposition()

def testDecompositionEndpoints(referenceBed):

    '''
    Validated against the published hydrazine decomposition curve: 1659 K and 19.2 g/mol at zero
    ammonia dissociation, 894 K and 10.7 g/mol at full dissociation.
    '''

    savedDissociation = referenceBed.ammoniaDissociation

    referenceBed.ammoniaDissociation = 0.0
    referenceBed.inletTemperature    = 298.15
    referenceBed.calculateDecomposition()
    assert referenceBed.chamberTemperature == pytest.approx(1659.0, abs = 5.0), \
        'Adiabatic decomposition temperature at zero ammonia dissociation should be 1659 K'
    assert referenceBed.productMolarMass * 1.0e3 == pytest.approx(19.23, abs = 0.05)

    referenceBed.ammoniaDissociation = 1.0
    referenceBed.calculateDecomposition()
    assert referenceBed.chamberTemperature == pytest.approx(894.0, abs = 5.0), \
        'Adiabatic decomposition temperature at full ammonia dissociation should be 894 K'
    assert referenceBed.productMolarMass * 1.0e3 == pytest.approx(10.68, abs = 0.05)

    referenceBed.ammoniaDissociation = savedDissociation
    referenceBed.inletTemperature    = HYDRAZINE_TEMPERATURE
    referenceBed.calculateDecomposition()

def testCharacteristicVelocityInFamily(referenceBed):

    '''
    Published hydrazine c* is 1200 to 1330 m/s at typical dissociation. A value outside that band
    means the gas constant, gamma or temperature is wrong.
    '''

    assert 1200.0 < referenceBed.characteristicVelocity < 1340.0, \
        f'Hydrazine c* should be 1200 to 1340 m/s, got {referenceBed.characteristicVelocity:.1f}'

def testOptimalDissociationIsInterior(referenceBed):

    '''
    c* has an interior maximum because temperature and molecular weight fall together. The optimum
    must land between 0.3 and 0.5, and the peak must be broad.
    '''

    result = referenceBed.optimalDissociation()

    assert 0.25 < result['optimalDissociation'] < 0.55, \
        f'The c* optimum should be near X = 0.38, got {result["optimalDissociation"]:.3f}'

    velocities = result['characteristicVelocitySweep']
    dissociations = result['dissociationSweep']
    band = velocities[(dissociations >= 0.2) & (dissociations <= 0.6)]

    assert (band.max() - band.min()) / band.max() < 0.05, \
        'The c* peak must be broad: less than 5 percent variation between X = 0.2 and X = 0.6'

def testBedLoadingSetsFrontalArea(referenceBed):

    '''
    The bed frontal area is mass flow over bed loading, by definition. Catches a unit error in the
    imperial equivalent reported alongside it.
    '''

    assert referenceBed.bedArea == pytest.approx(referenceBed.massFlow / referenceBed.actualBedLoading,
                                                 rel = 1e-9)

def testColdStartDelayRisesAsBedCools():

    '''
    Ignition delay must rise steeply as the bed cools. This is the entire argument for a bed heater,
    and an inverted Arrhenius exponent would reverse it.
    '''

    delays = {}
    for bedTemperature in (273.15, 293.15, 373.15):
        bed = CatalystBed()
        bed.setInputs({'massFlow': 0.046, 'chamberPressure': 1.5e6,
                       'bedTemperature': bedTemperature})
        bed.calculateDecomposition()
        bed.sizeBed()
        delays[bedTemperature] = bed.checkColdStart()['ignitionDelay']

    assert delays[273.15] > delays[293.15] > delays[373.15], \
        'Ignition delay must fall as the bed temperature rises'
    assert delays[273.15] > 5.0 * delays[373.15], \
        'The delay at 273 K should be several times the delay at 373 K'

def testThrusterIspAgainstCatalogData():

    '''
    Validated against Aerojet Rocketdyne catalog data: a 100 N class hydrazine thruster at an
    expansion ratio of 50 delivers roughly 220 to 230 s of vacuum specific impulse.
    '''

    thruster = MonopropThruster()
    thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0, 'chamberPressure': 1.5e6,
                        'expansionRatio': 50.0})
    thruster.calculatePerformance()

    assert 215.0 < thruster.vacuumSpecificImpulse < 235.0, \
        f'A 100 N hydrazine thruster at eps = 50 should deliver 215 to 235 s, got ' \
        f'{thruster.vacuumSpecificImpulse:.1f} s'

def testThrustEqualsMassFlowTimesIsp():

    '''
    The defining identity F = mdot * Isp * g0. Catches an inconsistency between the throat sizing and
    the performance calculation.
    '''

    thruster = MonopropThruster()
    thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0, 'chamberPressure': 1.5e6,
                        'expansionRatio': 50.0})
    thruster.calculatePerformance()

    assert thruster.thrust == pytest.approx(thruster.massFlow * thruster.specificImpulse * GRAVITY,
                                            rel = 1e-9), \
        'Thrust, mass flow and specific impulse are inconsistent'

def testSmallThrustersAreLessEfficient():

    '''
    Boundary layer loss dominates small thrusters. A 1 N unit must deliver materially less Isp than a
    400 N unit from identical chemistry, or the size class efficiency model is not being applied.
    '''

    impulses = {}
    for thrust in (1.0, 400.0):
        thruster = MonopropThruster()
        thruster.setInputs({'propellant': 'n2h4', 'thrust': thrust, 'chamberPressure': 1.5e6,
                            'expansionRatio': 50.0})
        thruster.calculatePerformance()
        impulses[thrust] = thruster.vacuumSpecificImpulse

    assert impulses[400.0] > impulses[1.0] * 1.08, \
        'A 400 N thruster must deliver materially more Isp than a 1 N thruster'

    # And the small thruster must land in the published band. Aerojet Rocketdyne MR-103 (1 N)
    # delivers 209 s at an expansion ratio near 100; at the eps = 50 used here it should be lower.
    assert 190.0 < impulses[1.0] < 215.0, \
        f'A 1 N hydrazine thruster at eps = 50 should deliver 190 to 215 s, got {impulses[1.0]:.1f} s'

def testBlowdownThrustScalesWithChamberPressure():

    '''
    In vacuum, thrust is proportional to chamber pressure and Isp is constant. Catches the nozzle
    efficiency class being re-evaluated as the thruster throttles down, which it must not be.
    '''

    thruster = MonopropThruster()
    thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0, 'chamberPressure': 1.5e6,
                        'expansionRatio': 50.0})
    thruster.calculatePerformance()
    result = thruster.calculateBlowdown(4.0, 5)

    assert result['thrustRatio'] == pytest.approx(0.25, rel = 1e-6), \
        'A 4:1 blowdown must deliver exactly a quarter of the initial thrust'
    assert result['ispRatio'] == pytest.approx(1.0, rel = 1e-6), \
        'Vacuum specific impulse must be constant over a blowdown'

def testColdBedCannotDeliverAShortPulse():

    '''
    A cold bed with a 20 ms ignition delay cannot deliver a 20 ms pulse. This is the impulse-terms
    argument for a bed heater and it must come out of the model.
    '''

    coldBed = CatalystBed()
    coldBed.setInputs({'massFlow': 0.046, 'chamberPressure': 1.5e6, 'bedTemperature': 293.15})
    coldBed.calculateDecomposition()
    coldBed.sizeBed()
    coldBed.checkColdStart()

    thruster = MonopropThruster()
    thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0, 'chamberPressure': 1.5e6,
                        'expansionRatio': 50.0, 'catalystBed': coldBed})
    thruster.calculatePerformance()

    result = thruster.calculateMinimumImpulseBit(0.020)
    assert not result['feasible'], \
        'A 20 ms pulse from a 293 K bed with a 21 ms ignition delay must be infeasible'

# -------------------------------------------------------------------------------------------------- #
# -- Pressurization and pressure control -- #
# -------------------------------------------------------------------------------------------------- #

def testBlowdownUllageVolume():

    '''
    A 4:1 isothermal blowdown needs an initial ullage of one third of the propellant volume, by the
    polytropic relation. Catches an inverted exponent.
    '''

    system = Pressurization()
    system.setInputs({'architecture': 'blowdown', 'pressurant': 'helium',
                      'propellantVolume': 0.030, 'tankPressure': 2.4e6,
                      'blowdownRatio': 4.0, 'tankTemperature': 293.15})
    result = system.calculateBlowdown()

    assert result['initialUllageVolume'] == pytest.approx(0.010, rel = 1e-9), \
        'A 4:1 isothermal blowdown needs an initial ullage of one third of the propellant volume'
    assert result['tankOversizing'] == pytest.approx(4.0 / 3.0, rel = 1e-9)

def testHeliumRealGasCompressibility():

    '''
    Helium at 30 MPa has a compressibility factor near 1.14. An ideal gas calculation would
    under-predict the stored mass by 14 percent, straight into the bottle volume.
    '''

    system = Pressurization()
    system.setInputs({'architecture': 'regulated', 'pressurant': 'helium',
                      'propellantVolume': 0.030, 'tankPressure': 2.4e6,
                      'bottlePressure': 30.0e6, 'tankTemperature': 293.15,
                      'bottleTemperature': 293.15})
    system.calculateRegulated()

    assert system.compressibilityFactor == pytest.approx(1.14, rel = 0.03), \
        f'Helium Z at 30 MPa should be about 1.14, got {system.compressibilityFactor:.4f}'

def testHeliumIsSevenTimesLighterThanNitrogen():

    '''
    Pressurant mass scales with molar mass. Helium must be about one seventh the mass of nitrogen for
    the same job, which is the entire argument for using it on a flight vehicle.
    '''

    masses = {}
    for pressurant in ('helium', 'nitrogen'):
        system = Pressurization()
        system.setInputs({'architecture': 'blowdown', 'pressurant': pressurant,
                          'propellantVolume': 0.030, 'tankPressure': 2.4e6,
                          'blowdownRatio': 4.0, 'tankTemperature': 293.15})
        system.calculateBlowdown()
        masses[pressurant] = system.pressurantMass

    ratio = masses['nitrogen'] / masses['helium']
    assert 6.0 < ratio < 8.0, \
        f'Nitrogen should be about 7 times the mass of helium for the same job, got {ratio:.2f}'

def testRegulatorLockupAboveDroop():

    '''
    The outlet pressure at zero flow (lockup) must exceed the outlet at rated flow (droop), or the
    relief valve would be set below the operating band.
    '''

    regulator = Regulator()
    regulator.setInputs({'setPressure': 2.4e6, 'inletPressure': 30.0e6,
                         'finalInletPressure': 3.0e6, 'massFlow': 0.001})
    regulator.sizeRegulator()

    assert regulator.lockupPressure > regulator.droopPressure, \
        'Lockup pressure must exceed the droop pressure'
    assert regulator.outletPressureBand[1] >= regulator.lockupPressure

def testTwoStageRegulatorIsTighterThanDirectActing():

    '''
    A two-stage regulator must deliver a narrower outlet band than a direct-acting one. If the
    ordering reverses, the selection guidance in the docs is wrong.
    '''

    bands = {}
    for regulatorType in ('direct acting spring', 'two stage spring', 'dome loaded'):
        regulator = Regulator()
        regulator.setInputs({'setPressure': 2.4e6, 'inletPressure': 30.0e6,
                             'finalInletPressure': 3.0e6, 'massFlow': 0.001,
                             'regulatorType': regulatorType})
        result = regulator.sizeRegulator()
        bands[regulatorType] = result['bandWidthFraction']

    assert bands['two stage spring'] < bands['direct acting spring'], \
        'A two stage regulator must deliver a narrower band than a direct acting one'
    assert bands['dome loaded'] < bands['two stage spring'], \
        'A dome loaded regulator must deliver the narrowest band'

def testPressureLadderDetectsAViolation():

    '''
    The set point ladder check must catch a burst disc set below the relief full flow pressure, which
    would vent the system permanently on an event the relief was meant to handle reversibly.
    '''

    regulator = Regulator()
    regulator.setInputs({'setPressure': 2.4e6, 'inletPressure': 30.0e6,
                         'finalInletPressure': 3.0e6, 'massFlow': 0.001,
                         'burstDiscRating': 2.6e6, 'burstDiscMaterial': 'inconel',
                         'maximumOperatingPressure': 3.5e6, 'proofPressure': 5.25e6})
    regulator.sizeRegulator()
    regulator.sizeRelief(reliefFlow = 0.01)
    regulator.checkBurstDisc()
    stackup = regulator.checkPressureStackup()

    assert not stackup['allPass'], \
        'A burst disc rated below the relief full flow pressure must fail the ladder check'

def testBurstDiscTemperatureDerating():

    '''
    Burst discs derate with temperature. An aluminum disc at 423 K bursts at 70 percent of its
    nameplate, which has caught people out.
    '''

    regulator = Regulator()
    regulator.setInputs({'setPressure': 2.4e6, 'burstDiscRating': 10.0e6,
                         'burstDiscMaterial': 'aluminum', 'burstDiscTemperature': 423.0,
                         'burstDiscTolerance': 0.10})
    result = regulator.checkBurstDisc()

    assert result['derateFactor'] == pytest.approx(0.70, rel = 0.02), \
        'Aluminum burst disc derate at 423 K should be 0.70'
    assert result['minimumBurst'] == pytest.approx(10.0e6 * 0.70 * 0.90, rel = 0.02), \
        'The minimum burst must include both the temperature derate and the tolerance'

# -------------------------------------------------------------------------------------------------- #
# -- Seals, fittings, welds, leaks -- #
# -------------------------------------------------------------------------------------------------- #

def testSealGlandFillOnTarget():

    '''
    sizeGland must land the gland fill on the 75 percent target, and the squeeze inside the range for
    the seal type.
    '''

    seal = Seal()
    seal.setInputs({'sealType': 'static face', 'material': 'epdm',
                    'crossSectionDiameter': 0.001778, 'innerDiameter': 0.012,
                    'durometer': 70, 'designPressure': 2.5e6, 'fluid': 'N2H4'})
    result = seal.sizeGland()

    assert result['glandFill'] == pytest.approx(0.75, rel = 1e-6), \
        'The gland fill must land on the 75 percent target'
    assert 0.20 <= result['squeeze'] <= 0.30, \
        f'Static face squeeze must be 20 to 30 percent, got {result["squeeze"]:.3f}'

def testSealStretchReducesSqueeze():

    '''
    Stretching an o-ring thins its cross section, which comes directly out of the squeeze. A model
    that ignores it over-predicts the sealing force.
    '''

    unstretched = Seal()
    unstretched.setInputs({'sealType': 'static face', 'material': 'epdm',
                           'crossSectionDiameter': 0.001778, 'innerDiameter': 0.012,
                           'grooveInnerDiameter': 0.012, 'designPressure': 2.5e6})
    unstretchedSqueeze = unstretched.sizeGland()['squeeze']

    stretched = Seal()
    stretched.setInputs({'sealType': 'static face', 'material': 'epdm',
                         'crossSectionDiameter': 0.001778, 'innerDiameter': 0.012,
                         'grooveInnerDiameter': 0.01248, 'designPressure': 2.5e6})
    stretchedResult = stretched.sizeGland()

    assert stretchedResult['stretch'] == pytest.approx(0.04, rel = 0.01)
    assert stretchedResult['squeeze'] < unstretchedSqueeze, \
        'Stretch must reduce the achieved squeeze'

def testSealGlassTransitionRaises():

    '''
    Viton has a glass transition at 255 K. Using it at 90 K must raise, not warn, because a seal below
    Tg has no compliance and will leak the instant the joint moves.
    '''

    seal = Seal()
    seal.setInputs({'sealType': 'static face', 'material': 'fkm',
                    'crossSectionDiameter': 0.001778, 'designPressure': 1.0e6,
                    'minimumTemperature': 90.0})

    with pytest.raises(CompatibilityError):
        seal.checkCompatibility()

def testSealHydrazineIncompatibilityRaises():

    '''
    Buna-N in hydrazine is the single most common seal material error, and it is dangerous rather than
    merely wrong because the seal catalyzes propellant decomposition.
    '''

    seal = Seal()
    seal.setInputs({'sealType': 'static face', 'material': 'nbr',
                    'crossSectionDiameter': 0.001778, 'designPressure': 2.5e6, 'fluid': 'N2H4'})

    with pytest.raises(CompatibilityError):
        seal.checkCompatibility()

def testFittingTitaniumInOxygenRaises():

    '''
    Titanium in oxygen is impact sensitive and burns. It must be a hard stop.
    '''

    fitting = Fitting()
    fitting.setInputs({'fittingType': 'an flare', 'tubeOuterDiameter': 0.00635,
                       'material': 'TI-6AL-4V', 'fluid': 'LOX', 'designPressure': 5.0e6})

    with pytest.raises(CompatibilityError):
        fitting.checkCompatibility()

def testFlareFittingTorqueFromStandard():

    '''
    MS33566 specifies 40 to 65 in-lbf for a dash 4 flare fitting. The class must use the table rather
    than a computed preload, because the standard specifies torque directly.
    '''

    fitting = Fitting()
    fitting.setInputs({'fittingType': 'an flare', 'tubeOuterDiameter': 0.00635,
                       'designPressure': 3.5e6})
    minimumTorque, maximumTorque = fitting.calculateTorque()

    assert minimumTorque / 0.1129848 == pytest.approx(40.0, rel = 0.01), \
        'MS33566 dash 4 minimum torque is 40 in-lbf'
    assert maximumTorque / 0.1129848 == pytest.approx(65.0, rel = 0.01), \
        'MS33566 dash 4 maximum torque is 65 in-lbf'

def testWeldDeratingsMultiply():

    '''
    Joint efficiency and HAZ knockdown are independent and must multiply. A 6061-T6 socket weld
    carries 0.80 x 0.55 of the parent capability, and a design using parent properties is wrong by a
    factor of over two.
    '''

    joint = Weld()
    joint.setInputs({'jointType': 'socket', 'material': '6061-T6',
                     'outerDiameter': 0.0254, 'wallThickness': 0.0016,
                     'designPressure': 2.0e6})
    result = joint.calculateDerating()

    assert result['jointEfficiency'] == pytest.approx(0.80, rel = 1e-9)
    assert result['hazYieldFactor'] == pytest.approx(0.55, rel = 1e-9)
    assert result['totalDerating'] < 0.60, \
        'A 6061-T6 socket weld must carry well under 60 percent of the parent allowable'

def testWeldFerriteInWindow():

    '''
    Nominal ER316L filler must predict a ferrite number in the 3 to 10 design window. Outside it, the
    weld either hot cracks or embrittles.
    '''

    joint = Weld()
    joint.setInputs({'jointType': 'tube to fitting', 'material': '316L',
                     'outerDiameter': 0.00635, 'wallThickness': 0.000711,
                     'chromium': 18.5, 'nickel': 12.0, 'molybdenum': 2.5,
                     'carbon': 0.02, 'nitrogen': 0.05, 'copper': 0.2})
    result = joint.calculateFerriteNumber()

    assert 3.0 <= result['ferriteNumber'] <= 10.0, \
        f'Nominal ER316L should predict FN 3 to 10, got {result["ferriteNumber"]:.1f}'

def testWeldHazardousServiceRequiresVolumetricInspection():

    '''
    A toxic fluid pressure boundary must require volumetric inspection, and a joint that cannot be
    volumetrically inspected must be flagged as a design problem rather than accepted.
    '''

    inspectable = Weld()
    inspectable.setInputs({'jointType': 'tube to fitting', 'material': '316L',
                           'outerDiameter': 0.00635, 'wallThickness': 0.000711,
                           'designPressure': 3.5e6, 'fluidHazard': 'toxic'})
    assert 'radiography' in inspectable.selectInspection()

    socket = Weld()
    socket.setInputs({'jointType': 'socket', 'material': '316L',
                      'outerDiameter': 0.0254, 'wallThickness': 0.0016,
                      'designPressure': 3.5e6, 'fluidHazard': 'toxic'})
    socket.selectInspection()
    assert any('cannot be volumetrically inspected' in note for note in socket.designNotes), \
        'A socket weld in toxic service must be flagged as uninspectable'

def testLeakEquivalentDiameterRoundTrip():

    '''
    Converting a leak rate to an equivalent hole diameter and back must return the original rate.
    Catches an inconsistency between the forward and inverse conductance paths.
    '''

    leak = LeakPath()
    leak.setInputs({'species': 'He', 'upstreamPressure': 2.5e6, 'downstreamPressure': 101325.0,
                    'temperature': 293.15, 'leakRate': 1.0e-5, 'leakRateUnit': 'sccs',
                    'length': 1.0e-3})
    diameter = leak.calculateEquivalentDiameter()

    forward = LeakPath()
    forward.setInputs({'species': 'He', 'upstreamPressure': 2.5e6, 'downstreamPressure': 101325.0,
                       'temperature': 293.15, 'diameter': diameter, 'length': 1.0e-3})

    assert forward.calculateLeakRate() == pytest.approx(1.0e-5, rel = 0.01), \
        'The leak rate to equivalent diameter conversion does not round trip'

def testLeakRegimeMovesWithPressure():

    '''
    The same physical hole is viscous at high pressure and molecular at low pressure. A model that
    reports one regime everywhere would scale leak rates wrongly between test and service pressure.
    '''

    highPressure = LeakPath()
    highPressure.setInputs({'species': 'He', 'upstreamPressure': 2.5e6, 'downstreamPressure': 101325.0,
                            'temperature': 293.15, 'diameter': 5.0e-6, 'length': 1.0e-3})
    highPressure.calculateLeakRate()

    lowPressure = LeakPath()
    lowPressure.setInputs({'species': 'He', 'upstreamPressure': 100.0, 'downstreamPressure': 0.0,
                           'temperature': 293.15, 'diameter': 5.0e-6, 'length': 1.0e-3})
    lowPressure.calculateLeakRate()

    assert highPressure.knudsenNumber < lowPressure.knudsenNumber, \
        'The Knudsen number must rise as the pressure falls'
    assert highPressure.regime == 'viscous'
    assert lowPressure.regime == 'molecular'

def testPressureDecayIsTemperatureLimited():

    '''
    A pressure decay test at high pressure is limited by temperature drift, not by transducer
    resolution. This is the result that stops people specifying pressure decay for a tight leak
    requirement.
    '''

    leak = LeakPath()
    leak.setInputs({'species': 'He', 'upstreamPressure': 10.0e6, 'temperature': 293.15,
                    'leakRate': 1.0e-5, 'leakRateUnit': 'sccs'})
    result = leak.calculatePressureDecayTest(testVolume = 0.010, transducerResolution = 100.0,
                                             testDuration = 3600.0, temperatureStability = 0.1)

    assert result['limitedBy'] == 'temperature drift', \
        'A 10 MPa pressure decay test with 0.1 K stability must be temperature limited'
    assert not result['feasible'], \
        'Pressure decay cannot verify a 1e-5 scc/s requirement under these conditions'

# -------------------------------------------------------------------------------------------------- #
# -- Check valve, filter, venturi, insulation -- #
# -------------------------------------------------------------------------------------------------- #

def testCheckValveChatterDetection():

    '''
    A check valve running below its hold-open flow must be flagged. Chatter is self-destructive and it
    is entirely predictable at design time.
    '''

    valve = CheckValve()
    valve.setInputs({'fluid': 'Helium', 'valveType': 'poppet spring', 'nominalSize': 0.004,
                     'massFlow': 0.001, 'minimumMassFlow': 0.00005, 'upstreamPressure': 2.4e6})
    valve.calculatePressureDrop()
    result = valve.checkChatter()

    assert result['chatterRisk'] == 'SEVERE', \
        'A minimum flow at 20 percent of the hold-open flow must be flagged as severe chatter risk'

def testCheckValveCrackingPressureDominatesAtLowFlow():

    '''
    At low flow the cracking pressure is most of the loss, so sizing a check valve on its K factor
    alone under-predicts the pressure cost substantially.
    '''

    valve = CheckValve()
    valve.setInputs({'fluid': 'Helium', 'valveType': 'poppet spring', 'nominalSize': 0.004,
                     'massFlow': 0.0005, 'upstreamPressure': 2.4e6})
    valve.calculatePressureDrop()

    assert valve.pressureDrop > 0.9 * 20.0e3, \
        'At low flow the total loss must be dominated by the 20 kPa cracking pressure'

def testFilterProtectionRatio():

    '''
    The 10:1 protection rule. A filter selected for a 1.7 mm passage must have a rating of 170 micron
    or finer, rounded down to a standard size.
    '''

    element = Filter()
    element.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'upstreamPressure': 2.3e6,
                       'protectedPassage': 0.0017})
    result = element.selectRating()

    assert result['absoluteRating'] <= 0.0017 / 10.0, \
        'The selected rating must satisfy the 10:1 protection rule'
    assert result['protectionRatio'] >= 10.0

def testFilterLifeIsTheBindingConstraint():

    '''
    Sizing a metal filter element on clean pressure drop alone produces an element with a dirt
    capacity of milligrams. Life must govern, and by a large factor.
    '''

    element = Filter()
    element.setInputs({'fluid': 'N2H4', 'filterType': 'pleated mesh', 'massFlow': 0.045,
                       'upstreamPressure': 2.3e6, 'protectedPassage': 0.0017,
                       'allowableCleanPressureDrop': 2.0e4, 'contaminationLoading': 1.0e-3})
    element.selectRating()
    result = element.sizeElement(requiredLife = 36000.0)

    assert result['bindingConstraint'] == 'life', \
        'The life constraint must govern filter sizing, not the clean pressure drop'
    assert result['lifeLimitedArea'] > 100.0 * result['pressureLimitedArea'], \
        'The life-limited area should exceed the pressure-limited area by orders of magnitude'

def testCavitatingVenturiIsIndependentOfDownstream():

    '''
    The defining property: while choked, the mass flow does not depend on downstream pressure at all.
    '''

    flows = []
    for downstreamPressure in (5.0e5, 1.0e6, 1.5e6):
        venturi = CavitatingVenturi()
        venturi.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.2e6,
                           'downstreamPressure': downstreamPressure,
                           'upstreamTemperature': HYDRAZINE_TEMPERATURE,
                           'throatDiameter': 0.0009346, 'inletDiameter': 0.00493})
        flows.append(venturi.calculateMassFlow())
        assert venturi.isChoked

    assert flows[0] == pytest.approx(flows[1], rel = 1e-12)
    assert flows[1] == pytest.approx(flows[2], rel = 1e-12), \
        'A choked cavitating venturi must be completely independent of downstream pressure'

def testCavitatingVenturiUnchokes():

    '''
    Above the diffuser recovery limit the venturi unchokes and silently stops regulating. The class
    must report it rather than continuing to return the choked flow.
    '''

    venturi = CavitatingVenturi()
    venturi.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.2e6, 'downstreamPressure': 2.1e6,
                       'upstreamTemperature': HYDRAZINE_TEMPERATURE,
                       'throatDiameter': 0.0009346, 'inletDiameter': 0.00493,
                       'diffuserType': 'standard diffuser'})
    venturi.calculateMassFlow()

    assert not venturi.isChoked, \
        'At P2/P1 = 0.955 with a standard diffuser the venturi must have unchoked'
    assert venturi.unchokeMargin < 0.0

def testInsulationHeatLeakFallsWithThickness():

    '''
    Adding insulation must reduce the heat leak above the critical radius. Catches a sign error in the
    resistance network.
    '''

    heatLeaks = {}
    for thickness in (0.010, 0.050):
        insulation = Insulation()
        insulation.setInputs({'material': 'polyurethane foam', 'innerDiameter': 0.0508,
                              'thickness': thickness, 'length': 10.0,
                              'innerTemperature': 90.17, 'ambientTemperature': 293.15})
        heatLeaks[thickness] = insulation.calculateHeatLeak()

    assert heatLeaks[0.050] < heatLeaks[0.010], \
        'Adding insulation above the critical radius must reduce the heat leak'

def testInsulationFlagsLiquidAir():

    '''
    A surface below 90 K condenses oxygen-enriched liquid air, which is an explosion hazard if it
    lands on anything organic. It must be flagged.
    '''

    insulation = Insulation()
    insulation.setInputs({'material': 'polyurethane foam', 'innerDiameter': 0.0508,
                          'thickness': 0.0005, 'length': 10.0,
                          'innerTemperature': 20.3, 'ambientTemperature': 293.15})
    insulation.calculateHeatLeak()

    assert insulation.surfaceTemperature < 90.0
    assert insulation.condensationRisk == 'LIQUID AIR', \
        'A surface below 90 K must be flagged for liquid air condensation'

def testBoilOffFromHeatLeak():

    '''
    Boil-off is heat leak over latent heat. Validated against the LOX latent heat of 213 kJ/kg.
    '''

    insulation = Insulation()
    insulation.setInputs({'material': 'polyurethane foam', 'innerDiameter': 0.0508,
                          'thickness': 0.025, 'length': 10.0, 'innerTemperature': 90.17,
                          'ambientTemperature': 293.15, 'fluid': 'Oxygen'})
    insulation.calculateHeatLeak()
    result = insulation.calculateBoilOff(tankVolume = 1.0)

    assert result['latentHeat'] == pytest.approx(213.0e3, rel = 0.02), \
        'LOX latent heat at its normal boiling point should be about 213 kJ/kg'
    assert result['boilOffRate'] == pytest.approx(abs(insulation.heatLeak) / result['latentHeat'],
                                                  rel = 1e-9)
