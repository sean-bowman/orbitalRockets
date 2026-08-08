# -- Domain-specific helpers [propulsionTesting] -- #

'''

Hot fire campaign structure, test stands, instrumentation and data reduction.

Named propulsionTestUtils rather than utils. Every domain library in this repository has a utils.py
re-exporting the shared foundation, and they all resolve to the same 'utils' entry in sys.modules
when more than one domain is imported in a single process. That works by accident for the names
every domain re-exports and fails for anything only one domain defines.

Domain-specific helpers are added here as the library is built out. Anything needed by a second
domain belongs in orbitalRockets/common instead.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np

def _bootstrapCommon() -> None:

    '''
    Locate the orbitalRockets/common package and put it on sys.path.
    '''

    directory = os.path.dirname(os.path.abspath(__file__))

    while directory != os.path.dirname(directory):
        candidate = os.path.join(directory, 'common')
        if os.path.isdir(candidate):
            if candidate not in sys.path:
                sys.path.insert(0, candidate)
            return
        directory = os.path.dirname(directory)

    raise ImportError('Could not locate the orbitalRockets/common package.')

_bootstrapCommon()

# Re-export the shared foundation so the namespace inside this library stays flat.
from units import *
from fluidProperties import *
from materials import *
from structures import *
from solvers import *
from reporting import *
from errors import *

# Permissive numeric-input alias: these helpers accept arrays, lists, or scalars interchangeably.
ArrayLike = np.ndarray | list | float | int

#--------------------------------------------------------------------------------------------------------------------------#
# -- propulsionTesting Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError, so the whole error family stays
# catchable with one except clause. Domain-specific error types are added below as needed.
PropulsionTestingError = EngineeringError
