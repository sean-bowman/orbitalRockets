
# -- EnginePerformance -- #

'''

Characteristic velocity, thrust coefficient, specific impulse and altitude behaviour.

The organising idea is that `F = Cf c* mdot` factors performance into two independent halves, and
that the factorisation is a diagnostic rather than an algebraic convenience.

    c* is everything upstream of the throat. Injector, chamber, mixing, residence time, combustion.
    Cf is everything downstream of it. Area ratio, contour, divergence, ambient pressure.

Nothing the nozzle does can change c*, and nothing the injector does can change Cf. So a measured
specific impulse shortfall on its own says only that something is wrong. Measuring chamber pressure
and mass flow gives c* directly, and c* against its ideal value separates the two cases. An engine
five per cent down on Isp with nominal c* has a nozzle problem, and no amount of injector work will
find it.

That is why this class reports both efficiencies separately and refuses to collapse them into a
single Isp efficiency, which is the form the number is most often quoted in and the least useful.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from propulsionUtils import (PROPELLANT_COMBINATIONS, SUMMERFIELD_SEPARATION_RATIO,
                                 TYPICAL_CSTAR_EFFICIENCY,
                                 TYPICAL_THRUST_COEFFICIENT_EFFICIENCY,
                                 GRAVITY, vandenkerckhove,
                                 pressureRatioFromAreaRatio, convertAltitudeToPressure,
                                 convertPressureToAltitude,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, PerformanceError, PropellantError)
except ImportError:
    from .propulsionUtils import (PROPELLANT_COMBINATIONS, SUMMERFIELD_SEPARATION_RATIO,
                                  TYPICAL_CSTAR_EFFICIENCY,
                                  TYPICAL_THRUST_COEFFICIENT_EFFICIENCY,
                                  GRAVITY, vandenkerckhove,
                                  pressureRatioFromAreaRatio, convertAltitudeToPressure,
                                  convertPressureToAltitude,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, PerformanceError, PropellantError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Sea level ambient, the reference the sea level thrust coefficient is quoted against.
SEA_LEVEL_PRESSURE = 101325.0    # [Pa]

# Altitudes the performance sweep is reported at. The set spans the regime where ambient pressure
# actually matters: above roughly 30 km the pressure term has fallen far enough that the engine is
# effectively at its vacuum performance, and reporting further points says nothing.
REPORTING_ALTITUDES = [0.0, 5000.0, 10000.0, 20000.0, 30000.0, 50000.0]    # [m]

# ------------------------------------------------------------------------------------------------ #
# -- EnginePerformance -- #
# ------------------------------------------------------------------------------------------------ #

class EnginePerformance:

    '''

    Ideal and delivered performance for a bipropellant engine at a given chamber pressure and
    expansion.

    '''

    def __init__(self):

        self.combination              = ''
        self.chamberPressure          = np.nan
        self.areaRatio                = np.nan
        self.ambientPressure          = np.nan
        self.cstarEfficiency          = np.nan
        self.thrustCoefficientEfficiency = np.nan

        self.properties = {}
        self.findings   = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `combination` names an entry in PROPELLANT_COMBINATIONS, `chamberPressure` is in Pa and
        `areaRatio` is the exit over throat area.

        The two efficiencies default to what a well developed engine achieves. They are separate
        inputs on purpose: an engine programme measures them separately and improves them by
        entirely different means.

        '''

        requiredParams = {'combination':     str,
                          'chamberPressure': (int, float),
                          'areaRatio':       (int, float)}

        optionalParams = {'ambientPressure':              (int, float),
                          'cstarEfficiency':              (int, float),
                          'thrustCoefficientEfficiency':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise PropellantError(
                f'Unknown propellant combination \'{self.combination}\'. '
                f'Known: {sorted(PROPELLANT_COMBINATIONS)}.',
                context = createErrorContext(component = 'EnginePerformance'))

        self.properties = dict(PROPELLANT_COMBINATIONS[self.combination])

        if not np.isfinite(self.ambientPressure):
            self.ambientPressure = SEA_LEVEL_PRESSURE

        if not np.isfinite(self.cstarEfficiency):
            self.cstarEfficiency = TYPICAL_CSTAR_EFFICIENCY

        if not np.isfinite(self.thrustCoefficientEfficiency):
            self.thrustCoefficientEfficiency = TYPICAL_THRUST_COEFFICIENT_EFFICIENCY

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateCharacteristicVelocity(self) -> dict:

        '''

        Ideal and delivered characteristic velocity.

        c* is measured, not inferred: `c* = Pc At / mdot`, and every term on the right is
        instrumented on a test stand. That is what makes it the diagnostic. Specific impulse
        requires a thrust measurement and a nozzle that is behaving, and it confounds the two halves
        of the problem.

        '''

        self.findings = []

        ideal     = self.properties['referenceCstar']
        delivered = ideal * self.cstarEfficiency

        self.findings.append(
            f'Characteristic velocity {delivered:.1f} m/s delivered against {ideal:.0f} m/s ideal, '
            f'at {self.cstarEfficiency:.1%} combustion efficiency.')

        self.findings.append(
            'c* is measurable directly from chamber pressure, throat area and mass flow, with no '
            'thrust measurement and no dependence on the nozzle. That is what makes it the first '
            'number to look at when an engine underperforms.')

        if self.chamberPressure > 2.0 * self.properties['referencePressure']:
            self.findings.append(
                f'The chamber pressure is more than twice the {self.properties["referencePressure"] / 1.0e6:.1f} '
                f'MPa the tabulated c* was taken at. c* rises slowly with chamber pressure through '
                f'reduced dissociation, so this is conservative, and CEA at the actual pressure is '
                f'the fix.')

        return {'ideal':      ideal,
                'delivered':  delivered,
                'efficiency': self.cstarEfficiency,
                'findings':   self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateThrustCoefficient(self, ambientPressure: float = None) -> dict:

        '''

        Thrust coefficient at an ambient pressure, split into its momentum and pressure terms.

            Cf = Gamma sqrt( 2 gamma / (gamma - 1) (1 - (Pe/Pc)^((gamma-1)/gamma)) )
                 + eps (Pe - Pa) / Pc

        The second term is the one that carries all the altitude dependence, and it is the reason a
        single engine has two thrust numbers.

        '''

        gamma   = self.properties['gamma']
        ambient = self.ambientPressure if ambientPressure is None else float(ambientPressure)

        pressureRatio = pressureRatioFromAreaRatio(gamma, self.areaRatio)
        exitPressure  = pressureRatio * self.chamberPressure

        momentum = (vandenkerckhove(gamma)
                    * np.sqrt(2.0 * gamma / (gamma - 1.0)
                              * (1.0 - pressureRatio ** ((gamma - 1.0) / gamma))))

        pressureTerm = self.areaRatio * (exitPressure - ambient) / self.chamberPressure

        ideal     = momentum + pressureTerm
        delivered = ideal * self.thrustCoefficientEfficiency

        separated = exitPressure < SUMMERFIELD_SEPARATION_RATIO * ambient

        return {'ideal':          ideal,
                'delivered':      delivered,
                'momentumTerm':   momentum,
                'pressureTerm':   pressureTerm,
                'exitPressure':   exitPressure,
                'ambientPressure': ambient,
                'separated':      separated,
                'efficiency':     self.thrustCoefficientEfficiency}

    # -------------------------------------------------------------------------------------------- #

    def calculateSpecificImpulse(self, ambientPressure: float = None) -> dict:

        '''

        Specific impulse, and the two efficiencies that produced it.

        The delivered value is the product of both efficiencies, which is why an Isp efficiency
        quoted on its own is nearly useless: 0.94 is the same number whether it came from a poor
        injector and a good nozzle or the reverse, and the two have nothing in common.

        '''

        self.findings = []

        cstar             = self.calculateCharacteristicVelocity()
        thrustCoefficient = self.calculateThrustCoefficient(ambientPressure)

        ideal     = cstar['ideal'] * thrustCoefficient['ideal'] / GRAVITY
        delivered = cstar['delivered'] * thrustCoefficient['delivered'] / GRAVITY

        combined = self.cstarEfficiency * self.thrustCoefficientEfficiency

        self.findings = []

        self.findings.append(
            f'Specific impulse {delivered:.1f} s delivered against {ideal:.1f} s ideal, at '
            f'{combined:.1%} overall.')

        self.findings.append(
            f'That {combined:.1%} is {self.cstarEfficiency:.1%} combustion times '
            f'{self.thrustCoefficientEfficiency:.1%} nozzle. The same overall figure would come '
            f'from {self.thrustCoefficientEfficiency:.1%} combustion and '
            f'{self.cstarEfficiency:.1%} nozzle, which is a different engine with a different fix.')

        if thrustCoefficient['separated']:
            self.findings.append(
                f'The exit pressure of {thrustCoefficient["exitPressure"] / 1000.0:.1f} kPa is '
                f'below {SUMMERFIELD_SEPARATION_RATIO:.0%} of the ambient '
                f'{thrustCoefficient["ambientPressure"] / 1000.0:.1f} kPa, so the flow separates '
                f'from the wall. The thrust coefficient above assumes it does not, and the real '
                f'engine both performs differently and sees a side load the calculation cannot see.')

        return {'ideal':               ideal,
                'delivered':           delivered,
                'combinedEfficiency':  combined,
                'characteristicVelocity': cstar,
                'thrustCoefficient':   thrustCoefficient,
                'findings':            self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateAltitudePerformance(self) -> dict:

        '''

        Thrust coefficient and specific impulse across altitude, and the optimum expansion altitude.

        A fixed nozzle is at its optimum at exactly one altitude and is losing performance at every
        other. Below it the nozzle is over-expanded and the exit pressure is pulling backwards;
        above it the nozzle is under-expanded and there is expansion left on the table. The
        over-expanded side is the dangerous one, because past the separation limit it stops being a
        performance question and becomes a structural one.

        '''

        self.findings = []

        gamma         = self.properties['gamma']
        pressureRatio = pressureRatioFromAreaRatio(gamma, self.areaRatio)
        exitPressure  = pressureRatio * self.chamberPressure

        byAltitude = {}

        for altitude in REPORTING_ALTITUDES:

            ambient = float(convertAltitudeToPressure(altitude))

            thrustCoefficient = self.calculateThrustCoefficient(ambient)
            specificImpulse   = (self.properties['referenceCstar'] * self.cstarEfficiency
                                 * thrustCoefficient['delivered'] / GRAVITY)

            byAltitude[altitude] = {'ambientPressure':  ambient,
                                    'thrustCoefficient': thrustCoefficient['delivered'],
                                    'specificImpulse':  specificImpulse,
                                    'separated':        thrustCoefficient['separated']}

        vacuum = self.calculateThrustCoefficient(0.0)
        vacuumImpulse = (self.properties['referenceCstar'] * self.cstarEfficiency
                         * vacuum['delivered'] / GRAVITY)

        seaLevel = byAltitude[0.0]

        # the altitude at which ambient equals exit pressure is where this nozzle is optimum
        optimumAltitude = self._altitudeForPressure(exitPressure)

        self.findings.append(
            f'Vacuum specific impulse {vacuumImpulse:.1f} s against sea level '
            f'{seaLevel["specificImpulse"]:.1f} s, a ratio of '
            f'{vacuumImpulse / seaLevel["specificImpulse"]:.3f}.')

        self.findings.append(
            f'The exit pressure is {exitPressure / 1000.0:.2f} kPa, so this nozzle is optimally '
            f'expanded at about {optimumAltitude / 1000.0:.1f} km. Below that it is over-expanded '
            f'and above it under-expanded.')

        separatedAltitudes = [altitude for altitude, entry in byAltitude.items()
                              if entry['separated']]

        if separatedAltitudes:
            self.findings.append(
                f'The flow separates at {sorted(separatedAltitudes)} m. Separation is not a '
                f'performance penalty that can be traded: it is unsteady, it produces side loads '
                f'on the nozzle and the gimbal, and it has destroyed hardware.')
        else:
            self.findings.append(
                'The flow stays attached at every altitude reported, so the over-expansion is a '
                'performance cost rather than a structural risk.')

        return {'byAltitude':      byAltitude,
                'vacuumImpulse':   vacuumImpulse,
                'seaLevelImpulse': seaLevel['specificImpulse'],
                'exitPressure':    exitPressure,
                'optimumAltitude': optimumAltitude,
                'findings':        self.findings}

    # -------------------------------------------------------------------------------------------- #

    def compareExpansion(self, areaRatios: list = None) -> dict:

        '''

        The area ratio trade at fixed chamber pressure, reported at sea level and in vacuum.

        This is the calculation that shows why a booster and an upper stage carry different nozzles
        on the same power head. Expanding further always helps in vacuum and always hurts at sea
        level, and the crossover is set by the mission rather than by the engine.

        '''

        candidates = areaRatios if areaRatios else [10.0, 20.0, 40.0, 80.0, 160.0]

        original = self.areaRatio
        results  = {}

        try:
            for ratio in candidates:

                self.areaRatio = float(ratio)

                seaLevel = self.calculateThrustCoefficient(SEA_LEVEL_PRESSURE)
                vacuum   = self.calculateThrustCoefficient(0.0)

                cstar = self.properties['referenceCstar'] * self.cstarEfficiency

                results[ratio] = {
                    'seaLevelImpulse':  cstar * seaLevel['delivered'] / GRAVITY,
                    'vacuumImpulse':    cstar * vacuum['delivered'] / GRAVITY,
                    'exitPressure':     seaLevel['exitPressure'],
                    'separatedAtSeaLevel': seaLevel['separated']}
        finally:
            self.areaRatio = original

        usable = [ratio for ratio in candidates if not results[ratio]['separatedAtSeaLevel']]

        self.findings = []

        bestVacuum = max(candidates, key = lambda ratio: results[ratio]['vacuumImpulse'])

        self.findings.append(
            f'Vacuum impulse rises monotonically with area ratio and is highest at '
            f'{bestVacuum:.0f}, so in vacuum the only limits are mass, length and what the nozzle '
            f'can be cooled to.')

        if usable:
            bestSeaLevel = max(usable, key = lambda ratio: results[ratio]['seaLevelImpulse'])
            self.findings.append(
                f'At sea level the best attached expansion of those tried is '
                f'{bestSeaLevel:.0f}, giving {results[bestSeaLevel]["seaLevelImpulse"]:.1f} s.')

        separated = [ratio for ratio in candidates if results[ratio]['separatedAtSeaLevel']]
        if separated:
            self.findings.append(
                f'Area ratios {separated} separate at sea level. A vacuum optimised nozzle cannot '
                f'simply be lit on the pad, which is the entire reason upper stage engines are '
                f'altitude started or tested in a vacuum facility.')

        return {'areaRatios': results,
                'usableAtSeaLevel': usable,
                'findings':   self.findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full performance report.
        '''

        cstar     = self.calculateCharacteristicVelocity()
        impulse   = self.calculateSpecificImpulse()
        altitude  = self.calculateAltitudePerformance()
        expansion = self.compareExpansion()

        thrustCoefficient = impulse['thrustCoefficient']

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ENGINE PERFORMANCE: {self.combination}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Chamber pressure',        f'{self.chamberPressure / 1.0e6:.2f}',        'MPa'],
             ['Area ratio',              f'{self.areaRatio:.1f}',                      ''],
             ['Characteristic velocity', f'{cstar["delivered"]:.1f}',                  'm/s'],
             ['Thrust coefficient',      f'{thrustCoefficient["delivered"]:.4f}',      ''],
             ['  momentum term',         f'{thrustCoefficient["momentumTerm"]:.4f}',   ''],
             ['  pressure term',         f'{thrustCoefficient["pressureTerm"]:+.4f}',  ''],
             ['Specific impulse',        f'{impulse["delivered"]:.1f}',                's'],
             ['Vacuum specific impulse', f'{altitude["vacuumImpulse"]:.1f}',           's'],
             ['Optimum altitude',        f'{altitude["optimumAltitude"] / 1000.0:.1f}', 'km']],
            ['Quantity', 'Value', 'Unit'], title = 'Performance'))

        lines.append('')
        lines.append('  Across altitude:')
        lines.append('')
        lines.append(f'    {"altitude [km]":>14s} {"ambient [kPa]":>14s} {"Cf":>8s} '
                     f'{"Isp [s]":>9s}  separated')
        for value in REPORTING_ALTITUDES:
            entry = altitude['byAltitude'][value]
            lines.append(f'    {value / 1000.0:14.0f} {entry["ambientPressure"] / 1000.0:14.3f} '
                         f'{entry["thrustCoefficient"]:8.4f} {entry["specificImpulse"]:9.1f}  '
                         f'{entry["separated"]}')

        lines.append('')
        lines.append('  Against expansion, at this chamber pressure:')
        lines.append('')
        lines.append(f'    {"area ratio":>11s} {"sea level [s]":>14s} {"vacuum [s]":>12s}  '
                     f'separated')
        for ratio, entry in expansion['areaRatios'].items():
            lines.append(f'    {ratio:11.0f} {entry["seaLevelImpulse"]:14.1f} '
                         f'{entry["vacuumImpulse"]:12.1f}  {entry["separatedAtSeaLevel"]}')

        lines.append('')
        for finding in (cstar['findings'] + impulse['findings']
                        + altitude['findings'] + expansion['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            path = os.path.join(outputDir,
                                f'performance_{self.combination.replace("/", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _altitudeForPressure(self, pressure: float) -> float:

        '''

        The altitude at which the standard atmosphere reaches a pressure.

        Used to report where a fixed nozzle is optimally expanded. The inversion is the shared
        US Standard Atmosphere 1976 routine rather than a search of its forward form, so the two
        directions cannot disagree.

        Clamped at both ends. Below sea level the answer is sea level, and above the top of the
        model a nozzle is optimally expanded in vacuum, where an altitude is not the useful way to
        say so.

        '''

        ceiling = 84852.0    # [m], the top of the 1976 model

        if pressure >= float(convertAltitudeToPressure(0.0)):
            return 0.0
        if pressure <= float(convertAltitudeToPressure(ceiling)):
            return ceiling

        return float(convertPressureToAltitude(pressure))

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.chamberPressure <= 0.0:
            raise InvalidInputError(
                f'The chamber pressure must be positive, got {self.chamberPressure}.',
                context = createErrorContext(component = 'EnginePerformance'))

        if self.areaRatio <= 1.0:
            raise InvalidInputError(
                f'The area ratio must exceed one, got {self.areaRatio}. An area ratio of one is '
                f'the throat.',
                context = createErrorContext(component = 'EnginePerformance'))

        if self.ambientPressure < 0.0:
            raise InvalidInputError(
                f'The ambient pressure cannot be negative, got {self.ambientPressure}. Vacuum is '
                f'zero.',
                context = createErrorContext(component = 'EnginePerformance'))

        for name, value in (('c* efficiency', self.cstarEfficiency),
                            ('thrust coefficient efficiency',
                             self.thrustCoefficientEfficiency)):
            if not 0.0 < value <= 1.0:
                raise PerformanceError(
                    f'The {name} must lie in (0, 1], got {value}. An efficiency above one is an '
                    f'engine producing more than its propellant contains.',
                    context = createErrorContext(component = 'EnginePerformance'))

        if self.chamberPressure <= self.ambientPressure:
            raise PerformanceError(
                f'The chamber pressure {self.chamberPressure / 1000.0:.1f} kPa is at or below the '
                f'ambient {self.ambientPressure / 1000.0:.1f} kPa, so the nozzle is not choked and '
                f'none of these relations apply.',
                context = createErrorContext(component = 'EnginePerformance'))
