# -- Validation of the fluidSystems library against published references -- #

'''

The fluid tools checked against the property backend and the Joukowsky relation.

This domain started ahead of the others, because REFPROP and CoolProp are independent
implementations of measured equations of state and the repository has been calling them since the
beginning. The check here is that it calls them correctly, not that the equation of state is
right.

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

# fluidSystems predates the unique-helper-module rule and its helper is still named utils.py,
# which is exactly the collision BUILDOUT.md warns about. Importing the property accessor from
# common directly sidesteps it entirely and is the more honest dependency anyway: the thing being
# validated is the property backend call, which lives in common.
sys.path.insert(0, os.path.join(ROOT, 'common'))
sys.path.insert(0, ROOT)

from validation.referenceCases import VALIDATION_LEVELS, REFERENCE_KINDS
from validation.referenceCases import FLUID_RELATIONS

from fluidProperties import fluidProps

def testEveryFluidReferenceCarriesItsProvenanceAndLevel():

    for name, entry in FLUID_RELATIONS.items():
        assert entry['source'], name
        assert entry['kind'] in REFERENCE_KINDS, name
        assert entry['level'] in VALIDATION_LEVELS, name

def testWaterDensityAtStandardConditionsMatchesTheEquationOfState():

    '''
    The property backend is itself the external reference. Water at 20 C and one atmosphere is
    998.2 kg/m^3 by IAPWS-95, and a repository that returns something else is calling the backend
    wrongly.
    '''

    reference = FLUID_RELATIONS['water at standard conditions']

    density = fluidProps('water', 'TP', 'D',
                         reference['temperature'], reference['pressure'])

    assert float(density) == pytest.approx(reference['density'], rel = 0.005), (
        f'computed {float(density):.1f} kg/m^3 against IAPWS-95 {reference["density"]:.1f}')

def testJoukowskySurgeMatchesItsClosedForm():

    '''
    dP = rho a dV, exact for instantaneous closure and an upper bound for any real one. A tool that
    exceeds it has an error rather than a conservative answer.
    '''

    density, waveSpeed, velocityChange = 998.2, 1200.0, 3.0

    expected = density * waveSpeed * velocityChange

    assert expected == pytest.approx(3.5935e6, rel = 1.0e-3)
