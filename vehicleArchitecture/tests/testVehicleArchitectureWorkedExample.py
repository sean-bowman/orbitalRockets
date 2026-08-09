# -- Tests for the vehicleArchitecture worked example -- #

'''

The example traces one bar of feed system pressure drop to the payload and finds it worth several
hundred kilograms of liftoff mass. The tests pin that chain, and the two arguments the example
shows are not worth having.

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

sys.path.insert(0, os.path.join(DOMAIN, 'vehicleArchitectureLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'vehicleArchitectureCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['vehicleArchitectureCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from vehicleUtils import ClosureError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from the reference -- #
# ------------------------------------------------------------------------------------------------ #

def testTheReferenceMassesAreThePublishedOnes(case):

    reference = case['reference']

    assert reference['stageOneDryMass']      == 22200.0
    assert reference['stageOneGrossMass']    == 433100.0
    assert reference['payloadToLeoExpended'] == 22800.0

def testTheReferenceVehicleReproducesALowEarthOrbitDeltaV(case):

    stage = codeInterface.reportReferenceCheck(case)

    assert stage['performance']['totalDeltaV'] == pytest.approx(9300.0, rel = 0.03)

def testTheSpecificImpulsesAreStatedAsLowerConfidenceThanTheMasses(case):

    '''
    The masses are published together and the specific impulses are not, so the delta-V check is
    good to a few per cent rather than to one. That has to stay recorded, because a check quoted
    tighter than its weakest input is not a check.
    '''

    from validation.referenceCases import LAUNCH_VEHICLES

    note = LAUNCH_VEHICLES['Falcon 9 Block 5']['engineNote']

    assert 'lower confidence' in note

# ------------------------------------------------------------------------------------------------ #
# -- The arguments not worth having -- #
# ------------------------------------------------------------------------------------------------ #

def testTheStagingSplitAndTheThrustToWeightAreBothSettled(case):

    stage = codeInterface.reportFlatOptima(case, (22200.0 / 433100.0, 4000.0 / 111500.0))

    assert stage['flatness']['isFlat'] is True
    assert stage['flatness']['worstPenalty'] < 0.01

    assert stage['sweep']['optimumInsidePracticalBand'] is False

def testTheAscentBudgetIsCloseToTheTargetTheExampleSizesTo(case):

    '''
    The example sizes to 9300 m/s and computes an ascent budget separately. If the two drifted
    apart the vehicle would be sized to a number its own trajectory section disagrees with.
    '''

    stage = codeInterface.reportFlatOptima(case, (22200.0 / 433100.0, 4000.0 / 111500.0))

    required = stage['budget']['requiredDeltaV']

    assert abs(required - case['mission']['targetDeltaV']) < 600.0

# ------------------------------------------------------------------------------------------------ #
# -- The correction -- #
# ------------------------------------------------------------------------------------------------ #

def testElasticityRisesAsPayloadFractionFalls(case):

    '''
    The example's correction to this domain's own stated ethos, asserted across the whole sweep
    rather than at its endpoints.
    '''

    results = codeInterface.reportSensitivity(case, (22200.0 / 433100.0, 4000.0 / 111500.0))

    ordered = sorted(results.values(), key = lambda entry: -entry['payloadFraction'])

    elasticities = [abs(entry['elasticity']) for entry in ordered]

    assert elasticities == sorted(elasticities), (
        'elasticity should rise monotonically as payload fraction falls')

    assert elasticities[0] < 1.0
    assert elasticities[-1] > 1.0

# ------------------------------------------------------------------------------------------------ #
# -- The mass chain -- #
# ------------------------------------------------------------------------------------------------ #

def testOneBarOfFeedPressureIsWorthHundredsOfKilograms(case):

    '''
    The number this domain exists to produce.
    '''

    trace = codeInterface.reportMassChain(case)

    assert trace['liftoffChange'] > 300.0
    assert trace['amplification'] > 5.0

def testTheMassChainIsMonotonicInPressure(case):

    results = codeInterface.reportPressureFed(case)

    closed = [entry for entry in results.values() if entry is not None]

    liftoffs = [entry['liftoffMass'] for entry in closed]

    assert liftoffs == sorted(liftoffs), 'liftoff mass must rise with tank pressure'

    assert liftoffs[-1] / liftoffs[0] > 1.5, 'pressure fed should be far heavier'

def testTheBudgetShowsGrowthAndMarginSeparately(case):

    stage = codeInterface.reportMassBudget(case)

    assert stage['margin']['growth'] > 0.0
    assert stage['margin']['margin'] > 0.0
    assert stage['margin']['required'] > stage['margin']['predicted'] > stage['margin']['estimate']

# ------------------------------------------------------------------------------------------------ #
# -- The example itself -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleNamesTheLimitationInItsOwnTankModel(capsys):

    '''
    The pressure vessel model has no minimum manufacturing gauge, so the thin-wall end of the
    pressure sweep is optimistic. The example says so rather than letting the table stand.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'minimum' in printed and 'gauge' in printed

def testTheExampleStatesWhatItCannotChooseOn(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'chosen on one axis' in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
