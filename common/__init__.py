
# -- orbitalRockets common init -- #

'''

The shared foundation every domain in orbitalRockets is built on.

Rather than duplicating unit constants, fluid property access, material data and solver plumbing
into fifteen separate domain libraries, they live here once. Each domain's utils.py locates this
package and re-exports what it needs, so a call site inside any domain sees a flat namespace and
does not have to know where a helper came from.

What lives here is what more than one domain needs. Anything specific to a single domain (ASME
B31.3 piping wall thickness, shell buckling, catalyst bed chemistry) belongs to that domain, not
here. The test for whether something belongs in common is simple: name the second domain that needs
it. If you cannot, it does not belong here yet.

Modules:

--------------------------------------------------------------------------------------------------
> units
    >> Unit conversion constants and the US Standard Atmosphere 1976 model
> fluidProperties
    >> refWrap, coolWrap, hydrazineProps, fluidProps, species molar mass, leak rate and SCFM
       conversions
> materials
    >> Alloy properties with a cryogenic strength correction, and surface roughness by process
> structures
    >> Thin wall relations general enough for more than one domain
> solvers
    >> secantSolve and solveForUnknown, the two root finders every sizing routine uses
> reporting
    >> applyInputs (the setInputs implementation) and formatReportTable (the generateReport output)
> errors
    >> EngineeringError base plus the generic error types every domain raises
--------------------------------------------------------------------------------------------------

Author: Sean Bowman
Date:   08/06/2026

'''

from errors import *
from units import *
from fluidProperties import *
from materials import *
from structures import *
from solvers import *
from reporting import *
