
# -- PressureVessel Class Definition -- #

'''

Membrane stresses, dome geometry, wall sizing, proof and burst, and mass for a pressurized tank.

A propellant tank is three things at once and they do not agree. It is a pressure vessel, which
wants a thick wall and a hemispherical dome. It is primary structure, which wants a thin wall it
can stabilize with pressure. It is a fluid container, which wants a shape that drains and a volume
that packs into a given vehicle length. This class sizes the first and reports where it fights the
other two.

The membrane relations are the easy part:

    hoop        sigma_h = p R / t
    longitudinal sigma_l = p R / (2 t)
    sphere      sigma    = p R / (2 t)

Hoop is twice longitudinal in a cylinder, which is why cylindrical tanks fail along a line parallel
to the axis, and why a sphere of the same radius and pressure needs half the wall. A sphere is the
lightest pressure vessel there is and it packs into a vehicle badly, which is the entire reason
launch vehicles use cylinders with domed ends.

Three wall thicknesses come out of three different requirements and the largest wins:

    burst    p_burst  = FS_burst  * p_operating,  against ultimate
    yield    p_yield  = FS_yield  * p_operating,  against yield
    proof    p_proof  = FS_proof  * p_operating,  against yield, with no permanent set

Which one governs is the useful output, and it is frequently the proof test rather than burst. A
tank sized on burst alone can yield during its own acceptance test, which is a real and recurring
failure. The same binding-constraint pattern appears in the fluidSystems helium bottle.

Dome shape is the other trade. A hemisphere is the best pressure shape and the longest. An ellipse
is shorter and develops compressive hoop stress near its equator, which on a thin dome buckles.
The 1.38 aspect ratio is where that compression first appears, and it is why sqrt(2) ellipsoidal
domes are so common: they sit just inside the limit.

See Also:
---------
CylindricalShell : The same barrel in compression, where buckling rather than pressure governs
BoltedJoint      : The Y-ring joint between dome and barrel
Pressurization   : (fluidSystems) supplies the operating pressure this sizes against

Theory: docs/PressureVesselsAndTanks.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from structuresUtils import (applyInputs, formatReportTable, structuralAllowables, marginOfSafety,
                       InvalidInputError, GeometryError, createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables, marginOfSafety,
                        InvalidInputError, GeometryError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# NASA-STD-5001 pressure vessel factors, for a metallic tank qualified by test.
BURST_FACTOR_DEFAULT = 1.50    # [-], against ultimate strength
YIELD_FACTOR_DEFAULT = 1.10    # [-], against yield strength
PROOF_FACTOR_DEFAULT = 1.25    # [-], the acceptance test, against yield with no permanent set

# Above this dome aspect ratio (a/b, equatorial radius over dome height) the hoop stress at the
# equator goes compressive and a thin dome buckles there rather than bursting.
DOME_COMPRESSION_ASPECT_RATIO = np.sqrt(2.0)    # [-], 1.4142

# Thin-wall membrane theory holds above this R/t. Below it the through-thickness stress gradient
# matters and a thick-wall (Lame) treatment is required instead.
THIN_WALL_MINIMUM_RATIO = 10.0    # [-]

# Weld lands are locally thickened, and the joint efficiency applies to the parent thickness.
DEFAULT_JOINT_EFFICIENCY = 1.00   # [-], seamless. Set from Weld for a welded tank.

DOME_TYPES = {
    'hemispherical': {'aspectRatio': 1.0,           'note': 'best pressure shape, longest'},
    'sqrt2 ellipsoidal': {'aspectRatio': np.sqrt(2.0),
                          'note': 'the common compromise, just inside the compression limit'},
    '2:1 ellipsoidal': {'aspectRatio': 2.0,
                        'note': 'short and light in the dome, compressive hoop at the equator'},
}

# ------------------------------------------------------------------------------------------------ #
# -- PressureVessel -- #
# ------------------------------------------------------------------------------------------------ #

class PressureVessel:

    '''

    Membrane pressure vessel sizing.

    Usage:
    ------
        tank = PressureVessel()
        tank.setInputs({'material': '2219-T87', 'radius': 1.0, 'cylindricalLength': 4.0,
                        'operatingPressure': 2.5e6, 'domeType': 'sqrt2 ellipsoidal'})
        result = tank.sizeWallThickness()

    '''

    def __init__(self):

        # -- Geometry -- #

        self.radius             = np.nan  # [m], internal radius
        self.cylindricalLength  = np.nan  # [m], barrel length, excluding domes
        self.domeType           = 'sqrt2 ellipsoidal'  # key into DOME_TYPES
        self.thickness          = np.nan  # [m], set to check an existing wall

        # -- Material -- #

        self.material           = '2219-T87'
        self.condition          = None    # [-], temper key into the materials database
        self.basis              = 'typical'  # [-], 'typical', 'A' or 'B'
        self.allowablesSource   = ''      # [-], which database answered
        self.temperature        = 293.15  # [K]
        self.yieldStrength      = np.nan  # [Pa], overrides the lookup
        self.ultimateStrength   = np.nan  # [Pa], overrides the lookup
        self.density            = np.nan  # [kg/m^3], overrides the lookup
        self.jointEfficiency    = DEFAULT_JOINT_EFFICIENCY  # [-]

        # -- Pressure -- #

        self.operatingPressure  = np.nan  # [Pa], maximum expected operating pressure
        self.burstFactor        = BURST_FACTOR_DEFAULT  # [-]
        self.yieldFactor        = YIELD_FACTOR_DEFAULT  # [-]
        self.proofFactor        = PROOF_FACTOR_DEFAULT  # [-]

        # -- Results -- #

        self.requiredThickness  = np.nan  # [m]
        self.bindingConstraint  = ''      # [-], which of burst, yield or proof governed
        self.findings           = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: radius, operatingPressure.

        '''

        requiredParams = {'radius':            (int, float),
                          'operatingPressure': (int, float)}

        optionalParams = {'cylindricalLength': (int, float),
                          'domeType':          str,
                          'thickness':         (int, float),
                          'material':          str,
                          'temperature':       (int, float),
                          'condition':         str,
                          'basis':             str,
                          'yieldStrength':     (int, float),
                          'ultimateStrength':  (int, float),
                          'density':           (int, float),
                          'jointEfficiency':   (int, float),
                          'burstFactor':       (int, float),
                          'yieldFactor':       (int, float),
                          'proofFactor':       (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._resolveMaterial()

    def _resolveMaterial(self) -> None:

        '''
        Fill strengths and density from the material table unless given explicitly.
        '''

        properties = structuralAllowables(self.material, self.condition,
                                      temperature = self.temperature,
                                      basis = self.basis)
        self.allowablesSource = properties['source']

        if not np.isfinite(self.yieldStrength):
            self.yieldStrength = properties['yieldStrength']
        if not np.isfinite(self.ultimateStrength):
            self.ultimateStrength = properties['ultimateStrength']
        if not np.isfinite(self.density):
            self.density = properties['density']

    # -------------------------------------------------------------------------------------------- #

    def calculateMembraneStresses(self) -> dict:

        '''

        Hoop and longitudinal membrane stress in the barrel, and the equivalent stress in a dome.

        '''

        self._validateInputs(requireThickness = True)

        hoop         = self.operatingPressure * self.radius / self.thickness
        longitudinal = hoop / 2.0
        sphere       = hoop / 2.0

        # von Mises for the biaxial membrane state, which is what the yield check should use
        vonMises = np.sqrt(hoop ** 2 - hoop * longitudinal + longitudinal ** 2)

        return {'hoopStress':          hoop,
                'longitudinalStress':  longitudinal,
                'sphericalStress':     sphere,
                'vonMisesStress':      vonMises,
                'hoopToLongitudinal':  hoop / longitudinal,
                'radiusToThickness':   self.radius / self.thickness}

    # -------------------------------------------------------------------------------------------- #

    def sizeWallThickness(self) -> dict:

        '''

        The three candidate wall thicknesses, and which requirement binds.

        Burst is checked against ultimate, yield and proof against yield. The largest wins, and
        reporting which one it was is the point: it says what to change to get the wall down.

        '''

        self._validateInputs(requireThickness = False)

        allowableUltimate = self.ultimateStrength * self.jointEfficiency
        allowableYield    = self.yieldStrength * self.jointEfficiency

        # hoop governs in a cylinder, so size on it
        candidates = {
            'burst': self.burstFactor * self.operatingPressure * self.radius / allowableUltimate,
            'yield': self.yieldFactor * self.operatingPressure * self.radius / allowableYield,
            'proof': self.proofFactor * self.operatingPressure * self.radius / allowableYield,
        }

        self.bindingConstraint = max(candidates, key = candidates.get)
        self.requiredThickness = candidates[self.bindingConstraint]
        self.findings          = []

        runnerUp = sorted(candidates.values())[-2]
        margin   = self.requiredThickness / runnerUp - 1.0

        self.findings.append(
            f'The {self.bindingConstraint} requirement governs the wall at '
            f'{self.requiredThickness * 1000.0:.3f} mm, {margin * 100.0:.1f} % above the next '
            f'requirement.')

        if self.bindingConstraint == 'proof':
            self.findings.append(
                f'The proof test governs, not burst. A wall sized on burst alone would be '
                f'{candidates["burst"] * 1000.0:.3f} mm and would yield during its own acceptance '
                f'test at {self.proofFactor:.2f} x operating pressure.')

        if self.radius / self.requiredThickness < THIN_WALL_MINIMUM_RATIO:
            self.findings.append(
                f'R/t of {self.radius / self.requiredThickness:.1f} is below '
                f'{THIN_WALL_MINIMUM_RATIO:.0f}. Membrane theory is no longer adequate and a '
                f'thick-wall treatment is needed.')

        return {'candidates':        candidates,
                'bindingConstraint': self.bindingConstraint,
                'requiredThickness': self.requiredThickness,
                'marginOverRunnerUp': margin,
                'radiusToThickness': self.radius / self.requiredThickness,
                'jointEfficiency':   self.jointEfficiency,
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateDomeGeometry(self) -> dict:

        '''

        Dome height, volume and the equatorial hoop stress sign.

        An ellipsoidal dome develops compressive hoop stress near its equator once the aspect ratio
        exceeds sqrt(2). On a thin dome that compression buckles rather than bursts, which is a
        different failure mode entirely and is not caught by a membrane stress check.

        '''

        self._validateInputs(requireThickness = False)

        if self.domeType not in DOME_TYPES:
            raise InvalidInputError(
                f'Unknown dome type \'{self.domeType}\'. Known: {sorted(DOME_TYPES)}.',
                context = createErrorContext(component = 'PressureVessel'))

        aspectRatio = DOME_TYPES[self.domeType]['aspectRatio']
        domeHeight  = self.radius / aspectRatio

        # ellipsoid of revolution, two domes
        domeVolume = (2.0 / 3.0) * np.pi * self.radius ** 2 * domeHeight

        # equatorial hoop stress factor for an ellipsoid: goes negative above sqrt(2)
        hoopFactor = 1.0 - aspectRatio ** 2 / 2.0
        compressive = hoopFactor < 0.0

        findings = []
        if compressive:
            findings.append(
                f'A {self.domeType} dome has compressive hoop stress at its equator (factor '
                f'{hoopFactor:+.3f}). Check it for buckling, not just for burst.')
        elif np.isclose(aspectRatio, DOME_COMPRESSION_ASPECT_RATIO):
            findings.append(
                'This dome sits exactly at the compression threshold, which is why the sqrt(2) '
                'ellipse is the common choice.')

        return {'domeType':            self.domeType,
                'aspectRatio':         aspectRatio,
                'domeHeight':          domeHeight,
                'domeVolumeBothEnds':  domeVolume,
                'equatorialHoopFactor': hoopFactor,
                'equatorInCompression': bool(compressive),
                'note':                DOME_TYPES[self.domeType]['note'],
                'findings':            findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateVolumeAndMass(self) -> dict:

        '''

        Enclosed volume and shell mass for the sized wall.

        '''

        self._validateInputs(requireThickness = False)

        if not np.isfinite(self.cylindricalLength):
            raise InvalidInputError('Volume needs the cylindrical length.',
                                    context = createErrorContext(component = 'PressureVessel'))

        thickness = (self.thickness if np.isfinite(self.thickness)
                     else self.sizeWallThickness()['requiredThickness'])

        dome = self.calculateDomeGeometry()

        barrelVolume = np.pi * self.radius ** 2 * self.cylindricalLength
        totalVolume  = barrelVolume + dome['domeVolumeBothEnds']

        barrelArea = 2.0 * np.pi * self.radius * self.cylindricalLength
        # ellipsoid surface approximation, adequate for a mass estimate
        domeArea   = 2.0 * (2.0 * np.pi * self.radius ** 2
                            * (1.0 + (dome['domeHeight'] / self.radius) ** 1.6) / 2.0)

        mass = (barrelArea + domeArea) * thickness * self.density

        return {'barrelVolume':   barrelVolume,
                'domeVolume':     dome['domeVolumeBothEnds'],
                'totalVolume':    totalVolume,
                'wettedArea':     barrelArea + domeArea,
                'thickness':      thickness,
                'shellMass':      mass,
                'overallLength':  self.cylindricalLength + 2.0 * dome['domeHeight'],
                'massPerVolume':  mass / totalVolume}

    # -------------------------------------------------------------------------------------------- #

    def checkMargins(self) -> dict:

        '''

        Margins at operating, proof and burst pressure for the current wall.

        '''

        self._validateInputs(requireThickness = True)

        stresses = self.calculateMembraneStresses()
        hoop     = stresses['hoopStress']

        allowableYield    = self.yieldStrength * self.jointEfficiency
        allowableUltimate = self.ultimateStrength * self.jointEfficiency

        return {'operatingHoopStress': hoop,
                'yieldMargin':  marginOfSafety(allowableYield, hoop, self.yieldFactor),
                'proofMargin':  marginOfSafety(allowableYield, hoop, self.proofFactor),
                'burstMargin':  marginOfSafety(allowableUltimate, hoop, self.burstFactor),
                'burstPressure': allowableUltimate * self.thickness / self.radius,
                'yieldPressure': allowableYield * self.thickness / self.radius}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        A readable summary of the sized tank.

        '''

        sizing = self.sizeWallThickness()
        dome   = self.calculateDomeGeometry()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  PRESSURE VESSEL: {self.material}, R = {self.radius:.3f} m, '
                     f'p = {self.operatingPressure / 1.0e6:.3f} MPa')
        lines.append('=' * 96)
        lines.append('')

        rows = [[name, f'{value * 1000.0:.3f}',
                 'GOVERNS' if name == sizing['bindingConstraint'] else '']
                for name, value in sizing['candidates'].items()]
        lines.append(formatReportTable(rows, ['Requirement', 'Thickness [mm]', ''],
                                       title = 'Wall thickness candidates'))
        lines.append('')

        domeRows = [['Dome type', self.domeType, '-'],
                    ['Aspect ratio', f'{dome["aspectRatio"]:.4f}', '-'],
                    ['Dome height', f'{dome["domeHeight"]:.3f}', 'm'],
                    ['Equatorial hoop factor', f'{dome["equatorialHoopFactor"]:+.3f}', '-']]
        lines.append(formatReportTable(domeRows, ['Quantity', 'Value', 'Unit'], title = 'Dome'))

        allFindings = self.findings + dome['findings']
        if allFindings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in allFindings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'pressureVessel.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self, requireThickness: bool = False) -> None:

        '''

        Check the geometry and pressure are physical.

        '''

        context = createErrorContext(component = 'PressureVessel')

        if not np.isfinite(self.radius) or self.radius <= 0.0:
            raise InvalidInputError('Vessel radius must be positive.', context = context)

        if not np.isfinite(self.operatingPressure) or self.operatingPressure <= 0.0:
            raise InvalidInputError('Operating pressure must be positive.', context = context)

        if not 0.0 < self.jointEfficiency <= 1.0:
            raise InvalidInputError(
                f'Joint efficiency must be in (0, 1], got {self.jointEfficiency}.',
                context = context)

        if requireThickness:
            if not np.isfinite(self.thickness) or self.thickness <= 0.0:
                raise InvalidInputError(
                    'This calculation needs an explicit thickness. Call sizeWallThickness() first '
                    'or set one.', context = context)

            if self.radius / self.thickness < THIN_WALL_MINIMUM_RATIO:
                raise GeometryError(
                    f'R/t of {self.radius / self.thickness:.1f} is below '
                    f'{THIN_WALL_MINIMUM_RATIO:.0f}, outside thin-wall membrane theory.',
                    context = context)
