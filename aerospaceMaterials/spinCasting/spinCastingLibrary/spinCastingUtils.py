
# -- Collection of commonly used functions [spinCasting] -- #

'''

Shared function repository for the spinCasting library.

Centrifugal casting: rotational speed selection, solidification, and the inclusion migration that sets the bore machining allowance.

Most of what this module exposes it does not define. Two layers are re-exported below so a call site
inside this library sees one flat namespace:

    orbitalRockets/common                  units, fluid properties, solvers, reporting, errors
    aerospaceMaterials/aerospaceMaterialsLibrary   the alloy database and the allowables machinery

A NAMING NOTE. This module is called spinCastingUtils.py rather than utils.py, and that is deliberate.
Every library in this repository ends up on a flat sys.path when pytest collects them in one
process, so a second utils.py would shadow the first and whichever was imported earliest would win.
The aerospaceMaterials parent library owns the name utils.py; every sub-domain uses its own.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np

def _bootstrapPaths() -> None:

    '''

    Put orbitalRockets/common and the aerospaceMaterials library on sys.path.

    Walks up from this file until it finds the common directory, so it works from any nesting depth.
    The aerospaceMaterials library is located relative to the same anchor, which means this file does
    not care how deep the sub-domain sits.

    '''

    directory = os.path.dirname(os.path.abspath(__file__))

    while directory != os.path.dirname(directory):

        candidate = os.path.join(directory, 'common')

        if os.path.isdir(candidate):
            if candidate not in sys.path:
                sys.path.insert(0, candidate)
            materials = os.path.join(directory, 'aerospaceMaterials', 'aerospaceMaterialsLibrary')
            if os.path.isdir(materials) and materials not in sys.path:
                sys.path.insert(0, materials)
            return

        directory = os.path.dirname(directory)

    raise ImportError('Could not locate the orbitalRockets/common package by walking up from '
                      f'{os.path.abspath(__file__)}. Is this file still inside the tree?')

_bootstrapPaths()

# Re-export the shared foundation.
from units import *
from fluidProperties import *
from materials import *
from structures import *
from solvers import *
from reporting import *
from errors import *

# Re-export the materials domain, so a sub-domain class can query an alloy and apply a knockdown
# without every call site repeating the import.
from MaterialDatabase import queryMaterial, resolveMaterialKey, getProvenance
from materialData import MATERIAL_DATABASE, SOURCES

ArrayLike = np.ndarray | list | float | int

# ------------------------------------------------------------------------------------------------ #
# -- Errors -- #
# ------------------------------------------------------------------------------------------------ #

# Aliased onto the shared base rather than subclassed, so that an `except EngineeringError` in a
# caller catches this sub-domain's failures alongside every other domain's. Deliberately not given
# its own domainLabel: that attribute lives on the shared class and setting it here would relabel
# every other domain's errors in the same process.

CentrifugalCastingError = EngineeringError

class ProcessInfeasibleError(EngineeringError):

    '''

    Raised when the process cannot produce the requested result at all, as distinct from producing
    it badly. A geometry below the minimum feature size, a speed the machine cannot reach, a removal
    depth that exceeds the wall.

    '''

    domainLabel = 'PROCESS INFEASIBLE'
