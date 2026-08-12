
# -- PropellantLoading -- #

'''

How much propellant a launch consumes on the ground, which is more than the vehicle carries.

The flight load is the number everybody quotes. It is not what the ground system has to supply, and
on a cryogenic vehicle the difference is large enough to size the storage tank.

Four things are spent before liftoff and none of them reaches the engine.

**Chill-down** conditions the transfer line and the vehicle tank, and every kilogram of it boils and
vents. That mass is computed by `ChillDown` in propulsion/ignitionAndStart and is taken here as an
input rather than recomputed, because two implementations of an enthalpy balance would eventually
disagree.

**Boil-off during the load itself**, which runs for as long as the tanking does.

**Replenish during the hold**, which runs for as long as the hold does. A hold is therefore a
propellant cost as well as a schedule cost, and that is the connection between this class and
`CountdownTimeline`.

**The detank on a scrub**, which returns some of the load to storage and vents the rest, and then
the whole sequence repeats from chill-down on the next attempt.

**A scrub after tanking costs close to a full load.** That is the result this class exists to
produce, and it is why storage is sized in loads rather than in kilograms, and why the number of
attempts a campaign can afford is a propellant question before it is a schedule one.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from groundUtils import (LOADING_PHASES, REPLENISH_RATE_MARGIN,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, LoadingError)
except ImportError:
    from .groundUtils import (LOADING_PHASES, REPLENISH_RATE_MARGIN,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, LoadingError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Fraction of the vehicle load recovered to storage on a detank. The rest warms in the lines and
# vents. Recovery is possible only where the ground tank can accept warm returning fluid, which is
# a design decision made long before the scrub happens.
DEFAULT_DETANK_RECOVERY = 0.60    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- PropellantLoading -- #
# ------------------------------------------------------------------------------------------------ #

class PropellantLoading:

    '''

    Tanking sequence, elapsed time, and the ground propellant demand a launch attempt places on
    storage.

    '''

    def __init__(self):

        self.flightLoad     = np.nan
        self.transferRate   = np.nan
        self.chilldownMass  = np.nan
        self.boilOffRate    = np.nan
        self.holdDuration   = np.nan
        self.storageCapacity = np.nan
        self.detankRecovery = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `flightLoad` is the mass the vehicle carries at T-0 [kg]. `transferRate` is the maximum the
        ground system can deliver [kg/s], which the phase table scales down from.

        `chilldownMass` comes from propulsion/ignitionAndStart/ChillDown, which computes it as an
        enthalpy balance with an upper and a lower bound.

        `boilOffRate` is the steady vented rate once the tank is cold and full [kg/s], which comes
        from the insulation model in fluidSystems.

        `holdDuration` is the planned time at flight level before T-0.

        '''

        requiredParams = {'flightLoad':   (int, float),
                          'transferRate': (int, float),
                          'boilOffRate':  (int, float)}

        optionalParams = {'chilldownMass':   (int, float),
                          'holdDuration':    (int, float),
                          'storageCapacity': (int, float),
                          'detankRecovery':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.chilldownMass):
            self.chilldownMass = 0.0

        if not np.isfinite(self.holdDuration):
            self.holdDuration = 0.0

        if not np.isfinite(self.detankRecovery):
            self.detankRecovery = DEFAULT_DETANK_RECOVERY

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculatePhases(self) -> dict:

        '''

        The tanking sequence phase by phase: mass moved, rate, and elapsed time.

        Chill-down carries no load fraction, because none of it stays in the tank. Its duration is
        set by the mass and the reduced rate the phase runs at.

        '''

        phases = []
        elapsed = 0.0

        for name, phase in LOADING_PHASES.items():

            rate = self.transferRate * phase['rateFraction']

            if name == 'chilldown':
                mass = self.chilldownMass
            else:
                mass = self.flightLoad * phase['ofLoad']

            duration = mass / rate if rate > 0.0 else 0.0
            elapsed += duration

            phases.append({'phase':    name,
                           'mass':     mass,
                           'rate':     rate,
                           'duration': duration,
                           'purpose':  phase['purpose']})

        # The load fractions in the table are a sequence rather than a partition, so anything left
        # over belongs to fast fill. Checking rather than assuming, because a table edited later
        # would otherwise silently lose propellant.
        delivered = sum(entry['mass'] for entry in phases if entry['phase'] != 'chilldown')
        shortfall = self.flightLoad - delivered

        if abs(shortfall) > 1.0e-6 * self.flightLoad:
            for entry in phases:
                if entry['phase'] == 'fastFill':
                    entry['mass'] += shortfall
                    entry['duration'] = entry['mass'] / entry['rate']
            elapsed = sum(entry['duration'] for entry in phases)

        longest = max(phases, key = lambda entry: entry['duration'])

        return {'phases':       phases,
                'totalTime':    elapsed,
                'longestPhase': longest,
                'longestShare': longest['duration'] / elapsed if elapsed > 0.0 else 0.0}

    # -------------------------------------------------------------------------------------------- #

    def calculateGroundDemand(self) -> dict:

        '''

        Total propellant drawn from storage for one launch attempt, broken down by where it goes.

        The vehicle keeps the flight load. Everything else is spent.

        '''

        sequence = self.calculatePhases()

        # Boil-off runs through the fill and through the hold. During the fill the tank is filling,
        # so the average wetted area is lower; taking the full rate throughout is the conservative
        # reading and it is what a ground system is sized on.
        boilOffDuringFill = self.boilOffRate * sequence['totalTime']
        boilOffDuringHold = self.boilOffRate * self.holdDuration

        total = (self.chilldownMass + self.flightLoad
                 + boilOffDuringFill + boilOffDuringHold)

        breakdown = [{'item': 'chill-down',          'mass': self.chilldownMass},
                     {'item': 'flight load',         'mass': self.flightLoad},
                     {'item': 'boil-off during fill','mass': boilOffDuringFill},
                     {'item': 'replenish during hold','mass': boilOffDuringHold}]

        for entry in breakdown:
            entry['share'] = entry['mass'] / total

        spent = total - self.flightLoad

        result = {'breakdown':     breakdown,
                  'totalDemand':   total,
                  'flightLoad':    self.flightLoad,
                  'spent':         spent,
                  'demandRatio':   total / self.flightLoad,
                  'replenishRate': self.boilOffRate * REPLENISH_RATE_MARGIN}

        if np.isfinite(self.storageCapacity):

            if self.storageCapacity < total:
                raise LoadingError(
                    f'Storage holds {self.storageCapacity:,.0f} kg and one attempt draws '
                    f'{total:,.0f} kg. The tank cannot complete a single load.',
                    context = {'flightLoad':    self.flightLoad,
                                          'chilldownMass': self.chilldownMass,
                                          'holdDuration':  self.holdDuration})

            result['attemptsHeld'] = self.storageCapacity / total

        return result

    # -------------------------------------------------------------------------------------------- #

    def scrubCost(self) -> dict:

        '''

        What a scrub after tanking costs, and how many attempts the storage supports.

        A detank recovers some of the vehicle load and vents the rest. The next attempt starts from
        a warm tank, so the chill-down is paid again in full.

        '''

        attempt = self.calculateGroundDemand()

        recovered = self.flightLoad * self.detankRecovery
        lost = attempt['totalDemand'] - recovered

        result = {'attemptDemand':  attempt['totalDemand'],
                  'recovered':      recovered,
                  'lostOnScrub':    lost,
                  'lostFraction':   lost / self.flightLoad,
                  'detankRecovery': self.detankRecovery}

        if np.isfinite(self.storageCapacity):

            # Every attempt costs the lost mass, except that the last one has to complete, so the
            # attempts a tank supports are the scrubs it can absorb plus the launch itself.
            scrubs = int(np.floor((self.storageCapacity - attempt['totalDemand']) / lost)) \
                if lost > 0.0 else 0

            result['scrubsAffordable'] = max(0, scrubs)
            result['attemptsAffordable'] = max(1, scrubs + 1)

        return result

    # -------------------------------------------------------------------------------------------- #

    def holdSensitivity(self, durations: list = None) -> dict:

        '''

        Ground demand against hold duration.

        A hold is usually costed in schedule. On a cryogenic vehicle it is also a mass, and the
        slope is the boil-off rate, which makes it linear and easy to underestimate over a long
        hold.

        '''

        if durations is None:
            durations = [0.0, 600.0, 1800.0, 3600.0, 7200.0]

        original = self.holdDuration
        sweep = []

        try:
            for duration in durations:
                self.holdDuration = duration
                demand = self.calculateGroundDemand()
                sweep.append({'holdDuration': duration,
                              'totalDemand':  demand['totalDemand'],
                              'demandRatio':  demand['demandRatio']})
        finally:
            self.holdDuration = original

        span = sweep[-1]['totalDemand'] - sweep[0]['totalDemand']

        return {'sweep':      sweep,
                'span':       span,
                'spanShare':  span / self.flightLoad}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        The tanking sequence, the ground demand, and the scrub cost.

        '''

        sequence = self.calculatePhases()
        demand = self.calculateGroundDemand()
        scrub = self.scrubCost()

        lines = []

        lines.append(formatReportTable(
            [[entry['phase'],
              f'{entry["mass"]:,.0f}',
              f'{entry["rate"]:.1f}',
              f'{entry["duration"] / 60.0:.1f}'] for entry in sequence['phases']],
            ['phase', 'mass [kg]', 'rate [kg/s]', 'duration [min]'],
            title = 'TANKING SEQUENCE'))

        lines.append('')
        lines.append(f'Total tanking time {sequence["totalTime"] / 60.0:.1f} min, of which '
                     f'{sequence["longestShare"] * 100.0:.0f}% is {sequence["longestPhase"]["phase"]}.')
        lines.append('')

        lines.append(formatReportTable(
            [[entry['item'],
              f'{entry["mass"]:,.0f}',
              f'{entry["share"] * 100.0:.1f}%'] for entry in demand['breakdown']],
            ['item', 'mass [kg]', 'share'],
            title = 'GROUND PROPELLANT DEMAND'))

        lines.append('')
        lines.append(f'One attempt draws {demand["demandRatio"]:.2f} times the flight load.')
        lines.append(f'A scrub after tanking loses {scrub["lostFraction"]:.2f} flight loads.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'propellantLoading.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not np.isfinite(self.flightLoad) or self.flightLoad <= 0.0:
            raise InvalidInputError('Flight load must be a positive mass in kilograms.')

        if not np.isfinite(self.transferRate) or self.transferRate <= 0.0:
            raise InvalidInputError('Transfer rate must be a positive mass flow in kg/s.')

        if not np.isfinite(self.boilOffRate) or self.boilOffRate < 0.0:
            raise InvalidInputError('Boil-off rate cannot be negative.')

        if self.chilldownMass < 0.0:
            raise InvalidInputError('Chill-down mass cannot be negative.')

        if self.holdDuration < 0.0:
            raise InvalidInputError('Hold duration cannot be negative.')

        if not 0.0 <= self.detankRecovery <= 1.0:
            raise InvalidInputError('Detank recovery is a fraction between zero and one.')

        # Topping runs at a fraction of the transfer rate, and if that fraction falls below the
        # boil-off the tank never reaches flight level. That is a real failure and it is quiet: the
        # level sensor simply stops rising.
        toppingRate = self.transferRate * LOADING_PHASES['topping']['rateFraction']

        if toppingRate <= self.boilOffRate:
            raise LoadingError(
                f'Topping runs at {toppingRate:.2f} kg/s against a boil-off of '
                f'{self.boilOffRate:.2f} kg/s, so the tank cannot reach flight level. This fails '
                f'quietly on a pad: the level simply stops rising.',
                context = {'transferRate': self.transferRate,
                                      'boilOffRate':  self.boilOffRate})
