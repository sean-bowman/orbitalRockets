
# -- ThermalEnvironment Class Definition -- #

'''

Ascent aeroheating, on-orbit hot and cold cases, and the thermal cycle definition that follows.

Thermal is the environment that is least like the others. Vibration, shock and acoustics are
transient and statistical; thermal is slow, deterministic and driven by orbital geometry. It is
also the environment most likely to be the design driver for something that looked benign, because
a thermal gradient is a load case and thermal growth is a displacement constraint.

Three regimes, and they do not overlap:

    ascent aeroheating     minutes, stagnation heating, driven by velocity and density
    on-orbit steady        hours to years, radiation balance against sun, albedo and Earth
    thermal cycling        every orbit, and the fatigue consequence of doing it thousands of times

The ascent estimate here is a stagnation point correlation, which is the right level for deciding
whether a surface needs protection at all. Anything past that decision needs a real aerothermal
analysis; this cannot size a heat shield and does not pretend to.

The on-orbit hot and cold cases are the useful output for most hardware. They are constructed
from the worst combinations of solar constant, albedo, Earth infrared, internal dissipation and
surface properties, and the two cases use deliberately different assumptions rather than being the
same calculation with different numbers.

Surface optical properties do most of the work. The ratio of solar absorptivity to infrared
emissivity sets the equilibrium temperature of a sunlit surface almost by itself, and it changes
with time in orbit as the surface degrades. Beginning-of-life and end-of-life are different
thermal designs.

See Also:
---------
LoadFactorSet : Thermal gradients are a load case alongside the mechanical ones
thermalManagement : (planned) sizes the protection this environment demands

Theory: docs/ThermalEnvironments.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from environmentsUtils import (applyInputs, formatReportTable,
                                   InvalidInputError, DerivationError, createErrorContext)
except ImportError:
    from .environmentsUtils import (applyInputs, formatReportTable,
                                    InvalidInputError, DerivationError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

STEFAN_BOLTZMANN = 5.670374419e-8    # [W/m^2/K^4]

# Solar constant at 1 AU, and its annual variation from orbital eccentricity. The hot case uses
# perihelion and the cold case aphelion, which is a 6.9 percent swing and is not negligible.
SOLAR_CONSTANT_MEAN       = 1361.0   # [W/m^2]
SOLAR_CONSTANT_PERIHELION = 1412.0   # [W/m^2], early January
SOLAR_CONSTANT_APHELION   = 1322.0   # [W/m^2], early July

# Earth albedo and outgoing infrared. Both vary with latitude, season and cloud cover, and the
# ranges below are the values used to bound hot and cold cases in low Earth orbit.
ALBEDO_HOT  = 0.35    # [-]
ALBEDO_COLD = 0.25    # [-]
EARTH_INFRARED_HOT  = 260.0   # [W/m^2]
EARTH_INFRARED_COLD = 220.0   # [W/m^2]

# Surface optical properties, as (solar absorptivity, infrared emissivity). The alpha over epsilon
# ratio is what sets a sunlit equilibrium temperature, and it degrades with ultraviolet exposure
# and atomic oxygen, so beginning and end of life differ.
SURFACE_FINISHES = {
    'white paint':          {'absorptivity': 0.20, 'emissivity': 0.88,
                             'endOfLifeAbsorptivity': 0.40,
                             'note': 'the standard radiator finish. Degrades substantially'},
    'black paint':          {'absorptivity': 0.95, 'emissivity': 0.88,
                             'endOfLifeAbsorptivity': 0.96,
                             'note': 'stable, and hot in sunlight'},
    'bare aluminium':       {'absorptivity': 0.15, 'emissivity': 0.05,
                             'endOfLifeAbsorptivity': 0.25,
                             'note': 'high alpha over epsilon. Runs very hot in sun'},
    'aluminised kapton':    {'absorptivity': 0.40, 'emissivity': 0.80,
                             'endOfLifeAbsorptivity': 0.55,
                             'note': 'common MLI outer layer'},
    'optical solar reflector': {'absorptivity': 0.08, 'emissivity': 0.80,
                                'endOfLifeAbsorptivity': 0.20,
                                'note': 'the best radiator finish, and expensive'},
}

# Sutton-Graves stagnation heating constant for air. q = k sqrt(rho / R_nose) V^3.
SUTTON_GRAVES_CONSTANT = 1.7415e-4    # [SI]

# Below this altitude the atmosphere is dense enough for aeroheating to matter on ascent.
AEROHEATING_ALTITUDE_CEILING = 120000.0    # [m]

# Thermal cycling: a low Earth orbit is roughly 90 minutes, so cycles accumulate quickly.
LOW_EARTH_ORBIT_PERIOD = 5400.0    # [s], 90 minutes

# ------------------------------------------------------------------------------------------------ #
# -- ThermalEnvironment -- #
# ------------------------------------------------------------------------------------------------ #

class ThermalEnvironment:

    '''

    Ascent and on-orbit thermal environment definition.

    Usage:
    ------
        thermal = ThermalEnvironment()
        thermal.setInputs({'surfaceFinish': 'white paint', 'altitude': 500.0e3,
                           'internalDissipation': 50.0, 'radiatingArea': 2.0})
        result = thermal.calculateOnOrbitCases()

    '''

    def __init__(self):

        # -- Surface -- #

        self.surfaceFinish       = 'white paint'   # key into SURFACE_FINISHES
        self.absorptivity        = np.nan  # [-], overrides the finish table
        self.emissivity          = np.nan  # [-], overrides the finish table
        self.endOfLife           = False   # [-], use degraded absorptivity

        # -- Orbit -- #

        self.altitude            = 500.0e3  # [m]
        self.radiatingArea       = np.nan   # [m^2]
        self.absorbingArea       = np.nan   # [m^2], sunlit projected area. Defaults to radiating
        self.internalDissipation = 0.0      # [W]
        self.eclipseFraction     = 0.35     # [-], of the orbit in shadow

        # -- Ascent -- #

        self.velocity            = np.nan  # [m/s], for the aeroheating estimate
        self.atmosphericDensity  = np.nan  # [kg/m^3]
        self.noseRadius          = np.nan  # [m]

        # -- Mission -- #

        self.missionYears        = 1.0     # [yr]

        # -- Results -- #

        self.findings            = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        '''

        requiredParams = {}

        optionalParams = {'surfaceFinish':       str,
                          'absorptivity':        (int, float),
                          'emissivity':          (int, float),
                          'endOfLife':           bool,
                          'altitude':            (int, float),
                          'radiatingArea':       (int, float),
                          'absorbingArea':       (int, float),
                          'internalDissipation': (int, float),
                          'eclipseFraction':     (int, float),
                          'velocity':            (int, float),
                          'atmosphericDensity':  (int, float),
                          'noseRadius':          (int, float),
                          'missionYears':        (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.surfaceFinish not in SURFACE_FINISHES:
            raise InvalidInputError(
                f'Unknown surface finish \'{self.surfaceFinish}\'. '
                f'Known: {sorted(SURFACE_FINISHES)}.',
                context = createErrorContext(component = 'ThermalEnvironment'))

        entry = SURFACE_FINISHES[self.surfaceFinish]

        if not np.isfinite(self.absorptivity):
            self.absorptivity = (entry['endOfLifeAbsorptivity'] if self.endOfLife
                                 else entry['absorptivity'])
        if not np.isfinite(self.emissivity):
            self.emissivity = entry['emissivity']

        if not np.isfinite(self.absorbingArea) and np.isfinite(self.radiatingArea):
            self.absorbingArea = self.radiatingArea

    # -------------------------------------------------------------------------------------------- #

    def calculateAeroheating(self) -> dict:

        '''

        Stagnation point convective heating during ascent, by the Sutton-Graves correlation.

            q = k sqrt(rho / R_nose) V^3

        The cube of velocity is the whole story: heating is overwhelmingly a velocity problem, and
        a 20 percent increase in velocity is a 73 percent increase in heat flux. Density enters as
        a square root, which is why the peak heating altitude is well above the peak dynamic
        pressure altitude.

        This sizes nothing. It decides whether a surface needs protection, and anything past that
        needs a real aerothermal analysis.

        '''

        for name in ('velocity', 'atmosphericDensity', 'noseRadius'):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0.0:
                raise InvalidInputError(
                    f'Aeroheating needs a positive {name}.',
                    context = createErrorContext(component = 'ThermalEnvironment'))

        heatFlux = (SUTTON_GRAVES_CONSTANT
                    * np.sqrt(self.atmosphericDensity / self.noseRadius)
                    * self.velocity ** 3)

        # radiation equilibrium wall temperature, the temperature an uncooled surface reaches
        equilibrium = (heatFlux / (self.emissivity * STEFAN_BOLTZMANN)) ** 0.25

        findings = []
        findings.append(
            f'Stagnation heat flux is {heatFlux / 1000.0:.1f} kW/m^2, giving a radiation '
            f'equilibrium wall temperature of {equilibrium:.0f} K at an emissivity of '
            f'{self.emissivity:.2f}.')

        findings.append(
            'Heating goes as velocity cubed and as the square root of density, so peak heating '
            'occurs well above peak dynamic pressure. Sizing thermal protection at max-Q is the '
            'wrong condition.')

        if equilibrium > 800.0:
            findings.append(
                f'{equilibrium:.0f} K is beyond bare aluminium. This surface needs thermal '
                f'protection or an ablative, and this correlation cannot size it.')

        return {'heatFlux':              heatFlux,
                'equilibriumTemperature': equilibrium,
                'velocity':              self.velocity,
                'density':               self.atmosphericDensity,
                'noseRadius':            self.noseRadius,
                'findings':              findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateOnOrbitCases(self) -> dict:

        '''

        Hot and cold case equilibrium temperatures, from the radiation balance.

        The two cases use different assumptions rather than being one calculation with different
        numbers: hot uses perihelion solar, maximum albedo, maximum Earth infrared, maximum
        internal dissipation and end-of-life absorptivity; cold uses aphelion, minimum albedo,
        minimum infrared, no dissipation, eclipse and beginning-of-life properties.

        '''

        if not np.isfinite(self.radiatingArea) or self.radiatingArea <= 0.0:
            raise InvalidInputError('On-orbit cases need a positive radiating area.',
                                    context = createErrorContext(component = 'ThermalEnvironment'))

        entry = SURFACE_FINISHES[self.surfaceFinish]

        # view factor to Earth, from the altitude
        earthRadius = 6.371e6
        viewFactor  = (earthRadius / (earthRadius + self.altitude)) ** 2

        # -- hot case -- #
        hotAbsorptivity = entry['endOfLifeAbsorptivity']
        hotAbsorbed = (SOLAR_CONSTANT_PERIHELION * hotAbsorptivity * self.absorbingArea
                       + SOLAR_CONSTANT_PERIHELION * ALBEDO_HOT * hotAbsorptivity
                       * self.absorbingArea * viewFactor
                       + EARTH_INFRARED_HOT * self.emissivity * self.radiatingArea * viewFactor
                       + self.internalDissipation)

        hotTemperature = (hotAbsorbed
                          / (self.emissivity * STEFAN_BOLTZMANN * self.radiatingArea)) ** 0.25

        # -- cold case -- #
        coldAbsorbed = (EARTH_INFRARED_COLD * self.emissivity * self.radiatingArea * viewFactor)

        coldTemperature = (coldAbsorbed
                           / (self.emissivity * STEFAN_BOLTZMANN * self.radiatingArea)) ** 0.25

        self.findings = []

        self.findings.append(
            f'Hot case {hotTemperature:.1f} K ({hotTemperature - 273.15:+.1f} degC), cold case '
            f'{coldTemperature:.1f} K ({coldTemperature - 273.15:+.1f} degC), a swing of '
            f'{hotTemperature - coldTemperature:.1f} K every orbit.')

        beginningRatio = entry['absorptivity'] / self.emissivity
        endRatio       = entry['endOfLifeAbsorptivity'] / self.emissivity

        self.findings.append(
            f'alpha over epsilon goes from {beginningRatio:.2f} at beginning of life to '
            f'{endRatio:.2f} at end of life. The hot case is an end-of-life condition and the '
            f'cold case a beginning-of-life one, so they are not the same surface.')

        if endRatio / beginningRatio > 1.5:
            self.findings.append(
                f'{self.surfaceFinish} degrades by {endRatio / beginningRatio:.1f}x in alpha over '
                f'epsilon. A thermal design closed at beginning-of-life properties will not close '
                f'at end of life.')

        return {'hotTemperature':      hotTemperature,
                'coldTemperature':     coldTemperature,
                'swing':               hotTemperature - coldTemperature,
                'hotAbsorbed':         hotAbsorbed,
                'coldAbsorbed':        coldAbsorbed,
                'viewFactor':          viewFactor,
                'beginningOfLifeRatio': beginningRatio,
                'endOfLifeRatio':      endRatio,
                'findings':            self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateThermalCycles(self) -> dict:

        '''

        Cycle count over the mission, and the temperature range each one spans.

        A low Earth orbit is about 90 minutes, so a one year mission is roughly 5800 cycles and a
        fifteen year mission is close to 88000. That is a fatigue problem for anything with a
        coefficient of thermal expansion mismatch, and solder joints are the classic casualty.

        '''

        cases = self.calculateOnOrbitCases()

        secondsPerYear = 365.25 * 24.0 * 3600.0
        cycles = self.missionYears * secondsPerYear / LOW_EARTH_ORBIT_PERIOD

        findings = list(cases['findings'])
        findings.append(
            f'{cycles:.0f} thermal cycles over {self.missionYears:.1f} years, each spanning '
            f'{cases["swing"]:.0f} K. Anything with a expansion mismatch accumulates fatigue at '
            f'that rate, and solder joints are the usual casualty.')

        if cycles > 10000.0:
            findings.append(
                'Above ten thousand cycles, thermal fatigue is a primary design consideration '
                'rather than a check, and qualification testing has to demonstrate it.')

        return {'cycles':          cycles,
                'orbitPeriod':     LOW_EARTH_ORBIT_PERIOD,
                'missionYears':    self.missionYears,
                'temperatureSwing': cases['swing'],
                'hotTemperature':  cases['hotTemperature'],
                'coldTemperature': cases['coldTemperature'],
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def compareFinishes(self) -> dict:

        '''

        Equilibrium temperature across the available surface finishes, at end of life.

        Surface optical properties do more for a thermal design than almost anything else, and the
        spread across finishes is larger than most active thermal control can achieve.

        '''

        if not np.isfinite(self.radiatingArea) or self.radiatingArea <= 0.0:
            raise InvalidInputError('A comparison needs a positive radiating area.',
                                    context = createErrorContext(component = 'ThermalEnvironment'))

        saved   = self.surfaceFinish
        results = {}

        try:
            for finish in SURFACE_FINISHES:
                self.surfaceFinish = finish
                entry = SURFACE_FINISHES[finish]
                self.absorptivity = entry['endOfLifeAbsorptivity']
                self.emissivity   = entry['emissivity']
                cases = self.calculateOnOrbitCases()
                results[finish] = {'hot':  cases['hotTemperature'],
                                   'cold': cases['coldTemperature'],
                                   'ratio': entry['endOfLifeAbsorptivity'] / entry['emissivity']}
        finally:
            self.surfaceFinish = saved
            entry = SURFACE_FINISHES[saved]
            self.absorptivity = (entry['endOfLifeAbsorptivity'] if self.endOfLife
                                 else entry['absorptivity'])
            self.emissivity = entry['emissivity']

        hottest = max(results, key = lambda name: results[name]['hot'])
        coolest = min(results, key = lambda name: results[name]['hot'])

        return {'finishes': results,
                'hottest':  hottest,
                'coolest':  coolest,
                'spread':   results[hottest]['hot'] - results[coolest]['hot'],
                'note':     f'{results[hottest]["hot"] - results[coolest]["hot"]:.0f} K between '
                            f'the hottest and coolest finish, on the same hardware.'}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the thermal environment.
        '''

        cases  = self.calculateOnOrbitCases()
        cycles = self.calculateThermalCycles()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  THERMAL ENVIRONMENT: {self.surfaceFinish}, '
                     f'{self.altitude / 1000.0:.0f} km')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Hot case',   f'{cases["hotTemperature"]:.1f}',
                 f'{cases["hotTemperature"] - 273.15:+.1f}'],
                ['Cold case',  f'{cases["coldTemperature"]:.1f}',
                 f'{cases["coldTemperature"] - 273.15:+.1f}'],
                ['Swing',      f'{cases["swing"]:.1f}', '']]
        lines.append(formatReportTable(rows, ['Case', 'Temperature [K]', 'degC'],
                                       title = 'On-orbit equilibrium'))
        lines.append('')

        opticalRows = [['Beginning of life alpha/eps', f'{cases["beginningOfLifeRatio"]:.3f}'],
                       ['End of life alpha/eps',       f'{cases["endOfLifeRatio"]:.3f}'],
                       ['Thermal cycles',              f'{cycles["cycles"]:.0f}']]
        lines.append(formatReportTable(opticalRows, ['Quantity', 'Value'],
                                       title = 'Surface and mission'))

        if cycles['findings']:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in cycles['findings']:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'thermalEnvironment.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the optical properties and geometry are physical.
        '''

        context = createErrorContext(component = 'ThermalEnvironment')

        if not 0.0 < self.emissivity <= 1.0:
            raise InvalidInputError(
                f'Emissivity must be in (0, 1], got {self.emissivity}.', context = context)

        if not 0.0 <= self.absorptivity <= 1.0:
            raise InvalidInputError(
                f'Absorptivity must be in [0, 1], got {self.absorptivity}.', context = context)

        if self.altitude < 0.0:
            raise InvalidInputError('Altitude cannot be negative.', context = context)

        if not 0.0 <= self.eclipseFraction < 1.0:
            raise InvalidInputError(
                f'Eclipse fraction must be in [0, 1), got {self.eclipseFraction}.',
                context = context)
