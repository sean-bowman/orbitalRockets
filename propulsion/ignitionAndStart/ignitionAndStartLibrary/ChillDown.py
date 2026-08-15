
# -- ChillDown -- #

'''

Conditioning cryogenic hardware before a start, and why the answer is a band rather than a number.

Liquid oxygen poured into warm metal boils. It goes on boiling until the metal has given up its
stored enthalpy, and until it stops the engine is being fed a two-phase mixture that no pump will
tolerate and no injector was designed around. The propellant spent doing this is vented and lost.

The mass required is an enthalpy balance and it has two bounds that are far apart.

**The upper bound** assumes the vapour leaves at its saturation temperature, so every kilogram
absorbs only its latent heat. That is what happens when the flow is fast and the vapour is swept
out before it can warm.

**The lower bound** assumes the vapour leaves at the metal's starting temperature, so every
kilogram absorbs its latent heat plus the full sensible heating of the gas. That is what happens
when the flow is slow enough for the vapour to stay in contact.

For oxygen those two bounds differ by about a factor of two. **For hydrogen they differ by about a
factor of nine**, because hydrogen's vapour specific heat is enormous and its latent heat is not.
That single fact is why the liquid hydrogen chill-down literature is entirely about trickle versus
pulse flow scheduling and the liquid oxygen literature is not: with hydrogen, the method decides
the answer almost completely.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from ignitionUtils import (CRYOGENS, MEAN_SPECIFIC_HEAT, chillDownEnthalpy, fluidProps,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, ConditioningError)
except ImportError:
    from .ignitionUtils import (CRYOGENS, MEAN_SPECIFIC_HEAT, chillDownEnthalpy, fluidProps,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, ConditioningError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Ambient metal temperature before conditioning.
AMBIENT_TEMPERATURE = 293.15    # [K]

# Pressure at which the vapour sensible heating is evaluated. Chill-down vents overboard, so the
# vapour path is at or near atmospheric.
VENT_PRESSURE = 101325.0    # [Pa]

# A small margin above the boiling point that counts as conditioned. Reaching the boiling point
# exactly takes infinite time, so a target is stated.
CONDITIONED_MARGIN = 5.0    # [K]

# ------------------------------------------------------------------------------------------------ #
# -- ChillDown -- #
# ------------------------------------------------------------------------------------------------ #

class ChillDown:

    '''

    Cryogen mass needed to condition a mass of metal, bounded above and below.

    '''

    def __init__(self):

        self.cryogen  = ''
        self.material = ''
        self.metalMass = np.nan
        self.startTemperature = np.nan
        self.targetTemperature = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `metalMass` is the hardware being conditioned: the lines, the pump, the valves and the
        injector, everything the cryogen wets before the engine starts.

        '''

        requiredParams = {'cryogen':   str,
                          'material':  str,
                          'metalMass': (int, float)}

        optionalParams = {'startTemperature':  (int, float),
                          'targetTemperature': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.cryogen not in CRYOGENS:
            raise ConditioningError(
                f'\'{self.cryogen}\' is not a cryogen this class knows. A propellant with no '
                f'liquid to vapour transition in the temperature range has no chill-down to '
                f'compute. Known cryogens are {sorted(CRYOGENS)}.',
                context = createErrorContext(component = 'ChillDown'))

        if self.material not in MEAN_SPECIFIC_HEAT:
            raise InvalidInputError(
                f'No cryogenic specific heat for \'{self.material}\'. Known materials are '
                f'{sorted(MEAN_SPECIFIC_HEAT)}. Most are integrated from the NIST cryogenic curves '
                f'over the range actually traversed, and none is the room-temperature value in '
                f'common/materials.py.',
                context = createErrorContext(component = 'ChillDown'))

        if not np.isfinite(self.startTemperature):
            self.startTemperature = AMBIENT_TEMPERATURE

        if not np.isfinite(self.targetTemperature):
            self.targetTemperature = CRYOGENS[self.cryogen]['boilingPoint'] + CONDITIONED_MARGIN

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def metalEnthalpy(self) -> float:

        '''

        Enthalpy the hardware has to give up, in joules.

        Integrated over the range this chill-down actually traverses rather than taken as a
        constant times a span. The two differ because specific heat falls steeply below about
        100 K, so the mean depends on where the range ends: the same stainless line averages
        400 J/(kg K) chilling to liquid oxygen and 331 chilling to liquid hydrogen.

        '''

        return chillDownEnthalpy(self.material, self.metalMass,
                                 self.targetTemperature, self.startTemperature)

    def effectiveSpecificHeat(self) -> float:

        '''
        The enthalpy-averaged specific heat this chill-down actually sees, in J/(kg K). Reported so
        that a reader can see how far it sits from the table value quoted over the reference range.
        '''

        span = self.startTemperature - self.targetTemperature

        return self.metalEnthalpy() / (self.metalMass * span)

    def cryogenCapacity(self) -> dict:

        '''

        What one kilogram of cryogen can absorb, at each of the two bounds.

        Both come from the equation of state through the shared property wrapper, so nothing here
        is a tabulated latent heat that could go stale.

        '''

        species = CRYOGENS[self.cryogen]['species']
        boiling = CRYOGENS[self.cryogen]['boilingPoint']

        liquidEnthalpy = float(fluidProps(species, 'TQ', 'H', boiling, 0.0))
        vapourEnthalpy = float(fluidProps(species, 'TQ', 'H', boiling, 1.0))

        latentHeat = vapourEnthalpy - liquidEnthalpy

        warmedEnthalpy = float(fluidProps(species, 'TP', 'H', self.startTemperature,
                                          VENT_PRESSURE))

        sensibleHeat = warmedEnthalpy - vapourEnthalpy

        return {'latentHeat':   latentHeat,
                'sensibleHeat': sensibleHeat,
                'total':        latentHeat + sensibleHeat,
                'sensibleFraction': sensibleHeat / (latentHeat + sensibleHeat)}

    # -------------------------------------------------------------------------------------------- #

    def calculateMass(self) -> dict:

        '''

        The cryogen mass, bounded above by latent heat alone and below by full sensible recovery.

        The width of that band is the result. It is not an uncertainty in the calculation; it is
        the range that the chill-down method actually spans, and choosing where in it to sit is the
        design decision.

        '''

        findings = []

        enthalpy = self.metalEnthalpy()
        capacity = self.cryogenCapacity()

        upperBound = enthalpy / capacity['latentHeat']
        lowerBound = enthalpy / capacity['total']

        band = upperBound / lowerBound

        findings.append(
            f'{self.metalMass:.0f} kg of {self.material} cooling from '
            f'{self.startTemperature:.0f} K to {self.targetTemperature:.0f} K gives up '
            f'{enthalpy / 1.0e6:.2f} MJ.')

        findings.append(
            f'{self.cryogen} absorbs {capacity["latentHeat"] / 1.0e3:.0f} kJ/kg as latent heat and '
            f'a further {capacity["sensibleHeat"] / 1.0e3:.0f} kJ/kg if the vapour warms all the '
            f'way back to {self.startTemperature:.0f} K.')

        findings.append(
            f'So the mass is between {lowerBound:.1f} kg and {upperBound:.1f} kg, a band of '
            f'{band:.1f} to one.')

        if band > 4.0:
            findings.append(
                f'That band is wide enough that the chill-down **method** decides the answer, not '
                f'the hardware. {capacity["sensibleFraction"]:.0%} of the available capacity is in '
                f'the vapour rather than the phase change, and capturing it means slow flow and a '
                f'long chill. This is why the {self.cryogen} literature is about trickle and pulse '
                f'scheduling.')
        else:
            findings.append(
                f'That band is narrow enough that the hardware mass decides the answer and the '
                f'method only trims it. Only {capacity["sensibleFraction"]:.0%} of the available '
                f'capacity is in the vapour.')

        self.findings = findings

        return {'metalEnthalpy': enthalpy,
                'latentHeat':    capacity['latentHeat'],
                'sensibleHeat':  capacity['sensibleHeat'],
                'sensibleFraction': capacity['sensibleFraction'],
                'upperBound':    upperBound,
                'lowerBound':    lowerBound,
                'band':          band,
                'methodDominated': bool(band > 4.0),
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def compareCryogens(self, cryogens: list = None) -> dict:

        '''

        The same hardware conditioned by each cryogen, which is where the hydrogen result stands
        out rather than being asserted.

        '''

        if cryogens is None:
            cryogens = ['LOX', 'LCH4', 'LH2']

        original = self.cryogen

        results = {}

        try:
            for name in cryogens:

                if name not in CRYOGENS:
                    raise ConditioningError(
                        f'\'{name}\' is not a known cryogen. Known cryogens are '
                        f'{sorted(CRYOGENS)}.',
                        context = createErrorContext(component = 'ChillDown'))

                self.cryogen = name
                self.targetTemperature = CRYOGENS[name]['boilingPoint'] + CONDITIONED_MARGIN

                results[name] = self.calculateMass()

        finally:
            self.cryogen = original
            self.targetTemperature = CRYOGENS[original]['boilingPoint'] + CONDITIONED_MARGIN

        widest = max(results, key = lambda name: results[name]['band'])

        return {'results': results,
                'widestBand': widest,
                'bandRatio': {name: entry['band'] for name, entry in results.items()}}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full chill-down report.
        '''

        result = self.calculateMass()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  CHILL DOWN: {self.metalMass:.0f} kg of {self.material} with '
                     f'{self.cryogen}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Metal enthalpy',     f'{result["metalEnthalpy"] / 1.0e6:.2f}',       'MJ'],
             ['Latent heat',        f'{result["latentHeat"] / 1.0e3:.0f}',          'kJ/kg'],
             ['Vapour sensible',    f'{result["sensibleHeat"] / 1.0e3:.0f}',        'kJ/kg'],
             ['Mass, upper bound',  f'{result["upperBound"]:.1f}',                  'kg'],
             ['Mass, lower bound',  f'{result["lowerBound"]:.1f}',                  'kg'],
             ['Band',               f'{result["band"]:.1f}',                        'to one']],
            ['Quantity', 'Value', 'Unit'], title = 'Conditioning'))

        lines.append('')
        for finding in result['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'chill_down.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.metalMass <= 0.0:
            raise InvalidInputError(
                f'The metal mass must be positive, got {self.metalMass}.',
                context = createErrorContext(component = 'ChillDown'))

        if self.targetTemperature >= self.startTemperature:
            raise ConditioningError(
                f'The target temperature {self.targetTemperature:.1f} K is at or above the start '
                f'temperature {self.startTemperature:.1f} K, so there is nothing to chill. A '
                f'chill-down that does not have to remove heat is not a chill-down.',
                context = createErrorContext(component = 'ChillDown'))

        if self.targetTemperature < CRYOGENS[self.cryogen]['boilingPoint']:
            raise ConditioningError(
                f'The target temperature {self.targetTemperature:.1f} K is below the boiling point '
                f'of {self.cryogen}, {CRYOGENS[self.cryogen]["boilingPoint"]:.1f} K. Boiling '
                f'liquid cannot cool metal below its own saturation temperature at the vent '
                f'pressure, so this target is unreachable by this cryogen.',
                context = createErrorContext(component = 'ChillDown'))
