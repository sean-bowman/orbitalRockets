
# -- TestCampaign Class Definition -- #

'''

Test campaign assembly: which tests, at which level, in what order, and why.

This class assembles the matrix. It takes a hardware class, a fluid hazard classification and a set
of programme constraints, and produces the qualification and acceptance test sequences with the
rationale for each entry.

Three things it exists to get right, all of which are ordering problems rather than analysis
problems:

**Sequence matters and it is not arbitrary.** Proof runs before leak test, because proof can open a
marginal joint and the leak test is what catches it. Leak test repeats after every environmental
exposure rather than only at the end, because knowing which exposure caused a failure is worth the
extra tests. Burst runs last on a qualification article because it destroys it.

**Qualification and acceptance are different activities.** Qualification demonstrates the design with
margin, on dedicated articles, and may be destructive. Acceptance demonstrates that a specific
article was built to that design, at operating levels, non-destructively. Conflating them is the most
common and most expensive test planning error: an acceptance test that consumes life is a design
problem, and a qualification test applied to flight hardware wastes an article.

**Tailoring has to be deliberate and written down.** Programmes tailor standards, and that is
legitimate. What is not legitimate is tailoring by omission, where a test quietly does not happen
because nobody noticed it was required.

See Also:
---------
PressureTest, LeakTest, EnvironmentalTest, LifeTest : The individual tests this sequences
SampleSize : How many articles the campaign consumes

Theory: docs/TestCampaignPlanning.md, docs/RequirementsAndVerification.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from campaignUtils import (applyInputs, formatReportTable, TEST_LEVELS, VERIFICATION_METHODS,
                               PRESSURE_TEST_FACTORS, InvalidInputError, createErrorContext)
except ImportError:
    from .campaignUtils import (applyInputs, formatReportTable, TEST_LEVELS, VERIFICATION_METHODS,
                                PRESSURE_TEST_FACTORS, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The test catalogue. Each entry says what the test is, which levels it applies at, where it sits in
# the sequence, and whether it is destructive.
#
# The 'sequence' number is what enforces the ordering rules: proof before leak, environmental before
# the final leak check, burst last.
TEST_CATALOGUE = {
    'dimensional inspection': {
        'sequence': 10, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'The article is what the drawing says',
        'appliesTo': 'all'
    },
    'cleanliness verification': {
        'sequence': 20, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Particulate and NVR to the specified level, before anything is assembled onto it',
        'appliesTo': 'all'
    },
    'proof pressure': {
        'sequence': 30, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Strength demonstration with no permanent set. Every flight article',
        'appliesTo': 'pressurized'
    },
    'leak test, post proof': {
        'sequence': 40, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Proof can open a marginal joint. This is the test that catches it',
        'appliesTo': 'pressurized'
    },
    'functional test, ambient': {
        'sequence': 50, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'It works: stroke, timing, setpoint, response',
        'appliesTo': 'active'
    },
    'flow calibration': {
        'sequence': 60, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'The measured flow number, which is the baseline for detecting erosion and plugging over life',
        'appliesTo': 'flow'
    },
    'random vibration': {
        'sequence': 70, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Launch environment. Qualification is acceptance +3 dB for 2x duration, per axis',
        'appliesTo': 'all'
    },
    'leak test, post vibration': {
        'sequence': 75, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Vibration loosens joints and damages seals. Test after each exposure, not only at the end',
        'appliesTo': 'pressurized'
    },
    'shock': {
        'sequence': 80, 'levels': ('qualification',), 'destructive': False,
        'purpose': 'Separation and pyrotechnic events, 1.4x flight SRS, three per axis',
        'appliesTo': 'all'
    },
    'thermal cycling': {
        'sequence': 90, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Thermal fatigue and differential contraction, flight range plus 10 K margin',
        'appliesTo': 'all'
    },
    'thermal vacuum': {
        'sequence': 95, 'levels': ('qualification',), 'destructive': False,
        'purpose': 'On-orbit environment, including outgassing and thermal balance',
        'appliesTo': 'space'
    },
    'cryogenic functional': {
        'sequence': 100, 'levels': ('qualification',), 'destructive': False,
        'purpose': 'A seal that passes at ambient can fail cold. Ambient testing does not qualify a cryogenic joint',
        'appliesTo': 'cryogenic'
    },
    'leak test, at temperature': {
        'sequence': 105, 'levels': ('qualification',), 'destructive': False,
        'purpose': 'Differential contraction is what breaks a cryogenic seal, and it does not show at ambient',
        'appliesTo': 'cryogenic'
    },
    'life cycling': {
        'sequence': 110, 'levels': ('qualification',), 'destructive': False,
        'purpose': 'Four times the expected life, at the operating condition, leak tested throughout',
        'appliesTo': 'active'
    },
    'leak test, post life': {
        'sequence': 115, 'levels': ('qualification',), 'destructive': False,
        'purpose': 'Wear-out shows as leakage growth before it shows as a functional failure',
        'appliesTo': 'pressurized'
    },
    'functional test, final': {
        'sequence': 120, 'levels': ('qualification', 'acceptance'), 'destructive': False,
        'purpose': 'Performance after everything else, compared against the pre-environmental baseline',
        'appliesTo': 'active'
    },
    'burst pressure': {
        'sequence': 200, 'levels': ('qualification',), 'destructive': True,
        'purpose': 'Ultimate capability. Destroys the article, so it is last and never an acceptance test',
        'appliesTo': 'pressurized'
    }
}

# Hardware attribute sets. A test applies if its appliesTo tag is 'all' or is in the article's tags.
ARTICLE_ATTRIBUTES = {
    'line':            ('pressurized',),
    'valve':           ('pressurized', 'active', 'flow'),
    'regulator':       ('pressurized', 'active', 'flow'),
    'check valve':     ('pressurized', 'flow'),
    'filter':          ('pressurized', 'flow'),
    'orifice':         ('pressurized', 'flow'),
    'pressure vessel': ('pressurized',),
    'thruster':        ('pressurized', 'active', 'flow'),
    'fitting':         ('pressurized',),
    'seal':            ('pressurized',)
}

class TestCampaign:

    '''

    Qualification and acceptance test matrix assembly.

    Primary Input Properties:
    -------------------------
    articleName : str
        What is being qualified, for the report
    articleType : str
        Key into ARTICLE_ATTRIBUTES, which determines which tests apply
    hardwareClass : str
        Key into PRESSURE_TEST_FACTORS, for the pressure test levels
    fluidHazard : str
        'inert', 'flammable', 'toxic' or 'oxidizer'
    isCryogenic : bool
        Adds the cryogenic functional and cold leak tests
    isSpaceflight : bool
        Adds thermal vacuum
    tailoring : dict
        {test name: reason} for tests deliberately removed. Tailoring by omission is not permitted;
        every removal must carry a reason and it appears in the report.

    Key Output Properties:
    ----------------------
    qualificationSequence : list
        Ordered qualification tests with rationale
    acceptanceSequence : list
        Ordered acceptance tests with rationale
    destructiveTests : list
        Tests that consume the article

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    buildSequence(level)          The ordered test sequence for a level
    buildMatrix()                 Both sequences plus the tailoring record
    generateReport(outputDir)     Formatted campaign matrix

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Article -- #

        self.articleName   = ''            # for the report
        self.articleType   = 'valve'       # key into ARTICLE_ATTRIBUTES
        self.hardwareClass = 'component'   # key into PRESSURE_TEST_FACTORS
        self.fluidHazard   = 'inert'       # 'inert' / 'flammable' / 'toxic' / 'oxidizer'
        self.isCryogenic   = False         # [-]
        self.isSpaceflight = False         # [-]

        # -- Tailoring -- #

        # Tailoring by omission is the failure mode. Every removed test must carry a reason, and the
        # reason appears in the report so the decision is visible rather than silent.
        self.tailoring = {}                # {test name: reason for removal}

        # -- Results -- #

        self.qualificationSequence = []
        self.acceptanceSequence    = []
        self.destructiveTests      = []
        self.tailoredOut           = []
        self.designNotes           = []

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: articleName, articleType.

        '''

        requiredParams = {
            'articleName': 'Article name not provided.',
            'articleType': 'Article type not provided. It determines which tests apply.'
        }

        optionalParams = ['hardwareClass', 'fluidHazard', 'isCryogenic', 'isSpaceflight', 'tailoring']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def buildSequence(self, level: str) -> list:

        '''

        The ordered test sequence for a level.

        Ordering comes from the sequence number in the catalogue, which encodes the rules that matter:

            proof before leak            proof can open a marginal joint
            baseline functional early    so the post-environmental comparison means something
            leak after each environment  so the exposure that caused a failure is identifiable
            life before final functional wear-out shows as leakage before it shows as function
            burst last                   it destroys the article

        A test is included if its level list contains this level and its appliesTo tag matches the
        article, unless it has been explicitly tailored out.

        '''

        if level.strip().lower() not in TEST_LEVELS:
            raise InvalidInputError(
                message       = f'Unknown test level \'{level}\'.',
                parameterName = 'level', value = level, validRange = str(TEST_LEVELS)
            )

        attributes = set(ARTICLE_ATTRIBUTES[self.articleType.strip().lower()])

        if self.isCryogenic:
            attributes.add('cryogenic')
        if self.isSpaceflight:
            attributes.add('space')

        sequence = []

        for name, data in TEST_CATALOGUE.items():

            if level.strip().lower() not in data['levels']:
                continue

            if data['appliesTo'] != 'all' and data['appliesTo'] not in attributes:
                continue

            if name in self.tailoring:
                continue

            sequence.append({
                'sequence':    data['sequence'],
                'name':        name,
                'purpose':     data['purpose'],
                'destructive': data['destructive']
            })

        sequence.sort(key = lambda entry: entry['sequence'])

        return sequence

    def buildMatrix(self) -> dict:

        '''

        Both sequences, the destructive tests, and the tailoring record.

        The destructive list is the one that sizes the qualification article count: every destructive
        test consumes a unit, and a campaign with a burst test needs at least one article that will
        not be flown.

        '''

        self.qualificationSequence = self.buildSequence('qualification')
        self.acceptanceSequence    = self.buildSequence('acceptance')

        self.destructiveTests = [entry['name'] for entry in self.qualificationSequence
                                 if entry['destructive']]

        self.tailoredOut = [{'name': name, 'reason': reason}
                            for name, reason in self.tailoring.items()]

        # -- Advisories -- #

        if self.destructiveTests:
            self.designNotes.append(
                f'The qualification sequence includes {len(self.destructiveTests)} destructive test(s): '
                f'{", ".join(self.destructiveTests)}. Each consumes an article, so the campaign needs dedicated '
                f'qualification units that will not be flown.')

        acceptanceDestructive = [entry['name'] for entry in self.acceptanceSequence if entry['destructive']]
        if acceptanceDestructive:
            self.designNotes.append(
                f'A destructive test appears in the acceptance sequence: {", ".join(acceptanceDestructive)}. '
                f'Acceptance is applied to every flight article and must be non-destructive. This is a planning '
                f'error.')

        if self.fluidHazard.strip().lower() in ('toxic', 'flammable', 'oxidizer'):
            self.designNotes.append(
                f'{self.fluidHazard.capitalize()} fluid service. Volumetric weld inspection is required, the leak '
                f'requirement should be derived from the hazard rather than picked from a table, and every '
                f'hazardous operation needs a written and reviewed procedure.')

        if self.isCryogenic:
            self.designNotes.append(
                'Cryogenic service. Ambient leak testing does not qualify a cryogenic joint: differential '
                'contraction is what breaks the seal and it does not show at room temperature. The cold leak test '
                'is not optional.')

        if self.tailoredOut:
            self.designNotes.append(
                f'{len(self.tailoredOut)} test(s) tailored out. Each carries a stated reason below. Tailoring is '
                f'legitimate; tailoring by omission, where a test quietly does not happen because nobody noticed it '
                f'was required, is not.')

        return {
            'qualificationSequence': self.qualificationSequence,
            'acceptanceSequence':    self.acceptanceSequence,
            'destructiveTests':      self.destructiveTests,
            'tailoredOut':           self.tailoredOut
        }

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build the campaign matrix report.

        '''

        classData = PRESSURE_TEST_FACTORS.get(self.hardwareClass.strip().lower(), {})

        headerRows = [
            ['Article',          f'{self.articleName}'],
            ['Article type',     f'{self.articleType}'],
            ['Hardware class',   f'{self.hardwareClass}'],
            ['Proof / burst factors', f'{classData.get("proof", "n/a")} / {classData.get("burst", "n/a")}'],
            ['Fluid hazard',     f'{self.fluidHazard}'],
            ['Cryogenic',        f'{self.isCryogenic}'],
            ['Spaceflight',      f'{self.isSpaceflight}'],
            ['Qualification tests', f'{len(self.qualificationSequence)}'],
            ['Acceptance tests',    f'{len(self.acceptanceSequence)}']
        ]

        report = formatReportTable(headerRows, ['Quantity', 'Value'], title = 'TEST CAMPAIGN')

        qualRows = [[str(index + 1), entry['name'], entry['purpose'],
                     'DESTRUCTIVE' if entry['destructive'] else '']
                    for index, entry in enumerate(self.qualificationSequence)]
        report += '\n\n' + formatReportTable(qualRows, ['#', 'Test', 'Why it is there', ''],
                                             title = 'QUALIFICATION SEQUENCE (dedicated articles, may be destructive)')

        acceptRows = [[str(index + 1), entry['name'], entry['purpose']]
                      for index, entry in enumerate(self.acceptanceSequence)]
        report += '\n\n' + formatReportTable(acceptRows, ['#', 'Test', 'Why it is there'],
                                             title = 'ACCEPTANCE SEQUENCE (every flight article, non-destructive)')

        if self.tailoredOut:
            tailorRows = [[entry['name'], entry['reason']] for entry in self.tailoredOut]
            report += '\n\n' + formatReportTable(tailorRows, ['Test removed', 'Stated reason'],
                                                 title = 'TAILORING RECORD')

        for note in self.designNotes:
            report += f'\n\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'testCampaign.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.articleType.strip().lower() not in ARTICLE_ATTRIBUTES:
            raise InvalidInputError(
                message       = f'Unknown article type \'{self.articleType}\'.',
                parameterName = 'articleType', value = self.articleType,
                validRange    = str(sorted(ARTICLE_ATTRIBUTES.keys()))
            )

        if self.hardwareClass.strip().lower() not in PRESSURE_TEST_FACTORS:
            raise InvalidInputError(
                message       = f'Unknown hardware class \'{self.hardwareClass}\'.',
                parameterName = 'hardwareClass', value = self.hardwareClass,
                validRange    = str(sorted(PRESSURE_TEST_FACTORS.keys()))
            )

        for name in self.tailoring:
            if name not in TEST_CATALOGUE:
                raise InvalidInputError(
                    message       = f'Cannot tailor out \'{name}\': it is not in the test catalogue.',
                    parameterName = 'tailoring', value = name,
                    validRange    = str(sorted(TEST_CATALOGUE.keys()))
                )
