# -- Tests for the extrusionHoning library -- #

'''

Tiered tests for ExtrusionHoning.

Tier 1 covers the guards: inputs that must raise, and outputs that must never be silently wrong.
Tier 2 validates against published process data and against the other tables in this repository.
Tier 3 covers self-consistency and the scaling laws that have to hold whatever the inputs.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'extrusionHoningLibrary'))


from ExtrusionHoning import (ExtrusionHoning, MEDIA_GRADES, ABRASIVE_TYPES,
                             ROUGHNESS_FLOOR_DIVISOR, FLOW_BALANCE_TOLERANCE)
from honingUtils import InvalidInputError, ProcessInfeasibleError, roughnessTable

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testPassageTooSmallForAnyMediaRaises():

    '''
    Below the smallest media grade the putty cannot be extruded through the passage at any practical
    pressure, so the process is unavailable rather than slow.
    '''

    honing = ExtrusionHoning()
    with pytest.raises(ProcessInfeasibleError):
        honing.setInputs({'passageDiameter': 0.00005})

def testUnknownAbrasiveRaises():

    '''
    Abrasive hardness relative to the workpiece sets the removal efficiency.
    '''

    honing = ExtrusionHoning()
    with pytest.raises(InvalidInputError):
        honing.setInputs({'passageDiameter': 0.005, 'abrasiveType': 'sand'})

def testEmptyBranchListRaises():

    '''
    A flow split with no branches is a category error.
    '''

    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.005})

    with pytest.raises(InvalidInputError):
        honing.calculateFlowSplit([])

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testFinishImprovementMatchesTheSharedRoughnessTable():

    '''
    THE CROSS-DOMAIN CONSISTENCY TEST. common/materials.py carries the LPBF as-built roughness at
    20 um and the post-abrasive-flow value at 5 um, a factor of four. This class predicts the
    improvement independently from the media grit size and the decay law, and the two must agree.

    Without this test the shared table and the process model drift apart, and a document quoting
    either one becomes wrong.
    '''

    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.00476, 'passageLength': 0.180,
                      'material': 'Inconel 718', 'condition': 'lpbf hip + sta',
                      'cycleCount': 20})
    honing.calculateWallShear()
    result = honing.calculateSurfaceFinish()

    assert result['initialRoughness'] == pytest.approx(roughnessTable('lpbf as-built'), rel = 1e-9)
    assert result['finalRoughness'] == pytest.approx(roughnessTable('lpbf abrasive flow'),
                                                     rel = 0.10), \
        'The predicted finish must match roughnessTable(\'lpbf abrasive flow\'), or the shared ' \
        'table and the process model have drifted'
    assert result['improvementRatio'] == pytest.approx(4.0, rel = 0.10)

def testWallShearIsAForceBalance():

    '''
    tau_w = dP D / (4 L) is a force balance on the media column and it does not depend on the
    rheology at all. The pressure drop has to be reacted by shear on the wall, whatever the media is
    made of.
    '''

    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.005, 'passageLength': 0.200,
                      'extrusionPressure': 8.0e6})
    result = honing.calculateWallShear()

    expected = 8.0e6 * 0.005 / (4.0 * 0.200)
    assert result['wallShearStress'] == pytest.approx(expected, rel = 1e-9)

def testRoughnessFloorIsSetByGritSize():

    '''
    The abrasive cannot produce a surface finer than the scratch it leaves, so the floor scales with
    the grit. Running more cycles past it removes stock without improving the finish.
    '''

    for grade, entry in MEDIA_GRADES.items():
        honing = ExtrusionHoning()
        honing.setInputs({'passageDiameter': 0.5 * (entry['minimumPassage'] +
                                                    entry['maximumPassage']),
                          'mediaGrade': grade, 'cycleCount': 200})
        honing.calculateWallShear()
        result = honing.calculateSurfaceFinish()

        assert result['roughnessFloor'] == pytest.approx(
            entry['gritSize'] / ROUGHNESS_FLOOR_DIVISOR, rel = 1e-9)
        assert result['finalRoughness'] >= result['roughnessFloor'] * 0.999, \
            'The finish can never go below the grit-limited floor'

def testFlowSplitDiameterExponentIsAboveSix():

    '''
    For a power law fluid the conductance goes as D^(3 + 1/n), and with n near 0.28 the exponent is
    above six. THAT IS THE WHOLE PROBLEM: a ten percent diameter difference produces a seventy
    percent flow difference, and the favoured branch gets honed more, opens further and takes an
    even larger share.
    '''

    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.005})

    result = honing.calculateFlowSplit([{'diameter': 0.0050, 'length': 0.15},
                                        {'diameter': 0.0045, 'length': 0.15}])

    assert result['diameterExponent'] > 6.0

    fractions = [branch['flowFraction'] for branch in result['branches']]
    assert fractions[0] / fractions[1] > 1.5, \
        'A ten percent diameter difference must produce far more than a ten percent flow difference'

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testWallShearScalesWithPressureAndInverselyWithLength():

    '''
    Directly from the force balance. Doubling the pressure doubles the shear; doubling the length
    halves it.
    '''

    base = ExtrusionHoning()
    base.setInputs({'passageDiameter': 0.005, 'passageLength': 0.200,
                    'extrusionPressure': 7.0e6})
    baseShear = base.calculateWallShear()['wallShearStress']

    doubled = ExtrusionHoning()
    doubled.setInputs({'passageDiameter': 0.005, 'passageLength': 0.200,
                       'extrusionPressure': 14.0e6})
    assert doubled.calculateWallShear()['wallShearStress'] == pytest.approx(2.0 * baseShear,
                                                                           rel = 1e-9)

    longer = ExtrusionHoning()
    longer.setInputs({'passageDiameter': 0.005, 'passageLength': 0.400,
                      'extrusionPressure': 7.0e6})
    assert longer.calculateWallShear()['wallShearStress'] == pytest.approx(0.5 * baseShear,
                                                                          rel = 1e-9)

def testRemovalRisesSubLinearlyWithCycles():

    '''
    The passage opens as it is honed, which drops the wall shear, which slows the removal. The
    process self-limits, so doubling the cycles removes less than twice the material.
    '''

    removals = []
    for cycles in (10, 20, 40):
        honing = ExtrusionHoning()
        honing.setInputs({'passageDiameter': 0.005, 'cycleCount': cycles})
        honing.calculateWallShear()
        removals.append(honing.calculateRemoval()['radialRemoval'])

    assert removals[1] > removals[0]
    assert removals[1] / removals[0] < 2.0, 'Removal must rise sub-linearly with cycle count'
    assert removals[2] / removals[1] < 2.0

def testRoughnessDecaysMonotonicallyTowardsTheFloor():

    '''
    Exponential decay to a floor. Each cycle improves the finish by less than the last.
    '''

    roughnesses = []
    for cycles in (1, 5, 10, 20, 40):
        honing = ExtrusionHoning()
        honing.setInputs({'passageDiameter': 0.005, 'cycleCount': cycles,
                          'initialRoughness': 20.0e-6})
        honing.calculateWallShear()
        roughnesses.append(honing.calculateSurfaceFinish()['finalRoughness'])

    assert all(later < earlier for earlier, later in zip(roughnesses, roughnesses[1:]))

    firstImprovement = roughnesses[0] - roughnesses[1]
    lastImprovement  = roughnesses[-2] - roughnesses[-1]
    assert firstImprovement > lastImprovement, 'The decay must slow as the floor is approached'

def testBalancedBranchesNeedNoRestrictor():

    '''
    Identical branches split evenly and need nothing done to them. A model that recommended
    restrictors on a balanced manifold would be adding an operation for no reason.
    '''

    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.005})

    result = honing.calculateFlowSplit([{'diameter': 0.005, 'length': 0.15}] * 3)

    assert result['balanced'] is True
    assert result['imbalance'] < 1.0e-9
    assert not any(branch['needsRestrictor'] for branch in result['branches'])

def testFinerMediaSelectedForSmallerPassage():

    '''
    The media has to be soft enough to enter the passage. A small passage cannot take a coarse
    media at any pressure.
    '''

    small = ExtrusionHoning(); small.setInputs({'passageDiameter': 0.0010})
    large = ExtrusionHoning(); large.setInputs({'passageDiameter': 0.030})

    assert (MEDIA_GRADES[small.mediaGrade]['gritSize'] <
            MEDIA_GRADES[large.mediaGrade]['gritSize'])

def testReportRuns():

    '''
    Smoke test.
    '''

    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': 0.00476, 'material': 'Inconel 718',
                      'condition': 'lpbf hip + sta'})
    assert 'EXTRUSION HONING' in honing.generateReport()
