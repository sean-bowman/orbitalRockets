
# -- LoadCase Class Definition -- #

'''

Load combination, limit and ultimate factors, and identification of the governing case.

The governing load case is rarely the largest single load, and that is the whole reason this class
exists. Liftoff has the highest axial acceleration and almost no aerodynamic load. Max-Q has
moderate axial acceleration and the highest bending moment. Staging has a transient axial load and
a shock. A structure checked against the worst of each individually is checked against a case that
never occurs, and a structure checked only at liftoff misses max-Q entirely.

The factor ladder, per NASA-STD-5001:

    limit load        the maximum expected during the mission
    yield load        limit x 1.10, must not yield
    ultimate load     limit x 1.40, must not rupture

Those are for a structure qualified by test. A structure qualified by analysis alone carries higher
factors, and a model uncertainty factor multiplies on top where the loads themselves come from a
model rather than from measurement.

Two things are commonly got wrong. The first is applying the factor to the wrong quantity: the
factor multiplies the load, not the allowable, and for a nonlinear response, such as buckling under
combined load, those are not the same operation. The second is combining already-factored loads,
which double-counts.

See Also:
---------
CylindricalShell : Consumes the combined loads this produces
environmentsAndLoads : (planned) supplies the load sources this combines

Theory: docs/LoadsAndLoadCases.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from structuresUtils import (applyInputs, formatReportTable, marginOfSafety,
                                 InvalidInputError, createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, marginOfSafety,
                                  InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# NASA-STD-5001 factors of safety for structures qualified by test.
YIELD_FACTOR    = 1.10    # [-], against yield
ULTIMATE_FACTOR = 1.40    # [-], against rupture

# Higher factors where qualification is by analysis alone, with no qualification test article.
YIELD_FACTOR_ANALYSIS    = 1.60    # [-]
ULTIMATE_FACTOR_ANALYSIS = 2.00    # [-]

# A model uncertainty factor multiplies on top where the loads come from a model rather than from
# flight or test measurement.
MODEL_UNCERTAINTY_DEFAULT = 1.00    # [-], raise where the loads are unvalidated

# Representative mission phases. Accelerations are in g, moments and pressures are placeholders the
# caller overrides; the point of the table is the shape of a load case matrix, not these numbers.
STANDARD_PHASES = {
    'ground handling': {'axial': 1.0,  'lateral': 0.5, 'note': 'crane, transport, erection'},
    'liftoff':         {'axial': 3.0,  'lateral': 1.0, 'note': 'highest axial, acoustic, transient'},
    'max-Q':           {'axial': 2.5,  'lateral': 2.0, 'note': 'highest bending, aerodynamic'},
    'max acceleration': {'axial': 6.0, 'lateral': 0.3, 'note': 'end of first stage burn'},
    'staging':         {'axial': 0.5,  'lateral': 0.5, 'note': 'transient, shock, separation'},
    'entry':           {'axial': 4.0,  'lateral': 1.5, 'note': 'reusable stages only'},
}

# ------------------------------------------------------------------------------------------------ #
# -- LoadCase -- #
# ------------------------------------------------------------------------------------------------ #

class LoadCase:

    '''

    Load case combination and governing case identification.

    Usage:
    ------
        cases = LoadCase()
        cases.setInputs({'referenceMass': 5000.0, 'referenceRadius': 1.0,
                         'qualificationBy': 'test'})
        cases.addCase('liftoff', axialG = 3.0, lateralG = 1.0, internalPressure = 2.5e6)
        cases.addCase('max-Q', axialG = 2.5, lateralG = 2.0, internalPressure = 2.2e6,
                      dynamicPressure = 35.0e3)
        result = cases.identifyGoverning()

    '''

    def __init__(self):

        # -- Reference -- #

        self.referenceMass    = np.nan  # [kg], mass above the station being analysed
        self.referenceRadius  = np.nan  # [m], for converting lateral g into a moment
        self.referenceLength  = np.nan  # [m], moment arm for the lateral load

        # -- Factors -- #

        self.qualificationBy  = 'test'  # 'test' or 'analysis'
        self.modelUncertainty = MODEL_UNCERTAINTY_DEFAULT  # [-]

        # -- Cases -- #

        self.cases            = {}      # [-], name -> load dictionary

        # -- Results -- #

        self.findings         = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: referenceMass.

        '''

        requiredParams = {'referenceMass': (int, float)}

        optionalParams = {'referenceRadius':  (int, float),
                          'referenceLength':  (int, float),
                          'qualificationBy':  str,
                          'modelUncertainty': (int, float),
                          'cases':            dict}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.qualificationBy not in ('test', 'analysis'):
            raise InvalidInputError(
                f'qualificationBy must be \'test\' or \'analysis\', got '
                f'\'{self.qualificationBy}\'.',
                context = createErrorContext(component = 'LoadCase'))

    # -------------------------------------------------------------------------------------------- #

    @property
    def yieldFactor(self) -> float:

        '''
        Yield factor of safety, including the model uncertainty factor.
        '''

        base = YIELD_FACTOR if self.qualificationBy == 'test' else YIELD_FACTOR_ANALYSIS

        return base * self.modelUncertainty

    @property
    def ultimateFactor(self) -> float:

        '''
        Ultimate factor of safety, including the model uncertainty factor.
        '''

        base = (ULTIMATE_FACTOR if self.qualificationBy == 'test'
                else ULTIMATE_FACTOR_ANALYSIS)

        return base * self.modelUncertainty

    # -------------------------------------------------------------------------------------------- #

    def addCase(self, name: str, axialG: float = 0.0, lateralG: float = 0.0,
                internalPressure: float = 0.0, externalPressure: float = 0.0,
                dynamicPressure: float = 0.0, thermalDelta: float = 0.0,
                note: str = '') -> None:

        '''

        Add a load case. Values are limit loads, unfactored.

        Adding an already-factored load double-counts, which is one of the two errors this class
        exists to prevent, so the docstring says it here and the report says it again.

        '''

        if not np.isfinite(self.referenceMass):
            raise InvalidInputError('Set referenceMass before adding cases.',
                                    context = createErrorContext(component = 'LoadCase'))

        gravity = 9.80665    # [m/s^2]

        axialLoad   = axialG * self.referenceMass * gravity
        lateralLoad = lateralG * self.referenceMass * gravity

        moment = 0.0
        if np.isfinite(self.referenceLength):
            moment = lateralLoad * self.referenceLength / 2.0

        self.cases[name] = {'axialG':           axialG,
                            'lateralG':         lateralG,
                            'axialLoad':        axialLoad,
                            'lateralLoad':      lateralLoad,
                            'bendingMoment':    moment,
                            'internalPressure': internalPressure,
                            'externalPressure': externalPressure,
                            'dynamicPressure':  dynamicPressure,
                            'thermalDelta':     thermalDelta,
                            'note':             note}

    def addStandardPhases(self, phases: list = None) -> None:

        '''

        Populate from the representative phase table, as a starting point to be overridden.

        '''

        for name in (phases if phases is not None else list(STANDARD_PHASES)):
            if name not in STANDARD_PHASES:
                raise InvalidInputError(
                    f'Unknown phase \'{name}\'. Known: {sorted(STANDARD_PHASES)}.',
                    context = createErrorContext(component = 'LoadCase'))
            entry = STANDARD_PHASES[name]
            self.addCase(name, axialG = entry['axial'], lateralG = entry['lateral'],
                         note = entry['note'])

    # -------------------------------------------------------------------------------------------- #

    def factoredLoads(self, level: str = 'ultimate') -> dict:

        '''

        Every case at the requested factor level.

        The factor multiplies the load, not the allowable. For a nonlinear response such as
        buckling under combined load those are not the same operation, and factoring the allowable
        instead is unconservative wherever the interaction is superlinear.

        '''

        if level not in ('limit', 'yield', 'ultimate'):
            raise InvalidInputError(
                f'level must be \'limit\', \'yield\' or \'ultimate\', got \'{level}\'.',
                context = createErrorContext(component = 'LoadCase'))

        factor = {'limit': 1.0, 'yield': self.yieldFactor,
                  'ultimate': self.ultimateFactor}[level]

        factored = {}
        for name, case in self.cases.items():
            factored[name] = {key: (value * factor
                                    if isinstance(value, (int, float))
                                    and key not in ('axialG', 'lateralG')
                                    else value)
                              for key, value in case.items() if key != 'note'}
            factored[name]['appliedFactor'] = factor

        return factored

    # -------------------------------------------------------------------------------------------- #

    def identifyGoverning(self, metric: str = 'axialLoad') -> dict:

        '''

        Which case governs, by the chosen metric, and by a combined severity index.

        The severity index is a non-dimensional sum of the load components normalised by their
        maxima across the case set. It exists to catch the case that is not the largest in any one
        component and is the worst overall, which is the situation the class is built around.

        '''

        if not self.cases:
            raise InvalidInputError('No load cases have been added.',
                                    context = createErrorContext(component = 'LoadCase'))

        components = ('axialLoad', 'bendingMoment', 'internalPressure',
                      'externalPressure', 'dynamicPressure')

        maxima = {key: max(abs(case.get(key, 0.0)) for case in self.cases.values())
                  for key in components}

        severity = {}
        for name, case in self.cases.items():
            total = 0.0
            for key in components:
                if maxima[key] > 0.0:
                    total += abs(case.get(key, 0.0)) / maxima[key]
            severity[name] = total

        byMetric  = max(self.cases, key = lambda name: abs(self.cases[name].get(metric, 0.0)))
        bySeverity = max(severity, key = severity.get)

        self.findings = []

        self.findings.append(
            f'By {metric} alone, \'{byMetric}\' governs. By combined severity, '
            f'\'{bySeverity}\' does.')

        if byMetric != bySeverity:
            self.findings.append(
                f'These disagree. \'{bySeverity}\' is not the largest case in {metric} and is the '
                f'worst overall, which is exactly why load cases are combined rather than '
                f'enveloped component by component.')

        # the envelope is a case that never occurs
        envelope = {key: maxima[key] for key in components}
        realCase = self.cases[bySeverity]
        envelopeExcess = {}
        for key in components:
            if realCase.get(key, 0.0) > 0.0 and maxima[key] > 0.0:
                envelopeExcess[key] = maxima[key] / abs(realCase[key])

        if any(value > 1.05 for value in envelopeExcess.values()):
            self.findings.append(
                'Designing to the component-by-component envelope is conservative but it sizes '
                'against a condition that never occurs, and it hides which phase actually drives '
                'the structure.')

        self.findings.append(
            f'Factors applied: yield {self.yieldFactor:.2f}, ultimate '
            f'{self.ultimateFactor:.2f}, qualification by {self.qualificationBy}. These multiply '
            f'the load, not the allowable.')

        return {'governingByMetric':   byMetric,
                'governingBySeverity': bySeverity,
                'metric':              metric,
                'severityIndex':       severity,
                'componentMaxima':     maxima,
                'envelope':            envelope,
                'agree':               bool(byMetric == bySeverity),
                'findings':            self.findings}

    # -------------------------------------------------------------------------------------------- #

    def checkAgainstAllowable(self, allowableStress: float, area: float,
                              level: str = 'ultimate') -> dict:

        '''

        Margin for every case against a single allowable, at the requested factor level.

        '''

        factored = self.factoredLoads(level)

        margins = {}
        for name, case in factored.items():
            stress = abs(case['axialLoad']) / area if area > 0.0 else np.nan
            margins[name] = allowableStress / stress - 1.0 if stress > 0.0 else np.inf

        governing = min(margins, key = margins.get)

        return {'margins':         margins,
                'governingCase':   governing,
                'governingMargin': margins[governing],
                'level':           level,
                'acceptable':      bool(margins[governing] >= 0.0)}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable load case matrix.
        '''

        result = self.identifyGoverning()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  LOAD CASES: {len(self.cases)} cases, '
                     f'{self.referenceMass:.0f} kg reference mass')
        lines.append('=' * 96)
        lines.append('')

        rows = []
        for name, case in self.cases.items():
            rows.append([name,
                         f'{case["axialG"]:.2f}',
                         f'{case["lateralG"]:.2f}',
                         f'{case["internalPressure"] / 1.0e6:.2f}',
                         f'{result["severityIndex"][name]:.3f}',
                         'GOVERNS' if name == result['governingBySeverity'] else ''])

        lines.append(formatReportTable(
            rows, ['Case', 'Axial [g]', 'Lateral [g]', 'p_int [MPa]', 'Severity', ''],
            title = 'Limit loads'))

        lines.append('')
        factorRows = [['Yield',    f'{self.yieldFactor:.2f}', ''],
                      ['Ultimate', f'{self.ultimateFactor:.2f}', ''],
                      ['Qualification', self.qualificationBy, ''],
                      ['Model uncertainty', f'{self.modelUncertainty:.2f}', '']]
        lines.append(formatReportTable(factorRows, ['Factor', 'Value', ''],
                                       title = 'Factors of safety'))

        if self.findings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in self.findings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'loadCases.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the reference quantities are present.
        '''

        context = createErrorContext(component = 'LoadCase')

        if not np.isfinite(self.referenceMass) or self.referenceMass <= 0.0:
            raise InvalidInputError('Reference mass must be positive.', context = context)

        if self.modelUncertainty < 1.0:
            raise InvalidInputError(
                f'Model uncertainty factor must be at least 1.0, got {self.modelUncertainty}.',
                context = context)
