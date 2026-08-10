
# -- SolenoidDrive -- #

'''

Driving a solenoid valve, and the four-to-one saving that most vehicles leave on the table.

A solenoid needs a large force to pull in against its spring and a much smaller one to stay closed
once the gap has shut, because magnetic force goes roughly as the inverse square of the air gap.
Drive it at pull-in current for the whole time it is open and three quarters of the energy becomes
heat in the coil.

**Peak and hold drive cuts the holding power by about a factor of four**, because power goes as the
square of current and a typical hold current is half of pull-in. On a vehicle with valves open for
minutes rather than milliseconds that is the difference between a heater-sized load and a
negligible one.

It also cuts the coil temperature rise, which matters for a second reason: **coil resistance rises
with temperature, so a hot coil pulls less current and produces less force.** A solenoid that
works cold and marginally at temperature is the classic version of this failure, and it is why the
hot case is the design case.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from powerUtils import (COPPER_TEMPERATURE_COEFFICIENT, REFERENCE_TEMPERATURE,
                            applyInputs, formatReportTable, createErrorContext,
                            InvalidInputError, ElectricalPowerError)
except ImportError:
    from .powerUtils import (COPPER_TEMPERATURE_COEFFICIENT, REFERENCE_TEMPERATURE,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, ElectricalPowerError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Hold current as a fraction of pull-in, for a solenoid whose gap has closed. Representative and
# registered as unvalidated: the real value comes from the valve's own force curve.
DEFAULT_HOLD_FRACTION = 0.50    # [-]

# Time constants as a multiple of L over R at which the current is treated as established.
CURRENT_ESTABLISHED = 3.0    # [-]

# Flyback clamp voltage above the supply, for a diode-plus-zener suppression network. The higher
# the clamp, the faster the valve closes and the more the switching device has to withstand.
DEFAULT_CLAMP_VOLTAGE = 50.0    # [V]

# ------------------------------------------------------------------------------------------------ #
# -- SolenoidDrive -- #
# ------------------------------------------------------------------------------------------------ #

class SolenoidDrive:

    '''

    Inrush, hold, coil heating and flyback for a solenoid valve driver.

    '''

    def __init__(self):

        self.busVoltage       = np.nan
        self.coilResistance   = np.nan
        self.coilInductance   = np.nan
        self.holdFraction     = np.nan
        self.openDuration     = np.nan
        self.coilTemperature  = np.nan
        self.clampVoltage     = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `coilResistance` is quoted at 20 C, and the class applies the copper temperature
        coefficient to get the resistance at `coilTemperature`.

        `openDuration` is how long the valve is held open, which is what turns a power into an
        energy.

        '''

        requiredParams = {'busVoltage':     (int, float),
                          'coilResistance': (int, float)}

        optionalParams = {'coilInductance':  (int, float),
                          'holdFraction':    (int, float),
                          'openDuration':    (int, float),
                          'coilTemperature': (int, float),
                          'clampVoltage':    (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.holdFraction):
            self.holdFraction = DEFAULT_HOLD_FRACTION

        if not np.isfinite(self.coilTemperature):
            self.coilTemperature = REFERENCE_TEMPERATURE

        if not np.isfinite(self.clampVoltage):
            self.clampVoltage = DEFAULT_CLAMP_VOLTAGE

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def hotResistance(self) -> float:

        '''

        Coil resistance at temperature.

        Copper gains about 0.4 per cent per kelvin, so a coil at 100 C has 31 per cent more
        resistance than at 20, pulls 24 per cent less current, and makes about 42 per cent less
        force. **That is the whole hot-solenoid failure mode in one line.**

        '''

        return self.coilResistance * (1.0 + COPPER_TEMPERATURE_COEFFICIENT
                                      * (self.coilTemperature - REFERENCE_TEMPERATURE))

    # -------------------------------------------------------------------------------------------- #

    def calculateDrive(self) -> dict:

        '''

        Pull-in and hold currents and powers, hot and cold.

        '''

        cold = self.coilResistance
        hot  = self.hotResistance()

        pullInCold = self.busVoltage / cold
        pullInHot  = self.busVoltage / hot

        holdCurrent = pullInHot * self.holdFraction

        continuousPower = pullInHot ** 2 * hot
        holdPower       = holdCurrent ** 2 * hot

        # magnetic force goes roughly as the square of current
        forceRatio = (pullInHot / pullInCold) ** 2

        return {'coldResistance':  cold,
                'hotResistance':   hot,
                'resistanceRise':  hot / cold - 1.0,
                'pullInCold':      pullInCold,
                'pullInHot':       pullInHot,
                'currentLoss':     1.0 - pullInHot / pullInCold,
                'forceRatio':      forceRatio,
                'holdCurrent':     holdCurrent,
                'continuousPower': continuousPower,
                'holdPower':       holdPower,
                'powerSaving':     1.0 - holdPower / continuousPower}

    # -------------------------------------------------------------------------------------------- #

    def calculateInrush(self) -> dict:

        '''

        How long the current takes to establish, from the coil time constant.

        The inductance matters for two reasons. It sets how quickly the valve actually opens, which
        is a sequencing question. And it stores energy that has to go somewhere when the drive is
        removed, which is the flyback problem below.

        '''

        if not np.isfinite(self.coilInductance):
            raise InvalidInputError(
                'A coil inductance is needed for an inrush calculation. Without it the current is '
                'instantaneous, which is the assumption that hides both the opening delay and the '
                'flyback energy.',
                context = createErrorContext(component = 'SolenoidDrive'))

        hot = self.hotResistance()

        timeConstant = self.coilInductance / hot

        establishTime = CURRENT_ESTABLISHED * timeConstant

        storedEnergy = 0.5 * self.coilInductance * (self.busVoltage / hot) ** 2

        return {'timeConstant':   timeConstant,
                'establishTime':  establishTime,
                'storedEnergy':   storedEnergy}

    # -------------------------------------------------------------------------------------------- #

    def calculateFlyback(self) -> dict:

        '''

        What happens when the drive is removed, and why the suppression choice is a valve timing
        decision rather than an electrical one.

        The coil's stored energy has to be dissipated. A plain freewheeling diode clamps the
        voltage at about a volt, which is kind to the switch and slow: the current decays with the
        same time constant it built up with, and the valve stays open while it does.

        A diode plus zener clamps higher, dissipates the energy faster, and closes the valve
        sooner. **The clamp voltage sets the closing time**, and a designer choosing a suppression
        network on component stress alone has chosen a valve response time by accident.

        '''

        if not np.isfinite(self.coilInductance):
            raise InvalidInputError(
                'A coil inductance is needed for a flyback calculation.',
                context = createErrorContext(component = 'SolenoidDrive'))

        findings = []

        drive = self.calculateDrive()

        hot = drive['hotResistance']

        current = drive['holdCurrent']

        storedEnergy = 0.5 * self.coilInductance * current ** 2

        # decay through a plain diode, dominated by the coil resistance
        diodeTime = CURRENT_ESTABLISHED * self.coilInductance / hot

        # decay through a clamp, where the clamp voltage forces the current down linearly
        clampTime = self.coilInductance * current / self.clampVoltage

        findings.append(
            f'The coil holds {storedEnergy * 1000.0:.1f} mJ at {current:.2f} A, and it has to go '
            f'somewhere when the drive opens.')

        findings.append(
            f'A freewheeling diode alone takes {diodeTime * 1000.0:.1f} ms to decay; a '
            f'{self.clampVoltage:.0f} V clamp takes {clampTime * 1000.0:.2f} ms, a factor of '
            f'{diodeTime / clampTime:.0f}.')

        findings.append(
            '**The clamp voltage sets the valve closing time.** Choosing a suppression network on '
            'component stress alone chooses a valve response time by accident, and on a sequenced '
            'system that is a sequencing decision made in the wrong meeting.')

        self.findings = findings

        return {'storedEnergy':  storedEnergy,
                'diodeTime':     diodeTime,
                'clampTime':     clampTime,
                'clampVoltage':  self.clampVoltage,
                'speedFactor':   diodeTime / clampTime,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def compareDriveStrategies(self) -> dict:

        '''

        Continuous against peak and hold, in power and in energy over the open duration.

        This is the four-to-one saving, and it is the clearest case in this domain of a decision
        that is cheap in hardware and large in consequence.

        '''

        if not np.isfinite(self.openDuration):
            raise InvalidInputError(
                'An open duration is needed to compare drive strategies, because the saving is in '
                'energy and a power alone does not have one.',
                context = createErrorContext(component = 'SolenoidDrive'))

        findings = []

        drive = self.calculateDrive()

        continuousEnergy = drive['continuousPower'] * self.openDuration
        holdEnergy       = drive['holdPower'] * self.openDuration

        saving = continuousEnergy - holdEnergy

        findings.append(
            f'Continuous drive takes {drive["continuousPower"]:.1f} W; peak and hold at '
            f'{self.holdFraction:.0%} of pull-in takes {drive["holdPower"]:.1f} W.')

        findings.append(
            f'That is a {drive["powerSaving"]:.0%} saving, because power goes as the square of '
            f'current and the current has halved.')

        findings.append(
            f'Over {self.openDuration:.0f} s open it is {saving / 3600.0:.2f} W h per valve '
            f'actuation, and the same saving in coil heating.')

        self.findings = findings

        return {'continuousPower':  drive['continuousPower'],
                'holdPower':        drive['holdPower'],
                'continuousEnergy': continuousEnergy,
                'holdEnergy':       holdEnergy,
                'energySaved':      saving,
                'powerSaving':      drive['powerSaving'],
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full solenoid drive report.
        '''

        drive = self.calculateDrive()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  SOLENOID DRIVE: {self.coilResistance:.1f} ohm coil on a '
                     f'{self.busVoltage:.0f} V bus at {self.coilTemperature:.0f} C')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Coil resistance, 20 C',   f'{drive["coldResistance"]:.2f}',            'ohm'],
             ['Coil resistance, hot',    f'{drive["hotResistance"]:.2f}',             'ohm'],
             ['Resistance rise',         f'{drive["resistanceRise"]:.1%}',            ''],
             ['Pull-in current, cold',   f'{drive["pullInCold"]:.3f}',                'A'],
             ['Pull-in current, hot',    f'{drive["pullInHot"]:.3f}',                 'A'],
             ['Current lost to heat',    f'{drive["currentLoss"]:.1%}',               ''],
             ['Force ratio, hot to cold', f'{drive["forceRatio"]:.2f}',               ''],
             ['Hold current',            f'{drive["holdCurrent"]:.3f}',               'A'],
             ['Continuous power',        f'{drive["continuousPower"]:.2f}',           'W'],
             ['Hold power',              f'{drive["holdPower"]:.2f}',                 'W'],
             ['Power saving',            f'{drive["powerSaving"]:.0%}',               '']],
            ['Quantity', 'Value', 'Unit'], title = 'Drive'))

        lines.append('')
        lines.append(f'    - A coil at {self.coilTemperature:.0f} C has '
                     f'{drive["resistanceRise"]:.0%} more resistance than at 20, pulls '
                     f'{drive["currentLoss"]:.0%} less current, and makes about '
                     f'{1.0 - drive["forceRatio"]:.0%} less force. The hot case is the design case.')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'solenoid_drive.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('bus voltage',     self.busVoltage),
                            ('coil resistance', self.coilResistance)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'SolenoidDrive'))

        if not 0.0 < self.holdFraction <= 1.0:
            raise InvalidInputError(
                f'The hold fraction must lie in (0, 1], got {self.holdFraction}. At one there is '
                f'no peak and hold, which is a valid design and is what the comparison is against.',
                context = createErrorContext(component = 'SolenoidDrive'))

        if np.isfinite(self.coilInductance) and self.coilInductance <= 0.0:
            raise InvalidInputError(
                f'The coil inductance must be positive, got {self.coilInductance}.',
                context = createErrorContext(component = 'SolenoidDrive'))

        if np.isfinite(self.openDuration) and self.openDuration < 0.0:
            raise InvalidInputError(
                f'The open duration cannot be negative, got {self.openDuration}.',
                context = createErrorContext(component = 'SolenoidDrive'))

        if self.clampVoltage <= self.busVoltage:
            raise ElectricalPowerError(
                f'The flyback clamp is at {self.clampVoltage:.1f} V and the bus is at '
                f'{self.busVoltage:.1f} V. A clamp at or below the supply conducts continuously '
                f'while the valve is driven, which is a short across the drive rather than a '
                f'suppression network.',
                context = createErrorContext(component = 'SolenoidDrive'))
