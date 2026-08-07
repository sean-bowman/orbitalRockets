
# -- Seal Class Definition -- #

'''

O-ring gland sizing, seal material selection, extrusion and permeation analysis.

A static o-ring seal is not a complicated device, and the reason it fails is almost never the
rubber. It fails because the gland was the wrong size, because the extrusion gap was too large for
the pressure, because the elastomer went glassy at temperature, or because the material was not
compatible with the fluid. All four are design decisions, and all four are checked here.

The four numbers that define a gland:

    squeeze          how much the cross section is compressed, as a percentage of free diameter
    gland fill       the fraction of the groove volume the seal occupies
    stretch          how much the inner diameter is stretched on installation
    extrusion gap    the diametral clearance the seal has to bridge under pressure

Getting all four right simultaneously is the whole job, and they conflict: more squeeze improves
sealing and raises gland fill, more fill risks over-filling when the seal swells or heats, more
stretch reduces the cross section and therefore the squeeze.

The class also covers permeation, which is the leak rate you get from a seal that is not leaking.
An elastomer is a semi-permeable membrane, gas dissolves into it on the high pressure side and
comes out on the low pressure side, and no amount of squeeze stops it. For a long-duration
spacecraft that is the leak rate that matters.

Cryogenic and metal seals are covered by the material table and by the guidance in the docs; the
gland sizing math here is specific to elastomer o-rings.

See Also:
---------
Fitting  : The joint the seal lives inside
LeakPath : Leak rate units, detection, and what an allowable leak rate should be
Line     : Thermal contraction, which is what breaks a cryogenic elastomer seal

Theory: docs/Seals.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (applyInputs, formatReportTable, leakRateConvert,
                       M_PER_IN, PA_PER_PSIA, PA_PER_ATM,
                       InvalidInputError, CompatibilityError, createErrorContext)
except ImportError:
    from .utils import (applyInputs, formatReportTable, leakRateConvert,
                        M_PER_IN, PA_PER_PSIA, PA_PER_ATM,
                        InvalidInputError, CompatibilityError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# AS568 standard o-ring cross section diameters. The dash number series determines the cross
# section: -0xx is the 0.070 in series, -1xx the 0.103 in series, and so on. Using a standard cross
# section means the seal is a catalog item and the gland dimensions come from a published table.
AS568_CROSS_SECTIONS_IN = {
    '0xx': 0.070,   # 1.78 mm, the small-bore standard
    '1xx': 0.103,   # 2.62 mm
    '2xx': 0.139,   # 3.53 mm
    '3xx': 0.210,   # 5.33 mm
    '4xx': 0.275    # 6.99 mm
}

# Recommended squeeze ranges by application, as a fraction of the free cross section diameter.
#
# The lower bound is set by sealing: too little squeeze and surface finish irregularities are not
# bridged. The upper bound is set by compression set and by gland fill: too much squeeze permanently
# deforms the seal and leaves no room for thermal expansion.
SQUEEZE_RANGES = {
    'static face':        (0.20, 0.30),   # axial squeeze, flange or boss face seal
    'static radial':      (0.15, 0.25),   # piston or rod groove, no motion
    'dynamic reciprocating': (0.10, 0.20),   # sliding rod or piston
    'dynamic rotary':     (0.08, 0.15),   # rotating shaft; friction heating limits squeeze
    'vacuum':             (0.25, 0.30)    # high vacuum static; maximum squeeze to minimize permeation area
}

# Gland fill limits. Fill is the seal cross section area divided by the groove cross section area.
#
# Below 60 percent the seal can roll or spiral in the groove. Above 90 percent there is no room for
# thermal expansion or fluid swell, and an over-filled groove will extrude the seal or, worse,
# hydraulically lock and yield the hardware. Target 75 percent.
GLAND_FILL_MINIMUM = 0.60
GLAND_FILL_TARGET  = 0.75
GLAND_FILL_MAXIMUM = 0.90

# Maximum installed stretch on the inner diameter. Stretch reduces the cross section (roughly half
# the stretch percentage) and therefore reduces squeeze, and it accelerates stress relaxation.
STRETCH_MAXIMUM_INSTALL   = 0.05   # absolute limit for installation over a shoulder
STRETCH_MAXIMUM_SUSTAINED = 0.03   # limit for a seal that lives stretched

# Maximum diametral extrusion gap [in] before a backup ring is required, by pressure [psi] and
# durometer. From the Parker O-Ring Handbook extrusion limit curves. Interpolated on log pressure.
#
# This is the check that catches the classic failure: a seal that works fine on the bench at 500 psi
# and blows out at operating pressure, because the clearance the machinist left is fine at low
# pressure and far too large at high pressure.
EXTRUSION_PRESSURE_PSI = np.array([500.0, 1000.0, 1500.0, 2000.0, 3000.0, 5000.0])
EXTRUSION_GAP_IN = {
    70: np.array([0.0115, 0.0075, 0.0055, 0.0045, 0.0030, 0.0020]),
    80: np.array([0.0170, 0.0120, 0.0090, 0.0075, 0.0050, 0.0035]),
    90: np.array([0.0230, 0.0170, 0.0130, 0.0110, 0.0085, 0.0060])
}

# Elastomer and polymer seal materials.
#
#   minimumTemperature   practical lower service limit [K], set by the glass transition
#   maximumTemperature   practical upper service limit [K]
#   glassTransition      Tg [K]. Below this the material is glassy and has no sealing compliance.
#   heliumPermeability   [scc-cm / (cm^2 - s - atm)] x 1e-8, at 298 K
#   contraction          integrated linear contraction from 293 K to 77 K [-]
#   compatible           fluids this material is acceptable in
#   incompatible         fluids that destroy it
#
# The glass transition column is the one that matters for cryogenic work. An elastomer below Tg is
# not a soft seal; it is a hard plastic ring with the compliance of a washer, and it will leak the
# instant the joint moves. This is why cryogenic static seals are metal, spring-energized PTFE, or
# heavily preloaded PCTFE, and not o-rings.
SEAL_MATERIALS = {
    'fkm': {
        'name': 'FKM (Viton)', 'minimumTemperature': 253.0, 'maximumTemperature': 477.0,
        'glassTransition': 255.0, 'heliumPermeability': 12.0, 'contraction': 0.018,
        'compatible':   ['N2O4', 'NTO', 'IRFNA', 'GN2', 'GHE', 'AIR', 'HYDROCARBON', 'RP-1'],
        'incompatible': ['N2H4', 'HYDRAZINE', 'MMH', 'AMMONIA', 'HOT WATER', 'KETONES'],
        'notes': 'The default oxidizer-side elastomer. Excellent chemical resistance and low permeability, but '
                 'the glass transition near -20 degC rules it out for anything cold.'
    },
    'epdm': {
        'name': 'EPDM', 'minimumTemperature': 218.0, 'maximumTemperature': 423.0,
        'glassTransition': 218.0, 'heliumPermeability': 55.0, 'contraction': 0.020,
        'compatible':   ['N2H4', 'HYDRAZINE', 'MMH', 'AMMONIA', 'WATER', 'GN2', 'GHE', 'STEAM'],
        'incompatible': ['RP-1', 'HYDROCARBON', 'LOX', 'GOX', 'N2O4'],
        'notes': 'The standard hydrazine-compatible elastomer. Poor hydrocarbon resistance; will swell '
                 'catastrophically in any petroleum fluid.'
    },
    'nbr': {
        'name': 'NBR (Buna-N)', 'minimumTemperature': 233.0, 'maximumTemperature': 393.0,
        'glassTransition': 233.0, 'heliumPermeability': 20.0, 'contraction': 0.019,
        'compatible':   ['RP-1', 'HYDROCARBON', 'GN2', 'AIR', 'WATER'],
        'incompatible': ['N2H4', 'HYDRAZINE', 'MMH', 'N2O4', 'LOX', 'GOX', 'OZONE'],
        'notes': 'Cheap and everywhere, and wrong for almost every propellant. Degrades in hydrazine and '
                 'catalyzes its decomposition. Do not use it because it was in the drawer.'
    },
    'silicone': {
        'name': 'VMQ (Silicone)', 'minimumTemperature': 218.0, 'maximumTemperature': 505.0,
        'glassTransition': 213.0, 'heliumPermeability': 300.0, 'contraction': 0.025,
        'compatible':   ['GN2', 'AIR', 'DRY HEAT'],
        'incompatible': ['STEAM', 'N2O4', 'LOX', 'GOX', 'HIGH PRESSURE GAS'],
        'notes': 'Widest temperature range of the common elastomers but by far the most permeable and the '
                 'weakest. Never use in a pressurized gas seal where permeation matters.'
    },
    'butyl': {
        'name': 'IIR (Butyl)', 'minimumTemperature': 218.0, 'maximumTemperature': 393.0,
        'glassTransition': 208.0, 'heliumPermeability': 5.0, 'contraction': 0.019,
        'compatible':   ['N2H4', 'HYDRAZINE', 'MMH', 'GN2', 'GHE', 'VACUUM'],
        'incompatible': ['RP-1', 'HYDROCARBON', 'LOX', 'GOX'],
        'notes': 'The lowest gas permeability of any common elastomer, which makes it the choice for long '
                 'duration gas retention. Poor high temperature capability.'
    },
    'ptfe': {
        'name': 'PTFE', 'minimumTemperature': 4.0, 'maximumTemperature': 533.0,
        'glassTransition': np.nan, 'heliumPermeability': 70.0, 'contraction': 0.019,
        'compatible':   ['N2H4', 'HYDRAZINE', 'MMH', 'N2O4', 'LOX', 'GOX', 'LH2', 'LN2', 'RP-1', 'EVERYTHING'],
        'notes': 'Chemically inert to essentially everything and usable to 4 K. Not an elastomer: it cold '
                 'flows under sustained load, has no elastic recovery, and contracts 1.9 percent to LN2, six '
                 'times as much as the stainless around it. Use spring-energized, never as a plain o-ring in '
                 'a cryogenic joint.',
        'incompatible': ['MOLTEN ALKALI METALS', 'FLUORINE AT PRESSURE']
    },
    'pctfe': {
        'name': 'PCTFE (Kel-F)', 'minimumTemperature': 4.0, 'maximumTemperature': 423.0,
        'glassTransition': np.nan, 'heliumPermeability': 3.0, 'contraction': 0.013,
        'compatible':   ['LOX', 'GOX', 'LN2', 'LH2', 'N2O4', 'N2H4', 'HYDRAZINE'],
        'incompatible': [],
        'notes': 'The LOX-compatible seat and seal material of choice. Lower permeability and better '
                 'dimensional stability than PTFE, and it passes LOX mechanical impact testing. Harder and '
                 'less compliant, so it needs higher seating loads.'
    },
    'ffkm': {
        'name': 'FFKM (Kalrez, Chemraz)', 'minimumTemperature': 258.0, 'maximumTemperature': 600.0,
        'glassTransition': 264.0, 'heliumPermeability': 10.0, 'contraction': 0.018,
        'compatible':   ['N2O4', 'N2H4', 'HYDRAZINE', 'MMH', 'RP-1', 'STEAM', 'MOST SOLVENTS'],
        'incompatible': ['LOX', 'GOX'],
        'notes': 'Perfluoroelastomer. Nearly universal chemical compatibility and the highest temperature '
                 'capability of any elastomer, at ten to fifty times the cost. Reserve it for the joints '
                 'where nothing else works.'
    }
}

# Permeation scaling relative to helium, by species. Permeation through a polymer is a
# solution-diffusion process, so it does not follow the simple molecular-mass scaling that a
# physical leak does. Small, non-condensing molecules go through fastest.
PERMEATION_SPECIES_FACTOR = {
    'HE': 1.00, 'HELIUM': 1.00,
    'H2': 1.50, 'HYDROGEN': 1.50,
    'N2': 0.15, 'NITROGEN': 0.15, 'GN2': 0.15,
    'O2': 0.35, 'OXYGEN': 0.35, 'GOX': 0.35,
    'AIR': 0.20,
    'CO2': 1.20,
    'CH4': 0.25, 'METHANE': 0.25,
    'AR': 0.12, 'ARGON': 0.12
}

class Seal:

    '''

    O-ring gland sizing, material screening, extrusion and permeation analysis.

    Primary Input Properties:
    -------------------------
    sealType : str
        'static face', 'static radial', 'dynamic reciprocating', 'dynamic rotary' or 'vacuum'
    material : str
        Key into SEAL_MATERIALS
    crossSectionDiameter : float
        Free o-ring cross section diameter W [m]. Use an AS568 standard size.
    innerDiameter : float
        Free o-ring inner diameter [m]
    grooveInnerDiameter : float
        Groove inner diameter [m], for the stretch calculation
    designPressure : float
        Sealed differential pressure [Pa]
    designTemperature : float
        Service temperature [K]
    minimumTemperature : float
        Coldest excursion the seal will see [K]. Defaults to designTemperature.
    fluid : str
        Sealed fluid, for the compatibility check
    durometer : float
        Shore A hardness [-], 70, 80 or 90
    diametralClearance : float
        Diametral gap the seal must bridge under pressure [m]
    targetSqueeze : float
        Desired squeeze fraction. Defaults to the midpoint of the range for the seal type.

    Key Output Properties:
    ----------------------
    grooveDepth / grooveWidth : float
        Gland dimensions [m]
    squeeze : float
        Achieved squeeze fraction [-]
    glandFill : float
        Fraction of the groove volume occupied [-]
    stretch : float
        Installed inner diameter stretch [-]
    maximumAllowableGap : float
        Extrusion limit at the design pressure and durometer [m]
    backupRingRequired : bool
        True when the clearance exceeds the extrusion limit
    permeationRate : float
        Steady permeation leak rate [scc/s]

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    sizeGland()                   Compute groove dimensions for the target squeeze and fill
    checkExtrusion()              Extrusion limit and backup ring requirement
    checkCompatibility()          Material, fluid and temperature screening
    calculatePermeation()         Steady permeation leak rate through the seal
    generateReport(outputDir)     Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Seal Definition -- #

        self.sealType             = 'static face'  # key into SQUEEZE_RANGES
        self.material             = 'fkm'          # key into SEAL_MATERIALS
        self.crossSectionDiameter = np.nan  # [m], free o-ring cross section W
        self.innerDiameter        = np.nan  # [m], free o-ring ID
        self.durometer            = 70.0    # [-], Shore A

        # -- Installation -- #

        self.grooveInnerDiameter  = np.nan  # [m], for the stretch calculation
        self.diametralClearance   = np.nan  # [m], extrusion gap
        self.targetSqueeze        = np.nan  # [-], defaults to the midpoint of the range

        # -- Service Conditions -- #

        self.designPressure       = np.nan  # [Pa], sealed differential
        self.designTemperature    = 293.15  # [K]
        self.minimumTemperature   = np.nan  # [K], coldest excursion
        self.fluid                = ''      # [case sensitive string]
        self.exposedLength        = np.nan  # [m], sealing circumference. Computed from ID if unset.

        # -- Results -- #

        self.grooveDepth          = np.nan  # [m]
        self.grooveWidth          = np.nan  # [m]
        self.squeeze              = np.nan  # [-], fraction of free cross section
        self.squeezeAbsolute      = np.nan  # [m]
        self.glandFill            = np.nan  # [-]
        self.stretch              = np.nan  # [-]
        self.maximumAllowableGap  = np.nan  # [m]
        self.backupRingRequired   = False   # [-]
        self.permeationRate       = np.nan  # [scc/s]
        self.compatibilityNotes   = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: crossSectionDiameter.

        '''

        requiredParams = {
            'crossSectionDiameter': 'O-ring free cross section diameter not provided.'
        }

        optionalParams = ['sealType', 'material', 'innerDiameter', 'durometer',
                          'grooveInnerDiameter', 'diametralClearance', 'targetSqueeze',
                          'designPressure', 'designTemperature', 'minimumTemperature',
                          'fluid', 'exposedLength']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        if np.isnan(self.minimumTemperature):
            self.minimumTemperature = self.designTemperature

    def sizeGland(self) -> dict:

        '''

        Compute groove depth and width for the target squeeze and gland fill.

        Depth follows directly from the squeeze:

            depth = W * (1 - squeeze)

        Width is then set so the gland fill lands on the target:

            width = A_oring / (fill * depth)          A_oring = pi * W^2 / 4

        The stretch check comes last. If the groove inner diameter is given, the installed stretch is

            stretch = (D_groove_ID - D_oring_ID) / D_oring_ID

        and it matters because stretch reduces the cross section. A rule of thumb is that the cross
        section shrinks by roughly half the stretch percentage, so 4 percent stretch costs 2 percent
        of cross section, which comes directly out of the squeeze. The class applies that correction
        and reports the achieved squeeze after stretch.

        '''

        squeezeRange  = SQUEEZE_RANGES[self.sealType.strip().lower()]
        targetSqueeze = self.targetSqueeze
        if np.isnan(targetSqueeze):
            targetSqueeze = 0.5 * (squeezeRange[0] + squeezeRange[1])

        # -- Stretch correction, applied before sizing -- #
        effectiveCrossSection = self.crossSectionDiameter
        if not np.isnan(self.grooveInnerDiameter) and not np.isnan(self.innerDiameter):
            self.stretch = (self.grooveInnerDiameter - self.innerDiameter) / self.innerDiameter
            # Stretching the ring thins its cross section by approximately half the stretch fraction
            effectiveCrossSection = self.crossSectionDiameter * (1.0 - 0.5 * max(self.stretch, 0.0))

        # -- Groove depth from the target squeeze -- #
        self.grooveDepth     = effectiveCrossSection * (1.0 - targetSqueeze)
        self.squeezeAbsolute = effectiveCrossSection - self.grooveDepth
        self.squeeze         = self.squeezeAbsolute / self.crossSectionDiameter

        # -- Groove width from the target gland fill -- #
        oringArea        = np.pi * effectiveCrossSection**2 / 4.0
        self.grooveWidth = oringArea / (GLAND_FILL_TARGET * self.grooveDepth)
        self.glandFill   = oringArea / (self.grooveDepth * self.grooveWidth)

        # -- Checks -- #
        if self.squeeze < squeezeRange[0]:
            self.compatibilityNotes.append(
                f'Achieved squeeze {self.squeeze * 100.0:.1f} percent is below the {squeezeRange[0] * 100.0:.0f} percent '
                f'minimum for {self.sealType}. Surface finish irregularities may not be bridged.')
        if self.squeeze > squeezeRange[1]:
            self.compatibilityNotes.append(
                f'Achieved squeeze {self.squeeze * 100.0:.1f} percent exceeds the {squeezeRange[1] * 100.0:.0f} percent '
                f'maximum for {self.sealType}. Expect accelerated compression set.')

        if not np.isnan(self.stretch):
            if self.stretch > STRETCH_MAXIMUM_INSTALL:
                self.compatibilityNotes.append(
                    f'Installed stretch {self.stretch * 100.0:.1f} percent exceeds the {STRETCH_MAXIMUM_INSTALL * 100.0:.0f} '
                    f'percent installation limit. Use the next larger o-ring ID.')
            elif self.stretch > STRETCH_MAXIMUM_SUSTAINED:
                self.compatibilityNotes.append(
                    f'Installed stretch {self.stretch * 100.0:.1f} percent exceeds the {STRETCH_MAXIMUM_SUSTAINED * 100.0:.0f} '
                    f'percent sustained limit. Acceptable for assembly but will accelerate stress relaxation.')

        return {
            'grooveDepth':     self.grooveDepth,
            'grooveWidth':     self.grooveWidth,
            'squeeze':         self.squeeze,
            'squeezeAbsolute': self.squeezeAbsolute,
            'glandFill':       self.glandFill,
            'stretch':         self.stretch
        }

    def checkExtrusion(self) -> dict:

        '''

        Extrusion limit and backup ring requirement.

        Under pressure the seal is forced into the clearance gap on the low pressure side. If the gap
        is too large for the pressure and the material hardness, the seal nibbles into it and
        eventually shears. The limit falls steeply with pressure and rises with durometer.

        This is the check that catches the most common high-pressure seal failure: a gland that works
        on the bench at 500 psi and blows out at 3000 psi, because the machinist's clearance is fine
        at the first and four times too large at the second.

        Three ways to fix an extrusion problem, in order of preference:

        1. Reduce the clearance. Tighter tolerance on the bore and the piston.
        2. Harder durometer. Going from 70 to 90 Shore A roughly doubles the allowable gap, at the
           cost of sealing compliance on rough surfaces.
        3. Backup ring. A hard PTFE or PEEK anti-extrusion ring on the low pressure side. Effective,
           but it takes groove width, so the gland must be designed for it from the start.

        Note that the clearance to use is the WORST CASE clearance from the tolerance stack, at the
        temperature where the differential thermal contraction is largest, not the nominal.

        '''

        if np.isnan(self.designPressure) or np.isnan(self.diametralClearance):
            raise InvalidInputError(
                message       = 'checkExtrusion needs the design pressure and the diametral clearance.',
                parameterName = 'designPressure/diametralClearance',
                value         = (self.designPressure, self.diametralClearance),
                validRange    = 'Both positive real'
            )

        pressurePsi = self.designPressure / PA_PER_PSIA

        # Interpolate the limit curve for the nearest tabulated durometers and blend
        durometerKeys = sorted(EXTRUSION_GAP_IN.keys())
        durometer     = float(np.clip(self.durometer, durometerKeys[0], durometerKeys[-1]))

        limits = []
        for key in durometerKeys:
            # Log-log interpolation, because the limit curve is close to a power law in pressure
            limitIn = np.exp(np.interp(np.log(max(pressurePsi, EXTRUSION_PRESSURE_PSI[0])),
                                       np.log(EXTRUSION_PRESSURE_PSI),
                                       np.log(EXTRUSION_GAP_IN[key])))
            limits.append(limitIn)

        limitIn                  = float(np.interp(durometer, durometerKeys, limits))
        self.maximumAllowableGap = limitIn * M_PER_IN
        self.backupRingRequired  = self.diametralClearance > self.maximumAllowableGap

        if self.backupRingRequired:
            self.compatibilityNotes.append(
                f'Diametral clearance {self.diametralClearance * 1.0e3:.4f} mm exceeds the extrusion limit of '
                f'{self.maximumAllowableGap * 1.0e3:.4f} mm at {pressurePsi:.0f} psi and {self.durometer:.0f} '
                f'durometer. A backup ring is required, or the clearance must be reduced.')

        if pressurePsi > EXTRUSION_PRESSURE_PSI[-1]:
            self.compatibilityNotes.append(
                f'Design pressure {pressurePsi:.0f} psi is above the tabulated extrusion data. The limit is '
                f'extrapolated; a backup ring should be assumed mandatory.')

        return {
            'maximumAllowableGap': self.maximumAllowableGap,
            'actualClearance':     self.diametralClearance,
            'backupRingRequired':  self.backupRingRequired
        }

    def checkCompatibility(self) -> list:

        '''

        Screen the seal material against the fluid and the temperature range.

        Fluid compatibility is a hard stop: an incompatible elastomer does not degrade gracefully,
        it swells, softens, hardens or dissolves, and in the case of Buna-N in hydrazine it actively
        catalyzes decomposition of the propellant it is supposed to be containing.

        The temperature check has two parts, and the second is the one people miss:

        1. The service temperature must lie inside the material's range.
        2. The COLDEST EXCURSION must stay above the glass transition. An elastomer below Tg is not
           a soft seal. It is a hard plastic ring with no compliance, and it will leak the instant
           the joint moves or the pressure changes. This is why a Viton seal that works perfectly at
           room temperature leaks on a cold morning, and why cryogenic static seals are metal,
           spring-energized PTFE, or heavily preloaded PCTFE.

        '''

        self.compatibilityNotes = []
        materialData = SEAL_MATERIALS[self.material.strip().lower()]

        # -- Fluid compatibility -- #
        if self.fluid:
            fluidKey = self.fluid.strip().upper()
            if fluidKey in [entry.upper() for entry in materialData.get('incompatible', [])]:
                raise CompatibilityError(
                    message  = (f'{materialData["name"]} is not compatible with {self.fluid}. '
                                f'{materialData["notes"]}'),
                    material = materialData['name'], fluid = self.fluid
                )

            compatibleList = [entry.upper() for entry in materialData.get('compatible', [])]
            if compatibleList and fluidKey not in compatibleList and 'EVERYTHING' not in compatibleList:
                self.compatibilityNotes.append(
                    f'{self.fluid} is not on the verified compatible list for {materialData["name"]} '
                    f'({", ".join(materialData["compatible"])}). Verify against the material supplier data '
                    f'before committing.')

        # -- Temperature range -- #
        if self.designTemperature > materialData['maximumTemperature']:
            raise CompatibilityError(
                message  = (f'{materialData["name"]} is rated to {materialData["maximumTemperature"]:.0f} K and the '
                            f'service temperature is {self.designTemperature:.0f} K.'),
                material = materialData['name'], fluid = self.fluid
            )

        if self.minimumTemperature < materialData['minimumTemperature']:
            raise CompatibilityError(
                message  = (f'{materialData["name"]} is rated down to {materialData["minimumTemperature"]:.0f} K and the '
                            f'coldest excursion is {self.minimumTemperature:.0f} K.'),
                material = materialData['name'], fluid = self.fluid
            )

        # -- Glass transition -- #
        glassTransition = materialData['glassTransition']
        if not np.isnan(glassTransition):
            if self.minimumTemperature < glassTransition:
                raise CompatibilityError(
                    message  = (f'{materialData["name"]} has a glass transition at {glassTransition:.0f} K and the '
                                f'coldest excursion is {self.minimumTemperature:.0f} K. Below Tg the material has no '
                                f'sealing compliance. Use a metal seal, a spring-energized PTFE seal, or PCTFE.'),
                    material = materialData['name'], fluid = self.fluid
                )
            if self.minimumTemperature < glassTransition + 20.0:
                self.compatibilityNotes.append(
                    f'Coldest excursion {self.minimumTemperature:.0f} K is within 20 K of the {glassTransition:.0f} K '
                    f'glass transition. Sealing force falls off steeply approaching Tg; carry margin.')

        # -- Cryogenic contraction mismatch -- #
        if self.minimumTemperature < 150.0:
            self.compatibilityNotes.append(
                f'{materialData["name"]} contracts {materialData["contraction"] * 100.0:.2f} percent to 77 K against '
                f'about 0.30 percent for the stainless gland. That differential comes straight out of the squeeze; '
                f'size the gland for the cold condition, not the ambient one.')

        return self.compatibilityNotes

    def calculatePermeation(self, species: str = 'He') -> float:

        '''

        Steady permeation leak rate through the seal cross section.

        An elastomer is a semi-permeable membrane. Gas dissolves into the high pressure face,
        diffuses through, and desorbs on the low pressure face. This is not a leak in the sense of a
        flow through a hole, and no amount of squeeze reduces it: the only levers are material,
        area, thickness and pressure.

            Q = K * A * dP / t

        with K the permeability coefficient [scc-cm / (cm^2 - s - atm)], A the exposed sealing area,
        dP the differential, and t the diffusion path length (approximately the squeezed cross
        section).

        For a short-duration system this is negligible. For a spacecraft that has to hold pressurant
        for ten years, it is often the dominant leak term and it is the reason long-life systems use
        metal seals or welded joints rather than o-rings.

        Permeation does not follow the molecular-mass scaling that a physical leak does, because it
        is a solution-diffusion process. Hydrogen permeates faster than helium despite being heavier,
        and nitrogen permeates at about 15 percent of the helium rate.

        '''

        if np.isnan(self.designPressure):
            raise InvalidInputError(
                message       = 'calculatePermeation needs the design pressure.',
                parameterName = 'designPressure', value = self.designPressure, validRange = 'Positive real'
            )

        materialData    = SEAL_MATERIALS[self.material.strip().lower()]
        permeability    = materialData['heliumPermeability'] * 1.0e-8   # scc-cm/(cm^2-s-atm)
        speciesFactor   = PERMEATION_SPECIES_FACTOR.get(species.strip().upper(), 1.0)

        # Exposed sealing circumference. Use the explicit value if given, otherwise the o-ring mean
        # circumference from the free inner diameter plus one cross section.
        exposedLength = self.exposedLength
        if np.isnan(exposedLength):
            if np.isnan(self.innerDiameter):
                raise InvalidInputError(
                    message       = 'calculatePermeation needs either exposedLength or the o-ring inner diameter.',
                    parameterName = 'innerDiameter', value = self.innerDiameter, validRange = 'Positive real'
                )
            exposedLength = np.pi * (self.innerDiameter + self.crossSectionDiameter)

        # Diffusion path is the squeezed cross section; the exposed face height is the contact width,
        # approximated as the chord of the squeezed ring, roughly 1.5 times the squeeze.
        pathLength  = self.grooveDepth if not np.isnan(self.grooveDepth) else self.crossSectionDiameter * 0.75
        contactWidth = 1.5 * self.squeezeAbsolute if not np.isnan(self.squeezeAbsolute) else 0.3 * self.crossSectionDiameter

        # Convert to CGS for the permeability units
        areaCm2         = (exposedLength * contactWidth) * 1.0e4
        pathLengthCm    = pathLength * 1.0e2
        differentialAtm = self.designPressure / PA_PER_ATM

        self.permeationRate = permeability * speciesFactor * areaCm2 * differentialAtm / pathLengthCm

        return self.permeationRate

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        materialData = SEAL_MATERIALS[self.material.strip().lower()]

        rows = [
            ['Seal type',              f'{self.sealType}'],
            ['Material',               f'{materialData["name"]}'],
            ['Durometer',              f'{self.durometer:.0f} Shore A'],
            ['Cross section W',        f'{self.crossSectionDiameter * 1.0e3:.4f} mm ({self.crossSectionDiameter / M_PER_IN:.4f} in)'],
            ['Free inner diameter',    f'{self.innerDiameter * 1.0e3:.3f} mm' if not np.isnan(self.innerDiameter) else 'unspecified'],
            ['Service fluid',          f'{self.fluid if self.fluid else "unspecified"}'],
            ['Design pressure',        f'{self.designPressure / 1.0e6:.4f} MPa' if not np.isnan(self.designPressure) else 'unspecified'],
            ['Design temperature',     f'{self.designTemperature:.1f} K'],
            ['Coldest excursion',      f'{self.minimumTemperature:.1f} K'],
            ['Glass transition',       f'{materialData["glassTransition"]:.0f} K' if not np.isnan(materialData['glassTransition']) else 'none (not an elastomer)']
        ]

        if not np.isnan(self.grooveDepth):
            rows.append(['Groove depth',        f'{self.grooveDepth * 1.0e3:.4f} mm ({self.grooveDepth / M_PER_IN:.4f} in)'])
            rows.append(['Groove width',        f'{self.grooveWidth * 1.0e3:.4f} mm ({self.grooveWidth / M_PER_IN:.4f} in)'])
            rows.append(['Squeeze',             f'{self.squeeze * 100.0:.2f} % ({self.squeezeAbsolute * 1.0e3:.4f} mm)'])
            rows.append(['Gland fill',          f'{self.glandFill * 100.0:.2f} %'])
        if not np.isnan(self.stretch):
            rows.append(['Installed stretch',   f'{self.stretch * 100.0:.2f} %'])

        if not np.isnan(self.maximumAllowableGap):
            rows.append(['Diametral clearance',  f'{self.diametralClearance * 1.0e3:.4f} mm'])
            rows.append(['Extrusion limit',      f'{self.maximumAllowableGap * 1.0e3:.4f} mm'])
            rows.append(['Backup ring required', f'{self.backupRingRequired}'])

        if not np.isnan(self.permeationRate):
            rows.append(['Permeation rate',      f'{self.permeationRate:.3e} scc/s'])
            rows.append(['  as mbar-L/s',        f'{leakRateConvert(self.permeationRate, "sccs", "mbarls"):.3e}'])
            rows.append(['  per year',           f'{self.permeationRate * 31557600.0 / 1000.0:.4f} std L/yr'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'SEAL DESIGN REPORT')

        report += f'\n\nMATERIAL NOTES\n{"-" * 60}\n{materialData["notes"]}\n'

        for note in self.compatibilityNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'sealReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.sealType.strip().lower() not in SQUEEZE_RANGES:
            raise InvalidInputError(
                message       = f'Unknown seal type \'{self.sealType}\'.',
                parameterName = 'sealType', value = self.sealType,
                validRange    = str(sorted(SQUEEZE_RANGES.keys()))
            )

        if self.material.strip().lower() not in SEAL_MATERIALS:
            raise InvalidInputError(
                message       = f'Unknown seal material \'{self.material}\'.',
                parameterName = 'material', value = self.material,
                validRange    = str(sorted(SEAL_MATERIALS.keys()))
            )

        if self.crossSectionDiameter <= 0.0:
            raise InvalidInputError(
                message       = 'O-ring cross section diameter must be positive.',
                parameterName = 'crossSectionDiameter', value = self.crossSectionDiameter,
                validRange    = 'Greater than 0 m'
            )
