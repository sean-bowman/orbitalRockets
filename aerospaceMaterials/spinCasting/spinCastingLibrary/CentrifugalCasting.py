
# -- CentrifugalCasting Class Definition -- #

'''

Rotational speed selection, solidification, and the inclusion migration that sets the bore machining
allowance.

Centrifugal casting is inherently clean, and the reason is worth stating precisely because it is the
whole argument for the process. Molten metal is spun in a mould, and the centrifugal field sorts the
contents by density: the dense metal is thrown outward and everything less dense than it, meaning
slag, oxide, gas and refractory, migrates inward to the bore.

The result is a casting whose outer wall is exceptionally sound and whose bore carries essentially
all the contamination. Machine the bore away and what is left is cleaner than a static casting of the
same alloy could be.

THE CALCULATION THAT JUSTIFIES A CLASS IS THE MACHINING ALLOWANCE, not the speed. Speed selection is
a chart lookup. The depth of the segregated bore layer follows from integrating Stokes settling in
the centrifugal field over the solidification time, and it is a real, non-obvious number that
decides how much stock has to be left on the bore. Leave too little and the inclusions stay in the
part.

See Also:
---------
CastingProcess : Investment, sand and die casting, and the casting factor ladder
HeatTreatment  : What follows the casting

Theory: docs/ProcessFundamentals.md, docs/SolidificationAndSegregation.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from spinCastingUtils import (applyInputs, formatReportTable, queryMaterial, GRAVITY,
                                  InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .spinCastingUtils import (applyInputs, formatReportTable, queryMaterial, GRAVITY,
                                   InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# G-factor is the centrifugal acceleration as a multiple of gravity at the outer wall. It is the
# single governing process parameter and the window is narrow at both ends.
#
#   Too low    Gravity still matters relative to the centrifugal field, so the melt slumps at the
#              top of the arc and rains down the bore. The casting comes out with a thick bottom,
#              a thin top and entrapped defects.
#   Too high   The melt is pinned so hard that it cannot feed, and longitudinal tearing and banding
#              appear. Very high G also throws the mould coating.

G_FACTOR_WINDOW = {
    'minimum':     40.0,    # [-], below this the melt rains at top of arc
    'preferred':   (60.0, 100.0),
    'maximum':     150.0    # [-], above this banding and tearing appear
}

# Casting alloy properties for the solidification and settling calculations. Viscosity is the melt
# value at the pouring temperature and it is what governs the Stokes velocity.

CASTING_ALLOYS = {
    'STEEL':     {'density': 7000.0, 'viscosity': 6.0e-3, 'meltingPoint': 1750.0,
                  'pourSuperheat': 100.0, 'chvorinovConstant': 2.0e6,
                  'note': 'The most common centrifugal casting alloy, mostly for pipe and rings.'},
    '316L':      {'density': 7000.0, 'viscosity': 6.5e-3, 'meltingPoint': 1663.0,
                  'pourSuperheat': 110.0, 'chvorinovConstant': 2.1e6,
                  'note': 'Austenitic stainless. Wide freezing range, so feeding matters.'},
    'INCONEL 625': {'density': 7600.0, 'viscosity': 7.0e-3, 'meltingPoint': 1623.0,
                    'pourSuperheat': 120.0, 'chvorinovConstant': 2.3e6,
                    'note': 'Nickel alloys need vacuum or inert melting to avoid oxide inclusions.'},
    'BRONZE':    {'density': 8000.0, 'viscosity': 4.0e-3, 'meltingPoint': 1300.0,
                  'pourSuperheat': 120.0, 'chvorinovConstant': 1.6e6,
                  'note': 'The classic centrifugal bushing and bearing material.'},
    '6061':      {'density': 2400.0, 'viscosity': 1.2e-3, 'meltingPoint': 925.0,
                  'pourSuperheat': 90.0, 'chvorinovConstant': 1.1e6,
                  'note': 'Aluminium centrifugal casting is possible and uncommon. The low density '
                          'means a higher speed is needed for the same G-factor benefit.'}
}

# Inclusion types and their densities. The density DIFFERENCE against the melt is what drives the
# migration, so a light oxide separates far faster than a heavy one.

INCLUSION_TYPES = {
    'alumina':       {'density': 3950.0, 'diameter': 50.0e-6,
                      'note': 'Al2O3. The commonest oxide inclusion in steel and nickel.'},
    'silica':        {'density': 2650.0, 'diameter': 80.0e-6,
                      'note': 'SiO2, usually eroded refractory or entrained sand.'},
    'slag':          {'density': 2800.0, 'diameter': 200.0e-6,
                      'note': 'Large and light, so it separates fastest.'},
    'gas porosity':  {'density': 5.0,    'diameter': 300.0e-6,
                      'note': 'Effectively zero density, so it migrates almost immediately.'},
    'refractory':    {'density': 2400.0, 'diameter': 150.0e-6,
                      'note': 'Eroded mould or ladle lining.'}
}

# Chvorinov exponent. The classic value is 2 for a shape freezing by conduction into the mould.
CHVORINOV_EXPONENT = 2.0

# Practical geometry limits for the process.
GEOMETRY_LIMITS = {
    'minimumWallThickness':   0.004,   # [m]
    'maximumLengthToDiameter': 8.0,    # [-], beyond this the pour cannot be distributed evenly
    'minimumBoreDiameter':    0.025    # [m]
}

# ------------------------------------------------------------------------------------------------ #

class CentrifugalCasting:

    '''

    Speed selection, solidification and bore machining allowance for a centrifugally cast cylinder.

    Primary Input Properties:
    -------------------------
    alloy : str
        Key into CASTING_ALLOYS
    outerDiameter / wallThickness / length : float
        Finished casting geometry [m]
    rotationalSpeed : float
        [rev/min]. When absent it is selected from the preferred G-factor window.

    Key Output Properties:
    ----------------------
    gFactor : float
        Centrifugal acceleration at the outer wall, as a multiple of gravity
    solidificationTime : float
        [s], from Chvorinov
    segregatedLayerDepth : float
        [m] of contaminated bore that must be machined away
    boreMachiningAllowance : float
        [m], the segregated depth plus a margin

    Public Methods:
    ---------------
    setInputs(inputs)                  Load a configuration dictionary
    selectRotationalSpeed()            Speed from the preferred G-factor window
    calculateGFactor()                 G-factor and the process window check
    calculateSolidification()          Chvorinov time and the cooling rate
    calculateInclusionMigration()      Stokes settling and the segregated layer depth
    calculateMachiningAllowance()      Bore stock, and the pour mass it implies
    checkGeometry()                    Against the process limits
    generateReport(outputDir)          Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material and Geometry -- #

        self.alloy            = '316L'     # [case insensitive string]
        self.outerDiameter    = 0.200      # [m], finished
        self.wallThickness    = 0.020      # [m], finished
        self.length           = 0.400      # [m]

        # -- Process -- #

        self.rotationalSpeed  = np.nan     # [rev/min], nan selects from the G-factor window
        self.pourTemperature  = np.nan     # [K], nan takes melting point plus the alloy superheat
        self.mouldTemperature = 473.15     # [K]
        self.inclusionType    = 'alumina'  # [case insensitive string]

        # -- Results -- #

        self.gFactor              = np.nan   # [-]
        self.solidificationTime   = np.nan   # [s]
        self.segregatedLayerDepth = np.nan   # [m]
        self.boreMachiningAllowance = np.nan  # [m]
        self.castingNotes         = []       # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: alloy.

        '''

        requiredParams = {
            'alloy': 'Casting alloy not provided.'
        }

        optionalParams = ['outerDiameter', 'wallThickness', 'length', 'rotationalSpeed',
                          'pourTemperature', 'mouldTemperature', 'inclusionType']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        properties = CASTING_ALLOYS[self.alloy]

        if np.isnan(self.pourTemperature):
            self.pourTemperature = properties['meltingPoint'] + properties['pourSuperheat']

    def selectRotationalSpeed(self, targetGFactor: float = 80.0) -> dict:

        '''

        Rotational speed for a target G-factor at the outer wall.

            G = omega^2 r / g          so        N = (30 / pi) sqrt(G g / r)

        The speed is set at the OUTER radius because that is where the field is strongest and where
        the metal has to be pinned. The bore sees a lower G-factor by the radius ratio, and on a
        thick walled casting that difference is large enough to matter for the inclusion migration.

        '''

        outerRadius = self.outerDiameter / 2.0

        speed = (30.0 / np.pi) * np.sqrt(targetGFactor * GRAVITY / outerRadius)

        self.rotationalSpeed = speed

        boreRadius  = outerRadius - self.wallThickness
        boreGFactor = targetGFactor * boreRadius / outerRadius

        return {'targetGFactor': targetGFactor, 'rotationalSpeed': speed,
                'angularVelocity': speed * np.pi / 30.0,
                'outerRadius': outerRadius, 'boreRadius': boreRadius,
                'boreGFactor': boreGFactor,
                'gFactorRatio': boreGFactor / targetGFactor}

    def calculateGFactor(self) -> dict:

        '''

        G-factor at the outer wall and at the bore, checked against the process window.

        The window is narrow at both ends and the two failure modes are different:

            Below 40    Gravity still competes with the centrifugal field, so the melt slumps at
                        the top of the arc and rains down the bore. The result is a thick bottom,
                        a thin top and entrapped defects, and it is the classic symptom of an
                        under-speeded casting.

            Above 150   The melt is pinned so hard it cannot feed, and longitudinal tearing and
                        banding appear. Very high speed also throws the mould coating.

        '''

        if np.isnan(self.rotationalSpeed):
            self.selectRotationalSpeed()

        outerRadius = self.outerDiameter / 2.0
        boreRadius  = outerRadius - self.wallThickness

        angular = self.rotationalSpeed * np.pi / 30.0

        self.gFactor = angular ** 2 * outerRadius / GRAVITY
        boreGFactor  = angular ** 2 * boreRadius / GRAVITY

        lower, upper = G_FACTOR_WINDOW['preferred']

        if self.gFactor < G_FACTOR_WINDOW['minimum']:
            regime = 'too low'
            self.castingNotes.append(
                f'G-factor of {self.gFactor:.0f} is below the {G_FACTOR_WINDOW["minimum"]:.0f} '
                f'minimum. Gravity still competes with the centrifugal field, so the melt will '
                f'slump at the top of the arc and rain down the bore. The casting comes out with a '
                f'thick bottom, a thin top, and entrapped defects.')
        elif self.gFactor > G_FACTOR_WINDOW['maximum']:
            regime = 'too high'
            self.castingNotes.append(
                f'G-factor of {self.gFactor:.0f} exceeds the {G_FACTOR_WINDOW["maximum"]:.0f} '
                f'maximum. The melt is pinned too hard to feed, which produces longitudinal tearing '
                f'and banding, and the mould coating can be thrown.')
        elif lower <= self.gFactor <= upper:
            regime = 'preferred'
        else:
            regime = 'acceptable'

        return {'rotationalSpeed': self.rotationalSpeed, 'gFactor': self.gFactor,
                'boreGFactor': boreGFactor, 'regime': regime,
                'preferredWindow': G_FACTOR_WINDOW['preferred'],
                'minimum': G_FACTOR_WINDOW['minimum'], 'maximum': G_FACTOR_WINDOW['maximum']}

    def calculateSolidification(self) -> dict:

        '''

        Chvorinov solidification time from the modulus.

            t = B (V / A)^n            n = 2

        The volume to area ratio is the casting modulus, and it is the single geometric parameter
        that governs freezing time. A centrifugal casting is a cylindrical shell cooling almost
        entirely through the outer surface into the mould, because the bore is exposed to air and
        radiates comparatively little.

        THE SOLIDIFICATION TIME IS THE INTEGRATION WINDOW for the inclusion migration. A thin wall
        freezes fast and gives the inclusions little time to separate, which is why a thin
        centrifugal casting is less clean than a thick one at the same speed.

        '''

        properties = CASTING_ALLOYS[self.alloy]

        outerRadius = self.outerDiameter / 2.0
        boreRadius  = outerRadius - self.wallThickness

        volume = np.pi * (outerRadius ** 2 - boreRadius ** 2) * self.length

        # Heat leaves almost entirely through the outer surface into the mould. The bore is exposed
        # to air, so it is counted at a small fraction of its geometric area.
        outerArea = 2.0 * np.pi * outerRadius * self.length
        boreArea  = 2.0 * np.pi * boreRadius * self.length
        effectiveArea = outerArea + 0.15 * boreArea

        modulus = volume / effectiveArea

        self.solidificationTime = properties['chvorinovConstant'] * modulus ** CHVORINOV_EXPONENT

        superheat   = self.pourTemperature - properties['meltingPoint']
        coolingRate = superheat / max(self.solidificationTime, 1.0e-9)

        return {'volume': volume, 'effectiveArea': effectiveArea, 'modulus': modulus,
                'chvorinovConstant': properties['chvorinovConstant'],
                'solidificationTime': self.solidificationTime,
                'pourTemperature': self.pourTemperature, 'superheat': superheat,
                'averageCoolingRate': coolingRate,
                'castingMass': volume * properties['density']}

    def calculateInclusionMigration(self, inclusionVolumeFraction: float = 0.0010) -> dict:

        '''

        Inclusion escape against the advancing solidification front, and the depth of the
        contaminated bore layer that results.

        THE CORRECT QUESTION IS NOT HOW FAR AN INCLUSION TRAVELS. In a centrifugal field the Stokes
        velocity is enormous, tens of millimetres per second for an ordinary oxide, so a free
        particle crosses the whole wall in under a second. Integrating that velocity over the
        solidification time gives a distance of metres, which is meaningless.

        The question is whether an inclusion ESCAPES TO THE BORE BEFORE THE SOLIDIFICATION FRONT
        ENGULFS IT. Two competing velocities:

            v_stokes = d^2 (rho_melt - rho_inclusion) omega^2 r / (18 mu)       inward, the escape
            v_front  = wallThickness / t_solidification                          inward, the capture

        The ratio of the two is the capture number, and it is the figure of merit for the process:

            captureNumber = v_stokes / v_front

        Well above one and essentially every inclusion reaches the bore, which is exactly why a
        centrifugal casting is cleaner than a static one of the same alloy. Near or below one and
        the front outruns the inclusions, they are frozen in place, and the process has bought
        nothing.

        The segregated layer depth then follows from a MASS BALANCE rather than from kinematics. All
        the inclusions originally distributed through the wall end up concentrated in a thin layer at
        the bore, so its thickness is set by the inclusion volume fraction and how densely the
        escaped material packs:

            segregatedDepth = wallThickness * inclusionVolumeFraction / packingFraction

        That layer is thin, typically a few tenths of a millimetre, and it is not usually what
        governs the machining allowance. The bore is also a free surface, so it carries roughness,
        oxide and gas porosity, and that free surface condition is the larger of the two terms.
        Both are reported and calculateMachiningAllowance takes the larger.

        '''

        if np.isnan(self.solidificationTime):
            self.calculateSolidification()

        properties = CASTING_ALLOYS[self.alloy]
        inclusion  = INCLUSION_TYPES[self.inclusionType]

        outerRadius = self.outerDiameter / 2.0
        boreRadius  = outerRadius - self.wallThickness
        meanRadius  = 0.5 * (outerRadius + boreRadius)

        angular = self.rotationalSpeed * np.pi / 30.0

        densityDifference = properties['density'] - inclusion['density']

        # Stokes velocity in the centrifugal field, evaluated at the mean radius. Positive means
        # inward, towards the bore, because the inclusion is the lighter phase.
        stokesVelocity = (inclusion['diameter'] ** 2 * densityDifference * angular ** 2 *
                          meanRadius / (18.0 * properties['viscosity']))

        # The solidification front sweeps the wall over the freezing time.
        frontVelocity = self.wallThickness / max(self.solidificationTime, 1.0e-9)

        captureNumber = stokesVelocity / frontVelocity

        # Escape fraction. Well above one and everything escapes; below one the front wins. The
        # transition is not sharp because the front is not planar and the melt is mushy near it.
        escapeFraction = float(np.clip(1.0 - np.exp(-captureNumber / 3.0), 0.0, 1.0))

        # Mass balance on the escaped inclusions, concentrated at the bore.
        packingFraction = 0.30      # [-], loose packing of the segregated phase

        inclusionLayer = (self.wallThickness * inclusionVolumeFraction * escapeFraction /
                          packingFraction)

        # The bore is a free surface, so it carries roughness, oxide skin and subsurface gas
        # porosity independently of the inclusion content. This is usually the larger term.
        freeSurfaceLayer = 0.0015 + 0.02 * self.wallThickness

        self.segregatedLayerDepth = max(inclusionLayer, freeSurfaceLayer)

        result = {'inclusionType': self.inclusionType,
                  'inclusionDensity': inclusion['density'],
                  'inclusionDiameter': inclusion['diameter'],
                  'meltDensity': properties['density'],
                  'densityDifference': densityDifference,
                  'stokesVelocity': stokesVelocity,
                  'frontVelocity': frontVelocity,
                  'captureNumber': captureNumber,
                  'escapeFraction': escapeFraction,
                  'inclusionVolumeFraction': inclusionVolumeFraction,
                  'inclusionLayerDepth': inclusionLayer,
                  'freeSurfaceLayerDepth': freeSurfaceLayer,
                  'segregatedLayerDepth': self.segregatedLayerDepth,
                  'governingTerm': 'inclusion accumulation' if inclusionLayer >= freeSurfaceLayer
                                   else 'free surface condition',
                  'note': inclusion['note']}

        if captureNumber < 3.0:
            self.castingNotes.append(
                f'The capture number is {captureNumber:.1f}, so the solidification front is fast '
                f'enough to trap inclusions before they reach the bore and only '
                f'{escapeFraction * 100.0:.0f} percent escape. The centrifugal cleaning benefit is '
                f'largely lost. A higher G-factor, a thicker section or more superheat all slow the '
                f'front relative to the migration.')
        elif captureNumber > 100.0:
            self.castingNotes.append(
                f'The capture number is {captureNumber:.0f}, so essentially every inclusion of this '
                f'size reaches the bore well ahead of the front. This is the condition the process '
                f'exists to produce, and it is why a centrifugal casting is cleaner than a static '
                f'one of the same alloy.')

        return result

    def calculateMachiningAllowance(self, tolerancePerSurface: float = 0.0015) -> dict:

        '''

        Bore machining allowance, and the as-cast dimensions and pour mass it implies.

        The allowance is the BINDING CONSTRAINT of two:

            segregation    the contaminated bore layer, which must be removed entirely
            tolerance      the dimensional stock any casting needs

        Taking the maximum rather than the sum is correct, because removing the segregated layer
        also removes the dimensional stock. Which one binds is the useful output, and on a well
        spun casting it is usually the segregation.

        '''

        if np.isnan(self.segregatedLayerDepth):
            self.calculateInclusionMigration()

        properties = CASTING_ALLOYS[self.alloy]

        segregationAllowance = self.segregatedLayerDepth
        toleranceAllowance   = tolerancePerSurface

        self.boreMachiningAllowance = max(segregationAllowance, toleranceAllowance)
        binding = 'segregation' if segregationAllowance >= toleranceAllowance else 'tolerance'

        outerRadius = self.outerDiameter / 2.0
        finishedBoreRadius = outerRadius - self.wallThickness

        asCastBoreRadius   = finishedBoreRadius - self.boreMachiningAllowance
        asCastOuterRadius  = outerRadius + tolerancePerSurface

        asCastVolume = np.pi * (asCastOuterRadius ** 2 - asCastBoreRadius ** 2) * self.length
        finishedVolume = np.pi * (outerRadius ** 2 - finishedBoreRadius ** 2) * self.length

        pourMass = asCastVolume * properties['density'] * 1.05    # 5 percent for the sprue and loss

        return {'segregationAllowance': segregationAllowance,
                'toleranceAllowance': toleranceAllowance,
                'boreMachiningAllowance': self.boreMachiningAllowance,
                'bindingConstraint': binding,
                'asCastOuterDiameter': 2.0 * asCastOuterRadius,
                'asCastBoreDiameter': 2.0 * asCastBoreRadius,
                'asCastWallThickness': asCastOuterRadius - asCastBoreRadius,
                'asCastVolume': asCastVolume, 'finishedVolume': finishedVolume,
                'pourMass': pourMass,
                'buyToFly': pourMass / (finishedVolume * properties['density'])}

    def checkGeometry(self) -> dict:

        '''

        Geometry against the practical limits of the process.

        '''

        boreDiameter    = self.outerDiameter - 2.0 * self.wallThickness
        lengthToDiameter = self.length / self.outerDiameter

        issues = []

        if self.wallThickness < GEOMETRY_LIMITS['minimumWallThickness']:
            issues.append(
                f'Wall {self.wallThickness * 1.0e3:.1f} mm is below the '
                f'{GEOMETRY_LIMITS["minimumWallThickness"] * 1.0e3:.0f} mm minimum. A thinner '
                f'section freezes before the melt distributes.')

        if boreDiameter < GEOMETRY_LIMITS['minimumBoreDiameter']:
            issues.append(
                f'Bore {boreDiameter * 1.0e3:.0f} mm is below the '
                f'{GEOMETRY_LIMITS["minimumBoreDiameter"] * 1.0e3:.0f} mm minimum.')

        if lengthToDiameter > GEOMETRY_LIMITS['maximumLengthToDiameter']:
            issues.append(
                f'Length to diameter of {lengthToDiameter:.1f} exceeds '
                f'{GEOMETRY_LIMITS["maximumLengthToDiameter"]:.0f}. The pour cannot be distributed '
                f'evenly along the mould, so the wall will taper.')

        self.castingNotes.extend(issues)

        return {'boreDiameter': boreDiameter, 'lengthToDiameter': lengthToDiameter,
                'issues': issues, 'feasible': not issues}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        gFactor    = self.calculateGFactor()
        solidify   = self.calculateSolidification()
        migration  = self.calculateInclusionMigration()
        allowance  = self.calculateMachiningAllowance()

        properties = CASTING_ALLOYS[self.alloy]

        rows = [
            ['Alloy',                  f'{self.alloy}'],
            ['Finished OD x wall x L', f'{self.outerDiameter * 1.0e3:.0f} x '
                                       f'{self.wallThickness * 1.0e3:.1f} x '
                                       f'{self.length * 1.0e3:.0f} mm'],
            ['Rotational speed',       f'{self.rotationalSpeed:.0f} rev/min'],
            ['G-factor at OD',         f'{self.gFactor:.0f} ({gFactor["regime"]})'],
            ['G-factor at bore',       f'{gFactor["boreGFactor"]:.0f}'],
            ['Pour temperature',       f'{self.pourTemperature - 273.15:.0f} degC '
                                       f'({solidify["superheat"]:.0f} K superheat)'],
            ['Casting modulus',        f'{solidify["modulus"] * 1.0e3:.2f} mm'],
            ['Solidification time',    f'{self.solidificationTime:.1f} s'],
            ['Inclusion',              f'{self.inclusionType}, '
                                       f'{migration["inclusionDiameter"] * 1.0e6:.0f} um'],
            ['Stokes velocity',        f'{migration["stokesVelocity"] * 1.0e3:.2f} mm/s inward'],
            ['Front velocity',         f'{migration["frontVelocity"] * 1.0e3:.4f} mm/s inward'],
            ['Capture number',         f'{migration["captureNumber"]:.0f} '
                                       f'({migration["escapeFraction"] * 100.0:.0f} % escape)'],
            ['Segregated bore layer',  f'{self.segregatedLayerDepth * 1.0e3:.2f} mm '
                                       f'(governs: {migration["governingTerm"]})'],
            ['Bore machining allowance', f'{self.boreMachiningAllowance * 1.0e3:.2f} mm '
                                         f'(binding: {allowance["bindingConstraint"]})'],
            ['As-cast bore',           f'{allowance["asCastBoreDiameter"] * 1.0e3:.1f} mm'],
            ['Pour mass',              f'{allowance["pourMass"]:.2f} kg'],
            ['Buy-to-fly',             f'{allowance["buyToFly"]:.2f} : 1']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'CENTRIFUGAL CASTING')

        report += f'\n\nALLOY NOTE\n{"-" * 60}\n{properties["note"]}\n'
        report += f'\nINCLUSION NOTE\n{"-" * 60}\n{migration["note"]}\n'

        for note in self.castingNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'centrifugalCasting.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = ' '.join(self.alloy.strip().upper().split())

        if key not in CASTING_ALLOYS:
            raise InvalidInputError(
                message       = f'No casting properties for \'{self.alloy}\'. Melt viscosity and '
                                f'the Chvorinov constant cannot be assumed.',
                parameterName = 'alloy', value = self.alloy,
                validRange    = str(sorted(CASTING_ALLOYS.keys()))
            )

        self.alloy = key

        if self.inclusionType not in INCLUSION_TYPES:
            raise InvalidInputError(
                message       = f'Unknown inclusion type \'{self.inclusionType}\'.',
                parameterName = 'inclusionType', value = self.inclusionType,
                validRange    = str(sorted(INCLUSION_TYPES.keys()))
            )

        if self.wallThickness >= self.outerDiameter / 2.0:
            raise InvalidInputError(
                message       = f'A wall of {self.wallThickness * 1.0e3:.1f} mm on a '
                                f'{self.outerDiameter * 1.0e3:.0f} mm outer diameter leaves no bore. '
                                f'Centrifugal casting produces a hollow section by definition.',
                parameterName = 'wallThickness', value = self.wallThickness,
                validRange    = f'Less than {self.outerDiameter / 2.0 * 1.0e3:.0f} mm'
            )

        for name, value in (('outerDiameter', self.outerDiameter),
                            ('wallThickness', self.wallThickness), ('length', self.length)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0 m'
                )
