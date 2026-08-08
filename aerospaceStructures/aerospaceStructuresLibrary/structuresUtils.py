
# -- Domain-specific helpers [aerospaceStructures] -- #

'''

Structural helpers unique to this domain, plus the bridge to the aerospaceMaterials allowables.

This module is deliberately NOT named utils.py. Every domain library in this repository has a
utils.py that re-exports the shared foundation from common, and they all resolve to the same
'utils' entry in sys.modules when more than one domain is imported in a single process. That works
by accident for the shared names, because every domain re-exports the same ones, and it fails the
moment a caller asks for something only one domain defines.

The materials sub-domains hit exactly this and solved it by giving each library a uniquely named
helper module. This follows that pattern: utils.py stays the common re-export shim, and everything
specific to structures lives here under a name nothing else claims.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys

import numpy as np

def _bootstrapCommon() -> None:

    '''
    Locate orbitalRockets/common and put it on sys.path, independently of utils.py.
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

from units import *
from fluidProperties import *
from materials import *
from structures import *
from solvers import *
from reporting import *
from errors import *

ArrayLike = np.ndarray | list | float | int

AerospaceStructuresError = EngineeringError

#--------------------------------------------------------------------------------------------------------------------------#
# -- Domain Helpers -- #
#--------------------------------------------------------------------------------------------------------------------------#

def classicalShellBucklingStress(modulus: float, thickness: float, radius: float, poisson: float = 0.33) -> float:

    '''

    Classical small-deflection buckling stress for an axially loaded thin cylinder.

        sigma_cl = E t / (R sqrt(3 (1 - nu^2)))

    This is the number that overpredicts test by a factor of two to five, and every knockdown
    factor in this domain exists to correct it. It is exposed on its own precisely so the
    unfactored value can be looked at and disbelieved.

    '''

    if radius <= 0.0 or thickness <= 0.0:
        raise InvalidInputError('Shell radius and thickness must both be positive.',
                                context = createErrorContext(component = 'aerospaceStructures'))

    return modulus * thickness / (radius * np.sqrt(3.0 * (1.0 - poisson ** 2)))

def sp8007Knockdown(radiusToThickness: float) -> float:

    '''

    The NASA SP-8007 empirical knockdown for an unstiffened cylinder in axial compression.

        gamma = 1 - 0.901 (1 - exp(-phi))
        phi   = (1/16) sqrt(R/t)

    A lower-bound fit to the 1930s-1960s test scatter, not a physical model. It is conservative
    by design and it is still the starting point for preliminary sizing.

    '''

    if radiusToThickness <= 0.0:
        raise InvalidInputError('R/t must be positive.',
                                context = createErrorContext(component = 'aerospaceStructures'))

    phi = np.sqrt(radiusToThickness) / 16.0

    return 1.0 - 0.901 * (1.0 - np.exp(-phi))

def eulerCriticalStress(modulus: float, slenderness: float) -> float:

    '''

    Euler column stress, pi^2 E / (L'/rho)^2, valid only above the transition slenderness.

    '''

    if slenderness <= 0.0:
        raise InvalidInputError('Slenderness ratio must be positive.',
                                context = createErrorContext(component = 'aerospaceStructures'))

    return np.pi ** 2 * modulus / slenderness ** 2

def transitionSlenderness(modulus: float, yieldStrength: float) -> float:

    '''

    The slenderness at which Euler and Johnson meet, sqrt(2 pi^2 E / sigma_y).

    Below it a column crushes or yields in a Johnson parabola; above it, it buckles elastically.
    Applying Euler below this point is the classic column error and it is unconservative.

    '''

    if yieldStrength <= 0.0:
        raise InvalidInputError('Yield strength must be positive.',
                                context = createErrorContext(component = 'aerospaceStructures'))

    return np.sqrt(2.0 * np.pi ** 2 * modulus / yieldStrength)

