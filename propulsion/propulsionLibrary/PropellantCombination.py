
# -- PropellantCombination -- #

'''

Bipropellant property access, bulk density, density impulse and the combination trade.

The reason this class exists rather than a bare dictionary lookup is density impulse. Specific
impulse is the number everyone quotes and it ranks the combinations in one order. Density impulse,
which is what actually sizes tanks, ranks them in nearly the opposite order, and the disagreement
is not marginal: LOX/LH2 leads on specific impulse by 31 per cent over LOX/RP-1 and trails it on
density impulse by a factor of 2.3.

Which of the two governs depends on the stage. A first stage carries its tanks through the
atmosphere and pays for their volume in drag, structure and gravity losses, so it is a density
impulse problem. An upper stage in vacuum is closer to a pure specific impulse problem. Getting
this the wrong way round is the single most common error in a first pass vehicle trade, and it is
why the class reports both and refuses to name a winner.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from propulsionUtils import (PROPELLANT_COMBINATIONS, GRAVITY, bulkDensity,
                                 characteristicVelocity, vandenkerckhove,
                                 pressureRatioFromAreaRatio,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, PropellantError)
except ImportError:
    from .propulsionUtils import (PROPELLANT_COMBINATIONS, GRAVITY, bulkDensity,
                                  characteristicVelocity, vandenkerckhove,
                                  pressureRatioFromAreaRatio,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, PropellantError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The area ratio the density impulse comparison is taken at. Any comparison of combinations has to
# fix the expansion, because otherwise a combination can be made to look better by expanding it
# further, which is a nozzle decision rather than a propellant one.
COMPARISON_AREA_RATIO = 40.0    # [-]

# Peak specific impulse sits fuel rich of stoichiometric. Below roughly this fraction of the
# stoichiometric ratio the mixture is rich enough that unburnt fuel is being carried as dead weight
# rather than as a molecular weight reduction, and the tabulated performance no longer applies.
MINIMUM_STOICHIOMETRIC_FRACTION = 0.40    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- PropellantCombination -- #
# ------------------------------------------------------------------------------------------------ #

class PropellantCombination:

    '''

    Property access and the density against specific impulse trade for a bipropellant combination.

    '''

    def __init__(self):

        self.combination   = ''
        self.mixtureRatio  = np.nan
        self.areaRatio     = np.nan

        self.properties = {}
        self.findings   = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `combination` names an entry in PROPELLANT_COMBINATIONS.

        `mixtureRatio` defaults to the tabulated operating point. Supplying a different one is
        allowed and is flagged, because the tabulated chamber temperature and molar mass were taken
        at the tabulated ratio and do not travel with it.

        '''

        requiredParams = {'combination': str}

        optionalParams = {'mixtureRatio': (int, float),
                          'areaRatio':    (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise PropellantError(
                f'Unknown propellant combination \'{self.combination}\'. '
                f'Known: {sorted(PROPELLANT_COMBINATIONS)}.',
                context = createErrorContext(component = 'PropellantCombination'))

        self.properties = dict(PROPELLANT_COMBINATIONS[self.combination])

        if not np.isfinite(self.mixtureRatio):
            self.mixtureRatio = self.properties['mixtureRatio']

        if not np.isfinite(self.areaRatio):
            self.areaRatio = COMPARISON_AREA_RATIO

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateBulkDensity(self) -> dict:

        '''

        Bulk density and the volume split between the two tanks.

        The volume split is the number that decides the vehicle layout, and it is not the mixture
        ratio. LOX/LH2 at a mass mixture ratio of 5.5 puts 75 per cent of the propellant volume in
        the fuel tank, because hydrogen is sixteen times less dense than oxygen. A layout drawn from
        the mass ratio alone has the tanks the wrong way round.

        '''

        self.findings = []

        oxidiserDensity = self.properties['oxidiserDensity']
        fuelDensity     = self.properties['fuelDensity']

        density = bulkDensity(self.mixtureRatio, oxidiserDensity, fuelDensity)

        # per unit total mass: oxidiser mass fraction MR/(1+MR), fuel 1/(1+MR)
        oxidiserVolume = (self.mixtureRatio / (1.0 + self.mixtureRatio)) / oxidiserDensity
        fuelVolume     = (1.0 / (1.0 + self.mixtureRatio)) / fuelDensity
        totalVolume    = oxidiserVolume + fuelVolume

        fuelVolumeFraction = fuelVolume / totalVolume

        self.findings.append(
            f'Bulk density {density:.1f} kg/m^3 at a mixture ratio of {self.mixtureRatio:.2f}, '
            f'from {oxidiserDensity:.0f} kg/m^3 oxidiser and {fuelDensity:.0f} kg/m^3 fuel.')

        self.findings.append(
            f'The fuel takes {fuelVolumeFraction * 100.0:.0f} per cent of the propellant volume '
            f'while carrying {100.0 / (1.0 + self.mixtureRatio):.0f} per cent of the mass. Tank '
            f'sizing follows the volume, not the mixture ratio.')

        if fuelVolumeFraction > 0.6:
            self.findings.append(
                'The fuel tank is the larger of the two by volume despite carrying the smaller '
                'mass. That inverts the usual layout and it drives the vehicle length.')

        return {'bulkDensity':        density,
                'oxidiserDensity':    oxidiserDensity,
                'fuelDensity':        fuelDensity,
                'fuelVolumeFraction': fuelVolumeFraction,
                'fuelMassFraction':   1.0 / (1.0 + self.mixtureRatio),
                'findings':           self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateIdealPerformance(self) -> dict:

        '''

        Vacuum specific impulse at the comparison area ratio, and the two characteristic velocities.

        The gap between the tabulated characteristic velocity and the ideal one computed from the
        chamber temperature, molar mass and gamma is reported rather than hidden. It is the frozen
        against equilibrium difference, it runs from about four per cent low to two per cent high
        across this table, and a reader who does not know it is there will eventually wonder why
        two correct calculations disagree.

        '''

        self.findings = []

        gamma     = self.properties['gamma']
        reference = self.properties['referenceCstar']

        ideal = characteristicVelocity(gamma, self.properties['molarMass'],
                                       self.properties['chamberTemperature'])

        pressureRatio = pressureRatioFromAreaRatio(gamma, self.areaRatio)

        # vacuum thrust coefficient: momentum term plus the full pressure term
        momentum = (vandenkerckhove(gamma)
                    * np.sqrt(2.0 * gamma / (gamma - 1.0)
                              * (1.0 - pressureRatio ** ((gamma - 1.0) / gamma))))

        thrustCoefficient = momentum + pressureRatio * self.areaRatio

        specificImpulse = reference * thrustCoefficient / GRAVITY

        gap = (ideal - reference) / reference

        self.findings.append(
            f'Vacuum specific impulse {specificImpulse:.1f} s at an area ratio of '
            f'{self.areaRatio:.0f}, from a characteristic velocity of {reference:.0f} m/s and a '
            f'thrust coefficient of {thrustCoefficient:.4f}.')

        self.findings.append(
            f'The ideal one-dimensional characteristic velocity from the tabulated chamber '
            f'temperature, molar mass and gamma is {ideal:.0f} m/s, {gap * 100.0:+.1f} per cent '
            f'against the tabulated {reference:.0f} m/s. That is the frozen against equilibrium '
            f'difference and not a table error. CEA at the actual chamber pressure replaces both.')

        return {'specificImpulse':       specificImpulse,
                'thrustCoefficient':     thrustCoefficient,
                'characteristicVelocity': reference,
                'idealCharacteristicVelocity': ideal,
                'characteristicVelocityGap':   gap,
                'exitPressureRatio':     pressureRatio,
                'findings':              self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateDensityImpulse(self) -> dict:

        '''

        Density impulse, `rho_bulk Isp`, in kg s / m^3.

        This is the parameter that sizes a tank, and it is the one that decides a first stage. It
        is not a rearrangement of specific impulse: it is a different figure of merit that happens
        to contain it, and the two rank the combinations differently.

        '''

        density     = self.calculateBulkDensity()['bulkDensity']
        performance = self.calculateIdealPerformance()

        densityImpulse = density * performance['specificImpulse']

        self.findings = [
            f'Density impulse {densityImpulse / 1000.0:.1f} x 10^3 kg s / m^3, from '
            f'{density:.0f} kg/m^3 and {performance["specificImpulse"]:.1f} s.',
            'Specific impulse decides how much propellant a mission needs. Density impulse decides '
            'how large the tanks holding it are, and the tanks are carried through the atmosphere.']

        return {'densityImpulse':  densityImpulse,
                'bulkDensity':     density,
                'specificImpulse': performance['specificImpulse'],
                'findings':        self.findings}

    # -------------------------------------------------------------------------------------------- #

    def compareCombinations(self) -> dict:

        '''

        Every combination at the same area ratio, ranked both ways.

        Fixing the expansion is what makes the comparison mean anything. A combination expanded
        further looks better on specific impulse, and that is a nozzle decision rather than a
        propellant one.

        '''

        results = {}

        for name in PROPELLANT_COMBINATIONS:

            candidate = PropellantCombination()
            candidate.setInputs({'combination': name, 'areaRatio': self.areaRatio})

            density     = candidate.calculateBulkDensity()['bulkDensity']
            performance = candidate.calculateIdealPerformance()

            results[name] = {'specificImpulse': performance['specificImpulse'],
                             'bulkDensity':     density,
                             'densityImpulse':  density * performance['specificImpulse'],
                             'storable':        candidate.properties['storable'],
                             'hypergolic':      candidate.properties['hypergolic'],
                             'note':            candidate.properties['note']}

        byImpulse = sorted(results, key = lambda name: -results[name]['specificImpulse'])
        byDensity = sorted(results, key = lambda name: -results[name]['densityImpulse'])

        self.findings = []

        self.findings.append(
            f'On specific impulse the order is {", ".join(byImpulse[:3])}. On density impulse it '
            f'is {", ".join(byDensity[:3])}.')

        best        = results[byImpulse[0]]
        bestDensity = results[byDensity[0]]

        self.findings.append(
            f'\'{byImpulse[0]}\' leads on specific impulse at {best["specificImpulse"]:.1f} s, '
            f'{(best["specificImpulse"] / results[byDensity[0]]["specificImpulse"] - 1.0) * 100.0:+.0f} '
            f'per cent against \'{byDensity[0]}\', and trails it on density impulse by a factor of '
            f'{bestDensity["densityImpulse"] / best["densityImpulse"]:.1f}.')

        self.findings.append(
            'Neither ordering is the answer on its own. A first stage carries its tanks through the '
            'atmosphere and is a density impulse problem; an upper stage in vacuum is closer to a '
            'pure specific impulse problem.')

        storable = [name for name in results if results[name]['storable']]
        self.findings.append(
            f'{len(storable)} of {len(results)} combinations are storable, which is a different '
            f'axis again and the one that decides whether a stage can coast for a month.')

        return {'combinations':      results,
                'bySpecificImpulse': byImpulse,
                'byDensityImpulse':  byDensity,
                'areaRatio':         self.areaRatio,
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full property and trade report.
        '''

        density     = self.calculateBulkDensity()
        performance = self.calculateIdealPerformance()
        impulse     = self.calculateDensityImpulse()
        comparison  = self.compareCombinations()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  PROPELLANT COMBINATION: {self.combination}')
        lines.append('=' * 96)
        lines.append('')
        lines.append(f'  {self.properties["note"]}')
        lines.append('')

        lines.append(formatReportTable(
            [['Oxidiser',             self.properties['oxidiser'],                      ''],
             ['Fuel',                 self.properties['fuel'],                          ''],
             ['Mixture ratio',        f'{self.mixtureRatio:.2f}',                       ''],
             ['Stoichiometric ratio', f'{self.properties["stoichiometricRatio"]:.2f}',  ''],
             ['Hypergolic',           str(self.properties['hypergolic']),               ''],
             ['Storable',             str(self.properties['storable']),                 '']],
            ['Quantity', 'Value', 'Unit'], title = 'Composition'))

        lines.append('')
        lines.append(formatReportTable(
            [['Characteristic velocity', f'{performance["characteristicVelocity"]:.0f}',      'm/s'],
             ['Ideal, from Tc and M',    f'{performance["idealCharacteristicVelocity"]:.0f}', 'm/s'],
             ['Thrust coefficient',      f'{performance["thrustCoefficient"]:.4f}',           ''],
             ['Vacuum specific impulse', f'{performance["specificImpulse"]:.1f}',             's'],
             ['Bulk density',            f'{density["bulkDensity"]:.1f}',                     'kg/m^3'],
             ['Density impulse',         f'{impulse["densityImpulse"] / 1000.0:.1f}',         'x10^3 kg s/m^3']],
            ['Quantity', 'Value', 'Unit'], title = 'Performance'))

        lines.append('')
        lines.append('  Against the alternatives, all at the same area ratio:')
        lines.append('')
        lines.append(f'    {"combination":14s} {"Isp [s]":>9s} {"rho [kg/m3]":>13s} '
                     f'{"rho.Isp":>10s}')
        for name in comparison['byDensityImpulse']:
            entry  = comparison['combinations'][name]
            marker = '  <-' if name == self.combination else ''
            lines.append(f'    {name:14s} {entry["specificImpulse"]:9.1f} '
                         f'{entry["bulkDensity"]:13.0f} '
                         f'{entry["densityImpulse"] / 1000.0:10.1f}{marker}')

        lines.append('')
        for finding in (density['findings'] + performance['findings']
                        + impulse['findings'] + comparison['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            path = os.path.join(outputDir, f'propellant_{self.combination.replace("/", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.mixtureRatio <= 0.0:
            raise InvalidInputError(
                f'The mixture ratio must be positive, got {self.mixtureRatio}.',
                context = createErrorContext(component = 'PropellantCombination'))

        if self.areaRatio <= 1.0:
            raise InvalidInputError(
                f'The area ratio must exceed one, got {self.areaRatio}. An area ratio of one is '
                f'the throat, and it produces no expansion.',
                context = createErrorContext(component = 'PropellantCombination'))

        stoichiometric = self.properties['stoichiometricRatio']
        tabulated      = self.properties['mixtureRatio']

        if self.mixtureRatio < MINIMUM_STOICHIOMETRIC_FRACTION * stoichiometric:
            raise PropellantError(
                f'A mixture ratio of {self.mixtureRatio:.2f} is below '
                f'{MINIMUM_STOICHIOMETRIC_FRACTION:.0%} of the stoichiometric '
                f'{stoichiometric:.2f}. That is rich enough that unburnt fuel is dead weight, and '
                f'the tabulated chamber temperature and molar mass do not apply there.',
                context = createErrorContext(component = 'PropellantCombination'))

        if self.mixtureRatio > stoichiometric:
            raise PropellantError(
                f'A mixture ratio of {self.mixtureRatio:.2f} is above the stoichiometric '
                f'{stoichiometric:.2f}. Oxidiser rich operation at this scale is a real design '
                f'choice for a preburner and it is not what this table describes, and it attacks '
                f'the chamber wall rather than cooling it.',
                context = createErrorContext(component = 'PropellantCombination'))

        if abs(self.mixtureRatio - tabulated) > 0.01:
            self.findings.append(
                f'The mixture ratio {self.mixtureRatio:.2f} differs from the tabulated '
                f'{tabulated:.2f}. The chamber temperature, molar mass and characteristic velocity '
                f'in this table were taken at the tabulated ratio and do not travel with it, so '
                f'the performance below is the tabulated point rather than the requested one.')
