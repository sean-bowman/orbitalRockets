
# -- MassBudget -- #

'''

Subsystem mass rollup, growth allowance and margin, and the distinction between the last two.

**Mass growth allowance is not margin, and applying one while calling it the other is how a
programme discovers it has neither.**

Growth allowance covers what an estimate is *expected to become*. It is a statistical statement
about estimating at a given maturity: numbers from a scaling relationship have historically grown by
about a quarter, numbers from a released drawing set by about a twentieth. It is not optional and it
is not conservatism, it is the estimate.

Margin covers what is *not known at all*: the requirement that changes, the interface that turns out
to be heavier, the qualification failure that needs a doubler. It is a management reserve and it is
held at the programme level rather than distributed into the line items.

The two are added, not chosen between. A budget that shows a healthy margin because the growth
allowance was spent on it has no margin, and the two numbers this class keeps separate are the only
way to see that.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from vehicleUtils import (MASS_GROWTH_ALLOWANCE, massGrowthAllowance,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, ClosureError)
except ImportError:
    from .vehicleUtils import (MASS_GROWTH_ALLOWANCE, massGrowthAllowance,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, ClosureError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Programme margin held above the allocated mass, as a fraction of the predicted mass.
#
# This is a management reserve rather than an estimating allowance, and unlike the growth allowance
# it is a policy choice rather than a statistical one. A quarter at concept falling to a twentieth
# at first flight is a common shape and it is registered as unvalidated.
DEFAULT_MARGIN_POLICY = {
    'concept':      0.25,
    'preliminary':  0.15,
    'critical':     0.10,
    'qualification': 0.05,
    'flight':       0.02,
}

# ------------------------------------------------------------------------------------------------ #
# -- MassBudget -- #
# ------------------------------------------------------------------------------------------------ #

class MassBudget:

    '''

    Line item rollup with growth allowance and margin kept separate, and a centre of gravity.

    '''

    def __init__(self):

        self.items          = []
        self.allocatedMass  = np.nan
        self.programmePhase = ''

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `items` is a list of dictionaries, each with a `name`, a `mass` as the current best
        estimate, and a `maturity` from `MASS_GROWTH_ALLOWANCE`. An optional `station` gives the
        axial position for a centre of gravity.

        `allocatedMass` is what the vehicle sizing says this assembly is allowed to weigh. Without
        it the budget rolls up and reports nothing about whether it closes.

        '''

        requiredParams = {'items': list}

        optionalParams = {'allocatedMass':  (int, float),
                          'programmePhase': str}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.programmePhase:
            self.programmePhase = 'preliminary'

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def rollUp(self) -> dict:

        '''

        The budget, with the current best estimate, the growth allowance, and the predicted mass
        each reported separately.

        Predicted mass is the estimate plus its growth allowance. It is the number that should be
        compared against an allocation, and reporting the estimate alone against an allocation is
        the most common way a budget looks healthier than it is.

        '''

        lines = []

        estimate = 0.0
        growth   = 0.0

        for item in self.items:

            allowance = massGrowthAllowance(item['mass'], item['maturity'])

            lines.append({'name':      item['name'],
                          'estimate':  item['mass'],
                          'maturity':  item['maturity'],
                          'allowance': allowance,
                          'predicted': item['mass'] + allowance,
                          'allowanceRate': MASS_GROWTH_ALLOWANCE[item['maturity']]})

            estimate += item['mass']
            growth   += allowance

        predicted = estimate + growth

        # the effective allowance rate across the whole budget, which is a maturity measure
        effectiveRate = growth / estimate if estimate > 0.0 else 0.0

        return {'lines':          lines,
                'estimate':       estimate,
                'growth':         growth,
                'predicted':      predicted,
                'effectiveRate':  effectiveRate}

    # -------------------------------------------------------------------------------------------- #

    def checkMargin(self, marginPolicy: float = None) -> dict:

        '''

        Whether the budget closes against its allocation, with growth and margin kept apart.

        Three numbers and they answer different questions.

            estimate   what the hardware is currently believed to weigh
            predicted  estimate plus growth allowance: what it is expected to weigh
            required   predicted plus margin: what the allocation has to cover

        A budget that closes on `estimate` and not on `predicted` has not closed. A budget that
        closes on `predicted` and not on `required` has closed with no reserve, which is a
        legitimate position late in a programme and is not one at concept.

        '''

        if not np.isfinite(self.allocatedMass):
            raise InvalidInputError(
                'An allocated mass is needed to check a margin. It comes from the vehicle sizing, '
                'which is what decides how much this assembly is allowed to weigh.',
                context = createErrorContext(component = 'MassBudget'))

        if marginPolicy is None:

            if self.programmePhase not in DEFAULT_MARGIN_POLICY:
                raise InvalidInputError(
                    f'Unknown programme phase \'{self.programmePhase}\'. Known phases are '
                    f'{sorted(DEFAULT_MARGIN_POLICY)}, or pass a margin fraction explicitly.',
                    context = createErrorContext(component = 'MassBudget'))

            marginPolicy = DEFAULT_MARGIN_POLICY[self.programmePhase]

        findings = []

        rollup = self.rollUp()

        margin   = rollup['predicted'] * marginPolicy
        required = rollup['predicted'] + margin

        closesOnEstimate  = bool(rollup['estimate']  <= self.allocatedMass)
        closesOnPredicted = bool(rollup['predicted'] <= self.allocatedMass)
        closesOnRequired  = bool(required <= self.allocatedMass)

        findings.append(
            f'Current best estimate {rollup["estimate"]:.0f} kg, growth allowance '
            f'{rollup["growth"]:.0f} kg at an effective rate of {rollup["effectiveRate"]:.1%}, '
            f'predicted {rollup["predicted"]:.0f} kg.')

        findings.append(
            f'Programme margin at {marginPolicy:.0%} adds {margin:.0f} kg, so the allocation has '
            f'to cover {required:.0f} kg against {self.allocatedMass:.0f} kg available.')

        if closesOnEstimate and not closesOnPredicted:
            findings.append(
                '**This budget closes on the estimate and not on the prediction.** The growth '
                'allowance is not conservatism, it is what estimates at this maturity have '
                'historically become, so this budget does not close.')
        elif closesOnPredicted and not closesOnRequired:
            findings.append(
                'The budget closes on the prediction and not with margin. That is a legitimate '
                'position late in a programme and it is not one at concept, because there is then '
                'nothing left to absorb a requirement change.')
        elif closesOnRequired:
            findings.append(
                f'The budget closes with {self.allocatedMass - required:.0f} kg to spare beyond '
                f'both the growth allowance and the margin.')
        else:
            findings.append(
                f'**The budget does not close by {rollup["predicted"] - self.allocatedMass:.0f} kg '
                f'on the prediction alone**, before any margin is considered.')

        self.findings = findings

        return {'estimate':          rollup['estimate'],
                'growth':            rollup['growth'],
                'predicted':         rollup['predicted'],
                'marginPolicy':      marginPolicy,
                'margin':            margin,
                'required':          required,
                'allocated':         self.allocatedMass,
                'closesOnEstimate':  closesOnEstimate,
                'closesOnPredicted': closesOnPredicted,
                'closesOnRequired':  closesOnRequired,
                'findings':          findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateCentreOfGravity(self) -> dict:

        '''

        Axial centre of gravity from the line items, on the predicted masses rather than the
        estimates.

        Using the estimate here is a subtler version of the same error the margin check catches:
        the growth allowance is not distributed evenly across a vehicle, so a centre of gravity
        computed on estimates moves as the estimates mature.

        '''

        lines = self.rollUp()['lines']

        stations = [item.get('station') for item in self.items]

        if any(station is None for station in stations):
            raise InvalidInputError(
                'Every line item needs a station to compute a centre of gravity. Items without '
                'one are '
                f'{[item["name"] for item in self.items if item.get("station") is None]}.',
                context = createErrorContext(component = 'MassBudget'))

        predicted = np.array([line['predicted'] for line in lines])
        estimates = np.array([line['estimate'] for line in lines])
        positions = np.array(stations, dtype = float)

        total = float(np.sum(predicted))

        centreOnPredicted = float(np.sum(predicted * positions) / total)
        centreOnEstimate  = float(np.sum(estimates * positions) / np.sum(estimates))

        # second moment about the centre, which is the inertia contribution of the axial spread
        inertia = float(np.sum(predicted * (positions - centreOnPredicted) ** 2))

        return {'centreOfGravity':     centreOnPredicted,
                'centreOnEstimate':    centreOnEstimate,
                'shiftFromGrowth':     centreOnPredicted - centreOnEstimate,
                'totalMass':           total,
                'axialInertia':        inertia}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full mass budget report.
        '''

        rollup = self.rollUp()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  MASS BUDGET: {len(self.items)} items, {self.programmePhase} phase')
        lines.append('=' * 96)
        lines.append('')

        rows = [[entry['name'],
                 entry['maturity'],
                 f'{entry["estimate"]:.1f}',
                 f'{entry["allowanceRate"]:.0%}',
                 f'{entry["allowance"]:.1f}',
                 f'{entry["predicted"]:.1f}']
                for entry in rollup['lines']]

        rows.append(['TOTAL', '',
                     f'{rollup["estimate"]:.1f}',
                     f'{rollup["effectiveRate"]:.1%}',
                     f'{rollup["growth"]:.1f}',
                     f'{rollup["predicted"]:.1f}'])

        lines.append(formatReportTable(
            rows, ['Item', 'Maturity', 'Estimate [kg]', 'MGA', 'Growth [kg]', 'Predicted [kg]'],
            title = 'Rollup'))

        if np.isfinite(self.allocatedMass):

            margin = self.checkMargin()

            lines.append('')
            lines.append(formatReportTable(
                [['Predicted',  f'{margin["predicted"]:.1f}',  'kg'],
                 ['Margin',     f'{margin["margin"]:.1f}',     'kg'],
                 ['Required',   f'{margin["required"]:.1f}',   'kg'],
                 ['Allocated',  f'{margin["allocated"]:.1f}',  'kg'],
                 ['Closes',     f'{margin["closesOnRequired"]}', '']],
                ['Quantity', 'Value', 'Unit'], title = 'Against allocation'))

            lines.append('')
            for finding in margin['findings']:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'mass_budget.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if not self.items:
            raise InvalidInputError(
                'A mass budget needs at least one line item.',
                context = createErrorContext(component = 'MassBudget'))

        seen = set()

        for index, item in enumerate(self.items):

            for key in ('name', 'mass', 'maturity'):
                if key not in item:
                    raise InvalidInputError(
                        f'Line item {index + 1} has no {key}. Every item needs a name, a mass and '
                        f'a design maturity, because a mass without a maturity cannot carry a '
                        f'growth allowance and is therefore not a budget entry.',
                        context = createErrorContext(component = 'MassBudget'))

            if item['name'] in seen:
                raise InvalidInputError(
                    f'Duplicate line item name \'{item["name"]}\'. Duplicated names are how an '
                    f'item gets counted twice or dropped in a rollup.',
                    context = createErrorContext(component = 'MassBudget'))

            seen.add(item['name'])

            if item['mass'] < 0.0:
                raise InvalidInputError(
                    f'Line item \'{item["name"]}\' has a negative mass.',
                    context = createErrorContext(component = 'MassBudget'))

            if item['maturity'] not in MASS_GROWTH_ALLOWANCE:
                raise InvalidInputError(
                    f'Line item \'{item["name"]}\' has an unknown maturity '
                    f'\'{item["maturity"]}\'. Known levels are {sorted(MASS_GROWTH_ALLOWANCE)}.',
                    context = createErrorContext(component = 'MassBudget'))

        if np.isfinite(self.allocatedMass) and self.allocatedMass <= 0.0:
            raise ClosureError(
                f'The allocated mass must be positive, got {self.allocatedMass}. A non-positive '
                f'allocation means the vehicle sizing did not close, and the right place to fix '
                f'that is the sizing rather than the budget.',
                context = createErrorContext(component = 'MassBudget'))
