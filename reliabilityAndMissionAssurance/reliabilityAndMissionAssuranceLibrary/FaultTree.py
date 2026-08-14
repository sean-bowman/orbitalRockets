
# -- FaultTree -- #

'''

Working down from the failure rather than up from the parts, and finding the cut set nobody drew.

A fault tree starts at an undesired top event and decomposes it through AND and OR gates to basic
events. Two things come out of it and the second is the one worth the effort.

**A probability**, from the bottom up: an OR gate fails if any input fails, an AND gate only if all
of them do.

**And the minimal cut sets**: the smallest combinations of basic events that on their own cause the
top event. **A cut set of size one is a single point failure**, and finding them is what a fault
tree is actually for. A probability can be obtained from a spreadsheet; a cut set cannot.

**The single point failures are the output.** They should be listed, argued and accepted
deliberately, and a fault tree that produces a number without producing that list has been run for
the wrong reason.

Two cautions the arithmetic carries.

**The rare event approximation is optimistic.** Summing cut set probabilities double counts the
overlaps, so it overstates the top event probability for large values, which is the safe direction;
the exact inclusion-exclusion is computed alongside it here so the error is visible rather than
assumed.

**And an AND gate over identical units is not what it looks like.** Two units that share a design or
an environment share a failure cause, and a fault tree with independent basic events cannot see
that. See `RedundancyAnalysis`, which is where the beta factor lives.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os
from itertools import combinations

import numpy as np

try:
    from reliabilityUtils import (applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, FaultTreeError)
except ImportError:
    from .reliabilityUtils import (applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, FaultTreeError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Cut sets larger than this are not enumerated. A cut set of five simultaneous independent failures
# contributes nothing to a top event probability and enumerating them is exponential work for no
# result.
MAXIMUM_CUT_SET_ORDER = 4    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- FaultTree -- #
# ------------------------------------------------------------------------------------------------ #

class FaultTree:

    '''

    Top event probability, minimal cut sets, and the single point failures they expose.

    '''

    def __init__(self):

        self.topEvent    = ''
        self.gates       = {}
        self.basicEvents = {}

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `topEvent` names the gate at the top of the tree.

        `gates` maps a gate name to a dictionary with `type`, either 'and' or 'or', and `inputs`,
        a list of gate or basic event names.

        `basicEvents` maps a basic event name to its probability.

        '''

        requiredParams = {'topEvent':    str,
                          'gates':       dict,
                          'basicEvents': dict}

        applyInputs(self, inputs, requiredParams, {})

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateProbability(self, node: str = None) -> float:

        '''

        Top event probability, evaluated bottom up.

        OR gates use the complement product rather than a sum, so the answer is exact for
        independent inputs rather than approximate.

        '''

        name = node if node else self.topEvent

        if name in self.basicEvents:
            return float(self.basicEvents[name])

        gate = self.gates[name]
        values = [self.calculateProbability(child) for child in gate['inputs']]

        if gate['type'] == 'and':
            return float(np.prod(values))

        return float(1.0 - np.prod([1.0 - value for value in values]))

    # -------------------------------------------------------------------------------------------- #

    def minimalCutSets(self, node: str = None) -> list:

        '''

        The smallest combinations of basic events that cause the top event.

        Built bottom up: an OR gate's cut sets are the union of its inputs' cut sets, and an AND
        gate's are every combination of one cut set from each input. Non-minimal sets are removed
        at the end.

        '''

        name = node if node else self.topEvent

        if name in self.basicEvents:
            return [frozenset([name])]

        gate = self.gates[name]

        childSets = [self.minimalCutSets(child) for child in gate['inputs']]

        if gate['type'] == 'or':
            combined = [cutSet for sets in childSets for cutSet in sets]
        else:
            combined = [frozenset([])]
            for sets in childSets:
                combined = [existing | cutSet for existing in combined for cutSet in sets]

        # Drop anything that contains a smaller cut set, which is the minimality condition.
        combined = [cutSet for cutSet in combined if len(cutSet) <= MAXIMUM_CUT_SET_ORDER]

        minimal = []

        for cutSet in sorted(set(combined), key = len):
            if not any(existing <= cutSet for existing in minimal):
                minimal.append(cutSet)

        return minimal

    # -------------------------------------------------------------------------------------------- #

    def analyseCutSets(self) -> dict:

        '''

        The cut sets ranked by contribution, and the single point failures among them.

        **The single point failures are the output.** They are the cut sets of order one, and they
        should be listed, argued and accepted deliberately rather than discovered.

        '''

        cutSets = self.minimalCutSets()

        entries = []

        for cutSet in cutSets:

            probability = float(np.prod([self.basicEvents[event] for event in cutSet]))

            entries.append({'events':      sorted(cutSet),
                            'order':       len(cutSet),
                            'probability': probability,
                            'isSinglePoint': len(cutSet) == 1})

        entries.sort(key = lambda entry: entry['probability'], reverse = True)

        total = sum(entry['probability'] for entry in entries)

        for entry in entries:
            entry['share'] = entry['probability'] / total if total > 0.0 else 0.0

        singlePoints = [entry for entry in entries if entry['isSinglePoint']]

        exact = self.calculateProbability()

        return {'cutSets':         entries,
                'count':           len(entries),
                'singlePoints':    [entry['events'][0] for entry in singlePoints],
                'singlePointCount': len(singlePoints),
                'singlePointShare': sum(entry['share'] for entry in singlePoints),
                'rareEventSum':    total,
                'exactProbability': exact,
                'rareEventError':  (total - exact) / exact if exact > 0.0 else 0.0,
                'dominant':        entries[0]['events'] if entries else None,
                'dominantShare':   entries[0]['share'] if entries else 0.0}

    # -------------------------------------------------------------------------------------------- #

    def importance(self) -> dict:

        '''

        How much each basic event matters, by the Birnbaum measure: the change in the top event
        probability when that event goes from certain to impossible.

        **The ranking is not the ranking by probability.** A low probability event in a single
        point cut set matters far more than a high probability one behind two AND gates, and this
        is the measure that says so.

        '''

        base = self.calculateProbability()

        original = dict(self.basicEvents)
        results = []

        try:
            for event in original:

                self.basicEvents = dict(original)
                self.basicEvents[event] = 1.0
                certain = self.calculateProbability()

                self.basicEvents[event] = 0.0
                impossible = self.calculateProbability()

                results.append({'event':       event,
                                'probability': original[event],
                                'importance':  certain - impossible,
                                'reduction':   base - impossible,
                                'reductionShare': (base - impossible) / base if base > 0.0 else 0.0})
        finally:
            self.basicEvents = original

        results.sort(key = lambda entry: entry['importance'], reverse = True)

        byProbability = sorted(results, key = lambda entry: entry['probability'], reverse = True)

        return {'results':       results,
                'mostImportant': results[0]['event'],
                'mostProbable':  byProbability[0]['event'],
                'rankingsAgree': bool(results[0]['event'] == byProbability[0]['event'])}

    # -------------------------------------------------------------------------------------------- #

    def checkSinglePoints(self, accepted: list = None) -> dict:

        '''

        Every single point failure against the list of ones that have been accepted.

        Raises on an unaccepted one, because **single point failures should be listed, argued and
        accepted deliberately, never discovered**, and a tool that reports them as a number lets
        them stay undiscovered.

        '''

        analysis = self.analyseCutSets()

        accepted = set(accepted or [])
        found = set(analysis['singlePoints'])

        unaccepted = sorted(found - accepted)
        stale = sorted(accepted - found)

        result = {'singlePoints':  sorted(found),
                  'accepted':      sorted(accepted),
                  'unaccepted':    unaccepted,
                  'staleAcceptances': stale,
                  'share':         analysis['singlePointShare']}

        if unaccepted:
            raise FaultTreeError(
                f'{len(unaccepted)} single point failures are not on the accepted list: '
                f'{", ".join(unaccepted)}. They carry '
                f'{analysis["singlePointShare"] * 100.0:.0f} per cent of the top event '
                f'probability. **A single point failure is a decision, not a finding**, and an '
                f'undiscovered one has had the decision made by default.',
                context = {'unaccepted':   unaccepted,
                           'singlePoints': sorted(found),
                           'share':        analysis['singlePointShare']})

        return result

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The top event, the cut sets and the importance ranking.
        '''

        analysis = self.analyseCutSets()
        importance = self.importance()

        lines = []

        lines.append(formatReportTable(
            [[' + '.join(entry['events']),
              f'{entry["order"]}',
              f'{entry["probability"]:.3e}',
              f'{entry["share"] * 100.0:.0f}%',
              'SPF' if entry['isSinglePoint'] else ''] for entry in analysis['cutSets']],
            ['cut set', 'order', 'probability', 'share', ''],
            title = f'CUT SETS FOR {self.topEvent.upper()}'))

        lines.append('')
        lines.append(f'Top event {analysis["exactProbability"]:.3e} exact, '
                     f'{analysis["rareEventSum"]:.3e} by the rare event sum, an overstatement of '
                     f'{analysis["rareEventError"] * 100.0:.1f} per cent.')
        lines.append(f'{analysis["singlePointCount"]} single point failures carrying '
                     f'{analysis["singlePointShare"] * 100.0:.0f} per cent of the probability.')
        lines.append('')

        lines.append(formatReportTable(
            [[entry['event'],
              f'{entry["probability"]:.2e}',
              f'{entry["importance"]:.3e}',
              f'{entry["reductionShare"] * 100.0:.0f}%'] for entry in importance['results']],
            ['basic event', 'probability', 'importance', 'removing it buys'],
            title = 'IMPORTANCE'))

        lines.append('')
        lines.append(f'Most important {importance["mostImportant"]}, most probable '
                     f'{importance["mostProbable"]}: the rankings '
                     f'{"agree" if importance["rankingsAgree"] else "DISAGREE"}.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'faultTree.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not self.gates:
            raise InvalidInputError('A fault tree needs at least one gate.')

        if self.topEvent not in self.gates:
            raise InvalidInputError(f'The top event {self.topEvent} is not a gate in the tree.')

        for name, probability in self.basicEvents.items():
            if not 0.0 <= float(probability) <= 1.0:
                raise InvalidInputError(f'Basic event {name} has a probability outside zero to one.')

        known = set(self.gates) | set(self.basicEvents)

        for name, gate in self.gates.items():

            if gate.get('type') not in ('and', 'or'):
                raise InvalidInputError(f"Gate {name} must be of type 'and' or 'or'.")

            if not gate.get('inputs'):
                raise InvalidInputError(f'Gate {name} has no inputs. A gate with nothing under it '
                                        f'is a basic event that has been drawn as a gate.')

            for child in gate['inputs']:
                if child not in known:
                    raise InvalidInputError(
                        f'Gate {name} refers to {child}, which is neither a gate nor a basic '
                        f'event.')

        # Cycle detection, because a tree that contains itself never evaluates.
        def walk(name: str, visiting: set) -> None:

            if name in self.basicEvents:
                return

            if name in visiting:
                raise FaultTreeError(
                    f'The tree contains a cycle through {name}. A fault tree that contains itself '
                    f'is a directed graph rather than a tree, and it does not evaluate.')

            visiting.add(name)

            for child in self.gates[name]['inputs']:
                walk(child, visiting)

            visiting.remove(name)

        walk(self.topEvent, set())
