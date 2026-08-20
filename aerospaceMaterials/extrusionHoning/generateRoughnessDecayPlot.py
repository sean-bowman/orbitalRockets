
# -- Surface Roughness Decay Figure Generator [extrusionHoning] -- #

'''

Renders as-built LPBF internal surface roughness decaying exponentially towards the grit-limited
floor as abrasive flow machining cycle count rises, 1 to 60 cycles.

    Ra_N = Ra_inf + (Ra_0 - Ra_inf) exp(-k N)

The scenario is a 4.76 mm Inconel 718 manifold passage honed with the medium grit media the class
selects automatically for that bore, at 180 mm length and 7 MPa extrusion pressure (all class
defaults). This is the exact configuration validated in
extrusionHoning/tests/testExtrusionHoning.py::testFinishImprovementMatchesTheSharedRoughnessTable,
which asserts the initial roughness matches roughnessTable('lpbf as-built') = 20 um, the roughness
after 20 cycles matches roughnessTable('lpbf abrasive flow') = 5 um to within 10 percent, and the
improvement ratio is 4.0x. The 4.76 mm bore itself is not arbitrary: it is the thruster valve bore
carried through from the fluidSystems worked example into aerospaceMaterials/codeInterface.py as
"thruster valve bore 4.76 mm --> LPBF manifold channel", so this script continues that same part
into the one sub-domain that codeInterface.py does not visit. The cycle range brackets
::testRoughnessDecaysMonotonicallyTowardsTheFloor, which walks 1, 5, 10, 20, 40 cycles and asserts
each improvement is smaller than the last.

Every value plotted comes from calling ExtrusionHoning.calculateSurfaceFinish() at each cycle count,
not from re-deriving the exponential decay by hand.

Run it with:

    python generateRoughnessDecayPlot.py

Writes docs/images/roughnessDecay.png and prints the swept values.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'extrusionHoningLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from honingUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from ExtrusionHoning import ExtrusionHoning

#--------------------------------------------------------------------------------------------------#
# -- Sweep cycle count on the validated Inconel 718 manifold scenario -- #
#--------------------------------------------------------------------------------------------------#

PASSAGE_DIAMETER = 0.00476    # [m], the fluidSystems thruster valve bore, from testFinishImprovement...
PASSAGE_LENGTH   = 0.180      # [m]
MATERIAL         = 'Inconel 718'
CONDITION        = 'lpbf hip + sta'

cycleCounts = np.linspace(1, 60, 120)

roughnesses = []
floorValue  = None
initialRa   = None

for cycles in cycleCounts:
    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': PASSAGE_DIAMETER, 'passageLength': PASSAGE_LENGTH,
                      'material': MATERIAL, 'condition': CONDITION, 'cycleCount': float(cycles)})
    honing.calculateWallShear()
    finish = honing.calculateSurfaceFinish()
    roughnesses.append(finish['finalRoughness'])
    floorValue = finish['roughnessFloor']
    initialRa  = finish['initialRoughness']

roughnesses = np.array(roughnesses)

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(cycleCounts, roughnesses * 1.0e6, color = ACCENT, linewidth = 2.4,
        label = 'Ra, medium grit media')

ax.axhline(initialRa * 1.0e6, color = MUTED, linewidth = 0.9, linestyle = ':', alpha = 0.8)
ax.text(cycleCounts[-1], initialRa * 1.0e6 + 0.5, 'LPBF as-built (20 um)', color = MUTED,
        fontsize = 8.0, ha = 'right', va = 'bottom')

ax.axhline(floorValue * 1.0e6, color = GREEN, linewidth = 1.1, linestyle = '--', alpha = 0.85)
ax.text(cycleCounts[-1], floorValue * 1.0e6 + 0.4, 'grit-limited floor', color = GREEN,
        fontsize = 8.0, ha = 'right', va = 'bottom')

# Mark the validated 20-cycle point against roughnessTable('lpbf abrasive flow')
markerHoning = ExtrusionHoning()
markerHoning.setInputs({'passageDiameter': PASSAGE_DIAMETER, 'passageLength': PASSAGE_LENGTH,
                        'material': MATERIAL, 'condition': CONDITION, 'cycleCount': 20})
markerHoning.calculateWallShear()
markerFinish = markerHoning.calculateSurfaceFinish()
ax.scatter([20], [markerFinish['finalRoughness'] * 1.0e6], color = TEXT, s = 42, zorder = 5,
           edgecolor = BG, linewidth = 1.2)
ax.annotate(f'20 cycles: {markerFinish["finalRoughness"] * 1.0e6:.1f} um\n'
            f'(validated vs. roughnessTable)', xy = (20, markerFinish['finalRoughness'] * 1.0e6),
            xytext = (28, 11.0), color = TEXT, fontsize = 8.2,
            arrowprops = dict(arrowstyle = '->', color = MUTED, linewidth = 0.8))

ax.set_xlim(cycleCounts[0], cycleCounts[-1])
ax.set_ylim(0.0, initialRa * 1.0e6 * 1.15)
ax.set_xlabel('Cycles [-]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Surface roughness, Ra [um]', color = MUTED, fontsize = 9.5)
ax.set_title('Abrasive flow machining roughness decay vs. cycle count\n'
             '4.76 mm Inconel 718 manifold passage, as-built LPBF internal surface',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)
ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'center right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'roughnessDecay.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

sampleCycles = [1, 5, 10, 20, 30, 40, 60]
rows = []
for cycles in sampleCycles:
    honing = ExtrusionHoning()
    honing.setInputs({'passageDiameter': PASSAGE_DIAMETER, 'passageLength': PASSAGE_LENGTH,
                      'material': MATERIAL, 'condition': CONDITION, 'cycleCount': cycles})
    honing.calculateWallShear()
    finish = honing.calculateSurfaceFinish()
    rows.append([f'{cycles}', f'{finish["finalRoughness"] * 1.0e6:.2f}',
                 f'{finish["improvementRatio"]:.2f}'])

print(formatReportTable(
    rows, ['Cycles [-]', 'Ra [um]', 'Improvement vs. as-built [x]'],
    title = 'PLOTTED ROUGHNESS DECAY, 4.76 mm INCONEL 718 MANIFOLD'))

print(f'\nGrit-limited floor: {floorValue * 1.0e6:.2f} um (medium grit media, selected automatically')
print(f'for a 4.76 mm passage). Initial as-built roughness: {initialRa * 1.0e6:.1f} um.')
print('\nInput provenance: extrusionHoning/tests/testExtrusionHoning.py::')
print('testFinishImprovementMatchesTheSharedRoughnessTable (passageDiameter = 0.00476 m,')
print('passageLength = 0.180 m, material = Inconel 718, condition = lpbf hip + sta) and')
print('::testRoughnessDecaysMonotonicallyTowardsTheFloor (cycle range). The 4.76 mm bore traces to')
print('the thruster valve in aerospaceMaterials/codeInterface.py\'s fluidSystems-inherited example.')
