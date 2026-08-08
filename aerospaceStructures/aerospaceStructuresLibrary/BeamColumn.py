
# -- BeamColumn Class Definition -- #

'''

Column buckling: Euler, Johnson, effective length, and the amplification of combined bending.

A column is the one structural element where the classical solution is trustworthy, because a
column has a single buckling mode rather than the dense cluster a shell has. Euler is not knocked
down by a factor of three; it is accurate to within a few percent for a slender pinned column.
That contrast with CylindricalShell is the most useful thing in this class.

What Euler does get wrong is short columns, and it gets them wrong in the unconservative direction:

    Euler       sigma = pi^2 E / lambda^2
    Johnson     sigma = sigma_y - (sigma_y / (2 pi))^2 lambda^2 / E
    transition  lambda_c = sqrt(2 pi^2 E / sigma_y)

Below lambda_c, Euler predicts a buckling stress above the material yield, which is physically
impossible: the column crushes first. The Johnson parabola is tangent to Euler at the transition
and runs to the yield strength at zero slenderness. Applying Euler below the transition is the
classic column error and it is always unconservative.

The transition slenderness is a material property, not a geometry one, and it is worth recognising
on sight: about 70 for 6061-T6, about 90 for 2219-T87, about 120 for annealed 316L.

Effective length is where real columns are lost. The end restraint assumption moves the buckling
load by a factor of sixteen between fixed-fixed and free-fixed, and a joint designed as fixed that
behaves as pinned has half the capability it was credited with. The recommended design values are
deliberately more conservative than the theoretical ones for exactly that reason.

See Also:
---------
CylindricalShell : The contrast. A shell buckles far below its classical load, a column does not
StiffenedPanel   : Stringers are columns, and this is what sizes them

Theory: docs/StabilityAndCollapse.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                 marginOfSafety, eulerCriticalStress, transitionSlenderness,
                                 InvalidInputError, GeometryError, createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                  marginOfSafety, eulerCriticalStress, transitionSlenderness,
                                  InvalidInputError, GeometryError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Effective length factor K, by end restraint. The theoretical value assumes the restraint is
# perfect; the recommended value is what to design to, because real joints are never perfectly
# fixed and the error from assuming they are is unconservative.
END_CONDITIONS = {
    'pinned-pinned':  {'theoretical': 1.0, 'recommended': 1.0,
                       'note': 'the reference case, and the only one where theory is safe as-is'},
    'fixed-fixed':    {'theoretical': 0.5, 'recommended': 0.65,
                       'note': 'a joint that is truly fixed is rare'},
    'fixed-pinned':   {'theoretical': 0.7, 'recommended': 0.80,
                       'note': ''},
    'fixed-free':     {'theoretical': 2.0, 'recommended': 2.10,
                       'note': 'a cantilever, the weakest case by a factor of sixteen on load'},
    'fixed-sway':     {'theoretical': 1.0, 'recommended': 1.20,
                       'note': 'fixed ends but free to translate, as in an unbraced frame'},
}

# Common section shapes, as the radius of gyration expressed against a characteristic dimension.
SECTION_SHAPES = {
    'solid round':   {'note': 'rho = d / 4'},
    'thin tube':     {'note': 'rho = D / (2 sqrt(2)), the most efficient column section'},
    'solid square':  {'note': 'rho = a / sqrt(12)'},
    'custom':        {'note': 'area and second moment supplied directly'},
}

# ------------------------------------------------------------------------------------------------ #
# -- BeamColumn -- #
# ------------------------------------------------------------------------------------------------ #

class BeamColumn:

    '''

    Column buckling and combined axial-bending.

    Usage:
    ------
        strut = BeamColumn()
        strut.setInputs({'material': '6061-T6', 'length': 1.2, 'shape': 'thin tube',
                         'outerDiameter': 0.050, 'wallThickness': 0.002,
                         'endCondition': 'pinned-pinned', 'axialLoad': 30.0e3})
        result = strut.calculateBuckling()

    '''

    def __init__(self):

        # -- Geometry -- #

        self.length          = np.nan   # [m], unbraced length
        self.shape           = 'thin tube'   # key into SECTION_SHAPES
        self.outerDiameter   = np.nan   # [m]
        self.wallThickness   = np.nan   # [m], thin tube only
        self.sideLength      = np.nan   # [m], solid square only
        self.area            = np.nan   # [m^2], custom shape
        self.secondMoment    = np.nan   # [m^4], custom shape

        # -- Material -- #

        self.material        = '6061-T6'
        self.condition       = None     # [-]
        self.basis           = 'typical'  # [-]
        self.temperature     = 293.15   # [K]
        self.modulus         = np.nan   # [Pa], overrides the lookup
        self.yieldStrength   = np.nan   # [Pa], overrides the lookup
        self.density         = np.nan   # [kg/m^3], overrides the lookup

        # -- Restraint and Loading -- #

        self.endCondition    = 'pinned-pinned'  # key into END_CONDITIONS
        self.useTheoreticalK = False    # [-], True to use the theoretical rather than design K
        self.axialLoad       = 0.0      # [N], compression positive
        self.transverseMoment = 0.0     # [N*m], applied bending, for the combined check
        self.eccentricity    = 0.0      # [m], load offset from the centroid

        # -- Factors -- #

        self.factorOfSafety  = 1.4      # [-]

        # -- Results -- #

        self.findings        = []       # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: length.

        '''

        requiredParams = {'length': (int, float)}

        optionalParams = {'shape':            str,
                          'outerDiameter':    (int, float),
                          'wallThickness':    (int, float),
                          'sideLength':       (int, float),
                          'area':             (int, float),
                          'secondMoment':     (int, float),
                          'material':         str,
                          'condition':        str,
                          'basis':            str,
                          'temperature':      (int, float),
                          'modulus':          (int, float),
                          'yieldStrength':    (int, float),
                          'density':          (int, float),
                          'endCondition':     str,
                          'useTheoreticalK':  bool,
                          'axialLoad':        (int, float),
                          'transverseMoment': (int, float),
                          'eccentricity':     (int, float),
                          'factorOfSafety':   (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        properties = structuralAllowables(self.material, self.condition,
                                          temperature = self.temperature, basis = self.basis)

        if not np.isfinite(self.modulus):
            self.modulus = properties['elasticModulus']
        if not np.isfinite(self.yieldStrength):
            self.yieldStrength = properties['yieldStrength']
        if not np.isfinite(self.density):
            self.density = properties['density']

    # -------------------------------------------------------------------------------------------- #

    def calculateSectionProperties(self) -> dict:

        '''

        Area, second moment and radius of gyration for the selected shape.

        '''

        self._validateInputs()

        if self.shape == 'custom':
            area, second = self.area, self.secondMoment

        elif self.shape == 'solid round':
            radius = self.outerDiameter / 2.0
            area   = np.pi * radius ** 2
            second = np.pi * radius ** 4 / 4.0

        elif self.shape == 'thin tube':
            outer  = self.outerDiameter / 2.0
            inner  = outer - self.wallThickness
            area   = np.pi * (outer ** 2 - inner ** 2)
            second = np.pi * (outer ** 4 - inner ** 4) / 4.0

        elif self.shape == 'solid square':
            area   = self.sideLength ** 2
            second = self.sideLength ** 4 / 12.0

        else:
            raise InvalidInputError(f'Unknown shape \'{self.shape}\'.',
                                    context = createErrorContext(component = 'BeamColumn'))

        radiusOfGyration = np.sqrt(second / area)

        return {'area':             area,
                'secondMoment':     second,
                'radiusOfGyration': radiusOfGyration,
                'mass':             area * self.length * self.density,
                'sectionEfficiency': radiusOfGyration / np.sqrt(area)}

    # -------------------------------------------------------------------------------------------- #

    @property
    def effectiveLengthFactor(self) -> float:

        '''
        K for the selected end condition, design value unless the theoretical one was requested.
        '''

        if self.endCondition not in END_CONDITIONS:
            raise InvalidInputError(
                f'Unknown end condition \'{self.endCondition}\'. Known: {sorted(END_CONDITIONS)}.',
                context = createErrorContext(component = 'BeamColumn'))

        entry = END_CONDITIONS[self.endCondition]

        return entry['theoretical'] if self.useTheoreticalK else entry['recommended']

    def calculateSlenderness(self) -> dict:

        '''

        Effective slenderness ratio and the transition slenderness for the material.

        '''

        section = self.calculateSectionProperties()

        effectiveLength = self.effectiveLengthFactor * self.length
        slenderness     = effectiveLength / section['radiusOfGyration']
        transition      = transitionSlenderness(self.modulus, self.yieldStrength)

        return {'effectiveLengthFactor': self.effectiveLengthFactor,
                'effectiveLength':       effectiveLength,
                'radiusOfGyration':      section['radiusOfGyration'],
                'slenderness':           slenderness,
                'transitionSlenderness': transition,
                'isSlender':             bool(slenderness >= transition),
                'regime':                'Euler' if slenderness >= transition else 'Johnson'}

    # -------------------------------------------------------------------------------------------- #

    def calculateBuckling(self) -> dict:

        '''

        Critical stress from whichever of Euler or Johnson applies, and the margin.

        '''

        self._validateInputs()

        section     = self.calculateSectionProperties()
        slenderness = self.calculateSlenderness()

        lambdaValue = slenderness['slenderness']
        transition  = slenderness['transitionSlenderness']

        euler = eulerCriticalStress(self.modulus, lambdaValue)

        johnson = (self.yieldStrength
                   - (self.yieldStrength / (2.0 * np.pi)) ** 2 * lambdaValue ** 2 / self.modulus)

        if slenderness['isSlender']:
            critical = euler
        else:
            critical = johnson

        applied = abs(self.axialLoad) / section['area'] if section['area'] > 0.0 else np.nan

        self.findings = []

        if not slenderness['isSlender']:
            self.findings.append(
                f'Slenderness {lambdaValue:.1f} is below the transition at {transition:.1f}, so '
                f'Johnson governs at {johnson / 1.0e6:.1f} MPa. Euler would predict '
                f'{euler / 1.0e6:.1f} MPa here, which is '
                f'{euler / johnson:.2f}x optimistic and unconservative.')
        else:
            self.findings.append(
                f'Slenderness {lambdaValue:.1f} is above the transition at {transition:.1f}, so '
                f'Euler applies. Unlike a shell, this needs no empirical knockdown.')

        if self.endCondition != 'pinned-pinned' and not self.useTheoreticalK:
            entry = END_CONDITIONS[self.endCondition]
            self.findings.append(
                f'Design K of {entry["recommended"]:.2f} used rather than the theoretical '
                f'{entry["theoretical"]:.2f}, because a real joint is never perfectly restrained. '
                f'That is a {(entry["recommended"] / entry["theoretical"]) ** 2:.2f}x reduction in '
                f'buckling load.')

        return {'eulerStress':       euler,
                'johnsonStress':     johnson,
                'criticalStress':    critical,
                'regime':            slenderness['regime'],
                'slenderness':       lambdaValue,
                'transitionSlenderness': transition,
                'appliedStress':     applied,
                'criticalLoad':      critical * section['area'],
                'margin':            marginOfSafety(critical, applied, self.factorOfSafety),
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateCombinedAxialBending(self) -> dict:

        '''

        Combined compression and bending, with the P-delta amplification.

        An axial load acting through the lateral deflection that bending produces adds moment, so
        the two do not simply superpose. The amplification factor is

            AF = 1 / (1 - P / P_critical)

        which goes to infinity as the axial load approaches the buckling load. A column at half its
        buckling load doubles its applied moment, and an interaction check that ignores this is
        optimistic exactly where it matters.

        '''

        self._validateInputs()

        section  = self.calculateSectionProperties()
        buckling = self.calculateBuckling()

        criticalLoad = buckling['criticalLoad']
        axial        = abs(self.axialLoad)

        loadRatio = axial / criticalLoad if criticalLoad > 0.0 else np.inf

        if loadRatio >= 1.0:
            raise GeometryError(
                f'Applied axial load is {loadRatio:.2f} of the critical load. The column has '
                f'already buckled and the amplification factor is undefined.',
                context = createErrorContext(component = 'BeamColumn'))

        amplification = 1.0 / (1.0 - loadRatio)

        # eccentric load contributes a primary moment
        primaryMoment = abs(self.transverseMoment) + axial * abs(self.eccentricity)
        totalMoment   = primaryMoment * amplification

        extremeFibre = (self.outerDiameter / 2.0 if np.isfinite(self.outerDiameter)
                        else np.sqrt(section['secondMoment'] / section['area']))
        bendingStress = (totalMoment * extremeFibre / section['secondMoment']
                         if section['secondMoment'] > 0.0 else np.nan)
        axialStress   = axial / section['area']

        combined = axialStress + bendingStress

        findings = []
        if amplification > 1.2:
            findings.append(
                f'The axial load is {loadRatio:.2f} of critical, so the applied moment is '
                f'amplified {amplification:.2f}x by P-delta. Superposing the two loads without '
                f'this factor understates the stress by '
                f'{(1.0 - 1.0 / amplification) * 100.0:.0f} %.')

        return {'loadRatio':          loadRatio,
                'amplificationFactor': amplification,
                'primaryMoment':      primaryMoment,
                'amplifiedMoment':    totalMoment,
                'axialStress':        axialStress,
                'bendingStress':      bendingStress,
                'combinedStress':     combined,
                'margin':             marginOfSafety(self.yieldStrength, combined,
                                                     self.factorOfSafety),
                'findings':           findings}

    # -------------------------------------------------------------------------------------------- #

    def compareEndConditions(self) -> dict:

        '''

        The buckling load under every end condition, which is how large the restraint assumption is.

        '''

        self._validateInputs()

        saved   = self.endCondition
        results = {}

        try:
            for condition in END_CONDITIONS:
                self.endCondition = condition
                results[condition] = self.calculateBuckling()['criticalLoad']
        finally:
            self.endCondition = saved

        best  = max(results.values())
        worst = min(results.values())

        return {'criticalLoads': results,
                'spread':        best / worst,
                'note':          f'The end restraint assumption moves the buckling load by '
                                 f'{best / worst:.1f}x across the range.'}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the column.
        '''

        buckling = self.calculateBuckling()
        section  = self.calculateSectionProperties()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  BEAM COLUMN: {self.material}, {self.shape}, L = {self.length:.3f} m')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Area',               f'{section["area"] * 1.0e6:.1f}', 'mm^2'],
                ['Radius of gyration', f'{section["radiusOfGyration"] * 1000.0:.2f}', 'mm'],
                ['Effective length K', f'{self.effectiveLengthFactor:.2f}', '-'],
                ['Slenderness',        f'{buckling["slenderness"]:.1f}', '-'],
                ['Transition',         f'{buckling["transitionSlenderness"]:.1f}', '-'],
                ['Regime',             buckling['regime'], '-']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Section'))
        lines.append('')

        stress = [['Euler',           f'{buckling["eulerStress"] / 1.0e6:.1f}', 'MPa'],
                  ['Johnson',         f'{buckling["johnsonStress"] / 1.0e6:.1f}', 'MPa'],
                  ['Governing',       f'{buckling["criticalStress"] / 1.0e6:.1f}', 'MPa'],
                  ['Applied',         f'{buckling["appliedStress"] / 1.0e6:.1f}', 'MPa'],
                  ['Margin',          f'{buckling["margin"]:+.3f}', '-']]
        lines.append(formatReportTable(stress, ['Quantity', 'Value', 'Unit'],
                                       title = f'Buckling, FS {self.factorOfSafety:.2f}'))

        if self.findings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in self.findings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'beamColumn.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the geometry needed by the selected shape is present.
        '''

        context = createErrorContext(component = 'BeamColumn')

        if not np.isfinite(self.length) or self.length <= 0.0:
            raise InvalidInputError('Column length must be positive.', context = context)

        if self.shape not in SECTION_SHAPES:
            raise InvalidInputError(
                f'Unknown shape \'{self.shape}\'. Known: {sorted(SECTION_SHAPES)}.',
                context = context)

        if self.shape == 'custom':
            if not (np.isfinite(self.area) and np.isfinite(self.secondMoment)):
                raise InvalidInputError('A custom section needs area and secondMoment.',
                                        context = context)
        elif self.shape == 'solid square':
            if not np.isfinite(self.sideLength) or self.sideLength <= 0.0:
                raise InvalidInputError('A solid square needs a positive sideLength.',
                                        context = context)
        else:
            if not np.isfinite(self.outerDiameter) or self.outerDiameter <= 0.0:
                raise InvalidInputError(f'A {self.shape} needs a positive outerDiameter.',
                                        context = context)

        if self.shape == 'thin tube':
            if not np.isfinite(self.wallThickness) or self.wallThickness <= 0.0:
                raise InvalidInputError('A thin tube needs a positive wallThickness.',
                                        context = context)
            if self.wallThickness >= self.outerDiameter / 2.0:
                raise GeometryError(
                    f'Wall thickness {self.wallThickness * 1000.0:.2f} mm is at or beyond the '
                    f'tube radius. Use \'solid round\' instead.', context = context)

        if self.endCondition not in END_CONDITIONS:
            raise InvalidInputError(
                f'Unknown end condition \'{self.endCondition}\'. Known: {sorted(END_CONDITIONS)}.',
                context = context)
