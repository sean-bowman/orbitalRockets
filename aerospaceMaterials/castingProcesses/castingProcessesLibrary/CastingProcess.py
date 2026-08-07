
# -- CastingProcess Class Definition -- #

'''

Solidification, riser sizing, and the casting factor that sets the design allowable.

Casting is the cheapest route to a complex shape and it carries a knockdown that no other route
does. The reason is that a casting's properties are a property of the process rather than of the
alloy: the same alloy, the same chemistry and the same heat treatment produce different mechanical
properties depending on how it solidified and what got trapped while it did.

The industry's answer is the CASTING FACTOR, and it is the most consequential number in this class:

    2.00    Default. No qualified process. The allowable is HALVED.
    1.33    Partial qualification, or partial volumetric NDE.
    1.00    Qualified process, 100 percent volumetric NDE, three sample lots.

A factor of 2.0 means twice the material to carry the same load. No alloy substitution recovers
that, and qualifying the process is frequently cheaper than the mass the default factor costs. The
whole point of running this class is to make that trade visible before the part is designed around
a casting nobody intends to qualify.

The rest of the class is the solidification physics that decides whether the casting is sound at
all: Chvorinov freezing time, and riser sizing by the modulus method.

See Also:
---------
CentrifugalCasting : The rotating variant, where segregation is a feature rather than a defect
Allowables         : Where the casting factor enters the knockdown chain
ProcessComparison  : Where the casting routes are traded against wrought and additive

Theory: docs/CastingFactorAndQualification.md, docs/Solidification.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from castingUtils import (applyInputs, formatReportTable, queryMaterial,
                              InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .castingUtils import (applyInputs, formatReportTable, queryMaterial,
                               InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The casting factor ladder per NASA-STD-5001 and NASA-STD-6016. This is the table that decides the
# allowable, and the requirements column is what has to be met to earn each step.

CASTING_FACTORS = {
    1.00: {'allowableMultiplier': 1.00,
           'requirements': ['Qualified casting process, frozen and documented',
                            '100 percent volumetric NDE on every casting',
                            'Three sample lots demonstrating property consistency',
                            'Statistical process control in production'],
           'note': 'Full qualification. The allowable is the wrought allowable for the alloy and '
                   'condition, with no casting penalty at all.'},

    1.33: {'allowableMultiplier': 1.0 / 1.33,
           'requirements': ['Documented casting process',
                            'Volumetric NDE on a defined sample basis',
                            'At least one qualification lot'],
           'note': 'Partial qualification. The usual position for a programme that has done the '
                   'work but not all of it.'},

    2.00: {'allowableMultiplier': 0.50,
           'requirements': ['None. This is the default where nothing has been qualified.'],
           'note': 'The default, and it halves the allowable. A part designed at this factor needs '
                   'twice the material of the same part designed at 1.0, which is almost always '
                   'more expensive than qualifying the process would have been.'}
}

# Casting processes, with their capability envelopes. The tolerance grades are ISO 8062 and they are
# what screens a process out before the allowable ever enters the argument.

CASTING_PROCESSES = {
    'investment': {'minimumWall': 0.0015, 'maximumMass': 50.0, 'toleranceGrade': 'DCTG 6',
                   'surfaceRoughness': 3.2e-6, 'chvorinovConstant': 1.4e6,
                   'patternShrinkage': 0.012, 'leadTimeWeeks': 20, 'relativeCost': 1.2,
                   'note': 'The dominant aerospace casting route. Complex geometry in one piece '
                           'with an excellent as-cast surface, at a real tooling cost.'},

    'sand':       {'minimumWall': 0.005, 'maximumMass': 2000.0, 'toleranceGrade': 'DCTG 11',
                   'surfaceRoughness': 25.0e-6, 'chvorinovConstant': 2.2e6,
                   'patternShrinkage': 0.020, 'leadTimeWeeks': 12, 'relativeCost': 0.5,
                   'note': 'Cheap, large, coarse. Rarely a flight structure route without a '
                           'qualification programme.'},

    'die':        {'minimumWall': 0.0010, 'maximumMass': 25.0, 'toleranceGrade': 'DCTG 4',
                   'surfaceRoughness': 1.6e-6, 'chvorinovConstant': 0.6e6,
                   'patternShrinkage': 0.006, 'leadTimeWeeks': 26, 'relativeCost': 0.4,
                   'note': 'Excellent dimensions and surface, high tooling cost, and the trapped '
                           'gas from the fast fill makes it difficult to qualify for structure. '
                           'Aluminium and zinc alloys only in practice.'},

    'permanent mould': {'minimumWall': 0.0035, 'maximumMass': 150.0, 'toleranceGrade': 'DCTG 8',
                        'surfaceRoughness': 12.5e-6, 'chvorinovConstant': 1.0e6,
                        'patternShrinkage': 0.012, 'leadTimeWeeks': 16, 'relativeCost': 0.7,
                        'note': 'Between sand and die. Faster solidification than sand gives a '
                                'finer structure and better properties.'}
}

# ISO 8062 dimensional casting tolerance grades, as a total tolerance on a 100 mm dimension.
ISO_8062_TOLERANCE_100MM = {
    'DCTG 4': 0.26e-3, 'DCTG 6': 0.52e-3, 'DCTG 8': 1.40e-3,
    'DCTG 11': 5.00e-3, 'DCTG 14': 16.0e-3
}

# Riser sizing by the modulus method. A riser has to freeze after the casting it feeds, so its
# modulus must exceed the casting's by a margin. 1.2 is the conventional value.
RISER_MODULUS_RATIO = 1.2

# Solidification shrinkage by alloy family, as a volume fraction. This is the volume the riser has
# to supply, and it is separate from the pattern shrinkage that compensates for solid contraction.
SOLIDIFICATION_SHRINKAGE = {
    'aluminium': 0.065, 'steel': 0.030, 'stainless': 0.040,
    'nickel': 0.045, 'copper': 0.045, 'titanium': 0.030
}

CHVORINOV_EXPONENT = 2.0

# ------------------------------------------------------------------------------------------------ #

class CastingProcess:

    '''

    Solidification, riser sizing and casting factor selection for a static casting.

    Primary Input Properties:
    -------------------------
    process : str
        Key into CASTING_PROCESSES
    material : str
        Alloy key, passed to the materials database for the base allowable
    castingVolume / castingSurfaceArea : float
        [m^3] and [m^2], for the modulus
    qualificationLevel : float
        1.00, 1.33 or 2.00. The casting factor.

    Key Output Properties:
    ----------------------
    castingModulus : float
        Volume over cooling surface area [m]
    solidificationTime : float
        [s], from Chvorinov
    riserVolume : float
        [m^3] required to feed the shrinkage
    allowableMultiplier : float
        The knockdown the casting factor imposes

    Public Methods:
    ---------------
    setInputs(inputs)                 Load a configuration dictionary
    calculateSolidification()         Modulus and Chvorinov time
    sizeRiser()                       Modulus method plus the shrinkage volume check
    selectCastingFactor()             The factor, what it costs, and what earning 1.0 requires
    calculateMachiningAllowance()     ISO 8062 tolerance to stock, plus pattern shrinkage
    checkFeasibility()                Wall, mass and tolerance against the process envelope
    generateReport(outputDir)         Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Part and Process -- #

        self.process             = 'investment'   # [case insensitive string]
        self.material            = '316L'         # [case insensitive string]
        self.alloyFamily         = 'stainless'    # [case insensitive string]
        self.castingVolume       = 1.0e-4         # [m^3]
        self.castingSurfaceArea  = 0.05           # [m^2]
        self.minimumWallThickness = 0.004         # [m]
        self.characteristicSize  = 0.150          # [m]

        # -- Qualification -- #

        self.qualificationLevel  = 2.00           # [-], the casting factor

        # -- Results -- #

        self.castingModulus      = np.nan   # [m]
        self.solidificationTime  = np.nan   # [s]
        self.riserVolume         = np.nan   # [m^3]
        self.allowableMultiplier = np.nan   # [-]
        self.castingNotes        = []       # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: process.

        '''

        requiredParams = {
            'process': 'Casting process not provided.'
        }

        optionalParams = ['material', 'alloyFamily', 'castingVolume', 'castingSurfaceArea',
                          'minimumWallThickness', 'characteristicSize', 'qualificationLevel']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateSolidification(self) -> dict:

        '''

        Casting modulus and Chvorinov solidification time.

            M = V / A                  the casting modulus
            t = B M^n                  n = 2

        The modulus is the single geometric parameter that governs freezing time, and it is why a
        thick section freezes slowly and a thin one freezes fast regardless of the overall part
        size. Two castings with the same modulus freeze in the same time whatever their shape.

        The modulus is also what riser sizing works in, because a riser has to still be liquid when
        the casting it feeds has finished freezing.

        '''

        properties = CASTING_PROCESSES[self.process]

        self.castingModulus = self.castingVolume / self.castingSurfaceArea
        self.solidificationTime = properties['chvorinovConstant'] * \
                                  self.castingModulus ** CHVORINOV_EXPONENT

        return {'castingVolume': self.castingVolume,
                'castingSurfaceArea': self.castingSurfaceArea,
                'castingModulus': self.castingModulus,
                'chvorinovConstant': properties['chvorinovConstant'],
                'solidificationTime': self.solidificationTime,
                'process': self.process}

    def sizeRiser(self) -> dict:

        '''

        Riser sizing by the modulus method, checked against the shrinkage volume.

        TWO CONDITIONS HAVE TO HOLD SIMULTANEOUSLY and they are independent:

            Timing     The riser must freeze AFTER the casting, or it stops feeding while the
                       casting is still shrinking and the shrinkage cavity forms in the part
                       instead of in the riser.

                           M_riser >= 1.2 M_casting

            Volume     The riser must contain enough liquid to make up the solidification
                       shrinkage, which is 3 to 6.5 percent of the casting volume depending on the
                       alloy family.

                           V_riser * feedingEfficiency >= shrinkage * V_casting

        A riser that satisfies one and not the other does not work, and the failure modes look
        different: a timing failure gives centreline shrinkage in the heavy section, while a volume
        failure gives a shrinkage cavity under the riser neck.

        The binding condition is reported because it says what to change. A timing-bound riser needs
        to be fatter; a volume-bound one needs to be taller or there need to be more of them.

        '''

        if np.isnan(self.castingModulus):
            self.calculateSolidification()

        shrinkage = SOLIDIFICATION_SHRINKAGE[self.alloyFamily]

        # Timing condition, through the modulus. For a cylindrical riser of height equal to its
        # diameter, M = D/6, so D = 6 M.
        requiredModulus = RISER_MODULUS_RATIO * self.castingModulus
        riserDiameter   = 6.0 * requiredModulus
        timingVolume    = np.pi * riserDiameter ** 3 / 4.0

        # Volume condition. A riser feeds roughly 14 percent of its own volume before its own
        # solidification front closes it off.
        feedingEfficiency = 0.14
        volumeRequired    = shrinkage * self.castingVolume / feedingEfficiency

        self.riserVolume = max(timingVolume, volumeRequired)
        binding = 'timing' if timingVolume >= volumeRequired else 'volume'

        yieldFraction = self.castingVolume / (self.castingVolume + self.riserVolume)

        result = {'castingModulus': self.castingModulus,
                  'requiredRiserModulus': requiredModulus,
                  'riserDiameter': riserDiameter,
                  'timingVolume': timingVolume,
                  'shrinkageFraction': shrinkage,
                  'volumeRequired': volumeRequired,
                  'feedingEfficiency': feedingEfficiency,
                  'riserVolume': self.riserVolume,
                  'bindingCondition': binding,
                  'castingYield': yieldFraction}

        if binding == 'volume':
            self.castingNotes.append(
                f'The riser is volume bound rather than timing bound, which means the alloy '
                f'shrinkage of {shrinkage * 100.0:.1f} percent needs more liquid than a riser of '
                f'the right modulus happens to contain. Make the riser taller, or use more than '
                f'one, rather than simply fatter.')

        if yieldFraction < 0.50:
            self.castingNotes.append(
                f'The casting yield is {yieldFraction * 100.0:.0f} percent, so more than half the '
                f'metal poured ends up in the risers and the gating. That is normal for a heavy '
                f'section aluminium casting and it is a real cost that belongs in the route trade.')

        return result

    def selectCastingFactor(self) -> dict:

        '''

        The casting factor, what it costs, and what earning a better one requires.

        THIS IS THE MOST CONSEQUENTIAL CALCULATION IN THE CLASS. The factor multiplies straight into
        the allowable, and for a membrane the material required scales as its inverse. A factor of
        2.0 means literally twice the material for the same load.

        The comparison against the qualified case is included deliberately, because the decision
        that matters is not which factor applies today. It is whether the mass the default factor
        costs exceeds the cost of the qualification programme that would remove it, and that
        comparison is almost never made because the two numbers sit in different budgets.

        '''

        factor = CASTING_FACTORS[self.qualificationLevel]

        self.allowableMultiplier = factor['allowableMultiplier']

        massPenalty = 1.0 / self.allowableMultiplier

        qualified = CASTING_FACTORS[1.00]
        potentialSaving = 1.0 - self.allowableMultiplier / qualified['allowableMultiplier']

        result = {'castingFactor': self.qualificationLevel,
                  'allowableMultiplier': self.allowableMultiplier,
                  'massPenalty': massPenalty,
                  'requirements': factor['requirements'],
                  'note': factor['note'],
                  'potentialMassSaving': potentialSaving,
                  'requirementsForFactorOne': qualified['requirements']}

        if self.qualificationLevel > 1.00:
            self.castingNotes.append(
                f'At a casting factor of {self.qualificationLevel:.2f} the allowable is multiplied '
                f'by {self.allowableMultiplier:.3f}, so this part needs {massPenalty:.2f} times the '
                f'material a fully qualified casting would. Qualifying the process removes '
                f'{potentialSaving * 100.0:.0f} percent of the mass, and the qualification is '
                f'frequently cheaper than the mass. That comparison is rarely made because the two '
                f'costs sit in different budgets.')

        return result

    def calculateMachiningAllowance(self) -> dict:

        '''

        Machining stock from the ISO 8062 tolerance grade, and the pattern shrinkage allowance.

        Two separate allowances that are often confused:

            Machining stock     Compensates for the dimensional scatter of the process. It is
                                removed by machining and it is set by the tolerance grade.

            Pattern shrinkage   Compensates for the SOLID contraction of the casting as it cools
                                from the solidus to room temperature. The pattern is made oversize
                                by this amount and it is not machined off; it is what makes the
                                cold casting the right size.

        Getting the second one wrong makes every casting from that tool the wrong size, and it is
        not recoverable by machining if the error went the wrong way.

        '''

        properties = CASTING_PROCESSES[self.process]

        tolerance = ISO_8062_TOLERANCE_100MM[properties['toleranceGrade']]

        # Tolerance scales roughly with the dimension. Machining stock is conventionally the
        # tolerance plus an allowance for the as-cast surface condition.
        scaledTolerance = tolerance * (self.characteristicSize / 0.100)
        surfaceAllowance = 3.0 * properties['surfaceRoughness'] * 100.0

        machiningStock = scaledTolerance + surfaceAllowance

        patternShrinkage = properties['patternShrinkage']
        patternOversize  = self.characteristicSize * patternShrinkage

        return {'toleranceGrade': properties['toleranceGrade'],
                'toleranceOn100mm': tolerance,
                'scaledTolerance': scaledTolerance,
                'surfaceRoughness': properties['surfaceRoughness'],
                'surfaceAllowance': surfaceAllowance,
                'machiningStock': machiningStock,
                'patternShrinkageFraction': patternShrinkage,
                'patternOversize': patternOversize,
                'note': 'Machining stock is removed. Pattern shrinkage is not: it makes the cold '
                        'casting the right size and an error in it is not recoverable.'}

    def checkFeasibility(self) -> dict:

        '''

        Wall thickness, mass and size against the process envelope.

        '''

        properties = CASTING_PROCESSES[self.process]

        try:
            alloy = queryMaterial(self.material, None, 293.15)
            density = alloy['density']
        except Exception:
            density = 7800.0

        castingMass = self.castingVolume * density

        issues = []

        if self.minimumWallThickness < properties['minimumWall']:
            issues.append(
                f'{self.process} casting cannot hold a '
                f'{self.minimumWallThickness * 1.0e3:.2f} mm wall. The minimum is '
                f'{properties["minimumWall"] * 1.0e3:.2f} mm.')

        if castingMass > properties['maximumMass']:
            issues.append(
                f'Casting mass of {castingMass:.1f} kg exceeds the {properties["maximumMass"]:.0f} '
                f'kg practical maximum for {self.process} casting.')

        self.castingNotes.extend(issues)

        if issues:
            raise ProcessInfeasibleError(
                message = f'{self.process} casting cannot produce this part. ' + ' '.join(issues)
            )

        return {'castingMass': castingMass, 'process': self.process,
                'minimumWall': properties['minimumWall'],
                'maximumMass': properties['maximumMass'],
                'issues': issues, 'feasible': True}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        solidify  = self.calculateSolidification()
        riser     = self.sizeRiser()
        factor    = self.selectCastingFactor()
        allowance = self.calculateMachiningAllowance()

        properties = CASTING_PROCESSES[self.process]

        rows = [
            ['Process',              f'{self.process}'],
            ['Material',             f'{self.material} ({self.alloyFamily})'],
            ['Casting volume',       f'{self.castingVolume * 1.0e6:.1f} cm^3'],
            ['Casting modulus',      f'{self.castingModulus * 1.0e3:.2f} mm'],
            ['Solidification time',  f'{self.solidificationTime:.1f} s'],
            ['Riser diameter',       f'{riser["riserDiameter"] * 1.0e3:.1f} mm'],
            ['Riser volume',         f'{self.riserVolume * 1.0e6:.1f} cm^3 '
                                     f'(binding: {riser["bindingCondition"]})'],
            ['Casting yield',        f'{riser["castingYield"] * 100.0:.0f} %'],
            ['Tolerance grade',      f'{properties["toleranceGrade"]}'],
            ['Machining stock',      f'{allowance["machiningStock"] * 1.0e3:.2f} mm'],
            ['Pattern oversize',     f'{allowance["patternOversize"] * 1.0e3:.2f} mm '
                                     f'({allowance["patternShrinkageFraction"] * 100.0:.1f} %)'],
            ['Casting factor',       f'{self.qualificationLevel:.2f}'],
            ['Allowable multiplier', f'{self.allowableMultiplier:.3f}'],
            ['Mass penalty',         f'{factor["massPenalty"]:.2f} x'],
            ['Lead time',            f'{properties["leadTimeWeeks"]} weeks'],
            ['Relative cost',        f'{properties["relativeCost"]:.1f}']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'CASTING PROCESS')

        report += f'\n\nPROCESS NOTE\n{"-" * 60}\n{properties["note"]}\n'

        report += f'\nCASTING FACTOR {self.qualificationLevel:.2f}\n{"-" * 60}\n'
        report += f'{factor["note"]}\n\nRequirements met at this level:\n'
        for requirement in factor['requirements']:
            report += f'  {requirement}\n'

        if self.qualificationLevel > 1.00:
            report += f'\nTo reach a factor of 1.00:\n'
            for requirement in factor['requirementsForFactorOne']:
                report += f'  {requirement}\n'

        for note in self.castingNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'castingProcess.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = self.process.strip().lower()

        if key not in CASTING_PROCESSES:
            raise InvalidInputError(
                message       = f'Unknown casting process \'{self.process}\'.',
                parameterName = 'process', value = self.process,
                validRange    = str(sorted(CASTING_PROCESSES.keys()))
            )

        self.process = key

        family = self.alloyFamily.strip().lower()

        if family not in SOLIDIFICATION_SHRINKAGE:
            raise InvalidInputError(
                message       = f'Unknown alloy family \'{self.alloyFamily}\'. The solidification '
                                f'shrinkage cannot be assumed; it ranges from 3 to 6.5 percent.',
                parameterName = 'alloyFamily', value = self.alloyFamily,
                validRange    = str(sorted(SOLIDIFICATION_SHRINKAGE.keys()))
            )

        self.alloyFamily = family

        if self.qualificationLevel not in CASTING_FACTORS:
            raise InvalidInputError(
                message       = f'Casting factor {self.qualificationLevel} is not a defined level. '
                                f'The ladder is 1.00, 1.33 and 2.00 per NASA-STD-5001.',
                parameterName = 'qualificationLevel', value = self.qualificationLevel,
                validRange    = str(sorted(CASTING_FACTORS.keys()))
            )

        for name, value in (('castingVolume', self.castingVolume),
                            ('castingSurfaceArea', self.castingSurfaceArea),
                            ('minimumWallThickness', self.minimumWallThickness)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0'
                )
