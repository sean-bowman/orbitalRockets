
# -- ThermalControl Class Definition -- #

'''

Heater sizing, setpoint bands, duty cycle, and the hot and cold cases that bracket a design.

Thermal control is the business of keeping something inside a band, and the band is almost always
wider than people assume until they look it up. The design problem is that the hot case and the
cold case want opposite things: the hot case wants a large radiator and the cold case wants a small
one, and the heater is what buys the difference.

That trade is the whole subject:

    a larger radiator      lower hot case temperature, more heater power in the cold case
    a smaller radiator     less heater power, higher hot case temperature

**Heater power is a power budget item, not a thermal one.** A radiator oversized for the hot case
is paid for continuously by the electrical system in every cold case, for the life of the mission.
Thermal designs are frequently optimised without anyone costing that, and the electrical budget
absorbs it silently.

**The setpoint band and the survival band are different requirements.** Operational limits are
what the hardware needs to work; survival limits are what it needs to not be damaged while off.
Sizing heaters to the operational band when only survival is required is a common and expensive
error, because the survival band is usually much wider.

Duty cycle matters for reliability rather than for power. A thermostat cycling every few seconds
accumulates millions of cycles over a mission, and mechanical thermostats have a finite life
measured in cycles.

See Also:
---------
Radiator       : The area that the cold case heater power pays for
ThermalNetwork : Where the hot and cold case temperatures come from

Theory: docs/ThermalControlSystems.md

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
                              InvalidInputError, createErrorContext)
except ImportError:
    from .thermalUtils import (applyInputs, formatReportTable, STEFAN_BOLTZMANN,
                               InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Margin on sized heater power. Thermal models carry real uncertainty and a heater that is too
# small has no recovery, so the margin is generous.
HEATER_MARGIN_DEFAULT = 1.50    # [-]

# Thermostat deadband. Too narrow and it chatters, too wide and the hardware swings.
TYPICAL_DEADBAND = 5.0    # [K]

# A mechanical thermostat has a finite cycle life. Above this the design should use a solid state
# controller or a wider deadband.
THERMOSTAT_CYCLE_LIFE = 100000.0    # [-]

# Representative operational and survival bands, to make the point that they differ substantially.
TEMPERATURE_LIMITS = {
    'electronics':      {'operational': (263.15, 323.15), 'survival': (243.15, 343.15)},
    'battery':          {'operational': (273.15, 303.15), 'survival': (263.15, 318.15)},
    'propellant, N2H4': {'operational': (288.15, 313.15), 'survival': (280.15, 323.15)},
    'optics':           {'operational': (288.15, 298.15), 'survival': (263.15, 323.15)},
    'mechanism':        {'operational': (253.15, 333.15), 'survival': (233.15, 353.15)},
}

# ------------------------------------------------------------------------------------------------ #
# -- ThermalControl -- #
# ------------------------------------------------------------------------------------------------ #

class ThermalControl:

    '''

    Heater sizing and setpoint definition.

    Usage:
    ------
        control = ThermalControl()
        control.setInputs({'component': 'battery', 'coldCaseLoss': 12.0,
                           'hotCaseTemperature': 300.0, 'missionDuration': 3.15e7})
        result = control.sizeHeater()

    '''

    def __init__(self):

        # -- Component -- #

        self.component          = 'electronics'   # key into TEMPERATURE_LIMITS
        self.operationalLimits  = None    # [K], (low, high), overrides the table
        self.survivalLimits     = None    # [K], (low, high), overrides
        self.sizeToSurvival     = False   # [-], size heaters to survival rather than operational

        # -- Thermal Case -- #

        self.coldCaseLoss       = np.nan  # [W], net heat loss in the cold case with no heater
        self.hotCaseTemperature = np.nan  # [K], the equilibrium in the hot case
        self.internalDissipation = 0.0    # [W], the component's own power

        # -- Control -- #

        self.deadband           = TYPICAL_DEADBAND   # [K]
        self.heaterMargin       = HEATER_MARGIN_DEFAULT   # [-]
        self.thermalMass        = np.nan  # [J/K], for the duty cycle period

        # -- Mission -- #

        self.missionDuration    = np.nan  # [s]
        self.coldCaseFraction   = 0.5     # [-], of the mission spent in the cold case

        # -- Results -- #

        self.findings           = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: coldCaseLoss.

        '''

        requiredParams = {'coldCaseLoss': (int, float)}

        optionalParams = {'component':           str,
                          'operationalLimits':   (list, tuple),
                          'survivalLimits':      (list, tuple),
                          'sizeToSurvival':      bool,
                          'hotCaseTemperature':  (int, float),
                          'internalDissipation': (int, float),
                          'deadband':            (int, float),
                          'heaterMargin':        (int, float),
                          'thermalMass':         (int, float),
                          'missionDuration':     (int, float),
                          'coldCaseFraction':    (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.component not in TEMPERATURE_LIMITS:
            raise InvalidInputError(
                f'Unknown component \'{self.component}\'. Known: {sorted(TEMPERATURE_LIMITS)}.',
                context = createErrorContext(component = 'ThermalControl'))

        entry = TEMPERATURE_LIMITS[self.component]

        if self.operationalLimits is None:
            self.operationalLimits = entry['operational']
        if self.survivalLimits is None:
            self.survivalLimits = entry['survival']

        self.operationalLimits = tuple(float(value) for value in self.operationalLimits)
        self.survivalLimits    = tuple(float(value) for value in self.survivalLimits)

    # -------------------------------------------------------------------------------------------- #

    @property
    def governingLimits(self) -> tuple:

        '''
        The band the heater is sized against, operational unless survival was requested.
        '''

        return self.survivalLimits if self.sizeToSurvival else self.operationalLimits

    # -------------------------------------------------------------------------------------------- #

    def sizeHeater(self) -> dict:

        '''

        Heater power to hold the cold case at the lower setpoint.

        '''

        self._validateInputs()

        lower, upper = self.governingLimits

        required = max(self.coldCaseLoss - self.internalDissipation, 0.0)
        sized    = required * self.heaterMargin

        self.findings = []

        self.findings.append(
            f'Cold case loss {self.coldCaseLoss:.1f} W less {self.internalDissipation:.1f} W of '
            f'internal dissipation needs {required:.1f} W, sized to {sized:.1f} W with a '
            f'{self.heaterMargin:.2f} margin.')

        # the operational against survival point, which is where the money is
        survivalRequired = required * ((self.survivalLimits[0] - 4.0)
                                       / max(self.operationalLimits[0] - 4.0, 1.0))
        if not self.sizeToSurvival:
            operationalBand = self.operationalLimits[1] - self.operationalLimits[0]
            survivalBand    = self.survivalLimits[1] - self.survivalLimits[0]
            self.findings.append(
                f'Sized to the operational band of {operationalBand:.0f} K. The survival band is '
                f'{survivalBand:.0f} K, and if the hardware only has to survive rather than '
                f'operate while cold, sizing to it would need meaningfully less power. That is a '
                f'requirements question, not a thermal one.')

        return {'requiredPower':     required,
                'sizedPower':        sized,
                'margin':            self.heaterMargin,
                'lowerSetpoint':     lower,
                'upperSetpoint':     lower + self.deadband,
                'governingBand':     'survival' if self.sizeToSurvival else 'operational',
                'operationalLimits': self.operationalLimits,
                'survivalLimits':    self.survivalLimits,
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateDutyCycle(self) -> dict:

        '''

        Duty cycle and cycling period, and the thermostat cycle count over the mission.

        Duty cycle matters for reliability rather than for power. A thermostat cycling every few
        seconds accumulates millions of cycles, and a mechanical thermostat has a finite life.

        '''

        self._validateInputs()

        sizing = self.sizeHeater()

        if sizing['sizedPower'] <= 0.0:
            return {'dutyCycle': 0.0, 'note': 'No heater required in the cold case.',
                    'findings': ['The cold case is self-sustaining, so no heater is needed.']}

        duty = min(sizing['requiredPower'] / sizing['sizedPower'], 1.0)

        result = {'dutyCycle':      duty,
                  'requiredPower':  sizing['requiredPower'],
                  'sizedPower':     sizing['sizedPower'],
                  'findings':       []}

        if np.isfinite(self.thermalMass) and self.thermalMass > 0.0:

            # time to traverse the deadband heating, and cooling
            heatingRate = (sizing['sizedPower'] - sizing['requiredPower']) / self.thermalMass
            coolingRate = sizing['requiredPower'] / self.thermalMass

            if heatingRate > 0.0 and coolingRate > 0.0:
                period = self.deadband / heatingRate + self.deadband / coolingRate
                result['period'] = period

                if np.isfinite(self.missionDuration):
                    cycles = self.missionDuration * self.coldCaseFraction / period
                    result['cycles'] = cycles

                    result['findings'].append(
                        f'A {period:.1f} s cycle over the mission gives {cycles:.0f} thermostat '
                        f'cycles.')

                    if cycles > THERMOSTAT_CYCLE_LIFE:
                        result['findings'].append(
                            f'{cycles:.0f} cycles exceeds a typical mechanical thermostat life of '
                            f'{THERMOSTAT_CYCLE_LIFE:.0f}. Widen the deadband, which lengthens the '
                            f'period, or use a solid state controller.')

        if np.isfinite(self.missionDuration):
            energy = sizing['requiredPower'] * self.missionDuration * self.coldCaseFraction
            result['energy'] = energy
            result['findings'].append(
                f'{energy / 3.6e6:.1f} kWh of heater energy over the mission. That is an '
                f'electrical power budget item bought by the thermal design, and it is frequently '
                f'not costed against the radiator that caused it.')

        return result

    # -------------------------------------------------------------------------------------------- #

    def checkHotCase(self) -> dict:

        '''

        Whether the hot case sits inside the band without active cooling.

        '''

        self._validateInputs()

        if not np.isfinite(self.hotCaseTemperature):
            raise InvalidInputError('A hot case check needs hotCaseTemperature.',
                                    context = createErrorContext(component = 'ThermalControl'))

        lower, upper = self.governingLimits

        margin = upper - self.hotCaseTemperature
        acceptable = self.hotCaseTemperature <= upper

        findings = []
        if not acceptable:
            findings.append(
                f'The hot case at {self.hotCaseTemperature:.1f} K exceeds the {upper:.1f} K limit '
                f'by {-margin:.1f} K. A larger radiator fixes it and costs heater power in every '
                f'cold case, for the life of the mission.')
        else:
            findings.append(
                f'The hot case at {self.hotCaseTemperature:.1f} K sits {margin:.1f} K inside the '
                f'{upper:.1f} K limit.')

        return {'hotCaseTemperature': self.hotCaseTemperature,
                'upperLimit':         upper,
                'margin':             margin,
                'acceptable':         bool(acceptable),
                'findings':           findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the thermal control design.
        '''

        sizing = self.sizeHeater()
        duty   = self.calculateDutyCycle()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  THERMAL CONTROL: {self.component}, '
                     f'{sizing["governingBand"]} band')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Operational band',
                 f'{self.operationalLimits[0]:.1f} to {self.operationalLimits[1]:.1f}', 'K'],
                ['Survival band',
                 f'{self.survivalLimits[0]:.1f} to {self.survivalLimits[1]:.1f}', 'K'],
                ['Required power',  f'{sizing["requiredPower"]:.1f}', 'W'],
                ['Sized power',     f'{sizing["sizedPower"]:.1f}', 'W'],
                ['Duty cycle',      f'{duty["dutyCycle"] * 100.0:.1f}', '%'],
                ['Deadband',        f'{self.deadband:.1f}', 'K']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Heater'))

        allFindings = sizing['findings'] + duty.get('findings', [])
        if allFindings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in allFindings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'thermalControl.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the case definition and limits are physical.
        '''

        context = createErrorContext(component = 'ThermalControl')

        if not np.isfinite(self.coldCaseLoss):
            raise InvalidInputError('Cold case loss must be provided.', context = context)

        if self.coldCaseLoss < 0.0:
            raise InvalidInputError(
                'Cold case loss is a heat loss and is positive. A negative value means the '
                'component is gaining heat, which is a hot case.', context = context)

        for name, limits in (('operational', self.operationalLimits),
                             ('survival', self.survivalLimits)):
            if limits[0] >= limits[1]:
                raise InvalidInputError(
                    f'The {name} band is inverted: {limits[0]:.1f} to {limits[1]:.1f} K.',
                    context = context)

        if (self.survivalLimits[0] > self.operationalLimits[0]
                or self.survivalLimits[1] < self.operationalLimits[1]):
            raise InvalidInputError(
                f'The survival band {self.survivalLimits} does not contain the operational band '
                f'{self.operationalLimits}. Survival limits are always the wider pair.',
                context = context)

        if self.deadband <= 0.0:
            raise InvalidInputError('Deadband must be positive.', context = context)

        if self.heaterMargin < 1.0:
            raise InvalidInputError(
                f'Heater margin must be at least 1.0, got {self.heaterMargin}.', context = context)

        if not 0.0 <= self.coldCaseFraction <= 1.0:
            raise InvalidInputError(
                f'Cold case fraction must be in [0, 1], got {self.coldCaseFraction}.',
                context = context)
