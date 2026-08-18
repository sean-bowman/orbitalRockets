
# -- Shaft Speed Sweep Figure Generator [propulsion/turbomachinery] -- #

'''

Renders the open-cycle vs. closed-cycle total mass curves from the turbopump shaft-speed worked
example. `codeInterface.sweepShaftSpeed()` already computes the full swept series (16,000 to
66,000 rpm, 1,000 rpm steps) and returns it, so this script loads that function by explicit path and
calls it directly rather than re-deriving the sweep or scraping the printed table.

Run it with:

    python generateShaftSpeedPlot.py

Writes docs/images/shaftSpeedSweep.png and prints the series it plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'turbomachineryLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from turbomachineryUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('turbomachineryShaftSpeedCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case  = ci.loadCase()
sweep = ci.sweepShaftSpeed(case)

results    = sweep['results']
openBest   = sweep['openBest']
closedBest = sweep['closedBest']

speeds       = np.array([r['shaftSpeed']  for r in results])
openTotals   = np.array([r['openTotal']   for r in results])
closedTotals = np.array([r['closedTotal'] for r in results])

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
BLUE   = '#7baee8'
YELLOW = '#d4b86a'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(speeds / 1000.0, openTotals,   color = ACCENT, linewidth = 2.0, label = 'Open cycle total mass')
ax.plot(speeds / 1000.0, closedTotals, color = BLUE,   linewidth = 2.0, label = 'Closed cycle total mass')

ax.scatter([openBest['shaftSpeed'] / 1000.0], [openBest['openTotal']],
           color = ACCENT, s = 45, zorder = 5, edgecolor = BG, linewidth = 1.2)
ax.scatter([closedBest['shaftSpeed'] / 1000.0], [closedBest['closedTotal']],
           color = BLUE, s = 45, zorder = 5, edgecolor = BG, linewidth = 1.2)

ax.annotate(f'open optimum\n{openBest["shaftSpeed"]:.0f} rpm',
            xy = (openBest['shaftSpeed'] / 1000.0, openBest['openTotal']),
            xytext = (8, 14), textcoords = 'offset points', color = ACCENT, fontsize = 8.5)
ax.annotate(f'closed optimum\n{closedBest["shaftSpeed"]:.0f} rpm',
            xy = (closedBest['shaftSpeed'] / 1000.0, closedBest['closedTotal']),
            xytext = (14, 22), textcoords = 'offset points', color = BLUE, fontsize = 8.5)

ax.set_xlabel('Shaft speed [krpm]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Total mass [kg]', color = MUTED, fontsize = 9.5)
ax.set_title('Turbopump shaft speed: tank + turbopump + dumped-flow mass\nopen vs. closed engine cycle, same pumps',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

legend = ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'upper right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'shaftSpeedSweep.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [
    ['Open cycle optimum',   f'{openBest["shaftSpeed"]:.0f} rpm',   f'{openBest["openTotal"]:.1f} kg'],
    ['Closed cycle optimum', f'{closedBest["shaftSpeed"]:.0f} rpm', f'{closedBest["closedTotal"]:.1f} kg'],
    ['Ratio of optimum speeds', f'{openBest["shaftSpeed"] / closedBest["shaftSpeed"]:.2f}', ''],
]
print(formatReportTable(rows, ['Quantity', 'Speed', 'Mass'], title = 'PLOTTED SHAFT SPEED SWEEP'))
