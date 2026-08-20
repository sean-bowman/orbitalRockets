
# -- Altitude Compensation Figure Generator [propulsion/nozzles] -- #

'''

Renders fixed-nozzle vs. ideal-compensating-nozzle specific impulse across the ascent altitude
profile. `codeInterface.reportCompensationLever()` already sweeps altitude and returns both profiles,
so this script loads that function by explicit path and reads its returned arrays directly rather
than re-deriving the compensation bound.

Run it with:

    python generateAltitudeCompensationPlot.py

Writes docs/images/altitudeCompensation.png and prints the swept profile plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'nozzlesLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from nozzleUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('nozzlesAltitudeCompensationCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case         = ci.loadCase()
compensation = ci.reportCompensationLever(case)

bound     = compensation['bound']
altitudes = np.asarray(case['ascent']['altitudes']) / 1000.0
fixed     = np.asarray(bound['fixedProfile'])
ideal     = np.asarray(bound['idealProfile'])
gaps      = np.asarray(compensation['gaps'])

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

ax.plot(altitudes, ideal, color = GREEN,  linewidth = 2.0, marker = 'o', markersize = 5, label = 'Ideal compensating nozzle')
ax.plot(altitudes, fixed, color = ACCENT, linewidth = 2.0, marker = 'o', markersize = 5, label = 'Fixed bell (this engine)')

ax.fill_between(altitudes, fixed, ideal, color = GREEN, alpha = 0.08)

narrowestIndex = int(np.argmin(gaps))
ax.annotate(f'near match, gap {gaps[narrowestIndex]:.2f} s\n({altitudes[narrowestIndex]:.0f} km, design altitude)',
            xy = (altitudes[narrowestIndex], fixed[narrowestIndex]), xytext = (10, -34),
            textcoords = 'offset points', color = MUTED, fontsize = 8.5)
ax.annotate(f'gap {gaps[-1]:.1f} s\n({gaps[-1] / gaps[0]:.0f}x sea level)',
            xy = (altitudes[-1], (fixed[-1] + ideal[-1]) / 2.0), xytext = (-95, 0),
            textcoords = 'offset points', color = GREEN, fontsize = 8.5, va = 'center')
ax.annotate(f'gap {gaps[0]:.1f} s (sea level)', xy = (altitudes[0], (fixed[0] + ideal[0]) / 2.0),
            xytext = (10, -14), textcoords = 'offset points', color = GREEN, fontsize = 8.5)

ax.set_xlabel('Altitude [km]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Specific impulse [s]', color = MUTED, fontsize = 9.5)
ax.set_title('Altitude compensation: fixed bell vs. the ideal\nnear-matched around this engine\'s design altitude, then the fixed bell saturates while the ideal keeps climbing',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'lower right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'altitudeCompensation.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{a:.0f}', f'{f:.2f}', f'{i:.2f}', f'{g:.2f}'] for a, f, i, g in zip(altitudes, fixed, ideal, gaps)]
print(formatReportTable(rows, ['Altitude [km]', 'Fixed [s]', 'Ideal [s]', 'Gap [s]'],
                        title = f'PLOTTED ALTITUDE COMPENSATION (bound {bound["benefit"]:.2f} s, {bound["benefitFraction"]:.1%})'))
