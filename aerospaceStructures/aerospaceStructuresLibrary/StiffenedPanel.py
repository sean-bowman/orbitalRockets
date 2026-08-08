
# -- StiffenedPanel Class Definition -- #

'''

Isogrid, orthogrid and skin-stringer panels: smeared properties, crippling, and the three
instability modes.

Stiffening is the other answer to the shell buckling problem. Where a sandwich separates two
facesheets with a core, a stiffened panel puts discrete ribs on one face and lets the skin span
between them. The result is stiffer per unit mass than a monocoque skin and it is machined or
formed from one piece, so there is no bond line to qualify and no core to fill with water.

The reason it beats an unstiffened shell is not that it is stronger in the same mode. It is that
it changes which mode governs. An unstiffened cylinder buckles in the imperfection-sensitive mode
that carries the 0.357 knockdown; a stiffened one buckles either locally between stiffeners, which
is a plate problem with a mild knockdown, or globally as a stiffened shell, which is far less
imperfection sensitive because the stiffeners dominate the bending stiffness.

Three modes compete and a design is balanced when they are close together:

    local skin buckling    the skin panels between stiffeners buckle
    crippling              the stiffener's own flanges buckle locally and it loses section
    general instability    the whole stiffened shell buckles as a unit

Designing so all three occur at the same load is the classic optimum, because any mode that occurs
much later than the others is carrying mass that is not earning anything. A panel where general
instability governs by a wide margin has stiffeners that are too small; one where local buckling
governs has stiffeners too far apart.

Crippling is the one that is easy to get wrong. A stiffener does not fail by Euler buckling as a
column, it fails by its flanges buckling locally at a stress below the material yield, and after
that it has lost the section it needed. The Gerard method correlates this against a
non-dimensional geometry parameter and it is empirical, because the flange edge restraint is not
analytically tractable.

See Also:
---------
SandwichPanel    : The other stability-efficient panel, with a continuous core
CylindricalShell : What the unstiffened alternative would give
BeamColumn       : A stringer is a column, and this is what checks it as one

Theory: docs/StiffenedStructures.md

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
                                 marginOfSafety, classicalShellBucklingStress, sp8007Knockdown,
                                 InvalidInputError, GeometryError, createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                  marginOfSafety, classicalShellBucklingStress, sp8007Knockdown,
                                  InvalidInputError, GeometryError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Plate buckling coefficient k in sigma = k pi^2 E / (12 (1-nu^2)) (t/b)^2, by edge restraint.
PLATE_BUCKLING_COEFFICIENTS = {
    'simply supported': 4.00,   # [-], all four edges pinned. The conservative default
    'clamped':          6.98,   # [-], all four edges fixed
    'one edge free':    0.43,   # [-], a flange, supported on one edge only
}

# Gerard crippling coefficients, sigma_cc / sigma_y = beta (g t^2 / A * sqrt(E/sigma_y))^m
GERARD_COEFFICIENT = 0.56    # [-], for angle, tee and cruciform sections
GERARD_EXPONENT    = 0.85    # [-]
CRIPPLING_CUTOFF   = 1.0     # [-], crippling stress cannot exceed yield

# Isogrid: the equivalent smeared properties of an equilateral triangular grid, per Meyer's
# NASA CR-124075. alpha is the stiffener area ratio, delta the depth ratio.
ISOGRID_TRIANGLE_FACTOR = 3.0    # [-], stiffeners per triangle edge, shared between two triangles

STIFFENER_TYPES = {
    'blade':     {'flangeCount': 1, 'note': 'simplest, machined. Cripples earliest'},
    'tee':       {'flangeCount': 2, 'note': 'better crippling for the same area'},
    'angle':     {'flangeCount': 2, 'note': 'formed sheet, asymmetric'},
    'hat':       {'flangeCount': 4, 'note': 'closed section, best crippling and torsional stiffness'},
}

PANEL_TYPES = {
    'isogrid':       {'note': 'equilateral triangles, isotropic smeared properties'},
    'orthogrid':     {'note': 'orthogonal ribs, different properties in each direction'},
    'skin-stringer': {'note': 'discrete stringers on a skin, the classic airframe form'},
}

# ------------------------------------------------------------------------------------------------ #
# -- StiffenedPanel -- #
# ------------------------------------------------------------------------------------------------ #

class StiffenedPanel:

    '''

    Stiffened panel smeared properties and instability screening.

    Usage:
    ------
        panel = StiffenedPanel()
        panel.setInputs({'material': '2219-T87', 'condition': 't87', 'panelType': 'skin-stringer',
                         'skinThickness': 0.002, 'stiffenerSpacing': 0.10,
                         'stiffenerHeight': 0.030, 'stiffenerThickness': 0.003,
                         'radius': 1.0, 'frameSpacing': 0.5, 'axialLoad': 400.0e3})
        result = panel.screenInstabilityModes()

    '''

    def __init__(self):

        # -- Panel -- #

        self.panelType          = 'skin-stringer'  # key into PANEL_TYPES
        self.skinThickness      = np.nan  # [m]
        self.stiffenerSpacing   = np.nan  # [m], centre to centre
        self.stiffenerHeight    = np.nan  # [m], from the skin surface
        self.stiffenerThickness = np.nan  # [m]
        self.stiffenerType      = 'blade'  # key into STIFFENER_TYPES

        # -- Shell Geometry -- #

        self.radius             = np.nan  # [m], for a curved panel. NaN for flat
        self.frameSpacing       = np.nan  # [m], ring frame pitch, the general instability length

        # -- Material -- #

        self.material           = '2219-T87'
        self.condition          = None    # [-]
        self.basis              = 'typical'  # [-]
        self.temperature        = 293.15  # [K]
        self.modulus            = np.nan  # [Pa]
        self.yieldStrength      = np.nan  # [Pa]
        self.density            = np.nan  # [kg/m^3]
        self.poisson            = 0.33    # [-]

        # -- Loading -- #

        self.axialLoad          = 0.0     # [N], total on the panel or shell
        self.edgeRestraint      = 'simply supported'  # key into PLATE_BUCKLING_COEFFICIENTS

        # -- Factors -- #

        self.factorOfSafety     = 1.4     # [-]

        # -- Results -- #

        self.findings           = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: skinThickness, stiffenerSpacing, stiffenerHeight, stiffenerThickness.

        '''

        requiredParams = {'skinThickness':      (int, float),
                          'stiffenerSpacing':   (int, float),
                          'stiffenerHeight':    (int, float),
                          'stiffenerThickness': (int, float)}

        optionalParams = {'panelType':      str,
                          'stiffenerType':  str,
                          'radius':         (int, float),
                          'frameSpacing':   (int, float),
                          'material':       str,
                          'condition':      str,
                          'basis':          str,
                          'temperature':    (int, float),
                          'modulus':        (int, float),
                          'yieldStrength':  (int, float),
                          'density':        (int, float),
                          'poisson':        (int, float),
                          'axialLoad':      (int, float),
                          'edgeRestraint':  str,
                          'factorOfSafety': (int, float)}

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

    def calculateSmearedProperties(self) -> dict:

        '''

        Equivalent thickness and bending stiffness of the stiffened panel, smeared over its width.

        The smeared thickness is the thickness of an unstiffened skin of the same mass. Comparing
        the panel's buckling capability against an unstiffened skin of that thickness is the honest
        measure of what the stiffening bought.

        '''

        self._validateInputs()

        stiffenerArea = self.stiffenerHeight * self.stiffenerThickness
        skinArea      = self.stiffenerSpacing * self.skinThickness
        totalArea     = skinArea + stiffenerArea

        smearedThickness = totalArea / self.stiffenerSpacing

        # neutral axis from the skin mid-plane
        skinCentroid      = 0.0
        stiffenerCentroid = self.skinThickness / 2.0 + self.stiffenerHeight / 2.0
        neutralAxis       = stiffenerArea * stiffenerCentroid / totalArea

        # second moment about the panel neutral axis, per stiffener bay
        skinSecond = (self.stiffenerSpacing * self.skinThickness ** 3 / 12.0
                      + skinArea * (neutralAxis - skinCentroid) ** 2)
        stiffenerSecond = (self.stiffenerThickness * self.stiffenerHeight ** 3 / 12.0
                           + stiffenerArea * (stiffenerCentroid - neutralAxis) ** 2)
        secondMoment = skinSecond + stiffenerSecond

        radiusOfGyration = np.sqrt(secondMoment / totalArea)

        # the equivalent unstiffened skin of the same mass, for the comparison
        unstiffenedSecond = (self.stiffenerSpacing * smearedThickness ** 3 / 12.0)

        return {'stiffenerArea':     stiffenerArea,
                'skinArea':          skinArea,
                'totalArea':         totalArea,
                'areaRatio':         stiffenerArea / skinArea,
                'smearedThickness':  smearedThickness,
                'neutralAxis':       neutralAxis,
                'secondMoment':      secondMoment,
                'radiusOfGyration':  radiusOfGyration,
                'bendingEfficiency': secondMoment / unstiffenedSecond,
                'arealMass':         smearedThickness * self.density}

    # -------------------------------------------------------------------------------------------- #

    def calculateLocalSkinBuckling(self) -> dict:

        '''

        Buckling of a skin bay between two stiffeners, treated as a flat plate.

            sigma = k pi^2 E / (12 (1 - nu^2)) (t / b)^2

        A plate is far less imperfection sensitive than a shell, because its buckling modes are
        well separated. That is precisely why stiffening helps: it converts a shell problem into a
        plate problem.

        '''

        self._validateInputs()

        if self.edgeRestraint not in PLATE_BUCKLING_COEFFICIENTS:
            raise InvalidInputError(
                f'Unknown edge restraint \'{self.edgeRestraint}\'. '
                f'Known: {sorted(PLATE_BUCKLING_COEFFICIENTS)}.',
                context = createErrorContext(component = 'StiffenedPanel'))

        coefficient = PLATE_BUCKLING_COEFFICIENTS[self.edgeRestraint]

        allowable = (coefficient * np.pi ** 2 * self.modulus
                     / (12.0 * (1.0 - self.poisson ** 2))
                     * (self.skinThickness / self.stiffenerSpacing) ** 2)

        # a plate cannot buckle above yield; past that it crushes
        allowable = min(allowable, self.yieldStrength)

        applied = self._appliedStress()

        return {'bucklingCoefficient': coefficient,
                'edgeRestraint':       self.edgeRestraint,
                'bayWidth':            self.stiffenerSpacing,
                'allowableStress':     allowable,
                'appliedStress':       applied,
                'yieldLimited':        bool(allowable >= self.yieldStrength),
                'margin':              marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateCrippling(self) -> dict:

        '''

        Stiffener crippling by the Gerard method.

            sigma_cc / sigma_y = beta (g t^2 / A sqrt(E / sigma_y))^m

        g is the number of flanges and cuts in the section, which is why a hat section cripples
        later than a blade of the same area: more edges means more restraint.

        '''

        self._validateInputs()

        if self.stiffenerType not in STIFFENER_TYPES:
            raise InvalidInputError(
                f'Unknown stiffener type \'{self.stiffenerType}\'. '
                f'Known: {sorted(STIFFENER_TYPES)}.',
                context = createErrorContext(component = 'StiffenedPanel'))

        flangeCount   = STIFFENER_TYPES[self.stiffenerType]['flangeCount']
        stiffenerArea = self.stiffenerHeight * self.stiffenerThickness

        parameter = (flangeCount * self.stiffenerThickness ** 2 / stiffenerArea
                     * np.sqrt(self.modulus / self.yieldStrength))

        ratio = GERARD_COEFFICIENT * parameter ** GERARD_EXPONENT
        ratio = min(ratio, CRIPPLING_CUTOFF)

        allowable = ratio * self.yieldStrength
        applied   = self._appliedStress()

        return {'stiffenerType':      self.stiffenerType,
                'flangeCount':        flangeCount,
                'gerardParameter':    parameter,
                'cripplingRatio':     ratio,
                'cripplingStress':    allowable,
                'appliedStress':      applied,
                'fullyEffective':     bool(ratio >= CRIPPLING_CUTOFF),
                'margin':             marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateGeneralInstability(self) -> dict:

        '''

        Buckling of the whole stiffened shell between ring frames.

        Uses the classical shell relation on the smeared thickness, with the stiffened knockdown
        relaxed relative to an unstiffened shell: stiffeners dominate the bending stiffness, so the
        panel is much less sensitive to the skin's geometric imperfections.

        '''

        self._validateInputs()

        if not np.isfinite(self.radius):
            return {'applicable': False,
                    'reason': 'General instability applies to a curved shell. Set radius.',
                    'margin': np.inf}

        smeared = self.calculateSmearedProperties()

        # Effective thickness for bending, from the smeared second moment. I = b t^3 / 12, so this
        # is a cube root: a square root here silently returns a thickness below the smeared value
        # and makes stiffening look as though it reduces buckling capability.
        effectiveThickness = (12.0 * smeared['secondMoment'] / self.stiffenerSpacing) ** (1.0 / 3.0)

        classical = classicalShellBucklingStress(self.modulus, effectiveThickness,
                                                 self.radius, self.poisson)

        # the knockdown is computed on the effective, not the smeared, R/t. A stiffened shell is
        # far less imperfection sensitive than an unstiffened one of the same mass.
        knockdown = sp8007Knockdown(self.radius / effectiveThickness)

        # the stress is carried on the actual area, so convert back
        allowable = (classical * knockdown * effectiveThickness
                     / smeared['smearedThickness'])
        allowable = min(allowable, self.yieldStrength)

        applied = self._appliedStress()

        return {'applicable':          True,
                'effectiveThickness':  effectiveThickness,
                'smearedThickness':    smeared['smearedThickness'],
                'thicknessGain':       effectiveThickness / smeared['smearedThickness'],
                'knockdown':           knockdown,
                'allowableStress':     allowable,
                'appliedStress':       applied,
                'margin':              marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def compareAgainstUnstiffened(self) -> dict:

        '''

        What the stiffening actually bought, against an unstiffened shell of identical mass.

        This is the honest comparison and it is the one most often skipped. A stiffened panel that
        carries less than an unstiffened skin of the same areal mass is a worse design that took
        more machining to produce.

        '''

        self._validateInputs()

        if not np.isfinite(self.radius):
            raise InvalidInputError('The comparison needs a shell radius.',
                                    context = createErrorContext(component = 'StiffenedPanel'))

        smeared = self.calculateSmearedProperties()
        thickness = smeared['smearedThickness']

        classical = classicalShellBucklingStress(self.modulus, thickness, self.radius,
                                                 self.poisson)
        unstiffened = min(classical * sp8007Knockdown(self.radius / thickness),
                          self.yieldStrength)

        modes = self.screenInstabilityModes()
        stiffened = modes['governingStress']

        return {'unstiffenedAllowable': unstiffened,
                'stiffenedAllowable':   stiffened,
                'gain':                 stiffened / unstiffened,
                'arealMass':            smeared['arealMass'],
                'note':                 f'At equal areal mass the stiffened panel carries '
                                        f'{stiffened / unstiffened:.2f}x the unstiffened skin.'}

    # -------------------------------------------------------------------------------------------- #

    def screenInstabilityModes(self) -> dict:

        '''

        All three modes, with the governing one identified and the balance reported.

        A balanced design has the three modes within roughly 20 percent of each other. Anything
        much later than the governing mode is mass that is not earning its place.

        '''

        self._validateInputs()

        local     = self.calculateLocalSkinBuckling()
        crippling = self.calculateCrippling()
        general   = self.calculateGeneralInstability()

        stresses = {'local skin buckling': local['allowableStress'],
                    'crippling':           crippling['cripplingStress']}
        if general['applicable']:
            stresses['general instability'] = general['allowableStress']

        governing       = min(stresses, key = stresses.get)
        governingStress = stresses[governing]
        applied         = self._appliedStress()

        self.findings = []

        spread = max(stresses.values()) / governingStress

        self.findings.append(
            f'{governing} governs at {governingStress / 1.0e6:.1f} MPa.')

        if spread > 1.5:
            latest = max(stresses, key = stresses.get)
            self.findings.append(
                f'The modes are {spread:.2f}x apart, so the design is unbalanced. {latest} occurs '
                f'at {stresses[latest] / 1.0e6:.1f} MPa and is carrying mass that is not earning '
                f'anything.')
        else:
            self.findings.append(
                f'The three modes are within {(spread - 1.0) * 100.0:.0f} % of each other, which '
                f'is a reasonably balanced design.')

        if not crippling['fullyEffective']:
            self.findings.append(
                f'The stiffener cripples at {crippling["cripplingRatio"]:.2f} of yield, so it is '
                f'not fully effective. A {self.stiffenerType} has '
                f'{crippling["flangeCount"]} flange(s); a section with more edges would cripple '
                f'later for the same area.')

        return {'stresses':        stresses,
                'governingMode':   governing,
                'governingStress': governingStress,
                'appliedStress':   applied,
                'modeSpread':      spread,
                'balanced':        bool(spread <= 1.5),
                'margin':          marginOfSafety(governingStress, applied, self.factorOfSafety),
                'findings':        self.findings}

    # -------------------------------------------------------------------------------------------- #

    def _appliedStress(self) -> float:

        '''
        Applied axial stress on the smeared section.
        '''

        smeared = self.calculateSmearedProperties()

        if np.isfinite(self.radius):
            area = 2.0 * np.pi * self.radius * smeared['smearedThickness']
        else:
            area = smeared['totalArea']

        return abs(self.axialLoad) / area if area > 0.0 else np.nan

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the panel and its governing mode.
        '''

        screen  = self.screenInstabilityModes()
        smeared = self.calculateSmearedProperties()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  STIFFENED PANEL: {self.panelType}, {self.material}, '
                     f'{self.stiffenerType} stiffeners')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Skin thickness',     f'{self.skinThickness * 1000.0:.2f}', 'mm'],
                ['Stiffener spacing',  f'{self.stiffenerSpacing * 1000.0:.1f}', 'mm'],
                ['Stiffener height',   f'{self.stiffenerHeight * 1000.0:.1f}', 'mm'],
                ['Smeared thickness',  f'{smeared["smearedThickness"] * 1000.0:.3f}', 'mm'],
                ['Areal mass',         f'{smeared["arealMass"]:.2f}', 'kg/m^2'],
                ['Bending efficiency', f'{smeared["bendingEfficiency"]:.1f}',
                 'x equal-mass skin']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Geometry'))
        lines.append('')

        modeRows = [[name, f'{stress / 1.0e6:.1f}',
                     'GOVERNS' if name == screen['governingMode'] else '']
                    for name, stress in sorted(screen['stresses'].items(),
                                               key = lambda item: item[1])]
        lines.append(formatReportTable(modeRows, ['Instability mode', 'Stress [MPa]', ''],
                                       title = f'Modes, applied '
                                               f'{screen["appliedStress"] / 1.0e6:.1f} MPa'))

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
            with open(os.path.join(outputDir, 'stiffenedPanel.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the panel geometry is physical and consistent.
        '''

        context = createErrorContext(component = 'StiffenedPanel')

        for name in ('skinThickness', 'stiffenerSpacing', 'stiffenerHeight', 'stiffenerThickness'):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0.0:
                raise InvalidInputError(f'{name} must be positive.', context = context)

        if self.panelType not in PANEL_TYPES:
            raise InvalidInputError(
                f'Unknown panel type \'{self.panelType}\'. Known: {sorted(PANEL_TYPES)}.',
                context = context)

        if self.stiffenerThickness >= self.stiffenerSpacing:
            raise GeometryError(
                f'Stiffener thickness {self.stiffenerThickness * 1000.0:.2f} mm is not less than '
                f'the spacing {self.stiffenerSpacing * 1000.0:.1f} mm. The stiffeners overlap.',
                context = context)

        if self.stiffenerHeight / self.stiffenerThickness > 40.0:
            raise GeometryError(
                f'Stiffener height to thickness is '
                f'{self.stiffenerHeight / self.stiffenerThickness:.0f}, above 40. A blade that '
                f'slender cripples at a trivial stress and the correlation is out of range.',
                context = context)
