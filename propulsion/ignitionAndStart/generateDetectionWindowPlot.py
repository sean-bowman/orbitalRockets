
# -- Detection Window Figure Generator [propulsion/ignitionAndStart] -- #

'''

Renders the chamber-accumulation detection window vs. start flow fraction. `codeInterface.
reportDetectionWindow()` prints this exact five-point sweep (1.0, 0.5, 0.30, 0.10, 0.05) but only
returns the full-flow case, not the series. This script replicates the loop directly against the
same `IgnitionSystem` class, using the residence time computed by `reportResidenceTime()`, rather
than re-deriving the chamber accumulation physics.

Run it with:

    python generateDetectionWindowPlot.py

Writes docs/images/detectionWindow.png and prints the swept fractions plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'ignitionAndStartLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ignitionUtils import formatReportTable
from IgnitionSystem import IgnitionSystem

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('ignitionAndStartDetectionWindowCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case      = ci.loadCase()
stage1    = ci.reportResidenceTime(case)
residence = stage1['accumulation']['residenceTime']
engine    = case['engine']

#--------------------------------------------------------------------------------------------------------------------------#
# -- Replicate the Five-Point Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

fractions = (1.0, 0.5, 0.30, 0.10, 0.05)
windows, canAct, detectionLatency = [], [], None

for fraction in fractions:
    trial = IgnitionSystem()
    trial.setInputs({'combination':       engine['combination'],
                     'startsRequired':    engine['startsRequired'],
                     'residenceTime':     residence,
                     'startFlowFraction': fraction})
    entry = trial.calculateDetectionWindow()
    windows.append(entry['window'] * 1000.0)
    canAct.append(entry['detectionCanAct'])
    detectionLatency = entry['detectionLatency'] * 1000.0

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

fractionsPct = [f * 100.0 for f in fractions]
colors = [GREEN if c else RED for c in canAct]

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(fractionsPct, windows, color = ACCENT, linewidth = 1.8, zorder = 3)
ax.scatter(fractionsPct, windows, color = colors, s = 55, zorder = 4, edgecolor = BG, linewidth = 1.0)

ax.axhline(detectionLatency, color = RED, linewidth = 1.1, linestyle = '--')
ax.text(fractionsPct[0] * 0.97, detectionLatency + max(windows) * 0.02,
        f'detection latency needed, {detectionLatency:.0f} ms', color = RED, fontsize = 8.5, ha = 'right')

for x, y in zip(fractionsPct, windows):
    ax.annotate(f'{y:.1f} ms', xy = (x, y), xytext = (0, 10), textcoords = 'offset points',
                color = MUTED, fontsize = 8, ha = 'center')

ax.set_xlabel('Start flow fraction of mainstage [%]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Accumulation window before two chamber-fulls [ms]', color = MUTED, fontsize = 9.5)
ax.set_title('Detection window vs. start flow fraction\ngreen: detection can act before hard start; red: it cannot',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'detectionWindow.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{f:.0%}', f'{w:.1f}', 'yes' if c else 'no'] for f, w, c in zip(fractions, windows, canAct)]
print(formatReportTable(rows, ['Start flow', 'Window [ms]', 'Detection can act'],
                        title = f'PLOTTED DETECTION WINDOW (latency needed {detectionLatency:.0f} ms)'))
