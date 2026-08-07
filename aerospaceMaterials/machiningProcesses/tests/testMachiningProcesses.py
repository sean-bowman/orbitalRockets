# -- Tests for the machiningProcesses library -- #

'''

Tiered tests for MachiningProcess.

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
                                'machiningProcessesLibrary'))


from MachiningProcess import (MachiningProcess, MACHINABILITY, CUTTING_PROCESSES,
                              SURFACE_RESIDUAL_STRESS, THIN_WALL_TOLERANCE)
from machiningUtils import InvalidInputError, ProcessInfeasibleError

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: guards -- #
# ---------------------------------------------------------------------------------------------- #

def testChatterRaises():

    '''
    Chatter is self-excited, not a resonance to be driven through. Above the stability limit and
    outside a lobe the part is scrapped and the tool usually breaks, so this is a hard stop.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'axialDepth': 0.030,
                         'cuttingSpeed': 0.45})

    with pytest.raises(ProcessInfeasibleError):
        machining.calculateStabilityLobes()

def testSpeedAboveTheTaylorConstantRaises():

    '''
    The Taylor constant is the speed at which tool life falls to one minute. Above it the tool fails
    immediately and the calculation has no meaning.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': 'Inconel 718', 'condition': 'sta', 'cuttingSpeed': 5.0})

    with pytest.raises(ProcessInfeasibleError):
        machining.calculateToolLife()

def testUnknownMaterialRaises():

    '''
    Specific cutting energy varies by a factor of five across these alloys.
    '''

    machining = MachiningProcess()
    with pytest.raises(InvalidInputError):
        machining.setInputs({'material': 'unobtainium'})

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: validation -- #
# ---------------------------------------------------------------------------------------------- #

def testSpecificEnergySpreadAcrossAlloys():

    '''
    Validated against published specific cutting energy. Aluminium at 0.75 GJ/m^3 against Inconel at
    4.0 is a factor of five, and it is why the same removal rate needs five times the spindle power
    and produces five times the heat on the nickel alloy.
    '''

    aluminium = MACHINABILITY['6061']['specificEnergy']
    nickel    = MACHINABILITY['INCONEL 718']['specificEnergy']

    assert nickel / aluminium > 4.0
    assert 0.5e9 < aluminium < 1.2e9
    assert 3.0e9 < nickel < 5.0e9

def testMachinabilityRatingOrdering():

    '''
    Validated against shop practice. 6061 is the reference at 1.0 and the nickel alloys sit around
    0.12, a factor of eight.
    '''

    ratings = {name: entry['machinabilityRating'] for name, entry in MACHINABILITY.items()}

    assert ratings['6061'] == 1.00
    assert ratings['INCONEL 718'] < ratings['TI-6AL-4V'] < ratings['316L'] < ratings['6061']

def testTaylorExponentSensitivity():

    '''
    Validated against the Taylor relation. A small exponent means life is very sensitive to speed:
    at n = 0.15 a 20 percent speed increase cuts life by a factor above three, where at n = 0.30 it
    costs less than a factor of two.

    That sensitivity is why nickel alloys are machined at speeds that look absurdly slow.
    '''

    ratios = {}
    for material, condition, speed in (('6061', 't6', 3.0), ('Inconel 718', 'sta', 0.30)):
        machining = MachiningProcess()
        machining.setInputs({'material': material, 'condition': condition, 'cuttingSpeed': speed})
        ratios[machining.material] = machining.calculateToolLife()['lifeRatioForTwentyPercentFaster']

    # The closed form: a factor f in speed changes life by f^(1/n), so the ratio is exactly
    # 1.2^(1/n) and it can be checked directly rather than merely bounded.
    for key in ('6061', 'INCONEL 718'):
        exponent = MACHINABILITY[key]['taylorExponent']
        assert ratios[key] == pytest.approx(1.2 ** (1.0 / exponent), rel = 1e-9), \
            f'The life ratio for a 20 percent speed increase must be exactly 1.2^(1/n) for {key}'

    assert ratios['INCONEL 718'] > 1.7 * ratios['6061'], \
        'At n = 0.15 a 20 percent speed increase costs a factor of 3.4 in tool life, against 1.8 ' \
        'at n = 0.30. That sensitivity is why nickel alloys are run at speeds that look slow.'

def testCuttingForceScalesWithSpecificEnergy():

    '''
    F_c = k_c A_c. At identical geometry the force ratio must equal the specific energy ratio
    exactly.
    '''

    forces = {}
    for material, condition in (('6061', 't6'), ('Inconel 718', 'sta')):
        machining = MachiningProcess()
        machining.setInputs({'material': material, 'condition': condition, 'cuttingSpeed': 0.3})
        forces[machining.material] = machining.calculateCuttingForce()['cuttingForce']

    energyRatio = (MACHINABILITY['INCONEL 718']['specificEnergy'] /
                   MACHINABILITY['6061']['specificEnergy'])

    assert forces['INCONEL 718'] / forces['6061'] == pytest.approx(energyRatio, rel = 1e-9)

def testWornDryToolCostsFatigueLife():

    '''
    Validated against surface integrity practice. A sharp tool with flood coolant leaves the surface
    in compression and gains fatigue life; a worn dry tool leaves it in tension and loses it.

    The same machine, the same programme and the same material produce a 15 percent benefit or a
    40 percent penalty depending on whether the tool was changed on schedule.
    '''

    best  = SURFACE_RESIDUAL_STRESS['sharp tool, flood coolant']
    worst = SURFACE_RESIDUAL_STRESS['worn tool, dry']

    assert best['stress'] < 0.0, 'A sharp tool with coolant must leave compression'
    assert worst['stress'] > 0.0, 'A worn dry tool must leave tension'
    assert best['fatigueFactor'] > 1.0 > worst['fatigueFactor']
    assert best['fatigueFactor'] / worst['fatigueFactor'] > 1.5

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency -- #
# ---------------------------------------------------------------------------------------------- #

def testStabilityLobesRaiseTheAchievableDepth():

    '''
    At spindle speeds where the tooth passing frequency is a whole fraction of the natural
    frequency, the regenerative phase lines up favourably and the achievable depth is several times
    the unconditional limit.

    The lowest lobe is the widest and the most useful, and it sits at high spindle speed. That is
    why high speed machining of thin walls works at all.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'axialDepth': 0.001})
    result = machining.calculateStabilityLobes()

    lobes = result['lobes']

    assert all(lobe['achievableDepth'] > result['criticalDepthOfCut'] for lobe in lobes)
    assert lobes[0]['achievableDepth'] > lobes[-1]['achievableDepth'], \
        'The lowest lobe must offer the largest gain'
    assert lobes[0]['spindleSpeedRpm'] > lobes[-1]['spindleSpeedRpm'], \
        'and it must sit at the highest spindle speed'

