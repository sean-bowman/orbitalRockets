
# -- CorrosionAssessment Class Definition -- #

'''

Galvanic couple severity and penetration rate, pitting resistance, stress corrosion cracking margin,
and the hydrogen embrittlement bake-out trigger.

The fluid compatibility matrices in fluidSystems MaterialsCompatibility.md answer which combinations
are prohibited. This class answers the quantitative questions that follow: how fast, how deep after
ten years, at what stress, and what to do about it.

Four calculations carry most of the value.

    Galvanic     A potential difference and an area ratio produce a penetration rate in mm per year
                 through Faraday's law. The output is a depth over the service life compared against
                 the corrosion allowance, not a red-amber-green rating.

    Pitting      PREN = Cr + 3.3(Mo + 0.5W) + 16N, and a critical pitting temperature correlated
                 from it. 316L comes out at PREN 25 and a CPT near minus 8 C, which says plainly
                 that it pits at ambient in chlorides. A coastal launch site is a chloride
                 environment and that single number carries more of the corrosion story than any
                 table.

    SCC          K_applied against K_ISCC, and where the applied value exceeds the threshold, a
                 time to failure from the plateau growth velocity. Short transverse tension in
                 7075-T6 raises rather than warns, because 50 MPa is a stress a designer would not
                 think twice about.

    Hydrogen     A susceptibility index from crystal structure and strength level, and the
                 ASTM F1940 bake requirement triggered by tensile strength rather than by opinion.

One rule is enforced in code rather than documented, because getting it backwards actively makes
things worse: coat the CATHODE, never only the anode. Coating only the anode concentrates the whole
couple current onto the coating holidays and accelerates the failure it was meant to prevent.

See Also:
---------
MaterialDatabase : anodicIndex, chemistry and the sccThreshold block
fluidSystems/docs/MaterialsCompatibility.md : the galvanic series and the prohibited combinations

Theory: docs/CorrosionAndSCC.md, docs/HydrogenEmbrittlement.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (applyInputs, formatReportTable,
                       InvalidInputError, CompatibilityError, createErrorContext)
    from MaterialDatabase import queryMaterial
except ImportError:
    from .utils import (applyInputs, formatReportTable,
                        InvalidInputError, CompatibilityError, createErrorContext)
    from .MaterialDatabase import queryMaterial

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Permitted anodic index difference per MIL-STD-889B, by environment severity. A launch site is a
# marine environment and takes the 0.15 V limit, which rules out most dissimilar metal joints unless
# they are isolated.

GALVANIC_POTENTIAL_LIMIT = {
    'controlled indoor':  0.50,   # [V], climate controlled, filtered
    'normal':             0.25,   # [V], indoor industrial or sheltered outdoor
    'launch site marine': 0.15,   # [V], coastal, salt spray, condensation
    'harsh':              0.15    # [V], immersion, splash zone, chloride laden
}

# Faraday constant and the electrochemical data needed to turn a current density into a penetration
# rate. Equivalent weight is atomic mass divided by the valence of the dissolution reaction.

FARADAY_CONSTANT = 96485.0        # [C/mol]

EQUIVALENT_WEIGHT = {
    'aluminium': {'weight': 8.99,  'valence': 3, 'note': 'Al -> Al3+'},
    'iron':      {'weight': 27.92, 'valence': 2, 'note': 'Fe -> Fe2+'},
    'nickel':    {'weight': 29.36, 'valence': 2, 'note': 'Ni -> Ni2+'},
    'copper':    {'weight': 31.77, 'valence': 2, 'note': 'Cu -> Cu2+'},
    'titanium':  {'weight': 11.98, 'valence': 4, 'note': 'Ti -> Ti4+, but the passive film means '
                                                         'the calculated rate overstates reality '
                                                         'by orders of magnitude'},
    'magnesium': {'weight': 12.15, 'valence': 2, 'note': 'Mg -> Mg2+'},
    'zinc':      {'weight': 32.70, 'valence': 2, 'note': 'Zn -> Zn2+'}
}

# Exchange current density for a galvanic couple in a given electrolyte. This is the crude part of
# the calculation and it is why the output should be read as an order of magnitude rather than a
# prediction. A real rate needs a polarisation curve for the specific couple and electrolyte.

COUPLE_CURRENT_DENSITY = {
    'controlled indoor':  1.0e-3,   # [A/m^2] per volt of driving potential
    'normal':             1.0e-2,
    'launch site marine': 1.0e-1,
    'harsh':              5.0e-1
}

# Alloy family to the dissolving species, for the Faraday conversion.
FAMILY_TO_SPECIES = {
    'aluminium': 'aluminium', 'stainless': 'iron', 'nickel': 'nickel',
    'titanium': 'titanium', 'copper': 'copper', 'low alloy steel': 'iron',
    'composite': None
}

# Critical pitting temperature correlation from PREN. Approximate and widely used:
#
#     CPT [degC] = 2.5 * PREN - 71
#
# 316L at PREN 25.4 gives minus 8 C. That is the number that explains why 316L is not the automatic
# answer at a coastal site and why 625 at PREN 51 is.

CPT_SLOPE     = 2.5      # [degC per PREN unit]
CPT_INTERCEPT = -71.0    # [degC]

# Hydrogen embrittlement. The ASTM F1940 and AMS 2759/9 trigger is the tensile strength: above this
# level a plated part must be baked, and the bake is not optional.

HYDROGEN_BAKE_THRESHOLD = 1000.0e6   # [Pa] ultimate tensile strength
HYDROGEN_BAKE_TIME      = 82800.0    # [s], 23 hours
HYDROGEN_BAKE_TEMPERATURE = 463.15   # [K], 190 degC

# Susceptibility by crystal structure. BCC lattices have high hydrogen diffusivity and low
# solubility, which concentrates hydrogen at traps and crack tips. FCC is the opposite. This is the
# same mechanism that governs the ductile to brittle transition and it is not a coincidence.

STRUCTURE_HYDROGEN_FACTOR = {
    'bcc': 1.0, 'bcc martensite': 1.0, 'hcp': 0.5, 'fcc': 0.15,
    'hcp alpha + bcc beta': 0.6, 'n/a': 0.0
}

# Stress corrosion crack growth. Stage II plateau velocity, where growth is independent of K.
PLATEAU_VELOCITY = {
    'aluminium 7xxx':      1.0e-9,    # [m/s] in marine air, short transverse
    'aluminium 2xxx':      3.0e-10,
    'stainless austenitic': 1.0e-9,   # in hot chlorides
    'titanium alpha-beta': 1.0e-8,    # in methanol or uninhibited N2O4, and it is fast
    'low alloy steel':     5.0e-9,    # in hydrogen or H2S
    'stainless martensitic PH': 2.0e-9
}

# ------------------------------------------------------------------------------------------------ #

class CorrosionAssessment:

    '''

    Quantitative corrosion, stress corrosion and hydrogen screening for a material pair and
    environment.

    Primary Input Properties:
    -------------------------
    anodeMaterial / cathodeMaterial : str
        The less noble and more noble members of the couple
    anodeArea / cathodeArea : float
        Wetted areas [m^2]. The RATIO is what matters and the direction is counterintuitive.
    environment : str
        Key into GALVANIC_POTENTIAL_LIMIT
    appliedStress : float
        Sustained tensile stress [Pa] for the SCC check
    orientation : str
        'L', 'LT' or 'ST'. Short transverse is where SCC lives.
    serviceLife : float
        [s], for the accumulated penetration depth

    Key Output Properties:
    ----------------------
    potentialDifference : float
        [V] between the two anodic indices
    penetrationDepth : float
        [m] of anode consumed over the service life
    pittingResistance : float
        PREN
    sccMargin : float
        K_ISCC / K_applied

    Public Methods:
    ---------------
    setInputs(inputs)               Load a configuration dictionary
    calculateGalvanicCouple()       Potential, area ratio, current density, penetration rate
    calculatePittingResistance()    PREN and critical pitting temperature
    assessStressCorrosion()         K_applied against K_ISCC, and time to failure if exceeded
    assessHydrogenEmbrittlement()   Susceptibility index and the bake requirement
    recommendProtection()           Ordered mitigations, with the coat-the-cathode rule enforced
    generateReport(outputDir)       Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- The Couple -- #

        self.anodeMaterial      = '6061'      # [case insensitive string], the less noble member
        self.anodeCondition     = None        # [case insensitive string]
        self.cathodeMaterial    = '316L'      # [case insensitive string], the more noble member
        self.cathodeCondition   = None        # [case insensitive string]
        self.anodeArea          = np.nan      # [m^2], wetted
        self.cathodeArea        = np.nan      # [m^2], wetted

        # -- Environment -- #

        self.environment        = 'launch site marine'  # [case insensitive string]
        self.temperature        = 293.15      # [K]
        self.serviceLife        = 3.156e8     # [s], ten years
        self.corrosionAllowance = np.nan      # [m]

        # -- Stress State -- #

        self.appliedStress      = np.nan      # [Pa], SUSTAINED tensile stress
        self.orientation        = 'ST'        # [-], the direction the stress acts in
        self.flawDepth          = 0.000635    # [m], for the K_applied calculation
        self.sccEnvironmentKey  = 'marine air'  # [case insensitive string]

        # -- Results -- #

        self.potentialDifference = np.nan     # [V]
        self.areaRatio           = np.nan     # [-], cathode over anode
        self.penetrationRate     = np.nan     # [m/s]
        self.penetrationDepth    = np.nan     # [m] over the service life
        self.pittingResistance   = np.nan     # [-], PREN
        self.criticalPittingTemperature = np.nan  # [K]
        self.sccMargin           = np.nan     # [-]
        self.hydrogenSusceptibility = np.nan  # [-], 0 to 1
        self.corrosionNotes      = []         # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: anodeMaterial.

        '''

        requiredParams = {
            'anodeMaterial': 'Anode material not provided.'
        }

        optionalParams = ['anodeCondition', 'cathodeMaterial', 'cathodeCondition', 'anodeArea',
                          'cathodeArea', 'environment', 'temperature', 'serviceLife',
                          'corrosionAllowance', 'appliedStress', 'orientation', 'flawDepth',
                          'sccEnvironmentKey']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateGalvanicCouple(self) -> dict:

        '''

        Galvanic driving potential, area ratio and the resulting penetration rate on the anode.

            dE = |anodicIndex(cathode) - anodicIndex(anode)|
            areaRatio = A_cathode / A_anode
            i_anode = i_couple * dE * areaRatio
            rate [m/s] = i_anode * equivalentWeight / (Faraday * density)

        The area ratio effect is the one people get backwards. A small anode against a large cathode
        concentrates the entire couple current onto a small area, so a steel fastener in an aluminium
        plate is fine and an aluminium fastener in a steel plate is destroyed. The rate scales
        directly with the ratio.

        The absolute rate should be read as an order of magnitude. The couple current density is a
        crude stand-in for a real polarisation curve, and on a passive alloy like titanium it
        overstates the rate by orders of magnitude because the passive film is not modelled at all.
        What the calculation is genuinely good for is the comparison between two candidate joints
        and the direction of the area ratio effect.

        '''

        anode   = queryMaterial(self.anodeMaterial,   self.anodeCondition,   self.temperature)
        cathode = queryMaterial(self.cathodeMaterial, self.cathodeCondition, self.temperature)

        self.potentialDifference = abs(cathode['anodicIndex'] - anode['anodicIndex'])

        limit      = GALVANIC_POTENTIAL_LIMIT[self.environment]
        acceptable = self.potentialDifference <= limit

        # Confirm the caller has the anode and cathode the right way round. A higher anodic index in
        # MIL-STD-889 means MORE anodic, so the anode should have the larger index.
        if anode['anodicIndex'] < cathode['anodicIndex']:
            self.corrosionNotes.append(
                f'{self.anodeMaterial} has a LOWER anodic index than {self.cathodeMaterial}, so it '
                f'is the more noble member and the roles are reversed. The material that will '
                f'actually corrode is {self.cathodeMaterial}.')

        result = {'anodeMaterial': anode['commonName'], 'cathodeMaterial': cathode['commonName'],
                  'anodeIndex': anode['anodicIndex'], 'cathodeIndex': cathode['anodicIndex'],
                  'potentialDifference': self.potentialDifference,
                  'permittedDifference': limit, 'environment': self.environment,
                  'acceptable': acceptable}

        if not acceptable:
            self.corrosionNotes.append(
                f'The couple potential of {self.potentialDifference:.2f} V exceeds the '
                f'{limit:.2f} V permitted for a {self.environment} environment by MIL-STD-889B. '
                f'This joint needs isolation, and the isolation has to survive the service life '
                f'rather than merely exist at assembly.')

        # -- Penetration rate, when the areas are known -- #

        if not (np.isnan(self.anodeArea) or np.isnan(self.cathodeArea)):

            self.areaRatio = self.cathodeArea / self.anodeArea

            family  = anode['family'].split()[0].lower()
            species = FAMILY_TO_SPECIES.get(family)

            if species is None:
                self.corrosionNotes.append(
                    f'No dissolution reaction is defined for the {anode["family"]} family, so no '
                    f'penetration rate is computed. A composite does not corrode galvanically; it '
                    f'drives the corrosion of whatever it is bolted to.')
            else:
                electrochemistry = EQUIVALENT_WEIGHT[species]
                currentDensity   = COUPLE_CURRENT_DENSITY[self.environment] * \
                                   self.potentialDifference * self.areaRatio

                # Faraday: mass loss per unit area per unit time, converted to a depth.
                self.penetrationRate = currentDensity * electrochemistry['weight'] * 1.0e-3 / \
                                       (FARADAY_CONSTANT * anode['density'])
                self.penetrationDepth = self.penetrationRate * self.serviceLife

                result['areaRatio']        = self.areaRatio
                result['currentDensity']   = currentDensity
                result['penetrationRate']  = self.penetrationRate
                result['penetrationDepth'] = self.penetrationDepth
                result['penetrationPerYear'] = self.penetrationRate * 3.156e7
                result['dissolutionReaction'] = electrochemistry['note']

                if self.areaRatio > 1.0:
                    self.corrosionNotes.append(
                        f'The cathode is {self.areaRatio:.1f} times the anode area, which '
                        f'concentrates the couple current onto the smaller anode and multiplies the '
                        f'penetration rate by the same factor. Reversing the ratio, so that the '
                        f'anode is the large member, is usually the cheapest available fix.')

                if not np.isnan(self.corrosionAllowance):
                    result['corrosionAllowance'] = self.corrosionAllowance
                    result['allowanceMargin'] = self.corrosionAllowance / self.penetrationDepth \
                                                if self.penetrationDepth > 0.0 else np.inf
                    if self.penetrationDepth > self.corrosionAllowance:
                        self.corrosionNotes.append(
                            f'Predicted penetration of {self.penetrationDepth * 1.0e3:.3f} mm over '
                            f'the service life exceeds the {self.corrosionAllowance * 1.0e3:.3f} mm '
                            f'corrosion allowance.')

        return result

    def calculatePittingResistance(self) -> dict:

        '''

        Pitting resistance equivalent number and the critical pitting temperature it implies.

            PREN = %Cr + 3.3 (%Mo + 0.5 %W) + 16 %N
            CPT [degC] = 2.5 PREN - 71

        Above the critical pitting temperature, chlorides initiate stable pits. Below it they do
        not. For 316L the CPT lands near minus 8 C, which says in one number that 316L pits at
        ambient temperature in any chloride environment, and a coastal launch site is one.

        The correlation is approximate and it applies to austenitic and duplex stainless. It is
        meaningless for aluminium, titanium or nickel-copper, and returns None for them.

        '''

        anode = queryMaterial(self.anodeMaterial, self.anodeCondition, self.temperature)

        chemistry = anode.get('chemistry')

        if chemistry is None or chemistry.get('chromium', 0.0) < 10.5:
            self.corrosionNotes.append(
                f'PREN is defined for stainless alloys, and {anode["commonName"]} has less than '
                f'10.5 percent chromium. Its pitting behaviour is governed by a different '
                f'mechanism and this number would be meaningless.')
            return {'pren': None, 'criticalPittingTemperature': None,
                    'applicable': False, 'material': anode['commonName']}

        self.pittingResistance = (chemistry.get('chromium', 0.0) +
                                  3.3 * (chemistry.get('molybdenum', 0.0) +
                                         0.5 * chemistry.get('tungsten', 0.0)) +
                                  16.0 * chemistry.get('nitrogen', 0.0))

        celsius = CPT_SLOPE * self.pittingResistance + CPT_INTERCEPT
        self.criticalPittingTemperature = celsius + 273.15

        pitsAtService = self.temperature > self.criticalPittingTemperature

        result = {'material': anode['commonName'], 'pren': self.pittingResistance,
                  'criticalPittingTemperature': self.criticalPittingTemperature,
                  'criticalPittingCelsius': celsius,
                  'serviceTemperature': self.temperature,
                  'pitsAtServiceTemperature': pitsAtService, 'applicable': True,
                  'databasePren': anode.get('environmental', {}).get('pren')}

        if pitsAtService:
            self.corrosionNotes.append(
                f'{anode["commonName"]} has PREN {self.pittingResistance:.1f}, giving a critical '
                f'pitting temperature of {celsius:.0f} degC. At the service temperature of '
                f'{self.temperature - 273.15:.0f} degC it will pit in a chloride environment. '
                f'Passivation per AMS 2700 restores the film but does not raise the CPT; only a '
                f'higher alloy content does.')

        return result

    def assessStressCorrosion(self) -> dict:

        '''

        Stress corrosion cracking margin, and time to failure where the threshold is exceeded.

            K_applied = Y sigma sqrt(pi a)
            margin    = K_ISCC / K_applied

        Where the applied intensity exceeds the threshold, the crack grows at the stage II plateau
        velocity, which is independent of K, so the time to failure follows directly from the
        distance the crack has to travel.

        RAISES rather than warns for a sustained short transverse tensile stress above the threshold
        in a susceptible alloy. Fifty MPa in 7075-T6 short transverse is a stress nobody would think
        twice about, and it cracks.

        '''

        anode = queryMaterial(self.anodeMaterial, self.anodeCondition, self.temperature)

        environmental = anode.get('environmental', {})
        thresholds    = environmental.get('sccThreshold', {})
        rating        = environmental.get('sccRating', {}).get(self.orientation)

        if np.isnan(self.appliedStress):
            return {'material': anode['commonName'], 'orientation': self.orientation,
                    'sccRating': rating, 'thresholds': thresholds,
                    'note': 'No applied stress supplied, so only the qualitative rating is reported.'}

        threshold = thresholds.get(self.sccEnvironmentKey)

        if threshold is None and thresholds:
            key       = min(thresholds, key = lambda name: thresholds[name])
            threshold = thresholds[key]
            self.corrosionNotes.append(
                f'No threshold for \'{self.sccEnvironmentKey}\' is tabulated for '
                f'{anode["commonName"]}, so the worst tabulated environment \'{key}\' was used.')

        result = {'material': anode['commonName'], 'orientation': self.orientation,
                  'appliedStress': self.appliedStress, 'sccRating': rating,
                  'environment': self.sccEnvironmentKey, 'thresholdStress': threshold}

        if threshold is None:
            result['note'] = 'No SCC threshold data for this material.'
            return result

        result['stressMargin'] = threshold / self.appliedStress
        exceeds = self.appliedStress > threshold

        # -- Fracture mechanics form, when a flaw is postulated -- #

        fracture = anode.get('fracture', {})
        toughnessValues = fracture.get('planeStrainToughness', {})

        if toughnessValues:
            toughness = min(toughnessValues.values())
            geometryFactor = 1.12
            appliedIntensity = geometryFactor * self.appliedStress * np.sqrt(np.pi * self.flawDepth)

            # K_ISCC scaled from the threshold stress at the same postulated flaw
            thresholdIntensity = geometryFactor * threshold * np.sqrt(np.pi * self.flawDepth)

            self.sccMargin = thresholdIntensity / appliedIntensity

            criticalDepth = (1.0 / np.pi) * (toughness /
                                             (geometryFactor * self.appliedStress)) ** 2

            result.update({'appliedIntensity': appliedIntensity,
                           'thresholdIntensity': thresholdIntensity,
                           'sccMargin': self.sccMargin,
                           'criticalFlawDepth': criticalDepth})

            if exceeds:
                family   = anode['family']
                velocity = None
                for familyKey, value in PLATEAU_VELOCITY.items():
                    if familyKey in family:
                        velocity = value
                        break

                if velocity is not None:
                    growthDistance = max(criticalDepth - self.flawDepth, 0.0)
                    timeToFailure  = growthDistance / velocity
                    result['plateauVelocity'] = velocity
                    result['timeToFailure']   = timeToFailure
                    result['timeToFailureDays'] = timeToFailure / 86400.0

        if exceeds:
            message = (f'{anode["commonName"]} under a sustained {self.appliedStress / 1.0e6:.0f} '
                       f'MPa tensile stress in the {self.orientation} direction exceeds its SCC '
                       f'threshold of {threshold / 1.0e6:.0f} MPa in {self.sccEnvironmentKey}. '
                       f'The SCC rating in this direction is \'{rating}\'.')

            if rating in ('very low', 'low') and self.orientation == 'ST':
                raise CompatibilityError(
                    message  = message + ' A sustained short transverse tensile stress in an alloy '
                                         'with this rating will crack in service. This is not a '
                                         'margin to be accepted; the stress state has to change.',
                    material = anode['commonName'],
                    fluid    = self.sccEnvironmentKey
                )

            self.corrosionNotes.append(message)

        result['exceedsThreshold'] = exceeds

        return result

    def assessHydrogenEmbrittlement(self) -> dict:

        '''

        Susceptibility index and the plating bake-out requirement.

        Susceptibility is driven by three things and the class combines all three:

            crystal structure   BCC is worst. High diffusivity and low solubility concentrate
                                hydrogen at traps and crack tips.
            strength level      Susceptibility rises steeply above about 1000 MPa ultimate,
                                which is why the ASTM F1940 bake trigger sits there.
            notched ratio       The measured strength in hydrogen divided by the strength in
                                helium, which is the direct experimental measure.

        Temperature dependence is the counterintuitive part: embrittlement is WORST near 200 to 250
        K, not at the extremes. Cold slows the diffusion that feeds the crack tip and heat lets
        hydrogen escape faster than it accumulates.

        '''

        anode = queryMaterial(self.anodeMaterial, self.anodeCondition, self.temperature)

        structure     = anode['crystalStructure']
        structureRisk = STRUCTURE_HYDROGEN_FACTOR.get(structure, 0.5)

        ultimate      = anode.get('ultimateStrength', 0.0) or 0.0
        strengthRisk  = min(1.0, max(0.0, (ultimate - 700.0e6) / (1800.0e6 - 700.0e6)))

        notchedRatio  = anode.get('environmental', {}).get('hydrogenRatio', 1.0)
        measuredRisk  = 1.0 - notchedRatio

        # Weighted, with the measured ratio dominating where it exists because it is data rather
        # than inference.
        self.hydrogenSusceptibility = (0.25 * structureRisk + 0.25 * strengthRisk +
                                       0.50 * measuredRisk)

        # Temperature factor, peaking near 225 K
        peakTemperature = 225.0
        temperatureFactor = float(np.exp(-((self.temperature - peakTemperature) / 120.0) ** 2))

        bakeRequired = ultimate >= HYDROGEN_BAKE_THRESHOLD

        result = {'material': anode['commonName'], 'crystalStructure': structure,
                  'structureRisk': structureRisk, 'ultimateStrength': ultimate,
                  'strengthRisk': strengthRisk, 'notchedRatio': notchedRatio,
                  'susceptibilityIndex': self.hydrogenSusceptibility,
                  'temperatureFactor': temperatureFactor,
                  'worstCaseTemperature': peakTemperature,
                  'bakeRequired': bakeRequired,
                  'bakeTime': HYDROGEN_BAKE_TIME if bakeRequired else 0.0,
                  'bakeTemperature': HYDROGEN_BAKE_TEMPERATURE if bakeRequired else np.nan}

        if bakeRequired:
            self.corrosionNotes.append(
                f'{anode["commonName"]} at {ultimate / 1.0e6:.0f} MPa ultimate is above the '
                f'{HYDROGEN_BAKE_THRESHOLD / 1.0e6:.0f} MPa trigger in ASTM F1940. Any electroplating '
                f'or acid pickling operation requires a bake of at least '
                f'{HYDROGEN_BAKE_TIME / 3600.0:.0f} hours at '
                f'{HYDROGEN_BAKE_TEMPERATURE - 273.15:.0f} degC, started within four hours of '
                f'plating. This is not a recommendation.')

        if notchedRatio < 0.5:
            self.corrosionNotes.append(
                f'The notched tensile ratio in hydrogen is {notchedRatio:.2f}, meaning the material '
                f'retains only {notchedRatio * 100.0:.0f} percent of its notched strength in a '
                f'hydrogen environment. It should not be used in hydrogen service at all.')

        if abs(self.temperature - peakTemperature) < 60.0 and self.hydrogenSusceptibility > 0.3:
            self.corrosionNotes.append(
                f'The service temperature of {self.temperature:.0f} K sits near the {peakTemperature:.0f} K '
                f'peak of hydrogen embrittlement susceptibility. Testing at room temperature or at '
                f'cryogenic temperature would both understate the effect.')

        return result

    def recommendProtection(self) -> list:

        '''

        Ordered mitigations, most effective first.

        The coat-the-cathode rule is enforced here rather than left to the reader, because getting
        it backwards is worse than doing nothing: coating only the anode concentrates the entire
        couple current onto the inevitable holidays in the coating and drives rapid local attack.

        '''

        if np.isnan(self.potentialDifference):
            self.calculateGalvanicCouple()

        limit = GALVANIC_POTENTIAL_LIMIT[self.environment]

        recommendations = []

        if self.potentialDifference <= limit:
            recommendations.append(
                f'The couple is within the {limit:.2f} V limit for a {self.environment} '
                f'environment. No galvanic protection is required, though normal finishing applies.')
            return recommendations

        recommendations.append(
            'Eliminate the couple. Change one member so both sit in the same group of the galvanic '
            'series. This is the only fix that cannot degrade in service.')

        recommendations.append(
            'Electrically isolate the joint with a non-conductive gasket, sleeve and washer set. '
            'The isolation has to interrupt every metallic path including the fastener, and it has '
            'to be verified by resistance measurement rather than by inspection.')

        recommendations.append(
            'Coat the CATHODE, and coat the anode as well if either is coated. Never coat only the '
            'anode: a coating always has holidays, and coating only the anode concentrates the '
            'entire couple current onto them, producing faster local penetration than no coating '
            'at all.')

        if not np.isnan(self.areaRatio) and self.areaRatio > 1.0:
            recommendations.append(
                f'Reverse the area ratio. The cathode is currently {self.areaRatio:.1f} times the '
                f'anode area and the penetration rate scales directly with that. Making the anode '
                f'the large member reduces the rate by the same factor.')

        recommendations.append(
            'Seal the joint against electrolyte with a wet-installed sealant, so there is no '
            'continuous water path to complete the circuit.')

        if not np.isnan(self.penetrationDepth):
            recommendations.append(
                f'If the joint is accepted as-is, set an inspection interval from the predicted '
                f'penetration rate of {self.penetrationRate * 3.156e7 * 1.0e3:.3f} mm per year and '
                f'record the corrosion allowance it consumes.')

        return recommendations

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        galvanic = self.calculateGalvanicCouple()
        pitting  = self.calculatePittingResistance()

        rows = [
            ['Anode',              f'{galvanic["anodeMaterial"]} (index '
                                   f'{galvanic["anodeIndex"]:.2f} V)'],
            ['Cathode',            f'{galvanic["cathodeMaterial"]} (index '
                                   f'{galvanic["cathodeIndex"]:.2f} V)'],
            ['Environment',        f'{self.environment}'],
            ['Potential difference', f'{self.potentialDifference:.2f} V against a '
                                     f'{galvanic["permittedDifference"]:.2f} V limit'],
            ['Galvanic acceptable', f'{"YES" if galvanic["acceptable"] else "NO"}']
        ]

        if not np.isnan(self.areaRatio):
            rows.append(['Area ratio (cathode/anode)', f'{self.areaRatio:.1f}'])
            rows.append(['Penetration rate', f'{self.penetrationRate * 3.156e7 * 1.0e3:.4f} mm/yr'])
            rows.append(['Penetration over life',
                         f'{self.penetrationDepth * 1.0e3:.4f} mm in '
                         f'{self.serviceLife / 3.156e7:.1f} years'])

        if pitting['applicable']:
            rows.append(['PREN', f'{pitting["pren"]:.1f}'])
            rows.append(['Critical pitting temperature',
                         f'{pitting["criticalPittingCelsius"]:.0f} degC'])
            rows.append(['Pits at service temperature',
                         f'{"YES" if pitting["pitsAtServiceTemperature"] else "NO"}'])

        if not np.isnan(self.appliedStress):
            try:
                scc = self.assessStressCorrosion()
                if scc.get('thresholdStress') is not None:
                    rows.append(['SCC threshold',
                                 f'{scc["thresholdStress"] / 1.0e6:.0f} MPa in {scc["environment"]}'])
                    rows.append(['Applied stress',
                                 f'{self.appliedStress / 1.0e6:.0f} MPa ({self.orientation})'])
                    rows.append(['SCC stress margin', f'{scc["stressMargin"]:.2f}'])
            except CompatibilityError as error:
                rows.append(['SCC', 'PROHIBITED -- see the caution below'])
                self.corrosionNotes.append(str(error))

        hydrogen = self.assessHydrogenEmbrittlement()
        rows.append(['Hydrogen susceptibility',
                     f'{hydrogen["susceptibilityIndex"]:.2f} ({hydrogen["crystalStructure"]})'])
        rows.append(['H2 bake required',
                     f'{"YES, " + str(int(HYDROGEN_BAKE_TIME / 3600.0)) + " h at " + str(int(HYDROGEN_BAKE_TEMPERATURE - 273.15)) + " degC" if hydrogen["bakeRequired"] else "no"}'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'CORROSION ASSESSMENT')

        recommendations = self.recommendProtection()
        report += f'\n\nPROTECTION, MOST EFFECTIVE FIRST\n{"-" * 70}\n'
        for index, recommendation in enumerate(recommendations, start = 1):
            report += f'  {index}. {recommendation}\n'

        for note in self.corrosionNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'corrosionAssessment.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.environment not in GALVANIC_POTENTIAL_LIMIT:
            raise InvalidInputError(
                message       = f'Unknown environment \'{self.environment}\'.',
                parameterName = 'environment', value = self.environment,
                validRange    = str(sorted(GALVANIC_POTENTIAL_LIMIT.keys()))
            )

        if self.orientation not in ('L', 'LT', 'ST'):
            raise InvalidInputError(
                message       = f'Unknown orientation \'{self.orientation}\'.',
                parameterName = 'orientation', value = self.orientation,
                validRange    = "'L', 'LT' or 'ST'"
            )

        for name, value in (('anodeArea', self.anodeArea), ('cathodeArea', self.cathodeArea)):
            if not np.isnan(value) and value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0 m^2'
                )