def marginOfSafety(allowable: float, applied: float, factorOfSafety: float = 1.0) -> float:

    '''

    MS = allowable / (applied * FS) - 1.

    Returns positive infinity for zero applied load, which is the correct answer and avoids a
    divide by zero at every unloaded station in a sizing sweep.

    '''

    demand = abs(applied) * factorOfSafety

    if demand <= 0.0:
        return np.inf

    return allowable / demand - 1.0

#--------------------------------------------------------------------------------------------------------------------------#
# -- aerospaceStructures Error Types -- #
#--------------------------------------------------------------------------------------------------------------------------#

class BucklingError(AerospaceStructuresError):

    '''
    Raised when a buckling calculation is asked for outside the range its correlation covers.
    '''

    pass

class GeometryError(AerospaceStructuresError):

    '''
    Raised when a section or shell geometry is physically impossible or outside thin-wall theory.
    '''

    pass


#--------------------------------------------------------------------------------------------------------------------------#
# -- Material Allowables -- #
#--------------------------------------------------------------------------------------------------------------------------#

# aerospaceMaterials owns the allowables. common/materials.py carries only the nine-alloy seed
# table, which does not include 2219-T87 or any of the other tank and structure alloys, so this
# domain reaches into the materials database when it is present and degrades to the seed when it
# is not.
#
# The import has to be isolated. aerospaceMaterialsLibrary has its own utils.py, and putting it on
# sys.path shadows this one for every subsequent import in the process. The loader below saves and
# restores both sys.path and the 'utils' entry in sys.modules around the import.

_materialsDatabase = None
_materialsChecked  = False

def _loadMaterialsDatabase():

    '''

    Import aerospaceMaterials.MaterialDatabase without letting its utils module shadow ours.

    Returns the module, or None if the materials domain is not present. Cached after the first
    attempt so the path juggling happens once.

    '''

    global _materialsDatabase, _materialsChecked

    if _materialsChecked:
        return _materialsDatabase

    _materialsChecked = True

    directory = os.path.dirname(os.path.abspath(__file__))
    root      = directory
    while root != os.path.dirname(root):
        candidate = os.path.join(root, 'aerospaceMaterials', 'aerospaceMaterialsLibrary')
        if os.path.isdir(candidate):
            break
        root = os.path.dirname(root)
    else:
        return None

    if not os.path.isdir(candidate):
        return None

    savedPath  = list(sys.path)
    savedUtils = sys.modules.get('utils')

    try:
        sys.path.insert(0, candidate)
        # drop anything that would resolve to this domain's modules during the import
        for name in ('utils', 'MaterialDatabase', 'materialData'):
            sys.modules.pop(name, None)
        import MaterialDatabase as materialsModule
        _materialsDatabase = materialsModule
    except Exception:
        _materialsDatabase = None
    finally:
        sys.path[:] = savedPath
        if savedUtils is not None:
            sys.modules['utils'] = savedUtils
        else:
            sys.modules.pop('utils', None)

    return _materialsDatabase

def structuralAllowables(material: str, condition: str = None, temperature: float = 293.15,
                         orientation: str = 'L', basis: str = 'typical') -> dict:

    '''

    Elastic properties and strength allowables for a structural material.

    Tries the aerospaceMaterials database first, which carries the full alloy roster, the A and B
    basis allowables and the orientation dependence that short transverse loading needs. Falls back
    to the nine-alloy seed table in common when that domain is absent.

    The returned dictionary always carries 'source' saying which answered, because an A-basis
    allowable and a typical value are not the same number and the difference matters.

    '''

    database = _loadMaterialsDatabase()

    if database is not None:
        try:
            properties = database.queryMaterial(material, condition,
                                                temperature = temperature,
                                                orientation = orientation,
                                                basis = basis)
            properties = dict(properties)
            properties['source'] = 'aerospaceMaterials'
            properties['basis']  = basis
            return properties
        except Exception:
            pass

    properties = dict(materialProperties(material, temperature))
    properties['source'] = 'common seed table'
    properties['basis']  = 'typical'

    return properties

