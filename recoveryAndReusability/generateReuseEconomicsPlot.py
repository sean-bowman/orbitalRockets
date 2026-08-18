
# -- Reuse Economics Figure Generator [recoveryAndReusability] -- #

'''

Renders cost-per-flight vs. flight count from the booster reuse worked example.
`ReuseEconomics.flightCountSweep()` already returns the full swept series, so this script loads the
worked example's case and payload penalty by explicit path and calls that method directly rather
than re-deriving the amortization model.

Run it with:

    python generateReuseEconomicsPlot.py

Writes docs/images/reuseEconomics.png and prints the series plotted.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'recoveryAndReusabilityLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from recoveryUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('recoveryReuseEconomicsCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)   # module has a main() guard, so this only defines functions

case = ci.loadCase()

# The published payload penalty, the same measured (not modelled) figure main() uses so the
# model's own over-prediction is not compounded into the economics.
vehicle = case['vehicle']
publishedPenalty = ((vehicle['baselinePayload'] - vehicle['publishedReusablePayload'])
                    / vehicle['baselinePayload'])

economics = ci.buildEconomics(case, publishedPenalty)
result    = economics.flightCountSweep()
sweep     = result['sweep']

flights        = [entry['flights']       for entry in sweep]
costPerFlight  = [entry['costPerFlight'] for entry in sweep]

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

ax.plot(flights, costPerFlight, color = ACCENT, linewidth = 2.0, marker = 'o', markersize = 6)

ax.axvline(3, color = GREEN, linewidth = 1.0, linestyle = ':', alpha = 0.8)
ax.text(3.2, max(costPerFlight) * 0.92, f'{result["shareOfBenefitInThree"] * 100.0:.0f}% of the\nbenefit by flight 3',
        color = GREEN, fontsize = 8.5)

for x, y in zip(flights, costPerFlight):
    ax.annotate(f'{y:,.1f}M', xy = (x, y), xytext = (0, 9), textcoords = 'offset points',
                color = MUTED, fontsize = 7.5, ha = 'center')

ax.set_xlabel('Flights on the same airframe', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Cost per flight [$M]', color = MUTED, fontsize = 9.5)
ax.set_title('Booster reuse economics: cost per flight vs. flight count\nrefurbishment and recovery cost amortized over the fleet-leader',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'reuseEconomics.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [[f'{entry["flights"]:.0f}', f'{entry["costPerFlight"]:.2f}', f'{entry["amortisedShare"] * 100.0:.1f}%',
         f'{entry["marginalSaving"]:.2f}'] for entry in sweep]
print(formatReportTable(rows, ['Flights', 'Cost/flight [$M]', 'Amortised share', 'Marginal saving [$M]'],
                        title = f'PLOTTED REUSE ECONOMICS (share of benefit by flight 3: {result["shareOfBenefitInThree"] * 100.0:.0f}%)'))
