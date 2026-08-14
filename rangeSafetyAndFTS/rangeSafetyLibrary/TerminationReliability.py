
# -- TerminationReliability -- #

'''

The reliability claim that cannot be demonstrated, and what is done instead.

14 CFR 450.145 requires a flight safety system with **a design reliability of 0.999 at 95 per cent
confidence**, for the onboard and the off-vehicle portions both. That single pair of numbers shapes
the entire subject, and the reason is one line of binomial arithmetic.

With zero failures in n tests, the lower confidence bound on reliability is (1 - C) ** (1/n), so

    n = ln(1 - C) / ln(R) = ln(0.05) / ln(0.999) = 2,995

**Demonstrating 0.999 at 95 per cent confidence by test alone takes about three thousand successful
firings of a single-use ordnance system.** Nobody has ever done that and nobody ever will: the
articles are consumed by the test, the cost is prohibitive, and a three thousand unit lot would not
be the lot that flies.

So the claim is not demonstrated. **It is argued**, from redundancy, from parts with their own
qualification histories, from environmental testing to margin, and from an end-to-end test of the
actual flight article that proves the path rather than the rate.

That is not a weakness in the regulation. It is the only available answer, and knowing the
arithmetic behind it is the difference between understanding the requirement and reciting it.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from rangeSafetyUtils import (FLIGHT_SAFETY_RELIABILITY, FLIGHT_SAFETY_CONFIDENCE,
                                  zeroFailureTestCount,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, TerminationError)
except ImportError:
    from .rangeSafetyUtils import (FLIGHT_SAFETY_RELIABILITY, FLIGHT_SAFETY_CONFIDENCE,
                                   zeroFailureTestCount,
                                   applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, TerminationError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# A flight termination system is built from series and parallel elements, and the two behave in
# opposite directions.
#
# **Anything in series with the termination path reduces reliability**: a receiver, a battery, a
# safe and arm device. **Anything in parallel raises it**, which is why the ordnance, the receivers
# and the batteries are all doubled.
#
# The two-out-of-two case is the one that catches people: an initiator pair wired so that BOTH must
# fire to sever the charge is a series pair, and doubling it has made the system worse.
REDUNDANCY_TYPES = {
    'single':      {'paths': 1, 'requires': 1, 'note': 'no redundancy'},
    'dualParallel':{'paths': 2, 'requires': 1, 'note': 'either path terminates; the usual FTS case'},
    'dualSeries':  {'paths': 2, 'requires': 2, 'note': 'both must work, which is worse than one'},
    'tripleVote':  {'paths': 3, 'requires': 2, 'note': 'two of three, which trades misfire against no-fire'},
}

# ------------------------------------------------------------------------------------------------ #
# -- TerminationReliability -- #
# ------------------------------------------------------------------------------------------------ #

class TerminationReliability:

    '''

    The demonstration arithmetic, the redundancy arithmetic, and the check against 14 CFR 450.145.

    '''

    def __init__(self):

        self.elementReliability = np.nan
        self.configuration      = ''
        self.seriesElements     = {}
        self.requiredReliability = np.nan
        self.requiredConfidence  = np.nan
        self.testsAvailable      = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `elementReliability` is the reliability of one termination path.

        `configuration` is a key of REDUNDANCY_TYPES, describing how the paths are combined.

        `seriesElements` maps a name to a reliability for anything the whole system depends on, such
        as a command receiver or a battery. **Those multiply the answer down** and they are where a
        redundant system quietly stops being redundant.

        `requiredReliability` and `requiredConfidence` default to the regulation.

        '''

        requiredParams = {'elementReliability': (int, float)}

        optionalParams = {'configuration':       str,
                          'seriesElements':      dict,
                          'requiredReliability': (int, float),
                          'requiredConfidence':  (int, float),
                          'testsAvailable':      (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.configuration:
            self.configuration = 'dualParallel'

        if self.seriesElements is None or isinstance(self.seriesElements, float):
            self.seriesElements = {}

        if not np.isfinite(self.requiredReliability):
            self.requiredReliability = FLIGHT_SAFETY_RELIABILITY

        if not np.isfinite(self.requiredConfidence):
            self.requiredConfidence = FLIGHT_SAFETY_CONFIDENCE

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def demonstrationSize(self, reliability: float = None, confidence: float = None) -> dict:

        '''

        How many successful tests, with no failures, a reliability claim needs.

        **This is the arithmetic that shapes the subject.** It is one line and it explains why an
        FTS reliability is argued rather than demonstrated.

        '''

        target = reliability if reliability is not None else self.requiredReliability
        level = confidence if confidence is not None else self.requiredConfidence

        needed = zeroFailureTestCount(target, level)

        result = {'reliability':      target,
                  'confidence':       level,
                  'testsRequired':    needed,
                  'demonstrable':     False}

        if np.isfinite(self.testsAvailable):

            result['testsAvailable'] = self.testsAvailable
            result['shortfall'] = needed - self.testsAvailable

            # What a realistic test programme actually demonstrates, which is the useful inversion.
            result['demonstratedReliability'] = float(
                (1.0 - level) ** (1.0 / self.testsAvailable)) if self.testsAvailable > 0 else 0.0

            result['demonstrable'] = self.testsAvailable >= needed

        return result

    # -------------------------------------------------------------------------------------------- #

    def demonstrationLadder(self, reliabilities: list = None) -> dict:

        '''

        Tests required against the reliability claimed, at a fixed confidence.

        The shape is the point: the count grows without limit as the claim approaches one, and it
        is already impractical at three nines.

        '''

        if reliabilities is None:
            reliabilities = [0.90, 0.99, 0.999, 0.9999]

        ladder = [{'reliability':   value,
                   'testsRequired': zeroFailureTestCount(value, self.requiredConfidence)}
                  for value in reliabilities]

        return {'ladder':      ladder,
                'confidence':  self.requiredConfidence,
                'perNine':     ladder[-1]['testsRequired'] / ladder[-2]['testsRequired']}

    # -------------------------------------------------------------------------------------------- #

    def configurationReliability(self, configuration: str = None) -> dict:

        '''

        System reliability from the path configuration and anything in series with it.

        The series elements are where the interesting failure lives. **A dual redundant ordnance
        train behind a single command receiver is a single string system**, and its reliability is
        the receiver's, whatever the ordnance does.

        '''

        name = configuration if configuration else self.configuration
        entry = REDUNDANCY_TYPES[name]

        element = self.elementReliability
        paths = entry['paths']
        requires = entry['requires']

        # k out of n with identical elements.
        from math import comb

        pathReliability = sum(comb(paths, count) * element ** count
                              * (1.0 - element) ** (paths - count)
                              for count in range(requires, paths + 1))

        seriesProduct = 1.0
        seriesEntries = []

        for elementName, reliability in self.seriesElements.items():
            seriesProduct *= float(reliability)
            seriesEntries.append({'element': elementName, 'reliability': float(reliability)})

        system = pathReliability * seriesProduct

        seriesEntries.sort(key = lambda item: item['reliability'])

        return {'configuration':     name,
                'paths':             paths,
                'requires':          requires,
                'elementReliability': element,
                'pathReliability':   float(pathReliability),
                'seriesElements':    seriesEntries,
                'seriesProduct':     seriesProduct,
                'systemReliability': float(system),
                'redundancyGain':    float(pathReliability) / element,
                'seriesLoss':        1.0 - seriesProduct,
                'weakestSeries':     seriesEntries[0]['element'] if seriesEntries else None,
                'note':              entry['note']}

    # -------------------------------------------------------------------------------------------- #

    def compareConfigurations(self) -> dict:

        '''

        Every configuration at the same element reliability.

        The result worth having is that **a two out of two series pair is worse than a single
        path**, which is not what the word redundant suggests and is a real wiring mistake: an
        initiator pair that must both fire to sever a charge has doubled the number of things that
        can stop it.

        '''

        results = []

        for name in REDUNDANCY_TYPES:

            entry = self.configurationReliability(name)

            results.append({'configuration':     name,
                            'paths':             entry['paths'],
                            'requires':          entry['requires'],
                            'pathReliability':   entry['pathReliability'],
                            'systemReliability': entry['systemReliability'],
                            'betterThanSingle':  bool(name == 'single'
                                                     or entry['pathReliability']
                                                     > self.elementReliability),
                            'note':              entry['note']})

        results.sort(key = lambda entry: entry['pathReliability'], reverse = True)

        worse = [entry for entry in results if not entry['betterThanSingle']
                 and entry['configuration'] != 'single']

        return {'results':        results,
                'best':           results[0]['configuration'],
                'worseThanSingle': [entry['configuration'] for entry in worse]}

    # -------------------------------------------------------------------------------------------- #

    def checkRequirement(self) -> dict:

        '''

        The system against 14 CFR 450.145.

        Raises where it falls short, because a flight safety system that does not meet the
        requirement is a launch that does not get a licence rather than a design with a margin to
        argue about.

        '''

        configuration = self.configurationReliability()
        demonstration = self.demonstrationSize()

        system = configuration['systemReliability']

        result = {'systemReliability':   system,
                  'requiredReliability': self.requiredReliability,
                  'requiredConfidence':  self.requiredConfidence,
                  'margin':              (1.0 - self.requiredReliability) / (1.0 - system)
                                         if system < 1.0 else np.inf,
                  'testsForClaim':       demonstration['testsRequired'],
                  'configuration':       configuration['configuration'],
                  'weakestSeries':       configuration['weakestSeries']}

        if system < self.requiredReliability:
            raise TerminationError(
                f'The system reaches {system:.5f} against a required '
                f'{self.requiredReliability:.3f} at {self.requiredConfidence:.0%} confidence. '
                f'The path configuration gives {configuration["pathReliability"]:.5f} and the '
                f'series elements take it down by {configuration["seriesLoss"]:.5f}, with '
                f'{configuration["weakestSeries"]} the weakest. **A redundant ordnance train '
                f'behind a single series element is a single string system.**',
                context = {'systemReliability':   system,
                           'pathReliability':     configuration['pathReliability'],
                           'weakestSeries':       configuration['weakestSeries'],
                           'requiredReliability': self.requiredReliability})

        return result

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The demonstration arithmetic, the configuration comparison, and the requirement check.
        '''

        ladder = self.demonstrationLadder()
        comparison = self.compareConfigurations()

        lines = []

        lines.append(formatReportTable(
            [[f'{entry["reliability"]:.4f}', f'{entry["testsRequired"]:,.0f}']
             for entry in ladder['ladder']],
            ['reliability claimed', 'successful tests needed'],
            title = f'ZERO FAILURE DEMONSTRATION AT {ladder["confidence"]:.0%} CONFIDENCE'))

        lines.append('')
        lines.append(f'Each additional nine costs {ladder["perNine"]:.0f} times the tests.')
        lines.append('')

        lines.append(formatReportTable(
            [[entry['configuration'],
              f'{entry["paths"]} of {entry["requires"]}',
              f'{entry["pathReliability"]:.5f}',
              f'{entry["systemReliability"]:.5f}',
              '' if entry['betterThanSingle'] else 'worse than single']
             for entry in comparison['results']],
            ['configuration', 'paths', 'path R', 'system R', 'note'],
            title = 'CONFIGURATIONS'))

        lines.append('')

        try:
            check = self.checkRequirement()
            lines.append(f'System {check["systemReliability"]:.5f} against a required '
                         f'{check["requiredReliability"]:.3f}, margin {check["margin"]:.2f}.')
        except TerminationError as error:
            lines.append('REQUIREMENT NOT MET')
            lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'terminationReliability.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not 0.0 < self.elementReliability < 1.0:
            raise InvalidInputError('Element reliability must lie strictly between zero and one. A '
                                    'reliability of exactly one is a claim rather than a number.')

        if self.configuration not in REDUNDANCY_TYPES:
            raise InvalidInputError(
                f'{self.configuration} is not a configuration. Available: '
                f'{sorted(REDUNDANCY_TYPES)}.')

        for name, reliability in self.seriesElements.items():
            if not 0.0 < float(reliability) <= 1.0:
                raise InvalidInputError(f'Series element {name} has a reliability outside zero to '
                                        f'one.')

        if not 0.0 < self.requiredReliability < 1.0:
            raise InvalidInputError('Required reliability must lie strictly between zero and one.')

        if not 0.0 < self.requiredConfidence < 1.0:
            raise InvalidInputError('Required confidence must lie strictly between zero and one.')

        if np.isfinite(self.testsAvailable) and self.testsAvailable < 0.0:
            raise InvalidInputError('Test count cannot be negative.')
