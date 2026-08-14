
# -- RedundancyAnalysis -- #

'''

What redundancy is actually worth, which is far less than the ideal arithmetic says.

**Redundancy that shares a failure cause is not redundancy.** That is the domain's ethos and this
class is the arithmetic behind it.

A failure rate splits into an independent part and a common cause part, and the split is the beta
factor. For n parallel units the system failure probability is

    Q = ((1 - beta) * q) ** n  +  beta * q

**The first term falls as the nth power and the second does not fall at all.** At a ten per cent
beta and a one per cent element failure, two units give 1.08e-3 against an ideal 1.00e-4: the
redundancy is worth a factor of nine rather than a factor of a hundred, and **common cause is 93
per cent of what is left.**

Adding a third unit takes it to 1.001e-3. **It buys seven per cent**, because the common cause term
is already the answer and no amount of duplication touches it.

Two consequences follow and both are design decisions rather than analysis ones.

**The way to improve a redundant system is to reduce beta, not to add units.** Separate them
physically and thermally, source them from different lots, and where the consequence justifies it
use different designs. Those are the only things that move the term that dominates.

**And coverage matters for standby redundancy and not for active.** A standby unit that is not
known to have failed is not there when it is called on, so the benefit is multiplied by the
fraction of failures the monitoring actually detects.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from reliabilityUtils import (BETA_FACTORS, DEFAULT_COVERAGE,
                                  betaFactorReliability, parallelReliability,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, RedundancyError)
except ImportError:
    from .reliabilityUtils import (BETA_FACTORS, DEFAULT_COVERAGE,
                                   betaFactorReliability, parallelReliability,
                                   applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, RedundancyError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# A redundant set whose common cause term exceeds this share of the total failure probability is
# reported as common cause dominated. Above it, adding units is close to useless and the only
# available improvement is reducing beta.
COMMON_CAUSE_DOMINANCE = 0.5    # [-]

# The marginal improvement below which another unit is treated as buying nothing. A five per cent
# reduction in failure probability for a whole additional unit, its mass, its power and its
# interfaces is not a trade anybody should make.
MARGINAL_THRESHOLD = 0.05    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- RedundancyAnalysis -- #
# ------------------------------------------------------------------------------------------------ #

class RedundancyAnalysis:

    '''

    Configuration reliability with common cause, what another unit buys, and what reducing beta
    buys instead.

    '''

    def __init__(self):

        self.elementReliability = np.nan
        self.units              = np.nan
        self.sharing            = ''
        self.beta               = np.nan
        self.coverage           = np.nan
        self.standby            = False
        self.requiredReliability = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `elementReliability` is one unit's reliability over the mission.

        `sharing` selects a representative beta from BETA_FACTORS by how much the units share.
        `beta` overrides it with a specific value.

        `standby` marks the set as standby rather than active, which is where `coverage` applies:
        a standby unit that is not known to have failed is not there when it is called on.

        '''

        requiredParams = {'elementReliability': (int, float),
                          'units':              (int, float)}

        optionalParams = {'sharing':             str,
                          'beta':                (int, float),
                          'coverage':            (int, float),
                          'standby':             bool,
                          'requiredReliability': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.sharing:
            self.sharing = 'identicalDifferentLot'

        if not np.isfinite(self.coverage):
            self.coverage = DEFAULT_COVERAGE

        self._validateInputs()

        if not np.isfinite(self.beta):
            self.beta = BETA_FACTORS[self.sharing]['beta']

    # -------------------------------------------------------------------------------------------- #

    def calculateConfiguration(self, units: int = None, beta: float = None) -> dict:

        '''

        System reliability from the unit count and the common cause fraction.

        '''

        count = int(units if units is not None else self.units)
        share = beta if beta is not None else self.beta

        result = betaFactorReliability(self.elementReliability, count, share)

        result['commonCauseDominated'] = bool(result['commonCauseShare'] > COMMON_CAUSE_DOMINANCE)
        result['sharing'] = self.sharing

        # Standby redundancy only works if the failure of a running unit is detected, so the
        # benefit of every unit after the first is multiplied by the coverage.
        if self.standby and count > 1:

            covered = betaFactorReliability(self.elementReliability, count, share)
            uncovered = 1.0 - self.elementReliability

            effective = (self.coverage * covered['systemFailure']
                         + (1.0 - self.coverage) * uncovered)

            result['coverage'] = self.coverage
            result['coveredFailure'] = covered['systemFailure']
            result['effectiveFailure'] = effective
            result['effectiveReliability'] = 1.0 - effective
            result['coveragePenalty'] = effective / covered['systemFailure']

        return result

    # -------------------------------------------------------------------------------------------- #

    def unitSweep(self, maximum: int = 5) -> dict:

        '''

        What each additional unit buys.

        The table is the argument: the first duplication is worth a great deal, the second is worth
        very little, and the third is worth nothing at all, because the common cause term is
        already the answer.

        '''

        sweep = []

        for count in range(1, maximum + 1):

            entry = self.calculateConfiguration(units = count)

            previous = sweep[-1]['systemFailure'] if sweep else None

            sweep.append({'units':            count,
                          'systemFailure':    entry['systemFailure'],
                          'idealFailure':     entry['idealFailure'],
                          'commonCauseShare': entry['commonCauseShare'],
                          'penalty':          entry['penalty'],
                          'marginalGain':     (1.0 - entry['systemFailure'] / previous)
                                              if previous else 0.0})

        useful = [entry for entry in sweep[1:] if entry['marginalGain'] > MARGINAL_THRESHOLD]

        return {'sweep':            sweep,
                'usefulUnits':      (useful[-1]['units'] if useful else 1),
                'firstUnitGain':    sweep[1]['marginalGain'] if len(sweep) > 1 else 0.0,
                'lastUnitGain':     sweep[-1]['marginalGain'],
                'idealDivergence':  sweep[-1]['penalty']}

    # -------------------------------------------------------------------------------------------- #

    def betaSweep(self, sharings: list = None) -> dict:

        '''

        The same configuration at every level of sharing.

        **This is the lever that works.** At a fixed unit count the system failure probability is
        nearly proportional to beta once common cause dominates, so separating the units or
        diversifying them buys what another unit cannot.

        '''

        if sharings is None:
            sharings = list(BETA_FACTORS)

        results = []

        for sharing in sharings:

            entry = BETA_FACTORS[sharing]
            configuration = self.calculateConfiguration(beta = entry['beta'])

            results.append({'sharing':          sharing,
                            'beta':             entry['beta'],
                            'systemFailure':    configuration['systemFailure'],
                            'commonCauseShare': configuration['commonCauseShare'],
                            'note':             entry['note']})

        results.sort(key = lambda entry: entry['systemFailure'])

        return {'results': results,
                'best':    results[0]['sharing'],
                'spread':  results[-1]['systemFailure'] / results[0]['systemFailure']}

    # -------------------------------------------------------------------------------------------- #

    def compareLevers(self) -> dict:

        '''

        Another unit against a lower beta, at the same starting point.

        The comparison a redundancy design review should run and almost never does.

        '''

        baseline = self.calculateConfiguration()

        moreUnits = self.calculateConfiguration(units = int(self.units) + 1)

        # The next step down the sharing ladder, which is a physical separation or a diverse design
        # rather than an analysis change.
        ladder = sorted(BETA_FACTORS.items(), key = lambda item: item[1]['beta'], reverse = True)
        names = [name for name, _ in ladder]

        current = names.index(self.sharing) if self.sharing in names else 0
        better = names[min(current + 1, len(names) - 1)]

        lowerBeta = self.calculateConfiguration(beta = BETA_FACTORS[better]['beta'])

        unitGain = 1.0 - moreUnits['systemFailure'] / baseline['systemFailure']
        betaGain = 1.0 - lowerBeta['systemFailure'] / baseline['systemFailure']

        return {'baselineFailure':  baseline['systemFailure'],
                'extraUnitFailure': moreUnits['systemFailure'],
                'lowerBetaFailure': lowerBeta['systemFailure'],
                'currentSharing':   self.sharing,
                'betterSharing':    better,
                'unitGain':         unitGain,
                'betaGain':         betaGain,
                'betaWins':         bool(betaGain > unitGain),
                'ratio':            betaGain / unitGain if unitGain > 0.0 else np.inf}

    # -------------------------------------------------------------------------------------------- #

    def checkRequirement(self) -> dict:

        '''

        The configuration against a required reliability.

        Raises where a redundancy claim does not survive its own common cause, because reporting it
        as a small reduction invites somebody to keep calling it redundant.

        '''

        if not np.isfinite(self.requiredReliability):
            raise RedundancyError('A required reliability is needed to reach a verdict.')

        configuration = self.calculateConfiguration()

        achieved = (configuration.get('effectiveReliability')
                    if self.standby else configuration['systemReliability'])

        result = {'systemReliability':   achieved,
                  'requiredReliability': self.requiredReliability,
                  'idealReliability':    1.0 - configuration['idealFailure'],
                  'commonCauseShare':    configuration['commonCauseShare'],
                  'beta':                self.beta,
                  'margin':              (1.0 - self.requiredReliability)
                                         / (1.0 - achieved) if achieved < 1.0 else np.inf}

        if achieved < self.requiredReliability:

            ideal = 1.0 - configuration['idealFailure']

            raise RedundancyError(
                f'{int(self.units)} units at {self.elementReliability:.4f} reach {achieved:.6f} '
                f'against a required {self.requiredReliability:.6f}. **Without common cause they '
                f'would reach {ideal:.6f}**, so the requirement looks met on the ideal arithmetic '
                f'and is not. Common cause is '
                f'{configuration["commonCauseShare"] * 100.0:.0f} per cent of what remains, and '
                f'adding units will not move it: reduce beta instead.',
                context = {'units':             int(self.units),
                           'beta':              self.beta,
                           'systemReliability': achieved,
                           'idealReliability':  ideal})

        return result

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The unit sweep, the beta sweep, and the lever comparison.
        '''

        units = self.unitSweep()
        betas = self.betaSweep()
        levers = self.compareLevers()

        lines = []

        lines.append(formatReportTable(
            [[f'{entry["units"]}',
              f'{entry["systemFailure"]:.3e}',
              f'{entry["idealFailure"]:.3e}',
              f'{entry["commonCauseShare"] * 100.0:.0f}%',
              f'{entry["marginalGain"] * 100.0:.0f}%'] for entry in units['sweep']],
            ['units', 'Q with beta', 'Q ideal', 'common cause', 'gain from this unit'],
            title = f'REDUNDANCY AT BETA {self.beta:.2f}'))

        lines.append('')
        lines.append(f'Useful up to {units["usefulUnits"]} units. Beyond that the common cause '
                     f'term is the answer.')
        lines.append('')

        lines.append(formatReportTable(
            [[entry['sharing'],
              f'{entry["beta"]:.2f}',
              f'{entry["systemFailure"]:.3e}',
              f'{entry["commonCauseShare"] * 100.0:.0f}%'] for entry in betas['results']],
            ['sharing', 'beta', 'Q', 'common cause'],
            title = f'SHARING AT {int(self.units)} UNITS'))

        lines.append('')
        lines.append(f'Another unit buys {levers["unitGain"] * 100.0:.0f}%; moving from '
                     f'{levers["currentSharing"]} to {levers["betterSharing"]} buys '
                     f'{levers["betaGain"] * 100.0:.0f}%.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'redundancyAnalysis.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not 0.0 < self.elementReliability <= 1.0:
            raise InvalidInputError('Element reliability must lie above zero and at or below one.')

        if int(self.units) < 1:
            raise InvalidInputError('A redundant set has at least one unit.')

        if self.sharing not in BETA_FACTORS:
            raise InvalidInputError(
                f'{self.sharing} is not a sharing class. Available: {sorted(BETA_FACTORS)}.')

        if np.isfinite(self.beta) and not 0.0 <= self.beta < 1.0:
            raise InvalidInputError('Beta is a fraction at or above zero and below one.')

        if not 0.0 < self.coverage <= 1.0:
            raise InvalidInputError('Coverage is a fraction above zero and at or below one.')

        if np.isfinite(self.requiredReliability):
            if not 0.0 < self.requiredReliability < 1.0:
                raise InvalidInputError('Required reliability must lie strictly between zero and '
                                        'one.')
