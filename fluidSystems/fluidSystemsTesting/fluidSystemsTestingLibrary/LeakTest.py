
# -- LeakTest Class Definition -- #

'''

Leak test method selection, sensitivity, duration and feasibility.

This class answers the question that should be asked at requirement-writing time and usually is not:
**can the leak rate we just specified actually be measured?**

The available detection methods span nine orders of magnitude, from an ultrasonic check at 1e-2 scc/s
to a hard-vacuum mass spectrometer at 1e-11. That spread means the choice of method is a hard
constraint on what leak rate a program is allowed to specify. A requirement below the floor of every
available method is not a requirement; it is a wish that will be dispositioned by waiver.

The physics of the leak itself lives in the fluidSystems design library, and this class delegates to
it rather than reimplementing it. `LeakPath` already knows the flow regimes, the detection method
sensitivities, the pressure decay temperature limit and the hazard-derived allowable. What this class
adds is the test engineering on top: which method, at what sensitivity, for how long, with what
calibration, at which point in the campaign.

The single most useful thing it does is refuse to plan a test that cannot work.

See Also:
---------
fluidSystems LeakPath : The leak physics, regimes and detection sensitivities this class uses
PressureTest          : Runs before leak test, because proof can open a marginal joint
TestCampaign          : Where leak testing sits in the sequence, and why it repeats

Theory: docs/LeakTesting.md, and fluidSystems/docs/Leaks.md for the physics

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (applyInputs, formatReportTable, leakRateConvert,
                               InvalidInputError, TestInfeasibleError, createErrorContext)
except ImportError:
    from .campaignUtils import (applyInputs, formatReportTable, leakRateConvert,
                                InvalidInputError, TestInfeasibleError, createErrorContext)

# The fluidSystems design library, put on the path by the campaignUtils bootstrap.
from LeakPath import LeakPath, DETECTION_METHODS

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Margin required between the specified leak rate and the sensitivity floor of the chosen method.
#
# A requirement set at the exact floor of a method makes every measurement a coin flip between pass
# and fail, and turns every disposition into an argument about instrumentation rather than about
# hardware. A factor of ten is the conventional minimum.
DETECTION_MARGIN = 10.0

# Where in a campaign a leak test is performed, and why. Leak testing repeats more than any other
# test because it is the one that detects damage from everything else.
LEAK_TEST_POINTS = {
    'post assembly':      'Baseline, before anything is done to the article',
    'post proof':         'Proof can open a marginal joint',
    'post vibration':     'Vibration loosens joints and damages seals',
    'post thermal cycle': 'Differential contraction is what breaks a cryogenic seal',
    'at temperature':     'A seal that passes at ambient can fail cold',
    'pre flight':         'Final verification in the flight configuration'
}

# Calibrated leak standard practice: every test is bracketed by a calibration so the sensitivity is
# known at the time of the measurement rather than assumed from the instrument datasheet.
CALIBRATION_BRACKET_REQUIRED = True

class LeakTest:

    '''

    Leak test planning: method selection, sensitivity, duration and feasibility.

    Primary Input Properties:
    -------------------------
    allowableLeakRate : float
        The specified leak rate the test must verify [scc/s of the test species]
    species : str
        Test gas, almost always helium
    serviceFluid : str
        The fluid the hardware actually contains, for scaling the helium result
    testPressure : float
        Test pressure [Pa, absolute]
    downstreamPressure : float
        Low side pressure [Pa, absolute]. Zero for a vacuum-side measurement.
    temperature : float
        Test temperature [K]
    testVolume : float
        Isolated volume, for a pressure decay test [m^3]
    transducerResolution : float
        Smallest resolvable pressure change [Pa]
    testDuration : float
        Available test duration [s]
    temperatureStability : float
        Expected temperature drift over the test [K]
    jointCount : int
        Number of joints in the article, for the allocation

    Key Output Properties:
    ----------------------
    selectedMethod : str
        The least sensitive method that clears the requirement with margin
    methodSensitivity : float
        That method's floor [scc/s]
    detectionMargin : float
        Allowable rate over the method floor [-]
    perJointAllowable : float
        The system allowable divided across the joints [scc/s]
    equivalentDiameter : float
        Equivalent hole size for the allowable rate [m]
    pressureDecayFeasible : bool
        Whether a pressure decay test can verify this requirement
    serviceFluidLeakRate : float
        The helium result scaled to the service fluid [scc/s]

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    selectMethod()                 Choose a detection method and check it has margin
    allocateAcrossJoints()         Divide the system allowable across the joints
    evaluatePressureDecay()        Feasibility of a pressure decay test at these conditions
    scaleToServiceFluid()          Convert the helium test result to the service fluid
    generateReport(outputDir)      Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Requirement -- #

        self.allowableLeakRate    = np.nan  # [scc/s]
        self.species              = 'He'    # test gas
        self.serviceFluid         = ''      # what the hardware actually contains
        self.jointCount           = 1       # [-]

        # -- Test Conditions -- #

        self.testPressure         = np.nan  # [Pa, absolute]
        self.downstreamPressure   = 0.0     # [Pa, absolute]
        self.temperature          = 293.15  # [K]
        self.pathLength           = 1.0e-3  # [m], nominal sealing land

        # -- Pressure Decay Setup -- #

        self.testVolume           = np.nan  # [m^3]
        self.transducerResolution = np.nan  # [Pa]
        self.testDuration         = np.nan  # [s]
        self.temperatureStability = 0.1     # [K]

        # -- Results -- #

        self.selectedMethod        = ''      # key into DETECTION_METHODS
        self.methodSensitivity     = np.nan  # [scc/s]
        self.detectionMargin       = np.nan  # [-]
        self.perJointAllowable     = np.nan  # [scc/s]
        self.equivalentDiameter    = np.nan  # [m]
        self.flowRegime            = ''      # from the LeakPath physics
        self.pressureDecayFeasible = None    # [-]
        self.pressureDecayFloor    = np.nan  # [scc/s]
        self.pressureDecayLimitedBy = ''     # 'temperature drift' or 'transducer resolution'
        self.serviceFluidLeakRate  = np.nan  # [scc/s]
        self.leakPath              = None    # the underlying LeakPath object
        self.designNotes           = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: allowableLeakRate, testPressure.

        '''

        requiredParams = {
            'allowableLeakRate': 'Allowable leak rate not provided. It is the requirement the test exists to verify.',
            'testPressure':      'Leak test pressure not provided.'
        }

        optionalParams = ['species', 'serviceFluid', 'jointCount', 'downstreamPressure',
                          'temperature', 'pathLength', 'testVolume', 'transducerResolution',
                          'testDuration', 'temperatureStability']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()
        self._buildLeakPath()

    def selectMethod(self) -> dict:

        '''

        Choose the least sensitive detection method that clears the requirement with margin.

        Least sensitive rather than most sensitive is deliberate. A mass spectrometer will measure
        anything, and it is slow, expensive, and requires the article to hold vacuum. The right method
        is the cheapest one that can actually see the requirement with a factor of ten to spare.

        **If no method clears the requirement, this raises.** That is the intended behaviour: a leak
        requirement that cannot be measured is a planning failure, and it should surface while the
        requirement can still be renegotiated rather than during the test campaign.

        The delegation to `LeakPath.selectDetectionMethod` means this uses exactly the same
        sensitivity floors the design library reasons about, so a design-side statement about
        achievable leak class and a test-side statement about measurability cannot drift apart.

        '''

        self.selectedMethod    = self.leakPath.selectDetectionMethod()
        self.methodSensitivity = DETECTION_METHODS[self.selectedMethod]['sensitivity']
        self.detectionMargin   = self.allowableLeakRate / self.methodSensitivity

        # The floor of the most sensitive method available
        finestMethod      = min(DETECTION_METHODS.items(), key = lambda item: item[1]['sensitivity'])
        finestSensitivity = finestMethod[1]['sensitivity']

        if self.allowableLeakRate < finestSensitivity * DETECTION_MARGIN:
            raise TestInfeasibleError(
                message = (f'A {self.allowableLeakRate:.2e} scc/s requirement cannot be verified with '
                           f'{DETECTION_MARGIN:.0f}x margin by any available method. The most sensitive is '
                           f'{finestMethod[0]} at {finestSensitivity:.1e} scc/s. Either relax the requirement, '
                           f'allocate it across fewer joints, or accept verification at the instrument floor with '
                           f'the resulting pass/fail ambiguity.'),
                context    = createErrorContext(component = 'LeakTest', fluid = self.species),
                required   = self.allowableLeakRate,
                achievable = finestSensitivity * DETECTION_MARGIN,
                method     = finestMethod[0]
            )

        if self.detectionMargin < DETECTION_MARGIN:
            self.designNotes.append(
                f'The {self.selectedMethod} floor is {self.methodSensitivity:.1e} scc/s against a '
                f'{self.allowableLeakRate:.2e} scc/s requirement, a margin of only {self.detectionMargin:.1f}. '
                f'Move to a more sensitive method or every measurement will be a pass/fail argument.')

        if CALIBRATION_BRACKET_REQUIRED:
            self.designNotes.append(
                'Bracket the test with a calibrated leak standard before and after. If the two calibrations '
                'disagree, the data between them is not usable.')

        return {
            'selectedMethod':    self.selectedMethod,
            'methodSensitivity': self.methodSensitivity,
            'detectionMargin':   self.detectionMargin,
            'description':       DETECTION_METHODS[self.selectedMethod]['description'],
            'limitation':        DETECTION_METHODS[self.selectedMethod]['limitation']
        }

    def allocateAcrossJoints(self) -> dict:

        '''

        Divide the system allowable across the joints in the article.

        Leak rates add. A system allowable of 1e-5 scc/s across twenty joints is 5e-7 scc/s per joint,
        which is two orders of magnitude tighter than an AN flare fitting achieves and which
        immediately tells you the joint architecture has to change.

        This is the calculation that connects a hazard-derived system requirement to a joint selection
        decision, and doing it early is what stops a program discovering at leak check that its
        fittings were never going to work.

        '''

        if self.jointCount < 1:
            raise InvalidInputError(
                message       = 'Joint count must be at least 1.',
                parameterName = 'jointCount', value = self.jointCount, validRange = '1 or greater'
            )

        self.perJointAllowable = self.allowableLeakRate / self.jointCount

        # Compare against what the common joint families actually achieve, from the design library
        achievableClasses = {
            'welded':                1.0e-9,
            'VCR metal gasket':      4.0e-9,
            'compression fitting':   1.0e-6,
            'SAE boss o-ring':       1.0e-6,
            'AN flare':              1.0e-4,
            'NPT':                   1.0e-3
        }

        adequate = [name for name, rate in achievableClasses.items() if rate <= self.perJointAllowable]

        if not adequate:
            self.designNotes.append(
                f'A per-joint allowable of {self.perJointAllowable:.2e} scc/s is tighter than any joint family '
                f'achieves, including welded at 1e-9. Reduce the joint count or relax the system requirement.')
        else:
            self.designNotes.append(
                f'A per-joint allowable of {self.perJointAllowable:.2e} scc/s across {self.jointCount} joints '
                f'permits: {", ".join(adequate)}.')

        return {
            'systemAllowable':    self.allowableLeakRate,
            'jointCount':         self.jointCount,
            'perJointAllowable':  self.perJointAllowable,
            'adequateJointTypes': adequate,
            'achievableClasses':  achievableClasses
        }

    def evaluatePressureDecay(self) -> dict:

        '''

        Feasibility of verifying this requirement by pressure decay.

        Delegates to `LeakPath.calculatePressureDecayTest`, which carries the physics: the transducer
        resolution floor, the temperature drift floor, and which of the two binds.

        The result is almost always the same and it is almost always surprising to whoever proposed
        the test. **Pressure decay is temperature limited, not transducer limited.** For a fixed
        volume of gas, dP/P equals dT/T, so 0.1 K of drift at 10 MPa is 3.4 kPa of apparent pressure
        change, which is orders of magnitude above any leak signal worth chasing.

        Pressure decay is a system integrity check, not a joint qualification test, and this method
        exists to make that concrete before someone schedules a week of it.

        '''

        if any(np.isnan(value) for value in (self.testVolume, self.transducerResolution, self.testDuration)):
            raise InvalidInputError(
                message       = 'evaluatePressureDecay needs testVolume, transducerResolution and testDuration.',
                parameterName = 'testVolume/transducerResolution/testDuration',
                value         = (self.testVolume, self.transducerResolution, self.testDuration),
                validRange    = 'All positive real'
            )

        result = self.leakPath.calculatePressureDecayTest(
            testVolume           = self.testVolume,
            transducerResolution = self.transducerResolution,
            testDuration         = self.testDuration,
            temperatureStability = self.temperatureStability)

        self.pressureDecayFloor     = result['overallFloorSccs']
        self.pressureDecayLimitedBy = result['limitedBy']
        self.pressureDecayFeasible  = result['feasible']

        if not self.pressureDecayFeasible:
            requiredHours = result['requiredDurationSeconds'] / 3600.0
            self.designNotes.append(
                f'Pressure decay cannot verify this requirement. The floor is {self.pressureDecayFloor:.2e} scc/s, '
                f'limited by {self.pressureDecayLimitedBy}, against a {self.allowableLeakRate:.2e} scc/s target. '
                f'Reaching it would take {requiredHours:.0f} hours. Use {self.selectedMethod or "a tracer gas method"} '
                f'instead, or add a temperature-compensated reference volume.')

        return result

    def scaleToServiceFluid(self) -> dict:

        '''

        Scale the helium test result to the fluid the hardware actually contains.

        Delegates to `LeakPath.scaleToSpecies`, which carries the regime dependence. The two limits
        point in opposite directions and that is why this cannot be a single factor:

            molecular flow:  rate scales as 1/sqrt(M), so nitrogen leaks 2.6x less than helium
            viscous flow:    rate scales as 1/mu, so nitrogen leaks 10 percent MORE than helium

        Helium is more viscous than nitrogen at room temperature, which surprises everyone and which
        makes a helium test into vacuum conservative while a helium test at pressure into atmosphere
        is slightly optimistic.

        '''

        if not self.serviceFluid:
            raise InvalidInputError(
                message       = 'scaleToServiceFluid needs the service fluid the hardware contains.',
                parameterName = 'serviceFluid', value = self.serviceFluid, validRange = 'A species name'
            )

        self.leakPath.leakRate     = self.allowableLeakRate
        self.leakPath.leakRateUnit = 'sccs'

        result = self.leakPath.scaleToSpecies(self.serviceFluid)
        self.serviceFluidLeakRate = result['targetLeakRate']

        if result['appliedRatio'] < 1.0:
            self.designNotes.append(
                f'A helium test is conservative here: the same path passes {result["appliedRatio"]:.2f}x as much '
                f'{self.serviceFluid} as helium in the {result["regime"]} regime.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        rows = [
            ['Test species',           f'{self.species}'],
            ['Allowable leak rate',    f'{self.allowableLeakRate:.3e} scc/s'],
            ['  as mbar-L/s',          f'{leakRateConvert(self.allowableLeakRate, "sccs", "mbarls", species = self.species):.3e}'],
            ['  as lbm/yr',            f'{leakRateConvert(self.allowableLeakRate, "sccs", "lbmyr", species = self.species):.3e}'],
            ['Test pressure',          f'{self.testPressure / 1.0e6:.4f} MPa'],
            ['Test temperature',       f'{self.temperature:.2f} K'],
            ['Flow regime',            f'{self.flowRegime}'],
            ['Equivalent hole',        f'{self.equivalentDiameter * 1.0e6:.4f} micron']
        ]

        if self.selectedMethod:
            rows.extend([
                ['Selected method',    f'{self.selectedMethod}'],
                ['Method floor',       f'{self.methodSensitivity:.1e} scc/s'],
                ['Detection margin',   f'{self.detectionMargin:.1f}x']
            ])

        if not np.isnan(self.perJointAllowable):
            rows.extend([
                ['Joint count',        f'{self.jointCount:d}'],
                ['Per-joint allowable', f'{self.perJointAllowable:.3e} scc/s']
            ])

        if self.pressureDecayFeasible is not None:
            rows.extend([
                ['Pressure decay floor', f'{self.pressureDecayFloor:.3e} scc/s'],
                ['  limited by',         f'{self.pressureDecayLimitedBy}'],
                ['  feasible',           f'{self.pressureDecayFeasible}']
            ])

        if not np.isnan(self.serviceFluidLeakRate):
            rows.append([f'Scaled to {self.serviceFluid}', f'{self.serviceFluidLeakRate:.3e} scc/s'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'LEAK TEST PLAN')

        pointRows = [[point, reason] for point, reason in LEAK_TEST_POINTS.items()]
        report += '\n\n' + formatReportTable(pointRows, ['Test point', 'Why it is there'],
                                             title = 'WHERE LEAK TESTING REPEATS IN THE CAMPAIGN')

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'leakTestReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.allowableLeakRate <= 0.0:
            raise InvalidInputError(
                message       = 'Allowable leak rate must be positive.',
                parameterName = 'allowableLeakRate', value = self.allowableLeakRate,
                validRange    = 'Greater than 0 scc/s'
            )

        if self.testPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Leak test pressure must be absolute and positive.',
                parameterName = 'testPressure', value = self.testPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

    def _buildLeakPath(self) -> None:

        '''

        Construct the underlying LeakPath from the fluidSystems design library and solve it for the
        equivalent geometry, so the test plan and the design-side physics stay consistent.

        '''

        self.leakPath = LeakPath()
        self.leakPath.setInputs({
            'species':            self.species,
            'upstreamPressure':   self.testPressure,
            'downstreamPressure': self.downstreamPressure,
            'temperature':        self.temperature,
            'length':             self.pathLength,
            'leakRate':           self.allowableLeakRate,
            'leakRateUnit':       'sccs'
        })

        self.equivalentDiameter = self.leakPath.calculateEquivalentDiameter()
        self.flowRegime         = self.leakPath.regime
