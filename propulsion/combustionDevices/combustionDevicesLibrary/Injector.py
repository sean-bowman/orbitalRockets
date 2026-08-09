
# -- Injector -- #

'''

Element sizing, pressure drop, stiffness and the wall compatibility problem.

An injector has two jobs that pull against each other. It has to mix the propellants well enough
to burn completely in the residence time available, and it has to not do that next to the wall.

The first is what c* efficiency measures. The second is what burns chambers through, and it is the
reason essentially every engine runs a different element pattern in its outer row and accepts the
c* efficiency loss that comes with it. An injector that is uniform from centre to wall is either
mixing badly everywhere or destroying its chamber, and which one depends on how good it is.

The third job is not to couple with anything. That is `CombustionStability`, and the parameter
this class owns which feeds it is stiffness: the injector pressure drop as a fraction of chamber
pressure, which is what decouples the feed system from the chamber.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from combustionUtils import (INJECTOR_ELEMENTS, CHUG_STIFFNESS_FLOOR,
                                 RECOMMENDED_STIFFNESS_LOWER, RECOMMENDED_STIFFNESS_UPPER,
                                 PROPELLANT_COMBINATIONS,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, InjectorError)
except ImportError:
    from .combustionUtils import (INJECTOR_ELEMENTS, CHUG_STIFFNESS_FLOOR,
                                  RECOMMENDED_STIFFNESS_LOWER, RECOMMENDED_STIFFNESS_UPPER,
                                  PROPELLANT_COMBINATIONS,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, InjectorError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Propellant liquid densities at injection, which is where the orifice sizing happens. These are
# the same values the hub carries for bulk density and they are read from it rather than repeated.
INJECTION_DENSITIES = {name: {'oxidiser': entry['oxidiserDensity'], 'fuel': entry['fuelDensity']}
                       for name, entry in PROPELLANT_COMBINATIONS.items()}

# Momentum ratio, the oxidiser stream momentum over the fuel stream momentum, is what decides where
# the mixed core ends up. Near one the streams penetrate each other evenly; far from one the
# stronger stream sweeps the weaker one aside and the mixing happens somewhere other than intended.
RECOMMENDED_MOMENTUM_RATIO = (0.7, 1.5)    # [-]

# Below this orifice diameter the holes are difficult to drill repeatably, difficult to keep clean
# and easy to block with a single particle. Above roughly 2 mm the atomisation suffers because the
# jet is too coarse.
MINIMUM_ORIFICE_DIAMETER = 0.4e-3    # [m]
MAXIMUM_ORIFICE_DIAMETER = 2.0e-3    # [m]

# Fraction of total fuel flow typically diverted to the outer row for wall protection. It buys wall
# temperature directly and costs c* efficiency directly, because that propellant burns at a mixture
# ratio that was chosen for the wall rather than for performance.
TYPICAL_FILM_FRACTION = 0.05    # [-]

# The c* efficiency penalty per unit of film fraction. Film propellant is not simply lost: it burns
# partly, at a mixture ratio chosen for the wall rather than for impulse. The loss is therefore a
# fraction of the diverted flow.
#
# These bounds are an estimate and are registered as unvalidated. They exist to stop the penalty
# being stated as equal to the film fraction, which overstates it by two to three times.
FILM_EFFICIENCY_PENALTY_LOWER = 0.30    # [-]
FILM_EFFICIENCY_PENALTY_UPPER = 0.50    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- Injector -- #
# ------------------------------------------------------------------------------------------------ #

class Injector:

    '''

    Orifice sizing, pressure drop, stiffness, momentum ratio and the wall row trade.

    '''

    def __init__(self):

        self.combination      = ''
        self.elementType      = ''
        self.chamberPressure  = np.nan
        self.oxidiserFlow     = np.nan
        self.fuelFlow         = np.nan
        self.elementCount     = np.nan
        self.stiffness        = np.nan
        self.filmFraction     = np.nan

        self.densities = {}
        self.element   = {}
        self.findings  = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `stiffness` is the design injector pressure drop as a fraction of chamber pressure, and it
        is an input because it is a stability decision rather than a consequence of the flow.

        On a throttling engine it has to be specified at the deepest intended setting rather than
        at full thrust, because it falls linearly with throttle. See the hub document
        ThrottlingAndMixtureRatio.

        '''

        requiredParams = {'combination':     str,
                          'chamberPressure': (int, float),
                          'oxidiserFlow':    (int, float),
                          'fuelFlow':        (int, float)}

        optionalParams = {'elementType':  str,
                          'elementCount': (int, float),
                          'stiffness':    (int, float),
                          'filmFraction': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.elementType:
            self.elementType = 'unlike impinging doublet'

        if self.elementType not in INJECTOR_ELEMENTS:
            raise InjectorError(
                f'Unknown element type \'{self.elementType}\'. Known: {sorted(INJECTOR_ELEMENTS)}.',
                context = createErrorContext(component = 'Injector'))

        if self.combination not in INJECTION_DENSITIES:
            raise InjectorError(
                f'Unknown propellant combination \'{self.combination}\'. '
                f'Known: {sorted(INJECTION_DENSITIES)}.',
                context = createErrorContext(component = 'Injector'))

        self.element   = dict(INJECTOR_ELEMENTS[self.elementType])
        self.densities = dict(INJECTION_DENSITIES[self.combination])

        if not np.isfinite(self.stiffness):
            self.stiffness = RECOMMENDED_STIFFNESS_LOWER

        if not np.isfinite(self.filmFraction):
            self.filmFraction = TYPICAL_FILM_FRACTION

        if not np.isfinite(self.elementCount):
            self.elementCount = 100.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def sizeOrifices(self) -> dict:

        '''

        Orifice diameter per element for each propellant, from the flow and the design pressure drop.

            mdot = Cd A sqrt(2 rho dP)

        Solved for area, then for diameter. The element count is an input because it is a packaging
        decision as much as a flow one: it has to fit on the face with enough land between elements
        to drill and enough to keep the pattern from merging.

        '''

        findings = []

        pressureDrop = self.stiffness * self.chamberPressure
        discharge    = self.element['dischargeCoefficient']

        results = {}

        for name, flow in (('oxidiser', self.oxidiserFlow), ('fuel', self.fuelFlow)):

            density = self.densities[name]

            perElement = flow / self.elementCount
            area       = perElement / (discharge * np.sqrt(2.0 * density * pressureDrop))
            diameter   = 2.0 * np.sqrt(area / np.pi)
            velocity   = perElement / (density * area)

            results[name] = {'flowPerElement': perElement,
                             'area':           area,
                             'diameter':       diameter,
                             'velocity':       velocity,
                             'density':        density}

        findings.append(
            f'{self.elementCount:.0f} {self.elementType} elements at '
            f'{self.stiffness:.0%} stiffness, {pressureDrop / 1.0e6:.2f} MPa drop.')

        findings.append(
            f'Oxidiser orifice {results["oxidiser"]["diameter"] * 1000.0:.2f} mm at '
            f'{results["oxidiser"]["velocity"]:.1f} m/s, fuel orifice '
            f'{results["fuel"]["diameter"] * 1000.0:.2f} mm at '
            f'{results["fuel"]["velocity"]:.1f} m/s.')

        for name, entry in results.items():
            if entry['diameter'] < MINIMUM_ORIFICE_DIAMETER:
                findings.append(
                    f'The {name} orifice at {entry["diameter"] * 1000.0:.2f} mm is below the '
                    f'{MINIMUM_ORIFICE_DIAMETER * 1000.0:.1f} mm practical floor. Holes this small '
                    f'are hard to drill repeatably and a single particle blocks one. Fewer '
                    f'elements or a lower stiffness.')
            elif entry['diameter'] > MAXIMUM_ORIFICE_DIAMETER:
                findings.append(
                    f'The {name} orifice at {entry["diameter"] * 1000.0:.2f} mm is above the '
                    f'{MAXIMUM_ORIFICE_DIAMETER * 1000.0:.1f} mm practical ceiling. The jet is '
                    f'coarse and atomisation suffers. More elements.')

        self.findings = findings

        return {'pressureDrop': pressureDrop,
                'orifices':     results,
                'elementCount': self.elementCount,
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateMomentumRatio(self) -> dict:

        '''

        Oxidiser to fuel stream momentum ratio, which decides where the mixed core sits.

            J = (rho V^2)_ox / (rho V^2)_fuel     per element, on the orifice areas

        Near one the two streams penetrate each other evenly and the mixing plane is where the
        geometry put it. Far from one the stronger stream sweeps the weaker aside, the mixing plane
        moves, and on an impinging element it can move onto the wall.

        '''

        findings = []

        orifices = self.sizeOrifices()['orifices']

        momenta = {}
        for name, entry in orifices.items():
            momenta[name] = entry['density'] * entry['velocity'] ** 2 * entry['area']

        ratio = momenta['oxidiser'] / momenta['fuel']

        lower, upper = RECOMMENDED_MOMENTUM_RATIO

        findings.append(
            f'Momentum ratio {ratio:.2f}, oxidiser over fuel, against a recommended '
            f'{lower:.1f} to {upper:.1f}.')

        # at equal pressure drop on both circuits the momentum ratio is forced:
        #   V ~ sqrt(dP / rho), so J = MR sqrt(rho_fuel / rho_ox)
        # which for a dense oxidiser and a light fuel is well above one before any design choice
        # has been made.
        mixtureRatio = self.oxidiserFlow / self.fuelFlow
        forcedRatio  = mixtureRatio * np.sqrt(self.densities['fuel']
                                              / self.densities['oxidiser'])

        findings.append(
            f'At equal pressure drop on both circuits the momentum ratio is not a free choice: it '
            f'is MR sqrt(rho_fuel / rho_ox) = {forcedRatio:.2f}. Matching the drops is what fixes '
            f'it there.')

        if ratio < lower:
            findings.append(
                'The fuel stream dominates. The mixing plane moves toward the oxidiser side and '
                'the oxidiser is under-penetrated, which shows up as a c* efficiency loss rather '
                'than as a wall problem.')
        elif ratio > upper:
            # the fuel side drop that would bring J to the top of the band
            targetVelocity = (momenta['oxidiser'] / orifices['oxidiser']['area']
                              * orifices['fuel']['area']) / 1.0
            requiredFuelVelocity = (orifices['oxidiser']['density']
                                    * orifices['oxidiser']['velocity'] ** 2
                                    * orifices['oxidiser']['area']
                                    / (upper * orifices['fuel']['density']
                                       * orifices['fuel']['area'])) ** 0.5

            discharge = self.element['dischargeCoefficient']
            requiredDrop = (orifices['fuel']['density'] * requiredFuelVelocity ** 2
                            / (2.0 * discharge ** 2))

            findings.append(
                'The oxidiser stream dominates. The mixing plane moves toward the fuel side, and '
                'on an outer row element that direction is toward the wall. This is the momentum '
                'ratio that burns chambers.')

            findings.append(
                f'Bringing it to {upper:.1f} needs the fuel side at '
                f'{requiredFuelVelocity:.1f} m/s, a {requiredDrop / 1.0e6:.2f} MPa drop against '
                f'the oxidiser side {self.stiffness * self.chamberPressure / 1.0e6:.2f} MPa. Real '
                f'injectors run the two circuits at different pressure drops for exactly this '
                f'reason, and a single stiffness number describes neither of them.')
        else:
            findings.append(
                'The streams are balanced and the mixing plane is where the geometry put it.')

        self.findings = findings

        return {'momentumRatio': ratio,
                'momenta':       momenta,
                'recommended':   RECOMMENDED_MOMENTUM_RATIO,
                'withinBand':    bool(lower <= ratio <= upper),
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def checkStiffness(self, throttleSetting: float = 1.0) -> dict:

        '''

        Injector stiffness at a throttle setting, and whether it clears the chug floor.

        Stiffness falls linearly with throttle at fixed geometry, because the pressure drop goes as
        the square of the flow and the chamber pressure goes linearly with it. A 20 per cent design
        at full thrust is 5 per cent at quarter throttle.

        The floor is a necessary condition rather than a sufficient one. Chug involves the feed line
        inertance and the chamber volume as well, so clearing it does not prove stability, and
        failing it does prove a problem.

        '''

        findings = []

        if not 0.0 < throttleSetting <= 1.0:
            raise InjectorError(
                f'The throttle setting must lie in (0, 1], got {throttleSetting}.',
                context = createErrorContext(component = 'Injector'))

        stiffness = self.stiffness * throttleSetting

        clearsFloor = stiffness >= CHUG_STIFFNESS_FLOOR

        deepestThrottle = CHUG_STIFFNESS_FLOOR / self.stiffness

        findings.append(
            f'Stiffness {stiffness:.1%} at {throttleSetting:.0%} throttle, from a '
            f'{self.stiffness:.0%} design value.')

        if not clearsFloor:
            findings.append(
                f'That is below the {CHUG_STIFFNESS_FLOOR:.0%} chug floor. The feed system and the '
                f'chamber are coupled strongly enough to sustain a low frequency oscillation.')
        elif stiffness < RECOMMENDED_STIFFNESS_LOWER:
            findings.append(
                f'Above the floor and below the recommended {RECOMMENDED_STIFFNESS_LOWER:.0%}. '
                f'Workable and worth demonstrating by test rather than by calculation.')

        findings.append(
            f'A fixed area injector at this design value reaches the floor at '
            f'{deepestThrottle:.0%} throttle. Deeper than that needs a variable area element, '
            f'which is the argument for a pintle.')

        if self.stiffness > RECOMMENDED_STIFFNESS_UPPER:
            findings.append(
                f'{self.stiffness:.0%} is above the recommended {RECOMMENDED_STIFFNESS_UPPER:.0%}. '
                f'The extra drop is pump work that buys stability margin already held, and it '
                f'lands on the feed system as discharge pressure.')

        self.findings = findings

        return {'stiffness':        stiffness,
                'designStiffness':  self.stiffness,
                'throttleSetting':  throttleSetting,
                'clearsFloor':      clearsFloor,
                'deepestThrottle':  deepestThrottle,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def checkWallCompatibility(self) -> dict:

        '''

        The outer row trade: what the film fraction buys and what it costs.

        Diverting fuel to the outer row protects the wall and removes that propellant from the
        performance mixture ratio. The c* loss is roughly the film fraction, because that flow
        burns at a mixture ratio chosen for the wall rather than for impulse.

        '''

        findings = []

        compatible = self.element['wallCompatible']

        # the core runs at a higher mixture ratio because film fuel has been taken out of it
        coreFuel     = self.fuelFlow * (1.0 - self.filmFraction)
        coreRatio    = self.oxidiserFlow / coreFuel
        overallRatio = self.oxidiserFlow / self.fuelFlow

        # The c* penalty is NOT the film fraction. Film propellant partly burns, so the loss is a
        # fraction of the diverted flow rather than all of it. Commonly quoted as 0.3 to 0.5 times
        # the film fraction, and that range is an estimate rather than a sourced value, so both
        # ends are reported instead of a single number.
        #
        # An earlier version of this class asserted the loss equalled the film fraction. That is the
        # pessimistic end of the range stated as a value, and it overstated the penalty by two to
        # three times.
        lowerLoss = FILM_EFFICIENCY_PENALTY_LOWER * self.filmFraction
        upperLoss = FILM_EFFICIENCY_PENALTY_UPPER * self.filmFraction

        efficiencyLoss = 0.5 * (lowerLoss + upperLoss)

        findings.append(
            f'{self.filmFraction:.0%} of the fuel to the outer row lifts the core mixture ratio '
            f'from {overallRatio:.2f} to {coreRatio:.2f}.')

        findings.append(
            f'The c* efficiency cost is {lowerLoss:.1%} to {upperLoss:.1%}, because the diverted '
            f'propellant burns at a ratio chosen for the wall rather than for impulse and only '
            f'partly burns at all. It is bought back in not having to replace the chamber.')

        findings.append(
            'That range is an estimate rather than a sourced value and it is recorded as '
            'unvalidated. The loss is not the film fraction itself, which is a common '
            'overstatement by a factor of two to three.')

        if not compatible:
            findings.append(
                f'A {self.elementType} in the outer row will find the wall. {self.element["note"]}. '
                f'The outer row is normally a different element from the core for exactly this '
                f'reason, and the usual choice is like-on-like.')
        else:
            findings.append(
                f'A {self.elementType} is tolerant in the outer row: {self.element["note"]}.')

        alternatives = {name: entry for name, entry in INJECTOR_ELEMENTS.items()
                        if entry['wallCompatible']}

        findings.append(
            f'Wall tolerant elements: {", ".join(sorted(alternatives))}.')

        self.findings = findings

        return {'wallCompatible':  compatible,
                'filmFraction':    self.filmFraction,
                'efficiencyLossLower': lowerLoss,
                'efficiencyLossUpper': upperLoss,
                'coreMixtureRatio': coreRatio,
                'overallMixtureRatio': overallRatio,
                'efficiencyLoss':  efficiencyLoss,
                'alternatives':    sorted(alternatives),
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def compareElements(self) -> dict:

        '''
        Every element type at the same flow and stiffness, so the trade is visible.
        '''

        original = self.elementType
        results  = {}

        try:
            for name in INJECTOR_ELEMENTS:

                self.elementType = name
                self.element     = dict(INJECTOR_ELEMENTS[name])

                orifices = self.sizeOrifices()['orifices']

                results[name] = {
                    'oxidiserDiameter': orifices['oxidiser']['diameter'],
                    'fuelDiameter':     orifices['fuel']['diameter'],
                    'mixingQuality':    self.element['mixingQuality'],
                    'wallCompatible':   self.element['wallCompatible'],
                    'note':             self.element['note']}
        finally:
            self.elementType = original
            self.element     = dict(INJECTOR_ELEMENTS[original])

        best = max(results, key = lambda name: results[name]['mixingQuality'])

        self.findings = [
            f'\'{best}\' mixes best at a relative quality of '
            f'{results[best]["mixingQuality"]:.2f}, and it is '
            f'{"wall tolerant" if results[best]["wallCompatible"] else "not wall tolerant"}.',
            'Mixing quality and wall tolerance are close to opposites across this set, which is '
            'the whole difficulty: the element that burns the propellant best is the element that '
            'burns the chamber.']

        return {'elements': results, 'bestMixing': best, 'findings': self.findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full injector report.
        '''

        orifices  = self.sizeOrifices()
        momentum  = self.calculateMomentumRatio()
        stiffness = self.checkStiffness()
        wall      = self.checkWallCompatibility()
        elements  = self.compareElements()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  INJECTOR: {self.combination}, {self.elementType}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Element count',      f'{self.elementCount:.0f}',                          ''],
             ['Design stiffness',   f'{self.stiffness:.1%}',                             ''],
             ['Pressure drop',      f'{orifices["pressureDrop"] / 1.0e6:.2f}',           'MPa'],
             ['Oxidiser orifice',   f'{orifices["orifices"]["oxidiser"]["diameter"] * 1000.0:.2f}', 'mm'],
             ['Fuel orifice',       f'{orifices["orifices"]["fuel"]["diameter"] * 1000.0:.2f}',     'mm'],
             ['Oxidiser velocity',  f'{orifices["orifices"]["oxidiser"]["velocity"]:.1f}',          'm/s'],
             ['Fuel velocity',      f'{orifices["orifices"]["fuel"]["velocity"]:.1f}',              'm/s'],
             ['Momentum ratio',     f'{momentum["momentumRatio"]:.2f}',                  ''],
             ['Deepest throttle',   f'{stiffness["deepestThrottle"]:.0%}',               ''],
             ['Film fraction',      f'{wall["filmFraction"]:.0%}',                       ''],
             ['Core mixture ratio', f'{wall["coreMixtureRatio"]:.2f}',                   '']],
            ['Quantity', 'Value', 'Unit'], title = 'Injector'))

        lines.append('')
        lines.append('  Element comparison at the same flow and stiffness:')
        lines.append('')
        lines.append(f'    {"element":26s} {"ox [mm]":>9s} {"fuel [mm]":>10s} {"mixing":>8s}   wall')
        for name, entry in elements['elements'].items():
            marker = '  <-' if name == self.elementType else ''
            lines.append(f'    {name:26s} {entry["oxidiserDiameter"] * 1000.0:9.2f} '
                         f'{entry["fuelDiameter"] * 1000.0:10.2f} {entry["mixingQuality"]:8.2f}   '
                         f'{str(entry["wallCompatible"]):5s}{marker}')

        lines.append('')
        for finding in (orifices['findings'] + momentum['findings'] + stiffness['findings']
                        + wall['findings'] + elements['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            path = os.path.join(outputDir, f'injector_{self.combination.replace("/", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('chamber pressure', self.chamberPressure),
                            ('oxidiser flow', self.oxidiserFlow),
                            ('fuel flow', self.fuelFlow)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(component = 'Injector'))

        if self.elementCount < 1:
            raise InjectorError(
                f'The element count must be at least one, got {self.elementCount}.',
                context = createErrorContext(component = 'Injector'))

        if not 0.0 < self.stiffness < 1.0:
            raise InjectorError(
                f'The stiffness must lie in (0, 1), got {self.stiffness}. It is a fraction of '
                f'chamber pressure, and a value at or above one is an injector drop exceeding the '
                f'chamber pressure it feeds.',
                context = createErrorContext(component = 'Injector'))

        if not 0.0 <= self.filmFraction < 1.0:
            raise InjectorError(
                f'The film fraction must lie in [0, 1), got {self.filmFraction}. All of the fuel '
                f'to the wall leaves nothing to burn in the core.',
                context = createErrorContext(component = 'Injector'))
