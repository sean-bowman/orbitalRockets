
# -- Film Cooling Sweep Figure Generator [propulsion/combustionDevices] -- #

'''

Renders coolant outlet temperature vs. film-cooling fraction for the 100 kN chamber that cannot be
regeneratively cooled by its own fuel alone. `codeInterface.sizeFilmCooling()` already sweeps every
film fraction in the JSON asset and returns the full result set, so this script loads the worked
example by explicit path and reads the returned dict directly rather than re-deriving the heat
balance.

Run it with:

    python generateFilmCoolingPlot.py

Writes docs/images/filmCooling.png and prints the swept fractions plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'combustionDevicesLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from combustionUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('combustionDevicesFilmCoolingCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case       = ci.loadCase()
loadResult = ci.computeHeatLoad(case)
capability = ci.checkClosure(case, loadResult)
filmResult = ci.sizeFilmCooling(case, loadResult, capability)

fractions = sorted(filmResult['results'].keys())
outlet    = [filmResult['results'][f]['outlet'] for f in fractions]
closes    = [filmResult['results'][f]['closes'] for f in fractions]
limit     = capability['limit']

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

fractionsPct = [f * 100.0 for f in fractions]
colors = [GREEN if c else RED for c in closes]

ax.plot(fractionsPct, outlet, color = ACCENT, linewidth = 1.6, zorder = 3)
ax.scatter(fractionsPct, outlet, color = colors, s = 45, zorder = 4, edgecolor = BG, linewidth = 1.0)

ax.axhline(limit, color = RED, linewidth = 1.1, linestyle = '--')
ax.text(fractionsPct[-1] * 0.98, limit + (max(outlet) - min(outlet)) * 0.02,
        f'coolant limit {limit:.0f} K', color = RED, fontsize = 8.5, ha = 'right', va = 'bottom')

if filmResult['chosen'] is not None:
    chosenPct = filmResult['chosen'] * 100.0
    ax.axvline(chosenPct, color = GREEN, linewidth = 1.0, linestyle = ':', alpha = 0.8)
    ax.text(chosenPct + 0.3, min(outlet), f'closes at {chosenPct:.0f}%', color = GREEN, fontsize = 8.5,
            rotation = 90, va = 'bottom')

ax.set_xlabel('Film cooling fraction of fuel flow [%]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Coolant outlet temperature [K]', color = MUTED, fontsize = 9.5)
ax.set_title('Film cooling fraction vs. coolant outlet temperature\ngreen closes the regenerative circuit within the coolant limit, red does not',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'filmCooling.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{f * 100.0:.0f}%', f'{filmResult["results"][f]["removed"] * 100.0:.0f}%',
         f'{filmResult["results"][f]["outlet"]:.0f}', 'yes' if filmResult['results'][f]['closes'] else 'NO']
        for f in fractions]
print(formatReportTable(rows, ['Film fraction', 'Load removed', 'Outlet [K]', 'Closes'],
                        title = f'PLOTTED FILM COOLING SWEEP (limit {limit:.0f} K, chosen {filmResult["chosen"]})'))
