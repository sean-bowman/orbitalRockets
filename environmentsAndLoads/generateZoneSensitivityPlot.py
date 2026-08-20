
# -- Zone Sensitivity Figure Generator [environmentsAndLoads] -- #

'''

Renders the random-vibration zone sensitivity sweep from the component-environment-derivation
worked example. `codeInterface.deriveEnvironment()` builds a `RandomVibrationSpec` normalised onto
the maximum-predicted level derived from six flights, and `zoneSensitivity()` walks it through six
mounting zones with `spec.applyZone(zone)`. This script calls the same two functions directly and
reads `applyZone()`'s returned Grms per zone, rather than re-deriving the spectrum or scraping the
printed table.

Run it with:

    python generateZoneSensitivityPlot.py

Writes docs/images/zoneSensitivity.png and prints the zone table plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'environmentsAndLoadsLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from environmentsUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Derive the Zone Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('environmentsZoneSensitivityCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case    = ci.loadCase()
derived = ci.deriveEnvironment(case)
vibSpec = derived['spec']

zones = ('engine compartment', 'aft skirt', 'tank barrel',
         'forward skirt', 'payload bay', 'isolated payload')

results = [vibSpec.applyZone(zone) for zone in zones]

grmsValues   = np.array([result['grms'] for result in results])
factors      = np.array([result['factor'] for result in results])
offsets      = np.array([result['offsetDecibels'] for result in results])

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
GREEN  = '#86C06C'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

xPositions = np.arange(len(zones))
colors     = [ACCENT if i < len(zones) - 1 else GREEN for i in range(len(zones))]

ax.bar(xPositions, grmsValues, color = colors, width = 0.6, edgecolor = 'none')
ax.set_yscale('log')

ax.set_xticks(xPositions)
ax.set_xticklabels([zone.replace(' ', '\n') for zone in zones], color = TEXT, fontsize = 8.5)
ax.set_ylabel('Overall level [Grms] (log scale)', color = MUTED, fontsize = 9.5)
ax.set_title('Random-vibration zone sensitivity, same derived spectrum\n'
             f'engine compartment to isolated payload spans {grmsValues[0] / grmsValues[-1]:.0f}x '
             f'({offsets[0] - offsets[-1]:+.1f} dB)',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.yaxis.grid(True, which = 'both', color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

for x, g in zip(xPositions, grmsValues):
    ax.text(x, g * 1.08, f'{g:.2f}', ha = 'center', va = 'bottom', color = MUTED, fontsize = 8.5)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'zoneSensitivity.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[zone, f'{factor:.1f}', f'{offset:+.1f}', f'{grms:.2f}']
        for zone, factor, offset, grms in zip(zones, factors, offsets, grmsValues)]
print(formatReportTable(rows, ['Zone', 'Factor', 'Offset [dB]', 'Grms'],
                        title = 'PLOTTED ZONE SENSITIVITY SWEEP'))
