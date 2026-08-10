
# -- HarnessSizing -- #

'''

Wire gauge, and the result that surprises people who size wire on current.

**Ampacity does not choose the gauge on a launch vehicle. Voltage drop does.**

A 3 A load on a 12 m run needs 22 AWG to carry the current after bundle and altitude derating, and
16 AWG to arrive with enough voltage to work. Those are three gauge steps apart and a factor of four
in copper mass, and a harness sized on the first number does not function.

The reason is geometry rather than electricity. A launch vehicle harness is long relative to its
currents, and voltage drop scales with length while ampacity does not.

The second half of this class is mass. **Harness mass is always more than estimated**, and the
reason is that it is usually estimated as a fraction of dry mass rather than counted. Counting it
from run lengths, gauges, insulation and connectors is more work and it is the only method that
does not drift.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from powerUtils import (SINGLE_WIRE_AMPACITY, BUNDLE_DERATING, ALTITUDE_DERATING,
                            VOLTAGE_DROP_LIMIT, INSULATION_MASS_FACTOR, CONNECTOR_TYPES,
                            COPPER_DENSITY, wireDiameter, wireArea, wireResistance, voltageDrop,
                            interpolateFactor,
                            applyInputs, formatReportTable, createErrorContext,
                            InvalidInputError, HarnessError)
except ImportError:
    from .powerUtils import (SINGLE_WIRE_AMPACITY, BUNDLE_DERATING, ALTITUDE_DERATING,
                             VOLTAGE_DROP_LIMIT, INSULATION_MASS_FACTOR, CONNECTOR_TYPES,
                             COPPER_DENSITY, wireDiameter, wireArea, wireResistance, voltageDrop,
                             interpolateFactor,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, HarnessError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Gauges considered when sizing, from heavy power feed to fine signal wire.
CANDIDATE_GAUGES = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]

# Allowance for the length a wire runs beyond the straight-line distance: routing around structure,
# service loops, and the slack a connector needs to be mated.
#
# Twenty per cent is representative and it is registered as unvalidated. It is also the number most
# often left out entirely, which is a large part of why harness mass is underestimated.
ROUTING_ALLOWANCE = 0.20    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- HarnessSizing -- #
# ------------------------------------------------------------------------------------------------ #

class HarnessSizing:

    '''

    Gauge selection against both constraints, and a harness mass counted rather than fractioned.

    '''

    def __init__(self):

        self.busVoltage       = np.nan
        self.current          = np.nan
        self.length           = np.nan
        self.bundleSize       = np.nan
        self.altitude         = np.nan
        self.conductorTemperature = np.nan
        self.dropLimit        = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `bundleSize` is the number of current-carrying wires in the bundle this one sits in, which
        is what decides how well it can shed heat.

        `length` is the one-way run length. The class doubles it for the return path.

        '''

        requiredParams = {'busVoltage': (int, float),
                          'current':    (int, float),
                          'length':     (int, float)}

        optionalParams = {'bundleSize':           (int, float),
                          'altitude':             (int, float),
                          'conductorTemperature': (int, float),
                          'dropLimit':            (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.bundleSize):
            self.bundleSize = 15.0

        if not np.isfinite(self.altitude):
            self.altitude = 0.0

        if not np.isfinite(self.conductorTemperature):
            self.conductorTemperature = 70.0

        if not np.isfinite(self.dropLimit):
            self.dropLimit = VOLTAGE_DROP_LIMIT

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def deratedAmpacity(self, gauge: int) -> dict:

        '''

        What a wire can actually carry in its bundle at its altitude.

        The bundle factor is the larger of the two and it is the one most often forgotten. A wire in
        the middle of a thirty-wire harness carries under half its free-air rating, because it
        cannot shed heat to anywhere except its neighbours, which are also warm.

        '''

        if gauge not in SINGLE_WIRE_AMPACITY:
            raise InvalidInputError(
                f'No free-air ampacity for {gauge} AWG. Known gauges are '
                f'{sorted(SINGLE_WIRE_AMPACITY)}.',
                context = createErrorContext(component = 'HarnessSizing'))

        freeAir = SINGLE_WIRE_AMPACITY[gauge]

        bundle   = interpolateFactor(BUNDLE_DERATING, self.bundleSize)
        altitude = interpolateFactor(ALTITUDE_DERATING, self.altitude)

        return {'gauge':           gauge,
                'freeAir':         freeAir,
                'bundleFactor':    bundle,
                'altitudeFactor':  altitude,
                'derated':         freeAir * bundle * altitude}

    # -------------------------------------------------------------------------------------------- #

    def sizeGauge(self) -> dict:

        '''

        The gauge each constraint demands, and the one that governs.

        Both are computed and reported rather than only the answer, because **which constraint
        binds is the useful information**. A harness where ampacity binds is a short, high current
        harness and a harness where voltage drop binds is a long one, and they are managed
        differently.

        '''

        findings = []

        allowedDrop = self.dropLimit * self.busVoltage

        ampacityGauge = None
        dropGauge     = None

        detail = {}

        for gauge in sorted(CANDIDATE_GAUGES, reverse = True):

            derated = self.deratedAmpacity(gauge)

            drop = voltageDrop(gauge, self.length, self.current, self.conductorTemperature)

            detail[gauge] = {'derated': derated['derated'], 'drop': drop,
                             'dropFraction': drop / self.busVoltage}

            if ampacityGauge is None and derated['derated'] >= self.current:
                ampacityGauge = gauge

            if dropGauge is None and drop <= allowedDrop:
                dropGauge = gauge

        if ampacityGauge is None:
            raise HarnessError(
                f'No gauge in {CANDIDATE_GAUGES} carries {self.current:.1f} A in a bundle of '
                f'{self.bundleSize:.0f} at {self.altitude:.0f} m. The derating is doing the work: '
                f'the largest candidate carries '
                f'{self.deratedAmpacity(min(CANDIDATE_GAUGES))["derated"]:.1f} A. Split the load '
                f'across parallel runs or reduce the bundle size.',
                context = createErrorContext(component = 'HarnessSizing'))

        if dropGauge is None:
            raise HarnessError(
                f'No gauge in {CANDIDATE_GAUGES} keeps the drop over {self.length:.1f} m within '
                f'{allowedDrop:.2f} V at {self.current:.1f} A. **This is a run length problem '
                f'rather than a wire problem**: doubling the copper halves the drop, and the '
                f'largest candidate still loses '
                f'{detail[min(CANDIDATE_GAUGES)]["drop"]:.2f} V. Move the source closer, raise the '
                f'bus voltage, or accept a local regulator.',
                context = createErrorContext(component = 'HarnessSizing'))

        # the smaller AWG number is the heavier wire, so the governing gauge is the minimum
        governing = min(ampacityGauge, dropGauge)

        binding = 'voltage drop' if dropGauge < ampacityGauge else 'ampacity'

        if dropGauge == ampacityGauge:
            binding = 'both'

        findings.append(
            f'Ampacity needs {ampacityGauge} AWG and voltage drop needs {dropGauge} AWG, so '
            f'**{binding}** governs at {governing} AWG.')

        if binding == 'voltage drop':

            massRatio = wireArea(governing) / wireArea(ampacityGauge)

            findings.append(
                f'That is {ampacityGauge - governing} gauge steps heavier than the current alone '
                f'demands, and {massRatio:.1f} times the copper. **A harness sized on ampacity '
                f'would not function**, because the load would see '
                f'{self.busVoltage - detail[ampacityGauge]["drop"]:.1f} V.')

        findings.append(
            f'The drop at {governing} AWG is {detail[governing]["drop"]:.2f} V, '
            f'{detail[governing]["dropFraction"]:.1%} of the bus.')

        self.findings = findings

        return {'ampacityGauge': ampacityGauge,
                'dropGauge':     dropGauge,
                'governing':     governing,
                'binding':       binding,
                'allowedDrop':   allowedDrop,
                'detail':        detail,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateMass(self, runs: list, connectors: dict = None) -> dict:

        '''

        Harness mass counted from runs and connectors rather than taken as a fraction.

        `runs` is a list of dictionaries with a `gauge`, a `length` and a `count` of conductors.
        `connectors` maps a type from `CONNECTOR_TYPES` to a quantity.

        The routing allowance is applied to every run, because a wire never goes where the straight
        line goes.

        '''

        if not runs:
            raise InvalidInputError(
                'A harness needs at least one run to have a mass. Estimating it as a fraction of '
                'dry mass is the method this class exists to replace.',
                context = createErrorContext(component = 'HarnessSizing'))

        findings = []

        wireMass = 0.0
        detail   = []

        for index, run in enumerate(runs):

            for key in ('gauge', 'length', 'count'):
                if key not in run:
                    raise InvalidInputError(
                        f'Run {index + 1} has no {key}.',
                        context = createErrorContext(component = 'HarnessSizing'))

            gauge = run['gauge']

            if gauge not in INSULATION_MASS_FACTOR:
                raise InvalidInputError(
                    f'No insulation mass factor for {gauge} AWG. Known gauges are '
                    f'{sorted(INSULATION_MASS_FACTOR)}.',
                    context = createErrorContext(component = 'HarnessSizing'))

            routed = run['length'] * (1.0 + ROUTING_ALLOWANCE)

            copper = wireArea(gauge) * routed * COPPER_DENSITY * run['count']

            insulated = copper * INSULATION_MASS_FACTOR[gauge]

            wireMass += insulated

            detail.append({'gauge':      gauge,
                           'length':     run['length'],
                           'routed':     routed,
                           'count':      run['count'],
                           'copperMass': copper,
                           'mass':       insulated})

        connectorMass  = 0.0
        connectorCount = 0

        if connectors:
            for name, quantity in connectors.items():

                if name not in CONNECTOR_TYPES:
                    raise InvalidInputError(
                        f"Unknown connector type '{name}'. Known types are "
                        f'{sorted(CONNECTOR_TYPES)}.',
                        context = createErrorContext(component = 'HarnessSizing'))

                connectorMass  += CONNECTOR_TYPES[name]['mass'] * quantity
                connectorCount += quantity

        total = wireMass + connectorMass

        findings.append(
            f'{len(runs)} runs give {wireMass:.2f} kg of wire, including a '
            f'{ROUTING_ALLOWANCE:.0%} routing allowance.')

        if connectorCount:
            findings.append(
                f'{connectorCount} connectors add {connectorMass:.2f} kg, '
                f'{connectorMass / total:.0%} of the total.')

            findings.append(
                '**Connector count is the best available reliability proxy for a harness**, so '
                'that number is worth tracking for a reason other than mass.')

        findings.append(
            'Counted rather than fractioned. A harness estimated as a percentage of dry mass '
            'grows every time the vehicle does and never converges, because the thing it is a '
            'fraction of is not what drives it.')

        self.findings = findings

        return {'wireMass':       wireMass,
                'connectorMass':  connectorMass,
                'totalMass':      total,
                'connectorCount': connectorCount,
                'runs':           detail,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def compareBusVoltage(self, voltages: list = None) -> dict:

        '''

        The same load at different bus voltages, which is the cleanest argument for a higher bus.

        Power is fixed, so current falls with voltage, and the allowed drop rises with it. Both
        move the same way, so **the copper required falls roughly with the square of bus voltage.**

        '''

        if voltages is None:
            voltages = [12.0, 28.0, 50.0, 100.0]

        power = self.busVoltage * self.current

        original = (self.busVoltage, self.current)

        results = {}

        try:
            for voltage in voltages:

                self.busVoltage = voltage
                self.current    = power / voltage

                try:
                    sized = self.sizeGauge()
                except HarnessError:
                    results[voltage] = None
                    continue

                results[voltage] = {'current':   self.current,
                                    'governing': sized['governing'],
                                    'binding':   sized['binding'],
                                    'area':      wireArea(sized['governing'])}

        finally:
            self.busVoltage, self.current = original

        viable = {key: entry for key, entry in results.items() if entry}

        lightest = min(viable, key = lambda key: viable[key]['area']) if viable else None

        return {'power':    power,
                'results':  results,
                'lightest': lightest}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full harness sizing report.
        '''

        sized = self.sizeGauge()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  HARNESS: {self.current:.1f} A over {self.length:.1f} m on a '
                     f'{self.busVoltage:.0f} V bus')
        lines.append('=' * 96)
        lines.append('')

        rows = [[f'{gauge}',
                 f'{wireDiameter(gauge) * 1000.0:.2f}',
                 f'{entry["derated"]:.1f}',
                 f'{entry["drop"]:.2f}',
                 f'{entry["dropFraction"]:.1%}']
                for gauge, entry in sorted(sized['detail'].items())]

        lines.append(formatReportTable(
            rows, ['AWG', 'Diameter [mm]', 'Derated [A]', 'Drop [V]', 'Fraction'],
            title = 'Candidates'))

        lines.append('')
        lines.append(formatReportTable(
            [['Bundle size',         f'{self.bundleSize:.0f}',                        'wires'],
             ['Altitude',            f'{self.altitude:.0f}',                          'm'],
             ['Ampacity needs',      f'{sized["ampacityGauge"]}',                     'AWG'],
             ['Voltage drop needs',  f'{sized["dropGauge"]}',                         'AWG'],
             ['Governing',           f'{sized["governing"]}',                         'AWG'],
             ['Binding constraint',  f'{sized["binding"]}',                           '']],
            ['Quantity', 'Value', 'Unit'], title = 'Sizing'))

        lines.append('')
        for finding in sized['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'harness_sizing.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('bus voltage', self.busVoltage),
                            ('current',     self.current),
                            ('length',      self.length)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'HarnessSizing'))

        if self.bundleSize < 1:
            raise InvalidInputError(
                f'A bundle has at least one wire in it, got {self.bundleSize}.',
                context = createErrorContext(component = 'HarnessSizing'))

        if self.altitude < 0.0:
            raise InvalidInputError(
                f'The altitude cannot be negative, got {self.altitude}.',
                context = createErrorContext(component = 'HarnessSizing'))

        if not 0.0 < self.dropLimit < 1.0:
            raise InvalidInputError(
                f'The voltage drop limit must lie in (0, 1) as a fraction of bus voltage, got '
                f'{self.dropLimit}.',
                context = createErrorContext(component = 'HarnessSizing'))
