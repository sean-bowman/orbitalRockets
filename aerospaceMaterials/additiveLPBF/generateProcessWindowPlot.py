
# -- LPBF Process Window Figure Generator [additiveLPBF] -- #

'''

Renders melt pool depth-to-layer ratio and normalised enthalpy against laser power, 60 to 900 W, at
the scan speed, hatch spacing, layer thickness and beam diameter of a validated Inconel 718
production parameter set.

The anchor point is 285 W at 0.960 m/s, which LpbfProcess.py's own module docstring calls out as a
"well documented production parameter set" calibrated to produce a melt pool roughly 90 um deep,
2.3 layers on a 40 um layer. The same point is exercised in
additiveLPBF/tests/testAdditiveLPBF.py::testMeltPoolReachesThePreviousLayer (asserts 1.5 <=
depthToLayerRatio <= 2.5) and ::testEnergyDensityAgainstPublishedParameterSets (asserts the
volumetric energy density lands between 30 and 100 J/mm^3). The power sweep bounds echo
::testProcessWindowOrderingIsMonotonic, which walks 60 to 1500 W on 316L to show the regime ordering
lack of fusion -> stable -> keyhole; this script holds Inconel 718 and narrows the top of the range
to 900 W so the stable window fills more of the plot.

Every value plotted comes from calling LpbfProcess.calculateEnergyDensity() and .calculateMeltPool()
directly at each power, not from re-deriving the Eagar-Tsai scaling by hand.

Run it with:

    python generateProcessWindowPlot.py

Writes docs/images/lpbfProcessWindow.png and prints the swept values.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'additiveLpbfLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from lpbfUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from LpbfProcess import LpbfProcess, NORMALISED_ENTHALPY_LOWER, NORMALISED_ENTHALPY_UPPER

#--------------------------------------------------------------------------------------------------#
# -- Sweep laser power at the Inconel 718 production scan speed -- #
#--------------------------------------------------------------------------------------------------#

MATERIAL   = 'Inconel 718'
SCAN_SPEED = 0.960     # [m/s], from the calibration point in LpbfProcess.py and the test file

powers = np.linspace(60.0, 900.0, 200)

depthRatios = np.full_like(powers, np.nan)
enthalpies  = np.full_like(powers, np.nan)
regimes     = []

for index, power in enumerate(powers):
    process = LpbfProcess()
    process.setInputs({'material': MATERIAL, 'laserPower': float(power), 'scanSpeed': SCAN_SPEED})
    process.calculateEnergyDensity()
    meltPool = process.calculateMeltPool()
    classification = process.classifyRegime()

    depthRatios[index] = meltPool['depthToLayerRatio']
    enthalpies[index]  = classification['normalisedEnthalpy']
    regimes.append(classification['processRegime'])

regimes = np.array(regimes)

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Shade the three regimes by normalised enthalpy, converted back to power for the fill
lackOfFusion = enthalpies < NORMALISED_ENTHALPY_LOWER
keyhole      = enthalpies > NORMALISED_ENTHALPY_UPPER

ax.fill_between(powers, 0.0, 3.0, where = lackOfFusion, color = BLUE, alpha = 0.12, linewidth = 0)
ax.fill_between(powers, 0.0, 3.0, where = keyhole, color = RED, alpha = 0.12, linewidth = 0)

ax.plot(powers, depthRatios, color = ACCENT, linewidth = 2.2, label = 'Melt pool depth / layer thickness')

ax.axhline(1.0, color = MUTED, linewidth = 0.9, linestyle = '--', alpha = 0.8)
ax.text(powers[-1], 1.03, 'depth = 1 layer (lack of fusion below this)', color = MUTED,
        fontsize = 7.8, ha = 'right', va = 'bottom')
ax.axhspan(1.5, 2.5, color = GREEN, alpha = 0.08, linewidth = 0)
ax.text(powers[3], 2.0, 'target band\n1.5 to 2.5 layers', color = GREEN, fontsize = 7.8, ha = 'left',
        va = 'center')

# Mark the validated production point: 285 W
anchorProcess = LpbfProcess()
anchorProcess.setInputs({'material': MATERIAL, 'laserPower': 285.0, 'scanSpeed': SCAN_SPEED})
anchorProcess.calculateEnergyDensity()
anchorMeltPool = anchorProcess.calculateMeltPool()
ax.scatter([285.0], [anchorMeltPool['depthToLayerRatio']], color = TEXT, s = 42, zorder = 5,
           edgecolor = BG, linewidth = 1.2)
ax.annotate('285 W production point\n(validated, 2.3 layers)', xy = (285.0, anchorMeltPool['depthToLayerRatio']),
            xytext = (400.0, 2.85), color = TEXT, fontsize = 8.0,
            arrowprops = dict(arrowstyle = '->', color = MUTED, linewidth = 0.8))

ax.text(powers[lackOfFusion][len(powers[lackOfFusion]) // 2] if lackOfFusion.any() else powers[0],
        0.15, 'LACK OF FUSION', color = BLUE, fontsize = 8.5, ha = 'center', fontweight = 'bold')
ax.text(powers[keyhole][len(powers[keyhole]) // 2] if keyhole.any() else powers[-1],
        0.15, 'KEYHOLE', color = RED, fontsize = 8.5, ha = 'center', fontweight = 'bold')

ax.set_xlim(powers[0], powers[-1])
ax.set_ylim(0.0, 3.0)
ax.set_title('LPBF process window, Inconel 718 at 0.960 m/s scan speed\n'
             'melt pool penetration vs. laser power, 110 um hatch, 40 um layer',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)
ax.set_xlabel('Laser power [W]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Melt pool depth / layer thickness [-]', color = MUTED, fontsize = 9.5)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)
ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'upper left')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'lpbfProcessWindow.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

samplePowers = [60.0, 150.0, 285.0, 450.0, 700.0, 900.0]
rows = []
for power in samplePowers:
    process = LpbfProcess()
    process.setInputs({'material': MATERIAL, 'laserPower': power, 'scanSpeed': SCAN_SPEED})
    process.calculateEnergyDensity()
    meltPool = process.calculateMeltPool()
    classification = process.classifyRegime()
    rows.append([f'{power:.0f}', f'{classification["normalisedEnthalpy"]:.1f}',
                 f'{meltPool["depthToLayerRatio"]:.2f}', classification['processRegime'].upper()])

print(formatReportTable(
    rows, ['Laser power [W]', 'Normalised enthalpy [-]', 'Depth/layer [-]', 'Regime'],
    title = 'PLOTTED LPBF PROCESS WINDOW, INCONEL 718 AT 0.960 m/s'))

print('\nInput provenance: additiveLPBF/additiveLpbfLibrary/LpbfProcess.py module docstring')
print('(285 W / 0.960 m/s / 80 um beam calibration point) and')
print('additiveLPBF/tests/testAdditiveLPBF.py::testMeltPoolReachesThePreviousLayer,')
print('::testEnergyDensityAgainstPublishedParameterSets and ::testProcessWindowOrderingIsMonotonic.')
