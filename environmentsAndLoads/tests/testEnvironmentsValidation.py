# -- Validation of the environmentsAndLoads library against published references -- #

'''

The random vibration tools checked against the GEVS generalised test levels.

GEVS is unusually good validation material because it publishes both a spectrum and the Grms that
spectrum integrates to. The Grms is an independent check on the spectrum, and a tool that computes
one from the other sits inside a closed loop.

Every other test file in this domain checks that the code does what it was written to do. This one
checks whether what it was written to do is right, which is a different question and the only one
that can catch a wrong model.

The `level` recorded against each reference says how strong the check is. A `hardware` check
compares against measured or specified real hardware and can catch a wrong model. A `standard`
check reproduces a published formula exactly and can only catch an implementation error. Calling
the second one validation without qualification is how a repository convinces itself of something
false.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'environmentsAndLoadsLibrary'))
sys.path.insert(0, ROOT)

from validation.referenceCases import VALIDATION_LEVELS, REFERENCE_KINDS
from validation.referenceCases import RANDOM_VIBRATION_LEVELS

from environmentsUtils import overallRms

GEVS = RANDOM_VIBRATION_LEVELS['GEVS qualification, 22.7 kg or less']

def testTheReferenceCarriesItsProvenanceAndLevel():

    assert GEVS['source']
    assert GEVS['kind'] in REFERENCE_KINDS
    assert GEVS['level'] in VALIDATION_LEVELS
    assert GEVS['note']

def testGrmsMatchesThePublishedOverallLevel():

    '''
    The headline check. GEVS publishes the breakpoints and states the overall as 14.1 Grms.
    Integrating the breakpoints has to reproduce it, and this is a hardware level check because the
    spectrum is a real qualification level flown hardware has been tested to.
    '''

    computed = overallRms(GEVS['breakpoints'])

    assert computed == pytest.approx(GEVS['overallRms'], abs = 0.1), (
        f'computed {computed:.2f} Grms against a published {GEVS["overallRms"]:.1f}')

def testTheSpectrumIsInternallyConsistentWithItsSlope():

    '''
    The plateau is reached from 20 Hz by a +6 dB per octave slope, which is a square law in
    frequency. If the tabulated plateau did not follow from the tabulated start point, the table
    would have been transcribed wrongly, and this is the check that would have caught it.
    '''

    (startFrequency, startDensity), (plateauFrequency, plateauDensity) = GEVS['breakpoints'][:2]

    implied = startDensity * (plateauFrequency / startFrequency) ** 2

    assert implied == pytest.approx(plateauDensity, rel = 0.02), (
        f'a +6 dB/oct slope from {startDensity} at {startFrequency} Hz reaches {implied:.4f} at '
        f'{plateauFrequency} Hz, not the tabulated {plateauDensity}')

def testAcceptanceIsQualificationLessThreeDecibels():

    '''
    Two secondary sources appeared to contradict each other on the GEVS level, one quoting 14.1
    Grms and one quoting 10.0. They are the qualification and acceptance levels of the same
    spectrum: 3 dB is a factor of two in density and therefore sqrt(2) in Grms.

    Reproducing that relationship resolves the contradiction and validates the scaling at once.
    '''

    qualification = overallRms(GEVS['breakpoints'])
    acceptance    = qualification / np.sqrt(2.0)

    assert acceptance == pytest.approx(GEVS['acceptanceRms'], abs = 0.1)

def testGrmsIsUnchangedByAddingACollinearBreakpoint():

    '''
    Inserting a point that already lies on the spectrum must not change the integral. It catches a
    segment integration that mishandles its endpoints, which is invisible on a well formed table.
    '''

    original = overallRms(GEVS['breakpoints'])
    inserted = overallRms([(20.0, 0.026), (50.0, 0.16), (400.0, 0.16), (800.0, 0.16),
                           (2000.0, 0.026)])

    assert inserted == pytest.approx(original, rel = 1.0e-9)
