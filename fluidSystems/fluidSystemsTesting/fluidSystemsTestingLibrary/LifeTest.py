
# -- LifeTest Class Definition -- #

'''

Life and endurance test definition, including accelerated testing.

The requirement is straightforward: demonstrate four times the expected life. The engineering is in
what "life" means for a given article and whether the test can be run in the time available.

**Life is not one number.** A valve has actuation cycles, a catalyst bed has pulses and cumulative
burn time, a seal has compressed hours at temperature, a bellows has flex cycles, a pressure vessel
has pressure cycles. Testing the wrong one demonstrates nothing: cycling a valve open and closed at
ambient with no differential tests the actuator, not the seat.

**Acceleration is how a ten-year life fits in a six-month program**, and it rests on a model. Two
are standard:

    Arrhenius, for thermally activated degradation:
        AF = exp( (Ea / k) * (1/T_use - 1/T_test) )

    Coffin-Manson, for thermal cycling fatigue:
        AF = (dT_test / dT_use)^n

Both require an activation energy or an exponent that is material and mechanism specific. Using a
default is a stated assumption, not a calculation, and this class says so every time.

The failure mode is the point. A life test that produces no failures at 4x has demonstrated the
margin; one that produces a failure at 3.5x has demonstrated considerably more, because now the
wear-out mechanism is known.

See Also:
---------
EnvironmentalTest : Environment-driven fatigue rather than cycle-driven wear
SampleSize        : How many articles the life demonstration needs
TestCampaign      : Where life testing sits in the sequence

Theory: docs/LifeAndEnduranceTesting.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (applyInputs, formatReportTable, LIFE_TEST_FACTOR,
                               DEFAULT_ACTIVATION_ENERGY, BOLTZMANN_EV,
                               DEFAULT_COFFIN_MANSON_EXPONENT,
                               InvalidInputError, TestInfeasibleError, createErrorContext)
except ImportError:
    from .campaignUtils import (applyInputs, formatReportTable, LIFE_TEST_FACTOR,
                                DEFAULT_ACTIVATION_ENERGY, BOLTZMANN_EV,
                                DEFAULT_COFFIN_MANSON_EXPONENT,
                                InvalidInputError, TestInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# What "life" means, by article type, and the condition the test must reproduce.
#
# The condition column is the one that matters. Cycling at the wrong condition demonstrates the wrong
# thing, and it is the most common way a life test passes while the hardware still fails in service.
LIFE_DEFINITIONS = {
    'valve': {
        'unit': 'actuation cycles',
        'condition': 'At the operating differential, at temperature, with the service fluid or a '
                     'representative one, leak tested throughout rather than only at the end.',
        'wearOut': 'Seat wear, stem seal wear, actuator degradation, galling'
    },
    'regulator': {
        'unit': 'cycles and total throughput',
        'condition': 'Across the full inlet pressure range, verifying setpoint drift at intervals.',
        'wearOut': 'Seat erosion, spring relaxation, diaphragm fatigue, setpoint drift'
    },
    'check valve': {
        'unit': 'cycles',
        'condition': 'Including flow reversal, at the minimum flow where chatter occurs.',
        'wearOut': 'Seat wear from chatter, spring fatigue, reverse leakage growth'
    },
    'catalyst bed': {
        'unit': 'pulses and cumulative burn seconds',
        'condition': 'At the flight duty cycle and bed temperature, tracking ignition delay.',
        'wearOut': 'Catalyst attrition, washout, sintering, poisoning; ignition delay growth'
    },
    'seal': {
        'unit': 'compressed hours at temperature',
        'condition': 'Compressed at the design squeeze, at temperature, in the service fluid.',
        'wearOut': 'Compression set, stress relaxation, chemical attack, permeation increase'
    },
    'bellows': {
        'unit': 'flex cycles',
        'condition': 'At the design deflection and pressure, then burst tested.',
        'wearOut': 'Fatigue cracking at the convolution root'
    },
    'pressure vessel': {
        'unit': 'pressure cycles',
        'condition': 'From ambient to MEOP, then burst tested. COPVs also need sustained-load testing.',
        'wearOut': 'Fatigue crack growth; stress rupture for composite overwrap'
    },
    'filter': {
        'unit': 'throughput mass',
        'condition': 'With representative contamination at the specified loading.',
        'wearOut': 'Dirt capacity exhausted; element collapse under differential'
    }
}

# Acceleration model names.
ACCELERATION_MODELS = ('none', 'arrhenius', 'coffin-manson')

class LifeTest:

    '''

    Life and endurance test definition, with optional acceleration.

    Primary Input Properties:
    -------------------------
    articleType : str
        Key into LIFE_DEFINITIONS. Determines what "life" means and the test condition.
    expectedLife : float
        Life expected in service, in the unit for this article type
    lifeFactor : float
        Demonstration factor. Defaults to LIFE_TEST_FACTOR (4x).
    cycleRate : float
        Achievable test rate [cycles/s or units/s], for the duration estimate
    availableDuration : float
        Time available for the test [s]
    accelerationModel : str
        'none', 'arrhenius' or 'coffin-manson'
    useTemperature / testTemperature : float
        Service and test temperature [K], for Arrhenius
    activationEnergy : float
        Arrhenius activation energy [eV]
    useTemperatureRange / testTemperatureRange : float
        Service and test thermal cycle amplitude [K], for Coffin-Manson
    coffinMansonExponent : float
        Coffin-Manson exponent [-]

    Key Output Properties:
    ----------------------
    requiredLife : float
        Life to be demonstrated, in the article's unit
    accelerationFactor : float
        Acceleration achieved by the model [-]
    acceleratedLife : float
        Equivalent test life after acceleration
    requiredDuration : float
        Test duration at the achievable rate [s]
    feasible : bool
        Whether the test fits in the available duration

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    calculateRequiredLife()        Demonstration life and the test condition
    calculateAcceleration()        Acceleration factor from the selected model
    calculateDuration()            Test duration and feasibility
    generateReport(outputDir)      Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Requirement -- #

        self.articleType   = 'valve'  # key into LIFE_DEFINITIONS
        self.expectedLife  = np.nan   # in the unit for this article type
        self.lifeFactor    = np.nan   # [-], defaults to LIFE_TEST_FACTOR

        # -- Test Setup -- #

        self.cycleRate         = np.nan  # [units/s]
        self.availableDuration = np.nan  # [s]

        # -- Acceleration -- #

        self.accelerationModel    = 'none'
        self.useTemperature       = np.nan  # [K], service
        self.testTemperature      = np.nan  # [K], accelerated
        self.activationEnergy     = np.nan  # [eV]
        self.useTemperatureRange  = np.nan  # [K], service cycle amplitude
        self.testTemperatureRange = np.nan  # [K], test cycle amplitude
        self.coffinMansonExponent = np.nan  # [-]

        # -- Results -- #

        self.requiredLife       = np.nan  # in the article's unit
        self.accelerationFactor = 1.0     # [-]
        self.acceleratedLife    = np.nan  # equivalent test life
        self.requiredDuration   = np.nan  # [s]
        self.feasible           = None    # [-]
        self.designNotes        = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: articleType, expectedLife.

        '''

        requiredParams = {
            'articleType':  'Article type not provided. It determines what "life" means for this test.',
            'expectedLife': 'Expected service life not provided.'
        }

        optionalParams = ['lifeFactor', 'cycleRate', 'availableDuration', 'accelerationModel',
                          'useTemperature', 'testTemperature', 'activationEnergy',
                          'useTemperatureRange', 'testTemperatureRange', 'coffinMansonExponent']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateRequiredLife(self) -> dict:

        '''

        The life to be demonstrated, and the condition the test must reproduce.

        Four times the expected life is the usual flight hardware requirement. A program with
        fracture control and credible usage monitoring can sometimes argue for two; a critical
        single-string item may warrant more.

        The condition returned alongside the number is the important part. **Cycling at the wrong
        condition demonstrates the wrong thing**, and it is the most common way a life test passes
        while the hardware still fails in service. A valve cycled at ambient with no differential has
        demonstrated its actuator and nothing about its seat.

        '''

        factor            = self.lifeFactor if not np.isnan(self.lifeFactor) else LIFE_TEST_FACTOR
        self.requiredLife = self.expectedLife * factor

        definition = LIFE_DEFINITIONS[self.articleType.strip().lower()]

        self.designNotes.append(
            f'Test condition for a {self.articleType}: {definition["condition"]}')
        self.designNotes.append(
            f'Wear-out mechanisms to instrument for: {definition["wearOut"]}')

        return {
            'articleType':  self.articleType,
            'unit':         definition['unit'],
            'expectedLife': self.expectedLife,
            'lifeFactor':   factor,
            'requiredLife': self.requiredLife,
            'condition':    definition['condition'],
            'wearOut':      definition['wearOut']
        }

    def calculateAcceleration(self) -> dict:

        '''

        Acceleration factor from the selected model.

        **Arrhenius**, for thermally activated degradation such as elastomer ageing, lubricant
        breakdown or diffusion-driven mechanisms:

            AF = exp( (Ea / k) * (1/T_use - 1/T_test) )

        **Coffin-Manson**, for thermal cycling fatigue:

            AF = (dT_test / dT_use)^n

        Both rest on a parameter that is material and mechanism specific. The 0.7 eV activation
        energy and the exponent of 2 that this class defaults to are common values, not measured
        ones, and using them is a stated assumption rather than a calculation. The class flags that
        every time a default is used.

        **The limit on acceleration is that it must not change the failure mechanism.** Raising the
        test temperature until the elastomer is above its own thermal decomposition point does not
        accelerate ageing; it substitutes a different failure. A rule of thumb is that an
        acceleration factor above about 20 needs the mechanism explicitly argued.

        '''

        model = self.accelerationModel.strip().lower()

        if model == 'none':
            self.accelerationFactor = 1.0
            self.acceleratedLife    = self.requiredLife
            return {'model': 'none', 'accelerationFactor': 1.0}

        if model == 'arrhenius':

            if np.isnan(self.useTemperature) or np.isnan(self.testTemperature):
                raise InvalidInputError(
                    message       = 'The Arrhenius model needs useTemperature and testTemperature.',
                    parameterName = 'useTemperature/testTemperature',
                    value         = (self.useTemperature, self.testTemperature),
                    validRange    = 'Both positive real, in K'
                )

            activationEnergy = self.activationEnergy
            if np.isnan(activationEnergy):
                activationEnergy = DEFAULT_ACTIVATION_ENERGY
                self.designNotes.append(
                    f'Using the default {DEFAULT_ACTIVATION_ENERGY} eV activation energy. This is a stated '
                    f'assumption, not a measurement. The correct value is material and mechanism specific and '
                    f'changes the acceleration factor exponentially.')

            self.accelerationFactor = float(np.exp((activationEnergy / BOLTZMANN_EV) *
                                                   (1.0 / self.useTemperature - 1.0 / self.testTemperature)))

        elif model == 'coffin-manson':

            if np.isnan(self.useTemperatureRange) or np.isnan(self.testTemperatureRange):
                raise InvalidInputError(
                    message       = 'The Coffin-Manson model needs useTemperatureRange and testTemperatureRange.',
                    parameterName = 'useTemperatureRange/testTemperatureRange',
                    value         = (self.useTemperatureRange, self.testTemperatureRange),
                    validRange    = 'Both positive real, in K'
                )

            exponent = self.coffinMansonExponent
            if np.isnan(exponent):
                exponent = DEFAULT_COFFIN_MANSON_EXPONENT
                self.designNotes.append(
                    f'Using the default Coffin-Manson exponent of {DEFAULT_COFFIN_MANSON_EXPONENT}. Values of 2 to '
                    f'3 are typical for ductile metals and solder; a brittle material needs a higher exponent.')

            self.accelerationFactor = float((self.testTemperatureRange / self.useTemperatureRange)**exponent)

        if np.isnan(self.requiredLife):
            self.calculateRequiredLife()

        self.acceleratedLife = self.requiredLife / self.accelerationFactor

        if self.accelerationFactor > 20.0:
            self.designNotes.append(
                f'An acceleration factor of {self.accelerationFactor:.1f} is aggressive. Above about 20 the test '
                f'condition needs an explicit argument that it has not substituted a different failure mechanism '
                f'for the one being accelerated.')

        return {
            'model':              model,
            'accelerationFactor': self.accelerationFactor,
            'requiredLife':       self.requiredLife,
            'acceleratedLife':    self.acceleratedLife
        }

    def calculateDuration(self) -> dict:

        '''

        Test duration at the achievable rate, and whether it fits the time available.

        Raises `TestInfeasibleError` when it does not, because a life test that cannot be run in the
        program schedule is a planning problem that has to surface while there are still options:
        accelerate it, run more articles in parallel, or renegotiate the life requirement.

        '''

        if np.isnan(self.requiredLife):
            self.calculateRequiredLife()

        if np.isnan(self.cycleRate) or self.cycleRate <= 0.0:
            raise InvalidInputError(
                message       = 'calculateDuration needs an achievable test rate.',
                parameterName = 'cycleRate', value = self.cycleRate, validRange = 'Greater than 0 units/s'
            )

        effectiveLife         = self.acceleratedLife if not np.isnan(self.acceleratedLife) else self.requiredLife
        self.requiredDuration = effectiveLife / self.cycleRate

        if not np.isnan(self.availableDuration):

            self.feasible = self.requiredDuration <= self.availableDuration

            if not self.feasible:
                parallelArticles = int(np.ceil(self.requiredDuration / self.availableDuration))
                raise TestInfeasibleError(
                    message = (f'The life test needs {self.requiredDuration / 86400.0:.1f} days at '
                               f'{self.cycleRate:.4g} units/s against {self.availableDuration / 86400.0:.1f} days '
                               f'available. Options: accelerate the test, run {parallelArticles} articles in '
                               f'parallel, raise the cycle rate, or renegotiate the life requirement.'),
                    context    = createErrorContext(component = 'LifeTest', articleType = self.articleType),
                    required   = self.requiredDuration,
                    achievable = self.availableDuration,
                    method     = 'life test'
                )

        return {
            'requiredLife':      self.requiredLife,
            'acceleratedLife':   effectiveLife,
            'cycleRate':         self.cycleRate,
            'requiredDuration':  self.requiredDuration,
            'requiredDurationDays': self.requiredDuration / 86400.0,
            'availableDuration': self.availableDuration,
            'feasible':          self.feasible
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        definition = LIFE_DEFINITIONS[self.articleType.strip().lower()]
        factor     = self.lifeFactor if not np.isnan(self.lifeFactor) else LIFE_TEST_FACTOR

        rows = [
            ['Article type',       f'{self.articleType}'],
            ['Life unit',          f'{definition["unit"]}'],
            ['Expected life',      f'{self.expectedLife:.6g}'],
            ['Life factor',        f'{factor:.1f}x'],
            ['Required life',      f'{self.requiredLife:.6g}'],
            ['Acceleration model', f'{self.accelerationModel}'],
            ['Acceleration factor', f'{self.accelerationFactor:.3f}']
        ]

        if not np.isnan(self.acceleratedLife):
            rows.append(['Accelerated test life', f'{self.acceleratedLife:.6g}'])

        if not np.isnan(self.requiredDuration):
            rows.append(['Test rate',        f'{self.cycleRate:.4g} units/s'])
            rows.append(['Test duration',    f'{self.requiredDuration / 86400.0:.2f} days '
                                             f'({self.requiredDuration / 3600.0:.1f} h)'])
        if self.feasible is not None:
            rows.append(['Fits the schedule', f'{self.feasible}'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'LIFE TEST PLAN')

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'lifeTestReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.articleType.strip().lower() not in LIFE_DEFINITIONS:
            raise InvalidInputError(
                message       = f'Unknown article type \'{self.articleType}\'.',
                parameterName = 'articleType', value = self.articleType,
                validRange    = str(sorted(LIFE_DEFINITIONS.keys()))
            )

        if self.accelerationModel.strip().lower() not in ACCELERATION_MODELS:
            raise InvalidInputError(
                message       = f'Unknown acceleration model \'{self.accelerationModel}\'.',
                parameterName = 'accelerationModel', value = self.accelerationModel,
                validRange    = str(ACCELERATION_MODELS)
            )

        if self.expectedLife <= 0.0:
            raise InvalidInputError(
                message       = 'Expected life must be positive.',
                parameterName = 'expectedLife', value = self.expectedLife, validRange = 'Greater than 0'
            )
