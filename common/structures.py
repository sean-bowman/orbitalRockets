
# -- Shared Structural Relations [orbitalRockets common] -- #

'''

Structural relations general enough to be needed by more than one domain.

Deliberately small. Anything specific to a code (ASME B31.3 piping wall thickness) or to a
structural form (shell buckling, sandwich panels, bolted joints) belongs to the domain that owns
it, not here. This module is the seed for aerospaceStructures.

Author: Sean Bowman
Date:   08/06/2026

'''

import numpy as np

#--------------------------------------------------------------------------------------------------------------------------#
# -- Thin Wall Relations -- #
#--------------------------------------------------------------------------------------------------------------------------#

def hoopStressCalculator(pressureDifferential: float, diameter: float, thickness: float = None, hoopStress: float = None) -> float:

    '''

    Thin-wall cylindrical hoop stress, solving for whichever argument is left None.

    sigma_h = dP * D / (2 * t)

    Valid for D/t greater than about 20. Below that the through-thickness stress gradient matters
    and the thick-wall (Lame) solution should be used instead; b31_3WallThickness carries the
    correction terms that make the thin-wall form usable up to the code limit.

    '''

    # Which version of the problem are we solving
    if thickness is not None and hoopStress is None:
        return (pressureDifferential * diameter) / (2 * thickness)
    if thickness is None and hoopStress is not None:
        return (pressureDifferential * diameter) / (2 * hoopStress)

    raise ValueError('hoopStressCalculator needs exactly one of thickness or hoopStress to be None. Leave the one you want solved for unspecified.')
