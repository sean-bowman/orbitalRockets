
# -- SandwichPanel Class Definition -- #

'''

Honeycomb and foam core sandwich: facesheet wrinkling, core shear, dimpling, crimping and bending.

A sandwich panel is an I-beam smeared out over an area. The facesheets carry the bending as tension
and compression, the core carries the shear and holds the facesheets apart, and the separation is
what buys the stiffness: flexural rigidity goes as the square of the core depth while mass goes
almost linearly with it. That is why a sandwich beats a monocoque skin on stiffness per unit mass
by a wide margin, and why it is used wherever a panel is stability critical rather than strength
critical.

It also fails in ways a monolithic panel does not, and they are the reason this class exists:

    facesheet wrinkling   the facesheet buckles into the core, at a short wavelength
    intracell dimpling    the facesheet dips into an individual honeycomb cell
    shear crimping        a very short wavelength wrinkle through the whole section
    core shear            the core fails in shear before either facesheet yields
    flatwise tension      the bond between facesheet and core lets go

Wrinkling is the one that catches people. It does not depend on the panel length or the boundary
conditions at all, only on the facesheet and core moduli:

    sigma_wrinkle = K (E_f E_c G_c)^(1/3)

so a longer panel does not wrinkle at a lower stress. A designer used to column buckling expects
length to matter and it does not.

Dimpling depends on the cell size, which is the parameter most likely to be changed late for
availability reasons, and it scales as the inverse square of it.

See Also:
---------
StiffenedPanel  : The other way to make a stability-efficient panel, with discrete stiffeners
CylindricalShell : A curved sandwich still has to be checked for shell buckling

Theory: docs/SandwichPanels.md

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
                                 marginOfSafety, InvalidInputError, GeometryError,
                                 createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                  marginOfSafety, InvalidInputError, GeometryError,
                                  createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants and Core Table -- #
# ------------------------------------------------------------------------------------------------ #

# Wrinkling coefficient in sigma = K (E_f E_c G_c)^(1/3). The theoretical value is 0.91 for an
# ideal flat facesheet; test practice uses 0.5 to 0.6 because real facesheets are not flat and
# wrinkling is imperfection sensitive in the same way shell buckling is.
WRINKLING_COEFFICIENT_THEORY   = 0.91    # [-]
WRINKLING_COEFFICIENT_PRACTICE = 0.50    # [-], the design value

# Intracell dimpling, sigma = K E_f (t_f / s)^2 / (1 - nu^2), with s the cell inscribed diameter.
DIMPLING_COEFFICIENT = 2.0    # [-]

# Below this facesheet-thickness-to-core-depth ratio the thin-facesheet approximation holds, and the
# facesheet bending stiffness about its own axis can be neglected against the sandwich stiffness.
THIN_FACESHEET_RATIO = 0.10    # [-]

# Honeycomb and foam cores. Moduli are ribbon-direction (L) values for honeycomb, which is the
# stiffer of the two shear directions; W-direction shear modulus is roughly half.
CORE_TYPES = {
    'aluminium honeycomb 3.1 pcf': {'density': 49.7,  'compressiveModulus': 310.0e6,
                                    'shearModulusL': 310.0e6, 'shearStrengthL': 1.55e6,
                                    'cellSize': 0.00476,
                                    'note': '3/16 in cell, the common lightweight core'},
    'aluminium honeycomb 4.5 pcf': {'density': 72.1,  'compressiveModulus': 655.0e6,
                                    'shearModulusL': 448.0e6, 'shearStrengthL': 2.24e6,
                                    'cellSize': 0.00476,
                                    'note': 'the general purpose structural core'},
    'aluminium honeycomb 8.1 pcf': {'density': 130.0, 'compressiveModulus': 1520.0e6,
                                    'shearModulusL': 924.0e6, 'shearStrengthL': 4.83e6,
                                    'cellSize': 0.00318,
                                    'note': '1/8 in cell, for high load and thin facesheets'},
    'nomex honeycomb 3.0 pcf':     {'density': 48.1,  'compressiveModulus': 138.0e6,
                                    'shearModulusL': 44.0e6,  'shearStrengthL': 1.24e6,
                                    'cellSize': 0.00476,
                                    'note': 'non-metallic, radar transparent, lower modulus'},
    'rohacell foam 51':            {'density': 52.0,  'compressiveModulus': 70.0e6,
                                    'shearModulusL': 19.0e6,  'shearStrengthL': 0.80e6,
                                    'cellSize': np.nan,
                                    'note': 'closed cell foam, isotropic, no dimpling mode'},
}

# ------------------------------------------------------------------------------------------------ #
# -- SandwichPanel -- #
# ------------------------------------------------------------------------------------------------ #

class SandwichPanel:

    '''

    Sandwich panel sizing and failure mode screening.

    Usage:
    ------
        panel = SandwichPanel()
        panel.setInputs({'faceMaterial': '6061-T6', 'faceThickness': 0.0005,
                         'coreType': 'aluminium honeycomb 4.5 pcf', 'coreDepth': 0.025,
                         'panelLength': 0.8, 'panelWidth': 0.5, 'appliedMoment': 500.0})
        result = panel.screenFailureModes()

    '''

    def __init__(self):

        # -- Facesheets -- #

        self.faceMaterial    = '6061-T6'
        self.condition       = None      # [-], temper key into the materials database
        self.basis           = 'typical' # [-]
        self.temperature     = 293.15    # [K]
        self.faceThickness   = np.nan    # [m], each facesheet, assumed equal
        self.faceModulus     = np.nan    # [Pa], overrides the lookup
        self.faceYield       = np.nan    # [Pa], overrides the lookup
        self.faceDensity     = np.nan    # [kg/m^3], overrides the lookup
        self.poisson         = 0.33      # [-]

        # -- Core -- #

        self.coreType        = 'aluminium honeycomb 4.5 pcf'  # key into CORE_TYPES
        self.coreDepth       = np.nan    # [m], facesheet inner surface to inner surface
        self.cellSize        = np.nan    # [m], overrides the core table

        # -- Panel and Loading -- #

        self.panelLength     = np.nan    # [m]
        self.panelWidth      = np.nan    # [m]
        self.appliedMoment   = 0.0       # [N*m/m], bending moment per unit width
        self.appliedShear    = 0.0       # [N/m], shear flow
        self.appliedCompression = 0.0    # [N/m], in-plane compression per unit width

        # -- Factors -- #

        self.factorOfSafety  = 1.4       # [-]
        self.wrinklingCoefficient = WRINKLING_COEFFICIENT_PRACTICE  # [-]

        # -- Results -- #

        self.findings        = []        # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: faceThickness, coreDepth.

        '''

        requiredParams = {'faceThickness': (int, float),
                          'coreDepth':     (int, float)}

        optionalParams = {'faceMaterial':        str,
                          'condition':           str,
                          'basis':               str,
                          'temperature':         (int, float),
                          'faceModulus':         (int, float),
                          'faceYield':           (int, float),
                          'faceDensity':         (int, float),
                          'poisson':             (int, float),
                          'coreType':            str,
                          'cellSize':            (int, float),
                          'panelLength':         (int, float),
                          'panelWidth':          (int, float),
                          'appliedMoment':       (int, float),
                          'appliedShear':        (int, float),
                          'appliedCompression':  (int, float),
                          'factorOfSafety':      (int, float),
                          'wrinklingCoefficient': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        properties = structuralAllowables(self.faceMaterial, self.condition,
                                          temperature = self.temperature, basis = self.basis)

        if not np.isfinite(self.faceModulus):
            self.faceModulus = properties['elasticModulus']
        if not np.isfinite(self.faceYield):
            self.faceYield = properties['yieldStrength']
        if not np.isfinite(self.faceDensity):
            self.faceDensity = properties['density']

    # -------------------------------------------------------------------------------------------- #

    @property
    def core(self) -> dict:

        '''
        The selected core's properties.
        '''

        if self.coreType not in CORE_TYPES:
            raise InvalidInputError(f'Unknown core \'{self.coreType}\'. Known: {sorted(CORE_TYPES)}.',
                                    context = createErrorContext(component = 'SandwichPanel'))

        return CORE_TYPES[self.coreType]

    @property
    def separation(self) -> float:

        '''
        Distance between facesheet centroids, d = coreDepth + faceThickness. This, not the core
        depth, is the lever arm that carries the bending.
        '''

        return self.coreDepth + self.faceThickness

    # -------------------------------------------------------------------------------------------- #

    def calculateSectionProperties(self) -> dict:

        '''

        Flexural rigidity, shear rigidity and areal mass, per unit width.

        The thin-facesheet form is used: D = E_f t_f d^2 / 2, which neglects the facesheets bending
        about their own axes. That term is under a percent while t_f/d is small, and this reports
        the ratio so the assumption can be checked rather than assumed.

        '''

        self._validateInputs()

        core = self.core

        # per unit width
        flexuralRigidity = self.faceModulus * self.faceThickness * self.separation ** 2 / 2.0
        ownAxisTerm      = self.faceModulus * self.faceThickness ** 3 / 6.0
        shearRigidity    = core['shearModulusL'] * self.separation ** 2 / self.coreDepth

        arealMass = (2.0 * self.faceThickness * self.faceDensity
                     + self.coreDepth * core['density'])

        # the equivalent solid plate of the same areal mass, for the stiffness comparison
        solidThickness = arealMass / self.faceDensity
        solidRigidity  = (self.faceModulus * solidThickness ** 3
                          / (12.0 * (1.0 - self.poisson ** 2)))

        return {'separation':          self.separation,
                'flexuralRigidity':    flexuralRigidity,
                'facesheetOwnAxisTerm': ownAxisTerm,
                'ownAxisFraction':     ownAxisTerm / flexuralRigidity,
                'shearRigidity':       shearRigidity,
                'arealMass':           arealMass,
                'equivalentSolidThickness': solidThickness,
                'stiffnessAdvantage':  flexuralRigidity / solidRigidity,
                'faceThicknessRatio':  self.faceThickness / self.coreDepth}

    # -------------------------------------------------------------------------------------------- #

    def calculateFacesheetStress(self) -> dict:

        '''

        Facesheet membrane stress from bending and in-plane compression.

        The facesheets act as a force couple, so the bending stress is M / (t_f d) rather than the
        My/I of a solid section.

        '''

        self._validateInputs()

        bendingStress     = (abs(self.appliedMoment) / (self.faceThickness * self.separation)
                             if self.separation > 0.0 else np.nan)
        compressionStress = abs(self.appliedCompression) / (2.0 * self.faceThickness)

        return {'bendingStress':      bendingStress,
                'compressionStress':  compressionStress,
                'totalStress':        bendingStress + compressionStress,
                'yieldStrength':      self.faceYield}

    # -------------------------------------------------------------------------------------------- #

    def calculateWrinkling(self) -> dict:

        '''

        Facesheet wrinkling, the short-wavelength buckle into the core.

            sigma_wr = K (E_f E_c G_c)^(1/3)

        Independent of panel length and boundary conditions, which is the property that surprises
        people. A designer used to column buckling expects a longer panel to be weaker and it is
        not: wrinkling is a local instability set by the facesheet and core moduli alone.

        '''

        self._validateInputs()

        core = self.core

        allowable = (self.wrinklingCoefficient
                     * (self.faceModulus * core['compressiveModulus']
                        * core['shearModulusL']) ** (1.0 / 3.0))

        applied = self.calculateFacesheetStress()['totalStress']

        return {'wrinklingStress':   allowable,
                'coefficientUsed':   self.wrinklingCoefficient,
                'theoreticalStress': (WRINKLING_COEFFICIENT_THEORY
                                      * (self.faceModulus * core['compressiveModulus']
                                         * core['shearModulusL']) ** (1.0 / 3.0)),
                'appliedStress':     applied,
                'lengthIndependent': True,
                'margin':            marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateDimpling(self) -> dict:

        '''

        Intracell dimpling, the facesheet dipping into a single honeycomb cell.

            sigma_d = K E_f (t_f / s)^2 / (1 - nu^2)

        Scales as the inverse square of the cell size, which makes it the mode most sensitive to a
        late core substitution. Foam cores have no cells and therefore no dimpling mode.

        '''

        self._validateInputs()

        core     = self.core
        cellSize = self.cellSize if np.isfinite(self.cellSize) else core['cellSize']

        if not np.isfinite(cellSize):
            return {'applicable': False,
                    'reason': f'{self.coreType} has no cells, so there is no dimpling mode.',
                    'dimplingStress': np.inf, 'margin': np.inf, 'cellSize': np.nan}

        allowable = (DIMPLING_COEFFICIENT * self.faceModulus
                     * (self.faceThickness / cellSize) ** 2 / (1.0 - self.poisson ** 2))

        applied = self.calculateFacesheetStress()['totalStress']

        return {'applicable':     True,
                'cellSize':       cellSize,
                'dimplingStress': allowable,
                'appliedStress':  applied,
                'margin':         marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateShearCrimping(self) -> dict:

        '''

        Shear crimping, a wrinkle whose wavelength is comparable to the core depth.

            sigma_cr = G_c d^2 / (2 t_f h_c)

        Governs when the core shear modulus is low, which is why foam cored panels crimp where
        honeycomb ones wrinkle.

        '''

        self._validateInputs()

        core = self.core

        allowable = (core['shearModulusL'] * self.separation ** 2
                     / (2.0 * self.faceThickness * self.coreDepth))

        applied = self.calculateFacesheetStress()['totalStress']

        return {'crimpingStress': allowable,
                'appliedStress':  applied,
                'margin':         marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateCoreShear(self) -> dict:

        '''

        Core shear stress and margin.

        The core carries essentially all the transverse shear, distributed over the separation
        rather than the core depth, because the shear flows between the facesheet centroids.

        '''

        self._validateInputs()

        core = self.core

        applied = abs(self.appliedShear) / self.separation if self.separation > 0.0 else np.nan

        return {'coreShearStress':    applied,
                'coreShearStrength':  core['shearStrengthL'],
                'coreShearModulus':   core['shearModulusL'],
                'margin':             marginOfSafety(core['shearStrengthL'], applied,
                                                     self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def screenFailureModes(self) -> dict:

        '''

        Every mode at once, with the governing one identified.

        This is the point of the class. A sandwich panel has five competing failure modes and the
        governing one moves with the geometry, so checking the mode you expect to govern is not a
        design process.

        '''

        self._validateInputs()

        stresses  = self.calculateFacesheetStress()
        wrinkling = self.calculateWrinkling()
        dimpling  = self.calculateDimpling()
        crimping  = self.calculateShearCrimping()
        coreShear = self.calculateCoreShear()

        modes = {
            'facesheet yield': marginOfSafety(self.faceYield, stresses['totalStress'],
                                              self.factorOfSafety),
            'wrinkling':       wrinkling['margin'],
            'crimping':        crimping['margin'],
            'core shear':      coreShear['margin'],
        }
        if dimpling['applicable']:
            modes['dimpling'] = dimpling['margin']

        governing = min(modes, key = modes.get)

        self.findings = []

        self.findings.append(
            f'The governing mode is {governing} at a margin of {modes[governing]:+.3f}.')

        if governing != 'facesheet yield':
            self.findings.append(
                f'A facesheet stress check alone would miss this: yield has a margin of '
                f'{modes["facesheet yield"]:+.3f} while {governing} has '
                f'{modes[governing]:+.3f}.')

        if dimpling['applicable'] and modes.get('dimpling', np.inf) < 0.5:
            self.findings.append(
                f'Dimpling is close at a {dimpling["cellSize"] * 1000.0:.2f} mm cell. It scales as '
                f'the inverse square of cell size, so a core substitution to a larger cell would '
                f'make it govern.')

        section = self.calculateSectionProperties()
        if section['faceThicknessRatio'] > THIN_FACESHEET_RATIO:
            self.findings.append(
                f'Facesheet to core depth ratio is {section["faceThicknessRatio"]:.3f}, above '
                f'{THIN_FACESHEET_RATIO:.2f}. The thin-facesheet rigidity form is losing accuracy.')

        return {'margins':          modes,
                'governingMode':    governing,
                'governingMargin':  modes[governing],
                'acceptable':       bool(modes[governing] >= 0.0),
                'stiffnessAdvantage': section['stiffnessAdvantage'],
                'arealMass':        section['arealMass'],
                'findings':         self.findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the panel and its governing mode.
        '''

        screen  = self.screenFailureModes()
        section = self.calculateSectionProperties()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  SANDWICH PANEL: {self.faceMaterial} facesheets, {self.coreType}')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Facesheet thickness', f'{self.faceThickness * 1000.0:.3f}', 'mm'],
                ['Core depth',          f'{self.coreDepth * 1000.0:.2f}', 'mm'],
                ['Separation d',        f'{section["separation"] * 1000.0:.2f}', 'mm'],
                ['Areal mass',          f'{section["arealMass"]:.3f}', 'kg/m^2'],
                ['Stiffness advantage', f'{section["stiffnessAdvantage"]:.1f}',
                 'x solid of equal mass']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Section'))
        lines.append('')

        modeRows = [[name, f'{margin:+.3f}',
                     'GOVERNS' if name == screen['governingMode'] else '']
                    for name, margin in sorted(screen['margins'].items(),
                                               key = lambda item: item[1])]
        lines.append(formatReportTable(modeRows, ['Failure mode', 'Margin', ''],
                                       title = f'Failure modes, FS {self.factorOfSafety:.2f}'))

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
            with open(os.path.join(outputDir, 'sandwichPanel.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the section is a sandwich and not something else.
        '''

        context = createErrorContext(component = 'SandwichPanel')

        if not np.isfinite(self.faceThickness) or self.faceThickness <= 0.0:
            raise InvalidInputError('Facesheet thickness must be positive.', context = context)

        if not np.isfinite(self.coreDepth) or self.coreDepth <= 0.0:
            raise InvalidInputError('Core depth must be positive.', context = context)

        if self.coreType not in CORE_TYPES:
            raise InvalidInputError(
                f'Unknown core \'{self.coreType}\'. Known: {sorted(CORE_TYPES)}.',
                context = context)

        if self.faceThickness >= self.coreDepth:
            raise GeometryError(
                f'Facesheet thickness {self.faceThickness * 1000.0:.2f} mm is not less than the '
                f'core depth {self.coreDepth * 1000.0:.2f} mm. This is not a sandwich.',
                context = context)
