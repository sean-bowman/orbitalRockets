
# -- Valve Class Definition -- #

'''

Valve sizing, flow coefficient analysis, characteristic selection and actuation loads.

A valve is an orifice whose area you can change, and almost every question about a valve reduces to
one of four:

1. What flow coefficient do I need?      IEC 60534 sizing, liquid and gas, choked and unchoked
2. What happens when it chokes?          Pressure recovery factor FL, terminal pressure ratio xT
3. How does it behave part-open?         Inherent characteristic, installed characteristic, authority
4. What does it take to move it?         Seat load, unbalanced pressure force, actuator torque

The class answers all four. The one it gets asked least and should be asked most is the third:
a valve sized correctly at full open can still be uncontrollable, because in a system whose
resistance is dominated by the line rather than the valve, the installed characteristic is nothing
like the inherent one and all the control happens in the first ten percent of travel.

A note on flow coefficients. Cv is defined as US gallons per minute of 60 degF water that pass with
a 1 psi differential. It is an imperial definition wearing an engineering hat, and it will not go
away, so this class carries it and converts at the boundary. Internally everything is SI:

    mdot [kg/s] = Cv * 2.40172e-5 * sqrt(rho [kg/m^3] * dP [Pa])

Kv, the metric equivalent (m^3/h of water at 1 bar), is Cv * 0.8646.

See Also:
---------
Orifice          : Fixed area version of the same physics
CheckValve       : Passive one-way valve, cracking pressure driven
Regulator        : Valve with an integral control loop on outlet pressure
WaterHammer      : What happens when this valve closes too fast

Theory: docs/Valves.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                       KV_PER_CV, PA_PER_PSIA, NM_PER_INLBF,
                       InvalidInputError, ChokedFlowError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                        KV_PER_CV, PA_PER_PSIA, NM_PER_INLBF,
                        InvalidInputError, ChokedFlowError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# SI flow coefficient constant. Derived rather than looked up, from the definition of Cv:
# 1 gpm = 6.30902e-5 m^3/s, 1 psi = 6894.757 Pa, water at 60 degF = 999.0 kg/m^3.
#   mdot [kg/s] = Cv * CV_FLOW_CONSTANT * sqrt(rho [kg/m^3] * dP [Pa])
CV_FLOW_CONSTANT = 2.40172e-5

# Valve type data. FL is the liquid pressure recovery factor: how much of the pressure dropped at
# the vena contracta is recovered downstream. A high FL (globe) means little recovery, so the vena
# contracta pressure is close to the outlet pressure and the valve resists cavitation. A low FL
# (butterfly, ball) means strong recovery, a much lower vena contracta pressure, and cavitation at
# differentials where a globe valve would be perfectly happy.
#
# xT is the terminal pressure drop ratio for gas: the value of dP/P1 at which the valve chokes.
# Note how low it is for high-recovery valves. A butterfly valve chokes at a pressure ratio a globe
# valve sails through.
#
# torqueFactor is a dimensionless breakaway torque coefficient, T = torqueFactor * dP * d^3, used as
# a first-cut actuator sizing estimate. Vendor data supersedes it in every case.
VALVE_TYPES = {
    'globe':            {'FL': 0.90, 'xT': 0.72, 'CvPerInch2': 12.0, 'torqueFactor': 0.00, 'characteristic': 'equal percentage'},
    'globe cage':       {'FL': 0.90, 'xT': 0.75, 'CvPerInch2': 10.0, 'torqueFactor': 0.00, 'characteristic': 'linear'},
    'angle':            {'FL': 0.90, 'xT': 0.72, 'CvPerInch2': 14.0, 'torqueFactor': 0.00, 'characteristic': 'equal percentage'},
    'ball full bore':   {'FL': 0.60, 'xT': 0.15, 'CvPerInch2': 45.0, 'torqueFactor': 0.06, 'characteristic': 'equal percentage'},
    'ball reduced':     {'FL': 0.68, 'xT': 0.22, 'CvPerInch2': 28.0, 'torqueFactor': 0.05, 'characteristic': 'equal percentage'},
    'ball segmented':   {'FL': 0.66, 'xT': 0.30, 'CvPerInch2': 25.0, 'torqueFactor': 0.05, 'characteristic': 'equal percentage'},
    'butterfly':        {'FL': 0.55, 'xT': 0.15, 'CvPerInch2': 35.0, 'torqueFactor': 0.04, 'characteristic': 'quick opening'},
    'butterfly high perf': {'FL': 0.70, 'xT': 0.30, 'CvPerInch2': 30.0, 'torqueFactor': 0.05, 'characteristic': 'quick opening'},
    'gate':             {'FL': 0.80, 'xT': 0.30, 'CvPerInch2': 40.0, 'torqueFactor': 0.00, 'characteristic': 'quick opening'},
    'needle':           {'FL': 0.95, 'xT': 0.80, 'CvPerInch2': 1.5,  'torqueFactor': 0.00, 'characteristic': 'linear'},
    'poppet':           {'FL': 0.90, 'xT': 0.72, 'CvPerInch2': 8.0,  'torqueFactor': 0.00, 'characteristic': 'linear'},
    'plug':             {'FL': 0.84, 'xT': 0.55, 'CvPerInch2': 30.0, 'torqueFactor': 0.05, 'characteristic': 'linear'}
}

# Equal percentage rangeability. The ratio of maximum to minimum controllable Cv. R = 50 is the
# industry standard for a globe valve trim.
EQUAL_PERCENTAGE_RANGEABILITY = 50.0

# Typical seat contact stress required to seal, by seat material [Pa]. Multiply by the seat contact
# area to get the seating load the actuator has to deliver on top of the pressure unbalance.
SEAT_SEALING_STRESS = {
    'ptfe':          14.0e6,   # soft seat, low load, limited temperature and no cryogenic creep margin
    'peek':          35.0e6,
    'kel-f':         28.0e6,   # PCTFE, the LOX-compatible soft seat of choice
    'vespel':        45.0e6,
    'elastomer':      7.0e6,   # o-ring or lip seat
    'metal to metal': 200.0e6  # lapped metal seat; the only option for hot gas or long term storage
}

class Valve:

    '''

    Flow coefficient sizing and actuation analysis for a variable restriction.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    upstreamPressure : float
        Static pressure upstream [Pa, absolute]
    downstreamPressure : float
        Static pressure downstream [Pa, absolute]
    upstreamTemperature : float
        Fluid temperature upstream [K]
    massFlow : float
        Required mass flow rate [kg/s]. Leave unset to analyze a known Cv.
    flowCoefficient : float
        Valve Cv [-]. Leave unset to size it.
    valveType : str
        Key into VALVE_TYPES. Sets FL, xT, and the default characteristic.
    nominalSize : float
        Valve nominal port size [m], used for the actuation estimate and the Cv/K conversion
    travelFraction : float
        Fractional stem travel or rotation, 0 to 1 [-]
    characteristic : str
        'linear', 'equal percentage' or 'quick opening'. Overrides the valve type default.
    seatMaterial : str
        Key into SEAT_SEALING_STRESS
    seatDiameter : float
        Sealing diameter [m]. Defaults to the nominal size.

    Key Output Properties:
    ----------------------
    requiredFlowCoefficient : float
        Cv needed to pass massFlow at the given differential [-]
    flowCoefficientKv : float
        Metric equivalent [m^3/h at 1 bar]
    isChoked : bool
        True when the valve is at or past its choking condition
    chokedPressureDrop : float
        The dP at which choking begins [Pa]
    lossCoefficient : float
        Equivalent K referenced to the nominal port area [-]
    equivalentOrificeArea : float
        Area of a Cd = 0.61 orifice that would pass the same flow [m^2]
    installedFlowFraction : float
        Flow at the current travel divided by flow at full open, with the system resistance
        included [-]
    actuationForce / actuationTorque : float
        First-cut actuator sizing [N] / [N-m]

    Public Methods:
    ---------------
    setInputs(inputs)                 Load a configuration dictionary
    sizeFlowCoefficient()             Find the Cv required for the duty
    calculateMassFlow()               Forward problem from a known Cv
    calculateCharacteristic(points)   Inherent and installed characteristic curves
    calculateActuationLoad()          Seat load, unbalance force, breakaway torque
    convertToLossCoefficient()        Cv to K and to an equivalent orifice area
    generateReport(outputDir)         Formatted results table

    Typical Workflow:
    -----------------
    >>> isolationValve = Valve()
    >>> isolationValve.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.35e6,
    ...                           'downstreamPressure': 2.30e6, 'upstreamTemperature': 293.15,
    ...                           'massFlow': 0.045, 'valveType': 'ball full bore',
    ...                           'nominalSize': 0.00635})
    >>> isolationValve.sizeFlowCoefficient()
    >>> isolationValve.calculateActuationLoad()
    >>> print(isolationValve.generateReport())

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

        # -- Duty -- #

        self.massFlow                = np.nan  # [kg/s]
        self.flowCoefficient         = np.nan  # [-], Cv. Set to analyze rather than size.

        # -- Valve Definition -- #

        self.valveType               = 'ball full bore'  # key into VALVE_TYPES
        self.nominalSize             = np.nan  # [m], port diameter
        self.characteristic          = ''      # overrides the valve type default if set
        self.travelFraction          = 1.0     # [-], 0 closed to 1 full open
        self.pressureRecoveryFactor  = np.nan  # [-], FL. Overrides the valve type value.
        self.terminalPressureRatio   = np.nan  # [-], xT. Overrides the valve type value.

        # -- Seat and Actuation -- #

        self.seatMaterial            = 'ptfe'  # key into SEAT_SEALING_STRESS
        self.seatDiameter            = np.nan  # [m], defaults to nominalSize
        self.seatContactWidth        = np.nan  # [m], defaults to 2 percent of the seat diameter
        self.springPreload           = 0.0     # [N], return spring force at the closed position
        self.actuatorEfficiency      = 0.80    # [-], mechanism losses between actuator and seat

        # -- System Context (for the installed characteristic) -- #

        # Valve authority is the fraction of the total system pressure drop that the valve takes at
        # full open. Below about 0.3 the valve loses control authority and the installed
        # characteristic collapses toward quick-opening no matter what trim is fitted.
        self.systemPressureDrop      = np.nan  # [Pa], total system dP at the design flow

        # -- Results -- #

        self.requiredFlowCoefficient = np.nan  # [-], Cv
        self.flowCoefficientKv       = np.nan  # [m^3/h at 1 bar]
        self.pressureDrop            = np.nan  # [Pa]
        self.chokedPressureDrop      = np.nan  # [Pa]
        self.isChoked                = False   # [-]
        self.isLiquid                = True    # [-]
        self.density                 = np.nan  # [kg/m^3], upstream
        self.vaporPressure           = np.nan  # [Pa]
        self.criticalPressure        = np.nan  # [Pa]
        self.expansionFactor         = 1.0     # [-], Y for gas sizing
        self.pressureDropRatio       = np.nan  # [-], x = dP/P1
        self.lossCoefficient         = np.nan  # [-], equivalent K
        self.equivalentOrificeArea   = np.nan  # [m^2]
        self.valveAuthority          = np.nan  # [-]
        self.actuationForce          = np.nan  # [N]
        self.actuationTorque         = np.nan  # [N-m]
        self.seatLoad                = np.nan  # [N]
        self.unbalanceForce          = np.nan  # [N]
        self.cavitationIndex         = np.nan  # [-], sigma = (P1 - Pv) / (P1 - P2)
        self.cavitationStatus        = ''      # 'none' / 'incipient' / 'choked' / 'flashing'

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, upstreamPressure, downstreamPressure, upstreamTemperature.

        '''

        requiredParams = {
            'fluid':               'Valve fluid species not provided.',
            'upstreamPressure':    'Valve upstream pressure not provided.',
            'downstreamPressure':  'Valve downstream pressure not provided.',
            'upstreamTemperature': 'Valve upstream temperature not provided.'
        }

        optionalParams = ['massFlow', 'flowCoefficient', 'valveType', 'nominalSize', 'characteristic',
                          'travelFraction', 'pressureRecoveryFactor', 'terminalPressureRatio',
                          'seatMaterial', 'seatDiameter', 'seatContactWidth', 'springPreload',
                          'actuatorEfficiency', 'systemPressureDrop']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._evaluateFluidState()

    def sizeFlowCoefficient(self) -> float:

        '''

        Find the Cv required to pass massFlow at the specified differential.

        For a liquid this inverts the IEC 60534-2-1 sizing equation with the choked-flow limit
        applied: if the actual differential exceeds FL^2 * (P1 - FF * Pv), the valve is choked and
        the sizing differential is capped at that value. Sizing a choked valve on the full
        differential undersizes it, sometimes badly.

        For a gas the expansion factor Y and the terminal pressure drop ratio xT are applied the
        same way. Once x exceeds Fgamma * xT the flow is choked, Y is pinned at 2/3, and further
        pressure drop buys nothing.

        Returns the required Cv at the current travel fraction. If travelFraction is less than 1,
        the returned value is the FULL OPEN Cv the valve must have in order to deliver the duty at
        that partial travel, which is the number you actually shop for.

        '''

        if np.isnan(self.massFlow):
            raise InvalidInputError(
                message       = 'sizeFlowCoefficient needs a target mass flow.',
                parameterName = 'massFlow', value = self.massFlow, validRange = 'Positive real'
            )

        self.pressureDrop = self.upstreamPressure - self.downstreamPressure

        sizingPressureDrop = self._sizingPressureDrop()

        # Invert mdot = Cv * K * sqrt(rho * dP)
        flowCoefficientAtTravel = self.massFlow / (CV_FLOW_CONSTANT * self.expansionFactor * np.sqrt(self.density * sizingPressureDrop))

        # Scale up to full open through the inherent characteristic
        travelFraction               = min(max(self.travelFraction, 1.0e-6), 1.0)
        self.requiredFlowCoefficient = flowCoefficientAtTravel / self._inherentFraction(travelFraction)

        self.flowCoefficient   = self.requiredFlowCoefficient
        self.flowCoefficientKv = self.requiredFlowCoefficient * KV_PER_CV

        self.convertToLossCoefficient()
        self._assessCavitation()

        return self.requiredFlowCoefficient

    def calculateMassFlow(self) -> float:

        '''

        Forward problem: mass flow through a valve of known Cv at the current travel and
        differential. The same regime logic as sizeFlowCoefficient applies.

        '''

        if np.isnan(self.flowCoefficient):
            raise InvalidInputError(
                message       = 'calculateMassFlow needs a flow coefficient. Set flowCoefficient, or call sizeFlowCoefficient().',
                parameterName = 'flowCoefficient', value = self.flowCoefficient, validRange = 'Positive real'
            )

        self.pressureDrop  = self.upstreamPressure - self.downstreamPressure
        sizingPressureDrop = self._sizingPressureDrop()

        travelFraction = min(max(self.travelFraction, 0.0), 1.0)
        effectiveCv    = self.flowCoefficient * self._inherentFraction(travelFraction)

        self.massFlow = effectiveCv * CV_FLOW_CONSTANT * self.expansionFactor * np.sqrt(self.density * sizingPressureDrop)

        self.convertToLossCoefficient()
        self._assessCavitation()

        return self.massFlow

    def calculateCharacteristic(self, numberOfPoints: int = 21) -> dict:

        '''

        Inherent and installed characteristic curves.

        The inherent characteristic is what the trim gives at constant differential: linear, equal
        percentage, or quick opening. It is a property of the valve alone.

        The installed characteristic is what you actually get once the valve is plumbed into a
        system whose resistance rises with flow. As the valve opens, more of the total pressure drop
        shifts to the line, the valve differential collapses, and the flow rises much less than the
        inherent curve promises. The metric is valve authority:

            N = dP_valve(full open) / dP_total(full open)

        Authority above 0.5 means the installed curve is close to the inherent one. Authority below
        0.2 means every characteristic degenerates toward quick-opening: the valve does all of its
        work in the first few percent of travel and is effectively an on/off device. That is the
        single most common reason a control valve will not hold a setpoint.

        Requires systemPressureDrop to compute the installed curve. Without it, only the inherent
        curve is returned.

        Returns a dictionary with 'travel', 'inherent', 'installed' and 'authority'.

        '''

        travel   = np.linspace(0.0, 1.0, numberOfPoints)
        inherent = np.array([self._inherentFraction(max(fraction, 1.0e-6)) for fraction in travel])
        inherent[0] = 0.0

        result = {'travel': travel, 'inherent': inherent, 'installed': None, 'authority': np.nan}

        if np.isnan(self.systemPressureDrop) or np.isnan(self.pressureDrop):
            return result

        # Series resistance model. The rest of the system takes a drop proportional to flow squared;
        # the valve takes the remainder. Solving for the flow fraction at each travel position:
        #
        #   dP_total = dP_valve + dP_rest,  dP_valve ~ (q/Cv_frac)^2,  dP_rest ~ q^2
        #
        # gives q(h) = 1 / sqrt( (1 - N) + N / f(h)^2 ) with N the valve authority.
        totalPressureDrop = self.systemPressureDrop
        authority         = self.pressureDrop / totalPressureDrop
        authority         = min(max(authority, 1.0e-6), 1.0)

        with np.errstate(divide = 'ignore', invalid = 'ignore'):
            installed = 1.0 / np.sqrt((1.0 - authority) + authority / np.maximum(inherent, 1.0e-9)**2)
        installed[0] = 0.0

        self.valveAuthority  = authority
        result['installed']  = installed
        result['authority']  = authority

        return result

    def calculateActuationLoad(self) -> dict:

        '''

        First-cut actuator sizing: the load the actuator must deliver to seat and unseat the valve.

        Three contributions:

        seat load        The contact force required to make the seat seal, seat sealing stress times
                         the seat contact area. Soft seats need little; a lapped metal seat needs a
                         great deal, which is why metal-seated cryogenic valves have such large
                         actuators.

        unbalance force  The differential pressure acting over the unbalanced seat area. For a
                         poppet or globe valve this is dP times the seat area and it can dominate
                         everything else at high pressure. Balanced trim exists specifically to
                         cancel it, at the cost of a leak path across the balance seal.

        spring preload   The return spring, which for a fail-safe valve must be strong enough to
                         close the valve against the full differential with no actuation power.

        For quarter-turn valves the torque estimate T = torqueFactor * dP * d^3 is used instead of
        a force. It is a rough approximation only: real breakaway torque depends on seat material,
        seat interference, temperature history and how long the valve has been sitting closed. Size
        actuators from vendor torque data with a safety factor of at least 1.5, and remember that
        breakaway after a long cold soak can be several times the catalog value.

        '''

        if np.isnan(self.nominalSize):
            raise InvalidInputError(
                message       = 'calculateActuationLoad needs the valve nominal port size.',
                parameterName = 'nominalSize', value = self.nominalSize, validRange = 'Positive real'
            )

        seatDiameter     = self.nominalSize if np.isnan(self.seatDiameter) else self.seatDiameter
        seatContactWidth = 0.02 * seatDiameter if np.isnan(self.seatContactWidth) else self.seatContactWidth

        sealingStress = SEAT_SEALING_STRESS.get(self.seatMaterial.strip().lower())
        if sealingStress is None:
            raise InvalidInputError(
                message       = f'Unknown seat material \'{self.seatMaterial}\'.',
                parameterName = 'seatMaterial', value = self.seatMaterial,
                validRange    = str(sorted(SEAT_SEALING_STRESS.keys()))
            )

        seatContactArea = np.pi * seatDiameter * seatContactWidth
        seatArea        = np.pi * seatDiameter**2 / 4.0

        self.seatLoad       = sealingStress * seatContactArea
        self.unbalanceForce = (self.upstreamPressure - self.downstreamPressure) * seatArea
        self.actuationForce = (self.seatLoad + self.unbalanceForce + self.springPreload) / self.actuatorEfficiency

        torqueFactor = VALVE_TYPES[self.valveType.strip().lower()]['torqueFactor']
        if torqueFactor > 0.0:
            self.actuationTorque = torqueFactor * (self.upstreamPressure - self.downstreamPressure) * self.nominalSize**3 / self.actuatorEfficiency
        else:
            self.actuationTorque = np.nan

        return {
            'seatLoad':        self.seatLoad,
            'unbalanceForce':  self.unbalanceForce,
            'springPreload':   self.springPreload,
            'actuationForce':  self.actuationForce,
            'actuationTorque': self.actuationTorque
        }

    def convertToLossCoefficient(self, dischargeCoefficient: float = 0.61) -> dict:

        '''

        Convert Cv into the two forms the rest of a fluid system model wants:

        K, the dimensionless loss coefficient referenced to the nominal port area, so the valve can
        be dropped into a Line minor-loss budget:

            K = 2 * A^2 / (N^2 * Cv^2)

        and the equivalent orifice area, so the valve can be compared directly against a fixed
        restriction:

            A_eq = Cv * N / (Cd * sqrt(2))

        The K conversion needs a reference area and therefore needs nominalSize. Without it, only
        the equivalent orifice area is returned.

        '''

        flowCoefficient = self.flowCoefficient if not np.isnan(self.flowCoefficient) else self.requiredFlowCoefficient

        if np.isnan(flowCoefficient) or flowCoefficient <= 0.0:
            return {'lossCoefficient': np.nan, 'equivalentOrificeArea': np.nan}

        self.equivalentOrificeArea = flowCoefficient * CV_FLOW_CONSTANT / (dischargeCoefficient * np.sqrt(2.0))

        if not np.isnan(self.nominalSize):
            referenceArea        = np.pi * self.nominalSize**2 / 4.0
            self.lossCoefficient = 2.0 * referenceArea**2 / (CV_FLOW_CONSTANT**2 * flowCoefficient**2)

        return {'lossCoefficient': self.lossCoefficient, 'equivalentOrificeArea': self.equivalentOrificeArea}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        valveData = VALVE_TYPES[self.valveType.strip().lower()]

        rows = [
            ['Fluid',                   f'{self.fluid}'],
            ['Valve type',              f'{self.valveType}'],
            ['Characteristic',          f'{self._characteristic()}'],
            ['Upstream pressure',       f'{self.upstreamPressure / 1.0e6:.4f} MPa'],
            ['Downstream pressure',     f'{self.downstreamPressure / 1.0e6:.4f} MPa'],
            ['Pressure drop',           f'{self.pressureDrop / 1.0e3:.3f} kPa'],
            ['Upstream temperature',    f'{self.upstreamTemperature:.2f} K'],
            ['Upstream density',        f'{self.density:.3f} kg/m^3'],
            ['Mass flow',               f'{self.massFlow:.5f} kg/s'],
            ['Travel fraction',         f'{self.travelFraction:.3f}'],
            ['Required Cv (full open)', f'{self.requiredFlowCoefficient:.4f}'],
            ['Equivalent Kv',           f'{self.flowCoefficientKv:.4f}'],
            ['Pressure recovery FL',    f'{self._recoveryFactor():.3f}'],
            ['Terminal ratio xT',       f'{self._terminalRatio():.3f}'],
            ['Choked',                  f'{self.isChoked}'],
            ['Choked pressure drop',    f'{self.chokedPressureDrop / 1.0e3:.3f} kPa']
        ]

        if self.isLiquid:
            rows.append(['Cavitation index',  f'{self.cavitationIndex:.3f}'])
            rows.append(['Cavitation status', f'{self.cavitationStatus}'])
        else:
            rows.append(['Pressure drop ratio x', f'{self.pressureDropRatio:.4f}'])
            rows.append(['Expansion factor Y',    f'{self.expansionFactor:.4f}'])

        if not np.isnan(self.lossCoefficient):
            rows.append(['Equivalent K',          f'{self.lossCoefficient:.4f}'])
        if not np.isnan(self.equivalentOrificeArea):
            rows.append(['Equivalent orifice dia', f'{np.sqrt(4.0 * self.equivalentOrificeArea / np.pi) * 1.0e3:.4f} mm'])
        if not np.isnan(self.valveAuthority):
            rows.append(['Valve authority',       f'{self.valveAuthority:.3f}'])

        if not np.isnan(self.actuationForce):
            rows.append(['Seat load',        f'{self.seatLoad:.1f} N'])
            rows.append(['Unbalance force',  f'{self.unbalanceForce:.1f} N'])
            rows.append(['Actuation force',  f'{self.actuationForce:.1f} N'])
        if not np.isnan(self.actuationTorque):
            rows.append(['Breakaway torque', f'{self.actuationTorque:.2f} N-m ({self.actuationTorque / NM_PER_INLBF:.1f} in-lbf)'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'VALVE SIZING REPORT')

        # Suitability note based on the recovery factor and the duty
        if self.isLiquid and self.cavitationStatus in ('choked', 'flashing'):
            report += (f'\n\nNOTE: this duty cavitates in a {self.valveType} (FL = {self._recoveryFactor():.2f}). '
                       f'A higher recovery factor trim (globe FL = 0.90, or multi-stage anti-cavitation trim) '
                       f'would tolerate the same differential without damage.')

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'valveReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.valveType.strip().lower() not in VALVE_TYPES:
            raise InvalidInputError(
                message       = f'Unknown valve type \'{self.valveType}\'.',
                parameterName = 'valveType', value = self.valveType,
                validRange    = str(sorted(VALVE_TYPES.keys()))
            )

        if self.upstreamPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Valve upstream pressure must be absolute and positive.',
                parameterName = 'upstreamPressure', value = self.upstreamPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if self.downstreamPressure > self.upstreamPressure:
            raise InvalidInputError(
                message       = 'Downstream pressure exceeds upstream pressure. Check the flow direction.',
                parameterName = 'downstreamPressure', value = self.downstreamPressure,
                validRange    = f'0 to {self.upstreamPressure:.6g} Pa'
            )

        if self.upstreamPressure == self.downstreamPressure:
            raise InvalidInputError(
                message       = 'Zero differential across the valve. A valve with no pressure drop has no defined Cv.',
                parameterName = 'downstreamPressure', value = self.downstreamPressure,
                validRange    = f'Less than {self.upstreamPressure:.6g} Pa'
            )

    def _evaluateFluidState(self) -> None:

        '''

        Upstream density, phase, and the vapor and critical pressures the choked-flow factors need.

        '''

        self.density = float(fluidProps(self.fluid, 'TP', 'D', self.upstreamTemperature, self.upstreamPressure))

        if self.fluid.strip().upper() in ('N2H4', 'HYDRAZINE'):
            self.isLiquid         = True
            self.vaporPressure    = float(fluidProps(self.fluid, 'TP', 'P',     self.upstreamTemperature, self.upstreamPressure))
            self.criticalPressure = float(fluidProps(self.fluid, 'TP', 'PCRIT', self.upstreamTemperature, self.upstreamPressure))
            return

        criticalTemperature   = float(fluidProps(self.fluid, 'TP', 'TCRIT', self.upstreamTemperature, self.upstreamPressure))
        self.criticalPressure = float(fluidProps(self.fluid, 'TP', 'PCRIT', self.upstreamTemperature, self.upstreamPressure))

        if self.upstreamTemperature >= criticalTemperature:
            self.isLiquid      = False
            self.vaporPressure = np.nan
            return

        self.vaporPressure = float(fluidProps(self.fluid, 'TQ', 'P', self.upstreamTemperature, 0.0))
        self.isLiquid      = self.upstreamPressure > self.vaporPressure

    def _characteristic(self) -> str:

        '''

        Active inherent characteristic: the explicit override if set, otherwise the valve type
        default.

        '''

        if self.characteristic:
            return self.characteristic.strip().lower()

        return VALVE_TYPES[self.valveType.strip().lower()]['characteristic']

    def _recoveryFactor(self) -> float:

        '''

        Liquid pressure recovery factor FL, from the override or the valve type table.

        '''

        if not np.isnan(self.pressureRecoveryFactor):
            return self.pressureRecoveryFactor

        return VALVE_TYPES[self.valveType.strip().lower()]['FL']

    def _terminalRatio(self) -> float:

        '''

        Terminal pressure drop ratio xT, from the override or the valve type table.

        '''

        if not np.isnan(self.terminalPressureRatio):
            return self.terminalPressureRatio

        return VALVE_TYPES[self.valveType.strip().lower()]['xT']

    def _inherentFraction(self, travelFraction: float) -> float:

        '''

        Inherent characteristic: fraction of full-open Cv at a given fractional travel.

        linear            f = h
        equal percentage  f = R^(h - 1), equal percentage change in Cv per equal change in travel
        quick opening     f = sqrt(h), most of the capacity in the first part of the stroke

        Equal percentage is the right default for a control valve in a system with meaningful line
        resistance, because its rising slope partially cancels the falling valve differential and
        the installed characteristic comes out closer to linear. That is the entire reason the trim
        shape exists.

        '''

        characteristic = self._characteristic()

        if characteristic == 'linear':
            return travelFraction
        if characteristic in ('equal percentage', 'equal-percentage', 'eqpct'):
            return EQUAL_PERCENTAGE_RANGEABILITY**(travelFraction - 1.0)
        if characteristic in ('quick opening', 'quick-opening', 'quickopening'):
            return np.sqrt(travelFraction)

        raise InvalidInputError(
            message       = f'Unknown valve characteristic \'{characteristic}\'.',
            parameterName = 'characteristic', value = characteristic,
            validRange    = 'linear, equal percentage, or quick opening'
        )

    def _sizingPressureDrop(self) -> float:

        '''

        The differential to use in the sizing equation, capped at the choked value, with the gas
        expansion factor Y set as a side effect.

        Liquid (IEC 60534-2-1):
            FF     = 0.96 - 0.28 * sqrt(Pv / Pc)          liquid critical pressure ratio factor
            dP_max = FL^2 * (P1 - FF * Pv)

        Gas:
            x       = dP / P1
            Fgamma  = gamma / 1.4
            x_max   = Fgamma * xT
            Y       = 1 - x / (3 * Fgamma * xT),  floored at 2/3

        '''

        actualPressureDrop = self.upstreamPressure - self.downstreamPressure

        if self.isLiquid:

            self.expansionFactor = 1.0

            # Liquid critical pressure ratio factor. Accounts for the fact that a fluid near its
            # critical point flashes at a pressure well above its vapor pressure.
            criticalRatioFactor     = 0.96 - 0.28 * np.sqrt(max(self.vaporPressure, 0.0) / self.criticalPressure)
            recoveryFactor          = self._recoveryFactor()
            self.chokedPressureDrop = recoveryFactor**2 * (self.upstreamPressure - criticalRatioFactor * self.vaporPressure)

            self.isChoked = actualPressureDrop >= self.chokedPressureDrop

            return min(actualPressureDrop, self.chokedPressureDrop)

        # -- Gas -- #

        gamma  = float(fluidProps(self.fluid, 'TP', 'Cp/Cv', self.upstreamTemperature, self.upstreamPressure))
        fGamma = gamma / 1.4

        self.pressureDropRatio = actualPressureDrop / self.upstreamPressure
        terminalRatio          = self._terminalRatio()
        chokedRatio            = fGamma * terminalRatio

        self.chokedPressureDrop = chokedRatio * self.upstreamPressure
        self.isChoked           = self.pressureDropRatio >= chokedRatio

        effectiveRatio       = min(self.pressureDropRatio, chokedRatio)
        self.expansionFactor = max(1.0 - effectiveRatio / (3.0 * chokedRatio), 2.0 / 3.0)

        return effectiveRatio * self.upstreamPressure

    def _assessCavitation(self) -> None:

        '''

        Cavitation assessment for liquid service, using the standard service severity index
        sigma = (P1 - Pv) / (P1 - P2).

        Large sigma means the upstream pressure sits far above vapor pressure relative to the
        differential and the vena contracta never reaches vapor pressure. As sigma falls toward
        1/FL^2 the valve begins to cavitate; below that it is fully choked, and if the outlet
        pressure itself falls below vapor pressure the fluid flashes and stays two-phase downstream.

        Cavitation and flashing damage look similar and are fixed differently. Cavitation collapses
        bubbles against metal and is cured by staging the pressure drop or by moving to a
        high-recovery-factor trim. Flashing does not collapse and cannot be cured by trim; it is
        cured by raising the downstream pressure or by accepting hardened trim and erosion.

        '''

        if not self.isLiquid or np.isnan(self.vaporPressure):
            self.cavitationIndex  = np.nan
            self.cavitationStatus = 'not applicable'
            return

        pressureDrop         = max(self.upstreamPressure - self.downstreamPressure, 1.0e-9)
        self.cavitationIndex = (self.upstreamPressure - self.vaporPressure) / pressureDrop

        recoveryFactor  = self._recoveryFactor()
        chokedIndex     = 1.0 / recoveryFactor**2
        incipientIndex  = 1.7 * chokedIndex   # incipient cavitation is audible well before choking

        if self.downstreamPressure <= self.vaporPressure:
            self.cavitationStatus = 'flashing'
        elif self.cavitationIndex <= chokedIndex:
            self.cavitationStatus = 'choked'
        elif self.cavitationIndex <= incipientIndex:
            self.cavitationStatus = 'incipient'
        else:
            self.cavitationStatus = 'none'
