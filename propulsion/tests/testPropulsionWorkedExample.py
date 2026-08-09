# -- Tests for the propulsion worked example -- #

'''

The example makes one claim: three defensible questions about the area ratio give three different
answers, the intuitive one is the worst, and the constraint that rules out the best sits close
enough to it to be nearly free.

That claim is worth a test, because it is the kind of result that quietly stops being true when a
coefficient moves and nobody notices the example has stopped demonstrating anything. An example
that still runs and still prints while proving nothing is worse than one that fails.

These tests import the example rather than parsing its output, so they assert on the numbers. The
tolerances are loose enough to survive an honest change to the model and tight enough to catch the
example losing its point.

Author: Sean Bowman
Date:   08/08/2026

'''

import importlib.util
import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, DOMAIN)
sys.path.insert(0, os.path.join(DOMAIN, 'propulsionLibrary'))

# Every domain has a codeInterface.py at its root, and a flat sys.path resolves all of them to
# the same 'codeInterface' entry in sys.modules. The second domain to be imported in a single
# pytest process silently receives the first domain's example, and its tests then pass while
# testing the wrong file.
#
# Loading by explicit path under a domain-unique module name is the fix. It is the same problem the
# libraries solve by naming their helper module propulsionUtils rather than utils, and it has to be
# solved again here because the example modules cannot be renamed without breaking the documented
# 'python propulsion/codeInterface.py' entry point.

def _loadExample():

    specification = importlib.util.spec_from_file_location(
        'propulsionCodeInterface', os.path.join(DOMAIN, 'codeInterface.py'))

    module = importlib.util.module_from_spec(specification)
    sys.modules['propulsionCodeInterface'] = module
    specification.loader.exec_module(module)

    return module

codeInterface = _loadExample()

@pytest.fixture(scope = 'module')
def case():

    return codeInterface.loadCase()

@pytest.fixture(scope = 'module')
def propellant(case):

    return codeInterface.selectPropellant(case)

@pytest.fixture(scope = 'module')
def expansion(case, propellant):

    return codeInterface.selectExpansion(case, propellant)

@pytest.fixture(scope = 'module')
def engine(case, expansion):

    return codeInterface.sizeEngine(case, expansion)

# ------------------------------------------------------------------------------------------------ #
# -- The propellant choice -- #
# ------------------------------------------------------------------------------------------------ #

def testTheChosenPropellantLosesOnImpulseAndWinsOnDensity(propellant, case):

    '''
    The whole reason the example opens with a propellant trade. If LOX/RP-1 ever stops being beaten
    on specific impulse by LOX/LH2, the trade has become uninteresting and the narrative is wrong.
    '''

    combinations = propellant['comparison']['combinations']

    chosen   = combinations[case['selection']['chosen']]
    hydrogen = combinations['LOX/LH2']

    assert hydrogen['specificImpulse'] > chosen['specificImpulse']
    assert chosen['densityImpulse']    > hydrogen['densityImpulse']

def testTheDensityAdvantageIsLarge(propellant, case):

    combinations = propellant['comparison']['combinations']

    ratio = (combinations[case['selection']['chosen']]['densityImpulse']
             / combinations['LOX/LH2']['densityImpulse'])

    assert ratio > 2.0

# ------------------------------------------------------------------------------------------------ #
# -- The claim the example exists to make -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSweepPeakAgreesWithThePressureMatchedExpansion(expansion):

    '''
    Two independent routes to the same answer: the analytic area ratio whose exit pressure equals
    ambient, and the numerical peak of the sea level impulse sweep. If they disagree, one of the
    two is wrong and there is no way to tell which from the example alone.
    '''

    analytic = expansion['pressureMatched']
    numeric  = expansion['answers']['sea level optimum']['areaRatio']

    assert numeric == pytest.approx(analytic, abs = 0.5)

def testTheThreeAnswersAreOrderedAndDistinct(expansion):

    answers = expansion['answers']

    seaLevel   = answers['sea level optimum']['areaRatio']
    separation = answers['separation limit']['areaRatio']
    average    = answers['burn-average optimum']['areaRatio']

    assert seaLevel < separation < average
    assert average / seaLevel > 2.0, 'the answers must be far enough apart to matter'

