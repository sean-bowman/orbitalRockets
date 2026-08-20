
# -- Expander Ceiling Figure Generator [propulsion/engineCycles] -- #

'''

Renders jacket heat, pump power, and available power vs. chamber pressure for the expander-cycle
heat-balance check. `codeInterface.expanderCeiling()` already sweeps chamber pressure across the
seven points in the JSON asset and returns every row, so this script loads that function by explicit
path and reads its returned rows directly rather than re-deriving the heat balance.

Run it with:

    python generateExpanderCeilingPlot.py

Writes docs/images/expanderCeiling.png and prints the swept rows plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'engineCyclesLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from cycleUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('engineCyclesExpanderCeilingCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case     = ci.loadCase()
expander = ci.expanderCeiling(case)
rows     = expander['rows']

pressuresMPa = [row['pressure'] / 1.0e6 for row in rows]
jacketMW     = [row['jacket']    / 1.0e6 for row in rows]
pumpMW       = [row['pumpPower'] / 1.0e6 for row in rows]
availableMW  = [row['available'] / 1.0e6 for row in rows]
closes       = [row['closes'] for row in rows]

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
BLUE   = '#7baee8'
GREEN  = '#86C06C'
RED    = '#e08080'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Pump power and available power (after turbine losses) sit on the same 0-1.3 MW scale, where the
# actual closing/failing crossover lives. Jacket heat is thermal energy at the chamber wall, roughly
# an order of magnitude larger, so it gets its own axis rather than swamping the story.
ax.plot(pressuresMPa, pumpMW,      color = BLUE,  linewidth = 2.0, marker = 'o', markersize = 5, label = 'Pump power required')
ax.plot(pressuresMPa, availableMW, color = GREEN, linewidth = 2.0, marker = 's', markersize = 5, label = 'Available shaft power')

if expander['ceiling'] and expander['firstFailure']:
    ceilingMPa = expander['ceiling'] / 1.0e6
    failMPa    = expander['firstFailure'] / 1.0e6
    ax.axvspan(ceilingMPa, failMPa, color = RED, alpha = 0.12)
    ax.text((ceilingMPa + failMPa) / 2.0, max(pumpMW) * 0.95, f'ceiling\n{ceilingMPa:.1f}-{failMPa:.1f} MPa',
            color = RED, fontsize = 8, ha = 'center', va = 'top')

ax.axvline(4.4, color = MUTED, linewidth = 1.0, linestyle = ':', alpha = 0.8)
ax.text(4.55, min(pumpMW) + 0.02, 'RL10: 4.4 MPa', color = MUTED, fontsize = 8, va = 'bottom', ha = 'left')

ax.set_xlabel('Chamber pressure [MPa]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Shaft power [MW]', color = MUTED, fontsize = 9.5)
ax.set_title('Expander cycle heat balance vs. chamber pressure\npump power crosses available shaft power; jacket heat (right axis) barely moves',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

axRight = ax.twinx()
axRight.plot(pressuresMPa, jacketMW, color = ACCENT, linewidth = 1.4, linestyle = '--', label = 'Jacket heat available')
axRight.set_ylabel('Jacket heat [MW]', color = ACCENT, fontsize = 9.5)
axRight.tick_params(axis = 'y', colors = ACCENT, labelsize = 8.5)
axRight.set_ylim(0, max(jacketMW) * 1.15)
for spine in axRight.spines.values():
    spine.set_color(BORDER)

linesLeft, labelsLeft   = ax.get_legend_handles_labels()
linesRight, labelsRight = axRight.get_legend_handles_labels()
ax.legend(linesLeft + linesRight, labelsLeft + labelsRight, frameon = False, fontsize = 9,
          labelcolor = TEXT, loc = 'center left', bbox_to_anchor = (0.02, 0.62))

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'expanderCeiling.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

tableRows = [[f'{p:.1f}', f'{j:.2f}', f'{pw:.3f}', f'{a:.3f}', 'yes' if c else 'NO']
             for p, j, pw, a, c in zip(pressuresMPa, jacketMW, pumpMW, availableMW, closes)]
print(formatReportTable(tableRows, ['Pc [MPa]', 'Jacket [MW]', 'Pump [MW]', 'Available [MW]', 'Closes'],
                        title = 'PLOTTED EXPANDER CEILING'))
