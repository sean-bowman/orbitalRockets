
# -- HeatTreatment Class Definition -- #

'''

Quench factor analysis, aging equivalence, sensitization, HIP cycles and the distortion released
when a residually stressed part is machined asymmetrically.

Heat treatment is not a schedule to be looked up. It is a set of competing rate processes, and the
useful questions are quantitative: how much strength does a slow quench cost, are these two aging
cycles equivalent, how long can this weld sit in the sensitization range, and how far will the part
bow when half the plate is machined away.

Four calculations carry the class.

    Quench factor    Staley's integral over the cooling curve against the C-curve of the alloy.
                     Predicts the retained strength directly, and explains why a 100 mm 7075
                     forging cannot be through-hardened while a 10 mm plate can.

    Aging            The Larson-Miller form P = T (C + log10 t) makes time and temperature
                     interchangeable, so a 24 hour cycle at 120 C and a 6 hour cycle at 140 C can be
                     shown equivalent, and over-aging can be predicted rather than discovered.

    Sensitization    The time-temperature-sensitization curve turns the 316 versus 316L argument
                     into a number. 316 at 0.08 carbon sensitizes in minutes at 675 C; 316L at 0.03
                     takes hours. That is the whole reason the L grades exist.

    Distortion       Quench residual stress, and the bow released when it is machined off one side.
                     This is the number that ruins a machined 7075 plate part, and it is the direct
                     link between heat treatment and machining.

HIP lives here rather than in postProcessing, because it is a thermal cycle at pressure and it
belongs with solution treatment and aging rather than with surface work.

See Also:
---------
MaterialDatabase  : Supplies the quench factor constants and the sensitization data
Allowables        : Consumes the quench knockdown as a link in the chain
machiningProcesses/MachiningProcess : Consumes the residual stress that drives distortion

Theory: docs/HeatTreatment.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import applyInputs, formatReportTable, InvalidInputError, createErrorContext
    from MaterialDatabase import queryMaterial
except ImportError:
    from .utils import applyInputs, formatReportTable, InvalidInputError, createErrorContext
    from .MaterialDatabase import queryMaterial

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

UNIVERSAL_GAS_CONSTANT = 8.3145        # [J/mol-K]

# Grossmann quench severity H = h / k, the ratio of the surface heat transfer coefficient to the
# thermal conductivity of the part, so it is a property of the quenchant and the agitation rather
# than of the alloy.
#
# UNITS. Grossmann H is almost universally tabulated in inverse INCHES, and the familiar values
# (still oil 0.25, still water 1.0, agitated water 1.5) are those. Everything in this repository is
# base SI, so the values below are inverse metres: the tabulated number multiplied by 39.37.
# Using the inverse-inch numbers directly gives a Biot number two orders of magnitude too small,
# which reports every quench as perfectly uniform and every part as fully hardened.

QUENCH_SEVERITY = {
    'still air':          0.8,     # [1/m], 0.02 1/in. Effectively no quench.
    'forced air':         2.0,     # [1/m], 0.05 1/in
    'still oil':          10.0,    # [1/m], 0.25 1/in
    'agitated oil':       18.0,    # [1/m], 0.45 1/in
    'polymer 25 percent': 28.0,    # [1/m], 0.70 1/in
    'still water':        40.0,    # [1/m], 1.00 1/in
    'agitated water':     60.0,    # [1/m], 1.50 1/in
    'agitated brine':     80.0,    # [1/m], 2.00 1/in
    'ideal':              np.inf   # [1/m], the theoretical limit
}

# Larson-Miller constant for the aging response of precipitation hardening alloys. C is close to 20
# for most systems and the parameter is P = T (C + log10 t) with T in kelvin and t in hours.

LARSON_MILLER_CONSTANT = 20.0

# Sensitization. The time-temperature-sensitization nose for austenitic stainless, as a function of
# carbon content. Chromium carbide precipitation at the grain boundaries depletes the adjacent
# chromium below the 12 percent needed for passivity, and the alloy then corrodes intergranularly.
#
# The carbon exponent is steep, which is the entire justification for the L grades.

SENSITIZATION_REFERENCE_CARBON = 0.08     # [-], the standard grade
SENSITIZATION_CARBON_EXPONENT  = 2.5      # [-], empirical, time scales as (Cref/C)^n
SENSITIZATION_ACTIVATION       = 180000.0  # [J/mol], chromium diffusion in austenite

# HIP cycles by alloy family. Pressure closes internal porosity by creep; temperature has to be high
# enough for creep to be fast and low enough not to coarsen the microstructure.

HIP_CYCLES = {
    'nickel precipitation hardening': {'temperature': 1436.0, 'pressure': 100.0e6, 'time': 14400.0,
                                       'note': 'Above the gamma prime solvus, so a solution treat '
                                               'and age must follow'},
    'nickel solid solution':          {'temperature': 1393.0, 'pressure': 100.0e6, 'time': 14400.0,
                                       'note': 'No aging response to recover'},
    'titanium alpha-beta':            {'temperature': 1193.0, 'pressure': 100.0e6, 'time': 7200.0,
                                       'note': 'Below the beta transus, or the alpha morphology '
                                               'coarsens and toughness falls'},
    'aluminium casting alloy, additive': {'temperature': 793.0, 'pressure': 100.0e6, 'time': 7200.0,
                                          'note': 'Coarsens the fine silicon network and costs '
                                                  'strength; use only when porosity governs'},
    'copper dispersion strengthened': {'temperature': 1323.0, 'pressure': 100.0e6, 'time': 10800.0,
                                       'note': 'Cr2Nb dispersoids are stable, so there is no '
                                               'coarsening penalty'},
    'stainless austenitic':           {'temperature': 1393.0, 'pressure': 100.0e6, 'time': 14400.0,
                                       'note': 'Follow with a solution anneal to redissolve any '
                                               'carbides formed during the slow cool'}
}

# Residual stress from quenching. The coefficient converts the through-thickness temperature
# gradient into a surface residual stress; it is empirical and sits near 0.3 for a fully constrained
# quench of a thick section.

QUENCH_STRESS_COEFFICIENT = 0.30     # [-]

# ------------------------------------------------------------------------------------------------ #

class HeatTreatment:

    '''

    Predict the property outcome of a thermal history rather than look up a schedule.

    Primary Input Properties:
    -------------------------
    material / condition : str, str
        Passed to the database for the quench factor constants and sensitization data
    sectionThickness : float
        [m], the dimension that governs the cooling rate
    quenchant : str
        Key into QUENCH_SEVERITY
    coolingCurve : tuple
        (time [s], temperature [K]) arrays. Overrides the modelled curve when supplied.
    agingTemperature / agingTime : float, float
        [K] and [s]

    Key Output Properties:
    ----------------------
    quenchFactor : float
        The Staley integral. Larger means slower quench and more strength lost.
    retainedStrengthFraction : float
        Yield strength as a fraction of the ideally quenched value
    residualStress : float
        [Pa] surface residual stress from the quench
    predictedBow : float
        [m] released by asymmetric machining

    Public Methods:
    ---------------
    setInputs(inputs)               Load a configuration dictionary
    modelCoolingCurve()             Lumped capacitance cooling from thickness and quench severity
    calculateQuenchFactor()         Staley integral and the retained strength
    calculateAgingResponse()        Larson-Miller equivalence and over-aging
    calculateSensitization()        Time to sensitize at temperature, by carbon content
    calculateHipCycle()             The cycle for this alloy family and what must follow it
    calculateDistortion()           Quench residual stress and the bow on asymmetric machining
    generateReport(outputDir)       Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material and Geometry -- #

        self.material          = '7075'        # [case insensitive string]
        self.condition         = 't73'         # [case insensitive string]
        self.sectionThickness  = 0.025         # [m], governs the cooling rate
        self.partLength        = 0.500         # [m], for the distortion calculation
        self.partWidth         = 0.200         # [m]

        # -- Quench -- #

        self.solutionTemperature = 738.0       # [K], typical 7xxx solution treat
        self.quenchTemperature   = 293.15      # [K], the quenchant bulk temperature
        self.quenchant           = 'agitated water'  # [case insensitive string]
        self.coolingCurve        = None        # [tuple of arrays], overrides the model

        # -- Age -- #

        self.agingTemperature  = 393.0         # [K]
        self.agingTime         = 86400.0       # [s]

        # -- Machining, for the distortion release -- #

        self.machinedFraction  = 0.50          # [-], fraction of the thickness removed from one side

        # -- Results -- #

        self.quenchFactor      = np.nan        # [-]
        self.retainedStrengthFraction = np.nan  # [-]
        self.coolingRate       = np.nan        # [K/s], averaged over the critical range
        self.biotNumber        = np.nan        # [-]
        self.larsonMillerParameter = np.nan    # [-]
        self.residualStress    = np.nan        # [Pa]
        self.predictedBow      = np.nan        # [m]
        self.heatTreatNotes    = []            # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material.

        '''

        requiredParams = {
            'material': 'Material not provided.'
        }

        optionalParams = ['condition', 'sectionThickness', 'partLength', 'partWidth',
                          'solutionTemperature', 'quenchTemperature', 'quenchant', 'coolingCurve',
                          'agingTemperature', 'agingTime', 'machinedFraction']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def modelCoolingCurve(self, points: int = 400) -> dict:

        '''

        Lumped capacitance cooling from the section thickness and the quench severity.

            dT/dt = -h A (T - T_quench) / (rho c V)      with  h = H k

        The Biot number is reported alongside, because lumped capacitance only holds below about
        0.1 and a thick section quenched in agitated water is well above that. Above 0.1 the surface
        cools far faster than the core, the model understates the gradient, and the real part
        develops a residual stress the model cannot see.

        '''

        properties = queryMaterial(self.material, self.condition, self.solutionTemperature)

        density      = properties['density']
        conductivity = properties.get('thermalConductivity', 150.0)
        specificHeat = properties.get('specificHeat', 900.0)

        severity     = QUENCH_SEVERITY[self.quenchant]
        halfSection  = self.sectionThickness / 2.0

        if np.isinf(severity):
            heatTransfer = 1.0e9
        else:
            heatTransfer = severity * conductivity

        self.biotNumber = heatTransfer * halfSection / conductivity

        timeConstant = density * specificHeat * halfSection / heatTransfer

        duration = 8.0 * timeConstant
        times    = np.linspace(0.0, duration, points)
        temperatures = self.quenchTemperature + \
                       (self.solutionTemperature - self.quenchTemperature) * \
                       np.exp(-times / timeConstant)

        self.coolingCurve = (times, temperatures)

        # Average rate through the critical range, conventionally 400 to 290 degC for 7xxx
        upper, lower = 673.0, 563.0
        inRange = (temperatures <= upper) & (temperatures >= lower)
        if np.any(inRange):
            rangeTimes = times[inRange]
            self.coolingRate = (upper - lower) / max(rangeTimes[-1] - rangeTimes[0], 1.0e-9)

        if self.biotNumber > 0.1:
            self.heatTreatNotes.append(
                f'The Biot number is {self.biotNumber:.2f}, above the 0.1 where lumped capacitance '
                f'holds. The surface cools much faster than the core, so this curve understates the '
                f'through-thickness gradient and therefore both the residual stress and the '
                f'variation in properties from surface to centre.')

        return {'timeConstant': timeConstant, 'biotNumber': self.biotNumber,
                'heatTransferCoefficient': heatTransfer,
                'averageCoolingRate': self.coolingRate,
                'time': times, 'temperature': temperatures}

    def calculateQuenchFactor(self) -> dict:

        '''

        Staley quench factor analysis.

            C_T = -k1 k2 exp( k3 k4^2 / (R T (k4 - T)^2) ) exp( k5 / (R T) )
            Q   = integral dt / C_T(T)
            sigma / sigma_max = exp(k1 Q)

        C_T is the time to reach a defined fraction of transformation at temperature, so it is the
        C-curve of the alloy. The integral accumulates the fraction of available transformation
        consumed on the way down, and the retained strength follows.

        This is the calculation that says how much a slow quench costs, and it is why a thick
        section cannot be through-hardened: the core simply cannot be cooled fast enough to outrun
        the nose of the C-curve.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)
        constants  = properties.get('quenchFactor')

        if constants is None:
            raise InvalidInputError(
                message       = f'No quench factor constants for {self.material} in the '
                                f'{self.condition} condition. Quench factor analysis is calibrated '
                                f'per alloy and the constants cannot be assumed.',
                parameterName = 'material', value = self.material,
                validRange    = 'An alloy with a quenchFactor block in materialData.py'
            )

        if self.coolingCurve is None:
            self.modelCoolingCurve()

        times, temperatures = self.coolingCurve

        k1, k2, k3, k4, k5 = (constants['k1'], constants['k2'], constants['k3'],
                              constants['k4'], constants['k5'])

        # Only the temperature range where transformation is kinetically possible contributes.
        active = (temperatures > self.quenchTemperature + 20.0) & (temperatures < k4 - 1.0)

        if not np.any(active):
            self.quenchFactor = 0.0
            self.retainedStrengthFraction = 1.0
            return {'quenchFactor': 0.0, 'retainedStrengthFraction': 1.0,
                    'note': 'The cooling curve does not pass through the transformation range.'}

        activeTimes        = times[active]
        activeTemperatures = temperatures[active]

        exponentOne = k3 * k4 ** 2 / (UNIVERSAL_GAS_CONSTANT * activeTemperatures *
                                      (k4 - activeTemperatures) ** 2)
        exponentTwo = k5 / (UNIVERSAL_GAS_CONSTANT * activeTemperatures)

        criticalTime = -k1 * k2 * np.exp(exponentOne) * np.exp(exponentTwo)
        criticalTime = np.abs(criticalTime)

        integrand = 1.0 / np.maximum(criticalTime, 1.0e-30)

        self.quenchFactor = float(np.trapezoid(integrand, activeTimes)) \
                            if hasattr(np, 'trapezoid') else float(np.trapz(integrand, activeTimes))

        self.retainedStrengthFraction = float(np.exp(k1 * self.quenchFactor))
        self.retainedStrengthFraction = min(1.0, max(0.0, self.retainedStrengthFraction))

        loss = 1.0 - self.retainedStrengthFraction

        if loss > 0.05:
            self.heatTreatNotes.append(
                f'The quench costs {loss * 100.0:.1f} percent of the achievable yield strength at '
                f'a {self.sectionThickness * 1000.0:.0f} mm section in {self.quenchant}. That is a '
                f'knockdown that belongs in the Allowables chain, not a rounding error.')

        if loss > 0.15:
            self.heatTreatNotes.append(
                f'A loss above 15 percent means this section cannot be through-hardened in this '
                f'quenchant. Either the section has to come down, the quench has to be more '
                f'severe (at the cost of distortion and cracking risk), or a more hardenable alloy '
                f'is needed. 7050 exists precisely for this case.')

        return {'quenchFactor': self.quenchFactor,
                'retainedStrengthFraction': self.retainedStrengthFraction,
                'strengthLoss': loss,
                'sectionThickness': self.sectionThickness, 'quenchant': self.quenchant,
                'averageCoolingRate': self.coolingRate,
                'retainedYieldStrength': properties['yieldStrength'] * self.retainedStrengthFraction}

    def calculateAgingResponse(self, comparisonTemperature: float = None,
                               comparisonTime: float = None) -> dict:

        '''

        Larson-Miller aging equivalence.

            P = T (C + log10 t)          T in kelvin, t in hours, C about 20

        Two cycles with the same parameter produce the same degree of precipitation. That makes time
        and temperature interchangeable within limits, which is how a 24 hour age gets compressed
        into 6 hours, and how over-aging is predicted rather than discovered on a hardness check.

        The limit is that the mechanism has to stay the same. Pushing the temperature far enough to
        cross a solvus or start a different precipitate does not accelerate the same process, it
        substitutes another one.

        '''

        timeHours = self.agingTime / 3600.0

        self.larsonMillerParameter = self.agingTemperature * \
                                     (LARSON_MILLER_CONSTANT + np.log10(max(timeHours, 1.0e-6)))

        result = {'agingTemperature': self.agingTemperature, 'agingTime': self.agingTime,
                  'agingTimeHours': timeHours,
                  'larsonMillerParameter': self.larsonMillerParameter,
                  'constant': LARSON_MILLER_CONSTANT}

        if comparisonTemperature is not None:
            # Solve for the time that gives the same parameter at the comparison temperature
            exponent = self.larsonMillerParameter / comparisonTemperature - LARSON_MILLER_CONSTANT
            equivalentHours = 10.0 ** exponent
            result['comparisonTemperature'] = comparisonTemperature
            result['equivalentTimeHours']   = equivalentHours
            result['equivalentTime']        = equivalentHours * 3600.0
            result['timeRatio']             = equivalentHours / timeHours

            self.heatTreatNotes.append(
                f'{timeHours:.1f} h at {self.agingTemperature - 273.15:.0f} degC is equivalent to '
                f'{equivalentHours:.2f} h at {comparisonTemperature - 273.15:.0f} degC on the '
                f'Larson-Miller parameter. The equivalence holds only while the same precipitate is '
                f'forming; check that the higher temperature has not crossed a solvus.')

        if comparisonTime is not None:
            exponent = np.log10(max(comparisonTime / 3600.0, 1.0e-6))
            equivalentTemperature = self.larsonMillerParameter / (LARSON_MILLER_CONSTANT + exponent)
            result['comparisonTime'] = comparisonTime
            result['equivalentTemperature'] = equivalentTemperature

        return result

    def calculateSensitization(self, exposureTemperature: float = None,
                               exposureTime: float = None) -> dict:

        '''

        Time to sensitize an austenitic stainless at temperature, as a function of carbon content.

        Chromium carbide precipitates at the grain boundaries and depletes the adjacent chromium
        below the roughly 12 percent needed for passivity. The alloy then corrodes intergranularly
        and the damage is not visible.

        The time to the nose scales steeply with carbon:

            t = t_reference (C_reference / C)^n exp( Q / R (1/T - 1/T_nose) )

        which turns the 316 versus 316L argument into a number rather than a preference. The
        standard grade at 0.08 carbon sensitizes in minutes at the nose; the L grade at 0.03 takes
        hours, and that is the difference between a weld that is at risk and one that is not.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)
        data       = properties.get('sensitization')

        if data is None:
            return {'applicable': False, 'material': properties['commonName'],
                    'note': f'{properties["commonName"]} is not an austenitic stainless and does '
                            f'not sensitize by this mechanism.'}

        carbonContent  = data['carbonContent']
        noseTemperature = data['noseTemperature']
        noseTime        = data['noseTimeSeconds']

        if exposureTemperature is None:
            exposureTemperature = noseTemperature

        carbonFactor = (SENSITIZATION_REFERENCE_CARBON / carbonContent) ** \
                       SENSITIZATION_CARBON_EXPONENT

        arrheniusFactor = np.exp(SENSITIZATION_ACTIVATION / UNIVERSAL_GAS_CONSTANT *
                                 (1.0 / exposureTemperature - 1.0 / noseTemperature))

        timeToSensitize = noseTime * arrheniusFactor

        # Reference time for the 0.08 carbon standard grade, for the comparison that matters
        standardGradeTime = timeToSensitize / carbonFactor

        result = {'applicable': True, 'material': properties['commonName'],
                  'carbonContent': carbonContent,
                  'noseTemperature': noseTemperature,
                  'exposureTemperature': exposureTemperature,
                  'timeToSensitize': timeToSensitize,
                  'timeToSensitizeMinutes': timeToSensitize / 60.0,
                  'standardGradeTime': standardGradeTime,
                  'standardGradeMinutes': standardGradeTime / 60.0,
                  'carbonAdvantage': carbonFactor}

        if exposureTime is not None:
            result['exposureTime'] = exposureTime
            result['sensitized']   = exposureTime > timeToSensitize
            result['exposureFraction'] = exposureTime / timeToSensitize

            if result['sensitized']:
                self.heatTreatNotes.append(
                    f'An exposure of {exposureTime / 60.0:.1f} minutes at '
                    f'{exposureTemperature - 273.15:.0f} degC exceeds the '
                    f'{timeToSensitize / 60.0:.1f} minutes to sensitize {properties["commonName"]}. '
                    f'The grain boundaries are chromium depleted and the part will corrode '
                    f'intergranularly. A solution anneal is the only recovery.')

        if carbonContent <= 0.035:
            self.heatTreatNotes.append(
                f'At {carbonContent:.3f} percent carbon this grade tolerates '
                f'{carbonFactor:.1f} times the time at temperature that the 0.08 carbon standard '
                f'grade would. That factor is the whole reason the L grades exist and it is why a '
                f'welded fluid system is built from 316L rather than 316.')

        return result

    def calculateHipCycle(self) -> dict:

        '''

        The hot isostatic pressing cycle for this alloy family, and what has to follow it.

        HIP closes internal porosity by creep under pressure. It lives in this class rather than in
        postProcessing because it is a thermal cycle at pressure and it interacts with the solution
        and aging treatments directly: HIP of a precipitation hardened nickel alloy runs above the
        gamma prime solvus, so it dissolves the strengthening precipitate and a full solution treat
        and age has to follow or the part is left soft.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)
        family     = properties['family']

        cycle = None
        for familyKey, definition in HIP_CYCLES.items():
            if familyKey in family:
                cycle = definition
                break

        if cycle is None:
            return {'applicable': False, 'family': family,
                    'note': f'No HIP cycle is tabulated for the {family} family. HIP is not '
                            f'universally beneficial and applying it without a qualified cycle can '
                            f'coarsen the microstructure and lose more than the porosity was '
                            f'costing.'}

        result = {'applicable': True, 'family': family,
                  'temperature': cycle['temperature'], 'pressure': cycle['pressure'],
                  'time': cycle['time'], 'note': cycle['note']}

        transus = properties.get('betaTransus')
        if transus is not None and cycle['temperature'] > transus:
            self.heatTreatNotes.append(
                f'The HIP temperature of {cycle["temperature"] - 273.15:.0f} degC is above the beta '
                f'transus of {transus - 273.15:.0f} degC. The alpha morphology will coarsen into a '
                f'lamellar structure and the fatigue strength will fall substantially. Lower the '
                f'cycle or accept the change deliberately.')

        result['requiresPostHeatTreatment'] = 'solution' in cycle['note'].lower() or \
                                              'age' in cycle['note'].lower()

        if result['requiresPostHeatTreatment']:
            self.heatTreatNotes.append(
                f'This HIP cycle requires a subsequent heat treatment: {cycle["note"]}. A part '
                f'HIPed and not re-treated is in an unknown condition and none of the allowables '
                f'in the database apply to it.')

        return result

    def calculateDistortion(self) -> dict:

        '''

        Quench residual stress, and the bow released when the part is machined asymmetrically.

            sigma_residual = beta E alpha dT_gradient / (1 - nu)

        A quenched plate carries compression at the surface and tension in the core, balanced. Machine
        one side away and the balance is destroyed: the remaining section carries an unbalanced
        moment and the part bows.

            M = sigma_residual * A_removed * armLength
            delta = M L^2 / (8 E I)

        This is the number that ruins a machined 7075 plate part, and it is why thick machined
        aluminium parts are stress relieved by stretching (the T351 and T7451 tempers) rather than
        merely solution treated and aged.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)

        modulus   = properties['elasticModulus']
        expansion = properties.get('thermalExpansion', 23.0e-6)
        poisson   = properties['poissonRatio']

        if self.coolingCurve is None:
            self.modelCoolingCurve()

        # The through-thickness gradient scales with the Biot number: a low Biot number quench is
        # uniform and generates little stress.
        gradientFraction = min(1.0, self.biotNumber / (1.0 + self.biotNumber))
        temperatureGradient = (self.solutionTemperature - self.quenchTemperature) * gradientFraction

        self.residualStress = QUENCH_STRESS_COEFFICIENT * modulus * expansion * \
                              temperatureGradient / (1.0 - poisson)

        yieldStrength = properties['yieldStrength']
        capped = False
        if self.residualStress > yieldStrength:
            self.residualStress = yieldStrength
            capped = True

        # -- The bow released by asymmetric machining -- #
        #
        # The residual stress from a quench is SELF-EQUILIBRATING through the thickness: compression
        # at both surfaces balanced by tension in the core, with zero net force and zero net moment.
        # That is what allows the plate to sit flat in the first place.
        #
        # Treating the removed layer as carrying a uniform stress and multiplying by an arm length
        # overstates the released moment by roughly a factor of four, because it ignores that the
        # removed layer contains both the compressive surface and part of the tensile core. The
        # profile has to be integrated.
        #
        # A parabolic profile is the standard idealisation and it satisfies both equilibrium
        # conditions exactly:
        #
        #     sigma(z) = sigma_surface (3 (2z/t)^2 - 1) / 2      z from -t/2 to +t/2
        #
        # giving sigma_surface at both faces and -sigma_surface/2 at the mid-plane.

        removedThickness   = self.sectionThickness * self.machinedFraction
        remainingThickness = self.sectionThickness - removedThickness

        if remainingThickness <= 0.0:
            raise InvalidInputError(
                message       = 'The machined fraction removes the whole section.',
                parameterName = 'machinedFraction', value = self.machinedFraction,
                validRange    = 'Less than 1.0'
            )

        thickness = self.sectionThickness

        def stressProfile(position: np.ndarray) -> np.ndarray:
            '''Self-equilibrating parabolic residual stress through the thickness.'''
            return self.residualStress * (3.0 * (2.0 * position / thickness) ** 2 - 1.0) / 2.0

        # Material is removed from the top face downward, so the remainder runs from -t/2 to
        # t/2 - removed.
        upperLimit = thickness / 2.0 - removedThickness
        lowerLimit = -thickness / 2.0

        positions = np.linspace(lowerLimit, upperLimit, 2001)
        stresses  = stressProfile(positions)

        integrate = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz

        # The remaining section is no longer in equilibrium with itself. The unbalanced force and
        # the unbalanced moment about the NEW centroid are what the part relieves by straining and
        # curving.
        centroid = (lowerLimit + upperLimit) / 2.0

        netForce  = self.partWidth * float(integrate(stresses, positions))
        netMoment = self.partWidth * float(integrate(stresses * (positions - centroid), positions))

        secondMoment = self.partWidth * remainingThickness ** 3 / 12.0

        curvature         = netMoment / (modulus * secondMoment)
        self.predictedBow = abs(curvature) * self.partLength ** 2 / 8.0

        result = {'residualStress': self.residualStress, 'yieldCapped': capped,
                  'temperatureGradient': temperatureGradient,
                  'biotNumber': self.biotNumber,
                  'removedThickness': removedThickness,
                  'remainingThickness': remainingThickness,
                  'surfaceStress': self.residualStress,
                  'midPlaneStress': -self.residualStress / 2.0,
                  'unbalancedForce': netForce,
                  'unbalancedMoment': netMoment, 'secondMomentOfArea': secondMoment,
                  'curvature': curvature,
                  'predictedBow': self.predictedBow,
                  'bowPerMetre': self.predictedBow / self.partLength}

        if capped:
            self.heatTreatNotes.append(
                'The computed quench residual stress exceeds the yield strength, so it was capped '
                'at yield. The part yields locally during the quench, which relieves some stress '
                'and is also how quench cracking starts in a thick section.')

        if self.predictedBow > 0.001:
            self.heatTreatNotes.append(
                f'The predicted bow of {self.predictedBow * 1000.0:.2f} mm over a '
                f'{self.partLength * 1000.0:.0f} mm part is a real machining problem. The fixes are '
                f'a stress relieved temper (T351 or T7451 rather than T6), symmetric machining in '
                f'alternating passes, or a stress relief between roughing and finishing.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)

        rows = [
            ['Material',           f'{properties["commonName"]} ({self.condition})'],
            ['Section thickness',  f'{self.sectionThickness * 1000.0:.1f} mm'],
            ['Quenchant',          f'{self.quenchant} (H = {QUENCH_SEVERITY[self.quenchant]:.3f} 1/m)'],
            ['Solution temperature', f'{self.solutionTemperature - 273.15:.0f} degC']
        ]

        if not np.isnan(self.biotNumber):
            rows.append(['Biot number', f'{self.biotNumber:.2f}'])
        if not np.isnan(self.coolingRate):
            rows.append(['Average cooling rate', f'{self.coolingRate:.2f} K/s through 400-290 degC'])
        if not np.isnan(self.quenchFactor):
            rows.append(['Quench factor', f'{self.quenchFactor:.4f}'])
            rows.append(['Retained strength',
                         f'{self.retainedStrengthFraction * 100.0:.1f} % of the ideal quench'])
        if not np.isnan(self.larsonMillerParameter):
            rows.append(['Aging cycle',
                         f'{self.agingTime / 3600.0:.1f} h at '
                         f'{self.agingTemperature - 273.15:.0f} degC'])
            rows.append(['Larson-Miller parameter', f'{self.larsonMillerParameter:.0f}'])
        if not np.isnan(self.residualStress):
            rows.append(['Quench residual stress', f'{self.residualStress / 1.0e6:.1f} MPa'])
            rows.append(['Predicted bow',
                         f'{self.predictedBow * 1000.0:.3f} mm over '
                         f'{self.partLength * 1000.0:.0f} mm'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'HEAT TREATMENT')

        for note in self.heatTreatNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'heatTreatment.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.quenchant not in QUENCH_SEVERITY:
            raise InvalidInputError(
                message       = f'Unknown quenchant \'{self.quenchant}\'.',
                parameterName = 'quenchant', value = self.quenchant,
                validRange    = str(sorted(QUENCH_SEVERITY.keys()))
            )

        if self.sectionThickness <= 0.0:
            raise InvalidInputError(
                message       = 'Section thickness must be positive.',
                parameterName = 'sectionThickness', value = self.sectionThickness,
                validRange    = 'Greater than 0 m'
            )

        if not 0.0 <= self.machinedFraction < 1.0:
            raise InvalidInputError(
                message       = 'machinedFraction is the fraction of the section removed from one '
                                'side and must lie in [0, 1).',
                parameterName = 'machinedFraction', value = self.machinedFraction,
                validRange    = '[0, 1)'
            )

        if self.solutionTemperature <= self.quenchTemperature:
            raise InvalidInputError(
                message       = 'The solution temperature must exceed the quenchant temperature.',
                parameterName = 'solutionTemperature', value = self.solutionTemperature,
                validRange    = 'Greater than quenchTemperature'
            )
