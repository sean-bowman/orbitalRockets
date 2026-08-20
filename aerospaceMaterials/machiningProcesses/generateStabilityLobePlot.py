
# -- Chatter Stability Lobe Figure Generator [machiningProcesses] -- #

'''

Renders the classic machining stability lobe diagram: achievable axial depth of cut against spindle
speed, for a Ti-6Al-4V end mill cut on the class's default flexible mode.

    a_lim = -1 / (2 K_s Re[G(omega)]_min)                  unconditional stability limit
    N_lobe = 60 f_n / (z * lobeNumber)                     each lobe's centre speed

Below the unconditional limit the cut is stable at any spindle speed. Above it, stability only
returns at spindle speeds where the tooth passing frequency divides the natural frequency evenly:
CHATTER_LOBE_COUNT = 6 such lobes are computed, and MachiningProcess.py's own docstring calls out
that running in the lowest (widest, highest speed) lobe is often the difference between a 1 mm and a
5 mm cut at no added cost.

The scenario, material, natural frequency (800 Hz), modal stiffness (2.0e7 N/m), damping ratio
(0.03), tool diameter (12 mm) and end mill geometry (4 teeth) are all MachiningProcess's own class
defaults, and the material/axial-depth pairing is exactly
machiningProcesses/tests/testMachiningProcesses.py::testStabilityLobesRaiseTheAchievableDepth
(material = 'Ti-6Al-4V', condition = 'annealed', axialDepth = 0.001 m), which asserts every lobe's
achievable depth exceeds the unconditional limit and that the lowest lobe is both the widest gain and
the highest spindle speed.

Every point plotted comes from a single call to MachiningProcess.calculateStabilityLobes(); no lobe
geometry is derived independently in this script.

Run it with:

    python generateStabilityLobePlot.py

Writes docs/images/stabilityLobeDiagram.png and prints the six lobes.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'machiningProcessesLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from machiningUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from MachiningProcess import MachiningProcess

#--------------------------------------------------------------------------------------------------#
# -- The validated scenario: Ti-6Al-4V end mill, default flexible mode -- #
#--------------------------------------------------------------------------------------------------#

machining = MachiningProcess()
machining.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed', 'axialDepth': 0.001})
result = machining.calculateStabilityLobes()

lobes = result['lobes']
criticalDepth = result['criticalDepthOfCut']

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

speedsRpm = np.array([lobe['spindleSpeedRpm'] for lobe in lobes])
depthsMm  = np.array([lobe['achievableDepth'] * 1.0e3 for lobe in lobes])
maxSpeed  = speedsRpm.max() * 1.10

# Unconditionally stable region, below the critical depth at any speed
ax.axhspan(0.0, criticalDepth * 1.0e3, color = GREEN, alpha = 0.12, linewidth = 0)
ax.axhline(criticalDepth * 1.0e3, color = GREEN, linewidth = 1.1, linestyle = '--', alpha = 0.85)
ax.text(maxSpeed * 0.98, criticalDepth * 1.0e3 - 0.15,
        f'unconditional stability limit ({criticalDepth * 1.0e3:.2f} mm)', color = GREEN,
        fontsize = 8.0, ha = 'right', va = 'top')

# Each lobe: a stem from the critical depth up to the achievable depth at its centre speed, which is
# exactly what calculateStabilityLobes() computes -- a discrete set of favourable operating points
# rather than a continuously interpolated boundary.
for lobe in lobes:
    speed = lobe['spindleSpeedRpm']
    depth = lobe['achievableDepth'] * 1.0e3
    ax.plot([speed, speed], [criticalDepth * 1.0e3, depth], color = ACCENT, linewidth = 1.6, alpha = 0.85)
    ax.scatter([speed], [depth], color = ACCENT, s = 40, zorder = 5, edgecolor = BG, linewidth = 1.0)
    ax.text(speed, depth + 0.15, f'lobe {lobe["lobeNumber"]}', color = TEXT, fontsize = 7.6,
            ha = 'center')

ax.plot(speedsRpm, depthsMm, color = ACCENT, linewidth = 1.0, alpha = 0.5, linestyle = ':')

# The commanded operating point from the test
ax.axvline(result['currentSpindleSpeedRpm'], color = MUTED, linewidth = 0.9, linestyle = ':', alpha = 0.7)
ax.text(result['currentSpindleSpeedRpm'] + 150.0, depthsMm.max() * 0.95,
        f'commanded speed\n{result["currentSpindleSpeedRpm"]:.0f} rpm\n'
        f'(0.60 m/s surface speed)', color = MUTED, fontsize = 7.6, ha = 'left', va = 'top')

ax.set_xlim(0.0, maxSpeed)
ax.set_ylim(0.0, depthsMm.max() * 1.20)
ax.set_xlabel('Spindle speed [rev/min]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Axial depth of cut [mm]', color = MUTED, fontsize = 9.5)
ax.set_title('Chatter stability lobes, Ti-6Al-4V end mill\n'
             '4-tooth cutter, 800 Hz mode, zeta = 0.03, 12 mm tool diameter',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'stabilityLobeDiagram.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

rows = [[f'{lobe["lobeNumber"]}', f'{lobe["spindleSpeedRpm"]:.0f}', f'{lobe["gain"]:.2f}',
         f'{lobe["achievableDepth"] * 1.0e3:.2f}'] for lobe in lobes]

print(formatReportTable(
    rows, ['Lobe #', 'Spindle speed [rpm]', 'Gain over critical [-]', 'Achievable depth [mm]'],
    title = 'PLOTTED STABILITY LOBES, TI-6AL-4V END MILL'))

print(f'\nUnconditional stability limit: {criticalDepth * 1.0e3:.3f} mm (stable at ANY spindle speed)')
print(f'Commanded operating point: {result["currentSpindleSpeedRpm"]:.0f} rpm, '
      f'{"in" if result["runningInLobe"] else "not in"} a lobe')

print('\nInput provenance: machiningProcesses/machiningProcessesLibrary/MachiningProcess.py class')
print('defaults (naturalFrequency = 800 Hz, modalStiffness = 2.0e7 N/m, dampingRatio = 0.03,')
print('toolDiameter = 0.012 m, process = end mill / 4 teeth, CHATTER_LOBE_COUNT = 6) and')
print('machiningProcesses/tests/testMachiningProcesses.py::testStabilityLobesRaiseTheAchievableDepth')
print('(material = Ti-6Al-4V, condition = annealed, axialDepth = 0.001 m).')
