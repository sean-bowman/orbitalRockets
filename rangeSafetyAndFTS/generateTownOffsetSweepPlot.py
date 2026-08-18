
# -- Town Offset Sweep Figure Generator [rangeSafetyAndFTS] -- #

'''

Renders casualty expectation vs. town cross-range offset from the coastal launch worked example.
`codeInterface.reportDispersion()` runs this exact sweep (16 offsets, 0 to 30 km in 2 km steps) and
prints it, but only returns the final licensing threshold, not the series. This script replicates
the loop against the same `DebrisDispersion` and `PublicRisk` objects the worked example builds,
rather than re-deriving the debris model.

Run it with:

    python generateTownOffsetSweepPlot.py

Writes docs/images/townOffsetSweep.png and prints the series plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'rangeSafetyLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from rangeSafetyUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('rangeSafetyTownOffsetCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case       = ci.loadCase()
dispersion = ci.buildDispersion(case)

regions = [{key: region[key] for key in
            ('name', 'start', 'end', 'crossRange', 'crossWidth') if key in region}
           for region in case['risk']['regions']]

offsets = case['dispersion']['townOffsets']

#--------------------------------------------------------------------------------------------------------------------------#
# -- Replicate the Offset Sweep -- #
#--------------------------------------------------------------------------------------------------------------------------#

offsetsKm, expectedCasualties, clearsFlags = [], [], []
threshold = None

for offset in offsets:

    trial = [dict(region) for region in regions]
    for region in trial:
        if 'town' in region['name']:
            region['crossRange'] = offset

    result   = dispersion.impactProbabilities(trial)
    computed = {entry['name']: entry['impactProbability'] for entry in result['regions']}

    risk = ci.buildRisk(case, computed)

    try:
        collective = risk.calculateCollective()
        expected, clears = collective['expectedCasualties'], True
    except ci.RiskError as error:
        expected, clears = error.context['expectedCasualties'], False

    if clears and threshold is None:
        threshold = offset

    offsetsKm.append(offset / 1000.0)
    expectedCasualties.append(expected)
    clearsFlags.append(clears)

thresholdLevel = ci.LAUNCH_SAFETY_CRITERIA['publicCollective']['limit']

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

colors = [GREEN if clears else RED for clears in clearsFlags]
ax.plot(offsetsKm, expectedCasualties, color = ACCENT, linewidth = 1.6, zorder = 3)
ax.scatter(offsetsKm, expectedCasualties, color = colors, s = 32, zorder = 4, edgecolor = BG, linewidth = 0.8)
ax.set_yscale('log')

ax.axhline(thresholdLevel, color = RED, linewidth = 1.1, linestyle = '--')
ax.text(offsetsKm[-1] * 0.98, thresholdLevel * 1.3, f'licensing threshold {thresholdLevel:.0e}',
        color = RED, fontsize = 8.5, ha = 'right', va = 'bottom')

if threshold is not None:
    ax.axvline(threshold / 1000.0, color = GREEN, linewidth = 1.0, linestyle = ':', alpha = 0.8)
    ax.text(threshold / 1000.0 + 0.4, ax.get_ylim()[0], f'clears at {threshold / 1000.0:.0f} km',
            color = GREEN, fontsize = 8.5, rotation = 90, va = 'bottom')

ax.set_xlabel('Town cross-range offset from ground track [km]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Expected casualties, Ec (log scale)', color = MUTED, fontsize = 9.5)
ax.set_title('Public risk vs. town offset, coastal launch\ngreen clears the collective-risk criterion, red does not',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, which = 'both', color = BORDER, alpha = 0.35, linewidth = 0.6)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'townOffsetSweep.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{o:.0f}', f'{e:.3e}', 'yes' if c else 'NO'] for o, e, c in
        zip(offsetsKm, expectedCasualties, clearsFlags)]
print(formatReportTable(rows, ['Town offset [km]', 'Ec', 'Licensable'],
                        title = f'PLOTTED TOWN OFFSET SWEEP (threshold {threshold / 1000.0:.0f} km)'))
