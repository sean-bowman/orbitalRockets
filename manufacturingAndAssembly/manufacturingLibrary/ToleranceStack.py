
# -- ToleranceStack -- #

'''

Whether the parts go together, and the factor of root n that decides how the question is asked.

A stack of dimensions has two answers and they are far apart.

**The worst case stack** adds every tolerance arithmetically, on the assumption that all of them sit
at their limit at the same time and in the same direction. It guarantees assembly and it is
expensive, because it demands tolerances tight enough that a coincidence which will never happen
would still fit.

**The statistical stack** adds them in quadrature, on the assumption that they are independent and
roughly normal. It is smaller by about the square root of the contributor count, and it accepts
that some assemblies will not fit.

    worst case  = sum of tolerances
    statistical = sqrt( sum of squares )        ratio ~ sqrt(n) for equal contributors

**Twelve equal contributors differ by a factor of 3.5 between the two methods**, which is the
difference between a machined tolerance and a ground one on every part in the stack. That is the
single most consequential arithmetic in assembly design, and it is a decision about how many
assemblies you are willing to rework rather than a calculation.

Two things about the statistical case are worth stating before it is used.

**Independence is the assumption doing the work**, and it fails exactly where it matters: parts from
one batch, one machine or one operator share a bias, and a shared bias adds arithmetically like the
worst case rather than in quadrature.

**And the distribution is assumed centred.** A process running at the top of its tolerance band puts
the whole stack off centre, and the quadrature sum says nothing about that.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from manufacturingUtils import (PROCESS_TOLERANCES, DEFAULT_STATISTICAL_SIGMA,
                                    applyInputs, formatReportTable, createErrorContext,
                                    InvalidInputError, ToleranceError)
except ImportError:
    from .manufacturingUtils import (PROCESS_TOLERANCES, DEFAULT_STATISTICAL_SIGMA,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, ToleranceError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# A contributor holding more than this share of the quadrature sum is called dominant. Below it the
# stack is genuinely distributed and tightening any one dimension buys very little.
DOMINANCE_THRESHOLD = 0.5    # [-] of the sum of squares

# ------------------------------------------------------------------------------------------------ #
# -- ToleranceStack -- #
# ------------------------------------------------------------------------------------------------ #

class ToleranceStack:

    '''

    Worst case and statistical stacks, the dominant contributor, the shim demand and the reject
    fraction.

    '''

    def __init__(self):

        self.contributors  = []
        self.nominalGap    = np.nan
        self.minimumGap    = np.nan
        self.maximumGap    = np.nan
        self.sigmaLevel    = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `contributors` is a list of dictionaries with `name`, `tolerance` as a half-width in metres,
        and optionally `direction`, plus or minus one, for how the dimension enters the gap.

        `nominalGap` is the designed gap at nominal dimensions. `minimumGap` and `maximumGap` are
        what the joint requires, which is what turns a stack into a verdict: a gap that closes is
        an interference and a gap that opens too far is a shim.

        `sigmaLevel` is how many standard deviations the statistical stack is quoted at, which sets
        how many assemblies fall outside it.

        '''

        requiredParams = {'contributors': list,
                          'nominalGap':   (int, float)}

        optionalParams = {'minimumGap': (int, float),
                          'maximumGap': (int, float),
                          'sigmaLevel': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.sigmaLevel):
            self.sigmaLevel = DEFAULT_STATISTICAL_SIGMA

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateStack(self) -> dict:

        '''

        Both stacks, side by side, with the contribution of each dimension to each.

        The two rankings differ, and that is the useful part: a contributor is a fixed share of the
        worst case and a squared share of the statistical one, so a single loose dimension
        dominates the statistical stack far more than it dominates the worst case.

        '''

        tolerances = np.array([float(entry['tolerance']) for entry in self.contributors])

        worstCase = float(np.sum(tolerances))
        statistical = float(np.sqrt(np.sum(tolerances ** 2)))

        entries = []

        for index, entry in enumerate(self.contributors):

            tolerance = tolerances[index]

            entries.append({'name':             entry['name'],
                            'tolerance':        tolerance,
                            'worstCaseShare':   tolerance / worstCase,
                            'statisticalShare': tolerance ** 2 / statistical ** 2,
                            'direction':        int(entry.get('direction', 1))})

        entries.sort(key = lambda item: item['statisticalShare'], reverse = True)

        dominant = entries[0]

        # A statistical stack quoted at k sigma exceeds the arithmetic worst case whenever
        # k > sum(t) / sqrt(sum(t**2)), which for n equal contributors is k > sqrt(n).
        #
        # **So a three sigma statistical stack is no saving at all below about nine contributors**,
        # and the crossover moves further out as the contributors become unequal. That is the fact
        # that decides whether the statistical method is worth using on a given joint, and it is
        # usually assumed rather than checked.
        crossover = worstCase / statistical

        return {'contributors':     entries,
                'count':            len(entries),
                'worstCase':        worstCase,
                'statistical':      statistical,
                'ratio':            crossover,
                'equalContributorRatio': float(np.sqrt(len(entries))),
                'sigmaCrossover':   crossover,
                'statisticalHelps': bool(self.sigmaLevel < crossover),
                'unequalPenalty':   float(np.sqrt(len(entries))) / crossover,
                'dominant':         dominant['name'],
                'dominantShare':    dominant['statisticalShare'],
                'isDominated':      bool(dominant['statisticalShare'] > DOMINANCE_THRESHOLD)}

    # -------------------------------------------------------------------------------------------- #

    def checkGap(self, method: str = 'worstCase') -> dict:

        '''

        The gap at its extremes, against what the joint requires.

        Raises where the gap closes, because an interference at assembly is a part that does not go
        together rather than a design with a small negative margin. **A gap that opens too far is a
        shim and is reported**, because that is a cost rather than a failure.

        '''

        if method not in ('worstCase', 'statistical'):
            raise InvalidInputError("Method must be 'worstCase' or 'statistical'.")

        stack = self.calculateStack()

        if method == 'worstCase':
            spread = stack['worstCase']
            capped = False
        else:
            raw = stack['statistical'] * self.sigmaLevel
            # The worst case is a hard bound: no combination of tolerances can exceed the
            # arithmetic sum. A sigma level above the crossover produces a spread that cannot
            # physically occur, so it is capped and the cap is reported rather than hidden.
            spread = min(raw, stack['worstCase'])
            capped = raw > stack['worstCase']

        smallest = self.nominalGap - spread
        largest = self.nominalGap + spread

        result = {'method':      method,
                  'spread':      spread,
                  'nominalGap':  self.nominalGap,
                  'smallestGap': smallest,
                  'largestGap':  largest,
                  'cappedAtWorstCase': capped,
                  'sigmaLevel':  self.sigmaLevel if method == 'statistical' else None}

        if smallest < 0.0:
            raise ToleranceError(
                f'The {method} stack of {spread * 1000.0:.3f} mm exceeds a nominal gap of '
                f'{self.nominalGap * 1000.0:.3f} mm, so the parts interfere at the extreme. '
                f'The dominant contributor is {stack["dominant"]} at '
                f'{stack["dominantShare"] * 100.0:.0f} per cent of the statistical stack.',
                context = {'method':        method,
                           'spread':       spread,
                           'nominalGap':   self.nominalGap,
                           'dominant':     stack['dominant']})

        if np.isfinite(self.minimumGap):

            result['minimumGap'] = self.minimumGap
            result['minimumMargin'] = smallest - self.minimumGap

            if smallest < self.minimumGap:
                raise ToleranceError(
                    f'The smallest gap of {smallest * 1000.0:.3f} mm falls below the '
                    f'{self.minimumGap * 1000.0:.3f} mm the joint requires. A gap that closes is '
                    f'an assembly that does not go together.',
                    context = {'method':      method,
                               'smallestGap': smallest,
                               'minimumGap':  self.minimumGap})

        if np.isfinite(self.maximumGap):

            result['maximumGap'] = self.maximumGap
            result['shimRequired'] = max(0.0, largest - self.maximumGap)
            result['needsShim'] = largest > self.maximumGap

        return result

    # -------------------------------------------------------------------------------------------- #

    def rejectFraction(self) -> dict:

        '''

        What fraction of assemblies fall outside the statistical stack, and what that is worth.

        A stack quoted at three sigma leaves 0.27 per cent outside, which sounds small until it is
        multiplied by the number of stacks in a vehicle. **The number that matters is assemblies
        per rework, not the tail probability**, and this reports both.

        '''

        # Two-sided normal tail, without importing a statistics package for one function.
        # erf is in numpy's math module through the standard library.
        from math import erf, sqrt

        inside = erf(self.sigmaLevel / sqrt(2.0))
        outside = 1.0 - inside

        return {'sigmaLevel':        self.sigmaLevel,
                'insideFraction':    inside,
                'outsideFraction':   outside,
                'assembliesPerReject': (1.0 / outside) if outside > 0.0 else np.inf,
                'partsPerMillion':   outside * 1.0e6}

    # -------------------------------------------------------------------------------------------- #

    def compareProcesses(self, processes: list = None, dimension: float = None) -> dict:

        '''

        The same stack made by different processes.

        Achievable tolerance spans three orders of magnitude across the process list, which is why
        process selection is a tolerance decision before it is a cost one.

        '''

        if processes is None:
            processes = list(PROCESS_TOLERANCES)

        if dimension is None:
            dimension = self.nominalGap * 100.0

        count = len(self.contributors)
        results = []

        for process in processes:

            if process not in PROCESS_TOLERANCES:
                raise InvalidInputError(f'{process} is not in the process tolerance table.')

            tolerance = PROCESS_TOLERANCES[process] * dimension

            results.append({'process':     process,
                            'tolerance':   tolerance,
                            'worstCase':   tolerance * count,
                            'statistical': tolerance * np.sqrt(count)})

        results.sort(key = lambda entry: entry['tolerance'])

        return {'results':   results,
                'dimension': dimension,
                'spread':    results[-1]['tolerance'] / results[0]['tolerance']}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Both stacks, the contributors ranked, and the gap check.
        '''

        stack = self.calculateStack()

        lines = []

        lines.append(formatReportTable(
            [[entry['name'],
              f'{entry["tolerance"] * 1000.0:.3f}',
              f'{entry["worstCaseShare"] * 100.0:.0f}%',
              f'{entry["statisticalShare"] * 100.0:.0f}%'] for entry in stack['contributors']],
            ['contributor', 'tolerance [mm]', 'worst case', 'statistical'],
            title = 'TOLERANCE CONTRIBUTORS'))

        lines.append('')
        lines.append(f'Worst case {stack["worstCase"] * 1000.0:.3f} mm against a statistical '
                     f'{stack["statistical"] * 1000.0:.3f} mm, a ratio of {stack["ratio"]:.2f} '
                     f'over {stack["count"]} contributors.')
        lines.append(f'Dominant contributor {stack["dominant"]} at '
                     f'{stack["dominantShare"] * 100.0:.0f} per cent of the statistical stack.')

        for method in ('worstCase', 'statistical'):

            lines.append('')

            try:
                check = self.checkGap(method)
                lines.append(f'{method}: gap from {check["smallestGap"] * 1000.0:.3f} to '
                             f'{check["largestGap"] * 1000.0:.3f} mm.')
                if check.get('needsShim'):
                    lines.append(f'  Shim required up to {check["shimRequired"] * 1000.0:.3f} mm.')
            except ToleranceError as error:
                lines.append(f'{method}: FAILED')
                lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'toleranceStack.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not self.contributors:
            raise InvalidInputError('A stack needs at least one contributor.')

        names = [entry['name'] for entry in self.contributors]

        if len(names) != len(set(names)):
            raise InvalidInputError('Contributor names must be unique, because the report ranks '
                                    'them by name.')

        for entry in self.contributors:

            if 'tolerance' not in entry:
                raise InvalidInputError(f"Contributor {entry.get('name', 'unnamed')} has no "
                                        f'tolerance.')

            if float(entry['tolerance']) <= 0.0:
                raise InvalidInputError(
                    f"Contributor {entry['name']} has a non-positive tolerance. A dimension with "
                    f'no tolerance is a dimension nobody has to make, which is not a thing.')

        if not np.isfinite(self.nominalGap):
            raise InvalidInputError('A nominal gap is required. Without it the stack is a spread '
                                    'with nothing to compare against.')

        if self.sigmaLevel <= 0.0:
            raise InvalidInputError('Sigma level must be positive.')

        if np.isfinite(self.minimumGap) and np.isfinite(self.maximumGap):
            if self.minimumGap >= self.maximumGap:
                raise InvalidInputError('The minimum gap must be below the maximum.')
