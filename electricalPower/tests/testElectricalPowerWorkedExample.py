# -- Tests for the electricalPower worked example -- #

'''

The example argues that most of what decides an electrical system is decided outside it. The tests
pin that argument, and the correction the rollup forced on it.

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

sys.path.insert(0, os.path.join(DOMAIN, 'electricalPowerLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'electricalPowerCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['electricalPowerCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from fluidSystems -- #
# ------------------------------------------------------------------------------------------------ #

def testTheHeaterLoadIsPresentAndContinuous(case):

    '''
    The coupling the objectives named: a fluid system full of solenoid valves, heaters and
    transducers is an electrical system.
    '''

    heaters = next(load for load in case['loads'] if load['name'] == 'propellant line heaters')

    assert heaters['power'] > 0.0

    for phase in case['phases']:
        assert phase['name'] in heaters['dutyCycle']

def testTheBatteryIsSizedAtTheColdCase(case):

    '''
    Cold soaked on the pad rather than at flight temperature, because that is what decides the
    capacity.
    '''

    assert case['battery']['temperature'] < 0.0

# ------------------------------------------------------------------------------------------------ #
# -- The argument -- #
# ------------------------------------------------------------------------------------------------ #

def testTheHeaterIsNotTheLargestLoadButIsTheLargestUncertainty(case):

    '''
    The correction the rollup forced. The narrative originally claimed the heaters dominate the
    energy; they do not, because a continuous smaller load beats a larger cycling one. What they do
    dominate is the uncertainty.
    '''

    stage = codeInterface.reportBudget(case)

    byLoad = stage['rollup']['byLoad']

    assert byLoad['avionics']['energy'] > byLoad['propellant line heaters']['energy']
    assert byLoad['avionics']['power'] < byLoad['propellant line heaters']['power']

    assert stage['sensitivity']['spanFraction'] > case['battery']['energyMargin']

def testTheEnergyAndPeakDriversAreDifferent(case):

    stage = codeInterface.reportBudget(case)

    assert stage['drivers']['sameLoad'] is False

def testTheNameplateIsNearlyTwiceTheDeliveredEnergy(case):

    budget = codeInterface.reportBudget(case)

    stage = codeInterface.reportBattery(case,
                                        budget['rollup']['sourceEnergy'],
                                        budget['rollup']['peakPower'])

    assert stage['sized']['oversizeFactor'] > 1.7

def testTheHighestSpecificEnergyChemistryIsNotViable(case):

    budget = codeInterface.reportBudget(case)

    stage = codeInterface.reportBattery(case,
                                        budget['rollup']['sourceEnergy'],
                                        budget['rollup']['peakPower'])

    assert 'lithium thionyl chloride' not in stage['comparison']['viable']

def testVoltageDropGovernsTheGauge(case):

    stage = codeInterface.reportHarness(case)

    assert stage['sized']['binding'] == 'voltage drop'
    assert stage['sized']['dropGauge'] < stage['sized']['ampacityGauge']

def testTheTwelveVoltBusDoesNotClose(case):

    '''
    The clearest single argument for a higher bus, and it comes out of the sweep rather than being
    asserted.
    '''

    stage = codeInterface.reportHarness(case)

    assert stage['voltages']['results'][12.0] is None

def testTheHarnessMassIsCountedAndConnectorsAreSignificant(case):

    stage = codeInterface.reportHarness(case)

    assert stage['mass']['connectorCount'] > 20
    assert stage['mass']['connectorMass'] / stage['mass']['totalMass'] > 0.1

def testPeakAndHoldReturnsThreeQuarters(case):

    stage = codeInterface.reportSolenoid(case)

    assert stage['strategies']['powerSaving'] == pytest.approx(0.75)
    assert stage['drive']['forceRatio'] < 0.65

# ------------------------------------------------------------------------------------------------ #
# -- The example itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleNamesTheBoundaryWithMechanisms(capsys):

    '''
    PyroCircuit was planned for this library and deliberately not built, because
    PyrotechnicInitiator in mechanismsAndSeparation already does it. The example has to say so, or
    the omission reads as an oversight.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'PyroCircuit' in printed
    assert 'deliberately not built' in printed
    assert 'PyrotechnicInitiator' in printed

def testTheExampleStatesWhatItDoesNotModel(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'MIL-STD-461' in printed
    assert 'thermal runaway' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
