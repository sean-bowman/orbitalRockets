
# -- NozzleLosses -- #

'''

What the thrust coefficient efficiency is made of.

The propulsion hub carries a single number, 0.98, described as what a well developed nozzle
achieves. That number is adequate for sizing and it is useless for improving anything, because it
does not say which of three unrelated mechanisms is responsible.

    divergence      the exit flow is not axial. A contour problem, and the only one a designer
                    controls directly
    boundary layer  friction on the wall. A wetted area problem
    kinetic         the chemistry does not keep up with the expansion. A residence time problem

They multiply. For a typical bell they come to 0.995 x 0.990 x 0.995 = 0.980, which is where the
hub's single number comes from, and knowing the split is the difference between shortening a nozzle
and lengthening it.

**This class does not compute a thrust coefficient.** The hub owns that and a second implementation
would be a second thing to keep in agreement. See the README for the two classes this sub-domain
deliberately does not build.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from nozzleUtils import (NOZZLE_CONTOURS, TYPICAL_BOUNDARY_LAYER_LOSS, TYPICAL_KINETIC_LOSS,
                             SUMMERFIELD_SEPARATION_RATIO, divergenceEfficiency,
                             schmuckerSeparationPressure, pressureRatioFromAreaRatio,
                             areaRatioFromPressureRatio, PROPELLANT_COMBINATIONS,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, ContourError, SeparationError)
except ImportError:
    from .nozzleUtils import (NOZZLE_CONTOURS, TYPICAL_BOUNDARY_LAYER_LOSS, TYPICAL_KINETIC_LOSS,
                              SUMMERFIELD_SEPARATION_RATIO, divergenceEfficiency,
                              schmuckerSeparationPressure, pressureRatioFromAreaRatio,
                              areaRatioFromPressureRatio, PROPELLANT_COMBINATIONS,
                              applyInputs, formatReportTable, createErrorContext,
                              InvalidInputError, ContourError, SeparationError)

# ------------------------------------------------------------------------------------------------ #
# -- NozzleLosses -- #
# ------------------------------------------------------------------------------------------------ #

class NozzleLosses:

    '''

    The decomposition of thrust coefficient efficiency into divergence, boundary layer and kinetic
    losses, and the separation limit on area ratio.

    '''

    def __init__(self):

        self.combination     = ''
        self.contour         = ''
        self.areaRatio       = np.nan
        self.chamberPressure = np.nan
        self.ambientPressure = np.nan

        self.properties = {}
        self.findings   = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        requiredParams = {'combination':     str,
                          'areaRatio':       (int, float),
                          'chamberPressure': (int, float)}

        optionalParams = {'contour':         str,
                          'ambientPressure': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.contour:
            self.contour = 'bell 80 per cent'

        if self.contour not in NOZZLE_CONTOURS:
            raise ContourError(
                f'Unknown contour \'{self.contour}\'. Known: {sorted(NOZZLE_CONTOURS)}.',
                context = createErrorContext(component = 'NozzleLosses'))

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise ContourError(
                f'Unknown propellant combination \'{self.combination}\'.',
                context = createErrorContext(component = 'NozzleLosses'))

        self.properties = dict(PROPELLANT_COMBINATIONS[self.combination])

        if not np.isfinite(self.ambientPressure):
            self.ambientPressure = 101325.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def decomposeEfficiency(self) -> dict:

        '''

        The three mechanisms and the product they make.

        The divergence term is the only one a contour designer controls directly, and it is
        frequently the smallest of the three on a well shaped bell. That is the useful finding:
        past a certain point, shaping the contour better stops being where the loss is.

        '''

        findings = []

        contour = NOZZLE_CONTOURS[self.contour]

        divergence = divergenceEfficiency(contour['exitAngle'])

        # boundary layer loss scales with wetted area, which scales with the contour length
        boundaryLayer = 1.0 - TYPICAL_BOUNDARY_LAYER_LOSS * contour['lengthFraction']

        # kinetic loss worsens with expansion, because the residence time falls as the gas thins
        kinetic = 1.0 - TYPICAL_KINETIC_LOSS * np.log(self.areaRatio) / np.log(20.0)

        overall = divergence * boundaryLayer * kinetic

        losses = {'divergence':     1.0 - divergence,
                  'boundary layer': 1.0 - boundaryLayer,
                  'kinetic':        1.0 - kinetic}

        largest = max(losses, key = losses.get)

        findings.append(
            f'{self.contour} at an area ratio of {self.areaRatio:.1f}: divergence '
            f'{divergence:.4f}, boundary layer {boundaryLayer:.4f}, kinetic {kinetic:.4f}, '
            f'overall {overall:.4f}.')

        findings.append(
            f'The largest single loss is {largest} at {losses[largest]:.2%}. That is where effort '
            f'goes, and it is not always the contour.')

        findings.append(
            'The propulsion hub carries a single thrust coefficient efficiency of 0.98. This is '
            'what it decomposes into, and the decomposition is the difference between shortening '
            'a nozzle and lengthening it.')

        self.findings = findings

        return {'divergence':      divergence,
                'boundaryLayer':   boundaryLayer,
                'kinetic':         kinetic,
                'overall':         overall,
                'losses':          losses,
                'largestLoss':     largest,
                'exitAngle':       contour['exitAngle'],
                'lengthFraction':  contour['lengthFraction'],
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def compareContours(self) -> dict:

        '''

        Every contour at the same area ratio, so the divergence against length trade is visible.

        A shorter bell has more divergence loss and less boundary layer loss, and the two move in
        opposite directions. The eighty per cent bell is the common answer because the sum has a
        broad minimum near it rather than because either term is small there.

        '''

        original = self.contour
        results  = {}

        try:
            for name in NOZZLE_CONTOURS:
                self.contour = name
                results[name] = self.decomposeEfficiency()
        finally:
            self.contour = original

        best = max(results, key = lambda name: results[name]['overall'])

        spread = (max(entry['overall'] for entry in results.values())
                  - min(entry['overall'] for entry in results.values()))

        self.findings = [
            f'\'{best}\' is highest at {results[best]["overall"]:.4f}, and the whole set spans '
            f'{spread:.4f}.',
            'A shorter bell has more divergence loss and less boundary layer loss. The two move '
            'in opposite directions, so the sum has a broad minimum and the eighty per cent bell '
            'sits near it rather than at a sharp optimum.',
            'The spread across every contour is smaller than the difference between a good and a '
            'poor injector, which is worth remembering before spending a programme on contour '
            'shape.']

        return {'contours': results, 'best': best, 'spread': spread,
                'findings': self.findings}

    # -------------------------------------------------------------------------------------------- #

    def checkSeparation(self) -> dict:

        '''

        Both separation criteria, and the area ratio each allows.

        Summerfield puts separation at a fixed 0.4 of ambient. Schmucker makes the threshold depend
        on the pressure ratio, and at launch vehicle pressure ratios it is **less conservative**,
        which means it permits a larger area ratio.

        The two disagree by enough to change a design, and reporting only one of them hides that.

        '''

        findings = []

        gamma = self.properties['gamma']

        pressureRatio = pressureRatioFromAreaRatio(gamma, self.areaRatio)
        exitPressure  = pressureRatio * self.chamberPressure

        summerfield = SUMMERFIELD_SEPARATION_RATIO * self.ambientPressure
        schmucker   = schmuckerSeparationPressure(self.chamberPressure, self.ambientPressure)

        separatedBySummerfield = exitPressure < summerfield
        separatedBySchmucker   = exitPressure < schmucker

        # the largest area ratio each criterion permits
        summerfieldLimit = areaRatioFromPressureRatio(gamma, summerfield / self.chamberPressure)
        schmuckerLimit   = areaRatioFromPressureRatio(gamma, schmucker / self.chamberPressure)

        findings.append(
            f'Exit pressure {exitPressure / 1000.0:.1f} kPa against a Summerfield threshold of '
            f'{summerfield / 1000.0:.1f} kPa and a Schmucker threshold of '
            f'{schmucker / 1000.0:.1f} kPa.')

        findings.append(
            f'Summerfield permits an area ratio up to {summerfieldLimit:.1f} and Schmucker up to '
            f'{schmuckerLimit:.1f}, a difference of '
            f'{(schmuckerLimit / summerfieldLimit - 1.0) * 100.0:.0f} per cent.')

        if separatedBySummerfield and not separatedBySchmucker:
            findings.append(
                'The two criteria disagree about this nozzle. Summerfield says it separates and '
                'Schmucker says it does not, and that is a design decision resting on which '
                'correlation is believed. Both are curve fits and neither is a physical limit.')
        elif separatedBySummerfield:
            findings.append(
                'Both criteria say the flow separates. That is a structural problem rather than a '
                'performance one: the separation point moves, the load is unsteady, and it has '
                'destroyed hardware.')
        else:
            findings.append('Neither criterion predicts separation.')

        self.findings = findings

        return {'exitPressure':          exitPressure,
                'summerfieldThreshold':  summerfield,
                'schmuckerThreshold':    schmucker,
                'separatedBySummerfield': bool(separatedBySummerfield),
                'separatedBySchmucker':  bool(separatedBySchmucker),
                'summerfieldLimit':      summerfieldLimit,
                'schmuckerLimit':        schmuckerLimit,
                'criteriaAgree':         bool(separatedBySummerfield == separatedBySchmucker),
                'findings':              findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full loss report.
        '''

        decomposition = self.decomposeEfficiency()
        contours      = self.compareContours()
        separation    = self.checkSeparation()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  NOZZLE LOSSES: {self.contour}, area ratio {self.areaRatio:.1f}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Exit angle',            f'{decomposition["exitAngle"]:.0f}',        'degrees'],
             ['Length fraction',       f'{decomposition["lengthFraction"]:.2f}',   ''],
             ['Divergence efficiency', f'{decomposition["divergence"]:.4f}',       ''],
             ['Boundary layer',        f'{decomposition["boundaryLayer"]:.4f}',    ''],
             ['Kinetic',               f'{decomposition["kinetic"]:.4f}',          ''],
             ['Overall',               f'{decomposition["overall"]:.4f}',          ''],
             ['Largest loss',          decomposition['largestLoss'],               ''],
             ['Exit pressure',         f'{separation["exitPressure"] / 1000.0:.1f}', 'kPa'],
             ['Summerfield limit',     f'{separation["summerfieldLimit"]:.1f}',    'area ratio'],
             ['Schmucker limit',       f'{separation["schmuckerLimit"]:.1f}',      'area ratio']],
            ['Quantity', 'Value', 'Unit'], title = 'Losses'))

        lines.append('')
        lines.append('  Contour comparison at the same area ratio:')
        lines.append('')
        lines.append(f'    {"contour":22s} {"exit":>6s} {"length":>8s} {"diverge":>9s} '
                     f'{"b.layer":>9s} {"overall":>9s}')
        for name, entry in contours['contours'].items():
            marker = '  <-' if name == self.contour else ''
            lines.append(f'    {name:22s} {entry["exitAngle"]:6.0f} '
                         f'{entry["lengthFraction"]:8.2f} {entry["divergence"]:9.4f} '
                         f'{entry["boundaryLayer"]:9.4f} {entry["overall"]:9.4f}{marker}')

        lines.append('')
        for finding in (decomposition['findings'] + contours['findings']
                        + separation['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'nozzle_losses.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.areaRatio <= 1.0:
            raise InvalidInputError(
                f'The area ratio must exceed one, got {self.areaRatio}.',
                context = createErrorContext(component = 'NozzleLosses'))

        for name, value in (('chamber pressure', self.chamberPressure),
                            ('ambient pressure', self.ambientPressure)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}. Use the altitude compensation '
                    f'class for a vacuum case rather than a zero ambient here, because a '
                    f'separation criterion has no meaning in vacuum.',
                    context = createErrorContext(component = 'NozzleLosses'))
