
# -- Insulation Class Definition -- #

'''

Thermal insulation sizing: heat leak, boil-off, surface temperature and condensation.

Insulation on a fluid system does one of three jobs, and which one it is determines how it is sized:

1. **Limit heat leak into a cryogen**, so the propellant does not boil off during hold and so the
   tank does not have to be vented. Sized on the heat rate.
2. **Keep a surface above the dew point**, so a cold line does not condense water or, worse, liquid
   air. Sized on the outer surface temperature.
3. **Keep a surface below a touch limit or a structural limit**, on a hot gas line. Also sized on
   the outer surface temperature.

Those are different constraints and they can give different thicknesses, so the class evaluates all
of them.

The physics is a one-dimensional resistance network: conduction through the insulation in series
with convection and radiation at the outer surface. The complication in cryogenic work is that the
best insulations are not conduction-limited at all. Multilayer insulation works by suppressing
radiation between many reflective layers in a vacuum, and its effective conductivity depends on
layer density and on interstitial gas pressure far more than on any material property.

The other thing this class checks, and which gets missed, is **liquid air condensation**. A surface
below 90 K exposed to air condenses oxygen-enriched liquid air. That liquid drips onto whatever is
below it, and if what is below it is an organic material, an asphalt pad, or a piece of insulation,
it is now an impact-sensitive explosive.

See Also:
---------
Line             : The pipe the insulation goes on
CryogenicSystems : Chilldown, two-phase flow and the operational side of cryogenic heat leak
Pressurization   : Boil-off feeding tank pressure

Theory: docs/Insulation.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                       STEFAN_BOLTZMANN, GRAVITY, SECONDS_PER_YEAR,
                       InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                        STEFAN_BOLTZMANN, GRAVITY, SECONDS_PER_YEAR,
                        InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Insulation materials.
#
#   conductivity     effective thermal conductivity [W/m-K] at the stated mean temperature
#   density          [kg/m^3]
#   minimumTemperature / maximumTemperature   service range [K]
#   requiresVacuum   whether the quoted conductivity assumes an evacuated jacket
#   emissivity       outer surface emissivity for the radiation boundary
#
# The spread from polyurethane foam to good MLI is a factor of 700 in conductivity, and the entire
# difference is that MLI works in a vacuum and foam does not. That is the central trade in cryogenic
# insulation: a vacuum jacket is heavy, expensive and can fail, and nothing else comes close to it.
INSULATION_MATERIALS = {
    'polyurethane foam': {
        'conductivity': 0.026, 'density': 35.0, 'minimumTemperature': 20.0,
        'maximumTemperature': 400.0, 'requiresVacuum': False, 'emissivity': 0.90,
        'notes': 'Sprayed-on foam insulation (SOFI). The Shuttle external tank standard. Cheap, light, '
                 'applied in place, and it must be closed-cell and sealed or it takes on moisture and '
                 'cryopumps air, at which point its conductivity collapses.'
    },
    'polyisocyanurate': {
        'conductivity': 0.023, 'density': 40.0, 'minimumTemperature': 20.0,
        'maximumTemperature': 420.0, 'requiresVacuum': False, 'emissivity': 0.90,
        'notes': 'Rigid board foam. Better than polyurethane at cryogenic temperature and dimensionally '
                 'more stable.'
    },
    'aerogel blanket': {
        'conductivity': 0.014, 'density': 150.0, 'minimumTemperature': 4.0,
        'maximumTemperature': 920.0, 'requiresVacuum': False, 'emissivity': 0.85,
        'notes': 'Silica aerogel in a fiber batting. The best non-vacuum insulation available and usable '
                 'over an enormous temperature range. Expensive, dusty to install, and compresses under '
                 'load, which raises its conductivity.'
    },
    'mineral wool': {
        'conductivity': 0.040, 'density': 100.0, 'minimumTemperature': 200.0,
        'maximumTemperature': 920.0, 'requiresVacuum': False, 'emissivity': 0.90,
        'notes': 'Hot service standard. Not for cryogenic use: it is open cell and it will hold condensed '
                 'moisture, then ice.'
    },
    'ceramic fiber': {
        'conductivity': 0.10, 'density': 128.0, 'minimumTemperature': 290.0,
        'maximumTemperature': 1600.0, 'requiresVacuum': False, 'emissivity': 0.90,
        'notes': 'Hot gas and exhaust duct insulation. The conductivity rises steeply with temperature '
                 'because radiation through the fiber matrix takes over.'
    },
    'perlite': {
        'conductivity': 0.0009, 'density': 130.0, 'minimumTemperature': 4.0,
        'maximumTemperature': 1000.0, 'requiresVacuum': True, 'emissivity': 0.90,
        'notes': 'Evacuated expanded perlite powder in an annulus. The standard for large cryogenic storage '
                 'tanks: it fills any shape, it is cheap by volume, and it settles over time, which opens '
                 'voids at the top of a vertical annulus.'
    },
    'mli 20 layer': {
        'conductivity': 5.0e-5, 'density': 60.0, 'minimumTemperature': 4.0,
        'maximumTemperature': 400.0, 'requiresVacuum': True, 'emissivity': 0.05,
        'notes': 'Multilayer insulation, 20 layers of aluminized Mylar with a spacer. Effective conductivity '
                 'is quoted for an ideal installation at high vacuum; a real installation with seams, '
                 'penetrations and supports typically performs two to five times worse.'
    },
    'mli 60 layer': {
        'conductivity': 2.0e-5, 'density': 60.0, 'minimumTemperature': 4.0,
        'maximumTemperature': 400.0, 'requiresVacuum': True, 'emissivity': 0.05,
        'notes': 'Higher layer count for a lower heat rate at the cost of thickness and of a longer pump-down. '
                 'Diminishing returns above roughly 40 layers because the layer-to-layer solid conduction '
                 'starts to dominate.'
    },
    'vacuum only': {
        'conductivity': 1.0e-4, 'density': 0.0, 'minimumTemperature': 4.0,
        'maximumTemperature': 800.0, 'requiresVacuum': True, 'emissivity': 0.20,
        'notes': 'A bare evacuated annulus with no filler. Heat transfer is radiation between the two walls '
                 'plus residual gas conduction. Low emissivity surfaces are essential.'
    }
}

# Convection correlation coefficients for natural convection from a horizontal cylinder, in the form
#   Nu = C * Ra^n
# Churchill and Chu correlation ranges.
NATURAL_CONVECTION_LAMINAR   = (0.53, 0.25)    # 1e4 < Ra < 1e9
NATURAL_CONVECTION_TURBULENT = (0.13, 0.333)   # Ra > 1e9

# Interstitial gas pressure above which MLI stops working. Below about 1e-3 Pa the residual gas
# conduction is negligible and the insulation performs as designed. Above 1 Pa the gas conduction
# dominates and the MLI is no better than a bare vacuum gap.
#
# This is the single most common way a cryogenic insulation system fails in service: the vacuum
# jacket develops a small leak, the annulus pressure rises, and the heat leak goes up by two orders
# of magnitude with no external sign at all until the boil-off rate is measured.
MLI_VACUUM_THRESHOLD_GOOD = 1.0e-3   # [Pa]
MLI_VACUUM_THRESHOLD_LOST = 1.0      # [Pa]

# Liquid air condensation threshold. Air liquefies at about 79 K (nitrogen) to 90 K (oxygen) at one
# atmosphere. A surface below 90 K condenses oxygen-enriched liquid air.
LIQUID_AIR_THRESHOLD = 90.0   # [K]

class Insulation:

    '''

    One-dimensional insulation sizing for a cylindrical line or a flat surface.

    Primary Input Properties:
    -------------------------
    material : str
        Key into INSULATION_MATERIALS
    geometry : str
        'cylindrical' or 'planar'
    innerDiameter : float
        Bare pipe outer diameter, i.e. the insulation inner diameter [m]
    thickness : float
        Insulation thickness [m]. Leave unset when sizing.
    length : float
        Insulated length [m]
    innerTemperature : float
        Temperature at the insulation inner surface, taken as the fluid temperature [K]
    ambientTemperature : float
        Surrounding air temperature [K]
    windSpeed : float
        External air speed [m/s]. Zero for natural convection.
    surfaceEmissivity : float
        Outer surface emissivity [-]. Overrides the material default.
    relativeHumidity : float
        Ambient relative humidity [-], for the dew point check
    annulusPressure : float
        Interstitial gas pressure for vacuum insulations [Pa]
    fluid : str
        Contained fluid, for the boil-off calculation

    Key Output Properties:
    ----------------------
    heatLeak : float
        Total heat rate into (or out of) the insulated length [W]
    heatFlux : float
        Heat rate per unit outer surface area [W/m^2]
    surfaceTemperature : float
        Outer surface temperature [K]
    boilOffRate : float
        Propellant boil-off from the heat leak [kg/s]
    dewPointTemperature : float
        Ambient dew point [K]
    condensationRisk : str
        'none', 'water condensation', 'frost' or 'LIQUID AIR'
    criticalRadius : float
        Radius below which adding insulation increases heat loss [m]

    Public Methods:
    ---------------
    setInputs(inputs)                     Load a configuration dictionary
    calculateHeatLeak()                   Solve the resistance network
    sizeThickness(targetHeatLeak, targetSurfaceTemperature)
                                          Thickness for a heat or temperature target
    calculateBoilOff(tankVolume, fillFraction)
                                          Boil-off rate and hold time
    checkCondensation()                   Dew point, frost and liquid air
    calculateCriticalRadius()             The add-insulation-lose-more-heat radius
    generateReport(outputDir)             Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Insulation Definition -- #

        self.material            = 'polyurethane foam'  # key into INSULATION_MATERIALS
        self.geometry            = 'cylindrical'        # 'cylindrical' or 'planar'
        self.innerDiameter       = np.nan  # [m], bare pipe OD
        self.thickness           = np.nan  # [m]
        self.length              = 1.0     # [m], insulated length
        self.area                = np.nan  # [m^2], planar geometry only
        self.conductivity        = np.nan  # [W/m-K], overrides the material lookup
        self.surfaceEmissivity   = np.nan  # [-], overrides the material lookup

        # -- Boundary Conditions -- #

        self.innerTemperature    = np.nan  # [K], fluid or pipe wall temperature
        self.ambientTemperature  = 293.15  # [K]
        self.windSpeed           = 0.0     # [m/s], 0 for natural convection
        self.relativeHumidity    = 0.50    # [-]
        self.radiationSinkTemperature = np.nan  # [K], defaults to ambient. Use ~4 K for space.

        # -- Vacuum Insulation -- #

        self.annulusPressure     = 1.0e-4  # [Pa], interstitial gas pressure
        self.penetrationFactor   = 2.0     # [-], degradation from seams, supports and penetrations

        # -- Fluid -- #

        self.fluid               = ''      # [case sensitive string], for boil-off

        # -- Results -- #

        self.heatLeak            = np.nan  # [W]
        self.heatFlux            = np.nan  # [W/m^2]
        self.surfaceTemperature  = np.nan  # [K]
        self.convectionCoefficient = np.nan  # [W/m^2-K]
        self.radiationCoefficient  = np.nan  # [W/m^2-K]
        self.conductionResistance  = np.nan  # [K/W]
        self.surfaceResistance     = np.nan  # [K/W]
        self.boilOffRate         = np.nan  # [kg/s]
        self.dewPointTemperature = np.nan  # [K]
        self.condensationRisk    = ''      # [str]
        self.criticalRadius      = np.nan  # [m]
        self.effectiveConductivity = np.nan  # [W/m-K], after vacuum and penetration degradation
        self.insulationMass      = np.nan  # [kg]
        self.designNotes         = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: innerTemperature. Cylindrical geometry also needs innerDiameter; planar needs area.

        '''

        requiredParams = {
            'innerTemperature': 'Insulation inner surface temperature not provided.'
        }

        optionalParams = ['material', 'geometry', 'innerDiameter', 'thickness', 'length', 'area',
                          'conductivity', 'surfaceEmissivity', 'ambientTemperature', 'windSpeed',
                          'relativeHumidity', 'radiationSinkTemperature', 'annulusPressure',
                          'penetrationFactor', 'fluid']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        if np.isnan(self.radiationSinkTemperature):
            self.radiationSinkTemperature = self.ambientTemperature

    def calculateHeatLeak(self) -> float:

        '''

        Solve the one-dimensional resistance network.

        For a cylindrical geometry:

            R_conduction = ln(r_outer / r_inner) / (2 * pi * k * L)
            R_surface    = 1 / ( (h_convection + h_radiation) * A_outer )
            Q            = (T_ambient - T_inner) / (R_conduction + R_surface)

        The surface resistance is nonlinear because the radiation coefficient depends on the surface
        temperature, which depends on the heat rate, which depends on the resistance. The class
        iterates on the surface temperature to convergence, which takes a handful of passes.

        **The surface resistance is not negligible.** On a well-insulated cryogenic line the
        conduction resistance dominates and the surface term is a few percent. On a thinly insulated
        or bare line the surface term can be most of the total, and an insulation calculation that
        omits it will over-predict the heat leak substantially.

        For vacuum insulations the effective conductivity is degraded first by the annulus pressure
        and then by the penetration factor. Both degradations are large and both are routinely
        omitted, which is why measured cryogenic heat leaks are so often several times the predicted
        value.

        '''

        if np.isnan(self.thickness):
            raise InvalidInputError(
                message       = 'calculateHeatLeak needs an insulation thickness. Set thickness, or call sizeThickness().',
                parameterName = 'thickness', value = self.thickness, validRange = 'Positive real'
            )

        self.effectiveConductivity = self._effectiveConductivity()

        isCylindrical = self.geometry.strip().lower() == 'cylindrical'

        if isCylindrical:
            innerRadius = self.innerDiameter / 2.0
            outerRadius = innerRadius + self.thickness
            outerArea   = 2.0 * np.pi * outerRadius * self.length
            self.conductionResistance = np.log(outerRadius / innerRadius) / (2.0 * np.pi * self.effectiveConductivity * self.length)
        else:
            outerArea   = self.area
            self.conductionResistance = self.thickness / (self.effectiveConductivity * outerArea)

        emissivity = self.surfaceEmissivity
        if np.isnan(emissivity):
            emissivity = INSULATION_MATERIALS[self.material.strip().lower()]['emissivity']

        # Iterate on the outer surface temperature. Seed at the midpoint between the two boundaries.
        surfaceTemperature = 0.5 * (self.innerTemperature + self.ambientTemperature)

        for _ in range(100):

            convectionCoefficient = self._convectionCoefficient(surfaceTemperature, outerArea, isCylindrical)

            # Linearized radiation coefficient. Exact at the current surface temperature, so the
            # iteration converges to the correct nonlinear solution rather than to an approximation.
            radiationCoefficient = (emissivity * STEFAN_BOLTZMANN *
                                    (self.radiationSinkTemperature**2 + surfaceTemperature**2) *
                                    (self.radiationSinkTemperature + surfaceTemperature))

            surfaceResistance = 1.0 / ((convectionCoefficient + radiationCoefficient) * outerArea)
            totalResistance   = self.conductionResistance + surfaceResistance

            heatLeak = (self.ambientTemperature - self.innerTemperature) / totalResistance

            # The surface temperature follows from the heat rate crossing the surface resistance
            newSurfaceTemperature = self.ambientTemperature - heatLeak * surfaceResistance

            if abs(newSurfaceTemperature - surfaceTemperature) < 1.0e-8:
                surfaceTemperature = newSurfaceTemperature
                break

            # Under-relax to keep the iteration stable when the radiation term is strong
            surfaceTemperature = 0.5 * (surfaceTemperature + newSurfaceTemperature)

        self.surfaceTemperature       = surfaceTemperature
        self.convectionCoefficient    = convectionCoefficient
        self.radiationCoefficient     = radiationCoefficient
        self.surfaceResistance        = surfaceResistance
        self.heatLeak                 = heatLeak
        self.heatFlux                 = heatLeak / outerArea

        # Insulation mass
        materialDensity = INSULATION_MATERIALS[self.material.strip().lower()]['density']
        if isCylindrical:
            innerRadius = self.innerDiameter / 2.0
            outerRadius = innerRadius + self.thickness
            volume      = np.pi * (outerRadius**2 - innerRadius**2) * self.length
        else:
            volume      = self.area * self.thickness
        self.insulationMass = volume * materialDensity

        self.checkCondensation()

        return self.heatLeak

    def sizeThickness(self, targetHeatLeak: float = None, targetSurfaceTemperature: float = None) -> float:

        '''

        Find the thickness that meets a heat leak target, a surface temperature target, or both.

        When both are given, the larger required thickness wins, because the insulation must satisfy
        both constraints. That is the common case on a cryogenic line: the heat leak target comes
        from the boil-off allowance and the surface temperature target comes from the requirement not
        to condense liquid air, and which one governs is not obvious in advance.

        '''

        if targetHeatLeak is None and targetSurfaceTemperature is None:
            raise InvalidInputError(
                message       = 'sizeThickness needs at least one of targetHeatLeak or targetSurfaceTemperature.',
                parameterName = 'targetHeatLeak/targetSurfaceTemperature', value = None,
                validRange    = 'At least one specified'
            )

        thicknesses = []

        if targetHeatLeak is not None:
            def heatResidual(trialThickness: float) -> float:
                self.thickness = trialThickness
                return abs(self.calculateHeatLeak()) - abs(targetHeatLeak)

            thicknesses.append(secantSolve(heatResidual, 0.025, lowerBound = 1.0e-5, upperBound = 2.0))

        if targetSurfaceTemperature is not None:
            def temperatureResidual(trialThickness: float) -> float:
                self.thickness = trialThickness
                self.calculateHeatLeak()
                return self.surfaceTemperature - targetSurfaceTemperature

            thicknesses.append(secantSolve(temperatureResidual, 0.025, lowerBound = 1.0e-5, upperBound = 2.0))

        self.thickness = max(thicknesses)
        self.calculateHeatLeak()

        return self.thickness

    def calculateBoilOff(self, tankVolume: float = None, fillFraction: float = 0.95) -> dict:

        '''

        Boil-off rate from the heat leak, and the hold time before a given fraction is lost.

            mdot_boiloff = Q / h_fg

        The latent heat is evaluated at the saturation condition, so this assumes the tank is vented
        and sitting at its saturation pressure. A locked-up tank does not boil off; it self-pressurizes
        instead, and the heat leak goes into raising the ullage pressure rather than into vaporizing
        liquid. That is a different and more dangerous calculation.

        Reference latent heats at one atmosphere, for scale:

            LN2   199 kJ/kg      LOX   213 kJ/kg
            LH2   446 kJ/kg      LCH4  511 kJ/kg

        Hydrogen has by far the highest latent heat per unit mass, which sounds favorable until you
        note that its density is 71 kg/m^3, so the latent heat per unit VOLUME is 31.6 MJ/m^3 against
        243 MJ/m^3 for LOX. A hydrogen tank boils off roughly eight times as fast as an oxygen tank
        for the same heat leak per unit volume, and that is why hydrogen insulation is such a
        disproportionate part of a hydrolox vehicle.

        '''

        if np.isnan(self.heatLeak):
            self.calculateHeatLeak()

        if not self.fluid:
            raise InvalidInputError(
                message       = 'calculateBoilOff needs a fluid to look up the latent heat.',
                parameterName = 'fluid', value = self.fluid, validRange = 'A valid species name'
            )

        # Latent heat at the saturation temperature corresponding to the inner temperature
        saturationPressure = float(fluidProps(self.fluid, 'TQ', 'P', self.innerTemperature, 0.0))
        liquidEnthalpy     = float(fluidProps(self.fluid, 'TQ', 'H', self.innerTemperature, 0.0))
        vaporEnthalpy      = float(fluidProps(self.fluid, 'TQ', 'H', self.innerTemperature, 1.0))
        latentHeat         = vaporEnthalpy - liquidEnthalpy

        liquidDensity      = float(fluidProps(self.fluid, 'TQ', 'D', self.innerTemperature, 0.0))

        self.boilOffRate = abs(self.heatLeak) / latentHeat

        result = {
            'heatLeak':           self.heatLeak,
            'latentHeat':         latentHeat,
            'saturationPressure': saturationPressure,
            'boilOffRate':        self.boilOffRate,
            'boilOffPerDay':      self.boilOffRate * 86400.0
        }

        if tankVolume is not None:
            liquidMass                = tankVolume * fillFraction * liquidDensity
            result['liquidMass']      = liquidMass
            result['boilOffFractionPerDay'] = self.boilOffRate * 86400.0 / liquidMass
            result['holdTimeToEmpty'] = liquidMass / self.boilOffRate
            result['holdTimeTo90Percent'] = 0.10 * liquidMass / self.boilOffRate

        return result

    def checkCondensation(self) -> str:

        '''

        Condensation, frost and liquid air check on the outer surface.

        Three thresholds, in increasing severity:

        1. **Below the dew point:** water condenses. A nuisance on most systems, a serious problem on
           anything electrical and on any insulation that is not sealed, because a wet insulation
           conducts far better than a dry one and the problem is self-reinforcing.
        2. **Below 273 K:** frost forms. Frost is itself an insulator, so it partially self-limits,
           but it also adds mass, it falls off in sheets, and it hides the surface from inspection.
        3. **Below 90 K: LIQUID AIR.** This is a hazard, not an inconvenience. Air condensing on a
           cold surface is oxygen-enriched, because oxygen liquefies at 90 K and nitrogen at 77 K, so
           the first condensate is roughly 50 percent oxygen against the 21 percent in air. That
           liquid drips onto whatever is below. If what is below is asphalt, an organic coating, a
           polymer, or contaminated insulation, the result is an impact-sensitive explosive.

        The liquid air case is the reason bare LH2 and LHe lines are never routed above anything, and
        the reason a vacuum-jacketed line is used rather than a foam-insulated one wherever the
        surface would otherwise go below 90 K.

        The dew point is computed from the Magnus formula, which is accurate to a few tenths of a
        kelvin over the normal atmospheric range.

        '''

        # Magnus formula for dew point
        magnusA, magnusB = 17.625, 243.04   # degC basis
        ambientCelsius   = self.ambientTemperature - 273.15
        humidity         = max(min(self.relativeHumidity, 1.0), 1.0e-6)

        gamma = (magnusA * ambientCelsius / (magnusB + ambientCelsius)) + np.log(humidity)
        self.dewPointTemperature = 273.15 + magnusB * gamma / (magnusA - gamma)

        if np.isnan(self.surfaceTemperature):
            self.condensationRisk = 'not evaluated'
            return self.condensationRisk

        if self.surfaceTemperature <= LIQUID_AIR_THRESHOLD:
            self.condensationRisk = 'LIQUID AIR'
            self.designNotes.append(
                f'Outer surface temperature {self.surfaceTemperature:.1f} K is below the {LIQUID_AIR_THRESHOLD:.0f} K '
                f'liquid air threshold. Oxygen-enriched liquid air will condense and drip. This is an explosion '
                f'hazard if it lands on any organic material. Increase the insulation thickness, use a vacuum '
                f'jacket, or provide a dry gas purge in the annulus.')
        elif self.surfaceTemperature <= 273.15:
            self.condensationRisk = 'frost'
            self.designNotes.append(
                f'Outer surface at {self.surfaceTemperature:.1f} K will form frost. Frost adds mass, sheds in '
                f'sheets, and hides the surface from inspection.')
        elif self.surfaceTemperature <= self.dewPointTemperature:
            self.condensationRisk = 'water condensation'
            self.designNotes.append(
                f'Outer surface at {self.surfaceTemperature:.1f} K is below the {self.dewPointTemperature:.1f} K dew '
                f'point. Water will condense. Any insulation that is not vapor sealed will take on moisture and its '
                f'conductivity will rise, which makes the problem worse.')
        else:
            self.condensationRisk = 'none'

        return self.condensationRisk

    def calculateCriticalRadius(self) -> float:

        '''

        Critical insulation radius: the radius below which ADDING insulation INCREASES heat loss.

            r_critical = k / h

        Adding insulation to a cylinder does two opposing things: it increases the conduction
        resistance (good) and it increases the outer surface area, which decreases the surface
        resistance (bad). Below the critical radius the second effect wins.

        For a typical foam on a small tube with natural convection, `k = 0.026 W/m-K` and
        `h = 8 W/m^2-K` gives `r_critical = 3.3 mm`, which is smaller than most pipes. So in practice
        the critical radius rarely bites on insulation.

        Where it does bite is on **small-diameter items with a high-conductivity covering**: an
        instrumentation line, a small tube, or an electrical cable with a plastic jacket. There the
        jacket can genuinely increase the heat loss, which is exactly why electrical cable insulation
        is designed as a heat-shedding feature rather than a heat-retaining one.

        '''

        if np.isnan(self.convectionCoefficient) or np.isnan(self.radiationCoefficient):
            raise InvalidInputError(
                message       = 'calculateCriticalRadius needs the surface coefficients. Call calculateHeatLeak() first.',
                parameterName = 'convectionCoefficient', value = self.convectionCoefficient,
                validRange    = 'Computed by calculateHeatLeak'
            )

        conductivity          = self._effectiveConductivity()
        surfaceCoefficient    = self.convectionCoefficient + self.radiationCoefficient
        self.criticalRadius   = conductivity / surfaceCoefficient

        if self.geometry.strip().lower() == 'cylindrical':
            outerRadius = self.innerDiameter / 2.0 + self.thickness
            if outerRadius < self.criticalRadius:
                self.designNotes.append(
                    f'Outer radius {outerRadius * 1.0e3:.2f} mm is below the critical radius of '
                    f'{self.criticalRadius * 1.0e3:.2f} mm. Adding insulation at this diameter INCREASES heat loss '
                    f'because the added surface area outweighs the added conduction resistance.')

        return self.criticalRadius

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        materialData = INSULATION_MATERIALS[self.material.strip().lower()]

        rows = [
            ['Material',               f'{self.material}'],
            ['Geometry',               f'{self.geometry}'],
            ['Nominal conductivity',   f'{materialData["conductivity"]:.5g} W/m-K'],
            ['Effective conductivity', f'{self.effectiveConductivity:.5g} W/m-K'],
            ['Inner diameter',         f'{self.innerDiameter * 1.0e3:.3f} mm' if not np.isnan(self.innerDiameter) else 'planar'],
            ['Thickness',              f'{self.thickness * 1.0e3:.3f} mm'],
            ['Length',                 f'{self.length:.3f} m'],
            ['Inner temperature',      f'{self.innerTemperature:.2f} K'],
            ['Ambient temperature',    f'{self.ambientTemperature:.2f} K'],
            ['Wind speed',             f'{self.windSpeed:.2f} m/s'],
            ['Conduction resistance',  f'{self.conductionResistance:.5g} K/W'],
            ['Surface resistance',     f'{self.surfaceResistance:.5g} K/W'],
            ['Convection coefficient', f'{self.convectionCoefficient:.4f} W/m^2-K'],
            ['Radiation coefficient',  f'{self.radiationCoefficient:.4f} W/m^2-K'],
            ['Heat leak',              f'{self.heatLeak:.4f} W'],
            ['Heat flux',              f'{self.heatFlux:.4f} W/m^2'],
            ['Surface temperature',    f'{self.surfaceTemperature:.2f} K'],
            ['Dew point',              f'{self.dewPointTemperature:.2f} K'],
            ['Condensation risk',      f'{self.condensationRisk}'],
            ['Insulation mass',        f'{self.insulationMass:.4f} kg']
        ]

        if not np.isnan(self.criticalRadius):
            rows.append(['Critical radius', f'{self.criticalRadius * 1.0e3:.3f} mm'])
        if not np.isnan(self.boilOffRate):
            rows.append(['Boil-off rate',   f'{self.boilOffRate * 1.0e3:.5f} g/s ({self.boilOffRate * 86400.0:.4f} kg/day)'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'INSULATION REPORT')

        report += f'\n\nMATERIAL NOTES\n{"-" * 60}\n{materialData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'insulationReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.material.strip().lower() not in INSULATION_MATERIALS:
            raise InvalidInputError(
                message       = f'Unknown insulation material \'{self.material}\'.',
                parameterName = 'material', value = self.material,
                validRange    = str(sorted(INSULATION_MATERIALS.keys()))
            )

        if self.geometry.strip().lower() not in ('cylindrical', 'planar'):
            raise InvalidInputError(
                message       = f'Unknown geometry \'{self.geometry}\'.',
                parameterName = 'geometry', value = self.geometry, validRange = 'cylindrical or planar'
            )

        if self.geometry.strip().lower() == 'cylindrical' and np.isnan(self.innerDiameter):
            raise InvalidInputError(
                message       = 'Cylindrical geometry needs the bare pipe outer diameter as innerDiameter.',
                parameterName = 'innerDiameter', value = self.innerDiameter, validRange = 'Positive real'
            )

        if self.geometry.strip().lower() == 'planar' and np.isnan(self.area):
            raise InvalidInputError(
                message       = 'Planar geometry needs the surface area.',
                parameterName = 'area', value = self.area, validRange = 'Positive real'
            )

        materialData = INSULATION_MATERIALS[self.material.strip().lower()]
        if self.innerTemperature < materialData['minimumTemperature']:
            self.designNotes.append(
                f'{self.material} is rated to {materialData["minimumTemperature"]:.0f} K and the cold boundary is '
                f'{self.innerTemperature:.0f} K. The quoted conductivity does not apply and the material may not '
                f'survive.')

    def _effectiveConductivity(self) -> float:

        '''

        Effective conductivity after the vacuum quality and penetration degradations.

        Vacuum insulations are quoted at high vacuum in an ideal installation. Two things degrade
        that, and both are large:

        **Annulus pressure.** Below about 1e-3 Pa the residual gas contributes nothing. Above about
        1 Pa the gas conduction dominates and the MLI performs no better than a bare vacuum gap, a
        degradation of two orders of magnitude. Between those two the degradation is roughly
        logarithmic in pressure. **A slowly failing vacuum jacket gives no external sign at all until
        the boil-off rate is measured**, which is why cryogenic tanks are instrumented for boil-off.

        **Penetrations and seams.** Supports, fill lines, instrumentation leads, seams and the
        compression of MLI around a curve all short-circuit the insulation locally. A real
        installation performs two to five times worse than a laboratory coupon, and the factor is
        larger for a small, highly penetrated vessel than for a large simple one.

        '''

        materialData = INSULATION_MATERIALS[self.material.strip().lower()]

        conductivity = self.conductivity
        if np.isnan(conductivity):
            conductivity = materialData['conductivity']

        if not materialData['requiresVacuum']:
            return conductivity

        # Vacuum quality degradation
        if self.annulusPressure <= MLI_VACUUM_THRESHOLD_GOOD:
            vacuumFactor = 1.0
        elif self.annulusPressure >= MLI_VACUUM_THRESHOLD_LOST:
            vacuumFactor = 100.0
            self.designNotes.append(
                f'Annulus pressure of {self.annulusPressure:.3g} Pa has destroyed the vacuum insulation. Residual '
                f'gas conduction dominates and the heat leak is roughly 100 times the design value. Pump down or '
                f'find the leak.')
        else:
            # Logarithmic interpolation between the two thresholds
            fraction     = (np.log10(self.annulusPressure) - np.log10(MLI_VACUUM_THRESHOLD_GOOD)) / \
                           (np.log10(MLI_VACUUM_THRESHOLD_LOST) - np.log10(MLI_VACUUM_THRESHOLD_GOOD))
            vacuumFactor = 10.0**(2.0 * fraction)
            self.designNotes.append(
                f'Annulus pressure of {self.annulusPressure:.3g} Pa degrades the insulation by a factor of '
                f'{vacuumFactor:.1f}. Target below {MLI_VACUUM_THRESHOLD_GOOD:.0e} Pa.')

        return conductivity * vacuumFactor * self.penetrationFactor

    def _convectionCoefficient(self, surfaceTemperature: float, outerArea: float, isCylindrical: bool) -> float:

        '''

        External convection coefficient, natural or forced.

        **Natural convection** from a horizontal cylinder, via the Rayleigh number and the Churchill
        and Chu style power law:

            Ra = g * beta * |T_s - T_inf| * L^3 / (nu * alpha)
            Nu = C * Ra^n

        with `L` the outer diameter for a cylinder. Typical result is 3 to 10 W/m^2-K, which is the
        number to keep in your head for a still-air surface.

        **Forced convection** from a cross flow over a cylinder, Hilpert correlation:

            Nu = C * Re^m * Pr^(1/3)

        Wind matters more than people expect. A 5 m/s breeze roughly triples the surface coefficient
        relative to still air, which on a thinly insulated line can double the heat leak. Outdoor
        ground systems should be sized for wind.

        Air properties are evaluated at the film temperature.

        '''

        filmTemperature = 0.5 * (surfaceTemperature + self.ambientTemperature)
        filmTemperature = max(filmTemperature, 100.0)

        # Air properties at the film temperature and one atmosphere
        airDensity      = float(fluidProps('Air', 'TP', 'D',   filmTemperature, 101325.0))
        airViscosity    = float(fluidProps('Air', 'TP', 'VIS', filmTemperature, 101325.0))
        airConductivity = float(fluidProps('Air', 'TP', 'TCX', filmTemperature, 101325.0))
        airSpecificHeat = float(fluidProps('Air', 'TP', 'Cp',  filmTemperature, 101325.0))

        kinematicViscosity = airViscosity / airDensity
        prandtlNumber      = airViscosity * airSpecificHeat / airConductivity
        thermalDiffusivity = airConductivity / (airDensity * airSpecificHeat)

        characteristicLength = self.innerDiameter + 2.0 * self.thickness if isCylindrical else np.sqrt(outerArea)

        # -- Forced convection -- #
        if self.windSpeed > 0.1:

            reynolds = self.windSpeed * characteristicLength / kinematicViscosity

            # Hilpert correlation constants for cross flow over a cylinder
            if reynolds < 4.0:
                constantC, exponentM = 0.989, 0.330
            elif reynolds < 40.0:
                constantC, exponentM = 0.911, 0.385
            elif reynolds < 4000.0:
                constantC, exponentM = 0.683, 0.466
            elif reynolds < 40000.0:
                constantC, exponentM = 0.193, 0.618
            else:
                constantC, exponentM = 0.027, 0.805

            nusselt = constantC * reynolds**exponentM * prandtlNumber**(1.0 / 3.0)

            return nusselt * airConductivity / characteristicLength

        # -- Natural convection -- #
        temperatureDifference = abs(self.ambientTemperature - surfaceTemperature)
        if temperatureDifference < 1.0e-6:
            return 1.0e-6

        # Volumetric expansion coefficient for an ideal gas
        expansionCoefficient = 1.0 / filmTemperature

        rayleigh = (GRAVITY * expansionCoefficient * temperatureDifference * characteristicLength**3 /
                    (kinematicViscosity * thermalDiffusivity))

        if rayleigh < 1.0e9:
            constantC, exponentN = NATURAL_CONVECTION_LAMINAR
        else:
            constantC, exponentN = NATURAL_CONVECTION_TURBULENT

        nusselt = constantC * rayleigh**exponentN

        return max(nusselt * airConductivity / characteristicLength, 1.0e-6)
