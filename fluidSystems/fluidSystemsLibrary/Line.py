
# -- Line Class Definition -- #

'''

Pipe and tube segment sizing, pressure drop, and wall thickness.

A line is the least glamorous component in a feed system and the one that most often decides
whether the system works. Line sizing sets the pressure budget, the pressure budget sets the tank
pressure, the tank pressure sets the tank wall thickness, and the tank is usually the heaviest
single item on the vehicle. Undersizing a line by one tube size can cost more mass than every valve
in the system put together.

This class covers the three things you actually do with a line:

1. Pressure drop      Darcy-Weisbach friction plus minor losses plus elevation, marched along the
                      line so that density changes with pressure are captured. Handles liquids,
                      compressible gases, and the choking limit at the exit of a gas line.

2. Sizing             Find the inner diameter that meets a velocity limit, a pressure drop budget,
                      or both, then snap to the nearest standard tube size.

3. Wall thickness     ASME B31.3 pressure design thickness with mill tolerance, and the AIAA S-080
                      style proof and burst factors that govern flight hardware.

The pressure drop calculation marches the line in stations rather than using a single lumped
density. That matters more than it sounds: a long gas line loses density as it loses pressure, the
velocity rises to conserve mass, and the friction loss per unit length rises with the square of
velocity. A lumped calculation using inlet density will under-predict the drop, and the error grows
with the pressure ratio.

See Also:
---------
Fitting     : Discrete joint losses and connector selection
Orifice     : Local restriction rather than distributed friction
WaterHammer : Transient surge from changing the velocity in this line
Insulation  : Heat leak into or out of this line

Theory: docs/PipeRoutingAndSizing.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable, frictionFactor,
                       roughnessTable, materialProperties, b31_3WallThickness, criticalPressureRatio,
                       R_UNIVERSAL, speciesMolarMass, GRAVITY, M_PER_IN,
                       InvalidInputError, PressureDropError, ChokedFlowError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable, frictionFactor,
                        roughnessTable, materialProperties, b31_3WallThickness, criticalPressureRatio,
                        R_UNIVERSAL, speciesMolarMass, GRAVITY, M_PER_IN,
                        InvalidInputError, PressureDropError, ChokedFlowError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Equivalent length ratios L/D for common fittings, from Crane Technical Paper 410. Multiply by the
# line inner diameter to get an added length, or by the friction factor to get a K value.
#
# The equivalent length method and the K method give the same answer in fully turbulent flow and
# diverge in laminar flow, where the K method is more nearly right. Both are here; the class uses
# whichever the user supplies.
EQUIVALENT_LENGTH_RATIOS = {
    'elbow 90 standard':     30,    # r/D = 1
    'elbow 90 long radius':  20,    # r/D = 1.5
    'elbow 45':              16,
    'bend 90 r/d=3':         12,    # smooth tube bend, the usual aerospace case
    'bend 90 r/d=5':         10,
    'return bend 180':       50,
    'tee run':               20,    # flow straight through the run
    'tee branch':            60,    # flow turning into or out of the branch
    'gate valve open':        8,
    'ball valve open':        3,
    'globe valve open':     340,    # the reason globe valves are never used as isolation valves
    'angle valve open':     145,
    'butterfly valve open':  45,
    'check valve swing':    100,
    'check valve lift':     600,
    'plug valve open':       18
}

# Loss coefficients K for entrance, exit and other geometry-defined features. These are area-ratio
# or shape driven rather than fitting-catalog driven.
LOSS_COEFFICIENTS = {
    'entrance sharp':        0.50,
    'entrance rounded':      0.04,   # r/D >= 0.15
    'entrance reentrant':    0.78,   # Borda, tube projecting into the tank
    'exit':                  1.00,   # all velocity head is lost to the downstream volume
    'flexhose per meter':    0.60,   # convoluted metal hose, on top of the friction term
    'an flare union':        0.20,   # AN/MS 37 degree flared union
    'vcr union':             0.15,   # metal gasket face seal, near full bore
    'quick disconnect':      2.00    # highly design dependent; measure yours
}

# Recommended maximum velocities [m/s]. These are not physics, they are accumulated operational
# experience, and the ignition-hazard entries in particular are hard limits rather than guidance.
VELOCITY_LIMITS = {
    'liquid general':        10.0,   # above this, minor losses and erosion start to dominate
    'liquid pump suction':    3.0,   # protect NPSH; the suction line is where cavitation begins
    'liquid propellant fill': 5.0,   # limits surge energy when a fill valve slams
    'lox':                    7.6,   # 25 ft/s, NASA guidance to limit particle impact ignition energy
    'lox clean system':      12.2,   # 40 ft/s, only with a verified cleanliness level and no soft goods
    'gox carbon steel':      30.0,   # ASTM G88 / NASA-STD-6001 impingement guidance
    'gaseous general':      100.0,   # noise and erosion practical limit
    'cryogenic two-phase':    3.0,   # chilldown lines, keep the slug velocity down
    'hydrazine':              6.0    # limits adiabatic compression energy on valve closure
}

# Standard seamless tube sizes commonly stocked in 316L, as (outer diameter, wall thickness) in
# inches. This is the aerospace instrumentation and feed line set, not the pipe schedule set.
STANDARD_TUBE_SIZES_IN = [
    (0.125, 0.028), (0.125, 0.035),
    (0.1875, 0.035),
    (0.250, 0.028), (0.250, 0.035), (0.250, 0.049), (0.250, 0.065),
    (0.375, 0.035), (0.375, 0.049), (0.375, 0.065),
    (0.500, 0.035), (0.500, 0.049), (0.500, 0.065), (0.500, 0.083),
    (0.625, 0.049), (0.625, 0.065), (0.625, 0.083),
    (0.750, 0.049), (0.750, 0.065), (0.750, 0.083), (0.750, 0.109),
    (1.000, 0.065), (1.000, 0.083), (1.000, 0.109), (1.000, 0.120),
    (1.250, 0.083), (1.250, 0.109), (1.250, 0.120),
    (1.500, 0.083), (1.500, 0.109), (1.500, 0.120),
    (2.000, 0.109), (2.000, 0.120), (2.000, 0.156)
]

class Line:

    '''

    Steady-state pressure drop, sizing and wall thickness for a single line segment.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    massFlow : float
        Mass flow rate through the line [kg/s]
    length : float
        Developed length of the segment [m]
    innerDiameter : float
        Tube or pipe inner diameter [m]. Leave unset when sizing.
    inletPressure : float
        Static pressure at the inlet [Pa, absolute]
    inletTemperature : float
        Fluid temperature at the inlet [K]
    surface : str
        Key into roughnessTable, or set absoluteRoughness directly
    elevationChange : float
        Outlet elevation minus inlet elevation [m]. Positive is uphill.
    fittings : dict
        {fitting name: count} keyed into EQUIVALENT_LENGTH_RATIOS
    lossCoefficients : dict
        {feature name: count} keyed into LOSS_COEFFICIENTS
    material : str
        Key into materialProperties, for the wall thickness calculation
    designPressure : float
        Maximum expected operating pressure for wall sizing [Pa, gauge]

    Key Output Properties:
    ----------------------
    pressureDrop : float
        Total inlet-to-outlet pressure loss [Pa]
    outletPressure : float
        Static pressure at the outlet [Pa, absolute]
    velocity : float
        Bulk velocity at the outlet, the worst case in a compressible line [m/s]
    reynolds : float
        Reynolds number at the inlet [-]
    machNumber : float
        Outlet Mach number, gases only [-]
    frictionPressureDrop / minorPressureDrop / elevationPressureDrop : float
        Breakdown of the total [Pa]
    wallThickness : dict
        B31.3 pressure design, minimum and ordered thickness [m]

    Public Methods:
    ---------------
    setInputs(inputs)            Load a configuration dictionary
    calculatePressureDrop()      March the line and return the total loss
    sizeDiameter()               Find the ID meeting a velocity limit or dP budget
    selectStandardTube()         Snap the sized ID to a real stocked tube size
    calculateWallThickness()     ASME B31.3 pressure design thickness
    calculateMass()              Line dry mass from the selected geometry
    generateReport(outputDir)    Formatted results table

    Typical Workflow:
    -----------------
    >>> feedLine = Line()
    >>> feedLine.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'length': 2.5,
    ...                     'inletPressure': 2.4e6, 'inletTemperature': 293.15,
    ...                     'fittings': {'bend 90 r/D=3': 4, 'tee run': 1},
    ...                     'allowablePressureDrop': 5.0e4})
    >>> feedLine.sizeDiameter()
    >>> feedLine.selectStandardTube()
    >>> feedLine.calculateWallThickness()
    >>> print(feedLine.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid and Flow -- #

        self.fluid                  = ''      # [case sensitive string]
        self.massFlow               = np.nan  # [kg/s]
        self.inletPressure          = np.nan  # [Pa, absolute]
        self.inletTemperature       = np.nan  # [K]

        # -- Geometry -- #

        # Inner diameter drives everything. Pressure drop scales as 1/D^5 at constant mass flow in
        # turbulent flow, so a 10 percent diameter error is a 60 percent pressure drop error. This
        # is the single most sensitive number in a feed system model.
        self.innerDiameter          = np.nan  # [m]
        self.outerDiameter          = np.nan  # [m]
        self.wallThicknessActual    = np.nan  # [m], as-built, set by selectStandardTube
        self.length                 = np.nan  # [m], developed length including bends
        self.elevationChange        = 0.0     # [m], outlet minus inlet, positive uphill
        self.surface                = 'drawn tube'  # key into roughnessTable
        self.absoluteRoughness      = np.nan  # [m], overrides the surface lookup if set

        # -- Minor Losses -- #

        # Two ways to specify the same physics. fittings uses the Crane equivalent length method;
        # lossCoefficients uses direct K values. Both can be used together.
        self.fittings               = {}      # {name: count} into EQUIVALENT_LENGTH_RATIOS
        self.lossCoefficients       = {}      # {name: count} into LOSS_COEFFICIENTS
        self.additionalK            = 0.0     # [-], catch-all for measured or vendor K values

        # -- Sizing Targets -- #

        self.allowablePressureDrop  = np.nan  # [Pa], sizing constraint
        self.velocityLimit          = np.nan  # [m/s], sizing constraint
        self.service                = 'liquid general'  # key into VELOCITY_LIMITS

        # -- Structural -- #

        self.material               = '316L'  # key into materialProperties
        self.designPressure         = np.nan  # [Pa, gauge], maximum expected operating pressure
        self.designTemperature      = np.nan  # [K], defaults to inlet temperature
        self.jointEfficiency        = 1.0     # [-], B31.3 E, 1.0 for seamless tube
        self.corrosionAllowance     = 0.0     # [m]
        self.millTolerance          = 0.10    # [-], 0.10 for tube, 0.125 for pipe

        # -- Numerics -- #

        # Number of axial stations. Twenty is plenty for a liquid line and marginal for a long gas
        # line with a large pressure ratio; the class warns if the per-station pressure change is
        # large enough that the discretization is contributing error.
        self.numberOfStations       = 20      # [-]

        # -- Results -- #

        self.pressureDrop           = np.nan  # [Pa]
        self.outletPressure         = np.nan  # [Pa, absolute]
        self.frictionPressureDrop   = np.nan  # [Pa]
        self.minorPressureDrop      = np.nan  # [Pa]
        self.elevationPressureDrop  = np.nan  # [Pa]
        self.accelerationPressureDrop = np.nan  # [Pa], compressible lines only
        self.velocity               = np.nan  # [m/s], outlet
        self.inletVelocity          = np.nan  # [m/s]
        self.reynolds               = np.nan  # [-], inlet
        self.frictionFactorValue    = np.nan  # [-], inlet
        self.relativeRoughness      = np.nan  # [-]
        self.machNumber             = np.nan  # [-], outlet, gases only
        self.totalLossCoefficient   = np.nan  # [-], summed minor loss K
        self.equivalentLength       = np.nan  # [m], added by the fittings
        self.isChoked               = False   # [-], gas line choked at the exit
        self.isLiquid               = True    # [-]
        self.wallThickness          = {}      # dict from b31_3WallThickness
        self.dryMass                = np.nan  # [kg]
        self.selectedTube           = ''      # human readable OD x wall

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, massFlow, length, inletPressure, inletTemperature.

        '''

        requiredParams = {
            'fluid':            'Line fluid species not provided.',
            'massFlow':         'Line mass flow rate not provided.',
            'length':           'Line developed length not provided.',
            'inletPressure':    'Line inlet pressure not provided.',
            'inletTemperature': 'Line inlet temperature not provided.'
        }

        optionalParams = ['innerDiameter', 'outerDiameter', 'elevationChange', 'surface',
                          'absoluteRoughness', 'fittings', 'lossCoefficients', 'additionalK',
                          'allowablePressureDrop', 'velocityLimit', 'service', 'material',
                          'designPressure', 'designTemperature', 'jointEfficiency',
                          'corrosionAllowance', 'millTolerance', 'numberOfStations']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._evaluateFluidState()

    def calculatePressureDrop(self) -> float:

        '''

        March the line from inlet to outlet and accumulate the pressure loss.

        At each station the local density and viscosity are re-evaluated at the local pressure, the
        Reynolds number and friction factor are recomputed, and the incremental loss is added. Four
        contributions are tracked separately so the report can show where the budget went:

        friction      f * (L/D) * rho * V^2 / 2, distributed along the line
        minor         K_total * rho * V^2 / 2, lumped at the inlet station
        elevation     rho * g * dz, the static head
        acceleration  rho_out * V_out^2 - rho_in * V_in^2, momentum change in a compressible line

        For a gas line the outlet Mach number is checked against unity. A line that chokes at its
        exit cannot pass the requested mass flow no matter what the downstream pressure is, and
        ChokedFlowError is raised rather than returning a nonsense negative pressure.

        '''

        if np.isnan(self.innerDiameter):
            raise InvalidInputError(
                message       = 'calculatePressureDrop needs an inner diameter. Set innerDiameter, or call sizeDiameter() first.',
                parameterName = 'innerDiameter', value = self.innerDiameter,
                validRange    = 'Positive real'
            )

        flowArea               = np.pi * self.innerDiameter**2 / 4.0
        massFlux               = self.massFlow / flowArea          # [kg/s-m^2], constant along the line
        self.relativeRoughness = self._roughness() / self.innerDiameter

        # Minor losses, evaluated once. Equivalent lengths are added to the physical length; K values
        # are applied to the inlet velocity head.
        self.equivalentLength     = self._equivalentLength()
        self.totalLossCoefficient = self._totalLossCoefficient()

        effectiveLength = self.length + self.equivalentLength
        stationLength   = effectiveLength / self.numberOfStations

        localPressure     = self.inletPressure
        stationElevation  = self.elevationChange / self.numberOfStations

        frictionLoss  = 0.0
        elevationLoss = 0.0

        inletDensity       = float(fluidProps(self.fluid, 'TP', 'D', self.inletTemperature, self.inletPressure))
        self.inletVelocity = massFlux / inletDensity
        self.reynolds      = massFlux * self.innerDiameter / float(fluidProps(self.fluid, 'TP', 'VIS', self.inletTemperature, self.inletPressure))
        self.frictionFactorValue = frictionFactor(self.reynolds, self.relativeRoughness)

        # Minor loss on inlet velocity head
        minorLoss = self.totalLossCoefficient * inletDensity * self.inletVelocity**2 / 2.0

        for station in range(self.numberOfStations):

            # Local properties. The flow is treated as isothermal, which is the right assumption for
            # a line short enough that the wall holds the fluid at ambient. For a long insulated gas
            # line the expansion is closer to adiabatic and this under-predicts the temperature drop.
            localDensity   = float(fluidProps(self.fluid, 'TP', 'D',   self.inletTemperature, localPressure))
            localViscosity = float(fluidProps(self.fluid, 'TP', 'VIS', self.inletTemperature, localPressure))

            localVelocity  = massFlux / localDensity
            localReynolds  = massFlux * self.innerDiameter / localViscosity
            localFriction  = frictionFactor(localReynolds, self.relativeRoughness)

            stationFriction  = localFriction * (stationLength / self.innerDiameter) * localDensity * localVelocity**2 / 2.0
            stationElevationLoss = localDensity * GRAVITY * stationElevation

            frictionLoss  += stationFriction
            elevationLoss += stationElevationLoss

            localPressure -= (stationFriction + stationElevationLoss)

            # Apply the lumped minor loss at the first station so downstream densities see it
            if station == 0:
                localPressure -= minorLoss

            if localPressure <= 0.0:
                raise PressureDropError(
                    message = (f'Line pressure went below absolute zero at station {station + 1} of '
                               f'{self.numberOfStations}. The requested {self.massFlow:.4g} kg/s cannot pass '
                               f'through {self.innerDiameter * 1.0e3:.3f} mm ID over {self.length:.3g} m at this inlet pressure.'),
                    context = createErrorContext(component = 'Line', fluid = self.fluid,
                                                 massFlow = self.massFlow,
                                                 upstreamPressure = self.inletPressure,
                                                 temperature = self.inletTemperature,
                                                 innerDiameter = self.innerDiameter,
                                                 length = self.length)
                )

        outletDensity = float(fluidProps(self.fluid, 'TP', 'D', self.inletTemperature, localPressure))
        self.velocity = massFlux / outletDensity

        # Momentum (acceleration) term. Zero for an incompressible liquid, significant for a gas
        # line with a meaningful pressure ratio.
        self.accelerationPressureDrop = massFlux * (self.velocity - self.inletVelocity)

        self.frictionPressureDrop  = frictionLoss
        self.minorPressureDrop     = minorLoss
        self.elevationPressureDrop = elevationLoss
        self.outletPressure        = localPressure - self.accelerationPressureDrop
        self.pressureDrop          = self.inletPressure - self.outletPressure

        # Choking check for gases: compare the outlet velocity to the local speed of sound
        if not self.isLiquid:
            speedOfSound    = float(fluidProps(self.fluid, 'TP', 'W', self.inletTemperature, max(self.outletPressure, 1.0)))
            self.machNumber = self.velocity / speedOfSound
            self.isChoked   = self.machNumber >= 1.0

            if self.isChoked:
                raise ChokedFlowError(
                    message = (f'Gas line chokes at the exit: outlet Mach {self.machNumber:.3f}. The line cannot pass '
                               f'{self.massFlow:.4g} kg/s at {self.innerDiameter * 1.0e3:.3f} mm ID regardless of '
                               f'downstream pressure. Increase the diameter.'),
                    context = createErrorContext(component = 'Line', fluid = self.fluid,
                                                 massFlow = self.massFlow,
                                                 upstreamPressure = self.inletPressure,
                                                 downstreamPressure = self.outletPressure),
                    pressureRatio = self.outletPressure / self.inletPressure
                )

            if self.machNumber > 0.3:
                print(f'Warning: outlet Mach number {self.machNumber:.3f} exceeds 0.3. The isothermal marching '
                      f'assumption is losing accuracy; consider a Fanno line treatment.')

        # Discretization sanity check
        if self.pressureDrop / self.numberOfStations > 0.1 * self.inletPressure:
            print(f'Warning: pressure change per station exceeds 10 percent of inlet pressure. '
                  f'Increase numberOfStations above {self.numberOfStations} for a converged answer.')

        return self.pressureDrop

    def sizeDiameter(self) -> float:

        '''

        Find the inner diameter that satisfies the binding constraint.

        Two constraints can be active. The velocity limit is a hard operational bound driven by
        erosion, ignition hazard or NPSH. The pressure drop budget is an allocation from the system
        pressure schedule. Both are evaluated, and the larger required diameter wins, because a line
        must satisfy both.

        If neither allowablePressureDrop nor velocityLimit is set, the service key is used to pick a
        velocity limit from VELOCITY_LIMITS.

        '''

        inletDensity = float(fluidProps(self.fluid, 'TP', 'D', self.inletTemperature, self.inletPressure))

        # -- Velocity constraint -- #
        velocityLimit = self.velocityLimit
        if np.isnan(velocityLimit):
            velocityLimit = VELOCITY_LIMITS.get(self.service.strip().lower())
            if velocityLimit is None:
                raise InvalidInputError(
                    message       = f'Unknown service class \'{self.service}\' and no explicit velocityLimit given.',
                    parameterName = 'service', value = self.service,
                    validRange    = str(sorted(VELOCITY_LIMITS.keys()))
                )

        velocityDiameter = np.sqrt(4.0 * self.massFlow / (np.pi * inletDensity * velocityLimit))

        # -- Pressure drop constraint -- #
        pressureDiameter = 0.0
        if not np.isnan(self.allowablePressureDrop):

            def residual(trialDiameter: float) -> float:
                self.innerDiameter = trialDiameter
                return self.calculatePressureDrop() - self.allowablePressureDrop

            # Seed from the velocity-limited diameter, which is always in the right neighborhood
            pressureDiameter = secantSolve(residual, velocityDiameter,
                                           lowerBound = 1.0e-5, upperBound = 1.0)

        self.innerDiameter = max(velocityDiameter, pressureDiameter)
        self.calculatePressureDrop()

        return self.innerDiameter

    def selectStandardTube(self, material: str = None) -> str:

        '''

        Snap the computed inner diameter up to the nearest standard stocked tube size and recompute
        the pressure drop with the real geometry.

        Snapping UP is deliberate. A line sized to the next size down will exceed its pressure drop
        budget, and pressure budget overruns propagate all the way back to tank pressure. Going one
        size up costs a small amount of mass and buys margin.

        The selection also checks that the tube wall is thick enough for the design pressure, and
        skips any size that fails, so the returned tube is both hydraulically and structurally
        adequate.

        '''

        if np.isnan(self.innerDiameter):
            raise InvalidInputError(
                message       = 'selectStandardTube needs a computed inner diameter. Call sizeDiameter() first.',
                parameterName = 'innerDiameter', value = self.innerDiameter,
                validRange    = 'Positive real'
            )

        materialKey  = material if material is not None else self.material
        requiredWall = 0.0

        if not np.isnan(self.designPressure):
            properties   = materialProperties(materialKey, self._designTemperature())
            # Placeholder OD for the first pass; refined per candidate below
            requiredWall = 0.0
            allowable    = properties['allowableStress']

        bestSize = None
        for outerDiameterInches, wallInches in STANDARD_TUBE_SIZES_IN:

            outerDiameter = outerDiameterInches * M_PER_IN
            wall          = wallInches * M_PER_IN
            innerDiameter = outerDiameter - 2.0 * wall

            if innerDiameter < self.innerDiameter:
                continue

            # Structural screen
            if not np.isnan(self.designPressure):
                thicknessResult = b31_3WallThickness(self.designPressure, outerDiameter, allowable,
                                                     jointEfficiency    = self.jointEfficiency,
                                                     corrosionAllowance = self.corrosionAllowance,
                                                     millTolerance      = self.millTolerance)
                requiredWall = thicknessResult['orderedThickness']
                if wall < requiredWall:
                    continue

            if bestSize is None or innerDiameter < bestSize[2]:
                bestSize = (outerDiameterInches, wallInches, innerDiameter)

        if bestSize is None:
            raise InvalidInputError(
                message       = (f'No standard tube size satisfies an inner diameter of '
                                 f'{self.innerDiameter * 1.0e3:.3f} mm at {self.designPressure / 1.0e6:.3f} MPa design pressure. '
                                 f'The line needs pipe rather than tube, or a higher strength alloy.'),
                parameterName = 'innerDiameter', value = self.innerDiameter,
                validRange    = f'Up to {STANDARD_TUBE_SIZES_IN[-1][0]:.3f} in OD'
            )

        outerDiameterInches, wallInches, innerDiameter = bestSize

        self.outerDiameter       = outerDiameterInches * M_PER_IN
        self.wallThicknessActual = wallInches * M_PER_IN
        self.innerDiameter       = innerDiameter
        self.selectedTube        = f'{outerDiameterInches:.4g} in OD x {wallInches:.4g} in wall'

        self.calculatePressureDrop()

        return self.selectedTube

    def calculateWallThickness(self) -> dict:

        '''

        ASME B31.3 straight-pipe pressure design thickness for the selected outer diameter.

        Reports the pressure design thickness, the minimum thickness with allowances, and the
        ordered thickness after mill tolerance, plus the actual wall of the selected tube and the
        resulting margin.

        The margin number is the one to look at. A tube that clears B31.3 by two percent has no room
        for a wall thinning weld, a scratch, or a design pressure growth of the kind that happens on
        every program.

        '''

        if np.isnan(self.designPressure):
            raise InvalidInputError(
                message       = 'calculateWallThickness needs a design pressure.',
                parameterName = 'designPressure', value = self.designPressure,
                validRange    = 'Positive real, gauge'
            )

        if np.isnan(self.outerDiameter):
            # Fall back to the inner diameter as a first estimate if no tube has been selected
            self.outerDiameter = self.innerDiameter * 1.15

        properties = materialProperties(self.material, self._designTemperature())

        self.wallThickness = b31_3WallThickness(self.designPressure, self.outerDiameter,
                                                properties['allowableStress'],
                                                jointEfficiency    = self.jointEfficiency,
                                                corrosionAllowance = self.corrosionAllowance,
                                                millTolerance      = self.millTolerance)

        self.wallThickness['actualThickness'] = self.wallThicknessActual
        self.wallThickness['allowableStress'] = properties['allowableStress']

        if not np.isnan(self.wallThicknessActual):
            self.wallThickness['margin'] = self.wallThicknessActual / self.wallThickness['orderedThickness'] - 1.0
            # Actual hoop stress at design pressure, thin wall
            self.wallThickness['hoopStress'] = self.designPressure * (self.outerDiameter - 2.0 * self.wallThicknessActual) / (2.0 * self.wallThicknessActual)

        return self.wallThickness

    def calculateMass(self) -> float:

        '''

        Dry mass of the line from the selected geometry and material density. Fittings and supports
        are not included; on a real vehicle they typically add 30 to 60 percent on top of this for
        small bore tubing.

        '''

        if np.isnan(self.outerDiameter) or np.isnan(self.wallThicknessActual):
            raise InvalidInputError(
                message       = 'calculateMass needs a selected tube. Call selectStandardTube() first.',
                parameterName = 'outerDiameter', value = self.outerDiameter,
                validRange    = 'Positive real'
            )

        properties     = materialProperties(self.material, self._designTemperature())
        wallArea       = np.pi / 4.0 * (self.outerDiameter**2 - self.innerDiameter**2)
        self.dryMass   = wallArea * self.length * properties['density']

        return self.dryMass

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table with the pressure budget broken out by contribution.

        '''

        rows = [
            ['Fluid',                     f'{self.fluid}'],
            ['Mass flow',                 f'{self.massFlow:.5f} kg/s'],
            ['Length (physical)',         f'{self.length:.3f} m'],
            ['Equivalent length added',   f'{self.equivalentLength:.3f} m'],
            ['Selected tube',             f'{self.selectedTube if self.selectedTube else "not selected"}'],
            ['Inner diameter',            f'{self.innerDiameter * 1.0e3:.4f} mm'],
            ['Relative roughness',        f'{self.relativeRoughness:.3e}'],
            ['Inlet pressure',            f'{self.inletPressure / 1.0e6:.4f} MPa'],
            ['Outlet pressure',           f'{self.outletPressure / 1.0e6:.4f} MPa'],
            ['Total pressure drop',       f'{self.pressureDrop / 1.0e3:.3f} kPa'],
            ['  friction',                f'{self.frictionPressureDrop / 1.0e3:.3f} kPa'],
            ['  minor losses',            f'{self.minorPressureDrop / 1.0e3:.3f} kPa'],
            ['  elevation',               f'{self.elevationPressureDrop / 1.0e3:.3f} kPa'],
            ['  acceleration',            f'{self.accelerationPressureDrop / 1.0e3:.3f} kPa'],
            ['Total minor loss K',        f'{self.totalLossCoefficient:.3f}'],
            ['Inlet velocity',            f'{self.inletVelocity:.3f} m/s'],
            ['Outlet velocity',           f'{self.velocity:.3f} m/s'],
            ['Reynolds number (inlet)',   f'{self.reynolds:.4g}'],
            ['Darcy friction factor',     f'{self.frictionFactorValue:.5f}']
        ]

        if not self.isLiquid:
            rows.append(['Outlet Mach number', f'{self.machNumber:.4f}'])

        if self.wallThickness:
            rows.append(['Material',              f'{self.material}'])
            rows.append(['Allowable stress',      f'{self.wallThickness["allowableStress"] / 1.0e6:.2f} MPa'])
            rows.append(['B31.3 design thickness', f'{self.wallThickness["pressureDesignThickness"] * 1.0e3:.4f} mm'])
            rows.append(['B31.3 ordered thickness', f'{self.wallThickness["orderedThickness"] * 1.0e3:.4f} mm'])
            if 'margin' in self.wallThickness:
                rows.append(['Actual wall',       f'{self.wallThickness["actualThickness"] * 1.0e3:.4f} mm'])
                rows.append(['Wall margin',       f'{self.wallThickness["margin"] * 100.0:+.1f} %'])
                rows.append(['Hoop stress at MEOP', f'{self.wallThickness["hoopStress"] / 1.0e6:.2f} MPa'])

        if not np.isnan(self.dryMass):
            rows.append(['Dry mass', f'{self.dryMass:.4f} kg'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'LINE SIZING REPORT')

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'lineReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs before any property lookup.

        '''

        if self.massFlow <= 0.0:
            raise InvalidInputError(
                message       = 'Line mass flow must be positive. For a reverse flow case, swap the inlet and outlet.',
                parameterName = 'massFlow', value = self.massFlow, validRange = 'Greater than 0 kg/s'
            )

        if self.length <= 0.0:
            raise InvalidInputError(
                message       = 'Line length must be positive.',
                parameterName = 'length', value = self.length, validRange = 'Greater than 0 m'
            )

        if self.inletPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Line inlet pressure must be absolute and positive.',
                parameterName = 'inletPressure', value = self.inletPressure, validRange = 'Greater than 0 Pa absolute'
            )

        for fittingName in self.fittings:
            if fittingName.strip().lower() not in EQUIVALENT_LENGTH_RATIOS:
                raise InvalidInputError(
                    message       = f'Unknown fitting \'{fittingName}\'.',
                    parameterName = 'fittings', value = fittingName,
                    validRange    = str(sorted(EQUIVALENT_LENGTH_RATIOS.keys()))
                )

        for featureName in self.lossCoefficients:
            if featureName.strip().lower() not in LOSS_COEFFICIENTS:
                raise InvalidInputError(
                    message       = f'Unknown loss feature \'{featureName}\'.',
                    parameterName = 'lossCoefficients', value = featureName,
                    validRange    = str(sorted(LOSS_COEFFICIENTS.keys()))
                )

    def _evaluateFluidState(self) -> None:

        '''

        Decide whether the line is running liquid or gas. Drives the choking check and the report
        contents.

        '''

        if self.fluid.strip().upper() in ('N2H4', 'HYDRAZINE'):
            self.isLiquid = True
            return

        criticalTemperature = float(fluidProps(self.fluid, 'TP', 'TCRIT', self.inletTemperature, self.inletPressure))

        if self.inletTemperature >= criticalTemperature:
            self.isLiquid = False
            return

        saturationPressure = float(fluidProps(self.fluid, 'TQ', 'P', self.inletTemperature, 0.0))
        self.isLiquid      = self.inletPressure > saturationPressure

    def _designTemperature(self) -> float:

        '''

        Design temperature for the material lookup, defaulting to the inlet fluid temperature.

        Note that this is the fluid temperature, not the wall temperature. On an uninsulated
        cryogenic line the wall sits close to the fluid and this is right; on a hot gas line with
        external radiation it is optimistic and should be overridden.

        '''

        return self.inletTemperature if np.isnan(self.designTemperature) else self.designTemperature

    def _roughness(self) -> float:

        '''

        Absolute roughness, from the explicit override if set or the surface lookup otherwise.

        '''

        if not np.isnan(self.absoluteRoughness):
            return self.absoluteRoughness

        return roughnessTable(self.surface)

    def _equivalentLength(self) -> float:

        '''

        Total equivalent length added by the fittings, sum of (L/D) * D * count.

        '''

        totalRatio = 0.0
        for fittingName, count in self.fittings.items():
            totalRatio += EQUIVALENT_LENGTH_RATIOS[fittingName.strip().lower()] * count

        return totalRatio * self.innerDiameter

    def _totalLossCoefficient(self) -> float:

        '''

        Total minor loss coefficient K from the entrance, exit and other geometry features, plus any
        user-supplied additional K.

        '''

        totalK = self.additionalK
        for featureName, count in self.lossCoefficients.items():
            totalK += LOSS_COEFFICIENTS[featureName.strip().lower()] * count

        return totalK
