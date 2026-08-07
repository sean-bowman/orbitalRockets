
# -- Input Plumbing and Report Formatting [orbitalRockets common] -- #

'''

The shared plumbing every component class in this repository uses.

applyInputs is the setInputs() implementation. It coerces None to np.nan so downstream isnan
logic behaves, raises a named error for a missing required parameter rather than failing three
functions later with an AttributeError, and warns about unrecognized keys so that a typo in a
config file does not silently do nothing.

formatReportTable renders the generateReport() output, so every class in every domain prints its
results the same way.

Author: Sean Bowman
Date:   08/06/2026

'''

import os
import pickle
from typing import Any, Optional

import numpy as np

try:
    from errors import InvalidInputError
except ImportError:
    from .errors import InvalidInputError

#--------------------------------------------------------------------------------------------------------------------------#
# -- Component Input Plumbing -- #
#--------------------------------------------------------------------------------------------------------------------------#

def applyInputs(component: Any, inputs: dict, requiredParams: dict, optionalParams: Optional[dict] = None) -> None:

    '''

    Shared setInputs() plumbing used by every component class in this library.

    Every component takes its configuration as a flat dictionary, so this function does the three
    things that every setInputs() would otherwise reimplement:

    1. Coerce None to np.nan, so downstream np.isnan() checks behave and a missing optional value
       does not silently propagate as a TypeError three functions later.
    2. Assign each required parameter, raising a named error if it is absent. The error message
       comes from requiredParams so the user is told what the parameter means, not just its key.
    3. Assign each optional parameter if present, leaving the class default alone if it is not.

    ---------------------------------------------------------------------------
                                    INPUTS
    ---------------------------------------------------------------------------
    - component        The object to set attributes on (usually self)
    - inputs           Flat dictionary of user-supplied values
    - requiredParams   {attributeName: 'error message if missing'}
    - optionalParams   Iterable or dict of attribute names that may be absent

    '''

    # Convert None values to np.nan for compatibility with np.isnan() logic downstream
    workingInputs = dict(inputs)
    for key, value in workingInputs.items():
        if value is None:
            workingInputs[key] = np.nan

    for parameterName, errorMessage in requiredParams.items():
        if parameterName in workingInputs:
            setattr(component, parameterName, workingInputs[parameterName])
        else:
            raise InvalidInputError(
                message       = errorMessage,
                parameterName = parameterName,
                value         = None,
                validRange    = 'Any value; this parameter is required'
            )

    if optionalParams is not None:
        for parameterName in optionalParams:
            if parameterName in workingInputs:
                setattr(component, parameterName, workingInputs[parameterName])

    # Warn about keys the component does not recognize. A silently ignored typo in a config file is
    # one of the more expensive ways to waste an afternoon.
    knownKeys   = set(requiredParams.keys()) | set(optionalParams or [])
    unknownKeys = set(workingInputs.keys()) - knownKeys
    if unknownKeys:
        print(f'Warning: {type(component).__name__}.setInputs received unrecognized keys that will be ignored: {sorted(unknownKeys)}')
#--------------------------------------------------------------------------------------------------------------------------#
# -- Output Helpers -- #
#--------------------------------------------------------------------------------------------------------------------------#

def formatReportTable(rows: list, columnHeaders: list, title: str = '') -> str:

    '''

    Render a list of rows as a fixed-width text table for generateReport().

    Every component class prints its results the same way, so the formatting lives here rather than
    being reinvented sixteen times. Columns are auto-sized to their widest entry.

    '''

    stringRows = [[str(cell) for cell in row] for row in rows]
    allRows    = [[str(header) for header in columnHeaders]] + stringRows

    columnWidths = [max(len(row[index]) for row in allRows) for index in range(len(columnHeaders))]

    def renderRow(cells: list) -> str:
        return '  '.join(cell.ljust(columnWidths[index]) for index, cell in enumerate(cells))

    totalWidth = sum(columnWidths) + 2 * (len(columnWidths) - 1)

    lines = []
    if title:
        lines.append('=' * totalWidth)
        lines.append(title)
    lines.append('=' * totalWidth)
    lines.append(renderRow([str(header) for header in columnHeaders]))
    lines.append('-' * totalWidth)
    for row in stringRows:
        lines.append(renderRow(row))
    lines.append('=' * totalWidth)

    return '\n'.join(lines)

def writeFile(filename: str, data: np.ndarray | list, headers: bool = False) -> None:

    '''

    Wrapper for writing tabular data to a .csv or .txt file. The delimiter is chosen from the file
    extension so that .csv opens cleanly in Excel and .txt stays whitespace delimited for CAD import.

    '''

    dataArray = np.asarray(data)
    delimiter = ',' if filename.lower().endswith('.csv') else '\t'

    headerRow = ''
    if headers is not False and headers is not None and headers is not True:
        headerRow = delimiter.join(str(entry) for entry in headers)

    np.savetxt(filename, dataArray, delimiter = delimiter, header = headerRow, comments = '')

def pickleObject(obj: Any, filePath: str) -> None:

    '''

    Serialize a component object to disk so a completed sizing run can be reloaded without repeating
    the property lookups. Only ever unpickle files you produced yourself.

    '''

    directory = os.path.dirname(filePath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok = True)

    with open(filePath, 'wb') as fileHandle:
        pickle.dump(obj, fileHandle)
