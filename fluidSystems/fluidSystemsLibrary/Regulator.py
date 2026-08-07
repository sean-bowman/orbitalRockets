
# -- Regulator Class Definition -- #

'''

Pressure regulator, relief valve and burst disc sizing and behaviour.

These three devices are grouped because they are the pressure control set: the regulator sets a
pressure, the relief valve limits it, and the burst disc is the last defence when the relief valve
does not work. A system that has a regulator and no relief downstream of it is a system that has not
thought about what happens when the regulator fails open, which is the dominant regulator failure
mode.

**Regulator behaviour.** A regulator does not hold a constant outlet pressure. It holds a pressure
that varies with two things:

    droop                 outlet pressure falls as flow increases
    supply pressure effect (SPE)   outlet pressure changes as inlet pressure falls

Both are consequences of the force balance on the sensing element, and both are unavoidable. A
regulator quoted as "500 psi" delivers 500 psi at one flow rate and one inlet pressure, and something
else everywhere else. The outlet pressure band across the operating envelope is what the downstream
system actually has to tolerate, and it is often 15 to 25 percent wide.

**Relief valve behaviour.** A relief valve opens at its set pressure, reaches full flow at some
accumulation above it, and recloses at a reseat pressure below it. The gap between set and reseat is
the blowdown, and it exists to stop the valve chattering.

**Burst disc behaviour.** A burst disc has a manufacturing tolerance on its burst pressure, typically
plus or minus 5 to 10 percent, and its rating falls with temperature. It is a one-shot device: once
it opens, the system is vented and stays vented.

See Also:
---------
Valve          : The general valve sizing this class specializes
Pressurization : The system the regulator is controlling
CheckValve     : The other passive device in the same set

Theory: docs/FlowControlDevices.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                       criticalPressureRatio, chokedMassFlux, R_UNIVERSAL, speciesMolarMass,
                       PA_PER_PSIA, KV_PER_CV, InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                        criticalPressureRatio, chokedMassFlux, R_UNIVERSAL, speciesMolarMass,
                        PA_PER_PSIA, KV_PER_CV, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# SI flow coefficient constant, same definition as in Valve.py.
CV_FLOW_CONSTANT = 2.40172e-5

# Regulator types.
#
#   droopCoefficient   fractional outlet pressure fall at full rated flow [-]
#   supplyPressureEffect  fractional outlet pressure change per unit fractional inlet pressure change
#   lockupRise         fractional outlet pressure rise above setpoint at zero flow [-]
#   minimumDifferential  minimum inlet-to-outlet differential for the regulator to function [-]
#
# The sign of the supply pressure effect is the thing to know. In a conventional direct-acting
# regulator the inlet pressure acts on the poppet in the OPENING direction, so as the supply falls
# the poppet closes slightly and the outlet pressure RISES. That is counterintuitive and it means a
# blowdown system's regulated pressure creeps up as the bottle empties.
REGULATOR_TYPES = {
    'direct acting spring': {
        'droopCoefficient': 0.15, 'supplyPressureEffect': -0.03, 'lockupRise': 0.05,
        'minimumDifferential': 0.20,
        'description': 'Spring loaded, single stage, poppet sensed by a diaphragm or piston.',
        'notes': 'Simplest and most common. Large droop because the spring force falls as the sensing element '
                 'moves to open. Outlet pressure rises as the supply falls, because inlet pressure acts on the '
                 'poppet in the opening direction.'
    },
    'two stage spring': {
        'droopCoefficient': 0.05, 'supplyPressureEffect': -0.005, 'lockupRise': 0.03,
        'minimumDifferential': 0.25,
        'description': 'Two regulators in series in one body; the first stage holds a constant inlet to the second.',
        'notes': 'Much better regulation because the second stage sees a nearly constant inlet. Heavier, more '
                 'expensive, and two sets of internals to fail.'
    },
    'dome loaded': {
        'droopCoefficient': 0.03, 'supplyPressureEffect': -0.01, 'lockupRise': 0.02,
        'minimumDifferential': 0.15,
        'description': 'A gas-filled dome replaces the spring; the dome pressure sets the outlet pressure.',
        'notes': 'The best regulation available, because a gas dome has a much flatter force-displacement curve '
                 'than a spring. Also remotely adjustable by changing the dome pressure, which is why it is the '
                 'standard for test stands. Needs a dome loading supply, which is another system.'
    },
    'back pressure': {
        'droopCoefficient': 0.10, 'supplyPressureEffect': -0.02, 'lockupRise': 0.04,
        'minimumDifferential': 0.10,
        'description': 'Regulates its INLET pressure by relieving downstream, rather than regulating its outlet.',
        'notes': 'Used to hold a constant upstream pressure, for example on a tank being drained. Functionally a '
                 'proportional relief valve.'
    }
}

# Relief device types.
#
#   accumulation       fractional overpressure above set at rated capacity [-]
#   blowdown           fractional pressure fall below set before reseat [-]
#   dischargeCoefficient  Kd for the relief orifice [-]
RELIEF_TYPES = {
    'spring relief': {
        'accumulation': 0.10, 'blowdown': 0.07, 'dischargeCoefficient': 0.87,
        'description': 'Conventional spring-loaded relief valve.',
        'notes': 'Back pressure acts on the spring side and shifts the set point, so a conventional relief valve '
                 'cannot be used with a variable back pressure. Reseats after the event.'
    },
    'balanced bellows relief': {
        'accumulation': 0.10, 'blowdown': 0.07, 'dischargeCoefficient': 0.87,
        'description': 'A bellows isolates the spring side from back pressure.',
        'notes': 'Set point independent of back pressure, which is what you need when the relief discharges into '
                 'a manifold. The bellows is a fatigue-limited pressure boundary.'
    },
    'pilot operated relief': {
        'accumulation': 0.03, 'blowdown': 0.02, 'dischargeCoefficient': 0.87,
        'description': 'A small pilot senses the pressure and controls a large main valve.',
        'notes': 'Tight set point, full lift at low accumulation, and it can operate at up to 98 percent of set '
                 'pressure without leaking. More complex, and a pilot failure can disable the relief entirely.'
    },
    'burst disc': {
        'accumulation': 0.00, 'blowdown': np.nan, 'dischargeCoefficient': 0.62,
        'description': 'A one-shot rupture element.',
        'notes': 'Opens fully and instantly, never leaks before it bursts, and does not reseat. Burst pressure has '
                 'a manufacturing tolerance of typically 5 to 10 percent and falls with temperature. Once it '
                 'opens the system is vented and stays vented.'
    }
}

# Burst disc temperature derating. Burst pressure falls with temperature because the disc material
# softens. Fractional rating relative to the 295 K rating.
BURST_DISC_TEMPERATURE_DERATE = {
    'nickel':          [(295.0, 1.00), (373.0, 0.93), (473.0, 0.80), (573.0, 0.62)],
    'inconel':         [(295.0, 1.00), (373.0, 0.97), (473.0, 0.92), (673.0, 0.82), (873.0, 0.66)],
    '316 stainless':   [(295.0, 1.00), (373.0, 0.95), (473.0, 0.88), (673.0, 0.76)],
    'aluminum':        [(295.0, 1.00), (373.0, 0.85), (423.0, 0.70)],
    'monel':           [(295.0, 1.00), (373.0, 0.96), (473.0, 0.90), (673.0, 0.78)]
}

class Regulator:

    '''

    Pressure regulator, relief valve and burst disc sizing and behaviour.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    regulatorType : str
        Key into REGULATOR_TYPES
    inletPressure : float
        Regulator inlet pressure [Pa, absolute]. For a blowdown, the initial bottle pressure.
    finalInletPressure : float
        Inlet pressure at the end of the blowdown [Pa, absolute]
    setPressure : float
        Nominal regulated outlet pressure [Pa, absolute]
    massFlow : float
        Rated (maximum) mass flow [kg/s]
    temperature : float
        Gas temperature [K]
    reliefSetPressure : float
        Relief valve set pressure [Pa, absolute]
    reliefType : str
        Key into RELIEF_TYPES
    burstDiscRating : float
        Nominal burst pressure at 295 K [Pa]
    burstDiscMaterial : str
        Key into BURST_DISC_TEMPERATURE_DERATE
    burstDiscTolerance : float
        Manufacturing tolerance on burst pressure [-], e.g. 0.05 for +/- 5 percent

    Key Output Properties:
    ----------------------
    requiredFlowCoefficient : float
        Regulator Cv required for the rated flow [-]
    outletPressureBand : tuple
        (minimum, maximum) outlet pressure over the operating envelope [Pa]
    lockupPressure : float
        Outlet pressure at zero flow [Pa]
    minimumInletPressure : float
        Inlet pressure below which the regulator can no longer hold setpoint [Pa]
    reliefArea / reliefDiameter : float
        Required relief flow area and equivalent diameter
    burstDiscBand : tuple
        (minimum, maximum) actual burst pressure including tolerance and temperature [Pa]

    Public Methods:
    ---------------
    setInputs(inputs)                  Load a configuration dictionary
    sizeRegulator()                    Cv, outlet pressure band, lockup, minimum inlet pressure
    calculateOutletPressure(flow, inlet)  Outlet pressure at an arbitrary operating point
    sizeRelief(reliefFlow)             Relief device area for a required relieving capacity
    checkBurstDisc()                   Burst pressure band with tolerance and temperature derate
    checkPressureStackup()             Verify the whole set point ladder is consistent
    generateReport(outputDir)          Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid -- #

        self.fluid                = 'Helium'  # [case sensitive string]
        self.temperature          = 293.15    # [K]

        # -- Regulator -- #

        self.regulatorType        = 'direct acting spring'  # key into REGULATOR_TYPES
        self.inletPressure        = np.nan  # [Pa, absolute], initial
        self.finalInletPressure   = np.nan  # [Pa, absolute], end of blowdown
        self.setPressure          = np.nan  # [Pa, absolute], nominal outlet
        self.massFlow             = np.nan  # [kg/s], rated maximum

        # -- Relief Device -- #

        self.reliefType           = 'spring relief'  # key into RELIEF_TYPES
        self.reliefSetPressure    = np.nan  # [Pa, absolute]

        # -- Burst Disc -- #

        self.burstDiscRating      = np.nan  # [Pa], nominal at 295 K
        self.burstDiscMaterial    = 'inconel'  # key into BURST_DISC_TEMPERATURE_DERATE
        self.burstDiscTolerance   = 0.05    # [-], fractional
        self.burstDiscTemperature = 295.0   # [K]

        # -- System Limits, for the stackup check -- #

        self.maximumOperatingPressure = np.nan  # [Pa], MEOP of the downstream system
        self.proofPressure            = np.nan  # [Pa]

        # -- Results -- #

        self.requiredFlowCoefficient = np.nan  # [-], Cv
        self.lockupPressure          = np.nan  # [Pa]
        self.droopPressure           = np.nan  # [Pa], outlet at rated flow
        self.outletPressureBand      = (np.nan, np.nan)  # [Pa]
        self.minimumInletPressure    = np.nan  # [Pa]
        self.reliefArea              = np.nan  # [m^2]
        self.reliefDiameter          = np.nan  # [m]
        self.reliefFullFlowPressure  = np.nan  # [Pa]
        self.reliefReseatPressure    = np.nan  # [Pa]
        self.burstDiscBand           = (np.nan, np.nan)  # [Pa]
        self.designNotes             = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: setPressure. Everything else is optional depending on which calculation is wanted.

        '''

        requiredParams = {
            'setPressure': 'Regulator set pressure not provided.'
        }

        optionalParams = ['fluid', 'temperature', 'regulatorType', 'inletPressure',
                          'finalInletPressure', 'massFlow', 'reliefType', 'reliefSetPressure',
                          'burstDiscRating', 'burstDiscMaterial', 'burstDiscTolerance',
                          'burstDiscTemperature', 'maximumOperatingPressure', 'proofPressure']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def sizeRegulator(self) -> dict:

        '''

        Regulator flow coefficient, outlet pressure band, lockup pressure and minimum inlet pressure.

        **The outlet pressure is not constant.** Three effects move it:

        1. **Droop.** As flow increases, the sensing element must move further to open the poppet
           further, which changes the spring force and reduces the outlet pressure. Droop is quoted as
           a fraction of set pressure at rated flow, and it is the largest effect for a
           direct-acting spring regulator (15 percent is typical).

        2. **Supply pressure effect (SPE).** The inlet pressure acts on the poppet, usually in the
           opening direction. As the supply falls over a blowdown, the poppet closes slightly and the
           outlet pressure **rises**. That sign is counterintuitive and it means the regulated
           pressure of a blowdown system creeps UP as the bottle empties, which is the opposite of
           what most people expect.

        3. **Lockup.** At zero flow the poppet must close fully, and it takes a small overpressure to
           seat it. The outlet pressure at zero flow is therefore above the set pressure. That
           overshoot is what the downstream relief valve has to be set above.

        The delivered band is the combination of all three across the operating envelope, and it is
        the number the downstream system has to tolerate. For a direct-acting spring regulator it is
        typically 15 to 25 percent wide.

        **Minimum inlet pressure.** A regulator needs a working differential across it. Below roughly
        1.15 to 1.25 times the set pressure (depending on type) the poppet is fully open and the
        regulator has become a restriction rather than a regulator. That is the lockup point for the
        upstream bottle, and it determines how much pressurant is stranded.

        '''

        regulatorData = REGULATOR_TYPES[self.regulatorType.strip().lower()]

        # -- Outlet pressure extremes -- #
        self.lockupPressure = self.setPressure * (1.0 + regulatorData['lockupRise'])
        self.droopPressure  = self.setPressure * (1.0 - regulatorData['droopCoefficient'])

        # Supply pressure effect over the blowdown. Evaluated as the fractional inlet pressure change
        # times the SPE coefficient.
        supplyEffect = 0.0
        if not np.isnan(self.inletPressure) and not np.isnan(self.finalInletPressure):
            inletFraction = (self.finalInletPressure - self.inletPressure) / self.inletPressure
            supplyEffect  = regulatorData['supplyPressureEffect'] * inletFraction * self.setPressure

        # The band spans droop at full flow with the initial supply, up to lockup at zero flow with
        # the final (lowest) supply, which is where the SPE contribution is largest.
        minimumOutlet = self.droopPressure
        maximumOutlet = self.lockupPressure + max(supplyEffect, 0.0)

        self.outletPressureBand = (minimumOutlet, maximumOutlet)

        # -- Minimum inlet pressure -- #
        self.minimumInletPressure = self.setPressure * (1.0 + regulatorData['minimumDifferential'])

        # -- Flow coefficient -- #
        # Sized at the worst case: the lowest inlet pressure at which full flow is still required.
        if not np.isnan(self.massFlow):

            sizingInlet = self.finalInletPressure if not np.isnan(self.finalInletPressure) else self.inletPressure
            if np.isnan(sizingInlet):
                raise InvalidInputError(
                    message       = 'sizeRegulator needs an inlet pressure to size the flow coefficient.',
                    parameterName = 'inletPressure', value = sizingInlet, validRange = 'Positive real'
                )

            sizingInlet = max(sizingInlet, self.minimumInletPressure)

            density       = float(fluidProps(self.fluid, 'TP', 'D', self.temperature, sizingInlet))
            gamma         = float(fluidProps(self.fluid, 'TP', 'Cp/Cv', self.temperature, sizingInlet))

            pressureDrop  = sizingInlet - self.droopPressure
            pressureRatio = pressureDrop / sizingInlet

            # Terminal pressure drop ratio for a regulator poppet, close to a globe valve
            terminalRatio = 0.72 * (gamma / 1.4)
            effectiveRatio = min(pressureRatio, terminalRatio)
            expansionFactor = max(1.0 - effectiveRatio / (3.0 * terminalRatio), 2.0 / 3.0)

            self.requiredFlowCoefficient = self.massFlow / (CV_FLOW_CONSTANT * expansionFactor *
                                                            np.sqrt(density * effectiveRatio * sizingInlet))

            if pressureRatio >= terminalRatio:
                self.designNotes.append(
                    f'The regulator is choked at the sizing point (x = {pressureRatio:.3f} against a terminal ratio '
                    f'of {terminalRatio:.3f}). That is normal for a high pressure regulator and it means the flow '
                    f'capacity is set by the inlet pressure alone.')

        # -- Advisories -- #
        bandWidth = (maximumOutlet - minimumOutlet) / self.setPressure
        if bandWidth > 0.20:
            self.designNotes.append(
                f'Outlet pressure band is {bandWidth * 100.0:.1f} percent of set pressure '
                f'({minimumOutlet / 1.0e6:.4f} to {maximumOutlet / 1.0e6:.4f} MPa). The downstream system and every '
                f'component in it has to tolerate the whole band, and the relief valve has to be set above the top '
                f'of it. A two-stage or dome-loaded regulator would narrow this substantially.')

        if not np.isnan(self.finalInletPressure) and self.finalInletPressure < self.minimumInletPressure:
            self.designNotes.append(
                f'The final inlet pressure of {self.finalInletPressure / 1.0e6:.3f} MPa is below the '
                f'{self.minimumInletPressure / 1.0e6:.3f} MPa minimum working differential. The regulator will lose '
                f'control before the bottle is empty and the remaining gas is stranded.')

        return {
            'requiredFlowCoefficient': self.requiredFlowCoefficient,
            'requiredKv':              self.requiredFlowCoefficient * KV_PER_CV if not np.isnan(self.requiredFlowCoefficient) else np.nan,
            'lockupPressure':          self.lockupPressure,
            'droopPressure':           self.droopPressure,
            'outletPressureBand':      self.outletPressureBand,
            'bandWidthFraction':       bandWidth,
            'minimumInletPressure':    self.minimumInletPressure
        }

    def calculateOutletPressure(self, flowFraction: float, inletPressure: float = None) -> float:

        '''

        Outlet pressure at an arbitrary operating point.

        `flowFraction` is the flow as a fraction of rated flow, 0 at lockup and 1 at rated. The
        droop is applied linearly with flow fraction, which is the usual first-order representation
        of a regulator curve.

        Use this to build the actual outlet pressure history over a mission profile, rather than
        working from the band extremes.

        '''

        regulatorData = REGULATOR_TYPES[self.regulatorType.strip().lower()]

        outlet = self.setPressure * (1.0 + regulatorData['lockupRise'] -
                                     (regulatorData['lockupRise'] + regulatorData['droopCoefficient']) * flowFraction)

        if inletPressure is not None and not np.isnan(self.inletPressure):
            inletFraction = (inletPressure - self.inletPressure) / self.inletPressure
            outlet += regulatorData['supplyPressureEffect'] * inletFraction * self.setPressure

        return outlet

    def sizeRelief(self, reliefFlow: float = None) -> dict:

        '''

        Relief device flow area for a required relieving capacity.

        **The credible relieving case is a regulator failed fully open.** That is the dominant
        regulator failure mode and it is what the relief valve exists for. The relief must therefore
        pass the flow that the failed-open regulator can deliver at the maximum inlet pressure, not
        the normal system flow rate.

        For a choked gas relief:

            A = mdot / ( Kd * G_choked(P_relieving, T) )

        where the relieving pressure is the set pressure plus the accumulation.

        **Set point ladder.** The pressures must be ordered with margin between each step:

            operating pressure band (top)
                <  relief set pressure
                <  relief full flow (set + accumulation)
                <  system MEOP
                <  burst disc minimum (rating minus tolerance)
                <  proof pressure
                <  burst pressure of the weakest component

        If any two of those cross, the system either relieves during normal operation (which vents
        the pressurant and is a mission failure) or fails to relieve before something bursts.

        '''

        reliefData = RELIEF_TYPES[self.reliefType.strip().lower()]

        if np.isnan(self.reliefSetPressure):
            # Default to 10 percent above the regulator lockup pressure, which is the top of the
            # normal operating band.
            if np.isnan(self.lockupPressure):
                self.sizeRegulator()
            self.reliefSetPressure = 1.10 * self.lockupPressure
            self.designNotes.append(
                f'Relief set pressure not specified; assumed {self.reliefSetPressure / 1.0e6:.4f} MPa, which is 10 '
                f'percent above the regulator lockup pressure. A real relief valve has a stated set pressure '
                f'tolerance and it should be used instead.')

        self.reliefFullFlowPressure = self.reliefSetPressure * (1.0 + reliefData['accumulation'])
        if not np.isnan(reliefData['blowdown']):
            self.reliefReseatPressure = self.reliefSetPressure * (1.0 - reliefData['blowdown'])

        # Relieving flow: the failed-open regulator case unless one is given explicitly
        if reliefFlow is None:
            if np.isnan(self.massFlow) or np.isnan(self.inletPressure):
                raise InvalidInputError(
                    message       = ('sizeRelief needs either an explicit relief flow or a rated flow and inlet '
                                     'pressure so the failed-open regulator case can be constructed.'),
                    parameterName = 'reliefFlow', value = reliefFlow, validRange = 'Positive real'
                )
            # A failed-open regulator passes its full Cv at the full inlet pressure. Estimate that as
            # the rated flow scaled by the pressure ratio, which is the choked-flow scaling.
            reliefFlow = self.massFlow * self.inletPressure / max(self.finalInletPressure if not np.isnan(self.finalInletPressure) else self.inletPressure, 1.0)
            self.designNotes.append(
                f'Relief flow not specified; using the failed-open regulator case of {reliefFlow:.5f} kg/s, which is '
                f'the rated flow scaled to the maximum inlet pressure. Verify against the actual regulator Cv.')

        gamma       = float(fluidProps(self.fluid, 'TP', 'Cp/Cv', self.temperature, self.reliefFullFlowPressure))
        gasConstant = R_UNIVERSAL / speciesMolarMass(self.fluid)

        massFlux = chokedMassFlux(self.reliefFullFlowPressure, self.temperature, gamma, gasConstant)

        self.reliefArea     = reliefFlow / (reliefData['dischargeCoefficient'] * massFlux)
        self.reliefDiameter = np.sqrt(4.0 * self.reliefArea / np.pi)

        return {
            'reliefSetPressure':      self.reliefSetPressure,
            'reliefFullFlowPressure': self.reliefFullFlowPressure,
            'reliefReseatPressure':   self.reliefReseatPressure,
            'reliefFlow':             reliefFlow,
            'reliefArea':             self.reliefArea,
            'reliefDiameter':         self.reliefDiameter,
            'accumulation':           reliefData['accumulation'],
            'blowdown':               reliefData['blowdown']
        }

    def checkBurstDisc(self) -> dict:

        '''

        Actual burst pressure band including manufacturing tolerance and temperature derating.

        A burst disc is characterized by three numbers and people usually only quote the first:

        1. **Nominal burst pressure** at the reference temperature, usually 295 K
        2. **Manufacturing tolerance**, typically plus or minus 5 to 10 percent. Tighter tolerances
           are available at a cost, down to about 2 percent
        3. **Temperature derate.** The disc material softens with temperature and the burst pressure
           falls, by as much as 30 percent at moderate temperatures for aluminum

        **The band that matters is the LOW end for protection and the HIGH end for nuisance.** The
        disc must burst below the pressure that would damage the system, so the design case for
        protection is the maximum of the band. And it must not burst during normal operation, so the
        design case for nuisance is the minimum of the band. Both edges have to clear their
        respective limits.

        A disc rated 10 MPa with a 10 percent tolerance at 473 K in aluminum bursts somewhere between
        6.3 and 7.7 MPa, which is 30 percent below its nameplate. That has caught people out.

        '''

        if np.isnan(self.burstDiscRating):
            raise InvalidInputError(
                message       = 'checkBurstDisc needs a nominal burst disc rating.',
                parameterName = 'burstDiscRating', value = self.burstDiscRating, validRange = 'Positive real'
            )

        materialKey = self.burstDiscMaterial.strip().lower()
        if materialKey not in BURST_DISC_TEMPERATURE_DERATE:
            raise InvalidInputError(
                message       = f'Unknown burst disc material \'{self.burstDiscMaterial}\'.',
                parameterName = 'burstDiscMaterial', value = self.burstDiscMaterial,
                validRange    = str(sorted(BURST_DISC_TEMPERATURE_DERATE.keys()))
            )

        derateTable  = BURST_DISC_TEMPERATURE_DERATE[materialKey]
        temperatures = np.array([entry[0] for entry in derateTable])
        factors      = np.array([entry[1] for entry in derateTable])

        derateFactor = float(np.interp(self.burstDiscTemperature, temperatures, factors))

        deratedRating = self.burstDiscRating * derateFactor

        self.burstDiscBand = (deratedRating * (1.0 - self.burstDiscTolerance),
                              deratedRating * (1.0 + self.burstDiscTolerance))

        if self.burstDiscTemperature > temperatures[-1]:
            self.designNotes.append(
                f'Burst disc temperature {self.burstDiscTemperature:.0f} K is above the tabulated range for '
                f'{self.burstDiscMaterial}. The derate is extrapolated and should be verified with the manufacturer.')

        if derateFactor < 0.85:
            self.designNotes.append(
                f'Burst disc temperature derating is {(1.0 - derateFactor) * 100.0:.1f} percent at '
                f'{self.burstDiscTemperature:.0f} K. The nameplate rating is not the burst pressure.')

        return {
            'nominalRating':      self.burstDiscRating,
            'derateFactor':       derateFactor,
            'deratedRating':      deratedRating,
            'minimumBurst':       self.burstDiscBand[0],
            'maximumBurst':       self.burstDiscBand[1],
            'tolerance':          self.burstDiscTolerance,
            'temperature':        self.burstDiscTemperature
        }

    def checkPressureStackup(self) -> dict:

        '''

        Verify that the whole set point ladder is ordered correctly with margin.

        The required ordering, lowest to highest:

            regulator outlet band maximum
                < relief set pressure
                < relief full flow pressure
                < system MEOP
                < burst disc minimum burst
                < proof pressure

        **Two failure modes, and both are common:**

        - If the relief set pressure is too close to the regulator lockup pressure, the relief
          weeps or lifts during normal operation. On a spacecraft that vents the pressurant and ends
          the mission.
        - If the burst disc minimum is below the relief full flow pressure, the disc bursts before
          the relief can do its job, and the system is vented permanently by an event the relief was
          supposed to handle reversibly.

        Returns the ladder with the margin at each step and a pass/fail on each.

        '''

        ladder = []

        if np.isnan(self.lockupPressure):
            self.sizeRegulator()

        ladder.append(('Regulator outlet maximum', self.outletPressureBand[1]))

        if not np.isnan(self.reliefSetPressure):
            ladder.append(('Relief set pressure', self.reliefSetPressure))
        if not np.isnan(self.reliefFullFlowPressure):
            ladder.append(('Relief full flow', self.reliefFullFlowPressure))
        if not np.isnan(self.maximumOperatingPressure):
            ladder.append(('System MEOP', self.maximumOperatingPressure))
        if not np.isnan(self.burstDiscBand[0]):
            ladder.append(('Burst disc minimum', self.burstDiscBand[0]))
        if not np.isnan(self.proofPressure):
            ladder.append(('Proof pressure', self.proofPressure))

        results = []
        for index in range(len(ladder) - 1):
            lowerName, lowerValue = ladder[index]
            upperName, upperValue = ladder[index + 1]
            margin = (upperValue - lowerValue) / lowerValue
            passed = upperValue > lowerValue
            results.append({
                'lower': lowerName, 'lowerValue': lowerValue,
                'upper': upperName, 'upperValue': upperValue,
                'margin': margin, 'pass': passed
            })
            if not passed:
                self.designNotes.append(
                    f'PRESSURE LADDER VIOLATION: {upperName} ({upperValue / 1.0e6:.4f} MPa) is not above {lowerName} '
                    f'({lowerValue / 1.0e6:.4f} MPa).')
            elif margin < 0.05:
                self.designNotes.append(
                    f'Only {margin * 100.0:.1f} percent margin between {lowerName} and {upperName}. Set point '
                    f'tolerances alone can consume that.')

        return {'ladder': ladder, 'steps': results,
                'allPass': all(step['pass'] for step in results) if results else None}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        regulatorData = REGULATOR_TYPES[self.regulatorType.strip().lower()]

        rows = [
            ['Fluid',                   f'{self.fluid}'],
            ['Regulator type',          f'{self.regulatorType}'],
            ['Temperature',             f'{self.temperature:.2f} K'],
            ['Set pressure',            f'{self.setPressure / 1.0e6:.4f} MPa ({self.setPressure / PA_PER_PSIA:.1f} psia)'],
            ['Inlet pressure (initial)', f'{self.inletPressure / 1.0e6:.4f} MPa' if not np.isnan(self.inletPressure) else 'not specified'],
            ['Inlet pressure (final)',  f'{self.finalInletPressure / 1.0e6:.4f} MPa' if not np.isnan(self.finalInletPressure) else 'not specified'],
            ['Rated mass flow',         f'{self.massFlow:.5f} kg/s' if not np.isnan(self.massFlow) else 'not specified'],
            ['Droop coefficient',       f'{regulatorData["droopCoefficient"] * 100.0:.1f} %'],
            ['Supply pressure effect',  f'{regulatorData["supplyPressureEffect"] * 100.0:+.2f} % per unit inlet fraction'],
            ['Lockup rise',             f'{regulatorData["lockupRise"] * 100.0:.1f} %'],
            ['Outlet at rated flow',    f'{self.droopPressure / 1.0e6:.4f} MPa'],
            ['Outlet at lockup',        f'{self.lockupPressure / 1.0e6:.4f} MPa'],
            ['Outlet pressure band',    f'{self.outletPressureBand[0] / 1.0e6:.4f} to {self.outletPressureBand[1] / 1.0e6:.4f} MPa'],
            ['Band width',              f'{(self.outletPressureBand[1] - self.outletPressureBand[0]) / self.setPressure * 100.0:.2f} % of set'],
            ['Minimum inlet pressure',  f'{self.minimumInletPressure / 1.0e6:.4f} MPa'],
            ['Required Cv',             f'{self.requiredFlowCoefficient:.4f}' if not np.isnan(self.requiredFlowCoefficient) else 'not sized']
        ]

        if not np.isnan(self.reliefArea):
            rows.extend([
                ['Relief type',             f'{self.reliefType}'],
                ['Relief set pressure',     f'{self.reliefSetPressure / 1.0e6:.4f} MPa'],
                ['Relief full flow',        f'{self.reliefFullFlowPressure / 1.0e6:.4f} MPa'],
                ['Relief reseat',           f'{self.reliefReseatPressure / 1.0e6:.4f} MPa' if not np.isnan(self.reliefReseatPressure) else 'does not reseat'],
                ['Relief flow area',        f'{self.reliefArea * 1.0e6:.5f} mm^2'],
                ['Relief equivalent dia',   f'{self.reliefDiameter * 1.0e3:.4f} mm']
            ])

        if not np.isnan(self.burstDiscBand[0]):
            rows.extend([
                ['Burst disc material',     f'{self.burstDiscMaterial}'],
                ['Burst disc nominal',      f'{self.burstDiscRating / 1.0e6:.4f} MPa at 295 K'],
                ['Burst disc temperature',  f'{self.burstDiscTemperature:.1f} K'],
                ['Burst disc actual band',  f'{self.burstDiscBand[0] / 1.0e6:.4f} to {self.burstDiscBand[1] / 1.0e6:.4f} MPa']
            ])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'PRESSURE CONTROL REPORT')

        report += f'\n\nREGULATOR NOTES\n{"-" * 60}\n{regulatorData["description"]}\n{regulatorData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'regulatorReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.regulatorType.strip().lower() not in REGULATOR_TYPES:
            raise InvalidInputError(
                message       = f'Unknown regulator type \'{self.regulatorType}\'.',
                parameterName = 'regulatorType', value = self.regulatorType,
                validRange    = str(sorted(REGULATOR_TYPES.keys()))
            )

        if self.reliefType.strip().lower() not in RELIEF_TYPES:
            raise InvalidInputError(
                message       = f'Unknown relief type \'{self.reliefType}\'.',
                parameterName = 'reliefType', value = self.reliefType,
                validRange    = str(sorted(RELIEF_TYPES.keys()))
            )

        if self.setPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Regulator set pressure must be absolute and positive.',
                parameterName = 'setPressure', value = self.setPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if not np.isnan(self.inletPressure) and self.inletPressure <= self.setPressure:
            raise InvalidInputError(
                message       = 'Inlet pressure must exceed the set pressure. A regulator cannot raise pressure.',
                parameterName = 'inletPressure', value = self.inletPressure,
                validRange    = f'Greater than {self.setPressure:.6g} Pa'
            )
