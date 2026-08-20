
# -- Area Ratio Sweep Figure Generator [propulsion] -- #

'''

Renders sea-level and burn-averaged specific impulse vs. nozzle area ratio for the 100 kN LOX/RP-1
booster worked example. `codeInterface.selectExpansion()` already sweeps area ratio from 6.0 to 40.0
in 0.25 steps (about 136 points) and returns the full series, but only prints the four named answers
as a table. This script loads that function by explicit path and reads its returned arrays directly.

Run it with:

    python generateAreaRatioSweepPlot.py

Writes docs/images/areaRatioSweep.png and prints the four named answers plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'propulsionLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from propulsionUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('propulsionAreaRatioCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case       = ci.loadCase()
propellant = ci.selectPropellant(case)
expansion  = ci.selectExpansion(case, propellant)

ratios          = np.asarray(expansion['ratios'])
seaLevelImpulse = np.asarray(expansion['seaLevelImpulse'])
averageImpulse  = np.asarray(expansion['averageImpulse'])
answers         = expansion['answers']

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

ax.plot(ratios, seaLevelImpulse, color = ACCENT, linewidth = 2.0, label = 'Sea-level Isp')
ax.plot(ratios, averageImpulse,  color = BLUE,   linewidth = 2.0, label = 'Burn-averaged Isp')

markerColors = {'sea level optimum': ACCENT, 'burn-average optimum': BLUE,
                'separation limit': RED, 'design point': GREEN}
markerY = {'sea level optimum': 'seaLevelImpulse', 'burn-average optimum': 'averageImpulse',
           'separation limit': 'averageImpulse', 'design point': 'averageImpulse'}
# The three burn-averaged points sit close together in area ratio (20.35, 21.42, 25.75), so each
# gets its own offset and horizontal alignment to keep the labels from overlapping.
labelOffsets = {'sea level optimum':     (0, 10, 'center'),
                'design point':         (-8, -20, 'right'),
                'separation limit':     (0, 14, 'center'),
                'burn-average optimum': (10, 10, 'left')}

for label, entry in answers.items():
    yKey = markerY[label]
    dx, dy, align = labelOffsets[label]
    ax.scatter([entry['areaRatio']], [entry[yKey]], color = markerColors[label], s = 45, zorder = 5,
               edgecolor = BG, linewidth = 1.0)
    ax.annotate(label, xy = (entry['areaRatio'], entry[yKey]), xytext = (dx, dy),
                textcoords = 'offset points', color = markerColors[label], fontsize = 7.8,
                ha = align)

ax.set_xlabel('Area ratio, $\\epsilon$', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Specific impulse [s]', color = MUTED, fontsize = 9.5)
ax.set_title('100 kN LOX/RP-1 booster: Isp vs. area ratio\nfour defensible answers to "what area ratio," none of them the naive one',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'lower center')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'areaRatioSweep.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[label, f'{entry["areaRatio"]:.2f}', f'{entry["seaLevelImpulse"]:.1f}',
         f'{entry["averageImpulse"]:.1f}', str(entry['separated'])] for label, entry in answers.items()]
print(formatReportTable(rows, ['Answer', 'eps', 'SL Isp [s]', 'Burn avg [s]', 'Separated'],
                        title = 'PLOTTED AREA RATIO SWEEP'))
