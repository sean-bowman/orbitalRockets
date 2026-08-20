
# -- Instrumentation Improvement Figure Generator [propulsion/propulsionTesting] -- #

'''

Renders c* uncertainty across instrumentation-improvement scenarios: as tested, each channel
improved individually, and both improved together. `codeInterface.reportImprovement()` already
computes every scenario through `PerformanceReduction.calculateUncertainty()` and returns the full
result set, so this script loads that function by explicit path and reads its returned dict directly.

This is a categorical comparison rather than a continuous sweep (the weakest chart candidate among
the six propulsion sub-domains, since nothing here is a swept continuous variable), so the figure is
a bar chart rather than a line.

Run it with:

    python generateInstrumentationImprovementPlot.py

Writes docs/images/instrumentationImprovement.png and prints the scenarios plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'propulsionTestingLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from propulsionTestUtils import formatReportTable
from HotFireTest import DISCRIMINATION_RATIO_FLOOR

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('propulsionTestingImprovementCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case    = ci.loadCase()
results = ci.reportImprovement(case)

labels       = list(results.keys())
uncertainty  = [results[label] * 100.0 for label in labels]
ratioAt1Pct  = [0.01 / results[label] for label in labels]

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
GREEN  = '#86C06C'
RED    = '#e08080'

colors = [GREEN if r >= DISCRIMINATION_RATIO_FLOOR else RED for r in ratioAt1Pct]

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

yPositions = np.arange(len(labels))
ax.barh(yPositions, uncertainty, color = colors, height = 0.6, edgecolor = 'none')

ax.set_yticks(yPositions)
ax.set_yticklabels(labels, color = TEXT, fontsize = 9.5)
ax.invert_yaxis()

for y, u, r in zip(yPositions, uncertainty, ratioAt1Pct):
    ax.text(u + max(uncertainty) * 0.015, y, f'{u:.2f}%  (ratio {r:.1f} at 1% band)', va = 'center',
            ha = 'left', color = MUTED, fontsize = 8)

ax.set_xlabel('u(c*) [%]', color = MUTED, fontsize = 9.5)
ax.set_title(f'c* uncertainty by instrumentation scenario\nred: below the {DISCRIMINATION_RATIO_FLOOR:.0f}x working floor to rank two injectors a point apart; green: at or above it',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.xaxis.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'instrumentationImprovement.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[label, f'{u:.2f}%', f'{r:.1f}'] for label, u, r in zip(labels, uncertainty, ratioAt1Pct)]
print(formatReportTable(rows, ['Scenario', 'u(c*)', 'Ratio at 1% band'],
                        title = f'PLOTTED INSTRUMENTATION IMPROVEMENT (floor {DISCRIMINATION_RATIO_FLOOR:.0f}x)'))
