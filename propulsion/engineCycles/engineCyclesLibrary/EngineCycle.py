
# -- EngineCycle -- #

'''

The pressure ladder, the discarded flow, and the specific impulse each cycle actually delivers.

A cycle is a decision about where the turbine exhaust goes, and every other difference between the
cycles follows from that one answer.

    open        the exhaust goes overboard at a fraction of main chamber impulse, and the pump
                only has to reach the chamber
    closed      the exhaust goes to the main injector, so nothing is lost, and the pump has to
                reach the turbine inlet instead

That is the whole trade. An open cycle throws away one to three per cent of its impulse and buys a
pump that runs a quarter above chamber pressure. A closed cycle throws away nothing and buys a pump
that runs at twice chamber pressure.

Everything else, the preburner, the interpropellant seal, the start sequence, the development cost,
is downstream of that single choice.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from cycleUtils import (ENGINE_CYCLES, PRESSURE_LADDER, DUMPED_EXHAUST_IMPULSE_FRACTION,
                            CYCLE_TURBINE_TEMPERATURE, cycleDefinition, pressureLadder,
                            applyInputs, formatReportTable, createErrorContext,
                            InvalidInputError, CycleError, PressureLadderError)
except ImportError:
    from .cycleUtils import (ENGINE_CYCLES, PRESSURE_LADDER, DUMPED_EXHAUST_IMPULSE_FRACTION,
                             CYCLE_TURBINE_TEMPERATURE, cycleDefinition, pressureLadder,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, CycleError, PressureLadderError)

# ------------------------------------------------------------------------------------------------ #
# -- EngineCycle -- #
# ------------------------------------------------------------------------------------------------ #

class EngineCycle:

    '''

    Pressure schedule, discarded flow fraction and delivered specific impulse for a named cycle.

    '''

    def __init__(self):

        self.cycle           = ''
        self.chamberPressure = np.nan
        self.idealImpulse    = np.nan
        self.turbineFlowFraction = np.nan

        self.definition = {}
        self.findings   = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `turbineFlowFraction` is the driving gas flow as a fraction of total propellant. On an open
        cycle it is the flow that gets thrown away, and it comes from the turbomachinery
        sub-domain. On a closed cycle it is not a loss and is carried only for reporting.

        '''

        requiredParams = {'cycle':           str,
                          'chamberPressure': (int, float)}

        optionalParams = {'idealImpulse':        (int, float),
                          'turbineFlowFraction': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self.definition = cycleDefinition(self.cycle)

        if not np.isfinite(self.turbineFlowFraction):
            self.turbineFlowFraction = 0.0 if not self.definition['hasTurbomachinery'] else 0.035

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculatePressureLadder(self) -> dict:

        '''

        The schedule from pump discharge down to the chamber, and the ratio that results.

        The ratio is the number to carry away. A gas generator pump runs about a quarter above
        chamber pressure; a staged combustion pump runs at roughly twice it. That factor is not a
        detail of implementation, it is the price of closing the cycle, and it is paid by the
        turbomachinery and then by the tank.

        '''

        findings = []

        ladder = pressureLadder(self.chamberPressure, self.cycle)

        findings.append(
            f'{self.cycle}: pump discharge {ladder["dischargePressure"] / 1.0e6:.1f} MPa for a '
            f'{self.chamberPressure / 1.0e6:.1f} MPa chamber, a ratio of '
            f'{ladder["dischargeRatio"]:.2f}.')

        if self.definition['hasTurbomachinery'] and self.definition['closed']:
            findings.append(
                f'The turbine exhausts into the main injector at '
                f'{ladder["turbineExit"] / 1.0e6:.1f} MPa, so its inlet has to be '
                f'{ladder["turbineInlet"] / 1.0e6:.1f} MPa and the pump has to reach above that. '
                f'A closed cycle pump works against its own turbine, not against the chamber.')
        elif self.definition['hasTurbomachinery']:
            findings.append(
                f'The turbine exhausts overboard, so it can take a pressure ratio of '
                f'{self.definition["turbinePressureRatio"]:.0f} and the pump only has to reach the '
                f'chamber. That is the whole reason an open cycle pump is easy.')
        else:
            findings.append(
                'No turbomachinery, so the tank is the pump and this discharge pressure is a tank '
                'pressure. See PressureFedSystems.')

        self.findings = findings

        return {**ladder, 'findings': findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateImpulseDelivered(self) -> dict:

        '''

        The specific impulse the cycle delivers against the ideal thrust chamber value.

        On a closed cycle these are the same number. On an open cycle the dumped flow produces
        roughly thirty per cent of main chamber impulse, so the engine average is

            Isp_engine = Isp_chamber (1 - f) + Isp_dumped f

        where `f` is the turbine flow fraction. That is the loss the propulsion hub library does
        not model, and it is why the F-1 disagrees with that library by eight per cent while RS-25
        agrees to two.

        '''

        findings = []

        if not np.isfinite(self.idealImpulse):
            raise CycleError(
                'No ideal specific impulse was supplied, so the delivered value cannot be '
                'computed. It comes from the propulsion hub EnginePerformance class.',
                context = createErrorContext(component = 'EngineCycle'))

        fraction = self.turbineFlowFraction

        if self.definition['closed']:

            delivered = self.idealImpulse
            penalty   = 0.0

            findings.append(
                f'{self.cycle} is closed, so every kilogram goes through the main chamber and the '
                f'{fraction:.1%} driving flow costs nothing in impulse.')

        else:

            dumped    = self.idealImpulse * DUMPED_EXHAUST_IMPULSE_FRACTION
            delivered = self.idealImpulse * (1.0 - fraction) + dumped * fraction
            penalty   = 1.0 - delivered / self.idealImpulse

            findings.append(
                f'{self.cycle} is open. {fraction:.1%} of the propellant leaves through the '
                f'turbine at {dumped:.0f} s against {self.idealImpulse:.0f} s in the chamber, so '
                f'the engine delivers {delivered:.1f} s, a {penalty:.2%} loss.')

            findings.append(
                'That loss is invisible to a thrust chamber calculation. It is the reason a '
                'published open cycle engine impulse cannot be compared directly against a chamber '
                'and nozzle model.')

        self.findings = findings

        return {'idealImpulse':     self.idealImpulse,
                'deliveredImpulse': delivered,
                'penalty':          penalty,
                'turbineFlowFraction': fraction,
                'closed':           self.definition['closed'],
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def compareCycles(self, chamberPressure: float = None) -> dict:

        '''

        Every cycle at the same chamber pressure, so the pressure ladder and the impulse penalty
        can be seen together.

        The comparison is the point of this class. Read either column alone and one cycle looks
        obviously right; read both and the trade appears.

        '''

        pressure = self.chamberPressure if chamberPressure is None else float(chamberPressure)

        results = {}

        for name in ENGINE_CYCLES:

            # a pressure fed cycle has no turbine, so it cannot be handed a turbine flow
            # fraction. The guard in _validateInputs is correct and the caller has to respect it.
            flow = (self.turbineFlowFraction
                    if ENGINE_CYCLES[name]['hasTurbomachinery'] else 0.0)

            candidate = EngineCycle()
            candidate.setInputs({'cycle':               name,
                                 'chamberPressure':     pressure,
                                 'idealImpulse':        self.idealImpulse,
                                 'turbineFlowFraction': flow})

            ladder = candidate.calculatePressureLadder()

            entry = {'dischargeRatio':   ladder['dischargeRatio'],
                     'dischargePressure': ladder['dischargePressure'],
                     'closed':           candidate.definition['closed'],
                     'turbomachinery':   candidate.definition['hasTurbomachinery'],
                     'note':             candidate.definition['note']}

            if np.isfinite(self.idealImpulse):
                impulse = candidate.calculateImpulseDelivered()
                entry['deliveredImpulse'] = impulse['deliveredImpulse']
                entry['penalty']          = impulse['penalty']

            results[name] = entry

        self.findings = [
            'A closed cycle loses no impulse and pays for it in pump discharge pressure. An open '
            'cycle loses one to three per cent and pays almost nothing. Neither column decides on '
            'its own.',
            'The pressure ratio is the honest measure of how hard a cycle is on its turbomachinery, '
            'and it is roughly a factor of one and a half between the open and closed families.']

        return {'cycles': results, 'chamberPressure': pressure, 'findings': self.findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full cycle report.
        '''

        ladder     = self.calculatePressureLadder()
        comparison = self.compareCycles()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ENGINE CYCLE: {self.cycle}')
        lines.append('=' * 96)
        lines.append('')
        lines.append(f'  {self.definition["note"]}')
        lines.append('')

        rows = [['Chamber pressure',  f'{self.chamberPressure / 1.0e6:.2f}',          'MPa'],
                ['Closed',            str(self.definition['closed']),                 ''],
                ['Turbomachinery',    str(self.definition['hasTurbomachinery']),      ''],
                ['Pump discharge',    f'{ladder["dischargePressure"] / 1.0e6:.2f}',   'MPa'],
                ['Discharge ratio',   f'{ladder["dischargeRatio"]:.2f}',              '']]

        if ladder['turbineInlet'] is not None:
            rows.append(['Turbine inlet', f'{ladder["turbineInlet"] / 1.0e6:.2f}', 'MPa'])
            rows.append(['Turbine exit',  f'{ladder["turbineExit"] / 1.0e6:.2f}',  'MPa'])

        if np.isfinite(self.idealImpulse):
            impulse = self.calculateImpulseDelivered()
            rows.append(['Ideal impulse',     f'{impulse["idealImpulse"]:.1f}',     's'])
            rows.append(['Delivered impulse', f'{impulse["deliveredImpulse"]:.1f}', 's'])
            rows.append(['Cycle penalty',     f'{impulse["penalty"]:.2%}',          ''])

        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Cycle'))

        lines.append('')
        lines.append('  Every cycle at this chamber pressure:')
        lines.append('')
        lines.append(f'    {"cycle":30s} {"discharge":>10s} {"ratio":>7s} {"Isp [s]":>9s} '
                     f'{"penalty":>9s}  closed')

        for name, entry in comparison['cycles'].items():
            marker = '  <-' if name == self.cycle else ''
            impulse = f'{entry.get("deliveredImpulse", float("nan")):9.1f}' \
                if 'deliveredImpulse' in entry else f'{"":>9s}'
            penalty = f'{entry.get("penalty", 0.0):9.2%}' if 'penalty' in entry else f'{"":>9s}'
            lines.append(f'    {name:30s} {entry["dischargePressure"] / 1.0e6:10.1f} '
                         f'{entry["dischargeRatio"]:7.2f} {impulse} {penalty}  '
                         f'{str(entry["closed"]):5s}{marker}')

        lines.append('')
        for finding in (ladder['findings'] + comparison['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, f'cycle_{self.cycle.replace(" ", "_")}.txt'),
                      'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.chamberPressure <= 0.0:
            raise InvalidInputError(
                f'The chamber pressure must be positive, got {self.chamberPressure}.',
                context = createErrorContext(component = 'EngineCycle'))

        if not 0.0 <= self.turbineFlowFraction < 1.0:
            raise CycleError(
                f'The turbine flow fraction must lie in [0, 1), got '
                f'{self.turbineFlowFraction}. A fraction of one is an engine whose entire '
                f'propellant flow drives the turbine and none of it reaches the chamber.',
                context = createErrorContext(component = 'EngineCycle'))

        if (not self.definition['hasTurbomachinery']) and self.turbineFlowFraction > 0.0:
            raise CycleError(
                f'{self.cycle} has no turbomachinery, so a turbine flow fraction of '
                f'{self.turbineFlowFraction} is not meaningful.',
                context = createErrorContext(component = 'EngineCycle'))
