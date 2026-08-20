
# -- Launch Availability Sweep Figure Generator [groundSystemsAndOperations] -- #

'''

Renders cumulative campaign launch probability vs. attempt count from the six-launch-commit-
criteria worked example. `LaunchAvailability.attemptSweep()` already returns the full swept series
and the attempt counts needed to cross 90/95/99 per cent, so this script loads the worked example's
case and attempt count by explicit path and calls that method directly rather than re-deriving the
combined go probability.

Run it with:

    python generateLaunchAvailabilitySweepPlot.py

Writes docs/images/launchAvailabilitySweep.png and prints the series plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'groundSystemsLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from groundUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('groundSystemsAvailabilitySweepCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case = ci.loadCase()

timeline = ci.buildTimeline(case)
attemptsInfo = timeline.attemptsPerCampaign(case['countdown']['campaignDuration'])

availability = ci.buildAvailability(case, attemptsInfo['attempts'])
result = availability.attemptSweep()
sweep = result['sweep']
thresholds = result['thresholds']

attempts   = [entry['attempts']   for entry in sweep]
cumulative = [entry['cumulative'] * 100.0 for entry in sweep]
marginal   = [entry['marginal']   * 100.0 for entry in sweep]

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

ax.plot(attempts, cumulative, color = ACCENT, linewidth = 2.0, marker = 'o', markersize = 6,
        label = 'cumulative go probability')

axRight = ax.twinx()
axRight.bar(attempts, marginal, color = GREEN, alpha = 0.35, width = 0.5,
            label = 'marginal gain, this attempt')
axRight.set_ylabel('Marginal gain [percentage points]', color = MUTED, fontsize = 9.5)
axRight.tick_params(colors = MUTED, labelsize = 8.5)
for spine in axRight.spines.values():
    spine.set_color(BORDER)

thresholdColors = {0.90: GREEN, 0.95: YELLOW, 0.99: ACCENT}
for level, needed in thresholds.items():
    if needed is None:
        continue
    color = thresholdColors.get(level, MUTED)
    ax.axvline(needed, color = color, linewidth = 1.0, linestyle = ':', alpha = 0.8)
    ax.text(needed + 0.08, 8.0, f'{level * 100.0:.0f}% at {needed}',
            color = color, fontsize = 8, rotation = 90, va = 'bottom', ha = 'left')

ax.set_xlabel('Launch attempts in the campaign', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Cumulative go probability [%]', color = MUTED, fontsize = 9.5)
ax.set_title('Campaign launch probability vs. attempt count\nsix launch commit criteria, independent attempts',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)
ax.set_ylim(0.0, 105.0)
ax.set_xticks(attempts)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

lines, labels = ax.get_legend_handles_labels()
barsHandles, barsLabels = axRight.get_legend_handles_labels()
legend = ax.legend(lines + barsHandles, labels + barsLabels, loc = 'lower right', fontsize = 8,
                    facecolor = BG, edgecolor = BORDER, labelcolor = TEXT)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'launchAvailabilitySweep.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{entry["attempts"]}', f'{entry["cumulative"] * 100.0:.1f}%', f'{entry["marginal"] * 100.0:.1f}%']
        for entry in sweep]

thresholdLine = ', '.join(f'{level * 100.0:.0f}% at {needed}' for level, needed in thresholds.items()
                          if needed is not None)

print(formatReportTable(rows, ['Attempts', 'Cumulative', 'Marginal gain'],
                        title = f'PLOTTED LAUNCH AVAILABILITY SWEEP ({thresholdLine})'))
