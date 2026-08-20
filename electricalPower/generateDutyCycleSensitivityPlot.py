
# -- Duty Cycle Sensitivity Figure Generator [electricalPower] -- #

'''

Renders the propellant-line-heater duty-cycle sensitivity sweep from the upper-stage power budget
worked example. `codeInterface.reportBudget()` calls
`budget.dutyCycleSensitivity('propellant line heaters')`, which holds every other load fixed and
recomputes `PowerBudget.rollUp()['deliveredEnergy']` at duty cycles of 0.2, 0.4, 0.6, 0.8 and 1.0.
This script builds the same `PowerBudget` object and calls that same method directly, rather than
re-deriving the roll-up or scraping the printed table.

Run it with:

    python generateDutyCycleSensitivityPlot.py

Writes docs/images/dutyCycleSensitivity.png and prints the sweep plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'electricalPowerLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from powerUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('electricalPowerDutyCycleCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case   = ci.loadCase()
budget = ci.buildBudget(case)

rollup      = budget.rollUp()
heaterShare = rollup['byLoad']['propellant line heaters']['energy'] / rollup['deliveredEnergy']

sensitivity = budget.dutyCycleSensitivity('propellant line heaters')

duties        = np.array(sorted(sensitivity['results'].keys()))
energiesWattH = np.array([sensitivity['results'][duty] / 3600.0 for duty in duties])

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
GREEN  = '#86C06C'
YELLOW = '#d4b86a'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(duties * 100.0, energiesWattH, color = ACCENT, linewidth = 2.0, zorder = 3)
ax.scatter(duties * 100.0, energiesWattH, color = ACCENT, s = 45, zorder = 4,
           edgecolor = BG, linewidth = 1.2)

minIndex, maxIndex = int(np.argmin(energiesWattH)), int(np.argmax(energiesWattH))
ax.annotate(f'{energiesWattH[minIndex]:.1f} W h',
            xy = (duties[minIndex] * 100.0, energiesWattH[minIndex]),
            xytext = (10, -14), textcoords = 'offset points', color = MUTED, fontsize = 8.5)
ax.annotate(f'{energiesWattH[maxIndex]:.1f} W h',
            xy = (duties[maxIndex] * 100.0, energiesWattH[maxIndex]),
            xytext = (-55, 8), textcoords = 'offset points', color = MUTED, fontsize = 8.5)

ax.annotate('', xy = (duties[maxIndex] * 100.0 + 3.0, energiesWattH[maxIndex]),
            xytext = (duties[maxIndex] * 100.0 + 3.0, energiesWattH[minIndex]),
            arrowprops = dict(arrowstyle = '<->', color = YELLOW, linewidth = 1.2))
ax.text(duties[maxIndex] * 100.0 + 4.5, (energiesWattH[minIndex] + energiesWattH[maxIndex]) / 2.0,
        f'{sensitivity["spanFraction"]:.0%} span',
        color = YELLOW, fontsize = 8.5, ha = 'left', va = 'center', rotation = 90)

ax.set_xlim(duties[0] * 100.0 - 4.0, duties[-1] * 100.0 + 12.0)

ax.set_xlabel('Propellant line heater duty cycle [%]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Mission delivered energy [W h]', color = MUTED, fontsize = 9.5)
ax.set_title('Mission energy sensitivity to one thermal assumption\n'
             f'heater duty cycle is {heaterShare:.0%} of mission energy but swings the budget '
             f'{sensitivity["spanFraction"]:.0%}',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'dutyCycleSensitivity.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{duty:.0%}', f'{energy:.1f}'] for duty, energy in zip(duties, energiesWattH)]
print(formatReportTable(rows, ['Heater duty cycle', 'Mission energy [W h]'],
                        title = f'PLOTTED DUTY CYCLE SENSITIVITY (span {sensitivity["spanFraction"]:.0%} '
                                f'of baseline {sensitivity["baseline"] / 3600.0:.1f} W h)'))
