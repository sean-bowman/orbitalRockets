
# -- Learning Curve Figure Generator [manufacturingAndAssembly] -- #

'''

Renders unit cost vs. unit number from the tank barrel worked example's learning curve.
`ProductionRate.doublingSweep()` already returns the full doubling series (units 1, 2, 4, ... 64),
so this script loads the worked example's production model by explicit path and calls that method
directly rather than re-deriving Wright's curve. Unit 20, the worked example's run length, is not a
power of two and so is not one of the swept points; it is added from the same `unitCost()` and
`cumulativeCost()` calls `codeInterface.py` itself uses, so the callout is read off the model rather
than hand-computed.

Run it with:

    python generateLearningCurvePlot.py

Writes docs/images/learningCurve.png and prints the series plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'manufacturingLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from manufacturingUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('manufacturingLearningCurveCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case = ci.loadCase()
production = ci.buildProduction(case)

doublings = production.doublingSweep()
sweep = doublings['sweep']

runLength = case['production']['runLength']
cumulative = production.cumulativeCost(runLength)

units          = [entry['unit'] for entry in sweep]
fractionOfFirst = [entry['fractionOfFirst'] * 100.0 for entry in sweep]

runLengthFraction    = cumulative['lastUnitCost'] / cumulative['firstUnitCost'] * 100.0
cumulativeAverageFraction = cumulative['cumulativeAverage'] / cumulative['firstUnitCost'] * 100.0

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

ax.plot(units, fractionOfFirst, color = ACCENT, linewidth = 2.0, marker = 'o', markersize = 6,
        label = 'unit cost, doubling series')
ax.set_xscale('log', base = 2)

for x, y in zip(units, fractionOfFirst):
    ax.annotate(f'{y:.0f}%', xy = (x, y), xytext = (0, 9), textcoords = 'offset points',
                color = MUTED, fontsize = 7.5, ha = 'center')

ax.plot(runLength, runLengthFraction, color = GREEN, marker = 'D', markersize = 8, linestyle = 'None',
        label = f'unit {runLength}, actual run length')
ax.annotate(f'unit {runLength}: {runLengthFraction:.0f}% of first',
            xy = (runLength, runLengthFraction), xytext = (-15, -20), textcoords = 'offset points',
            color = GREEN, fontsize = 8.5, ha = 'right')

ax.axhline(cumulativeAverageFraction, color = YELLOW, linewidth = 1.0, linestyle = ':', alpha = 0.85)
ax.text(units[0], cumulativeAverageFraction + 2.0,
        f'cumulative average through unit {runLength}: {cumulativeAverageFraction:.0f}% of first',
        color = YELLOW, fontsize = 8.5, va = 'bottom')

ax.set_xticks(units)
ax.set_xticklabels([str(u) for u in units], color = TEXT)
ax.set_xlabel('Unit number (log scale)', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Unit cost [% of first unit]', color = MUTED, fontsize = 9.5)
ax.set_title(f'Learning curve, tank barrel weld station\n{production.learningRate:.2f} learning '
             f'rate, {case["production"]["processClass"]} process class',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)
ax.set_ylim(0.0, 105.0)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7, which = 'both')
ax.set_axisbelow(True)

ax.legend(loc = 'upper right', fontsize = 8, facecolor = BG, edgecolor = BORDER, labelcolor = TEXT)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'learningCurve.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{entry["unit"]}', f'{entry["unitCost"]:.3f}', f'{entry["fractionOfFirst"] * 100.0:.0f}%',
         f'{entry["savingFromPrevious"]:.3f}'] for entry in sweep]
rows.append([f'{runLength} (run length)', f'{cumulative["lastUnitCost"]:.3f}',
            f'{runLengthFraction:.0f}%', f'cumulative avg {cumulative["cumulativeAverage"]:.3f} '
            f'({cumulativeAverageFraction:.0f}% of first)'])

print(formatReportTable(rows, ['Unit', 'Unit cost', 'Of first', 'Saving from previous doubling'],
                        title = f'PLOTTED LEARNING CURVE ({production.learningRate:.2f} learning '
                                f'rate, {case["production"]["processClass"]})'))
