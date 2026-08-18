
# -- Pressure-Fed Sizing Sweep Figure Generator [vehicleArchitecture] -- #

'''

Renders liftoff mass vs. tank pressure from the worked example's pump-fed-to-pressure-fed
comparison. `codeInterface.reportPressureFed()` closes `SizingLoop` at each of five tank pressures
and returns the closed result (or None where the loop does not converge), so this script loads that
function by explicit path and calls it directly rather than re-closing the sizing loop itself.

Run it with:

    python generatePressureFedSizingPlot.py

Writes docs/images/pressureFedSizing.png and prints the points plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'vehicleArchitectureLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from vehicleUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example and Run the Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('vehicleArchitecturePressureFedCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case    = ci.loadCase()
results = ci.reportPressureFed(case)

pressures = list(results.keys())
closedPressuresMPa = [p / 1.0e6 for p in pressures if results[p] is not None]
liftoffTonnes       = [results[p]['liftoffMass'] / 1000.0 for p in pressures if results[p] is not None]
openPressuresMPa    = [p / 1.0e6 for p in pressures if results[p] is None]

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
RED    = '#e08080'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

order = np.argsort(closedPressuresMPa)
xs = np.array(closedPressuresMPa)[order]
ys = np.array(liftoffTonnes)[order]
ax.plot(xs, ys, color = ACCENT, linewidth = 2.0, marker = 'o', markersize = 6)

for x, y in zip(xs, ys):
    ax.annotate(f'{y:.1f} t', xy = (x, y), xytext = (0, 9), textcoords = 'offset points',
                color = MUTED, fontsize = 8, ha = 'center')

if openPressuresMPa:
    for x in openPressuresMPa:
        ax.axvline(x, color = RED, linewidth = 1.0, linestyle = ':', alpha = 0.7)
        ax.text(x, ax.get_ylim()[0], 'does not close', color = RED, fontsize = 7.5,
                rotation = 90, va = 'bottom', ha = 'right')

ax.set_xlabel('Tank pressure [MPa]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Liftoff mass [t]', color = MUTED, fontsize = 9.5)
ax.set_title('Liftoff mass vs. tank pressure, same payload\npump-fed baseline through a fully pressure-fed limit',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'pressureFedSizing.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = []
for pressure in pressures:
    closed = results[pressure]
    if closed is None:
        rows.append([f'{pressure / 1.0e6:.2f}', 'does not close', '', ''])
    else:
        rows.append([f'{pressure / 1.0e6:.2f}',
                     f'{closed["tanks"][0]["wallThickness"] * 1000.0:.2f}',
                     f'{closed["coefficients"][0]:.4f}',
                     f'{closed["liftoffMass"] / 1000.0:.1f}'])

print(formatReportTable(rows, ['Tank P [MPa]', 'Wall [mm]', 'Struct coeff', 'Liftoff [t]'],
                        title = 'PLOTTED PRESSURE-FED SIZING SWEEP'))
