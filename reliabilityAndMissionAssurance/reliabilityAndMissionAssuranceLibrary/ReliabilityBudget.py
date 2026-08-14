
# -- ReliabilityBudget -- #

'''

Where a launch vehicle's reliability actually goes, and why the number nobody argues about is the
one that decides it.

A vehicle is a series system: everything has to work. So the reliabilities multiply, and the
multiplication is unforgiving.

    100 items at 0.999 each   ->  0.905
    1000 items at 0.999 each  ->  0.368

**Item count is a reliability parameter.** A design with twice the parts at the same per-part
reliability has roughly twice the failure probability, and part count reduction is a reliability
decision before it is a cost or a mass one.

Two things fall out of the series form and both are useful.

**Allocation is a division of a small number.** Given a vehicle target, each subsystem gets a share
of the allowed unreliability rather than a share of the reliability, and the arithmetic is additive
in failure probability rather than multiplicative in reliability. That is why a budget is kept in
failure probability and reported in reliability.

**And the largest contributor is usually not the largest subsystem.** A subsystem with a hundred
components at four nines contributes as much as one with ten at three nines, and the two look
nothing alike on a block diagram.

**A reliability number without a stated basis is a wish.** Every allocation here carries where it
came from, and the class refuses a budget that does not close.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from reliabilityUtils import (FAILURE_RATES, seriesReliability, zeroFailureDemonstration,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, AllocationError)
except ImportError:
    from .reliabilityUtils import (FAILURE_RATES, seriesReliability, zeroFailureDemonstration,
                                   applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, AllocationError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# A subsystem holding more than this share of the vehicle's allowed unreliability is reported as
# dominant. Below it the budget is genuinely distributed and improving any one subsystem buys
# little.
DOMINANCE_THRESHOLD = 0.4    # [-]

# The bases an allocation can carry, in descending order of how much they are worth. **A reliability
# number without one of these behind it is a wish**, which is the domain ethos in its most literal
# form.
ALLOCATION_BASES = {
    'demonstrated': {'rank': 1, 'means': 'a test programme with a stated confidence'},
    'heritage':     {'rank': 2, 'means': 'flight history on this design'},
    'predicted':    {'rank': 3, 'means': 'a parts count prediction, which is usually optimistic'},
    'allocated':    {'rank': 4, 'means': 'a share of the target, with nothing behind it yet'},
    'assumed':      {'rank': 5, 'means': 'a number somebody wrote down'},
}

# ------------------------------------------------------------------------------------------------ #
# -- ReliabilityBudget -- #
# ------------------------------------------------------------------------------------------------ #

class ReliabilityBudget:

    '''

    Series rollup across subsystems, allocation against a vehicle target, and what each allocation
    rests on.

    '''

    def __init__(self):

        self.subsystems  = []
        self.target      = np.nan
        self.itemCount   = np.nan
        self.itemReliability = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `subsystems` is a list of dictionaries with `name`, `reliability`, and `basis` from
        ALLOCATION_BASES. **The basis is required rather than optional**, because a reliability
        number without one is a wish and the class exists partly to say so.

        `target` is the vehicle reliability the budget has to meet.

        `itemCount` and `itemReliability` describe a flat part population, for the demonstration
        that item count is a reliability parameter.

        '''

        requiredParams = {'subsystems': list}

        optionalParams = {'target':          (int, float),
                          'itemCount':       (int, float),
                          'itemReliability': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateRollup(self) -> dict:

        '''

        The series product across the subsystems, and where the unreliability sits.

        **The budget is kept in failure probability rather than reliability**, because failure
        probabilities are nearly additive for small values and reliabilities are not, so the shares
        mean something.

        '''

        entries = []

        for subsystem in self.subsystems:

            reliability = float(subsystem['reliability'])
            failure = 1.0 - reliability

            entries.append({'name':        subsystem['name'],
                            'reliability': reliability,
                            'failure':     failure,
                            'basis':       subsystem['basis'],
                            'basisRank':   ALLOCATION_BASES[subsystem['basis']]['rank'],
                            'basisMeans':  ALLOCATION_BASES[subsystem['basis']]['means']})

        system = seriesReliability([entry['reliability'] for entry in entries])
        systemFailure = 1.0 - system

        totalFailure = sum(entry['failure'] for entry in entries)

        for entry in entries:
            entry['share'] = entry['failure'] / totalFailure if totalFailure > 0.0 else 0.0

        entries.sort(key = lambda entry: entry['failure'], reverse = True)

        dominant = entries[0]

        weakest = max(entries, key = lambda entry: entry['basisRank'])

        result = {'subsystems':      entries,
                  'count':           len(entries),
                  'systemReliability': system,
                  'systemFailure':   systemFailure,
                  'sumOfFailures':   totalFailure,
                  'dominant':        dominant['name'],
                  'dominantShare':   dominant['share'],
                  'isDominated':     bool(dominant['share'] > DOMINANCE_THRESHOLD),
                  'weakestBasis':    weakest['name'],
                  'weakestBasisKind': weakest['basis'],
                  'additiveError':   abs(totalFailure - systemFailure) / systemFailure
                                     if systemFailure > 0.0 else 0.0}

        if np.isfinite(self.target):

            result['target'] = self.target
            result['margin'] = (1.0 - self.target) / systemFailure if systemFailure > 0.0 else np.inf
            result['meetsTarget'] = system >= self.target

            if system < self.target:
                raise AllocationError(
                    f'The rollup reaches {system:.5f} against a target of {self.target:.5f}. '
                    f'The dominant subsystem is {dominant["name"]} at '
                    f'{dominant["share"] * 100.0:.0f} per cent of the allowed unreliability, and '
                    f'the weakest basis in the budget is {weakest["name"]}, which is '
                    f'{weakest["basis"]}. **A budget that does not close is a budget**, not a '
                    f'design margin to argue about.',
                    context = {'systemReliability': system,
                               'target':            self.target,
                               'dominant':          dominant['name'],
                               'weakestBasis':      weakest['name']})

        return result

    # -------------------------------------------------------------------------------------------- #

    def allocate(self, weights: dict = None) -> dict:

        '''

        Divide the vehicle target across the subsystems.

        The allowed unreliability is divided rather than the reliability, because failure
        probabilities add and reliabilities multiply. An equal allocation gives every subsystem the
        same share of the failure budget, which is rarely right and is the honest starting point.

        '''

        if not np.isfinite(self.target):
            raise AllocationError('A vehicle target is needed to allocate against.')

        allowed = 1.0 - self.target

        names = [subsystem['name'] for subsystem in self.subsystems]

        if weights is None:
            weights = {name: 1.0 for name in names}

        for name in weights:
            if name not in names:
                raise AllocationError(f'{name} is not a subsystem in the budget.')

        total = sum(weights.get(name, 0.0) for name in names)

        if total <= 0.0:
            raise AllocationError('Allocation weights must sum to something positive.')

        entries = []

        for subsystem in self.subsystems:

            name = subsystem['name']
            share = weights.get(name, 0.0) / total
            allocated = allowed * share

            current = 1.0 - float(subsystem['reliability'])

            entries.append({'name':           name,
                            'weight':         weights.get(name, 0.0),
                            'allocatedFailure': allocated,
                            'allocatedReliability': 1.0 - allocated,
                            'currentFailure': current,
                            'meetsAllocation': bool(current <= allocated),
                            'shortfall':      max(0.0, current - allocated)})

        entries.sort(key = lambda entry: entry['shortfall'], reverse = True)

        overspent = [entry for entry in entries if not entry['meetsAllocation']]

        return {'target':      self.target,
                'allowed':     allowed,
                'allocations': entries,
                'overspent':   [entry['name'] for entry in overspent],
                'worstOverspend': entries[0]['name'] if overspent else None,
                'closes':      len(overspent) == 0}

    # -------------------------------------------------------------------------------------------- #

    def itemCountEffect(self, counts: list = None) -> dict:

        '''

        Series reliability against item count, at a fixed per-item reliability.

        **Item count is a reliability parameter**, and this is the table that says so. It is also
        the argument for part count reduction that a mass or cost case cannot make on its own.

        '''

        if not np.isfinite(self.itemReliability):
            raise AllocationError('A per-item reliability is needed for the item count sweep.')

        if counts is None:
            counts = [10, 50, 100, 500, 1000, 5000]

        sweep = [{'items':       count,
                  'reliability': float(self.itemReliability ** count),
                  'failure':     float(1.0 - self.itemReliability ** count)}
                 for count in counts]

        # The count at which the vehicle reaches a nine of unreliability, which is a useful way to
        # express how quickly the multiplication bites.
        return {'sweep':           sweep,
                'itemReliability': self.itemReliability,
                'halvingCount':    float(np.log(0.5) / np.log(self.itemReliability)),
                'spread':          sweep[0]['failure'] and sweep[-1]['failure'] / sweep[0]['failure']}

    # -------------------------------------------------------------------------------------------- #

    def basisAudit(self) -> dict:

        '''

        What the budget actually rests on.

        **A reliability number without a stated basis is a wish**, and this is the audit that says
        how much of the vehicle target is supported by evidence and how much by an allocation
        nobody has closed yet.

        '''

        rollup = self.calculateRollup() if not np.isfinite(self.target) else None

        entries = []

        for subsystem in self.subsystems:

            failure = 1.0 - float(subsystem['reliability'])

            entries.append({'name':      subsystem['name'],
                            'basis':     subsystem['basis'],
                            'rank':      ALLOCATION_BASES[subsystem['basis']]['rank'],
                            'failure':   failure})

        total = sum(entry['failure'] for entry in entries)

        byBasis = {}

        for entry in entries:
            byBasis.setdefault(entry['basis'], 0.0)
            byBasis[entry['basis']] += entry['failure']

        summary = [{'basis':  name,
                    'rank':   ALLOCATION_BASES[name]['rank'],
                    'means':  ALLOCATION_BASES[name]['means'],
                    'failure': value,
                    'share':  value / total if total > 0.0 else 0.0}
                   for name, value in byBasis.items()]

        summary.sort(key = lambda entry: entry['rank'])

        evidenced = sum(entry['share'] for entry in summary if entry['rank'] <= 2)

        return {'byBasis':        summary,
                'subsystems':     entries,
                'evidencedShare': evidenced,
                'assumedShare':   sum(entry['share'] for entry in summary if entry['rank'] >= 4),
                'weakest':        max(entries, key = lambda entry: entry['rank'])['name']}

    # -------------------------------------------------------------------------------------------- #

    def demonstrationCost(self, confidence: float = 0.95) -> dict:

        '''

        What demonstrating the vehicle target by test alone would take.

        The same arithmetic [rangeSafetyAndFTS] applies to a flight termination system, and it
        applies to a whole vehicle with the same force: a target of 0.98 needs about 150 flights
        with no failures to demonstrate at 95 per cent confidence.

        **Which is why a vehicle reliability is argued from its parts rather than demonstrated as a
        whole**, and why the basis audit above matters more than the number.

        '''

        if not np.isfinite(self.target):
            raise AllocationError('A vehicle target is needed to cost a demonstration.')

        flights = zeroFailureDemonstration(self.target, confidence)

        return {'target':      self.target,
                'confidence':  confidence,
                'flights':     flights,
                'perNine':     zeroFailureDemonstration(1.0 - (1.0 - self.target) / 10.0,
                                                        confidence) / flights}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The rollup, the basis audit, and the item count effect.
        '''

        lines = []

        try:
            rollup = self.calculateRollup()

            lines.append(formatReportTable(
                [[entry['name'],
                  f'{entry["reliability"]:.5f}',
                  f'{entry["failure"]:.2e}',
                  f'{entry["share"] * 100.0:.0f}%',
                  entry['basis']] for entry in rollup['subsystems']],
                ['subsystem', 'reliability', 'failure', 'share', 'basis'],
                title = 'RELIABILITY ROLLUP'))

            lines.append('')
            lines.append(f'System {rollup["systemReliability"]:.5f}, dominated by '
                         f'{rollup["dominant"]} at {rollup["dominantShare"] * 100.0:.0f} per cent.')

        except AllocationError as error:
            lines.append('BUDGET DOES NOT CLOSE')
            lines.append(str(error))

        audit = self.basisAudit()

        lines.append('')
        lines.append(formatReportTable(
            [[entry['basis'],
              f'{entry["share"] * 100.0:.0f}%',
              entry['means']] for entry in audit['byBasis']],
            ['basis', 'share of failure budget', 'means'],
            title = 'WHAT THE BUDGET RESTS ON'))

        lines.append('')
        lines.append(f'{audit["evidencedShare"] * 100.0:.0f} per cent of the failure budget has '
                     f'evidence behind it; {audit["assumedShare"] * 100.0:.0f} per cent does not.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'reliabilityBudget.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not self.subsystems:
            raise InvalidInputError('A budget needs at least one subsystem.')

        names = [subsystem['name'] for subsystem in self.subsystems]

        if len(names) != len(set(names)):
            raise InvalidInputError('Subsystem names must be unique.')

        for subsystem in self.subsystems:

            if 'basis' not in subsystem:
                raise InvalidInputError(
                    f"Subsystem {subsystem['name']} has no basis. **A reliability number without "
                    f'a stated basis is a wish**, so the basis is required rather than optional. '
                    f'Available: {sorted(ALLOCATION_BASES)}.')

            if subsystem['basis'] not in ALLOCATION_BASES:
                raise InvalidInputError(
                    f"{subsystem['basis']} is not an allocation basis. Available: "
                    f'{sorted(ALLOCATION_BASES)}.')

            if not 0.0 < float(subsystem['reliability']) <= 1.0:
                raise InvalidInputError(
                    f"Subsystem {subsystem['name']} has a reliability outside zero to one.")

        if np.isfinite(self.target) and not 0.0 < self.target < 1.0:
            raise InvalidInputError('The target must lie strictly between zero and one. A target '
                                    'of one is not a target.')

        if np.isfinite(self.itemReliability):
            if not 0.0 < self.itemReliability < 1.0:
                raise InvalidInputError('Item reliability must lie strictly between zero and one.')
