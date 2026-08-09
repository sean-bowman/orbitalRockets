# -- Tests for the thermalManagement worked example -- #

'''

The worked example makes one claim that the rest of the domain exists to support: the same model,
the same hardware and the same heat pulse pass or fail depending only on when the analyst stopped
integrating. That claim is worth a test, because it is the kind of result that quietly stops being
true when a coefficient changes and nobody notices the example no longer demonstrates anything.

These tests import the example directly rather than parsing its output, so they assert on the
numbers themselves. The tolerances are loose enough to survive an honest change to the model and
tight enough to catch the example silently losing its point.

Author: Sean Bowman
Date:   08/08/2026

'''

import importlib.util
import os
import sys

import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, DOMAIN)
sys.path.insert(0, os.path.join(DOMAIN, 'thermalManagementLibrary'))

# Every domain has a codeInterface.py at its root, and a flat sys.path resolves all of them to
# the same 'codeInterface' entry in sys.modules. The second domain to be imported in a single
# pytest process silently receives the first domain's example, and its tests then pass while
# testing the wrong file.
#
# Loading by explicit path under a domain-unique module name is the fix. It is the same problem the
# libraries solve by naming their helper module thermalUtils rather than utils, and it has to be
# solved again here because the example modules cannot be renamed without breaking the documented
# 'python thermalManagement/codeInterface.py' entry point.

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'thermalCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['thermalCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

@pytest.fixture(scope = 'module')
def environment(case):

    return codeInterface.reportEnvironment(case)

@pytest.fixture(scope = 'module')
def protection(case, environment):

    return codeInterface.sizeProtection(case, environment)

@pytest.fixture(scope = 'module')
def transient(case, environment, protection):

    return codeInterface.runTransient(case, environment, protection)

# ------------------------------------------------------------------------------------------------ #
# -- The inherited environment -- #
# ------------------------------------------------------------------------------------------------ #

def testAeroheatingMatchesTheEnvironmentsDomain(environment):

    '''
    Sutton-Graves with the same constant environmentsAndLoads uses, on the same trajectory point.
    If this drifts, the chain the example claims to demonstrate has been broken at the first link.
    '''

    assert environment['heatFlux'] == pytest.approx(1.63e5, rel = 0.02)

def testIntegratedLoadIsFluxTimesDuration(environment):

    assert environment['heatLoad'] == pytest.approx(environment['heatFlux']
                                                    * environment['duration'])

# ------------------------------------------------------------------------------------------------ #
# -- The protection -- #
# ------------------------------------------------------------------------------------------------ #

def testTheShieldAblates(protection):

    '''
    Cork at this flux is above its ablation temperature, so recession is real rather than a
    radiative equilibrium that never recedes. The alternative branch is exercised in the class
    tests; here it matters that the example is on the ablating side of it.
    '''

    assert protection['flux']['isAblating'] is True
    assert (protection['flux']['equilibriumTemperature']
            >= protection['flux']['ablationTemperature'])

def testTheDesignIsInsulationLimited(protection):

    '''
    The finding text tells the reader that virgin conductivity is the lever rather than heat of
    ablation. That advice is only correct while insulation governs.
    '''

    assert protection['sizing']['limitedBy'] == 'insulation'
    assert (protection['sizing']['insulatingDepth']
            > protection['sizing']['recessionDepth'])

def testCorkBeatsThePhenolicsOnMass(protection):

    '''
    Cork is the ascent workhorse for a reason, and the example is only honest if it checked.
    PICA is lighter still, which the findings say out loud rather than hiding.
    '''

    assert protection['sizing']['arealMass'] < 25.0
    assert protection['mass'] == pytest.approx(protection['sizing']['arealMass']
                                               * 0.55, rel = 1.0e-6)

# ------------------------------------------------------------------------------------------------ #
# -- The claim the example exists to make -- #
# ------------------------------------------------------------------------------------------------ #

def testTheShortRunIsTruncatedAndSaysSo(transient):

    '''
    The short run stops when the heating stops. Two nodes are still rising, and the solver has to
    report that rather than returning a maximum as though it were a peak.
    '''

    result = transient['short']['result']

    assert result['truncated'] is True
    assert set(result['stillRising']) == {'avionics', 'bulkhead'}

def testTheLongRunIsNotTruncated(transient):

    assert transient['long']['result']['truncated'] is False

def testTheShortRunPassesAndTheLongRunFails(transient):

    '''
    This is the entire point of the example. If a model change ever makes both runs pass or both
    fail, the example still runs and still prints, but it no longer demonstrates anything, and
    this test is the only thing that will say so.
    '''

    limit = 323.15

    shortPeak = transient['short']['result']['peaks']['avionics']['peakTemperature']
    longPeak  = transient['long']['result']['peaks']['avionics']['peakTemperature']

    assert shortPeak < limit, 'the short run must pass, or there is no trap to fall into'
    assert longPeak > limit,  'the long run must fail, or the trap costs nothing'

def testTheAvionicsPeakLongAfterTheHeatingStops(transient, environment):

    '''
    Soakback is only interesting if the delay is large. A peak a few seconds after cutoff would be
    a curiosity; a peak at eight times the event duration is a different design problem.
    '''

    peakTime = transient['long']['result']['peaks']['avionics']['peakTime']

    assert peakTime > 5.0 * environment['duration']

def testTheDeeperNodePeaksLater(transient):

    '''
    Heat arrives at the avionics through the bulkhead, so the ordering is fixed by the topology
    and not by the numbers. If it ever inverts, the network has been wired wrongly.
    '''

    peaks = transient['long']['result']['peaks']

    assert peaks['tps backface']['peakTime'] < peaks['bulkhead']['peakTime']
    assert peaks['bulkhead']['peakTime']     < peaks['avionics']['peakTime']

def testEveryInteriorNodeSoaksBack(transient, environment):

    soakback = transient['long']['network'].findSoakback(
        eventEndTime = environment['duration'])

    assert soakback['nodes']['avionics']['soaksBack'] is True
    assert soakback['nodes']['bulkhead']['soaksBack'] is True
    assert soakback['nodes']['tps backface']['soaksBack'] is False

def testRadiationToTheSinkCarriesMostOfTheResistance(transient):

    '''
    The sensitivity output tells the reader where to spend effort. That advice has to follow the
    model rather than being asserted in prose.
    '''

    shares = transient['long']['network'].resistanceSensitivity()['shares']

    dominant = max(shares.items(), key = lambda item: item[1]['fraction'])

    assert dominant[0] == 'bulkhead to sink'
    assert dominant[1]['fraction'] > 0.5

# ------------------------------------------------------------------------------------------------ #
# -- The example runs end to end -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleLoadedIsThisDomainsOwn():

    '''
    Guard on a real failure. Every domain has a codeInterface.py, a flat sys.path resolves them all
    to one entry in sys.modules, and a plain `import codeInterface` in a second domain returns the
    first domain's module. The tests then pass while asserting against the wrong example.

    It was caught by a pytest collection error on the duplicate test basename rather than by
    anything checking the import, which is luck. This checks it.
    '''

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))


def testTheExampleRunsWithoutRaising(capsys):

    '''
    Every stage, including the on orbit leg the other tests do not touch.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert 'unusable' in printed, 'the sun facing sink must be reported rather than crashing'
