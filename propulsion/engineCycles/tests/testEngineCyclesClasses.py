# -- Tests for the engineCycles classes -- #

'''

Tiered tests for the two cycle classes.

Tier 1 covers the contract: unknown cycles, a turbine flow fraction handed to a cycle with no
turbine, an expander closure check with no heat supplied, and an impulse calculation with no ideal
to compare against.

Tier 2 validates against closed forms: the pressure ladder against its own definition, the
expansion term against the isentropic relation, and the open cycle impulse against the weighted
average it is.

Tier 3 covers the structural results this sub-domain exists to produce, chiefly that the turbine
pressure ratio is what separates the cycles and that everything else follows from it.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'engineCyclesLibrary'))

from cycleUtils import (ENGINE_CYCLES, PRESSURE_LADDER, DUMPED_EXHAUST_IMPULSE_FRACTION,
                        CYCLE_TURBINE_TEMPERATURE, cycleDefinition, pressureLadder,
                        InvalidInputError, CycleError)
from EngineCycle import EngineCycle
from PowerBalance import (PowerBalance, DRIVE_GAS_GAMMA, DRIVE_GAS_SPECIFIC_HEAT,
                          BLEED_FRACTION_LIMIT)

REFERENCE = {'chamberPressure': 10.0e6, 'totalFlow': 36.81, 'pumpPower': 0.624e6,
             'idealImpulse': 298.6}

def buildCycle(cycle = 'gas generator', **overrides) -> EngineCycle:

    inputs = {'cycle': cycle, 'chamberPressure': REFERENCE['chamberPressure'],
              'idealImpulse': REFERENCE['idealImpulse'], 'turbineFlowFraction': 0.036}
    inputs.update(overrides)

    engine = EngineCycle()
    engine.setInputs(inputs)

    return engine

def buildBalance(cycle = 'gas generator', **overrides) -> PowerBalance:

    inputs = {'cycle': cycle, 'chamberPressure': REFERENCE['chamberPressure'],
              'totalFlow': REFERENCE['totalFlow'], 'pumpPower': REFERENCE['pumpPower']}
    inputs.update(overrides)

    balance = PowerBalance()
    balance.setInputs(inputs)

    return balance

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testUnknownCycleIsRejected():

    with pytest.raises(CycleError, match = 'Unknown engine cycle'):
        buildCycle('magic')

def testATurbineFlowOnAPressureFedCycleIsRejected():

    '''
    There is no turbine, so the fraction is not a small number, it is a meaningless one.
    '''

    with pytest.raises(CycleError, match = 'no turbomachinery'):
        buildCycle('pressure fed', turbineFlowFraction = 0.03)

def testAllOfTheFlowThroughTheTurbineIsRejected():

    with pytest.raises(CycleError, match = 'must lie in'):
        buildCycle(turbineFlowFraction = 1.0)

def testImpulseWithoutAnIdealIsRefused():

    '''
    The delivered impulse is a fraction of an ideal that comes from the propulsion hub. Without it
    there is nothing to take a fraction of, and guessing would be worse than refusing.
    '''

    engine = EngineCycle()
    engine.setInputs({'cycle': 'gas generator', 'chamberPressure': 10.0e6})

    with pytest.raises(CycleError, match = 'No ideal specific impulse'):
        engine.calculateImpulseDelivered()

def testAPowerBalanceOnAPressureFedCycleIsRefused():

    with pytest.raises(CycleError, match = 'no turbomachinery'):
        buildBalance('pressure fed').specificWork()

def testAnExpanderClosureCheckWithoutHeatIsRefused():

    '''
    An expander's power source is the jacket heat. A closure check without it is not a check.
    '''

    with pytest.raises(CycleError, match = 'heat available'):
        buildBalance('expander').checkClosure()

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms -- #
# ------------------------------------------------------------------------------------------------ #

def testTheOpenCycleLadderIsTheSumOfItsConsumers():

    '''
    An open cycle pump only has to reach the chamber, so its discharge is the chamber plus the
    three drops between it and them.
    '''

    ladder = pressureLadder(10.0e6, 'gas generator')

    expected = 10.0e6 * (1.0 + PRESSURE_LADDER['injector']['fraction']
                         + PRESSURE_LADDER['cooling jacket']['fraction']
                         + PRESSURE_LADDER['lines and valves']['fraction'])

    assert ladder['dischargePressure'] == pytest.approx(expected)

def testTheClosedCycleLadderIsBuiltUpFromTheTurbineExit():

    '''
    A closed cycle turbine exhausts into the main injector, so the ladder is built from chamber
    plus injector, multiplied up by the turbine pressure ratio, then the preburner on top.
    '''

    ladder = pressureLadder(10.0e6, 'staged combustion')

    exit_ = 10.0e6 * (1.0 + PRESSURE_LADDER['injector']['fraction'])

    assert ladder['turbineExit'] == pytest.approx(exit_)
    assert ladder['turbineInlet'] == pytest.approx(
        exit_ * ENGINE_CYCLES['staged combustion']['turbinePressureRatio'])

def testAnExpanderIsNotChargedAPreburnerDrop():

    '''
    An expander has no preburner: the fuel goes jacket, turbine, injector. Charging it one would
    overstate its pump discharge by a fifth of chamber pressure, and it is the cycle least able to
    afford one.
    '''

    assert ENGINE_CYCLES['expander']['hasPreburner'] is False

    ladder = pressureLadder(10.0e6, 'expander')

    assert 'preburner injector' not in ladder['consumers']

def testTheExpansionTermMatchesTheIsentropicRelation():

    for cycle in ('gas generator', 'staged combustion', 'expander'):

        balance = buildBalance(cycle)
        work    = balance.specificWork()

        ratio    = ENGINE_CYCLES[cycle]['turbinePressureRatio']
        exponent = (DRIVE_GAS_GAMMA - 1.0) / DRIVE_GAS_GAMMA

        assert work['expansionTerm'] == pytest.approx(1.0 - ratio ** (-exponent))

def testSpecificWorkIsTheProductItClaimsToBe():

    balance = buildBalance()
    work    = balance.specificWork()

    expected = (balance.turbineEfficiency * DRIVE_GAS_SPECIFIC_HEAT
                * balance.turbineInletTemperature * work['expansionTerm'])

    assert work['specificWork'] == pytest.approx(expected)

def testTheOpenCycleImpulseIsAWeightedAverage():

    engine = buildCycle('gas generator', turbineFlowFraction = 0.05)

    result = engine.calculateImpulseDelivered()

    ideal  = REFERENCE['idealImpulse']
    dumped = ideal * DUMPED_EXHAUST_IMPULSE_FRACTION

    expected = ideal * 0.95 + dumped * 0.05

    assert result['deliveredImpulse'] == pytest.approx(expected)

def testDrivingFlowIsPowerOverSpecificWork():

    balance = buildBalance()

    driving = balance.calculateDrivingFlow()

    assert driving['drivingFlow'] == pytest.approx(
        balance.pumpPower / driving['specificWork'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the structural results -- #
# ------------------------------------------------------------------------------------------------ #

def testAClosedCycleLosesNoImpulseAndAnOpenOneDoes():

    '''
    The trade in one line. Everything else about the cycles is downstream of this.
    '''

    closed = buildCycle('staged combustion').calculateImpulseDelivered()
    open_  = buildCycle('gas generator').calculateImpulseDelivered()

    assert closed['penalty'] == 0.0
    assert open_['penalty'] > 0.0
    assert closed['deliveredImpulse'] > open_['deliveredImpulse']

def testAClosedCyclePumpRunsAtRoughlyTwiceChamberPressure():

    '''
    And an open cycle pump at roughly a quarter above it. That factor is the price of closing the
    cycle and it is paid by the turbomachinery and then by the tank.
    '''

    open_  = pressureLadder(10.0e6, 'gas generator')['dischargeRatio']
    closed = pressureLadder(10.0e6, 'staged combustion')['dischargeRatio']

    assert 1.3 < open_ < 1.6
    assert 1.9 < closed < 2.4
    assert closed / open_ > 1.4

def testTheTurbinePressureRatioIsWhatSeparatesTheCycles():

    '''
    The mechanism. A closed cycle turbine exhausts into the main injector, so it gets a pressure
    ratio near one and a half rather than twenty, and the same gas delivers several times less
    work.
    '''

    open_  = buildBalance('gas generator').specificWork()
    closed = buildBalance('staged combustion').specificWork()

    assert open_['pressureRatio'] > 10.0 * closed['pressureRatio']
    assert open_['expansionTerm'] > 4.0 * closed['expansionTerm']

def testAClosedCycleNeedsFarMoreDrivingFlowForTheSamePower():

    '''
    The consequence, and the reason a staged combustion preburner passes most of one propellant
    while a gas generator passes three per cent of the total.
    '''

    open_  = buildBalance('gas generator').calculateDrivingFlow()
    closed = buildBalance('staged combustion').calculateDrivingFlow()

    assert closed['drivingFlow'] > 4.0 * open_['drivingFlow']

    assert open_['isBleed'] is True
    assert closed['isBleed'] is False

def testAnOpenCycleDrivingFlowIsASmallFraction():

    '''
    A few per cent, which matches the F-1 cycle penalty inferred when the propulsion hub library
    was validated against it.
    '''

    fraction = buildBalance('gas generator').calculateDrivingFlow()['flowFraction']

    assert 0.01 < fraction < 0.06

def testABleedIsFlaggedWhenItStopsBeingOne():

    '''
    Above ten per cent of total flow a turbine drive is a preburner, not a bleed, and the class
    says so rather than reporting a large fraction without comment.
    '''

    balance = buildBalance('staged combustion')

    driving = balance.calculateDrivingFlow()

    assert driving['flowFraction'] > BLEED_FRACTION_LIMIT
    assert driving['isBleed'] is False
    assert any('preburner' in finding for finding in driving['findings'])

def testNonExpanderCyclesCloseByBurningMorePropellant():

    '''
    They have a throttle on their power source. An expander does not, which is the whole
    distinction.
    '''

    for cycle in ('gas generator', 'staged combustion'):
        closure = buildBalance(cycle).checkClosure()
        assert closure['closes'] is True
        assert closure['limited'] is False

def testAnExpanderClosesOrNotDependingOnTheHeatAvailable():

    '''
    The expander is the only cycle in this library whose closure is a real question, because its
    power source is fixed by the chamber wall rather than by how much propellant it is willing to
    burn.
    '''

    generous = buildBalance('expander', availableHeat = 30.0e6).checkClosure()
    meagre   = buildBalance('expander', availableHeat = 2.0e6).checkClosure()

    assert generous['closes'] is True
    assert meagre['closes'] is False
    assert generous['margin'] > meagre['margin']

def testTheExpanderShortfallSaysThereIsNoInternalLever():

    '''
    The useful part of the failure message. A cycle that cannot close is not fixed by adjusting
    something inside it.
    '''

    closure = buildBalance('expander', availableHeat = 2.0e6).checkClosure()

    assert any('no lever inside the cycle' in finding for finding in closure['findings'])

def testEveryCycleHasATurbineTemperatureExceptThePressureFedOne():

    for name, definition in ENGINE_CYCLES.items():
        if definition['hasTurbomachinery']:
            assert name in CYCLE_TURBINE_TEMPERATURE, name

def testTheExpanderTurbineRunsFarColderThanACombustionDrivenOne():

    '''
    Because its inlet temperature is whatever the coolant picked up, not what a blade tolerates.
    That is the ceiling on expander cycle power and it is a different sort of limit entirely.
    '''

    assert CYCLE_TURBINE_TEMPERATURE['expander'] < \
        0.6 * CYCLE_TURBINE_TEMPERATURE['staged combustion']

def testEveryCycleComparesWithoutRaising():

    comparison = buildCycle().compareCycles()

    assert set(comparison['cycles']) == set(ENGINE_CYCLES)

    for name, entry in comparison['cycles'].items():
        assert entry['dischargeRatio'] >= 1.0, name

def testBooleanFlagsAreRealPythonBooleans():

    flags = [
        buildBalance().calculateDrivingFlow()['isBleed'],
        buildBalance().checkClosure()['closes'],
        buildBalance('expander', availableHeat = 30.0e6).checkClosure()['closes'],
    ]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testReportsRunForBothClasses():

    assert 'ENGINE CYCLE'  in buildCycle().generateReport()
    assert 'POWER BALANCE' in buildBalance().generateReport()
