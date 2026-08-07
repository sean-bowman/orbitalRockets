
# -- Collection of commonly used functions [fluidSystemsTesting] -- #

'''

Shared function repository for the fluidSystemsTesting library.

Most of what this module exposes it does not define. The shared foundation lives in
orbitalRockets/common and is re-exported below, so a call site inside this library sees one flat
namespace. The fluidSystems design library is also put on the path, because a test campaign is built
against the hardware that library sized: LeakTest delegates to LeakPath rather than reimplementing
detection sensitivity, and PressureTest uses the same material allowables the design used.

Defined here are the constants specific to test engineering: the qualification and acceptance margin
policy, the pressure test factors, and the fatigue and acceleration model parameters that turn a
flight environment into a test specification.

A NOTE ON THE MODULE NAME. Every other library in this repository names its shared module utils.py.
This one is campaignUtils.py, deliberately. Both this library and the fluidSystems design library sit
on a flat sys.path, so two modules named utils would collide and whichever imported first would
shadow the other. Since the design library owns utils.py in the fluidSystems tree and this library
imports from it, this module yields the name. Naming it testUtils.py was the other option and it was
rejected because pytest would collect it as a test file.

Author: Sean Bowman
Date:   08/06/2026

'''

import os
import sys

import numpy as np

def _bootstrapPaths() -> None:

    '''

    Put both orbitalRockets/common and the sibling fluidSystems design library on sys.path.

    Walks up from this file until it finds the directory containing 'common', which is the
    orbitalRockets root, then adds the shared package and the fluidSystems library from there. This
    library sits three levels below the root, so a fixed relative path would be fragile.

    '''

    directory = os.path.dirname(os.path.abspath(__file__))

    while directory != os.path.dirname(directory):

        commonPath = os.path.join(directory, 'common')

        if os.path.isdir(commonPath):

            designPath = os.path.join(directory, 'fluidSystems', 'fluidSystemsLibrary')

            for path in (commonPath, designPath):
                if os.path.isdir(path) and path not in sys.path:
                    sys.path.insert(0, path)
            return

        directory = os.path.dirname(directory)

    raise ImportError('Could not locate the orbitalRockets/common package by walking up from '
                      f'{os.path.abspath(__file__)}.')

_bootstrapPaths()

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
# -- Verification and Margin Policy -- #
#--------------------------------------------------------------------------------------------------------------------------#

# Verification methods, in the order a program should prefer them when either would satisfy the
# requirement. Test is the most expensive and the most convincing; similarity is the cheapest and the
# one most frequently claimed without a defensible argument behind it.
VERIFICATION_METHODS = ('test', 'demonstration', 'analysis', 'inspection', 'similarity')

# Test levels. Qualification demonstrates the design with margin and may be destructive; acceptance
# demonstrates that a specific article was built to that design, and must not consume its life.
TEST_LEVELS = ('development', 'qualification', 'acceptance', 'preflight')

# Pressure test factors on MEOP, from AIAA S-080 and S-081 for flight hardware.
#
# The 4.0 burst factor on a hazardous fluid line is much higher than the 2.0 on a pressure vessel,
# because a line is thin, exposed, handled, and the consequence of a hydrazine or LOX line rupture is
# a personnel hazard rather than a mission loss.
PRESSURE_TEST_FACTORS = {
    'pressure vessel metallic':   {'proof': 1.5, 'burst': 2.0},
    'pressure vessel copv':       {'proof': 1.5, 'burst': 2.5},
    'line hazardous fluid':       {'proof': 1.5, 'burst': 4.0},
    'line nonhazardous fluid':    {'proof': 1.5, 'burst': 2.5},
    'component':                  {'proof': 1.5, 'burst': 2.5},
    'hose flexible line':         {'proof': 1.5, 'burst': 4.0},
    'ground support equipment':   {'proof': 1.5, 'burst': 3.0}
}

# Environmental qualification margin over the flight (acceptance) level, from MIL-STD-1540 and
# NASA-STD-7002. These are the numbers that turn a flight environment into a test specification, and
# every one of them should be traceable rather than chosen.
QUALIFICATION_MARGINS = {
    'randomVibrationDecibels':    3.0,   # dB above acceptance
    'randomVibrationDuration':    2.0,   # x the acceptance duration, per axis
    'acousticDecibels':           3.0,   # dB above acceptance
    'shockFactor':                1.4,   # x the flight SRS
    'thermalMargin':             10.0,   # K beyond each end of the flight range
    'thermalCycleFactor':         2.0,   # x the acceptance cycle count
    'sineAmplitudeFactor':        1.25   # x the flight sine amplitude
}

# Acceptance random vibration duration, per axis, in seconds. Qualification is this times the
# duration factor above.
ACCEPTANCE_RANDOM_DURATION = 60.0

# Life test factor. Four times the expected life is the usual flight hardware requirement; a program
# with fracture control and credible usage monitoring may argue for two.
LIFE_TEST_FACTOR = 4.0

#--------------------------------------------------------------------------------------------------------------------------#
# -- Fatigue and Acceleration Models -- #
#--------------------------------------------------------------------------------------------------------------------------#

# Miner's rule fatigue exponent for random vibration duration scaling. The standard value of 4 comes
# from a typical S-N slope combined with the square-root relationship between PSD and stress
# amplitude, and it is what MIL-STD-1540 and NASA-STD-7001 assume.
#
# It is the reason a 3 dB level increase and a 2x duration increase are considered equivalent margin:
# a factor of 2 in PSD raises stress by sqrt(2), and sqrt(2)^4 = 4, so 3 dB buys a factor of 4 in
# equivalent time while 2x duration buys only 2.
MINER_FATIGUE_EXPONENT = 4.0

# Arrhenius activation energy for thermally accelerated life, in eV. The 0.7 eV default is the common
# electronics and elastomer value; the correct number is material and mechanism specific and should
# be measured rather than assumed.
DEFAULT_ACTIVATION_ENERGY = 0.7
BOLTZMANN_EV               = 8.617333262e-5   # eV/K

# Coffin-Manson exponent for thermal cycling acceleration. Values of 2 to 3 are typical for solder
# and for ductile metals; higher values apply to brittle materials.
DEFAULT_COFFIN_MANSON_EXPONENT = 2.0

#--------------------------------------------------------------------------------------------------------------------------#
# -- Test Engineering Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

# The domain base is an alias of the shared EngineeringError so the whole error family stays
# catchable with a single except clause. It is deliberately not given its own domainLabel, because
# that attribute is shared and mutating it would relabel every other domain's errors in the same
# process.
TestEngineeringError = EngineeringError

class TestInfeasibleError(EngineeringError):

    '''

    Exception raised when a test as specified cannot achieve what is being asked of it.

    The common cases, all of which should be caught at planning time rather than discovered in the
    test cell:

        - A leak requirement below the sensitivity floor of every available detection method
        - A pressure decay test whose temperature-limited floor sits above the target leak rate
        - A life test whose required duration exceeds the program schedule
        - A sample size requirement that exceeds the number of articles that will ever be built

    This is its own error type because the response differs from an input error. The inputs are
    valid; the test is simply not capable, and the fix is a different method or a renegotiated
    requirement rather than a corrected number.

    '''

    def __init__(self, message: str, context: dict = None,
                 required: float = None, achievable: float = None, method: str = None):

        if context is None:
            context = {}

        if required is not None:
            context['required'] = required
        if achievable is not None:
            context['achievable'] = achievable
        if method is not None:
            context['method'] = method

        super().__init__(message, context)
