
# -- ExtrusionHoning Class Definition -- #

'''

Abrasive flow machining: media rheology, wall shear, the flow split across branching passages, and
surface finish decay.

Abrasive flow machining pushes a viscoelastic abrasive-laden putty back and forth through a passage.
The media acts as a self-conforming tool: it flows where the passage flows, so it reaches internal
geometry that no rigid tool can, and it removes material in proportion to the local wall shear
stress.

That last point is the whole engineering problem. Removal follows shear, shear follows the local
flow, and the flow follows the passage. **A restriction sees more media, more shear and more
removal, so it opens faster than the passage around it.** The process is self-correcting within a
single passage and it is the opposite of self-correcting across parallel branches, where the branch
that flows best gets honed most and takes an ever larger share.

    tau_w = dP D / (4 L)               wall shear from the pressure gradient
    Ra_N  = Ra_inf + (Ra_0 - Ra_inf) exp(-k N)     roughness decays exponentially to a floor

THE FLOW SPLIT IS WHY FIXTURING AND RESTRICTORS EXIST. A manifold with three branches of different
resistance does not hone evenly, and left alone the differences amplify. The fix is a restrictor
that deliberately throttles the easy branches until the flows match, and sizing it is what this
class is for.

See Also:
---------
LpbfProcess     : Where the as-built internal roughness comes from
SurfaceTreatment : External surfaces, which are finished by other means
fluidSystems/Line, Orifice : What the finished roughness feeds into

Theory: docs/MediaAndRheology.md, docs/FixturingAndFlowControl.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from honingUtils import (applyInputs, formatReportTable, roughnessTable, queryMaterial,
                             InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .honingUtils import (applyInputs, formatReportTable, roughnessTable, queryMaterial,
                              InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Media grades. The carrier is a viscoelastic polymer and the abrasive is suspended in it. Viscosity
# selects the passage size the media suits: a stiff media cannot enter a small passage, and a soft
# media flows through a large one without loading the wall.
#
# The consistency index K and the flow behaviour index n are the power law parameters:
#
#     tau = K gammaDot^n
#
# n well below one means strongly shear thinning, which is what lets the media both hold together in
# the fixture and flow through the passage.

MEDIA_GRADES = {
    'very soft': {'consistencyIndex': 2.0e3,  'flowIndex': 0.32, 'gritSize': 60.0e-6,
                  'minimumPassage': 0.0003, 'maximumPassage': 0.003, 'removalFactor': 0.45,
                  'note': 'Small passages and fine finishing. Low removal rate.'},
    'soft':      {'consistencyIndex': 6.0e3,  'flowIndex': 0.30, 'gritSize': 110.0e-6,
                  'minimumPassage': 0.0008, 'maximumPassage': 0.008, 'removalFactor': 0.70,
                  'note': 'The general purpose grade for small internal passages.'},
    'medium':    {'consistencyIndex': 1.6e4,  'flowIndex': 0.28, 'gritSize': 200.0e-6,
                  'minimumPassage': 0.002,  'maximumPassage': 0.020, 'removalFactor': 1.00,
                  'note': 'The reference grade. Most additive manifold work.'},
    'hard':      {'consistencyIndex': 4.5e4,  'flowIndex': 0.25, 'gritSize': 350.0e-6,
                  'minimumPassage': 0.005,  'maximumPassage': 0.050, 'removalFactor': 1.60,
                  'note': 'Large passages and heavy stock removal. Coarse finish floor.'},
    'very hard': {'consistencyIndex': 1.2e5,  'flowIndex': 0.22, 'gritSize': 550.0e-6,
                  'minimumPassage': 0.012,  'maximumPassage': 0.100, 'removalFactor': 2.40,
                  'note': 'Deburring and edge radiusing on large bores.'}
}

# Abrasive types. Hardness relative to the workpiece sets the removal efficiency.
ABRASIVE_TYPES = {
    'silicon carbide':   {'hardness': 2600.0, 'efficiency': 1.00,
                          'note': 'The default. Friable, so it self-sharpens.'},
    'aluminium oxide':   {'hardness': 2100.0, 'efficiency': 0.75,
                          'note': 'Tougher and less friable. Longer media life, slower removal.'},
    'boron carbide':     {'hardness': 3200.0, 'efficiency': 1.35,
                          'note': 'For nickel alloys and anything that work hardens under the '
                                  'abrasive. Expensive.'},
    'diamond':           {'hardness': 8000.0, 'efficiency': 1.80,
                          'note': 'Ceramics and carbides only. Rarely justified on metal.'}
}

# Surface finish decay. Roughness falls exponentially towards a floor set by the grit size, because
# the abrasive cannot produce a surface finer than the scratch it leaves.
#
#     Ra_inf ~ gritSize / 40
#
# THAT FLOOR IS THE MOST IMPORTANT LIMIT IN THE PROCESS. Running more cycles past it accomplishes
# nothing except removing stock and opening the passage. A finer finish needs a finer media, which
# needs a second setup.

ROUGHNESS_FLOOR_DIVISOR = 40.0     # [-], grit size to achievable Ra
ROUGHNESS_DECAY_RATE    = 0.28     # [1/cycle], the exponential decay constant

# Removal correlation. Radial removal per cycle scales with the wall shear stress and with the
# cycle count, both sub-linearly.
REMOVAL_SHEAR_EXPONENT = 1.15      # [-], removal against wall shear
REMOVAL_CYCLE_EXPONENT = 0.85      # [-], removal against cycle count, sub-linear as the passage opens

REMOVAL_COEFFICIENT = 2.2e-11      # [m per cycle per Pa^1.15], calibrated, see calculateRemoval

# Flow split. Branches are balanced when their flow fractions match to within this tolerance.
FLOW_BALANCE_TOLERANCE = 0.10      # [-]

# Edge radiusing. AFM rounds sharp edges as a side effect, which is usually wanted and occasionally
# is not, because it also rounds the orifice entries that were sized sharp.
EDGE_RADIUS_FACTOR = 0.55          # [-], edge radius as a fraction of the radial removal

# ------------------------------------------------------------------------------------------------ #

class ExtrusionHoning:

    '''

    Media selection, wall shear, removal, finish and flow balancing for abrasive flow machining.

    Primary Input Properties:
    -------------------------
    passageDiameter / passageLength : float
        [m]
    extrusionPressure : float
        [Pa]
    cycleCount : int
        Media passes, counting both directions as one cycle
    mediaGrade / abrasiveType : str
    initialRoughness : float
        [m] Ra, typically from roughnessTable('lpbf as-built')

    Key Output Properties:
    ----------------------
    wallShearStress : float
        [Pa]
    radialRemoval : float
        [m] of wall removed
    finalRoughness : float
        [m] Ra
    roughnessFloor : float
        [m] Ra, set by the grit size

    Public Methods:
    ---------------
    setInputs(inputs)                    Load a configuration dictionary
    selectMedia()                        Media grade from the passage size
    calculateWallShear()                 Shear stress and the apparent shear rate
    calculateRemoval()                   Radial removal, dimensional growth, edge radius
    calculateSurfaceFinish()             Exponential decay and the grit-limited floor
    calculateFlowSplit(branches)         Parallel branch flow fractions and restrictor sizing
    generateReport(outputDir)            Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Passage -- #

        self.passageDiameter  = 0.00476    # [m]
        self.passageLength    = 0.180      # [m]
        self.material         = 'INCONEL 718'   # [case insensitive string]
        self.condition        = None       # [case insensitive string]

        # -- Media and Process -- #

        self.mediaGrade       = None       # [case insensitive string], None selects by passage size
        self.abrasiveType     = 'silicon carbide'   # [case insensitive string]
        self.extrusionPressure = 7.0e6     # [Pa]
        self.cycleCount       = 20         # [-]
        self.initialRoughness = np.nan     # [m] Ra, nan takes the LPBF as-built value

        # -- Results -- #

        self.wallShearStress  = np.nan     # [Pa]
        self.radialRemoval    = np.nan     # [m]
        self.finalRoughness   = np.nan     # [m] Ra
        self.roughnessFloor   = np.nan     # [m] Ra
        self.honingNotes      = []         # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: passageDiameter.

        '''

        requiredParams = {
            'passageDiameter': 'Passage diameter not provided.'
        }

        optionalParams = ['passageLength', 'material', 'condition', 'mediaGrade', 'abrasiveType',
                          'extrusionPressure', 'cycleCount', 'initialRoughness']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        if np.isnan(self.initialRoughness):
            self.initialRoughness = roughnessTable('lpbf as-built')

        if self.mediaGrade is None:
            self.selectMedia()

    def selectMedia(self) -> dict:

        '''

        Media grade from the passage size.

        The media has to be soft enough to enter the passage and stiff enough to load the wall once
        it is in. Too stiff and it will not flow at any practical pressure; too soft and it passes
        through without doing work.

        The candidates are ordered by removal rate, and the fastest one that fits the passage wins,
        because cycle time is the cost.

        '''

        candidates = [name for name, grade in MEDIA_GRADES.items()
                      if grade['minimumPassage'] <= self.passageDiameter <= grade['maximumPassage']]

        if not candidates:
            smallest = min(MEDIA_GRADES.values(), key = lambda grade: grade['minimumPassage'])
            largest  = max(MEDIA_GRADES.values(), key = lambda grade: grade['maximumPassage'])
            raise ProcessInfeasibleError(
                message = f'A {self.passageDiameter * 1.0e3:.2f} mm passage is outside the range '
                          f'any media grade covers, which is {smallest["minimumPassage"] * 1.0e3:.2f} '
                          f'to {largest["maximumPassage"] * 1.0e3:.0f} mm. Below the lower bound the '
                          f'media cannot be extruded through the passage at any practical pressure.'
            )

        # Fastest removal among the candidates
        self.mediaGrade = max(candidates, key = lambda name: MEDIA_GRADES[name]['removalFactor'])

        grade = MEDIA_GRADES[self.mediaGrade]

        return {'selected': self.mediaGrade, 'candidates': candidates,
                'passageDiameter': self.passageDiameter,
                'gritSize': grade['gritSize'],
                'roughnessFloor': grade['gritSize'] / ROUGHNESS_FLOOR_DIVISOR,
                'note': grade['note']}

    def calculateWallShear(self) -> dict:

        '''

        Wall shear stress and the apparent shear rate.

            tau_w = dP D / (4 L)

        This is a force balance on the media column and it does not depend on the rheology at all:
        the pressure drop across the passage has to be reacted by shear on the wall, whatever the
        media is made of.

        The rheology enters through the shear RATE, which is what determines whether the media
        actually flows:

            tau = K gammaDot^n            so       gammaDot = (tau / K)^(1/n)

        With n around 0.28 the media is strongly shear thinning, which is the property that makes
        the process work: it is stiff enough to stay in the fixture and hold the abrasive in
        suspension, and it thins dramatically once it is being forced through a passage.

        THE INVERSE DIAMETER DEPENDENCE IS WHY SMALL PASSAGES ARE HARD. At a fixed pressure and
        length, halving the diameter halves the wall shear, so the removal rate falls with it. Small
        passages need higher pressure, more cycles, or both.

        '''

        grade = MEDIA_GRADES[self.mediaGrade]

        self.wallShearStress = (self.extrusionPressure * self.passageDiameter /
                                (4.0 * self.passageLength))

        # Apparent shear rate from the power law
        shearRate = (self.wallShearStress / grade['consistencyIndex']) ** (1.0 / grade['flowIndex'])

        # Apparent viscosity at that rate
        apparentViscosity = self.wallShearStress / max(shearRate, 1.0e-12)

        # Mean velocity, from the power law solution for a circular passage
        radius = self.passageDiameter / 2.0
        exponent = 1.0 / grade['flowIndex']
        meanVelocity = (grade['flowIndex'] / (3.0 * grade['flowIndex'] + 1.0)) * radius * \
                       (self.wallShearStress / grade['consistencyIndex']) ** exponent

        return {'extrusionPressure': self.extrusionPressure,
                'passageDiameter': self.passageDiameter,
                'passageLength': self.passageLength,
                'wallShearStress': self.wallShearStress,
                'consistencyIndex': grade['consistencyIndex'],
                'flowIndex': grade['flowIndex'],
                'apparentShearRate': shearRate,
                'apparentViscosity': apparentViscosity,
                'meanVelocity': meanVelocity,
                'lengthToDiameter': self.passageLength / self.passageDiameter}

    def calculateRemoval(self) -> dict:

        '''

        Radial removal, dimensional growth and edge radius.

            deltaR = C tau_w^a N^b

        Both exponents are below one. The shear exponent is 1.15 rather than 1.0 because higher
        shear both presses the abrasive harder into the wall and increases the number of particles
        passing per unit time, so the two effects compound slightly. The cycle exponent is 0.85
        because the passage opens as it is honed, which drops the wall shear, which slows the
        removal: the process self-limits.

        DIMENSIONAL GROWTH IS THE CONSEQUENCE PEOPLE FORGET. Removing material from the wall of a
        passage opens it, so an orifice that was sized before honing is no longer the size it was.
        On a flow-critical passage the honing has to be in the tolerance stack, or the orifice has
        to be sized after it.

        Edge radiusing comes free and is usually wanted. Occasionally it is not, because it also
        rounds the sharp orifice entries that were sized sharp, and a rounded entry has a different
        discharge coefficient.

        '''

        if np.isnan(self.wallShearStress):
            self.calculateWallShear()

        grade    = MEDIA_GRADES[self.mediaGrade]
        abrasive = ABRASIVE_TYPES[self.abrasiveType]

        # Workpiece hardness scales the removal inversely
        try:
            properties = queryMaterial(self.material, self.condition, 293.15)
            hardness = properties.get('hardness', 250.0) or 250.0
        except Exception:
            hardness = 250.0

        hardnessFactor = (250.0 / hardness) ** 0.5

        self.radialRemoval = (REMOVAL_COEFFICIENT *
                              self.wallShearStress ** REMOVAL_SHEAR_EXPONENT *
                              self.cycleCount ** REMOVAL_CYCLE_EXPONENT *
                              grade['removalFactor'] * abrasive['efficiency'] * hardnessFactor)

        diametralGrowth = 2.0 * self.radialRemoval
        finalDiameter   = self.passageDiameter + diametralGrowth

        edgeRadius = self.radialRemoval * EDGE_RADIUS_FACTOR

        # Volume removed, for the media loading estimate
        volumeRemoved = np.pi * self.passageDiameter * self.passageLength * self.radialRemoval

        result = {'wallShearStress': self.wallShearStress,
                  'cycleCount': self.cycleCount,
                  'mediaGrade': self.mediaGrade,
                  'abrasiveType': self.abrasiveType,
                  'hardness': hardness, 'hardnessFactor': hardnessFactor,
                  'radialRemoval': self.radialRemoval,
                  'diametralGrowth': diametralGrowth,
                  'initialDiameter': self.passageDiameter,
                  'finalDiameter': finalDiameter,
                  'diametralGrowthPercent': diametralGrowth / self.passageDiameter * 100.0,
                  'edgeRadius': edgeRadius,
                  'volumeRemoved': volumeRemoved}

        if diametralGrowth > 0.02 * self.passageDiameter:
            self.honingNotes.append(
                f'The passage grows {diametralGrowth * 1.0e6:.0f} um on diameter, which is '
                f'{result["diametralGrowthPercent"]:.1f} percent. An orifice sized before honing is '
                f'no longer the size it was, and on a flow-critical passage the honing has to be in '
                f'the tolerance stack or the orifice has to be sized afterwards.')

        self.honingNotes.append(
            f'Edge radiusing of about {edgeRadius * 1.0e6:.0f} um comes free with the process. That '
            f'is usually wanted, and it also rounds any sharp orifice entry that was sized sharp, '
            f'which changes its discharge coefficient.')

        return result

    def calculateSurfaceFinish(self) -> dict:

        '''

        Surface finish decay towards the grit-limited floor.

            Ra_N = Ra_inf + (Ra_0 - Ra_inf) exp(-k N)

        Roughness falls exponentially because each cycle removes the remaining peaks and the peaks
        get progressively harder to reach. It asymptotes to a floor set by the grit size, because
        the abrasive cannot produce a surface finer than the scratch it leaves:

            Ra_inf ~ gritSize / 40

        THE FLOOR IS THE MOST IMPORTANT LIMIT IN THE PROCESS. Running more cycles past it
        accomplishes nothing except removing stock and opening the passage. A finer finish requires
        a finer media in a second setup, and that is a real cost that has to be planned rather than
        discovered.

        The improvement ratio against the as-built LPBF surface is the number that justifies the
        process at all, and a test asserts it matches the roughnessTable entries in the shared
        package so the two cannot drift.

        '''

        grade = MEDIA_GRADES[self.mediaGrade]

        self.roughnessFloor = grade['gritSize'] / ROUGHNESS_FLOOR_DIVISOR

        if self.initialRoughness <= self.roughnessFloor:
            self.finalRoughness = self.initialRoughness
            self.honingNotes.append(
                f'The initial roughness of {self.initialRoughness * 1.0e6:.1f} um is already at or '
                f'below the {self.roughnessFloor * 1.0e6:.1f} um floor for '
                f'{self.mediaGrade} media. Honing will not improve it and will only remove stock. '
                f'A finer media is needed.')
        else:
            self.finalRoughness = (self.roughnessFloor +
                                   (self.initialRoughness - self.roughnessFloor) *
                                   np.exp(-ROUGHNESS_DECAY_RATE * self.cycleCount))

        improvement = self.initialRoughness / self.finalRoughness

        # Cycles to reach within 10 percent of the floor
        if self.initialRoughness > self.roughnessFloor:
            target = self.roughnessFloor * 1.10
            if target < self.initialRoughness:
                cyclesToFloor = -np.log((target - self.roughnessFloor) /
                                        (self.initialRoughness - self.roughnessFloor)) / \
                                ROUGHNESS_DECAY_RATE
            else:
                cyclesToFloor = 0.0
        else:
            cyclesToFloor = 0.0

        result = {'initialRoughness': self.initialRoughness,
                  'finalRoughness': self.finalRoughness,
                  'roughnessFloor': self.roughnessFloor,
                  'gritSize': grade['gritSize'],
                  'improvementRatio': improvement,
                  'cycleCount': self.cycleCount,
                  'cyclesToReachFloor': cyclesToFloor,
                  'drawnTubeReference': roughnessTable('drawn tube'),
                  'ratioToDrawnTube': self.finalRoughness / roughnessTable('drawn tube')}

        if self.cycleCount > 2.0 * cyclesToFloor and cyclesToFloor > 0.0:
            self.honingNotes.append(
                f'{self.cycleCount} cycles is well past the {cyclesToFloor:.0f} needed to reach the '
                f'finish floor. The extra cycles remove stock and open the passage without '
                f'improving the finish. Stop at the floor or change to a finer media.')

        return result

    def calculateFlowSplit(self, branches: list) -> dict:

        '''

        Flow fractions across parallel branches, and the restrictor sizing that balances them.

        Each branch is supplied as a dict with 'diameter' and 'length'. For a power law fluid the
        conductance of a circular passage scales as

            Q ~ D^(3 + 1/n) / L^(1/n)

        and with n near 0.28 the diameter exponent is above six. THAT IS THE WHOLE PROBLEM. A ten
        percent diameter difference between two branches produces a seventy percent flow
        difference, and the branch that flows more gets honed more, opens further, and takes an even
        larger share.

        The process is self-correcting within one passage, where a restriction sees more shear and
        opens faster. It is exactly the opposite across parallel branches, where the differences
        amplify with every cycle.

        THIS IS WHY FIXTURING AND RESTRICTORS EXIST. The fix is to deliberately throttle the easy
        branches until the flows match, and the required restrictor area follows from the
        conductance ratio.

        '''

        if not branches:
            raise InvalidInputError(
                message       = 'At least one branch is needed.',
                parameterName = 'branches', value = branches, validRange = 'A non-empty list'
            )

        grade = MEDIA_GRADES[self.mediaGrade]
        exponent = 1.0 / grade['flowIndex']

        conductances = []
        for index, branch in enumerate(branches):
            diameter = branch.get('diameter')
            length   = branch.get('length')
            if diameter is None or length is None or diameter <= 0.0 or length <= 0.0:
                raise InvalidInputError(
                    message       = f'Branch {index} needs a positive diameter and length.',
                    parameterName = 'branches', value = branch,
                    validRange    = "Each branch needs 'diameter' and 'length'"
                )
            conductance = diameter ** (3.0 + exponent) / length ** exponent
            conductances.append(conductance)

        conductances = np.array(conductances)
        total = float(np.sum(conductances))
        fractions = conductances / total

        idealFraction = 1.0 / len(branches)
        imbalance = float(np.max(np.abs(fractions - idealFraction)) / idealFraction)

        # Restrictor sizing: throttle every branch down to the worst one so the flows match
        worstConductance = float(np.min(conductances))
        restrictorRatios = worstConductance / conductances

        # Removal scales with the flow fraction, so unbalanced flow means unbalanced removal
        removalRatios = fractions / float(np.min(fractions))

        branchResults = []
        for index, branch in enumerate(branches):
            branchResults.append({
                'index': index,
                'diameter': branch['diameter'],
                'length': branch['length'],
                'conductance': float(conductances[index]),
                'flowFraction': float(fractions[index]),
                'relativeRemoval': float(removalRatios[index]),
                'restrictorAreaRatio': float(restrictorRatios[index]),
                'needsRestrictor': bool(restrictorRatios[index] < 0.95)})

        balanced = imbalance <= FLOW_BALANCE_TOLERANCE

        result = {'branches': branchResults,
                  'diameterExponent': 3.0 + exponent,
                  'idealFraction': idealFraction,
                  'imbalance': imbalance,
                  'balanced': balanced,
                  'tolerance': FLOW_BALANCE_TOLERANCE,
                  'maximumRemovalRatio': float(np.max(removalRatios))}

        if not balanced:
            worst = max(branchResults, key = lambda entry: entry['relativeRemoval'])
            self.honingNotes.append(
                f'The branches are unbalanced by {imbalance * 100.0:.0f} percent against a '
                f'{FLOW_BALANCE_TOLERANCE * 100.0:.0f} percent tolerance. Branch '
                f'{worst["index"]} takes {worst["flowFraction"] * 100.0:.0f} percent of the flow '
                f'and will be honed {worst["maximumRemovalRatio"] if "maximumRemovalRatio" in worst else result["maximumRemovalRatio"]:.1f} '
                f'times as much as the least favoured one. With a diameter exponent of '
                f'{3.0 + exponent:.1f} the differences amplify with every cycle rather than '
                f'evening out. Restrictors are needed on the favoured branches.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        shear   = self.calculateWallShear()
        removal = self.calculateRemoval()
        finish  = self.calculateSurfaceFinish()

        grade    = MEDIA_GRADES[self.mediaGrade]
        abrasive = ABRASIVE_TYPES[self.abrasiveType]

        rows = [
            ['Passage',              f'{self.passageDiameter * 1.0e3:.2f} mm dia x '
                                     f'{self.passageLength * 1.0e3:.0f} mm '
                                     f'(L/D = {shear["lengthToDiameter"]:.0f})'],
            ['Material',             f'{self.material}'],
            ['Media grade',          f'{self.mediaGrade} '
                                     f'({grade["gritSize"] * 1.0e6:.0f} um grit)'],
            ['Abrasive',             f'{self.abrasiveType}'],
            ['Extrusion pressure',   f'{self.extrusionPressure / 1.0e6:.1f} MPa'],
            ['Cycles',               f'{self.cycleCount}'],
            ['Wall shear stress',    f'{self.wallShearStress / 1.0e3:.1f} kPa'],
            ['Apparent shear rate',  f'{shear["apparentShearRate"]:.1f} 1/s'],
            ['Radial removal',       f'{self.radialRemoval * 1.0e6:.1f} um'],
            ['Diametral growth',     f'{removal["diametralGrowth"] * 1.0e6:.1f} um '
                                     f'({removal["diametralGrowthPercent"]:.2f} %)'],
            ['Final diameter',       f'{removal["finalDiameter"] * 1.0e3:.3f} mm'],
            ['Edge radius',          f'{removal["edgeRadius"] * 1.0e6:.0f} um'],
            ['Initial roughness',    f'{self.initialRoughness * 1.0e6:.1f} um Ra'],
            ['Final roughness',      f'{self.finalRoughness * 1.0e6:.2f} um Ra'],
            ['Roughness floor',      f'{self.roughnessFloor * 1.0e6:.2f} um Ra (grit limited)'],
            ['Improvement',          f'{finish["improvementRatio"]:.1f} x'],
            ['Versus drawn tube',    f'{finish["ratioToDrawnTube"]:.1f} x']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'EXTRUSION HONING')

        report += f'\n\nMEDIA NOTE\n{"-" * 60}\n{grade["note"]}\n'
        report += f'\nABRASIVE NOTE\n{"-" * 60}\n{abrasive["note"]}\n'

        for note in self.honingNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'extrusionHoning.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.mediaGrade is not None:
            grade = self.mediaGrade.strip().lower()
            if grade not in MEDIA_GRADES:
                raise InvalidInputError(
                    message       = f'Unknown media grade \'{self.mediaGrade}\'.',
                    parameterName = 'mediaGrade', value = self.mediaGrade,
                    validRange    = str(sorted(MEDIA_GRADES.keys()))
                )
            self.mediaGrade = grade

        abrasive = self.abrasiveType.strip().lower()

        if abrasive not in ABRASIVE_TYPES:
            raise InvalidInputError(
                message       = f'Unknown abrasive type \'{self.abrasiveType}\'.',
                parameterName = 'abrasiveType', value = self.abrasiveType,
                validRange    = str(sorted(ABRASIVE_TYPES.keys()))
            )

        self.abrasiveType = abrasive

        for name, value in (('passageDiameter', self.passageDiameter),
                            ('passageLength', self.passageLength),
                            ('extrusionPressure', self.extrusionPressure)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0'
                )

        if self.cycleCount < 1:
            raise InvalidInputError(
                message       = 'At least one cycle is needed.',
                parameterName = 'cycleCount', value = self.cycleCount, validRange = 'At least 1'
            )
