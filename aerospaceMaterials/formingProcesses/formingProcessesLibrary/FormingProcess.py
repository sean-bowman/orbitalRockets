
# -- FormingProcess Class Definition -- #

'''

Bend radius, springback, forming limits and work hardening for sheet and tube forming.

Forming is how most thin-walled launch vehicle structure is made and it has the best buy-to-fly of
any conventional route, because it moves material rather than removing it. It is also the route
where the analysis is most directly useful, because four separate questions all have closed-form
answers:

    Can it be bent?      Minimum bend radius follows from the reduction of area, which is a
                         ductility measurement, not a strength one.

    Where does it end
    up?                  Springback has a closed form. A part bent to the drawing angle comes out
                         of the tool at a different angle, every time, and the tool has to be cut
                         for the compensated angle rather than the drawn one.

    Will it tear?        The forming limit diagram bounds the major and minor strain, and the
                         failure is a local neck rather than a general one.

    What is it worth
    afterwards?          Cold work raises the strength of the formed section and spends the
                         ductility that raised it. Both halves matter and only the first is
                         usually claimed.

See Also:
---------
MaterialDatabase : Reduction of area and the work hardening exponent
Allowables       : Where the cold work strength gain would have to be substantiated to be claimed
HeatTreatment    : Interstage annealing, when the accumulated strain forces it

Theory: docs/BendingAndSpringback.md, docs/FormingLimits.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from formingUtils import (applyInputs, formatReportTable, queryMaterial,
                              InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .formingUtils import (applyInputs, formatReportTable, queryMaterial,
                               InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Work hardening parameters for the Hollomon relation, sigma = K eps^n. The exponent n is also the
# uniform elongation, which is a useful identity: a material necks when the strain reaches n, so a
# high n material both hardens more and stretches further before it necks.

WORK_HARDENING = {
    '316L':      {'strengthCoefficient': 1275.0e6, 'hardeningExponent': 0.45,
                  'anisotropyRatio': 1.0, 'note': 'Austenitic stainless has an unusually high n, '
                                                  'which is why it deep draws so well.'},
    '304L':      {'strengthCoefficient': 1400.0e6, 'hardeningExponent': 0.45,
                  'anisotropyRatio': 1.0, 'note': 'As 316L. Strain induced martensite raises the '
                                                  'hardening rate further at large strain.'},
    '6061':      {'strengthCoefficient': 400.0e6,  'hardeningExponent': 0.20,
                  'anisotropyRatio': 0.7, 'note': 'Form in the O or T4 temper and age afterwards. '
                                                  'T6 has very little formability left.'},
    '2219':      {'strengthCoefficient': 620.0e6,  'hardeningExponent': 0.18,
                  'anisotropyRatio': 0.7, 'note': 'Formed in the O or W temper for tank domes.'},
    '2024':      {'strengthCoefficient': 690.0e6,  'hardeningExponent': 0.16,
                  'anisotropyRatio': 0.7, 'note': 'Formed in the O or W temper, aged afterwards.'},
    '7075':      {'strengthCoefficient': 780.0e6,  'hardeningExponent': 0.13,
                  'anisotropyRatio': 0.7, 'note': 'Poor formability in any temper. Machine it.'},
    'TI-6AL-4V': {'strengthCoefficient': 1300.0e6, 'hardeningExponent': 0.08,
                  'anisotropyRatio': 2.0, 'note': 'Very low n, so it forms hot. Cold forming is '
                                                  'limited to gentle radii and the springback is '
                                                  'severe because the modulus is low relative to '
                                                  'the strength.'},
    'INCONEL 718': {'strengthCoefficient': 1800.0e6, 'hardeningExponent': 0.25,
                    'anisotropyRatio': 1.0, 'note': 'Form solution annealed and age the assembly.'},
    'INCONEL 625': {'strengthCoefficient': 1600.0e6, 'hardeningExponent': 0.35,
                    'anisotropyRatio': 1.0, 'note': 'Excellent formability, which is part of why '
                                                    'bellows are made from it.'}
}

# Forming processes and their strain capability.
FORMING_PROCESSES = {
    'air bend':        {'maximumStrain': 0.20, 'springbackFactor': 1.00,
                        'note': 'The cheapest bend. Springback is largest because the tool does not '
                                'set the material.'},
    'bottoming':       {'maximumStrain': 0.20, 'springbackFactor': 0.40,
                        'note': 'Coining the bend against the die reduces springback substantially.'},
    'roll form':       {'maximumStrain': 0.15, 'springbackFactor': 1.00,
                        'note': 'Progressive, so each pass adds a little strain.'},
    'stretch form':    {'maximumStrain': 0.10, 'springbackFactor': 0.25,
                        'note': 'Stretching past yield across the whole section nearly eliminates '
                                'springback, which is why it is used for contoured skins.'},
    'deep draw':       {'maximumStrain': 0.50, 'springbackFactor': 0.60,
                        'note': 'Limited by the limiting draw ratio rather than by a single strain.'},
    'hydroform':       {'maximumStrain': 0.35, 'springbackFactor': 0.30,
                        'note': 'Pressure forms against a single die half. Excellent thickness '
                                'uniformity.'},
    'flow form':       {'maximumStrain': 0.75, 'springbackFactor': 0.10,
                        'note': 'Very high strain because the deformation is incremental and highly '
                                'compressive. The cold work raises the strength substantially.'},
    'spin form':       {'maximumStrain': 0.40, 'springbackFactor': 0.20,
                        'note': 'Incremental, so the achievable strain is far above a single hit.'},
    'superplastic':    {'maximumStrain': 3.00, 'springbackFactor': 0.05,
                        'note': 'Requires a fine stable grain size and a controlled strain rate. '
                                'Very slow, and it forms shapes nothing else can.'}
}

# Forming limit diagram. The FLD0 value is the major strain at plane strain, which is the lowest
# point on the curve and therefore the critical condition. It scales with the hardening exponent and
# the thickness.
FLD_THICKNESS_REFERENCE = 0.001    # [m], the reference thickness for the FLD0 correlation

# Springback. The closed form for a wide sheet in pure bending relates the radius before and after
# release to the elastic strain at the surface.
SPRINGBACK_CUBIC_COEFFICIENT = 4.0
SPRINGBACK_LINEAR_COEFFICIENT = 3.0

# Interstage annealing. Above this accumulated effective strain most alloys have consumed their
# formability and need a recrystallisation anneal before further work.
ANNEAL_STRAIN_THRESHOLD = 0.50     # [-]

# ------------------------------------------------------------------------------------------------ #

class FormingProcess:

    '''

    Bend radius, springback, forming limits and work hardening for a formed part.

    Primary Input Properties:
    -------------------------
    material : str
        Key into WORK_HARDENING
    process : str
        Key into FORMING_PROCESSES
    thickness : float
        [m]
    bendRadius / bendAngle : float
        [m] and [deg]

    Key Output Properties:
    ----------------------
    minimumBendRadius : float
        [m], from the reduction of area
    springbackAngle : float
        [deg] the part opens after release
    compensatedAngle : float
        [deg] the tool must be cut to
    formedYieldStrength : float
        [Pa] after the cold work

    Public Methods:
    ---------------
    setInputs(inputs)                   Load a configuration dictionary
    calculateMinimumBendRadius()        From reduction of area, and the grain direction effect
    calculateSpringback()               Closed form, and the tool compensation
    calculateBendAllowance()            Neutral axis, k-factor and the flat pattern
    checkFormingLimit(major, minor)     Against the forming limit diagram
    calculateWorkHardening(strain)      Strength gained and ductility spent
    calculateHydroformPressure()        Pressure to form against the die
    generateReport(outputDir)           Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material and Geometry -- #

        self.material        = '316L'        # [case insensitive string]
        self.condition       = None          # [case insensitive string], None takes the first
        self.process         = 'air bend'    # [case insensitive string]
        self.thickness       = 0.0016        # [m]
        self.bendRadius      = 0.0032        # [m], inner radius
        self.bendAngle       = 90.0          # [deg]
        self.grainDirection  = 'transverse'  # [-], 'transverse' or 'parallel' to the bend line
        self.partDiameter    = 0.200         # [m], for hydroforming

        # -- Results -- #

        self.minimumBendRadius   = np.nan    # [m]
        self.springbackAngle     = np.nan    # [deg]
        self.compensatedAngle    = np.nan    # [deg]
        self.formedYieldStrength = np.nan    # [Pa]
        self.formingNotes        = []        # [list of str]

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

        optionalParams = ['condition', 'process', 'thickness', 'bendRadius', 'bendAngle',
                          'grainDirection', 'partDiameter']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateMinimumBendRadius(self) -> dict:

        '''

        Minimum bend radius from the reduction of area.

            r_min / t = (50 / RA) - 1              RA as a percentage

        The relation says something worth stating plainly: BEND RADIUS IS A DUCTILITY LIMIT, NOT A
        STRENGTH LIMIT. The outer fibre of a bend is in tension, and it fails when the local strain
        exceeds what the material can absorb. Reduction of area is the direct measure of that, and
        the yield strength does not appear.

        At RA = 50 percent the formula gives r_min = 0, meaning the material can be folded flat on
        itself. Below about RA = 25 percent a bend needs a radius larger than the thickness, and
        below 10 percent the material is not a forming material at all.

        GRAIN DIRECTION MATTERS AND IT IS THE COMMONEST OMISSION. Bending across the rolling
        direction, so that the bend line runs transverse to the grain, is the favourable case.
        Bending along the grain puts the elongated grain boundaries directly in the tensile outer
        fibre and roughly doubles the required radius.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)

        reductionOfArea = properties.get('reductionOfArea')

        if reductionOfArea is None:
            raise InvalidInputError(
                message       = f'No reduction of area for {self.material} in the '
                                f'{properties["condition"]} condition. Bend radius is a ductility '
                                f'limit and it cannot be computed from strength data.',
                parameterName = 'material', value = self.material,
                validRange    = 'A material with reductionOfArea in its typical block'
            )

        reductionPercent = reductionOfArea * 100.0

        ratio = max(0.0, (50.0 / reductionPercent) - 1.0)

        # Bending parallel to the grain puts the elongated boundaries in the tensile fibre.
        directionFactor = 2.0 if self.grainDirection == 'parallel' else 1.0

        self.minimumBendRadius = ratio * self.thickness * directionFactor

        actualRatio = self.bendRadius / self.thickness

        result = {'reductionOfArea': reductionOfArea,
                  'minimumRatio': ratio * directionFactor,
                  'minimumBendRadius': self.minimumBendRadius,
                  'actualBendRadius': self.bendRadius,
                  'actualRatio': actualRatio,
                  'grainDirection': self.grainDirection,
                  'directionFactor': directionFactor,
                  'acceptable': self.bendRadius >= self.minimumBendRadius}

        if self.bendRadius < self.minimumBendRadius:
            raise ProcessInfeasibleError(
                message = f'A {self.bendRadius * 1.0e3:.2f} mm inner radius on '
                          f'{self.thickness * 1.0e3:.2f} mm {self.material} is below the '
                          f'{self.minimumBendRadius * 1.0e3:.2f} mm minimum for a reduction of area '
                          f'of {reductionPercent:.0f} percent bending '
                          f'{self.grainDirection} to the grain. The outer fibre will crack. Either '
                          f'open the radius, bend across the grain instead of along it, or form in '
                          f'a softer condition and heat treat afterwards.'
            )

        if self.grainDirection == 'parallel':
            self.formingNotes.append(
                'Bending parallel to the grain doubles the minimum radius, because the elongated '
                'grain boundaries lie directly in the tensile outer fibre. Rotating the blank so '
                'the bend line runs transverse to the rolling direction is free and it halves the '
                'requirement.')

        return result

    def calculateSpringback(self) -> dict:

        '''

        Springback, in closed form, and the tool compensation it demands.

        For a wide sheet in pure bending, the ratio of the radius before and after release is

            R_i / R_f = 4 (R_i F_ty / (E t))^3 - 3 (R_i F_ty / (E t)) + 1

        The governing group is R F_ty / (E t), the ratio of the yield strain to the bend strain.
        Everything follows from it:

            High strength      More springback. A titanium bend springs back far more than a
                               stainless one at the same geometry.
            Low modulus        More springback, for the same reason. Titanium is doubly penalised
                               because it is strong AND compliant.
            Large radius       More springback. A gentle bend barely yields the section.
            Thin material      More springback.

        A PART BENT TO THE DRAWING ANGLE COMES OUT WRONG, EVERY TIME. The tool has to be cut to the
        compensated angle, and that is a tooling decision made from this calculation rather than by
        iterating on scrap parts.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)
        process    = FORMING_PROCESSES[self.process]

        yieldStrength = properties['yieldStrength']
        modulus       = properties['elasticModulus']

        # The governing dimensionless group
        group = self.bendRadius * yieldStrength / (modulus * self.thickness)

        radiusRatio = (SPRINGBACK_CUBIC_COEFFICIENT * group ** 3 -
                       SPRINGBACK_LINEAR_COEFFICIENT * group + 1.0)
        radiusRatio = float(np.clip(radiusRatio, 0.05, 1.0))

        finalRadius = self.bendRadius / radiusRatio

        # Angle springback follows from the arc length being preserved
        finalAngle = self.bendAngle * radiusRatio

        self.springbackAngle = (self.bendAngle - finalAngle) * process['springbackFactor']
        self.compensatedAngle = self.bendAngle + self.springbackAngle

        result = {'governingGroup': group,
                  'radiusRatio': radiusRatio,
                  'targetRadius': self.bendRadius,
                  'releasedRadius': finalRadius,
                  'targetAngle': self.bendAngle,
                  'springbackAngle': self.springbackAngle,
                  'compensatedAngle': self.compensatedAngle,
                  'processFactor': process['springbackFactor'],
                  'processNote': process['note']}

        if self.springbackAngle > 5.0:
            self.formingNotes.append(
                f'Springback of {self.springbackAngle:.1f} degrees is large. The tool has to be cut '
                f'to {self.compensatedAngle:.1f} degrees to land on '
                f'{self.bendAngle:.0f}. Bottoming or stretch forming would reduce it by a factor of '
                f'two to four if the geometry allows.')

        return result

    def calculateBendAllowance(self) -> dict:

        '''

        Bend allowance and the k-factor, for the flat pattern.

            BA = angle (R + k t)                   angle in radians

        The k-factor locates the neutral axis as a fraction of the thickness from the inside
        surface. It is not 0.5, and the reason is that the material on the inside of the bend is in
        compression and thickens while the outside is in tension and thins, so the neutral axis
        migrates towards the inside.

        A tight bend has a lower k-factor than a gentle one, which is why a single assumed value
        produces flat patterns that are wrong for one end of the radius range.

        '''

        ratio = self.bendRadius / self.thickness

        # Empirical k-factor migration with the radius to thickness ratio
        if ratio < 1.0:
            kFactor = 0.33
        elif ratio < 3.0:
            kFactor = 0.33 + 0.09 * (ratio - 1.0)
        else:
            kFactor = min(0.50, 0.45 + 0.01 * (ratio - 3.0))

        angleRadians = np.radians(self.bendAngle)

        bendAllowance = angleRadians * (self.bendRadius + kFactor * self.thickness)

        # Bend deduction, which is what a flat pattern actually subtracts
        outsideSetback = (self.bendRadius + self.thickness) * np.tan(angleRadians / 2.0)
        bendDeduction  = 2.0 * outsideSetback - bendAllowance

        return {'radiusToThickness': ratio, 'kFactor': kFactor,
                'bendAllowance': bendAllowance,
                'outsideSetback': outsideSetback,
                'bendDeduction': bendDeduction,
                'note': 'The k-factor is not 0.5. The neutral axis migrates towards the inside of '
                        'the bend because the inner fibre thickens in compression while the outer '
                        'thins in tension, and the migration is larger on a tight bend.'}

    def checkFormingLimit(self, majorStrain: float, minorStrain: float) -> dict:

        '''

        Major and minor strain against the forming limit diagram.

        The FLD is the locus of strain combinations at which a local neck forms. Its lowest point is
        at PLANE STRAIN, where the minor strain is zero, and that is the critical condition:

            FLD0 = n * (thickness scaling)

        The shape either side of plane strain is different, and the asymmetry matters:

            Minor strain negative (drawing)   The limit RISES. Material flows in from the side to
                                              feed the deformation, so the section thins less.

            Minor strain positive (stretching) The limit rises more slowly. Biaxial stretching thins
                                              the material everywhere at once with nowhere to draw
                                              material from.

        THE CONSEQUENCE IS THAT PLANE STRAIN IS THE STATE TO AVOID. A designer who puts a long
        straight-sided feature into a formed part has created a plane strain region, and it will
        neck before any of the more severely deformed corners do.

        '''

        parameters = WORK_HARDENING[self.material]
        exponent   = parameters['hardeningExponent']

        # FLD0 at plane strain, scaled for thickness
        thicknessFactor = min(2.0, (self.thickness / FLD_THICKNESS_REFERENCE) ** 0.5)
        fld0 = exponent * thicknessFactor

        # The limit curve either side of plane strain
        if minorStrain < 0.0:
            limit = fld0 * (1.0 - 1.5 * minorStrain)      # rises steeply in the drawing quadrant
        else:
            limit = fld0 * (1.0 + 0.6 * minorStrain)      # rises slowly in the stretching quadrant

        margin = limit - majorStrain
        safe   = majorStrain < limit

        strainPath = ('plane strain' if abs(minorStrain) < 0.02 else
                      ('drawing' if minorStrain < 0.0 else 'stretching'))

        result = {'majorStrain': majorStrain, 'minorStrain': minorStrain,
                  'strainPath': strainPath,
                  'fld0': fld0, 'limitStrain': limit,
                  'margin': margin, 'safe': safe,
                  'hardeningExponent': exponent,
                  'thicknessFactor': thicknessFactor}

        if not safe:
            raise ProcessInfeasibleError(
                message = f'A major strain of {majorStrain:.3f} at a minor strain of '
                          f'{minorStrain:.3f} exceeds the forming limit of {limit:.3f} for '
                          f'{self.material} at {self.thickness * 1.0e3:.2f} mm. The part will neck '
                          f'and tear. The strain path is {strainPath}.'
            )

        if strainPath == 'plane strain':
            self.formingNotes.append(
                f'The strain path is plane strain, which is the lowest point on the forming limit '
                f'diagram and therefore the critical condition. A long straight-sided feature '
                f'creates a plane strain region and it will neck before more severely deformed '
                f'corners do. Adding a slight crown or a draw bead moves the path off plane strain '
                f'and raises the limit.')
        elif margin < 0.05:
            self.formingNotes.append(
                f'The forming limit margin is only {margin:.3f}. Sheet thickness scatter, lubricant '
                f'variation and die wear all move the strain, so a margin this small will produce '
                f'occasional tears rather than none.')

        return result

    def calculateWorkHardening(self, effectiveStrain: float) -> dict:

        '''

        Strength gained and ductility spent by cold work.

            sigma = K eps^n                        Hollomon

        BOTH HALVES MATTER AND ONLY THE FIRST IS USUALLY CLAIMED. A flow formed cylinder is
        genuinely stronger than the tube it started as, and it is also less able to absorb any
        further deformation. If the part sees a subsequent forming operation, or a service load
        that requires ductility, the spent ductility is the number that governs.

        The hardening exponent n is also the uniform elongation, which gives a useful identity: a
        material necks when the strain reaches n. Accumulated strain approaching n means the
        material is at the end of its uniform deformation and further work localises.

        Claiming the strength gain in a stress report requires substantiating it, because the
        allowables in any database are for the unworked condition.

        '''

        parameters = WORK_HARDENING[self.material]
        properties = queryMaterial(self.material, self.condition, 293.15)

        coefficient = parameters['strengthCoefficient']
        exponent    = parameters['hardeningExponent']

        flowStress = coefficient * max(effectiveStrain, 1.0e-6) ** exponent

        originalYield = properties['yieldStrength']
        self.formedYieldStrength = max(originalYield, flowStress)

        strengthGain = self.formedYieldStrength / originalYield

        # Uniform elongation remaining. The material necks at eps = n.
        remainingUniform = max(0.0, exponent - effectiveStrain)
        ductilitySpent   = min(1.0, effectiveStrain / exponent) if exponent > 0.0 else 1.0

        result = {'effectiveStrain': effectiveStrain,
                  'strengthCoefficient': coefficient,
                  'hardeningExponent': exponent,
                  'flowStress': flowStress,
                  'originalYield': originalYield,
                  'formedYieldStrength': self.formedYieldStrength,
                  'strengthGain': strengthGain,
                  'remainingUniformElongation': remainingUniform,
                  'ductilitySpentFraction': ductilitySpent,
                  'annealRequired': effectiveStrain > ANNEAL_STRAIN_THRESHOLD,
                  'note': parameters['note']}

        if effectiveStrain > ANNEAL_STRAIN_THRESHOLD:
            self.formingNotes.append(
                f'An accumulated effective strain of {effectiveStrain:.2f} exceeds the '
                f'{ANNEAL_STRAIN_THRESHOLD:.2f} threshold where most alloys have consumed their '
                f'formability. An interstage recrystallisation anneal is needed before further '
                f'work, and it resets the strength gain as well as the ductility.')

        if ductilitySpent > 0.8:
            self.formingNotes.append(
                f'{ductilitySpent * 100.0:.0f} percent of the uniform elongation has been consumed. '
                f'The material necks at a strain of {exponent:.2f} and it is at '
                f'{effectiveStrain:.2f}. Any further deformation will localise rather than '
                f'distribute.')

        if strengthGain > 1.15:
            self.formingNotes.append(
                f'The cold work raises the yield strength by {(strengthGain - 1.0) * 100.0:.0f} '
                f'percent. Claiming that in a stress report requires substantiating it, because '
                f'every allowable in the database is for the unworked condition.')

        return result

    def calculateHydroformPressure(self) -> dict:

        '''

        Pressure required to form the part against the die.

            P = 2 F_ty t / D

        This is the thin wall hoop relation solved for the pressure that yields the section, which
        is what forming requires. The practical pressure is higher, because the corner radii have to
        be filled and that needs local yielding at a smaller effective radius.

        The number matters because hydroform presses are rated in pressure and the rating is the
        constraint. A part needing 100 MPa is a different machine from one needing 30.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)

        yieldStrength = properties['yieldStrength']

        formingPressure = 2.0 * yieldStrength * self.thickness / self.partDiameter

        # Corner filling needs local yielding at the corner radius rather than the part diameter
        cornerRadius = max(self.bendRadius, 2.0 * self.thickness)
        cornerPressure = 2.0 * yieldStrength * self.thickness / (2.0 * cornerRadius)

        required = max(formingPressure, cornerPressure)

        return {'yieldStrength': yieldStrength,
                'partDiameter': self.partDiameter,
                'thickness': self.thickness,
                'formingPressure': formingPressure,
                'cornerRadius': cornerRadius,
                'cornerFillPressure': cornerPressure,
                'requiredPressure': required,
                'bindingCondition': 'corner fill' if cornerPressure > formingPressure
                                    else 'general forming'}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        bend       = self.calculateMinimumBendRadius()
        springback = self.calculateSpringback()
        allowance  = self.calculateBendAllowance()

        parameters = WORK_HARDENING[self.material]
        process    = FORMING_PROCESSES[self.process]

        rows = [
            ['Material',            f'{self.material}'],
            ['Process',             f'{self.process}'],
            ['Thickness',           f'{self.thickness * 1.0e3:.2f} mm'],
            ['Reduction of area',   f'{bend["reductionOfArea"] * 100.0:.0f} %'],
            ['Grain direction',     f'{self.grainDirection} to the bend line '
                                    f'(x{bend["directionFactor"]:.0f})'],
            ['Minimum bend radius', f'{self.minimumBendRadius * 1.0e3:.2f} mm '
                                    f'(r/t = {bend["minimumRatio"]:.2f})'],
            ['Actual bend radius',  f'{self.bendRadius * 1.0e3:.2f} mm '
                                    f'(r/t = {bend["actualRatio"]:.2f})'],
            ['Target angle',        f'{self.bendAngle:.1f} deg'],
            ['Springback',          f'{self.springbackAngle:.2f} deg'],
            ['Tool angle',          f'{self.compensatedAngle:.2f} deg'],
            ['k-factor',            f'{allowance["kFactor"]:.3f}'],
            ['Bend allowance',      f'{allowance["bendAllowance"] * 1.0e3:.2f} mm'],
            ['Bend deduction',      f'{allowance["bendDeduction"] * 1.0e3:.2f} mm'],
            ['Hardening exponent',  f'{parameters["hardeningExponent"]:.2f}'],
            ['Maximum process strain', f'{process["maximumStrain"]:.2f}']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'FORMING PROCESS')

        report += f'\n\nMATERIAL NOTE\n{"-" * 60}\n{parameters["note"]}\n'
        report += f'\nPROCESS NOTE\n{"-" * 60}\n{process["note"]}\n'

        for note in self.formingNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'formingProcess.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = ' '.join(self.material.strip().upper().split())

        if key not in WORK_HARDENING:
            raise InvalidInputError(
                message       = f'No work hardening parameters for \'{self.material}\'. The '
                                f'strength coefficient and hardening exponent cannot be assumed; '
                                f'they range from 0.08 to 0.45 across the alloys here.',
                parameterName = 'material', value = self.material,
                validRange    = str(sorted(WORK_HARDENING.keys()))
            )

        self.material = key

        process = self.process.strip().lower()

        if process not in FORMING_PROCESSES:
            raise InvalidInputError(
                message       = f'Unknown forming process \'{self.process}\'.',
                parameterName = 'process', value = self.process,
                validRange    = str(sorted(FORMING_PROCESSES.keys()))
            )

        self.process = process

        if self.grainDirection not in ('transverse', 'parallel'):
            raise InvalidInputError(
                message       = 'Grain direction must be transverse or parallel to the bend line.',
                parameterName = 'grainDirection', value = self.grainDirection,
                validRange    = "'transverse' or 'parallel'"
            )

        for name, value in (('thickness', self.thickness), ('bendRadius', self.bendRadius),
                            ('partDiameter', self.partDiameter)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0 m'
                )

        if not 0.0 < self.bendAngle <= 180.0:
            raise InvalidInputError(
                message       = 'Bend angle must lie between 0 and 180 degrees.',
                parameterName = 'bendAngle', value = self.bendAngle, validRange = '(0, 180]'
            )
