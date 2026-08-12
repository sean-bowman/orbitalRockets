
# -- HazardSiting -- #

'''

How far away everything has to be, and why a small hydrogen stage is not a small problem.

A launch pad is sited by converting the propellant load into an equivalent weight of TNT and then
applying cube-root scaling to get a separation distance for each thing that needs protecting. Both
halves come from DESR 6055.09, reproduced as NASA-STD-8719.12A, and both were read in full.

The equivalence table is mostly flat percentages. **Hydrogen is the exception and it is the
interesting one.** Its equivalent weight is the larger of a sublinear term and a flat fraction:

    W_TNT = max( 8 * W ** (2/3),  0.14 * W )        W in pounds

The two are equal at 186,589 lb of LO2/LH2. Below that the sublinear term governs and the effective
fraction is HIGHER than fourteen per cent, rising without limit as the load falls. **A small
hydrogen stage is disproportionately hazardous per kilogram**, which is the reverse of the intuition
that a small vehicle is a small siting problem, and it is why a modest upper stage can drive a pad
layout that its propellant mass would not suggest.

The separation distance itself is Hopkinson-Cranz cube-root scaling, d = K W**(1/3) in feet and
pounds, with K chosen from the consequence being designed against. Inhabited building distance is
K = 40, which is 1.2 psi.

**Cube-root scaling is forgiving in the wrong direction.** Eight times the propellant is twice the
distance, so a distance that is short is short by a lot of propellant, and a facility that fails its
siting cannot be fixed by trimming the load.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from groundUtils import (K_FACTORS, TNT_EQUIVALENCE, HYDROGEN_FLAT_FRACTION,
                             HYDROGEN_SUBLINEAR_COEFFICIENT, KG_PER_LBM,
                             explosiveEquivalent, hopkinsonCranzDistance,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, SitingError)
except ImportError:
    from .groundUtils import (K_FACTORS, TNT_EQUIVALENCE, HYDROGEN_FLAT_FRACTION,
                              HYDROGEN_SUBLINEAR_COEFFICIENT, KG_PER_LBM,
                              explosiveEquivalent, hopkinsonCranzDistance,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, SitingError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The criterion applied when a facility does not name one. Inhabited building distance is the
# strictest of the routine set and the right default for anything with people in it that is not
# part of the operation.
DEFAULT_CRITERION = 'inhabitedBuilding'

# ------------------------------------------------------------------------------------------------ #
# -- HazardSiting -- #
# ------------------------------------------------------------------------------------------------ #

class HazardSiting:

    '''

    Explosive equivalent of a propellant load, the separation distances it demands, and whether a
    proposed pad layout meets them.

    '''

    def __init__(self):

        self.combination    = ''
        self.propellantMass = np.nan
        self.setting        = ''
        self.facilities     = []
        self.additionalLoads = {}

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `combination` is a key of TNT_EQUIVALENCE and `propellantMass` is the total oxidiser plus
        fuel present, in kilograms. The standard is explicit that this is the whole quantity subject
        to mixing in a credible accident, not the amount that would burn.

        `setting` selects the range launch or static test stand column. They differ, because a
        stand can be built to keep the propellants apart in a way a vehicle cannot.

        `additionalLoads` maps further combinations to their masses, for a vehicle carrying more
        than one. The standard's combined row is a sum of the individual rules rather than a rule
        of its own, which is what this reproduces.

        `facilities` is a list of dictionaries with `name`, `distance` in metres, and optionally
        `criterion`, a key of K_FACTORS.

        '''

        requiredParams = {'combination':    str,
                          'propellantMass': (int, float)}

        optionalParams = {'setting':         str,
                          'facilities':      list,
                          'additionalLoads': dict}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.setting:
            self.setting = 'rangeLaunch'

        if self.facilities is None or isinstance(self.facilities, float):
            self.facilities = []

        if self.additionalLoads is None or isinstance(self.additionalLoads, float):
            self.additionalLoads = {}

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateEquivalent(self) -> dict:

        '''

        TNT equivalent weight of the load, and which of the standard's rules produced it.

        Where more than one combination is present the equivalents add, because the standard's
        combined entry is a sum of the individual rules. That matters for a hydrogen upper stage on
        a kerosene first stage: the hydrogen contributes a larger fraction of its own mass than the
        kerosene does, even though it is the smaller load.

        '''

        result = explosiveEquivalent(self.combination, self.propellantMass, self.setting)

        contributions = [dict(result)]
        total = result['equivalentMass']
        totalPropellant = self.propellantMass

        for combination, mass in self.additionalLoads.items():

            extra = explosiveEquivalent(combination, float(mass), self.setting)

            contributions.append(extra)
            total += extra['equivalentMass']
            totalPropellant += float(mass)

        result['contributions']  = contributions
        result['equivalentMass'] = total
        result['propellantMass'] = totalPropellant
        result['effectiveFraction'] = total / totalPropellant
        result['equivalentPounds'] = total / KG_PER_LBM

        if self.additionalLoads:
            result['governing'] = 'sum over ' + ', '.join(entry['combination']
                                                          for entry in contributions)

        return result

    # -------------------------------------------------------------------------------------------- #

    def calculateDistances(self, criteria: list = None) -> dict:

        '''

        Separation distance for each K factor, with the overpressure each one represents.

        Sorted by distance so the table reads as a set of concentric rings, which is how a pad
        layout is actually drawn.

        '''

        equivalent = self.calculateEquivalent()

        if criteria is None:
            criteria = list(K_FACTORS)

        rings = []

        for name in criteria:

            if name not in K_FACTORS:
                raise SitingError(f'{name} is not a K factor in the standard table. Available: '
                                  f'{sorted(K_FACTORS)}.')

            entry = K_FACTORS[name]

            rings.append({'criterion':    name,
                          'kFactor':      entry['k'],
                          'overpressure': entry['overpressure'],
                          'means':        entry['means'],
                          'distance':     hopkinsonCranzDistance(entry['k'],
                                                                 equivalent['equivalentMass'])})

        rings.sort(key = lambda ring: ring['distance'])

        return {'equivalent': equivalent,
                'rings':      rings}

    # -------------------------------------------------------------------------------------------- #

    def checkFacilities(self) -> dict:

        '''

        Every facility against the distance its criterion demands.

        Raises rather than reporting a negative margin. A control room inside inhabited building
        distance is not a design with a small shortfall in it, and reporting it as a percentage
        invites somebody to accept the percentage.

        '''

        if not self.facilities:
            raise SitingError('No facilities were supplied, so there is nothing to check. Pass a '
                              'list of dictionaries with name and distance.')

        equivalent = self.calculateEquivalent()

        results = []
        violations = []

        for facility in self.facilities:

            criterion = facility.get('criterion', DEFAULT_CRITERION)

            if criterion not in K_FACTORS:
                raise SitingError(f"Facility '{facility.get('name', 'unnamed')}' asks for "
                                  f'criterion {criterion}, which is not in the standard table.')

            required = hopkinsonCranzDistance(K_FACTORS[criterion]['k'],
                                              equivalent['equivalentMass'])

            actual = float(facility['distance'])

            entry = {'name':      facility.get('name', 'unnamed'),
                     'criterion': criterion,
                     'required':  required,
                     'actual':    actual,
                     'margin':    actual - required,
                     'ratio':     actual / required}

            results.append(entry)

            if actual < required:
                violations.append(entry)

        if violations:

            lines = [f"{entry['name']}: {entry['actual']:.0f} m against "
                     f"{entry['required']:.0f} m required for {entry['criterion']}"
                     for entry in violations]

            raise SitingError(
                f'{len(violations)} of {len(results)} facilities sit inside the separation '
                f'distance the {equivalent["equivalentMass"]:.0f} kg TNT equivalent requires. '
                + '; '.join(lines) + '.',
                context = {'combination':      self.combination,
                                      'propellantMass':   self.propellantMass,
                                      'equivalentMass':   equivalent['equivalentMass'],
                                      'governing':        equivalent['governing']})

        # The binding facility is the one with the least ratio, and it is the one that moves if the
        # propellant load grows.
        binding = min(results, key = lambda entry: entry['ratio'])

        return {'facilities': results,
                'binding':    binding,
                'equivalent': equivalent}

    # -------------------------------------------------------------------------------------------- #

    def hydrogenCrossover(self) -> dict:

        '''

        The load at which the two hydrogen rules change places, and what the effective fraction is
        on either side of it.

        The crossover is where 8 W**(2/3) equals 0.14 W, so W = (8 / 0.14) ** 3 in pounds. Below it
        the sublinear rule governs, which is the case for most vehicles smaller than a heavy lift
        core stage.

        '''

        crossoverPounds = (HYDROGEN_SUBLINEAR_COEFFICIENT / HYDROGEN_FLAT_FRACTION) ** 3
        crossover = crossoverPounds * KG_PER_LBM

        samples = []

        for mass in (0.05, 0.2, 0.5, 1.0, 2.0, 5.0):

            sampleMass = crossover * mass
            result = explosiveEquivalent('LO2/LH2', sampleMass, self.setting)

            samples.append({'propellantMass':    sampleMass,
                            'fractionOfCrossover': mass,
                            'effectiveFraction': result['effectiveFraction'],
                            'governing':         result['governing']})

        return {'crossoverMass':   crossover,
                'crossoverPounds': crossoverPounds,
                'samples':         samples}

    # -------------------------------------------------------------------------------------------- #

    def compareCombinations(self) -> dict:

        '''

        Every combination in the standard table at this propellant mass, ranked by the separation
        distance it demands.

        The ranking is not the ranking of the percentages, because cube-root scaling compresses
        them: a factor of five in equivalent weight is a factor of 1.7 in distance.

        '''

        results = []

        for combination in TNT_EQUIVALENCE:

            equivalent = explosiveEquivalent(combination, self.propellantMass, self.setting)

            results.append({'combination':       combination,
                            'effectiveFraction': equivalent['effectiveFraction'],
                            'equivalentMass':    equivalent['equivalentMass'],
                            'inhabitedBuilding': hopkinsonCranzDistance(
                                K_FACTORS['inhabitedBuilding']['k'], equivalent['equivalentMass'])})

        results.sort(key = lambda entry: entry['equivalentMass'], reverse = True)

        spread = (results[0]['equivalentMass'] / results[-1]['equivalentMass'])
        distanceSpread = (results[0]['inhabitedBuilding'] / results[-1]['inhabitedBuilding'])

        return {'results':        results,
                'massSpread':     spread,
                'distanceSpread': distanceSpread}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        The equivalent weight, the rings it produces, and the facility check.

        '''

        distances = self.calculateDistances()
        equivalent = distances['equivalent']

        lines = []

        lines.append(formatReportTable(
            [[self.combination,
              f'{self.propellantMass:,.0f}',
              f'{equivalent["equivalentMass"]:,.0f}',
              f'{equivalent["effectiveFraction"] * 100.0:.1f}%',
              equivalent['governing']]],
            ['combination', 'propellant [kg]', 'TNT equiv [kg]', 'fraction', 'governing rule'],
            title = 'EXPLOSIVE EQUIVALENT'))

        lines.append('')

        lines.append(formatReportTable(
            [[ring['criterion'],
              f'{ring["kFactor"]:.2f}',
              f'{ring["overpressure"]:.1f}',
              f'{ring["distance"]:,.0f}'] for ring in distances['rings']],
            ['criterion', 'K', 'psi', 'distance [m]'],
            title = 'SEPARATION DISTANCES'))

        if self.facilities:

            lines.append('')

            try:
                check = self.checkFacilities()
                rows = [[entry['name'],
                         entry['criterion'],
                         f'{entry["required"]:,.0f}',
                         f'{entry["actual"]:,.0f}',
                         f'{entry["ratio"]:.2f}'] for entry in check['facilities']]
                lines.append(formatReportTable(
                    rows, ['facility', 'criterion', 'required [m]', 'actual [m]', 'ratio'],
                    title = 'FACILITY CHECK'))
                lines.append('')
                lines.append(f'Binding facility: {check["binding"]["name"]} at '
                             f'{check["binding"]["ratio"]:.2f} times its required distance.')

            except SitingError as error:
                lines.append('FACILITY CHECK FAILED')
                lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'hazardSiting.txt'), 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if self.combination not in TNT_EQUIVALENCE:
            raise InvalidInputError(
                f'{self.combination} is not in the standard equivalence table. The standard sends '
                f'anything not listed to individual assessment rather than to a default. '
                f'Available: {sorted(TNT_EQUIVALENCE)}.')

        if not np.isfinite(self.propellantMass) or self.propellantMass <= 0.0:
            raise InvalidInputError('Propellant mass must be a positive number of kilograms.',
                                    context = {'propellantMass': self.propellantMass})

        if self.setting not in ('rangeLaunch', 'staticTest'):
            raise InvalidInputError("Setting must be 'rangeLaunch' or 'staticTest'.")

        for combination, mass in self.additionalLoads.items():

            if combination not in TNT_EQUIVALENCE:
                raise InvalidInputError(
                    f'{combination} is not in the standard equivalence table.')

            if float(mass) <= 0.0:
                raise InvalidInputError(f'{combination} has a non-positive mass.')

        for facility in self.facilities:

            if 'distance' not in facility:
                raise InvalidInputError(
                    f"Facility {facility.get('name', 'unnamed')} has no distance. Every facility "
                    f'needs one, because a siting check without a distance is a table of rings.')

            if float(facility['distance']) <= 0.0:
                raise InvalidInputError(
                    f"Facility {facility.get('name', 'unnamed')} has a non-positive distance.")
