
# -- StagedVehicle -- #

'''

The rocket equation across stages, the payload it leaves, and how little the staging split matters.

Two results are worth having and they pull in opposite directions.

**The optimal delta-V split is flat.** Perturbing the split between stages by ten per cent from the
optimum costs a fraction of a per cent of payload. The optimisation is worth doing once and it is
not worth defending.

**The payload is violently sensitive to the structural coefficient.** It is the residual of a large
subtraction, so a one per cent error in stage dry mass fraction is a payload error an order of
magnitude larger. Every hour spent on the staging split would be better spent on the tank.

Those two together are the argument for this whole domain. The thing that looks like the design
decision is not, and the thing that looks like an estimating detail is.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from vehicleUtils import (STANDARD_GRAVITY, STRUCTURAL_COEFFICIENT_BAND,
                              exhaustVelocity, deltaV, structuralCoefficient,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, ClosureError, StagingError)
except ImportError:
    from .vehicleUtils import (STANDARD_GRAVITY, STRUCTURAL_COEFFICIENT_BAND,
                               exhaustVelocity, deltaV, structuralCoefficient,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, ClosureError, StagingError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Bracket and tolerance for the staging optimisation, which solves one scalar equation.
LAGRANGE_LOWER = 1.0e-6
LAGRANGE_UPPER = 1.0e2
LAGRANGE_TOLERANCE = 1.0e-10
LAGRANGE_ITERATIONS = 200

# How far the delta-V split is perturbed when demonstrating that the optimum is flat.
FLATNESS_PERTURBATION = 0.10    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- StagedVehicle -- #
# ------------------------------------------------------------------------------------------------ #

class StagedVehicle:

    '''

    Payload, mass breakdown and staging optimisation for a serially staged vehicle.

    '''

    def __init__(self):

        self.stages       = []
        self.payloadMass  = np.nan
        self.targetDeltaV = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `stages` is a list of dictionaries, ordered from the one that fires first. Each needs a
        `specificImpulse` and a `structuralCoefficient`, and either a `propellantMass` for a
        defined vehicle or nothing at all for one being sized to a delta-V target.

        Supply either `payloadMass` with defined stages, or `targetDeltaV` with a payload, and the
        class computes the other.

        '''

        requiredParams = {'stages': list}

        optionalParams = {'payloadMass':  (int, float),
                          'targetDeltaV': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def exhaustVelocities(self) -> list:

        return [exhaustVelocity(stage['specificImpulse']) for stage in self.stages]

    # -------------------------------------------------------------------------------------------- #

    def calculatePerformance(self) -> dict:

        '''

        The delta-V a defined vehicle delivers, stage by stage, from the top down.

        The bookkeeping is the part that goes wrong. Each stage lifts everything above it, so the
        upper stages have to be resolved first and the burnout mass of a stage includes its own dry
        mass plus everything it is still carrying.

        '''

        for index, stage in enumerate(self.stages):
            if 'propellantMass' not in stage:
                raise StagingError(
                    f'Stage {index + 1} has no propellant mass, so this vehicle is not defined and '
                    f'its performance cannot be computed. Use sizeToDeltaV() to size it instead.',
                    context = createErrorContext(component = 'StagedVehicle'))

        if not np.isfinite(self.payloadMass):
            raise InvalidInputError(
                'A payload mass is needed to compute the performance of a defined vehicle.',
                context = createErrorContext(component = 'StagedVehicle'))

        exhausts = self.exhaustVelocities()

        # gross mass of each stage, from its propellant and its structural coefficient
        grossMasses = []
        dryMasses   = []

        for index, stage in enumerate(self.stages):

            epsilon = stage['structuralCoefficient']

            # eps = dry / gross and gross = dry + propellant, so gross = propellant / (1 - eps)
            gross = stage['propellantMass'] / (1.0 - epsilon)

            grossMasses.append(gross)
            dryMasses.append(gross - stage['propellantMass'])

        # the mass each stage has to lift is itself plus everything above it plus the payload
        results = []

        total = 0.0

        for index in range(len(self.stages)):

            above = sum(grossMasses[index + 1:]) + self.payloadMass

            initial = grossMasses[index] + above
            final   = initial - self.stages[index]['propellantMass']

            increment = deltaV(exhausts[index], initial / final)

            total += increment

            results.append({'stage':          index + 1,
                            'grossMass':      grossMasses[index],
                            'dryMass':        dryMasses[index],
                            'propellantMass': self.stages[index]['propellantMass'],
                            'initialMass':    initial,
                            'burnoutMass':    final,
                            'massRatio':      initial / final,
                            'deltaV':         increment,
                            'exhaustVelocity': exhausts[index]})

        liftoffMass = sum(grossMasses) + self.payloadMass

        return {'stages':      results,
                'totalDeltaV': total,
                'liftoffMass': liftoffMass,
                'payloadMass': self.payloadMass,
                'payloadFraction': self.payloadMass / liftoffMass}

    # -------------------------------------------------------------------------------------------- #

    def optimiseStaging(self) -> dict:

        '''

        The delta-V split that maximises payload for a given total, by the classical Lagrange
        multiplier condition.

        Maximising payload subject to a fixed total delta-V gives, for each stage,

            massRatio_i = (c_i * L - 1) / (c_i * L * eps_i)

        with one Lagrange multiplier `L` shared across the stages, chosen so the delta-V sums to
        the target. That is one scalar equation in one unknown and it is solved by bisection.

        The condition is only meaningful where every mass ratio comes out above one, which requires
        `c_i * L > 1 / (1 - eps_i)`. Below that the stage would have to end heavier than it started
        and the bracket is moved rather than the result reported.

        '''

        if not np.isfinite(self.targetDeltaV):
            raise InvalidInputError(
                'A target delta-V is needed to optimise a staging split.',
                context = createErrorContext(component = 'StagedVehicle'))

        exhausts     = self.exhaustVelocities()
        coefficients = [stage['structuralCoefficient'] for stage in self.stages]

        def totalDeltaV(multiplier: float) -> float:

            total = 0.0

            for exhaust, epsilon in zip(exhausts, coefficients):

                numerator = exhaust * multiplier - 1.0

                if numerator <= 0.0:
                    return -np.inf

                ratio = numerator / (exhaust * multiplier * epsilon)

                if ratio <= 1.0:
                    return -np.inf

                total += exhaust * np.log(ratio)

            return total

        # The total delta-V rises monotonically with the multiplier, from zero at the point where
        # the last stage becomes admissible up to the asymptote where every mass ratio reaches
        # 1 / eps. So the feasibility check belongs at the HIGH end, where the maximum is.
        #
        # The lower bracket is computed rather than searched for. A stage is admissible when its
        # mass ratio exceeds one, which requires c_i * L * (1 - eps_i) > 1, so the binding bound is
        # the largest of those across the stages. An earlier version found this by multiplying a
        # small starting value by 1.5 until it became admissible, and that overshot the boundary by
        # enough to skip the region containing the answer, pinning the optimiser at a corner and
        # silently returning a split that did not sum to the target.
        boundary = max(1.0 / (exhaust * (1.0 - epsilon))
                       for exhaust, epsilon in zip(exhausts, coefficients))

        lower = boundary * (1.0 + LAGRANGE_TOLERANCE)
        upper = LAGRANGE_UPPER

        ceiling = totalDeltaV(upper)

        if lower >= upper or ceiling < self.targetDeltaV:

            # the asymptote, which is what these stages could deliver with infinite propellant
            asymptote = sum(exhaust * np.log(1.0 / epsilon)
                            for exhaust, epsilon in zip(exhausts, coefficients))

            raise StagingError(
                f'No staging split reaches {self.targetDeltaV:.0f} m/s with these stages. Even '
                f'with unbounded propellant these structural coefficients {coefficients} cap the '
                f'delta-V at {asymptote:.0f} m/s, because a stage cannot exceed a mass ratio of '
                f'one over its structural coefficient. No split of an unreachable total is '
                f'possible, so the structure or the propellant has to change rather than the '
                f'staging.',
                context = createErrorContext(component = 'StagedVehicle'))

        for _ in range(LAGRANGE_ITERATIONS):

            middle = 0.5 * (lower + upper)

            if totalDeltaV(middle) > self.targetDeltaV:
                upper = middle
            else:
                lower = middle

            if abs(upper - lower) < LAGRANGE_TOLERANCE * max(1.0, abs(lower)):
                break

        multiplier = 0.5 * (lower + upper)

        splits = []

        for exhaust, epsilon in zip(exhausts, coefficients):

            ratio = (exhaust * multiplier - 1.0) / (exhaust * multiplier * epsilon)

            splits.append({'massRatio': ratio,
                           'deltaV':    exhaust * np.log(ratio)})

        total = sum(entry['deltaV'] for entry in splits)

        return {'multiplier': multiplier,
                'splits':     splits,
                'deltaVSplit': [entry['deltaV'] for entry in splits],
                'fractions':  [entry['deltaV'] / total for entry in splits],
                'totalDeltaV': total}

    # -------------------------------------------------------------------------------------------- #

    def sizeToDeltaV(self, split: list = None) -> dict:

        '''

        Size the stages from the payload up, to a given delta-V split.

        With no split supplied the optimal one is used. The stages are built from the top down,
        because each stage's propellant depends on everything above it and nothing below it.

        '''

        if not np.isfinite(self.payloadMass):
            raise InvalidInputError(
                'A payload mass is needed to size a vehicle to a delta-V target.',
                context = createErrorContext(component = 'StagedVehicle'))

        if split is None:
            split = self.optimiseStaging()['deltaVSplit']

        if len(split) != len(self.stages):
            raise StagingError(
                f'The delta-V split has {len(split)} entries and the vehicle has '
                f'{len(self.stages)} stages.',
                context = createErrorContext(component = 'StagedVehicle'))

        exhausts = self.exhaustVelocities()

        carried = self.payloadMass

        stages = []

        for index in reversed(range(len(self.stages))):

            epsilon = self.stages[index]['structuralCoefficient']

            ratio = float(np.exp(split[index] / exhausts[index]))

            # from mass ratio and structural coefficient, the gross mass that lifts `carried`
            denominator = 1.0 - ratio * epsilon

            if denominator <= 0.0:
                raise ClosureError(
                    f'Stage {index + 1} cannot deliver {split[index]:.0f} m/s at a structural '
                    f'coefficient of {epsilon:.3f}. The required mass ratio of {ratio:.2f} times '
                    f'that coefficient exceeds one, which means the stage structure alone weighs '
                    f'more than the propellant it would need. **This vehicle does not close**, and '
                    f'that is reported as a failure rather than as a negative payload, because a '
                    f'negative payload invites somebody to treat it as a small one.',
                    context = createErrorContext(component = 'StagedVehicle'))

            gross = carried * (ratio - 1.0) / denominator

            propellant = gross * (1.0 - epsilon)
            dry        = gross * epsilon

            stages.insert(0, {'stage':          index + 1,
                              'grossMass':      gross,
                              'dryMass':        dry,
                              'propellantMass': propellant,
                              'massRatio':      ratio,
                              'deltaV':         split[index],
                              'carriedAbove':   carried})

            carried += gross

        return {'stages':      stages,
                'liftoffMass': carried,
                'payloadMass': self.payloadMass,
                'payloadFraction': self.payloadMass / carried,
                'totalDeltaV': sum(split),
                'split':       list(split)}

    # -------------------------------------------------------------------------------------------- #

    def checkStagingFlatness(self, perturbation: float = FLATNESS_PERTURBATION) -> dict:

        '''

        How much payload the optimal split is actually worth, which is the result this class
        exists to produce.

        The optimum is perturbed by shifting delta-V from one stage to the other and re-sizing.
        The liftoff mass needed to deliver the same payload is the comparison, because that is what
        a heavier design costs.

        '''

        if len(self.stages) < 2:
            raise StagingError(
                'Staging flatness needs at least two stages to shift delta-V between.',
                context = createErrorContext(component = 'StagedVehicle'))

        findings = []

        optimal = self.optimiseStaging()['deltaVSplit']

        baseline = self.sizeToDeltaV(optimal)

        shift = perturbation * optimal[0]

        cases = {}

        for name, direction in (('more on the first stage', +1.0),
                                ('more on the second stage', -1.0)):

            trial = list(optimal)

            trial[0] += direction * shift
            trial[1] -= direction * shift

            sized = self.sizeToDeltaV(trial)

            cases[name] = {'split':       trial,
                           'liftoffMass': sized['liftoffMass'],
                           'penalty':     sized['liftoffMass'] / baseline['liftoffMass'] - 1.0}

        worst = max(cases, key = lambda name: cases[name]['penalty'])

        findings.append(
            f'The optimal split puts {optimal[0] / sum(optimal):.0%} of the delta-V on the first '
            f'stage.')

        findings.append(
            f'Shifting {perturbation:.0%} of the first stage delta-V either way costs at most '
            f'{cases[worst]["penalty"]:.2%} of liftoff mass.')

        findings.append(
            'The optimum is flat. It is worth finding once and it is not worth defending, and an '
            'argument about the staging split is almost always an argument about the wrong thing.')

        self.findings = findings

        return {'optimalSplit': optimal,
                'baselineLiftoffMass': baseline['liftoffMass'],
                'cases':        cases,
                'worstPenalty': cases[worst]['penalty'],
                'isFlat':       bool(cases[worst]['penalty'] < 0.02),
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def payloadSensitivity(self, perturbation: float = 0.01) -> dict:

        '''

        How much payload moves when each input moves by one per cent, on two different vehicles.

        **The two answers differ by an order of magnitude and the difference is the point.**

        A *rubber* vehicle is re-sized around the change: the tanks grow, the liftoff mass grows,
        and the payload fraction absorbs most of the error. That is the sensitivity that matters
        during conceptual design, when the vehicle is still a spreadsheet.

        A *fixed* vehicle has already been built. The propellant load and the tank volumes are what
        they are, so an error in dry mass comes off the payload and nothing else. That is the
        sensitivity that matters after metal is cut, and it is much larger, because **payload is
        the residual of a large subtraction**.

        The elasticity reported in both cases is the fractional change in payload per fractional
        change in the input, which makes them comparable across quantities with different units.

        '''

        if not np.isfinite(self.targetDeltaV):
            raise InvalidInputError(
                'A target delta-V is needed to compute a payload sensitivity, because payload is '
                'what is being solved for.',
                context = createErrorContext(component = 'StagedVehicle'))

        findings = []

        baseline = self._payloadForFixedLiftoff()

        elasticities = {}

        for index, stage in enumerate(self.stages):

            for parameter in ('specificImpulse', 'structuralCoefficient'):

                original = stage[parameter]

                stage[parameter] = original * (1.0 + perturbation)

                try:
                    moved = self._payloadForFixedLiftoff()
                    elasticity = (moved / baseline - 1.0) / perturbation
                except (ClosureError, StagingError):
                    elasticity = np.nan
                finally:
                    stage[parameter] = original

                elasticities[f'stage {index + 1} {parameter}'] = elasticity

        original = self.targetDeltaV
        self.targetDeltaV = original * (1.0 + perturbation)

        try:
            moved = self._payloadForFixedLiftoff()
            elasticities['target delta-V'] = (moved / baseline - 1.0) / perturbation
        except (ClosureError, StagingError):
            elasticities['target delta-V'] = np.nan
        finally:
            self.targetDeltaV = original

        finite = {name: value for name, value in elasticities.items() if np.isfinite(value)}

        largest = max(finite, key = lambda name: abs(finite[name]))

        fixed = self._fixedVehicleSensitivity(perturbation)

        structural = max(abs(value) for name, value in finite.items() if 'structural' in name)

        payloadFraction = self.sizeToDeltaV()['payloadFraction']

        findings.append(
            f'On a rubber vehicle, a one per cent change in {largest} moves the payload fraction '
            f'by {abs(finite[largest]):.2f} per cent, and the largest structural elasticity is '
            f'{structural:.2f}.')

        findings.append(
            f'On the same vehicle already built, a one per cent dry mass error costs '
            f'{abs(fixed["dryMassElasticity"]):.2f} per cent of payload. A built vehicle cannot '
            f'grow to absorb an estimating error, so it comes off the payload instead.')

        findings.append(
            f'**Both elasticities are of order one on this vehicle, and that is a statement about '
            f'this vehicle rather than about rockets.** At a payload fraction of '
            f'{payloadFraction:.2%} the payload is not a knife-edge residual: it is comparable to '
            f'the total dry mass. The elasticity scales roughly inversely with payload fraction, '
            f'so a marginal design at one per cent carries several times this sensitivity and a '
            f'design near closure carries far more.')

        findings.append(
            'The common statement that small upstream errors are large payload errors is therefore '
            'a claim about marginal vehicles, not about the rocket equation. It becomes true '
            'exactly when a design stops having margin, which is when it is least able to respond.')

        return {'baselinePayload': baseline,
                'elasticities':    elasticities,
                'largest':         largest,
                'fixedVehicle':    fixed,
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def exchangeRatios(self, step: float = 10.0) -> dict:

        '''

        Payload lost per kilogram of first stage dry mass, and per kilogram of first stage
        propellant that the ascent burn does not use.

        These are the two numbers a recovery budget needs, and they are properties of the vehicle
        rather than of the recovery system: a landing leg and a landing burn cost payload through
        the same rocket equation that everything else on the stage does.

        The two perturbations are different in one respect and that is the whole result. Added dry
        mass raises the first stage initial mass and its burnout mass together. Reserved propellant
        is already aboard, so it raises the burnout mass alone. Differentiating the stage
        contribution `c ln(I / F)` gives `c (1/I - 1/F)` for the first and `-c / F` for the second,
        so their ratio is

            dry / reserve = 1 - F / I = 1 - 1 / R

        with `R` the first stage mass ratio. **That is below one on every vehicle that flies**,
        which means a kilogram of reserve propellant always costs more payload than a kilogram of
        dry mass. The offsetting rise in initial mass is what dry mass gets and reserve does not.

        The closed form is exact and it is reported alongside the numerical result rather than
        instead of it, because a closed form that has not been checked against the thing it claims
        to describe is a claim about algebra.

        '''

        if step <= 0.0:
            raise InvalidInputError(
                f'A perturbation of {step} kg cannot produce a gradient.',
                context = createErrorContext(component = 'StagedVehicle'))

        # A vehicle whose propellant loads are given is taken as built, because a recovery budget
        # is written against a stage that exists. Only a vehicle without them is re-optimised, and
        # the exchange ratio then belongs to the optimal split rather than to any real article.
        asBuilt = all('propellantMass' in stage for stage in self.stages)

        sized  = self.calculatePerformance() if asBuilt else self.sizeToDeltaV()
        target = self.targetDeltaV if np.isfinite(self.targetDeltaV) else sized['totalDeltaV']

        if not np.isfinite(target):
            raise InvalidInputError(
                'A target delta-V is needed to compute an exchange ratio, because the ratio is '
                'measured by holding the mission fixed and letting the payload move.',
                context = createErrorContext(component = 'StagedVehicle'))

        exhausts    = self.exhaustVelocities()
        drys        = [entry['dryMass'] for entry in sized['stages']]
        propellants = [entry['propellantMass'] for entry in sized['stages']]

        def payloadFor(dryMasses: list, loads: list, burned: list) -> float:

            '''
            Payload achieving the target, with the loaded propellant and the burned propellant
            carried separately so that a reserve can be held aboard without being spent.
            '''

            def achieved(payload: float) -> float:

                total = 0.0

                for index in range(len(dryMasses)):

                    above = (sum(dryMasses[index + 1:]) + sum(loads[index + 1:]) + payload)

                    initial = dryMasses[index] + loads[index] + above
                    final   = initial - burned[index]

                    total += exhausts[index] * np.log(initial / final)

                return total

            low, high = 0.0, max(sized.get('payloadMass', self.payloadMass), 1.0) * 10.0

            # delta-V falls as payload rises, so bisect downward
            if achieved(low) < target:
                return 0.0

            for _ in range(LAGRANGE_ITERATIONS):

                middle = 0.5 * (low + high)

                if achieved(middle) > target:
                    low = middle
                else:
                    high = middle

                if high - low < 1.0e-9 * max(1.0, high):
                    break

            return 0.5 * (low + high)

        baseline = payloadFor(drys, propellants, propellants)

        if baseline <= 0.0:
            raise ClosureError(
                'This vehicle delivers no payload on the target mission, so there is no payload '
                'for recovery hardware to be traded against.',
                context = createErrorContext(component = 'StagedVehicle'))

        # Added hardware on the first stage: liftoff mass and burnout mass both rise.
        heavier = payloadFor([drys[0] + step] + drys[1:], propellants, propellants)

        # Propellant already loaded that the ascent burn does not use: burnout mass alone rises.
        reserved = payloadFor(drys, propellants,
                              [propellants[0] - step] + propellants[1:])

        dryRatio     = (baseline - heavier)  / step
        reserveRatio = (baseline - reserved) / step

        initial = sum(drys) + sum(propellants) + baseline
        final   = initial - propellants[0]

        firstStageMassRatio = initial / final
        closedForm          = 1.0 - final / initial

        measured = dryRatio / reserveRatio if reserveRatio > 0.0 else np.nan

        findings = []

        findings.append(
            f'A kilogram of first stage dry mass costs {dryRatio:.3f} kg of payload and a kilogram '
            f'of reserve propellant costs {reserveRatio:.3f} kg, on a first stage mass ratio of '
            f'{firstStageMassRatio:.2f}.')

        findings.append(
            f'**The reserve is the more expensive of the two, by a factor of '
            f'{1.0 / measured:.2f}.** Dry mass raises the initial and the burnout mass together '
            f'and the reserve raises the burnout mass alone, so the ratio is 1 - 1/R = '
            f'{closedForm:.4f} and the measured value is {measured:.4f}.')

        findings.append(
            'The ordering does not depend on the vehicle. 1 - 1/R is below one for any stage that '
            'burns any propellant at all, so reserve propellant costs more payload per kilogram '
            'than dry mass on every vehicle, and it costs relatively more the smaller the mass '
            'ratio of the stage carrying it.')

        self.findings = findings

        return {'baselinePayload':      baseline,
                'dryMassExchangeRatio': dryRatio,
                'reserveExchangeRatio': reserveRatio,
                'firstStageMassRatio':  firstStageMassRatio,
                'measuredRatio':        measured,
                'closedFormRatio':      closedForm,
                'reserveCostsMore':     bool(reserveRatio > dryRatio),
                'findings':             findings}

    # -------------------------------------------------------------------------------------------- #

    def _fixedVehicleSensitivity(self, perturbation: float) -> dict:

        '''

        Payload elasticity to dry mass on a vehicle whose propellant load is already fixed.

        The stages are sized once at the optimum, then their dry masses are perturbed with the
        propellant held constant and the payload is solved for. Nothing about the vehicle is
        allowed to grow.

        '''

        sized = self.sizeToDeltaV()

        exhausts = self.exhaustVelocities()

        def payloadFor(dryScale: float) -> float:

            drys        = [entry['dryMass'] * dryScale for entry in sized['stages']]
            propellants = [entry['propellantMass'] for entry in sized['stages']]

            def achieved(payload: float) -> float:

                total = 0.0

                for index in range(len(drys)):

                    above = sum(drys[index + 1:]) + sum(propellants[index + 1:]) + payload

                    initial = drys[index] + propellants[index] + above
                    final   = initial - propellants[index]

                    total += exhausts[index] * np.log(initial / final)

                return total

            low, high = 0.0, sized['payloadMass'] * 10.0

            # delta-V falls as payload rises, so bisect downward
            if achieved(low) < self.targetDeltaV:
                return 0.0

            for _ in range(LAGRANGE_ITERATIONS):

                middle = 0.5 * (low + high)

                if achieved(middle) > self.targetDeltaV:
                    low = middle
                else:
                    high = middle

                if high - low < 1.0e-9 * max(1.0, high):
                    break

            return 0.5 * (low + high)

        baseline = payloadFor(1.0)
        heavier  = payloadFor(1.0 + perturbation)

        if baseline <= 0.0:
            return {'baselinePayload': baseline, 'dryMassElasticity': np.nan}

        return {'baselinePayload':   baseline,
                'perturbedPayload':  heavier,
                'dryMassElasticity': (heavier / baseline - 1.0) / perturbation}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full staging report.
        '''

        if np.isfinite(self.targetDeltaV) and np.isfinite(self.payloadMass):
            result = self.sizeToDeltaV()
            title  = f'sized to {self.targetDeltaV:.0f} m/s'
        else:
            result = self.calculatePerformance()
            title  = f'delivering {result["totalDeltaV"]:.0f} m/s'

        lines = []
        lines.append('=' * 96)
        lines.append(f'  STAGED VEHICLE: {len(self.stages)} stages, {title}')
        lines.append('=' * 96)
        lines.append('')

        rows = [[f'{entry["stage"]}',
                 f'{entry["grossMass"] / 1000.0:.2f}',
                 f'{entry["dryMass"] / 1000.0:.2f}',
                 f'{entry["propellantMass"] / 1000.0:.2f}',
                 f'{entry["massRatio"]:.3f}',
                 f'{entry["deltaV"]:.0f}']
                for entry in result['stages']]

        lines.append(formatReportTable(
            rows, ['Stage', 'Gross [t]', 'Dry [t]', 'Propellant [t]', 'Mass ratio', 'dV [m/s]'],
            title = 'Stages'))

        lines.append('')
        lines.append(formatReportTable(
            [['Liftoff mass',     f'{result["liftoffMass"] / 1000.0:.2f}',   't'],
             ['Payload',          f'{result["payloadMass"] / 1000.0:.3f}',   't'],
             ['Payload fraction', f'{result["payloadFraction"]:.3%}',        ''],
             ['Total delta-V',    f'{result["totalDeltaV"]:.0f}',            'm/s']],
            ['Quantity', 'Value', 'Unit'], title = 'Vehicle'))

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'staged_vehicle.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _payloadForFixedLiftoff(self) -> float:

        '''
        Payload delivered at the optimal split, holding the liftoff mass constant. Sizing is linear
        in the payload for a fixed split, so one sizing run scales to any liftoff mass.
        '''

        reference = 1.0

        original = self.payloadMass
        self.payloadMass = reference

        try:
            sized = self.sizeToDeltaV()
        finally:
            self.payloadMass = original

        # payload per unit liftoff mass, scaled to a fixed liftoff mass of one
        return reference / sized['liftoffMass']

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if len(self.stages) < 1:
            raise StagingError(
                'A vehicle needs at least one stage.',
                context = createErrorContext(component = 'StagedVehicle'))

        for index, stage in enumerate(self.stages):

            for parameter in ('specificImpulse', 'structuralCoefficient'):
                if parameter not in stage:
                    raise StagingError(
                        f'Stage {index + 1} has no {parameter}. Every stage needs a specific '
                        f'impulse and a structural coefficient.',
                        context = createErrorContext(component = 'StagedVehicle'))

            if stage['specificImpulse'] <= 0.0:
                raise InvalidInputError(
                    f'Stage {index + 1} has a specific impulse of {stage["specificImpulse"]}.',
                    context = createErrorContext(component = 'StagedVehicle'))

            if not 0.0 < stage['structuralCoefficient'] < 1.0:
                raise ClosureError(
                    f'Stage {index + 1} has a structural coefficient of '
                    f'{stage["structuralCoefficient"]}, which must lie in (0, 1). At zero the '
                    f'stage has no structure and at one it has no propellant, and neither is a '
                    f'stage. Real values run from about '
                    f'{min(low for low, _ in STRUCTURAL_COEFFICIENT_BAND.values()):.3f} to '
                    f'{max(high for _, high in STRUCTURAL_COEFFICIENT_BAND.values()):.3f}.',
                    context = createErrorContext(component = 'StagedVehicle'))

        if np.isfinite(self.payloadMass) and self.payloadMass <= 0.0:
            raise InvalidInputError(
                f'The payload mass must be positive, got {self.payloadMass}.',
                context = createErrorContext(component = 'StagedVehicle'))

        if np.isfinite(self.targetDeltaV) and self.targetDeltaV <= 0.0:
            raise InvalidInputError(
                f'The target delta-V must be positive, got {self.targetDeltaV}.',
                context = createErrorContext(component = 'StagedVehicle'))
