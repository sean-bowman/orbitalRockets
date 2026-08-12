
# -- LaunchAvailability -- #

'''

The probability of getting off the ground, and what actually moves it.

Launch commit criteria are a list of independent conditions, every one of which has to be satisfied
at the same instant. The probability of that is the product, and a product of numbers below one
falls faster than anybody expects: **six criteria each satisfied nine times out of ten give 53 per
cent, not 90.**

That is the first result and it is the reason a criterion is never free. Adding one costs the whole
launch probability its own violation rate, regardless of how rarely it fires on its own.

The second result is the one that matters operationally. **Attempts beat criteria.** Improving a
single constraint from 90 to 95 per cent moves the campaign probability by a few points; halving the
turnaround so the campaign gets twice the attempts moves it far more, because the cumulative
probability is one minus the product of the failures.

That makes turnaround a launch probability requirement rather than a convenience, which is the
connection between this class and `CountdownTimeline`.

**Independence is the assumption doing the work**, and for weather it is optimistic: a front sitting
over the range violates the same criteria tomorrow. The correlated case is computed alongside the
independent one and the gap between them is the honest uncertainty in the answer.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from groundUtils import (SCRUB_CAUSES, cumulativeGoProbability,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, GroundSystemsError)
except ImportError:
    from .groundUtils import (SCRUB_CAUSES, cumulativeGoProbability,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, GroundSystemsError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Day-to-day correlation applied to the weather constraints in the correlated case. A value of zero
# reproduces the independent result and a value of one means a scrub today guarantees a scrub
# tomorrow. Weather sits well above zero and well below one.
DEFAULT_CORRELATION = 0.4    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- LaunchAvailability -- #
# ------------------------------------------------------------------------------------------------ #

class LaunchAvailability:

    '''

    Per-attempt and campaign launch probability from a set of launch commit criteria, and the
    sensitivity of both to constraints and to attempts.

    '''

    def __init__(self):

        self.constraints = {}
        self.attempts    = np.nan
        self.correlation = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `constraints` maps a launch commit criterion to its probability of being violated at the
        instant of the attempt. A criterion violated one time in ten is 0.10.

        `attempts` is how many attempts the campaign gets, which usually comes from
        `CountdownTimeline.attemptsPerCampaign`.

        `correlation` is the day-to-day persistence applied in the correlated case.

        '''

        requiredParams = {'constraints': dict}

        optionalParams = {'attempts':    (int, float),
                          'correlation': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.attempts):
            self.attempts = 1

        if not np.isfinite(self.correlation):
            self.correlation = DEFAULT_CORRELATION

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculatePerAttempt(self) -> dict:

        '''

        Probability that every criterion is satisfied at once.

        The product is the whole calculation. What the table adds is the cost of each criterion
        expressed as the launch probability it removes, which is the number worth arguing about
        when a criterion is proposed.

        '''

        satisfied = 1.0

        for probability in self.constraints.values():
            satisfied *= (1.0 - probability)

        entries = []

        for name, probability in self.constraints.items():

            # What the launch probability would be if this criterion did not exist. The difference
            # is what the criterion costs, and it depends on the others as well as on itself.
            without = satisfied / (1.0 - probability) if probability < 1.0 else 1.0

            entries.append({'constraint':     name,
                            'violationRate':  probability,
                            'goProbability':  1.0 - probability,
                            'withoutIt':      without,
                            'costsUs':        without - satisfied})

        entries.sort(key = lambda entry: entry['costsUs'], reverse = True)

        # A useful comparison: the worst single criterion against the combined result. The gap is
        # the part that is invisible when criteria are reviewed one at a time.
        worst = entries[0] if entries else None

        return {'perAttempt':     satisfied,
                'constraints':    entries,
                'worst':          worst,
                'worstAlone':     1.0 - worst['violationRate'] if worst else 1.0,
                'combinedPenalty': (1.0 - worst['violationRate']) - satisfied if worst else 0.0,
                'count':          len(self.constraints)}

    # -------------------------------------------------------------------------------------------- #

    def calculateCampaign(self, attempts: int = None) -> dict:

        '''

        Cumulative launch probability over the campaign, independent and correlated.

        The correlated case reduces each attempt after the first: a scrub makes the next attempt
        less likely than the unconditional rate, which is what a weather system does.

        '''

        if attempts is None:
            attempts = int(self.attempts)

        perAttempt = self.calculatePerAttempt()['perAttempt']

        independent = cumulativeGoProbability(perAttempt, attempts)

        # Correlated case, as a two-state chain on the go condition with lag-one correlation equal
        # to the correlation input:
        #
        #     P(go | went yesterday)     = p + (1 - p) * rho
        #     P(go | scrubbed yesterday) = p * (1 - rho)
        #
        # Those two reproduce the unconditional p exactly and give a lag-one correlation
        # coefficient of exactly rho, which is what makes this a model rather than a fudge.
        #
        # A campaign only ever follows the scrub branch, because the first go ends it. So the
        # probability of scrubbing every attempt is the first scrub times the conditional scrub
        # for each one after it.
        afterScrub = perAttempt * (1.0 - self.correlation)

        failure = (1.0 - perAttempt) * (1.0 - afterScrub) ** max(0, attempts - 1)
        correlated = 1.0 - failure if attempts > 0 else 0.0

        return {'attempts':         attempts,
                'perAttempt':       perAttempt,
                'independent':      independent,
                'correlated':       correlated,
                'conditionalAfterScrub': afterScrub,
                'gap':              independent - correlated,
                'correlation':      self.correlation}

    # -------------------------------------------------------------------------------------------- #

    def compareLevers(self, improvement: float = 0.05) -> dict:

        '''

        Two ways to raise the campaign probability, side by side.

        The first is fixing the worst constraint by `improvement`. The second is one more attempt.
        They are compared at the same baseline so the answer is a straight preference.

        '''

        baseline = self.calculateCampaign()
        worst = self.calculatePerAttempt()['worst']

        if worst is None:
            raise GroundSystemsError('No constraints were supplied, so there is nothing to compare.')

        # Lever one: improve the worst constraint.
        original = dict(self.constraints)

        try:
            self.constraints = dict(original)
            self.constraints[worst['constraint']] = max(0.0,
                                                        worst['violationRate'] - improvement)
            improved = self.calculateCampaign()
        finally:
            self.constraints = original

        # Lever two: one more attempt.
        extra = self.calculateCampaign(baseline['attempts'] + 1)

        constraintGain = improved['independent'] - baseline['independent']
        attemptGain = extra['independent'] - baseline['independent']

        return {'attempts':        baseline['attempts'],
                'baseline':        baseline['independent'],
                'worstConstraint': worst['constraint'],
                'improvement':    improvement,
                'constraintCase': improved['independent'],
                'constraintGain': constraintGain,
                'attemptCase':    extra['independent'],
                'attemptGain':    attemptGain,
                'attemptsWin':    attemptGain > constraintGain,
                'ratio':          attemptGain / constraintGain if constraintGain > 0.0 else np.inf}

    # -------------------------------------------------------------------------------------------- #

    def attemptSweep(self, maximum: int = 10) -> dict:

        '''

        Campaign probability against attempt count, and the attempts needed to reach thresholds.

        The returns diminish, because each attempt multiplies the remaining failure probability
        rather than adding to the success. That is why the first extra attempt is worth several of
        the later ones.

        '''

        perAttempt = self.calculatePerAttempt()['perAttempt']

        sweep = [{'attempts':   count,
                  'cumulative': cumulativeGoProbability(perAttempt, count),
                  'marginal':   (cumulativeGoProbability(perAttempt, count)
                                 - cumulativeGoProbability(perAttempt, count - 1))}
                 for count in range(1, maximum + 1)]

        thresholds = {}

        for level in (0.90, 0.95, 0.99):
            needed = next((entry['attempts'] for entry in sweep if entry['cumulative'] >= level),
                          None)
            thresholds[level] = needed

        return {'sweep':      sweep,
                'thresholds': thresholds,
                'perAttempt': perAttempt}

    # -------------------------------------------------------------------------------------------- #

    def scrubAttribution(self) -> dict:

        '''

        Expected scrubs in a campaign, attributed to cause.

        The weather share is anchored to the Eastern Range record, where roughly half of scrubs
        across three decades were weather. The remainder of the split is representative.

        '''

        campaign = self.calculateCampaign()
        expectedScrubs = campaign['attempts'] * (1.0 - campaign['perAttempt'])

        return {'expectedScrubs': expectedScrubs,
                'byCause':        [{'cause':  cause,
                                    'share':  share,
                                    'scrubs': expectedScrubs * share}
                                   for cause, share in SCRUB_CAUSES.items()]}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        The per-attempt product, the campaign result, and the lever comparison.

        '''

        perAttempt = self.calculatePerAttempt()
        campaign = self.calculateCampaign()
        levers = self.compareLevers()

        lines = []

        lines.append(formatReportTable(
            [[entry['constraint'],
              f'{entry["violationRate"] * 100.0:.0f}%',
              f'{entry["goProbability"] * 100.0:.0f}%',
              f'{entry["costsUs"] * 100.0:.1f}%'] for entry in perAttempt['constraints']],
            ['constraint', 'violated', 'go alone', 'costs the launch'],
            title = 'LAUNCH COMMIT CRITERIA'))

        lines.append('')
        lines.append(f'{perAttempt["count"]} criteria give {perAttempt["perAttempt"] * 100.0:.1f}% '
                     f'per attempt, against {perAttempt["worstAlone"] * 100.0:.0f}% for the worst '
                     f'one alone.')
        lines.append('')

        lines.append(formatReportTable(
            [[f'{campaign["attempts"]}',
              f'{campaign["independent"] * 100.0:.1f}%',
              f'{campaign["correlated"] * 100.0:.1f}%',
              f'{campaign["gap"] * 100.0:.1f}%']],
            ['attempts', 'independent', 'correlated', 'gap'],
            title = 'CAMPAIGN PROBABILITY'))

        lines.append('')
        lines.append(f'Improving {levers["worstConstraint"]} by '
                     f'{levers["improvement"] * 100.0:.0f} points buys '
                     f'{levers["constraintGain"] * 100.0:.1f}%; one more attempt buys '
                     f'{levers["attemptGain"] * 100.0:.1f}%.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'launchAvailability.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not self.constraints:
            raise InvalidInputError('At least one launch commit criterion is needed.')

        for name, probability in self.constraints.items():

            if not 0.0 <= float(probability) <= 1.0:
                raise InvalidInputError(
                    f'Constraint {name} has a violation probability of {probability}, which is '
                    f'not a probability.',
                    context = {'constraints': self.constraints})

        if int(self.attempts) < 1:
            raise InvalidInputError('A campaign has at least one attempt.')

        if not 0.0 <= self.correlation < 1.0:
            raise InvalidInputError('Correlation is a fraction at or above zero and below one. A '
                                    'correlation of one means a scrub is permanent.')
