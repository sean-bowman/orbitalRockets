
# -- electricalPower init -- #

'''

__init__.py specifies to python that this repository is a library and can be imported and
used in other python projects with the familiar from NAME.OTHERNAME import NAMES structure
as long as this package is being called locally or is installed in the python environment.

Author: Sean Bowman
Date:   08/06/2026

'''

from powerUtils import *

from PowerBudget import PowerBudget
from Battery import Battery
from HarnessSizing import HarnessSizing
from SolenoidDrive import SolenoidDrive
