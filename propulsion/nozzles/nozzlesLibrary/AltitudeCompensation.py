
# -- AltitudeCompensation -- #

'''

What altitude compensation is worth, and why almost none of it has flown.

A fixed nozzle is optimally expanded at exactly one altitude and is losing performance everywhere
else. A first stage spends its burn climbing through two orders of magnitude of ambient pressure,
so the loss is real and it is not small.

This class computes the upper bound, which is the performance a perfectly compensating nozzle would
deliver, and then the fraction of it each real arrangement actually recovers. **The upper bound for
the reference booster is 14.2 seconds, 4.7 per cent.**

That number is the whole subject. It is large enough to be worth chasing and small enough that
every scheme for capturing it has so far lost more in mass, cooling or complexity than it gained,
which is why the aerospike has never flown operationally and the dual bell has never flown at all.

The one arrangement that has flown is the extendible nozzle, and it works precisely because it
solves an easier problem: a single deployment in vacuum on an upper stage, rather than continuous
compensation through the atmosphere.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from nozzleUtils import (ALTITUDE_COMPENSATION, PROPELLANT_COMBINATIONS, GRAVITY,
                             vandenkerckhove, pressureRatioFromAreaRatio,
                             idealCompensatingAreaRatio, convertAltitudeToPressure,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, ContourError)
except ImportError:
    from .nozzleUtils import (ALTITUDE_COMPENSATION, PROPELLANT_COMBINATIONS, GRAVITY,
                              vandenkerckhove, pressureRatioFromAreaRatio,
                              idealCompensatingAreaRatio, convertAltitudeToPressure,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, ContourError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The fraction of the ideal compensation benefit each arrangement actually recovers. These are
# representative figures rather than sourced values and they are registered as unvalidated: what
# they encode is an ordering and a rough magnitude, not a prediction for a specific device.
#
# The aerospike figure is deliberately well below one. A truncated spike does not compensate
# perfectly, the base flow is a real loss, and the cooling problem forces compromises that cost
# more.
RECOVERY_FRACTION = {
    'fixed bell':  0.00,
    'extendible':  0.55,
    'dual bell':   0.45,
    'aerospike':   0.70,
}

# Mass penalty as a fraction of a fixed bell nozzle of the same throat. Also representative, also
# unvalidated, and the reason the trade closes the way it does.
MASS_PENALTY = {
    'fixed bell':  0.00,
    'extendible':  0.25,
    'dual bell':   0.15,
    'aerospike':   0.80,
}

# ------------------------------------------------------------------------------------------------ #
# -- AltitudeCompensation -- #
# ------------------------------------------------------------------------------------------------ #

class AltitudeCompensation:

    '''

    The ideal compensation benefit over an ascent, and what each real arrangement recovers of it.

    '''

    def __init__(self):

        self.combination     = ''
        self.chamberPressure = np.nan
        self.areaRatio       = np.nan
        self.characteristicVelocity = np.nan
        self.altitudes       = None

        self.properties = {}
        self.findings   = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `altitudes` is the ascent profile, sampled at equal intervals of burn time, and it comes
        from the same place the propulsion hub's example takes it.

        '''

        requiredParams = {'combination':     str,
                          'chamberPressure': (int, float),
                          'areaRatio':       (int, float)}

        optionalParams = {'characteristicVelocity': (int, float),
                          'altitudes':              list}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise ContourError(
                f'Unknown propellant combination \'{self.combination}\'.',
                context = createErrorContext(component = 'AltitudeCompensation'))

        self.properties = dict(PROPELLANT_COMBINATIONS[self.combination])

        if not np.isfinite(self.characteristicVelocity):
            self.characteristicVelocity = self.properties['referenceCstar'] * 0.96

        if self.altitudes is None:
            self.altitudes = [0.0, 3000.0, 8000.0, 15000.0, 25000.0, 38000.0, 55000.0]

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def _impulseAt(self, areaRatio: float, ambientPressure: float) -> float:

        '''
        Specific impulse at an area ratio and an ambient pressure.
        '''

        gamma = self.properties['gamma']

        ratio = pressureRatioFromAreaRatio(gamma, areaRatio)

        momentum = (vandenkerckhove(gamma)
                    * np.sqrt(2.0 * gamma / (gamma - 1.0)
                              * (1.0 - ratio ** ((gamma - 1.0) / gamma))))

        pressureTerm = areaRatio * (ratio * self.chamberPressure - ambientPressure) \
            / self.chamberPressure

        return self.characteristicVelocity * (momentum + pressureTerm) / GRAVITY

    # -------------------------------------------------------------------------------------------- #

    def calculateIdealBenefit(self) -> dict:

        '''

        The upper bound: what a nozzle that expanded exactly to ambient at every altitude would
        deliver, against the fixed bell it is being compared with.

        No real device reaches this. It is the size of the prize, and knowing it is what makes the
        rest of the subject tractable: an arrangement that costs more than this in mass cannot pay
        for itself however well it works.

        '''

        findings = []

        gamma = self.properties['gamma']

        fixed  = []
        ideal  = []

        for altitude in self.altitudes:

            ambient = float(convertAltitudeToPressure(altitude))

            fixed.append(self._impulseAt(self.areaRatio, ambient))

            matched = idealCompensatingAreaRatio(gamma, self.chamberPressure, ambient)
            ideal.append(self._impulseAt(matched, ambient))

        fixedAverage = float(np.mean(fixed))
        idealAverage = float(np.mean(ideal))

        benefit = idealAverage - fixedAverage

        findings.append(
            f'A fixed bell at an area ratio of {self.areaRatio:.1f} averages '
            f'{fixedAverage:.1f} s over the ascent. A perfectly compensating nozzle would average '
            f'{idealAverage:.1f} s.')

        findings.append(
            f'The prize is {benefit:.1f} s, {benefit / fixedAverage:.1%}. That is the upper bound '
            f'on altitude compensation and no real device reaches it.')

        findings.append(
            'Knowing the bound is what makes the subject tractable. An arrangement that costs more '
            'than this in mass cannot pay for itself however well it compensates.')

        self.findings = findings

        return {'fixedAverage':  fixedAverage,
                'idealAverage':  idealAverage,
                'benefit':       benefit,
                'benefitFraction': benefit / fixedAverage,
                'fixedProfile':  fixed,
                'idealProfile':  ideal,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def compareArrangements(self) -> dict:

        '''

        What each arrangement recovers of the ideal benefit, and what it costs in nozzle mass.

        The recovery fractions and mass penalties are representative rather than sourced, and they
        are registered as unvalidated. What they encode is an ordering and a rough magnitude.

        '''

        findings = []

        bound = self.calculateIdealBenefit()

        results = {}

        for name, definition in ALTITUDE_COMPENSATION.items():

            recovery = RECOVERY_FRACTION[name]
            gained   = bound['benefit'] * recovery

            results[name] = {'recovery':      recovery,
                             'impulseGain':   gained,
                             'averageImpulse': bound['fixedAverage'] + gained,
                             'massPenalty':   MASS_PENALTY[name],
                             'compensating':  definition['compensating'],
                             'flown':         definition['flownOperationally'],
                             'note':          definition['note']}

        best = max(results, key = lambda name: results[name]['impulseGain'])

        flown = [name for name, entry in results.items() if entry['flown']]

        findings.append(
            f'\'{best}\' recovers the most at {results[best]["impulseGain"]:.1f} s, '
            f'{results[best]["recovery"]:.0%} of the bound, for a '
            f'{results[best]["massPenalty"]:.0%} nozzle mass penalty.')

        findings.append(
            f'Of the four, {len(flown)} have flown operationally: {", ".join(flown)}. The '
            f'best performing one is not among them.')

        findings.append(
            'The extendible nozzle is the one that works, and it works by solving an easier '
            'problem: a single deployment in vacuum on an upper stage rather than continuous '
            'compensation through the atmosphere.')

        findings.append(
            'The recovery fractions and mass penalties here are representative rather than sourced '
            'and are registered as unvalidated. The ordering is the useful part.')

        self.findings = findings

        return {'arrangements': results, 'bound': bound['benefit'], 'best': best,
                'flown': flown, 'findings': findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full compensation report.
        '''

        bound       = self.calculateIdealBenefit()
        arrangements = self.compareArrangements()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ALTITUDE COMPENSATION: {self.combination}, '
                     f'fixed area ratio {self.areaRatio:.1f}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Chamber pressure',      f'{self.chamberPressure / 1.0e6:.2f}',    'MPa'],
             ['Fixed bell average',    f'{bound["fixedAverage"]:.1f}',           's'],
             ['Perfectly compensating', f'{bound["idealAverage"]:.1f}',          's'],
             ['The prize',             f'{bound["benefit"]:.1f}',                's'],
             ['As a fraction',         f'{bound["benefitFraction"]:.1%}',        '']],
            ['Quantity', 'Value', 'Unit'], title = 'The bound'))

        lines.append('')
        lines.append('  What each arrangement recovers:')
        lines.append('')
        lines.append(f'    {"arrangement":16s} {"recovers":>9s} {"gain [s]":>10s} '
                     f'{"mass":>7s}  flown')
        for name, entry in arrangements['arrangements'].items():
            lines.append(f'    {name:16s} {entry["recovery"]:9.0%} '
                         f'{entry["impulseGain"]:10.1f} {entry["massPenalty"]:7.0%}  '
                         f'{entry["flown"]}')

        lines.append('')
        lines.append('  Impulse against altitude, fixed bell and ideal:')
        lines.append('')
        lines.append(f'    {"altitude [km]":>14s} {"fixed [s]":>11s} {"ideal [s]":>11s} '
                     f'{"gap [s]":>9s}')
        for index, altitude in enumerate(self.altitudes):
            lines.append(f'    {altitude / 1000.0:14.0f} {bound["fixedProfile"][index]:11.1f} '
                         f'{bound["idealProfile"][index]:11.1f} '
                         f'{bound["idealProfile"][index] - bound["fixedProfile"][index]:9.1f}')

        lines.append('')
        for finding in (bound['findings'] + arrangements['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'altitude_compensation.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.areaRatio <= 1.0:
            raise InvalidInputError(
                f'The area ratio must exceed one, got {self.areaRatio}.',
                context = createErrorContext(component = 'AltitudeCompensation'))

        if self.chamberPressure <= 0.0:
            raise InvalidInputError(
                f'The chamber pressure must be positive, got {self.chamberPressure}.',
                context = createErrorContext(component = 'AltitudeCompensation'))

        if not self.altitudes:
            raise ContourError(
                'An ascent profile of at least one altitude is needed to average over.',
                context = createErrorContext(component = 'AltitudeCompensation'))

        if any(altitude < 0.0 for altitude in self.altitudes):
            raise InvalidInputError(
                'Altitudes cannot be negative.',
                context = createErrorContext(component = 'AltitudeCompensation'))
