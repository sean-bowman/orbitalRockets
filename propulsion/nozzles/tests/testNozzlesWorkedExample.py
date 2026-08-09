# -- Tests for the nozzles worked example and its validation -- #

'''

The example ranks the levers available to a nozzle designer and finds the ordering is nearly the
reverse of the attention each receives. The tests pin the ordering rather than the numbers, because
the ordering is what the example is for and it is robust to models the numbers are not.

The validation section at the bottom records something the data cannot do. RS-25 publishes a
specific impulse, which is a product of c* efficiency and thrust coefficient efficiency, and
nothing published separates them. So the loss decomposition cannot be validated against it
directly, and the honest outcome is a bound rather than a comparison.

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

sys.path.insert(0, os.path.join(DOMAIN, 'nozzlesLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'nozzlesCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['nozzlesCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from NozzleLosses import NozzleLosses
from validation.referenceCases import LIQUID_ENGINES

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDesignPointStillMatchesTheHub(case):

    '''
    The example restates the hub's chosen area ratio and its separation reasoning. If the hub moves
    its design point, this example is ranking levers on a nozzle that no longer exists.
    '''

    hub = case['hubResult']

    assert hub['designPoint'] == pytest.approx(hub['summerfieldLimit'] * hub['separationMargin'],
                                               abs = 0.02)
    assert case['engine']['areaRatio'] == pytest.approx(hub['designPoint'], abs = 0.02)

# ------------------------------------------------------------------------------------------------ #
# -- The ranking -- #
# ------------------------------------------------------------------------------------------------ #

def testAltitudeCompensationIsTheLargestLever(case):

    '''
    The point of the example. Everything a contour designer controls is smaller than the one thing
    nobody has captured.
    '''

    contour      = codeInterface.reportContourLever(case)
    separation   = codeInterface.reportSeparationLever(case)
    compensation = codeInterface.reportCompensationLever(case)

    ideal = compensation['bound']['benefit']

    assert ideal > contour['coneToBell']
    assert ideal > separation['gain']
    assert ideal > 2.0 * contour['coneToBell']

def testTheSeparationCriterionIsTheSmallestLeverDespiteTheLargestChange(case):

    '''
    The surprise. Choosing Schmucker over Summerfield changes the permitted area ratio by 36 per
    cent and the delivered impulse by less than half a second, because the area ratio optimum is
    broad.
    '''

    separation = codeInterface.reportSeparationLever(case)
    contour    = codeInterface.reportContourLever(case)

    areaRatioChange = separation['schmuckerLimit'] / separation['summerfieldLimit'] - 1.0

    assert areaRatioChange > 0.30, 'the criteria should differ substantially on area ratio'
    assert separation['gain'] < 1.0, 'and hardly at all on impulse'
    assert separation['gain'] < contour['coneToBell']

def testSchmuckerMakesTheHubsRejectedOptimumReachable(case):

    '''
    The hub found its burn-average optimum at an area ratio of 25.75 and rejected it because
    Summerfield said it separates. Schmucker does not, and that is a genuine change of conclusion
    even though it is worth very little.
    '''

    separation = codeInterface.reportSeparationLever(case)

    optimum = case['hubResult']['burnAverageOptimum']

    assert optimum > separation['summerfieldLimit'], 'Summerfield should forbid it'
    assert optimum < separation['schmuckerLimit'],   'Schmucker should permit it'
    assert separation['optimumReachable'] is True

def testABellOverAConeIsWorthSeveralSecondsAndAFullerBellIsNot(case):

    '''
    The first decision was made on every flying engine decades ago. The second costs a quarter of
    the nozzle length for a third of a second, which is why nobody flies a hundred per cent bell.
    '''

    contour = codeInterface.reportContourLever(case)

    assert contour['coneToBell'] > 2.0
    assert contour['bellToFull'] < 1.0
    assert contour['coneToBell'] > 4.0 * contour['bellToFull']

def testMostOfTheCompensationGapIsAtAltitude(case):

    compensation = codeInterface.reportCompensationLever(case)

    gaps = compensation['gaps']

    assert gaps[-1] > 4.0 * gaps[0]

# ------------------------------------------------------------------------------------------------ #
# -- What the validation can and cannot do -- #
# ------------------------------------------------------------------------------------------------ #

def testThePublishedDataCannotSeparateTheTwoEfficiencies():

    '''
    The honest limit, recorded as a test so it does not get forgotten and quietly claimed as a
    validation later.

    RS-25 publishes a specific impulse. That is c* efficiency times thrust coefficient efficiency,
    and nothing published separates them. A loss decomposition that produces only the second cannot
    be checked against it without assuming the first, and assuming it is what makes the check
    circular.
    '''

    engine = LIQUID_ENGINES['RS-25']

    hubIdeal = 459.8

    combined = engine['vacuumImpulse'] / hubIdeal

    # every split of that product is consistent with the published data
    for cstarEfficiency in (0.985, 0.99, 1.00):
        implied = combined / cstarEfficiency
        assert 0.0 < implied <= 1.02, (
            'each split has to be physically admissible, which is exactly the problem')

def testTheDataDoesBoundTheCombustionEfficiencyFromBelow():

    '''
    What the published data can do. A thrust coefficient efficiency above one is impossible, so
    RS-25's c* efficiency has to be at least the combined figure.

    That is a real inference and it is another confirmation that the hub's 0.96 default is
    conservative for a best-in-class engine.
    '''

    engine = LIQUID_ENGINES['RS-25']

    combined = engine['vacuumImpulse'] / 459.8

    # eta_Cf <= 1 implies eta_c* >= combined
    assert combined > 0.96, (
        f'RS-25 implies a c* efficiency of at least {combined:.4f}, above the library default')

def testTheDecompositionIsConservativeAgainstTheBestFlyingEngine():

    '''
    Bounded rather than validated. At RS-25's area ratio the decomposition gives 0.980, and the
    thrust coefficient efficiency implied by the published impulse is between 0.984 and 1.004
    depending on the c* split assumed.

    So the decomposition is conservative, by somewhere between half a point and two and a half.
    Conservative is the right direction and the width of that range is the measure of what the
    check is worth.
    '''

    engine = LIQUID_ENGINES['RS-25']

    losses = NozzleLosses()
    losses.setInputs({'combination':     'LOX/LH2',
                      'areaRatio':       engine['areaRatio'],
                      'chamberPressure': engine['chamberPressure'],
                      'contour':         'bell 80 per cent'})

    predicted = losses.decomposeEfficiency()['overall']

    combined = engine['vacuumImpulse'] / 459.8

    # the most generous admissible split, c* efficiency of one, gives the lowest implied Cf
    lowestImplied = combined

    assert predicted < lowestImplied, (
        f'the decomposition gives {predicted:.4f} against a lowest implied {lowestImplied:.4f}; '
        f'it should be conservative')

    assert lowestImplied - predicted < 0.05, 'and not wildly so'

def testTheExampleNamesWhatItCannotValidate(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'NOVA' in printed, 'the contour boundary has to be named'
    assert 'never flown operationally' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
