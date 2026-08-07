
# -- LeakPath Class Definition -- #

'''

Leak rate analysis: units, flow regimes, equivalent hole size, detection methods and test design.

Leaks are the most misunderstood topic in fluid systems, for three reasons.

First, the units. Three unrelated families are in common use -- throughput (Pa-m^3/s, mbar-L/s),
standard volumetric (scc/s, sccm) and mass (lbm/yr) -- and converting between the first two and the
third requires knowing the gas. A specification written in one and verified in another is a common
and expensive mistake.

Second, the gas. Leak checks are run on helium and the hardware is used on something else. The
scaling between them depends on the flow regime, and it is not a single factor: in molecular flow
the rate scales as 1/sqrt(M), in viscous flow it scales as 1/mu, and those give different answers.
A joint that leaks 1e-5 scc/s of helium does not leak 1e-5 scc/s of hydrazine vapor, and the ratio
is not obvious.

Third, the physical meaning. A 'leak rate' is a flow through a passage, and how that passage behaves
depends on how its size compares to the mean free path of the gas. A leak that is viscous at 10 MPa
upstream is molecular at 1 kPa upstream, and the rate does not scale the way anyone expects.

This class handles all three, plus the two practical questions that follow: what size hole does this
leak rate correspond to, and what test method and duration can actually measure it.

See Also:
---------
Seal    : Permeation, which is a leak rate through a seal that is not leaking
Fitting : Achievable leak class by joint family
Weld    : The joint with the best achievable leak rate

Theory: docs/Leaks.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable, leakRateConvert,
                       speciesMolarMass, secantSolve, criticalPressureRatio, chokedMassFlux,
                       R_UNIVERSAL, PA_PER_ATM, LEAK_STD_PRESSURE, LEAK_STD_TEMPERATURE,
                       SECONDS_PER_YEAR, InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable, leakRateConvert,
                        speciesMolarMass, secantSolve, criticalPressureRatio, chokedMassFlux,
                        R_UNIVERSAL, PA_PER_ATM, LEAK_STD_PRESSURE, LEAK_STD_TEMPERATURE,
                        SECONDS_PER_YEAR, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Practical sensitivity floors for leak detection methods, in scc/s of helium. These are what a
# competent technician achieves on real hardware, not what the instrument datasheet claims in a
# laboratory.
#
# The spread is nine orders of magnitude. Choosing a method is therefore not a preference, it is a
# hard constraint on what leak rate you are allowed to specify: a requirement you cannot measure is
# not a requirement.
DETECTION_METHODS = {
    'mass spectrometer hard vacuum': {
        'sensitivity': 1.0e-11,
        'description': 'Part evacuated and connected to the spectrometer, helium sprayed outside. The most '
                       'sensitive method available and the reference for flight hardware.',
        'limitation':  'Requires the part to hold vacuum and to be small enough to pump down. Locates the leak '
                       'only as precisely as the spray probe is controlled.'
    },
    'mass spectrometer inside out': {
        'sensitivity': 1.0e-10,
        'description': 'Part pressurized with helium inside a vacuum chamber connected to the spectrometer. '
                       'Measures total leakage without locating it.',
        'limitation':  'Needs a vacuum chamber that fits the part. Gives a total, not a location.'
    },
    'accumulation': {
        'sensitivity': 1.0e-8,
        'description': 'Part pressurized with helium and enclosed in a bag or hood; the accumulated helium '
                       'concentration is sampled after a known dwell.',
        'limitation':  'Slow. Sensitivity depends on the enclosure volume and dwell time, so both must be '
                       'controlled and recorded.'
    },
    'sniffer probe': {
        'sensitivity': 1.0e-6,
        'description': 'Part pressurized with helium, a sampling probe traversed over each joint.',
        'limitation':  'Highly operator dependent. Probe standoff, traverse speed and background helium all '
                       'change the result by an order of magnitude. Good for locating, poor for quantifying.'
    },
    'pressure decay': {
        'sensitivity': 1.0e-4,
        'description': 'Isolated volume pressurized and the pressure decay measured over time.',
        'limitation':  'Sensitivity is set by transducer resolution, test volume and duration, and it is '
                       'destroyed by temperature drift. See calculatePressureDecayTest.'
    },
    'bubble immersion': {
        'sensitivity': 1.0e-4,
        'description': 'Part pressurized and immersed in liquid; bubbles counted. ASTM E515.',
        'limitation':  'Cannot be used on anything that must stay clean or dry afterward. Surface tension sets '
                       'the floor.'
    },
    'bubble solution': {
        'sensitivity': 1.0e-3,
        'description': 'Leak detection solution brushed onto the joint of a pressurized part.',
        'limitation':  'A contamination source. The solution must be removed and the joint re-cleaned.'
    },
    'ultrasonic': {
        'sensitivity': 1.0e-2,
        'description': 'Acoustic detection of the turbulent jet from a large leak.',
        'limitation':  'Only finds gross leaks. Useful for a first pass on a large system before spending '
                       'helium.'
    }
}

# Typical specified allowable leak rates by application, in scc/s of helium. Given so that a
# computed leak can be compared against what the industry actually requires.
TYPICAL_ALLOWABLE_LEAK_RATES = {
    'spacecraft propulsion, long duration':  1.0e-6,
    'spacecraft propulsion, per joint':      1.0e-7,
    'launch vehicle feed system':            1.0e-4,
    'hazardous fluid, external':             1.0e-6,
    'ground support equipment':              1.0e-3,
    'valve seat, class VI equivalent':       1.0e-4,
    'ultra high vacuum':                     1.0e-10
}

# Molecular diameters [m], for the mean free path calculation.
MOLECULAR_DIAMETERS = {
    'HE': 2.60e-10, 'HELIUM': 2.60e-10,
    'H2': 2.89e-10, 'HYDROGEN': 2.89e-10,
    'N2': 3.64e-10, 'NITROGEN': 3.64e-10, 'GN2': 3.64e-10,
    'O2': 3.46e-10, 'OXYGEN': 3.46e-10, 'GOX': 3.46e-10,
    'AIR': 3.66e-10,
    'AR': 3.40e-10, 'ARGON': 3.40e-10,
    'CH4': 3.80e-10, 'METHANE': 3.80e-10,
    'CO2': 3.30e-10,
    'NH3': 2.90e-10
}

class LeakPath:

    '''

    Leak rate analysis for a single leak path, treated as a capillary.

    Primary Input Properties:
    -------------------------
    species : str
        Leaking gas. Usually 'He' for a test, the service fluid for an assessment.
    upstreamPressure : float
        Pressure on the high side [Pa, absolute]
    downstreamPressure : float
        Pressure on the low side [Pa, absolute]
    temperature : float
        Gas temperature [K]
    diameter : float
        Leak path diameter [m]. Leave unset to solve for it from a measured rate.
    length : float
        Leak path length [m]. Defaults to 1 mm, a reasonable proxy for a joint.
    leakRate : float
        Measured or specified leak rate. Leave unset to compute it from the geometry.
    leakRateUnit : str
        Unit of leakRate; any unit accepted by leakRateConvert. Defaults to 'sccs'.

    Key Output Properties:
    ----------------------
    knudsenNumber : float
        Mean free path over path diameter [-]
    regime : str
        'viscous', 'transitional', 'molecular' or 'choked'
    conductance : float
        Path conductance [m^3/s]
    leakRateStandard : float
        Leak rate in scc/s
    equivalentDiameter : float
        Diameter of a round capillary that would give the measured rate [m]
    requiredMethod : str
        The least sensitive detection method that can measure this rate

    Public Methods:
    ---------------
    setInputs(inputs)                    Load a configuration dictionary
    calculateLeakRate()                  Geometry to leak rate
    calculateEquivalentDiameter()        Leak rate to geometry
    convertUnits()                       The rate expressed in every unit
    scaleToSpecies(target)               Convert a helium test result to the service fluid
    selectDetectionMethod()              Least sensitive method that can see this rate
    calculatePressureDecayTest(volume, resolution, duration)
                                         Feasibility of a pressure decay test
    calculateAllowableFromHazard(...)    Allowable rate from a concentration limit
    generateReport(outputDir)            Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Gas and State -- #

        self.species              = 'He'    # [case insensitive string]
        self.upstreamPressure     = np.nan  # [Pa, absolute]
        self.downstreamPressure   = 0.0     # [Pa, absolute], 0 for a vacuum-side measurement
        self.temperature          = 293.15  # [K]

        # -- Geometry -- #

        # A real leak is a crack, a scratch across a seal, or a porosity channel, none of which are
        # round capillaries. The capillary model is a standardized proxy: it gives a single
        # equivalent diameter that reproduces the measured rate, which is what lets two leaks be
        # compared. Do not read the equivalent diameter as a physical dimension.
        self.diameter             = np.nan  # [m]
        self.length               = 1.0e-3  # [m], typical joint sealing land length

        # -- Measured or Specified Rate -- #

        self.leakRate             = np.nan  # [in leakRateUnit]
        self.leakRateUnit         = 'sccs'  # any unit accepted by leakRateConvert

        # -- Results -- #

        self.meanFreePath         = np.nan  # [m]
        self.knudsenNumber        = np.nan  # [-]
        self.regime               = ''      # 'viscous' / 'transitional' / 'molecular' / 'choked'
        self.conductance          = np.nan  # [m^3/s]
        self.throughput           = np.nan  # [Pa-m^3/s]
        self.leakRateStandard     = np.nan  # [scc/s]
        self.massLeakRate         = np.nan  # [kg/s]
        self.equivalentDiameter   = np.nan  # [m]
        self.requiredMethod       = ''      # key into DETECTION_METHODS
        self.viscosity            = np.nan  # [Pa-s]
        self.molarMass            = np.nan  # [kg/mol]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: upstreamPressure.

        '''

        requiredParams = {
            'upstreamPressure': 'Leak path upstream pressure not provided.'
        }

        optionalParams = ['species', 'downstreamPressure', 'temperature', 'diameter', 'length',
                          'leakRate', 'leakRateUnit']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._evaluateGasState()

    def calculateLeakRate(self) -> float:

        '''

        Forward problem: leak rate through a capillary of known diameter and length.

        The regime is selected from the Knudsen number, the ratio of the mean free path to the path
        diameter:

            Kn < 0.01          viscous (continuum). Poiseuille flow.
            0.01 < Kn < 1      transitional. Sum of the viscous and molecular contributions.
            Kn > 1             molecular. Free molecular (Knudsen) conductance.

        Viscous (Poiseuille) throughput:

            Q = pi * d^4 * (P1^2 - P2^2) / (256 * mu * L)

        Molecular (Knudsen) conductance of a long tube:

            C = (pi/12) * v_mean * d^3 / L,     v_mean = sqrt( 8*R*T / (pi*M) )
            Q = C * (P1 - P2)

        Transitional flow is handled by adding the two contributions, which is the standard
        engineering approximation and is accurate to about 20 percent across the transition.

        A large leak at high differential can also choke. That is checked, and if the choked mass
        flux gives a lower rate than the viscous solution, choking governs.

        Note that the regime moves with pressure. The same physical crack is viscous at 10 MPa
        upstream and molecular at 1 kPa, and the rate does not scale the way anyone expects between
        the two. This is exactly why a leak measured at test pressure cannot be linearly scaled to
        operating pressure.

        '''

        if np.isnan(self.diameter):
            raise InvalidInputError(
                message       = 'calculateLeakRate needs a path diameter. Set diameter, or call calculateEquivalentDiameter().',
                parameterName = 'diameter', value = self.diameter, validRange = 'Positive real'
            )

        self._evaluateRegime()

        gasConstant       = R_UNIVERSAL / self.molarMass
        meanThermalSpeed  = np.sqrt(8.0 * gasConstant * self.temperature / np.pi)

        # -- Viscous (Poiseuille) contribution -- #
        viscousThroughput = (np.pi * self.diameter**4 *
                             (self.upstreamPressure**2 - self.downstreamPressure**2) /
                             (256.0 * self.viscosity * self.length))

        # -- Molecular (Knudsen) contribution -- #
        molecularConductance = (np.pi / 12.0) * meanThermalSpeed * self.diameter**3 / self.length
        molecularThroughput  = molecularConductance * (self.upstreamPressure - self.downstreamPressure)

        if self.regime == 'viscous':
            self.throughput = viscousThroughput
        elif self.regime == 'molecular':
            self.throughput = molecularThroughput
        else:
            # Transitional: sum the contributions
            self.throughput = viscousThroughput + molecularThroughput

        # -- Choking check -- #
        # A large leak with a high pressure ratio is limited by sonic velocity at the exit, not by
        # viscosity. Take whichever mechanism gives the lower flow.
        gamma         = float(fluidProps(self.species, 'TP', 'Cp/Cv', self.temperature, max(self.upstreamPressure, 1.0)))
        pressureRatio = self.downstreamPressure / self.upstreamPressure

        if pressureRatio <= criticalPressureRatio(gamma):
            flowArea          = np.pi * self.diameter**2 / 4.0
            chokedMass        = 0.61 * flowArea * chokedMassFlux(self.upstreamPressure, self.temperature, gamma, gasConstant)
            # Convert the choked mass flow to throughput at the standard reference state
            chokedThroughput  = chokedMass / (self.molarMass / (R_UNIVERSAL * LEAK_STD_TEMPERATURE))
            if chokedThroughput < self.throughput:
                self.throughput = chokedThroughput
                self.regime     = 'choked'

        self.conductance      = self.throughput / max(self.upstreamPressure - self.downstreamPressure, 1.0e-12)
        self.leakRateStandard = leakRateConvert(self.throughput, 'pam3s', 'sccs', species = self.species,
                                                temperature = LEAK_STD_TEMPERATURE)
        self.massLeakRate     = leakRateConvert(self.throughput, 'pam3s', 'kgs', species = self.species,
                                                temperature = LEAK_STD_TEMPERATURE)

        self.leakRate     = self.leakRateStandard
        self.leakRateUnit = 'sccs'

        return self.leakRateStandard

    def calculateEquivalentDiameter(self) -> float:

        '''

        Inverse problem: the diameter of a round capillary that would produce the measured leak rate,
        at the stated pressures and path length.

        This is a standardized comparison quantity, not a physical measurement. A real leak is a
        crack in a weld, a scratch across a sealing face, or an interconnected porosity network, and
        none of those are round holes. What the equivalent diameter buys you is the ability to
        compare two leaks and to develop intuition for what a specification actually means.

        For scale: a 1e-6 scc/s helium leak at 1 atm differential corresponds to an equivalent hole
        of about a micron. A 1e-11 scc/s leak, the flight hardware standard, corresponds to a few
        nanometers, which is smaller than the surface roughness of a well-lapped seal. At that level
        the leak is not a hole at all; it is transport through the interface.

        '''

        if np.isnan(self.leakRate):
            raise InvalidInputError(
                message       = 'calculateEquivalentDiameter needs a measured or specified leak rate.',
                parameterName = 'leakRate', value = self.leakRate, validRange = 'Positive real'
            )

        targetThroughput = leakRateConvert(self.leakRate, self.leakRateUnit, 'pam3s',
                                           species = self.species, temperature = LEAK_STD_TEMPERATURE)

        savedDiameter = self.diameter

        def residual(trialDiameter: float) -> float:
            self.diameter = trialDiameter
            self.calculateLeakRate()
            # Solve on log throughput: the relation spans many orders of magnitude and a linear
            # residual makes the secant method behave badly at the small end.
            return np.log(max(self.throughput, 1.0e-300)) - np.log(max(targetThroughput, 1.0e-300))

        self.equivalentDiameter = secantSolve(residual, 1.0e-6, lowerBound = 1.0e-12, upperBound = 1.0e-2)
        self.diameter           = self.equivalentDiameter

        self.calculateLeakRate()
        self.leakRate     = leakRateConvert(targetThroughput, 'pam3s', 'sccs', species = self.species,
                                            temperature = LEAK_STD_TEMPERATURE)
        self.leakRateUnit = 'sccs'

        return self.equivalentDiameter

    def convertUnits(self) -> dict:

        '''

        The current leak rate expressed in every supported unit.

        Provided because leak specifications arrive in whatever unit the author was raised on, and
        the conversion between the volumetric and mass families requires the molar mass, which makes
        it easy to get wrong by hand.

        '''

        if np.isnan(self.leakRate):
            raise InvalidInputError(
                message       = 'convertUnits needs a leak rate.',
                parameterName = 'leakRate', value = self.leakRate, validRange = 'Positive real'
            )

        units = ['sccs', 'sccm', 'slpm', 'pam3s', 'mbarls', 'torrls', 'atmccs', 'kgs', 'gyr', 'lbmyr']

        return {unit: leakRateConvert(self.leakRate, self.leakRateUnit, unit,
                                      species = self.species, temperature = LEAK_STD_TEMPERATURE)
                for unit in units}

    def scaleToSpecies(self, targetSpecies: str) -> dict:

        '''

        Scale a leak rate measured on one gas to another gas through the same physical path.

        This is the conversion that turns a helium acceptance test into a statement about the fluid
        the hardware actually contains, and it is regime dependent:

            Molecular flow:   rate scales as 1 / sqrt(M)     (thermal speed)
            Viscous flow:     rate scales as 1 / mu          (Poiseuille)
            Choked flow:      rate scales as sqrt(gamma/M) x the choked function

        The ratios returned are target over source. For helium to nitrogen the two limits point in
        opposite directions, which is the whole reason this method exists:

            molecular:  sqrt(M_He / M_N2)   = sqrt(4/28)  = 0.38   nitrogen leaks 2.6x LESS
            viscous:    mu_He / mu_N2       = 1.96 / 1.79 = 1.10   nitrogen leaks 10 % MORE

        Helium is more viscous than nitrogen at room temperature, which surprises everyone, and in
        viscous flow that makes nitrogen the faster leaker despite being seven times heavier.

        Both are returned along with the value for the current regime, because knowing which one
        applies requires knowing the regime, and the regime depends on the pressure at which the
        hardware is used rather than the pressure at which it was tested.

        '''

        if np.isnan(self.leakRate):
            raise InvalidInputError(
                message       = 'scaleToSpecies needs a leak rate.',
                parameterName = 'leakRate', value = self.leakRate, validRange = 'Positive real'
            )

        sourceMolarMass = speciesMolarMass(self.species)
        targetMolarMass = speciesMolarMass(targetSpecies)

        sourceViscosity = self.viscosity
        targetViscosity = float(fluidProps(targetSpecies, 'TP', 'VIS', self.temperature,
                                           max(self.upstreamPressure, 1.0e3)))

        molecularRatio = np.sqrt(sourceMolarMass / targetMolarMass)
        viscousRatio   = sourceViscosity / targetViscosity

        if self.regime == 'molecular':
            appliedRatio = molecularRatio
        elif self.regime in ('viscous', 'choked'):
            appliedRatio = viscousRatio
        else:
            appliedRatio = np.sqrt(molecularRatio * viscousRatio)   # geometric blend in transition

        return {
            'sourceSpecies':   self.species,
            'targetSpecies':   targetSpecies,
            'regime':          self.regime,
            'molecularRatio':  molecularRatio,
            'viscousRatio':    viscousRatio,
            'appliedRatio':    appliedRatio,
            'sourceLeakRate':  self.leakRate,
            'targetLeakRate':  self.leakRate * appliedRatio
        }

    def selectDetectionMethod(self) -> str:

        '''

        Identify the least sensitive detection method that can measure the current leak rate with a
        factor of ten of margin.

        The margin matters. Specifying a leak rate at the exact sensitivity floor of a method means
        every measurement is a coin flip between pass and fail, and the argument that follows is
        about instrumentation rather than hardware.

        '''

        if np.isnan(self.leakRate):
            raise InvalidInputError(
                message       = 'selectDetectionMethod needs a leak rate.',
                parameterName = 'leakRate', value = self.leakRate, validRange = 'Positive real'
            )

        rateInSccs = leakRateConvert(self.leakRate, self.leakRateUnit, 'sccs',
                                     species = self.species, temperature = LEAK_STD_TEMPERATURE)

        # Sort methods coarse to fine and pick the first that clears the rate by 10x
        candidates = sorted(DETECTION_METHODS.items(), key = lambda item: -item[1]['sensitivity'])

        for name, data in candidates:
            if data['sensitivity'] * 10.0 <= rateInSccs:
                self.requiredMethod = name
                return name

        self.requiredMethod = candidates[-1][0]

        if DETECTION_METHODS[self.requiredMethod]['sensitivity'] > rateInSccs:
            print(f'Warning: a leak rate of {rateInSccs:.2e} scc/s is below the {self.requiredMethod} floor of '
                  f'{DETECTION_METHODS[self.requiredMethod]["sensitivity"]:.1e} scc/s. This requirement cannot be '
                  f'verified by any method in the table.')

        return self.requiredMethod

    def calculatePressureDecayTest(self, testVolume: float, transducerResolution: float,
                                   testDuration: float, temperatureStability: float = 0.1) -> dict:

        '''

        Feasibility of measuring the current leak rate by pressure decay.

        A pressure decay test isolates a known volume, pressurizes it, and measures the pressure fall
        over time. The leak throughput is

            Q = V * dP / dt

        so the minimum detectable leak is set by the transducer resolution, the volume and the
        duration:

            Q_min = V * dP_resolution / t_test

        That part is simple. The part that kills pressure decay tests is temperature. For a fixed
        volume of ideal gas,

            dP / P = dT / T

        so a temperature drift of only 0.1 K at 293 K produces a pressure change of 3.4e-4 of the
        absolute pressure. At 10 MPa that is 3.4 kPa, which is very often orders of magnitude larger
        than the leak signal being sought. **Pressure decay tests are almost always
        temperature-limited, not transducer-limited.**

        The returned dictionary reports both floors so the binding one is visible. If the
        temperature-equivalent leak exceeds the target, the test cannot work without active
        temperature control or a temperature-compensated reference volume, no matter how good the
        transducer is.

        ---------------------------------------------------------------------------
                                        INPUTS
        ---------------------------------------------------------------------------
        - testVolume            Isolated volume [m^3]
        - transducerResolution  Smallest resolvable pressure change [Pa]
        - testDuration          Test duration [s]
        - temperatureStability  Expected temperature drift over the test [K]

        '''

        # -- Transducer-limited floor -- #
        transducerThroughput = testVolume * transducerResolution / testDuration
        transducerFloorSccs  = leakRateConvert(transducerThroughput, 'pam3s', 'sccs',
                                               species = self.species, temperature = LEAK_STD_TEMPERATURE)

        # -- Temperature-limited floor -- #
        # A temperature drift dT produces an apparent pressure change P * dT/T, indistinguishable
        # from a leak over the test duration.
        temperatureEquivalentPressure = self.upstreamPressure * temperatureStability / self.temperature
        temperatureThroughput         = testVolume * temperatureEquivalentPressure / testDuration
        temperatureFloorSccs          = leakRateConvert(temperatureThroughput, 'pam3s', 'sccs',
                                                        species = self.species, temperature = LEAK_STD_TEMPERATURE)

        overallFloor = max(transducerFloorSccs, temperatureFloorSccs)
        limitedBy    = 'temperature drift' if temperatureFloorSccs > transducerFloorSccs else 'transducer resolution'

        targetRate = np.nan
        feasible   = None
        requiredDuration = np.nan
        if not np.isnan(self.leakRate):
            targetRate = leakRateConvert(self.leakRate, self.leakRateUnit, 'sccs',
                                         species = self.species, temperature = LEAK_STD_TEMPERATURE)
            feasible   = targetRate >= 10.0 * overallFloor
            # Duration required to reach a 10x margin, scaling the floor as 1/t
            requiredDuration = testDuration * 10.0 * overallFloor / targetRate

        return {
            'transducerFloorSccs':   transducerFloorSccs,
            'temperatureFloorSccs':  temperatureFloorSccs,
            'overallFloorSccs':      overallFloor,
            'limitedBy':             limitedBy,
            'targetLeakRateSccs':    targetRate,
            'feasible':              feasible,
            'requiredDurationSeconds': requiredDuration,
            'expectedPressureDrop':  (leakRateConvert(targetRate, 'sccs', 'pam3s', species = self.species,
                                                      temperature = LEAK_STD_TEMPERATURE) * testDuration / testVolume)
                                     if not np.isnan(targetRate) else np.nan
        }

    def calculateAllowableFromHazard(self, enclosureVolume: float, concentrationLimit: float,
                                     ventilationRate: float = 0.0, exposureTime: float = 3600.0) -> dict:

        '''

        Derive an allowable leak rate from a hazard criterion rather than picking one from a table.

        This is the right way to set a leak requirement for a toxic or flammable fluid: work back
        from the concentration that is actually dangerous in the volume the leak discharges into.

        With no ventilation, the concentration after a time t is

            C = Q_leak * t / V_enclosure

        With ventilation at volumetric rate V_dot, the steady state concentration is

            C_steady = Q_leak / V_dot

        and the allowable leak follows directly. The returned dictionary gives both, because a
        design that relies on ventilation must also survive the ventilation failing.

        ---------------------------------------------------------------------------
                                        INPUTS
        ---------------------------------------------------------------------------
        - enclosureVolume     Volume the leak discharges into [m^3]
        - concentrationLimit  Allowable volume fraction [-]. Examples:
                                hydrazine 8-hour TWA        1.0e-8  (0.01 ppm)
                                hydrogen lower flammability 0.04    (4 percent)
                                oxygen enrichment limit     0.235   (23.5 percent)
                                ammonia 8-hour TWA          2.5e-5  (25 ppm)
        - ventilationRate     Enclosure ventilation [m^3/s]. Zero for a sealed volume.
        - exposureTime        Accumulation time for the unventilated case [s]

        '''

        # -- Unventilated accumulation -- #
        allowableVolumetric = concentrationLimit * enclosureVolume / exposureTime   # [m^3/s of leaked gas at ambient]

        # Convert an ambient-condition volumetric rate to standard cc/s
        allowableThroughput = allowableVolumetric * LEAK_STD_PRESSURE
        allowableSccs       = leakRateConvert(allowableThroughput, 'pam3s', 'sccs',
                                              species = self.species, temperature = LEAK_STD_TEMPERATURE)

        # -- Ventilated steady state -- #
        ventilatedSccs = np.nan
        if ventilationRate > 0.0:
            ventilatedVolumetric = concentrationLimit * ventilationRate
            ventilatedSccs       = leakRateConvert(ventilatedVolumetric * LEAK_STD_PRESSURE, 'pam3s', 'sccs',
                                                   species = self.species, temperature = LEAK_STD_TEMPERATURE)

        return {
            'allowableUnventilatedSccs': allowableSccs,
            'allowableVentilatedSccs':   ventilatedSccs,
            'governingAllowableSccs':    allowableSccs,   # the unventilated case always governs for a safety case
            'enclosureVolume':           enclosureVolume,
            'concentrationLimit':        concentrationLimit,
            'exposureTime':              exposureTime
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table with the rate expressed in every unit.

        '''

        rows = [
            ['Species',              f'{self.species}'],
            ['Molar mass',           f'{self.molarMass * 1.0e3:.4f} g/mol'],
            ['Upstream pressure',    f'{self.upstreamPressure / 1.0e3:.4f} kPa'],
            ['Downstream pressure',  f'{self.downstreamPressure / 1.0e3:.4f} kPa'],
            ['Temperature',          f'{self.temperature:.2f} K'],
            ['Path length',          f'{self.length * 1.0e3:.4f} mm'],
            ['Path diameter',        f'{self.diameter * 1.0e6:.5f} micron' if not np.isnan(self.diameter) else 'not computed'],
            ['Mean free path',       f'{self.meanFreePath * 1.0e6:.5f} micron'],
            ['Knudsen number',       f'{self.knudsenNumber:.4g}'],
            ['Flow regime',          f'{self.regime}'],
            ['Conductance',          f'{self.conductance:.4e} m^3/s' if not np.isnan(self.conductance) else 'not computed']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'LEAK PATH REPORT')

        if not np.isnan(self.leakRate):
            conversions = self.convertUnits()
            unitRows = [
                ['scc/s',      f'{conversions["sccs"]:.4e}'],
                ['sccm',       f'{conversions["sccm"]:.4e}'],
                ['std L/min',  f'{conversions["slpm"]:.4e}'],
                ['Pa-m^3/s',   f'{conversions["pam3s"]:.4e}'],
                ['mbar-L/s',   f'{conversions["mbarls"]:.4e}'],
                ['torr-L/s',   f'{conversions["torrls"]:.4e}'],
                ['kg/s',       f'{conversions["kgs"]:.4e}'],
                ['g/yr',       f'{conversions["gyr"]:.4e}'],
                ['lbm/yr',     f'{conversions["lbmyr"]:.4e}']
            ]
            report += '\n\n' + formatReportTable(unitRows, ['Unit', 'Value'], title = 'LEAK RATE IN ALL UNITS')

            method = self.selectDetectionMethod()
            report += (f'\n\nDETECTION\n{"-" * 60}\n'
                       f'Least sensitive adequate method (10x margin): {method}\n'
                       f'  Floor:      {DETECTION_METHODS[method]["sensitivity"]:.1e} scc/s\n'
                       f'  Method:     {DETECTION_METHODS[method]["description"]}\n'
                       f'  Limitation: {DETECTION_METHODS[method]["limitation"]}\n')

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'leakReport.txt'), 'w') as fileHandle:
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
                message       = 'Leak path upstream pressure must be absolute and positive.',
                parameterName = 'upstreamPressure', value = self.upstreamPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if self.downstreamPressure > self.upstreamPressure:
            raise InvalidInputError(
                message       = 'Downstream pressure exceeds upstream pressure. A leak flows one way.',
                parameterName = 'downstreamPressure', value = self.downstreamPressure,
                validRange    = f'0 to {self.upstreamPressure:.6g} Pa'
            )

        if self.length <= 0.0:
            raise InvalidInputError(
                message       = 'Leak path length must be positive.',
                parameterName = 'length', value = self.length, validRange = 'Greater than 0 m'
            )

    def _evaluateGasState(self) -> None:

        '''

        Molar mass and viscosity of the leaking species. Viscosity is evaluated at the mean pressure,
        which for a gas at these pressures barely matters, but it costs nothing to be correct.

        '''

        self.molarMass = speciesMolarMass(self.species)

        meanPressure   = max(0.5 * (self.upstreamPressure + self.downstreamPressure), 1.0e3)
        self.viscosity = float(fluidProps(self.species, 'TP', 'VIS', self.temperature, meanPressure))

    def _evaluateRegime(self) -> None:

        '''

        Mean free path, Knudsen number and flow regime.

        The mean free path is evaluated at the MEAN pressure through the path, because that is what
        the gas in the passage actually sees. Using the upstream pressure would put a leak into
        vacuum in the viscous regime when most of its length is molecular.

            lambda = k_B * T / ( sqrt(2) * pi * d_molecule^2 * P )

        '''

        boltzmannConstant = 1.380649e-23   # J/K

        molecularDiameter = MOLECULAR_DIAMETERS.get(self.species.strip().upper(), 3.5e-10)
        meanPressure      = max(0.5 * (self.upstreamPressure + self.downstreamPressure), 1.0e-3)

        self.meanFreePath  = boltzmannConstant * self.temperature / (np.sqrt(2.0) * np.pi * molecularDiameter**2 * meanPressure)
        self.knudsenNumber = self.meanFreePath / self.diameter

        if self.knudsenNumber < 0.01:
            self.regime = 'viscous'
        elif self.knudsenNumber < 1.0:
            self.regime = 'transitional'
        else:
            self.regime = 'molecular'
