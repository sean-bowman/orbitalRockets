
# -- MonopropThruster Class Definition -- #

'''

Monopropellant thruster performance, nozzle sizing and blowdown behaviour.

A monopropellant thruster is a catalyst bed with a nozzle on it. This class covers the nozzle and
performance half: throat sizing, expansion ratio, thrust coefficient, specific impulse, blowdown
decay and pulse mode behaviour. The chemistry and the bed itself are in
[CatalystBed](CatalystBed.py).

Hydrazine is the reference propellant and the one this class is calibrated against, delivering
roughly 220 to 235 s of vacuum specific impulse depending on expansion ratio and how much ammonia
the bed dissociates. That is unremarkable performance by bipropellant standards, and it is not the
point. The point is that a monopropellant thruster:

- has no oxidizer, so there is one tank, one feed system and no mixture ratio to control
- ignites spontaneously on the catalyst, so there is no igniter and no ignition sequence
- can pulse for milliseconds, thousands of times, over a decade in orbit
- can be built with a total of about three moving parts

The alternatives are covered in the comparison table: green monopropellants (AF-M315E/ASCENT,
LMP-103S) buy 10 to 15 percent more density-impulse and remove the toxicity handling burden, at the
cost of much higher combustion temperature and a preheat requirement. High-test peroxide gives lower
performance and much easier handling.

The other half of the design is the blowdown. Most spacecraft monopropellant systems are blowdown
rather than regulated: the tank is charged with pressurant once and the pressure falls as propellant
is consumed. Thrust falls with it. A 4:1 blowdown ratio means the last impulse is delivered at a
quarter of the initial chamber pressure and roughly half the initial thrust, and the vehicle control
system has to work across that whole range.

See Also:
---------
CatalystBed    : The decomposition chemistry and bed sizing
Pressurization : The blowdown or regulated pressurant system feeding it
Orifice        : The injector that meters propellant onto the bed

Theory: docs/MonopropellantThrusters.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                       GRAVITY, R_UNIVERSAL, PA_PER_PSIA, N_PER_LBF,
                       InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                        GRAVITY, R_UNIVERSAL, PA_PER_PSIA, N_PER_LBF,
                        InvalidInputError, createErrorContext)

try:
    from CatalystBed import CatalystBed
except ImportError:
    from .CatalystBed import CatalystBed

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Monopropellant comparison. Chamber conditions are at the typical operating dissociation or
# decomposition state for each; vacuum Isp is at an expansion ratio of about 50 with a realistic
# efficiency applied.
#
# Read the density-impulse column, not the Isp column. For a volume-limited spacecraft, which is
# almost all of them, rho*Isp is the figure of merit and it is where the green propellants win.
MONOPROPELLANTS = {
    'n2h4': {
        'name': 'Hydrazine (N2H4)', 'density': 1008.0, 'chamberTemperature': 1350.0,
        'characteristicVelocity': 1310.0, 'vacuumIsp': 230.0, 'freezingPoint': 274.7,
        'preheatRequired': False,
        'notes': 'The reference. Spontaneous catalytic decomposition down to 275 K, so no preheat is strictly '
                 'required. Acutely toxic and a suspected carcinogen; the handling infrastructure is the real '
                 'cost. Freezes at 1.5 degC, which drives heater power on every spacecraft that uses it.'
    },
    'af-m315e': {
        'name': 'AF-M315E / ASCENT (HAN-based)', 'density': 1465.0, 'chamberTemperature': 1900.0,
        'characteristicVelocity': 1450.0, 'vacuumIsp': 250.0, 'freezingPoint': 208.0,
        'preheatRequired': True,
        'notes': 'Hydroxylammonium nitrate ionic liquid. About 45 percent denser than hydrazine and 9 percent '
                 'higher Isp, so nearly 60 percent more density-impulse. Low toxicity and a very low freezing '
                 'point. The cost is a 1900 K chamber, which demands iridium-rhenium or similar refractory '
                 'chamber materials, and a catalyst bed preheat to roughly 640 K before every start.'
    },
    'lmp-103s': {
        'name': 'LMP-103S (ADN-based)', 'density': 1240.0, 'chamberTemperature': 1900.0,
        'characteristicVelocity': 1420.0, 'vacuumIsp': 245.0, 'freezingPoint': 183.0,
        'preheatRequired': True,
        'notes': 'Ammonium dinitramide in a methanol/water/ammonia solution. Flight proven on PRISMA. Similar '
                 'trade to AF-M315E: better performance and handling, at the cost of chamber temperature and '
                 'a preheat requirement.'
    },
    'h2o2-90': {
        'name': '90 % hydrogen peroxide', 'density': 1390.0, 'chamberTemperature': 1020.0,
        'characteristicVelocity': 950.0, 'vacuumIsp': 160.0, 'freezingPoint': 262.0,
        'preheatRequired': False,
        'notes': 'Decomposes over a silver or manganese oxide catalyst to steam and oxygen. Low performance, '
                 'but non-toxic products, high density, and the decomposition products are an oxidizer, which '
                 'makes it usable as the oxidizer half of a bipropellant. Decomposes slowly in storage and '
                 'requires scrupulous cleanliness: any catalytic contamination causes runaway decomposition.'
    },
    'h2o2-98': {
        'name': '98 % hydrogen peroxide', 'density': 1430.0, 'chamberTemperature': 1230.0,
        'characteristicVelocity': 990.0, 'vacuumIsp': 180.0, 'freezingPoint': 272.0,
        'preheatRequired': False,
        'notes': 'Higher concentration, higher decomposition temperature and performance. Correspondingly less '
                 'tolerant of contamination.'
    }
}

# Nozzle efficiency factors applied to the ideal performance.
#
#   c* efficiency        combustion or decomposition completeness and heat loss in the bed
#   divergence           momentum loss from non-axial exit flow, lambda = (1 + cos(alpha))/2
#   boundary layer       viscous loss, which is severe on a small thruster because the boundary
#                        layer is a large fraction of the throat
#
# The boundary layer number is the one that matters for a small thruster. On a 1 N thruster the
# throat is around 1 mm and the boundary layer displacement thickness is a meaningful fraction of it,
# which is why small thrusters deliver so much less than their theoretical Isp.
NOZZLE_EFFICIENCIES = {
    'large':  {'cStar': 0.96, 'boundaryLayer': 0.98, 'threshold': 100.0},   # above 100 N
    'medium': {'cStar': 0.95, 'boundaryLayer': 0.96, 'threshold': 10.0},    # 10 to 100 N
    'small':  {'cStar': 0.93, 'boundaryLayer': 0.92, 'threshold': 1.0},     # 1 to 10 N
    'micro':  {'cStar': 0.90, 'boundaryLayer': 0.85, 'threshold': 0.0}      # below 1 N
}

class MonopropThruster:

    '''

    Nozzle sizing, performance and blowdown behaviour for a monopropellant thruster.

    Primary Input Properties:
    -------------------------
    propellant : str
        Key into MONOPROPELLANTS
    thrust : float
        Required vacuum thrust [N]. Mutually exclusive with massFlow.
    massFlow : float
        Propellant mass flow rate [kg/s]. Mutually exclusive with thrust.
    chamberPressure : float
        Chamber (bed exit) pressure [Pa]
    expansionRatio : float
        Nozzle area ratio Ae/At [-]
    ambientPressure : float
        Back pressure [Pa]. Zero for vacuum.
    nozzleHalfAngle : float
        Conical nozzle divergence half angle [deg]
    injectorPressureDrop : float
        Injector differential as a fraction of chamber pressure [-]
    catalystBed : CatalystBed
        Optional. If supplied, c*, Tc and gamma are taken from it rather than the table.

    Key Output Properties:
    ----------------------
    throatArea / throatDiameter : float
        Nozzle throat [m^2], [m]
    exitArea / exitDiameter : float
        Nozzle exit [m^2], [m]
    thrustCoefficient : float
        Cf [-]
    specificImpulse : float
        Delivered Isp [s]
    vacuumSpecificImpulse : float
        Isp at zero back pressure [s]
    exitMachNumber / exitPressure : float
        Nozzle exit conditions
    feedPressure : float
        Required pressure upstream of the injector [Pa]

    Public Methods:
    ---------------
    setInputs(inputs)                       Load a configuration dictionary
    calculatePerformance()                  Throat, expansion, Cf, Isp, thrust
    calculateBlowdown(ratio, points)        Thrust and Isp decay over a blowdown
    calculateMinimumImpulseBit(pulseWidth)  Pulse mode minimum impulse
    comparePropellants()                    Side by side propellant selection table
    generateReport(outputDir)               Formatted results table

    Typical Workflow:
    -----------------
    >>> thruster = MonopropThruster()
    >>> thruster.setInputs({'propellant': 'n2h4', 'thrust': 100.0,
    ...                     'chamberPressure': 1.5e6, 'expansionRatio': 50.0})
    >>> thruster.calculatePerformance()
    >>> print(thruster.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Propellant and Duty -- #

        self.propellant           = 'n2h4'   # key into MONOPROPELLANTS
        self.thrust               = np.nan   # [N], vacuum. Mutually exclusive with massFlow.
        self.massFlow             = np.nan   # [kg/s]. Mutually exclusive with thrust.
        self.chamberPressure      = np.nan   # [Pa]
        self.ambientPressure      = 0.0      # [Pa], 0 for vacuum

        # -- Nozzle Geometry -- #

        self.expansionRatio       = 50.0     # [-], Ae/At
        self.nozzleHalfAngle      = 15.0     # [deg], conical divergence half angle

        # -- Feed System -- #

        # Injector stiffness. A monopropellant injector runs stiffer than a bipropellant one, because
        # a catalyst bed has its own pressure oscillations and the injector is the only thing
        # isolating the feed system from them.
        self.injectorPressureDrop = 0.25     # [-], fraction of chamber pressure

        # -- Chamber Source -- #

        # Optionally take the chamber conditions from an actual CatalystBed object rather than from
        # the propellant table. That is the right way to run a real design: the table entries are
        # nominal values, and the bed you actually built has its own dissociation fraction.
        self.catalystBed          = None     # CatalystBed instance or None

        # Size class override. The boundary layer efficiency is a property of the nozzle geometry,
        # not of the instantaneous thrust, so once hardware is sized the class must be frozen.
        # calculateBlowdown() sets this so that throttling down a fixed nozzle does not spuriously
        # reclassify it into a lower efficiency band.
        self.sizeClassOverride    = ''       # key into NOZZLE_EFFICIENCIES, or '' to auto-select

        # -- Results -- #

        self.chamberTemperature   = np.nan   # [K]
        self.characteristicVelocity = np.nan # [m/s], ideal
        self.deliveredCharacteristicVelocity = np.nan  # [m/s], after efficiency
        self.specificHeatRatio    = np.nan   # [-]
        self.throatArea           = np.nan   # [m^2]
        self.throatDiameter       = np.nan   # [m]
        self.exitArea             = np.nan   # [m^2]
        self.exitDiameter         = np.nan   # [m]
        self.exitMachNumber       = np.nan   # [-]
        self.exitPressure         = np.nan   # [Pa]
        self.thrustCoefficient    = np.nan   # [-]
        self.idealThrustCoefficient = np.nan # [-]
        self.specificImpulse      = np.nan   # [s]
        self.vacuumSpecificImpulse = np.nan  # [s]
        self.feedPressure         = np.nan   # [Pa]
        self.divergenceEfficiency = np.nan   # [-]
        self.sizeClass            = ''       # key into NOZZLE_EFFICIENCIES
        self.designNotes          = []       # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: chamberPressure, plus exactly one of thrust or massFlow.

        '''

        requiredParams = {
            'chamberPressure': 'Thruster chamber pressure not provided.'
        }

        optionalParams = ['propellant', 'thrust', 'massFlow', 'ambientPressure', 'expansionRatio',
                          'nozzleHalfAngle', 'injectorPressureDrop', 'catalystBed', 'sizeClassOverride']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculatePerformance(self) -> dict:

        '''

        Nozzle sizing and delivered performance.

        The chain is:

        1. Chamber conditions from the catalyst bed if one was supplied, otherwise from the
           propellant table.
        2. Ideal thrust coefficient from the expansion ratio and the specific heat ratio.
        3. Efficiency factors applied: c* efficiency, divergence, boundary layer.
        4. Throat area from `At = mdot * c* / Pc`, or mass flow from a required thrust.
        5. Feed pressure from the chamber pressure and the injector stiffness.

        **Thrust coefficient:**

            Cf_ideal = sqrt( (2*g^2/(g-1)) * (2/(g+1))^((g+1)/(g-1)) * (1 - (Pe/Pc)^((g-1)/g)) )
                     + (Pe - Pa)/Pc * epsilon

        The first term is the momentum contribution and the second is the pressure thrust. In vacuum
        the pressure thrust term is entirely positive and grows with expansion ratio, which is why
        vacuum thrusters use large area ratios.

        **Divergence efficiency** for a conical nozzle:

            lambda = (1 + cos(alpha)) / 2

        which is 0.983 at 15 degrees. A bell contour recovers most of that 1.7 percent, but on a
        small monopropellant thruster the boundary layer loss is five times larger than the
        divergence loss, so a conical nozzle is usually the right engineering answer.

        **Size-dependent efficiency** is the dominant effect on small thrusters. A 1 N thruster has a
        throat around 1 mm and a boundary layer displacement thickness that is a meaningful fraction
        of it. That is why a 1 N hydrazine thruster delivers around 200 s while a 400 N unit
        delivers 235 s from identical chemistry.

        '''

        # -- Chamber conditions -- #
        if self.catalystBed is not None:
            if np.isnan(self.catalystBed.characteristicVelocity):
                self.catalystBed.calculateDecomposition()
            self.characteristicVelocity = self.catalystBed.characteristicVelocity
            self.chamberTemperature     = self.catalystBed.chamberTemperature
            self.specificHeatRatio      = self.catalystBed.specificHeatRatio
            propellantDensity           = float(fluidProps('N2H4', 'TP', 'D', self.catalystBed.inletTemperature, self.chamberPressure))
        else:
            propellantData              = MONOPROPELLANTS[self.propellant.strip().lower()]
            self.characteristicVelocity = propellantData['characteristicVelocity']
            self.chamberTemperature     = propellantData['chamberTemperature']
            self.specificHeatRatio      = 1.31 if self.propellant.strip().lower().startswith('n2h4') else 1.25
            propellantDensity           = propellantData['density']

        gamma = self.specificHeatRatio

        # -- Nozzle expansion -- #
        self.exitMachNumber = self._exitMachNumber(self.expansionRatio, gamma)
        self.exitPressure   = self.chamberPressure / (1.0 + 0.5 * (gamma - 1.0) * self.exitMachNumber**2)**(gamma / (gamma - 1.0))

        # -- Ideal thrust coefficient -- #
        momentumTerm = np.sqrt((2.0 * gamma**2 / (gamma - 1.0)) *
                               (2.0 / (gamma + 1.0))**((gamma + 1.0) / (gamma - 1.0)) *
                               (1.0 - (self.exitPressure / self.chamberPressure)**((gamma - 1.0) / gamma)))
        pressureTerm = (self.exitPressure - self.ambientPressure) / self.chamberPressure * self.expansionRatio

        self.idealThrustCoefficient = momentumTerm + pressureTerm

        # -- Efficiencies -- #
        self.divergenceEfficiency = 0.5 * (1.0 + np.cos(np.radians(self.nozzleHalfAngle)))

        # Size class is set by the thrust level, which may not be known yet if mass flow was the
        # input. Estimate it from whichever is available.
        estimatedThrust = self.thrust
        if np.isnan(estimatedThrust):
            estimatedThrust = self.massFlow * self.characteristicVelocity * self.idealThrustCoefficient

        self.sizeClass = self.sizeClassOverride if self.sizeClassOverride else self._sizeClass(estimatedThrust)
        efficiencies   = NOZZLE_EFFICIENCIES[self.sizeClass]

        self.deliveredCharacteristicVelocity = self.characteristicVelocity * efficiencies['cStar']
        self.thrustCoefficient = (self.idealThrustCoefficient *
                                  self.divergenceEfficiency * efficiencies['boundaryLayer'])

        # -- Size the throat -- #
        if not np.isnan(self.thrust):
            # Thrust is the requirement; solve for mass flow and throat area
            self.throatArea = self.thrust / (self.chamberPressure * self.thrustCoefficient)
            self.massFlow   = self.chamberPressure * self.throatArea / self.deliveredCharacteristicVelocity
        else:
            self.throatArea = self.massFlow * self.deliveredCharacteristicVelocity / self.chamberPressure
            self.thrust     = self.chamberPressure * self.throatArea * self.thrustCoefficient

        self.throatDiameter = np.sqrt(4.0 * self.throatArea / np.pi)
        self.exitArea       = self.throatArea * self.expansionRatio
        self.exitDiameter   = np.sqrt(4.0 * self.exitArea / np.pi)

        # -- Specific impulse -- #
        self.specificImpulse = self.deliveredCharacteristicVelocity * self.thrustCoefficient / GRAVITY

        # Vacuum Isp, recomputed at zero back pressure
        vacuumPressureTerm      = self.exitPressure / self.chamberPressure * self.expansionRatio
        vacuumThrustCoefficient = ((momentumTerm + vacuumPressureTerm) *
                                   self.divergenceEfficiency * efficiencies['boundaryLayer'])
        self.vacuumSpecificImpulse = self.deliveredCharacteristicVelocity * vacuumThrustCoefficient / GRAVITY

        # -- Feed pressure -- #
        self.feedPressure = self.chamberPressure * (1.0 + self.injectorPressureDrop)

        # -- Advisories -- #
        if self.ambientPressure > 0.0 and self.exitPressure < 0.35 * self.ambientPressure:
            self.designNotes.append(
                f'Exit pressure {self.exitPressure / 1.0e3:.2f} kPa is below 35 percent of the '
                f'{self.ambientPressure / 1.0e3:.2f} kPa back pressure. The nozzle will flow separate. '
                f'Reduce the expansion ratio for sea level operation.')

        if self.sizeClass in ('small', 'micro'):
            self.designNotes.append(
                f'Thrust class \'{self.sizeClass}\' carries a boundary layer efficiency of '
                f'{efficiencies["boundaryLayer"]:.2f}. Small thruster performance is dominated by viscous loss in '
                f'the throat, not by chemistry. The delivered Isp is well below the theoretical value and no '
                f'amount of nozzle contouring recovers it.')

        return {
            'throatArea':            self.throatArea,
            'throatDiameter':        self.throatDiameter,
            'exitDiameter':          self.exitDiameter,
            'massFlow':              self.massFlow,
            'thrust':                self.thrust,
            'thrustCoefficient':     self.thrustCoefficient,
            'specificImpulse':       self.specificImpulse,
            'vacuumSpecificImpulse': self.vacuumSpecificImpulse,
            'feedPressure':          self.feedPressure
        }

    def calculateBlowdown(self, blowdownRatio: float = 4.0, numberOfPoints: int = 11,
                          polytropicExponent: float = 1.0) -> dict:

        '''

        Thrust and specific impulse decay over a blowdown.

        Most spacecraft monopropellant systems are blowdown rather than regulated: the tank is
        charged with pressurant once and the pressure falls as propellant is consumed. No regulator,
        no pressurant bottle, no isolation valves, which for a small satellite is a decisive
        simplification.

        The cost is that thrust falls with tank pressure. The chamber pressure tracks the feed
        pressure almost proportionally (the injector and the bed are both roughly square-law
        resistances in series with a choked throat), and thrust is proportional to chamber pressure:

            F ~ Pc,   mdot ~ Pc,   Isp roughly constant

        so a 4:1 blowdown ratio delivers its last impulse at a quarter of the initial thrust.
        Specific impulse falls only slightly, because c* is nearly independent of chamber pressure
        and the thrust coefficient improves marginally as the exit pressure ratio grows.

        **The design implications are all on the vehicle side:**

        - The attitude control system must be stable across a 4:1 thrust range
        - The minimum impulse bit changes by the same factor, which is what actually limits pointing
          accuracy at end of life
        - Burn durations grow, so thermal soakback grows
        - Beyond about 4:1 the low-end thrust becomes impractical, which is why 4:1 is the near
          universal choice

        `polytropicExponent` selects the ullage gas process: 1.0 for isothermal (slow expulsion, the
        gas stays in equilibrium with the tank wall) and gamma for adiabatic (fast expulsion). Real
        systems are between the two and closer to isothermal for typical spacecraft duty cycles.

        '''

        if np.isnan(self.throatArea):
            self.calculatePerformance()

        initialChamberPressure = self.chamberPressure
        initialThrust          = self.thrust
        savedMassFlow          = self.massFlow
        savedOverride          = self.sizeClassOverride

        # Freeze the nozzle efficiency class at the design point. The hardware does not change as the
        # tank blows down, so its boundary layer efficiency must not either.
        self.sizeClassOverride = self.sizeClass

        pressureRatios = np.linspace(1.0, 1.0 / blowdownRatio, numberOfPoints)

        thrusts        = np.zeros(numberOfPoints)
        massFlows      = np.zeros(numberOfPoints)
        specificImpulses = np.zeros(numberOfPoints)
        chamberPressures = np.zeros(numberOfPoints)

        for index, ratio in enumerate(pressureRatios):

            self.chamberPressure = initialChamberPressure * ratio
            self.thrust          = np.nan
            self.massFlow        = self.chamberPressure * self.throatArea / self.deliveredCharacteristicVelocity

            self.calculatePerformance()

            chamberPressures[index] = self.chamberPressure
            thrusts[index]          = self.thrust
            massFlows[index]        = self.massFlow
            specificImpulses[index] = self.vacuumSpecificImpulse

        # Restore the design point
        self.chamberPressure   = initialChamberPressure
        self.thrust            = initialThrust
        self.massFlow          = savedMassFlow
        self.sizeClassOverride = savedOverride
        self.calculatePerformance()

        # Ullage volume ratio required for the blowdown ratio
        ullageVolumeRatio = blowdownRatio**(1.0 / polytropicExponent)

        return {
            'blowdownRatio':      blowdownRatio,
            'chamberPressures':   chamberPressures,
            'thrusts':            thrusts,
            'massFlows':          massFlows,
            'specificImpulses':   specificImpulses,
            'initialThrust':      thrusts[0],
            'finalThrust':        thrusts[-1],
            'thrustRatio':        thrusts[-1] / thrusts[0],
            'ispRatio':           specificImpulses[-1] / specificImpulses[0],
            'ullageVolumeRatio':  ullageVolumeRatio,
            'initialUllageFraction': 1.0 / ullageVolumeRatio
        }

    def calculateMinimumImpulseBit(self, pulseWidth: float = 0.020,
                                   valveOpeningTime: float = 0.005,
                                   valveClosingTime: float = 0.005) -> dict:

        '''

        Minimum impulse bit for pulse mode operation.

        A monopropellant thruster used for attitude control spends most of its life firing pulses of
        a few tens of milliseconds. The impulse delivered by a short pulse is much less than
        `F * t`, because:

        - The valve takes time to open, during which flow is building
        - The bed has to fill and light, which is the **ignition delay** and is the dominant term for
          a cold bed
        - The chamber has to fill to pressure, which takes a few chamber residence times
        - On closing, the valve takes time to shut and the bed continues to decompose the propellant
          already in it, producing a **tail-off impulse** that is not commanded and is not
          repeatable

        The result is that the delivered impulse for a short pulse is nonlinear in pulse width, and
        below some minimum width it is not repeatable at all. That minimum is what limits the
        pointing accuracy achievable with a given thruster.

        This function estimates the impulse bit with a simple rise-and-decay model:

            t_effective = t_commanded - t_ignitionDelay - 0.5*t_open + 0.5*t_close

        The opening transient SUBTRACTS impulse, because thrust is building rather than steady over
        that interval. The closing transient ADDS impulse, because the bed keeps decomposing the
        propellant already in it after the valve has shut. The ignition delay subtracts directly:
        nothing at all is produced until the bed lights, which is why a cold bed can swallow a short
        pulse entirely and produce no impulse.

        With symmetric 5 ms valve transients the two cancel and the effective time is simply the
        commanded width less the ignition delay.

        **This is a first-order estimate.** Real minimum impulse bits are measured on a thrust stand,
        and the scatter between pulses is as important as the mean.

        '''

        if np.isnan(self.thrust):
            self.calculatePerformance()

        ignitionDelay = 0.0
        if self.catalystBed is not None and not np.isnan(self.catalystBed.ignitionDelay):
            ignitionDelay = self.catalystBed.ignitionDelay

        # Effective burn time. Opening subtracts (thrust is building), closing adds (the bed keeps
        # decomposing what is already in it), and the ignition delay subtracts outright.
        effectiveTime = pulseWidth - ignitionDelay - 0.5 * valveOpeningTime + 0.5 * valveClosingTime

        if effectiveTime <= 0.0:
            return {
                'pulseWidth':        pulseWidth,
                'ignitionDelay':     ignitionDelay,
                'effectiveTime':     0.0,
                'minimumImpulseBit': 0.0,
                'steadyStateImpulse': self.thrust * pulseWidth,
                'impulseEfficiency': 0.0,
                'feasible':          False,
                'note': f'The {ignitionDelay * 1.0e3:.1f} ms ignition delay exceeds the pulse width. The thruster '
                        f'will not light at all at this pulse width from this bed temperature.'
            }

        minimumImpulseBit  = self.thrust * effectiveTime
        steadyStateImpulse = self.thrust * pulseWidth

        return {
            'pulseWidth':         pulseWidth,
            'ignitionDelay':      ignitionDelay,
            'effectiveTime':      effectiveTime,
            'minimumImpulseBit':  minimumImpulseBit,
            'steadyStateImpulse': steadyStateImpulse,
            'impulseEfficiency':  minimumImpulseBit / steadyStateImpulse,
            'propellantPerPulse': self.massFlow * effectiveTime,
            'feasible':           True
        }

    def comparePropellants(self) -> str:

        '''

        Side by side monopropellant comparison at the current chamber pressure and expansion ratio.

        The column to read is density-impulse, `rho * Isp`. For a volume-limited spacecraft, which is
        almost all of them, that is the figure of merit rather than Isp alone, and it is where the
        green propellants win decisively despite their modest Isp advantage.

        '''

        savedPropellant  = self.propellant
        savedBed         = self.catalystBed
        savedThrust      = self.thrust
        savedMassFlow    = self.massFlow

        self.catalystBed = None
        rows = []

        for key, data in MONOPROPELLANTS.items():

            self.propellant = key
            self.thrust     = savedThrust if not np.isnan(savedThrust) else 100.0
            self.massFlow   = np.nan

            try:
                self.calculatePerformance()
            except Exception:
                continue

            densityImpulse = data['density'] * self.vacuumSpecificImpulse

            rows.append([
                data['name'],
                f'{data["density"]:.0f}',
                f'{data["chamberTemperature"]:.0f}',
                f'{self.vacuumSpecificImpulse:.1f}',
                f'{densityImpulse / 1.0e3:.1f}',
                f'{data["freezingPoint"]:.1f}',
                'yes' if data['preheatRequired'] else 'no'
            ])

        self.propellant  = savedPropellant
        self.catalystBed = savedBed
        self.thrust      = savedThrust
        self.massFlow    = savedMassFlow
        self.calculatePerformance()

        return formatReportTable(rows,
                                 ['Propellant', 'rho [kg/m3]', 'Tc [K]', 'Isp_vac [s]',
                                  'rho*Isp [kNs/m3]', 'Tfreeze [K]', 'Preheat'],
                                 title = f'MONOPROPELLANT COMPARISON  (Pc = {self.chamberPressure / 1.0e6:.2f} MPa, '
                                         f'eps = {self.expansionRatio:.0f})')

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        propellantData = MONOPROPELLANTS[self.propellant.strip().lower()]

        rows = [
            ['Propellant',              f'{propellantData["name"]}'],
            ['Chamber source',          'CatalystBed object' if self.catalystBed is not None else 'propellant table'],
            ['Chamber pressure',        f'{self.chamberPressure / 1.0e6:.4f} MPa ({self.chamberPressure / PA_PER_PSIA:.1f} psia)'],
            ['Chamber temperature',     f'{self.chamberTemperature:.1f} K'],
            ['Ideal c*',                f'{self.characteristicVelocity:.2f} m/s'],
            ['Delivered c*',            f'{self.deliveredCharacteristicVelocity:.2f} m/s'],
            ['Specific heat ratio',     f'{self.specificHeatRatio:.4f}'],
            ['Expansion ratio',         f'{self.expansionRatio:.2f}'],
            ['Exit Mach number',        f'{self.exitMachNumber:.4f}'],
            ['Exit pressure',           f'{self.exitPressure / 1.0e3:.4f} kPa'],
            ['Ambient pressure',        f'{self.ambientPressure / 1.0e3:.4f} kPa'],
            ['Size class',              f'{self.sizeClass}'],
            ['Divergence efficiency',   f'{self.divergenceEfficiency:.4f}'],
            ['Ideal Cf',                f'{self.idealThrustCoefficient:.4f}'],
            ['Delivered Cf',            f'{self.thrustCoefficient:.4f}'],
            ['Throat diameter',         f'{self.throatDiameter * 1.0e3:.4f} mm'],
            ['Exit diameter',           f'{self.exitDiameter * 1.0e3:.4f} mm'],
            ['Mass flow',               f'{self.massFlow:.6f} kg/s'],
            ['Thrust',                  f'{self.thrust:.3f} N ({self.thrust / N_PER_LBF:.3f} lbf)'],
            ['Specific impulse',        f'{self.specificImpulse:.2f} s'],
            ['Vacuum specific impulse', f'{self.vacuumSpecificImpulse:.2f} s'],
            ['Injector dP fraction',    f'{self.injectorPressureDrop:.3f}'],
            ['Required feed pressure',  f'{self.feedPressure / 1.0e6:.4f} MPa']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'MONOPROPELLANT THRUSTER REPORT')

        report += f'\n\nPROPELLANT NOTES\n{"-" * 60}\n{propellantData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'monopropThrusterReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.propellant.strip().lower() not in MONOPROPELLANTS:
            raise InvalidInputError(
                message       = f'Unknown monopropellant \'{self.propellant}\'.',
                parameterName = 'propellant', value = self.propellant,
                validRange    = str(sorted(MONOPROPELLANTS.keys()))
            )

        if self.chamberPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Chamber pressure must be positive.',
                parameterName = 'chamberPressure', value = self.chamberPressure,
                validRange    = 'Greater than 0 Pa'
            )

        thrustGiven   = not np.isnan(self.thrust)
        massFlowGiven = not np.isnan(self.massFlow)

        if thrustGiven == massFlowGiven:
            raise InvalidInputError(
                message       = ('Specify exactly one of thrust or massFlow. They are mutually exclusive: one is '
                                 'the requirement and the other is the result.'),
                parameterName = 'thrust/massFlow', value = (self.thrust, self.massFlow),
                validRange    = 'Exactly one specified'
            )

        if self.expansionRatio < 1.0:
            raise InvalidInputError(
                message       = 'Expansion ratio must be at least 1.',
                parameterName = 'expansionRatio', value = self.expansionRatio, validRange = '1 or greater'
            )

    def _sizeClass(self, thrust: float) -> str:

        '''

        Thrust size class for the efficiency lookup.

        '''

        for key in ('large', 'medium', 'small', 'micro'):
            if thrust >= NOZZLE_EFFICIENCIES[key]['threshold']:
                return key

        return 'micro'

    def _exitMachNumber(self, expansionRatio: float, gamma: float) -> float:

        '''

        Solve the area-Mach relation for the supersonic exit Mach number.

            A/At = (1/M) * [ (2/(g+1)) * (1 + (g-1)/2 * M^2) ]^((g+1)/(2*(g-1)))

        The relation has two roots, one subsonic and one supersonic. Seeding above Mach 1 selects the
        supersonic branch, which is the one a converging-diverging nozzle produces when it is
        operating correctly.

        '''

        if expansionRatio <= 1.0:
            return 1.0

        exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))

        def residual(machNumber: float) -> float:
            return (1.0 / machNumber) * ((2.0 / (gamma + 1.0)) *
                                         (1.0 + 0.5 * (gamma - 1.0) * machNumber**2))**exponent - expansionRatio

        # Seed above Mach 1 to land on the supersonic branch
        return secantSolve(residual, 3.0, lowerBound = 1.0001, upperBound = 50.0)
