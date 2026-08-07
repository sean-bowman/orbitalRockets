
# -- Cavitating Venturi Class Definition -- #

'''

Cavitating venturi sizing and operating margin.

A cavitating venturi is a flow control device with no moving parts, no control loop and no power.
It works by deliberately dropping the throat static pressure to the propellant vapor pressure. Once
that happens a vapor cavity forms at the throat, the throat pressure is pinned at the vapor
pressure, and the mass flow depends only on upstream conditions:

    mdot = Cd * At * sqrt(2 * rho * (P1 - Pvapor))

Downstream pressure has no effect at all, as long as the venturi stays choked. That is the entire
value proposition. Put one in each branch of a feed system and the branches stop talking to each
other: chamber pressure oscillations cannot propagate back into the feed line, a valve slamming in
one branch does not disturb the others, and the flow split is set by geometry rather than by the
relative resistance of downstream hardware.

It is also a hydraulic fuse. If the chamber loses pressure the venturi does not let more propellant
through, which is not true of a plain orifice.

The costs are real. A cavitating venturi requires a permanently spent pressure budget: the venturi
must keep its throat below vapor pressure, so the recoverable fraction of (P1 - P2) is limited by
the diffuser, and roughly 10 to 20 percent of the upstream pressure is unrecoverable. It also
cavitates by design, so the diffuser has to be built to survive continuous bubble collapse: hardened
or thick-walled, with the collapse region positioned in the diffuser rather than against a wall
transition.

The single number that matters in operation is the unchoke margin. If downstream pressure rises
above the recovery limit the cavity collapses, the venturi silently becomes an ordinary venturi, and
the flow becomes a function of downstream pressure again. Nothing warns you; the flow just changes.

See Also:
---------
Orifice     : Fixed restriction; cavitates as a failure mode rather than by design
Valve       : Active flow control with a control loop
CatalystBed : The downstream pressure this venturi is protecting the feed system from

Theory: docs/Orifices.md, docs/FlowControlDevices.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable,
                       InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable,
                        InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Pressure recovery ratio at unchoke, P2/P1, by diffuser quality. This is the highest downstream
# pressure the venturi will tolerate before the cavity collapses and it stops regulating.
#
# The physics is that the diffuser converts throat velocity head back into static pressure. A long,
# shallow diffuser recovers more, so it tolerates a higher back pressure. A sharp expansion recovers
# almost nothing and unchokes early.
DIFFUSER_RECOVERY = {
    'sharp expansion':   0.55,   # sudden area change, essentially no recovery
    'short diffuser':    0.75,   # 10 to 15 degree half angle, compact but lossy
    'standard diffuser': 0.85,   # 6 degree half angle, the usual design point
    'long diffuser':     0.92    # 3 degree half angle, maximum recovery, long and heavy
}

# Discharge coefficients for a machined converging-diverging throat. Much higher than an orifice
# because the converging section eliminates the vena contracta entirely.
VENTURI_DISCHARGE_COEFFICIENTS = {
    'machined':   0.985,   # ground and polished throat, classical venturi contour
    'as cast':    0.960,
    'lpbf':       0.940    # additively manufactured, as-built internal surface
}

class CavitatingVenturi:

    '''

    Sizing and operating margin for a cavitating venturi.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    upstreamPressure : float
        Static pressure upstream of the venturi [Pa, absolute]
    downstreamPressure : float
        Static pressure downstream of the diffuser [Pa, absolute]
    upstreamTemperature : float
        Fluid temperature [K]
    massFlow : float
        Required mass flow rate [kg/s]. Leave unset to analyze a known throat.
    throatDiameter : float
        Throat diameter [m]. Leave unset when sizing.
    inletDiameter : float
        Inlet pipe diameter [m], for the beta ratio and the velocity of approach
    diffuserType : str
        Key into DIFFUSER_RECOVERY
    surfaceFinish : str
        Key into VENTURI_DISCHARGE_COEFFICIENTS

    Key Output Properties:
    ----------------------
    throatDiameter : float
        Sized throat diameter [m]
    throatVelocity : float
        Velocity at the throat [m/s]
    isChoked : bool
        True when the venturi is cavitating and therefore regulating
    unchokePressure : float
        The downstream pressure at which regulation is lost [Pa]
    unchokeMargin : float
        (unchokePressure - downstreamPressure) / upstreamPressure [-]
    unrecoveredPressureLoss : float
        Permanent pressure loss through the device [Pa]
    cavitationNumber : float
        (P1 - Pvapor) / (0.5 * rho * Vthroat^2) [-]

    Public Methods:
    ---------------
    setInputs(inputs)          Load a configuration dictionary
    sizeThroat()               Find the throat diameter for the required flow
    calculateMassFlow()        Forward problem from a known throat
    calculateUnchokeMargin()   Operating margin against loss of regulation
    generateReport(outputDir)  Formatted results table

    Typical Workflow:
    -----------------
    >>> venturi = CavitatingVenturi()
    >>> venturi.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.20e6,
    ...                    'downstreamPressure': 1.60e6, 'upstreamTemperature': 293.15,
    ...                    'massFlow': 0.045, 'inletDiameter': 0.00493})
    >>> venturi.sizeThroat()
    >>> print(venturi.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid State -- #

        self.fluid                   = ''      # [case sensitive string]
        self.upstreamPressure        = np.nan  # [Pa, absolute]
        self.downstreamPressure      = np.nan  # [Pa, absolute]
        self.upstreamTemperature     = np.nan  # [K]

        # -- Geometry -- #

        self.throatDiameter          = np.nan  # [m]
        self.throatArea              = np.nan  # [m^2]
        self.inletDiameter           = np.nan  # [m], upstream pipe ID
        self.betaRatio               = np.nan  # [-], throat over inlet diameter
        self.convergingHalfAngle     = 10.5    # [deg], classical venturi inlet cone, 21 deg included
        self.diffuserHalfAngle       = 6.0     # [deg], sets the recovery and the length
        self.diffuserType            = 'standard diffuser'  # key into DIFFUSER_RECOVERY
        self.surfaceFinish           = 'machined'           # key into VENTURI_DISCHARGE_COEFFICIENTS
        self.dischargeCoefficient    = np.nan  # [-], overrides the surface finish lookup

        # -- Duty -- #

        self.massFlow                = np.nan  # [kg/s]

        # -- Results -- #

        self.density                 = np.nan  # [kg/m^3]
        self.vaporPressure           = np.nan  # [Pa]
        self.throatVelocity          = np.nan  # [m/s]
        self.isChoked                = False   # [-], cavitating and therefore regulating
        self.unchokePressure         = np.nan  # [Pa], downstream pressure at loss of regulation
        self.unchokeMargin           = np.nan  # [-], fraction of upstream pressure
        self.unrecoveredPressureLoss = np.nan  # [Pa]
        self.cavitationNumber        = np.nan  # [-]
        self.diffuserLength          = np.nan  # [m]
        self.overallLength           = np.nan  # [m]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, upstreamPressure, downstreamPressure, upstreamTemperature.

        '''

        requiredParams = {
            'fluid':               'Venturi fluid species not provided.',
            'upstreamPressure':    'Venturi upstream pressure not provided.',
            'downstreamPressure':  'Venturi downstream pressure not provided.',
            'upstreamTemperature': 'Venturi upstream temperature not provided.'
        }

        optionalParams = ['massFlow', 'throatDiameter', 'inletDiameter', 'convergingHalfAngle',
                          'diffuserHalfAngle', 'diffuserType', 'surfaceFinish', 'dischargeCoefficient']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._evaluateFluidState()

    def sizeThroat(self) -> float:

        '''

        Size the throat for the required mass flow, assuming the venturi is cavitating.

        The relation inverts directly, with no iteration, because the choked mass flow does not
        depend on the throat velocity through any Reynolds-dependent term: a venturi discharge
        coefficient is essentially constant above Re = 10^5, which it always is at a throat.

            At = mdot / (Cd * sqrt(2 * rho * (P1 - Pvapor)))

        After sizing, calculateUnchokeMargin() is called automatically, because a throat sized
        without checking that it actually chokes at the operating point is worse than useless.

        '''

        if np.isnan(self.massFlow):
            raise InvalidInputError(
                message       = 'sizeThroat needs a target mass flow.',
                parameterName = 'massFlow', value = self.massFlow, validRange = 'Positive real'
            )

        dischargeCoefficient = self._dischargeCoefficient()
        drivingPressure      = self.upstreamPressure - self.vaporPressure

        if drivingPressure <= 0.0:
            raise InvalidInputError(
                message       = ('Upstream pressure is at or below the propellant vapor pressure. The fluid is '
                                 'already boiling in the feed line and no venturi will regulate it.'),
                parameterName = 'upstreamPressure', value = self.upstreamPressure,
                validRange    = f'Greater than {self.vaporPressure:.6g} Pa'
            )

        self.throatArea     = self.massFlow / (dischargeCoefficient * np.sqrt(2.0 * self.density * drivingPressure))
        self.throatDiameter = np.sqrt(4.0 * self.throatArea / np.pi)

        self.calculateUnchokeMargin()
        self._calculateGeometry()

        return self.throatDiameter

    def calculateMassFlow(self) -> float:

        '''

        Forward problem: mass flow through a known throat.

        If the venturi is choked, the flow is the cavitating value and downstream pressure is
        irrelevant. If it has unchoked, the device reverts to a conventional venturi flow meter and
        the flow follows the ordinary incompressible relation on (P1 - P2) with the velocity of
        approach factor. The class reports which of those two it used, because the difference
        between them is the whole design intent.

        '''

        if np.isnan(self.throatDiameter):
            raise InvalidInputError(
                message       = 'calculateMassFlow needs a throat diameter. Set throatDiameter, or call sizeThroat().',
                parameterName = 'throatDiameter', value = self.throatDiameter, validRange = 'Positive real'
            )

        self.throatArea      = np.pi * self.throatDiameter**2 / 4.0
        dischargeCoefficient = self._dischargeCoefficient()

        self.calculateUnchokeMargin()

        if self.isChoked:
            drivingPressure = self.upstreamPressure - self.vaporPressure
            velocityOfApproach = 1.0
        else:
            drivingPressure    = self.upstreamPressure - self.downstreamPressure
            velocityOfApproach = self._velocityOfApproach()

        self.massFlow = dischargeCoefficient * velocityOfApproach * self.throatArea * np.sqrt(2.0 * self.density * max(drivingPressure, 0.0))

        self._calculateGeometry()

        return self.massFlow

    def calculateUnchokeMargin(self) -> float:

        '''

        Operating margin against loss of regulation.

        The venturi stays cavitating while the downstream pressure remains below

            P_unchoke = recoveryRatio * P1

        with recoveryRatio taken from the diffuser type. The margin is reported as a fraction of
        upstream pressure, so a margin of 0.15 means the downstream pressure has 15 percent of P1
        of headroom before regulation is lost.

        A design margin below about 0.05 is not a design, it is a coincidence. Chamber pressure
        rises during a burn as the catalyst bed heats, back pressure rises as a filter loads, and
        supply pressure sags over a blowdown. All three eat margin in the same direction.

        '''

        recoveryRatio        = DIFFUSER_RECOVERY.get(self.diffuserType.strip().lower())
        if recoveryRatio is None:
            raise InvalidInputError(
                message       = f'Unknown diffuser type \'{self.diffuserType}\'.',
                parameterName = 'diffuserType', value = self.diffuserType,
                validRange    = str(sorted(DIFFUSER_RECOVERY.keys()))
            )

        self.unchokePressure = recoveryRatio * self.upstreamPressure
        self.isChoked        = self.downstreamPressure < self.unchokePressure
        self.unchokeMargin   = (self.unchokePressure - self.downstreamPressure) / self.upstreamPressure

        # Permanent loss. When choked, everything from P1 down to P2 is spent, but the recoverable
        # part is what the diffuser gives back; the unrecovered part is the real cost of the device.
        self.unrecoveredPressureLoss = (1.0 - recoveryRatio) * self.upstreamPressure

        if not np.isnan(self.throatArea) and self.throatArea > 0.0:
            self.throatVelocity   = self.massFlow / (self.density * self.throatArea) if not np.isnan(self.massFlow) else np.nan
            if not np.isnan(self.throatVelocity):
                dynamicPressure       = 0.5 * self.density * self.throatVelocity**2
                self.cavitationNumber = (self.upstreamPressure - self.vaporPressure) / dynamicPressure

        return self.unchokeMargin

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table, with an explicit statement of whether the device is
        regulating.

        '''

        rows = [
            ['Fluid',                    f'{self.fluid}'],
            ['Upstream pressure',        f'{self.upstreamPressure / 1.0e6:.4f} MPa'],
            ['Downstream pressure',      f'{self.downstreamPressure / 1.0e6:.4f} MPa'],
            ['Vapor pressure',           f'{self.vaporPressure / 1.0e3:.4f} kPa'],
            ['Temperature',              f'{self.upstreamTemperature:.2f} K'],
            ['Density',                  f'{self.density:.3f} kg/m^3'],
            ['Throat diameter',          f'{self.throatDiameter * 1.0e3:.4f} mm'],
            ['Throat area',              f'{self.throatArea * 1.0e6:.5f} mm^2'],
            ['Beta ratio',               f'{self.betaRatio:.4f}' if not np.isnan(self.betaRatio) else 'inlet diameter not given'],
            ['Discharge coefficient',    f'{self._dischargeCoefficient():.4f}'],
            ['Mass flow',                f'{self.massFlow:.5f} kg/s'],
            ['Throat velocity',          f'{self.throatVelocity:.2f} m/s'],
            ['Cavitation number',        f'{self.cavitationNumber:.4f}'],
            ['Diffuser type',            f'{self.diffuserType}'],
            ['Regulating (choked)',      f'{self.isChoked}'],
            ['Unchoke pressure',         f'{self.unchokePressure / 1.0e6:.4f} MPa'],
            ['Unchoke margin',           f'{self.unchokeMargin * 100.0:+.2f} % of P1'],
            ['Unrecovered loss',         f'{self.unrecoveredPressureLoss / 1.0e6:.4f} MPa'],
            ['Diffuser length',          f'{self.diffuserLength * 1.0e3:.2f} mm'],
            ['Overall length',           f'{self.overallLength * 1.0e3:.2f} mm']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'CAVITATING VENTURI REPORT')

        if not self.isChoked:
            report += ('\n\nWARNING: this venturi is NOT choked at the stated downstream pressure. It is behaving as a '
                       'conventional venturi and the flow is a function of downstream pressure. Either lower the '
                       'downstream pressure, raise the upstream pressure, or accept that this is not a flow control '
                       'device at this operating point.')
        elif self.unchokeMargin < 0.05:
            report += (f'\n\nWARNING: unchoke margin is only {self.unchokeMargin * 100.0:.2f} percent of upstream pressure. '
                       'Chamber pressure rise, filter loading and supply pressure decay all consume this margin in the '
                       'same direction. Target at least 10 percent.')

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'cavitatingVenturiReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.upstreamPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Venturi upstream pressure must be absolute and positive.',
                parameterName = 'upstreamPressure', value = self.upstreamPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if self.downstreamPressure > self.upstreamPressure:
            raise InvalidInputError(
                message       = 'Downstream pressure exceeds upstream pressure.',
                parameterName = 'downstreamPressure', value = self.downstreamPressure,
                validRange    = f'0 to {self.upstreamPressure:.6g} Pa'
            )

        if self.surfaceFinish.strip().lower() not in VENTURI_DISCHARGE_COEFFICIENTS:
            raise InvalidInputError(
                message       = f'Unknown surface finish \'{self.surfaceFinish}\'.',
                parameterName = 'surfaceFinish', value = self.surfaceFinish,
                validRange    = str(sorted(VENTURI_DISCHARGE_COEFFICIENTS.keys()))
            )

    def _evaluateFluidState(self) -> None:

        '''

        Density and vapor pressure at the upstream state. A cavitating venturi is a liquid device by
        definition, so a gas input is a configuration error rather than an alternate mode.

        '''

        self.density = float(fluidProps(self.fluid, 'TP', 'D', self.upstreamTemperature, self.upstreamPressure))

        if self.fluid.strip().upper() in ('N2H4', 'HYDRAZINE'):
            self.vaporPressure = float(fluidProps(self.fluid, 'TP', 'P', self.upstreamTemperature, self.upstreamPressure))
            return

        criticalTemperature = float(fluidProps(self.fluid, 'TP', 'TCRIT', self.upstreamTemperature, self.upstreamPressure))

        if self.upstreamTemperature >= criticalTemperature:
            raise InvalidInputError(
                message       = ('A cavitating venturi requires a liquid with a vapor pressure. The fluid is above its '
                                 'critical temperature and has no saturation line.'),
                parameterName = 'upstreamTemperature', value = self.upstreamTemperature,
                validRange    = f'Below {criticalTemperature:.4g} K'
            )

        self.vaporPressure = float(fluidProps(self.fluid, 'TQ', 'P', self.upstreamTemperature, 0.0))

        if self.upstreamPressure <= self.vaporPressure:
            raise InvalidInputError(
                message       = 'Upstream state is not liquid: pressure is at or below the saturation pressure.',
                parameterName = 'upstreamPressure', value = self.upstreamPressure,
                validRange    = f'Greater than {self.vaporPressure:.6g} Pa'
            )

    def _dischargeCoefficient(self) -> float:

        '''

        Discharge coefficient from the explicit override or the surface finish lookup.

        '''

        if not np.isnan(self.dischargeCoefficient):
            return self.dischargeCoefficient

        return VENTURI_DISCHARGE_COEFFICIENTS[self.surfaceFinish.strip().lower()]

    def _velocityOfApproach(self) -> float:

        '''

        Velocity of approach factor 1 / sqrt(1 - beta^4), used only in the unchoked branch. When
        choked the upstream velocity head is irrelevant because the throat is pinned at vapor
        pressure regardless.

        '''

        if np.isnan(self.inletDiameter) or np.isnan(self.throatDiameter):
            return 1.0

        self.betaRatio = self.throatDiameter / self.inletDiameter

        return 1.0 / np.sqrt(1.0 - self.betaRatio**4)

    def _calculateGeometry(self) -> None:

        '''

        Derive the beta ratio and the physical envelope from the cone angles.

        The diffuser length is what makes a cavitating venturi a packaging problem. A 6 degree half
        angle diffuser expanding from a 2 mm throat back to a 5 mm line is 14 mm long, which is
        nothing; the same diffuser on a 20 mm throat in a 50 mm line is 140 mm, which has to go
        somewhere. Shortening the diffuser costs recovery, which costs unchoke margin.

        '''

        if np.isnan(self.inletDiameter) or np.isnan(self.throatDiameter):
            return

        self.betaRatio = self.throatDiameter / self.inletDiameter

        radiusChange        = (self.inletDiameter - self.throatDiameter) / 2.0
        convergingLength    = radiusChange / np.tan(np.radians(self.convergingHalfAngle))
        self.diffuserLength = radiusChange / np.tan(np.radians(self.diffuserHalfAngle))

        # Throat land, conventionally about one throat diameter, to stabilize the cavity
        throatLength       = self.throatDiameter
        self.overallLength = convergingLength + throatLength + self.diffuserLength
