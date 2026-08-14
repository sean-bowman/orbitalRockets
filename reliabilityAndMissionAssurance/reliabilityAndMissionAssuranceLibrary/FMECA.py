
# -- FMECA -- #

'''

Working up from the parts, and the ranking that decides whether anybody acts.

A failure modes, effects and criticality analysis lists every way a component can fail, what each
failure does to the system, how likely it is and whether anybody would notice. That much is
bookkeeping. What makes it useful or useless is what happens to the list afterwards.

**The FMECA is only useful if somebody acts on it. An unactioned finding is worse than none**,
because it converts a real hazard into a document that says the hazard was considered.

Two things about the ranking are worth knowing before it is used.

**A risk priority number is a product of three ranks and it is not a number.** Severity, occurrence
and detection are ordinal scales, and multiplying ordinals produces something that sorts but does
not measure: an RPN of 100 is not twice an RPN of 50, and two modes with the same RPN can be
completely different problems.

**And ranking by RPN buries the catastrophic modes.** A catastrophic mode that is rare and
detectable scores lower than a marginal one that is common and hidden, which is exactly backwards
for a launch vehicle where the catastrophic ones are the whole point. **Criticality, which is
severity and occurrence without detection, is the ranking that finds them**, and this class reports
both and says which is which.

The one thing an FMECA finds that nothing else does is the mode nobody thought about, and it finds
it by being exhaustive rather than by being clever.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from reliabilityUtils import (SEVERITY_CLASSES, DETECTION_CLASSES,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, FmecaError)
except ImportError:
    from .reliabilityUtils import (SEVERITY_CLASSES, DETECTION_CLASSES,
                                   applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, FmecaError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Occurrence ranks from a failure probability. The bands are a convention rather than a measurement,
# which is the whole problem with an RPN and is why criticality is reported alongside it.
OCCURRENCE_BANDS = [(1.0e-6, 1), (1.0e-5, 2), (1.0e-4, 3), (1.0e-3, 4), (1.0, 5)]

# Any mode at or above this severity is reported regardless of its RPN, because a catastrophic mode
# that scores low on an ordinal product is still a catastrophic mode.
MANDATORY_REVIEW_SEVERITY = 'critical'

# ------------------------------------------------------------------------------------------------ #
# -- FMECA -- #
# ------------------------------------------------------------------------------------------------ #

class FMECA:

    '''

    The failure mode table, criticality and risk priority rankings, and the findings that have to
    be actioned.

    '''

    def __init__(self):

        self.modes    = []
        self.actioned = []

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `modes` is a list of dictionaries with `item`, `mode`, `effect`, `severity` from
        SEVERITY_CLASSES, `probability`, and `detection` from DETECTION_CLASSES.

        `actioned` lists the modes that have an action against them, by mode name. **A finding
        without an action is what this class exists to surface.**

        '''

        requiredParams = {'modes': list}

        optionalParams = {'actioned': list}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.actioned is None or isinstance(self.actioned, float):
            self.actioned = []

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def occurrenceRank(self, probability: float) -> int:

        '''
        The occurrence rank for a probability, from the banded scale.
        '''

        for threshold, rank in OCCURRENCE_BANDS:
            if probability <= threshold:
                return rank

        return OCCURRENCE_BANDS[-1][1]

    # -------------------------------------------------------------------------------------------- #

    def calculateTable(self) -> dict:

        '''

        The full table, with both rankings.

        **Criticality is severity times occurrence and it is the one that finds the catastrophic
        modes.** The risk priority number multiplies detection in as well, which pushes a rare and
        detectable catastrophe below a common and hidden nuisance.

        '''

        entries = []

        for mode in self.modes:

            severity = SEVERITY_CLASSES[mode['severity']]['rank']
            detection = DETECTION_CLASSES[mode['detection']]['rank']
            probability = float(mode['probability'])
            occurrence = self.occurrenceRank(probability)

            entries.append({'item':        mode['item'],
                            'mode':        mode['mode'],
                            'effect':      mode['effect'],
                            'severity':    mode['severity'],
                            'severityRank': severity,
                            'probability': probability,
                            'occurrence':  occurrence,
                            'detection':   mode['detection'],
                            'detectionRank': detection,
                            'criticality': severity * occurrence,
                            'riskPriority': severity * occurrence * detection,
                            'actioned':    mode['mode'] in self.actioned})

        byCriticality = sorted(entries, key = lambda entry: entry['criticality'], reverse = True)
        byPriority = sorted(entries, key = lambda entry: entry['riskPriority'], reverse = True)

        return {'modes':          entries,
                'byCriticality':  byCriticality,
                'byRiskPriority': byPriority,
                'count':          len(entries),
                'topByCriticality':  byCriticality[0]['mode'],
                'topByRiskPriority': byPriority[0]['mode'],
                'rankingsAgree':  bool(byCriticality[0]['mode'] == byPriority[0]['mode'])}

    # -------------------------------------------------------------------------------------------- #

    def rankingDisagreement(self) -> dict:

        '''

        Where the two rankings disagree, and which modes each buries.

        **This is the useful output of running both.** A mode that ranks high on criticality and
        low on risk priority is a catastrophe the detection column has hidden, and it is exactly
        the mode a launch vehicle programme cannot afford to sort to the bottom.

        '''

        table = self.calculateTable()

        criticalityOrder = {entry['mode']: index
                            for index, entry in enumerate(table['byCriticality'])}
        priorityOrder = {entry['mode']: index
                         for index, entry in enumerate(table['byRiskPriority'])}

        entries = []

        for mode in table['modes']:

            name = mode['mode']
            movement = priorityOrder[name] - criticalityOrder[name]

            entries.append({'mode':             name,
                            'severity':         mode['severity'],
                            'criticalityRank':  criticalityOrder[name] + 1,
                            'priorityRank':     priorityOrder[name] + 1,
                            'movement':         movement,
                            'buriedByDetection': bool(movement > 0
                                                      and mode['severityRank']
                                                      >= SEVERITY_CLASSES
                                                      [MANDATORY_REVIEW_SEVERITY]['rank'])})

        entries.sort(key = lambda entry: entry['movement'], reverse = True)

        buried = [entry for entry in entries if entry['buriedByDetection']]

        return {'entries':      entries,
                'buried':       [entry['mode'] for entry in buried],
                'worstMovement': entries[0]['movement'] if entries else 0,
                'anyBuried':    len(buried) > 0}

    # -------------------------------------------------------------------------------------------- #

    def mandatoryReview(self) -> dict:

        '''

        Every mode at or above the mandatory review severity, regardless of how it ranks.

        **This is the filter that does not use an ordinal product at all.** A catastrophic mode is
        reviewed because it is catastrophic, and no amount of rarity or detectability removes it
        from the list.

        '''

        table = self.calculateTable()
        threshold = SEVERITY_CLASSES[MANDATORY_REVIEW_SEVERITY]['rank']

        entries = [mode for mode in table['modes'] if mode['severityRank'] >= threshold]

        entries.sort(key = lambda entry: (entry['severityRank'], entry['probability']),
                     reverse = True)

        unactioned = [entry for entry in entries if not entry['actioned']]

        return {'threshold':      MANDATORY_REVIEW_SEVERITY,
                'modes':          entries,
                'count':          len(entries),
                'share':          len(entries) / table['count'] if table['count'] else 0.0,
                'unactioned':     [entry['mode'] for entry in unactioned],
                'unactionedCount': len(unactioned)}

    # -------------------------------------------------------------------------------------------- #

    def checkActions(self) -> dict:

        '''

        Every mode that needs an action, against the ones that have one.

        Raises where a mandatory review mode has no action, because **an unactioned finding is
        worse than none**: it converts a real hazard into a document that says the hazard was
        considered.

        '''

        review = self.mandatoryReview()

        result = {'reviewed':   review['count'],
                  'actioned':   review['count'] - review['unactionedCount'],
                  'unactioned': review['unactioned']}

        if review['unactioned']:
            raise FmecaError(
                f'{review["unactionedCount"]} of {review["count"]} modes at or above '
                f'{MANDATORY_REVIEW_SEVERITY} severity have no action against them: '
                f'{", ".join(review["unactioned"])}. **An unactioned finding is worse than none**, '
                f'because it converts a real hazard into a document saying the hazard was '
                f'considered.',
                context = {'unactioned': review['unactioned'],
                           'reviewed':   review['count']})

        return result

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Both rankings, the disagreement between them, and the action check.
        '''

        table = self.calculateTable()
        disagreement = self.rankingDisagreement()

        lines = []

        lines.append(formatReportTable(
            [[entry['item'],
              entry['mode'],
              entry['severity'],
              f'{entry["probability"]:.1e}',
              entry['detection'],
              f'{entry["criticality"]}',
              f'{entry["riskPriority"]}'] for entry in table['byCriticality']],
            ['item', 'mode', 'severity', 'probability', 'detection', 'crit', 'RPN'],
            title = 'FAILURE MODES, RANKED BY CRITICALITY'))

        lines.append('')
        lines.append(f'Top by criticality {table["topByCriticality"]}, top by risk priority '
                     f'{table["topByRiskPriority"]}: the rankings '
                     f'{"agree" if table["rankingsAgree"] else "DISAGREE"}.')

        if disagreement['anyBuried']:
            lines.append(f'Buried by the detection column: {", ".join(disagreement["buried"])}.')

        lines.append('')

        try:
            actions = self.checkActions()
            lines.append(f'All {actions["reviewed"]} mandatory review modes have actions.')
        except FmecaError as error:
            lines.append('UNACTIONED FINDINGS')
            lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'fmeca.txt'), 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not self.modes:
            raise InvalidInputError('A FMECA needs at least one failure mode.')

        names = [mode['mode'] for mode in self.modes]

        if len(names) != len(set(names)):
            raise FmecaError('Failure mode names must be unique. A mode listed twice under '
                             'different names is a mode that will be actioned once and closed '
                             'twice.')

        for mode in self.modes:

            for key in ('item', 'mode', 'effect', 'severity', 'detection', 'probability'):
                if key not in mode:
                    raise InvalidInputError(f"Mode {mode.get('mode', 'unnamed')} has no {key}.")

            if mode['severity'] not in SEVERITY_CLASSES:
                raise InvalidInputError(
                    f"{mode['severity']} is not a severity class. Available: "
                    f'{sorted(SEVERITY_CLASSES)}.')

            if mode['detection'] not in DETECTION_CLASSES:
                raise InvalidInputError(
                    f"{mode['detection']} is not a detection class. Available: "
                    f'{sorted(DETECTION_CLASSES)}.')

            if not 0.0 <= float(mode['probability']) <= 1.0:
                raise InvalidInputError(
                    f"Mode {mode['mode']} has a probability outside zero to one.")

        for name in self.actioned:
            if name not in names:
                raise FmecaError(
                    f'{name} is on the actioned list and is not a failure mode in the table. An '
                    f'action against a mode that no longer exists is a closed action with nothing '
                    f'behind it.')
