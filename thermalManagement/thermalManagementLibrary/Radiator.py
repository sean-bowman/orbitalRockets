
# -- Radiator Class Definition -- #

'''

Radiator sizing against a sink temperature, with fin efficiency and view factor.

Radiation is the only way to reject heat in vacuum, and it is a fourth power law, which makes a
radiator's behaviour unlike any other heat exchanger.

    Q = eps sigma A F (T_rad^4 - T_sink^4)

Two consequences follow directly and both are counterintuitive:

**Rejection collapses as the radiator gets cold.** Halving the absolute radiating temperature cuts
the rejection by sixteen. A radiator sized comfortably at 320 K is nearly useless at 250 K, which
is why low temperature waste heat is so expensive to reject and why cryogenic radiators are
enormous.

**The sink temperature barely matters until it is close.** At 320 K radiating to 250 K, the sink
term is 37 percent of the surface term, so a 20 K error in the sink is a modest error in the
answer. At 270 K radiating to 250 K it dominates, and the same 20 K error changes the answer by a
factor of two.

The other trap is that a radiator absorbs as well as emits. A surface with a poor alpha over
epsilon ratio pointed at the sun can absorb more than it rejects, making it a heater. That is why
radiator finishes are chosen for the lowest achievable ratio and why radiator pointing is a real
constraint on attitude.

See Also:
---------
ThermalControl : The heater that pays for an oversized radiator in the cold case
HeatPipe       : How the heat gets to the radiator from where it was generated

Theory: docs/RadiatorsAndRejection.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from thermalUtils import (applyInputs, formatReportTable, STEFAN_BOLTZMANN,
                              SURFACE_PROPERTIES, InvalidInputError, createErrorContext)
except ImportError:
    from .thermalUtils import (applyInputs, formatReportTable, STEFAN_BOLTZMANN,
                               SURFACE_PROPERTIES, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Deep space sink. Anything radiating to open space with no planet in view sees this.
DEEP_SPACE_TEMPERATURE = 4.0    # [K]

# Representative sink temperatures, which are what a radiator actually sees rather than 4 K.
SINK_TEMPERATURES = {
    'deep space':          {'value': 4.0,   'note': 'anti-sun, no planet in view. The best case'},
    'low earth orbit':     {'value': 250.0, 'note': 'Earth fills much of the hemisphere'},
    'geostationary':       {'value': 100.0, 'note': 'Earth is small in the field of view'},
    'sun facing':          {'value': 390.0, 'note': 'effectively a heat source, not a sink'},
}

# Fin efficiency: a radiating fin is cooler at its tip than its root, so it rejects less than an
# isothermal fin of the same area would.
MINIMUM_USEFUL_FIN_EFFICIENCY = 0.5    # [-], below this the fin is mostly dead area

# ------------------------------------------------------------------------------------------------ #
# -- Radiator -- #
# ------------------------------------------------------------------------------------------------ #

class Radiator:

    '''

    Radiator area sizing and performance.

    Usage:
    ------
        radiator = Radiator()
        radiator.setInputs({'heatLoad': 500.0, 'radiatingTemperature': 320.0,
                            'sinkEnvironment': 'low earth orbit',
                            'surfaceFinish': 'optical solar reflector'})
        result = radiator.sizeArea()

    '''

    def __init__(self):

        # -- Requirement -- #

        self.heatLoad             = np.nan   # [W]
        self.radiatingTemperature = np.nan   # [K], the radiator surface

        # -- Environment -- #

        self.sinkEnvironment      = 'low earth orbit'   # key into SINK_TEMPERATURES
        self.sinkTemperature      = np.nan   # [K], overrides the table
        self.solarFlux            = 0.0      # [W/m^2] incident on the radiator
        self.viewFactor           = 1.0      # [-] to the sink

        # -- Surface -- #

        self.surfaceFinish        = 'optical solar reflector'   # key into SURFACE_PROPERTIES
        self.emissivity           = np.nan   # [-], overrides
        self.absorptivity         = np.nan   # [-], overrides

        # -- Fin -- #

        self.finLength            = np.nan   # [m], root to tip
        self.finThickness         = np.nan   # [m]
        self.finConductivity      = np.nan   # [W/m/K]

        # -- Results -- #

        self.findings             = []       # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: heatLoad, radiatingTemperature.

        '''

        requiredParams = {'heatLoad':             (int, float),
                          'radiatingTemperature': (int, float)}

        optionalParams = {'sinkEnvironment':  str,
                          'sinkTemperature':  (int, float),
                          'solarFlux':        (int, float),
                          'viewFactor':       (int, float),
                          'surfaceFinish':    str,
                          'emissivity':       (int, float),
                          'absorptivity':     (int, float),
                          'finLength':        (int, float),
                          'finThickness':     (int, float),
                          'finConductivity':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.surfaceFinish not in SURFACE_PROPERTIES:
            raise InvalidInputError(
                f'Unknown finish \'{self.surfaceFinish}\'. Known: {sorted(SURFACE_PROPERTIES)}.',
                context = createErrorContext(component = 'Radiator'))

        entry = SURFACE_PROPERTIES[self.surfaceFinish]

        if not np.isfinite(self.emissivity):
            self.emissivity = entry['emissivity']
        if not np.isfinite(self.absorptivity):
            self.absorptivity = entry['absorptivity']

        if not np.isfinite(self.sinkTemperature):
            if self.sinkEnvironment not in SINK_TEMPERATURES:
                raise InvalidInputError(
                    f'Unknown sink \'{self.sinkEnvironment}\'. '
                    f'Known: {sorted(SINK_TEMPERATURES)}.',
                    context = createErrorContext(component = 'Radiator'))
            self.sinkTemperature = SINK_TEMPERATURES[self.sinkEnvironment]['value']

    # -------------------------------------------------------------------------------------------- #

    def calculateNetFlux(self) -> dict:

        '''

        Net rejection per unit area, after the absorbed solar load.

        A radiator absorbs as well as emits. With a poor alpha over epsilon ratio and sun on it,
        the absorbed load can exceed the rejected one and the radiator becomes a heater.

        '''

        self._validateInputs()

        emitted = (self.emissivity * STEFAN_BOLTZMANN * self.viewFactor
                   * (self.radiatingTemperature ** 4 - self.sinkTemperature ** 4))

        absorbed = self.absorptivity * self.solarFlux

        net = emitted - absorbed

        findings = []

        sinkTerm = self.sinkTemperature ** 4 / self.radiatingTemperature ** 4
        findings.append(
            f'The sink term is {sinkTerm * 100.0:.0f} % of the surface term. '
            + ('It dominates, so the answer is very sensitive to the sink temperature.'
               if sinkTerm > 0.5 else
               'The sink is comparatively unimportant here.'))

        if absorbed > 0.0:
            findings.append(
                f'Absorbed solar is {absorbed:.1f} W/m^2 against {emitted:.1f} W/m^2 emitted, at '
                f'alpha over epsilon of {self.absorptivity / self.emissivity:.2f}.')

        if net <= 0.0:
            findings.append(
                'The radiator absorbs more than it rejects. It is a heater in this condition, and '
                'either the finish or the pointing has to change.')

        return {'emitted':      emitted,
                'absorbed':     absorbed,
                'netFlux':      net,
                'sinkFraction': sinkTerm,
                'alphaOverEpsilon': self.absorptivity / self.emissivity,
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeArea(self) -> dict:

        '''

        Radiator area for the required heat load.

        '''

        self._validateInputs()

        flux = self.calculateNetFlux()

        if flux['netFlux'] <= 0.0:
            raise InvalidInputError(
                'Net rejection is zero or negative, so no finite area rejects this load. Change '
                'the finish, the pointing or the radiating temperature.',
                context = createErrorContext(component = 'Radiator'))

        area = self.heatLoad / flux['netFlux']

        efficiency = 1.0
        if np.isfinite(self.finLength):
            efficiency = self.calculateFinEfficiency()['efficiency']
            area /= efficiency

        self.findings = list(flux['findings'])

        # the fourth power sensitivity, which is the thing to internalise
        colder = self.radiatingTemperature - 30.0
        if colder > self.sinkTemperature:
            colderFlux = (self.emissivity * STEFAN_BOLTZMANN * self.viewFactor
                          * (colder ** 4 - self.sinkTemperature ** 4)
                          - self.absorptivity * self.solarFlux)
            if colderFlux > 0.0:
                self.findings.append(
                    f'Radiating 30 K colder at {colder:.0f} K would need '
                    f'{self.heatLoad / colderFlux / efficiency:.2f} m^2 against {area:.2f}, a '
                    f'{(self.heatLoad / colderFlux / efficiency) / area:.2f}x increase. Rejection '
                    f'is a fourth power law, so a cold radiator is an enormous one.')

        return {'area':           area,
                'netFlux':        flux['netFlux'],
                'finEfficiency':  efficiency,
                'heatLoad':       self.heatLoad,
                'radiatingTemperature': self.radiatingTemperature,
                'sinkTemperature': self.sinkTemperature,
                'findings':       self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateFinEfficiency(self) -> dict:

        '''

        Fin efficiency for a straight radiating fin.

        A fin is cooler at its tip than its root, so it rejects less than an isothermal fin of the
        same area. Below about 0.5 the outer part of the fin is mostly dead area and a shorter,
        thicker fin rejects more for the same mass.

        '''

        self._validateInputs()

        for name in ('finLength', 'finThickness', 'finConductivity'):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0.0:
                raise InvalidInputError(f'Fin efficiency needs a positive {name}.',
                                        context = createErrorContext(component = 'Radiator'))

        # linearised radiation coefficient about the operating point
        coefficient = (self.emissivity * STEFAN_BOLTZMANN
                       * (self.radiatingTemperature + self.sinkTemperature)
                       * (self.radiatingTemperature ** 2 + self.sinkTemperature ** 2))

        # radiating from both faces
        parameter = np.sqrt(2.0 * coefficient / (self.finConductivity * self.finThickness))
        argument  = parameter * self.finLength

        efficiency = float(np.tanh(argument) / argument) if argument > 0.0 else 1.0

        findings = []
        if efficiency < MINIMUM_USEFUL_FIN_EFFICIENCY:
            findings.append(
                f'Fin efficiency {efficiency:.2f} is below '
                f'{MINIMUM_USEFUL_FIN_EFFICIENCY:.1f}, so the outer part of the fin is mostly dead '
                f'area. A shorter or thicker fin rejects more for the same mass.')

        return {'efficiency':          efficiency,
                'finParameter':        parameter,
                'dimensionlessLength': argument,
                'radiationCoefficient': coefficient,
                'findings':            findings}

    # -------------------------------------------------------------------------------------------- #

    def compareSinks(self) -> dict:

        '''

        Area required across the sink environments, which is what pointing buys.

        '''

        self._validateInputs()

        saved = (self.sinkEnvironment, self.sinkTemperature)
        results = {}

        try:
            for name, entry in SINK_TEMPERATURES.items():

                self.sinkTemperature = entry['value']

                # A sink at or above the radiator temperature is a legitimate comparison result,
                # not an error: it says this pointing does not work. Letting the validation raise
                # here would lose the most informative row in the table.
                if entry['value'] >= self.radiatingTemperature:
                    results[name] = {'sinkTemperature': entry['value'],
                                     'netFlux':         0.0,
                                     'area':            np.inf,
                                     'usable':          False,
                                     'note':            entry['note'] + '. Above the radiator '
                                                        'temperature, so it absorbs'}
                    continue

                flux = self.calculateNetFlux()
                results[name] = {'sinkTemperature': entry['value'],
                                 'netFlux':         flux['netFlux'],
                                 'area':            (self.heatLoad / flux['netFlux']
                                                     if flux['netFlux'] > 0.0 else np.inf),
                                 'usable':          bool(flux['netFlux'] > 0.0),
                                 'note':            entry['note']}
        finally:
            self.sinkEnvironment, self.sinkTemperature = saved

        feasible = {name: entry for name, entry in results.items() if np.isfinite(entry['area'])}
        best  = min(feasible, key = lambda name: feasible[name]['area'])
        worst = max(feasible, key = lambda name: feasible[name]['area'])

        return {'sinks':   results,
                'best':    best,
                'worst':   worst,
                'spread':  feasible[worst]['area'] / feasible[best]['area'],
                'note':    f'{feasible[worst]["area"] / feasible[best]["area"]:.1f}x between the '
                           f'best and worst usable sink, on the same hardware.'}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the radiator.
        '''

        sizing = self.sizeArea()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  RADIATOR: {self.heatLoad:.0f} W at '
                     f'{self.radiatingTemperature:.0f} K, {self.surfaceFinish}')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Sink temperature', f'{self.sinkTemperature:.1f}', 'K'],
                ['Net flux',         f'{sizing["netFlux"]:.1f}', 'W/m^2'],
                ['Fin efficiency',   f'{sizing["finEfficiency"]:.3f}', '-'],
                ['Area',             f'{sizing["area"]:.3f}', 'm^2'],
                ['alpha / eps',      f'{self.absorptivity / self.emissivity:.3f}', '-']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Sizing'))

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
            with open(os.path.join(outputDir, 'radiator.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the requirement and environment are physical.
        '''

        context = createErrorContext(component = 'Radiator')

        if not np.isfinite(self.heatLoad) or self.heatLoad <= 0.0:
            raise InvalidInputError('Heat load must be positive.', context = context)

        if not np.isfinite(self.radiatingTemperature) or self.radiatingTemperature <= 0.0:
            raise InvalidInputError('Radiating temperature must be absolute and positive.',
                                    context = context)

        if self.radiatingTemperature <= self.sinkTemperature:
            raise InvalidInputError(
                f'The radiator at {self.radiatingTemperature:.1f} K is at or below its sink at '
                f'{self.sinkTemperature:.1f} K, so it absorbs rather than rejects.',
                context = context)

        if not 0.0 < self.emissivity <= 1.0:
            raise InvalidInputError(f'Emissivity must be in (0, 1], got {self.emissivity}.',
                                    context = context)

        if not 0.0 < self.viewFactor <= 1.0:
            raise InvalidInputError(f'View factor must be in (0, 1], got {self.viewFactor}.',
                                    context = context)
