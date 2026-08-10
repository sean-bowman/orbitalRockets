
# -- MechanismActuator -- #

'''

Torque and force margin to NASA-STD-5017B equation 4-1.

    margin = T_avail / (sum FSf Tf + sum FSv Tv + sum FSa Ta) - 1

**The requirement is a margin at or above zero, not one.** The reserve lives inside the safety
factors rather than on top of the result, and a search summary of this same standard reported the
threshold as 1.0. Reading the standard rather than a summary of it is the whole reason this class
carries the factors as data with the source attached.

Three margins, and they are different calculations rather than three views of one.

**Static margin** asks whether the mechanism can start moving. Static friction, no acceleration
term.

**Dynamic margin** asks whether it can achieve a required acceleration. The acceleration term is
included and the friction values are the ones appropriate to motion.

**Holding margin** asks whether it stays put against disturbances. `T_avail` is the intentional
holding torque only, and the standard is explicit that incidental sources such as joint friction,
harness bending and blanket rubbing are excluded from it because they are unreliable.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from mechanismUtils import (TORQUE_MARGIN_FACTORS, REQUIRED_TORQUE_MARGIN, torqueMargin,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, MarginError)
except ImportError:
    from .mechanismUtils import (TORQUE_MARGIN_FACTORS, REQUIRED_TORQUE_MARGIN, torqueMargin,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, MarginError)

# ------------------------------------------------------------------------------------------------ #
# -- MechanismActuator -- #
# ------------------------------------------------------------------------------------------------ #

class MechanismActuator:

    '''

    Static, dynamic and holding torque margin, with the standard's factors and its threshold.

    '''

    def __init__(self):

        self.availableTorque = np.nan
        self.fixedTorques    = []
        self.variableTorques = []
        self.accelerationTorque = np.nan
        self.dataSource      = ''
        self.gearRatio       = np.nan
        self.gearEfficiency  = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `fixedTorques` are the resisting torques not strongly influenced by environment or cycles:
        bearing drag, return springs, unbalanced pressure. `variableTorques` are the ones that do
        change: friction, viscous drag, harness torque from flexing and set.

        Getting an item into the wrong list changes its safety factor by a factor of two, so the
        split is the input most worth checking.

        '''

        requiredParams = {'availableTorque': (int, float),
                          'fixedTorques':    list,
                          'variableTorques': list}

        optionalParams = {'accelerationTorque': (int, float),
                          'dataSource':         str,
                          'gearRatio':          (int, float),
                          'gearEfficiency':     (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.dataSource:
            self.dataSource = 'theory or analysis'

        if not np.isfinite(self.gearEfficiency):
            self.gearEfficiency = 0.85

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def staticMargin(self) -> dict:

        '''

        Whether the mechanism can start moving. The standard excludes the acceleration term and its
        factor from the static calculation.

        '''

        return torqueMargin(self.availableTorque, self.fixedTorques, self.variableTorques, [],
                            source = self.dataSource)

    def dynamicMargin(self) -> dict:

        '''

        Whether the mechanism can achieve a required acceleration. Only applicable where a minimum
        acceleration, time or velocity is actually required of it.

        '''

        if not np.isfinite(self.accelerationTorque):
            raise InvalidInputError(
                'A dynamic margin needs an acceleration torque. The standard applies this margin '
                'only to mechanisms required to provide a minimum acceleration, so if there is no '
                'such requirement there is no dynamic margin to compute.',
                context = createErrorContext(component = 'MechanismActuator'))

        return torqueMargin(self.availableTorque, self.fixedTorques, self.variableTorques,
                            [self.accelerationTorque], source = self.dataSource)

    def holdingMargin(self, disturbances: list, holdingTorque: float) -> dict:

        '''

        Whether the mechanism stays put against disturbances.

        Two things differ from the other margins and both are in the standard. `holdingTorque` is
        the **intentional** holding torque only, from brakes, springs, detents or a powered motor;
        incidental sources such as joint friction, harness bending and blanket rubbing are excluded
        because they are unreliable and uncharacterised. And the disturbing torques all go in the
        variable list regardless of how variable they actually are, because the holding torque
        itself carries the variability.

        '''

        if holdingTorque <= 0.0:
            raise InvalidInputError(
                f'The intentional holding torque must be positive, got {holdingTorque}. If the '
                f'only thing holding the mechanism is incidental friction, the standard says that '
                f'does not count and the answer is that there is no holding capability.',
                context = createErrorContext(component = 'MechanismActuator'))

        return torqueMargin(holdingTorque, [], disturbances, [], source = self.dataSource)

    # -------------------------------------------------------------------------------------------- #

    def checkMargins(self) -> dict:

        '''

        Both applicable margins against the standard's threshold, refused rather than reported when
        negative.

        '''

        findings = []

        static = self.staticMargin()

        results = {'static': static}

        findings.append(
            f'Static margin {static["margin"]:+.2f} at {self.dataSource} factors '
            f'(FSf {static["factors"]["fixed"]:.2f}, FSv {static["factors"]["variable"]:.2f}).')

        if np.isfinite(self.accelerationTorque):

            dynamic = self.dynamicMargin()

            results['dynamic'] = dynamic

            findings.append(f'Dynamic margin {dynamic["margin"]:+.2f}.')

        findings.append(
            f'The requirement is a margin at or above {REQUIRED_TORQUE_MARGIN:.0f}, because the '
            f'reserve is inside the factors rather than applied to the result.')

        worst = min(results, key = lambda name: results[name]['margin'])

        if results[worst]['margin'] < REQUIRED_TORQUE_MARGIN:
            raise MarginError(
                f'The {worst} torque margin is {results[worst]["margin"]:+.2f}, below the required '
                f'{REQUIRED_TORQUE_MARGIN:.0f}. The mechanism has {self.availableTorque:.2f} '
                f'available against {results[worst]["factoredResisting"]:.2f} factored resisting, '
                f'from {results[worst]["unfactoredResisting"]:.2f} unfactored. **A mechanism '
                f'operates once and a negative margin is not a degraded mechanism**, so this is '
                f'refused. Either the driving torque rises, the resisting torque falls, or the '
                f'factors are earned down by testing the flight article in its environment.',
                context = createErrorContext(component = 'MechanismActuator'))

        self.findings = findings

        return {'results':  results,
                'worst':    worst,
                'worstMargin': results[worst]['margin'],
                'passes':   True,
                'findings': findings}

    # -------------------------------------------------------------------------------------------- #

    def compareDataSources(self) -> dict:

        '''

        The same mechanism assessed at every level of test evidence.

        The result is the argument for testing. **The factors fall from 3.00 to 2.00 on variable
        torques as the evidence improves**, so the same hardware goes from failing to passing
        without a single design change. That is not the standard being lenient; it is uncertainty
        being retired by measurement.

        '''

        original = self.dataSource

        results = {}

        try:
            for source in TORQUE_MARGIN_FACTORS:

                if source == 'one spring out':
                    continue

                self.dataSource = source

                results[source] = self.staticMargin()

        finally:
            self.dataSource = original

        passing = [name for name, entry in results.items()
                   if entry['margin'] >= REQUIRED_TORQUE_MARGIN]

        return {'results':  results,
                'passing':  passing,
                'passesAtAnalysis': bool('theory or analysis' in passing)}

    # -------------------------------------------------------------------------------------------- #

    def checkGearedMargins(self) -> dict:

        '''

        Margin at both the input and the output of a torque multiplier, which the standard requires
        separately.

        The reason is worth knowing: a gearbox is not a hundred per cent efficient, and some
        resisting torques act before the multiplication rather than after. Basing a margin on the
        overall output alone can give a false impression of the true margin, which is the
        standard's own wording.

        '''

        if not np.isfinite(self.gearRatio):
            raise InvalidInputError(
                'A gear ratio is needed to check margins either side of a torque multiplier.',
                context = createErrorContext(component = 'MechanismActuator'))

        inputMargin = self.staticMargin()

        outputAvailable = self.availableTorque * self.gearRatio * self.gearEfficiency

        outputResisting = [torque * self.gearRatio for torque in self.fixedTorques]
        outputVariable  = [torque * self.gearRatio for torque in self.variableTorques]

        outputMargin = torqueMargin(outputAvailable, outputResisting, outputVariable, [],
                                    source = self.dataSource)

        return {'input':  inputMargin,
                'output': outputMargin,
                'gearRatio': self.gearRatio,
                'gearEfficiency': self.gearEfficiency,
                'outputIsWorse': bool(outputMargin['margin'] < inputMargin['margin'])}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full actuator margin report.
        '''

        static = self.staticMargin()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  MECHANISM ACTUATOR: margin to NASA-STD-5017B, {self.dataSource}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Available torque',    f'{self.availableTorque:.3f}',                   'N m'],
             ['Fixed resisting',     f'{sum(self.fixedTorques):.3f}',                 'N m'],
             ['Variable resisting',  f'{sum(self.variableTorques):.3f}',              'N m'],
             ['FSf',                 f'{static["factors"]["fixed"]:.2f}',             ''],
             ['FSv',                 f'{static["factors"]["variable"]:.2f}',          ''],
             ['Factored resisting',  f'{static["factoredResisting"]:.3f}',            'N m'],
             ['Static margin',       f'{static["margin"]:+.3f}',                      ''],
             ['Required',            f'{REQUIRED_TORQUE_MARGIN:.0f}',                 '']],
            ['Quantity', 'Value', 'Unit'], title = 'Static margin'))

        comparison = self.compareDataSources()

        lines.append('')
        lines.append(formatReportTable(
            [[name,
              f'{entry["factors"]["variable"]:.2f}',
              f'{entry["factors"]["fixed"]:.2f}',
              f'{entry["margin"]:+.3f}',
              'yes' if entry['margin'] >= REQUIRED_TORQUE_MARGIN else 'no']
             for name, entry in comparison['results'].items()],
            ['Data source', 'FSv', 'FSf', 'Margin', 'Passes'],
            title = 'The same hardware at every level of evidence'))

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'mechanism_actuator.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.availableTorque <= 0.0:
            raise InvalidInputError(
                f'The available torque must be positive, got {self.availableTorque}.',
                context = createErrorContext(component = 'MechanismActuator'))

        for name, values in (('fixed', self.fixedTorques), ('variable', self.variableTorques)):

            for value in values:
                if value < 0.0:
                    raise InvalidInputError(
                        f'A {name} resisting torque is negative, {value}. A torque that helps the '
                        f'mechanism belongs in the available torque rather than as a negative '
                        f'resistance, or the margin silently gains reserve it does not have.',
                        context = createErrorContext(component = 'MechanismActuator'))

        if not self.fixedTorques and not self.variableTorques:
            raise InvalidInputError(
                'A mechanism with no resisting torques at all has not been analysed rather than '
                'being infinitely good. The standard lists twenty conditions to account for, from '
                'material property variation to harness set to damper drag.',
                context = createErrorContext(component = 'MechanismActuator'))

        if self.dataSource not in TORQUE_MARGIN_FACTORS:
            raise InvalidInputError(
                f'Unknown torque data source \'{self.dataSource}\'. Known sources are '
                f'{sorted(TORQUE_MARGIN_FACTORS)}.',
                context = createErrorContext(component = 'MechanismActuator'))

        if np.isfinite(self.gearRatio) and self.gearRatio <= 0.0:
            raise InvalidInputError(
                f'The gear ratio must be positive, got {self.gearRatio}.',
                context = createErrorContext(component = 'MechanismActuator'))

        if not 0.0 < self.gearEfficiency <= 1.0:
            raise InvalidInputError(
                f'The gear efficiency must lie in (0, 1], got {self.gearEfficiency}.',
                context = createErrorContext(component = 'MechanismActuator'))
