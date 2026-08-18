
# -- Pressure Stabilization Figure Generator [aerospaceStructures] -- #

'''

Renders axial buckling knockdown factor and margin vs. internal pressure for the stage tank, the
same four-point sweep `codeInterface.pressureStabilization()` prints but does not return. This
script replicates that loop directly against `CylindricalShell`, using the sized wall thickness from
`codeInterface.sizeVessels()`, rather than reimplementing the buckling physics.

Run it with:

    python generatePressureStabilizationPlot.py

Writes docs/images/pressureStabilization.png and prints the points plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'aerospaceStructuresLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from structuresUtils import formatReportTable
from CylindricalShell import CylindricalShell

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('aerospaceStructuresPressureStabilizationCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case  = ci.loadCase()
sized = ci.sizeVessels(case)

#--------------------------------------------------------------------------------------------------------------------------#
# -- Replicate the Four-Point Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

gravity   = 9.80665
thickness = sized['stageTank']['sizing']['requiredThickness']
axialLoad = 6.0 * case['stageTank']['dryMassAbove'] * gravity

pressuresPa = (0.0, 0.5e6, 1.0e6, 2.236e6)
knockdowns, margins, allowables = [], [], []

for pressure in pressuresPa:
    shell = CylindricalShell()
    shell.setInputs({'material': '2219-T87', 'condition': 't87', 'basis': 'A',
                     'radius': case['stageTank']['radius'], 'thickness': thickness,
                     'length': case['stageTank']['cylindricalLength'],
                     'axialLoad': axialLoad, 'internalPressure': pressure})
    result = shell.calculateAxialBuckling()
    knockdowns.append(result['knockdown'])
    margins.append(result['margin'])
    allowables.append(result['allowableStress'] / 1.0e6)

pressuresMPa = [p / 1.0e6 for p in pressuresPa]

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
GREEN  = '#86C06C'

fig, axLeft = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
axLeft.set_facecolor(BG)

axLeft.plot(pressuresMPa, knockdowns, color = ACCENT, linewidth = 2.0, marker = 'o', markersize = 6,
            label = 'Knockdown factor')
axLeft.set_xlabel('Internal pressure [MPa]', color = MUTED, fontsize = 9.5)
axLeft.set_ylabel('Knockdown factor', color = ACCENT, fontsize = 9.5)
axLeft.tick_params(axis = 'y', colors = ACCENT, labelsize = 8.5)
axLeft.tick_params(axis = 'x', colors = MUTED, labelsize = 8.5)

axRight = axLeft.twinx()
axRight.plot(pressuresMPa, margins, color = GREEN, linewidth = 2.0, marker = 's', markersize = 6,
             label = 'Margin')
axRight.set_ylabel('Margin', color = GREEN, fontsize = 9.5)
axRight.tick_params(axis = 'y', colors = GREEN, labelsize = 8.5)
axRight.axhline(0.0, color = GREEN, linewidth = 0.8, linestyle = ':', alpha = 0.6)

axLeft.set_title('Pressure stabilization of the stage tank\naxial buckling knockdown and margin vs. internal pressure',
                 color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in axLeft.spines.values():
    spine.set_color(BORDER)
for spine in axRight.spines.values():
    spine.set_color(BORDER)
axLeft.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
axLeft.set_axisbelow(True)

linesLeft, labelsLeft   = axLeft.get_legend_handles_labels()
linesRight, labelsRight = axRight.get_legend_handles_labels()
axLeft.legend(linesLeft + linesRight, labelsLeft + labelsRight, frameon = False, fontsize = 9,
              labelcolor = TEXT, loc = 'center right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'pressureStabilization.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{p:.3f}', f'{k:.4f}', f'{a:.1f}', f'{m:+.3f}']
        for p, k, a, m in zip(pressuresMPa, knockdowns, allowables, margins)]
print(formatReportTable(rows, ['Internal p [MPa]', 'Knockdown', 'Allowable [MPa]', 'Margin'],
                        title = 'PLOTTED PRESSURE STABILIZATION'))
