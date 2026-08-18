
# -- Cryogenic Specific Heat Figure Generator [aerospaceMaterials] -- #

'''

Renders specific heat vs. temperature, 4 to 300 K, for the three metals `common/cryogenicProperties`
carries its own NIST curve fit for: 304 stainless, 316 stainless (published as two segments meeting
at 50 K), and 6061 aluminium. These are the materials every other alloy in the aerospaceMaterials
substitution table (316L, 304L, 2219, 2195, 7075) maps onto for a chill-down enthalpy calculation.

The values plotted come from calling `specificHeat()` itself, not from re-transcribing the NIST
polynomial coefficients, so a change to the fit shows up here automatically.

Run it with:

    python generateCryogenicSpecificHeatPlot.py

Writes docs/images/cryogenicSpecificHeat.png and prints the sampled points.

Author: Sean Bowman
Date:   08/15/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'aerospaceMaterialsLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from utils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from cryogenicProperties import specificHeat, CRYOGENIC_SPECIFIC_HEAT_FITS

#--------------------------------------------------------------------------------------------------------------------------#
# -- Sample Each Fit -- #
#--------------------------------------------------------------------------------------------------------------------------#

materials  = ['stainless 304', 'stainless 316', 'aluminium 6061']
labels     = ['304 stainless', '316 stainless', '6061 aluminium']
colors     = ['#7baee8', '#E0975A', '#86C06C']

temperatures = np.linspace(4.0, 300.0, 400)
curves = {material: specificHeat(material, temperatures) for material in materials}

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
YELLOW = '#d4b86a'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for material, label, color in zip(materials, labels, colors):
    ax.plot(temperatures, curves[material], color = color, linewidth = 2.0, label = label)

# Mark the 316 stainless segment join at 50 K, the free check on transcription the module's own
# docstring calls out: an error in either published segment would show up as a step here.
ax.axvline(50.0, color = YELLOW, linewidth = 0.9, linestyle = '--', alpha = 0.7)
ax.text(50.0, ax.get_ylim()[1] if False else max(curves['stainless 316']) * 0.05,
        '316 fit joins two\nNIST segments at 50 K', color = YELLOW, fontsize = 7.5, ha = 'left')

ax.set_xlabel('Temperature [K]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Specific heat [J / (kg K)]', color = MUTED, fontsize = 9.5)
ax.set_title('Cryogenic specific heat, NIST curve fits\n4 to 300 K, structural metals',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7)
ax.set_axisbelow(True)

ax.legend(frameon = False, fontsize = 9, labelcolor = TEXT, loc = 'lower right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'cryogenicSpecificHeat.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

sampleTemperatures = [20.0, 77.0, 90.0, 150.0, 293.0]
rows = []
for temperature in sampleTemperatures:
    row = [f'{temperature:.0f} K']
    for material in materials:
        row.append(f'{specificHeat(material, temperature):.1f}')
    rows.append(row)

print(formatReportTable(rows, ['Temperature'] + labels, title = 'PLOTTED CRYOGENIC SPECIFIC HEAT [J/(kg K)]'))
