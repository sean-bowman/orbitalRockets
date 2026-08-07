
# -- MaterialSelector Class Definition -- #

'''

Screening and ranking across the alloy database against a requirement set, using Ashby material
indices and a per-candidate rejection audit trail.

Two things make this more than a loop over a table.

The first is the index. Minimum mass for a given load is not achieved by the strongest material or
the lightest one, it is achieved by maximising a combination that depends on the loading mode and
the constraint. A tie in tension maximises sigma/rho. A plate in bending maximises sigma^(1/2)/rho,
which is a completely different ordering. Selecting on strength alone gets the answer wrong often
enough to matter.

The second is the rejection trail. A screen that returns three survivors and no explanation is
useless in a design review, because the question that always gets asked is why a particular alloy is
not on the list. Every candidate that fails records which requirement it failed and by how much.

A note on cost. This class deals in ratios indexed to 316L bar and never in currency. Absolute
prices are wrong within a quarter and a number with a currency symbol invites a decision it cannot
support. Every cost figure carries the basis date it came from, and a basis more than eighteen
months old is flagged.

See Also:
---------
MaterialDatabase   : The candidate set and every property this class screens on
Allowables         : Supplies the design value the index should be computed from, not the typical
ProcessComparison  : Once the alloy is chosen, how it gets made

Theory: docs/MaterialsOverview.md, docs/MaterialSelection.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import applyInputs, formatReportTable, InvalidInputError, createErrorContext
    from MaterialDatabase import queryMaterial, resolveMaterialKey, listMaterials
    from materialData import MATERIAL_DATABASE, SOURCES
except ImportError:
    from .utils import applyInputs, formatReportTable, InvalidInputError, createErrorContext
    from .MaterialDatabase import queryMaterial, resolveMaterialKey, listMaterials
    from .materialData import MATERIAL_DATABASE, SOURCES

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Ashby material indices. Each entry says which properties combine, with what exponents, to give the
# quantity that should be MAXIMISED for minimum mass in that loading mode.
#
# The exponents are not decoration. For a tie the index is sigma/rho; for a plate in bending it is
# sigma^(1/2)/rho. Between those two, titanium beats aluminium on the first and loses on the second,
# because the half power flattens the strength advantage while the density penalty is untouched.
#
#   exponents: (strength, modulus, density, conductivity, expansion)

ASHBY_INDICES = {
    'tie':                    {'exponents': (1.0,     0.0,     -1.0, 0.0,  0.0),
                               'description': 'Bar in tension, strength limited',
                               'formula': 'sigma / rho'},
    'pressure vessel':        {'exponents': (1.0,     0.0,     -1.0, 0.0,  0.0),
                               'description': 'Thin wall membrane, strength limited',
                               'formula': 'sigma / rho'},
    'beam strength':          {'exponents': (2.0/3.0, 0.0,     -1.0, 0.0,  0.0),
                               'description': 'Beam in bending, strength limited',
                               'formula': 'sigma^(2/3) / rho'},
    'plate strength':         {'exponents': (0.5,     0.0,     -1.0, 0.0,  0.0),
                               'description': 'Plate in bending, strength limited',
                               'formula': 'sigma^(1/2) / rho'},
    'tie stiffness':          {'exponents': (0.0,     1.0,     -1.0, 0.0,  0.0),
                               'description': 'Bar in tension, stiffness limited',
                               'formula': 'E / rho'},
    'beam stiffness':         {'exponents': (0.0,     0.5,     -1.0, 0.0,  0.0),
                               'description': 'Beam in bending, stiffness limited',
                               'formula': 'E^(1/2) / rho'},
    'panel buckling':         {'exponents': (0.0,     1.0/3.0, -1.0, 0.0,  0.0),
                               'description': 'Plate or shell in compression, buckling limited',
                               'formula': 'E^(1/3) / rho'},
    'thermal shock':          {'exponents': (1.0,     -1.0,     0.0, 1.0, -1.0),
                               'description': 'Resistance to a thermal transient',
                               'formula': 'sigma k / (E alpha)'},
    'regen chamber liner':    {'exponents': (1.0,     -1.0,     0.0, 1.0, -1.0),
                               'description': 'Regeneratively cooled liner, thermal strain limited',
                               'formula': 'sigma k / (E alpha)'}
}

# Leak before burst is handled separately: it maximises the critical flaw size rather than a
# strength to density ratio, and the quantity to maximise is K_Ic^2 / sigma. A vessel that leaks
# before it bursts fails detectably, which is worth more than the mass it costs.

FRACTURE_INDEX = {'leak before burst': {'description': 'Maximise critical flaw size',
                                        'formula': 'K_Ic^2 / sigma'}}

# Environment severity sets the permitted galvanic potential difference and picks the SCC threshold
# column. Launch sites are marine environments and that is not a detail.

ENVIRONMENT_SEVERITY = {
    'controlled indoor':  {'potentialLimit': 0.50, 'sccColumn': None},
    'normal':             {'potentialLimit': 0.25, 'sccColumn': 'marine air'},
    'launch site marine': {'potentialLimit': 0.15, 'sccColumn': 'marine air'},
    'harsh':              {'potentialLimit': 0.15, 'sccColumn': 'chlorides'}
}

# Cost data rots. A basis older than this is flagged in every report that quotes it.
COST_BASIS_STALE_MONTHS = 18

# Risk score by source basis class. An alloy whose allowable is an author estimate carries programme
# risk that an MMPDS value does not, and the ranking should see that.
BASIS_RISK_SCORE = {'statistical': 0.0, 'spec minimum': 0.25, 'typical': 0.60, 'estimate': 1.0}

# ------------------------------------------------------------------------------------------------ #

class MaterialSelector:

    '''

    Screen and rank the alloy database against a requirement set.

    Primary Input Properties:
    -------------------------
    requirements : dict
        Hard pass or fail criteria. Any key may be omitted.
    loadingMode : str
        Key into ASHBY_INDICES, or 'leak before burst'
    objective : str
        'minimum mass', 'minimum cost' or 'minimum lead time'
    weights : dict
        Relative importance of mass, cost, lead time and risk in the ranked score
    basis : str
        Statistical basis used for the index. Should be the design basis, not 'typical'.

    Key Output Properties:
    ----------------------
    passed : list
        Candidates meeting every requirement
    rejected : dict
        Candidate -> list of the specific reasons it failed
    ranking : list
        Ordered results with index, relative mass, cost, lead time and risk

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    screen()                       Hard pass or fail with a rejection trail
    calculateMaterialIndex()       Ashby index for every surviving candidate
    calculateMassIndex(reference)  Relative part mass at fixed load and geometry
    rank()                         Weighted normalised score
    tradeStudy()                   The full matrix
    generateReport(outputDir)      Screening matrix, ranking and rejection reasons

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Requirements -- #

        self.requirements   = {}                  # [dict], see screen() for the recognised keys
        self.candidates     = []                  # [list], empty means the whole database

        # -- Objective -- #

        self.loadingMode    = 'pressure vessel'   # [case insensitive string]
        self.objective      = 'minimum mass'      # [case insensitive string]
        self.basis          = 'typical'           # [-], 'typical', 'S', 'B' or 'A'
        self.strengthProperty = 'ultimateStrength'  # [case sensitive string]
        self.weights        = {'mass': 0.50, 'cost': 0.20, 'leadTime': 0.20, 'risk': 0.10}

        # -- Results -- #

        self.passed         = []    # [list of tuple], (material, condition)
        self.rejected       = {}    # [dict], label -> list of reasons
        self.indices        = {}    # [dict], label -> index value
        self.ranking        = []    # [list of dict]
        self.selectorNotes  = []    # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: requirements.

        '''

        requiredParams = {
            'requirements': 'A requirement set is needed. An unconstrained screen returns the '
                            'whole database and answers nothing.'
        }

        optionalParams = ['candidates', 'loadingMode', 'objective', 'basis', 'strengthProperty',
                          'weights']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def screen(self) -> dict:

        '''

        Hard pass or fail against every stated requirement.

        Recognised requirement keys, all optional:

            minimumYieldStrength      [Pa] at the service temperature
            minimumUltimateStrength   [Pa]
            minimumToughness          [Pa-sqrt(m)]
            minimumElongation         [-]
            maximumDensity            [kg/m^3]
            serviceTemperature        [K], the temperature every property is evaluated at
            minimumTemperature        [K], the coldest excursion
            maximumTemperature        [K], the hottest excursion
            fluids                    [list of str], every fluid the material contacts
            environment               [str], key into ENVIRONMENT_SEVERITY
            form                      [str], required mill product form
            weldable                  [bool]
            maximumRelativeCost       [-], indexed to 316L bar
            maximumLeadTimeWeeks      [int]
            requireStatisticalBasis   [bool], reject anything without an A or B basis

        The rejection reasons are the output that matters. A screen that says only which alloys
        survived cannot answer the question a design review always asks.

        '''

        requirements = self.requirements
        temperature  = requirements.get('serviceTemperature', 293.15)

        candidateSet = self.candidates if self.candidates else listMaterials()

        self.passed   = []
        self.rejected = {}

        for entry in candidateSet:

            name, condition = entry if isinstance(entry, (tuple, list)) else (entry, None)

            try:
                properties = queryMaterial(name, condition, temperature, basis = self.basis)
            except InvalidInputError as error:
                self.rejected[f'{name} {condition}'] = [f'Database query failed: {error}']
                continue

            label   = f'{properties["material"]} {properties["condition"]}'
            reasons = []

            # -- Strength and stiffness -- #

            yieldStrength = properties.get('yieldStrength')
            ultimate      = properties.get('ultimateStrength')

            if requirements.get('minimumYieldStrength') is not None:
                if yieldStrength is None:
                    reasons.append(f'No yield strength at the {self.basis} basis')
                elif yieldStrength < requirements['minimumYieldStrength']:
                    reasons.append(
                        f'Yield {yieldStrength / 1.0e6:.0f} MPa below the required '
                        f'{requirements["minimumYieldStrength"] / 1.0e6:.0f} MPa at '
                        f'{temperature:.0f} K')

            if requirements.get('minimumUltimateStrength') is not None:
                if ultimate is None:
                    reasons.append(f'No ultimate strength at the {self.basis} basis')
                elif ultimate < requirements['minimumUltimateStrength']:
                    reasons.append(
                        f'Ultimate {ultimate / 1.0e6:.0f} MPa below the required '
                        f'{requirements["minimumUltimateStrength"] / 1.0e6:.0f} MPa')

            if requirements.get('minimumElongation') is not None:
                elongation = properties.get('elongation')
                if elongation is not None and elongation < requirements['minimumElongation']:
                    reasons.append(
                        f'Elongation {elongation * 100.0:.0f} % below the required '
                        f'{requirements["minimumElongation"] * 100.0:.0f} %')

            if requirements.get('maximumDensity') is not None and \
               properties['density'] > requirements['maximumDensity']:
                reasons.append(f'Density {properties["density"]:.0f} kg/m^3 above the limit')

            # -- Fracture toughness -- #

            if requirements.get('minimumToughness') is not None:
                fracture = properties.get('fracture', {})
                toughnessValues = fracture.get('planeStrainToughness', {})
                if not toughnessValues:
                    reasons.append('No fracture toughness data in the database')
                else:
                    worst = min(toughnessValues.values())
                    if worst < requirements['minimumToughness']:
                        reasons.append(
                            f'Toughness {worst / 1.0e6:.0f} MPa-sqrt(m) below the required '
                            f'{requirements["minimumToughness"] / 1.0e6:.0f}')

            # -- Temperature range -- #

            record    = MATERIAL_DATABASE[properties['material']]['conditions'][properties['condition']]
            hotBlock  = record.get('temperatureCurves')
            cryoBlock = record.get('cryogenicCurves')

            lowerBound = (cryoBlock or hotBlock or {}).get('validRange', (0.0, 1.0e4))[0]
            upperBound = (hotBlock or cryoBlock or {}).get('validRange', (0.0, 1.0e4))[1]

            if requirements.get('minimumTemperature') is not None and \
               requirements['minimumTemperature'] < lowerBound:
                reasons.append(
                    f'Validated only to {lowerBound:.0f} K, service requires '
                    f'{requirements["minimumTemperature"]:.0f} K')

            if requirements.get('maximumTemperature') is not None and \
               requirements['maximumTemperature'] > upperBound:
                reasons.append(
                    f'Validated only to {upperBound:.0f} K, service requires '
                    f'{requirements["maximumTemperature"]:.0f} K')

            # -- Fluid compatibility. This is where titanium leaves an oxidiser system. -- #

            for fluid in requirements.get('fluids', []):
                target = ' '.join(fluid.strip().upper().split())
                for prohibited in properties.get('incompatible', []):
                    if target == prohibited or target in prohibited:
                        reasons.append(f'PROHIBITED in {fluid} ({prohibited})')
                        break

            # -- Environment and stress corrosion -- #

            environmentKey = requirements.get('environment')
            if environmentKey is not None:
                severity = ENVIRONMENT_SEVERITY.get(environmentKey)
                if severity is None:
                    raise InvalidInputError(
                        message       = f'Unknown environment \'{environmentKey}\'.',
                        parameterName = 'environment', value = environmentKey,
                        validRange    = str(sorted(ENVIRONMENT_SEVERITY.keys()))
                    )
                environmental = properties.get('environmental', {})
                rating = environmental.get('sccRating', {}).get(
                    requirements.get('orientation', 'ST'),
                    environmental.get('sccRating', {}).get('L'))
                if rating in ('very low', 'low') and environmentKey != 'controlled indoor':
                    reasons.append(
                        f'SCC resistance is \'{rating}\' in the '
                        f'{requirements.get("orientation", "ST")} direction, in a '
                        f'{environmentKey} environment')

            # -- Manufacturing -- #

            if requirements.get('form') is not None and \
               requirements['form'] not in properties.get('forms', []):
                reasons.append(
                    f'Not available as {requirements["form"]} '
                    f'(available: {", ".join(properties.get("forms", [])) or "none listed"})')

            if requirements.get('weldable') and 'as-welded' not in \
               MATERIAL_DATABASE[properties['material']]['conditions']:
                weldableFamilies = ('austenitic', 'solid solution', 'titanium', 'aluminium 2xxx',
                                    'aluminium 6xxx')
                if not any(family in properties['family'] for family in weldableFamilies):
                    reasons.append(f'Not considered weldable ({properties["family"]})')

            # -- Cost and schedule. Ratios only, never currency. -- #

            if requirements.get('maximumRelativeCost') is not None and \
               properties['relativeCost'] > requirements['maximumRelativeCost']:
                reasons.append(
                    f'Relative cost {properties["relativeCost"]:.1f}x above the limit of '
                    f'{requirements["maximumRelativeCost"]:.1f}x (316L bar = 1.0, '
                    f'{properties["costBasisDate"]})')

            if requirements.get('maximumLeadTimeWeeks') is not None:
                leadTimes = properties.get('leadTimeWeeks', {})
                formKey   = requirements.get('form')
                leadTime  = leadTimes.get(formKey) if formKey else \
                            (min(leadTimes.values()) if leadTimes else None)
                if leadTime is not None and leadTime > requirements['maximumLeadTimeWeeks']:
                    reasons.append(
                        f'Lead time {leadTime} weeks above the limit of '
                        f'{requirements["maximumLeadTimeWeeks"]}')

            # -- Data quality -- #

            if requirements.get('requireStatisticalBasis'):
                sourceKey  = properties.get('sources', {}).get('allowables')
                basisClass = SOURCES.get(sourceKey, {}).get('basisClass')
                if basisClass != 'statistical':
                    reasons.append(
                        f'No statistical allowable: the allowables block is '
                        f'\'{basisClass or "absent"}\'. A fracture critical part needs one.')

            if reasons:
                self.rejected[label] = reasons
            else:
                self.passed.append((properties['material'], properties['condition']))

        if not self.passed:
            self.selectorNotes.append(
                'No candidate met every requirement. The rejection reasons show which requirement '
                'is doing the work; relaxing the binding one is usually a cheaper conversation than '
                'qualifying a new material.')

        return {'passed': self.passed, 'rejected': self.rejected,
                'candidateCount': len(candidateSet), 'passCount': len(self.passed)}

    def calculateMaterialIndex(self) -> dict:

        '''

        Ashby index for every surviving candidate, in the configured loading mode.

        The index is computed from the strength at the CONFIGURED BASIS, not the typical value, so
        the ranking reflects the design allowable and the temperature. That coupling is what makes
        the ranking meaningful rather than decorative.

        '''

        if not self.passed:
            self.screen()

        temperature = self.requirements.get('serviceTemperature', 293.15)
        mode        = self.loadingMode.strip().lower()

        self.indices = {}

        for name, condition in self.passed:

            properties = queryMaterial(name, condition, temperature, basis = self.basis)
            label      = f'{name} {condition}'

            strength     = properties.get(self.strengthProperty)
            modulus      = properties.get('elasticModulus')
            density      = properties.get('density')
            conductivity = properties.get('thermalConductivity')
            expansion    = properties.get('thermalExpansion')

            if mode in FRACTURE_INDEX:
                fracture  = properties.get('fracture', {}).get('planeStrainToughness', {})
                if not fracture or strength is None:
                    continue
                toughness = min(fracture.values())
                self.indices[label] = toughness ** 2 / strength
                continue

            definition = ASHBY_INDICES[mode]
            exponents  = definition['exponents']

            values = (strength, modulus, density, conductivity, expansion)

            if any(value is None for value, exponent in zip(values, exponents) if exponent != 0.0):
                continue

            index = 1.0
            for value, exponent in zip(values, exponents):
                if exponent != 0.0:
                    index *= value ** exponent

            self.indices[label] = index

        return self.indices

    def calculateMassIndex(self, referenceMaterial: str = '316L',
                           referenceCondition: str = 'annealed') -> dict:

        '''

        Relative part mass against a reference alloy, at fixed load and geometry.

        Mass scales as the inverse of the index, so this answers the question actually asked in a
        design review: how much heavier is the stainless version.

        '''

        if not self.indices:
            self.calculateMaterialIndex()

        temperature = self.requirements.get('serviceTemperature', 293.15)
        reference   = queryMaterial(referenceMaterial, referenceCondition, temperature,
                                    basis = self.basis)
        referenceLabel = f'{reference["material"]} {reference["condition"]}'

        if referenceLabel not in self.indices:
            savedPassed  = list(self.passed)
            self.passed  = [(reference['material'], reference['condition'])]
            referenceIndex = self.calculateMaterialIndex().get(referenceLabel)
            self.passed  = savedPassed
            self.calculateMaterialIndex()
        else:
            referenceIndex = self.indices[referenceLabel]

        if referenceIndex is None:
            raise InvalidInputError(
                message       = f'Could not compute the index for the reference material '
                                f'{referenceMaterial}.',
                parameterName = 'referenceMaterial', value = referenceMaterial,
                validRange    = 'A material with the properties this loading mode needs'
            )

        return {label: referenceIndex / index for label, index in self.indices.items()}

    def rank(self) -> list:

        '''

        Weighted normalised score across mass, cost, lead time and risk.

        Every axis is normalised to the best candidate in the surviving set, so a score is a relative
        statement about this trade and not an absolute material property. Risk comes from the source
        basis class: an alloy whose allowable is an author estimate scores worse than one from MMPDS,
        which is a real programme cost that a pure physics ranking misses.

        '''

        if not self.indices:
            self.calculateMaterialIndex()

        if not self.indices:
            self.selectorNotes.append('No candidate had the properties this loading mode requires.')
            return []

        temperature   = self.requirements.get('serviceTemperature', 293.15)
        formKey       = self.requirements.get('form')
        massIndices   = self.calculateMassIndex()

        entries = []

        for label, index in self.indices.items():

            name, condition = label.rsplit(' ', 1)[0], label[len(label.rsplit(' ', 1)[0]) + 1:]
            for candidateName, candidateCondition in self.passed:
                if f'{candidateName} {candidateCondition}' == label:
                    name, condition = candidateName, candidateCondition
                    break

            properties = queryMaterial(name, condition, temperature, basis = self.basis)

            leadTimes = properties.get('leadTimeWeeks', {})
            leadTime  = leadTimes.get(formKey) if formKey else \
                        (min(leadTimes.values()) if leadTimes else 52)

            sourceKey  = properties.get('sources', {}).get('allowables',
                                                           properties.get('sources', {}).get('typical'))
            basisClass = SOURCES.get(sourceKey, {}).get('basisClass', 'estimate')

            entries.append({
                'material': name, 'condition': condition, 'label': label,
                'index': index, 'relativeMass': massIndices.get(label, np.nan),
                'relativeCost': properties['relativeCost'],
                'costBasisDate': properties['costBasisDate'],
                'leadTimeWeeks': leadTime,
                'basisClass': basisClass,
                'risk': BASIS_RISK_SCORE.get(basisClass, 1.0),
                'density': properties['density'],
                'strength': properties.get(self.strengthProperty)})

        bestMass = min(entry['relativeMass'] for entry in entries)
        bestCost = min(entry['relativeCost'] for entry in entries)
        bestLead = min(entry['leadTimeWeeks'] for entry in entries)

        for entry in entries:
            massScore = bestMass / entry['relativeMass'] if entry['relativeMass'] else 0.0
            costScore = bestCost / entry['relativeCost'] if entry['relativeCost'] else 0.0
            leadScore = bestLead / entry['leadTimeWeeks'] if entry['leadTimeWeeks'] else 0.0
            riskScore = 1.0 - entry['risk']

            entry['score'] = (self.weights['mass']     * massScore +
                              self.weights['cost']     * costScore +
                              self.weights['leadTime'] * leadScore +
                              self.weights['risk']     * riskScore)

        self.ranking = sorted(entries, key = lambda entry: entry['score'], reverse = True)

        if self.ranking and self.ranking[0]['basisClass'] == 'estimate':
            self.selectorNotes.append(
                f'The top ranked candidate, {self.ranking[0]["label"]}, rests on author estimated '
                f'properties rather than a statistical basis. It may well be the right answer, but '
                f'the programme carries the cost of establishing the allowable and that belongs in '
                f'the trade.')

        return self.ranking

    def tradeStudy(self) -> dict:

        '''

        The full matrix: screening outcome, indices, ranking and the binding constraint.

        The binding constraint is the requirement that rejected the most candidates, and it is
        usually the one worth renegotiating.

        '''

        screening = self.screen()
        ranking   = self.rank()

        reasonCounts = {}
        for reasons in self.rejected.values():
            for reason in reasons:
                key = reason.split(' ')[0] + ' ' + (reason.split(' ')[1] if len(reason.split(' ')) > 1
                                                    else '')
                reasonCounts[key] = reasonCounts.get(key, 0) + 1

        binding = max(reasonCounts.items(), key = lambda item: item[1]) if reasonCounts else None

        return {'screening': screening, 'ranking': ranking,
                'bindingConstraint': binding,
                'rejectionCounts': dict(sorted(reasonCounts.items(),
                                               key = lambda item: item[1], reverse = True))}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build the screening matrix, the ranking and the rejection reasons.

        '''

        if not self.ranking:
            self.rank()

        mode       = self.loadingMode.strip().lower()
        definition = ASHBY_INDICES.get(mode, FRACTURE_INDEX.get(mode, {}))

        rows = [
            ['Loading mode',   f'{self.loadingMode} -- {definition.get("description", "")}'],
            ['Material index', f'{definition.get("formula", "n/a")}'],
            ['Objective',      f'{self.objective}'],
            ['Statistical basis', f'{self.basis}'],
            ['Service temperature', f'{self.requirements.get("serviceTemperature", 293.15):.1f} K'],
            ['Candidates screened', f'{len(self.passed) + len(self.rejected)}'],
            ['Passed',         f'{len(self.passed)}'],
            ['Rejected',       f'{len(self.rejected)}']
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'MATERIAL SELECTION')

        if self.ranking:
            rankRows = [[f'{index + 1}', entry['label'],
                         f'{entry["index"]:.4g}',
                         f'{entry["relativeMass"]:.2f}',
                         f'{entry["relativeCost"]:.1f}',
                         f'{entry["leadTimeWeeks"]:.0f}',
                         entry['basisClass'],
                         f'{entry["score"]:.3f}']
                        for index, entry in enumerate(self.ranking)]
            report += '\n\n' + formatReportTable(
                rankRows,
                ['#', 'Material', 'Index', 'Rel mass', 'Rel cost', 'Lead wk', 'Basis', 'Score'],
                title = 'RANKING')

        if self.rejected:
            report += f'\n\nREJECTED ({len(self.rejected)})\n{"-" * 80}\n'
            for label, reasons in sorted(self.rejected.items()):
                report += f'  {label}\n'
                for reason in reasons:
                    report += f'      {reason}\n'

        report += (f'\nCost figures are ratios indexed to 316L bar = 1.0. Absolute prices are not '
                   f'published here because they are wrong within a quarter.\n')

        for note in self.selectorNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'materialSelection.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        mode = self.loadingMode.strip().lower()
        if mode not in ASHBY_INDICES and mode not in FRACTURE_INDEX:
            raise InvalidInputError(
                message       = f'Unknown loading mode \'{self.loadingMode}\'.',
                parameterName = 'loadingMode', value = self.loadingMode,
                validRange    = str(sorted(list(ASHBY_INDICES.keys()) + list(FRACTURE_INDEX.keys())))
            )

        if not isinstance(self.requirements, dict):
            raise InvalidInputError(
                message       = 'requirements must be a dictionary.',
                parameterName = 'requirements', value = type(self.requirements).__name__,
                validRange    = 'dict'
            )

        weightTotal = sum(self.weights.values())
        if not np.isclose(weightTotal, 1.0, atol = 1.0e-6):
            raise InvalidInputError(
                message       = f'Ranking weights sum to {weightTotal:.3f}, not 1.0. A score built '
                                f'from weights that do not sum to one is not comparable between runs.',
                parameterName = 'weights', value = weightTotal, validRange = 'Sum to 1.0'
            )

        environmentKey = self.requirements.get('environment')
        if environmentKey is not None and environmentKey not in ENVIRONMENT_SEVERITY:
            raise InvalidInputError(
                message       = f'Unknown environment \'{environmentKey}\'.',
                parameterName = 'environment', value = environmentKey,
                validRange    = str(sorted(ENVIRONMENT_SEVERITY.keys()))
            )
