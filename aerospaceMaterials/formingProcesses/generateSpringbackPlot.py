
# -- Springback Figure Generator [formingProcesses] -- #

'''

Renders air-bend springback angle against bend radius, 2 to 20 mm, for 316L and Ti-6Al-4V sheet at a
common 1.6 mm thickness and 90 degree target angle.

    R_i / R_f = 4 (R_i F_ty / (E t))^3 - 3 (R_i F_ty / (E t)) + 1

The governing group R F_ty / (E t) is the ratio of the yield strain to the bend strain, and titanium
is doubly penalised in it: F_ty/E is far higher for Ti-6Al-4V than for austenitic stainless, so the
same geometry yields the titanium section less thoroughly and it springs back more.

The scenario is exactly the one in
formingProcesses/tests/testFormingProcesses.py::testTitaniumSpringsBackMoreThanStainless (316L
annealed vs. Ti-6Al-4V annealed, thickness = 0.0016 m, bendRadius = 0.0064 m, bendAngle = 90 deg,
asserting springback['Ti-6Al-4V'] > 3.0 * springback['316L']), and the radius sweep brackets
::testSpringbackFallsWithATighterBend, which walks bendRadius = 0.002, 0.006, 0.020 m on 316L and
asserts the springback angle rises monotonically with radius. The lower end of the sweep, 2 mm, sits
above the Ti-6Al-4V minimum bend radius at this thickness (1.6 mm, from the reduction-of-area
relation in calculateMinimumBendRadius()), so every point plotted is a bend the material can
actually make without cracking.

Every value plotted comes from calling FormingProcess.calculateSpringback() at each radius, not from
re-deriving the closed-form cubic by hand.

Run it with:

    python generateSpringbackPlot.py

Writes docs/images/springbackVsBendRadius.png and prints the swept values.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'formingProcessesLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from formingUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from FormingProcess import FormingProcess

#--------------------------------------------------------------------------------------------------#
# -- Sweep bend radius for both materials -- #
#--------------------------------------------------------------------------------------------------#

THICKNESS  = 0.0016    # [m], the test's fixed thickness
BEND_ANGLE = 90.0      # [deg]

materials = [('316L', 'annealed'), ('Ti-6Al-4V', 'annealed')]
colors    = {'316L': '#7baee8', 'Ti-6Al-4V': '#E0975A'}

radii = np.linspace(0.002, 0.020, 100)

curves = {}
for material, condition in materials:
    angles = []
    for radius in radii:
        forming = FormingProcess()
        forming.setInputs({'material': material, 'condition': condition, 'thickness': THICKNESS,
                           'bendRadius': float(radius), 'bendAngle': BEND_ANGLE})
        forming.calculateMinimumBendRadius()
        angles.append(forming.calculateSpringback()['springbackAngle'])
    curves[material] = np.array(angles)

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for material, _ in materials:
    ax.plot(radii * 1.0e3, curves[material], color = colors[material], linewidth = 2.2,
            label = f'{material} annealed')

# Mark the exact validated test point at 6.4 mm
markerRadius = 0.0064
for material, condition in materials:
    forming = FormingProcess()
    forming.setInputs({'material': material, 'condition': condition, 'thickness': THICKNESS,
                       'bendRadius': markerRadius, 'bendAngle': BEND_ANGLE})
    forming.calculateMinimumBendRadius()
    angle = forming.calculateSpringback()['springbackAngle']
    ax.scatter([markerRadius * 1.0e3], [angle], color = TEXT, s = 36, zorder = 5,
               edgecolor = BG, linewidth = 1.0)

ax.annotate('6.4 mm test point:\nTi-6Al-4V springs back\n>3x the 316L angle',
            xy = (6.4, curves['Ti-6Al-4V'][np.argmin(np.abs(radii * 1.0e3 - 6.4))]),
            xytext = (10.5, 18.0), color = TEXT, fontsize = 8.3,
            arrowprops = dict(arrowstyle = '->', color = MUTED, linewidth = 0.8))

ax.set_xlim(radii[0] * 1.0e3, radii[-1] * 1.0e3)
ax.set_xlabel('Bend radius (inner) [mm]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Springback angle [deg]', color = MUTED, fontsize = 9.5)
ax.set_title('Air-bend springback vs. bend radius, 1.6 mm sheet, 90 deg target\n'
             '316L austenitic stainless vs. Ti-6Al-4V, both annealed',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)
ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'upper left')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'springbackVsBendRadius.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

sampleRadii = [0.002, 0.0064, 0.010, 0.014, 0.020]
rows = []
for radius in sampleRadii:
    row = [f'{radius * 1.0e3:.1f}']
    for material, condition in materials:
        forming = FormingProcess()
        forming.setInputs({'material': material, 'condition': condition, 'thickness': THICKNESS,
                           'bendRadius': radius, 'bendAngle': BEND_ANGLE})
        forming.calculateMinimumBendRadius()
        row.append(f'{forming.calculateSpringback()["springbackAngle"]:.2f}')
    ratio = float(row[2]) / float(row[1])
    row.append(f'{ratio:.1f}x')
    rows.append(row)

print(formatReportTable(
    rows, ['Bend radius [mm]', '316L springback [deg]', 'Ti-6Al-4V springback [deg]', 'Ti/316L ratio'],
    title = 'PLOTTED SPRINGBACK, 1.6 mm SHEET, 90 deg TARGET'))

print('\nInput provenance: formingProcesses/tests/testFormingProcesses.py::')
print('testTitaniumSpringsBackMoreThanStainless (316L annealed vs. Ti-6Al-4V annealed, thickness =')
print('0.0016 m, bendRadius = 0.0064 m, bendAngle = 90 deg) and ::testSpringbackFallsWithATighterBend')
print('(radius sweep 0.002 to 0.020 m on 316L, monotonic rise asserted).')
