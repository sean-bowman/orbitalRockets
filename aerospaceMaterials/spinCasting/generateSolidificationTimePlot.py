
# -- Centrifugal Casting Solidification Time Figure Generator [spinCasting] -- #

'''

Renders Chvorinov solidification time against wall thickness, 4 to 80 mm, for four centrifugal
casting alloys at a fixed 200 mm outer diameter and 400 mm length, both CentrifugalCasting's own
class defaults.

    t = B (V / A_effective)^2,   A_effective = outerArea + 0.15 * boreArea

The centrifugal casting modulus differs from a static casting's plain V/A because a spinning shell
cools almost entirely through the outer wall into the mould; the bore is exposed to air and radiates
comparatively little, so it is weighted at 15 percent of its geometric area rather than counted in
full. THE SOLIDIFICATION TIME IS THE INTEGRATION WINDOW for the Stokes inclusion migration this
sub-domain's class exists to compute (CentrifugalCasting.py's own docstring): a thin wall freezes
fast and gives inclusions little time to separate, which is why a thin centrifugal casting is less
clean than a thick one at the same speed.

The n = 2 modulus-squared scaling is validated in
spinCasting/tests/testSpinCasting.py::testSolidificationTimeScalesWithModulusSquared (alloy = 316L,
outerDiameter = 0.200 m, wallThickness = 0.010 and 0.020 m, asserting the time ratio equals the
modulus ratio squared). 316L is the class's own default alloy; bronze and Inconel 625 are added
because CASTING_ALLOYS's own notes call them out by name -- bronze as "the classic centrifugal
bushing and bearing material" and Inconel 625 as needing "vacuum or inert melting to avoid oxide
inclusions" -- and steel as "the most common centrifugal casting alloy, mostly for pipe and rings."

Every value plotted comes from calling CentrifugalCasting.calculateSolidification() at each wall
thickness, not from re-deriving the Chvorinov relation by hand.

NOTE ON A DELIBERATE DEVIATION: the directed starting point for this sub-domain was G-factor vs.
Stokes escape fraction. That sweep was built and discarded: at the class's own default geometry the
capture number already exceeds 100 (escape fraction saturated above 99 percent) at every G-factor in
the real process window (40 to 150, per G_FACTOR_WINDOW), which is exactly what
testCentrifugalFieldOutrunsTheSolidificationFront validates. Showing the transition at all would
require sweeping G below about 1, which is not a centrifugal casting speed used in practice and
appears nowhere in the test file or the class's own documented range. Rather than fabricate an
operating window the class does not support, this script uses the sub-domain's own documented
fallback: solidification time vs. section thickness, in the centrifugal-specific form.

Run it with:

    python generateSolidificationTimePlot.py

Writes docs/images/centrifugalSolidificationTime.png and prints the swept values.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'spinCastingLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from spinCastingUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from CentrifugalCasting import CentrifugalCasting, CASTING_ALLOYS, GEOMETRY_LIMITS

#--------------------------------------------------------------------------------------------------#
# -- Sweep wall thickness for four alloys at the class's default geometry -- #
#--------------------------------------------------------------------------------------------------#

OUTER_DIAMETER = 0.200   # [m], the class default
LENGTH         = 0.400   # [m], the class default

alloys = ['316L', 'bronze', 'inconel 625', 'steel']
colors = {'316L': '#E0975A', 'bronze': '#d4b86a', 'inconel 625': '#7baee8', 'steel': '#8a95a8'}

wallThicknesses = np.linspace(0.004, 0.080, 150)

curves = {}
for alloy in alloys:
    times = []
    for wall in wallThicknesses:
        casting = CentrifugalCasting()
        casting.setInputs({'alloy': alloy, 'outerDiameter': OUTER_DIAMETER,
                           'wallThickness': float(wall), 'length': LENGTH})
        casting.selectRotationalSpeed()
        times.append(casting.calculateSolidification()['solidificationTime'])
    curves[alloy] = np.array(times)

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for alloy in alloys:
    ax.plot(wallThicknesses * 1.0e3, curves[alloy], color = colors[alloy], linewidth = 2.2,
            label = f'{alloy} (B = {CASTING_ALLOYS[alloy.upper()]["chvorinovConstant"]:.1e})')

# Mark the validated test point at 20 mm wall (316L)
markerCasting = CentrifugalCasting()
markerCasting.setInputs({'alloy': '316L', 'outerDiameter': OUTER_DIAMETER, 'wallThickness': 0.020,
                         'length': LENGTH})
markerCasting.selectRotationalSpeed()
markerTime = markerCasting.calculateSolidification()['solidificationTime']
ax.scatter([20.0], [markerTime], color = TEXT, s = 42, zorder = 5, edgecolor = BG, linewidth = 1.2)
ax.annotate(f'20 mm wall (test point):\n{markerTime:.0f} s', xy = (20.0, markerTime),
            xytext = (32.0, markerTime * 0.35), color = TEXT, fontsize = 8.2,
            arrowprops = dict(arrowstyle = '->', color = MUTED, linewidth = 0.8))

ax.set_yscale('log')
ax.set_xlim(wallThicknesses[0] * 1.0e3, wallThicknesses[-1] * 1.0e3)
ax.set_xlabel('Wall thickness [mm]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Solidification time [s] (log scale)', color = MUTED, fontsize = 9.5)
ax.set_title('Centrifugal casting solidification time vs. wall thickness\n'
             '200 mm OD x 400 mm cylinder, outer-wall-dominated cooling',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7, which = 'both')
ax.set_axisbelow(True)
ax.legend(frameon = False, fontsize = 8.5, labelcolor = TEXT, loc = 'lower right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'centrifugalSolidificationTime.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

sampleWalls = [0.004, 0.010, 0.020, 0.040, 0.060, 0.080]
rows = []
for wall in sampleWalls:
    row = [f'{wall * 1.0e3:.0f}']
    for alloy in alloys:
        casting = CentrifugalCasting()
        casting.setInputs({'alloy': alloy, 'outerDiameter': OUTER_DIAMETER, 'wallThickness': wall,
                           'length': LENGTH})
        casting.selectRotationalSpeed()
        row.append(f'{casting.calculateSolidification()["solidificationTime"]:.1f}')
    rows.append(row)

print(formatReportTable(
    rows, ['Wall [mm]'] + [alloy.title() for alloy in alloys],
    title = 'PLOTTED SOLIDIFICATION TIME [s], 200 mm OD x 400 mm CYLINDER'))

print('\nInput provenance: spinCasting/spinCastingLibrary/CentrifugalCasting.py class defaults')
print('(outerDiameter = 0.200 m, length = 0.400 m) and module constants CASTING_ALLOYS')
print('(chvorinovConstant per alloy) and spinCasting/tests/testSpinCasting.py::')
print('testSolidificationTimeScalesWithModulusSquared (alloy = 316L, wallThickness = 0.010/0.020 m).')
