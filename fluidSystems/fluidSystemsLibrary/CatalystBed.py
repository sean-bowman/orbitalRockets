
# -- CatalystBed Class Definition -- #

'''

Hydrazine catalyst bed sizing, decomposition chemistry and pressure drop.

A catalyst bed is the combustion chamber of a monopropellant thruster. It has no igniter, no
oxidizer and no injector spray to worry about: liquid hydrazine contacts an iridium-on-alumina
catalyst, decomposes spontaneously, and leaves as hot gas. That simplicity is why monopropellant
systems are the default for spacecraft attitude control and why they have flown on essentially every
satellite since the 1960s.

The chemistry runs in two steps, and the split between them controls everything:

    3 N2H4  ->  4 NH3 + N2                  strongly exothermic
    4 NH3   ->  2 N2 + 6 H2                 endothermic

The first step releases the heat. The second step consumes some of it back but reduces the molecular
weight, and characteristic velocity depends on both:

    c* ~ sqrt( T / MW )

so there is an optimum ammonia dissociation fraction. It sits around 0.3 to 0.4, and it is set by
bed geometry and residence time rather than by anything you can dial in directly. Long beds
dissociate more ammonia; short beds dissociate less.

The three sizing quantities are:

    bed loading G        mass flow per unit bed cross section [kg/m^2-s]
    bed length L         sets residence time and therefore ammonia dissociation
    granule size         sets pressure drop, surface area and attrition resistance

This class covers all three, plus the Ergun pressure drop, the decomposition energy balance, and the
operational limits that actually kill catalyst beds: cold starts, poisoning, and attrition.

See Also:
---------
MonopropThruster : The nozzle and performance side of the same device
Orifice          : The injector that distributes propellant onto the bed
Hydrazine        : Propellant properties, handling and materials (docs/Hydrazine.md)

Theory: docs/CatalystBeds.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                       R_UNIVERSAL, PA_PER_PSIA, KG_PER_LBM, M_PER_IN,
                       InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                        R_UNIVERSAL, PA_PER_PSIA, KG_PER_LBM, M_PER_IN,
                        InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Hydrazine decomposition energetics, per mole of N2H4 decomposed, from liquid at 298 K.
HYDRAZINE_MOLAR_MASS        = 32.0451e-3   # kg/mol
AMMONIA_MOLAR_MASS          = 17.0305e-3   # kg/mol
NITROGEN_MOLAR_MASS         = 28.0134e-3   # kg/mol
HYDROGEN_MOLAR_MASS         = 2.01588e-3   # kg/mol

HEAT_OF_DECOMPOSITION       = 112.3e3      # J/mol N2H4, exothermic, step 1
HEAT_OF_AMMONIA_DISSOCIATION = 46.0e3      # J/mol NH3, endothermic, step 2

# Adiabatic decomposition temperature as a function of ammonia dissociation fraction X, for
# hydrazine initially at 298 K. The published curve is very nearly linear over the full range:
#
#   X = 0.0   ->  1659 K   all the heat retained, but MW = 19.2 g/mol
#   X = 1.0   ->   894 K   MW down to 10.7 g/mol, but the endotherm has taken most of the heat
#
# The linear fit reproduces the published curve to within about 1 percent. The energy balance that
# produces it is derived in docs/CatalystBeds.md; the fit is used here because the mean product Cp
# needed for the balance is itself a fit, and chaining two fits gains nothing.
ADIABATIC_TEMPERATURE_ZERO_DISSOCIATION = 1659.0   # K
ADIABATIC_TEMPERATURE_SLOPE             = -765.0   # K per unit dissociation fraction

# Catalyst granule sizes by US mesh designation [m]. Shell 405 and its equivalents are supplied
# graded to these ranges.
#
# The size trade is direct: smaller granules give more surface area per unit volume (faster
# decomposition, shorter bed) and more pressure drop, and they are more prone to being blown out of
# the bed. Larger granules give the reverse. Most beds are packed with a coarse layer at the inlet
# (to survive the liquid impingement) and a finer layer downstream.
MESH_SIZES = {
    '14-18': (1.410e-3, 1.000e-3),   # coarse, inlet layer
    '20-25': (0.841e-3, 0.707e-3),   # the general purpose size
    '25-30': (0.707e-3, 0.595e-3),   # fine, downstream layer
    '30-35': (0.595e-3, 0.500e-3)
}

# Catalyst properties.
#
#   bulkDensity     as-packed bed density [kg/m^3]
#   voidFraction    interparticle void fraction [-]
#   activityFactor  relative decomposition rate, Shell 405 = 1.0
#   minimumStartTemperature   coldest bed temperature at which a reliable cold start occurs [K]
CATALYSTS = {
    'shell 405': {
        'bulkDensity': 1200.0, 'voidFraction': 0.37, 'activityFactor': 1.00,
        'minimumStartTemperature': 275.0, 'iridiumLoading': 0.32,
        'description': 'Iridium on high surface area alumina, roughly 32 weight percent Ir. The reference '
                       'spontaneous hydrazine catalyst since 1962.',
        'notes': 'Spontaneous down to about 275 K, which is what makes an unheated cold start possible. Below '
                 'that the start is rough or fails. Expensive: the iridium content dominates the cost of a '
                 'small thruster.'
    },
    'lch-202': {
        'bulkDensity': 1150.0, 'voidFraction': 0.38, 'activityFactor': 0.95,
        'minimumStartTemperature': 280.0, 'iridiumLoading': 0.30,
        'description': 'European equivalent of Shell 405, produced by Aerojet/ArianeGroup lineage.',
        'notes': 'Comparable performance and availability outside the US export chain.'
    },
    'h-kc12ga': {
        'bulkDensity': 1250.0, 'voidFraction': 0.36, 'activityFactor': 0.92,
        'minimumStartTemperature': 285.0, 'iridiumLoading': 0.28,
        'description': 'Kaiser/Aerojet iridium-alumina catalyst.',
        'notes': 'Slightly lower activity than Shell 405, marginally better attrition resistance.'
    }
}

# Bed loading limits, mass flow per unit bed frontal area.
#
# Below the minimum the bed runs cold and wet: not enough heat is generated per unit area to hold the
# bed above the decomposition temperature, and liquid hydrazine works its way through undecomposed.
# Above the maximum the residence time is too short, dissociation falls, and the catalyst is
# physically eroded by the flow.
#
# Values in kg/m^2-s. The imperial equivalents (lbm/in^2-s) are the ones in the literature:
#   0.02 lbm/in^2-s = 14.1 kg/m^2-s
#   0.05 lbm/in^2-s = 35.2 kg/m^2-s
BED_LOADING_MINIMUM   = 10.0   # kg/m^2-s, roughly 0.014 lbm/in^2-s
BED_LOADING_NOMINAL   = 25.0   # kg/m^2-s, roughly 0.036 lbm/in^2-s
BED_LOADING_MAXIMUM   = 40.0   # kg/m^2-s, roughly 0.057 lbm/in^2-s

# Catalyst poisons and their effect. A poisoned bed does not fail suddenly; it degrades, with rising
# ignition delay and falling performance, until a start fails.
CATALYST_POISONS = {
    'water':    'MIL-PRF-26536 limits water to 1.0 weight percent. Water occupies active sites and raises '
                'ignition delay. It is also the most common contaminant because hydrazine is hygroscopic.',
    'aniline':  'Limited to 0.5 weight percent. A residual from the hydrazine production process. Strongly '
                'adsorbed and effectively permanent.',
    'carbon dioxide': 'Forms carbonate on the alumina support. Picked up from any air exposure of the '
                      'propellant or of the bed itself. A bed left open to air degrades.',
    'chlorides': 'Attack the alumina support and the iridium. Sources include cleaning solvents, handling '
                 'with bare hands, and PVC.',
    'iron and other metals': 'Catalyze hydrazine decomposition in the feed line rather than in the bed, which '
                             'produces gas upstream of the injector. Copper is the worst; keep all '
                             'copper-bearing alloys out of a hydrazine system.',
    'sulfur':   'Classic noble metal catalyst poison. Trace sulfur from any source is permanent.'
}

class CatalystBed:

    '''

    Sizing and analysis for a hydrazine monopropellant catalyst bed.

    Primary Input Properties:
    -------------------------
    massFlow : float
        Propellant mass flow rate [kg/s]
    chamberPressure : float
        Bed exit (chamber) pressure [Pa]
    inletTemperature : float
        Propellant temperature entering the bed [K]
    bedLoading : float
        Mass flow per unit bed frontal area [kg/m^2-s]. Defaults to BED_LOADING_NOMINAL.
    bedLength : float
        Catalyst bed length [m]. Leave unset to size from the residence time target.
    ammoniaDissociation : float
        Fraction of the ammonia that dissociates, X [-]. Defaults to 0.40.
    catalyst : str
        Key into CATALYSTS
    meshSize : str
        Key into MESH_SIZES
    bedTemperature : float
        Bed temperature at start [K], for the cold start check
    lengthToDiameterRatio : float
        Target bed L/D [-]. Used when bedLength is not given.

    Key Output Properties:
    ----------------------
    bedDiameter / bedArea / bedLength / bedVolume : float
        Bed geometry [m], [m^2], [m], [m^3]
    chamberTemperature : float
        Adiabatic decomposition temperature [K]
    characteristicVelocity : float
        c* of the decomposition products [m/s]
    productMolarMass : float
        Mean molecular weight of the products [kg/mol]
    specificHeatRatio : float
        Product gamma [-]
    pressureDrop : float
        Ergun pressure drop across the bed [Pa]
    residenceTime : float
        Gas residence time in the bed [s]
    catalystMass : float
        Mass of catalyst in the bed [kg]

    Public Methods:
    ---------------
    setInputs(inputs)                 Load a configuration dictionary
    calculateDecomposition()          Chemistry, temperature, molecular weight, c*
    sizeBed()                         Bed diameter, length, volume and catalyst mass
    calculatePressureDrop()           Ergun packed bed pressure drop
    optimalDissociation()             The X that maximizes c*
    checkColdStart()                  Cold start feasibility and ignition delay estimate
    generateReport(outputDir)         Formatted results table

    Typical Workflow:
    -----------------
    >>> bed = CatalystBed()
    >>> bed.setInputs({'massFlow': 0.045, 'chamberPressure': 1.5e6,
    ...                'inletTemperature': 293.15, 'ammoniaDissociation': 0.40})
    >>> bed.calculateDecomposition()
    >>> bed.sizeBed()
    >>> bed.calculatePressureDrop()
    >>> print(bed.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Duty -- #

        self.massFlow              = np.nan  # [kg/s]
        self.chamberPressure       = np.nan  # [Pa], bed exit
        self.inletTemperature      = 293.15  # [K], propellant entering the bed

        # -- Bed Definition -- #

        self.catalyst              = 'shell 405'  # key into CATALYSTS
        self.meshSize              = '20-25'      # key into MESH_SIZES
        self.bedLoading            = np.nan  # [kg/m^2-s], defaults to nominal
        self.bedLength             = np.nan  # [m], leave unset to size from L/D
        self.lengthToDiameterRatio = 1.5     # [-], target when bedLength is not given
        self.voidFraction          = np.nan  # [-], overrides the catalyst default

        # -- Chemistry -- #

        # Ammonia dissociation fraction. Not a free design variable in practice: it is an outcome of
        # bed geometry and residence time. It is exposed as an input because the bed geometry that
        # produces a given X cannot be predicted without test data, so real design work runs the
        # other way: measure X from a test, then use it here.
        self.ammoniaDissociation   = 0.40    # [-]

        # -- Start Conditions -- #

        self.bedTemperature        = 293.15  # [K], bed temperature at start

        # -- Results -- #

        self.bedArea               = np.nan  # [m^2]
        self.bedDiameter           = np.nan  # [m]
        self.bedVolume             = np.nan  # [m^3]
        self.catalystMass          = np.nan  # [kg]
        self.chamberTemperature    = np.nan  # [K]
        self.productMolarMass      = np.nan  # [kg/mol]
        self.specificGasConstant   = np.nan  # [J/kg-K]
        self.specificHeatRatio     = np.nan  # [-]
        self.characteristicVelocity = np.nan # [m/s]
        self.productMoles          = {}      # {species: mol per mol N2H4}
        self.pressureDrop          = np.nan  # [Pa]
        self.superficialVelocity   = np.nan  # [m/s]
        self.residenceTime         = np.nan  # [s]
        self.particleDiameter      = np.nan  # [m]
        self.actualBedLoading      = np.nan  # [kg/m^2-s]
        self.ignitionDelay         = np.nan  # [s]
        self.designNotes           = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: massFlow, chamberPressure.

        '''

        requiredParams = {
            'massFlow':        'Catalyst bed mass flow rate not provided.',
            'chamberPressure': 'Catalyst bed chamber pressure not provided.'
        }

        optionalParams = ['inletTemperature', 'catalyst', 'meshSize', 'bedLoading', 'bedLength',
                          'lengthToDiameterRatio', 'voidFraction', 'ammoniaDissociation',
                          'bedTemperature']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateDecomposition(self) -> dict:

        '''

        Decomposition chemistry: product composition, adiabatic temperature, molecular weight,
        specific heat ratio and characteristic velocity.

        Per mole of hydrazine, with ammonia dissociation fraction X:

            N2H4  ->  (4/3)(1-X) NH3  +  (1/3 + (2/3)X) N2  +  2X H2

        Check the extremes. At X = 0 the products are 4/3 mol NH3 and 1/3 mol N2, total 5/3 mol, mean
        molecular weight 19.2 g/mol. At X = 1 the products are 1 mol N2 and 2 mol H2, total 3 mol,
        mean molecular weight 10.7 g/mol.

        **The temperature and molecular weight move in opposite directions**, and c* depends on the
        ratio:

            c* ~ sqrt( R_universal * T / (MW * gamma) )

        so there is an interior optimum. Dissociating ammonia costs temperature and buys molecular
        weight, and somewhere between X = 0.3 and X = 0.4 the two effects balance. Use
        optimalDissociation() to find it for the current conditions.

        The adiabatic temperature uses the published linear fit
        `T = 1659 - 765*X`, corrected for the propellant inlet temperature. It reproduces the
        published curve to about 1 percent over the full range.

        '''

        dissociation = float(np.clip(self.ammoniaDissociation, 0.0, 1.0))

        # -- Product composition per mole of N2H4 -- #
        ammoniaMoles  = (4.0 / 3.0) * (1.0 - dissociation)
        nitrogenMoles = (1.0 / 3.0) + (2.0 / 3.0) * dissociation
        hydrogenMoles = 2.0 * dissociation
        totalMoles    = ammoniaMoles + nitrogenMoles + hydrogenMoles

        self.productMoles = {
            'NH3': ammoniaMoles,
            'N2':  nitrogenMoles,
            'H2':  hydrogenMoles,
            'total': totalMoles
        }

        # Mass is conserved, so the mean molar mass follows directly from the mole count
        self.productMolarMass    = HYDRAZINE_MOLAR_MASS / totalMoles
        self.specificGasConstant = R_UNIVERSAL / self.productMolarMass

        # -- Adiabatic temperature -- #
        # Linear fit to the published curve, plus a first-order correction for propellant inlet
        # temperature. The correction uses the liquid specific heat: propellant arriving warm brings
        # sensible heat with it that does not have to come out of the reaction.
        baseTemperature = ADIABATIC_TEMPERATURE_ZERO_DISSOCIATION + ADIABATIC_TEMPERATURE_SLOPE * dissociation

        liquidSpecificHeat = float(fluidProps('N2H4', 'TP', 'Cp', self.inletTemperature, self.chamberPressure))
        # Mean product molar specific heat, back-calculated from the fit so the correction is
        # consistent with it rather than introducing a second, conflicting property set.
        meanProductMolarCp = (HEAT_OF_DECOMPOSITION - HEAT_OF_AMMONIA_DISSOCIATION * (4.0 / 3.0) * dissociation) / \
                             (totalMoles * (baseTemperature - 298.15))
        inletCorrection    = (liquidSpecificHeat * HYDRAZINE_MOLAR_MASS * (self.inletTemperature - 298.15)) / \
                             (totalMoles * meanProductMolarCp)

        self.chamberTemperature = baseTemperature + inletCorrection

        # -- Specific heat ratio -- #
        # Ammonia is a polyatomic with a low gamma; the N2/H2 mixture is diatomic with a higher one.
        # Mole-weighted between the two limits: 1.27 at X = 0, 1.37 at X = 1.
        self.specificHeatRatio = 1.27 + 0.10 * dissociation

        # -- Characteristic velocity -- #
        gamma = self.specificHeatRatio
        vandenkerckhove = np.sqrt(gamma) * (2.0 / (gamma + 1.0))**((gamma + 1.0) / (2.0 * (gamma - 1.0)))
        self.characteristicVelocity = np.sqrt(self.specificGasConstant * self.chamberTemperature) / vandenkerckhove

        return {
            'chamberTemperature':     self.chamberTemperature,
            'productMolarMass':       self.productMolarMass,
            'specificGasConstant':    self.specificGasConstant,
            'specificHeatRatio':      self.specificHeatRatio,
            'characteristicVelocity': self.characteristicVelocity,
            'productMoles':           self.productMoles
        }

    def optimalDissociation(self) -> dict:

        '''

        The ammonia dissociation fraction that maximizes characteristic velocity.

        Sweeps X from 0 to 1, evaluates c* at each point, and returns the maximum. The result
        typically lands between 0.3 and 0.4 and the peak is broad, which is fortunate because X is
        not directly controllable.

        The broadness of the peak is the practical takeaway: c* varies by only a few percent between
        X = 0.2 and X = 0.6, so a bed that runs anywhere in that band is performing near its
        theoretical best. What is NOT flat is the chamber temperature, which falls by nearly 300 K
        across the same range and directly sets the thermal environment for the chamber wall, the
        throat and the valve soakback. **Bed length is usually chosen for thermal reasons, not for
        performance ones.**

        '''

        savedDissociation = self.ammoniaDissociation

        dissociations = np.linspace(0.0, 1.0, 101)
        velocities    = np.zeros_like(dissociations)
        temperatures  = np.zeros_like(dissociations)

        for index, value in enumerate(dissociations):
            self.ammoniaDissociation = value
            self.calculateDecomposition()
            velocities[index]   = self.characteristicVelocity
            temperatures[index] = self.chamberTemperature

        bestIndex = int(np.argmax(velocities))

        self.ammoniaDissociation = savedDissociation
        self.calculateDecomposition()

        return {
            'optimalDissociation':      float(dissociations[bestIndex]),
            'maximumCharacteristicVelocity': float(velocities[bestIndex]),
            'temperatureAtOptimum':     float(temperatures[bestIndex]),
            'dissociationSweep':        dissociations,
            'characteristicVelocitySweep': velocities,
            'temperatureSweep':         temperatures
        }

    def sizeBed(self) -> dict:

        '''

        Bed frontal area, diameter, length, volume and catalyst mass.

        The frontal area comes directly from the bed loading:

            A_bed = mdot / G

        Bed loading is the primary sizing parameter and it has a narrow acceptable band:

            below 10 kg/m^2-s   the bed runs cold and wet. Not enough heat is generated per unit area
                                to hold the bed above the decomposition temperature, and liquid
                                hydrazine works its way through undecomposed. Undecomposed hydrazine
                                arriving at the throat is a hard failure.
            10 to 40 kg/m^2-s   the design band. Nominal is around 25.
            above 40 kg/m^2-s   residence time is too short, dissociation falls, and the flow
                                physically erodes the catalyst.

        Bed length is either specified or derived from the target L/D. There is no first-principles
        way to predict the length required for a given ammonia dissociation without test data, which
        is why L/D is used as a design heuristic and the resulting X is measured.

        '''

        bedLoading = self.bedLoading
        if np.isnan(bedLoading):
            bedLoading = BED_LOADING_NOMINAL

        self.actualBedLoading = bedLoading
        self.bedArea          = self.massFlow / bedLoading
        self.bedDiameter      = np.sqrt(4.0 * self.bedArea / np.pi)

        if np.isnan(self.bedLength):
            self.bedLength = self.lengthToDiameterRatio * self.bedDiameter

        self.bedVolume = self.bedArea * self.bedLength

        catalystData      = CATALYSTS[self.catalyst.strip().lower()]
        self.catalystMass = self.bedVolume * catalystData['bulkDensity']

        # Bed loading advisories
        if bedLoading < BED_LOADING_MINIMUM:
            self.designNotes.append(
                f'Bed loading {bedLoading:.2f} kg/m^2-s is below the {BED_LOADING_MINIMUM:.0f} kg/m^2-s minimum. '
                f'The bed will run cold and wet, and undecomposed hydrazine can reach the throat.')
        elif bedLoading > BED_LOADING_MAXIMUM:
            self.designNotes.append(
                f'Bed loading {bedLoading:.2f} kg/m^2-s exceeds the {BED_LOADING_MAXIMUM:.0f} kg/m^2-s maximum. '
                f'Residence time is short, ammonia dissociation will be low, and the catalyst will erode.')

        # Residence time, based on the hot gas leaving the bed. This is the gas-phase residence time
        # in the void volume, which is the quantity that governs the ammonia dissociation kinetics.
        if not np.isnan(self.chamberTemperature):
            voidFraction  = self._voidFraction()
            gasDensity    = self.chamberPressure / (self.specificGasConstant * self.chamberTemperature)
            voidVolume    = self.bedVolume * voidFraction
            self.residenceTime = voidVolume * gasDensity / self.massFlow

        return {
            'bedArea':       self.bedArea,
            'bedDiameter':   self.bedDiameter,
            'bedLength':     self.bedLength,
            'bedVolume':     self.bedVolume,
            'catalystMass':  self.catalystMass,
            'bedLoading':    self.actualBedLoading,
            'residenceTime': self.residenceTime
        }

    def calculatePressureDrop(self) -> float:

        '''

        Ergun equation pressure drop through the packed bed.

            dP/L = 150 * mu * (1-eps)^2 * U / (eps^3 * dp^2)
                 + 1.75 * (1-eps) * rho * U^2 / (eps^3 * dp)

        The first term is viscous (Blake-Kozeny) and dominates at low Reynolds number; the second is
        inertial (Burke-Plummer) and dominates at high Reynolds number. `U` is the superficial
        velocity, the volumetric flow divided by the total bed frontal area as if the bed were empty.

        **This is a substantial approximation and it should be treated as one.** A hydrazine catalyst
        bed is not a single-phase packed bed. The inlet is liquid, the outlet is hot gas at ten times
        the volume flow, and the transition happens over the first few particle diameters. The
        density and viscosity change by orders of magnitude across a region where most of the
        pressure drop occurs.

        The treatment here evaluates the Ergun equation at the hot gas exit condition, which is where
        the superficial velocity and therefore the inertial term are largest. That is deliberately
        conservative and it is the right answer within a factor of about two. **A real bed pressure
        drop is measured, not calculated**, and it is typically 10 to 25 percent of chamber pressure.

        '''

        if np.isnan(self.bedArea):
            raise InvalidInputError(
                message       = 'calculatePressureDrop needs the bed geometry. Call sizeBed() first.',
                parameterName = 'bedArea', value = self.bedArea, validRange = 'Positive real'
            )

        if np.isnan(self.chamberTemperature):
            self.calculateDecomposition()

        voidFraction          = self._voidFraction()
        self.particleDiameter = self._particleDiameter()

        # Hot gas exit condition
        gasDensity   = self.chamberPressure / (self.specificGasConstant * self.chamberTemperature)
        # Product gas viscosity. Sutherland-style estimate for a hot N2/NH3/H2 mixture; the Ergun
        # viscous term is small at these Reynolds numbers so this does not need to be precise.
        gasViscosity = 3.5e-5 * (self.chamberTemperature / 1000.0)**0.7

        self.superficialVelocity = self.massFlow / (gasDensity * self.bedArea)

        viscousTerm  = (150.0 * gasViscosity * (1.0 - voidFraction)**2 * self.superficialVelocity /
                        (voidFraction**3 * self.particleDiameter**2))
        inertialTerm = (1.75 * (1.0 - voidFraction) * gasDensity * self.superficialVelocity**2 /
                        (voidFraction**3 * self.particleDiameter))

        self.pressureDrop = (viscousTerm + inertialTerm) * self.bedLength

        pressureDropFraction = self.pressureDrop / self.chamberPressure
        if pressureDropFraction > 0.30:
            self.designNotes.append(
                f'Bed pressure drop is {pressureDropFraction * 100.0:.1f} percent of chamber pressure. That is high; '
                f'a typical bed is 10 to 25 percent. Consider a coarser granule size, a shorter bed, or a lower '
                f'bed loading.')

        return self.pressureDrop

    def checkColdStart(self) -> dict:

        '''

        Cold start feasibility and an ignition delay estimate.

        Shell 405 is a **spontaneous** catalyst: hydrazine decomposes on contact with no ignition
        source, down to roughly 275 K. That is the entire reason monopropellant systems are so
        reliable, and it is what the catalyst was developed for.

        Below that temperature the start becomes rough or fails:

        - Ignition delay lengthens from milliseconds to hundreds of milliseconds
        - Unreacted hydrazine accumulates in the bed during the delay
        - When it does light, the accumulated propellant decomposes at once, producing a **hard
          start**: a pressure spike that can exceed several times the nominal chamber pressure
        - Repeated hard starts shatter the catalyst granules, which then wash out of the bed

        Catalyst bed heaters exist for exactly this reason. A spacecraft monopropellant thruster is
        typically held at 350 to 400 K by a bed heater before any firing, which eliminates the delay,
        eliminates the hard start, and substantially extends catalyst life.

        The ignition delay estimate here is an Arrhenius-form correlation anchored on the published
        behaviour: a few milliseconds at 350 K, tens of milliseconds near 290 K, and hundreds of
        milliseconds approaching the freezing point. It is indicative and no substitute for test
        data on the specific bed.

        '''

        catalystData        = CATALYSTS[self.catalyst.strip().lower()]
        minimumTemperature  = catalystData['minimumStartTemperature']

        # Arrhenius-form ignition delay, anchored on 3 ms at 350 K with an activation temperature
        # that reproduces the published order-of-magnitude rise toward the freezing point.
        referenceDelay       = 3.0e-3    # s at 350 K
        activationTemperature = 3500.0   # K
        self.ignitionDelay   = referenceDelay * np.exp(activationTemperature * (1.0 / self.bedTemperature - 1.0 / 350.0))

        feasible = self.bedTemperature >= minimumTemperature

        if not feasible:
            self.designNotes.append(
                f'Bed temperature {self.bedTemperature:.1f} K is below the {minimumTemperature:.0f} K reliable start '
                f'threshold for {self.catalyst}. Expect long ignition delay, hard starts, and catalyst attrition. '
                f'A bed heater is required.')
        elif self.bedTemperature < 320.0:
            self.designNotes.append(
                f'Bed temperature {self.bedTemperature:.1f} K gives an estimated ignition delay of '
                f'{self.ignitionDelay * 1.0e3:.1f} ms. A bed heater holding 350 to 400 K would reduce this to a few '
                f'milliseconds and substantially extend catalyst life.')

        return {
            'bedTemperature':         self.bedTemperature,
            'minimumStartTemperature': minimumTemperature,
            'feasible':               feasible,
            'ignitionDelay':          self.ignitionDelay,
            'hardStartRisk':          'high' if not feasible else ('moderate' if self.bedTemperature < 320.0 else 'low')
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        catalystData = CATALYSTS[self.catalyst.strip().lower()]

        rows = [
            ['Catalyst',                 f'{self.catalyst}'],
            ['Granule mesh size',        f'{self.meshSize} ({self.particleDiameter * 1.0e3:.4f} mm mean)' if not np.isnan(self.particleDiameter) else self.meshSize],
            ['Mass flow',                f'{self.massFlow:.5f} kg/s'],
            ['Chamber pressure',         f'{self.chamberPressure / 1.0e6:.4f} MPa ({self.chamberPressure / PA_PER_PSIA:.1f} psia)'],
            ['Propellant inlet temp',    f'{self.inletTemperature:.2f} K'],
            ['Ammonia dissociation X',   f'{self.ammoniaDissociation:.4f}'],
            ['Chamber temperature',      f'{self.chamberTemperature:.1f} K'],
            ['Product molar mass',       f'{self.productMolarMass * 1.0e3:.3f} g/mol'],
            ['Specific gas constant',    f'{self.specificGasConstant:.2f} J/kg-K'],
            ['Specific heat ratio',      f'{self.specificHeatRatio:.4f}'],
            ['Characteristic velocity',  f'{self.characteristicVelocity:.2f} m/s'],
            ['Bed loading',              f'{self.actualBedLoading:.3f} kg/m^2-s ({self.actualBedLoading * M_PER_IN**2 / KG_PER_LBM:.4f} lbm/in^2-s)'],
            ['Bed frontal area',         f'{self.bedArea * 1.0e4:.4f} cm^2'],
            ['Bed diameter',             f'{self.bedDiameter * 1.0e3:.3f} mm'],
            ['Bed length',               f'{self.bedLength * 1.0e3:.3f} mm'],
            ['Bed L/D',                  f'{self.bedLength / self.bedDiameter:.3f}'],
            ['Bed volume',               f'{self.bedVolume * 1.0e6:.3f} cm^3'],
            ['Catalyst mass',            f'{self.catalystMass * 1.0e3:.2f} g'],
            ['Void fraction',            f'{self._voidFraction():.4f}']
        ]

        if not np.isnan(self.productMoles.get('total', np.nan)):
            rows.append(['Products per mol N2H4',
                         f'{self.productMoles["NH3"]:.4f} NH3 + {self.productMoles["N2"]:.4f} N2 + {self.productMoles["H2"]:.4f} H2'])

        if not np.isnan(self.pressureDrop):
            rows.append(['Superficial velocity', f'{self.superficialVelocity:.2f} m/s'])
            rows.append(['Bed pressure drop',    f'{self.pressureDrop / 1.0e3:.2f} kPa '
                                                 f'({self.pressureDrop / self.chamberPressure * 100.0:.1f} % of Pc)'])
        if not np.isnan(self.residenceTime):
            rows.append(['Gas residence time',  f'{self.residenceTime * 1.0e3:.4f} ms'])
        if not np.isnan(self.ignitionDelay):
            rows.append(['Bed temperature',     f'{self.bedTemperature:.1f} K'])
            rows.append(['Ignition delay est.', f'{self.ignitionDelay * 1.0e3:.2f} ms'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'CATALYST BED REPORT')

        report += f'\n\nCATALYST\n{"-" * 60}\n{catalystData["description"]}\n{catalystData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'catalystBedReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.catalyst.strip().lower() not in CATALYSTS:
            raise InvalidInputError(
                message       = f'Unknown catalyst \'{self.catalyst}\'.',
                parameterName = 'catalyst', value = self.catalyst,
                validRange    = str(sorted(CATALYSTS.keys()))
            )

        if self.meshSize.strip() not in MESH_SIZES:
            raise InvalidInputError(
                message       = f'Unknown granule mesh size \'{self.meshSize}\'.',
                parameterName = 'meshSize', value = self.meshSize,
                validRange    = str(sorted(MESH_SIZES.keys()))
            )

        if self.massFlow <= 0.0:
            raise InvalidInputError(
                message       = 'Catalyst bed mass flow must be positive.',
                parameterName = 'massFlow', value = self.massFlow, validRange = 'Greater than 0 kg/s'
            )

        if not 0.0 <= self.ammoniaDissociation <= 1.0:
            raise InvalidInputError(
                message       = 'Ammonia dissociation fraction must lie between 0 and 1.',
                parameterName = 'ammoniaDissociation', value = self.ammoniaDissociation,
                validRange    = '0 to 1'
            )

        if self.inletTemperature < 274.69:
            self.designNotes.append(
                f'Propellant inlet temperature {self.inletTemperature:.2f} K is below the 274.69 K hydrazine '
                f'freezing point. Line and tank heaters exist to prevent exactly this.')

    def _voidFraction(self) -> float:

        '''

        Interparticle void fraction, from the override or the catalyst default.

        '''

        if not np.isnan(self.voidFraction):
            return self.voidFraction

        return CATALYSTS[self.catalyst.strip().lower()]['voidFraction']

    def _particleDiameter(self) -> float:

        '''

        Mean granule diameter from the mesh size range.

        '''

        upper, lower = MESH_SIZES[self.meshSize.strip()]

        return 0.5 * (upper + lower)
