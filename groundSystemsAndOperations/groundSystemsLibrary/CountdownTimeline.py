
# -- CountdownTimeline -- #

'''

What sets the length of a countdown, and what a hold actually costs.

A countdown looks like a list of tasks and it is a dependency graph. Some tasks run in parallel and
some cannot, and the total is the longest chain rather than the sum. **The tasks not on the critical
path are free until they are not**, which is why an activity that has never mattered becomes the
schedule the first time it slips.

Two numbers come out of this and they are different questions.

**The recycle time** is how far back a hold sends the count. It is not the duration of the hold. A
hold at T-4 minutes that requires backing up to T-20 costs sixteen minutes of re-run plus the hold
itself, and whether the window survives that is the launch commit decision.

**The scrub turnaround** is how long before the next attempt. It is set by one thing, usually the
slowest of propellant replenishment, battery recharge or crew duty limits, and adding capability
anywhere else does not move it.

**Turnaround is a design requirement rather than an operational detail**, because it sets how many
attempts a campaign gets, and attempts drive launch probability far harder than any single
constraint does. That link is in `LaunchAvailability`.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from groundUtils import (applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, TimelineError)
except ImportError:
    from .groundUtils import (applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, TimelineError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# A task whose float is below this fraction of the total count is called near-critical. Those are
# the ones that become the critical path on a bad day, and they are worth naming separately from
# the ones with hours of slack.
NEAR_CRITICAL_FLOAT = 0.05    # [-] of total duration

# ------------------------------------------------------------------------------------------------ #
# -- CountdownTimeline -- #
# ------------------------------------------------------------------------------------------------ #

class CountdownTimeline:

    '''

    Critical path through a countdown, recycle time from a hold, and scrub turnaround.

    '''

    def __init__(self):

        self.tasks          = []
        self.windowDuration = np.nan
        self.turnaroundDrivers = {}

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `tasks` is a list of dictionaries with `name`, `duration` in seconds, and `predecessors`,
        a list of task names that must finish first. A task with no predecessors starts at zero.

        `windowDuration` is the launch window in seconds, which turns a recycle into a verdict.

        `turnaroundDrivers` maps a driver name to its duration in seconds. The turnaround is the
        largest of them, which is the point: it is set by one thing.

        '''

        requiredParams = {'tasks': list}

        optionalParams = {'windowDuration':    (int, float),
                          'turnaroundDrivers': dict}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.turnaroundDrivers is None or isinstance(self.turnaroundDrivers, float):
            self.turnaroundDrivers = {}

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateCriticalPath(self) -> dict:

        '''

        Earliest and latest start for every task, the total duration, and the chain that sets it.

        Forward pass for the earliest times, backward pass for the latest. Float is the difference,
        and a task with zero float is on the critical path.

        '''

        byName = {task['name']: task for task in self.tasks}

        earliestFinish = {}

        def resolve(name: str, visiting: set) -> float:

            if name in earliestFinish:
                return earliestFinish[name]

            if name in visiting:
                raise TimelineError(
                    f'The task graph contains a cycle through {name}. A countdown that waits on '
                    f'itself never reaches T-0.')

            visiting.add(name)

            task = byName[name]
            start = max([resolve(predecessor, visiting)
                         for predecessor in task.get('predecessors', [])] or [0.0])

            earliestFinish[name] = start + float(task['duration'])
            visiting.remove(name)

            return earliestFinish[name]

        for task in self.tasks:
            resolve(task['name'], set())

        total = max(earliestFinish.values())

        # Backward pass. A task's latest finish is the earliest of its successors' latest starts,
        # or the total for a task nothing depends on.
        successors = {task['name']: [] for task in self.tasks}
        for task in self.tasks:
            for predecessor in task.get('predecessors', []):
                successors[predecessor].append(task['name'])

        latestFinish = {}

        def resolveLate(name: str) -> float:

            if name in latestFinish:
                return latestFinish[name]

            following = successors[name]

            if not following:
                latestFinish[name] = total
            else:
                latestFinish[name] = min(resolveLate(other) - float(byName[other]['duration'])
                                         for other in following)

            return latestFinish[name]

        for task in self.tasks:
            resolveLate(task['name'])

        results = []

        for task in self.tasks:

            name = task['name']
            duration = float(task['duration'])
            slack = latestFinish[name] - earliestFinish[name]

            results.append({'name':           name,
                            'duration':       duration,
                            'earliestStart':  earliestFinish[name] - duration,
                            'earliestFinish': earliestFinish[name],
                            'float':          slack,
                            'critical':       slack < 1.0e-9})

        results.sort(key = lambda entry: entry['earliestStart'])

        critical = [entry['name'] for entry in results if entry['critical']]

        nearCritical = [entry['name'] for entry in results
                        if not entry['critical'] and entry['float'] <= NEAR_CRITICAL_FLOAT * total]

        serialSum = sum(float(task['duration']) for task in self.tasks)

        return {'tasks':         results,
                'totalDuration': total,
                'criticalPath':  critical,
                'nearCritical':  nearCritical,
                'serialSum':     serialSum,
                'parallelGain':  serialSum / total if total > 0.0 else 1.0}

    # -------------------------------------------------------------------------------------------- #

    def calculateRecycle(self, holdAt: float, backUpTo: float, holdDuration: float = 0.0) -> dict:

        '''

        Time from calling a hold to reaching T-0 again.

        `holdAt` and `backUpTo` are times before T-0, in seconds and positive, so a hold at T-4 min
        that backs up to T-20 min is holdAt = 240 and backUpTo = 1200.

        The recycle is the hold itself plus the re-run of everything between the two points. It is
        longer than the hold and that is the part that surprises people.

        '''

        if backUpTo < holdAt:
            raise TimelineError(
                f'Backing up to T-{backUpTo:.0f} s from a hold at T-{holdAt:.0f} s is forward in '
                f'time. A recycle point sits earlier in the count than the hold that calls it.')

        rerun = backUpTo - holdAt
        recycle = holdDuration + rerun

        result = {'holdAt':       holdAt,
                  'backUpTo':     backUpTo,
                  'holdDuration': holdDuration,
                  'rerun':        rerun,
                  'recycle':      recycle,
                  'multiplier':   recycle / holdDuration if holdDuration > 0.0 else np.inf}

        if np.isfinite(self.windowDuration):

            result['windowDuration'] = self.windowDuration
            result['fitsWindow'] = recycle <= self.windowDuration
            result['windowMargin'] = self.windowDuration - recycle

        return result

    # -------------------------------------------------------------------------------------------- #

    def calculateTurnaround(self) -> dict:

        '''

        Scrub turnaround, and which driver sets it.

        The drivers run in parallel with each other, so the turnaround is the largest rather than
        the sum. That is why shortening any driver except the governing one buys nothing, and it is
        the most commonly ignored fact about turnaround.

        '''

        if not self.turnaroundDrivers:
            raise TimelineError('No turnaround drivers were supplied, so there is nothing to size '
                                'the turnaround from.')

        governing = max(self.turnaroundDrivers, key = self.turnaroundDrivers.get)
        turnaround = self.turnaroundDrivers[governing]

        ranked = sorted(self.turnaroundDrivers.items(), key = lambda item: item[1], reverse = True)

        # What removing the governing driver would buy: the turnaround falls to the next largest,
        # not to zero.
        second = ranked[1][1] if len(ranked) > 1 else 0.0

        return {'turnaround':   turnaround,
                'governing':    governing,
                'ranked':       [{'driver': name, 'duration': duration} for name, duration in ranked],
                'nextLargest':  second,
                'gainIfFixed':  turnaround - second,
                'sumOfDrivers': sum(self.turnaroundDrivers.values())}

    # -------------------------------------------------------------------------------------------- #

    def attemptsPerCampaign(self, campaignDuration: float) -> dict:

        '''

        How many launch attempts a campaign of a given length supports.

        The first attempt is free and every one after it costs a turnaround, which is the arithmetic
        that connects a turnaround requirement to a launch probability.

        '''

        turnaround = self.calculateTurnaround()['turnaround']

        if turnaround <= 0.0:
            raise TimelineError('Turnaround must be positive to count attempts.')

        attempts = 1 + int(np.floor(campaignDuration / turnaround))

        return {'campaignDuration': campaignDuration,
                'turnaround':       turnaround,
                'attempts':         attempts}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        The critical path, and the turnaround if drivers were supplied.

        '''

        path = self.calculateCriticalPath()

        lines = []

        lines.append(formatReportTable(
            [[entry['name'],
              f'{entry["duration"] / 60.0:.1f}',
              f'{entry["earliestStart"] / 60.0:.1f}',
              f'{entry["float"] / 60.0:.1f}',
              'yes' if entry['critical'] else ''] for entry in path['tasks']],
            ['task', 'duration [min]', 'starts [min]', 'float [min]', 'critical'],
            title = 'COUNTDOWN CRITICAL PATH'))

        lines.append('')
        lines.append(f'Total {path["totalDuration"] / 60.0:.1f} min against a serial sum of '
                     f'{path["serialSum"] / 60.0:.1f} min, a parallel gain of '
                     f'{path["parallelGain"]:.2f}.')
        lines.append(f'Critical path: {" -> ".join(path["criticalPath"])}.')

        if self.turnaroundDrivers:

            turnaround = self.calculateTurnaround()

            lines.append('')
            lines.append(formatReportTable(
                [[entry['driver'], f'{entry["duration"] / 3600.0:.1f}']
                 for entry in turnaround['ranked']],
                ['driver', 'duration [h]'],
                title = 'SCRUB TURNAROUND'))

            lines.append('')
            lines.append(f'Turnaround {turnaround["turnaround"] / 3600.0:.1f} h, set by '
                         f'{turnaround["governing"]}. Fixing it buys '
                         f'{turnaround["gainIfFixed"] / 3600.0:.1f} h and no more.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'countdownTimeline.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not self.tasks:
            raise InvalidInputError('At least one task is needed to build a timeline.')

        names = [task['name'] for task in self.tasks]

        if len(names) != len(set(names)):
            raise InvalidInputError('Task names must be unique, because predecessors refer to '
                                    'them by name.')

        for task in self.tasks:

            if float(task['duration']) < 0.0:
                raise InvalidInputError(f"Task {task['name']} has a negative duration.")

            for predecessor in task.get('predecessors', []):
                if predecessor not in names:
                    raise InvalidInputError(
                        f"Task {task['name']} depends on {predecessor}, which is not in the list.",
                        context = {'known': sorted(names)})