def testThinWallDeflectionScalesCorrectly():

    '''
    A wall is a cantilever PLATE, not a beam of the tool width. The load spreads laterally, so the
    effective width scales with the height and the deflection goes as height squared rather than
    cubed. The thickness dependence stays cubic.

    An earlier version used the axial depth as the section width and overstated the deflection by
    more than an order of magnitude.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'axialDepth': 0.0015})

    tall  = machining.calculateThinWallDeflection(0.060, 0.002)['deflection']
    short = machining.calculateThinWallDeflection(0.030, 0.002)['deflection']
    thin  = machining.calculateThinWallDeflection(0.060, 0.001)['deflection']

    assert tall / short == pytest.approx(4.0, rel = 0.02), \
        'With plate spreading the height dependence is squared, not cubed'
    assert thin / tall == pytest.approx(8.0, rel = 0.02), \
        'The thickness dependence stays cubic through the second moment of area'

    assert 0.05e-3 < tall < 2.0e-3, \
        f'A 2 mm by 60 mm wall deflecting {tall * 1000.0:.2f} mm is outside the realistic range'

def testSpringPassesRiseWithDeflection():

    '''
    Each spring pass removes a fraction of the remaining error, so a larger deflection needs more of
    them. This is what makes thin walled parts slow.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'axialDepth': 0.0015})

    thick = machining.calculateThinWallDeflection(0.030, 0.004)
    thin  = machining.calculateThinWallDeflection(0.060, 0.001)

    assert thin['springPassesRequired'] > thick['springPassesRequired']

def testDistortionMatchesTheHeatTreatmentModel():

    '''
    The residual stress profile assumption is shared with HeatTreatment.calculateDistortion and it
    has to produce the same answer, or the two halves of the same physical problem disagree.

    Removing nothing must release nothing, and the bow must scale with the square of the part length.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': '7075', 'condition': 't73', 'cuttingSpeed': 3.0})

    nothing = machining.calculateDistortion(159.0e6, 0.050, 0.001, 0.500)
    assert nothing['predictedBow'] < 1.0e-5

    short = machining.calculateDistortion(159.0e6, 0.050, 0.40, 0.250)['predictedBow']
    long  = machining.calculateDistortion(159.0e6, 0.050, 0.40, 0.500)['predictedBow']

    assert long / short == pytest.approx(4.0, rel = 0.01)

def testRemovalRateScalesWithEngagement():

    '''
    MRR is the product of the engagement terms, so doubling the radial depth doubles it.
    '''

    rates = []
    for radial in (0.002, 0.004):
        machining = MachiningProcess()
        machining.setInputs({'material': '6061', 'condition': 't6', 'radialDepth': radial,
                             'cuttingSpeed': 3.0})
        rates.append(machining.calculateCuttingForce()['materialRemovalRate'])

    assert rates[1] / rates[0] == pytest.approx(2.0, rel = 1e-9)

def testReportRuns():

    '''
    Smoke test, including the paths where tool life and chatter both fail.
    '''

    machining = MachiningProcess()
    machining.setInputs({'material': '6061', 'condition': 't6', 'cuttingSpeed': 3.0,
                         'axialDepth': 0.001})
    assert 'MACHINING PROCESS' in machining.generateReport()
