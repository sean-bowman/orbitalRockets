
# -- Spring Count Sweep Figure Generator [mechanismsAndSeparation] -- #

'''

Renders the separation spring count comparison from the stage separation worked example.
`codeInterface.reportSeparation()` calls `system.compareSpringCounts(case['separation']
['springCountsTried'])`, which holds the total stored energy constant and redistributes it across
2, 4, 6, 8 and 12 springs, recomputing the deterministic worst-case tipoff and the statistical
(root-sum-square) tipoff at each count. This script builds the same `SeparationSystem` object and
calls that same method directly, rather than re-deriving the tipoff mechanics or scraping the
printed table.

Run it with:

    python generateSpringCountSweepPlot.py

Writes docs/images/springCountSweep.png and prints the sweep plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'mechanismsAndSeparationLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mechanismUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('mechanismsSpringCountCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case   = ci.loadCase()
system = ci.buildSeparation(case)

counts = system.compareSpringCounts(case['separation']['springCountsTried'])

springCounts     = np.array(sorted(counts['results'].keys()))
worstCaseTipoff  = np.array([counts['results'][count]['tipoff']      for count in springCounts])
statisticalTipoff = np.array([counts['results'][count]['statistical'] for count in springCounts])

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
BLUE   = '#7baee8'
RED    = '#e08080'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(springCounts, worstCaseTipoff, color = RED, linewidth = 2.0, marker = 'o', markersize = 6,
        label = 'Deterministic worst case (flat)')
ax.plot(springCounts, statisticalTipoff, color = BLUE, linewidth = 2.0, marker = 'o', markersize = 6,
        label = 'Statistical, RSS (falls as 1/sqrt(n))')

ax.annotate(f'{worstCaseTipoff[0]:.4f} deg/s, unchanged',
            xy = (springCounts[-1], worstCaseTipoff[-1]), xytext = (-10, 10),
            textcoords = 'offset points', color = RED, fontsize = 8.5, ha = 'right')
ax.annotate(f'{statisticalTipoff[-1]:.4f} deg/s',
            xy = (springCounts[-1], statisticalTipoff[-1]), xytext = (-10, -16),
            textcoords = 'offset points', color = BLUE, fontsize = 8.5, ha = 'right')

ax.set_xlabel('Number of separation springs (total stored energy held constant)', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Tipoff rate [deg/s]', color = MUTED, fontsize = 9.5)
ax.set_title('Separation tipoff vs. spring count, constant stored energy\n'
             'the worst-case bound does not move; only the statistical estimate improves',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

ax.set_xticks(springCounts)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

legend = ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'center right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'springCountSweep.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{count:d}', f'{counts["results"][count]["stiffness"]:.0f}',
        f'{counts["results"][count]["velocity"]:.3f}', f'{worst:.4f}', f'{statistical:.4f}']
        for count, worst, statistical in zip(springCounts, worstCaseTipoff, statisticalTipoff)]
print(formatReportTable(rows, ['Springs', 'Stiffness [N/m]', 'Velocity [m/s]',
                               'Worst case [deg/s]', 'Statistical [deg/s]'],
                        title = f'PLOTTED SPRING COUNT SWEEP (worst case flat: {counts["worstCaseIsFlat"]})'))
