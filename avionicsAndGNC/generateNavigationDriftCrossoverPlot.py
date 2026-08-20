
# -- Navigation Drift Crossover Figure Generator [avionicsAndGNC] -- #

'''

Renders the accelerometer-bias vs. gyro-bias-through-tilt position error crossover from the ascent
navigation worked example. `codeInterface.reportNavigation()` prints this comparison at five
discrete times, but `NavigationDrift.identifyCrossover()` already computes the full continuous
sweep (both terms, 400 points from 1 s to flight duration) and returns where the gyro term
overtakes the accelerometer term. This script calls that method directly and plots its returned
arrays, rather than re-deriving the error terms or scraping the printed table.

Run it with:

    python generateNavigationDriftCrossoverPlot.py

Writes docs/images/navigationDriftCrossover.png and prints the sweep plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'avionicsLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from avionicsUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Crossover Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('avionicsNavigationDriftCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case       = ci.loadCase()
navigation = ci.buildNavigation(case)

crossover = navigation.identifyCrossover(upper = case['flight']['duration'])

times     = crossover['times']
accelTerm = crossover['accelTerm']
gyroTerm  = crossover['gyroTerm']
tCross    = crossover['crossover']

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

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(times, accelTerm, color = ACCENT, linewidth = 2.0, label = 'Accelerometer bias (grows as t^2)')
ax.plot(times, gyroTerm,  color = BLUE,   linewidth = 2.0, label = 'Gyro bias through tilt (grows as t^3)')
ax.set_xscale('log')
ax.set_yscale('log')

if tCross is not None:
    crossLevel = float(np.interp(tCross, times, accelTerm))
    ax.axvline(tCross, color = GREEN, linewidth = 1.1, linestyle = '--', zorder = 2)
    ax.scatter([tCross], [crossLevel], color = GREEN, s = 55, zorder = 5, edgecolor = BG, linewidth = 1.2)
    ax.annotate(f'crossover {tCross:.0f} s',
                xy = (tCross, crossLevel), xytext = (10, -22), textcoords = 'offset points',
                color = GREEN, fontsize = 9)

ax.set_xlabel('Time since liftoff [s] (log scale)', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Position error contribution [m] (log scale)', color = MUTED, fontsize = 9.5)
ax.set_title('Navigation drift: which sensor error dominates\n'
             'gyro bias through tilt overtakes accelerometer bias early in a launch vehicle flight',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, which = 'both', color = BORDER, alpha = 0.35, linewidth = 0.6)
ax.set_axisbelow(True)

legend = ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'upper left')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'navigationDriftCrossover.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

sampleTimes = [30.0, 60.0, 120.0, 300.0, case['flight']['duration']]
rows = []
for t in sampleTimes:
    entry = navigation.calculateDrift(t)
    rows.append([f'{t:.0f}', f'{entry["terms"]["accelerometer bias"]:.4f}',
                f'{entry["terms"]["gyro bias through tilt"]:.4f}'])

print(formatReportTable(rows, ['Time [s]', 'Accelerometer bias [m]', 'Gyro bias through tilt [m]'],
                        title = f'PLOTTED NAVIGATION DRIFT CROSSOVER (crossover at {tCross:.1f} s)'))
