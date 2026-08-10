# -- Tests for the mechanismsAndSeparation worked example -- #

'''

The example walks one stage separation from the band that holds the joint to the panel that deploys
afterwards, and its argument is that single-shot hardware is simple and its confidence is expensive.
The tests pin that argument.

Author: Sean Bowman
Date:   09/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'mechanismsAndSeparationLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'mechanismsCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['mechanismsCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from mechanismUtils import REQUIRED_TORQUE_MARGIN, MarginError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from vehicleArchitecture -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSeparatingMassesAreTheVehicleTheOtherDomainClosed(case):

    '''
    The separating and remaining masses are the two stages vehicleArchitecture sized. If they drift
    this example is separating stages that no longer exist.
    '''

    separation = case['separation']

    assert separation['separatingMass'] == 1800.0
    assert separation['remainingMass'] == 6000.0

def testTheInertiaIsATransverseOneRatherThanABoltCircleEstimate(case):

    '''
    Regression guard on a defect that shipped in the library. A transverse inertia estimated from
    the bolt circle radius understates it by an order of magnitude.
    '''

    separation = case['separation']

    boltCircleEstimate = 0.5 * separation['separatingMass'] * separation['springRadius'] ** 2

    assert separation['inertia'] > 5.0 * boltCircleEstimate

# ------------------------------------------------------------------------------------------------ #
# -- The argument -- #
# ------------------------------------------------------------------------------------------------ #

def testTheJointLosesRealPreloadToStorage(case):

    stage = codeInterface.reportClampBand(case)

    assert stage['relaxation']['totalLoss'] > 0.05

    fresh  = stage['trace'][0.0]['retained']
    stored = stage['trace'][24.0]['retained']

    assert stored < fresh

def testTheWedgeIsWhatMakesTheDeviceWork(case):

    stage = codeInterface.reportClampBand(case)

    assert stage['preload']['amplification'] > 15.0
    assert stage['preload']['wedgeEfficiency'] < 1.0

def testTheFiringCircuitFiresAndTheStrayCurrentIsSafe(case):

    stage = codeInterface.reportInitiator(case)

    assert stage['allFire']['fires'] is True
    assert stage['noFire']['safe'] is True

    assert stage['allFire']['allFireRatio'] > 1.5

def testTheSeparationClearsWithMargin(case):

    stage = codeInterface.reportSeparation(case)

    assert stage['recontact']['clearanceFactor'] > 2.0
    assert stage['recontact']['meetsConvention'] is True

def testTheWorstCaseTipoffIsFlatAndTheStatisticalCaseIsNot(case):

    '''
    The result the example was not written expecting, and the one its narrative was corrected to.
    '''

    stage = codeInterface.reportSeparation(case)

    counts = stage['counts']

    assert counts['worstCaseIsFlat'] is True

    statistical = [entry['statistical'] for entry in counts['results'].values()]

    assert statistical == sorted(statistical, reverse = True)

def testTheDamperBuysLatchEnergyAndCostsDeploymentTime(case):

    stage = codeInterface.reportDeployment(case)

    assert stage['damper']['damperNeeded'] is True
    assert stage['damped']['impactEnergy'] < stage['undamped']['impactEnergy']
    assert stage['damped']['deploymentTime'] > stage['undamped']['deploymentTime']

def testTestEvidenceMovesTheMarginWithoutADesignChange(case):

    stage = codeInterface.reportMargins(case)

    results = stage['comparison']['results']

    assert (results['acceptance test, extremes']['margin']
            > 2.0 * results['theory or analysis']['margin'])

    for entry in results.values():
        assert entry['margin'] >= REQUIRED_TORQUE_MARGIN

# ------------------------------------------------------------------------------------------------ #
# -- The example itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleStatesTheThresholdCorrection(capsys):

    '''
    Reading the standard rather than a summary changed every margin verdict in this domain, and the
    example has to say so, because a reader who takes the summary's 1.0 will think this hardware is
    twice as marginal as it is.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'at or above 0, not one' in printed
    assert 'summary' in printed

def testTheExampleNamesWhatItDoesNotCompute(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'Pyroshock prediction is test-derived' in printed
    assert 'Tribology' in printed

def testTheExampleShowsTheStallRefusalRatherThanDescribingIt(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'MechanismsAndSeparationError' in printed
    assert 'stalls' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
