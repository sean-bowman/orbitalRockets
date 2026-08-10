
# -- PowerBudget -- #

'''

Load rollup by mission phase, and the load that turns out to dominate a storable-propellant vehicle.

A power budget is bookkeeping, and it goes wrong in two specific ways.

**Peak power and energy are different budgets.** A load that draws 200 W for two seconds and one
that draws 5 W for four hours are the same line in a list and different problems: the first sizes
the bus and the wire, the second sizes the battery. Reporting one number for both is how a pack
gets sized on average power and fails on inrush.

**Duty cycle is where the optimism lives.** A heater at fifty per cent duty is an assumption about
a thermal environment, and it is usually the assumption nobody has checked. On a hydrazine vehicle
the heaters keeping propellant above its freezing point are the largest steady load, they run for
the whole mission, and their duty cycle depends on an orbit and an attitude rather than on
anything electrical.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from powerUtils import (applyInputs, formatReportTable, createErrorContext,
                            InvalidInputError, PowerBudgetError)
except ImportError:
    from .powerUtils import (applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, PowerBudgetError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Share of the combined variance at which a single load is called dominant.
DOMINANCE_THRESHOLD = 0.4    # [-]

# Distribution efficiency: what fraction of the energy leaving the battery reaches the loads, after
# harness losses, regulation and switching. Representative, and registered as unvalidated.
DISTRIBUTION_EFFICIENCY = 0.90    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- PowerBudget -- #
# ------------------------------------------------------------------------------------------------ #

class PowerBudget:

    '''

    Loads by phase, peak power and energy reported separately, and what dominates each.

    '''

    def __init__(self):

        self.loads   = []
        self.phases  = []
        self.efficiency = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `phases` is a list of dictionaries with a `name` and a `duration` in seconds.

        `loads` is a list with a `name`, a `power` in watts, and a `dutyCycle` dictionary mapping
        phase names to the fraction of that phase the load is active for. A load absent from a
        phase is off in it.

        '''

        requiredParams = {'loads':  list,
                          'phases': list}

        optionalParams = {'efficiency': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.efficiency):
            self.efficiency = DISTRIBUTION_EFFICIENCY

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def rollUp(self) -> dict:

        '''

        Energy and peak power by phase, and by load.

        Both are reported because they size different things and they are frequently dominated by
        different loads.

        '''

        byPhase = {}

        for phase in self.phases:

            energy = 0.0
            peak   = 0.0

            contributors = {}

            for load in self.loads:

                duty = load['dutyCycle'].get(phase['name'], 0.0)

                if duty <= 0.0:
                    continue

                loadEnergy = load['power'] * duty * phase['duration']

                energy += loadEnergy
                peak   += load['power'] if load.get('simultaneous', True) else 0.0

                contributors[load['name']] = {'energy': loadEnergy,
                                              'power':  load['power'],
                                              'duty':   duty}

            byPhase[phase['name']] = {'duration':     phase['duration'],
                                      'energy':       energy,
                                      'peakPower':    peak,
                                      'contributors': contributors}

        byLoad = {}

        for load in self.loads:

            total = sum(load['power'] * load['dutyCycle'].get(phase['name'], 0.0)
                        * phase['duration'] for phase in self.phases)

            byLoad[load['name']] = {'energy': total, 'power': load['power']}

        deliveredEnergy = sum(entry['energy'] for entry in byPhase.values())

        sourceEnergy = deliveredEnergy / self.efficiency

        peakPower = max(entry['peakPower'] for entry in byPhase.values())

        peakPhase = max(byPhase, key = lambda name: byPhase[name]['peakPower'])
        energyPhase = max(byPhase, key = lambda name: byPhase[name]['energy'])

        return {'byPhase':         byPhase,
                'byLoad':          byLoad,
                'deliveredEnergy': deliveredEnergy,
                'sourceEnergy':    sourceEnergy,
                'peakPower':       peakPower,
                'peakPhase':       peakPhase,
                'energyPhase':     energyPhase,
                'efficiency':      self.efficiency,
                'totalDuration':   sum(phase['duration'] for phase in self.phases)}

    # -------------------------------------------------------------------------------------------- #

    def identifyDrivers(self) -> dict:

        '''

        Which load drives the energy and which drives the peak, and whether they are the same one.

        **They usually are not**, and knowing which is which decides where effort goes: reducing
        the energy driver saves battery mass, and reducing the peak driver saves harness and
        switching hardware.

        '''

        findings = []

        rollup = self.rollUp()

        byLoad = rollup['byLoad']

        energyDriver = max(byLoad, key = lambda name: byLoad[name]['energy'])
        peakDriver   = max(byLoad, key = lambda name: byLoad[name]['power'])

        energyShare = byLoad[energyDriver]['energy'] / rollup['deliveredEnergy']
        peakShare   = byLoad[peakDriver]['power'] / rollup['peakPower']

        findings.append(
            f'{energyDriver} drives the energy at {energyShare:.0%} of '
            f'{rollup["deliveredEnergy"] / 3600.0:.1f} W h, over '
            f'{rollup["totalDuration"] / 3600.0:.2f} hours.')

        findings.append(
            f'{peakDriver} drives the peak at {byLoad[peakDriver]["power"]:.0f} W, '
            f'{peakShare:.0%} of the {rollup["peakPower"]:.0f} W maximum.')

        if energyDriver != peakDriver:
            findings.append(
                '**They are different loads, which is the usual case.** The energy driver sizes '
                'the battery and the peak driver sizes the harness and the switching, so effort '
                'spent on one does not help the other.')
        else:
            findings.append(
                'They are the same load, which is unusual and makes it the obvious target.')

        if energyShare >= DOMINANCE_THRESHOLD:
            findings.append(
                f'{energyDriver} alone is {energyShare:.0%} of the mission energy. Nothing else on '
                f'the list is worth attacking until it has been.')

        self.findings = findings

        return {'energyDriver': energyDriver,
                'peakDriver':   peakDriver,
                'energyShare':  energyShare,
                'peakShare':    peakShare,
                'sameLoad':     bool(energyDriver == peakDriver),
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def dutyCycleSensitivity(self, loadName: str, duties: list = None) -> dict:

        '''

        How the mission energy moves with one load's duty cycle.

        This exists because duty cycle is where a power budget's optimism lives. A heater duty
        cycle is an assumption about a thermal environment rather than an electrical quantity, and
        it is usually the least examined number in the budget.

        '''

        if duties is None:
            duties = [0.2, 0.4, 0.6, 0.8, 1.0]

        target = next((load for load in self.loads if load['name'] == loadName), None)

        if target is None:
            raise InvalidInputError(
                f"No load named '{loadName}'. Known loads are "
                f'{sorted(load["name"] for load in self.loads)}.',
                context = createErrorContext(component = 'PowerBudget'))

        original = dict(target['dutyCycle'])

        results = {}

        try:
            for duty in duties:

                target['dutyCycle'] = {name: duty for name in original}

                results[duty] = self.rollUp()['deliveredEnergy']

        finally:
            target['dutyCycle'] = original

        baseline = self.rollUp()['deliveredEnergy']

        span = max(results.values()) - min(results.values())

        return {'load':      loadName,
                'results':   results,
                'baseline':  baseline,
                'span':      span,
                'spanFraction': span / baseline}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full power budget report.
        '''

        rollup  = self.rollUp()
        drivers = self.identifyDrivers()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  POWER BUDGET: {len(self.loads)} loads over {len(self.phases)} phases')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [[name,
              f'{entry["duration"] / 60.0:.1f}',
              f'{entry["peakPower"]:.0f}',
              f'{entry["energy"] / 3600.0:.2f}']
             for name, entry in rollup['byPhase'].items()],
            ['Phase', 'Duration [min]', 'Peak [W]', 'Energy [W h]'], title = 'By phase'))

        lines.append('')
        lines.append(formatReportTable(
            [[name,
              f'{entry["power"]:.0f}',
              f'{entry["energy"] / 3600.0:.2f}',
              f'{entry["energy"] / rollup["deliveredEnergy"]:.1%}']
             for name, entry in sorted(rollup['byLoad'].items(),
                                       key = lambda item: -item[1]['energy'])],
            ['Load', 'Power [W]', 'Energy [W h]', 'Share'], title = 'By load'))

        lines.append('')
        lines.append(formatReportTable(
            [['Delivered energy',  f'{rollup["deliveredEnergy"] / 3600.0:.1f}',   'W h'],
             ['Distribution efficiency', f'{rollup["efficiency"]:.0%}',           ''],
             ['Source energy',     f'{rollup["sourceEnergy"] / 3600.0:.1f}',      'W h'],
             ['Peak power',        f'{rollup["peakPower"]:.0f}',                  'W'],
             ['Peak phase',        f'{rollup["peakPhase"]}',                      ''],
             ['Energy phase',      f'{rollup["energyPhase"]}',                    '']],
            ['Quantity', 'Value', 'Unit'], title = 'Totals'))

        lines.append('')
        for finding in drivers['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'power_budget.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if not self.loads:
            raise InvalidInputError(
                'A power budget needs at least one load.',
                context = createErrorContext(component = 'PowerBudget'))

        if not self.phases:
            raise InvalidInputError(
                'A power budget needs at least one phase. Without phases there is a peak power and '
                'no energy, and the energy is what sizes the battery.',
                context = createErrorContext(component = 'PowerBudget'))

        phaseNames = set()

        for index, phase in enumerate(self.phases):

            for key in ('name', 'duration'):
                if key not in phase:
                    raise InvalidInputError(
                        f'Phase {index + 1} has no {key}.',
                        context = createErrorContext(component = 'PowerBudget'))

            if phase['duration'] <= 0.0:
                raise InvalidInputError(
                    f"Phase '{phase['name']}' has a duration of {phase['duration']}.",
                    context = createErrorContext(component = 'PowerBudget'))

            if phase['name'] in phaseNames:
                raise InvalidInputError(
                    f"Duplicate phase name '{phase['name']}'.",
                    context = createErrorContext(component = 'PowerBudget'))

            phaseNames.add(phase['name'])

        loadNames = set()

        for index, load in enumerate(self.loads):

            for key in ('name', 'power', 'dutyCycle'):
                if key not in load:
                    raise InvalidInputError(
                        f'Load {index + 1} has no {key}.',
                        context = createErrorContext(component = 'PowerBudget'))

            if load['name'] in loadNames:
                raise InvalidInputError(
                    f"Duplicate load name '{load['name']}'. Duplicated names are how a load gets "
                    f'counted twice or dropped in a rollup.',
                    context = createErrorContext(component = 'PowerBudget'))

            loadNames.add(load['name'])

            if load['power'] < 0.0:
                raise InvalidInputError(
                    f"Load '{load['name']}' has negative power.",
                    context = createErrorContext(component = 'PowerBudget'))

            for phaseName, duty in load['dutyCycle'].items():

                if phaseName not in phaseNames:
                    raise InvalidInputError(
                        f"Load '{load['name']}' has a duty cycle for phase '{phaseName}', which is "
                        f'not in the phase list {sorted(phaseNames)}. A duty cycle against a phase '
                        f'that does not exist is silently ignored in most tools, and its energy '
                        f'disappears.',
                        context = createErrorContext(component = 'PowerBudget'))

                if not 0.0 <= duty <= 1.0:
                    raise InvalidInputError(
                        f"Load '{load['name']}' has a duty cycle of {duty} in phase "
                        f"'{phaseName}', which must lie in [0, 1].",
                        context = createErrorContext(component = 'PowerBudget'))

        if not 0.0 < self.efficiency <= 1.0:
            raise InvalidInputError(
                f'The distribution efficiency must lie in (0, 1], got {self.efficiency}.',
                context = createErrorContext(component = 'PowerBudget'))
