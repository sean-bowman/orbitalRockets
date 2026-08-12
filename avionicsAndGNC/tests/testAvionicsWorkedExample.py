# -- Tests for the avionicsAndGNC worked example -- #

'''

The example argues that in each of its three subjects the quantity that dominates is not the
quantity that gets specified. The tests pin that, and the scope decision the domain made about what
to build at all.

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

sys.path.insert(0, os.path.join(DOMAIN, 'avionicsLibrary'))
sys.path.insert(0, ROOT)

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'avionicsCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['avionicsCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

from avionicsUtils import ControlAuthorityError

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

# ------------------------------------------------------------------------------------------------ #
# -- The chain from vehicleArchitecture -- #
# ------------------------------------------------------------------------------------------------ #

def testTheFlightTimeIsTheAscentDurationTheVehicleWasSizedFor(case):

    assert case['flight']['duration'] == 540.0

def testTheVehicleIsAerodynamicallyUnstable(case):

    '''
    A launch vehicle has its centre of pressure ahead of its centre of gravity. A positive static
    margin here would be a sign convention error and the class refuses one.
    '''

    assert case['control']['staticMargin'] < 0.0

# ------------------------------------------------------------------------------------------------ #
# -- The argument -- #
# ------------------------------------------------------------------------------------------------ #

def testTheGyroTermDominatesAndCrossesOverEarly(case):

    stage = codeInterface.reportNavigation(case)

    assert stage['drift']['dominant'] == 'gyro bias through tilt'
    assert stage['drift']['dominantShare'] > 0.9

    assert stage['crossover']['crossover'] < 120.0
    assert stage['crossover']['gyroDominatesAtFlightTime'] is True

def testTheGradeSpreadIsOrdersOfMagnitude(case):

    stage = codeInterface.reportNavigation(case)

    assert stage['grades']['spread'] > 1000.0

def testAidingBoundsRatherThanReduces(case):

    stage = codeInterface.reportNavigation(case)

    assert stage['check']['effectiveError'] < stage['check']['unaidedError']
    assert stage['check']['availability'] < 1.0

def testTheGoverningDisturbanceChangesThroughTheFlight(case):

    '''
    The result the control stage exists to produce. A gimbal sized on one condition is sized on the
    wrong one for most of the flight.
    '''

    stage = codeInterface.reportControl(case)

    results = stage['results']

    assert results['above the atmosphere']['disturbances']['governing'] == 'thrust misalignment'
    assert (results['max-Q']['disturbances']['governing']
            == 'aerodynamic at angle of attack')

def testTheGustCaseIsRefused(case):

    '''
    The margin between the design case and the gust case is where the refusal fires, and it is the
    case a vehicle is actually lost in.
    '''

    stage = codeInterface.reportControl(case)

    assert stage['results']['max-Q']['authority'] is not None
    assert stage['results']['max-Q with gust']['authority'] is None

def testTheActuatorRateIsReportedAlongsideTheAngle(case):

    stage = codeInterface.reportControl(case)

    assert stage['rate']['requiredRate'] > 0.0
    assert np.isfinite(stage['rate']['bendingSeparation'])

def testAFewChannelsCarryMostOfTheTelemetry(case):

    stage = codeInterface.reportTelemetry(case)

    largest = max(stage['rate']['detail'], key = lambda entry: entry['bitRate'])

    assert largest['share'] > 0.7
    assert largest['count'] / stage['rate']['channelCount'] < 0.2

def testTheLinkFitsAndTheRecorderHoldsTheFlight(case):

    stage = codeInterface.reportTelemetry(case)

    assert stage['link']['fits'] is True
    assert stage['recorder']['fits'] is True

# ------------------------------------------------------------------------------------------------ #
# -- The scope decision -- #
# ------------------------------------------------------------------------------------------------ #

def testTheExampleStatesWhyEachClassWasBuilt(capsys):

    '''
    The domain was scaffolded documentation-first and three classes were built anyway. The test
    applied was whether each computes something no other domain does, and the example has to say
    so, because otherwise the classes read as scope creep.
    '''

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'documentation-first' in printed
    assert 'no other domain does' in printed

def testTheExampleNamesWhatItDeliberatelyDidNotBuild(capsys):

    codeInterface.main()

    printed = capsys.readouterr().out

    for absent in ('Guidance algorithms', 'Control law synthesis', 'Kalman filtering'):
        assert absent in printed

def testTheExampleLoadedIsThisDomainsOwn():

    assert os.path.abspath(codeInterface.__file__) == os.path.abspath(
        os.path.join(DOMAIN, 'codeInterface.py'))