def testTheIntuitiveAnswerIsTheWorstOnBurnAverage(expansion):

    '''
    The point. Maximising thrust at liftoff is a defensible question with a defensible answer, and
    it produces the lowest burn-averaged impulse of the three.
    '''

    answers = expansion['answers']

    assert (answers['sea level optimum']['averageImpulse']
            < answers['design point']['averageImpulse'])
    assert (answers['sea level optimum']['averageImpulse']
            < answers['burn-average optimum']['averageImpulse'])

def testTheIntuitiveAnswerIsTheBestAtSeaLevel(expansion):

    '''
    The other half of the point: it is not a bad answer, it is the right answer to the wrong
    question. It genuinely does maximise sea level impulse.
    '''

    answers = expansion['answers']

    for label in ('design point', 'separation limit', 'burn-average optimum'):
        assert (answers['sea level optimum']['seaLevelImpulse']
                >= answers[label]['seaLevelImpulse'])

def testTheTrueOptimumSeparatesAndCannotBeFlown(expansion):

    assert expansion['answers']['burn-average optimum']['separated'] is True

def testTheDesignPointDoesNotSeparate(expansion):

    '''
    A design point that separates is not a design point. This is why the example holds margin off
    the limit rather than sitting on it.
    '''

    assert expansion['answers']['design point']['separated'] is False

def testTheDesignPointIsCloseToTheUnreachableOptimum(expansion):

    '''
    What makes the case pleasant rather than painful. If the gap ever grows past a second or so,
    the conclusion changes: the constraint would then be expensive and worth engineering around
    with an altitude-compensating nozzle.
    '''

    answers = expansion['answers']

    gap = (answers['burn-average optimum']['averageImpulse']
           - answers['design point']['averageImpulse'])

    assert 0.0 < gap < 1.0

def testTheDeltaVPenaltyIsRealButNotHuge(expansion):

    '''
    Sixty odd metres per second is worth having and is not worth redesigning the vehicle for. Both
    halves of that matter, so the test brackets it rather than asserting a floor.
    '''

    assert 30.0 < expansion['deltaVPenalty'] < 150.0

def testTheDesignPointRespectsTheStatedMargin(expansion, case):

    answers = expansion['answers']

    expected = (answers['separation limit']['areaRatio']
                * case['expansion']['separationMargin'])

    assert answers['design point']['areaRatio'] == pytest.approx(expected)

# ------------------------------------------------------------------------------------------------ #
# -- The engine that results -- #
# ------------------------------------------------------------------------------------------------ #

def testTheEngineIsSizedAtTheDesignPoint(engine, expansion):

    assert engine['sizing'].areaRatio == pytest.approx(
        expansion['answers']['design point']['areaRatio'])

def testTheSizingReproducesTheRequiredThrust(engine, case):

    sizing = engine['sizing']

    thrust = (sizing.performance.calculateThrustCoefficient()['delivered']
              * sizing.chamberPressure * engine['throat']['throatArea'])

    assert thrust == pytest.approx(case['requirement']['thrust'], rel = 1.0e-9)

def testResidenceTimeIsPhysical(engine):

    assert 0.5e-3 < engine['chamber']['residenceTime'] < 10.0e-3

def testTheNozzleCarriesMostOfTheWallArea(engine):

    '''
    The reason the cooling cross-check has to include it. If this ever inverts, the geometry has
    changed enough that the chamber sizing argument needs revisiting.
    '''

    chamber = engine['chamber']

    assert chamber['nozzleWallArea'] / chamber['availableWallArea'] > 0.5

def testPropellantMassFollowsFlowAndBurnTime(engine, case):

    expected = engine['throat']['massFlow'] * case['requirement']['burnTime']

    assert engine['propellantMass'] == pytest.approx(expected)

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

    codeInterface.main()

    printed = capsys.readouterr().out

    assert 'SUMMARY' in printed
    assert 'design point' in printed
    assert 'fluidSystems' in printed, 'the interface handoffs must be reported'
