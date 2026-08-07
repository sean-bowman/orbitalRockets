
# -- DamageTolerance Class Definition -- #

'''

Critical flaw size, leak before burst, proof test screening and fatigue crack growth life.

Damage tolerance starts from an assumption that is uncomfortable and correct: the part already
contains a crack. Not might contain one, does contain one, at the largest size the inspection method
could have missed. Everything else follows from that.

    K = Y sigma sqrt(pi a)

The part fails when K reaches the material's fracture toughness, so for a given stress there is a
critical flaw size, and the design question is whether the initial flaw can grow to it within the
service life.

Three results this class produces are worth stating in advance because they are not obvious.

    Leak before burst      If the critical flaw is longer than the wall is thick, a through-wall
                           crack forms and the vessel leaks before it bursts. That is a detectable,
                           survivable failure rather than a fragmentation event, and it is worth
                           paying mass for.

    Proof as inspection    A proof test at 1.5x MEOP screens out any flaw larger than the critical
                           size AT PROOF STRESS. That is a smaller flaw than the one critical at
                           operating stress, so surviving proof guarantees a margin. This is why
                           proof testing is a fracture control method and not merely a strength
                           demonstration.

    The toughness trade    STA titanium buys 17 percent yield and gives back 35 percent of the
                           toughness. On a fracture critical pressure vessel that is usually the
                           wrong trade, and the critical flaw size is what shows it.

See Also:
---------
MaterialDatabase : Supplies K_Ic, the Paris constants and the threshold
Allowables       : Supplies the design value the applied stress is checked against
fluidSystemsTesting/PressureTest : The proof and burst levels this class screens against

Theory: docs/FractureAndDamageTolerance.md

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

# Geometry factors Y in K = Y sigma sqrt(pi a). The surface flaw value carries the 1.12 free surface
# correction, which is the one that matters because surface flaws are what inspection finds and what
# service produces.

GEOMETRY_FACTORS = {
    'through crack, infinite plate':  {'factor': 1.00, 'note': 'The textbook reference case'},
    'surface flaw, semi-elliptical':  {'factor': 1.12, 'note': 'Free surface correction. The usual '
                                                               'case for a machined or welded part.'},
    'corner crack':                   {'factor': 1.20, 'note': 'Two free surfaces at a hole or edge'},
    'embedded flaw':                  {'factor': 1.00, 'note': 'No free surface correction'},
    'edge crack':                     {'factor': 1.12, 'note': 'Single edge notched geometry'}
}

# Initial flaw sizes per NASA-STD-5009. These are what the inspection method is CREDITED with
# finding, not what it typically finds, and the difference is the point: a standard penetrant
# inspection is credited with 1.27 mm and a part is analysed as though a 1.27 mm crack is present.

NDE_FLAW_SIZES = {
    'penetrant, standard':   {'depth': 0.000635, 'length': 0.00127,
                              'note': 'NASA-STD-5009 standard penetrant, a/2c = 0.5'},
    'penetrant, special':    {'depth': 0.000381, 'length': 0.000762,
                              'note': 'Special penetrant procedure with a demonstrated capability'},
    'eddy current, standard': {'depth': 0.000508, 'length': 0.00102,
                               'note': 'Surface eddy current'},
    'ultrasonic, standard':  {'depth': 0.00190, 'length': 0.00381,
                              'note': 'Contact ultrasonic. Poor for tight surface flaws.'},
    'radiography, standard': {'depth': 0.00254, 'length': 0.00508,
                              'note': 'Film radiography. Effectively blind to a tight planar crack '
                                      'normal to the beam, which is the dangerous orientation.'},
    'computed tomography':   {'depth': 0.000254, 'length': 0.000508,
                              'note': 'Micro CT. The only practical volumetric method for an '
                                      'additive internal passage.'},
    'proof test':            {'depth': None, 'length': None,
                              'note': 'Computed from the proof stress rather than tabulated'}
}

# Where the crack growth integration stops caring about accuracy. Below the threshold range the
# crack does not grow at all, and above about 0.9 K_Ic the Paris law no longer describes the
# behaviour because the growth is unstable.

PARIS_UPPER_FRACTION = 0.90     # [-], of K_Ic

# ------------------------------------------------------------------------------------------------ #

class DamageTolerance:

    '''

    Fracture mechanics screening for a pressurised or cyclically loaded part.

    Primary Input Properties:
    -------------------------
    material / condition / temperature : str, str, float
        Passed to the database for toughness and Paris constants
    operatingStress / proofStress : float
        Membrane stress at MEOP and at proof [Pa]
    wallThickness : float
        [m], the leak before burst comparison
    inspectionMethod : str
        Key into NDE_FLAW_SIZES, setting the initial flaw
    designCycles : int
        Pressure cycles the part must survive

    Key Output Properties:
    ----------------------
    criticalFlawSize : float
        [m], flaw depth at which the part fails at operating stress
    leakBeforeBurst : bool
        True when the critical flaw exceeds the wall thickness
    cyclesToFailure : float
        Paris integration from the initial flaw to critical
    lifeMargin : float
        cyclesToFailure / designCycles

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    calculateCriticalFlaw()        At operating and at proof stress
    checkLeakBeforeBurst()         Critical flaw against wall thickness
    calculateProofScreening()      What flaw size the proof test guarantees is absent
    calculateCrackGrowth()         Paris integration to failure
    calculateThresholdStress()     Stress below which no crack grows
    generateReport(outputDir)      Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material -- #

        self.material          = 'TI-6AL-4V'   # [case insensitive string]
        self.condition         = 'annealed'    # [case insensitive string]
        self.temperature       = 293.15        # [K]
        self.orientation       = 'L-T'         # [-], fracture plane orientation

        # -- Loading -- #

        self.operatingStress   = np.nan        # [Pa], membrane stress at MEOP
        self.proofStress       = np.nan        # [Pa], membrane stress at proof pressure
        self.minimumStress     = 0.0           # [Pa], for the stress ratio
        self.designCycles      = 500           # [-], pressure cycles required

        # -- Geometry -- #

        self.wallThickness     = np.nan        # [m]
        self.geometryCase      = 'surface flaw, semi-elliptical'  # [case insensitive string]
        self.flawAspectRatio   = 0.5           # [-], a / 2c

        # -- Inspection -- #

        self.inspectionMethod  = 'penetrant, standard'  # [case insensitive string]
        self.initialFlawSize   = np.nan        # [m], overrides the NDE table when set

        # -- Results -- #

        self.fractureToughness = np.nan        # [Pa-sqrt(m)]
        self.criticalFlawSize  = np.nan        # [m], at operating stress
        self.proofFlawSize     = np.nan        # [m], at proof stress
        self.leakBeforeBurst   = False         # [bool]
        self.cyclesToFailure   = np.nan        # [-]
        self.lifeMargin        = np.nan        # [-]
        self.thresholdStress   = np.nan        # [Pa]
        self.fractureNotes     = []            # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material, operatingStress.

        '''

        requiredParams = {
            'material':        'Material not provided.',
            'operatingStress': 'Operating membrane stress not provided.'
        }

        optionalParams = ['condition', 'temperature', 'orientation', 'proofStress', 'minimumStress',
                          'designCycles', 'wallThickness', 'geometryCase', 'flawAspectRatio',
                          'inspectionMethod', 'initialFlawSize']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateCriticalFlaw(self) -> dict:

        '''

        Critical flaw depth at operating and at proof stress.

        Inverting K = Y sigma sqrt(pi a) at K = K_Ic:

            a_critical = (1 / pi) (K_Ic / (Y sigma))^2

        The inverse square dependence on stress is the whole story. Halving the stress quadruples the
        tolerable flaw, which is why a lightly stressed vessel is easy to fracture control and a
        highly stressed one is not.

        '''

        properties = queryMaterial(self.material, self.condition, self.temperature)
        fracture   = properties.get('fracture')

        if fracture is None or not fracture.get('planeStrainToughness'):
            raise InvalidInputError(
                message       = f'No fracture toughness in the database for {self.material} in the '
                                f'{self.condition} condition. A fracture critical part cannot be '
                                f'analysed without it, and assuming a value is not acceptable.',
                parameterName = 'material', value = self.material,
                validRange    = 'A material with a fracture block in materialData.py'
            )

        toughnessValues = fracture['planeStrainToughness']
        self.fractureToughness = toughnessValues.get(self.orientation,
                                                     min(toughnessValues.values()))

        # Temperature correction on the toughness, through the same ratio curve mechanism.
        roomProperties = queryMaterial(self.material, self.condition, 293.15)
        roomToughness  = roomProperties['fracture']['planeStrainToughness'].get(
            self.orientation, min(roomProperties['fracture']['planeStrainToughness'].values()))
        databaseCold   = queryMaterial(self.material, self.condition, self.temperature)
        del databaseCold

        geometryFactor = GEOMETRY_FACTORS[self.geometryCase]['factor']

        self.criticalFlawSize = (1.0 / np.pi) * \
            (self.fractureToughness / (geometryFactor * self.operatingStress)) ** 2

        result = {'fractureToughness': self.fractureToughness,
                  'geometryFactor': geometryFactor,
                  'operatingStress': self.operatingStress,
                  'criticalFlawSize': self.criticalFlawSize,
                  'roomTemperatureToughness': roomToughness}

        if not np.isnan(self.proofStress):
            self.proofFlawSize = (1.0 / np.pi) * \
                (self.fractureToughness / (geometryFactor * self.proofStress)) ** 2
            result['proofFlawSize'] = self.proofFlawSize

        # The yield check. Small scale yielding has to hold or linear elastic fracture mechanics does
        # not apply, and the thickness for valid plane strain is the standard criterion.
        yieldStrength = properties.get('yieldStrength')
        if yieldStrength is not None:
            plasticZone = (1.0 / (6.0 * np.pi)) * (self.fractureToughness / yieldStrength) ** 2
            result['plasticZoneSize'] = plasticZone
            result['plainStrainThickness'] = 2.5 * (self.fractureToughness / yieldStrength) ** 2

            if not np.isnan(self.wallThickness) and \
               self.wallThickness < result['plainStrainThickness']:
                self.fractureNotes.append(
                    f'The wall is {self.wallThickness * 1000.0:.2f} mm and plane strain needs '
                    f'{result["plainStrainThickness"] * 1000.0:.2f} mm for this material. The part '
                    f'is in plane stress, where the effective toughness is HIGHER than K_Ic, so '
                    f'using K_Ic is conservative but the critical flaw size is understated.')

        if self.operatingStress > 0.9 * (yieldStrength or np.inf):
            self.fractureNotes.append(
                'The operating stress is above 90 percent of yield. Linear elastic fracture '
                'mechanics assumes small scale yielding and it does not hold here; an elastic '
                'plastic method is needed.')

        return result

    def checkLeakBeforeBurst(self) -> dict:

        '''

        Compare the critical flaw depth against the wall thickness.

        When a_critical exceeds the wall, a growing flaw penetrates the wall and vents before it
        reaches the length that would cause unstable fracture. The vessel leaks, the leak is
        detectable, and the failure is not a fragmentation event.

        This is a design criterion worth paying mass for on any pressure vessel that sits near
        people or near flight hardware, and it is a property of the stress and the material
        together rather than of either alone.

        '''

        if np.isnan(self.criticalFlawSize):
            self.calculateCriticalFlaw()

        if np.isnan(self.wallThickness):
            raise InvalidInputError(
                message       = 'Wall thickness is needed for the leak before burst comparison.',
                parameterName = 'wallThickness', value = self.wallThickness,
                validRange    = 'Greater than 0 m'
            )

        self.leakBeforeBurst = self.criticalFlawSize > self.wallThickness

        ratio = self.criticalFlawSize / self.wallThickness

        if self.leakBeforeBurst:
            self.fractureNotes.append(
                f'Leak before burst is satisfied: the critical flaw is {ratio:.2f} times the wall '
                f'thickness, so a growing crack penetrates and vents before it becomes unstable. '
                f'The failure mode is a detectable leak rather than a fragmentation event.')
        else:
            self.fractureNotes.append(
                f'Leak before burst is NOT satisfied: the critical flaw is only {ratio:.2f} times '
                f'the wall thickness. The vessel can fail unstably from a flaw that has not yet '
                f'penetrated the wall, so there is no leak to detect first. This demands either '
                f'lower stress, a tougher material, or a fracture control programme that relies '
                f'entirely on inspection.')

        return {'criticalFlawSize': self.criticalFlawSize, 'wallThickness': self.wallThickness,
                'ratio': ratio, 'leakBeforeBurst': self.leakBeforeBurst}

    def calculateProofScreening(self) -> dict:

        '''

        What the proof test guarantees is absent.

        A part that survives proof cannot contain a flaw larger than the critical size at proof
        stress. Since proof stress exceeds operating stress, that screened size is SMALLER than the
        flaw that would be critical in service, and the ratio between them is a real margin bought
        by the test.

        This is why a proof test is a fracture control method. It is a 100 percent inspection with a
        credited flaw size, applied to every article, using the article itself as the instrument.

        '''

        if np.isnan(self.proofStress):
            raise InvalidInputError(
                message       = 'Proof stress is needed to compute what the proof test screens.',
                parameterName = 'proofStress', value = self.proofStress,
                validRange    = 'Greater than the operating stress'
            )

        if np.isnan(self.criticalFlawSize):
            self.calculateCriticalFlaw()

        nde = NDE_FLAW_SIZES[self.inspectionMethod]
        ndeFlaw = self.initialFlawSize if not np.isnan(self.initialFlawSize) else nde['depth']

        screeningRatio = self.criticalFlawSize / self.proofFlawSize

        result = {'proofStress': self.proofStress, 'proofFlawSize': self.proofFlawSize,
                  'operatingCriticalFlaw': self.criticalFlawSize,
                  'screeningRatio': screeningRatio,
                  'ndeFlawSize': ndeFlaw, 'inspectionMethod': self.inspectionMethod}

        if ndeFlaw is not None:
            result['governingInitialFlaw'] = min(ndeFlaw, self.proofFlawSize)
            result['governedBy'] = 'proof test' if self.proofFlawSize < ndeFlaw else 'NDE'

            self.fractureNotes.append(
                f'The initial flaw is set by the {result["governedBy"]}: proof screens to '
                f'{self.proofFlawSize * 1000.0:.3f} mm and {self.inspectionMethod} is credited '
                f'with {ndeFlaw * 1000.0:.3f} mm, so the analysis starts from '
                f'{result["governingInitialFlaw"] * 1000.0:.3f} mm.')

        return result

    def calculateCrackGrowth(self, initialFlaw: float = None) -> dict:

        '''

        Paris law integration from the initial flaw to the critical size.

            da/dN = C (dK)^m          dK = Y d_sigma sqrt(pi a)

        Integrated numerically rather than in closed form, because the closed form assumes Y is
        constant and stops being usable as soon as the flaw approaches the wall.

        Growth below the threshold range is zero, which is why calculateThresholdStress matters: a
        part held below the threshold has infinite life regardless of cycle count.

        '''

        if np.isnan(self.criticalFlawSize):
            self.calculateCriticalFlaw()

        properties = queryMaterial(self.material, self.condition, self.temperature)
        fracture   = properties['fracture']

        coefficient = fracture.get('parisCoefficient')
        exponent    = fracture.get('parisExponent')
        threshold   = fracture.get('thresholdRange', 0.0)

        if coefficient is None or exponent is None:
            raise InvalidInputError(
                message       = f'No Paris constants for {self.material} in the {self.condition} '
                                f'condition. Crack growth life cannot be computed without them.',
                parameterName = 'material', value = self.material,
                validRange    = 'A material with parisCoefficient and parisExponent'
            )

        if initialFlaw is None:
            if not np.isnan(self.initialFlawSize):
                initialFlaw = self.initialFlawSize
            elif not np.isnan(self.proofStress):
                initialFlaw = self.calculateProofScreening()['governingInitialFlaw']
            else:
                initialFlaw = NDE_FLAW_SIZES[self.inspectionMethod]['depth']

        if initialFlaw is None or initialFlaw <= 0.0:
            raise InvalidInputError(
                message       = 'An initial flaw size is needed. Damage tolerance assumes the part '
                                'already contains a crack.',
                parameterName = 'initialFlawSize', value = initialFlaw,
                validRange    = 'Greater than 0 m'
            )

        if initialFlaw >= self.criticalFlawSize:
            self.cyclesToFailure = 0.0
            self.lifeMargin      = 0.0
            self.fractureNotes.append(
                f'The initial flaw of {initialFlaw * 1000.0:.3f} mm already exceeds the critical '
                f'size of {self.criticalFlawSize * 1000.0:.3f} mm. The part fails on first '
                f'application of load. Either the stress is too high or the inspection is not '
                f'sensitive enough for this material.')
            return {'initialFlaw': initialFlaw, 'criticalFlaw': self.criticalFlawSize,
                    'cyclesToFailure': 0.0, 'lifeMargin': 0.0, 'thresholdExceeded': True}

        geometryFactor = GEOMETRY_FACTORS[self.geometryCase]['factor']
        stressRange    = self.operatingStress - self.minimumStress

        initialRange = geometryFactor * stressRange * np.sqrt(np.pi * initialFlaw)

        if initialRange < threshold:
            self.cyclesToFailure = np.inf
            self.lifeMargin      = np.inf
            self.fractureNotes.append(
                f'The initial stress intensity range of {initialRange / 1.0e6:.2f} MPa-sqrt(m) is '
                f'below the threshold of {threshold / 1.0e6:.2f}. The crack does not grow and the '
                f'life is unlimited by this mechanism. That is a stronger result than a large '
                f'cycle count and it is worth designing for.')
            return {'initialFlaw': initialFlaw, 'criticalFlaw': self.criticalFlawSize,
                    'initialStressIntensityRange': initialRange, 'threshold': threshold,
                    'cyclesToFailure': np.inf, 'lifeMargin': np.inf, 'thresholdExceeded': False}

        # -- Numerical integration in crack length -- #

        upperLimit = min(self.criticalFlawSize,
                         (1.0 / np.pi) * (PARIS_UPPER_FRACTION * self.fractureToughness /
                                          (geometryFactor * self.operatingStress)) ** 2)

        steps      = 2000
        flawSizes  = np.linspace(initialFlaw, upperLimit, steps)
        ranges     = geometryFactor * stressRange * np.sqrt(np.pi * flawSizes)

        # The Paris coefficient is quoted for dK in MPa-sqrt(m), which is the universal convention in
        # every published da/dN table. Everything else in this repository is base SI, so the
        # conversion has to happen here and only here. Feeding Pa-sqrt(m) into the power law with an
        # exponent near 3.3 overstates the growth rate by 1e20 and returns zero life, which is at
        # least an obvious failure rather than a plausible one.
        rangesMega = np.maximum(ranges, threshold) / 1.0e6
        growthRate = coefficient * rangesMega ** exponent

        # Below threshold contributes no growth, so those increments are dropped rather than
        # integrated at the threshold rate.
        growthRate[ranges < threshold] = np.inf

        with np.errstate(divide = 'ignore'):
            cycles = float(np.trapezoid(1.0 / growthRate, flawSizes)) \
                     if hasattr(np, 'trapezoid') else float(np.trapz(1.0 / growthRate, flawSizes))

        self.cyclesToFailure = cycles
        self.lifeMargin      = cycles / self.designCycles if self.designCycles else np.inf

        if self.lifeMargin < 4.0:
            self.fractureNotes.append(
                f'The crack growth life margin is {self.lifeMargin:.1f} against the four times '
                f'scatter factor conventionally required for a safe life analysis. This part does '
                f'not have adequate life from the assumed initial flaw.')

        return {'initialFlaw': initialFlaw, 'criticalFlaw': self.criticalFlawSize,
                'integrationLimit': upperLimit,
                'initialStressIntensityRange': initialRange, 'threshold': threshold,
                'parisCoefficient': coefficient, 'parisExponent': exponent,
                'cyclesToFailure': cycles, 'designCycles': self.designCycles,
                'lifeMargin': self.lifeMargin, 'thresholdExceeded': True}

    def calculateThresholdStress(self, flawSize: float = None) -> dict:

        '''

        The stress below which a crack of a given size does not grow at all.

            sigma_threshold = dK_th / (Y sqrt(pi a))

        A part held below this has unlimited life by the crack growth mechanism, which is a far
        stronger statement than any finite cycle count. On a pressure vessel that cycles many
        thousands of times it is often the criterion worth designing to.

        '''

        properties = queryMaterial(self.material, self.condition, self.temperature)
        threshold  = properties['fracture'].get('thresholdRange')

        if threshold is None:
            raise InvalidInputError(
                message       = f'No threshold stress intensity range for {self.material}.',
                parameterName = 'material', value = self.material,
                validRange    = 'A material with thresholdRange in its fracture block'
            )

        if flawSize is None:
            flawSize = self.initialFlawSize if not np.isnan(self.initialFlawSize) else \
                       NDE_FLAW_SIZES[self.inspectionMethod]['depth']

        geometryFactor = GEOMETRY_FACTORS[self.geometryCase]['factor']

        self.thresholdStress = threshold / (geometryFactor * np.sqrt(np.pi * flawSize))

        return {'flawSize': flawSize, 'thresholdRange': threshold,
                'thresholdStress': self.thresholdStress,
                'operatingStress': self.operatingStress,
                'belowThreshold': self.operatingStress < self.thresholdStress}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        if np.isnan(self.criticalFlawSize):
            self.calculateCriticalFlaw()

        rows = [
            ['Material',            f'{self.material} ({self.condition})'],
            ['Temperature',         f'{self.temperature:.1f} K'],
            ['Fracture toughness',  f'{self.fractureToughness / 1.0e6:.1f} MPa-sqrt(m) '
                                    f'({self.orientation})'],
            ['Geometry',            f'{self.geometryCase}, Y = '
                                    f'{GEOMETRY_FACTORS[self.geometryCase]["factor"]:.2f}'],
            ['Operating stress',    f'{self.operatingStress / 1.0e6:.1f} MPa'],
            ['Critical flaw depth', f'{self.criticalFlawSize * 1000.0:.3f} mm']
        ]

        if not np.isnan(self.proofStress):
            rows.append(['Proof stress',      f'{self.proofStress / 1.0e6:.1f} MPa'])
            rows.append(['Proof screens to',  f'{self.proofFlawSize * 1000.0:.3f} mm'])

        if not np.isnan(self.wallThickness):
            rows.append(['Wall thickness',    f'{self.wallThickness * 1000.0:.3f} mm'])
            rows.append(['Leak before burst', f'{"YES" if self.leakBeforeBurst else "NO"}'])

        if not np.isnan(self.cyclesToFailure):
            rows.append(['Cycles to failure',
                         'unlimited (below threshold)' if np.isinf(self.cyclesToFailure)
                         else f'{self.cyclesToFailure:.0f}'])
            rows.append(['Design cycles',     f'{self.designCycles}'])
            rows.append(['Life margin',
                         'unlimited' if np.isinf(self.lifeMargin) else f'{self.lifeMargin:.1f}x'])

        if not np.isnan(self.thresholdStress):
            rows.append(['Threshold stress',  f'{self.thresholdStress / 1.0e6:.1f} MPa'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'DAMAGE TOLERANCE')

        for note in self.fractureNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'damageTolerance.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.geometryCase not in GEOMETRY_FACTORS:
            raise InvalidInputError(
                message       = f'Unknown geometry case \'{self.geometryCase}\'.',
                parameterName = 'geometryCase', value = self.geometryCase,
                validRange    = str(sorted(GEOMETRY_FACTORS.keys()))
            )

        if self.inspectionMethod not in NDE_FLAW_SIZES:
            raise InvalidInputError(
                message       = f'Unknown inspection method \'{self.inspectionMethod}\'.',
                parameterName = 'inspectionMethod', value = self.inspectionMethod,
                validRange    = str(sorted(NDE_FLAW_SIZES.keys()))
            )

        if self.operatingStress <= 0.0:
            raise InvalidInputError(
                message       = 'Operating stress must be positive. A compressive membrane stress '
                                'does not drive crack growth and does not need this analysis.',
                parameterName = 'operatingStress', value = self.operatingStress,
                validRange    = 'Greater than 0 Pa'
            )

        if not np.isnan(self.proofStress) and self.proofStress <= self.operatingStress:
            raise InvalidInputError(
                message       = 'Proof stress must exceed operating stress, or the proof test '
                                'screens nothing that service would not already have found.',
                parameterName = 'proofStress', value = self.proofStress,
                validRange    = 'Greater than the operating stress'
            )
