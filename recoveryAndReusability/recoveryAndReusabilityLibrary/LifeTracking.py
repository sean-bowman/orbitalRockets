
# -- LifeTracking -- #

'''

How many more times an article can fly, and why the honest answer is usually a shrug.

Life tracking is Miner's rule applied to an airframe: every flight consumes a fraction of each
item's allowable life, the fractions accumulate, and the article is retired when one of them reaches
one. That much is arithmetic.

**What makes it hard is that the damage per flight depends on the environment the article actually
saw**, and almost nothing measures that. A flight flown hot, or long, or through a heavier gust
consumes more life than a nominal one, and a tracker fed nominal flights returns a nominal answer
regardless of what happened. **Life tracking only works if the flight environment was measured**,
which is a telemetry requirement rather than a structures one.

Three results come out of the arithmetic and each is worth having.

**The limiting item is rarely the one that looks worst.** A thermal protection system that comes back
visibly scorched may have decades of life; a turbopump that looks untouched may be two flights from
its low cycle fatigue limit. Appearance and damage rate are unrelated.

**Retirement is set by one item, and replacing it moves the limit to the next.** The gain from
extending any life limit is the gap to the second, exactly as it is for a turnaround driver.

**The fleet leader is the instrument.** Flying one article ahead of the rest buys warning, and how
much warning is the lead in flights. A fleet with no leader discovers its life limit in service, on
all of them at once.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from recoveryUtils import (LIFE_LIMITED_ITEMS, INSPECTION_LEVELS,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, LifeError)
except ImportError:
    from .recoveryUtils import (LIFE_LIMITED_ITEMS, INSPECTION_LEVELS,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, LifeError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Damage accumulated at one. Miner's rule is a linear accumulation and the number is a convention
# rather than a measurement: real failures scatter around it by a factor of several either way,
# which is why life limits carry a scatter factor on top.
MINER_LIMIT = 1.0    # [-]

# The scatter factor applied between a demonstrated life and a certified one. A demonstrated life
# is one article; a certified life has to cover the fleet.
DEFAULT_SCATTER_FACTOR = 4.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- LifeTracking -- #
# ------------------------------------------------------------------------------------------------ #

class LifeTracking:

    '''

    Damage accumulation by item, the limiting item, remaining flights, and the fleet leader lead.

    '''

    def __init__(self):

        self.flightsFlown    = np.nan
        self.items           = {}
        self.severityFactor  = np.nan
        self.certifiedLife   = np.nan
        self.scatterFactor   = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `flightsFlown` is what this article has already done. `items` maps an item name to its
        damage per nominal flight, overriding LIFE_LIMITED_ITEMS where given.

        `severityFactor` scales the damage per flight for an article flown harder than nominal.
        **It is the input that makes this a tracker rather than a counter**, and it has to come
        from a measured environment.

        `certifiedLife` is the flight count the article is approved to, which is a separate and
        usually smaller number than the one the damage accumulation gives.

        '''

        requiredParams = {'flightsFlown': (int, float)}

        optionalParams = {'items':          dict,
                          'severityFactor': (int, float),
                          'certifiedLife':  (int, float),
                          'scatterFactor':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.items is None or isinstance(self.items, float) or not self.items:
            self.items = {name: entry['damagePerFlight']
                          for name, entry in LIFE_LIMITED_ITEMS.items()}

        if not np.isfinite(self.severityFactor):
            self.severityFactor = 1.0

        if not np.isfinite(self.scatterFactor):
            self.scatterFactor = DEFAULT_SCATTER_FACTOR

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateAccumulation(self) -> dict:

        '''

        Damage consumed by each item, and which one limits the article.

        '''

        results = []

        for name, damagePerFlight in self.items.items():

            perFlight = float(damagePerFlight) * self.severityFactor
            consumed = perFlight * self.flightsFlown
            remaining = max(0.0, MINER_LIMIT - consumed)

            results.append({'item':            name,
                            'damagePerFlight': perFlight,
                            'consumed':        consumed,
                            'remainingFraction': remaining,
                            'remainingFlights': remaining / perFlight if perFlight > 0.0 else np.inf,
                            'allowableFlights': MINER_LIMIT / perFlight if perFlight > 0.0 else np.inf,
                            'driver':          LIFE_LIMITED_ITEMS.get(name, {}).get('driver', '')})

        results.sort(key = lambda entry: entry['remainingFlights'])

        limiting = results[0]
        second = results[1] if len(results) > 1 else None

        if limiting['consumed'] > MINER_LIMIT:
            raise LifeError(
                f'{limiting["item"]} has consumed {limiting["consumed"]:.2f} of its allowable '
                f'life over {self.flightsFlown:.0f} flights at a severity factor of '
                f'{self.severityFactor:.2f}. An article past a life limit is a disposition rather '
                f'than a number, and it is not this tool that makes it.',
                context = {'item':           limiting['item'],
                           'flightsFlown':   self.flightsFlown,
                           'severityFactor': self.severityFactor,
                           'allowable':      limiting['allowableFlights']})

        return {'items':            results,
                'limitingItem':     limiting['item'],
                'remainingFlights': limiting['remainingFlights'],
                'totalLife':        limiting['allowableFlights'],
                'nextItem':         second['item'] if second else None,
                'gainIfExtended':   (second['allowableFlights'] - limiting['allowableFlights']
                                     if second else 0.0)}

    # -------------------------------------------------------------------------------------------- #

    def severitySensitivity(self, factors: list = None) -> dict:

        '''

        Remaining life against how hard the article was flown.

        The point is the leverage. A twenty per cent harsher environment does not cost twenty per
        cent of the life left, because the damage already consumed does not shrink: it costs more,
        and the more flights are already on the article the worse the leverage gets.

        Far enough up the range the article is already past its limit. That is not an error in a
        sensitivity study, it is the answer, so it is recorded rather than raised.

        '''

        if factors is None:
            factors = [0.8, 1.0, 1.2, 1.5, 2.0]

        original = self.severityFactor
        results = []

        try:
            for factor in factors:

                self.severityFactor = factor

                try:
                    accumulation = self.calculateAccumulation()
                    results.append({'severityFactor':   factor,
                                    'limitingItem':     accumulation['limitingItem'],
                                    'remainingFlights': accumulation['remainingFlights'],
                                    'totalLife':        accumulation['totalLife'],
                                    'pastLimit':        False})

                except LifeError:

                    # Recompute the limiting item without the refusal, because the study needs to
                    # report which item went past and by how much.
                    worst = min(self.items.items(),
                                key = lambda item: MINER_LIMIT / (float(item[1]) * factor))
                    allowable = MINER_LIMIT / (float(worst[1]) * factor)

                    results.append({'severityFactor':   factor,
                                    'limitingItem':     worst[0],
                                    'remainingFlights': 0.0,
                                    'totalLife':        allowable,
                                    'pastLimit':        True})
        finally:
            self.severityFactor = original

        nominal = next(entry for entry in results if entry['severityFactor'] == 1.0)
        harsh = results[-1]

        # The factor at which the article first runs out, found by inverting the accumulation for
        # the limiting item rather than by searching the sweep.
        heaviest = max(float(damage) for damage in self.items.values())
        exhaustsAt = (MINER_LIMIT / (heaviest * self.flightsFlown)
                      if self.flightsFlown > 0.0 else np.inf)

        return {'results':          results,
                'nominalRemaining': nominal['remainingFlights'],
                'harshRemaining':   harsh['remainingFlights'],
                'exhaustsAtSeverity': exhaustsAt,
                'lifeLoss':         (1.0 - harsh['remainingFlights'] / nominal['remainingFlights']
                                     if nominal['remainingFlights'] > 0.0 else 1.0)}

    # -------------------------------------------------------------------------------------------- #

    def fleetLeaderLead(self, fleetFlights: list) -> dict:

        '''

        How much warning the fleet leader buys.

        The lead is the gap in flights between the leader and the next article, expressed in the
        life of the limiting item. **A fleet flown evenly has no leader and no warning**: every
        article reaches the limit at once, and the first indication is a failure rather than an
        inspection finding.

        '''

        if not fleetFlights:
            raise LifeError('A fleet with no articles has no leader.')

        counts = sorted((float(count) for count in fleetFlights), reverse = True)

        leader = counts[0]
        follower = counts[1] if len(counts) > 1 else leader

        accumulation = self.calculateAccumulation()
        perFlight = accumulation['items'][0]['damagePerFlight']

        lead = leader - follower

        return {'fleetSize':       len(counts),
                'leaderFlights':   leader,
                'followerFlights': follower,
                'leadInFlights':   lead,
                'leadInLife':      lead * perFlight,
                'leaderRemaining': max(0.0, accumulation['totalLife'] - leader),
                'hasWarning':      lead > 0.0,
                'limitingItem':    accumulation['limitingItem']}

    # -------------------------------------------------------------------------------------------- #

    def certifiedAgainstDemonstrated(self) -> dict:

        '''

        The gap between what has been demonstrated and what may be certified.

        A demonstrated life is one article surviving a count. A certified life has to cover the
        fleet, so it carries a scatter factor, and **the certified number is therefore always
        smaller than the demonstrated one**, often by a factor of several. A programme that quotes
        its demonstrated life as its certified life has skipped the step that covers the scatter.

        '''

        accumulation = self.calculateAccumulation()

        demonstrated = accumulation['totalLife']
        certified = demonstrated / self.scatterFactor

        result = {'demonstratedLife': demonstrated,
                  'scatterFactor':    self.scatterFactor,
                  'impliedCertified': certified,
                  'limitingItem':     accumulation['limitingItem']}

        if np.isfinite(self.certifiedLife):

            result['statedCertified'] = self.certifiedLife
            result['impliedScatter'] = demonstrated / self.certifiedLife
            result['coversScatter'] = self.certifiedLife <= certified

        return result

    # -------------------------------------------------------------------------------------------- #

    def inspectionLadder(self) -> dict:

        '''

        What each level of post-flight inspection costs and what it catches.

        The ordering is the useful part. **Cost rises faster than coverage**, which is why the
        disposition question is never "inspect more" and always "inspect what, and decide what on
        the answer".

        '''

        levels = [{'level':        name,
                   'relativeCost': entry['relativeCost'],
                   'catches':      entry['catches']}
                  for name, entry in INSPECTION_LEVELS.items()]

        levels.sort(key = lambda entry: entry['relativeCost'])

        return {'levels':      levels,
                'costSpread':  levels[-1]['relativeCost'] / levels[0]['relativeCost'],
                'endsTheArticle': levels[-1]['level']}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The accumulation, the limiting item, and what extending it would buy.
        '''

        accumulation = self.calculateAccumulation()

        lines = []

        lines.append(formatReportTable(
            [[entry['item'],
              f'{entry["allowableFlights"]:.0f}',
              f'{entry["consumed"] * 100.0:.0f}%',
              f'{entry["remainingFlights"]:.1f}'] for entry in accumulation['items']],
            ['item', 'allowable flights', 'consumed', 'remaining'],
            title = f'LIFE AFTER {self.flightsFlown:.0f} FLIGHTS'))

        lines.append('')
        lines.append(f'Limited by {accumulation["limitingItem"]} at '
                     f'{accumulation["remainingFlights"]:.1f} flights remaining.')

        if accumulation['nextItem']:
            lines.append(f'Extending it moves the limit to {accumulation["nextItem"]}, worth '
                         f'{accumulation["gainIfExtended"]:.0f} flights and no more.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'lifeTracking.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not np.isfinite(self.flightsFlown) or self.flightsFlown < 0.0:
            raise InvalidInputError('Flights flown cannot be negative.')

        if not self.items:
            raise InvalidInputError('At least one life limited item is needed.')

        for name, damage in self.items.items():
            if not 0.0 < float(damage) <= 1.0:
                raise InvalidInputError(
                    f'{name} has a damage per flight of {damage}, which is not a fraction of an '
                    f'allowable life. A value above one is an item that fails on its first flight.')

        if self.severityFactor <= 0.0:
            raise InvalidInputError('Severity factor must be positive.')

        if self.scatterFactor < 1.0:
            raise InvalidInputError('A scatter factor below one certifies past the demonstrated '
                                    'life, which is the opposite of what it is for.')
