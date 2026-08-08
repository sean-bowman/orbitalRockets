
# -- HeatPipe Class Definition -- #

'''

Heat pipe transport capability and the four operating limits that bound it.

A heat pipe moves heat by evaporating a working fluid at one end and condensing it at the other,
with a wick returning the liquid by capillary action. It has no moving parts and an effective
conductivity orders of magnitude above any solid, which is why it is used wherever heat has to
travel from where it is made to where it can be rejected.

It also stops working entirely rather than degrading, and there are four separate ways to reach
that point:

    capillary    the wick cannot pump the liquid back fast enough. The usual limit
    sonic        vapour flow chokes at the evaporator exit. A startup problem
    entrainment  vapour shear tears liquid off the wick surface
    boiling      the wick nucleates vapour and the liquid path is broken

The governing limit is whichever is lowest, and the design question is almost always the capillary
one because it falls with length and with adverse tilt. A heat pipe that works horizontally can
fail entirely with a few millimetres of the wrong tilt in one gravity, which makes ground testing a
real problem: a pipe qualified in the lab in the wrong orientation was never tested.

Working fluid choice sets the temperature range and it is not adjustable. Each fluid works between
roughly its triple point and its critical point, and outside that band the pipe is inert. A pipe
frozen below its fluid's melting point does not conduct, and starting one from frozen is its own
engineering problem.

See Also:
---------
Radiator       : Where the heat pipe is usually taking heat to
ThermalNetwork : A heat pipe is a very low resistance path in a network

Theory: docs/HeatPipesAndTwoPhase.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from thermalUtils import (applyInputs, formatReportTable,
                              InvalidInputError, createErrorContext)
except ImportError:
    from .thermalUtils import (applyInputs, formatReportTable,
                               InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Working Fluids -- #
# ------------------------------------------------------------------------------------------------ #

# Working fluids with their usable temperature band and the properties the limits need, evaluated
# at a representative operating temperature. A heat pipe outside its fluid's band is inert.
WORKING_FLUIDS = {
    'ammonia':  {'range': (213.0, 373.0), 'latentHeat': 1.16e6, 'liquidDensity': 600.0,
                 'vapourDensity': 4.8, 'surfaceTension': 0.0213, 'liquidViscosity': 1.4e-4,
                 'vapourViscosity': 9.0e-6,
                 'note': 'the spacecraft standard. Excellent merit number'},
    'water':    {'range': (303.0, 473.0), 'latentHeat': 2.26e6, 'liquidDensity': 958.0,
                 'vapourDensity': 0.60, 'surfaceTension': 0.0589, 'liquidViscosity': 2.8e-4,
                 'vapourViscosity': 1.2e-5,
                 'note': 'best merit number of all, and it freezes at 273 K'},
    'methanol': {'range': (283.0, 403.0), 'latentHeat': 1.10e6, 'liquidDensity': 750.0,
                 'vapourDensity': 1.2, 'surfaceTension': 0.0200, 'liquidViscosity': 4.0e-4,
                 'vapourViscosity': 1.0e-5,
                 'note': 'lower freezing point than water, lower performance'},
    'ethane':   {'range': (150.0, 300.0), 'latentHeat': 4.90e5, 'liquidDensity': 520.0,
                 'vapourDensity': 8.0, 'surfaceTension': 0.0090, 'liquidViscosity': 1.0e-4,
                 'vapourViscosity': 7.0e-6,
                 'note': 'cryogenic range, for detectors and cold hardware'},
}

# Wick types, as effective pore radius and permeability. The pore radius sets the capillary head
# and the permeability sets the flow resistance, and they pull in opposite directions: a finer
# wick pumps harder and flows worse.
WICK_TYPES = {
    'axial groove':   {'poreRadius': 2.5e-4, 'permeability': 5.0e-9,
                       'note': 'extruded, the spacecraft standard. Poor against gravity'},
    'sintered metal': {'poreRadius': 3.0e-5, 'permeability': 2.0e-11,
                       'note': 'high capillary head, works against gravity, high flow resistance'},
    'screen mesh':    {'poreRadius': 8.0e-5, 'permeability': 3.0e-10,
                       'note': 'the middle option'},
    'arterial':       {'poreRadius': 2.0e-5, 'permeability': 1.0e-9,
                       'note': 'separate liquid artery. High performance, priming risk'},
}

GRAVITY = 9.80665    # [m/s^2]

# Nucleation site radius in a wick, which sets the boiling limit. Three orders below the pore
# radius, and it dominates the boiling driving term completely.
NUCLEATION_RADIUS = 2.5e-7    # [m]

# Entrainment is characterised by a Weber number of order one at the liquid-vapour interface.
ENTRAINMENT_WEBER_NUMBER = 1.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- HeatPipe -- #
# ------------------------------------------------------------------------------------------------ #

class HeatPipe:

    '''

    Heat pipe transport limits.

    Usage:
    ------
        pipe = HeatPipe()
        pipe.setInputs({'workingFluid': 'ammonia', 'wickType': 'axial groove',
                        'length': 1.0, 'vapourRadius': 0.006,
                        'wickThickness': 0.001, 'operatingTemperature': 300.0})
        result = pipe.calculateLimits()

    '''

    def __init__(self):

        # -- Fluid and Wick -- #

        self.workingFluid   = 'ammonia'      # key into WORKING_FLUIDS
        self.wickType       = 'axial groove' # key into WICK_TYPES
        self.poreRadius     = np.nan  # [m], overrides the wick table
        self.permeability   = np.nan  # [m^2], overrides

        # -- Geometry -- #

        self.length         = np.nan  # [m], effective length, evaporator to condenser centres
        self.vapourRadius   = np.nan  # [m], vapour core
        self.wickThickness  = np.nan  # [m]

        # -- Operating -- #

        self.operatingTemperature = 300.0   # [K]
        self.tiltAngle      = 0.0     # [deg], positive is evaporator above condenser, the bad way
        self.gravityLevel   = 0.0     # [-], multiples of Earth gravity. Zero on orbit

        # -- Results -- #

        self.findings       = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: length, vapourRadius.

        '''

        requiredParams = {'length':       (int, float),
                          'vapourRadius': (int, float)}

        optionalParams = {'workingFluid':         str,
                          'wickType':             str,
                          'poreRadius':           (int, float),
                          'permeability':         (int, float),
                          'wickThickness':        (int, float),
                          'operatingTemperature': (int, float),
                          'tiltAngle':            (int, float),
                          'gravityLevel':         (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.workingFluid not in WORKING_FLUIDS:
            raise InvalidInputError(
                f'Unknown working fluid \'{self.workingFluid}\'. '
                f'Known: {sorted(WORKING_FLUIDS)}.',
                context = createErrorContext(component = 'HeatPipe'))

        if self.wickType not in WICK_TYPES:
            raise InvalidInputError(
                f'Unknown wick \'{self.wickType}\'. Known: {sorted(WICK_TYPES)}.',
                context = createErrorContext(component = 'HeatPipe'))

        wick = WICK_TYPES[self.wickType]

        if not np.isfinite(self.poreRadius):
            self.poreRadius = wick['poreRadius']
        if not np.isfinite(self.permeability):
            self.permeability = wick['permeability']

    # -------------------------------------------------------------------------------------------- #

    @property
    def fluid(self) -> dict:

        '''
        The working fluid's properties.
        '''

        return WORKING_FLUIDS[self.workingFluid]

    @property
    def wickArea(self) -> float:

        '''
        Annular wick cross section.
        '''

        outer = self.vapourRadius + self.wickThickness

        return np.pi * (outer ** 2 - self.vapourRadius ** 2)

    # -------------------------------------------------------------------------------------------- #

    def calculateCapillaryLimit(self) -> dict:

        '''

        The capillary limit: the wick cannot return liquid faster than it evaporates.

            Q_cap = (2 sigma / r_pore - rho g L sin(theta)) K A rho h_fg / (mu L)

        This is the usual governing limit, and it is the one that falls with length and with
        adverse tilt. The gravity term is what makes ground testing difficult: a pipe that works on
        orbit can fail on a bench with a few millimetres of the wrong tilt.

        '''

        self._validateInputs()

        fluid = self.fluid

        capillaryHead = 2.0 * fluid['surfaceTension'] / self.poreRadius

        gravityHead = (fluid['liquidDensity'] * GRAVITY * self.gravityLevel
                       * self.length * np.sin(np.radians(self.tiltAngle)))

        netHead = capillaryHead - gravityHead

        findings = []

        if netHead <= 0.0:
            findings.append(
                f'The gravity head of {gravityHead:.0f} Pa exceeds the capillary head of '
                f'{capillaryHead:.0f} Pa, so the wick cannot return liquid at all. The pipe is '
                f'dry and transports nothing. This is what an adverse tilt does on the ground.')
            limit = 0.0
        else:
            limit = (netHead * self.permeability * self.wickArea
                     * fluid['liquidDensity'] * fluid['latentHeat']
                     / (fluid['liquidViscosity'] * self.length))

        return {'capillaryHead': capillaryHead,
                'gravityHead':   gravityHead,
                'netHead':       netHead,
                'limit':         limit,
                'findings':      findings}

    def calculateSonicLimit(self) -> dict:

        '''

        The sonic limit: vapour flow chokes at the evaporator exit.

        A startup problem rather than a steady state one. At low temperature the vapour density is
        small, so the velocity needed to carry the heat is high, and the flow can choke before the
        pipe reaches its operating temperature.

        '''

        self._validateInputs()

        fluid = self.fluid
        area  = np.pi * self.vapourRadius ** 2

        # the standard choked-flow form for a heat pipe vapour core
        limit = (0.474 * area * fluid['latentHeat']
                 * np.sqrt(fluid['vapourDensity'] * self._vapourPressure()))

        return {'limit': limit, 'vapourArea': area}

    def calculateEntrainmentLimit(self) -> dict:

        '''

        The entrainment limit: vapour shear tears liquid off the wick surface.

        Characterised by a Weber number of order one at the interface.

        '''

        self._validateInputs()

        fluid = self.fluid
        area  = np.pi * self.vapourRadius ** 2

        limit = area * fluid['latentHeat'] * np.sqrt(
            fluid['vapourDensity'] * fluid['surfaceTension']
            / (2.0 * self.poreRadius * ENTRAINMENT_WEBER_NUMBER))

        return {'limit': limit}

    def calculateBoilingLimit(self) -> dict:

        '''

        The boiling limit: the wick nucleates vapour and the liquid return path is broken.

        Radial rather than axial, so unlike the others it does not depend on pipe length. It is the
        limit that a short high-flux evaporator runs into.

        '''

        self._validateInputs()

        fluid = self.fluid

        # effective wick conductivity, taken as the liquid's for a conservative estimate
        effectiveConductivity = 0.5    # [W/m/K], representative for a liquid-filled wick

        # The driving term is the difference between the nucleation radius and the wick pore
        # radius, and because the nucleation radius is three orders smaller it dominates
        # completely. Using the pore radius alone in its place understates the limit by roughly
        # that ratio and makes boiling appear to govern when it does not.
        prefactor = (4.0 * np.pi * self.length * effectiveConductivity
                     * self.operatingTemperature * fluid['surfaceTension']
                     / (fluid['latentHeat'] * fluid['vapourDensity']
                        * np.log((self.vapourRadius + self.wickThickness) / self.vapourRadius)))

        radiusTerm = 1.0 / NUCLEATION_RADIUS - 1.0 / self.poreRadius

        limit = prefactor * radiusTerm

        return {'limit': limit,
                'prefactor': prefactor,
                'nucleationRadius': NUCLEATION_RADIUS}

    # -------------------------------------------------------------------------------------------- #

    def calculateLimits(self) -> dict:

        '''

        All four limits, with the governing one identified.

        A heat pipe stops working rather than degrading, so the governing limit is a cliff and not
        a margin. Knowing which one it is decides what to change.

        '''

        self._validateInputs()

        capillary   = self.calculateCapillaryLimit()
        sonic       = self.calculateSonicLimit()
        entrainment = self.calculateEntrainmentLimit()
        boiling     = self.calculateBoilingLimit()

        limits = {'capillary':   capillary['limit'],
                  'sonic':       sonic['limit'],
                  'entrainment': entrainment['limit'],
                  'boiling':     boiling['limit']}

        governing = min(limits, key = limits.get)

        self.findings = list(capillary['findings'])

        self.findings.append(
            f'The {governing} limit governs at {limits[governing]:.1f} W. A heat pipe stops '
            f'working rather than degrading, so that is a cliff and not a margin.')

        fixes = {'capillary':   'a finer wick, a shorter pipe, or removing the adverse tilt',
                 'sonic':       'a larger vapour core, or a higher operating temperature',
                 'entrainment': 'a larger vapour core, or a coarser wick',
                 'boiling':     'a thinner wick, or spreading the evaporator heat flux'}

        self.findings.append(f'The lever is {fixes[governing]}.')

        low, high = self.fluid['range']
        if not low <= self.operatingTemperature <= high:
            self.findings.append(
                f'{self.operatingTemperature:.0f} K is outside the usable band for '
                f'{self.workingFluid}, which is {low:.0f} to {high:.0f} K. Outside it the pipe is '
                f'inert, and below the freezing point it does not conduct at all.')

        return {'limits':        limits,
                'governing':     governing,
                'transportCapability': limits[governing],
                'capillaryDetail': capillary,
                'findings':      self.findings}

    # -------------------------------------------------------------------------------------------- #

    def checkGroundTestability(self, tiltAngles: list = None) -> dict:

        '''

        Transport capability against tilt in one gravity, which is what a bench test sees.

        A pipe qualified in the lab at a favourable tilt was never tested. The capability against
        adverse tilt is the number that says whether a ground test means anything.

        '''

        self._validateInputs()

        angles = tiltAngles if tiltAngles is not None else [-2.0, -0.5, 0.0, 0.5, 2.0, 5.0]

        saved = (self.tiltAngle, self.gravityLevel)
        results = {}

        try:
            self.gravityLevel = 1.0
            for angle in angles:
                self.tiltAngle = angle
                results[angle] = self.calculateCapillaryLimit()['limit']
        finally:
            self.tiltAngle, self.gravityLevel = saved

        orbital = self.calculateCapillaryLimit()['limit'] if self.gravityLevel == 0.0 else None

        findings = []

        adverse = [angle for angle in angles if angle > 0.0]
        dead = [angle for angle in adverse if results[angle] <= 0.0]

        if dead:
            findings.append(
                f'The pipe transports nothing at {min(dead):.1f} degrees adverse tilt in one '
                f'gravity. A bench test has to control tilt to better than that, and a pipe tested '
                f'favourably was never tested.')

        return {'byTilt':        results,
                'orbitalLimit':  orbital,
                'deadAngles':    dead,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def _vapourPressure(self) -> float:

        '''
        A representative vapour pressure from the ideal gas relation on the tabulated density.
        '''

        fluid = self.fluid
        gasConstant = 8.314462618 / 0.017    # [J/kg/K], ammonia-like molar mass as a stand-in

        return fluid['vapourDensity'] * gasConstant * self.operatingTemperature

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the heat pipe.
        '''

        result = self.calculateLimits()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  HEAT PIPE: {self.workingFluid}, {self.wickType}, '
                     f'{self.length:.2f} m')
        lines.append('=' * 96)
        lines.append('')

        rows = [[name, f'{value:.1f}',
                 'GOVERNS' if name == result['governing'] else '']
                for name, value in sorted(result['limits'].items(), key = lambda item: item[1])]
        lines.append(formatReportTable(rows, ['Limit', 'Capability [W]', ''],
                                       title = f'Operating limits at '
                                               f'{self.operatingTemperature:.0f} K'))

        if self.findings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in self.findings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'heatPipe.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the geometry and operating point are physical.
        '''

        context = createErrorContext(component = 'HeatPipe')

        for name in ('length', 'vapourRadius'):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0.0:
                raise InvalidInputError(f'{name} must be positive.', context = context)

        if not np.isfinite(self.wickThickness) or self.wickThickness <= 0.0:
            raise InvalidInputError('Wick thickness must be positive.', context = context)

        if self.poreRadius <= 0.0 or self.permeability <= 0.0:
            raise InvalidInputError('Pore radius and permeability must be positive.',
                                    context = context)

        if self.operatingTemperature <= 0.0:
            raise InvalidInputError('Operating temperature must be absolute and positive.',
                                    context = context)

        if self.gravityLevel < 0.0:
            raise InvalidInputError('Gravity level cannot be negative.', context = context)

        if abs(self.tiltAngle) > 90.0:
            raise InvalidInputError(
                f'Tilt angle must be within +/- 90 degrees, got {self.tiltAngle}.',
                context = context)
