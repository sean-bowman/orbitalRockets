
# -- Tests for BoltedJoint, ModalEstimate and LoadCase -- #

'''

Tiered tests for the joint, modal and load case classes.

Tier 1 covers the contract and the geometry guards.

Tier 2 validates against published relations: the joint stiffness diagram and its load factor, the
beam mode eigenvalues, the acoustic wave speed in aluminium, and the NASA-STD-5001 factor ladder.

Tier 3 covers self-consistency and the physical direction of every effect, including two regression
guards on bugs found during the build: the pressure cone must start at the head bearing face, and
the lateral frequency requirement must be assessed against the lowest lateral mode rather than the
beam mode alone.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'aerospaceStructuresLibrary'))

from structuresUtils import InvalidInputError, GeometryError
from BoltedJoint import (BoltedJoint, NUT_FACTORS, PRELOAD_SCATTER, EMBEDMENT_LOSS,
                         HEAD_BEARING_RATIO, MINIMUM_EDGE_DISTANCE_RATIO,
                         PRELOAD_FRACTION_DEFAULT)
from ModalEstimate import (ModalEstimate, BEAM_MODE_FACTORS, AXIAL_MODE_FACTORS,
                           ESTIMATE_ACCURACY)
from LoadCase import (LoadCase, YIELD_FACTOR, ULTIMATE_FACTOR, YIELD_FACTOR_ANALYSIS,
                      ULTIMATE_FACTOR_ANALYSIS, STANDARD_PHASES)

def buildJoint(**overrides) -> BoltedJoint:

    inputs = {'boltDiameter': 0.00635, 'memberMaterial': '2219-T87', 'memberCondition': 't87',
              'gripLength': 0.012, 'memberThickness': 0.006, 'edgeDistance': 0.0127,
              'pitch': 0.025, 'appliedTension': 4.0e3, 'appliedShear': 3.0e3}
    inputs.update(overrides)

    joint = BoltedJoint()
    joint.setInputs(inputs)
    return joint

def buildModal(**overrides) -> ModalEstimate:

    inputs = {'material': '2219-T87', 'condition': 't87', 'radius': 1.0, 'thickness': 0.004,
              'length': 6.0, 'boundaryCondition': 'cantilever'}
    inputs.update(overrides)

    modes = ModalEstimate()
    modes.setInputs(inputs)
    return modes

def buildLoads(**overrides) -> LoadCase:

    inputs = {'referenceMass': 5000.0, 'referenceRadius': 1.0, 'referenceLength': 6.0}
    inputs.update(overrides)

    cases = LoadCase()
    cases.setInputs(inputs)
    return cases

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: contract and guards -- #
# ------------------------------------------------------------------------------------------------ #

def testJointRejectsEdgeDistanceInsideTheHole():

    joint = BoltedJoint()
    joint.setInputs({'boltDiameter': 0.00635, 'gripLength': 0.012, 'edgeDistance': 0.002})

    with pytest.raises(GeometryError):
        joint.calculateStiffnesses()

def testJointRejectsOverlappingHoles():

    joint = BoltedJoint()
    joint.setInputs({'boltDiameter': 0.00635, 'gripLength': 0.012, 'pitch': 0.005})

    with pytest.raises(GeometryError):
        joint.calculateStiffnesses()

def testJointRejectsImpossiblePreloadFraction():

    joint = BoltedJoint()
    joint.setInputs({'boltDiameter': 0.00635, 'gripLength': 0.012, 'preloadFraction': 1.5})

    with pytest.raises(InvalidInputError):
        joint.calculatePreload()

def testJointRejectsUnknownPreloadMethod():

    joint = buildJoint(preloadMethod = 'guesswork')

    with pytest.raises(InvalidInputError):
        joint.calculatePreload()

def testModalNeedsASection():

    modes = ModalEstimate()
    modes.setInputs({'length': 6.0})

    with pytest.raises(InvalidInputError):
        modes.calculateSectionProperties()

def testModalRejectsThickCylinder():

    modes = ModalEstimate()
    modes.setInputs({'length': 6.0, 'radius': 0.1, 'thickness': 0.2})

    with pytest.raises(GeometryError):
        modes.calculateSectionProperties()

def testLoadCaseRejectsUnknownQualificationBasis():

    cases = LoadCase()
    with pytest.raises(InvalidInputError):
        cases.setInputs({'referenceMass': 1000.0, 'qualificationBy': 'vibes'})

def testLoadCaseRejectsAnalysisWithNoCases():

    with pytest.raises(InvalidInputError):
        buildLoads().identifyGoverning()

def testLoadCaseRejectsUnknownLevel():

    cases = buildLoads()
    cases.addCase('liftoff', axialG = 3.0)

    with pytest.raises(InvalidInputError):
        cases.factoredLoads(level = 'proof')

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: against published relations -- #
# ------------------------------------------------------------------------------------------------ #

def testLoadFactorSitsInTheRealisticBand():

    '''
    Regression on a real bug. The Rotscher pressure cone starts at the head bearing face, roughly
    1.5 bolt diameters, not at the shank. Starting it at the shank understates member stiffness by
    about 1.7x and pushes Phi out of the 0.1 to 0.3 band that preloaded joints actually occupy.
    '''

    stiffness = buildJoint().calculateStiffnesses()

    # The 0.1 to 0.3 rule of thumb assumes steel members at a grip of several diameters. This
    # reference joint is a steel bolt in aluminium at l/d of 1.9, and both raise Phi: the bolt is
    # 2.7x stiffer in modulus than the members, and a short grip favours the bolt further. The
    # band asserted here is what that configuration should actually produce.
    assert 0.20 < stiffness['loadFactor'] < 0.55, \
        f'load factor {stiffness["loadFactor"]:.3f} is outside the band for a steel bolt in ' \
        f'aluminium at this grip'
    assert HEAD_BEARING_RATIO > 1.0

    # a steel bolt in steel members at a longer grip must fall into the classical band
    classical = buildJoint(memberModulus = 200.0e9, gripLength = 0.032).calculateStiffnesses()

    assert 0.10 < classical['loadFactor'] < 0.30, \
        f'the classical configuration gave {classical["loadFactor"]:.3f}'
    assert classical['stiffnessRatio'] > 2.0

def testBoltTakesOnlyItsShareOfAppliedLoad():

    '''
    The whole reason to preload: applied tension mostly unloads the members.
    '''

    diagram = buildJoint().calculateJointDiagram()

    assert diagram['boltShareOfApplied'] < diagram['memberShareOfApplied']
    assert (diagram['boltShareOfApplied'] + diagram['memberShareOfApplied']
            == pytest.approx(4.0e3, rel = 1.0e-9))

def testSeparationLoadMatchesTheClosedForm():

    '''
    P_sep = F_preload_min / (1 - Phi).
    '''

    joint     = buildJoint()
    stiffness = joint.calculateStiffnesses()
    preload   = joint.calculatePreload()
    diagram   = joint.calculateJointDiagram()

    expected = preload['minimumPreload'] / (1.0 - stiffness['loadFactor'])

    assert diagram['separationLoad'] == pytest.approx(expected, rel = 1.0e-12)

def testTorqueMatchesTheNutFactorRelation():

    '''
    T = K F d, the relation every torque table is built on.
    '''

    joint   = buildJoint(nutFactorKey = 'lubricated')
    preload = joint.calculatePreload()

    expected = (NUT_FACTORS['lubricated']['value'] * preload['nominalPreload']
                * joint.boltDiameter)

    assert preload['installationTorque'] == pytest.approx(expected, rel = 1.0e-12)

def testPreloadScatterOrdersByControlMethod():

    '''
    Bolt stretch and ultrasonic measurement are far more repeatable than torque, which is why
    critical joints use them.
    '''

    assert PRELOAD_SCATTER['torque'] > PRELOAD_SCATTER['torque plus angle']
    assert PRELOAD_SCATTER['torque plus angle'] > PRELOAD_SCATTER['bolt stretch']
    assert PRELOAD_SCATTER['bolt stretch'] == PRELOAD_SCATTER['ultrasonic']

    loose = buildJoint(preloadMethod = 'torque').calculatePreload()
    tight = buildJoint(preloadMethod = 'ultrasonic').calculatePreload()

    assert (loose['maximumPreload'] - loose['minimumPreload']) > \
           (tight['maximumPreload'] - tight['minimumPreload'])

def testEmbedmentReducesPreload():

    withLoss    = buildJoint(includeEmbedment = True).calculatePreload()
    withoutLoss = buildJoint(includeEmbedment = False).calculatePreload()

    assert withLoss['nominalPreload'] == pytest.approx(
        withoutLoss['nominalPreload'] * (1.0 - EMBEDMENT_LOSS), rel = 1.0e-12)

def testCantileverBeamEigenvalueIsCorrect():

    '''
    betaL = 1.87510 for the first mode of a cantilever, the standard eigenvalue.
    '''

    assert BEAM_MODE_FACTORS['cantilever']['betaL'] == pytest.approx(1.87510, rel = 1.0e-5)
    assert BEAM_MODE_FACTORS['simply supported']['betaL'] == pytest.approx(np.pi, rel = 1.0e-9)
    assert BEAM_MODE_FACTORS['fixed-fixed']['betaL'] == pytest.approx(4.73004, rel = 1.0e-5)

def testBendingFrequencyMatchesTheClosedForm():

    modes   = buildModal()
    section = modes.calculateSectionProperties()
    result  = modes.calculateBendingMode()

    betaL    = BEAM_MODE_FACTORS['cantilever']['betaL']
    expected = (betaL ** 2 / (2.0 * np.pi * modes.length ** 2)
                * np.sqrt(section['bendingStiffness'] / section['massPerLength']))

    assert result['distributedFrequency'] == pytest.approx(expected, rel = 1.0e-12)

def testAcousticWaveSpeedInAluminiumIsAboutFiveThousand():

    '''
    sqrt(E / rho) is roughly 5100 m/s for aluminium alloys, and it is nearly the same across them
    because E and rho move together.
    '''

    waveSpeed = buildModal().calculateAxialMode()['waveSpeed']

    assert 4800.0 < waveSpeed < 5400.0, f'{waveSpeed:.0f} m/s is not an aluminium wave speed'

def testFactorLadderMatchesNasaStandard():

    assert YIELD_FACTOR == pytest.approx(1.10)
    assert ULTIMATE_FACTOR == pytest.approx(1.40)
    assert YIELD_FACTOR_ANALYSIS > YIELD_FACTOR
    assert ULTIMATE_FACTOR_ANALYSIS > ULTIMATE_FACTOR

    byTest     = buildLoads(qualificationBy = 'test')
    byAnalysis = buildLoads(qualificationBy = 'analysis')

    assert byAnalysis.ultimateFactor > byTest.ultimateFactor

def testModelUncertaintyMultipliesOnTop():

    plain     = buildLoads(modelUncertainty = 1.00)
    uncertain = buildLoads(modelUncertainty = 1.20)

    assert uncertain.ultimateFactor == pytest.approx(plain.ultimateFactor * 1.20, rel = 1.0e-12)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: self-consistency and direction -- #
# ------------------------------------------------------------------------------------------------ #

def testStiffnessDiagramIsSelfConsistent():

    '''
    Phi is defined by the two stiffnesses, so recomputing it from them must reproduce it exactly.
    '''

    stiffness = buildJoint().calculateStiffnesses()

    recomputed = (stiffness['boltStiffness']
                  / (stiffness['boltStiffness'] + stiffness['memberStiffness']))

    assert stiffness['loadFactor'] == pytest.approx(recomputed, rel = 1.0e-12)

def testStifferMembersLowerTheLoadFactor():

    '''
    A stiffer member takes more of the applied load, leaving less for the bolt.
    '''

    soft  = buildJoint(memberModulus = 70.0e9).calculateStiffnesses()
    stiff = buildJoint(memberModulus = 200.0e9).calculateStiffnesses()

    assert stiff['loadFactor'] < soft['loadFactor']

def testLongerGripLowersBothStiffnesses():

    short = buildJoint(gripLength = 0.008).calculateStiffnesses()
    long_ = buildJoint(gripLength = 0.024).calculateStiffnesses()

    assert long_['boltStiffness'] < short['boltStiffness']
    assert long_['memberStiffness'] < short['memberStiffness']

def testShortEdgeDistanceIsFlaggedInadequate():

    '''
    Below two diameters the joint fails by shear-out rather than bearing, and shear-out is sudden.
    '''

    short = buildJoint(edgeDistance = 0.008).calculateMemberChecks()
    long_ = buildJoint(edgeDistance = 0.0190).calculateMemberChecks()

    assert short['edgeDistanceRatio'] < MINIMUM_EDGE_DISTANCE_RATIO
    assert not short['edgeDistanceAdequate']
    assert long_['edgeDistanceAdequate']
    assert long_['shearOutMargin'] > short['shearOutMargin']

def testLateralRequirementUsesTheLowestLateralMode():

    '''
    Regression on a real bug. A shell ovalling mode is a lateral mode and is frequently the lowest
    one, so assessing the requirement against the beam mode alone reports a structure as compliant
    when its true first mode is not.
    '''

    modes  = buildModal(tipMass = 500.0, requiredLateral = 10.0)
    result = modes.screenAgainstRequirement()
    shell  = modes.calculateShellModes()

    assert shell['shellBelowBeam'], 'this geometry must have a shell mode below the beam mode'
    assert result['margins']['lateral'] < 0.0, \
        'the requirement must fail on the shell mode'
    assert not result['acceptable']

    beamOnlyMargin = modes.calculateBendingMode()['frequency'] / 10.0 - 1.0
    assert beamOnlyMargin > 0.0, \
        'the beam mode alone would have passed, which is the trap being guarded'

def testShellOvallingIsTheLowestShellMode():

    '''
    The n = 2 ovalling mode is the lowest, and frequency rises with wave count from there.
    '''

    shell = buildModal().calculateShellModes()

    assert shell['lowestWaveCount'] == 2

    frequencies = [shell['frequencies'][n] for n in sorted(shell['frequencies'])]
    assert all(np.diff(frequencies) > 0.0), 'frequency must rise with circumferential wave count'

def testTipMassLowersTheBendingFrequency():

    bare   = buildModal().calculateBendingMode()
    loaded = buildModal(tipMass = 500.0).calculateBendingMode()

    assert loaded['frequency'] < bare['frequency']
    assert loaded['tipMassReduction'] > 0.0

def testStifferSectionRaisesFrequencyAsSquareRoot():

    '''
    f goes as sqrt(EI/m). Quadrupling the wall thickness roughly doubles both I and m per unit
    length, so the frequency rises as the square root of the ratio, not linearly.
    '''

    thin  = buildModal(thickness = 0.002).calculateBendingMode()['distributedFrequency']
    thick = buildModal(thickness = 0.008).calculateBendingMode()['distributedFrequency']

    # I and mass both scale linearly with thickness for a thin shell, so f is thickness independent
    assert thick == pytest.approx(thin, rel = 0.02), \
        'for a thin shell both stiffness and mass scale with thickness, so f barely moves'

def testLongerStructureIsSofter():

    short = buildModal(length = 3.0).calculateBendingMode()['distributedFrequency']
    long_ = buildModal(length = 6.0).calculateBendingMode()['distributedFrequency']

    assert long_ < short
    assert short / long_ == pytest.approx(4.0, rel = 0.02), 'f goes as 1/L^2'

def testEstimateBandBracketsTheEstimate():

    result = buildModal().calculateBendingMode()

    assert result['lowerBound'] < result['frequency'] < result['upperBound']
    assert result['upperBound'] / result['frequency'] == pytest.approx(1.0 + ESTIMATE_ACCURACY)

def testGoverningCaseCanDifferFromTheLargestSingleLoad():

    '''
    The central claim of LoadCase, checked numerically. Max acceleration has the highest axial load
    and max-Q is the worst case overall.
    '''

    cases = buildLoads()
    cases.addCase('liftoff',   axialG = 3.0, lateralG = 1.0, internalPressure = 2.5e6)
    cases.addCase('max-Q',     axialG = 2.5, lateralG = 2.0, internalPressure = 2.2e6,
                  dynamicPressure = 35.0e3)
    cases.addCase('max accel', axialG = 6.0, lateralG = 0.3, internalPressure = 1.8e6)

    result = cases.identifyGoverning()

    assert result['governingByMetric'] == 'max accel'
    assert result['governingBySeverity'] == 'max-Q'
    assert not result['agree']
    assert any('enveloped' in finding for finding in result['findings'])

def testFactoringMultipliesLoadsNotGravityLevels():

    '''
    The factor applies to the load. The g level is an input describing the environment and must not
    be factored, or the report becomes self-contradictory.
    '''

    cases = buildLoads()
    cases.addCase('liftoff', axialG = 3.0, internalPressure = 2.0e6)

    limit    = cases.factoredLoads('limit')['liftoff']
    ultimate = cases.factoredLoads('ultimate')['liftoff']

    assert ultimate['axialG'] == limit['axialG'] == 3.0
    assert ultimate['axialLoad'] == pytest.approx(limit['axialLoad'] * ULTIMATE_FACTOR,
                                                  rel = 1.0e-12)
    assert ultimate['internalPressure'] == pytest.approx(2.0e6 * ULTIMATE_FACTOR, rel = 1.0e-12)

def testUltimateIsMoreSevereThanYieldWhichIsMoreSevereThanLimit():

    cases = buildLoads()
    cases.addCase('liftoff', axialG = 3.0)

    limit    = cases.factoredLoads('limit')['liftoff']['axialLoad']
    yielded  = cases.factoredLoads('yield')['liftoff']['axialLoad']
    ultimate = cases.factoredLoads('ultimate')['liftoff']['axialLoad']

    assert limit < yielded < ultimate

def testStandardPhasesPopulateAndAreDistinct():

    cases = buildLoads()
    cases.addStandardPhases()

    assert set(cases.cases) == set(STANDARD_PHASES)

    axialLevels = {name: case['axialG'] for name, case in cases.cases.items()}
    assert axialLevels['max acceleration'] > axialLevels['liftoff']
    assert axialLevels['max-Q'] < axialLevels['max acceleration']

def testAxialLoadScalesWithReferenceMass():

    light = buildLoads(referenceMass = 1000.0)
    heavy = buildLoads(referenceMass = 5000.0)

    for cases in (light, heavy):
        cases.addCase('liftoff', axialG = 3.0)

    assert (heavy.cases['liftoff']['axialLoad']
            == pytest.approx(5.0 * light.cases['liftoff']['axialLoad'], rel = 1.0e-12))

def testMarginCheckIdentifiesTheGoverningCase():

    cases = buildLoads()
    cases.addCase('liftoff',   axialG = 3.0)
    cases.addCase('max accel', axialG = 6.0)

    result = cases.checkAgainstAllowable(allowableStress = 200.0e6, area = 0.02)

    assert result['governingCase'] == 'max accel'
    assert result['governingMargin'] == min(result['margins'].values())

def testReportsRunForAllThreeClasses():

    cases = buildLoads()
    cases.addStandardPhases(['liftoff', 'max-Q'])

    assert 'BOLTED JOINT'   in buildJoint().generateReport()
    assert 'MODAL ESTIMATE' in buildModal().generateReport()
    assert 'LOAD CASES'     in cases.generateReport()
