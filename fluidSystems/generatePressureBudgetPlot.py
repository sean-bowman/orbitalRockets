
# -- Pressure Budget Figure Generator [fluidSystems] -- #

'''

Renders the pressure budget from the 100 N hydrazine monopropellant feed system worked example as a
horizontal bar chart, station by station from the chamber up to the He bottle.

The station pressures are not recomputed here. They are read directly off the `stations` list that
`codeInterface.py` builds while walking the chain, loaded by explicit path so this script never
collides with another domain's `codeInterface` module in `sys.modules`.

Run it with:

    python generatePressureBudgetPlot.py

Writes fluidSystemsLibrary/docs/images/pressureBudget.png (this domain keeps its documentation
under fluidSystemsLibrary/docs rather than a domain-root docs/, predating the convention every
later domain follows) and prints the station table plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'fluidSystemsLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('fluidSystemsPressureBudgetCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

stations = ci.stations   # [(name, pressure [Pa], note), ...], upstream order (chamber to bottle)

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
GREEN  = '#86C06C'

names       = [s[0] for s in stations]
pressuresMPa = [s[1] / 1.0e6 for s in stations]

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

yPositions = np.arange(len(names))
colors     = [ACCENT if i < len(names) - 1 else GREEN for i in range(len(names))]
ax.barh(yPositions, pressuresMPa, color = colors, height = 0.62, edgecolor = 'none')

ax.set_yticks(yPositions)
ax.set_yticklabels(names, color = TEXT, fontsize = 9)
ax.invert_yaxis()
ax.set_xlabel('Pressure [MPa]', color = MUTED, fontsize = 9.5)
ax.set_title('Pressure budget, 100 N hydrazine monoprop feed system\nchamber to He bottle, upstream order',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.xaxis.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

for y, p in zip(yPositions, pressuresMPa):
    ax.text(p + max(pressuresMPa) * 0.015, y, f'{p:.2f}', va = 'center', ha = 'left',
             color = MUTED, fontsize = 8)

fig.tight_layout()

outPath = os.path.join(HERE, 'fluidSystemsLibrary', 'docs', 'images', 'pressureBudget.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[name, f'{p:.4f}', note] for name, p, note in [(s[0], s[1] / 1.0e6, s[2]) for s in stations]]
print(formatReportTable(rows, ['Station (upstream order)', 'P [MPa]', 'Note'], title = 'PLOTTED PRESSURE BUDGET'))
