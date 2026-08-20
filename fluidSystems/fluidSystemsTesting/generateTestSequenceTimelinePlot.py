
# -- Test Sequence Timeline Figure Generator [fluidSystems/fluidSystemsTesting] -- #

'''

Renders the qualification and acceptance test sequences from the thruster valve campaign worked
example as a two-panel horizontal timeline. `codeInterface.py` builds a `TestCampaign`, calls
`campaign.buildMatrix()`, and prints the two sequences as tables; this script reads the same
`campaign.qualificationSequence` and `campaign.acceptanceSequence` lists of dicts (each carrying
the catalogue's `sequence` position, `name`, `purpose` and `destructive` flag) that `buildMatrix()`
populates, rather than re-deriving the catalogue or scraping the printed tables.

`codeInterface.py` has no `if __name__ == '__main__':` guard, so loading it by explicit path runs
the entire worked example on import (it even clears the terminal with `os.system('cls')`). That is
harmless here: it leaves `campaign` fully built as a module attribute, which is all this script
needs.

The x-position of each test is its real catalogue `sequence` number, not a row index, so the gaps
in the numbering are visible: sequence 95, 100 and 105 (thermal vacuum, cryogenic functional, leak
at temperature) are absent because this article is tailored non-cryogenic and thermal vacuum is
tailored out, and the jump from 120 to 200 for burst pressure is the real distance the catalogue
puts between the last non-destructive test and the one that destroys the article.

Run it with:

    python generateTestSequenceTimelinePlot.py

Writes docs/images/testSequenceTimeline.png and prints both sequences plotted.

Author: Sean Bowman
Date:   08/17/2026

'''

import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'fluidSystemsTestingLibrary'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from campaignUtils import formatReportTable

#--------------------------------------------------------------------------------------------------------------------------#
# -- Load the Worked Example (runs fully on import; no main() guard) -- #
#--------------------------------------------------------------------------------------------------------------------------#

ciPath = os.path.join(HERE, 'codeInterface.py')
spec   = importlib.util.spec_from_file_location('fluidSystemsTestingSequenceCI', ciPath)
ci     = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

qualificationSequence = ci.campaign.qualificationSequence   # [{sequence, name, purpose, destructive}, ...]
acceptanceSequence    = ci.campaign.acceptanceSequence

#--------------------------------------------------------------------------------------------------------------------------#
# -- Figure -- #
#--------------------------------------------------------------------------------------------------------------------------#

BG     = '#1a1e2a'
BORDER = '#3a4055'
TEXT   = '#d8e0ec'
MUTED  = '#8a95a8'
ACCENT = '#E0975A'
RED    = '#e08080'

fig, (axQual, axAccept) = plt.subplots(2, 1, figsize = (9.5, 8.0),
                                       gridspec_kw = {'height_ratios': [len(qualificationSequence),
                                                                        len(acceptanceSequence)]})
fig.patch.set_facecolor(BG)

maxSequence = max(entry['sequence'] for entry in qualificationSequence) * 1.06

for ax, sequence, label in ((axQual, qualificationSequence, 'QUALIFICATION (dedicated articles)'),
                            (axAccept, acceptanceSequence, 'ACCEPTANCE (every flight article)')):

    ax.set_facecolor(BG)

    positions = np.arange(len(sequence))
    xValues   = [entry['sequence'] for entry in sequence]
    colors    = [RED if entry['destructive'] else ACCENT for entry in sequence]
    labels    = [entry['name'] for entry in sequence]

    ax.barh(positions, xValues, color = colors, height = 0.55, left = 0, edgecolor = 'none', zorder = 3)

    for y, x, entry in zip(positions, xValues, sequence):
        tag = '  DESTRUCTIVE' if entry['destructive'] else ''
        ax.text(x + maxSequence * 0.012, y, f'{entry["name"]}{tag}', va = 'center', ha = 'left',
                color = RED if entry['destructive'] else TEXT, fontsize = 8.5, zorder = 4)

    ax.set_yticks(positions)
    ax.set_yticklabels([f'{x:.0f}' for x in xValues], color = MUTED, fontsize = 7.5)
    ax.set_ylabel('sequence #', color = MUTED, fontsize = 8)
    ax.invert_yaxis()
    ax.set_xlim(0, maxSequence)

    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.tick_params(colors = MUTED, labelsize = 8)
    ax.xaxis.grid(True, color = BORDER, alpha = 0.35, linewidth = 0.6, zorder = 0)
    ax.set_axisbelow(True)
    ax.set_title(f'{label}, {len(sequence)} tests', color = TEXT, fontsize = 9.5, loc = 'left', pad = 6)

axAccept.set_xlabel('Catalogue sequence position (proof before leak, life before final functional, burst last)',
                    color = MUTED, fontsize = 9)

fig.suptitle('Qualification and acceptance test sequence, thruster isolation valve\n'
             'one destructive test ends qualification; acceptance is a 10-test non-destructive subset',
             color = TEXT, fontsize = 11, x = 0.01, ha = 'left', y = 0.995)

fig.tight_layout(rect = (0, 0, 1, 0.93))

outPath = os.path.join(HERE, 'docs', 'images', 'testSequenceTimeline.png')
os.makedirs(os.path.dirname(outPath), exist_ok = True)
fig.savefig(outPath, dpi = 150, bbox_inches = 'tight', facecolor = fig.get_facecolor())
print(f'\nWrote {outPath}')

#--------------------------------------------------------------------------------------------------------------------------#
# -- Summary Table -- #
#--------------------------------------------------------------------------------------------------------------------------#

rows = [['Qualification', str(index + 1), f'{entry["sequence"]:.0f}', entry['name'],
        'DESTRUCTIVE' if entry['destructive'] else '']
        for index, entry in enumerate(qualificationSequence)]
rows += [['Acceptance', str(index + 1), f'{entry["sequence"]:.0f}', entry['name'],
         'DESTRUCTIVE' if entry['destructive'] else '']
         for index, entry in enumerate(acceptanceSequence)]

print(formatReportTable(rows, ['Level', '#', 'Sequence', 'Test', 'Flag'],
                        title = 'PLOTTED TEST SEQUENCE TIMELINE'))
