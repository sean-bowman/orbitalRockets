
# -- IgnitionSystem -- #

'''

Igniter selection, and the detection window that turns out not to be an instrumentation problem.

Igniter selection is decided by three questions and almost never by energy. How many times does the
engine have to light. Is electrical power available at the engine at that moment. And is the
propellant hypergolic, in which case there is no igniter at all. Energy comes fourth, because every
device on the list delivers far more than the minimum ignition energy of a gaseous mixture.

The second half of this class is the ignition detection window, and it produces a result worth
stating plainly. The window is not set by how fast a pressure transducer responds. It is set by how
much propellant may accumulate before combustion, which is a mass budget, and on a large engine
that budget is exhausted in a few milliseconds. **No practical detection system is fast enough to
prevent a hard start.** What prevents one is the flow schedule: an engine that admits a tenth of
its mainstage flow while it lights has ten times the window of one that admits all of it.

Detection exists to abort, not to protect. The protection is in the sequence.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from ignitionUtils import (IGNITER_TYPES, IGNITION_DELAY, PROPELLANT_COMBINATIONS,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, IgnitionError)
except ImportError:
    from .ignitionUtils import (IGNITER_TYPES, IGNITION_DELAY, PROPELLANT_COMBINATIONS,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, IgnitionError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Accumulation permitted before combustion, in chamber-fulls, as a detection budget.
#
# Two chamber-fulls is the same convention StartTransient uses for a hard start and it is carried
# here so the two classes cannot disagree about what counts as too much.
PERMITTED_CHAMBER_FULLS = 2.0    # [-]

# The fastest a chamber pressure rise can realistically be detected and acted on, from transducer
# response through the controller loop to a commanded valve movement.
#
# This is an order of magnitude rather than a specification. The point it is used to make does not
# depend on which end of the range is taken, because the answer is off by a factor of ten either
# way.
DETECTION_LATENCY = 0.010    # [s]

# ------------------------------------------------------------------------------------------------ #
# -- IgnitionSystem -- #
# ------------------------------------------------------------------------------------------------ #

class IgnitionSystem:

    '''

    Igniter selection against the mission's constraints, and the detection window it has to work in.

    '''

    def __init__(self):

        self.combination   = ''
        self.startsRequired = np.nan
        self.powerAvailable = True
        self.residenceTime  = np.nan
        self.startFlowFraction = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `startsRequired` is the number of times one installation has to light, over the life of the
        hardware. `startFlowFraction` is the fraction of mainstage flow admitted while the engine
        lights, which is the single lever that widens the detection window.

        '''

        requiredParams = {'combination':    str,
                          'startsRequired': (int, float)}

        optionalParams = {'powerAvailable':    bool,
                          'residenceTime':     (int, float),
                          'startFlowFraction': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise InvalidInputError(
                f'Unknown propellant combination \'{self.combination}\'. Known combinations are '
                f'{sorted(PROPELLANT_COMBINATIONS)}.',
                context = createErrorContext(component = 'IgnitionSystem'))

        if not np.isfinite(self.startFlowFraction):
            self.startFlowFraction = 1.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def isHypergolic(self) -> bool:

        return bool(PROPELLANT_COMBINATIONS[self.combination]['hypergolic'])

    # -------------------------------------------------------------------------------------------- #

    def selectIgniter(self) -> dict:

        '''

        Screen the igniter types against the mission and report what survives, with the reason each
        rejection fired.

        The audit trail is the useful part. A selection that says only "torch" tells nobody why,
        and the why is usually one hard constraint doing all the work.

        '''

        findings = []

        if self.isHypergolic():

            findings.append(
                f'{self.combination} is hypergolic, so there is no igniter to select. The ignition '
                f'delay is a property of the propellants and the injector, and it is '
                f'{IGNITION_DELAY[self.combination][0]:.0f} to '
                f'{IGNITION_DELAY[self.combination][1]:.0f} ms.')

            findings.append(
                'That is the real reason storable propellants dominate spacecraft propulsion. Not '
                'the storability, which is in the name, but that a system with no igniter has one '
                'fewer thing to fail after ten years in orbit.')

            self.findings = findings

            return {'hypergolic': True, 'selected': None, 'candidates': {}, 'findings': findings}

        candidates = {}

        for name, entry in IGNITER_TYPES.items():

            rejections = []

            if entry['restarts'] is not None and entry['restarts'] < self.startsRequired:
                rejections.append(
                    f'supports {entry["restarts"]} start and {self.startsRequired:.0f} are needed, '
                    f'so it would take {self.startsRequired:.0f} installations')

            if entry['needsPower'] and not self.powerAvailable:
                rejections.append('needs electrical power at the engine and none is available')

            if name == 'catalytic':
                rejections.append('is a monopropellant device and this is a bipropellant engine')

            candidates[name] = {'viable':     bool(not rejections),
                                'rejections': rejections,
                                'restarts':   entry['restarts'],
                                'consumable': entry['needsConsumable'],
                                'note':       entry['note']}

        viable = [name for name, entry in candidates.items() if entry['viable']]

        if not viable:
            raise IgnitionError(
                f'No igniter type survives the constraints: {self.startsRequired:.0f} starts, '
                f'power available {self.powerAvailable}, propellant {self.combination}. Either the '
                f'start count or the power assumption has to move.',
                context = createErrorContext(component = 'IgnitionSystem'))

        # prefer a device with no consumable when more than one survives, because that is the axis
        # that decides it in practice once restart is satisfied
        selected = sorted(viable, key = lambda name: (candidates[name]['consumable'], name))[0]

        findings.append(
            f'{len(viable)} of {len(candidates)} igniter types survive: {", ".join(viable)}.')

        rejected = [name for name in candidates if not candidates[name]['viable']]

        if rejected:
            findings.append(
                f'Rejected: ' + '; '.join(
                    f'{name} ({candidates[name]["rejections"][0]})' for name in rejected) + '.')

        findings.append(
            f'Selected {selected}, on the grounds that it carries no consumable once the restart '
            f'requirement is satisfied.')

        self.findings = findings

        return {'hypergolic': False,
                'selected':   selected,
                'candidates': candidates,
                'viable':     viable,
                'findings':   findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateDetectionWindow(self) -> dict:

        '''

        How long combustion may be absent before the accumulated propellant is a problem, and
        whether any detection system could act inside it.

        The window is the permitted accumulation divided by the flow rate, which in chamber-fulls
        is simply the permitted number of chamber-fulls times the residence time, divided by the
        fraction of mainstage flow being admitted.

            t_window  =  N_permitted * t_residence / flowFraction

        Reducing the start flow is the only lever with real authority in that expression, and it is
        exactly what a staged valve sequence does.

        '''

        if not np.isfinite(self.residenceTime):
            raise InvalidInputError(
                'A residence time is needed to compute a detection window. Take it from '
                'StartTransient.residenceTime() for the same engine, so the two classes are '
                'describing one chamber.',
                context = createErrorContext(component = 'IgnitionSystem'))

        findings = []

        window = PERMITTED_CHAMBER_FULLS * self.residenceTime / self.startFlowFraction

        achievable = bool(window >= DETECTION_LATENCY)

        findings.append(
            f'At {self.startFlowFraction:.0%} of mainstage flow, {PERMITTED_CHAMBER_FULLS:.0f} '
            f'chamber-fulls accumulate in {window * 1000.0:.1f} ms.')

        if not achievable:
            findings.append(
                f'A detection system needs on the order of {DETECTION_LATENCY * 1000.0:.0f} ms to '
                f'sense a chamber pressure rise and command a valve, so it cannot act inside that '
                f'window. **Detection cannot prevent this hard start.** It can only record it.')

            required = PERMITTED_CHAMBER_FULLS * self.residenceTime / DETECTION_LATENCY

            findings.append(
                f'The flow schedule can. Admitting {required:.1%} of mainstage flow during '
                f'ignition would open the window to the detection latency, which is what a staged '
                f'valve sequence is for. The RS-25 takes 1.5 seconds to prime its main chamber and '
                f'this is why.')
        else:
            findings.append(
                f'That is longer than the {DETECTION_LATENCY * 1000.0:.0f} ms a detection system '
                f'needs, so detection can act inside the window. That is unusual and it comes from '
                f'the low start flow, not from fast instrumentation.')

        self.findings = findings

        return {'window':            window,
                'detectionLatency':  DETECTION_LATENCY,
                'detectionCanAct':   achievable,
                'permittedFulls':    PERMITTED_CHAMBER_FULLS,
                'requiredFlowFraction': PERMITTED_CHAMBER_FULLS * self.residenceTime
                                        / DETECTION_LATENCY,
                'findings':          findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full ignition system report.
        '''

        selection = self.selectIgniter()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  IGNITION SYSTEM: {self.combination}, {self.startsRequired:.0f} starts '
                     f'required')
        lines.append('=' * 96)
        lines.append('')

        if selection['hypergolic']:
            lines.append('    No igniter. The propellants are hypergolic.')
        else:
            rows = [[name,
                     'yes' if entry['viable'] else 'no',
                     'unlimited' if entry['restarts'] is None else f'{entry["restarts"]}',
                     'yes' if entry['consumable'] else 'no',
                     entry['rejections'][0] if entry['rejections'] else '']
                    for name, entry in selection['candidates'].items()]

            lines.append(formatReportTable(
                rows, ['Igniter', 'Viable', 'Restarts', 'Consumable', 'Why not'],
                title = 'Selection'))

        lines.append('')
        for finding in selection['findings']:
            lines.append(f'    - {finding}')

        if np.isfinite(self.residenceTime):

            window = self.calculateDetectionWindow()

            lines.append('')
            lines.append(formatReportTable(
                [['Residence time',    f'{self.residenceTime * 1000.0:.2f}',           'ms'],
                 ['Start flow',        f'{self.startFlowFraction:.0%}',                ''],
                 ['Detection window',  f'{window["window"] * 1000.0:.1f}',             'ms'],
                 ['Detection latency', f'{window["detectionLatency"] * 1000.0:.0f}',   'ms'],
                 ['Detection can act', f'{window["detectionCanAct"]}',                 '']],
                ['Quantity', 'Value', 'Unit'], title = 'Detection window'))

            lines.append('')
            for finding in window['findings']:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'ignition_system.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.startsRequired < 1:
            raise InvalidInputError(
                f'An engine has to light at least once, got {self.startsRequired}.',
                context = createErrorContext(component = 'IgnitionSystem'))

        if not 0.0 < self.startFlowFraction <= 1.0:
            raise InvalidInputError(
                f'The start flow fraction must lie in (0, 1], got {self.startFlowFraction}. It is '
                f'the fraction of mainstage flow admitted while the engine lights.',
                context = createErrorContext(component = 'IgnitionSystem'))

        if np.isfinite(self.residenceTime) and self.residenceTime <= 0.0:
            raise InvalidInputError(
                f'The residence time must be positive, got {self.residenceTime}.',
                context = createErrorContext(component = 'IgnitionSystem'))
