
# -- Soakback Transient Figure Generator [thermalManagement] -- #

'''

Renders the avionics-node temperature history from both runs of the ascent soakback worked example:
a short run (stopped when the heat pulse ends) and a long run (carried until every node turns over).
`codeInterface.runTransient()` keeps both `ThermalNetwork` instances alive in its return value
specifically so the full time history is reachable, but only prints the peak table. This script
reads `network.history` directly rather than re-solving the transient.

Run it with:

    python generateSoakbackTransientPlot.py

Writes docs/images/soakbackTransient.png and prints the peak values plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'thermalManagementLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from thermalUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run Both Transients -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('thermalManagementSoakbackCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case        = ci.loadCase()
environment = ci.reportEnvironment(case)
protection  = ci.sizeProtection(case, environment)
transient   = ci.runTransient(case, environment, protection)

limit = case['structure']['avionicsLimit']

def avionicsTrace(run):
    network = transient[run]['network']
    history = network.history
    position = history['nodes'].index('avionics')
    return history['time'], history['temperatures'][:, position]

shortTime, shortTemp = avionicsTrace('short')
longTime,  longTemp  = avionicsTrace('long')

shortPeak = transient['short']['result']['peaks']['avionics']
longPeak  = transient['long']['result']['peaks']['avionics']

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

ax.plot(longTime, longTemp, color = BLUE, linewidth = 2.0,
        label = f'Long run ({case["transient"]["longRun"]:.0f} s, full soakback)')
ax.plot(shortTime, shortTemp, color = ACCENT, linewidth = 2.2,
        label = f'Short run ({case["transient"]["shortRun"]:.0f} s, stops at heating end)')

ax.axhline(limit, color = RED, linewidth = 1.2, linestyle = '--')
ax.text(longTime[-1] * 0.02, limit + 2.5, f'avionics limit {limit:.1f} K',
        color = RED, fontsize = 8.5, va = 'bottom')

ax.scatter([shortPeak['peakTime']], [shortPeak['peakTemperature']], color = ACCENT, s = 45, zorder = 5,
           edgecolor = BG, linewidth = 1.2)
ax.scatter([longPeak['peakTime']], [longPeak['peakTemperature']], color = BLUE, s = 45, zorder = 5,
           edgecolor = BG, linewidth = 1.2)

ax.annotate(f'{shortPeak["peakTemperature"]:.1f} K\n(still rising)',
            xy = (shortPeak['peakTime'], shortPeak['peakTemperature']),
            xytext = (-75, -18), textcoords = 'offset points', color = ACCENT, fontsize = 8.5)
ax.annotate(f'{longPeak["peakTemperature"]:.1f} K',
            xy = (longPeak['peakTime'], longPeak['peakTemperature']),
            xytext = (12, 4), textcoords = 'offset points', color = BLUE, fontsize = 8.5)

ax.set_ylim(285, 385)

ax.set_xlabel('Time [s]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Avionics node temperature [K]', color = MUTED, fontsize = 9.5)
ax.set_title('Avionics soakback: same model and hardware, two run lengths\none clears the limit, the other only because it stopped integrating early',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'lower right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'soakbackTransient.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [
    ['Short run', f'{case["transient"]["shortRun"]:.0f} s', f'{shortPeak["peakTemperature"]:.1f} K',
     f'{shortPeak["peakTime"]:.0f} s', 'yes' if transient['short']['result']['truncated'] else 'no'],
    ['Long run', f'{case["transient"]["longRun"]:.0f} s', f'{longPeak["peakTemperature"]:.1f} K',
     f'{longPeak["peakTime"]:.0f} s', 'yes' if transient['long']['result']['truncated'] else 'no'],
]
print(formatReportTable(rows, ['Run', 'Duration', 'Avionics peak', 'Peak time', 'Still rising'],
                        title = f'PLOTTED SOAKBACK TRANSIENT (limit {limit:.1f} K)'))
