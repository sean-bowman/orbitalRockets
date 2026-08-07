
# -- SurfaceTreatment Class Definition -- #

'''

Shot peening, chemical milling, electropolishing, plating and thermal spray.

Fatigue cracks start at surfaces. Almost every treatment in this class exists to change that, either
by putting the surface into compression so a crack cannot open, or by removing the layer that would
have started one.

Four calculations carry the class.

    Peening        Almen intensity converts to a compressive layer depth and a fatigue improvement
                   factor. Coverage follows an exponential saturation law, which is why 200 percent
                   coverage is a real specification and not a typo.

    Faraday        Chemical milling and electropolishing both remove stock at a rate set by the
                   current or the etch rate, and both remove it from BOTH surfaces of a wall. That
                   doubling is the error people make.

    Alpha case     Titanium picks up oxygen above about 800 K, forming a hard brittle surface layer
                   that is a fatigue crack initiation site. Removing it is a required specification
                   with a computed depth, not an optional refinement.

    Bake trigger   Any plating operation on a part above 1000 MPa ultimate charges hydrogen into it
                   and requires a bake per ASTM F1940. The trigger is the tensile strength, not the
                   service.

HOT ISOSTATIC PRESSING IS DELIBERATELY NOT HERE. It is a thermal cycle at pressure and it belongs
with solution treatment and aging in HeatTreatment, where it interacts with them directly.

See Also:
---------
HeatTreatment       : HIP, and the stress relief that a peened surface must survive
CorrosionAssessment : The hydrogen bake trigger, from the other direction
ExtrusionHoning     : Internal surfaces, which none of these treatments reach

Theory: docs/PeeningAndSurfaceStress.md, docs/ChemicalAndElectroProcesses.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from surfaceUtils import (applyInputs, formatReportTable, queryMaterial, roughnessTable,
                              InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .surfaceUtils import (applyInputs, formatReportTable, queryMaterial, roughnessTable,
                               InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

FARADAY_CONSTANT = 96485.0     # [C/mol]

# Almen strips measure peening intensity by the arc height a standard strip takes. The A strip is
# the usual one; N is for light intensities and C for heavy.
#
# The compressive layer depth scales with the intensity, and so does the surface roughening, which
# is the trade: more compression and a rougher surface, and above a point the roughening starts
# creating the initiation sites the compression was meant to prevent.

ALMEN_STRIPS = {
    'N': {'multiplier': 0.31, 'range': (0.05e-3, 0.30e-3), 'note': 'Light. Thin sections and '
                                                                   'aluminium.'},
    'A': {'multiplier': 1.00, 'range': (0.10e-3, 0.60e-3), 'note': 'The standard strip. Most '
                                                                   'aerospace specifications.'},
    'C': {'multiplier': 3.50, 'range': (0.15e-3, 0.60e-3), 'note': 'Heavy. Thick sections, gears '
                                                                   'and landing gear.'}
}

# Peening media. Shot size sets the dimple size and therefore the roughening, and the hardness has
# to exceed the workpiece or the shot deforms instead of the part.
PEENING_MEDIA = {
    'cast steel shot':  {'diameter': 0.60e-3, 'hardness': 500.0, 'roughnessFactor': 1.00,
                         'note': 'The default. Cheap and effective, and it leaves iron on the '
                                 'surface, which is a problem on stainless and titanium.'},
    'ceramic bead':     {'diameter': 0.35e-3, 'hardness': 700.0, 'roughnessFactor': 0.60,
                         'note': 'No iron contamination. The choice for stainless, titanium and '
                                 'anything that will be passivated afterwards.'},
    'glass bead':       {'diameter': 0.30e-3, 'hardness': 500.0, 'roughnessFactor': 0.50,
                         'note': 'Light intensity and a good finish. Cleaning more than peening.'},
    'laser shock':      {'diameter': 0.0,     'hardness': 0.0,   'roughnessFactor': 0.05,
                         'note': 'No media at all. A confined plasma drives a shock wave. Four to '
                                 'five times the layer depth of shot peening with almost no '
                                 'surface roughening, at many times the cost.'}
}

# Coverage follows an exponential saturation, because each impact is random and later impacts
# increasingly land where earlier ones already have.
#
#     C = 1 - exp(-A t)
#
# Full coverage is defined as 98 percent, because 100 percent is asymptotic and unreachable. That is
# why specifications call for 200 percent coverage, meaning twice the time to reach 98 percent: it
# is a time specification, not a geometric impossibility.

COVERAGE_SATURATION = 0.98      # [-], what is called 100 percent coverage

# Electrochemical processes. Removal rate follows Faraday for electrochemical processes and a
# chemical rate law for etching.
ELECTROCHEMICAL_PROCESSES = {
    'electropolish':    {'currentDensity': 200.0, 'efficiency': 0.60, 'roughnessFloor': 0.2e-6,
                         'roughnessRatio': 0.35,
                         'note': 'Removes the peaks preferentially, so it improves Ra and also '
                                 'removes any compressive layer from peening. Never electropolish '
                                 'after peening.'},
    'chemical mill':    {'currentDensity': 0.0,   'efficiency': 1.00, 'roughnessFloor': 1.6e-6,
                         'roughnessRatio': 1.00,
                         'note': 'Removes uniformly, so it preserves the surface profile and the '
                                 'geometry. It does not improve roughness.'},
    'electrochemical machine': {'currentDensity': 5000.0, 'efficiency': 0.85,
                                'roughnessFloor': 0.4e-6, 'roughnessRatio': 0.50,
                                'note': 'No tool contact, so no residual stress and no recast '
                                        'layer. Slow and it needs a shaped cathode.'}
}

# Equivalent weight and valence for the Faraday calculation.
DISSOLUTION_CHEMISTRY = {
    'aluminium': {'equivalentWeight': 8.99,  'note': 'Al -> Al3+'},
    'stainless': {'equivalentWeight': 27.92, 'note': 'Fe -> Fe2+, approximated as iron'},
    'nickel':    {'equivalentWeight': 29.36, 'note': 'Ni -> Ni2+'},
    'titanium':  {'equivalentWeight': 11.98, 'note': 'Ti -> Ti4+'},
    'copper':    {'equivalentWeight': 31.77, 'note': 'Cu -> Cu2+'}
}

# Titanium alpha case. Oxygen diffuses in above about 800 K, forming a hard brittle oxygen-enriched
# layer. The depth follows a parabolic diffusion law.
#
#     depth = sqrt(D t),  D = D0 exp(-Q / R T)

ALPHA_CASE_DIFFUSIVITY = 1.4e-6      # [m^2/s], pre-exponential for oxygen in alpha titanium
ALPHA_CASE_ACTIVATION  = 200000.0    # [J/mol]
UNIVERSAL_GAS_CONSTANT = 8.3145      # [J/mol-K]
ALPHA_CASE_SAFETY      = 1.5         # [-], removal depth as a multiple of the computed case depth

# Hydrogen embrittlement relief, per ASTM F1940 and AMS 2759/9. Same numbers as the materials domain
# carries, and a test asserts they agree.
HYDROGEN_BAKE_THRESHOLD   = 1000.0e6   # [Pa] ultimate tensile strength
HYDROGEN_BAKE_TIME        = 82800.0    # [s], 23 hours
HYDROGEN_BAKE_TEMPERATURE = 463.15     # [K], 190 degC
HYDROGEN_BAKE_START_WINDOW = 14400.0   # [s], four hours from plating

# Plating processes, and whether they charge hydrogen.
PLATING_PROCESSES = {
    'cadmium':          {'chargesHydrogen': True,  'thickness': 12.5e-6,
                         'note': 'Being designed out for environmental reasons. IVD aluminium is '
                                 'the replacement and it charges no hydrogen.'},
    'zinc':             {'chargesHydrogen': True,  'thickness': 12.5e-6, 'note': 'As cadmium.'},
    'hard chrome':      {'chargesHydrogen': True,  'thickness': 50.0e-6,
                         'note': 'Charges hydrogen and it also cracks, so the fatigue debit is '
                                 'severe. Peen before plating to offset it.'},
    'electroless nickel': {'chargesHydrogen': True, 'thickness': 25.0e-6,
                           'note': 'Charges less than the electrolytic processes and still enough '
                                   'to require a bake above the threshold.'},
    'silver':           {'chargesHydrogen': True,  'thickness': 12.5e-6,
                         'note': 'Anti-galling on threaded stainless. Prohibited near hydrazine.'},
    'ivd aluminium':    {'chargesHydrogen': False, 'thickness': 25.0e-6,
                         'note': 'Ion vapour deposited. NO hydrogen charging at all, which is why '
                                 'it replaced cadmium on high strength steel.'},
    'anodise type II':  {'chargesHydrogen': False, 'thickness': 8.0e-6,
                         'note': 'Aluminium only. Carries a real fatigue debit because the anodic '
                                 'layer is brittle and cracks.'},
    'anodise type III': {'chargesHydrogen': False, 'thickness': 50.0e-6,
                         'note': 'Hard anodise. Thicker, harder and a larger fatigue debit.'}
}

# Thermal spray. Residual stress comes from the CTE mismatch between coating and substrate.
THERMAL_SPRAY = {
    'HVOF':         {'bondStrength': 70.0e6,  'porosity': 0.01, 'thickness': 300.0e-6,
                     'note': 'Dense, well bonded, low oxide. The aerospace default.'},
    'plasma':       {'bondStrength': 35.0e6,  'porosity': 0.05, 'thickness': 500.0e-6,
                     'note': 'Higher temperature, so it sprays ceramics that HVOF cannot.'},
    'cold spray':   {'bondStrength': 50.0e6,  'porosity': 0.005, 'thickness': 2000.0e-6,
                     'note': 'Solid state, so no oxidation and no thermal residual stress. Thick '
                             'deposits and dimensional restoration.'}
}

# ------------------------------------------------------------------------------------------------ #

class SurfaceTreatment:

    '''

    Peening, chemical and electrochemical removal, alpha case, plating and thermal spray.

    Primary Input Properties:
    -------------------------
    material : str
        Alloy key, passed to the materials database
    almenIntensity : float
        [m] arc height on the specified strip
    almenStrip / peeningMedia : str
    wallThickness : float
        [m], for the both-sides removal check

    Key Output Properties:
    ----------------------
    compressiveLayerDepth : float
        [m] from peening
    fatigueImprovementFactor : float
        [-] on the endurance limit
    stockRemoval : float
        [m] per surface
    alphaCaseRemoval : float
        [m] per surface, required for titanium

    Public Methods:
    ---------------
    setInputs(inputs)                        Load a configuration dictionary
    calculatePeening()                       Layer depth, coverage and the fatigue factor
    calculateStockRemoval(process, time)     Faraday or etch rate, both surfaces
    calculateAlphaCase(temperature, time)    Diffusion depth and the required removal
    checkPlatingBake(process)                ASTM F1940 trigger and the cycle
    calculateThermalSprayStress(process, ...) CTE mismatch residual stress
    generateReport(outputDir)                Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material and Geometry -- #

        self.material       = 'TI-6AL-4V'   # [case insensitive string]
        self.condition      = None          # [case insensitive string]
        self.alloyFamily    = 'titanium'    # [case insensitive string]
        self.wallThickness  = 0.0020        # [m]
        self.initialRoughness = 3.2e-6      # [m] Ra

        # -- Peening -- #

        self.almenIntensity = 0.20e-3       # [m], arc height
        self.almenStrip     = 'A'           # [case sensitive string]
        self.peeningMedia   = 'ceramic bead'  # [case insensitive string]
        self.peeningTime    = 120.0         # [s]
        self.saturationTime = 60.0          # [s], time to reach 98 percent coverage

        # -- Results -- #

        self.compressiveLayerDepth    = np.nan   # [m]
        self.surfaceCompressiveStress = np.nan   # [Pa]
        self.fatigueImprovementFactor = np.nan   # [-]
        self.coverage                 = np.nan   # [-]
        self.stockRemoval             = np.nan   # [m] per surface
        self.alphaCaseRemoval         = np.nan   # [m] per surface
        self.surfaceNotes             = []       # [list of str]

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

        optionalParams = ['condition', 'alloyFamily', 'wallThickness', 'initialRoughness',
                          'almenIntensity', 'almenStrip', 'peeningMedia', 'peeningTime',
                          'saturationTime']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculatePeening(self) -> dict:

        '''

        Compressive layer depth, coverage and the fatigue improvement factor.

        The compressive layer depth scales with the Almen intensity and the strip multiplier. The
        surface compressive stress saturates near half the yield strength, because that is where the
        material yields in compression and cannot hold more.

        COVERAGE FOLLOWS AN EXPONENTIAL SATURATION:

            C = 1 - exp(-t / t_saturation * ln(1 / (1 - 0.98)))

        Each impact lands randomly, so later impacts increasingly fall where earlier ones already
        have. Full coverage is DEFINED as 98 percent because 100 percent is asymptotic and
        unreachable, and that is why a specification calling for 200 percent coverage is not a typo:
        it means twice the time to reach 98 percent, and it is a time specification rather than a
        geometric one.

        THE FATIGUE BENEFIT IS REAL AND IT IS NOT PERMANENT. The compressive layer relaxes under
        thermal exposure and under high cyclic load, so a peened part that sees a stress relief
        afterwards has lost the benefit and nobody notices.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)
        strip      = ALMEN_STRIPS[self.almenStrip]
        media      = PEENING_MEDIA[self.peeningMedia]

        yieldStrength = properties['yieldStrength']

        # Layer depth scales with the intensity and the strip. Laser shock peening reaches far
        # deeper because the shock wave propagates rather than the shot deforming a dimple.
        depthFactor = 4.5 if self.peeningMedia == 'laser shock' else 1.0

        self.compressiveLayerDepth = (self.almenIntensity * strip['multiplier'] * 0.85 *
                                      depthFactor)

        # Surface compressive stress saturates near half yield
        self.surfaceCompressiveStress = -0.50 * yieldStrength

        # Coverage, exponential saturation
        rate = np.log(1.0 / (1.0 - COVERAGE_SATURATION)) / max(self.saturationTime, 1.0e-9)
        self.coverage = 1.0 - np.exp(-rate * self.peeningTime)

        coveragePercent = self.peeningTime / self.saturationTime * 100.0

        # Fatigue improvement. The benefit rises with the layer depth and is reduced by the surface
        # roughening the media causes.
        depthBenefit = 1.0 + 0.55 * np.tanh(self.compressiveLayerDepth / 0.15e-3)
        roughnessPenalty = 1.0 - 0.12 * media['roughnessFactor']

        self.fatigueImprovementFactor = depthBenefit * roughnessPenalty

        # Coverage below full removes most of the benefit
        if self.coverage < COVERAGE_SATURATION:
            self.fatigueImprovementFactor = 1.0 + (self.fatigueImprovementFactor - 1.0) * \
                                            (self.coverage / COVERAGE_SATURATION) ** 2

        result = {'almenIntensity': self.almenIntensity, 'almenStrip': self.almenStrip,
                  'media': self.peeningMedia,
                  'compressiveLayerDepth': self.compressiveLayerDepth,
                  'surfaceCompressiveStress': self.surfaceCompressiveStress,
                  'coverage': self.coverage,
                  'coveragePercentSpecification': coveragePercent,
                  'fatigueImprovementFactor': self.fatigueImprovementFactor,
                  'roughnessFactor': media['roughnessFactor'],
                  'mediaNote': media['note'], 'stripNote': strip['note']}

        lower, upper = strip['range']
        if not lower <= self.almenIntensity <= upper:
            self.surfaceNotes.append(
                f'An intensity of {self.almenIntensity * 1.0e3:.3f} mm is outside the '
                f'{lower * 1.0e3:.2f} to {upper * 1.0e3:.2f} mm range normally specified on the '
                f'{self.almenStrip} strip. Use a different strip.')

        if self.compressiveLayerDepth > 0.25 * self.wallThickness:
            self.surfaceNotes.append(
                f'The compressive layer of {self.compressiveLayerDepth * 1.0e3:.3f} mm is more than '
                f'a quarter of the {self.wallThickness * 1.0e3:.2f} mm wall. Peening one side of a '
                f'thin section bows it, because the compressive layer is unbalanced. Peen both '
                f'sides or accept the distortion.')

        if self.coverage < COVERAGE_SATURATION:
            self.surfaceNotes.append(
                f'Coverage is {self.coverage * 100.0:.1f} percent against the 98 percent that '
                f'defines full coverage, so most of the fatigue benefit has not been earned. '
                f'Coverage saturates exponentially, so the last few percent take as long as the '
                f'first eighty.')

        self.surfaceNotes.append(
            'The compressive layer relaxes under thermal exposure and under high cyclic load. A '
            'peened part that sees a stress relief afterwards has lost the benefit, and a part '
            'that is electropolished afterwards has had the layer removed outright.')

        return result

    def calculateStockRemoval(self, process: str = 'chemical mill',
                              processTime: float = 600.0,
                              etchRate: float = 25.0e-6) -> dict:

        '''

        Stock removal from a chemical or electrochemical process, from BOTH surfaces.

        For an electrochemical process the removal follows Faraday:

            thickness = I t M / (n F rho A)     equivalently  currentDensity * t * EW / (F rho)

        For chemical milling the rate is a chemical rate law and it is supplied as an etch rate.

        THE BOTH-SURFACES DOUBLING IS THE ERROR PEOPLE MAKE. A part immersed in an etchant is
        attacked on every wetted surface, so a wall loses stock from both sides and the thickness
        falls by twice the removal depth. A 0.15 mm etch on a 2 mm wall leaves 1.7 mm, not 1.85.

        Masking one side is possible and it is an extra operation with its own failure modes, so the
        default assumption should be that both sides are attacked.

        '''

        if process not in ELECTROCHEMICAL_PROCESSES:
            raise InvalidInputError(
                message       = f'Unknown process \'{process}\'.',
                parameterName = 'process', value = process,
                validRange    = str(sorted(ELECTROCHEMICAL_PROCESSES.keys()))
            )

        definition = ELECTROCHEMICAL_PROCESSES[process]
        properties = queryMaterial(self.material, self.condition, 293.15)
        chemistry  = DISSOLUTION_CHEMISTRY[self.alloyFamily]

        density = properties['density']

        if definition['currentDensity'] > 0.0:
            # Faraday, for the electrochemical processes
            self.stockRemoval = (definition['currentDensity'] * definition['efficiency'] *
                                 processTime * chemistry['equivalentWeight'] * 1.0e-3 /
                                 (FARADAY_CONSTANT * density))
            mechanism = 'Faraday'
        else:
            # Chemical etch rate, supplied per unit time
            self.stockRemoval = etchRate * processTime / 60.0
            mechanism = 'chemical etch rate'

        bothSurfaces = 2.0 * self.stockRemoval
        remainingWall = self.wallThickness - bothSurfaces

        # Roughness outcome
        finalRoughness = max(definition['roughnessFloor'],
                             self.initialRoughness * definition['roughnessRatio'])

        result = {'process': process, 'mechanism': mechanism,
                  'processTime': processTime,
                  'stockRemovalPerSurface': self.stockRemoval,
                  'stockRemovalBothSurfaces': bothSurfaces,
                  'initialWallThickness': self.wallThickness,
                  'remainingWallThickness': remainingWall,
                  'initialRoughness': self.initialRoughness,
                  'finalRoughness': finalRoughness,
                  'roughnessImprovement': self.initialRoughness / finalRoughness,
                  'note': definition['note']}

        if remainingWall <= 0.0:
            raise ProcessInfeasibleError(
                message = f'{process} for {processTime:.0f} s removes '
                          f'{self.stockRemoval * 1.0e3:.3f} mm from each surface, so '
                          f'{bothSurfaces * 1.0e3:.3f} mm from a {self.wallThickness * 1.0e3:.2f} '
                          f'mm wall. Nothing is left. Remember that an immersed part is attacked on '
                          f'both sides.'
            )

        if bothSurfaces > 0.25 * self.wallThickness:
            self.surfaceNotes.append(
                f'{process} removes {bothSurfaces * 1.0e3:.3f} mm total from a '
                f'{self.wallThickness * 1.0e3:.2f} mm wall, which is '
                f'{bothSurfaces / self.wallThickness * 100.0:.0f} percent of the section. Both '
                f'surfaces are attacked, so the wall loses twice the removal depth.')

        if process == 'electropolish' and not np.isnan(self.compressiveLayerDepth):
            self.surfaceNotes.append(
                f'Electropolishing removes {self.stockRemoval * 1.0e3:.3f} mm per surface, and the '
                f'peening compressive layer is {self.compressiveLayerDepth * 1.0e3:.3f} mm deep. '
                f'Electropolishing after peening removes the layer the peening was done to create. '
                f'The order is peen last.')

        return result

    def calculateAlphaCase(self, exposureTemperature: float, exposureTime: float) -> dict:

        '''

        Titanium alpha case depth from oxygen diffusion, and the removal it requires.

            depth = sqrt(D t),        D = D0 exp(-Q / R T)

        Above about 800 K titanium dissolves oxygen from the atmosphere, forming a hard, brittle,
        oxygen-enriched surface layer. It is not an oxide scale that flakes off; it is a solid
        solution in the metal itself and it must be machined or etched away.

        ALPHA CASE IS A FATIGUE CRACK INITIATION SITE AND ITS REMOVAL IS A REQUIRED SPECIFICATION,
        not an optional refinement. A hot formed titanium part with the case left on has a fatigue
        strength a fraction of the parent material and it will crack from the surface.

        The removal depth carries a safety factor over the computed case depth, because the
        diffusion depth is a nominal and the case boundary is diffuse rather than sharp.

        THE REMOVAL COMES OFF THE WALL and has to be added to the stock dimension. On a thin section
        that is a real fraction of the thickness.

        '''

        if self.alloyFamily != 'titanium':
            return {'applicable': False, 'material': self.material,
                    'note': f'Alpha case forms in titanium by oxygen dissolution. '
                            f'{self.material} is not a titanium alloy and does not form it.'}

        if exposureTemperature < 800.0:
            return {'applicable': True, 'caseDepth': 0.0, 'removalDepth': 0.0,
                    'exposureTemperature': exposureTemperature,
                    'note': f'At {exposureTemperature - 273.15:.0f} degC the oxygen diffusion rate '
                            f'is negligible. Alpha case forms above about 530 degC.'}

        diffusivity = ALPHA_CASE_DIFFUSIVITY * np.exp(-ALPHA_CASE_ACTIVATION /
                                                      (UNIVERSAL_GAS_CONSTANT * exposureTemperature))

        caseDepth = np.sqrt(diffusivity * exposureTime)

        self.alphaCaseRemoval = caseDepth * ALPHA_CASE_SAFETY

        bothSurfaces  = 2.0 * self.alphaCaseRemoval
        remainingWall = self.wallThickness - bothSurfaces

        result = {'applicable': True,
                  'exposureTemperature': exposureTemperature,
                  'exposureTime': exposureTime,
                  'diffusivity': diffusivity,
                  'caseDepth': caseDepth,
                  'safetyFactor': ALPHA_CASE_SAFETY,
                  'removalDepth': self.alphaCaseRemoval,
                  'removalBothSurfaces': bothSurfaces,
                  'remainingWallThickness': remainingWall,
                  'stockRequired': bothSurfaces}

        if remainingWall <= 0.0:
            raise ProcessInfeasibleError(
                message = f'Alpha case from {exposureTime / 3600.0:.1f} h at '
                          f'{exposureTemperature - 273.15:.0f} degC is '
                          f'{caseDepth * 1.0e3:.3f} mm deep, and removing it with the '
                          f'{ALPHA_CASE_SAFETY:.1f} safety factor from both surfaces takes '
                          f'{bothSurfaces * 1.0e3:.3f} mm from a {self.wallThickness * 1.0e3:.2f} '
                          f'mm wall. Nothing is left. Form under inert cover, or start from thicker '
                          f'stock.'
            )

        self.surfaceNotes.append(
            f'Alpha case is {caseDepth * 1.0e3:.3f} mm deep after {exposureTime / 3600.0:.1f} h at '
            f'{exposureTemperature - 273.15:.0f} degC. Removing it takes '
            f'{bothSurfaces * 1.0e3:.3f} mm off the wall, which has to be added to the stock '
            f'dimension. This is a required specification, not an optional refinement: the case is '
            f'a fatigue crack initiation site.')

        return result

    def checkPlatingBake(self, process: str = 'cadmium') -> dict:

        '''

        Hydrogen embrittlement relief bake requirement per ASTM F1940 and AMS 2759/9.

        THE TRIGGER IS THE TENSILE STRENGTH, NOT THE SERVICE. A part that never sees hydrogen
        propellant still gets hydrogen charged into it by electroplating, and above 1000 MPa
        ultimate that is enough to cause delayed brittle fracture days after assembly.

        The four hour window matters as much as the bake itself. Hydrogen diffuses to traps and
        cracks initiate during that time, so a bake started late removes the hydrogen from a part
        that has already cracked.

        '''

        if process not in PLATING_PROCESSES:
            raise InvalidInputError(
                message       = f'Unknown plating process \'{process}\'.',
                parameterName = 'process', value = process,
                validRange    = str(sorted(PLATING_PROCESSES.keys()))
            )

        definition = PLATING_PROCESSES[process]
        properties = queryMaterial(self.material, self.condition, 293.15)

        ultimate = properties.get('ultimateStrength', 0.0) or 0.0

        aboveThreshold = ultimate >= HYDROGEN_BAKE_THRESHOLD
        bakeRequired   = aboveThreshold and definition['chargesHydrogen']

        result = {'process': process,
                  'chargesHydrogen': definition['chargesHydrogen'],
                  'ultimateStrength': ultimate,
                  'threshold': HYDROGEN_BAKE_THRESHOLD,
                  'aboveThreshold': aboveThreshold,
                  'bakeRequired': bakeRequired,
                  'bakeTime': HYDROGEN_BAKE_TIME if bakeRequired else 0.0,
                  'bakeTemperature': HYDROGEN_BAKE_TEMPERATURE if bakeRequired else np.nan,
                  'startWindow': HYDROGEN_BAKE_START_WINDOW if bakeRequired else np.nan,
                  'coatingThickness': definition['thickness'],
                  'note': definition['note']}

        if bakeRequired:
            self.surfaceNotes.append(
                f'{self.material} at {ultimate / 1.0e6:.0f} MPa ultimate is above the '
                f'{HYDROGEN_BAKE_THRESHOLD / 1.0e6:.0f} MPa ASTM F1940 trigger, and {process} '
                f'charges hydrogen. A bake of {HYDROGEN_BAKE_TIME / 3600.0:.0f} h at '
                f'{HYDROGEN_BAKE_TEMPERATURE - 273.15:.0f} degC is required, started within '
                f'{HYDROGEN_BAKE_START_WINDOW / 3600.0:.0f} h of plating. The window matters as '
                f'much as the bake: hydrogen diffuses to traps and cracks initiate during it, so a '
                f'late bake removes hydrogen from a part that has already cracked.')

        if aboveThreshold and definition['chargesHydrogen'] and process in ('cadmium', 'zinc'):
            self.surfaceNotes.append(
                f'IVD aluminium is the standard replacement for {process} on high strength steel '
                f'and it charges no hydrogen at all, which removes the bake requirement rather than '
                f'managing it.')

        return result

    def calculateThermalSprayStress(self, process: str = 'HVOF',
                                    coatingExpansion: float = 12.0e-6,
                                    depositTemperature: float = 573.15) -> dict:

        '''

        Residual stress in a thermal spray coating from the CTE mismatch with the substrate.

            sigma = E dAlpha dT / (1 - nu)

        The coating is deposited hot and cools bonded to the substrate. If the coating contracts
        more than the substrate it ends in tension, which cracks it and lets corrosive media through
        to the interface. If it contracts less it ends in compression, which is benign and is why
        the mismatch sign is worth checking rather than assuming.

        Cold spray is the exception: it deposits in the solid state with no thermal excursion, so
        there is no thermal mismatch stress at all and the residual stress is compressive from the
        particle impact.

        '''

        if process not in THERMAL_SPRAY:
            raise InvalidInputError(
                message       = f'Unknown thermal spray process \'{process}\'.',
                parameterName = 'process', value = process,
                validRange    = str(sorted(THERMAL_SPRAY.keys()))
            )

        definition = THERMAL_SPRAY[process]
        properties = queryMaterial(self.material, self.condition, 293.15)

        substrateExpansion = properties.get('thermalExpansion', 12.0e-6)
        modulus = properties['elasticModulus']
        poisson = properties['poissonRatio']

        if process == 'cold spray':
            residualStress = -150.0e6
            mechanism = 'solid state particle impact, compressive'
        else:
            temperatureDrop = depositTemperature - 293.15
            expansionMismatch = coatingExpansion - substrateExpansion
            residualStress = modulus * expansionMismatch * temperatureDrop / (1.0 - poisson)
            mechanism = 'CTE mismatch on cooling'

        result = {'process': process, 'mechanism': mechanism,
                  'coatingExpansion': coatingExpansion,
                  'substrateExpansion': substrateExpansion,
                  'residualStress': residualStress,
                  'bondStrength': definition['bondStrength'],
                  'porosity': definition['porosity'],
                  'maximumThickness': definition['thickness'],
                  'note': definition['note']}

        if residualStress > 0.0 and residualStress > 0.5 * definition['bondStrength']:
            self.surfaceNotes.append(
                f'The {process} coating ends in {residualStress / 1.0e6:.0f} MPa tension against a '
                f'{definition["bondStrength"] / 1.0e6:.0f} MPa bond strength. A coating in tension '
                f'cracks, and the cracks let corrosive media through to the interface where they '
                f'undercut the bond. Match the coating expansion more closely, use a graded bond '
                f'coat, or spray cooler.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        peening = self.calculatePeening()

        properties = queryMaterial(self.material, self.condition, 293.15)

        rows = [
            ['Material',              f'{self.material} ({self.alloyFamily})'],
            ['Wall thickness',        f'{self.wallThickness * 1.0e3:.2f} mm'],
            ['Almen intensity',       f'{self.almenIntensity * 1.0e3:.3f} mm {self.almenStrip}'],
            ['Media',                 f'{self.peeningMedia}'],
            ['Compressive layer',     f'{self.compressiveLayerDepth * 1.0e3:.3f} mm'],
            ['Surface stress',        f'{self.surfaceCompressiveStress / 1.0e6:.0f} MPa'],
            ['Coverage',              f'{self.coverage * 100.0:.1f} % '
                                      f'({peening["coveragePercentSpecification"]:.0f} % spec)'],
            ['Fatigue factor',        f'{self.fatigueImprovementFactor:.3f}'],
            ['Initial roughness',     f'{self.initialRoughness * 1.0e6:.1f} um Ra']
        ]

        if not np.isnan(self.alphaCaseRemoval):
            rows.append(['Alpha case removal', f'{self.alphaCaseRemoval * 1.0e3:.3f} mm per surface'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'SURFACE TREATMENT')

        report += f'\n\nMEDIA NOTE\n{"-" * 60}\n{peening["mediaNote"]}\n'

        for note in self.surfaceNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'surfaceTreatment.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.almenStrip not in ALMEN_STRIPS:
            raise InvalidInputError(
                message       = f'Unknown Almen strip \'{self.almenStrip}\'.',
                parameterName = 'almenStrip', value = self.almenStrip,
                validRange    = str(sorted(ALMEN_STRIPS.keys()))
            )

        media = self.peeningMedia.strip().lower()

        if media not in PEENING_MEDIA:
            raise InvalidInputError(
                message       = f'Unknown peening media \'{self.peeningMedia}\'.',
                parameterName = 'peeningMedia', value = self.peeningMedia,
                validRange    = str(sorted(PEENING_MEDIA.keys()))
            )

        self.peeningMedia = media

        family = self.alloyFamily.strip().lower()

        if family not in DISSOLUTION_CHEMISTRY:
            raise InvalidInputError(
                message       = f'Unknown alloy family \'{self.alloyFamily}\'. The equivalent '
                                f'weight is needed for the Faraday calculation.',
                parameterName = 'alloyFamily', value = self.alloyFamily,
                validRange    = str(sorted(DISSOLUTION_CHEMISTRY.keys()))
            )

        self.alloyFamily = family

        for name, value in (('wallThickness', self.wallThickness),
                            ('almenIntensity', self.almenIntensity),
                            ('saturationTime', self.saturationTime)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0'
                )
