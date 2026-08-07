
# -- CheckValve Class Definition -- #

'''

Check valve sizing, cracking pressure, chatter and reverse leakage.

A check valve is a passive one-way valve. It has no actuator, no command and no position feedback,
which makes it the cheapest way to enforce flow direction and also the component most likely to be
in an unknown state.

Three things matter and they conflict:

1. **Cracking pressure.** The forward differential at which the valve begins to open. A low cracking
   pressure costs less feed system pressure; a high one closes faster and reseats more reliably.
2. **Full-open flow.** The valve has to be far enough open at the operating flow that it is not
   throttling, and that means the flow has to be high enough to hold the poppet against the stop.
3. **Chatter.** If the flow is too low to hold the poppet fully open, it oscillates between the seat
   and its partially open position at the natural frequency of the moving element. Chatter destroys
   the seat, generates particles, and produces a pressure oscillation that propagates into the
   system.

**Chatter is the failure mode that catches people.** A check valve sized for the peak flow will
chatter at low flow, and a system that operates over a wide flow range needs either a valve sized
for the minimum flow or a different architecture. This is the single most common check valve problem
and it is entirely predictable at design time.

Check valves are also the standard way to isolate a common pressurant manifold from multiple
propellant tanks, and in that application a leaking check valve allows fuel and oxidizer vapor to mix
in the pressurant line. That has caused vehicle losses, which is why hypergolic systems use series
redundant check valves with a monitored interspace.

See Also:
---------
Valve      : Actively controlled valves
Regulator  : The other passive pressure control device
Line       : Where the check valve loss appears in the pressure budget

Theory: docs/FlowControlDevices.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable, leakRateConvert,
                       PA_PER_PSIA, InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable, leakRateConvert,
                        PA_PER_PSIA, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Check valve types.
#
#   lossCoefficient       K at full open, referenced to the port area
#   crackingPressure      typical cracking differential [Pa]
#   minimumFlowFraction   fraction of rated flow below which the poppet does not stay on its stop
#   reverseLeakClass      typical reverse leakage [scc/s He]
#   closureTime           typical time from flow reversal to seated [s]
CHECK_VALVE_TYPES = {
    'poppet spring': {
        'lossCoefficient': 3.0, 'crackingPressure': 20.0e3, 'minimumFlowFraction': 0.25,
        'reverseLeakClass': 1.0e-4, 'closureTime': 0.005,
        'description': 'Spring loaded poppet on a conical or flat seat.',
        'notes': 'The aerospace standard. Fast closing, orientation independent, and the spring can be selected '
                 'to set the cracking pressure. Soft seats give the best reverse sealing; metal seats survive '
                 'higher temperature and longer storage.'
    },
    'ball spring': {
        'lossCoefficient': 4.0, 'crackingPressure': 15.0e3, 'minimumFlowFraction': 0.30,
        'reverseLeakClass': 1.0e-3, 'closureTime': 0.008,
        'description': 'Spring loaded ball on a conical seat.',
        'notes': 'Simple and cheap. The ball can rotate to present a fresh sealing surface, which is either a '
                 'life advantage or a repeatability problem depending on the application.'
    },
    'swing': {
        'lossCoefficient': 2.0, 'crackingPressure': 2.0e3, 'minimumFlowFraction': 0.40,
        'reverseLeakClass': 1.0e-2, 'closureTime': 0.200,
        'description': 'Hinged disc that swings out of the flow path.',
        'notes': 'Very low pressure drop and very low cracking pressure. Slow to close, which makes it a water '
                 'hammer source on flow reversal, and it is orientation dependent. Ground systems.'
    },
    'lift': {
        'lossCoefficient': 12.0, 'crackingPressure': 25.0e3, 'minimumFlowFraction': 0.20,
        'reverseLeakClass': 1.0e-4, 'closureTime': 0.010,
        'description': 'Disc lifts vertically off a horizontal seat, guided.',
        'notes': 'High pressure drop (equivalent length L/D = 600) but excellent sealing and a short stroke. '
                 'Orientation dependent.'
    },
    'duckbill': {
        'lossCoefficient': 5.0, 'crackingPressure': 3.0e3, 'minimumFlowFraction': 0.10,
        'reverseLeakClass': 1.0e-2, 'closureTime': 0.020,
        'description': 'Elastomeric flattened tube that opens under forward pressure.',
        'notes': 'No moving parts and no chatter, because the element is compliant rather than rigid. Limited '
                 'by the elastomer temperature and compatibility range, and it is not a precise device.'
    },
    'dual poppet redundant': {
        'lossCoefficient': 6.0, 'crackingPressure': 40.0e3, 'minimumFlowFraction': 0.25,
        'reverseLeakClass': 1.0e-6, 'closureTime': 0.005,
        'description': 'Two poppet check valves in series in one body, with a monitored interspace.',
        'notes': 'The standard for hypergolic pressurant isolation. Series redundancy means a single seat failure '
                 'does not allow vapor mixing, and the interspace can be pressure monitored to detect the first '
                 'failure. Twice the cracking pressure and twice the loss.'
    }
}

# Chatter risk thresholds, as a fraction of the flow required to hold the poppet on its stop.
CHATTER_SEVERE   = 0.50   # below half the hold-open flow, sustained chatter
CHATTER_MARGINAL = 1.00   # below the hold-open flow, intermittent chatter

class CheckValve:

    '''

    Cracking pressure, pressure drop, chatter margin and reverse leakage for a check valve.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    valveType : str
        Key into CHECK_VALVE_TYPES
    nominalSize : float
        Port diameter [m]
    massFlow : float
        Operating (design) mass flow [kg/s]
    minimumMassFlow : float
        Lowest flow the valve will see [kg/s]. Drives the chatter check.
    ratedMassFlow : float
        Flow at which the valve is fully open [kg/s]. Defaults to the design flow.
    upstreamPressure : float
        Static pressure upstream [Pa, absolute]
    temperature : float
        Fluid temperature [K]
    crackingPressure : float
        Override for the type default [Pa]

    Key Output Properties:
    ----------------------
    pressureDrop : float
        Forward pressure drop at the design flow, including cracking pressure [Pa]
    velocity : float
        Port velocity [m/s]
    holdOpenFlow : float
        Flow required to hold the poppet against its stop [kg/s]
    chatterMargin : float
        Minimum flow divided by hold-open flow [-]
    chatterRisk : str
        'none', 'marginal' or 'SEVERE'
    reverseLeakRate : float
        Expected reverse leakage [scc/s He]

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    calculatePressureDrop()       Forward loss at the design flow
    checkChatter()                Chatter risk over the flow range
    calculateReverseLeakage()     Reverse leak rate and its consequence
    compareTypes(candidates)      Side by side selection table
    generateReport(outputDir)     Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid and Duty -- #

        self.fluid             = ''      # [case sensitive string]
        self.upstreamPressure  = np.nan  # [Pa, absolute]
        self.temperature       = 293.15  # [K]
        self.massFlow          = np.nan  # [kg/s], design flow
        self.minimumMassFlow   = np.nan  # [kg/s], lowest flow seen. Drives the chatter check.
        self.ratedMassFlow     = np.nan  # [kg/s], flow at full open. Defaults to the design flow.

        # -- Valve Definition -- #

        self.valveType         = 'poppet spring'  # key into CHECK_VALVE_TYPES
        self.nominalSize       = np.nan  # [m], port diameter
        self.crackingPressure  = np.nan  # [Pa], overrides the type default
        self.lossCoefficient   = np.nan  # [-], overrides the type default

        # -- Results -- #

        self.density           = np.nan  # [kg/m^3]
        self.velocity          = np.nan  # [m/s]
        self.dynamicPressure    = np.nan # [Pa]
        self.pressureDrop      = np.nan  # [Pa], total forward loss
        self.holdOpenFlow      = np.nan  # [kg/s]
        self.chatterMargin     = np.nan  # [-]
        self.chatterRisk       = ''      # 'none' / 'marginal' / 'SEVERE'
        self.reverseLeakRate   = np.nan  # [scc/s He]
        self.designNotes       = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, nominalSize, massFlow, upstreamPressure.

        '''

        requiredParams = {
            'fluid':            'Check valve fluid species not provided.',
            'nominalSize':      'Check valve port diameter not provided.',
            'massFlow':         'Check valve design mass flow not provided.',
            'upstreamPressure': 'Check valve upstream pressure not provided.'
        }

        optionalParams = ['temperature', 'minimumMassFlow', 'ratedMassFlow', 'valveType',
                          'crackingPressure', 'lossCoefficient']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        self.density = float(fluidProps(self.fluid, 'TP', 'D', self.temperature, self.upstreamPressure))

    def calculatePressureDrop(self) -> float:

        '''

        Forward pressure drop at the design flow.

        Two contributions:

            dP = P_cracking + K * rho * V^2 / 2

        The cracking pressure is the spring preload divided by the seat area and it is present at any
        flow. The dynamic term is the ordinary loss coefficient contribution.

        At low flow the cracking pressure dominates completely, which is why a check valve in a low
        flow line can cost far more pressure than its `K` suggests. At high flow the dynamic term
        dominates.

        '''

        valveData = CHECK_VALVE_TYPES[self.valveType.strip().lower()]

        crackingPressure = self.crackingPressure
        if np.isnan(crackingPressure):
            crackingPressure = valveData['crackingPressure']

        lossCoefficient = self.lossCoefficient
        if np.isnan(lossCoefficient):
            lossCoefficient = valveData['lossCoefficient']

        portArea            = np.pi * self.nominalSize**2 / 4.0
        self.velocity       = self.massFlow / (self.density * portArea)
        self.dynamicPressure = 0.5 * self.density * self.velocity**2

        self.pressureDrop = crackingPressure + lossCoefficient * self.dynamicPressure

        crackingFraction = crackingPressure / self.pressureDrop
        if crackingFraction > 0.7:
            self.designNotes.append(
                f'The cracking pressure is {crackingFraction * 100.0:.0f} percent of the total loss. At this flow '
                f'the valve is essentially a fixed pressure penalty rather than a flow resistance. A lower cracking '
                f'pressure spring would recover most of it, at the cost of slower and less reliable reseating.')

        return self.pressureDrop

    def checkChatter(self) -> dict:

        '''

        Chatter risk over the operating flow range.

        A check valve poppet is held open by the dynamic pressure of the flow acting against the
        spring. If the flow is too low, the poppet does not reach its stop and it sits in an
        equilibrium position where a small flow disturbance moves it. That is chatter: the poppet
        oscillates between the seat and its partially open position at the natural frequency of the
        spring-mass system, typically tens to hundreds of hertz.

        The consequences, in order of how quickly they arrive:

        1. **Noise and a pressure oscillation** that propagates into the system and can couple with
           other components
        2. **Seat and poppet wear**, because the impact energy is delivered thousands of times per
           minute
        3. **Particle generation** from that wear, which then damages everything downstream
        4. **Eventual seat failure**, at which point the valve no longer checks

        The hold-open flow is estimated as the fraction of rated flow below which the poppet leaves
        its stop, which is a property of the valve type and the spring rate.

        **The design response** to a chatter problem is one of:

        - Size the valve for the MINIMUM flow rather than the maximum, accepting more pressure drop
          at high flow
        - Use a valve type that does not chatter (a duckbill, or any compliant element)
        - Put the check valve where the flow is steady rather than where it is intermittent
        - Accept a lower cracking pressure so the poppet reaches its stop at lower flow

        '''

        valveData = CHECK_VALVE_TYPES[self.valveType.strip().lower()]

        ratedFlow = self.ratedMassFlow if not np.isnan(self.ratedMassFlow) else self.massFlow
        self.holdOpenFlow = ratedFlow * valveData['minimumFlowFraction']

        minimumFlow = self.minimumMassFlow if not np.isnan(self.minimumMassFlow) else self.massFlow
        self.chatterMargin = minimumFlow / self.holdOpenFlow

        if self.chatterMargin < CHATTER_SEVERE:
            self.chatterRisk = 'SEVERE'
            self.designNotes.append(
                f'SEVERE chatter risk: the minimum flow of {minimumFlow:.5g} kg/s is {self.chatterMargin * 100.0:.0f} '
                f'percent of the {self.holdOpenFlow:.5g} kg/s hold-open flow. The poppet will oscillate. Size the '
                f'valve for the minimum flow, or use a compliant element such as a duckbill.')
        elif self.chatterMargin < CHATTER_MARGINAL:
            self.chatterRisk = 'marginal'
            self.designNotes.append(
                f'Marginal chatter risk: the minimum flow is {self.chatterMargin * 100.0:.0f} percent of the '
                f'hold-open flow. Expect intermittent chatter at the low end of the operating range.')
        else:
            self.chatterRisk = 'none'

        return {
            'ratedFlow':     ratedFlow,
            'holdOpenFlow':  self.holdOpenFlow,
            'minimumFlow':   minimumFlow,
            'chatterMargin': self.chatterMargin,
            'chatterRisk':   self.chatterRisk
        }

    def calculateReverseLeakage(self, downstreamPressure: float = None,
                                exposureTime: float = 86400.0) -> dict:

        '''

        Reverse leakage and the mass that passes back over a given exposure time.

        A check valve leaks backwards. How much depends on the seat type and the reverse
        differential, and the number that matters is what accumulates over the exposure time rather
        than the instantaneous rate.

        **The application that makes this critical** is a common pressurant manifold feeding both a
        fuel tank and an oxidizer tank through separate check valves. If either check valve leaks,
        propellant vapor migrates back into the shared manifold. With a hypergolic pair, fuel vapor
        and oxidizer vapor meeting in the pressurant line react, deposit solids, and can ignite.
        Vehicle losses have been attributed to exactly this mechanism.

        The design response is **series redundant check valves with a monitored interspace**: two
        valves in series, with a pressure transducer between them so that a first failure is
        detectable before it becomes a second failure. That is why the `dual poppet redundant` type
        exists and why it is standard for hypergolic pressurant isolation.

        '''

        valveData = CHECK_VALVE_TYPES[self.valveType.strip().lower()]

        self.reverseLeakRate = valveData['reverseLeakClass']

        # Scale with reverse differential relative to a 1 atm reference, which is roughly how a
        # seat leak behaves in the viscous regime.
        if downstreamPressure is not None:
            reverseDifferential = max(downstreamPressure - self.upstreamPressure, 0.0)
            self.reverseLeakRate *= max(reverseDifferential / 101325.0, 0.0)

        accumulatedVolume = self.reverseLeakRate * exposureTime            # std cm^3
        accumulatedMass   = leakRateConvert(self.reverseLeakRate, 'sccs', 'kgs',
                                            species = 'He') * exposureTime  # kg

        return {
            'reverseLeakRate':   self.reverseLeakRate,
            'exposureTime':      exposureTime,
            'accumulatedVolume': accumulatedVolume,
            'accumulatedMass':   accumulatedMass,
            'leakClass':         valveData['reverseLeakClass']
        }

    def compareTypes(self, candidates: list = None) -> str:

        '''

        Side by side check valve selection table at the current duty.

        '''

        if candidates is None:
            candidates = list(CHECK_VALVE_TYPES.keys())

        savedType = self.valveType
        rows      = []

        for candidate in candidates:

            self.valveType = candidate
            valveData      = CHECK_VALVE_TYPES[candidate]

            try:
                pressureDrop = self.calculatePressureDrop()
                chatter      = self.checkChatter()
            except Exception:
                continue

            rows.append([
                candidate,
                f'{valveData["crackingPressure"] / 1.0e3:.1f}',
                f'{valveData["lossCoefficient"]:.1f}',
                f'{pressureDrop / 1.0e3:.2f}',
                f'{valveData["reverseLeakClass"]:.0e}',
                f'{valveData["closureTime"] * 1.0e3:.1f}',
                chatter['chatterRisk']
            ])

        self.valveType = savedType
        self.calculatePressureDrop()
        self.checkChatter()

        return formatReportTable(rows,
                                 ['Type', 'Crack [kPa]', 'K', 'Total dP [kPa]',
                                  'Rev leak [scc/s]', 'Close [ms]', 'Chatter'],
                                 title = f'CHECK VALVE SELECTION  ({self.fluid}, {self.massFlow:.5g} kg/s, '
                                         f'{self.nominalSize * 1.0e3:.2f} mm port)')

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        valveData = CHECK_VALVE_TYPES[self.valveType.strip().lower()]

        crackingPressure = self.crackingPressure if not np.isnan(self.crackingPressure) else valveData['crackingPressure']
        lossCoefficient  = self.lossCoefficient if not np.isnan(self.lossCoefficient) else valveData['lossCoefficient']

        rows = [
            ['Fluid',                f'{self.fluid}'],
            ['Valve type',           f'{self.valveType}'],
            ['Port diameter',        f'{self.nominalSize * 1.0e3:.3f} mm'],
            ['Upstream pressure',    f'{self.upstreamPressure / 1.0e6:.4f} MPa'],
            ['Temperature',          f'{self.temperature:.2f} K'],
            ['Density',              f'{self.density:.4f} kg/m^3'],
            ['Design mass flow',     f'{self.massFlow:.6f} kg/s'],
            ['Port velocity',        f'{self.velocity:.3f} m/s'],
            ['Dynamic pressure',     f'{self.dynamicPressure / 1.0e3:.4f} kPa'],
            ['Cracking pressure',    f'{crackingPressure / 1.0e3:.3f} kPa ({crackingPressure / PA_PER_PSIA:.2f} psi)'],
            ['Loss coefficient K',   f'{lossCoefficient:.2f}'],
            ['Total forward dP',     f'{self.pressureDrop / 1.0e3:.4f} kPa'],
            ['Closure time',         f'{valveData["closureTime"] * 1.0e3:.1f} ms']
        ]

        if not np.isnan(self.chatterMargin):
            rows.append(['Hold-open flow',  f'{self.holdOpenFlow:.6f} kg/s'])
            rows.append(['Chatter margin',  f'{self.chatterMargin:.3f}'])
            rows.append(['Chatter risk',    f'{self.chatterRisk}'])

        if not np.isnan(self.reverseLeakRate):
            rows.append(['Reverse leak rate', f'{self.reverseLeakRate:.3e} scc/s He'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'CHECK VALVE REPORT')

        report += f'\n\nVALVE NOTES\n{"-" * 60}\n{valveData["description"]}\n{valveData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'checkValveReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.valveType.strip().lower() not in CHECK_VALVE_TYPES:
            raise InvalidInputError(
                message       = f'Unknown check valve type \'{self.valveType}\'.',
                parameterName = 'valveType', value = self.valveType,
                validRange    = str(sorted(CHECK_VALVE_TYPES.keys()))
            )

        if self.nominalSize <= 0.0 or self.massFlow <= 0.0:
            raise InvalidInputError(
                message       = 'Check valve port diameter and mass flow must be positive.',
                parameterName = 'nominalSize/massFlow', value = (self.nominalSize, self.massFlow),
                validRange    = 'Both greater than 0'
            )

        if not np.isnan(self.minimumMassFlow) and self.minimumMassFlow > self.massFlow:
            raise InvalidInputError(
                message       = 'Minimum mass flow exceeds the design mass flow.',
                parameterName = 'minimumMassFlow', value = self.minimumMassFlow,
                validRange    = f'0 to {self.massFlow:.6g} kg/s'
            )
