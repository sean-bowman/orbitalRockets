
# -- PublicRisk -- #

'''

The number that decides whether a launch is licensed, and it is a number rather than a judgement.

Casualty expectation is the product of three things summed over every place debris could land:

    Ec = sum over regions of  ( population density * casualty area * probability of impact )

**14 CFR 450.101 sets it at 1e-4 for the public**, which is one expected casualty in ten thousand
launches, and it is a limit rather than a target: a launch above it does not get a licence and there
is no engineering argument that trades it against anything.

Three things about the calculation are worth knowing before it is used.

**Collective and individual risk are separate tests and both apply.** A launch can pass the
collective criterion by spreading a small risk thinly over a large population and still fail the
individual criterion for the one person nearest the trajectory. **The individual limit exists to
stop exactly that trade**, and it is the one that shapes a launch azimuth.

**Ocean is not zero.** An open ocean overflight has a population density near zero and a shipping
lane does not, and a launch that clears its criteria over water clears them because somebody counted
the ships.

**And the casualty area is far larger than the fragment.** A fragment threatens the area it lands in
plus an allowance for a standing person and for skipping, so a half kilogram fragment carries about
half a square metre of casualty area and an intact stage carries ninety.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from rangeSafetyUtils import (LAUNCH_SAFETY_CRITERIA, CASUALTY_AREA, POPULATION_DENSITY,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, RiskError)
except ImportError:
    from .rangeSafetyUtils import (LAUNCH_SAFETY_CRITERIA, CASUALTY_AREA, POPULATION_DENSITY,
                                   applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, RiskError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Square metres per square kilometre, used to turn a population density into people per square metre
# where the casualty area lives.
SQUARE_METRES_PER_SQUARE_KILOMETRE = 1.0e6

# ------------------------------------------------------------------------------------------------ #
# -- PublicRisk -- #
# ------------------------------------------------------------------------------------------------ #

class PublicRisk:

    '''

    Casualty expectation by region, the individual risk to the nearest person, and both against the
    regulatory criteria.

    '''

    def __init__(self):

        self.failureProbability = np.nan
        self.regions            = []
        self.fragments          = {}
        self.nearestPersonProbability = np.nan
        self.personnelType      = ''

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `failureProbability` is the probability the vehicle fails and produces debris at all, which
        scales the whole result linearly and is the single most consequential input.

        `regions` is a list of dictionaries with `name`, `landUse` from POPULATION_DENSITY or an
        explicit `density` in people per square kilometre, and `impactProbability`, the probability
        that debris from a failure lands in that region given a failure.

        `fragments` maps a class from CASUALTY_AREA to a count, which sets the casualty area per
        impact.

        `nearestPersonProbability` is the probability of casualty for the single most exposed
        person, which is the separate individual criterion.

        '''

        requiredParams = {'failureProbability': (int, float),
                          'regions':            list}

        optionalParams = {'fragments':                dict,
                          'nearestPersonProbability': (int, float),
                          'personnelType':            str}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.fragments is None or isinstance(self.fragments, float) or not self.fragments:
            self.fragments = {'medium': 1}

        if not self.personnelType:
            self.personnelType = 'public'

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def casualtyArea(self) -> dict:

        '''

        Total casualty area of the debris catalogue.

        **This is not the footprint of the debris.** It is the area within which a person is
        considered a casualty, which includes the fragment's own footprint, an allowance for a
        standing person, and an allowance for skipping and splashing.

        '''

        entries = []

        for name, count in self.fragments.items():

            entry = CASUALTY_AREA[name]
            area = entry['area'] * float(count)

            entries.append({'class':        name,
                            'count':        float(count),
                            'areaEach':     entry['area'],
                            'areaTotal':    area,
                            'note':         entry['note']})

        total = sum(entry['areaTotal'] for entry in entries)

        for entry in entries:
            entry['share'] = entry['areaTotal'] / total if total > 0.0 else 0.0

        entries.sort(key = lambda entry: entry['areaTotal'], reverse = True)

        return {'fragments':    entries,
                'totalArea':    total,
                'fragmentCount': sum(float(count) for count in self.fragments.values()),
                'dominant':     entries[0]['class'] if entries else None}

    # -------------------------------------------------------------------------------------------- #

    def calculateCollective(self) -> dict:

        '''

        Casualty expectation summed over the regions, against 14 CFR 450.101.

        Raises where a criterion is exceeded, because the regulation is a limit rather than a
        target and reporting a percentage over it invites somebody to accept the percentage.

        '''

        area = self.casualtyArea()

        entries = []

        for region in self.regions:

            density = (float(region['density']) if 'density' in region
                       else POPULATION_DENSITY[region['landUse']])

            perSquareMetre = density / SQUARE_METRES_PER_SQUARE_KILOMETRE

            expected = (self.failureProbability
                        * float(region['impactProbability'])
                        * perSquareMetre
                        * area['totalArea'])

            entries.append({'region':            region['name'],
                            'density':           density,
                            'impactProbability': float(region['impactProbability']),
                            'expectedCasualties': expected})

        total = sum(entry['expectedCasualties'] for entry in entries)

        for entry in entries:
            entry['share'] = entry['expectedCasualties'] / total if total > 0.0 else 0.0

        entries.sort(key = lambda entry: entry['expectedCasualties'], reverse = True)

        criterion = ('neighbouringCollective' if self.personnelType == 'neighbouring'
                     else 'publicCollective')
        limit = LAUNCH_SAFETY_CRITERIA[criterion]['limit']

        result = {'regions':           entries,
                  'expectedCasualties': total,
                  'casualtyArea':      area['totalArea'],
                  'criterion':         criterion,
                  'limit':             limit,
                  'margin':            limit / total if total > 0.0 else np.inf,
                  'dominant':          entries[0]['region'] if entries else None,
                  'dominantShare':     entries[0]['share'] if entries else 0.0}

        if total > limit:
            raise RiskError(
                f'Collective risk is {total:.3e} expected casualties against a limit of '
                f'{limit:.0e} in 14 CFR 450.101. **This is a limit rather than a target** and a '
                f'launch above it does not get a licence. The dominant region is '
                f'{entries[0]["region"]} at {entries[0]["share"] * 100.0:.0f} per cent.',
                context = {'expectedCasualties': total,
                           'limit':              limit,
                           'dominantRegion':     entries[0]['region']})

        return result

    # -------------------------------------------------------------------------------------------- #

    def calculateIndividual(self) -> dict:

        '''

        The probability of casualty for the single most exposed person, against the separate
        individual criterion.

        **Both tests apply and they catch different failures.** The collective criterion can be met
        by spreading a small risk thinly; the individual one cannot, and it is what stops a launch
        concentrating its risk on one household near the pad.

        '''

        if not np.isfinite(self.nearestPersonProbability):
            raise RiskError('An individual probability of casualty is needed. It is a separate '
                            'criterion from the collective one and there is no default for it.')

        criterion = ('neighbouringIndividual' if self.personnelType == 'neighbouring'
                     else 'publicIndividual')
        limit = LAUNCH_SAFETY_CRITERIA[criterion]['limit']

        result = {'probabilityOfCasualty': self.nearestPersonProbability,
                  'criterion':             criterion,
                  'limit':                 limit,
                  'margin':                limit / self.nearestPersonProbability
                                           if self.nearestPersonProbability > 0.0 else np.inf}

        if self.nearestPersonProbability > limit:
            raise RiskError(
                f'Individual risk is {self.nearestPersonProbability:.3e} against a limit of '
                f'{limit:.0e}. **The collective criterion can be met by spreading risk thinly and '
                f'this one cannot**, which is what it exists for.',
                context = {'probabilityOfCasualty': self.nearestPersonProbability,
                           'limit':                 limit})

        return result

    # -------------------------------------------------------------------------------------------- #

    def failureSensitivity(self, probabilities: list = None) -> dict:

        '''

        Collective risk against the vehicle failure probability.

        The relationship is linear, which is worth showing because it means **the risk analysis
        inherits the reliability estimate whole.** A launch that clears its criterion at an assumed
        two per cent failure probability does not clear it at five, and the failure probability is
        the least well established number in the calculation.

        '''

        if probabilities is None:
            probabilities = [0.005, 0.01, 0.02, 0.05, 0.10]

        original = self.failureProbability
        results = []

        try:
            for probability in probabilities:

                self.failureProbability = probability

                try:
                    collective = self.calculateCollective()
                    results.append({'failureProbability': probability,
                                    'expectedCasualties': collective['expectedCasualties'],
                                    'clears':             True})
                except RiskError:
                    # Recompute without the refusal so the sweep can report where it fails.
                    area = self.casualtyArea()['totalArea']
                    total = sum(probability * float(region['impactProbability'])
                                * (float(region['density']) if 'density' in region
                                   else POPULATION_DENSITY[region['landUse']])
                                / SQUARE_METRES_PER_SQUARE_KILOMETRE * area
                                for region in self.regions)
                    results.append({'failureProbability': probability,
                                    'expectedCasualties': total,
                                    'clears':             False})
        finally:
            self.failureProbability = original

        limit = LAUNCH_SAFETY_CRITERIA['publicCollective']['limit']

        clearing = [entry for entry in results if entry['clears']]

        return {'results':      results,
                'limit':        limit,
                'isLinear':     True,
                'highestClearing': clearing[-1]['failureProbability'] if clearing else None,
                'limitingProbability': (limit * results[0]['failureProbability']
                                        / results[0]['expectedCasualties']
                                        if results[0]['expectedCasualties'] > 0.0 else np.inf)}

    # -------------------------------------------------------------------------------------------- #

    def compareLandUse(self, impactProbability: float = 0.01) -> dict:

        '''

        The same debris over every land use class.

        The spread is the point, and it is the whole reason launch sites sit on coasts with an
        ocean downrange: the risk over dense urban land is five orders of magnitude above the risk
        over open ocean, for identical hardware and an identical failure.

        '''

        area = self.casualtyArea()['totalArea']

        results = []

        for landUse, density in POPULATION_DENSITY.items():

            expected = (self.failureProbability * impactProbability
                        * density / SQUARE_METRES_PER_SQUARE_KILOMETRE * area)

            results.append({'landUse':            landUse,
                            'density':            density,
                            'expectedCasualties': expected,
                            'clears':             expected <= LAUNCH_SAFETY_CRITERIA
                                                  ['publicCollective']['limit']})

        results.sort(key = lambda entry: entry['expectedCasualties'])

        nonZero = [entry for entry in results if entry['expectedCasualties'] > 0.0]

        return {'results':  results,
                'spread':   (nonZero[-1]['expectedCasualties'] / nonZero[0]['expectedCasualties']
                             if len(nonZero) > 1 else np.inf),
                'clearing': [entry['landUse'] for entry in results if entry['clears']]}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The casualty area, the collective risk by region, and both criteria.
        '''

        area = self.casualtyArea()

        lines = []

        lines.append(formatReportTable(
            [[entry['class'],
              f'{entry["count"]:.0f}',
              f'{entry["areaEach"]:.1f}',
              f'{entry["areaTotal"]:,.0f}',
              f'{entry["share"] * 100.0:.0f}%'] for entry in area['fragments']],
            ['class', 'count', 'area each [m2]', 'total [m2]', 'share'],
            title = 'CASUALTY AREA'))

        lines.append('')

        try:
            collective = self.calculateCollective()

            lines.append(formatReportTable(
                [[entry['region'],
                  f'{entry["density"]:,.0f}',
                  f'{entry["impactProbability"]:.4f}',
                  f'{entry["expectedCasualties"]:.3e}',
                  f'{entry["share"] * 100.0:.0f}%'] for entry in collective['regions']],
                ['region', 'density [/km2]', 'P(impact)', 'Ec', 'share'],
                title = 'COLLECTIVE RISK'))

            lines.append('')
            lines.append(f'Ec {collective["expectedCasualties"]:.3e} against a limit of '
                         f'{collective["limit"]:.0e}, a margin of {collective["margin"]:.1f}.')

        except RiskError as error:
            lines.append('COLLECTIVE RISK EXCEEDED')
            lines.append(str(error))

        if np.isfinite(self.nearestPersonProbability):

            lines.append('')

            try:
                individual = self.calculateIndividual()
                lines.append(f'Individual Pc {individual["probabilityOfCasualty"]:.3e} against '
                             f'{individual["limit"]:.0e}, a margin of {individual["margin"]:.1f}.')
            except RiskError as error:
                lines.append('INDIVIDUAL RISK EXCEEDED')
                lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'publicRisk.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not 0.0 <= self.failureProbability <= 1.0:
            raise InvalidInputError('Failure probability must be a probability.')

        if not self.regions:
            raise InvalidInputError('At least one region is needed.')

        if self.personnelType not in ('public', 'neighbouring'):
            raise InvalidInputError("Personnel type must be 'public' or 'neighbouring'. The "
                                    'regulation sets different criteria for each.')

        for region in self.regions:

            if 'density' not in region and 'landUse' not in region:
                raise InvalidInputError(
                    f"Region {region.get('name', 'unnamed')} needs a density or a land use class.")

            if 'landUse' in region and region['landUse'] not in POPULATION_DENSITY:
                raise InvalidInputError(
                    f"{region['landUse']} is not a land use class. Available: "
                    f'{sorted(POPULATION_DENSITY)}.')

            if not 0.0 <= float(region['impactProbability']) <= 1.0:
                raise InvalidInputError(
                    f"Region {region['name']} has an impact probability that is not a probability.")

        for name in self.fragments:
            if name not in CASUALTY_AREA:
                raise InvalidInputError(
                    f'{name} is not a fragment class. Available: {sorted(CASUALTY_AREA)}.')

        if np.isfinite(self.nearestPersonProbability):
            if not 0.0 <= self.nearestPersonProbability <= 1.0:
                raise InvalidInputError('Individual probability of casualty must be a probability.')
