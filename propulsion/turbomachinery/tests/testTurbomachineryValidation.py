# -- Validation of the turbomachinery library against published turbopumps -- #

'''

The pump model checked against the RS-25 turbopumps, which are the best documented in the open
literature and unusually publish shaft speed and shaft power together. Those two between them close
the loop on a pump model in a way a geometry alone cannot.

The result is a validation with a sharp caveat attached. Given the published three stages the
library overpredicts HPFTP shaft power by nine per cent, which is good agreement for a first order
model. Given one stage it overpredicts by fifty per cent.

**The model is not wrong; it is sensitive to an input that is easy to omit.** Each stage of a
multi-stage pump runs at a much higher specific speed than the machine as a whole, and efficiency
follows the per-stage value. A pump model handed an overall specific speed and no stage count will
report a plausible and badly pessimistic efficiency, and nothing in the answer will look wrong.

The LPFTP is retained as the opposite case: one where the library's geometry classification
disagrees with the real machine, for a reason that is about rocket practice rather than about the
model being broken.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(os.path.dirname(DOMAIN))

sys.path.insert(0, os.path.join(DOMAIN, 'turbomachineryLibrary'))
sys.path.insert(0, ROOT)

from validation.referenceCases import TURBOPUMPS, VALIDATION_LEVELS, REFERENCE_KINDS

from Pump import Pump
from turbomachineryUtils import specificSpeed, geometryForSpecificSpeed

HPFTP = TURBOPUMPS['RS-25 HPFTP']
LPFTP = TURBOPUMPS['RS-25 LPFTP']

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def hydrogenFlow() -> float:

    '''
    LH2 mass flow for RS-25 at its published total flow and mixture ratio.
    '''

    return 514.0 / (1.0 + 6.03)

def buildHpftp(stages: int) -> Pump:

    pump = Pump()
    pump.setInputs({'propellant':   HPFTP['propellant'],
                    'density':      HPFTP['density'],
                    'massFlow':     hydrogenFlow(),
                    'pressureRise': HPFTP['dischargePressure'],
                    'shaftSpeed':   HPFTP['shaftSpeed'],
                    'stages':       stages})
    return pump

# ------------------------------------------------------------------------------------------------ #
# -- The reference data -- #
# ------------------------------------------------------------------------------------------------ #

def testEveryTurbopumpReferenceCarriesItsProvenance():

    for name, entry in TURBOPUMPS.items():
        assert entry.get('source'), name
        assert entry.get('kind') in REFERENCE_KINDS, name
        assert entry.get('level') in VALIDATION_LEVELS, name
        assert entry.get('note'), name

# ------------------------------------------------------------------------------------------------ #
# -- The validation -- #
# ------------------------------------------------------------------------------------------------ #

def testTheHydraulicPowerIsBelowThePublishedShaftPower():

    '''
    The sanity check that has to pass before any efficiency claim means anything. Hydraulic power
    is what the fluid receives and shaft power is what the turbine supplies, so the first must be
    smaller. If it were not, either the published data or the duty assumed here is wrong.
    '''

    volumetric = hydrogenFlow() / HPFTP['density']

    hydraulic = volumetric * HPFTP['dischargePressure']

    assert hydraulic < HPFTP['shaftPower']

    implied = hydraulic / HPFTP['shaftPower']

    assert 0.70 < implied < 0.90, (
        f'the implied real efficiency is {implied:.1%}, which is outside what a large '
        f'well developed pump achieves')

def testTheModelMatchesTheHpftpAtItsPublishedStageCount():

    '''
    The headline validation. Nine per cent high on shaft power for a first order model against a
    real machine is a good result, and the direction is right: the model is conservative.
    '''

    predicted = buildHpftp(HPFTP['stages']).calculatePower()['shaftPower']

    error = (predicted - HPFTP['shaftPower']) / HPFTP['shaftPower']

    assert 0.0 < error < 0.15, (
        f'predicted {predicted / 1.0e6:.1f} MW against a published '
        f'{HPFTP["shaftPower"] / 1.0e6:.1f} MW, {error:+.1%}')

def testOmittingTheStageCountIsTheErrorThatMatters():

    '''
    The caveat, and it is worth a test of its own because it is the failure mode a user will
    actually hit. Treating a three stage pump as one stage overpredicts the shaft power by half,
    and the answer looks entirely plausible.
    '''

    single = buildHpftp(1).calculatePower()['shaftPower']
    staged = buildHpftp(HPFTP['stages']).calculatePower()['shaftPower']

    singleError = (single - HPFTP['shaftPower']) / HPFTP['shaftPower']
    stagedError = (staged - HPFTP['shaftPower']) / HPFTP['shaftPower']

    assert singleError > 0.35, 'the single stage error should be large'
    assert stagedError < 0.15

    assert singleError > 3.0 * stagedError

def testEfficiencyRisesWithStageCountForTheSameDuty():

    '''
    The mechanism. Each stage does a fraction of the head at the same flow and speed, so its
    specific speed is higher and its efficiency is better.
    '''

    efficiencies = [buildHpftp(stages).calculatePower()['efficiency']
                    for stages in (1, 2, 3, 4)]

    assert efficiencies == sorted(efficiencies)

def testThePerStageSpecificSpeedScalesWithTheHeadSplit():

    '''
    Om_s goes as H^-0.75, so splitting the head across n stages multiplies the per-stage specific
    speed by n^0.75. That is the whole reason staging helps efficiency.
    '''

    single = buildHpftp(1).calculateSpecificSpeed()['specificSpeed']
    triple = buildHpftp(3).calculateSpecificSpeed()['specificSpeed']

    assert triple / single == pytest.approx(3.0 ** 0.75, rel = 1.0e-6)

# ------------------------------------------------------------------------------------------------ #
# -- Where the model does not apply -- #
# ------------------------------------------------------------------------------------------------ #

def testTheClassicalGeometryMappingDisagreesWithTheRealBoostPump():

    '''
    Retained as a boundary case rather than fixed. The LPFTP runs at a dimensionless specific speed
    of about 0.285, where the classical industrial chart says radial. The real machine is axial.

    A rocket boost pump is axial because it is chosen for cavitation performance, and an axial
    inducer stage tolerates far more vapour than a radial impeller. That is a rocket practice
    reason rather than a specific speed one, and reading the industrial chart across gets it wrong.

    The test asserts the disagreement so that nobody later "fixes" the geometry bands to match one
    machine they were never meant to describe.
    '''

    volumetric = hydrogenFlow() / 71.0

    head = ((LPFTP['dischargePressure'] - LPFTP['inletPressure'])
            / (71.0 * 9.80665))

    angular = LPFTP['shaftSpeed'] * 2.0 * np.pi / 60.0

    dimensionless = specificSpeed(angular, volumetric, head)

    classified = geometryForSpecificSpeed(dimensionless)

    assert 0.2 < dimensionless < 0.5
    assert 'radial' in classified['geometry']
    assert LPFTP['geometry'] == 'axial'

def testTheHighAndLowPressurePumpsRunAtVeryDifferentSpeeds():

    '''
    A boost pump exists to raise the inlet pressure of the main pump so the main pump can spin
    fast. The published speeds differ by a factor of seven, which is that relationship made
    visible.
    '''

    ratio = HPFTP['shaftSpeed'] / LPFTP['shaftSpeed']

    assert ratio > 5.0

def testTheOxidiserAndFuelPumpsRunAtSimilarSpeedsOnSeparateShafts():

    '''
    RS-25 puts the two high pressure pumps on separate shafts, and they still come out within two
    per cent of each other. That is worth knowing against the worked example, which puts them on a
    common shaft and finds their preferred speeds land close together anyway.
    '''

    oxidiser = TURBOPUMPS['RS-25 HPOTP']['shaftSpeed']
    fuel     = HPFTP['shaftSpeed']

    assert abs(oxidiser - fuel) / fuel < 0.05
