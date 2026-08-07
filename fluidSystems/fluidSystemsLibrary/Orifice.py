
# -- Orifice Class Definition -- #

'''

Orifice sizing and flow analysis.

An orifice is the simplest and most useful element in a fluid system. It is a deliberate,
well-characterized restriction, and almost every flow rate in a feed system is ultimately set by
one: injector elements, trim orifices that balance parallel branches, cavitating venturis that
regulate flow independent of downstream conditions, purge restrictors that limit gas consumption,
and orifice plates that measure flow.

This class covers the four regimes an orifice can operate in, and the whole point of the class is
that it decides which one applies rather than making the user assume:

1. Incompressible liquid       -- mdot = Cd * A * sqrt(2 * rho * dP)
2. Cavitating / flashing liquid -- choked on vapor pressure, mdot independent of downstream pressure
3. Subsonic compressible gas    -- full compressible orifice relation
4. Choked compressible gas      -- mdot depends only on upstream stagnation conditions

Two discharge coefficient models are supported:

'plate'    ISO 5167-2 orifice plate installed in a pipe, with the Reader-Harris/Gallagher discharge
           coefficient equation and the standard expansibility factor. This is the metering case:
           a plate with defined tappings whose Cd is known to a fraction of a percent without
           calibration. Use it when the orifice is a flow measurement device.

'injector' Free-discharge orifice: an injector element, a trim restrictor, a drilled passage. Cd is
           set by the inlet geometry and the length-to-diameter ratio, with a Reynolds number
           correction that matters below about Re = 10^4. Use it when the orifice is a flow control
           device. Cd here is good to maybe 5 percent, and if the flow rate matters you flow-test
           the hardware.

The distinction is not academic. A sharp-edged plate is Cd = 0.61; the same hole drilled with an
L/D of 3 is Cd = 0.81. That is a 33 percent flow difference from a detail that does not appear on
a schematic.

See Also:
---------
CavitatingVenturi : Choked liquid flow control with pressure recovery
Valve             : Variable restriction, sized by Cv rather than by area
Line              : Distributed friction loss rather than a local restriction

Theory: docs/Orifices.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

# Local imports - try absolute first (for running directly or from a driver script),
# fall back to relative imports (for when the module is imported as part of the package)
try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                       criticalPressureRatio, chokedMassFlux, R_UNIVERSAL, speciesMolarMass,
                       InvalidInputError, PressureDropError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                        criticalPressureRatio, chokedMassFlux, R_UNIVERSAL, speciesMolarMass,
                        InvalidInputError, PressureDropError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# High-Reynolds discharge coefficients for free-discharge orifices, keyed by inlet geometry. These
# are the asymptotic values approached above roughly Re = 10^4; the Reynolds correction below scales
# them down at lower Re.
#
# The spread across this table is the single largest source of error in orifice sizing, and it is
# entirely geometric. Specify the inlet condition on the drawing or you do not know your flow rate.
DISCHARGE_COEFFICIENTS = {
    'sharp':        0.61,   # thin plate, sharp square inlet edge, free discharge. Vena contracta controls.
    'square':       0.81,   # square-edged drilled hole, L/D between 2 and 6. Flow reattaches inside the bore.
    'rounded':      0.96,   # inlet radius >= 0.25 d. Very little contraction loss.
    'conical':      0.90,   # conical converging inlet, 30 to 60 degree included angle
    'short tube':   0.72,   # L/D near 0.5, flow does not reliably reattach. Unstable, avoid by design.
    'reentrant':    0.52    # Borda tube, inlet projecting into the upstream volume. Worst case.
}

# Classic sharp/square-edged orifice discharge coefficient versus Reynolds number, normalized to the
# high-Reynolds asymptote. Digitized from the Lichtarowicz, Duggins and Markland (1965) compilation
# for L/D between 2 and 10. Interpolated on log(Re).
#
# Below Re = 100 the flow is fully viscous and Cd falls off as sqrt(Re); above Re = 3e4 it is flat.
# A trim orifice running cold, viscous propellant at low flow can easily sit at Re = 2000, where Cd
# is 10 percent below its catalog value.
REYNOLDS_CORRECTION_RE = np.array([1.0e1, 1.0e2, 3.0e2, 1.0e3, 3.0e3, 1.0e4, 3.0e4, 1.0e6])
REYNOLDS_CORRECTION_CD = np.array([0.11,  0.37,  0.62,  0.84,  0.94,  0.99,  1.00,  1.00])

# Cavitation number thresholds for a sharp-edged orifice, in terms of
# sigma = (P2 - Pvapor) / (P1 - P2).
CAVITATION_INCIPIENT = 1.8    # first audible/detectable cavitation below this
CAVITATION_CHOKED    = 0.6    # fully developed, flow becomes independent of P2 below this

class Orifice:

    '''

    Sizing and flow analysis for a fixed-area restriction.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps (e.g. 'Nitrogen', 'N2H4', 'Water')
    upstreamPressure : float
        Static pressure upstream of the orifice [Pa, absolute]
    downstreamPressure : float
        Static pressure downstream of the orifice [Pa, absolute]
    upstreamTemperature : float
        Fluid temperature upstream of the orifice [K]
    diameter : float
        Orifice bore diameter [m]. Leave unset when sizing.
    massFlow : float
        Mass flow rate [kg/s]. Leave unset when analyzing a known geometry.
    orificeType : str
        Key into DISCHARGE_COEFFICIENTS for the 'injector' model
    model : str
        'injector' (free discharge, default) or 'plate' (ISO 5167-2 in-pipe metering)
    pipeDiameter : float
        Upstream pipe inner diameter [m]. Required for the 'plate' model.
    tappings : str
        'corner', 'flange' or 'D and D/2'. ISO 5167-2 pressure tapping arrangement.
    dischargeCoefficient : float
        Override. If set, all Cd correlations are bypassed and this value is used directly.

    Key Output Properties:
    ----------------------
    area : float
        Orifice flow area [m^2]
    velocity : float
        Bulk velocity through the bore [m/s]
    reynolds : float
        Bore Reynolds number [-]
    regime : str
        'incompressible', 'cavitating', 'subsonic gas' or 'choked gas'
    isChoked : bool
        True when mass flow is independent of downstream pressure
    cavitationNumber : float
        (P2 - Pvapor) / (P1 - P2) for liquids [-]
    permanentPressureLoss : float
        Unrecovered pressure loss [Pa]. Less than the measured dP for a plate, equal to it for a
        free-discharge orifice.

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    calculateDischargeCoefficient() Evaluate Cd from the selected model
    calculateMassFlow()           Forward problem: geometry and dP to mass flow
    sizeDiameter()                Inverse problem: mass flow and dP to diameter
    calculatePressureDrop()       Mass flow and geometry to dP
    generateReport(outputDir)     Formatted results table

    Typical Workflow:
    -----------------
    >>> trimOrifice = Orifice()
    >>> trimOrifice.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.20e6,
    ...                        'downstreamPressure': 1.90e6, 'upstreamTemperature': 293.15,
    ...                        'massFlow': 0.045, 'orificeType': 'square'})
    >>> trimOrifice.sizeDiameter()
    >>> print(trimOrifice.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid State -- #

        # Species name handed to fluidProps. Anything REFPROP or CoolProp resolves, plus 'N2H4'.
        self.fluid                 = ''      # [case sensitive string]
        self.upstreamPressure      = np.nan  # [Pa, absolute]
        self.downstreamPressure    = np.nan  # [Pa, absolute]
        self.upstreamTemperature   = np.nan  # [K]

        # -- Geometry -- #

        # Bore diameter. Either this or massFlow is the unknown; specifying both means the class
        # will check consistency rather than solve.
        self.diameter              = np.nan  # [m]
        self.area                  = np.nan  # [m^2]
        self.lengthToDiameter      = 3.0     # [-], bore length over bore diameter
        self.pipeDiameter          = np.nan  # [m], upstream pipe ID, plate model only
        self.betaRatio             = np.nan  # [-], d/D, plate model only

        # -- Model Selection -- #

        self.model                 = 'injector'  # 'injector' or 'plate'
        self.orificeType           = 'square'    # key into DISCHARGE_COEFFICIENTS
        self.tappings              = 'flange'    # 'corner', 'flange' or 'D and D/2'
        self.dischargeCoefficient  = np.nan      # [-], set to override the correlations
        self.numberOfOrifices      = 1           # [-], parallel identical elements

        # -- Flow State -- #

        self.massFlow              = np.nan  # [kg/s], total through all parallel elements
        self.velocity              = np.nan  # [m/s], bulk velocity in a single bore
        self.reynolds              = np.nan  # [-], based on bore diameter
        self.density               = np.nan  # [kg/m^3], upstream
        self.viscosity             = np.nan  # [Pa-s], upstream
        self.vaporPressure         = np.nan  # [Pa], at upstream temperature, liquids only

        # -- Results and Flags -- #

        self.regime                = ''      # 'incompressible' / 'cavitating' / 'subsonic gas' / 'choked gas'
        self.isChoked              = False   # [-], mass flow independent of downstream pressure
        self.isLiquid              = True    # [-], set by the phase check
        self.cavitationNumber      = np.nan  # [-]
        self.cavitationStatus      = ''      # 'none' / 'incipient' / 'developed' / 'flashing'
        self.expansibilityFactor   = 1.0     # [-], compressibility correction, 1.0 for liquids
        self.permanentPressureLoss = np.nan  # [Pa]
        self.pressureDrop          = np.nan  # [Pa]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, upstreamPressure, downstreamPressure, upstreamTemperature.
        Everything else is optional and falls back to the constructor default.

        '''

        requiredParams = {
            'fluid':               'Orifice fluid species not provided.',
            'upstreamPressure':    'Orifice upstream pressure not provided.',
            'downstreamPressure':  'Orifice downstream pressure not provided.',
            'upstreamTemperature': 'Orifice upstream temperature not provided.'
        }

        optionalParams = ['diameter', 'massFlow', 'lengthToDiameter', 'pipeDiameter', 'model',
                          'orificeType', 'tappings', 'dischargeCoefficient', 'numberOfOrifices']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._evaluateFluidState()

    def calculateDischargeCoefficient(self) -> float:

        '''

        Evaluate the discharge coefficient for the current geometry and flow state.

        The 'plate' model uses the ISO 5167-2 Reader-Harris/Gallagher equation, which is the
        internationally accepted correlation for a standard orifice plate and is good to about
        0.5 percent for beta between 0.1 and 0.75 and Re_D above 5000.

        The 'injector' model looks up the asymptotic Cd for the inlet geometry and applies the
        Reynolds correction. If dischargeCoefficient was set explicitly, both are skipped.

        Requires either diameter or massFlow to already be known, because Cd depends on Reynolds
        number and Reynolds number depends on both. The solvers below handle that coupling by
        iterating; calling this directly with neither known raises.

        '''

        # Explicit override wins over everything
        if not np.isnan(self.dischargeCoefficient):
            return self.dischargeCoefficient

        if self.model.strip().lower() == 'plate':
            return self._readerHarrisGallagher()

        # -- Injector / free-discharge model -- #

        baseCd = DISCHARGE_COEFFICIENTS.get(self.orificeType.strip().lower())
        if baseCd is None:
            raise InvalidInputError(
                message       = f'Unknown orifice inlet geometry \'{self.orificeType}\'.',
                parameterName = 'orificeType',
                value         = self.orificeType,
                validRange    = str(sorted(DISCHARGE_COEFFICIENTS.keys()))
            )

        # Reynolds correction. When Reynolds number is not yet known (first pass of a sizing solve)
        # assume the fully turbulent asymptote and let the solver iterate.
        if np.isnan(self.reynolds) or self.reynolds <= 0.0:
            return baseCd

        correction = float(np.interp(np.log10(max(self.reynolds, 1.0)),
                                     np.log10(REYNOLDS_CORRECTION_RE),
                                     REYNOLDS_CORRECTION_CD))

        return baseCd * correction

    def calculateMassFlow(self) -> float:

        '''

        Forward problem: given the bore diameter and the pressure differential, compute mass flow.

        The regime is selected automatically:

        Liquid, P2 above vapor pressure     -> incompressible orifice equation
        Liquid, P2 at or below vapor pressure -> cavitating, choked on (P1 - Pvapor)
        Gas, pressure ratio above critical  -> subsonic compressible relation
        Gas, pressure ratio below critical  -> choked, upstream conditions only

        Because Cd depends on Reynolds number and Reynolds number depends on mass flow, the liquid
        and subsonic gas cases iterate to convergence. Two or three passes is typical.

        '''

        if np.isnan(self.diameter):
            raise InvalidInputError(
                message       = 'calculateMassFlow needs a bore diameter. Set diameter, or call sizeDiameter() instead.',
                parameterName = 'diameter',
                value         = self.diameter,
                validRange    = 'Positive real'
            )

        self.area         = self.numberOfOrifices * np.pi * self.diameter**2 / 4.0
        self.pressureDrop = self.upstreamPressure - self.downstreamPressure

        # Iterate on the Cd/Reynolds coupling. Seed with the turbulent asymptote.
        self.reynolds = np.nan
        for _ in range(20):

            dischargeCoefficient = self.calculateDischargeCoefficient()
            massFlow             = self._massFlowFromCd(dischargeCoefficient)

            previousReynolds = self.reynolds
            self._updateDerivedFlowState(massFlow)

            if not np.isnan(previousReynolds) and abs(self.reynolds - previousReynolds) < 1.0e-6 * max(1.0, self.reynolds):
                break

        self.massFlow             = massFlow
        self.dischargeCoefficient = dischargeCoefficient

        return self.massFlow

    def sizeDiameter(self) -> float:

        '''

        Inverse problem: given a required mass flow and an allowable pressure drop, find the bore
        diameter.

        This is the sizing call, and it is the one used most often. Note what the answer means: the
        diameter that produces exactly the requested flow at exactly the requested dP, with the Cd
        the model predicts. Real hardware is drilled to the nearest available drill size, so the
        useful output is usually 'the flow you get with the next drill size up and the next one
        down', which is what generateReport() prints alongside the exact answer.

        '''

        if np.isnan(self.massFlow):
            raise InvalidInputError(
                message       = 'sizeDiameter needs a target mass flow. Set massFlow, or call calculateMassFlow() instead.',
                parameterName = 'massFlow',
                value         = self.massFlow,
                validRange    = 'Positive real'
            )

        targetMassFlow = self.massFlow

        def residual(trialDiameter: float) -> float:
            self.diameter = trialDiameter
            self.massFlow = np.nan
            return self.calculateMassFlow() - targetMassFlow

        # Seed from the incompressible relation with the asymptotic Cd. Even for gas cases this puts
        # the initial guess within an order of magnitude, which is all the secant method needs.
        seedCd       = DISCHARGE_COEFFICIENTS.get(self.orificeType.strip().lower(), 0.7)
        seedArea     = targetMassFlow / (seedCd * np.sqrt(2.0 * self.density * max(self.upstreamPressure - self.downstreamPressure, 1.0)))
        seedDiameter = np.sqrt(4.0 * seedArea / (np.pi * self.numberOfOrifices))

        self.diameter = secantSolve(residual, seedDiameter, lowerBound = 1.0e-9, upperBound = 1.0)
        self.massFlow = targetMassFlow

        # Recompute the derived state at the converged diameter
        self.calculateMassFlow()
        self.massFlow = targetMassFlow

        return self.diameter

    def calculatePressureDrop(self) -> float:

        '''

        Given a bore diameter and a required mass flow, find the pressure drop across the orifice.

        Upstream pressure is held fixed and downstream pressure is solved for, because that is the
        physical situation: the supply sets P1 and the restriction sets what arrives downstream.

        Raises PressureDropError if no downstream pressure can pass the requested flow, which means
        the orifice is simply too small: even choked it cannot pass that much.

        '''

        if np.isnan(self.diameter) or np.isnan(self.massFlow):
            raise InvalidInputError(
                message       = 'calculatePressureDrop needs both diameter and massFlow.',
                parameterName = 'diameter/massFlow',
                value         = (self.diameter, self.massFlow),
                validRange    = 'Both positive real'
            )

        targetMassFlow = self.massFlow

        # Check the physical ceiling first. The maximum flow this orifice can ever pass is the
        # choked value, reached at zero downstream pressure for a gas and at vapor pressure for a
        # liquid. Asking for more than that has no solution.
        self.downstreamPressure = self.vaporPressure if self.isLiquid else 1.0
        maximumMassFlow         = self.calculateMassFlow()

        if targetMassFlow > maximumMassFlow:
            raise PressureDropError(
                message = (f'Orifice cannot pass {targetMassFlow:.4g} kg/s. The choked limit at this '
                           f'upstream condition is {maximumMassFlow:.4g} kg/s. Increase the diameter, '
                           f'the number of parallel elements, or the upstream pressure.'),
                context = createErrorContext(component = 'Orifice', fluid = self.fluid,
                                             massFlow = targetMassFlow,
                                             upstreamPressure = self.upstreamPressure,
                                             temperature = self.upstreamTemperature,
                                             diameter = self.diameter,
                                             chokedMassFlow = maximumMassFlow)
            )

        def residual(trialDownstreamPressure: float) -> float:
            self.downstreamPressure = trialDownstreamPressure
            return self.calculateMassFlow() - targetMassFlow

        seedPressure            = self.upstreamPressure * 0.9
        self.downstreamPressure = secantSolve(residual, seedPressure,
                                              lowerBound = 1.0, upperBound = self.upstreamPressure)

        self.calculateMassFlow()
        self.massFlow     = targetMassFlow
        self.pressureDrop = self.upstreamPressure - self.downstreamPressure

        return self.pressureDrop

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table. Written to <outputDir>/orificeReport.txt when outputDir is
        given, and returned as a string either way.

        For the sizing case the report also lists the flow that results from the nearest standard
        drill sizes above and below the exact answer, because that is the number that ends up on the
        drawing.

        '''

        rows = [
            ['Fluid',                    f'{self.fluid}'],
            ['Model',                    f'{self.model}'],
            ['Inlet geometry',           f'{self.orificeType}'],
            ['Regime',                   f'{self.regime}'],
            ['Upstream pressure',        f'{self.upstreamPressure / 1.0e6:.4f} MPa'],
            ['Downstream pressure',      f'{self.downstreamPressure / 1.0e6:.4f} MPa'],
            ['Pressure drop',            f'{self.pressureDrop / 1.0e6:.4f} MPa'],
            ['Upstream temperature',     f'{self.upstreamTemperature:.2f} K'],
            ['Upstream density',         f'{self.density:.3f} kg/m^3'],
            ['Bore diameter',            f'{self.diameter * 1.0e3:.4f} mm'],
            ['Number of elements',       f'{self.numberOfOrifices:d}'],
            ['Total flow area',          f'{self.area * 1.0e6:.5f} mm^2'],
            ['Discharge coefficient',    f'{self.dischargeCoefficient:.4f}'],
            ['Mass flow',                f'{self.massFlow:.5f} kg/s'],
            ['Bore velocity',            f'{self.velocity:.2f} m/s'],
            ['Reynolds number',          f'{self.reynolds:.4g}'],
            ['Choked',                   f'{self.isChoked}'],
            ['Permanent pressure loss',  f'{self.permanentPressureLoss / 1.0e6:.4f} MPa']
        ]

        if self.isLiquid:
            rows.append(['Vapor pressure',   f'{self.vaporPressure / 1.0e3:.3f} kPa'])
            rows.append(['Cavitation number', f'{self.cavitationNumber:.3f}'])
            rows.append(['Cavitation status', f'{self.cavitationStatus}'])
        else:
            rows.append(['Expansibility factor', f'{self.expansibilityFactor:.4f}'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'ORIFICE SIZING REPORT')

        # Nearest standard drill sizes, so the exact answer can be turned into a real hole
        report += '\n\n' + self._drillSizeTable()

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'orificeReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Check the inputs for physical sense before any property lookup happens, so that a sign error
        produces a readable message instead of a REFPROP error code.

        '''

        if self.upstreamPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Upstream pressure must be absolute and positive.',
                parameterName = 'upstreamPressure', value = self.upstreamPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if self.downstreamPressure < 0.0:
            raise InvalidInputError(
                message       = 'Downstream pressure must be absolute and non-negative.',
                parameterName = 'downstreamPressure', value = self.downstreamPressure,
                validRange    = '0 Pa absolute or greater'
            )

        if self.downstreamPressure > self.upstreamPressure:
            raise InvalidInputError(
                message       = ('Downstream pressure exceeds upstream pressure. An orifice is not a pump. '
                                 'Check the sign convention or swap the two values.'),
                parameterName = 'downstreamPressure', value = self.downstreamPressure,
                validRange    = f'0 to {self.upstreamPressure:.6g} Pa'
            )

        if self.upstreamTemperature <= 0.0:
            raise InvalidInputError(
                message       = 'Upstream temperature must be absolute and positive.',
                parameterName = 'upstreamTemperature', value = self.upstreamTemperature,
                validRange    = 'Greater than 0 K'
            )

        if self.model.strip().lower() == 'plate' and np.isnan(self.pipeDiameter):
            raise InvalidInputError(
                message       = 'The ISO 5167-2 plate model needs the upstream pipe inner diameter to form the beta ratio.',
                parameterName = 'pipeDiameter', value = self.pipeDiameter,
                validRange    = 'Positive real, greater than the bore diameter'
            )

    def _evaluateFluidState(self) -> None:

        '''

        Pull upstream density, viscosity and (for liquids) vapor pressure from the property backend,
        and decide whether this is a liquid or a gas.

        The phase decision drives everything downstream, so it is made once here from the upstream
        state rather than being re-derived by each calculation.

        '''

        self.density   = float(fluidProps(self.fluid, 'TP', 'D',   self.upstreamTemperature, self.upstreamPressure))
        self.viscosity = float(fluidProps(self.fluid, 'TP', 'VIS', self.upstreamTemperature, self.upstreamPressure))

        # Phase determination. Hydrazine is liquid by construction over its useful range. For
        # everything else, compare the upstream pressure against the saturation pressure at the
        # upstream temperature: above it the fluid is a liquid, below it a gas. Above the critical
        # temperature there is no saturation line and the fluid is treated as a gas.
        if self.fluid.strip().upper() in ('N2H4', 'HYDRAZINE'):
            self.isLiquid      = True
            self.vaporPressure = float(fluidProps(self.fluid, 'TP', 'P', self.upstreamTemperature, self.upstreamPressure))
            return

        criticalTemperature = float(fluidProps(self.fluid, 'TP', 'TCRIT', self.upstreamTemperature, self.upstreamPressure))

        if self.upstreamTemperature >= criticalTemperature:
            self.isLiquid      = False
            self.vaporPressure = np.nan
            return

        self.vaporPressure = float(fluidProps(self.fluid, 'TQ', 'P', self.upstreamTemperature, 0.0))
        self.isLiquid      = self.upstreamPressure > self.vaporPressure

    def _massFlowFromCd(self, dischargeCoefficient: float) -> float:

        '''

        Evaluate mass flow for a known discharge coefficient, selecting the regime.

        Split out from calculateMassFlow so the Cd/Reynolds iteration has a clean inner function.

        '''

        if self.isLiquid:
            return self._liquidMassFlow(dischargeCoefficient)

        return self._gasMassFlow(dischargeCoefficient)

    def _liquidMassFlow(self, dischargeCoefficient: float) -> float:

        '''

        Incompressible and cavitating liquid flow.

        Below the vapor pressure the vena contracta flashes, a vapor cavity forms, and the orifice
        chokes: further reduction in downstream pressure does not increase flow, because the
        pressure at the throat is pinned at the vapor pressure. The effective driving head becomes
        (P1 - Pvapor) instead of (P1 - P2).

        This is exactly the mechanism a cavitating venturi exploits deliberately, and exactly the
        mechanism that makes a trim orifice stop trimming when the downstream pressure drops.

        '''

        # Effective driving pressure. Once the downstream pressure falls below the vapor pressure
        # the flow is choked on the vapor pressure instead.
        if self.downstreamPressure <= self.vaporPressure:
            drivingPressure = self.upstreamPressure - self.vaporPressure
            self.isChoked   = True
            self.regime     = 'cavitating'
        else:
            drivingPressure = self.upstreamPressure - self.downstreamPressure
            self.isChoked   = False
            self.regime     = 'incompressible'

        drivingPressure = max(drivingPressure, 0.0)

        # Velocity of approach factor. For a free-discharge orifice the upstream area is effectively
        # infinite and beta is zero, so the factor is unity. For an in-pipe plate it matters.
        velocityOfApproach = 1.0
        if self.model.strip().lower() == 'plate' and not np.isnan(self.pipeDiameter):
            self.betaRatio     = self.diameter / self.pipeDiameter
            velocityOfApproach = 1.0 / np.sqrt(1.0 - self.betaRatio**4)

        self.expansibilityFactor = 1.0

        return dischargeCoefficient * velocityOfApproach * self.area * np.sqrt(2.0 * self.density * drivingPressure)

    def _gasMassFlow(self, dischargeCoefficient: float) -> float:

        '''

        Compressible gas flow, subsonic or choked.

        Subsonic:
            mdot = Cd * A * P1 * sqrt( 2*g/((g-1)*R*T1) * (r^(2/g) - r^((g+1)/g)) )
        Choked:
            mdot = Cd * A * P1 * sqrt( g/(R*T1) ) * (2/(g+1))^((g+1)/(2*(g-1)))

        with r = P2/P1 and g the ratio of specific heats at upstream conditions.

        The choked branch is the one that matters operationally. A GHe or GN2 orifice venting to
        atmosphere from any bottle pressure is choked, which is why a purge restrictor gives a
        constant, predictable gas consumption regardless of what the downstream plumbing is doing.

        '''

        gamma       = float(fluidProps(self.fluid, 'TP', 'Cp/Cv', self.upstreamTemperature, self.upstreamPressure))
        gasConstant = R_UNIVERSAL / speciesMolarMass(self.fluid)

        pressureRatio = self.downstreamPressure / self.upstreamPressure
        criticalRatio = criticalPressureRatio(gamma)

        if pressureRatio <= criticalRatio:
            self.isChoked            = True
            self.regime              = 'choked gas'
            self.expansibilityFactor = float(np.nan)
            massFlux = chokedMassFlux(self.upstreamPressure, self.upstreamTemperature, gamma, gasConstant)
            return dischargeCoefficient * self.area * massFlux

        self.isChoked = False
        self.regime   = 'subsonic gas'

        # ISO 5167-2 expansibility factor, reported for reference on the plate model. The full
        # compressible relation below already captures the expansion, so it is not applied twice.
        if self.model.strip().lower() == 'plate' and not np.isnan(self.pipeDiameter):
            self.betaRatio           = self.diameter / self.pipeDiameter
            self.expansibilityFactor = 1.0 - (0.351 + 0.256 * self.betaRatio**4 + 0.93 * self.betaRatio**8) * (1.0 - pressureRatio**(1.0 / gamma))
        else:
            self.expansibilityFactor = 1.0 - (0.351) * (1.0 - pressureRatio**(1.0 / gamma))

        expansionTerm = (2.0 * gamma / ((gamma - 1.0) * gasConstant * self.upstreamTemperature)) * \
                        (pressureRatio**(2.0 / gamma) - pressureRatio**((gamma + 1.0) / gamma))

        velocityOfApproach = 1.0
        if self.model.strip().lower() == 'plate' and not np.isnan(self.pipeDiameter):
            velocityOfApproach = 1.0 / np.sqrt(1.0 - self.betaRatio**4)

        return dischargeCoefficient * velocityOfApproach * self.area * self.upstreamPressure * np.sqrt(max(expansionTerm, 0.0))

    def _readerHarrisGallagher(self) -> float:

        '''

        ISO 5167-2 Reader-Harris/Gallagher discharge coefficient for a standard orifice plate.

        Valid for beta from 0.10 to 0.75, pipe diameter from 50 mm to 1000 mm, and Re_D above 5000
        (above 170 * beta^2 * D for beta below 0.56). Outside those bounds the equation still
        evaluates but the 0.5 percent uncertainty claim does not hold, so a warning is printed.

        '''

        self.betaRatio = self.diameter / self.pipeDiameter
        beta           = self.betaRatio

        if beta < 0.10 or beta > 0.75:
            print(f'Warning: beta ratio {beta:.3f} is outside the ISO 5167-2 validated range of 0.10 to 0.75.')

        # Pipe Reynolds number. Fall back to a high value on the first solver pass, before the flow
        # rate is known, so the correlation returns its fully turbulent asymptote.
        if np.isnan(self.reynolds) or self.reynolds <= 0.0:
            pipeReynolds = 1.0e7
        else:
            pipeReynolds = self.reynolds * beta

        # Tapping positions, normalized by pipe diameter
        tappingKey = self.tappings.strip().lower()
        if tappingKey == 'corner':
            upstreamTapping, downstreamTapping = 0.0, 0.0
        elif tappingKey == 'flange':
            upstreamTapping   = 0.0254 / self.pipeDiameter
            downstreamTapping = 0.0254 / self.pipeDiameter
        elif tappingKey in ('d and d/2', 'd', 'radius'):
            upstreamTapping, downstreamTapping = 1.0, 0.47
        else:
            raise InvalidInputError(
                message       = f'Unknown tapping arrangement \'{self.tappings}\'.',
                parameterName = 'tappings', value = self.tappings,
                validRange    = 'corner, flange, or D and D/2'
            )

        termA           = (19000.0 * beta / pipeReynolds)**0.8
        downstreamTerm  = 2.0 * downstreamTapping / (1.0 - beta)

        dischargeCoefficient = (0.5961
                                + 0.0261 * beta**2
                                - 0.216  * beta**8
                                + 0.000521 * (1.0e6 * beta / pipeReynolds)**0.7
                                + (0.0188 + 0.0063 * termA) * beta**3.5 * (1.0e6 / pipeReynolds)**0.3
                                + (0.043 + 0.080 * np.exp(-10.0 * upstreamTapping) - 0.123 * np.exp(-7.0 * upstreamTapping))
                                  * (1.0 - 0.11 * termA) * beta**4 / (1.0 - beta**4)
                                - 0.031 * (downstreamTerm - 0.8 * downstreamTerm**1.1) * beta**1.3)

        # Small-bore correction for pipes below 71.12 mm
        if self.pipeDiameter < 0.07112:
            dischargeCoefficient += 0.011 * (0.75 - beta) * (2.8 - self.pipeDiameter / 0.0254)

        return dischargeCoefficient

    def _updateDerivedFlowState(self, massFlow: float) -> None:

        '''

        Recompute velocity, Reynolds number, cavitation state and permanent pressure loss from a
        candidate mass flow. Called inside the Cd iteration.

        '''

        singleBoreArea = np.pi * self.diameter**2 / 4.0

        self.velocity = (massFlow / self.numberOfOrifices) / (self.density * singleBoreArea)
        self.reynolds = self.density * self.velocity * self.diameter / self.viscosity

        # Cavitation assessment for liquids. sigma = (P2 - Pv) / (P1 - P2): large sigma means the
        # downstream pressure sits well above vapor pressure and no cavity can form.
        if self.isLiquid and not np.isnan(self.vaporPressure):
            pressureDrop = max(self.upstreamPressure - self.downstreamPressure, 1.0e-9)
            self.cavitationNumber = (self.downstreamPressure - self.vaporPressure) / pressureDrop

            if self.downstreamPressure <= self.vaporPressure:
                self.cavitationStatus = 'flashing'
            elif self.cavitationNumber < CAVITATION_CHOKED:
                self.cavitationStatus = 'developed'
            elif self.cavitationNumber < CAVITATION_INCIPIENT:
                self.cavitationStatus = 'incipient'
            else:
                self.cavitationStatus = 'none'

        # Permanent pressure loss. A free-discharge orifice recovers nothing: the jet dissipates
        # into the downstream volume and the full dP is lost. An in-pipe plate recovers part of the
        # differential downstream of the vena contracta, by the ISO 5167 approximation
        # dP_permanent / dP_measured = (1 - beta^1.9).
        self.pressureDrop = self.upstreamPressure - self.downstreamPressure
        if self.model.strip().lower() == 'plate' and not np.isnan(self.betaRatio):
            self.permanentPressureLoss = self.pressureDrop * (1.0 - self.betaRatio**1.9)
        else:
            self.permanentPressureLoss = self.pressureDrop

    def _drillSizeTable(self) -> str:

        '''

        Bracket the computed diameter with the nearest standard drill sizes and report the flow each
        would give.

        Orifices are made with drills, and a drill index is a discrete set. The exact sizing answer
        is never the diameter that gets manufactured, so the useful deliverable is the pair of real
        sizes that bracket it and the flow error each carries. Number and letter drills plus common
        fractional sizes are included.

        '''

        # Number drills 80 through 1, letter drills A through Z, and fractional sizes to 1/2 inch.
        # Stored in inches, converted on use. This is the standard US drill index; metric shops will
        # want the metric set instead, but the mixed index is what a US machine shop actually stocks.
        numberDrills = [0.0135, 0.0145, 0.0156, 0.0160, 0.0180, 0.0200, 0.0210, 0.0225, 0.0240,
                        0.0250, 0.0260, 0.0280, 0.0292, 0.0310, 0.0320, 0.0330, 0.0350, 0.0360,
                        0.0370, 0.0380, 0.0390, 0.0400, 0.0410, 0.0420, 0.0430, 0.0465, 0.0520,
                        0.0550, 0.0595, 0.0635, 0.0670, 0.0700, 0.0730, 0.0760, 0.0785, 0.0810,
                        0.0820, 0.0860, 0.0890, 0.0935, 0.0960, 0.0980, 0.0995, 0.1015, 0.1040,
                        0.1065, 0.1100, 0.1110, 0.1130, 0.1160, 0.1200, 0.1250, 0.1285, 0.1360,
                        0.1405, 0.1440, 0.1470, 0.1495, 0.1520, 0.1540, 0.1570, 0.1590, 0.1610,
                        0.1660, 0.1695, 0.1730, 0.1770, 0.1800, 0.1820, 0.1850, 0.1890, 0.1910,
                        0.1935, 0.1960, 0.1990, 0.2010, 0.2040, 0.2055, 0.2090, 0.2130, 0.2210,
                        0.2280, 0.2340, 0.2380, 0.2420, 0.2460, 0.2500, 0.2570, 0.2610, 0.2660,
                        0.2720, 0.2770, 0.2810, 0.2900, 0.2950, 0.3020, 0.3160, 0.3230, 0.3320,
                        0.3390, 0.3480, 0.3580, 0.3680, 0.3770, 0.3860, 0.3970, 0.4040, 0.4130,
                        0.4219, 0.4375, 0.4531, 0.4688, 0.4844, 0.5000]

        drillDiametersMetric = np.array(sorted(numberDrills)) * 0.0254

        exactDiameter = self.diameter
        targetFlow    = self.massFlow

        below = drillDiametersMetric[drillDiametersMetric <= exactDiameter]
        above = drillDiametersMetric[drillDiametersMetric >= exactDiameter]

        candidates = []
        if below.size:
            candidates.append(below[-1])
        if above.size:
            candidates.append(above[0])

        rows = []
        for candidateDiameter in candidates:
            savedDiameter  = self.diameter
            savedMassFlow  = self.massFlow
            self.diameter  = candidateDiameter
            candidateFlow  = self.calculateMassFlow()
            self.diameter  = savedDiameter
            self.massFlow  = savedMassFlow
            rows.append([
                f'{candidateDiameter * 1.0e3:.4f}',
                f'{candidateDiameter / 0.0254:.4f}',
                f'{candidateFlow:.5f}',
                f'{100.0 * (candidateFlow - targetFlow) / targetFlow:+.2f}'
            ])

        # Restore the converged state after the excursions above
        self.calculateMassFlow()
        self.massFlow = targetFlow

        return formatReportTable(rows,
                                 ['Drill [mm]', 'Drill [in]', 'Mass flow [kg/s]', 'Flow error [%]'],
                                 title = f'NEAREST STANDARD DRILL SIZES (exact = {exactDiameter * 1.0e3:.4f} mm)')
