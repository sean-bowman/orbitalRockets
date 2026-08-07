# -- Tests for the castingProcesses library -- #

'''

Tiered tests for CastingProcess.

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
                                'castingProcessesLibrary'))


from CastingProcess import (CastingProcess, CASTING_FACTORS, CASTING_PROCESSES,
                            SOLIDIFICATION_SHRINKAGE, ISO_8062_TOLERANCE_100MM,
                            RISER_MODULUS_RATIO)
from castingUtils import InvalidInputError, ProcessInfeasibleError

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testUndefinedCastingFactorRaises():

    '''
    The ladder is 1.00, 1.33 and 2.00 per NASA-STD-5001. An intermediate value is somebody inventing
    a factor, and it must not be accepted silently.
    '''

    casting = CastingProcess()
    with pytest.raises(InvalidInputError):
        casting.setInputs({'process': 'investment', 'qualificationLevel': 1.15})

def testUnknownAlloyFamilyRaises():

    '''
    Solidification shrinkage ranges from 3 to 6.5 percent across the families and it sizes the
    riser. It cannot be assumed.
    '''

    casting = CastingProcess()
    with pytest.raises(InvalidInputError):
        casting.setInputs({'process': 'sand', 'alloyFamily': 'unobtainium'})

def testInfeasibleWallRaises():

    '''
    Sand casting cannot hold a 1 mm wall and no process development changes that.
    '''

    casting = CastingProcess()
    casting.setInputs({'process': 'sand', 'minimumWallThickness': 0.001})

    with pytest.raises(ProcessInfeasibleError):
        casting.checkFeasibility()

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testCastingFactorLadderAgainstStandard():

    '''
    Validated against NASA-STD-5001. A factor of 2.0 halves the allowable and 1.33 reduces it to
    0.752. These are the numbers that decide whether a cast part is viable.
    '''

    assert CASTING_FACTORS[2.00]['allowableMultiplier'] == pytest.approx(0.50, rel = 1e-9)
    assert CASTING_FACTORS[1.33]['allowableMultiplier'] == pytest.approx(1.0 / 1.33, rel = 1e-9)
    assert CASTING_FACTORS[1.00]['allowableMultiplier'] == pytest.approx(1.00, rel = 1e-9)

def testUnqualifiedCastingDoublesTheMaterial():

    '''
    The finding that makes this class worth running. For a membrane the material scales as the
    inverse of the allowable, so a 2.0 casting factor means literally twice the material for the
    same load, and no alloy substitution recovers it.
    '''

    casting = CastingProcess()
    casting.setInputs({'process': 'sand', 'alloyFamily': 'aluminium', 'qualificationLevel': 2.00})
    result = casting.selectCastingFactor()

    assert result['massPenalty'] == pytest.approx(2.0, rel = 1e-9)
    assert result['potentialMassSaving'] == pytest.approx(0.50, rel = 1e-9)

def testEveryFactorLevelStatesItsRequirements():

    '''
    The requirements column is what has to be met to earn each step, and a level with no stated
    requirements cannot be argued for at a review.
    '''

    for level, entry in CASTING_FACTORS.items():
        assert entry['requirements'], f'Casting factor {level} has no stated requirements'
        assert entry['note']

def testInvestmentHoldsFinerWallsThanSand():

    '''
    Validated against process capability. Investment casting reaches 1.5 mm where sand needs 5 mm,
    and the tolerance grades differ by three ISO steps.
    '''

    investment = CASTING_PROCESSES['investment']
    sand       = CASTING_PROCESSES['sand']

    assert investment['minimumWall'] < sand['minimumWall']
    assert (ISO_8062_TOLERANCE_100MM[investment['toleranceGrade']] <
            ISO_8062_TOLERANCE_100MM[sand['toleranceGrade']])
    assert investment['surfaceRoughness'] < sand['surfaceRoughness']

def testAluminiumShrinksMoreThanSteel():

    '''
    Validated against published solidification shrinkage. Aluminium at 6.5 percent needs roughly
    twice the riser volume of steel at 3.0, which is why aluminium castings have such poor yield.
    '''

    assert SOLIDIFICATION_SHRINKAGE['aluminium'] > 2.0 * SOLIDIFICATION_SHRINKAGE['steel']

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testRiserModulusExceedsCasting():

    '''
    A riser has to freeze AFTER the casting it feeds, or it stops feeding while the casting is still
    shrinking and the cavity forms in the part instead of the riser.
    '''

    casting = CastingProcess()
    casting.setInputs({'process': 'investment', 'alloyFamily': 'stainless'})
    casting.calculateSolidification()
    result = casting.sizeRiser()

    assert result['requiredRiserModulus'] == pytest.approx(
        RISER_MODULUS_RATIO * result['castingModulus'], rel = 1e-9)
    assert result['requiredRiserModulus'] > result['castingModulus']

def testRiserSatisfiesBothConditions():

    '''
    Timing and volume are independent conditions and the riser must satisfy both. The reported
    binding condition says which one to change: a timing-bound riser needs to be fatter, a
    volume-bound one taller.
    '''

    casting = CastingProcess()
    casting.setInputs({'process': 'sand', 'alloyFamily': 'aluminium',
                       'castingVolume': 5.0e-4, 'castingSurfaceArea': 0.10})
    casting.calculateSolidification()
    result = casting.sizeRiser()

    assert result['riserVolume'] >= result['timingVolume']
    assert result['riserVolume'] >= result['volumeRequired']
    assert result['bindingCondition'] in ('timing', 'volume')

def testSolidificationScalesWithModulusSquared():

    '''
    Chvorinov with n = 2, independent of the process constant.
    '''

    times = []
    for area in (0.10, 0.05):
        casting = CastingProcess()
        casting.setInputs({'process': 'investment', 'castingVolume': 1.0e-4,
                           'castingSurfaceArea': area})
        times.append(casting.calculateSolidification()['solidificationTime'])

    assert times[1] / times[0] == pytest.approx(4.0, rel = 1e-6), \
        'Halving the cooling area doubles the modulus and must quadruple the freezing time'

def testCastingYieldFallsWithShrinkage():

    '''
    A higher shrinkage alloy needs a larger riser for the same casting, so more of the poured metal
    ends up in the riser rather than the part.
    '''

    yields = {}
    for family in ('steel', 'aluminium'):
        casting = CastingProcess()
        casting.setInputs({'process': 'sand', 'alloyFamily': family,
                           'castingVolume': 1.0e-3, 'castingSurfaceArea': 0.15})
        casting.calculateSolidification()
        yields[family] = casting.sizeRiser()['castingYield']

    assert yields['aluminium'] < yields['steel']

def testReportRuns():

    '''
    Smoke test.
    '''

    casting = CastingProcess()
    casting.setInputs({'process': 'investment', 'alloyFamily': 'nickel',
                       'qualificationLevel': 1.33})
    assert 'CASTING PROCESS' in casting.generateReport()
