
# -- FluidView Class Definition -- #

'''

Thermophysical property viewer: single points, range sweeps, carpet plots and phase diagrams.

Every other class in this library asks the property backend a narrow question and gets on with
sizing hardware. This one asks broad questions and reports the answer, which is what you want when
you are still deciding what the hardware should be.

The four query modes, in increasing order of cost:

    single point     one (input1, input2) pair, N properties
    range sweep      one input swept, the other held constant, N properties
    carpet plot      both inputs swept, N properties over a 2D grid
    phase diagram    the phase field over a temperature-pressure grid

All four route through fluidProps, so they inherit its backend dispatch: the correlation table for
species with no equation of state, REFPROP where a licence is installed, CoolProp otherwise. That
matters here more than anywhere else in the library, because a property viewer is the tool most
likely to be pointed at a fluid the machine cannot model.

The input type pair is a two character code naming the two independent properties being specified,
'TP' for temperature and pressure being by far the most common. The output types are a space
delimited string of property labels. Both follow REFPROP's naming, and PROPERTY_LABELS maps the
readable names onto them.

A note on failure. REFPROP does not raise on a bad request, it returns a large negative sentinel,
and a viewer that plots that sentinel produces a chart with a spike to minus ten million in it.
Every call here is checked against REFPROP_ERROR_SENTINEL and converted into a typed error that
says which species and which state point failed.

Ported from the fluidView class in the propulsionDesign Streamlit application, with the multi-user
job manager, the parallel dispatch and the Streamlit page dropped: this library is not a GUI, and
the sweeps here are small enough to run inline.

See Also:
---------
Line     : The first consumer, for density and viscosity along a run
Orifice  : Chokes on gamma and the critical pressure ratio this reports
Seal     : Permeation, which needs solubility at the service state

Theory: docs/FluidProperties.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from utils import (applyInputs, formatReportTable, fluidProps, writeFile,
                       InvalidInputError, CompatibilityError, createErrorContext)
except ImportError:
    from .utils import (applyInputs, formatReportTable, fluidProps, writeFile,
                        InvalidInputError, CompatibilityError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Lookup Tables -- #
# ------------------------------------------------------------------------------------------------ #

# Readable property name -> backend label. This replaces the CSV the original read off disk, so the
# class has no data file to lose and the units are documented beside the label rather than inferred.
PROPERTY_LABELS = {
    'temperature':            {'label': 'T',      'unit': 'K',        'note': 'absolute'},
    'pressure':               {'label': 'P',      'unit': 'Pa',       'note': 'absolute'},
    'density':                {'label': 'D',      'unit': 'kg/m^3',   'note': 'mass basis'},
    'specific volume':        {'label': 'V',      'unit': 'm^3/kg',   'note': 'reciprocal of density'},
    'enthalpy':               {'label': 'H',      'unit': 'J/kg',     'note': 'reference state is backend dependent'},
    'entropy':                {'label': 'S',      'unit': 'J/kg/K',   'note': 'reference state is backend dependent'},
    'internal energy':        {'label': 'E',      'unit': 'J/kg',     'note': ''},
    'specific heat cp':       {'label': 'CP',     'unit': 'J/kg/K',   'note': 'constant pressure'},
    'specific heat cv':       {'label': 'CV',     'unit': 'J/kg/K',   'note': 'constant volume'},
    'gamma':                  {'label': 'CP/CV',  'unit': '-',        'note': 'ratio of specific heats'},
    'speed of sound':         {'label': 'W',      'unit': 'm/s',      'note': 'sets the choking condition'},
    'viscosity':              {'label': 'VIS',    'unit': 'Pa*s',     'note': 'dynamic, not kinematic'},
    'thermal conductivity':   {'label': 'TCX',    'unit': 'W/m/K',    'note': ''},
    'surface tension':        {'label': 'STN',    'unit': 'N/m',      'note': 'two phase only'},
    'quality':                {'label': 'QMASS',  'unit': '-',        'note': 'vapour mass fraction, two phase only'},
    'compressibility':        {'label': 'Z',      'unit': '-',        'note': 'deviation from ideal gas'},
    'molar mass':             {'label': 'M',      'unit': 'kg/mol',   'note': ''},
    'phase':                  {'label': 'PHASE',  'unit': '-',        'note': 'returns a string, not a number'},
}

# Phase strings mapped onto integers, because a contour plot needs a number. The ordering is not
# physically meaningful; it exists so that adjacent fields get adjacent contour levels.
PHASE_CODES = {
    'Subcooled liquid': 1,
    'Superheated gas':  2,
    'Supercritical':    3,
    'Two-phase':        4,
}
PHASE_UNKNOWN = 0    # [-], anything the backend reports that is not in the table above

# REFPROP signals a failed lookup with a large negative number rather than raising. Anything at or
# below this is a failure, not a property value.
REFPROP_ERROR_SENTINEL = -9.0e6    # [-]

# Two character input pair codes that are worth naming, for the report and for input validation.
INPUT_PAIRS = {
    'TP': 'temperature and pressure',
    'TD': 'temperature and density',
    'PD': 'pressure and density',
    'PH': 'pressure and enthalpy',
    'PS': 'pressure and entropy',
    'TQ': 'temperature and quality, on the saturation line',
    'PQ': 'pressure and quality, on the saturation line',
    'HS': 'enthalpy and entropy',
}

MAXIMUM_GRID_POINTS = 250000    # [-], a carpet plot larger than this is almost certainly a mistake

# ------------------------------------------------------------------------------------------------ #
# -- Module Level Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def resolveProperty(name: str) -> str:

    '''

    Resolve a readable property name onto its backend label.

    Accepts either form, so 'density' and 'D' both return 'D'. Unknown names raise rather than
    being passed through, because the backend's own response to an unknown label is the sentinel
    rather than an error, and that is much harder to diagnose downstream.

    '''

    if not isinstance(name, str) or not name.strip():
        raise InvalidInputError('Property name must be a non-empty string.',
                                context = createErrorContext(component = 'FluidView'))

    cleaned = name.strip()

    # readable name
    if cleaned.lower() in PROPERTY_LABELS:
        return PROPERTY_LABELS[cleaned.lower()]['label']

    # already a backend label
    knownLabels = {entry['label'] for entry in PROPERTY_LABELS.values()}
    if cleaned.upper() in knownLabels:
        return cleaned.upper()

    raise InvalidInputError(
        f'Unknown property \'{name}\'. Known readable names: {sorted(PROPERTY_LABELS)}.',
        context = createErrorContext(component = 'FluidView'))

def propertyUnit(label: str) -> str:

    '''

    The documented unit for a backend label, or an empty string if the label is not in the table.

    '''

    for entry in PROPERTY_LABELS.values():
        if entry['label'] == label:
            return entry['unit']
    return ''

def listAvailableFluids() -> dict:

    '''

    What the machine can actually model, by backend.

    The original scanned a REFPROP installation and raised if it found none, which is the wrong
    behaviour for a library that is meant to run on a machine without a licence. This reports what
    is present instead, and the caller decides whether that is enough.

    '''

    available = {'refprop': [], 'correlation': ['hydrazine'], 'refpropInstalled': False}

    for root in (os.path.join(os.path.expanduser('~'), 'REFPROP'),
                 os.path.join('C:', os.sep, 'Program Files (x86)', 'REFPROP')):

        fluidsDirectory = os.path.join(root, 'FLUIDS')
        if not os.path.isdir(fluidsDirectory):
            continue

        available['refpropInstalled'] = True
        available['refpropRoot']      = root
        available['refprop']          = sorted(os.path.splitext(name)[0]
                                               for name in os.listdir(fluidsDirectory)
                                               if name.upper().endswith('.FLD'))
        break

    return available

# ------------------------------------------------------------------------------------------------ #
# -- FluidView -- #
# ------------------------------------------------------------------------------------------------ #

class FluidView:

    '''

    Thermophysical property viewer.

    Usage:
    ------
        view = FluidView()
        view.setInputs({'species': 'N2', 'inputTypes': 'TP',
                        'outputTypes': ['density', 'viscosity'],
                        'firstValue': 300.0, 'secondValue': 5.0e6})
        result = view.calculateSinglePoint()

    '''

    def __init__(self):

        # -- Query Definition -- #

        self.species          = ''      # [case sensitive string], or 'A;B' for a mixture
        self.inputTypes       = 'TP'    # [-], two character code, key into INPUT_PAIRS
        self.outputTypes      = []      # [-], readable names or backend labels
        self.mixtureRatio     = [1.0]   # [-], mole fractions, one per component

        # -- Single Point -- #

        self.firstValue       = np.nan  # [varies with inputTypes]
        self.secondValue      = np.nan  # [varies with inputTypes]

        # -- Sweeps -- #

        self.firstRange       = None    # [varies], array of first input values
        self.secondRange      = None    # [varies], array of second input values

        # -- Results -- #

        self.outputLabels     = []      # [-], resolved backend labels
        self.outputUnits      = []      # [-], one unit string per output
        self.values           = None    # [varies], point, sweep or grid depending on the call
        self.phaseField       = None    # [-], integer coded phase grid
        self.findings         = []      # [-], anything worth telling the user

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: species.

        '''

        requiredParams = {'species': str}

        optionalParams = {'inputTypes':   str,
                          'outputTypes':  (list, tuple, str),
                          'mixtureRatio': (list, tuple),
                          'firstValue':   (int, float),
                          'secondValue':  (int, float),
                          'firstRange':   (list, tuple, np.ndarray),
                          'secondRange':  (list, tuple, np.ndarray)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        # a mixture is given to the backend as a semicolon delimited string
        if isinstance(self.species, (list, tuple)):
            self.species = ';'.join(self.species)

        # accept a space delimited string as well as a list
        if isinstance(self.outputTypes, str):
            self.outputTypes = self.outputTypes.split()

        self.inputTypes = str(self.inputTypes).upper()

        if self.firstRange is not None:
            self.firstRange = np.asarray(self.firstRange, dtype = float)
        if self.secondRange is not None:
            self.secondRange = np.asarray(self.secondRange, dtype = float)

        self.outputLabels = [resolveProperty(name) for name in self.outputTypes]

    # -------------------------------------------------------------------------------------------- #

    def _query(self, labels: str, firstValue: float, secondValue: float) -> list:

        '''

        One backend call, with the sentinel converted into a typed error.

        Returns a list even for a single output, so the callers do not have to branch on count.

        '''

        raw = fluidProps(self.species, self.inputTypes, labels,
                         float(firstValue), float(secondValue),
                         mixtureRatio = list(self.mixtureRatio))

        values = list(raw) if isinstance(raw, (list, tuple, np.ndarray)) else [raw]

        for value in values:
            # a phase query returns a string, which is a valid answer
            if isinstance(value, str):
                continue
            if not np.isfinite(value) or value <= REFPROP_ERROR_SENTINEL:
                raise CompatibilityError(
                    f'The property backend could not evaluate \'{self.species}\' at '
                    f'{self.inputTypes} = ({firstValue:g}, {secondValue:g}). The species may not be '
                    f'modelled on this machine, or the state point may be outside its range.',
                    context = createErrorContext(component = 'FluidView', fluid = self.species))

        return values

    def _resolveUnits(self) -> list:

        '''

        One unit string per output. The backend only returns units for the first output of a call,
        so this costs one call per property.

        '''

        anchorFirst  = self.firstValue  if np.isfinite(self.firstValue)  else float(self.firstRange[0])
        anchorSecond = self.secondValue if np.isfinite(self.secondValue) else float(self.secondRange[0])

        units = []
        for label in self.outputLabels:
            try:
                reported = fluidProps(self.species, self.inputTypes, label,
                                      anchorFirst, anchorSecond,
                                      mixtureRatio = list(self.mixtureRatio), units = True)
                units.append(reported if isinstance(reported, str) else propertyUnit(label))
            except Exception:
                # the documented unit is a perfectly good fallback and never fails
                units.append(propertyUnit(label))

        return units

    # -------------------------------------------------------------------------------------------- #

    def calculateSinglePoint(self) -> dict:

        '''

        Evaluate every requested property at one state point.

        '''

        self._validateInputs(mode = 'point')

        values = self._query(' '.join(self.outputLabels), self.firstValue, self.secondValue)

        self.values      = values
        self.outputUnits = self._resolveUnits()
        self.findings    = []

        self._noteBackend()

        return {'species':      self.species,
                'inputTypes':   self.inputTypes,
                'firstValue':   self.firstValue,
                'secondValue':  self.secondValue,
                'properties':   dict(zip(self.outputLabels, values)),
                'units':        dict(zip(self.outputLabels, self.outputUnits)),
                'findings':     self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateRangeSweep(self) -> dict:

        '''

        Sweep the first input across firstRange with the second held at secondValue.

        Returns one array per property, which is what a line plot wants.

        '''

        self._validateInputs(mode = 'sweep')

        rows = np.empty((len(self.firstRange), len(self.outputLabels)), dtype = float)

        for index, value in enumerate(self.firstRange):
            rows[index, :] = self._query(' '.join(self.outputLabels), value, self.secondValue)

        self.values      = rows
        self.outputUnits = self._resolveUnits()
        self.findings    = []

        self._noteBackend()

        return {'species':     self.species,
                'inputTypes':  self.inputTypes,
                'firstRange':  self.firstRange,
                'secondValue': self.secondValue,
                'properties':  {label: rows[:, column]
                                for column, label in enumerate(self.outputLabels)},
                'units':       dict(zip(self.outputLabels, self.outputUnits)),
                'findings':    self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateCarpetPlot(self) -> dict:

        '''

        Sweep both inputs, producing one 2D grid per property.

        The grid is indexed [firstRange, secondRange], so grid[i, j] is the property at
        firstRange[i] and secondRange[j].

        '''

        self._validateInputs(mode = 'carpet')

        rowCount    = len(self.firstRange)
        columnCount = len(self.secondRange)

        grids = {label: np.empty((rowCount, columnCount), dtype = float)
                 for label in self.outputLabels}

        joined = ' '.join(self.outputLabels)

        for row, firstValue in enumerate(self.firstRange):
            for column, secondValue in enumerate(self.secondRange):
                values = self._query(joined, firstValue, secondValue)
                for index, label in enumerate(self.outputLabels):
                    grids[label][row, column] = values[index]

        self.values      = grids
        self.outputUnits = self._resolveUnits()
        self.findings    = []

        self._noteBackend()

        return {'species':     self.species,
                'inputTypes':  self.inputTypes,
                'firstRange':  self.firstRange,
                'secondRange': self.secondRange,
                'gridPoints':  rowCount * columnCount,
                'properties':  grids,
                'units':       dict(zip(self.outputLabels, self.outputUnits)),
                'findings':    self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculatePhaseDiagram(self) -> dict:

        '''

        The phase field over a temperature-pressure grid, integer coded for contouring.

        Ignores outputTypes: the only output is the phase. Requires inputTypes of 'TP', since a
        phase diagram in any other pair of coordinates is a different chart.

        '''

        self._validateInputs(mode = 'carpet')

        if self.inputTypes != 'TP':
            raise InvalidInputError(
                f'A phase diagram needs inputTypes of \'TP\', not \'{self.inputTypes}\'.',
                context = createErrorContext(component = 'FluidView', fluid = self.species))

        rowCount    = len(self.firstRange)
        columnCount = len(self.secondRange)

        names = np.empty((rowCount, columnCount), dtype = object)
        codes = np.zeros((rowCount, columnCount), dtype = int)

        unrecognised = set()

        for row, temperature in enumerate(self.firstRange):
            for column, pressure in enumerate(self.secondRange):
                phase = self._query('PHASE', temperature, pressure)[0]
                names[row, column] = phase
                codes[row, column] = PHASE_CODES.get(phase, PHASE_UNKNOWN)
                if phase not in PHASE_CODES:
                    unrecognised.add(str(phase))

        self.phaseField = codes
        self.findings   = []

        if unrecognised:
            self.findings.append(
                f'The backend reported {len(unrecognised)} phase name(s) not in PHASE_CODES, '
                f'coded as {PHASE_UNKNOWN}: {sorted(unrecognised)}.')

        found = {name for name in PHASE_CODES if (names == name).any()}
        if len(found) == 1:
            self.findings.append(
                f'The whole grid is \'{sorted(found)[0]}\'. The bounds probably do not straddle a '
                f'phase boundary, so this diagram shows nothing.')

        self._noteBackend()

        return {'species':          self.species,
                'temperatureRange': self.firstRange,
                'pressureRange':    self.secondRange,
                'phaseNames':       names,
                'phaseCodes':       codes,
                'phasesPresent':    sorted(found),
                'codeLegend':       dict(PHASE_CODES),
                'findings':         self.findings}

    # -------------------------------------------------------------------------------------------- #

    def exportPropertyTable(self, outputDir: str = None) -> list:

        '''

        Write one CSV per property over the current carpet plot grid.

        Rows are the first input, columns are the second, and the first row and column carry the
        input values so the file is readable without the calling code.

        '''

        if not isinstance(self.values, dict):
            self.calculateCarpetPlot()

        targetDir = outputDir if outputDir is not None else os.getcwd()
        targetDir = os.path.join(targetDir, f'{self.species.replace(";", "_")}_properties')
        os.makedirs(targetDir, exist_ok = True)

        written = []

        for label, grid in self.values.items():

            table = np.zeros((len(self.firstRange) + 1, len(self.secondRange) + 1))
            table[0, 0]  = np.nan
            table[0, 1:] = self.secondRange
            table[1:, 0] = self.firstRange
            table[1:, 1:] = grid

            path = os.path.join(targetDir, f'{self.species.replace(";", "_")}_{label}.csv')
            writeFile(path, table)
            written.append(path)

        return written

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        A readable summary of the last query.

        '''

        if self.values is None and self.phaseField is None:
            self.calculateSinglePoint()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  FLUID VIEW: {self.species}')
        lines.append('=' * 96)
        lines.append('')
        lines.append(f'  input pair: {self.inputTypes} '
                     f'({INPUT_PAIRS.get(self.inputTypes, "unnamed pair")})')

        backend = listAvailableFluids()
        lines.append(f'  backend:    {"REFPROP" if backend["refpropInstalled"] else "CoolProp"}')
        lines.append('')

        if isinstance(self.values, list):
            rows = [[label, f'{value:.6g}' if not isinstance(value, str) else value, unit]
                    for label, value, unit in zip(self.outputLabels, self.values, self.outputUnits)]
            lines.append(formatReportTable(rows, ['Property', 'Value', 'Unit'],
                                           title = f'State point '
                                                   f'({self.firstValue:g}, {self.secondValue:g})'))

        elif isinstance(self.values, np.ndarray):
            rows = [[label,
                     f'{self.values[:, column].min():.6g}',
                     f'{self.values[:, column].max():.6g}',
                     unit]
                    for column, (label, unit) in enumerate(zip(self.outputLabels, self.outputUnits))]
            lines.append(formatReportTable(rows, ['Property', 'Minimum', 'Maximum', 'Unit'],
                                           title = f'Sweep over {len(self.firstRange)} points'))

        elif isinstance(self.values, dict):
            rows = [[label, f'{grid.min():.6g}', f'{grid.max():.6g}',
                     dict(zip(self.outputLabels, self.outputUnits)).get(label, '')]
                    for label, grid in self.values.items()]
            lines.append(formatReportTable(rows, ['Property', 'Minimum', 'Maximum', 'Unit'],
                                           title = f'Carpet plot, '
                                                   f'{len(self.firstRange)} x '
                                                   f'{len(self.secondRange)} grid'))

        if self.phaseField is not None:
            present = {name: int((self.phaseField == code).sum())
                       for name, code in PHASE_CODES.items()
                       if (self.phaseField == code).any()}
            rows = [[name, str(count),
                     f'{100.0 * count / self.phaseField.size:.1f} %']
                    for name, count in present.items()]
            lines.append('')
            lines.append(formatReportTable(rows, ['Phase', 'Grid points', 'Fraction'],
                                           title = 'Phase field'))

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
            path = os.path.join(outputDir, f'fluidView_{self.species.replace(";", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _noteBackend(self) -> None:

        '''

        Record which backend answered, since it changes the fidelity of every number above.

        '''

        backend = listAvailableFluids()

        if self.species.lower() in backend['correlation']:
            self.findings.append(
                f'\'{self.species}\' has no equation of state in either backend and was served by '
                f'the built-in correlation table. Treat the values as engineering estimates.')
        elif not backend['refpropInstalled']:
            self.findings.append(
                'No REFPROP installation was found, so CoolProp answered. CoolProp does not '
                'support mixtures through this interface.')

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self, mode: str = 'point') -> None:

        '''

        Check the inputs the requested mode actually needs.

        '''

        context = createErrorContext(component = 'FluidView', fluid = self.species)

        if not self.species:
            raise InvalidInputError('Species not provided.', context = context)

        if len(self.inputTypes) != 2:
            raise InvalidInputError(
                f'inputTypes must be a two character code, got \'{self.inputTypes}\'.',
                context = context)

        if not self.outputLabels and mode != 'phase':
            raise InvalidInputError('No output properties requested.', context = context)

        componentCount = len(self.species.split(';'))
        if len(self.mixtureRatio) != componentCount:
            raise InvalidInputError(
                f'mixtureRatio has {len(self.mixtureRatio)} entries for a {componentCount} '
                f'component species.', context = context)

        if mode == 'point':
            if not np.isfinite(self.firstValue) or not np.isfinite(self.secondValue):
                raise InvalidInputError(
                    'A single point calculation needs firstValue and secondValue.',
                    context = context)

        if mode in ('sweep', 'carpet'):
            if self.firstRange is None or len(self.firstRange) == 0:
                raise InvalidInputError('A sweep needs a non-empty firstRange.', context = context)

        if mode == 'sweep':
            if not np.isfinite(self.secondValue):
                raise InvalidInputError(
                    'A range sweep needs secondValue, the input held constant.', context = context)

        if mode == 'carpet':
            if self.secondRange is None or len(self.secondRange) == 0:
                raise InvalidInputError('A carpet plot needs a non-empty secondRange.',
                                        context = context)

            gridPoints = len(self.firstRange) * len(self.secondRange)
            if gridPoints > MAXIMUM_GRID_POINTS:
                raise InvalidInputError(
                    f'A {len(self.firstRange)} x {len(self.secondRange)} grid is '
                    f'{gridPoints} backend calls, above the {MAXIMUM_GRID_POINTS} guard. '
                    f'Coarsen the ranges or raise MAXIMUM_GRID_POINTS deliberately.',
                    context = context)
