
# -- fluidSystemsTesting init -- #

'''

__init__.py specifies to python that this repository is a library and can be imported and used in
other python projects with the familiar from NAME.OTHERNAME import NAMES structure as long as this
package is being called locally or is installed in the python environment.

Note that the shared module here is campaignUtils rather than utils. Both this library and the
fluidSystems design library sit on a flat sys.path, so two modules named utils would collide.

Author: Sean Bowman
Date:   08/06/2026

'''

from campaignUtils import *

from TestCampaign import *
from PressureTest import *
from LeakTest import *
from EnvironmentalTest import *
from LifeTest import *
from UncertaintyBudget import *
from SampleSize import *
