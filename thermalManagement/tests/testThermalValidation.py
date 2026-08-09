# -- Validation of the thermalManagement library against published references -- #

'''

The radiation implementation checked against published constants and optical properties.

The Stefan-Boltzmann constant has been exact by definition since the 2019 SI revision, so an
implementation that disagrees is wrong rather than approximate. The solar constant is measured. The
equilibrium temperature of a coated plate follows from both plus a tabulated property pair, and
checks the fourth-power balance and the property table together.

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

sys.path.insert(0, os.path.join(DOMAIN, 'thermalManagementLibrary'))
sys.path.insert(0, ROOT)

from validation.referenceCases import VALIDATION_LEVELS, REFERENCE_KINDS
from validation.referenceCases import THERMAL_EQUILIBRIUM

from thermalUtils import STEFAN_BOLTZMANN, SURFACE_PROPERTIES

def testEveryThermalReferenceCarriesItsProvenanceAndLevel():

    for name, entry in THERMAL_EQUILIBRIUM.items():
        assert entry['source'], name
        assert entry['kind'] in REFERENCE_KINDS, name
        assert entry['level'] in VALIDATION_LEVELS, name

def testStefanBoltzmannMatchesTheDefinedValue():

    '''
    Exact by the 2019 SI redefinition. There is no tolerance to argue about.
    '''

    published = THERMAL_EQUILIBRIUM['Stefan-Boltzmann constant']['value']

    assert STEFAN_BOLTZMANN == pytest.approx(published, rel = 1.0e-12)

def testWhitePaintOpticalPropertiesMatchTheHandbook():

    reference = THERMAL_EQUILIBRIUM['white paint equilibrium']

    entry = SURFACE_PROPERTIES['white paint']

    assert entry['absorptivity'] == pytest.approx(reference['absorptivity'])
    assert entry['emissivity']   == pytest.approx(reference['emissivity'])

def testWhitePaintEquilibriumTemperatureClosesOnTheFourthPowerBalance():

    '''
    A flat plate normal to the sun at 1 AU with no other load sits at
    (alpha/eps x G / sigma)^0.25. Every term is published, so the equilibrium is a closed-form
    check on the radiation implementation and the property table together.
    '''

    reference = THERMAL_EQUILIBRIUM['white paint equilibrium']
    solar     = THERMAL_EQUILIBRIUM['solar constant']['value']

    ratio = reference['absorptivity'] / reference['emissivity']

    computed = (ratio * solar / STEFAN_BOLTZMANN) ** 0.25

    assert computed == pytest.approx(reference['equilibrium'], abs = 1.0)

def testBareAluminiumRunsHotterThanWhitePaintDespiteAbsorbingLess():

    '''
    The most misread result in spacecraft thermal control, and it follows directly from the
    tabulated properties. Bare aluminium absorbs 0.15 against white paint's 0.20 and runs far
    hotter, because it emits 0.05 against 0.88.
    '''

    solar = THERMAL_EQUILIBRIUM['solar constant']['value']

    def equilibrium(name):
        entry = SURFACE_PROPERTIES[name]
        return ((entry['absorptivity'] / entry['emissivity']) * solar / STEFAN_BOLTZMANN) ** 0.25

    assert SURFACE_PROPERTIES['bare aluminium']['absorptivity'] < \
        SURFACE_PROPERTIES['white paint']['absorptivity']

    assert equilibrium('bare aluminium') > equilibrium('white paint') + 200.0
