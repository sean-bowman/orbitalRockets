
# -- UncertaintyBudget Class Definition -- #

'''

Measurement uncertainty budget, following the GUM method.

A test result without an uncertainty is not a measurement, it is a number. This class builds the
budget that turns one into the other, and it identifies which contributor actually dominates, which
is almost always the useful output.

The GUM (Guide to the Expression of Uncertainty in Measurement) method, in the form used here:

1. Write the measurement equation, y = f(x1, x2, ... xn)
2. For each input, estimate its standard uncertainty u(xi) from its distribution
3. Compute the sensitivity coefficient ci = dy/dxi, either analytically or numerically
4. Combine: uc(y) = sqrt( sum( (ci * u(xi))^2 ) )
5. Expand: U = k * uc(y), with k = 2 for approximately 95 percent coverage

**Type A and Type B are about how the uncertainty was evaluated, not what kind it is.** Type A comes
from statistical analysis of repeated observations; Type B comes from everything else: a calibration
certificate, a manufacturer specification, engineering judgement. Both are standard uncertainties and
both combine the same way. The distinction exists for traceability, not for the arithmetic.

**Distribution matters when converting a stated tolerance into a standard uncertainty.** A
calibration certificate quoting plus or minus a value at k=2 divides by 2. A manufacturer tolerance
with no distribution stated is treated as rectangular and divides by sqrt(3). Getting this wrong is
the most common error in a budget and it is always in the unconservative direction.

The dominant-contributor output is what makes a budget actionable. If one term is 80 percent of the
combined uncertainty, improving anything else is wasted effort.

See Also:
---------
LeakTest / PressureTest : The measurements this budget applies to
SampleSize              : Statistical confidence in the result, rather than in the measurement

Theory: docs/UncertaintyAndStatistics.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (applyInputs, formatReportTable, InvalidInputError, createErrorContext)
except ImportError:
    from .campaignUtils import (applyInputs, formatReportTable, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Divisors that convert a stated half-width into a standard uncertainty, by assumed distribution.
#
# The rectangular case is the one that matters in practice: a manufacturer tolerance with no
# distribution stated is rectangular, and dividing by sqrt(3) rather than treating the half-width as
# a standard uncertainty is the difference between a defensible budget and an optimistic one.
DISTRIBUTION_DIVISORS = {
    'normal k=1':    1.0,             # a standard uncertainty already
    'normal k=2':    2.0,             # a calibration certificate at 95 percent coverage
    'normal k=3':    3.0,
    'rectangular':   np.sqrt(3.0),    # a tolerance band with no distribution stated
    'triangular':    np.sqrt(6.0),    # a tolerance where the centre is more likely
    'u-shaped':      np.sqrt(2.0)     # a cyclic effect such as temperature control oscillation
}

# Coverage factor for the expanded uncertainty. k = 2 gives approximately 95 percent coverage for a
# normally distributed result, which is the usual reporting convention.
DEFAULT_COVERAGE_FACTOR = 2.0

# A contributor above this fraction of the combined variance is called dominant, because improving
# anything else will not move the result.
DOMINANCE_THRESHOLD = 0.5

class UncertaintyBudget:

    '''

    GUM measurement uncertainty budget.

    Primary Input Properties:
    -------------------------
    measurand : str
        What is being measured, for the report
    measurandValue : float
        The measured or nominal value
    measurandUnit : str
        Its unit, for the report
    coverageFactor : float
        Expansion factor k. Defaults to 2 for approximately 95 percent coverage.

    Contributors are added with addContributor() rather than through setInputs, because a budget is
    built up term by term.

    Key Output Properties:
    ----------------------
    combinedUncertainty : float
        uc(y), the root-sum-square of the weighted contributions
    expandedUncertainty : float
        U = k * uc(y)
    relativeExpandedUncertainty : float
        U / measurandValue [-]
    dominantContributor : str
        The contributor with the largest share of the combined variance
    contributions : list
        Every contributor with its standard uncertainty, sensitivity, contribution and share

    Public Methods:
    ---------------
    setInputs(inputs)                              Load a configuration dictionary
    addContributor(name, value, distribution, ...)  Add one term to the budget
    calculate()                                    Combine and expand
    generateReport(outputDir)                      Formatted budget table

    Typical Workflow:
    -----------------
    >>> budget = UncertaintyBudget()
    >>> budget.setInputs({'measurand': 'mass flow', 'measurandValue': 0.046,
    ...                   'measurandUnit': 'kg/s'})
    >>> budget.addContributor('transducer calibration', 0.0025, 'normal k=2',
    ...                       sensitivity = 1.0, evaluationType = 'B')
    >>> budget.addContributor('temperature effect', 0.004, 'rectangular',
    ...                       sensitivity = 1.0, evaluationType = 'B')
    >>> budget.addContributor('repeatability', 0.0015, 'normal k=1',
    ...                       sensitivity = 1.0, evaluationType = 'A')
    >>> budget.calculate()
    >>> print(budget.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Measurand -- #

        self.measurand      = ''      # what is being measured
        self.measurandValue = np.nan  # the measured or nominal value
        self.measurandUnit  = ''      # its unit
        self.coverageFactor = np.nan  # [-], defaults to DEFAULT_COVERAGE_FACTOR

        # -- Contributors -- #

        # Each entry: name, halfWidth, distribution, standardUncertainty, sensitivity,
        # contribution, evaluationType, note
        self.contributors = []

        # -- Results -- #

        self.combinedUncertainty         = np.nan  # uc(y)
        self.expandedUncertainty         = np.nan  # U = k * uc(y)
        self.relativeExpandedUncertainty = np.nan  # [-]
        self.dominantContributor         = ''      # name
        self.dominantShare               = np.nan  # [-]
        self.contributions               = []      # the fully evaluated table
        self.designNotes                 = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load the measurand definition. Contributors are added separately with addContributor().

        '''

        requiredParams = {
            'measurand':      'Measurand not provided. Name what is being measured.',
            'measurandValue': 'Measurand value not provided.'
        }

        optionalParams = ['measurandUnit', 'coverageFactor']

        applyInputs(self, inputs, requiredParams, optionalParams)

    def addContributor(self, name: str, halfWidth: float, distribution: str = 'rectangular',
                       sensitivity: float = 1.0, evaluationType: str = 'B',
                       isRelative: bool = False, note: str = '') -> None:

        '''

        Add one uncertainty contributor to the budget.

        ---------------------------------------------------------------------------
                                        INPUTS
        ---------------------------------------------------------------------------
        - name            What this term is, for the report
        - halfWidth       The stated half-width of the uncertainty, in the measurand's unit, or as a
                          fraction if isRelative is True
        - distribution    Key into DISTRIBUTION_DIVISORS. **This is the input most often got wrong.**
                          A calibration certificate stating plus or minus a value at 95 percent
                          coverage is 'normal k=2'. A manufacturer tolerance with no distribution
                          stated is 'rectangular'. Treating a rectangular half-width as a standard
                          uncertainty overstates confidence by a factor of 1.73.
        - sensitivity     The sensitivity coefficient ci = dy/dxi. Unity when the contributor is
                          already expressed in the measurand's unit, which is the common case.
        - evaluationType  'A' for a term evaluated statistically from repeated observations, 'B' for
                          everything else. This is about how it was evaluated, not what kind it is,
                          and it does not change the arithmetic.
        - isRelative      True if halfWidth is a fraction of the measurand rather than an absolute
        - note            Free text, typically the source: a certificate number or a datasheet

        '''

        if distribution.strip().lower() not in DISTRIBUTION_DIVISORS:
            raise InvalidInputError(
                message       = f'Unknown distribution \'{distribution}\'.',
                parameterName = 'distribution', value = distribution,
                validRange    = str(sorted(DISTRIBUTION_DIVISORS.keys()))
            )

        if evaluationType.strip().upper() not in ('A', 'B'):
            raise InvalidInputError(
                message       = 'Evaluation type must be A (statistical) or B (everything else).',
                parameterName = 'evaluationType', value = evaluationType, validRange = 'A or B'
            )

        absoluteHalfWidth = halfWidth * self.measurandValue if isRelative else halfWidth

        self.contributors.append({
            'name':           name,
            'halfWidth':      absoluteHalfWidth,
            'distribution':   distribution.strip().lower(),
            'sensitivity':    sensitivity,
            'evaluationType': evaluationType.strip().upper(),
            'note':           note
        })

    def calculate(self) -> dict:

        '''

        Combine the contributors and expand.

            u(xi) = halfWidth / divisor(distribution)
            uc(y) = sqrt( sum( (ci * u(xi))^2 ) )
            U     = k * uc(y)

        The root-sum-square combination assumes the contributors are independent. Correlated
        contributors need a covariance term, and the usual practical response is to combine them into
        a single term rather than to estimate a correlation coefficient nobody can defend.

        The dominant-contributor identification is what makes the budget actionable. Because the
        combination is in quadrature, a term at half the magnitude of the largest contributes only a
        quarter as much variance, so effort spent improving it is largely wasted.

        '''

        if not self.contributors:
            raise InvalidInputError(
                message       = 'The budget has no contributors. Add them with addContributor().',
                parameterName = 'contributors', value = [], validRange = 'At least one contributor'
            )

        coverageFactor = (self.coverageFactor if not np.isnan(self.coverageFactor)
                          else DEFAULT_COVERAGE_FACTOR)

        self.contributions = []
        totalVariance      = 0.0

        for contributor in self.contributors:

            divisor              = DISTRIBUTION_DIVISORS[contributor['distribution']]
            standardUncertainty  = contributor['halfWidth'] / divisor
            contribution         = contributor['sensitivity'] * standardUncertainty
            variance             = contribution**2

            totalVariance += variance

            self.contributions.append({
                'name':                contributor['name'],
                'halfWidth':           contributor['halfWidth'],
                'distribution':        contributor['distribution'],
                'divisor':             divisor,
                'standardUncertainty': standardUncertainty,
                'sensitivity':         contributor['sensitivity'],
                'contribution':        contribution,
                'variance':            variance,
                'evaluationType':      contributor['evaluationType'],
                'note':                contributor['note']
            })

        self.combinedUncertainty = float(np.sqrt(totalVariance))
        self.expandedUncertainty = coverageFactor * self.combinedUncertainty

        if self.measurandValue not in (0.0, None) and not np.isnan(self.measurandValue):
            self.relativeExpandedUncertainty = self.expandedUncertainty / abs(self.measurandValue)

        # Share of the combined variance, which is what determines where effort should go
        for entry in self.contributions:
            entry['share'] = entry['variance'] / totalVariance if totalVariance > 0.0 else 0.0

        self.contributions.sort(key = lambda entry: -entry['share'])

        dominant                 = self.contributions[0]
        self.dominantContributor = dominant['name']
        self.dominantShare       = dominant['share']

        if self.dominantShare >= DOMINANCE_THRESHOLD:
            self.designNotes.append(
                f'\'{self.dominantContributor}\' is {self.dominantShare * 100.0:.0f} percent of the combined '
                f'variance. Because the terms combine in quadrature, improving anything else will barely move the '
                f'result. If this uncertainty needs to come down, that is the term to attack.')

        rectangularTerms = [entry['name'] for entry in self.contributions
                            if entry['distribution'] == 'rectangular']
        if rectangularTerms:
            self.designNotes.append(
                f'Treated as rectangular (divided by sqrt(3)): {", ".join(rectangularTerms)}. If any of these came '
                f'from a calibration certificate stating a coverage factor, use the stated k instead; rectangular '
                f'is the assumption for a bare tolerance with no distribution given.')

        return {
            'combinedUncertainty':         self.combinedUncertainty,
            'coverageFactor':              coverageFactor,
            'expandedUncertainty':         self.expandedUncertainty,
            'relativeExpandedUncertainty': self.relativeExpandedUncertainty,
            'dominantContributor':         self.dominantContributor,
            'dominantShare':               self.dominantShare,
            'contributions':               self.contributions
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build the budget table, sorted by contribution share.

        '''

        coverageFactor = (self.coverageFactor if not np.isnan(self.coverageFactor)
                          else DEFAULT_COVERAGE_FACTOR)

        rows = []
        for entry in self.contributions:
            rows.append([
                entry['name'],
                entry['evaluationType'],
                f'{entry["halfWidth"]:.5g}',
                entry['distribution'],
                f'{entry["standardUncertainty"]:.5g}',
                f'{entry["sensitivity"]:.4g}',
                f'{entry["contribution"]:.5g}',
                f'{entry["share"] * 100.0:.1f}'
            ])

        report = formatReportTable(
            rows,
            ['Contributor', 'Type', 'Half width', 'Distribution', 'u(xi)', 'ci', 'ci*u(xi)', 'Share [%]'],
            title = f'UNCERTAINTY BUDGET -- {self.measurand}')

        summaryRows = [
            ['Measurand',              f'{self.measurand}'],
            ['Value',                  f'{self.measurandValue:.6g} {self.measurandUnit}'],
            ['Combined uncertainty',   f'{self.combinedUncertainty:.6g} {self.measurandUnit}'],
            ['Coverage factor',        f'k = {coverageFactor:.1f}'],
            ['Expanded uncertainty',   f'{self.expandedUncertainty:.6g} {self.measurandUnit}'],
            ['Relative expanded',      f'{self.relativeExpandedUncertainty * 100.0:.3f} %'
                                       if not np.isnan(self.relativeExpandedUncertainty) else 'n/a'],
            ['Result',                 f'{self.measurandValue:.6g} +/- {self.expandedUncertainty:.4g} '
                                       f'{self.measurandUnit} (k = {coverageFactor:.0f})'],
            ['Dominant contributor',   f'{self.dominantContributor} ({self.dominantShare * 100.0:.0f} %)']
        ]

        report += '\n\n' + formatReportTable(summaryRows, ['Quantity', 'Value'], title = 'RESULT')

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'uncertaintyBudget.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report
