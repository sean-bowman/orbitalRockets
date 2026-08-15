
# -- CylindricalShell Class Definition -- #

'''

Buckling of thin cylindrical shells: axial, bending, external pressure, torsion and combined load.

This is the class the domain is built around, because a launch vehicle is mostly thin cylinders in
compression and almost none of them fail by exceeding the material strength. A 2.5 mm 6061-T6 shell
of one metre radius yields at 276 MPa and buckles at 38, so a stress check against the allowable
passes by a factor of seven at the load that destroys it.

The classical solution overpredicts test by two to five times, and the reason is imperfection
sensitivity. A cylinder in axial compression has many buckling modes at nearly the same load, so
the smallest geometric deviation lets the shell find a lower-energy path down. Test scatter from
the 1930s onward never approached theory and never converged, which is why the design factors are
empirical lower bounds rather than corrections.

    sigma_classical = E t / (R sqrt(3 (1 - nu^2)))
    gamma           = 1 - 0.901 (1 - exp(-phi)),   phi = (1/16) sqrt(R/t)
    sigma_allowable = gamma * sigma_classical

Three things make the picture less bleak than that:

    internal pressure   stabilizes the shell and recovers a large part of the knockdown
    stiffening          moves the failure mode away from the imperfection-sensitive one
    knowing the shape   a measured imperfection field supports a far less punitive factor

The first is why a pressure-stabilized tank is efficient, and it is modelled here with a saturating
curve that is NOT the one SP-8007 gives. The document's Figure 4-5 is a figure, and reading values
off it would be worse provenance than saying so. The second is StiffenedPanel's subject. The third
is modern practice at the large end, needs a measured shell, and is out of scope for preliminary
sizing.

**The correlation has two stated bounds and both are enforced or reported here.** It applies below
r/t = 1500, which is a refusal, and it has not been verified by experiment above L/r = 5, which is
reported alongside the factor. A long shell also has to be checked as a column, because the
classical prediction the knockdown multiplies cannot see column buckling and becomes unconservative
in exactly that regime.

Bending is less imperfection sensitive than uniform compression, because only part of the
circumference is highly loaded and the peak stress region is short. Torsion and external pressure
are far less sensitive again: their buckling modes are well separated, so theory is close to test
and the knockdowns are mild.

See Also:
---------
PressureVessel : The same shell sized for internal pressure, where strength does govern
StiffenedPanel : What to do when the unstiffened shell is too heavy
BeamColumn     : Global buckling of the whole vehicle as a column

Theory: docs/ShellBuckling.md

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
                       classicalShellBucklingStress, sp8007Knockdown,
                       InvalidInputError, GeometryError, BucklingError, createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables, marginOfSafety,
                        classicalShellBucklingStress, sp8007Knockdown,
                        InvalidInputError, GeometryError, BucklingError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Below this R/t the shell is thick enough that thin-shell theory misleads and the failure mode
# drifts toward crushing. Above it, and up to a few thousand, the correlations here apply.
THIN_SHELL_MINIMUM_RATIO = 20.0     # [-]

# SP-8007 Rev 2 states the axial knockdown parameter as phi = (1/16) sqrt(r/t) FOR r/t < 1500. That
# bound is part of the correlation and not a convention, so a shell above it gets a refusal rather
# than an extrapolated factor.
THIN_SHELL_MAXIMUM_RATIO = 1500.0   # [-], SP-8007 Rev 2 Eq. 10

# The same section cautions that the axial knockdown "should be used with caution for cylinders
# with ratios of L/r > 5 since correlation has not been verified by experiment in this range", and
# separately that the Donnell prediction becomes UNCONSERVATIVE at large L/r because it cannot see
# the interaction between shell buckling and column buckling.
#
# Reported rather than refused, because the length is optional for an axial check and a caution is
# not a prohibition. A shell past it should be checked as a column as well, which BeamColumn does.
LENGTH_TO_RADIUS_CORRELATED = 5.0   # [-], SP-8007 Rev 2 section 4.1.1.1

# Bending is less imperfection sensitive than uniform axial compression. NASA SP-8007 allows the
# axial knockdown to be relaxed by this factor for pure bending, capped at 1.0.
BENDING_KNOCKDOWN_RELIEF = 1.30     # [-]

# Torsion. SP-8007 Rev 2 Eq. 34 carries the correlation as gamma^(3/4) inside the critical shear
# stress expression rather than as gamma, and Eq. 35 recommends 0.67 for that group as a lower
# bound to the test data for moderately long cylinders. It is applied here to the same classical
# expression the document writes, so it multiplies the stress directly.
TORSION_CORRELATION = 0.67          # [-], this is gamma^(3/4), SP-8007 Rev 2 Eq. 35

# External pressure, and the two branches carry different factors because they buckle differently.
#
# A long cylinder collapses into a two-lobe oval, theory and test are close, and Rev 2 Eq. 29
# recommends 0.90. A shorter one buckles into more circumferential waves, where the test scatter is
# far wider and the end restraint of the specimen was often not accounted for, and Rev 2 Eq. 28
# recommends sqrt(gamma) = 0.75, so gamma = 0.5625.
#
# **These differ by a factor of 1.6 and the short branch is the punishing one.** Applying the long
# cylinder factor to a short shell is unconservative by exactly that much.
EXTERNAL_PRESSURE_KNOCKDOWN_LONG  = 0.90    # [-], SP-8007 Rev 2 Eq. 29, oval mode
EXTERNAL_PRESSURE_KNOCKDOWN_SHORT = 0.5625  # [-], SP-8007 Rev 2 Eq. 28

# The interaction exponents for combined loading, per SP-8007. Axial and bending add linearly
# because they are the same stress; pressure and torsion enter quadratically.
COMBINED_AXIAL_EXPONENT   = 1.0     # [-]
COMBINED_SHEAR_EXPONENT   = 2.0     # [-]

# Internal pressure stabilization saturates: past this non-dimensional pressure the shell has
# recovered essentially all of the knockdown and more pressure buys nothing further.
#
# **This saturating model is NOT SP-8007's.** The document gives the pressurized capability as
# P = 2 pi E t^2 (0.605 gamma + d_gamma) + p pi r^2, with d_gamma read from its Figure 4-5 against
# the same non-dimensional pressure used here. The PARAMETER is the document's; the curve is a
# saturating interpolation with the right shape and no published points behind it, because Figure
# 4-5 is a figure and reading values off it would be a worse provenance than saying so. Registered
# as unvalidated, and the document's own warning applies: applying a recovery of this kind on top
# of a knockdown can produce an unconservative design.
PRESSURE_STABILIZATION_CAP = 1.0    # [-], on the parameter p (R/t)^2 / E

# ------------------------------------------------------------------------------------------------ #
# -- CylindricalShell -- #
# ------------------------------------------------------------------------------------------------ #

class CylindricalShell:

    '''

    Thin cylindrical shell buckling.

    Usage:
    ------
        shell = CylindricalShell()
        shell.setInputs({'material': '6061-T6', 'radius': 1.0, 'thickness': 0.0025,
                         'length': 3.0, 'axialLoad': 200.0e3})
        result = shell.calculateAxialBuckling()

    '''

    def __init__(self):

        # -- Geometry -- #

        self.radius            = np.nan  # [m], mid-surface radius
        self.thickness         = np.nan  # [m], wall thickness
        self.length            = np.nan  # [m], unsupported length between rings

        # -- Material -- #

        self.material          = '6061-T6'  # key into materialProperties
        self.condition         = None    # [-], temper key into the materials database
        self.basis             = 'typical'  # [-], 'typical', 'A' or 'B'
        self.allowablesSource  = ''      # [-], which database answered
        self.temperature       = 293.15  # [K]
        self.modulus           = np.nan  # [Pa], overrides the material lookup if set
        self.poisson           = 0.33    # [-]
        self.yieldStrength     = np.nan  # [Pa], overrides the material lookup if set

        # -- Applied Loading -- #

        self.axialLoad         = 0.0     # [N], compression positive
        self.bendingMoment     = 0.0     # [N*m]
        self.torsion           = 0.0     # [N*m]
        self.externalPressure  = 0.0     # [Pa], net crushing pressure
        self.internalPressure  = 0.0     # [Pa], stabilizing

        # -- Factors -- #

        self.factorOfSafety    = 1.4     # [-], ultimate, per NASA-STD-5001
        self.knockdownOverride = np.nan  # [-], set to bypass SP-8007 with a test-derived value

        # -- Results -- #

        self.classicalStress   = np.nan  # [Pa]
        self.knockdown         = np.nan  # [-]
        self.allowableStress   = np.nan  # [Pa]
        self.appliedStress     = np.nan  # [Pa]
        self.margin            = np.nan  # [-]
        self.findings          = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: radius, thickness.

        '''

        requiredParams = {'radius':    (int, float),
                          'thickness': (int, float)}

        optionalParams = {'length':            (int, float),
                          'material':          str,
                          'temperature':       (int, float),
                          'condition':         str,
                          'basis':             str,
                          'modulus':           (int, float),
                          'poisson':           (int, float),
                          'yieldStrength':     (int, float),
                          'axialLoad':         (int, float),
                          'bendingMoment':     (int, float),
                          'torsion':           (int, float),
                          'externalPressure':  (int, float),
                          'internalPressure':  (int, float),
                          'factorOfSafety':    (int, float),
                          'knockdownOverride': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._resolveMaterial()

    def _resolveMaterial(self) -> None:

        '''

        Fill the elastic properties from the material table unless they were given explicitly.

        '''

        if np.isfinite(self.modulus) and np.isfinite(self.yieldStrength):
            return

        properties = structuralAllowables(self.material, self.condition,
                                      temperature = self.temperature,
                                      basis = self.basis)
        self.allowablesSource = properties['source']

        if not np.isfinite(self.modulus):
            self.modulus = properties['elasticModulus']
        if not np.isfinite(self.yieldStrength):
            self.yieldStrength = properties['yieldStrength']

    # -------------------------------------------------------------------------------------------- #

    @property
    def radiusToThickness(self) -> float:

        '''
        R/t, the parameter that governs how imperfection sensitive the shell is.
        '''

        return self.radius / self.thickness

    @property
    def batdorfParameter(self) -> float:

        '''

        Z = L^2 sqrt(1 - nu^2) / (R t).

        Separates short shells, where the boundary conditions carry the load and buckling is
        plate-like, from long ones where the classical cylinder solution applies. Below Z of
        about 10 the shell is short; above a few hundred it is long.

        '''

        if not np.isfinite(self.length):
            return np.nan

        return self.length ** 2 * np.sqrt(1.0 - self.poisson ** 2) / (self.radius * self.thickness)

    # -------------------------------------------------------------------------------------------- #

    def calculateKnockdown(self) -> dict:

        '''

        The SP-8007 axial knockdown, plus whatever internal pressure recovers.

        Internal pressure stabilizes a shell by pretensioning it, which suppresses the inward
        buckling lobes the imperfections would otherwise trigger. The recovery is real and large:
        a pressurized tank skin can approach the classical value.

        '''

        self._validateInputs()

        base = sp8007Knockdown(self.radiusToThickness)

        # non-dimensional internal pressure, the parameter the SP-8007 stabilization curve uses
        pressureParameter = 0.0
        recovery          = 0.0

        if self.internalPressure > 0.0:
            pressureParameter = (self.internalPressure / self.modulus
                                 * self.radiusToThickness ** 2)
            capped = min(pressureParameter, PRESSURE_STABILIZATION_CAP)
            # recovery of the lost fraction, saturating at the cap
            recovery = (1.0 - base) * (capped / PRESSURE_STABILIZATION_CAP)

        knockdown = min(base + recovery, 1.0)

        if np.isfinite(self.knockdownOverride):
            knockdown = float(self.knockdownOverride)

        self.knockdown = knockdown

        # Where this shell sits against the range the correlation was verified over. A long shell
        # is not refused, because the caution is about the experimental basis rather than about the
        # arithmetic, and because the Donnell prediction it multiplies has its own separate problem
        # at large L/r: it cannot see column buckling.
        lengthToRadius = (self.length / self.radius if np.isfinite(self.length)
                          else np.nan)

        beyondCorrelated = bool(np.isfinite(lengthToRadius)
                                and lengthToRadius > LENGTH_TO_RADIUS_CORRELATED)

        return {'radiusToThickness':  self.radiusToThickness,
                'sp8007Knockdown':    base,
                'pressureParameter':  pressureParameter,
                'pressureRecovery':   recovery,
                'knockdown':          knockdown,
                'penaltyFactor':      1.0 / knockdown,
                'lengthToRadius':     lengthToRadius,
                'beyondCorrelatedLength': beyondCorrelated,
                'overridden':         bool(np.isfinite(self.knockdownOverride))}

    # -------------------------------------------------------------------------------------------- #

    def calculateAxialBuckling(self) -> dict:

        '''

        Axial compression buckling, the governing case for most vehicle barrel sections.

        '''

        self._validateInputs()

        knockdownResult = self.calculateKnockdown()

        self.classicalStress = classicalShellBucklingStress(self.modulus, self.thickness,
                                                            self.radius, self.poisson)
        self.allowableStress = self.knockdown * self.classicalStress

        area               = 2.0 * np.pi * self.radius * self.thickness
        self.appliedStress = self.axialLoad / area if area > 0.0 else np.nan

        self.margin   = marginOfSafety(self.allowableStress, self.appliedStress,
                                       self.factorOfSafety)
        self.findings = []

        # the observation the whole domain turns on
        yieldRatio = self.yieldStrength / self.allowableStress
        if yieldRatio > 1.0:
            self.findings.append(
                f'Buckling governs by {yieldRatio:.1f}x. The shell yields at '
                f'{self.yieldStrength / 1.0e6:.0f} MPa and buckles at '
                f'{self.allowableStress / 1.0e6:.0f} MPa, so a stress check against the material '
                f'allowable says nothing about this shell.')

        self.findings.append(
            f'The empirical knockdown is {self.knockdown:.3f}, so the classical solution is '
            f'{knockdownResult["penaltyFactor"]:.2f}x optimistic.')

        if self.internalPressure > 0.0 and knockdownResult['pressureRecovery'] > 0.0:
            self.findings.append(
                f'Internal pressure recovers {knockdownResult["pressureRecovery"]:.3f} of the '
                f'knockdown. Any analysis crediting this must also show the pressure cannot be '
                f'lost while the compressive load is applied.')

        if self.margin < 0.0:
            self.findings.append(
                f'Negative margin at FS {self.factorOfSafety:.2f}. Required thickness is about '
                f'{self.sizeThicknessForAxialLoad()["thickness"] * 1000.0:.2f} mm.')

        return {'classicalStress':  self.classicalStress,
                'knockdown':        self.knockdown,
                'allowableStress':  self.allowableStress,
                'appliedStress':    self.appliedStress,
                'yieldStrength':    self.yieldStrength,
                'bucklingGoverns':  bool(self.allowableStress < self.yieldStrength),
                'governingRatio':   yieldRatio,
                'margin':           self.margin,
                'findings':         self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateBendingBuckling(self) -> dict:

        '''

        Buckling under pure bending.

        Less imperfection sensitive than uniform compression, because the peak stress acts over a
        short arc of the circumference and the shell can shed load around it.

        '''

        self._validateInputs()

        self.calculateKnockdown()

        knockdown = min(self.knockdown * BENDING_KNOCKDOWN_RELIEF, 1.0)
        classical = classicalShellBucklingStress(self.modulus, self.thickness,
                                                 self.radius, self.poisson)
        allowable = knockdown * classical

        sectionModulus = np.pi * self.radius ** 2 * self.thickness
        applied        = abs(self.bendingMoment) / sectionModulus if sectionModulus > 0.0 else np.nan

        return {'classicalStress': classical,
                'knockdown':       knockdown,
                'reliefApplied':   BENDING_KNOCKDOWN_RELIEF,
                'allowableStress': allowable,
                'appliedStress':   applied,
                'sectionModulus':  sectionModulus,
                'margin':          marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateExternalPressureBuckling(self) -> dict:

        '''

        Collapse under external pressure, the vacuum jacket and the drained tank case.

        Long shells collapse into two lobes at a pressure independent of length; short ones are
        held up by their end rings and are much stronger. The transition is at a length of roughly
        1.14 R sqrt(R/t).

        '''

        self._validateInputs()

        if not np.isfinite(self.length):
            raise InvalidInputError(
                'External pressure buckling needs the unsupported length.',
                context = createErrorContext(component = 'CylindricalShell'))

        # long-shell (two lobe) collapse, the classical Bresse result
        longShellPressure = (self.modulus / (4.0 * (1.0 - self.poisson ** 2))
                             * (self.thickness / self.radius) ** 3)

        # short-shell collapse, where the end restraint carries load. Von Mises approximation.
        shortShellPressure = (0.92 * self.modulus
                              / ((self.length / (2.0 * self.radius))
                                 * self.radiusToThickness ** 2.5))

        transitionLength = 1.14 * self.radius * np.sqrt(self.radiusToThickness)
        isLongShell      = self.length >= transitionLength

        classical = longShellPressure if isLongShell else max(shortShellPressure,
                                                              longShellPressure)

        # The branch decides the factor as well as the classical pressure. A short shell buckles
        # into more circumferential waves and its test scatter is far wider, which is the 1.6 the
        # two factors differ by.
        knockdown = (EXTERNAL_PRESSURE_KNOCKDOWN_LONG if isLongShell
                     else EXTERNAL_PRESSURE_KNOCKDOWN_SHORT)

        allowable = knockdown * classical

        return {'longShellPressure':  longShellPressure,
                'shortShellPressure': shortShellPressure,
                'transitionLength':   transitionLength,
                'isLongShell':        bool(isLongShell),
                'classicalPressure':  classical,
                'knockdown':          knockdown,
                'allowablePressure':  allowable,
                'appliedPressure':    self.externalPressure,
                'margin':             marginOfSafety(allowable, self.externalPressure,
                                                     self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateTorsionalBuckling(self) -> dict:

        '''

        Torsional buckling, which produces the diagonal wrinkle pattern.

        Well separated modes mean theory is close to test, so the knockdown is mild.

        '''

        self._validateInputs()

        if not np.isfinite(self.length):
            raise InvalidInputError('Torsional buckling needs the unsupported length.',
                                    context = createErrorContext(component = 'CylindricalShell'))

        # Donnell long-shell torsional buckling
        classical = (0.747 * self.modulus * (self.thickness / self.radius) ** 1.25
                     * (self.radius / self.length) ** 0.5
                     / (1.0 - self.poisson ** 2) ** 0.625)

        allowable = TORSION_CORRELATION * classical

        polarModulus = 2.0 * np.pi * self.radius ** 2 * self.thickness
        applied      = abs(self.torsion) / polarModulus if polarModulus > 0.0 else np.nan

        return {'classicalShearStress': classical,
                'knockdown':            TORSION_CORRELATION,
                'allowableShearStress': allowable,
                'appliedShearStress':   applied,
                'margin':               marginOfSafety(allowable, applied, self.factorOfSafety)}

    # -------------------------------------------------------------------------------------------- #

    def calculateCombinedLoading(self) -> dict:

        '''

        Interaction under simultaneous axial, bending and torsional load.

            R_axial + R_bending + R_shear^2 <= 1

        Axial and bending add linearly because they produce the same membrane stress. Shear enters
        quadratically. The governing case for a vehicle is almost never one load alone, and a
        structure checked one load at a time can pass every check and fail the combination.

        '''

        self._validateInputs()

        axial   = self.calculateAxialBuckling()
        bending = self.calculateBendingBuckling()
        shear   = self.calculateTorsionalBuckling() if np.isfinite(self.length) else None

        ratioAxial   = (abs(axial['appliedStress']) * self.factorOfSafety
                        / axial['allowableStress']) if axial['allowableStress'] > 0.0 else 0.0
        ratioBending = (abs(bending['appliedStress']) * self.factorOfSafety
                        / bending['allowableStress']) if bending['allowableStress'] > 0.0 else 0.0
        ratioShear   = 0.0
        if shear is not None and shear['allowableShearStress'] > 0.0:
            ratioShear = (abs(shear['appliedShearStress']) * self.factorOfSafety
                          / shear['allowableShearStress'])

        interaction = (ratioAxial ** COMBINED_AXIAL_EXPONENT
                       + ratioBending ** COMBINED_AXIAL_EXPONENT
                       + ratioShear ** COMBINED_SHEAR_EXPONENT)

        findings = []
        if interaction > 1.0:
            findings.append(
                f'The interaction sum is {interaction:.3f}, above 1.0, so the shell fails under '
                f'the combination even where each load alone may pass.')

        worstAlone = max(ratioAxial, ratioBending, ratioShear)
        if worstAlone <= 1.0 < interaction:
            findings.append(
                f'Every load checked alone passes (worst is {worstAlone:.3f}) and the combination '
                f'does not. This is why load cases are combined rather than enveloped.')

        return {'ratioAxial':      ratioAxial,
                'ratioBending':    ratioBending,
                'ratioShear':      ratioShear,
                'interaction':     interaction,
                'acceptable':      bool(interaction <= 1.0),
                'marginOnLoad':    1.0 / interaction - 1.0 if interaction > 0.0 else np.inf,
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeThicknessForAxialLoad(self, targetMargin: float = 0.0) -> dict:

        '''

        Solve for the thickness that carries the applied axial load at the target margin.

        Iterative, because the knockdown depends on R/t which depends on the thickness. Converges
        in a handful of passes from any sensible start.

        '''

        self._validateInputs()

        if self.axialLoad <= 0.0:
            raise InvalidInputError('Sizing needs a positive compressive axial load.',
                                    context = createErrorContext(component = 'CylindricalShell'))

        required = 1.0 + targetMargin
        thickness = self.thickness if np.isfinite(self.thickness) else self.radius / 500.0

        for iteration in range(60):

            knockdown = sp8007Knockdown(self.radius / thickness)
            classical = classicalShellBucklingStress(self.modulus, thickness,
                                                     self.radius, self.poisson)
            allowable = knockdown * classical
            applied   = self.axialLoad / (2.0 * np.pi * self.radius * thickness)

            error = applied * self.factorOfSafety * required / allowable

            if abs(error - 1.0) < 1.0e-8:
                break

            # allowable grows faster than linearly with thickness, so damp the update
            thickness *= error ** 0.6

        else:
            raise BucklingError(
                'Thickness sizing did not converge in 60 iterations.',
                context = createErrorContext(component = 'CylindricalShell'))

        return {'thickness':         thickness,
                'iterations':        iteration + 1,
                'radiusToThickness': self.radius / thickness,
                'knockdown':         sp8007Knockdown(self.radius / thickness),
                'allowableStress':   allowable,
                'appliedStress':     applied,
                'shellMass':         (2.0 * np.pi * self.radius * thickness * self.length
                                      * structuralAllowables(self.material, self.condition,
                                                            temperature = self.temperature)['density']
                                      if np.isfinite(self.length) else np.nan)}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        A readable summary of the shell and its governing failure mode.

        '''

        axial = self.calculateAxialBuckling()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  CYLINDRICAL SHELL: {self.material}, R = {self.radius:.3f} m, '
                     f't = {self.thickness * 1000.0:.2f} mm')
        lines.append('=' * 96)
        lines.append('')

        geometry = [['Radius / thickness', f'{self.radiusToThickness:.1f}', '-'],
                    ['Batdorf parameter Z', f'{self.batdorfParameter:.1f}'
                     if np.isfinite(self.batdorfParameter) else 'n/a', '-']]
        lines.append(formatReportTable(geometry, ['Quantity', 'Value', 'Unit'],
                                       title = 'Geometry'))
        lines.append('')

        stresses = [['Classical buckling', f'{axial["classicalStress"] / 1.0e6:.1f}', 'MPa'],
                    ['Knockdown factor',   f'{axial["knockdown"]:.4f}', '-'],
                    ['Allowable buckling', f'{axial["allowableStress"] / 1.0e6:.1f}', 'MPa'],
                    ['Material yield',     f'{self.yieldStrength / 1.0e6:.1f}', 'MPa'],
                    ['Applied',            f'{axial["appliedStress"] / 1.0e6:.1f}', 'MPa'],
                    ['Margin of safety',   f'{axial["margin"]:+.3f}', '-']]
        lines.append(formatReportTable(stresses, ['Quantity', 'Value', 'Unit'],
                                       title = f'Axial compression, FS {self.factorOfSafety:.2f}'))

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
            with open(os.path.join(outputDir, 'cylindricalShell.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Check the geometry is thin-walled and the loading is physical.

        '''

        context = createErrorContext(component = 'CylindricalShell')

        if not np.isfinite(self.radius) or self.radius <= 0.0:
            raise InvalidInputError('Shell radius must be positive.', context = context)

        if not np.isfinite(self.thickness) or self.thickness <= 0.0:
            raise InvalidInputError('Shell thickness must be positive.', context = context)

        ratio = self.radiusToThickness

        if ratio < THIN_SHELL_MINIMUM_RATIO:
            raise GeometryError(
                f'R/t of {ratio:.1f} is below {THIN_SHELL_MINIMUM_RATIO:.0f}. This is a thick '
                f'shell and thin-shell buckling theory does not apply to it.', context = context)

        if ratio > THIN_SHELL_MAXIMUM_RATIO:
            raise GeometryError(
                f'R/t of {ratio:.0f} is above {THIN_SHELL_MAXIMUM_RATIO:.0f}, which is the bound '
                f'SP-8007 states on the knockdown parameter itself rather than a convention. The '
                f'correlation returns a number above it and the number means nothing.',
                context = context)

        if self.internalPressure > 0.0 and self.externalPressure > 0.0:
            raise InvalidInputError(
                'Set either internalPressure or externalPressure, not both. Use the net value.',
                context = context)
