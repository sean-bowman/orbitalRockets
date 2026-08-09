
# -- PerformanceReduction -- #

'''

Turning measured channels into c*, Cf and Isp, with the uncertainty that belongs to each.

The reduction itself is three lines of algebra. The reason this class exists is the uncertainty,
and specifically one mistake that a generic uncertainty budget cannot avoid because it cannot see
the problem.

    c*  = Pc * At / mdot
    Cf  = F / (Pc * At)
    Isp = F / (mdot * g)

**Pc and At appear in both c* and Cf, and they appear inverted.** So the two results are not
independent, their errors are anti-correlated, and combining them by root sum of squares
double-counts the two shared terms. Worse, the product c* * Cf is algebraically exactly F / mdot:
the shared terms cancel completely, so specific impulse computed that way carries no chamber
pressure or throat area uncertainty at all.

A generic budget class, including this repository's own `UncertaintyBudget` in fluidSystemsTesting,
combines independent contributors. Handed c* and Cf it would return a specific impulse uncertainty
substantially larger than the truth. That is not a defect in that class; it is a case its interface
cannot express, and it is why this reduction is written here rather than assembled from it.

**Never compute Isp as c* times Cf and propagate the two uncertainties independently.** Compute it
from thrust and mass flow directly, which is both simpler and correct.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from propulsionTestUtils import (INSTRUMENT_UNCERTAINTY, rootSumSquare,
                                     characteristicVelocity, thrustCoefficient,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, ReductionError)
except ImportError:
    from .propulsionTestUtils import (INSTRUMENT_UNCERTAINTY, rootSumSquare,
                                      characteristicVelocity, thrustCoefficient,
                                      applyInputs, formatReportTable, createErrorContext,
                                      InvalidInputError, ReductionError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

STANDARD_GRAVITY = 9.80665    # [m/s^2]

# A contributor is called dominant when it accounts for this share of the combined variance. The
# same threshold fluidSystemsTesting's UncertaintyBudget uses, restated so the two agree.
DOMINANCE_THRESHOLD = 0.5    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- PerformanceReduction -- #
# ------------------------------------------------------------------------------------------------ #

class PerformanceReduction:

    '''

    c*, Cf and Isp from measured channels, with a correctly correlated uncertainty budget.

    '''

    def __init__(self):

        self.chamberPressure = np.nan
        self.throatArea      = np.nan
        self.massFlow        = np.nan
        self.thrust          = np.nan

        self.uncertainties = {}

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        The four measured channels, and optionally the relative uncertainty of each. Anything not
        given falls back to the representative development stand figures in
        `INSTRUMENT_UNCERTAINTY`, which are registered as unvalidated.

        '''

        requiredParams = {'chamberPressure': (int, float),
                          'throatArea':      (int, float),
                          'massFlow':        (int, float),
                          'thrust':          (int, float)}

        optionalParams = {'uncertainties': dict}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not isinstance(self.uncertainties, dict):
            self.uncertainties = {}

        for channel, entry in INSTRUMENT_UNCERTAINTY.items():
            self.uncertainties.setdefault(channel, entry['relative'])

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def reduce(self) -> dict:

        '''

        The three performance parameters from the four channels.

        '''

        cstar = characteristicVelocity(self.chamberPressure, self.throatArea, self.massFlow)
        cf    = thrustCoefficient(self.thrust, self.chamberPressure, self.throatArea)

        impulse = self.thrust / (self.massFlow * STANDARD_GRAVITY)

        return {'characteristicVelocity': cstar,
                'thrustCoefficient':      cf,
                'specificImpulse':        impulse,
                'productCheck':           cstar * cf / STANDARD_GRAVITY}

    # -------------------------------------------------------------------------------------------- #

    def calculateUncertainty(self) -> dict:

        '''

        The uncertainty in each reduced parameter, and the two ways of getting the third one wrong.

        Each parameter is a product of powers of the measured channels, so the relative uncertainty
        is the root sum of squares of the relative channel uncertainties, each weighted by its
        exponent. All the exponents here are plus or minus one, so the weights are all one and the
        sign drops out of the squaring.

            u(c*)  from Pc, At, mdot
            u(Cf)  from F, Pc, At
            u(Isp) from F, mdot           <- and NOT from Pc or At

        The last line is the point. Specific impulse does not depend on chamber pressure or throat
        area at all, because they cancel, and a budget that carries them is inflating the answer.

        '''

        findings = []

        pressure = self.uncertainties['chamberPressure']
        area     = self.uncertainties['throatArea']
        flow     = self.uncertainties['massFlow']
        force    = self.uncertainties['thrust']

        cstar = rootSumSquare(pressure, area, flow)
        cf    = rootSumSquare(force, pressure, area)

        # the correct one: Pc and At cancel in F / (mdot g)
        impulse = rootSumSquare(force, flow)

        # what a generic budget returns when handed c* and Cf as independent inputs
        naive = rootSumSquare(cstar, cf)

        inflation = naive / impulse

        findings.append(
            f'c* carries {cstar:.2%}, from the throat area at {area:.1%}, the mass flow at '
            f'{flow:.1%} and the chamber pressure at {pressure:.1%}.')

        findings.append(
            f'Cf carries {cf:.2%}, and it shares the chamber pressure and throat area terms with '
            f'c* rather than adding to them.')

        findings.append(
            f'Isp carries {impulse:.2%}, from thrust and mass flow only. The chamber pressure and '
            f'throat area cancel exactly in F / (mdot g), so they contribute nothing.')

        findings.append(
            f'Combining c* and Cf as independent gives {naive:.2%}, which is {inflation:.2f} times '
            f'the truth. **That is the error this class exists to prevent**, and a generic '
            f'uncertainty budget cannot see it because its interface takes independent '
            f'contributors.')

        contributors = {'chamberPressure': pressure, 'throatArea': area,
                        'massFlow': flow, 'thrust': force}

        cstarShares = {name: (self.uncertainties[name] / cstar) ** 2
                       for name in ('chamberPressure', 'throatArea', 'massFlow')}

        dominant = max(cstarShares, key = cstarShares.get)

        if cstarShares[dominant] >= DOMINANCE_THRESHOLD:
            findings.append(
                f'The {dominant} accounts for {cstarShares[dominant]:.0%} of the c* variance. '
                f'Improving anything else first buys nothing.')
        else:
            findings.append(
                f'No single channel dominates the c* variance; the largest is {dominant} at '
                f'{cstarShares[dominant]:.0%}. That is the case where a budget is worth building '
                f'rather than guessing.')

        self.findings = findings

        return {'characteristicVelocity': cstar,
                'thrustCoefficient':      cf,
                'specificImpulse':        impulse,
                'naiveSpecificImpulse':   naive,
                'inflationFactor':        inflation,
                'contributors':           contributors,
                'cstarShares':            cstarShares,
                'dominantCstarTerm':      dominant,
                'findings':               findings}

    # -------------------------------------------------------------------------------------------- #

    def compareEfficiency(self, idealCstar: float, idealThrustCoefficient: float) -> dict:

        '''

        Measured against ideal, which is what a hot fire is actually for, and whether the
        difference is resolvable.

        A c* efficiency quoted without the uncertainty of the measurement behind it is a number
        rather than a result. If the shortfall from ideal is smaller than the uncertainty in the
        measurement, the test has not established that there is a shortfall.

        '''

        if idealCstar <= 0.0 or idealThrustCoefficient <= 0.0:
            raise ReductionError(
                f'The ideal c* and thrust coefficient must both be positive, got {idealCstar} and '
                f'{idealThrustCoefficient}. They come from an equilibrium calculation at the same '
                f'chamber pressure and mixture ratio as the test point, and comparing against a '
                f'different point is the most common way an efficiency is overstated.',
                context = createErrorContext(component = 'PerformanceReduction'))

        reduced     = self.reduce()
        uncertainty = self.calculateUncertainty()

        cstarEfficiency = reduced['characteristicVelocity'] / idealCstar
        cfEfficiency    = reduced['thrustCoefficient'] / idealThrustCoefficient

        cstarShortfall = 1.0 - cstarEfficiency
        cfShortfall    = 1.0 - cfEfficiency

        cstarResolved = bool(abs(cstarShortfall) > uncertainty['characteristicVelocity'])
        cfResolved    = bool(abs(cfShortfall) > uncertainty['thrustCoefficient'])

        findings = []

        findings.append(
            f'c* efficiency {cstarEfficiency:.4f}, a shortfall of {cstarShortfall:.2%} against a '
            f'measurement uncertainty of {uncertainty["characteristicVelocity"]:.2%}.')

        if cstarResolved:
            findings.append('The shortfall is larger than the uncertainty, so the test has '
                            'established that there is one.')
        else:
            findings.append(
                '**The shortfall is inside the measurement uncertainty.** This test has not '
                'established that the injector underperforms, whatever the point estimate says.')

        findings.append(
            f'Thrust coefficient efficiency {cfEfficiency:.4f}, a shortfall of {cfShortfall:.2%} '
            f'against {uncertainty["thrustCoefficient"]:.2%}.')

        return {'cstarEfficiency':      cstarEfficiency,
                'thrustCoefficientEfficiency': cfEfficiency,
                'cstarShortfall':       cstarShortfall,
                'thrustCoefficientShortfall': cfShortfall,
                'cstarResolved':        cstarResolved,
                'thrustCoefficientResolved': cfResolved,
                'findings':             findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full reduction report.
        '''

        reduced     = self.reduce()
        uncertainty = self.calculateUncertainty()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  PERFORMANCE REDUCTION: {self.thrust / 1.0e3:.1f} kN at '
                     f'{self.chamberPressure / 1.0e6:.2f} MPa')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Characteristic velocity', f'{reduced["characteristicVelocity"]:.1f}',
              f'{uncertainty["characteristicVelocity"]:.2%}', 'm/s'],
             ['Thrust coefficient',      f'{reduced["thrustCoefficient"]:.4f}',
              f'{uncertainty["thrustCoefficient"]:.2%}', ''],
             ['Specific impulse',        f'{reduced["specificImpulse"]:.2f}',
              f'{uncertainty["specificImpulse"]:.2%}', 's'],
             ['Isp, naive combination',  f'{reduced["productCheck"]:.2f}',
              f'{uncertainty["naiveSpecificImpulse"]:.2%}', 's']],
            ['Parameter', 'Value', 'Uncertainty', 'Unit'], title = 'Reduced'))

        lines.append('')
        lines.append(formatReportTable(
            [[name, f'{value:.2%}', INSTRUMENT_UNCERTAINTY[name]['note'][:52]]
             for name, value in uncertainty['contributors'].items()],
            ['Channel', 'Relative', 'Note'], title = 'Channels'))

        lines.append('')
        for finding in uncertainty['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'performance_reduction.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('chamber pressure', self.chamberPressure),
                            ('throat area',      self.throatArea),
                            ('mass flow',        self.massFlow),
                            ('thrust',           self.thrust)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}. A reduction from a channel that '
                    f'read zero or negative is a data problem, not a performance result.',
                    context = createErrorContext(component = 'PerformanceReduction'))

        for name, value in self.uncertainties.items():

            if not 0.0 < value < 1.0:
                raise ReductionError(
                    f'The relative uncertainty for \'{name}\' must lie in (0, 1), got {value}. A '
                    f'zero uncertainty claims a perfect instrument and a value above one claims '
                    f'the measurement carries no information.',
                    context = createErrorContext(component = 'PerformanceReduction'))
