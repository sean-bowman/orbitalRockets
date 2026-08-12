# -- avionicsAndGNC init -- #

'''

__init__.py specifies to python that this repository is a library and can be imported and
used in other python projects with the familiar from NAME.OTHERNAME import NAMES structure
as long as this package is being called locally or is installed in the python environment.

Author: Sean Bowman
Date:   10/08/2026

'''

from avionicsUtils import *

from NavigationDrift import NavigationDrift
from ControlAuthority import ControlAuthority
from TelemetryBudget import TelemetryBudget
