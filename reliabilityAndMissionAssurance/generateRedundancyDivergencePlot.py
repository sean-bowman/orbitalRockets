
# -- Redundancy Divergence Figure Generator [reliabilityAndMissionAssurance] -- #

'''

Renders system failure probability vs. redundant unit count from the worked example's common-cause
redundancy model, ideal against real on a log scale. `RedundancyAnalysis.unitSweep()` already
returns the full swept series, so this script loads the worked example's case by explicit path and
calls that method directly rather than re-deriving the beta-factor model.

Run it with:

    python generateRedundancyDivergencePlot.py

Writes docs/images/redundancyDivergence.png and prints the series plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'reliabilityAndMissionAssuranceLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from reliabilityUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('reliabilityRedundancyDivergenceCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case = ci.loadCase()
analysis = ci.buildRedundancy(case)

result = analysis.unitSweep()
sweep = result['sweep']

units          = [entry['units']         for entry in sweep]
systemFailure  = [entry['systemFailure'] for entry in sweep]
idealFailure   = [entry['idealFailure']  for entry in sweep]
commonCauseShare = [entry['commonCauseShare'] for entry in sweep]

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

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(units, systemFailure, color = RED, linewidth = 2.0, marker = 'o', markersize = 6,
        label = 'Q with common cause (real)')
ax.plot(units, idealFailure, color = GREEN, linewidth = 2.0, marker = 'o', markersize = 6,
        linestyle = '--', label = 'Q ideal (independent units)')
ax.set_yscale('log')

ax.annotate(f'{systemFailure[0]:.2e}, no redundancy yet', xy = (units[0], systemFailure[0]),
            xytext = (0, 12), textcoords = 'offset points', color = TEXT, fontsize = 7.5,
            ha = 'center')

for x, y in list(zip(units, systemFailure))[1:]:
    ax.annotate(f'{y:.2e}', xy = (x, y), xytext = (0, 9), textcoords = 'offset points',
                color = RED, fontsize = 7.5, ha = 'center')

for x, y in list(zip(units, idealFailure))[1:]:
    ax.annotate(f'{y:.2e}', xy = (x, y), xytext = (0, -14), textcoords = 'offset points',
                color = GREEN, fontsize = 7.5, ha = 'center')

ax.axvline(2, color = ACCENT, linewidth = 1.0, linestyle = ':', alpha = 0.8)
ax.text(2.15, 3.0e-4,
        f'common cause is {commonCauseShare[1] * 100.0:.0f}% of the dual-redundant Q',
        color = ACCENT, fontsize = 8.5, va = 'center', ha = 'left')

ax.set_xlabel('Redundant unit count', color = MUTED, fontsize = 9.5)
ax.set_ylabel('System failure probability, Q [-]', color = MUTED, fontsize = 9.5)
ax.set_title(f'Redundancy divergence: common-cause failure vs. an ideal count\nbeta = '
             f'{analysis.beta:.2f}, {case["redundancy"]["sharing"]}',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)
ax.set_xticks(units)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7, which = 'both')
ax.set_axisbelow(True)

ax.legend(loc = 'center right', fontsize = 8.5, facecolor = BG, edgecolor = BORDER, labelcolor = TEXT)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'redundancyDivergence.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{entry["units"]}', f'{entry["systemFailure"]:.3e}', f'{entry["idealFailure"]:.3e}',
         f'{entry["commonCauseShare"] * 100.0:.0f}%', f'{entry["marginalGain"] * 100.0:.0f}%']
        for entry in sweep]

print(formatReportTable(rows, ['Units', 'Q, common cause', 'Q, ideal', 'Common cause share',
                               'Marginal gain'],
                        title = f'PLOTTED REDUNDANCY DIVERGENCE (beta = {analysis.beta:.2f}, '
                                f'divergence by {result["idealDivergence"]:,.0f}x at 5 units)'))
