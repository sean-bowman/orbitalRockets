
# -- Chvorinov Solidification Time Figure Generator [castingProcesses] -- #

'''

Renders Chvorinov solidification time against casting modulus, 1 to 25 mm, for the four casting
routes CastingProcess.py carries: investment, sand, die and permanent mould.

    t = B (V/A)^n,   n = 2

The modulus is the volume-to-cooling-area ratio, the single geometric parameter Chvorinov's rule
says governs freezing time regardless of the part's overall size or shape, and for a plate of
thickness s it runs roughly M = s/2, so the swept range stands in for a wall from about 2 to 50 mm.

The four chvorinovConstant values plotted are CastingProcess.py's own module constants
(CASTING_PROCESSES dict), and the n = 2 scaling law they share is validated in
castingProcesses/tests/testCastingProcesses.py::testSolidificationTimeScalesWithModulusSquared
(process = investment, castingVolume = 1.0e-4 m^3, castingSurfaceArea swept 0.05 to 0.10 m^2, which
gives a 4x time increase for a 2x modulus increase). The relative ordering of the four routes'
process constants is exercised in ::testInvestmentHoldsFinerWallsThanSand (investment freezes fastest
at a given modulus because the mould conducts heat away fastest; sand is the slowest because sand is
itself an insulator).

Every value plotted comes from calling CastingProcess.calculateSolidification() at each modulus, not
from re-deriving t = B M^2 from the module constants by hand.

Run it with:

    python generateSolidificationTimePlot.py

Writes docs/images/castingSolidificationTime.png and prints the swept values.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'castingProcessesLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from castingUtils import formatReportTable   # bootstraps common/ onto sys.path as a side effect
from CastingProcess import CastingProcess, CASTING_PROCESSES

#--------------------------------------------------------------------------------------------------#
# -- Sweep casting modulus for each process route -- #
#--------------------------------------------------------------------------------------------------#

# Fixed casting volume (the test default, and CastingProcess's own class default), so sweeping the
# surface area sweeps the modulus M = V / A directly.
CASTING_VOLUME = 1.0e-4   # [m^3], the class default and the test's fixed volume

processes = ['investment', 'die', 'permanent mould', 'sand']
colors    = {'investment': '#E0975A', 'die': '#7baee8', 'permanent mould': '#86C06C', 'sand': '#e08080'}

# Modulus from 1 to 25 mm, spanning an investment-cast wall (1.5 mm minimum) up to a heavy sand
# section, via the surface area that produces it at the fixed volume.
moduliMetres = np.linspace(0.001, 0.025, 200)
areasForModulus = CASTING_VOLUME / moduliMetres

curves = {}
for process in processes:
    times = []
    for area in areasForModulus:
        casting = CastingProcess()
        casting.setInputs({'process': process, 'alloyFamily': 'stainless',
                           'castingVolume': CASTING_VOLUME, 'castingSurfaceArea': float(area)})
        times.append(casting.calculateSolidification()['solidificationTime'])
    curves[process] = np.array(times)

#--------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------#

BG, BORDER, TEXT, MUTED = '#1a1e2a', '#3a4055', '#d8e0ec', '#8a95a8'
ACCENT, GREEN, BLUE, YELLOW, RED, CYAN = '#E0975A', '#86C06C', '#7baee8', '#d4b86a', '#e08080', '#6ad4c8'

fig, ax = plt.subplots(figsize = (9.5, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

for process in processes:
    ax.plot(moduliMetres * 1.0e3, curves[process], color = colors[process], linewidth = 2.2,
            label = f'{process} (B = {CASTING_PROCESSES[process]["chvorinovConstant"]:.1e})')

ax.set_xlim(moduliMetres[0] * 1.0e3, moduliMetres[-1] * 1.0e3)

ax.set_yscale('log')
ax.set_xlabel('Casting modulus, V/A [mm]', color = MUTED, fontsize = 9.5)
ax.set_ylabel('Solidification time [s] (log scale)', color = MUTED, fontsize = 9.5)
ax.set_title('Chvorinov solidification time vs. casting modulus\n'
             'four routes, 316 stainless, fixed 100 cm^3 casting volume',
             color = TEXT, fontsize = 11, loc = 'left', pad = 12)

for spine in ax.spines.values():
    spine.set_color(BORDER)
ax.tick_params(colors = MUTED, labelsize = 8.5)
ax.grid(True, color = BORDER, alpha = 0.4, linewidth = 0.7, which = 'both')
ax.set_axisbelow(True)
ax.legend(frameon = False, fontsize = 8.5, labelcolor = TEXT, loc = 'lower right')

fig.tight_layout()

outPath = os.path.join(HERE, 'docs', 'images', 'castingSolidificationTime.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------#

sampleModuli = [0.002, 0.005, 0.010, 0.020, 0.025]
rows = []
for modulus in sampleModuli:
    area = CASTING_VOLUME / modulus
    row = [f'{modulus * 1.0e3:.1f}']
    for process in processes:
        casting = CastingProcess()
        casting.setInputs({'process': process, 'alloyFamily': 'stainless',
                           'castingVolume': CASTING_VOLUME, 'castingSurfaceArea': area})
        row.append(f'{casting.calculateSolidification()["solidificationTime"]:.1f}')
    rows.append(row)

print(formatReportTable(
    rows, ['Modulus [mm]'] + [process.title() for process in processes],
    title = 'PLOTTED SOLIDIFICATION TIME [s], 100 cm^3 CASTING'))

print('\nInput provenance: castingProcesses/castingProcessesLibrary/CastingProcess.py module')
print('constants CASTING_PROCESSES (chvorinovConstant per route) and castingProcesses/tests/')
print('testCastingProcesses.py::testSolidificationTimeScalesWithModulusSquared (castingVolume =')
print('1.0e-4 m^3, the n=2 scaling law) and ::testInvestmentHoldsFinerWallsThanSand (route ordering).')
