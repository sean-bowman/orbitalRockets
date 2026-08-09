
# -- PowerBalance -- #

'''

Turbine power equals pump power, and what makes a cycle close or not.

This is the equation the whole sub-domain turns on, and it is trivial to write:

    P_turbine = P_pumps

What makes it interesting is that each side is constrained by something different, and the
constraints belong to different sub-domains. The pump side is set by the pressure ladder, which is
a cycle decision. The turbine side is set by the flow available, the inlet temperature the blades
tolerate, and the pressure ratio the cycle allows, and that last one is where cycles diverge
sharply.

An open cycle turbine has a pressure ratio of twenty because it exhausts to ambient. A closed cycle
turbine has a pressure ratio near one and a half because its exhaust has to enter the main injector
at above chamber pressure. **The same turbine power therefore needs an order more flow on a closed
cycle**, which is why a staged combustion preburner passes most of one propellant and a gas
generator passes three per cent of the total.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from cycleUtils import (CYCLE_TURBINE_TEMPERATURE, cycleDefinition, pressureLadder,
                            applyInputs, formatReportTable, createErrorContext,
                            InvalidInputError, CycleError)
except ImportError:
    from .cycleUtils import (CYCLE_TURBINE_TEMPERATURE, cycleDefinition, pressureLadder,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, CycleError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Driving gas properties. A fuel rich preburner or gas generator exhaust is mostly hydrogen and
# light hydrocarbons, so its specific heat is high and its gamma is low.
DRIVE_GAS_SPECIFIC_HEAT = 2500.0    # [J/kg K]
DRIVE_GAS_GAMMA = 1.25    # [-]

# Turbine efficiency. Rocket turbines run well below their optimum blade speed ratio because the
# pump owns the shaft speed, so this is lower than industrial practice by a wide margin. See the
# turbomachinery sub-domain, which computes it properly from the blade speed ratio.
TYPICAL_TURBINE_EFFICIENCY = 0.55    # [-]

# Above this fraction of total propellant flow, a turbine drive is no longer a bleed. It is a
# preburner, the cycle has become staged combustion in all but name, and treating the flow as a
# small correction stops being defensible.
BLEED_FRACTION_LIMIT = 0.10    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- PowerBalance -- #
# ------------------------------------------------------------------------------------------------ #

class PowerBalance:

    '''

    Turbine and pump power matching, the driving flow it requires, and whether the cycle closes.

    '''

    def __init__(self):

        self.cycle            = ''
        self.chamberPressure  = np.nan
        self.totalFlow        = np.nan
        self.pumpPower        = np.nan
        self.turbineInletTemperature = np.nan
        self.turbineEfficiency = np.nan
        self.availableHeat    = np.nan

        self.definition = {}
        self.findings   = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `pumpPower` is the total shaft power both pumps require, which comes from the
        turbomachinery sub-domain.

        `availableHeat` applies only to expander cycles and is the heat the coolant picked up in
        the chamber jacket, which comes from combustionDevices. It is an input rather than
        computed here so this sub-domain does not acquire a second implementation of Bartz.

        '''

        requiredParams = {'cycle':           str,
                          'chamberPressure': (int, float),
                          'totalFlow':       (int, float),
                          'pumpPower':       (int, float)}

        optionalParams = {'turbineInletTemperature': (int, float),
                          'turbineEfficiency':       (int, float),
                          'availableHeat':           (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self.definition = cycleDefinition(self.cycle)

        if not np.isfinite(self.turbineInletTemperature):
            self.turbineInletTemperature = CYCLE_TURBINE_TEMPERATURE.get(self.cycle, 900.0)

        if not np.isfinite(self.turbineEfficiency):
            self.turbineEfficiency = TYPICAL_TURBINE_EFFICIENCY

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def specificWork(self) -> dict:

        '''

        The work a kilogram of driving gas can deliver, which is where the cycles part company.

            w = eta cp T_in (1 - PR^(-(gamma-1)/gamma))

        The pressure ratio term is the whole story. At a ratio of 20 the bracket is 0.55; at 1.5 it
        is 0.076. **The same gas at the same temperature delivers seven times less work on a closed
        cycle**, because its exhaust has to be handed to the main injector rather than to the
        atmosphere.

        '''

        ladder = pressureLadder(self.chamberPressure, self.cycle)

        if not self.definition['hasTurbomachinery']:
            raise CycleError(
                f'{self.cycle} has no turbomachinery, so there is no power balance to compute.',
                context = createErrorContext(component = 'PowerBalance'))

        ratio = self.definition['turbinePressureRatio']

        exponent = (DRIVE_GAS_GAMMA - 1.0) / DRIVE_GAS_GAMMA

        expansion = 1.0 - ratio ** (-exponent)

        work = (self.turbineEfficiency * DRIVE_GAS_SPECIFIC_HEAT
                * self.turbineInletTemperature * expansion)

        return {'specificWork':   work,
                'expansionTerm':  expansion,
                'pressureRatio':  ratio,
                'inletTemperature': self.turbineInletTemperature,
                'turbineInlet':   ladder['turbineInlet'],
                'turbineExit':    ladder['turbineExit']}

    # -------------------------------------------------------------------------------------------- #

    def calculateDrivingFlow(self) -> dict:

        '''

        The driving gas flow the pump power demands, and what fraction of the engine it is.

        Above roughly ten per cent of total flow a turbine drive is no longer a bleed: it is a
        preburner, and the cycle has become staged combustion in all but name. The class says so
        rather than reporting a large fraction without comment.

        '''

        findings = []

        work = self.specificWork()

        flow     = self.pumpPower / work['specificWork']
        fraction = flow / self.totalFlow

        findings.append(
            f'{self.pumpPower / 1.0e6:.3f} MW at a specific work of '
            f'{work["specificWork"] / 1000.0:.0f} kJ/kg needs {flow:.2f} kg/s, which is '
            f'{fraction:.1%} of the engine flow.')

        findings.append(
            f'The turbine pressure ratio is {work["pressureRatio"]:.1f}, giving an expansion term '
            f'of {work["expansionTerm"]:.3f}. That term is where the cycles part company: an open '
            f'cycle reaches 0.55 and a closed cycle 0.076.')

        if fraction > BLEED_FRACTION_LIMIT:
            findings.append(
                f'{fraction:.0%} is past the point where this is a bleed. It is a preburner, and '
                f'the cycle is staged combustion whether it is called that or not. A closed cycle '
                f'is expected to be here; an open cycle at this fraction is throwing away far too '
                f'much impulse and something is wrong upstream.')

        if not self.definition['closed'] and fraction > 0.06:
            findings.append(
                f'An open cycle dumping {fraction:.1%} overboard is unusual. Either the pump power '
                f'is high, the turbine inlet temperature is low, or the cycle choice needs '
                f'revisiting.')

        self.findings = findings

        return {'drivingFlow':   flow,
                'flowFraction':  fraction,
                'specificWork':  work['specificWork'],
                'isBleed':       bool(fraction <= BLEED_FRACTION_LIMIT),
                'expansionTerm': work['expansionTerm'],
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def checkClosure(self) -> dict:

        '''

        Whether the cycle closes, which for most cycles is trivially yes and for an expander is the
        entire question.

        A gas generator or staged combustion cycle burns more propellant to make more turbine power,
        so it closes by definition until something else runs out. **An expander has no such lever.**
        Its turbine runs on the heat the chamber wall gave up, and that heat is fixed by the wall
        area and the flux. If it is not enough, the cycle does not close and no adjustment inside
        the cycle fixes it.

        '''

        findings = []

        driving = self.calculateDrivingFlow()

        if self.cycle not in ('expander', 'expander bleed'):

            findings.append(
                f'{self.cycle} closes by burning more propellant. The driving flow of '
                f'{driving["drivingFlow"]:.2f} kg/s is an output rather than a constraint, and the '
                f'cycle closes until a temperature or a pressure limit stops it.')

            self.findings = findings

            return {'closes':      True,
                    'limited':     False,
                    'drivingFlow': driving['drivingFlow'],
                    'findings':    findings}

        if not np.isfinite(self.availableHeat):
            raise CycleError(
                'An expander cycle closure check needs the heat available from the chamber jacket, '
                'which comes from combustionDevices. Without it there is nothing to balance '
                'against.',
                context = createErrorContext(component = 'PowerBalance'))

        # the turbine runs on what the coolant picked up, so the available power is bounded by it
        availablePower = self.availableHeat * self.turbineEfficiency * driving['expansionTerm']

        closes = availablePower >= self.pumpPower

        margin = availablePower / self.pumpPower

        findings.append(
            f'The jacket gives up {self.availableHeat / 1.0e6:.2f} MW. At '
            f'{self.turbineEfficiency:.0%} turbine efficiency and an expansion term of '
            f'{driving["expansionTerm"]:.3f}, that is {availablePower / 1.0e6:.3f} MW at the shaft '
            f'against {self.pumpPower / 1.0e6:.3f} MW required.')

        if closes:
            findings.append(
                f'The cycle closes with a margin of {margin:.2f}. An expander has no throttle on '
                f'its power source, so that margin is the whole design reserve.')
        else:
            findings.append(
                f'The cycle does not close: it is short by a factor of {1.0 / margin:.2f}. There '
                f'is no lever inside the cycle. The answers are a lower chamber pressure, a larger '
                f'chamber surface area, or a different cycle, and the first is the one that '
                f'usually decides it.')

        self.findings = findings

        return {'closes':         bool(closes),
                'limited':        True,
                'availablePower': availablePower,
                'requiredPower':  self.pumpPower,
                'margin':         margin,
                'availableHeat':  self.availableHeat,
                'drivingFlow':    driving['drivingFlow'],
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full power balance report.
        '''

        work    = self.specificWork()
        driving = self.calculateDrivingFlow()
        closure = self.checkClosure()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  POWER BALANCE: {self.cycle}')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Chamber pressure',   f'{self.chamberPressure / 1.0e6:.2f}',        'MPa'],
                ['Total flow',         f'{self.totalFlow:.2f}',                      'kg/s'],
                ['Pump power',         f'{self.pumpPower / 1.0e6:.3f}',              'MW'],
                ['Turbine inlet',      f'{self.turbineInletTemperature:.0f}',        'K'],
                ['Turbine pressure ratio', f'{work["pressureRatio"]:.2f}',           ''],
                ['Expansion term',     f'{work["expansionTerm"]:.3f}',               ''],
                ['Specific work',      f'{work["specificWork"] / 1000.0:.0f}',       'kJ/kg'],
                ['Driving flow',       f'{driving["drivingFlow"]:.2f}',              'kg/s'],
                ['Flow fraction',      f'{driving["flowFraction"]:.1%}',             ''],
                ['Is a bleed',         str(driving['isBleed']),                      ''],
                ['Closes',             str(closure['closes']),                       '']]

        if closure['limited']:
            rows.append(['Available power', f'{closure["availablePower"] / 1.0e6:.3f}', 'MW'])
            rows.append(['Closure margin',  f'{closure["margin"]:.2f}',                 ''])

        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'],
                                       title = 'Power balance'))

        lines.append('')
        for finding in (driving['findings'] + closure['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, f'balance_{self.cycle.replace(" ", "_")}.txt'),
                      'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('chamber pressure', self.chamberPressure),
                            ('total flow', self.totalFlow),
                            ('pump power', self.pumpPower),
                            ('turbine inlet temperature', self.turbineInletTemperature)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(component = 'PowerBalance'))

        if not 0.0 < self.turbineEfficiency <= 1.0:
            raise CycleError(
                f'The turbine efficiency must lie in (0, 1], got {self.turbineEfficiency}.',
                context = createErrorContext(component = 'PowerBalance'))
