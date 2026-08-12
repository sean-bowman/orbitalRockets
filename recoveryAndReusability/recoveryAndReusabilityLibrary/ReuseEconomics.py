
# -- ReuseEconomics -- #

'''

Whether reuse pays, and what actually decides it.

The cost of a flight on a reusable stage is the stage amortised over its flights, plus the
refurbishment, plus the recovery operation, plus everything that was never reusable in the first
place:

    cost per flight = unit cost / flights + refurbishment + recovery + expendable elements

**The first term collapses fast and the others do not.** Going from one flight to two halves the
amortised unit cost; going from ten to twenty saves five per cent of it. So **most of the benefit of
reuse arrives in the first few flights**, and the argument for a very high flight count is about the
fixed terms rather than about amortisation.

That has a consequence people get backwards. Once the flight count is high, **the refurbishment cost
is the whole game**, because it is paid every flight and the amortised term has already gone to
nothing. A programme optimising flight count when its refurbishment cost is high is optimising the
term that has already stopped mattering.

**Recovery does not always succeed**, and a lost stage costs a whole unit. That turns the effective
flight count into an expectation rather than a plan, and at a low success rate the fleet shrinks
faster than it accumulates flights.

**The payload penalty is a cost too**, and it is the one most often left out. A reusable flight
carries less, so the cost per kilogram delivered rises even when the cost per flight falls.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from recoveryUtils import (applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, EconomicsError)
except ImportError:
    from .recoveryUtils import (applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, EconomicsError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Costs are carried as fractions of one expendable unit cost throughout, so the class never needs a
# currency and never goes stale. A refurbishment cost of 0.1 is a tenth of building a new stage.
EXPENDABLE_UNIT_COST = 1.0    # [-]

# Below this the amortised term has fallen far enough that further flights barely move the cost.
# It is a reporting threshold rather than a physical one.
AMORTISATION_EXHAUSTED = 0.05    # [-] of unit cost

# ------------------------------------------------------------------------------------------------ #
# -- ReuseEconomics -- #
# ------------------------------------------------------------------------------------------------ #

class ReuseEconomics:

    '''

    Cost per flight against flight count, the break-even, and what moves it.

    '''

    def __init__(self):

        self.refurbishmentCost = np.nan
        self.recoveryCost      = np.nan
        self.expendableElements = np.nan
        self.recoverySuccess   = np.nan
        self.flightsPerArticle = np.nan
        self.payloadPenalty    = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Every cost is a fraction of one expendable unit cost, so the class carries no currency.

        `refurbishmentCost` is paid every flight. `recoveryCost` covers the ships, the pad crew and
        the transport. `expendableElements` is everything not recovered, principally the upper
        stage and the fairing where those are not recovered.

        `recoverySuccess` is the probability the stage comes back usable, which turns the flight
        count into an expectation.

        `payloadPenalty` is the fraction of payload given up, from RecoveryBudget, and it turns a
        cost per flight into a cost per kilogram.

        '''

        requiredParams = {'refurbishmentCost': (int, float),
                          'flightsPerArticle': (int, float)}

        optionalParams = {'recoveryCost':       (int, float),
                          'expendableElements': (int, float),
                          'recoverySuccess':    (int, float),
                          'payloadPenalty':     (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        for attribute in ('recoveryCost', 'expendableElements', 'payloadPenalty'):
            if not np.isfinite(getattr(self, attribute)):
                setattr(self, attribute, 0.0)

        if not np.isfinite(self.recoverySuccess):
            self.recoverySuccess = 1.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def effectiveFlights(self) -> dict:

        '''

        Flights actually achieved per article once recovery can fail.

        A stage recovered with probability p flies a geometric number of times before it is lost,
        capped by the design life. The expectation is the smaller of the two effects, and at a low
        success rate it is the recovery rather than the life limit that sets it.

        '''

        if self.recoverySuccess >= 1.0:
            return {'planned':   self.flightsPerArticle,
                    'expected':  self.flightsPerArticle,
                    'limitedBy': 'design life',
                    'recoverySuccess': 1.0}

        # Expected flights before loss, for a stage flown until it is lost or reaches its life.
        # Sum over n of the probability of surviving to fly an nth time.
        planned = int(np.floor(self.flightsPerArticle))
        expected = sum(self.recoverySuccess ** index for index in range(planned))

        return {'planned':   self.flightsPerArticle,
                'expected':  expected,
                'limitedBy': 'recovery losses' if expected < 0.8 * planned else 'design life',
                'recoverySuccess': self.recoverySuccess,
                'shortfall': 1.0 - expected / planned if planned > 0 else 0.0}

    # -------------------------------------------------------------------------------------------- #

    def costPerFlight(self, flights: float = None) -> dict:

        '''

        Cost of one flight, split into the term that amortises and the terms that do not.

        '''

        count = flights if flights is not None else self.effectiveFlights()['expected']

        if count <= 0.0:
            raise EconomicsError('A flight count of zero has no cost per flight.')

        amortised = EXPENDABLE_UNIT_COST / count
        recurring = self.refurbishmentCost + self.recoveryCost + self.expendableElements

        total = amortised + recurring

        return {'flights':        count,
                'amortisedUnit':  amortised,
                'refurbishment':  self.refurbishmentCost,
                'recovery':       self.recoveryCost,
                'expendable':     self.expendableElements,
                'recurring':      recurring,
                'costPerFlight':  total,
                'amortisedShare': amortised / total,
                'againstExpendable': total / (EXPENDABLE_UNIT_COST + self.expendableElements)}

    # -------------------------------------------------------------------------------------------- #

    def breakEven(self) -> dict:

        '''

        The flight count at which reuse becomes cheaper than expending.

        An expendable flight costs one unit plus the expendable elements. A reusable one costs the
        amortised unit plus the recurring terms. Setting them equal gives

            n = 1 / (1 - refurbishment - recovery)

        **and the break-even does not exist at all if the recurring terms exceed one unit**, which
        is the failure mode worth naming: a stage that costs as much to refurbish as to build is
        never worth recovering, at any flight count.

        '''

        recurring = self.refurbishmentCost + self.recoveryCost

        if recurring >= EXPENDABLE_UNIT_COST:
            raise EconomicsError(
                f'Refurbishment and recovery together cost {recurring:.2f} unit costs, so a '
                f'reusable flight is dearer than an expendable one at every flight count. There '
                f'is no break-even to find. **The fix is the refurbishment cost, not the flight '
                f'count.**',
                context = {'refurbishmentCost': self.refurbishmentCost,
                           'recoveryCost':      self.recoveryCost})

        flights = EXPENDABLE_UNIT_COST / (EXPENDABLE_UNIT_COST - recurring)

        expendableCost = EXPENDABLE_UNIT_COST + self.expendableElements
        atPlanned = self.costPerFlight()

        return {'breakEvenFlights': flights,
                'recurringCost':    recurring,
                'expendableCost':   expendableCost,
                'costAtPlanned':    atPlanned['costPerFlight'],
                'savingAtPlanned':  1.0 - atPlanned['costPerFlight'] / expendableCost,
                'achievesBreakEven': self.effectiveFlights()['expected'] >= flights}

    # -------------------------------------------------------------------------------------------- #

    def flightCountSweep(self, counts: list = None) -> dict:

        '''

        Cost per flight against flight count, and where the amortised term stops mattering.

        The shape is the result: most of the benefit is in the first few flights, and the curve is
        flat long before the design life.

        '''

        if counts is None:
            counts = [1, 2, 3, 5, 10, 20, 40]

        sweep = []

        for count in counts:
            cost = self.costPerFlight(float(count))
            sweep.append({'flights':        count,
                          'costPerFlight':  cost['costPerFlight'],
                          'amortisedUnit':  cost['amortisedUnit'],
                          'amortisedShare': cost['amortisedShare']})

        for index, entry in enumerate(sweep):
            previous = sweep[index - 1]['costPerFlight'] if index > 0 else None
            entry['marginalSaving'] = (previous - entry['costPerFlight']) if previous else 0.0

        exhausted = next((entry['flights'] for entry in sweep
                          if entry['amortisedUnit'] <= AMORTISATION_EXHAUSTED), None)

        firstThree = sweep[0]['costPerFlight'] - sweep[2]['costPerFlight']
        wholeRange = sweep[0]['costPerFlight'] - sweep[-1]['costPerFlight']

        return {'sweep':                sweep,
                'amortisationExhausted': exhausted,
                'shareOfBenefitInThree': firstThree / wholeRange if wholeRange > 0.0 else 0.0,
                'floorCost':            self.refurbishmentCost + self.recoveryCost
                                        + self.expendableElements}

    # -------------------------------------------------------------------------------------------- #

    def costPerKilogram(self) -> dict:

        '''

        The comparison that includes the payload penalty.

        A reusable flight costs less and carries less. **The cost per kilogram can rise while the
        cost per flight falls**, and which of those a customer cares about depends entirely on
        whether their payload fits.

        '''

        cost = self.costPerFlight()

        expendableCost = EXPENDABLE_UNIT_COST + self.expendableElements
        reusableFraction = 1.0 - self.payloadPenalty

        if reusableFraction <= 0.0:
            raise EconomicsError('A payload penalty of one or more leaves nothing to launch.')

        expendablePerKg = expendableCost / 1.0
        reusablePerKg = cost['costPerFlight'] / reusableFraction

        return {'expendablePerFlight':  expendableCost,
                'reusablePerFlight':    cost['costPerFlight'],
                'flightSaving':         1.0 - cost['costPerFlight'] / expendableCost,
                'payloadPenalty':       self.payloadPenalty,
                'expendablePerKilogram': expendablePerKg,
                'reusablePerKilogram':  reusablePerKg,
                'kilogramSaving':       1.0 - reusablePerKg / expendablePerKg,
                'penaltyErodesSaving':  self.payloadPenalty > 0.0}

    # -------------------------------------------------------------------------------------------- #

    def refurbishmentSensitivity(self, costs: list = None) -> dict:

        '''

        Break-even and cost per flight against refurbishment cost.

        This is the sweep that matters once the flight count is high, and it is the one that is
        usually not run.

        '''

        if costs is None:
            costs = [0.02, 0.05, 0.10, 0.20, 0.40]

        original = self.refurbishmentCost
        results = []

        try:
            for cost in costs:

                self.refurbishmentCost = cost

                try:
                    breakEven = self.breakEven()['breakEvenFlights']
                except EconomicsError:
                    breakEven = np.inf

                results.append({'refurbishmentCost': cost,
                                'breakEvenFlights':  breakEven,
                                'costPerFlight':     self.costPerFlight()['costPerFlight']})
        finally:
            self.refurbishmentCost = original

        return {'results':     results,
                'costSpread':  results[-1]['costPerFlight'] / results[0]['costPerFlight'],
                'breakEvenSpread': (results[-1]['breakEvenFlights']
                                    / results[0]['breakEvenFlights'])}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The cost split, the break-even, and the sweep.
        '''

        cost = self.costPerFlight()
        sweep = self.flightCountSweep()

        lines = []

        lines.append(formatReportTable(
            [['amortised unit', f'{cost["amortisedUnit"]:.3f}',
              f'{cost["amortisedShare"] * 100.0:.0f}%'],
             ['refurbishment',  f'{cost["refurbishment"]:.3f}', ''],
             ['recovery',       f'{cost["recovery"]:.3f}', ''],
             ['expendable',     f'{cost["expendable"]:.3f}', ''],
             ['total',          f'{cost["costPerFlight"]:.3f}', '']],
            ['term', 'unit costs', 'share'],
            title = f'COST PER FLIGHT AT {cost["flights"]:.1f} FLIGHTS'))

        lines.append('')

        lines.append(formatReportTable(
            [[f'{entry["flights"]}',
              f'{entry["costPerFlight"]:.3f}',
              f'{entry["amortisedShare"] * 100.0:.0f}%',
              f'{entry["marginalSaving"]:.3f}'] for entry in sweep['sweep']],
            ['flights', 'cost per flight', 'amortised share', 'marginal saving'],
            title = 'FLIGHT COUNT'))

        lines.append('')
        lines.append(f'{sweep["shareOfBenefitInThree"] * 100.0:.0f}% of the benefit arrives by the '
                     f'third flight, and the floor is {sweep["floorCost"]:.3f} unit costs.')

        try:
            breakEven = self.breakEven()
            lines.append(f'Break-even at {breakEven["breakEvenFlights"]:.1f} flights.')
        except EconomicsError as error:
            lines.append('NO BREAK-EVEN')
            lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'reuseEconomics.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        for name in ('refurbishmentCost', 'recoveryCost', 'expendableElements', 'payloadPenalty'):
            if getattr(self, name) < 0.0:
                raise InvalidInputError(f'{name} cannot be negative.')

        if not np.isfinite(self.flightsPerArticle) or self.flightsPerArticle < 1.0:
            raise InvalidInputError('An article flies at least once.')

        if not 0.0 < self.recoverySuccess <= 1.0:
            raise InvalidInputError('Recovery success is a probability above zero and at or below '
                                    'one. A rate of zero is an expendable vehicle with legs on it.')

        if self.payloadPenalty >= 1.0:
            raise InvalidInputError('A payload penalty of one leaves nothing to launch.')
