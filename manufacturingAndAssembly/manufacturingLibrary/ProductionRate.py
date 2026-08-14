
# -- ProductionRate -- #

'''

What rate does to cost, and what one station does to rate.

Two pieces of arithmetic, and each has a result that is not obvious.

**Wright's learning curve.** The cost of the nth unit is `C(1) * n ** log2(rate)`, so every doubling
of cumulative production costs a fixed fraction of the previous doubling. **The first doublings are
where the money is**: at an 85 per cent curve the second unit saves 15 per cent of the first, and
the move from unit 32 to unit 64 saves the same 15 per cent of a much smaller number.

That has an uncomfortable consequence for a launch programme. **A vehicle built ten times has barely
started down its curve**, so its unit cost is closer to the first article than to the asymptote, and
a cost estimate that quotes the learned-out figure is quoting a number the programme will never
reach.

**The bottleneck.** A line produces at the rate of its slowest station and no faster, so **capacity
is a minimum rather than a sum**. Adding capability anywhere except the bottleneck buys nothing at
all, which is the same arithmetic as a [turnaround driver] and it is ignored just as often.

And the bottleneck moves. Fix the slowest station and the second slowest becomes the constraint, so
the gain from any fix is the gap to the next station rather than the whole difference.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from manufacturingUtils import (LEARNING_RATES, BOTTLENECK_UTILISATION, learningExponent,
                                    applyInputs, formatReportTable, createErrorContext,
                                    InvalidInputError, RateError)
except ImportError:
    from .manufacturingUtils import (LEARNING_RATES, BOTTLENECK_UTILISATION, learningExponent,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, RateError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Working hours in a year at one shift, used to turn a station cycle time into an annual capacity.
# A programme running two or three shifts multiplies this, which is usually the cheapest capacity
# available and is the first thing to check before buying a machine.
ANNUAL_HOURS_SINGLE_SHIFT = 2000.0    # [h]

# ------------------------------------------------------------------------------------------------ #
# -- ProductionRate -- #
# ------------------------------------------------------------------------------------------------ #

class ProductionRate:

    '''

    Learning curve cost against cumulative production, takt time against demand, and the station
    that sets the line rate.

    '''

    def __init__(self):

        self.firstUnitCost = np.nan
        self.learningRate  = np.nan
        self.processClass  = ''
        self.stations      = {}
        self.annualDemand  = np.nan
        self.shifts        = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `firstUnitCost` is whatever unit the programme costs in, and every result is proportional to
        it, so the class never needs a currency.

        `learningRate` is the fraction the cost falls to on each doubling. `processClass` selects a
        representative rate from LEARNING_RATES where one is not given.

        `stations` maps a station name to its cycle time in hours, which is what sets the line
        rate. `annualDemand` and `shifts` turn that into a verdict.

        '''

        requiredParams = {'firstUnitCost': (int, float)}

        optionalParams = {'learningRate': (int, float),
                          'processClass': str,
                          'stations':     dict,
                          'annualDemand': (int, float),
                          'shifts':       (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.stations is None or isinstance(self.stations, float):
            self.stations = {}

        if not np.isfinite(self.shifts):
            self.shifts = 1.0

        if not np.isfinite(self.learningRate):

            if not self.processClass:
                self.processClass = 'machining'

            if self.processClass not in LEARNING_RATES:
                raise InvalidInputError(
                    f'{self.processClass} is not in the learning rate table. Available: '
                    f'{sorted(LEARNING_RATES)}.')

            self.learningRate = LEARNING_RATES[self.processClass]['rate']

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def unitCost(self, unitNumber: float) -> float:

        '''
        Wright's curve: the cost of the nth unit built.
        '''

        if unitNumber < 1.0:
            raise RateError('Unit numbers start at one.')

        return self.firstUnitCost * unitNumber ** learningExponent(self.learningRate)

    # -------------------------------------------------------------------------------------------- #

    def cumulativeCost(self, units: int) -> dict:

        '''

        Total and average cost over a production run.

        The cumulative average is the number a programme is actually judged on, and it lags the
        unit cost badly: at unit fifty the average still carries every expensive early unit.

        '''

        if units < 1:
            raise RateError('A production run has at least one unit.')

        costs = np.array([self.unitCost(float(index)) for index in range(1, units + 1)])

        return {'units':            units,
                'totalCost':        float(np.sum(costs)),
                'cumulativeAverage': float(np.mean(costs)),
                'lastUnitCost':     float(costs[-1]),
                'firstUnitCost':    self.firstUnitCost,
                'averageOverLast':  float(np.mean(costs)) / float(costs[-1]),
                'learningRate':     self.learningRate}

    # -------------------------------------------------------------------------------------------- #

    def doublingSweep(self, doublings: int = 7) -> dict:

        '''

        Unit cost at each doubling, which is the form the curve is actually log-linear in.

        Every row costs the same fraction of the row above it, and every row saves less than the
        one above it in absolute terms. **That is why the first few units carry most of the
        learning**, and why a programme of ten vehicles has barely started.

        '''

        sweep = []

        for index in range(doublings):

            unit = 2 ** index
            cost = self.unitCost(float(unit))

            sweep.append({'unit':      unit,
                          'unitCost':  cost,
                          'fractionOfFirst': cost / self.firstUnitCost,
                          'savingFromPrevious': (sweep[-1]['unitCost'] - cost) if sweep else 0.0})

        firstThree = self.firstUnitCost - sweep[2]['unitCost']
        wholeRange = self.firstUnitCost - sweep[-1]['unitCost']

        return {'sweep':              sweep,
                'learningRate':       self.learningRate,
                'exponent':           learningExponent(self.learningRate),
                'shareInFirstFour':   firstThree / wholeRange if wholeRange > 0.0 else 0.0,
                'atLastDoubling':     sweep[-1]['fractionOfFirst']}

    # -------------------------------------------------------------------------------------------- #

    def compareProcessClasses(self, units: int = 20) -> dict:

        '''

        The same run at every representative learning rate.

        The ordering is the point: the more labour a process carries, the more there is to learn,
        and a process that is mostly a material purchase barely learns at all.

        '''

        original = self.learningRate
        results = []

        try:
            for name, entry in LEARNING_RATES.items():

                self.learningRate = entry['rate']
                cumulative = self.cumulativeCost(units)

                results.append({'processClass':      name,
                                'learningRate':      entry['rate'],
                                'lastUnitCost':      cumulative['lastUnitCost'],
                                'cumulativeAverage': cumulative['cumulativeAverage'],
                                'fractionOfFirst':   cumulative['lastUnitCost'] / self.firstUnitCost,
                                'note':              entry['note']})
        finally:
            self.learningRate = original

        results.sort(key = lambda entry: entry['fractionOfFirst'])

        return {'results': results,
                'units':   units,
                'spread':  results[-1]['fractionOfFirst'] / results[0]['fractionOfFirst']}

    # -------------------------------------------------------------------------------------------- #

    def calculateTakt(self) -> dict:

        '''

        The cycle time the line has to hit to meet its demand, and whether it does.

        Takt time is available time divided by demand. A line whose bottleneck cycle time exceeds
        it cannot meet the rate, and the class raises rather than reporting a shortfall, because a
        line that cannot meet its rate is a plan that does not work.

        '''

        if not np.isfinite(self.annualDemand):
            raise RateError('An annual demand is needed to compute a takt time.')

        if not self.stations:
            raise RateError('Station cycle times are needed to say whether the takt is met.')

        available = ANNUAL_HOURS_SINGLE_SHIFT * self.shifts
        takt = available / self.annualDemand

        ranked = sorted(self.stations.items(), key = lambda item: item[1], reverse = True)

        bottleneck, bottleneckTime = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0

        entries = [{'station':     name,
                    'cycleTime':   float(time),
                    'utilisation': float(time) / takt,
                    'isBottleneck': name == bottleneck}
                   for name, time in ranked]

        capacity = available / bottleneckTime

        result = {'taktTime':        takt,
                  'availableHours':  available,
                  'shifts':          self.shifts,
                  'annualDemand':    self.annualDemand,
                  'stations':        entries,
                  'bottleneck':      bottleneck,
                  'bottleneckTime':  bottleneckTime,
                  'nextStationTime': second,
                  'gainIfFixed':     bottleneckTime - second,
                  'capacity':        capacity,
                  'sumOfCycleTimes': sum(self.stations.values()),
                  'utilisation':     bottleneckTime / takt,
                  'overUtilised':    bottleneckTime / takt > BOTTLENECK_UTILISATION}

        if bottleneckTime > takt:
            raise RateError(
                f'The {bottleneck} station takes {bottleneckTime:.2f} h against a takt time of '
                f'{takt:.2f} h, so the line makes {capacity:.0f} units a year against a demand of '
                f'{self.annualDemand:.0f}. **Capacity is the slowest station and not the sum**, so '
                f'improving anything else buys nothing.',
                context = {'bottleneck':     bottleneck,
                           'bottleneckTime': bottleneckTime,
                           'taktTime':       takt,
                           'capacity':       capacity})

        return result

    # -------------------------------------------------------------------------------------------- #

    def shiftSensitivity(self, shiftCounts: list = None) -> dict:

        '''

        Capacity against shift count, which is usually the cheapest capacity a programme can buy.

        Worth running before a machine is bought, because a second shift doubles capacity for the
        cost of people and a second machine doubles it for the cost of a machine plus people.

        '''

        if shiftCounts is None:
            shiftCounts = [1.0, 2.0, 3.0]

        if not self.stations:
            raise RateError('Station cycle times are needed to compute a capacity.')

        bottleneckTime = max(self.stations.values())

        original = self.shifts
        results = []

        try:
            for count in shiftCounts:

                self.shifts = count
                capacity = ANNUAL_HOURS_SINGLE_SHIFT * count / bottleneckTime

                results.append({'shifts':   count,
                                'capacity': capacity,
                                'meetsDemand': (capacity >= self.annualDemand
                                                if np.isfinite(self.annualDemand) else None)})
        finally:
            self.shifts = original

        sufficient = next((entry['shifts'] for entry in results if entry['meetsDemand']), None)

        return {'results':          results,
                'bottleneckTime':   bottleneckTime,
                'shiftsRequired':   sufficient}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The learning curve and the line, side by side.
        '''

        doublings = self.doublingSweep()

        lines = []

        lines.append(formatReportTable(
            [[f'{entry["unit"]}',
              f'{entry["unitCost"]:.3f}',
              f'{entry["fractionOfFirst"] * 100.0:.0f}%'] for entry in doublings['sweep']],
            ['unit', 'unit cost', 'of the first'],
            title = f'LEARNING CURVE AT {self.learningRate:.2f}'))

        lines.append('')
        lines.append(f'Exponent {doublings["exponent"]:.3f}. By unit '
                     f'{doublings["sweep"][-1]["unit"]} the cost is '
                     f'{doublings["atLastDoubling"] * 100.0:.0f} per cent of the first.')

        if self.stations and np.isfinite(self.annualDemand):

            lines.append('')

            try:
                takt = self.calculateTakt()

                lines.append(formatReportTable(
                    [[entry['station'],
                      f'{entry["cycleTime"]:.2f}',
                      f'{entry["utilisation"] * 100.0:.0f}%',
                      'yes' if entry['isBottleneck'] else ''] for entry in takt['stations']],
                    ['station', 'cycle [h]', 'utilisation', 'bottleneck'],
                    title = 'LINE'))

                lines.append('')
                lines.append(f'Takt {takt["taktTime"]:.2f} h, capacity {takt["capacity"]:.0f} a '
                             f'year, set by {takt["bottleneck"]}.')
                lines.append(f'Fixing it buys {takt["gainIfFixed"]:.2f} h and no more.')

            except RateError as error:
                lines.append('LINE CANNOT MEET ITS RATE')
                lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'productionRate.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not np.isfinite(self.firstUnitCost) or self.firstUnitCost <= 0.0:
            raise InvalidInputError('First unit cost must be positive.')

        if not 0.0 < self.learningRate <= 1.0:
            raise InvalidInputError(
                'A learning rate is a fraction above zero and at or below one. A rate above one is '
                'a process that gets worse with practice, which happens and is not a learning '
                'curve.')

        if self.shifts <= 0.0:
            raise InvalidInputError('Shift count must be positive.')

        if np.isfinite(self.annualDemand) and self.annualDemand <= 0.0:
            raise InvalidInputError('Annual demand must be positive.')

        for name, time in self.stations.items():
            if float(time) <= 0.0:
                raise InvalidInputError(f'Station {name} has a non-positive cycle time.')
