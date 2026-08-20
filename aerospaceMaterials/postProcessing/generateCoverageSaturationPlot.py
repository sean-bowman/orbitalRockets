
# -- Peening Coverage Saturation Figure Generator [postProcessing] -- #

'''

Renders shot peening coverage and the resulting fatigue improvement factor against peening time, 1
to 250 s, at a 60 s time-to-98-percent-coverage for a 316L part with ceramic bead media.

    C = 1 - exp(-t / t_saturation * ln(1 / (1 - 0.98)))

Coverage is exponential-saturation because each impact lands randomly and later impacts increasingly
fall where earlier ones already have. Full coverage is DEFINED as 98 percent because 100 percent is
asymptotic and unreachable, which is why a "200 percent coverage" specification is a real, sane
callout: it means twice the time to reach 98 percent, not a geometric impossibility.

The scenario (material = 316L, condition = annealed, alloyFamily = stainless, saturationTime = 60 s,
wallThickness = 0.006 m) is exactly
postProcessing/tests/testPostProcessing.py::testCoverageSaturatesExponentially, which sweeps
peeningTime = 30, 60, 120, 240 s and asserts the 60 s point lands on the 98 percent that DEFINES full
coverage, and every value stays below 1.0 (100 percent is unreachable). The fatigue curve is the
companion calculation from ::testPartialCoverageLosesMostOfHelperBenefit
[testPartialCoverageLosesMostOfTheBenefit], which asserts partial coverage loses fatigue benefit
faster than coverage itself falls off.

Every value plotted comes from calling SurfaceTreatment.calculatePeening() at each peening time, not
from re-deriving the saturation exponential by hand.

Run it with:

    python generateCoverageSaturationPlot.py

Writes docs/images/coverageSaturation.png and prints the swept values.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'postProcessingLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from surfaceUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from SurfaceTreatment import SurfaceTreatment, COVERAGE_SATURATION

#--------------------------------------------------------------------------------------------------#
# -- Sweep peening time on the validated 316L scenario -- #
#--------------------------------------------------------------------------------------------------#

SATURATION_TIME = 60.0     # [s], the test's fixed time-to-98-percent-coverage
WALL_THICKNESS  = 0.006    # [m], the test's fixed wall

peeningTimes = np.linspace(1.0, 250.0, 200)

coverages = []
fatigueFactors = []
for time in peeningTimes:
    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                         'peeningTime': float(time), 'saturationTime': SATURATION_TIME,
                         'wallThickness': WALL_THICKNESS})
    peening = treatment.calculatePeening()
    coverages.append(peening['coverage'])
    fatigueFactors.append(peening['fatigueImprovementFactor'])

coverages = np.array(coverages)
fatigueFactors = np.array(fatigueFactors)

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

ax.plot(peeningTimes, coverages * 100.0, color = ACCENT, linewidth = 2.2, label = 'Coverage [%]')

ax.axhline(COVERAGE_SATURATION * 100.0, color = GREEN, linewidth = 1.0, linestyle = '--', alpha = 0.8)
ax.text(peeningTimes[-1], COVERAGE_SATURATION * 100.0 - 3.0,
        f'{COVERAGE_SATURATION * 100.0:.0f}% defines "full coverage"\n(100% is asymptotic)',
        color = GREEN, fontsize = 7.8, ha = 'right', va = 'top')

ax.axvline(SATURATION_TIME, color = MUTED, linewidth = 0.9, linestyle = ':', alpha = 0.75)
ax.text(SATURATION_TIME + 4.0, 40.0, f'{SATURATION_TIME:.0f} s\n(spec "100%"\ntime)', color = MUTED,
        fontsize = 7.8, ha = 'left')

ax.axvline(2.0 * SATURATION_TIME, color = MUTED, linewidth = 0.9, linestyle = ':', alpha = 0.5)
ax.text(2.0 * SATURATION_TIME + 4.0, 20.0, f'{2.0 * SATURATION_TIME:.0f} s\n("200%\ncoverage")',
        color = MUTED, fontsize = 7.8, ha = 'left')

axFatigue = ax.twinx()
axFatigue.plot(peeningTimes, fatigueFactors, color = BLUE, linewidth = 2.0, linestyle = '-.',
               label = 'Fatigue improvement factor')
axFatigue.set_ylabel('Fatigue improvement factor [-]', color = BLUE, fontsize = 9.5)
axFatigue.tick_params(colors = BLUE, labelsize = 8.5)
axFatigue.spines['right'].set_color(BLUE)
for side in ('top', 'left', 'bottom'):
    axFatigue.spines[side].set_visible(False)

ax.set_xlim(peeningTimes[0], peeningTimes[-1])
ax.set_ylim(0.0, 105.0)
ax.set_xlabel('Peening time [s]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Coverage [%]', color = MUTED, fontsize = 9.5)
ax.set_title('Shot peening coverage saturation vs. time\n'
             '316L, ceramic bead media, 60 s time-to-98%-coverage',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ('top', 'right'):
    ax.spines[spine].set_visible(False)
for spine in ('left', 'bottom'):
    ax.spines[spine].set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = axFatigue.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, frameon = False, fontsize = 9, labelcolor = TEXT,
          loc = 'center right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'coverageSaturation.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

sampleTimes = [10.0, 30.0, 60.0, 120.0, 180.0, 240.0]
rows = []
for time in sampleTimes:
    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '316L', 'condition': 'annealed', 'alloyFamily': 'stainless',
                         'peeningTime': time, 'saturationTime': SATURATION_TIME,
                         'wallThickness': WALL_THICKNESS})
    peening = treatment.calculatePeening()
    rows.append([f'{time:.0f}', f'{peening["coverage"] * 100.0:.3f}',
                 f'{peening["fatigueImprovementFactor"]:.3f}'])

print(formatReportTable(
    rows, ['Peening time [s]', 'Coverage [%]', 'Fatigue improvement factor [-]'],
    title = 'PLOTTED COVERAGE SATURATION, 316L / CERAMIC BEAD'))

print('\nInput provenance: postProcessing/tests/testPostProcessing.py::testCoverageSaturatesExponentially')
print('(material = 316L, condition = annealed, alloyFamily = stainless, saturationTime = 60 s,')
print('wallThickness = 0.006 m, peeningTime swept 30/60/120/240 s) and')
print('::testPartialCoverageLosesMostOfTheBenefit (same scenario, fatigue factor comparison).')
