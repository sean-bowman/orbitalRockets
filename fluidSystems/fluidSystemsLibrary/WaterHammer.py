
# -- WaterHammer Class Definition -- #

'''

Pressure surge from a transient change in flow velocity.

Water hammer is the most destructive thing an operator can do to a fluid system by accident, and it
is entirely predictable. When a valve closes, the momentum of the moving column of liquid has to go
somewhere, and it goes into pressure:

    dP = rho * a * dV

with `a` the pressure wave speed in the fluid-filled pipe, typically 1000 to 1400 m/s in a liquid
line. For water at 3 m/s that is a 4.3 MPa spike, which is far above most feed system operating
pressures and quite capable of bursting a line, breaking a transducer, or unseating a joint.

Three things determine whether it happens:

1. **How fast the velocity changes.** Closing faster than the pipe period `2L/a` produces the full
   Joukowsky surge. Slower closure reduces it approximately in proportion.
2. **How much velocity there is to lose.** The surge scales linearly with the velocity change, which
   is why line velocity limits exist and why a fill line is sized more conservatively than a run line.
3. **What the line is made of.** A stiff, thick-walled steel line has a high wave speed and a large
   surge. A compliant line, or one with entrained gas, has a much lower wave speed and a much smaller
   surge, which is why an accumulator works.

This class covers the classical surge calculation, the slow-closure reduction, column separation, and
two failure modes specific to propulsion: cryogenic priming surge, and adiabatic compression of
trapped gas in an oxygen system, which is an ignition hazard rather than a structural one.

See Also:
---------
Line   : The pipe the surge propagates in and the wall it has to survive
Valve  : The device that causes it and the closure time that controls it
Orifice: A restriction that damps the surge, at the cost of steady-state pressure

Theory: docs/WaterHammer.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                       hoopStressCalculator, GRAVITY, PA_PER_PSIA,
                       InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                        hoopStressCalculator, GRAVITY, PA_PER_PSIA,
                        InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Pipe restraint factor c1 in the wave speed equation. Accounts for how the pipe is anchored, which
# changes how much the wall can strain radially in response to the pressure pulse.
#
# The differences are modest, roughly 5 percent on wave speed, which is worth carrying but is not
# where the uncertainty in a surge calculation lives. The uncertainty lives in the closure time and
# in whether there is any entrained gas.
RESTRAINT_FACTORS = {
    'anchored upstream':     1.0,   # pipe anchored against axial movement at the upstream end only
    'anchored throughout':   0.91,  # anchored against axial movement along its whole length
    'expansion joints':      1.0    # free axial movement, expansion joints throughout
}

# Typical surge mitigation effectiveness, as a fraction of the unmitigated Joukowsky surge that
# remains after the mitigation is applied. Indicative values for first-cut trades.
MITIGATION_EFFECTIVENESS = {
    'slow closure':          0.20,   # closure time 5x the pipe period
    'accumulator':           0.15,   # gas-charged bladder accumulator adjacent to the valve
    'surge tank':            0.10,   # open standpipe, ground systems only
    'relief valve':          0.40,   # fast-acting relief; limited by its own response time
    'soft start valve':      0.25,   # profiled opening, addresses the priming surge
    'restricting orifice':   0.60    # damps the wave, costs steady-state pressure
}

class WaterHammer:

    '''

    Transient surge pressure from a velocity change in a liquid line.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    pressure : float
        Steady-state line pressure before the transient [Pa, absolute]
    temperature : float
        Fluid temperature [K]
    velocity : float
        Steady-state flow velocity before the transient [m/s]
    finalVelocity : float
        Velocity after the transient [m/s]. Zero for a full closure.
    innerDiameter : float
        Pipe inner diameter [m]
    wallThickness : float
        Pipe wall thickness [m]
    length : float
        Length from the valve back to the nearest reservoir or large volume [m]
    material : str
        Pipe material, key into materialProperties
    closureTime : float
        Effective time over which the velocity changes [s]
    restraint : str
        Key into RESTRAINT_FACTORS
    entrainedGasFraction : float
        Volume fraction of free gas in the liquid [-]. Devastating to wave speed even in traces.

    Key Output Properties:
    ----------------------
    waveSpeed : float
        Pressure wave propagation speed [m/s]
    pipePeriod : float
        2L/a, the round trip time of the pressure wave [s]
    joukowskySurge : float
        Full instantaneous-closure surge [Pa]
    actualSurge : float
        Surge accounting for the closure time [Pa]
    peakPressure : float
        Line pressure plus surge [Pa]
    hoopStress : float
        Hoop stress at the peak pressure [Pa]
    stressMargin : float
        Material allowable over the peak hoop stress [-]
    columnSeparation : bool
        True when the negative surge takes the line below vapor pressure
    criticalClosureTime : float
        The closure time below which the full Joukowsky surge is produced [s]

    Public Methods:
    ---------------
    setInputs(inputs)                Load a configuration dictionary
    calculateWaveSpeed()             Wave speed with pipe elasticity and entrained gas
    calculateSurge()                 Joukowsky and slow-closure surge, peak pressure
    checkColumnSeparation()          Negative surge against vapor pressure
    requiredClosureTime(target)      Closure time for a target peak pressure
    calculateAdiabaticCompression(...)  Trapped gas heating, an oxygen ignition check
    generateReport(outputDir)        Formatted results table

    Typical Workflow:
    -----------------
    >>> surge = WaterHammer()
    >>> surge.setInputs({'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15,
    ...                  'velocity': 3.0, 'innerDiameter': 0.05, 'wallThickness': 0.003,
    ...                  'length': 20.0, 'material': '316L', 'closureTime': 0.5})
    >>> surge.calculateSurge()
    >>> print(surge.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid State -- #

        self.fluid                = ''      # [case sensitive string]
        self.pressure             = np.nan  # [Pa, absolute], steady state before the transient
        self.temperature          = np.nan  # [K]
        self.velocity             = np.nan  # [m/s], steady state before the transient
        self.finalVelocity        = 0.0     # [m/s], after the transient. 0 for a full closure.

        # -- Pipe Geometry -- #

        self.innerDiameter        = np.nan  # [m]
        self.wallThickness        = np.nan  # [m]
        self.length               = np.nan  # [m], valve back to the nearest reservoir
        self.material             = '316L'  # key into materialProperties
        self.restraint            = 'anchored upstream'  # key into RESTRAINT_FACTORS

        # -- Transient -- #

        # The effective closure time is NOT the valve stroke time. A valve with an equal percentage
        # or quick opening characteristic does most of its flow reduction in the last part of its
        # travel, so the time over which the velocity actually changes can be a small fraction of
        # the stroke time. This is why a nominally slow valve still produces a full surge.
        self.closureTime          = np.nan  # [s], effective velocity change time

        # Entrained free gas destroys the wave speed. Even 0.1 percent by volume cuts it roughly in
        # half, because the gas compressibility dominates the mixture bulk modulus. This is why an
        # accumulator works, and why a line that has not been fully bled behaves completely
        # differently from the calculation.
        self.entrainedGasFraction = 0.0     # [-], volume fraction of free gas

        # -- Results -- #

        self.density              = np.nan  # [kg/m^3]
        self.bulkModulus          = np.nan  # [Pa]
        self.vaporPressure        = np.nan  # [Pa]
        self.waveSpeed            = np.nan  # [m/s]
        self.pipePeriod           = np.nan  # [s], 2L/a
        self.criticalClosureTime  = np.nan  # [s]
        self.joukowskySurge       = np.nan  # [Pa]
        self.actualSurge          = np.nan  # [Pa]
        self.peakPressure         = np.nan  # [Pa]
        self.minimumPressure      = np.nan  # [Pa], the negative half of the surge
        self.columnSeparation     = False   # [-]
        self.hoopStress           = np.nan  # [Pa]
        self.stressMargin         = np.nan  # [-]
        self.isRapidClosure       = False   # [-]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, pressure, temperature, velocity, innerDiameter, wallThickness, length.

        '''

        requiredParams = {
            'fluid':         'Water hammer fluid species not provided.',
            'pressure':      'Steady state line pressure not provided.',
            'temperature':   'Fluid temperature not provided.',
            'velocity':      'Steady state velocity not provided.',
            'innerDiameter': 'Pipe inner diameter not provided.',
            'wallThickness': 'Pipe wall thickness not provided.',
            'length':        'Line length from the valve to the reservoir not provided.'
        }

        optionalParams = ['finalVelocity', 'material', 'restraint', 'closureTime',
                          'entrainedGasFraction']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._evaluateFluidState()

    def calculateWaveSpeed(self) -> float:

        '''

        Pressure wave speed in a fluid-filled elastic pipe.

            a = sqrt( (K/rho) / ( 1 + (K*D)/(E*t) * c1 ) )

        The numerator is the acoustic speed in the unconfined fluid. The denominator is the
        correction for pipe wall compliance: a pipe that can strain radially stores some of the
        pressure pulse as wall deflection, which slows the wave.

        For water in a thick steel pipe the wave speed is close to the free-fluid value of about
        1480 m/s. For water in a thin-walled plastic pipe it can fall below 400 m/s, and the surge
        falls with it.

        **Entrained gas is the dominant effect when it is present.** A free gas fraction reduces the
        mixture bulk modulus dramatically because the gas is thousands of times more compressible
        than the liquid:

            1/K_mixture = (1 - alpha)/K_liquid + alpha/K_gas

        Even 0.1 percent free gas by volume roughly halves the wave speed, and 1 percent cuts it by
        a factor of four. That is the mechanism an accumulator uses deliberately. It is also why a
        line that has not been fully bled behaves nothing like the calculation: the surge is much
        smaller than predicted, which sounds like good news until the line is properly bled before a
        flight and the surge appears.

        '''

        properties = materialProperties(self.material, self.temperature)

        # Effective bulk modulus of the liquid-gas mixture. The gas is treated as isothermal ideal,
        # so its bulk modulus is simply its absolute pressure.
        effectiveBulkModulus = self.bulkModulus
        if self.entrainedGasFraction > 0.0:
            gasBulkModulus       = self.pressure
            inverseModulus       = ((1.0 - self.entrainedGasFraction) / self.bulkModulus +
                                    self.entrainedGasFraction / gasBulkModulus)
            effectiveBulkModulus = 1.0 / inverseModulus

        # Mixture density, gas contribution neglected (its mass is negligible at these fractions)
        effectiveDensity = self.density * (1.0 - self.entrainedGasFraction)

        restraintFactor = RESTRAINT_FACTORS.get(self.restraint.strip().lower())
        if restraintFactor is None:
            raise InvalidInputError(
                message       = f'Unknown pipe restraint condition \'{self.restraint}\'.',
                parameterName = 'restraint', value = self.restraint,
                validRange    = str(sorted(RESTRAINT_FACTORS.keys()))
            )

        complianceTerm = (effectiveBulkModulus * self.innerDiameter /
                          (properties['elasticModulus'] * self.wallThickness)) * restraintFactor

        self.waveSpeed  = np.sqrt((effectiveBulkModulus / effectiveDensity) / (1.0 + complianceTerm))
        self.pipePeriod = 2.0 * self.length / self.waveSpeed

        return self.waveSpeed

    def calculateSurge(self) -> float:

        '''

        Joukowsky surge and the slow-closure reduction.

        **Joukowsky (instantaneous closure):**

            dP = rho * a * dV

        This is the maximum possible surge and it is produced whenever the closure time is shorter
        than the pipe period `2L/a`. Note that it does not depend on the line length: a short line
        and a long line produce the same peak surge, they just produce it for different durations.
        What length changes is how long you have to close in to avoid it.

        **Slow closure (Allievi / Michaud):** if the closure takes longer than the pipe period, the
        reflected wave returns to the valve before closure is complete and partially cancels the
        surge:

            dP = rho * L * dV / t_closure          for t_closure > 2L/a

        which can also be written as the Joukowsky surge scaled by `(2L/a) / (2 * t_closure)`. The
        reduction is roughly proportional, so doubling the closure time halves the surge, but only
        once you are past the pipe period. Below it there is no benefit at all.

        **The negative surge matters too.** A valve closing at the downstream end of a line produces
        a positive surge upstream of it and a negative surge downstream. A pump tripping produces a
        negative surge first. If the negative excursion takes the line below vapor pressure, the
        column separates and the subsequent rejoining impact is typically far worse than the original
        event. See checkColumnSeparation.

        '''

        if np.isnan(self.waveSpeed):
            self.calculateWaveSpeed()

        velocityChange = abs(self.velocity - self.finalVelocity)

        # Full Joukowsky surge
        self.joukowskySurge      = self.density * self.waveSpeed * velocityChange
        self.criticalClosureTime = self.pipePeriod

        # Slow closure reduction
        if np.isnan(self.closureTime) or self.closureTime <= self.pipePeriod:
            self.actualSurge    = self.joukowskySurge
            self.isRapidClosure = True
        else:
            # Michaud: dP = rho * L * dV / t_closure. Equivalent to Joukowsky * (2L/a)/(2*t_close).
            self.actualSurge    = self.density * self.length * velocityChange / self.closureTime
            self.isRapidClosure = False

        self.peakPressure    = self.pressure + self.actualSurge
        self.minimumPressure = self.pressure - self.actualSurge

        # Structural check at the peak
        properties          = materialProperties(self.material, self.temperature)
        self.hoopStress     = hoopStressCalculator(self.peakPressure, self.innerDiameter,
                                                   thickness = self.wallThickness)
        self.stressMargin   = properties['allowableStress'] / self.hoopStress

        self.checkColumnSeparation()

        return self.actualSurge

    def checkColumnSeparation(self) -> bool:

        '''

        Check whether the negative half of the surge takes the line below vapor pressure.

        If it does, the liquid column separates: a vapor cavity forms, the two columns move apart,
        and then the pressure recovers and drives them back together. The rejoining impact is a
        liquid-on-liquid collision at the full separation velocity with no compliance in between, and
        the resulting pressure spike is routinely **two to five times** the original Joukowsky surge.

        This is the mechanism behind most catastrophic water hammer failures. The original transient
        is survivable; the cavity collapse is not.

        Column separation is most likely at high points in a routing, downstream of a closing valve,
        and in any system where the static pressure is already low. It is a hard reason to avoid
        local high points in liquid lines and to keep vent and drain valves at those points.

        '''

        if np.isnan(self.minimumPressure):
            return False

        self.columnSeparation = self.minimumPressure <= self.vaporPressure

        return self.columnSeparation

    def requiredClosureTime(self, targetPeakPressure: float) -> float:

        '''

        The closure time required to keep the peak pressure below a target.

        Inverts the Michaud relation:

            t_closure = rho * L * dV / (P_target - P_line)

        Returns NaN if the target is unreachable, which happens when the target is below the line
        pressure, and prints a warning if the required time is shorter than the pipe period, in which
        case slow closure cannot help and a different mitigation is needed.

        This is the number to hand to the valve and actuator design: the closure time is a
        requirement derived from the surge limit, not a free parameter.

        '''

        if np.isnan(self.waveSpeed):
            self.calculateWaveSpeed()

        allowableSurge = targetPeakPressure - self.pressure

        if allowableSurge <= 0.0:
            raise InvalidInputError(
                message       = (f'Target peak pressure {targetPeakPressure / 1.0e6:.3f} MPa is at or below the '
                                 f'steady line pressure {self.pressure / 1.0e6:.3f} MPa. No closure time achieves it.'),
                parameterName = 'targetPeakPressure', value = targetPeakPressure,
                validRange    = f'Greater than {self.pressure:.6g} Pa'
            )

        velocityChange = abs(self.velocity - self.finalVelocity)
        requiredTime   = self.density * self.length * velocityChange / allowableSurge

        if requiredTime <= self.pipePeriod:
            print(f'Warning: the required closure time of {requiredTime * 1.0e3:.2f} ms is at or below the pipe '
                  f'period of {self.pipePeriod * 1.0e3:.2f} ms. Slow closure cannot reduce the surge below the '
                  f'Joukowsky value of {self.joukowskySurge / 1.0e6:.3f} MPa. Use an accumulator, a surge relief '
                  f'device, or reduce the line velocity.')
            return np.nan

        return requiredTime

    def calculateAdiabaticCompression(self, initialPressure: float, finalPressure: float,
                                      gamma: float = 1.4, initialTemperature: float = 293.15) -> dict:

        '''

        Temperature rise from adiabatically compressing a trapped gas volume.

        This is not a structural failure mode, it is an **ignition** failure mode, and it is the
        reason oxygen system valves are opened slowly.

        When a valve opens rapidly into a dead-ended downstream volume, the gas already in that
        volume is compressed by the incoming high-pressure gas far faster than it can lose heat to
        the walls. The compression is adiabatic:

            T2 = T1 * (P2/P1)^((gamma-1)/gamma)

        Compressing GOX from 1 atm to 20 MPa takes 293 K to about 1330 K, which is above the
        autoignition temperature of every non-metal in common use and above the ignition temperature
        of many metals in oxygen. The classic accident is a fast-acting valve opened into a
        dead-ended line containing a polymer seat or a trace of hydrocarbon contamination.

        The same mechanism heats trapped gas in a hydrazine or hypergolic system, where the concern
        is thermal decomposition of the propellant rather than combustion of a polymer.

        **Mitigations:**

        - Open oxygen valves slowly (a defined opening rate, or a small bypass valve opened first to
          equalize pressure)
        - Eliminate dead-ended volumes downstream of fast valves
        - Use only oxygen-compatible materials in any volume that can be adiabatically compressed
        - Keep the system scrupulously clean; hydrocarbon contamination lowers the ignition threshold
          dramatically

        Returns the final temperature and a comparison against common autoignition thresholds.

        '''

        pressureRatio    = finalPressure / initialPressure
        finalTemperature = initialTemperature * pressureRatio**((gamma - 1.0) / gamma)

        # Autoignition temperatures in oxygen [K]. These are indicative; the actual threshold falls
        # with pressure and with contamination, sometimes dramatically.
        ignitionThresholds = {
            'hydrocarbon oil or grease': 500.0,
            'PTFE':                      780.0,
            'PCTFE (Kel-F)':             660.0,
            'Viton (FKM)':               590.0,
            'aluminum':                  1000.0,
            'carbon steel':              1600.0,
            '316 stainless':             1700.0,
            'Monel':                     2200.0
        }

        atRisk = [material for material, threshold in ignitionThresholds.items()
                  if finalTemperature >= threshold]

        return {
            'pressureRatio':        pressureRatio,
            'initialTemperature':   initialTemperature,
            'finalTemperature':     finalTemperature,
            'temperatureRise':      finalTemperature - initialTemperature,
            'materialsAtRisk':      atRisk,
            'ignitionThresholds':   ignitionThresholds
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        rows = [
            ['Fluid',                    f'{self.fluid}'],
            ['Line pressure',            f'{self.pressure / 1.0e6:.4f} MPa'],
            ['Temperature',              f'{self.temperature:.2f} K'],
            ['Density',                  f'{self.density:.3f} kg/m^3'],
            ['Bulk modulus',             f'{self.bulkModulus / 1.0e9:.4f} GPa'],
            ['Initial velocity',         f'{self.velocity:.3f} m/s'],
            ['Final velocity',           f'{self.finalVelocity:.3f} m/s'],
            ['Inner diameter',           f'{self.innerDiameter * 1.0e3:.3f} mm'],
            ['Wall thickness',           f'{self.wallThickness * 1.0e3:.4f} mm'],
            ['Line length',              f'{self.length:.3f} m'],
            ['Material',                 f'{self.material}'],
            ['Entrained gas fraction',   f'{self.entrainedGasFraction * 100.0:.4f} %'],
            ['Wave speed',               f'{self.waveSpeed:.1f} m/s'],
            ['Pipe period 2L/a',         f'{self.pipePeriod * 1.0e3:.3f} ms'],
            ['Closure time',             f'{self.closureTime * 1.0e3:.3f} ms' if not np.isnan(self.closureTime) else 'instantaneous'],
            ['Rapid closure',            f'{self.isRapidClosure}'],
            ['Joukowsky surge',          f'{self.joukowskySurge / 1.0e6:.4f} MPa ({self.joukowskySurge / PA_PER_PSIA:.1f} psi)'],
            ['Actual surge',             f'{self.actualSurge / 1.0e6:.4f} MPa ({self.actualSurge / PA_PER_PSIA:.1f} psi)'],
            ['Peak pressure',            f'{self.peakPressure / 1.0e6:.4f} MPa'],
            ['Minimum pressure',         f'{self.minimumPressure / 1.0e6:.4f} MPa'],
            ['Vapor pressure',           f'{self.vaporPressure / 1.0e3:.4f} kPa'],
            ['Column separation',        f'{self.columnSeparation}'],
            ['Hoop stress at peak',      f'{self.hoopStress / 1.0e6:.2f} MPa'],
            ['Stress margin',            f'{self.stressMargin:.3f}']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'WATER HAMMER SURGE REPORT')

        if self.columnSeparation:
            report += ('\n\nWARNING: the negative surge takes the line below vapor pressure and the liquid column '
                       'will separate. The rejoining impact is routinely two to five times the original surge, and '
                       'this is the mechanism behind most catastrophic water hammer failures. Raise the line '
                       'pressure, slow the transient, or add an accumulator at the high point.')

        if self.stressMargin < 1.0:
            report += (f'\n\nWARNING: peak hoop stress of {self.hoopStress / 1.0e6:.1f} MPa exceeds the material '
                       f'allowable. The line will yield or burst on this transient.')
        elif self.stressMargin < 1.5:
            report += (f'\n\nCAUTION: stress margin at the surge peak is only {self.stressMargin:.2f}. Surge is a '
                       f'repeated event, so this is a fatigue exposure as well as a static one.')

        if self.isRapidClosure and not np.isnan(self.closureTime):
            report += (f'\n\nNOTE: closure time {self.closureTime * 1.0e3:.2f} ms is at or below the pipe period of '
                       f'{self.pipePeriod * 1.0e3:.2f} ms, so the full Joukowsky surge is produced. Slowing the valve '
                       f'has no effect until the closure time exceeds the pipe period.')

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'waterHammerReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.pressure <= 0.0:
            raise InvalidInputError(
                message       = 'Line pressure must be absolute and positive.',
                parameterName = 'pressure', value = self.pressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if self.velocity < 0.0:
            raise InvalidInputError(
                message       = 'Velocity must be non-negative. For a reversing flow, analyze each direction.',
                parameterName = 'velocity', value = self.velocity, validRange = '0 m/s or greater'
            )

        if self.wallThickness <= 0.0 or self.innerDiameter <= 0.0 or self.length <= 0.0:
            raise InvalidInputError(
                message       = 'Pipe geometry must be positive.',
                parameterName = 'innerDiameter/wallThickness/length',
                value         = (self.innerDiameter, self.wallThickness, self.length),
                validRange    = 'All greater than 0 m'
            )

        if not 0.0 <= self.entrainedGasFraction < 1.0:
            raise InvalidInputError(
                message       = 'Entrained gas fraction must be a volume fraction between 0 and 1.',
                parameterName = 'entrainedGasFraction', value = self.entrainedGasFraction,
                validRange    = '0 to 1'
            )

    def _evaluateFluidState(self) -> None:

        '''

        Density, isentropic bulk modulus and vapor pressure.

        The bulk modulus is derived from the speed of sound rather than looked up, because
        `K = rho * c^2` and the speed of sound is a standard property lookup in every backend.
        Hydrazine has no equation of state, so its bulk modulus comes from the published value.

        '''

        self.density = float(fluidProps(self.fluid, 'TP', 'D', self.temperature, self.pressure))

        if self.fluid.strip().upper() in ('N2H4', 'HYDRAZINE'):
            # Published isentropic bulk modulus for anhydrous hydrazine near room temperature.
            # Sound speed is about 2100 m/s, giving K = rho * c^2 = 1008 * 2100^2 = 4.45 GPa.
            self.bulkModulus   = 4.45e9
            self.vaporPressure = float(fluidProps(self.fluid, 'TP', 'P', self.temperature, self.pressure))
            return

        speedOfSound     = float(fluidProps(self.fluid, 'TP', 'W', self.temperature, self.pressure))
        self.bulkModulus = self.density * speedOfSound**2

        criticalTemperature = float(fluidProps(self.fluid, 'TP', 'TCRIT', self.temperature, self.pressure))
        if self.temperature >= criticalTemperature:
            raise InvalidInputError(
                message       = ('Water hammer analysis applies to liquid lines. The fluid is above its critical '
                                 'temperature; a gas line transient is an acoustic problem, not a surge problem.'),
                parameterName = 'temperature', value = self.temperature,
                validRange    = f'Below {criticalTemperature:.4g} K'
            )

        self.vaporPressure = float(fluidProps(self.fluid, 'TQ', 'P', self.temperature, 0.0))
