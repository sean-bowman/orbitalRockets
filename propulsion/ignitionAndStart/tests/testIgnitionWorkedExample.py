# -- Tests for the ignitionAndStart worked example -- #

'''

The example argues that the start sequence exists to control accumulation rather than to give the
igniter time, and that the shutdown residual is the plumbing rather than the ramp. The tests pin
those arguments rather than the numbers, because the underlying models are registered as
unvalidated and the arguments are what survive that.

Author: Sean Bowman
Date:   09/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'ignitionAndStartLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'ignitionCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['ignitionCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from ignitionUtils import SequenceError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDesignPointStillMatchesTheChamberItCameFrom(case):

    '''
    Every geometry and flow rate in this example is an output of the propulsion hub as built out by
    combustionDevices. If they drift, this example is computing transients for a chamber that no
    longer exists.
    '''

    engine = case['engine']

    assert engine['chamberPressure'] == 10.0e6
    assert engine['throatDiameter']  == pytest.approx(0.0906)
    assert engine['oxidiserFlow'] + engine['fuelFlow'] == pytest.approx(36.81, abs = 0.01)

def testTheResidenceTimeIsTheOneCombustionDevicesComputed(case):

    start = codeInterface.buildStart(case, delay = 0.003)

    assert start.residenceTime() == pytest.approx(0.00147, abs = 1.0e-5)

# ------------------------------------------------------------------------------------------------ #
# -- The argument -- #
# ------------------------------------------------------------------------------------------------ #

def testEveryCandidateIgniterHardStartsAtMainstageFlow(case):

    '''
    The claim the example opens with, and it is the reason the rest of it follows. If some igniter
    were fast enough to light this chamber at mainstage flow, the sequence would not need to exist.
    '''

    stage = codeInterface.reportResidenceTime(case)

    for name, entry in stage['comparison']['results'].items():
        assert entry['hardStart'] is True, name

def testTheHypergolicSlugPermitsAnOrderOfMagnitudeMoreFlowThanASpark(case):

    '''
    What a cartridge actually buys. The example says it is permission to skip the slow part of the
    sequence rather than reliability, and this is the number behind that.
    '''

    stage = codeInterface.reportResidenceTime(case)

    permitted = stage['permittedFlow']

    assert permitted['hypergolic slug'] > 0.9
    assert permitted['spark, prompt'] < 0.2
    assert permitted['hypergolic slug'] > 5.0 * permitted['spark, prompt']

def testDetectionCannotActAndTheFlowScheduleCan(case):

    '''
    The result the example exists to make. Ignition detection is a mass budget rather than an
    instrumentation problem, and on this chamber the budget is spent before any sensor loop can
    respond.
    '''

    stage = codeInterface.reportDetectionWindow(case, 0.00147)

    window = stage['window']

    assert window['detectionCanAct'] is False
    assert window['window'] < window['detectionLatency']

    assert 0.0 < window['requiredFlowFraction'] < 1.0, (
        'there has to be a flow fraction that opens the window, or the argument has no conclusion')

def testTheIgniterAnswerChangesWithRestartAndWithPower(case):

    '''
    Both constraints, and each removes a different half of the list. If either stopped biting, the
    example's claim that selection is decided by these two rather than by energy would be empty.
    '''

    selections = codeInterface.reportIgniterSelection(case, 0.00147)

    once   = selections['booster, one start, powered']['viable']
    thrice = selections['upper stage, three starts']['viable']
    noPower = selections['booster, no power at the engine']['viable']

    assert len(thrice) < len(once)
    assert noPower == ['hypergolic slug']

def testTheSequenceIsOrderedAndTighterThanTheReferenceTolerance(case):

    '''
    The candidate sequence orders correctly, which it has to, and its tightest gap is inside the
    error the RS-25 calls damaging. The example says that plainly rather than presenting the
    sequence as validated.
    '''

    stage = codeInterface.reportSequence(case)

    assert stage['check']['ordered'] is True
    assert stage['check']['tightest'] > 0.0

def testPrimingTakesManyResidenceTimes(case):

    '''
    The example's claim that an engine is started when the feed volume has arrived as liquid, not
    when the igniter fires.
    '''

    stage = codeInterface.reportSequence(case)

    assert stage['priming']['primingTimeInResidenceTimes'] > 50.0

def testAnOutOfOrderSequenceIsStillRefused(case):

    '''
    The example demonstrates the refusal rather than describing it. If the guard stopped firing the
    demonstration would silently print nothing and the reader would not know.
    '''

    start = codeInterface.buildStart(case, delay = 0.003)

    broken = codeInterface.orderedSequence(case)
    broken['oxidiserValveCrack'] = 0.10

    with pytest.raises(SequenceError):
        start.checkSequence(broken)

def testTheShutdownResidualIsDominatedByTheDribbleVolume(case):

    stage = codeInterface.reportShutdown(case)

    assert stage['residual']['dribbleFraction'] > 0.7
    assert stage['order']['fuelRich'] is True

def testTheHydrogenChillDownBandIsTheWidest(case):

    stage = codeInterface.reportChillDown(case)

    assert stage['widestBand'] == 'LH2'
    assert stage['bandRatio']['LH2'] > 3.0 * stage['bandRatio']['LOX']

# ------------------------------------------------------------------------------------------------ #
# -- The example itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleNamesWhatItCannotSupport(capsys):

    '''
    The example's magnitudes are unvalidated and its rankings are not. It has to say so, because a
    reader who takes the spike pressures at face value has been misled by a tool that knew better.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'The bound is loose' in printed
    assert 'ranking' in printed

def testTheExampleRefusesRatherThanApproximatesInBothPlaces(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SequenceError' in printed
    assert 'IgnitionError' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
