
# -- LpbfQualification Class Definition -- #

'''

Part classification per NASA-STD-6030 and MSFC-STD-3716, and the witness coupon, inspection and
allowables requirements that follow from it.

Additive manufacturing inverts the usual qualification structure. For a wrought part the material
arrives qualified and the shop qualifies its processes. For an additive part the material and the
part are created in the same operation, so **the build is the melt**, and every parameter that would
be a mill's problem becomes the part's problem.

The consequence is that an additive part cannot be qualified by inspecting it. Most of the evidence
comes from process control and from witness coupons built alongside it, because the internal
geometry that additive exists to produce is exactly the geometry no inspection can reach.

The classification decides how much of that evidence is required, and it follows from two questions:
what happens if the part fails, and how much is known about how it was made.

See Also:
---------
LpbfProcess : The process window this qualification structure is built around
PowderLot   : Feedstock control, which is one of the pillars of the evidence
Allowables  : Where the resulting statistical basis is established

Theory: docs/Qualification.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from lpbfUtils import (applyInputs, formatReportTable, InvalidInputError,
                           ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .lpbfUtils import (applyInputs, formatReportTable, InvalidInputError,
                            ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Consequence of failure, which is the first half of the classification. This is the same ladder
# that fracture control uses, and for good reason: an additive part with an uninspectable internal
# passage is a fracture control problem whether or not anyone calls it one.

CONSEQUENCE_CLASSES = {
    'AXM': {'rank': 4, 'description': 'Fracture critical or high consequence. Failure causes loss '
                                      'of vehicle, loss of mission, or a safety hazard.',
            'coupons': 12, 'volumetricNde': True, 'processMonitoring': True,
            'equivalencySpecimens': 30, 'lotAcceptance': 'every build',
            'note': 'The full programme. Qualified process, qualified machine, statistical '
                    'allowables, 100 percent volumetric NDE, witness coupons on every build.'},

    'AXB': {'rank': 3, 'description': 'Structurally significant but not fracture critical, or '
                                      'fracture critical with a demonstrated fail-safe path.',
            'coupons': 6, 'volumetricNde': True, 'processMonitoring': True,
            'equivalencySpecimens': 18, 'lotAcceptance': 'every build',
            'note': 'Statistical basis required, volumetric NDE required, and the coupon count '
                    'is halved relative to AXM.'},

    'BXB': {'rank': 2, 'description': 'Load bearing with a redundant path, or a low consequence '
                                      'pressure boundary.',
            'coupons': 3, 'volumetricNde': False, 'processMonitoring': True,
            'equivalencySpecimens': 18, 'lotAcceptance': 'periodic',
            'note': 'B-basis acceptable given the redundant load path. Surface NDE plus a sample '
                    'volumetric inspection rather than 100 percent.'},

    'CXC': {'rank': 1, 'description': 'Non-structural. Brackets, covers, tooling, fit checks.',
            'coupons': 1, 'volumetricNde': False, 'processMonitoring': False,
            'equivalencySpecimens': 0, 'lotAcceptance': 'periodic',
            'note': 'Dimensional and visual inspection. No statistical allowable needed because '
                    'nothing structural depends on one.'}
}

# Process maturity, the second half. A qualified machine running a frozen parameter set on
# controlled powder is a different proposition from a service bureau build with parameters the
# customer never sees, and the qualification burden scales accordingly.

PROCESS_MATURITY = {
    'qualified':   {'multiplier': 1.00,
                    'description': 'Frozen parameter set, qualified machine, controlled powder '
                                   'with a written reuse policy, in-process monitoring.'},
    'controlled':  {'multiplier': 1.50,
                    'description': 'Documented parameters and powder control, but the machine or '
                                   'the monitoring is not formally qualified.'},
    'developmental': {'multiplier': 2.50,
                      'description': 'Parameters under development, or a machine and powder history '
                                     'that is not fully documented.'},
    'uncontrolled': {'multiplier': np.inf,
                     'description': 'Parameters unknown or not frozen, powder history unknown. '
                                    'A service bureau build with no parameter disclosure sits here.'}
}

# The five pillars of the evidence. NASA-STD-6030 structures the argument this way and it is a
# useful checklist because a programme that has four of them has not got three quarters of a
# qualification; it has a gap that will be found at the review.

QUALIFICATION_PILLARS = (
    ('qualifiedMaterialProcess', 'A frozen material and process specification, with every parameter '
                                 'that affects properties named and controlled'),
    ('qualifiedEquipment',       'Machine qualification, calibration and a maintenance record, plus '
                                 'the demonstration that a second machine produces the same result'),
    ('qualifiedPersonnel',       'Operator training and currency, and a defined authority for '
                                 'deviations'),
    ('partProcessQualification', 'Part-specific qualification: first article, witness coupons, and '
                                 'the demonstration that this geometry builds correctly'),
    ('productionControl',        'Lot acceptance, in-process monitoring, statistical process '
                                 'control, and the discipline that any change is a change')
)

# Witness coupon placement. Build position genuinely affects properties, so coupons taken from one
# corner of the plate monitor that corner. The distribution is a specification item.

COUPON_PLACEMENT = ('plate corner, low',   'plate centre, low',  'plate corner, high',
                    'plate centre, high',  'adjacent to the part', 'top of build')

# Anisotropy knockdowns by build orientation, after HIP. Z direction is normal to the layers and it
# is where the interlayer bond governs rather than the bulk material.

ORIENTATION_KNOCKDOWN = {
    'XY':       {'factor': 1.00, 'note': 'In plane. The reference orientation.'},
    'Z':        {'factor': 0.90, 'note': 'Normal to the layers. The interlayer bond governs.'},
    '45':       {'factor': 0.95, 'note': 'Diagonal. Between the two.'},
    'unknown':  {'factor': 0.85, 'note': 'Orientation not controlled on the drawing, so the worst '
                                         'case has to be assumed and it is worse than Z because '
                                         'nothing stops a build being oriented badly.'}
}

# ------------------------------------------------------------------------------------------------ #

class LpbfQualification:

    '''

    Classify an additive part and derive the qualification evidence it requires.

    Primary Input Properties:
    -------------------------
    consequenceClass : str
        Key into CONSEQUENCE_CLASSES
    processMaturity : str
        Key into PROCESS_MATURITY
    buildOrientation : str
        'XY', 'Z', '45' or 'unknown'
    hasInternalPassages : bool
        Drives the CT requirement, because nothing else reaches them
    partsPerBuild / buildsPerLot : int

    Key Output Properties:
    ----------------------
    couponsRequired : int
        Witness coupons per build, after the maturity multiplier
    inspectionPlan : dict
        What has to be inspected and by what method
    allowablesBasis : str
        The statistical basis this classification supports

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    classifyPart()                 The classification and what it demands
    calculateCouponRequirement()   Witness coupons, placement and test matrix
    buildInspectionPlan()          NDE method selection, including the CT trigger
    assessPillars(status)          The five pillar readiness check
    calculateAllowablesPath()      Which basis is reachable and what it costs
    generateReport(outputDir)      Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Part Definition -- #

        self.partName            = ''         # [case sensitive string]
        self.consequenceClass    = 'AXB'      # [case insensitive string]
        self.processMaturity     = 'qualified'  # [case insensitive string]
        self.buildOrientation    = 'Z'        # [case insensitive string]
        self.hasInternalPassages = False      # [bool]
        self.isPressureBoundary  = False      # [bool]

        # -- Production -- #

        self.partsPerBuild       = 1          # [-]
        self.buildsPerLot        = 1          # [-]

        # -- Results -- #

        self.couponsRequired     = 0          # [-]
        self.inspectionPlan      = {}         # [dict]
        self.allowablesBasis     = ''         # [case sensitive string]
        self.qualificationNotes  = []         # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: consequenceClass.

        '''

        requiredParams = {
            'consequenceClass': 'Consequence class not provided. The whole qualification structure '
                                'follows from it.'
        }

        optionalParams = ['partName', 'processMaturity', 'buildOrientation', 'hasInternalPassages',
                          'isPressureBoundary', 'partsPerBuild', 'buildsPerLot']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def classifyPart(self) -> dict:

        '''

        The classification, and what it demands.

        An uncontrolled process cannot produce flight hardware at any classification above
        non-structural, and this raises rather than returning a large coupon count. The reason is
        that no quantity of coupons substitutes for a frozen parameter set: coupons monitor a
        process that is under control, and they measure noise on one that is not.

        '''

        consequence = CONSEQUENCE_CLASSES[self.consequenceClass]
        maturity    = PROCESS_MATURITY[self.processMaturity]

        if np.isinf(maturity['multiplier']) and consequence['rank'] > 1:
            raise ProcessInfeasibleError(
                message = f'A {self.consequenceClass} part cannot be qualified from an uncontrolled '
                          f'process. {maturity["description"]} No quantity of witness coupons '
                          f'substitutes for a frozen parameter set: coupons monitor a process that '
                          f'is under control and they measure noise on one that is not. Either '
                          f'freeze and qualify the process, or reclassify the part as CXC '
                          f'non-structural.'
            )

        result = {'consequenceClass': self.consequenceClass,
                  'rank': consequence['rank'],
                  'description': consequence['description'],
                  'processMaturity': self.processMaturity,
                  'maturityMultiplier': maturity['multiplier'],
                  'maturityDescription': maturity['description'],
                  'volumetricNdeRequired': consequence['volumetricNde'],
                  'processMonitoringRequired': consequence['processMonitoring'],
                  'lotAcceptance': consequence['lotAcceptance'],
                  'note': consequence['note']}

        if self.isPressureBoundary and consequence['rank'] < 3:
            self.qualificationNotes.append(
                f'This part is a pressure boundary but is classified {self.consequenceClass}. A '
                f'pressure boundary is normally AXM or AXB, because a leak or a rupture is a safety '
                f'consequence regardless of what the load path looks like. Confirm the '
                f'classification.')

        return result

    def calculateCouponRequirement(self) -> dict:

        '''

        Witness coupons per build, their placement, and the test matrix.

        Coupons are built alongside the part, in the same build, from the same powder, and tested to
        confirm the process was in control that day. They are the primary evidence for an additive
        part because the part itself usually cannot be tested.

        PLACEMENT IS A SPECIFICATION ITEM, NOT A CONVENIENCE. Build position affects properties
        through the thermal history, the gas flow and the recoater direction, so coupons taken from
        one corner of the plate monitor that corner. A distributed placement is what makes them
        represent the build.

        The count scales with the process maturity multiplier, because a less controlled process
        needs more evidence to reach the same confidence.

        '''

        consequence = CONSEQUENCE_CLASSES[self.consequenceClass]
        maturity    = PROCESS_MATURITY[self.processMaturity]

        if np.isinf(maturity['multiplier']):
            self.classifyPart()      # raises for anything above CXC
            base = consequence['coupons']
            self.couponsRequired = base
        else:
            self.couponsRequired = int(np.ceil(consequence['coupons'] * maturity['multiplier']))

        placement = list(COUPON_PLACEMENT[:min(len(COUPON_PLACEMENT), self.couponsRequired)])
        while len(placement) < self.couponsRequired:
            placement.append(f'distributed, position {len(placement) + 1}')

        testMatrix = ['tensile, build direction']
        if consequence['rank'] >= 2:
            testMatrix.append('tensile, transverse to build')
            testMatrix.append('density, Archimedes or CT')
        if consequence['rank'] >= 3:
            testMatrix.append('fatigue')
            testMatrix.append('metallography, porosity and microstructure')
        if consequence['rank'] >= 4:
            testMatrix.append('fracture toughness')
            testMatrix.append('chemistry, including oxygen')

        return {'baseCoupons': consequence['coupons'],
                'maturityMultiplier': maturity['multiplier'],
                'couponsRequired': self.couponsRequired,
                'couponsPerLot': self.couponsRequired * self.buildsPerLot,
                'placement': placement,
                'testMatrix': testMatrix,
                'note': 'Coupons are built in the same build, from the same powder lot, and tested '
                        'to the same specification as the part. Placement is a specification item '
                        'because build position affects properties.'}

    def buildInspectionPlan(self) -> dict:

        '''

        NDE method selection.

        THE CT TRIGGER IS THE IMPORTANT PART. An internal passage that cannot be reached by a
        borescope cannot be inspected by any method except computed tomography, and that is the
        single largest cost driver in additive qualification. It is also the reason a part with
        uninspectable internal geometry should be a deliberate decision rather than a consequence of
        a designer using the freedom the process offers.

        Radiography is not a substitute. It integrates through the thickness, so a lack of fusion
        defect lying in the build plane is presented edge-on and is close to invisible, which is
        exactly the orientation additive produces.

        '''

        consequence = CONSEQUENCE_CLASSES[self.consequenceClass]

        methods = ['visual', 'dimensional']

        if consequence['rank'] >= 2:
            methods.append('surface penetrant')

        if consequence['volumetricNde']:
            if self.hasInternalPassages:
                methods.append('computed tomography, 100 percent')
                self.qualificationNotes.append(
                    'This part has internal passages and a volumetric NDE requirement, so computed '
                    'tomography is the only method that reaches them. Radiography is not a '
                    'substitute: it integrates through the thickness, so a lack of fusion defect '
                    'lying in the build plane is presented edge-on and is close to invisible. That '
                    'is exactly the orientation this process produces. CT is the largest single '
                    'cost driver in additive qualification and it belongs in the trade at design '
                    'time, not at inspection planning.')
            else:
                methods.append('radiography or computed tomography, 100 percent')

        elif consequence['rank'] >= 2:
            methods.append('radiography, sample basis')

        if consequence['processMonitoring']:
            methods.append('in-process layer monitoring, melt pool or optical')

        if self.hasInternalPassages:
            methods.append('powder evacuation verification, CT or flow test')

        self.inspectionPlan = {
            'methods': methods,
            'volumetricRequired': consequence['volumetricNde'],
            'computedTomographyRequired': consequence['volumetricNde'] and self.hasInternalPassages,
            'lotAcceptance': consequence['lotAcceptance']}

        return self.inspectionPlan

    def assessPillars(self, status: dict = None) -> dict:

        '''

        The five pillar readiness check.

        A programme with four of the five pillars has not got four fifths of a qualification. It has
        a gap, and the gap is what the review will find. The pillars are reported as a checklist
        rather than a score for that reason.

        '''

        status = status or {}

        assessment = []
        missing    = []

        for key, description in QUALIFICATION_PILLARS:
            complete = bool(status.get(key, False))
            assessment.append({'pillar': key, 'description': description, 'complete': complete})
            if not complete:
                missing.append(key)

        ready = not missing

        if missing:
            self.qualificationNotes.append(
                f'{len(missing)} of the five qualification pillars are incomplete: '
                f'{", ".join(missing)}. A partial qualification is not a partial risk; the missing '
                f'pillar is where the failure comes from.')

        return {'pillars': assessment, 'missing': missing, 'ready': ready,
                'completeCount': len(QUALIFICATION_PILLARS) - len(missing),
                'totalCount': len(QUALIFICATION_PILLARS)}

    def calculateAllowablesPath(self) -> dict:

        '''

        Which statistical basis this classification supports, and what establishing it costs.

        The orientation knockdown is applied here because it is a property of how the part was built
        rather than of the material, and it belongs in the allowables chain alongside the weld and
        casting factors.

        An UNKNOWN build orientation carries the worst knockdown, worse than Z, and the reason is
        not conservatism for its own sake: if the orientation is not on the drawing then nothing
        stops a build being oriented badly, and the worst case is what has to be assumed.

        '''

        consequence = CONSEQUENCE_CLASSES[self.consequenceClass]
        orientation = ORIENTATION_KNOCKDOWN[self.buildOrientation]

        if consequence['rank'] >= 4:
            self.allowablesBasis = 'A'
        elif consequence['rank'] >= 3:
            self.allowablesBasis = 'B'
        elif consequence['rank'] >= 2:
            self.allowablesBasis = 'B'
        else:
            self.allowablesBasis = 'typical'

        specimens = consequence['equivalencySpecimens']

        result = {'allowablesBasis': self.allowablesBasis,
                  'equivalencySpecimens': specimens,
                  'fullAllowablesSpecimens': 100 if consequence['rank'] >= 3 else 0,
                  'orientation': self.buildOrientation,
                  'orientationKnockdown': orientation['factor'],
                  'orientationNote': orientation['note'],
                  'route': ('equivalency against a published additive database'
                            if specimens else 'no statistical basis required')}

        if self.buildOrientation == 'unknown':
            self.qualificationNotes.append(
                f'The build orientation is not specified, so the worst case knockdown of '
                f'{orientation["factor"]:.2f} applies. That is worse than the Z direction value, '
                f'and deliberately: if the orientation is not on the drawing then nothing stops a '
                f'build being oriented badly. Specifying it on the drawing recovers 5 percent of '
                f'the allowable for free.')

        if consequence['rank'] >= 3 and specimens:
            self.qualificationNotes.append(
                f'A {self.allowablesBasis}-basis for this class needs an equivalency campaign of '
                f'{specimens} specimens against a published additive database, or roughly 100 '
                f'specimens across 10 builds for a standalone allowable. The equivalency route is '
                f'far cheaper and it requires the acceptance criteria to be agreed before the data '
                f'exists.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        classification = self.classifyPart()
        coupons        = self.calculateCouponRequirement()
        inspection     = self.buildInspectionPlan()
        allowables     = self.calculateAllowablesPath()

        rows = [
            ['Part',                  f'{self.partName or "unnamed"}'],
            ['Consequence class',     f'{self.consequenceClass} -- {classification["description"]}'],
            ['Process maturity',      f'{self.processMaturity} '
                                      f'(x{classification["maturityMultiplier"]:.2f})'],
            ['Build orientation',     f'{self.buildOrientation}, knockdown '
                                      f'{allowables["orientationKnockdown"]:.2f}'],
            ['Internal passages',     f'{"yes" if self.hasInternalPassages else "no"}'],
            ['Witness coupons',       f'{self.couponsRequired} per build, '
                                      f'{coupons["couponsPerLot"]} per lot'],
            ['Volumetric NDE',        f'{"required" if inspection["volumetricRequired"] else "not required"}'],
            ['Computed tomography',   f'{"REQUIRED" if inspection["computedTomographyRequired"] else "not required"}'],
            ['Lot acceptance',        f'{inspection["lotAcceptance"]}'],
            ['Allowables basis',      f'{allowables["allowablesBasis"]}'],
            ['Equivalency specimens', f'{allowables["equivalencySpecimens"]}']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'LPBF QUALIFICATION')

        report += f'\n\nINSPECTION PLAN\n{"-" * 60}\n'
        for method in inspection['methods']:
            report += f'  {method}\n'

        report += f'\nCOUPON TEST MATRIX ({self.couponsRequired} coupons)\n{"-" * 60}\n'
        for test in coupons['testMatrix']:
            report += f'  {test}\n'

        report += f'\nCOUPON PLACEMENT\n{"-" * 60}\n'
        for position in coupons['placement']:
            report += f'  {position}\n'

        report += f'\n\nCLASS NOTE\n{"-" * 60}\n{classification["note"]}\n'

        for note in self.qualificationNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'lpbfQualification.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = self.consequenceClass.strip().upper()

        if key not in CONSEQUENCE_CLASSES:
            raise InvalidInputError(
                message       = f'Unknown consequence class \'{self.consequenceClass}\'.',
                parameterName = 'consequenceClass', value = self.consequenceClass,
                validRange    = str(sorted(CONSEQUENCE_CLASSES.keys()))
            )

        self.consequenceClass = key

        maturity = self.processMaturity.strip().lower()

        if maturity not in PROCESS_MATURITY:
            raise InvalidInputError(
                message       = f'Unknown process maturity \'{self.processMaturity}\'.',
                parameterName = 'processMaturity', value = self.processMaturity,
                validRange    = str(sorted(PROCESS_MATURITY.keys()))
            )

        self.processMaturity = maturity

        if self.buildOrientation not in ORIENTATION_KNOCKDOWN:
            raise InvalidInputError(
                message       = f'Unknown build orientation \'{self.buildOrientation}\'.',
                parameterName = 'buildOrientation', value = self.buildOrientation,
                validRange    = str(sorted(ORIENTATION_KNOCKDOWN.keys()))
            )

        if self.partsPerBuild < 1 or self.buildsPerLot < 1:
            raise InvalidInputError(
                message       = 'partsPerBuild and buildsPerLot must be at least one.',
                parameterName = 'partsPerBuild/buildsPerLot',
                value         = (self.partsPerBuild, self.buildsPerLot),
                validRange    = 'At least 1'
            )
