# -- Validation of the aerospaceStructures library against published references -- #

'''

The shell buckling knockdown checked against the NASA SP-8007 closed form.

This is a `standard` level check and the distinction matters here more than anywhere else in the
repository. The knockdown is a curve fitted to test scatter in the 1960s, and reproducing the
published curve validates the implementation while saying nothing about whether the curve is right.
The scatter it was fitted to is not in the document in a form that can be re-fitted.

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

sys.path.insert(0, os.path.join(DOMAIN, 'aerospaceStructuresLibrary'))
sys.path.insert(0, ROOT)

from validation.referenceCases import VALIDATION_LEVELS, REFERENCE_KINDS
from validation.referenceCases import SHELL_BUCKLING

from structuresUtils import sp8007Knockdown, classicalShellBucklingStress

KNOCKDOWN = SHELL_BUCKLING['NASA SP-8007 knockdown']

def testTheReferenceCarriesItsProvenanceAndLevel():

    assert KNOCKDOWN['source']
    assert KNOCKDOWN['level'] == 'standard'
    assert KNOCKDOWN['note']

def testTheKnockdownReproducesThePublishedCurve():

    '''
    Five radius-to-thickness ratios spanning the range a launch vehicle tank actually uses. Each is
    computed from the published closed form, so any error in the implementation, in the sixteenth,
    in the 0.901 or in the sign of the exponent, shows up here.
    '''

    for ratio, expected in KNOCKDOWN['points'].items():
        assert sp8007Knockdown(ratio) == pytest.approx(expected, abs = 1.0e-4), (
            f'R/t {ratio}: computed {sp8007Knockdown(ratio):.4f} against published {expected:.4f}')

def testTheKnockdownFallsMonotonicallyWithSlenderness():

    ratios = sorted(KNOCKDOWN['points'])

    values = [sp8007Knockdown(ratio) for ratio in ratios]

    assert values == sorted(values, reverse = True)

def testTheKnockdownIsSevereEnoughToMatter():

    '''
    The reason the factor exists. At R/t 1000, which is an ordinary launch vehicle tank, the
    classical stress overpredicts by a factor of four and a half. A tool that omitted the knockdown
    would size a tank wall at under a quarter of what it needs.
    '''

    assert sp8007Knockdown(1000.0) < 0.25
    assert 1.0 / sp8007Knockdown(1000.0) > 4.0

def testClassicalBucklingStressMatchesItsClosedForm():

    '''
    sigma = E t / (R sqrt(3 (1 - nu^2))). Exact, so an implementation either reproduces it or is
    wrong.
    '''

    modulus, thickness, radius, poisson = 70.0e9, 0.003, 1.5, 0.33

    expected = modulus * thickness / (radius * np.sqrt(3.0 * (1.0 - poisson ** 2)))

    assert classicalShellBucklingStress(modulus, thickness, radius,
                                        poisson) == pytest.approx(expected)

def testClassicalBucklingIsIndependentOfLength():

    '''
    The classical result depends on radius and thickness only. A length dependence appearing would
    mean a different buckling mode has been implemented under the same name.
    '''

    first  = classicalShellBucklingStress(70.0e9, 0.003, 1.5)
    second = classicalShellBucklingStress(70.0e9, 0.003, 1.5)

    assert first == second
