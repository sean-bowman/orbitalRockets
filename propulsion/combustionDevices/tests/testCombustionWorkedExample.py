# -- Tests for the combustionDevices worked example -- #

'''

The example claims one thing: a 100 kN LOX/RP-1 engine at 10 MPa cannot be regeneratively cooled by
its own fuel, and film cooling is what makes it possible rather than what optimises it.

Three sorts of test here.

The chain has to hold: the numbers inherited from the propulsion hub have to still be the hub's
numbers, because the example restates them rather than importing them and a restated number drifts.

The claim has to survive: the circuit has to keep failing to close, and the film fraction that fixes
it has to stay in a range where the c* cost is real but affordable. An example where the circuit
closes on its own demonstrates nothing.

The unvalidated inputs have to stay labelled. Two numbers decide the conclusion and neither is
sourced. If they ever stop being flagged in the output, the example starts asserting more than it
knows.

Author: Sean Bowman
Date:   08/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'combustionDevicesLibrary'))
sys.path.insert(0, ROOT)

# Loaded by path under a unique name, per the rule in BUILDOUT.md. Every domain has a
# codeInterface.py and a plain import returns whichever was imported first.

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'combustionCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['combustionCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from validation.referenceCases import THROAT_HEAT_FLUX, UNVALIDATED

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

@pytest.fixture(scope = 'module')
def loadResult(case):

    return codeInterface.computeHeatLoad(case)

@pytest.fixture(scope = 'module')
def capability(case, loadResult):

    return codeInterface.checkClosure(case, loadResult)

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the hub -- #
# ------------------------------------------------------------------------------------------------ #

def testTheInheritedGeometryStillMatchesTheHub(case):

    '''
    The example restates the hub's outputs rather than importing them, so they can drift. This runs
    the hub sizing and checks they have not.

    Restating rather than importing is deliberate: it keeps the example runnable standalone and
    keeps the two domains from depending on each other's internals. The cost is that something has
    to check, and this is it.
    '''

    sys.path.insert(0, os.path.join(ROOT, 'propulsion', 'propulsionLibrary'))

    from EngineSizing import EngineSizing

    inherited = case['inherited']

    sizing = EngineSizing()
    sizing.setInputs({'combination':      inherited['combination'],
                      'thrust':           inherited['thrust'],
                      'chamberPressure':  inherited['chamberPressure'],
                      'areaRatio':        inherited['areaRatio'],
                      'contractionRatio': inherited['contractionRatio']})

    throat = sizing.sizeThroat()

    assert throat['throatDiameter'] == pytest.approx(inherited['throatDiameter'], abs = 0.0005)
    assert throat['oxidiserFlow']   == pytest.approx(inherited['oxidiserFlow'],   abs = 0.05)
    assert throat['fuelFlow']       == pytest.approx(inherited['fuelFlow'],       abs = 0.05)

def testTheHubPlaceholderIsCarriedForComparison(case):

    '''
    The example exists partly to replace a placeholder, so the placeholder has to be visible in the
    output rather than silently superseded.
    '''

    inherited = case['inherited']

    assert inherited['hubHeatLoadPlaceholder'] > 0.0
    assert inherited['hubPlaceholderFraction'] == pytest.approx(0.02)

# ------------------------------------------------------------------------------------------------ #
# -- The heat load, and its bound -- #
# ------------------------------------------------------------------------------------------------ #

def testBartzExceedsTheHubPlaceholderByAboutThree(loadResult, case):

    ratio = loadResult['heat']['totalLoad'] / case['inherited']['hubHeatLoadPlaceholder']

    assert 2.5 < ratio < 3.5

def testThePeakFluxFallsInsideTheMeasuredBand(loadResult):

    '''
    The bounding check. A computed peak throat flux outside the range measured across the open
    literature would mean something is wrong at the order-of-magnitude level.

    It is a weak check and it is labelled as one: the band spans a factor of three across different
    propellants, scales and pressures, so it would not catch an error of fifty per cent.
    '''

    band = THROAT_HEAT_FLUX['measured range, open literature']

    peak = loadResult['heat']['peakFlux']

    assert band['lower'] <= peak <= band['upper'], (
        f'{peak / 1.0e6:.1f} MW/m^2 is outside the measured {band["lower"] / 1.0e6:.0f} to '
        f'{band["upper"] / 1.0e6:.0f} MW/m^2')

def testTheDivergentSectionCarriesAThirdOfTheLoad(loadResult):

    heat = loadResult['heat']

    share = heat['sections']['divergent']['load'] / heat['totalLoad']

    assert 0.3 < share < 0.5

# ------------------------------------------------------------------------------------------------ #
# -- The claim the example exists to make -- #
# ------------------------------------------------------------------------------------------------ #

def testTheRegenerativeCircuitDoesNotClose(capability):

    '''
    The whole point. If this ever starts closing, the example demonstrates nothing and the finding
    has quietly reversed.
    '''

    assert capability['feasible'] is False
    assert capability['outletTemperature'] > capability['limit']

def testClosingWouldNeedMoreFuelThanTheEngineBurns(capability, case):

    assert capability['requiredFlow'] > case['inherited']['fuelFlow']

def testFilmCoolingClosesTheCircuitAtAnAffordableFraction(case, loadResult, capability):

    '''
    The trade has to land somewhere useful. A film fraction below a couple of per cent would mean
    the problem was not real; above about fifteen would mean film cooling was not the answer either.
    '''

    film = codeInterface.sizeFilmCooling(case, loadResult, capability)

    assert film['chosen'] is not None, 'no film fraction tried closes the circuit'
    assert 0.02 <= film['chosen'] <= 0.15

def testTheFilmCoolingPenaltyIsReportedAsARangeNotAValue(case, loadResult, capability):

    '''
    Regression guard on a correction. The class originally asserted the c* penalty equalled the
    film fraction, which is the pessimistic end of a range stated as a value and overstates it by
    two to three times. It is now a range, and a range is what an unsourced number should be.
    '''

    film = codeInterface.sizeFilmCooling(case, loadResult, capability)

    entry = film['results'][film['chosen']]

    assert entry['lossLower'] < entry['lossUpper']
    assert entry['lossUpper'] < film['chosen'], (
        'the upper bound of the penalty must still be below the film fraction itself')

def testMoreFilmCoolingRemovesMoreLoad(case, loadResult, capability):

    film = codeInterface.sizeFilmCooling(case, loadResult, capability)

    fractions = sorted(film['results'])
    removed   = [film['results'][f]['removed'] for f in fractions]

    assert removed == sorted(removed)

# ------------------------------------------------------------------------------------------------ #
# -- The unvalidated inputs stay labelled -- #
# ------------------------------------------------------------------------------------------------ #

def testTheTwoDecidingNumbersAreRegisteredAsUnvalidated():

    '''
    The coolant limit decides whether the circuit closes and the film penalty prices the fix.
    Neither is sourced. Both have to stay in the register, because an unvalidated number that
    stops being labelled is worse than one that was never checked.
    '''

    assert 'coolantLimits' in UNVALIDATED
    assert 'filmCoolingPenalty' in UNVALIDATED

    for name in ('coolantLimits', 'filmCoolingPenalty'):
        assert UNVALIDATED[name]['consequence']
        assert UNVALIDATED[name]['nextStep']

def testTheExampleSaysWhichNumbersAreUnvalidated(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'UNVALIDATED' in printed
    assert 'unvalidated' in printed
    assert 'bounding check and not a validation' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
