
# -- PressureTest Class Definition -- #

'''

Proof and burst pressure test definition, and the stored energy that decides whether the test is
dangerous.

Two tests, with different purposes and different consequences:

**Proof** demonstrates that an article takes its design load without permanent deformation or
leakage. It is applied to every flight article as an acceptance test, so it must be non-destructive.

**Burst** demonstrates ultimate capability. It destroys the article, so it is a qualification test on
dedicated units, never an acceptance test.

The part of this class that matters most is not the pressure levels, which are a lookup. It is the
stored energy calculation.

    A liquid proof test stores almost no energy. If the article fails, it leaks.

    A pneumatic proof test at the same pressure stores enough energy to be genuinely dangerous,
    because the gas expands. A 10 litre volume at 20 MPa holds roughly 400 kJ, which is comparable to
    100 g of TNT.

That difference is why the rule is to proof with a liquid wherever possible, and why a pneumatic
proof needs a calculated standoff rather than an assumed one. The class computes the energy, converts
it to a TNT equivalent, and applies a scaled-distance standoff so the number is defensible rather
than a guess.

See Also:
---------
LeakTest        : Runs after proof, because proof can open a marginal joint
TestCampaign    : Where proof and burst sit in the qualification sequence
fluidSystems Line and Weld : The design-side wall thickness and joint derating these levels test

Theory: docs/ProofAndBurstTesting.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                               hoopStressCalculator, PRESSURE_TEST_FACTORS, PA_PER_PSIA, M_PER_FT,
                               InvalidInputError, TestInfeasibleError, createErrorContext)
except ImportError:
    from .campaignUtils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                                hoopStressCalculator, PRESSURE_TEST_FACTORS, PA_PER_PSIA, M_PER_FT,
                                InvalidInputError, TestInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Energy released by one kilogram of TNT [J]. Used to express stored pneumatic energy in a unit that
# blast standoff correlations are written against.
TNT_ENERGY_PER_KG = 4.184e6

# Hopkinson-Cranz scaled distance thresholds, in m / kg^(1/3) of TNT equivalent. Blast overpressure
# at a given scaled distance is approximately constant regardless of charge size, which is what makes
# these usable as standoff criteria.
#
# The values below are conventional personnel-safety scaled distances. They are indicative: a real
# standoff comes from the facility safety analysis and the applicable range or site standard, not
# from a correlation in a library.
SCALED_DISTANCE_CRITERIA = {
    'personnel unprotected':  22.0,   # eardrum rupture threshold with margin
    'personnel behind barrier': 8.0,  # substantial barricade assumed
    'equipment damage limit':   4.0,  # threshold of damage to nearby hardware
    'structural damage':        2.0   # inside this, expect structural damage
}

# Proof test hold times [s]. Long enough for the article to reach equilibrium and for a leak to
# manifest, short enough that creep is not being introduced.
DEFAULT_PROOF_HOLD_TIME = 300.0

# Permanent set acceptance criterion, as a fraction of the elastic deflection at proof. Anything
# above this indicates yielding somewhere.
PERMANENT_SET_LIMIT = 0.002

class PressureTest:

    '''

    Proof and burst test levels, hold times, stored energy and safe standoff.

    Primary Input Properties:
    -------------------------
    maximumExpectedOperatingPressure : float
        MEOP [Pa, gauge]. Not the nominal operating pressure: it must include transients, relief
        accumulation and thermal rise.
    hardwareClass : str
        Key into PRESSURE_TEST_FACTORS, which sets the proof and burst factors
    testMedium : str
        'liquid' or 'gas'. Determines the stored energy and therefore the hazard.
    testFluid : str
        Species name for the gas case, passed to fluidProps
    testVolume : float
        Internal volume of the article under test [m^3]
    testTemperature : float
        Test temperature [K]
    material : str
        Article material, key into materialProperties
    outerDiameter : float
        Article outer diameter [m], for the hoop stress check
    wallThickness : float
        Article wall thickness [m]
    proofFactor / burstFactor : float
        Overrides for the hardware class defaults

    Key Output Properties:
    ----------------------
    proofPressure / burstPressure : float
        Test levels [Pa, gauge]
    storedEnergy : float
        Energy released on failure at proof pressure [J]
    tntEquivalent : float
        Stored energy as an equivalent mass of TNT [kg]
    safeStandoffDistance : dict
        Standoff [m] at each scaled-distance criterion
    hoopStressAtProof : float
        Hoop stress at proof pressure [Pa]
    yieldMargin : float
        Material yield strength over the proof hoop stress [-]

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    calculateLevels()              Proof and burst pressures, hold times
    calculateStoredEnergy()        Stored energy, TNT equivalent, standoff distances
    checkArticleCapability()       Hoop stress and yield margin at proof
    generateReport(outputDir)      Formatted results table

    Typical Workflow:
    -----------------
    >>> test = PressureTest()
    >>> test.setInputs({'maximumExpectedOperatingPressure': 2.4e6,
    ...                 'hardwareClass': 'line hazardous fluid',
    ...                 'testMedium': 'liquid', 'testVolume': 0.002,
    ...                 'material': '316L', 'outerDiameter': 0.00953,
    ...                 'wallThickness': 0.00165})
    >>> test.calculateLevels()
    >>> test.calculateStoredEnergy()
    >>> test.checkArticleCapability()
    >>> print(test.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Requirement -- #

        # MEOP is where the errors start. It must include the nominal operating pressure, the
        # regulator outlet band maximum, relief valve accumulation, water hammer surge if the
        # transient reaches this article, and thermal rise from a locked-up volume. A design that
        # took MEOP as the nominal operating pressure has no margin against a transient at all.
        self.maximumExpectedOperatingPressure = np.nan  # [Pa, gauge]
        self.hardwareClass                    = 'component'  # key into PRESSURE_TEST_FACTORS
        self.proofFactor                      = np.nan  # [-], overrides the class default
        self.burstFactor                      = np.nan  # [-], overrides the class default

        # -- Test Setup -- #

        self.testMedium      = 'liquid'  # 'liquid' or 'gas'
        self.testFluid       = 'Water'   # species for the stored energy calculation
        self.testVolume      = np.nan    # [m^3], internal volume of the article
        self.testTemperature = 293.15    # [K]
        self.holdTime        = np.nan    # [s], defaults to DEFAULT_PROOF_HOLD_TIME

        # -- Article -- #

        self.material        = '316L'    # key into materialProperties
        self.outerDiameter   = np.nan    # [m]
        self.wallThickness   = np.nan    # [m]

        # -- Results -- #

        self.proofPressure        = np.nan  # [Pa, gauge]
        self.burstPressure        = np.nan  # [Pa, gauge]
        self.storedEnergy         = np.nan  # [J]
        self.tntEquivalent        = np.nan  # [kg]
        self.safeStandoffDistance = {}      # {criterion: metres}
        self.hoopStressAtProof    = np.nan  # [Pa]
        self.hoopStressAtBurst    = np.nan  # [Pa]
        self.yieldMargin          = np.nan  # [-]
        self.ultimateMargin       = np.nan  # [-]
        self.designNotes          = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: maximumExpectedOperatingPressure.

        '''

        requiredParams = {
            'maximumExpectedOperatingPressure': 'MEOP not provided. It is the basis of every pressure '
                                                'test level and it is not the nominal operating pressure.'
        }

        optionalParams = ['hardwareClass', 'proofFactor', 'burstFactor', 'testMedium', 'testFluid',
                          'testVolume', 'testTemperature', 'holdTime', 'material',
                          'outerDiameter', 'wallThickness']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateLevels(self) -> dict:

        '''

        Proof and burst test pressures from MEOP and the hardware class factors.

            proof = proofFactor x MEOP
            burst = burstFactor x MEOP

        The factors come from AIAA S-080 and S-081 for flight hardware. The spread across hardware
        classes is worth noting: a metallic pressure vessel takes a 2.0 burst factor while a
        hazardous fluid line takes 4.0, because a line is thin, exposed, routinely handled, and the
        consequence of its rupture is a personnel hazard rather than a mission loss.

        Ground piping under ASME B31.3 works differently and does not use a burst factor at all: it
        sets an allowable stress and requires a 1.5x hydrostatic proof. The two systems are not
        interchangeable and an article qualified to one is not automatically acceptable under the
        other.

        '''

        classData = PRESSURE_TEST_FACTORS[self.hardwareClass.strip().lower()]

        proofFactor = self.proofFactor if not np.isnan(self.proofFactor) else classData['proof']
        burstFactor = self.burstFactor if not np.isnan(self.burstFactor) else classData['burst']

        self.proofPressure = proofFactor * self.maximumExpectedOperatingPressure
        self.burstPressure = burstFactor * self.maximumExpectedOperatingPressure

        if np.isnan(self.holdTime):
            self.holdTime = DEFAULT_PROOF_HOLD_TIME

        return {
            'maximumExpectedOperatingPressure': self.maximumExpectedOperatingPressure,
            'proofFactor':    proofFactor,
            'proofPressure':  self.proofPressure,
            'burstFactor':    burstFactor,
            'burstPressure':  self.burstPressure,
            'holdTime':       self.holdTime
        }

    def calculateStoredEnergy(self) -> dict:

        '''

        Stored energy at proof pressure, its TNT equivalent, and the resulting standoff distances.

        **This is the calculation that decides whether the test is dangerous**, and it is why the
        rule is to proof with a liquid wherever possible.

        For a gas expanding isentropically from the test pressure to ambient, the available work is

            E = (P * V) / (gamma - 1) * [ 1 - (P_ambient / P)^((gamma-1)/gamma) ]

        For a liquid, the stored energy is the compression energy only:

            E = (dP)^2 * V / (2 * K)

        with K the bulk modulus. The ratio between the two is enormous. Ten litres of water at
        20 MPa stores about 45 J. The same volume of nitrogen at the same pressure stores roughly
        400 kJ, a factor of nearly ten thousand. That is the difference between an article that
        leaks when it fails and one that becomes a fragmentation hazard.

        The TNT equivalent and the Hopkinson-Cranz scaled distance give a defensible standoff:

            R = Z * W^(1/3)

        with Z the scaled distance criterion and W the TNT-equivalent mass. Blast overpressure at a
        given scaled distance is approximately independent of charge size, which is what makes this
        usable.

        **These numbers are indicative and do not replace a facility safety analysis.** A real
        standoff comes from the applicable range or site standard. What this calculation is for is
        making the magnitude visible at planning time, so that a pneumatic proof test is a considered
        decision rather than a default.

        '''

        if np.isnan(self.proofPressure):
            self.calculateLevels()

        if np.isnan(self.testVolume):
            raise InvalidInputError(
                message       = 'calculateStoredEnergy needs the internal volume of the article.',
                parameterName = 'testVolume', value = self.testVolume, validRange = 'Positive real'
            )

        ambientPressure = 101325.0
        absolutePressure = self.proofPressure + ambientPressure

        if self.testMedium.strip().lower() == 'gas':

            gamma = float(fluidProps(self.testFluid, 'TP', 'Cp/Cv', self.testTemperature, absolutePressure))

            # Isentropic expansion work available from the compressed gas
            pressureRatio     = ambientPressure / absolutePressure
            self.storedEnergy = ((absolutePressure * self.testVolume) / (gamma - 1.0) *
                                 (1.0 - pressureRatio**((gamma - 1.0) / gamma)))

            self.designNotes.append(
                f'This is a PNEUMATIC proof test storing {self.storedEnergy / 1.0e3:.1f} kJ. A hydrostatic test '
                f'at the same pressure would store a small fraction of that. Use a liquid unless there is a '
                f'specific reason the article cannot be wetted, and if there is, barricade and clear the area.')

        else:

            # Liquid compression energy. Bulk modulus from the speed of sound, K = rho * c^2.
            density      = float(fluidProps(self.testFluid, 'TP', 'D', self.testTemperature, absolutePressure))
            speedOfSound = float(fluidProps(self.testFluid, 'TP', 'W', self.testTemperature, absolutePressure))
            bulkModulus  = density * speedOfSound**2

            self.storedEnergy = self.proofPressure**2 * self.testVolume / (2.0 * bulkModulus)

        self.tntEquivalent = self.storedEnergy / TNT_ENERGY_PER_KG

        # Hopkinson-Cranz scaled distance: R = Z * W^(1/3)
        self.safeStandoffDistance = {}
        for criterion, scaledDistance in SCALED_DISTANCE_CRITERIA.items():
            self.safeStandoffDistance[criterion] = scaledDistance * self.tntEquivalent**(1.0 / 3.0)

        return {
            'testMedium':      self.testMedium,
            'storedEnergy':    self.storedEnergy,
            'tntEquivalent':   self.tntEquivalent,
            'safeStandoffDistance': self.safeStandoffDistance
        }

    def checkArticleCapability(self) -> dict:

        '''

        Hoop stress at proof and burst, and the margin against the material allowables.

        The proof test must not yield the article, because proof is an acceptance test applied to
        flight hardware. If the hoop stress at proof exceeds the material yield strength, the test as
        specified will damage every article it is applied to, which is a design problem rather than a
        test problem.

        The burst prediction is a check that the article will actually survive to its required burst
        pressure. A burst test that fails below the required level is a design finding; one that fails
        somewhere other than the predicted location is an analysis finding even if the pressure was
        adequate.

        '''

        if np.isnan(self.proofPressure):
            self.calculateLevels()

        if np.isnan(self.outerDiameter) or np.isnan(self.wallThickness):
            raise InvalidInputError(
                message       = 'checkArticleCapability needs the article outer diameter and wall thickness.',
                parameterName = 'outerDiameter/wallThickness',
                value         = (self.outerDiameter, self.wallThickness),
                validRange    = 'Both positive real'
            )

        innerDiameter = self.outerDiameter - 2.0 * self.wallThickness
        properties    = materialProperties(self.material, self.testTemperature)

        self.hoopStressAtProof = hoopStressCalculator(self.proofPressure, innerDiameter,
                                                      thickness = self.wallThickness)
        self.hoopStressAtBurst = hoopStressCalculator(self.burstPressure, innerDiameter,
                                                      thickness = self.wallThickness)

        self.yieldMargin    = properties['yieldStrength'] / self.hoopStressAtProof
        self.ultimateMargin = properties['ultimateStrength'] / self.hoopStressAtBurst

        if self.yieldMargin < 1.0:
            raise TestInfeasibleError(
                message = (f'Hoop stress at proof pressure is {self.hoopStressAtProof / 1.0e6:.1f} MPa against a '
                           f'{properties["yieldStrength"] / 1.0e6:.1f} MPa yield strength. The proof test would '
                           f'permanently deform every article it is applied to. This is a design problem, not a '
                           f'test problem.'),
                context    = createErrorContext(component = 'PressureTest', material = self.material),
                required   = self.hoopStressAtProof,
                achievable = properties['yieldStrength'],
                method     = 'proof pressure test'
            )

        if self.yieldMargin < 1.25:
            self.designNotes.append(
                f'Yield margin at proof is only {self.yieldMargin:.2f}. Proof is applied to every flight article, '
                f'so a marginal article will accumulate set over repeated tests and rework cycles.')

        if self.ultimateMargin < 1.0:
            self.designNotes.append(
                f'Predicted hoop stress at burst pressure ({self.hoopStressAtBurst / 1.0e6:.1f} MPa) exceeds the '
                f'material ultimate ({properties["ultimateStrength"] / 1.0e6:.1f} MPa). The article is not expected '
                f'to reach its required burst pressure.')

        return {
            'hoopStressAtProof': self.hoopStressAtProof,
            'hoopStressAtBurst': self.hoopStressAtBurst,
            'yieldStrength':     properties['yieldStrength'],
            'ultimateStrength':  properties['ultimateStrength'],
            'yieldMargin':       self.yieldMargin,
            'ultimateMargin':    self.ultimateMargin,
            'permanentSetLimit': PERMANENT_SET_LIMIT
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        classData = PRESSURE_TEST_FACTORS[self.hardwareClass.strip().lower()]

        rows = [
            ['Hardware class',        f'{self.hardwareClass}'],
            ['MEOP',                  f'{self.maximumExpectedOperatingPressure / 1.0e6:.4f} MPa '
                                      f'({self.maximumExpectedOperatingPressure / PA_PER_PSIA:.1f} psig)'],
            ['Proof factor',          f'{classData["proof"]:.2f}'],
            ['Proof pressure',        f'{self.proofPressure / 1.0e6:.4f} MPa '
                                      f'({self.proofPressure / PA_PER_PSIA:.1f} psig)'],
            ['Proof hold time',       f'{self.holdTime:.0f} s'],
            ['Burst factor',          f'{classData["burst"]:.2f}'],
            ['Burst pressure',        f'{self.burstPressure / 1.0e6:.4f} MPa '
                                      f'({self.burstPressure / PA_PER_PSIA:.1f} psig)'],
            ['Test medium',           f'{self.testMedium} ({self.testFluid})'],
            ['Test temperature',      f'{self.testTemperature:.2f} K']
        ]

        if not np.isnan(self.storedEnergy):
            rows.append(['Test volume',      f'{self.testVolume * 1.0e3:.3f} L'])
            rows.append(['Stored energy',    f'{self.storedEnergy / 1.0e3:.4f} kJ'])
            rows.append(['TNT equivalent',   f'{self.tntEquivalent * 1.0e3:.4f} g'])
            for criterion, distance in self.safeStandoffDistance.items():
                rows.append([f'  standoff, {criterion}', f'{distance:.2f} m ({distance / M_PER_FT:.1f} ft)'])

        if not np.isnan(self.hoopStressAtProof):
            rows.append(['Article material',    f'{self.material}'])
            rows.append(['Hoop stress at proof', f'{self.hoopStressAtProof / 1.0e6:.2f} MPa'])
            rows.append(['Yield margin at proof', f'{self.yieldMargin:.2f}'])
            rows.append(['Hoop stress at burst', f'{self.hoopStressAtBurst / 1.0e6:.2f} MPa'])
            rows.append(['Ultimate margin at burst', f'{self.ultimateMargin:.2f}'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'PRESSURE TEST REPORT')

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'pressureTestReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.hardwareClass.strip().lower() not in PRESSURE_TEST_FACTORS:
            raise InvalidInputError(
                message       = f'Unknown hardware class \'{self.hardwareClass}\'.',
                parameterName = 'hardwareClass', value = self.hardwareClass,
                validRange    = str(sorted(PRESSURE_TEST_FACTORS.keys()))
            )

        if self.maximumExpectedOperatingPressure <= 0.0:
            raise InvalidInputError(
                message       = 'MEOP must be positive.',
                parameterName = 'maximumExpectedOperatingPressure',
                value         = self.maximumExpectedOperatingPressure,
                validRange    = 'Greater than 0 Pa gauge'
            )

        if self.testMedium.strip().lower() not in ('liquid', 'gas'):
            raise InvalidInputError(
                message       = f'Unknown test medium \'{self.testMedium}\'.',
                parameterName = 'testMedium', value = self.testMedium,
                validRange    = 'liquid or gas'
            )
