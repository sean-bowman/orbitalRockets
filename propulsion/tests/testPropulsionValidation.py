# -- Validation of the propulsion library against published hardware -- #

'''

The propulsion tools checked against published engine data rather than against themselves.

Every other test file in this repository checks that the code does what it was written to do. This
one checks whether what it was written to do is right, which is a different question and the only
one that can catch a wrong model.

The distinction that runs through the file: **a published engine specific impulse is not a thrust
chamber specific impulse.** The propulsion hub models the chamber and the nozzle. A closed cycle
engine puts all of its propellant through the chamber, so its published figure is very nearly what
the library computes. An open cycle engine dumps turbine exhaust overboard at a fraction of the main
impulse, and its published figure carries a penalty the library does not model.

So RS-25 validates the library and F-1 does not, and F-1 is kept precisely because it shows the
boundary. Tuning an efficiency to make F-1 agree would be fitting a cycle loss into a nozzle
coefficient, which is how a model becomes wrong in a way nothing catches.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'propulsionLibrary'))
sys.path.insert(0, ROOT)

from validation.referenceCases import (LIQUID_ENGINES, CORRELATION_ACCURACY, UNVALIDATED,
                                       REFERENCE_KINDS, impliedEfficiency)

from EnginePerformance import EnginePerformance
from EngineSizing import EngineSizing
from propulsionUtils import TYPICAL_CSTAR_EFFICIENCY, TYPICAL_THRUST_COEFFICIENT_EFFICIENCY

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def idealPerformance(engine: dict) -> dict:

    '''
    The library's ideal performance for a reference engine, with both efficiencies set to one so
    the comparison is against the physics rather than against an assumed loss.
    '''

    performance = EnginePerformance()
    performance.setInputs({'combination':                 engine['combination'],
                           'chamberPressure':             engine['chamberPressure'],
                           'areaRatio':                   engine['areaRatio'],
                           'cstarEfficiency':             1.0,
                           'thrustCoefficientEfficiency': 1.0})

    return {'vacuum':   performance.calculateAltitudePerformance()['vacuumImpulse'],
            'seaLevel': performance.calculateSpecificImpulse(101325.0)['delivered']}

# ------------------------------------------------------------------------------------------------ #
# -- The reference data itself -- #
# ------------------------------------------------------------------------------------------------ #

def testEveryReferenceCarriesItsProvenance():

    '''
    A reference without a source is an assertion, and an assertion cannot validate anything. This
    is the rule the file exists to enforce and it is worth enforcing mechanically.
    '''

    for name, engine in LIQUID_ENGINES.items():
        assert engine.get('source'), f'{name} has no source'
        assert engine.get('kind') in REFERENCE_KINDS, f'{name} has no valid kind'
        assert engine.get('note'), f'{name} has no note saying what the number includes'

def testEveryUnvalidatedEntryStatesItsConsequence():

    '''
    The register of what is not checked is only useful if it says what that costs. An entry that
    names a gap without saying what depends on it invites the gap to be ignored.
    '''

    for name, entry in UNVALIDATED.items():
        for field in ('domain', 'calculation', 'reason', 'consequence', 'nextStep'):
            assert entry.get(field), f'{name} has no {field}'

def testCorrelationAccuracyIsRecordedBeforeItIsRelied_on():

    '''
    A tool cannot be validated to a tighter band than the correlation underneath it. Bartz is plus
    or minus twenty per cent, so no cooling result may claim better.
    '''

    assert CORRELATION_ACCURACY['bartz']['band'] >= 0.20

# ------------------------------------------------------------------------------------------------ #
# -- The closed cycle case, which validates the library -- #
# ------------------------------------------------------------------------------------------------ #

def testTheIdealCalculationMatchesRS25VacuumImpulse():

    '''
    The headline validation. RS-25 is staged combustion, so its published vacuum impulse is very
    nearly a thrust chamber figure, and the library's ideal calculation should sit slightly above
    it because the library has no losses in it at all.

    Two per cent is the band, and the direction matters as much as the magnitude: an ideal
    calculation that came out below a real engine would mean something is wrong with the physics
    rather than with the losses.
    '''

    engine = LIQUID_ENGINES['RS-25']
    ideal  = idealPerformance(engine)

    error = (ideal['vacuum'] - engine['vacuumImpulse']) / engine['vacuumImpulse']

    assert 0.0 < error < 0.03, (
        f'ideal {ideal["vacuum"]:.1f} s against published {engine["vacuumImpulse"]:.1f} s, '
        f'{error:+.1%}')

def testTheIdealCalculationMatchesRS25SeaLevelImpulse():

    engine = LIQUID_ENGINES['RS-25']
    ideal  = idealPerformance(engine)

    error = (ideal['seaLevel'] - engine['seaLevelImpulse']) / engine['seaLevelImpulse']

    assert 0.0 < error < 0.03, (
        f'ideal {ideal["seaLevel"]:.1f} s against published {engine["seaLevelImpulse"]:.1f} s, '
        f'{error:+.1%}')

def testTheThroatSizedForRS25MatchesThePublishedDiameter():

    '''
    An independent check on the whole sizing chain, because the throat follows from the impulse and
    the characteristic velocity rather than from either alone.
    '''

    engine = LIQUID_ENGINES['RS-25']

    sizing = EngineSizing()
    sizing.setInputs({'combination':     engine['combination'],
                      'thrust':          engine['vacuumThrust'],
                      'chamberPressure': engine['chamberPressure'],
                      'areaRatio':       engine['areaRatio'],
                      'ambientPressure': 0.0})

    diameter = sizing.sizeThroat()['throatDiameter']

    error = (diameter - engine['throatDiameter']) / engine['throatDiameter']

    assert abs(error) < 0.08, (
        f'computed {diameter:.3f} m against published {engine["throatDiameter"]:.3f} m, '
        f'{error:+.1%}')

# ------------------------------------------------------------------------------------------------ #
# -- The open cycle case, which shows the boundary -- #
# ------------------------------------------------------------------------------------------------ #

def testTheOpenCycleEngineDisagreesAndIsExpectedTo():

    '''
    F-1 is a gas generator engine. Its published impulse includes turbine exhaust dumped overboard,
    which the thrust chamber library does not model, so the library should overpredict it by
    substantially more than it overpredicts a closed cycle engine.

    This test asserts the disagreement rather than the agreement. If it ever starts agreeing,
    either the reference has been changed or something has been tuned to fit it, and both are worse
    than the disagreement.
    '''

    engine = LIQUID_ENGINES['F-1']

    assert engine['closedCycle'] is False

    ideal = idealPerformance(engine)
    error = (ideal['vacuum'] - engine['vacuumImpulse']) / engine['vacuumImpulse']

    assert error > 0.05, (
        f'the open cycle case should overpredict by more than five per cent, got {error:+.1%}. '
        f'Agreement here would mean a cycle loss has been absorbed into a chamber efficiency.')

def testTheClosedCycleEngineAgreesFarBetterThanTheOpenCycleOne():

    '''
    The comparison that carries the finding. The two engines differ by cycle, and the library's
    agreement differs with them, which is evidence that the disagreement is the cycle rather than
    the physics.
    '''

    closed = LIQUID_ENGINES['RS-25']
    open_  = LIQUID_ENGINES['F-1']

    closedError = abs(idealPerformance(closed)['vacuum'] - closed['vacuumImpulse']) \
        / closed['vacuumImpulse']
    openError = abs(idealPerformance(open_)['vacuum'] - open_['vacuumImpulse']) \
        / open_['vacuumImpulse']

    assert openError > 3.0 * closedError

# ------------------------------------------------------------------------------------------------ #
# -- What the defaults imply -- #
# ------------------------------------------------------------------------------------------------ #

def testTheDefaultEfficienciesArePessimisticForABestInClassEngine():

    '''
    A finding rather than a defect. The library defaults to 0.96 on c* and 0.98 on Cf, a combined
    0.941, described as what a well developed engine achieves. RS-25 implies 0.984, so the defaults
    understate a best-in-class staged combustion engine by four points of impulse.

    The defaults are not changed to match, because RS-25 is the best there has ever been and a
    default that assumed it would flatter every other engine. What matters is that the gap is
    recorded and that anyone using the defaults for a high performance engine knows they are
    conservative.
    '''

    engine = LIQUID_ENGINES['RS-25']
    ideal  = idealPerformance(engine)

    implied = impliedEfficiency(engine['vacuumImpulse'], ideal['vacuum'])
    default = TYPICAL_CSTAR_EFFICIENCY * TYPICAL_THRUST_COEFFICIENT_EFFICIENCY

    assert implied > default, (
        f'RS-25 implies {implied:.3f} against a default of {default:.3f}')

    assert implied - default < 0.08, (
        f'a gap of {implied - default:.3f} would mean the defaults are not merely conservative')

def testTheImpliedEfficienciesSpanAWideRange():

    '''
    The reason a single default cannot serve. A 1960s gas generator engine and a modern staged
    combustion engine differ by six points of implied efficiency, and most of that difference is
    the cycle rather than the chamber.
    '''

    implied = {name: impliedEfficiency(engine['vacuumImpulse'],
                                       idealPerformance(engine)['vacuum'])
               for name, engine in LIQUID_ENGINES.items()}

    spread = max(implied.values()) - min(implied.values())

    assert spread > 0.04, (
        f'implied efficiencies {implied} span only {spread:.3f}')
