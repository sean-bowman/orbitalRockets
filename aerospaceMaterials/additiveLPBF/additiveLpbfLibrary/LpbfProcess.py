
# -- LpbfProcess Class Definition -- #

'''

Laser powder bed fusion process window, build time and design for additive geometry checks.

Two things decide whether an LPBF part comes out solid, and they pull in opposite directions.

    Too little energy   The melt pool does not reach the previous layer and the fusion is
                        incomplete. Lack of fusion porosity: irregular, flat, aligned with the
                        layers, and the worst possible defect for fatigue because it behaves
                        like a crack.

    Too much energy     The melt pool goes into keyhole mode, a deep narrow vapour cavity that
                        collapses and traps gas. Keyhole porosity: round, deep, and less harmful
                        than lack of fusion but still a fatigue initiation site.

Between them is the process window, and it is narrower than most parameter sets admit.

    E_v = P / (v * h * t)        volumetric energy density [J/m^3]

Energy density alone is a poor predictor, because the same E_v can be reached by a fast scan at high
power or a slow scan at low power and those produce different melt pools. The normalised enthalpy
form is the better discriminator and it is what the keyhole check uses here.

The second half of this class is design for additive, which is where most parts actually fail. A
geometry that violates the overhang angle, the minimum wall, or the powder evacuation limit does not
produce a marginal part. It produces a build crash, a warped part, or a passage full of sintered
powder that cannot be cleared and cannot be inspected.

See Also:
---------
LpbfQualification : The part classification and coupon requirements that follow from this
PowderLot         : Feedstock condition, which shifts the process window
ExtrusionHoning   : What can be done about the as-built internal surface afterwards

Theory: docs/ProcessFundamentals.md, docs/DesignForLpbf.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from lpbfUtils import (applyInputs, formatReportTable, queryMaterial, roughnessTable,
                           InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .lpbfUtils import (applyInputs, formatReportTable, queryMaterial, roughnessTable,
                            InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Thermophysical properties at the melt, which is where the process physics happens rather than at
# room temperature. Latent heat and melting point drive the enthalpy balance; absorptivity is the
# fraction of incident laser energy that actually enters the melt pool at 1070 nm.
#
# Absorptivity is the parameter that makes copper hard. Pure copper absorbs about 5 percent at a
# fibre laser wavelength, so most of the beam is reflected and the melt pool is unstable. GRCop-42
# works because chromium and niobium raise it enough for a conventional machine.

MELT_PROPERTIES = {
    'TI-6AL-4V':   {'meltingPoint': 1933.0, 'latentHeat': 286.0e3, 'density': 4430.0,
                    'specificHeat': 700.0, 'thermalDiffusivity': 8.0e-6, 'absorptivity': 0.40,
                    'note': 'The best behaved common LPBF alloy. Wide process window.'},
    'INCONEL 718': {'meltingPoint': 1609.0, 'latentHeat': 270.0e3, 'density': 8190.0,
                    'specificHeat': 620.0, 'thermalDiffusivity': 5.5e-6, 'absorptivity': 0.42,
                    'note': 'Mature. Cracking risk in the heat affected zone if the age is wrong.'},
    'INCONEL 625': {'meltingPoint': 1623.0, 'latentHeat': 272.0e3, 'density': 8440.0,
                    'specificHeat': 620.0, 'thermalDiffusivity': 5.2e-6, 'absorptivity': 0.42,
                    'note': 'Solid solution, so no post-build age is needed to reach properties.'},
    '316L':        {'meltingPoint': 1663.0, 'latentHeat': 260.0e3, 'density': 8000.0,
                    'specificHeat': 650.0, 'thermalDiffusivity': 5.0e-6, 'absorptivity': 0.38,
                    'note': 'Very forgiving. The alloy to develop parameters on.'},
    'ALSI10MG':    {'meltingPoint': 869.0, 'latentHeat': 423.0e3, 'density': 2670.0,
                    'specificHeat': 910.0, 'thermalDiffusivity': 5.0e-5, 'absorptivity': 0.25,
                    'note': 'High reflectivity and high diffusivity, so it needs high power and '
                            'fast scanning. Prone to hydrogen porosity from moist powder.'},
    'GRCOP-42':    {'meltingPoint': 1356.0, 'latentHeat': 205.0e3, 'density': 8756.0,
                    'specificHeat': 390.0, 'thermalDiffusivity': 9.4e-5, 'absorptivity': 0.15,
                    'note': 'Copper reflects the fibre laser wavelength. Cr and Nb raise the '
                            'absorptivity enough to make it processable, which is part of why the '
                            'alloy exists in this form.'}
}

# Normalised enthalpy thresholds. dH/h_s below the lower bound gives a melt pool too shallow to
# reach the previous layer; above the upper bound the pool goes into keyhole mode.
#
# The keyhole threshold near 30 is widely reported and it is a guide rather than a constant: it
# shifts with material, layer thickness and beam diameter.

NORMALISED_ENTHALPY_LOWER = 6.0     # [-], below this the fusion is incomplete
NORMALISED_ENTHALPY_UPPER = 30.0    # [-], above this the melt pool keyholes

# Eagar-Tsai shape coefficients, calibrated against published melt pool cross sections rather than
# derived. The moving point source solution gives the scaling; these set the magnitude.
#
# Calibration point: Inconel 718 at 285 W, 0.96 m/s, 80 um beam, which is a well documented
# production parameter set and produces a pool roughly 90 um deep and 155 um wide. That puts the
# depth at 2.3 layers on a 40 um layer, inside the 1.5 to 2.5 target band, and the hatch overlap at
# 30 percent on a 110 um hatch.
#
# Getting these wrong understates the depth and makes every parameter set look like lack of fusion.

MELT_POOL_DEPTH_COEFFICIENT = 1.10   # [-]
MELT_POOL_WIDTH_COEFFICIENT = 0.95   # [-]

# Design for additive limits. These are process capability figures for a well developed parameter
# set on a modern machine, and every one of them is a reason a part gets redesigned.

DFAM_LIMITS = {
    'minimumWallThickness':     0.0004,   # [m], 0.4 mm. Below this the wall is not fully dense
    'minimumFeatureSize':       0.0003,   # [m], the smallest resolvable feature
    'selfSupportingAngle':      45.0,     # [deg] from horizontal. Below this needs support
    'maximumUnsupportedSpan':   0.002,    # [m], a horizontal bridge without support
    'maximumRoundChannel':      0.008,    # [m], a horizontal round channel that self supports
    'minimumChannelDiameter':   0.0005,   # [m], below this powder cannot be evacuated at all
    'maximumChannelAspect':     20.0,     # [-], length over diameter for reliable powder removal
    'minimumHoleForDrilling':   0.0008    # [m], below this a printed hole should be drilled instead
}

# As-built roughness by surface orientation. Downskin is worse than upskin because the melt pool
# sits on loose powder rather than on solid material, and partially sintered particles adhere.
#
# The values are anchored to roughnessTable() in the shared common package, and a test asserts they
# agree so the two cannot drift.

SURFACE_ROUGHNESS = {
    'upskin':      {'roughness': 12.0e-6, 'note': 'Top facing, best case'},
    'vertical':    {'roughness': 20.0e-6, 'note': 'Side wall, the reference case'},
    'downskin':    {'roughness': 40.0e-6, 'note': 'Overhanging, sitting on loose powder'},
    'internal':    {'roughness': 20.0e-6, 'note': 'Internal passage, unfinishable except by AFM'}
}

# Build economics. Recoat time is per layer and it is why layer thickness has such leverage on cost:
# halving it doubles the layer count and therefore doubles the recoat time for the whole build.

RECOAT_TIME_PER_LAYER = 9.0        # [s], typical for a modern machine
MACHINE_SETUP_TIME    = 7200.0     # [s], two hours of setup and teardown per build
POWDER_PACKING_FACTOR = 0.55       # [-], apparent density over solid density

# ------------------------------------------------------------------------------------------------ #

class LpbfProcess:

    '''

    Process window, build time and design for additive geometry checks for a laser powder bed part.

    Primary Input Properties:
    -------------------------
    material : str
        Key into MELT_PROPERTIES
    laserPower / scanSpeed / hatchSpacing / layerThickness : float
        The four parameters that define the process point [W], [m/s], [m], [m]
    beamDiameter : float
        [m], the spot size at the powder bed

    Key Output Properties:
    ----------------------
    energyDensity : float
        Volumetric energy density [J/m^3]
    normalisedEnthalpy : float
        The keyhole and lack of fusion discriminator [-]
    meltPoolDepth : float
        [m], and whether it reaches the previous layer
    processRegime : str
        'lack of fusion', 'stable', or 'keyhole'

    Public Methods:
    ---------------
    setInputs(inputs)                Load a configuration dictionary
    calculateEnergyDensity()         Volumetric energy density and the normalised enthalpy
    calculateMeltPool()              Eagar-Tsai depth and width, and the layer overlap check
    classifyRegime()                 Lack of fusion, stable or keyhole
    checkGeometry(geometry)          Design for additive checks against DFAM_LIMITS
    checkPowderEvacuation(d, L)      Whether an internal passage can be cleared
    predictSurfaceRoughness(angle)   As-built Ra from the build angle
    calculateBuildTime(volume, h)    Scan plus recoat, and the cost driver split
    generateReport(outputDir)        Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material -- #

        self.material            = 'INCONEL 718'   # [case insensitive string]

        # -- Process Parameters -- #

        self.laserPower          = 285.0     # [W]
        self.scanSpeed           = 0.960     # [m/s]
        self.hatchSpacing        = 110.0e-6  # [m]
        self.layerThickness      = 40.0e-6   # [m]
        self.beamDiameter        = 80.0e-6   # [m]
        self.preheatTemperature  = 353.15    # [K], build plate

        # -- Results -- #

        self.energyDensity       = np.nan    # [J/m^3]
        self.linearEnergyDensity = np.nan    # [J/m]
        self.normalisedEnthalpy  = np.nan    # [-]
        self.meltPoolDepth       = np.nan    # [m]
        self.meltPoolWidth       = np.nan    # [m]
        self.processRegime       = ''        # [case sensitive string]
        self.processNotes        = []        # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material.

        '''

        requiredParams = {
            'material': 'Material not provided.'
        }

        optionalParams = ['laserPower', 'scanSpeed', 'hatchSpacing', 'layerThickness',
                          'beamDiameter', 'preheatTemperature']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateEnergyDensity(self) -> dict:

        '''

        Volumetric and linear energy density, and the normalised enthalpy.

            E_v = P / (v h t)                         [J/m^3]
            E_l = P / v                               [J/m]
            dH / h_s = A P / (rho h_s sqrt(pi alpha v sigma^3))

        Energy density on its own is a poor discriminator, because the same value is reached by a
        fast scan at high power and a slow scan at low power, and those produce different melt
        pools. Two parameter sets with identical E_v can sit on opposite sides of the keyhole
        threshold.

        The normalised enthalpy compares the absorbed energy to the enthalpy needed to melt the
        material, scaled by how far heat diffuses in the interaction time, and it separates the two
        cases properly. It is what classifyRegime uses.

        '''

        properties = MELT_PROPERTIES[self.material]

        self.energyDensity = self.laserPower / (self.scanSpeed * self.hatchSpacing *
                                                self.layerThickness)
        self.linearEnergyDensity = self.laserPower / self.scanSpeed

        # Enthalpy at melting, referenced to the build plate preheat rather than to ambient, because
        # a preheated plate genuinely reduces the energy needed.
        meltingEnthalpy = properties['density'] * (
            properties['specificHeat'] * (properties['meltingPoint'] - self.preheatTemperature) +
            properties['latentHeat'])

        beamRadius = self.beamDiameter / 2.0

        self.normalisedEnthalpy = (properties['absorptivity'] * self.laserPower) / (
            meltingEnthalpy * np.sqrt(np.pi * properties['thermalDiffusivity'] *
                                      self.scanSpeed * beamRadius ** 3))

        return {'energyDensity': self.energyDensity,
                'energyDensityJoulePerCubicMillimetre': self.energyDensity / 1.0e9,
                'linearEnergyDensity': self.linearEnergyDensity,
                'normalisedEnthalpy': self.normalisedEnthalpy,
                'meltingEnthalpy': meltingEnthalpy,
                'absorptivity': properties['absorptivity']}

    def calculateMeltPool(self) -> dict:

        '''

        Melt pool depth and width, and whether the pool reaches the previous layer.

        Uses the Eagar-Tsai moving point source solution, scaled by the normalised enthalpy. The
        depth prediction is approximate; what matters here is the comparison against the layer
        thickness rather than the absolute value.

        THE OVERLAP CRITERION IS THE ONE THAT MATTERS:

            meltPoolDepth > layerThickness

        If the pool does not penetrate into the already-solidified material below, the layers are
        not metallurgically joined. The result is lack of fusion porosity, which is flat, aligned
        with the build layers, and behaves like a pre-existing crack. It is the worst defect this
        process produces and it is invisible to a density measurement that only counts volume.

        A depth of 1.5 to 2.5 times the layer thickness is the usual target.

        '''

        if np.isnan(self.normalisedEnthalpy):
            self.calculateEnergyDensity()

        properties = MELT_PROPERTIES[self.material]
        beamRadius = self.beamDiameter / 2.0

        # Eagar-Tsai scaling: depth grows with the normalised enthalpy and with the interaction time
        shapeFactor = np.sqrt(self.normalisedEnthalpy / np.pi)

        self.meltPoolDepth = beamRadius * shapeFactor * MELT_POOL_DEPTH_COEFFICIENT
        self.meltPoolWidth = 2.0 * beamRadius * shapeFactor * MELT_POOL_WIDTH_COEFFICIENT

        depthRatio = self.meltPoolDepth / self.layerThickness
        hatchOverlap = (self.meltPoolWidth - self.hatchSpacing) / self.meltPoolWidth

        result = {'meltPoolDepth': self.meltPoolDepth, 'meltPoolWidth': self.meltPoolWidth,
                  'depthToLayerRatio': depthRatio,
                  'hatchOverlapFraction': hatchOverlap,
                  'aspectRatio': self.meltPoolDepth / self.meltPoolWidth}

        if depthRatio < 1.0:
            self.processNotes.append(
                f'The melt pool is {self.meltPoolDepth * 1.0e6:.0f} um deep against a '
                f'{self.layerThickness * 1.0e6:.0f} um layer, so it does not reach the previous '
                f'layer. This produces lack of fusion porosity: flat, layer-aligned defects that '
                f'behave like cracks. Raise the power or slow the scan.')
        elif depthRatio < 1.5:
            self.processNotes.append(
                f'The melt pool penetrates only {depthRatio:.2f} layers. The usual target is 1.5 to '
                f'2.5 to guarantee remelting of the previous layer across the whole hatch.')

        if hatchOverlap < 0.20:
            self.processNotes.append(
                f'Hatch overlap is {hatchOverlap * 100.0:.0f} percent. Below about 20 percent the '
                f'gaps between adjacent tracks do not remelt and lack of fusion appears between '
                f'scan vectors rather than between layers.')

        if result['aspectRatio'] > 1.5:
            self.processNotes.append(
                f'The melt pool aspect ratio is {result["aspectRatio"]:.2f}. A deep narrow pool is '
                f'the signature of keyhole mode, where the vapour cavity collapses and traps gas.')

        return result

    def classifyRegime(self) -> dict:

        '''

        Place the process point on the map: lack of fusion, stable, or keyhole.

        The window is narrower than most published parameter sets admit, and the two failure modes
        are not equally bad. Keyhole porosity is round and roughly spherical, so it is a stress
        concentration of about three. Lack of fusion porosity is flat and layer aligned, so it is a
        crack, and the fatigue debit is far larger.

        Given the choice, err towards keyhole rather than towards lack of fusion.

        '''

        if np.isnan(self.normalisedEnthalpy):
            self.calculateEnergyDensity()

        if self.normalisedEnthalpy < NORMALISED_ENTHALPY_LOWER:
            self.processRegime = 'lack of fusion'
            defect = ('Flat, layer-aligned pores that behave like cracks. The worst defect this '
                      'process produces, and HIP does not fully recover the fatigue properties '
                      'because the flaws are not spherical.')
        elif self.normalisedEnthalpy > NORMALISED_ENTHALPY_UPPER:
            self.processRegime = 'keyhole'
            defect = ('Round gas pores from vapour cavity collapse. Less harmful than lack of '
                      'fusion, and largely recoverable by HIP because the pores are spherical.')
        else:
            self.processRegime = 'stable'
            defect = 'Within the conduction mode window. Porosity should be below 0.1 percent.'

        margin = min(self.normalisedEnthalpy - NORMALISED_ENTHALPY_LOWER,
                     NORMALISED_ENTHALPY_UPPER - self.normalisedEnthalpy)

        result = {'processRegime': self.processRegime,
                  'normalisedEnthalpy': self.normalisedEnthalpy,
                  'lowerBound': NORMALISED_ENTHALPY_LOWER,
                  'upperBound': NORMALISED_ENTHALPY_UPPER,
                  'marginToNearestBound': margin,
                  'expectedDefect': defect}

        if self.processRegime != 'stable':
            self.processNotes.append(
                f'The process point is in the {self.processRegime} regime at a normalised enthalpy '
                f'of {self.normalisedEnthalpy:.1f}, against a window of '
                f'{NORMALISED_ENTHALPY_LOWER:.0f} to {NORMALISED_ENTHALPY_UPPER:.0f}. {defect}')
        elif margin < 4.0:
            self.processNotes.append(
                f'The process point is stable but only {margin:.1f} from the nearest bound. Lot to '
                f'lot powder variation and machine drift both move this, so a narrow margin means a '
                f'parameter set that works on the development build and not on the fifth one.')

        return result

    def checkGeometry(self, geometry: dict) -> dict:

        '''

        Design for additive checks against the process capability limits.

        Accepted geometry keys, all optional:

            minimumWallThickness   [m]
            minimumFeature         [m]
            overhangAngle          [deg] from horizontal, the shallowest in the part
            unsupportedSpan        [m]
            channelDiameter        [m]
            channelLength          [m]
            holeDiameter           [m]

        Every violation is reported with the limit and the margin, because a design review needs to
        know how far outside it is rather than merely that it is.

        '''

        violations = []
        warnings   = []

        wall = geometry.get('minimumWallThickness')
        if wall is not None and wall < DFAM_LIMITS['minimumWallThickness']:
            violations.append(
                f'Wall {wall * 1.0e3:.3f} mm is below the {DFAM_LIMITS["minimumWallThickness"] * 1.0e3:.1f} mm '
                f'minimum. A thinner wall is not fully dense and its properties are not those in any '
                f'database.')

        feature = geometry.get('minimumFeature')
        if feature is not None and feature < DFAM_LIMITS['minimumFeatureSize']:
            violations.append(
                f'Feature {feature * 1.0e3:.3f} mm is below the '
                f'{DFAM_LIMITS["minimumFeatureSize"] * 1.0e3:.1f} mm resolution limit.')

        angle = geometry.get('overhangAngle')
        if angle is not None and angle < DFAM_LIMITS['selfSupportingAngle']:
            violations.append(
                f'Overhang at {angle:.0f} deg from horizontal is below the '
                f'{DFAM_LIMITS["selfSupportingAngle"]:.0f} deg self-supporting limit. It needs '
                f'support, and support inside a closed passage cannot be removed.')

        span = geometry.get('unsupportedSpan')
        if span is not None and span > DFAM_LIMITS['maximumUnsupportedSpan']:
            violations.append(
                f'Unsupported horizontal span of {span * 1.0e3:.2f} mm exceeds the '
                f'{DFAM_LIMITS["maximumUnsupportedSpan"] * 1.0e3:.1f} mm limit. It will sag or curl.')

        channel = geometry.get('channelDiameter')
        if channel is not None:
            if channel > DFAM_LIMITS['maximumRoundChannel']:
                warnings.append(
                    f'A horizontal round channel of {channel * 1.0e3:.2f} mm exceeds the '
                    f'{DFAM_LIMITS["maximumRoundChannel"] * 1.0e3:.0f} mm self-supporting limit. '
                    f'Change the section to a teardrop or a diamond, which self support at any size '
                    f'because the crown is above the overhang angle everywhere.')
            if channel < DFAM_LIMITS['minimumChannelDiameter']:
                violations.append(
                    f'A channel of {channel * 1.0e3:.3f} mm is below the '
                    f'{DFAM_LIMITS["minimumChannelDiameter"] * 1.0e3:.1f} mm minimum, and powder '
                    f'cannot be evacuated from it at all.')

        hole = geometry.get('holeDiameter')
        if hole is not None and hole < DFAM_LIMITS['minimumHoleForDrilling']:
            warnings.append(
                f'A printed hole of {hole * 1.0e3:.3f} mm is below the '
                f'{DFAM_LIMITS["minimumHoleForDrilling"] * 1.0e3:.1f} mm threshold where printing '
                f'beats drilling. Print it undersize and drill it.')

        self.processNotes.extend(violations)

        return {'violations': violations, 'warnings': warnings,
                'acceptable': not violations, 'limits': DFAM_LIMITS}

    def checkPowderEvacuation(self, channelDiameter: float, channelLength: float,
                              bends: int = 0) -> dict:

        '''

        Whether powder can be cleared from an internal passage.

        The aspect ratio L/D is the governing parameter, and each bend counts against it because
        powder has to be shaken around a corner rather than poured out.

            effectiveAspect = (L / D) * (1 + 0.5 * bends)

        UNEVACUATED POWDER IS THE DEFINING RISK OF ADDITIVE INTERNAL PASSAGES. It is partially
        sintered by the heat of subsequent layers, so it is not loose. It cannot be seen except by
        computed tomography, it cannot be reached by any tool, and in a propulsion system it
        migrates downstream into an injector or a valve seat.

        A passage that cannot be verified clear should not be a closed passage. Split the part and
        join it, or accept a drilled hole with a plug.

        '''

        if channelDiameter <= 0.0 or channelLength <= 0.0:
            raise InvalidInputError(
                message       = 'Channel diameter and length must be positive.',
                parameterName = 'channelDiameter/channelLength',
                value         = (channelDiameter, channelLength), validRange = 'Both greater than 0'
            )

        aspectRatio          = channelLength / channelDiameter
        effectiveAspectRatio = aspectRatio * (1.0 + 0.5 * bends)

        feasible = (effectiveAspectRatio <= DFAM_LIMITS['maximumChannelAspect'] and
                    channelDiameter >= DFAM_LIMITS['minimumChannelDiameter'])

        result = {'channelDiameter': channelDiameter, 'channelLength': channelLength,
                  'bends': bends, 'aspectRatio': aspectRatio,
                  'effectiveAspectRatio': effectiveAspectRatio,
                  'limit': DFAM_LIMITS['maximumChannelAspect'],
                  'feasible': feasible,
                  'inspectionRequired': 'computed tomography'}

        if not feasible:
            raise ProcessInfeasibleError(
                message = f'A {channelDiameter * 1.0e3:.2f} mm channel {channelLength * 1.0e3:.0f} '
                          f'mm long with {bends} bends has an effective aspect ratio of '
                          f'{effectiveAspectRatio:.1f} against a limit of '
                          f'{DFAM_LIMITS["maximumChannelAspect"]:.0f}. Powder cannot be reliably '
                          f'evacuated. Partially sintered powder in a closed passage cannot be '
                          f'seen, reached or removed, and in a propulsion system it migrates '
                          f'downstream into an injector or a valve seat. Redesign the passage, '
                          f'split the part, or accept a drilled hole with a plug.'
            )

        if effectiveAspectRatio > 0.7 * DFAM_LIMITS['maximumChannelAspect']:
            self.processNotes.append(
                f'The channel is at {effectiveAspectRatio:.1f} of a {DFAM_LIMITS["maximumChannelAspect"]:.0f} '
                f'aspect ratio limit. Evacuation is feasible and it has to be verified by CT on '
                f'every article rather than demonstrated once.')

        return result

    def predictSurfaceRoughness(self, buildAngle: float = 90.0) -> dict:

        '''

        As-built arithmetic roughness from the build angle.

        Downskin surfaces are markedly worse than upskin because the melt pool sits on loose powder
        rather than on solid material, and partially sintered particles adhere to the underside. The
        transition is continuous with angle rather than a step.

        Build angle is measured from horizontal: 90 degrees is a vertical wall, 0 is a horizontal
        downskin.

        '''

        buildAngle = float(np.clip(buildAngle, 0.0, 180.0))

        if buildAngle >= 90.0:
            # Upskin: improves as the surface approaches horizontal facing up
            fraction  = (buildAngle - 90.0) / 90.0
            roughness = (SURFACE_ROUGHNESS['vertical']['roughness'] * (1.0 - fraction) +
                         SURFACE_ROUGHNESS['upskin']['roughness'] * fraction)
            orientation = 'upskin' if fraction > 0.5 else 'vertical'
        else:
            # Downskin: degrades rapidly below the self-supporting angle
            fraction  = (90.0 - buildAngle) / 90.0
            roughness = (SURFACE_ROUGHNESS['vertical']['roughness'] * (1.0 - fraction) +
                         SURFACE_ROUGHNESS['downskin']['roughness'] * fraction)
            orientation = 'downskin' if fraction > 0.5 else 'vertical'

        # Layer thickness scales the stair stepping component
        roughness *= (self.layerThickness / 40.0e-6) ** 0.5

        return {'buildAngle': buildAngle, 'orientation': orientation,
                'roughness': roughness,
                'roughnessMicrometres': roughness * 1.0e6,
                'drawnTubeReference': roughnessTable('drawn tube'),
                'ratioToDrawnTube': roughness / roughnessTable('drawn tube'),
                'afterAbrasiveFlow': roughnessTable('lpbf abrasive flow')}

    def calculateBuildTime(self, partVolume: float, buildHeight: float,
                           partsPerBuild: int = 1) -> dict:

        '''

        Build time from the scan time and the recoat time, and which of the two dominates.

            scanTime   = volume / (v * h * t)          the hatching itself
            recoatTime = (height / t) * recoatPerLayer

        LAYER THICKNESS HAS LEVERAGE ON BOTH TERMS AND IN THE SAME DIRECTION. Halving it doubles the
        layer count, so it doubles the recoat time, and it also halves the volume deposited per pass
        so it doubles the scan time. A 20 um build is not a little slower than a 40 um build, it is
        roughly twice as slow, and that is the whole cost argument for coarse layers where the
        surface finish permits.

        Recoat time is independent of how much is being built on each layer, so a build with one
        small part costs almost the same as a full plate. Nesting parts is nearly free.

        '''

        if partVolume <= 0.0 or buildHeight <= 0.0:
            raise InvalidInputError(
                message       = 'Part volume and build height must be positive.',
                parameterName = 'partVolume/buildHeight', value = (partVolume, buildHeight),
                validRange    = 'Both greater than 0'
            )

        totalVolume = partVolume * partsPerBuild

        scanTime   = totalVolume / (self.scanSpeed * self.hatchSpacing * self.layerThickness)
        layerCount = buildHeight / self.layerThickness
        recoatTime = layerCount * RECOAT_TIME_PER_LAYER

        totalTime = scanTime + recoatTime + MACHINE_SETUP_TIME

        dominant = 'recoat' if recoatTime > scanTime else 'scan'

        properties  = MELT_PROPERTIES[self.material]
        partMass    = totalVolume * properties['density']

        result = {'partVolume': partVolume, 'partsPerBuild': partsPerBuild,
                  'totalVolume': totalVolume, 'partMass': partMass,
                  'layerCount': layerCount,
                  'scanTime': scanTime, 'recoatTime': recoatTime,
                  'setupTime': MACHINE_SETUP_TIME, 'totalTime': totalTime,
                  'totalTimeHours': totalTime / 3600.0,
                  'dominantTerm': dominant,
                  'recoatFraction': recoatTime / totalTime,
                  'timePerPartHours': totalTime / 3600.0 / partsPerBuild}

        if dominant == 'recoat' and partsPerBuild == 1:
            result['nestingNote'] = (
                'Recoat dominates, and recoat time does not depend on how much is built per layer. '
                'Nesting more parts into the same build height is close to free.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        if np.isnan(self.energyDensity):
            self.calculateEnergyDensity()
        if np.isnan(self.meltPoolDepth):
            self.calculateMeltPool()
        if not self.processRegime:
            self.classifyRegime()

        properties = MELT_PROPERTIES[self.material]

        rows = [
            ['Material',              f'{self.material}'],
            ['Absorptivity',          f'{properties["absorptivity"]:.2f} at 1070 nm'],
            ['Laser power',           f'{self.laserPower:.0f} W'],
            ['Scan speed',            f'{self.scanSpeed:.3f} m/s'],
            ['Hatch spacing',         f'{self.hatchSpacing * 1.0e6:.0f} um'],
            ['Layer thickness',       f'{self.layerThickness * 1.0e6:.0f} um'],
            ['Beam diameter',         f'{self.beamDiameter * 1.0e6:.0f} um'],
            ['Volumetric energy',     f'{self.energyDensity / 1.0e9:.1f} J/mm^3'],
            ['Linear energy',         f'{self.linearEnergyDensity:.1f} J/m'],
            ['Normalised enthalpy',   f'{self.normalisedEnthalpy:.1f} '
                                      f'(window {NORMALISED_ENTHALPY_LOWER:.0f} to '
                                      f'{NORMALISED_ENTHALPY_UPPER:.0f})'],
            ['Process regime',        f'{self.processRegime.upper()}'],
            ['Melt pool depth',       f'{self.meltPoolDepth * 1.0e6:.0f} um '
                                      f'({self.meltPoolDepth / self.layerThickness:.2f} layers)'],
            ['Melt pool width',       f'{self.meltPoolWidth * 1.0e6:.0f} um'],
            ['Vertical wall Ra',      f'{self.predictSurfaceRoughness(90.0)["roughnessMicrometres"]:.1f} um'],
            ['Downskin Ra',           f'{self.predictSurfaceRoughness(30.0)["roughnessMicrometres"]:.1f} um']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'LPBF PROCESS')

        report += f'\n\nMATERIAL NOTES\n{"-" * 60}\n{properties["note"]}\n'

        for note in self.processNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'lpbfProcess.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = ' '.join(self.material.strip().upper().split())

        if key not in MELT_PROPERTIES:
            raise InvalidInputError(
                message       = f'No melt properties for \'{self.material}\'. The process model '
                                f'needs melting point, latent heat and absorptivity, and none of '
                                f'them can be assumed.',
                parameterName = 'material', value = self.material,
                validRange    = str(sorted(MELT_PROPERTIES.keys()))
            )

        self.material = key

        for name, value in (('laserPower', self.laserPower), ('scanSpeed', self.scanSpeed),
                            ('hatchSpacing', self.hatchSpacing),
                            ('layerThickness', self.layerThickness),
                            ('beamDiameter', self.beamDiameter)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0'
                )

        # The overlap criterion is hatch spacing against MELT POOL WIDTH, not against beam diameter.
        # The pool is wider than the beam because heat conducts laterally, so a real parameter set
        # routinely runs a 110 um hatch on an 80 um beam and the tracks still overlap. That check
        # belongs in calculateMeltPool, where the pool width is actually known, and it is there.
        #
        # What is checked here is only the obviously unphysical case, where no plausible pool could
        # bridge the gap.
        if self.hatchSpacing > 3.0 * self.beamDiameter:
            raise InvalidInputError(
                message       = f'Hatch spacing {self.hatchSpacing * 1.0e6:.0f} um is more than '
                                f'three times the beam diameter {self.beamDiameter * 1.0e6:.0f} um. '
                                f'No melt pool spreads that far, so adjacent tracks cannot overlap '
                                f'and the layer would not be continuous.',
                parameterName = 'hatchSpacing', value = self.hatchSpacing,
                validRange    = f'Below {3.0 * self.beamDiameter * 1.0e6:.0f} um for this beam'
            )
