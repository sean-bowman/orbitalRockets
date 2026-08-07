
# -- SampleSize Class Definition -- #

'''

Sample size and reliability demonstration.

The question this class answers is the one that decides how many articles a qualification programme
has to build: **how many units must be tested, with what result, to demonstrate a given reliability
at a given confidence?**

The core relationship is the success-run formula. Testing n units with zero failures demonstrates
reliability R at confidence C when

    n = ln(1 - C) / ln(R)

The consequence is brutal and worth internalizing before promising a number in a proposal:

    R = 0.90 at 90 percent confidence needs 22 units, all passing
    R = 0.99 at 90 percent confidence needs 230 units
    R = 0.999 at 95 percent confidence needs 2995 units

Nobody builds 2995 flight valves. This is why high reliability is never demonstrated by test alone;
it is argued from a combination of test, analysis, heritage, similarity and process control, and the
test contributes a bound rather than the number itself.

**The other direction is the useful one in practice.** Given the number of articles the programme can
actually afford, what reliability does a clean sweep demonstrate? That is an honest statement and it
is usually much weaker than people expect.

The class also covers the case with failures (binomial, requiring more units for the same claim) and
Weibull-based life demonstration, where testing longer substitutes for testing more.

See Also:
---------
LifeTest                        : What each of those units is subjected to
reliabilityAndMissionAssurance  : Where the demonstrated number feeds the reliability allocation

Theory: docs/UncertaintyAndStatistics.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (applyInputs, formatReportTable, secantSolve,
                               InvalidInputError, TestInfeasibleError, createErrorContext)
except ImportError:
    from .campaignUtils import (applyInputs, formatReportTable, secantSolve,
                                InvalidInputError, TestInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Reliability and confidence combinations commonly written into requirements, with the success-run
# sample size each demands. Provided so the cost of a requirement is visible while it is being
# written rather than after it has been baselined.
COMMON_REQUIREMENTS = {
    '0.90 at 50%':  (0.90, 0.50),
    '0.90 at 90%':  (0.90, 0.90),
    '0.95 at 90%':  (0.95, 0.90),
    '0.99 at 90%':  (0.99, 0.90),
    '0.99 at 95%':  (0.99, 0.95),
    '0.999 at 95%': (0.999, 0.95)
}

# Practical ceiling on articles a component qualification programme will build. Above this the
# reliability claim has to come from somewhere other than a demonstration test.
PRACTICAL_ARTICLE_LIMIT = 30

class SampleSize:

    '''

    Sample size for a reliability demonstration, and the reverse calculation.

    Primary Input Properties:
    -------------------------
    targetReliability : float
        The reliability to demonstrate, 0 to 1
    confidenceLevel : float
        The confidence level, 0 to 1
    allowedFailures : int
        Failures permitted during the demonstration. Zero is the success-run case.
    availableArticles : int
        Articles the programme can actually build, for the reverse calculation
    weibullShape : float
        Weibull shape parameter beta, for a life-based demonstration
    testDurationRatio : float
        Test duration as a multiple of the required life, for the Weibull trade

    Key Output Properties:
    ----------------------
    requiredSampleSize : int
        Units needed, with allowedFailures permitted
    demonstratedReliability : float
        What availableArticles actually demonstrates at the stated confidence
    weibullSampleSize : int
        Units needed when testing longer than the required life

    Public Methods:
    ---------------
    setInputs(inputs)                     Load a configuration dictionary
    calculateSuccessRun()                 n from R and C with zero failures
    calculateWithFailures()               n from R and C allowing failures (binomial)
    calculateDemonstrated()               The reverse: R from the articles available
    calculateWeibullTradeoff()            Testing longer instead of testing more
    compareRequirements()                 The cost of each common R and C combination
    generateReport(outputDir)             Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Requirement -- #

        self.targetReliability = np.nan  # [-], 0 to 1
        self.confidenceLevel   = 0.90    # [-], 0 to 1
        self.allowedFailures   = 0       # [-]

        # -- Programme Constraint -- #

        self.availableArticles = np.nan  # [-]

        # -- Weibull Life Demonstration -- #

        # Testing longer substitutes for testing more, but only when the failure mechanism is
        # wear-out (beta > 1). For a random failure mechanism (beta = 1) extra duration buys nothing.
        self.weibullShape      = np.nan  # [-], beta
        self.testDurationRatio = np.nan  # [-], test duration over required life

        # -- Results -- #

        self.requiredSampleSize      = np.nan  # [-]
        self.demonstratedReliability = np.nan  # [-]
        self.weibullSampleSize       = np.nan  # [-]
        self.designNotes             = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: targetReliability.

        '''

        requiredParams = {
            'targetReliability': 'Target reliability not provided.'
        }

        optionalParams = ['confidenceLevel', 'allowedFailures', 'availableArticles',
                          'weibullShape', 'testDurationRatio']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateSuccessRun(self) -> dict:

        '''

        Sample size for a zero-failure demonstration.

            n = ln(1 - C) / ln(R)

        This is the cheapest possible demonstration and it still costs more than most people expect.
        The formula comes from requiring that the probability of observing n consecutive successes
        from a population with true reliability R is no more than (1 - C):

            R^n <= 1 - C

        so any programme that observes n successes can state, at confidence C, that reliability is at
        least R.

        The class flags the case where the required sample exceeds what a component qualification
        programme realistically builds, because that is a requirement problem rather than a test
        problem and it should be raised while the requirement is still negotiable.

        '''

        sampleSize = np.log(1.0 - self.confidenceLevel) / np.log(self.targetReliability)
        self.requiredSampleSize = int(np.ceil(sampleSize))

        if self.requiredSampleSize > PRACTICAL_ARTICLE_LIMIT:
            self.designNotes.append(
                f'Demonstrating R = {self.targetReliability:.4g} at {self.confidenceLevel * 100.0:.0f} percent '
                f'confidence needs {self.requiredSampleSize} units tested with zero failures. That is beyond what a '
                f'component qualification programme builds, so this reliability cannot come from a demonstration '
                f'test. It has to be argued from test plus analysis plus heritage plus process control, with the '
                f'test contributing a bound rather than the number.')

        return {
            'targetReliability':  self.targetReliability,
            'confidenceLevel':    self.confidenceLevel,
            'requiredSampleSize': self.requiredSampleSize,
            'practical':          self.requiredSampleSize <= PRACTICAL_ARTICLE_LIMIT
        }

    def calculateWithFailures(self) -> dict:

        '''

        Sample size when failures are permitted, using the binomial distribution.

        The demonstration succeeds if the observed number of failures is at most `allowedFailures`.
        The required n solves

            sum_{i=0}^{f} C(n, i) * (1-R)^i * R^(n-i)  =  1 - C

        Allowing even one failure raises the required sample size substantially, which is why a
        qualification programme almost always specifies zero failures and treats any failure as a
        stop-and-investigate rather than as a budgeted allowance.

        '''

        if self.allowedFailures == 0:
            return self.calculateSuccessRun()

        from math import comb

        def cumulativeProbability(sampleSize: float) -> float:
            '''Probability of at most allowedFailures failures in n trials, minus (1 - C).'''
            n = int(np.ceil(sampleSize))
            total = sum(comb(n, i) * (1.0 - self.targetReliability)**i *
                        self.targetReliability**(n - i)
                        for i in range(self.allowedFailures + 1))
            return total - (1.0 - self.confidenceLevel)

        # The zero-failure answer is a lower bound; search upward from it
        lowerBound = int(np.ceil(np.log(1.0 - self.confidenceLevel) / np.log(self.targetReliability)))

        sampleSize = lowerBound
        for candidate in range(lowerBound, lowerBound * 100 + 100):
            if cumulativeProbability(candidate) <= 0.0:
                sampleSize = candidate
                break

        self.requiredSampleSize = sampleSize

        zeroFailureSize = lowerBound
        self.designNotes.append(
            f'Allowing {self.allowedFailures} failure(s) raises the sample from {zeroFailureSize} to '
            f'{sampleSize} units. A qualification programme almost always specifies zero failures and treats any '
            f'failure as a stop-and-investigate rather than a budgeted allowance.')

        return {
            'targetReliability':  self.targetReliability,
            'confidenceLevel':    self.confidenceLevel,
            'allowedFailures':    self.allowedFailures,
            'requiredSampleSize': self.requiredSampleSize,
            'zeroFailureSize':    zeroFailureSize
        }

    def calculateDemonstrated(self) -> dict:

        '''

        The reverse calculation: what reliability does a clean sweep of the articles available
        actually demonstrate?

            R = (1 - C)^(1/n)

        **This is the honest statement** and it is usually much weaker than the requirement it is
        being used to close. Three units passing demonstrates R = 0.46 at 90 percent confidence,
        which is not a number anybody wants to write down, and that gap is precisely why reliability
        claims rest on more than demonstration testing.

        '''

        if np.isnan(self.availableArticles) or self.availableArticles < 1:
            raise InvalidInputError(
                message       = 'calculateDemonstrated needs the number of articles available.',
                parameterName = 'availableArticles', value = self.availableArticles,
                validRange    = '1 or greater'
            )

        articles = int(self.availableArticles)
        self.demonstratedReliability = float((1.0 - self.confidenceLevel)**(1.0 / articles))

        shortfall = None
        if not np.isnan(self.targetReliability):
            shortfall = self.demonstratedReliability < self.targetReliability
            if shortfall:
                self.designNotes.append(
                    f'{articles} units passing demonstrates R = {self.demonstratedReliability:.4f} at '
                    f'{self.confidenceLevel * 100.0:.0f} percent confidence, against a target of '
                    f'{self.targetReliability:.4f}. The test alone does not close the requirement, and the gap has '
                    f'to be argued rather than asserted.')

        return {
            'availableArticles':       articles,
            'confidenceLevel':         self.confidenceLevel,
            'demonstratedReliability': self.demonstratedReliability,
            'targetReliability':       self.targetReliability,
            'shortfall':               shortfall
        }

    def calculateWeibullTradeoff(self) -> dict:

        '''

        Testing longer instead of testing more, for a wear-out failure mechanism.

        When failures follow a Weibull distribution with shape parameter beta, testing each unit for
        a multiple of the required life reduces the number of units needed:

            n = ln(1 - C) / ( ratio^beta * ln(R) )

        **This only works when beta is greater than 1**, meaning the failure mechanism is wear-out.
        For beta = 1 the failures are random and memoryless, extra duration buys nothing, and the
        expression collapses to the success-run result.

        The trade is genuinely useful for seals, bearings and anything with a wear mechanism, and it
        is precisely wrong for anything whose failures are random. Applying it without establishing
        beta from data is a common and expensive error.

        '''

        if np.isnan(self.weibullShape) or np.isnan(self.testDurationRatio):
            raise InvalidInputError(
                message       = 'calculateWeibullTradeoff needs weibullShape (beta) and testDurationRatio.',
                parameterName = 'weibullShape/testDurationRatio',
                value         = (self.weibullShape, self.testDurationRatio),
                validRange    = 'beta > 0, ratio > 0'
            )

        if self.weibullShape <= 1.0:
            self.designNotes.append(
                f'A Weibull shape of {self.weibullShape:.2f} means the failure mechanism is random or '
                f'infant-mortality rather than wear-out. Testing longer buys little or nothing, and at beta = 1 it '
                f'buys exactly nothing. The duration trade only works for a wear-out mechanism.')

        denominator = self.testDurationRatio**self.weibullShape * np.log(self.targetReliability)
        sampleSize  = np.log(1.0 - self.confidenceLevel) / denominator

        self.weibullSampleSize = max(1, int(np.ceil(sampleSize)))

        successRunSize = int(np.ceil(np.log(1.0 - self.confidenceLevel) / np.log(self.targetReliability)))

        return {
            'weibullShape':       self.weibullShape,
            'testDurationRatio':  self.testDurationRatio,
            'weibullSampleSize':  self.weibullSampleSize,
            'successRunSize':     successRunSize,
            'unitsSaved':         successRunSize - self.weibullSampleSize
        }

    def compareRequirements(self) -> str:

        '''

        The sample size cost of each commonly written reliability and confidence combination.

        Worth running while a requirement is being drafted rather than after it is baselined. The
        jump from R = 0.95 to R = 0.99 at the same confidence is a factor of five in articles, and
        the jump to R = 0.999 is a factor of fifty.

        '''

        rows = []
        for label, (reliability, confidence) in COMMON_REQUIREMENTS.items():
            sampleSize = int(np.ceil(np.log(1.0 - confidence) / np.log(reliability)))
            practical  = 'yes' if sampleSize <= PRACTICAL_ARTICLE_LIMIT else 'NO'
            rows.append([label, f'{reliability:.4g}', f'{confidence * 100.0:.0f}', f'{sampleSize:d}', practical])

        return formatReportTable(
            rows, ['Requirement', 'R', 'C [%]', 'Units, zero failures', 'Practical'],
            title = 'THE COST OF A RELIABILITY REQUIREMENT')

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        rows = [
            ['Target reliability', f'{self.targetReliability:.5g}'],
            ['Confidence level',   f'{self.confidenceLevel * 100.0:.1f} %'],
            ['Allowed failures',   f'{self.allowedFailures:d}']
        ]

        if not np.isnan(self.requiredSampleSize):
            rows.append(['Required sample size', f'{self.requiredSampleSize:d} units'])
        if not np.isnan(self.availableArticles):
            rows.append(['Articles available',   f'{int(self.availableArticles):d}'])
        if not np.isnan(self.demonstratedReliability):
            rows.append(['Demonstrated R',       f'{self.demonstratedReliability:.5f}'])
        if not np.isnan(self.weibullSampleSize):
            rows.append(['Weibull shape beta',   f'{self.weibullShape:.3f}'])
            rows.append(['Test duration ratio',  f'{self.testDurationRatio:.2f}x required life'])
            rows.append(['Weibull sample size',  f'{self.weibullSampleSize:d} units'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'RELIABILITY DEMONSTRATION')

        report += '\n\n' + self.compareRequirements()

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'sampleSizeReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if not 0.0 < self.targetReliability < 1.0:
            raise InvalidInputError(
                message       = 'Target reliability must lie strictly between 0 and 1. A reliability of exactly 1 '
                                'cannot be demonstrated by any finite number of tests.',
                parameterName = 'targetReliability', value = self.targetReliability,
                validRange    = 'Greater than 0 and less than 1'
            )

        if not 0.0 < self.confidenceLevel < 1.0:
            raise InvalidInputError(
                message       = 'Confidence level must lie strictly between 0 and 1.',
                parameterName = 'confidenceLevel', value = self.confidenceLevel,
                validRange    = 'Greater than 0 and less than 1'
            )

        if self.allowedFailures < 0:
            raise InvalidInputError(
                message       = 'Allowed failures cannot be negative.',
                parameterName = 'allowedFailures', value = self.allowedFailures,
                validRange    = '0 or greater'
            )
