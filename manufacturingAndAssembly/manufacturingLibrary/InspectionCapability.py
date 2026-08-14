
# -- InspectionCapability -- #

'''

What an inspection actually establishes, which is less than people assume and is a number.

An inspection does not find flaws. It finds flaws with a probability that depends on their size,
and MIL-HDBK-1823A models that probability with a log-odds curve:

    POD(a) = 1 / ( 1 + (a50 / a) ** (1 / sigma) )

Two sizes come off it and both are named in the standard. **a50** is the size found half the time.
**a90** is the size found nine times in ten, and its ratio to a50 is fixed by sigma alone:

    a90 / a50 = 9 ** sigma

**a90/95 is a different kind of number and the difference matters.** It is the 95 per cent
confidence bound on the ESTIMATE of a90, so it depends on how many specimens the demonstration used
as well as on the inspection itself. The handbook notes that it has become a de facto design
criterion, which means **the flaw size a programme designs to is partly a statement about how many
specimens somebody paid for.**

The result this class exists to produce sits at the interface with damage tolerance.

**If the reliably detectable flaw size is larger than the critical flaw size, the inspection
establishes nothing.** It cannot rule out a flaw big enough to fail the part, so the part is not
inspectable in any useful sense and has to be proof tested, life limited, or made from something
with a larger critical flaw. That is a design conclusion rather than an inspection finding, and it
is the one that gets discovered late.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from manufacturingUtils import (NDE_METHODS, MINIMUM_HIT_MISS_TARGETS,
                                    MINIMUM_SIGNAL_TARGETS, UNFLAWED_SITE_RATIO,
                                    logOddsPod, podSize,
                                    applyInputs, formatReportTable, createErrorContext,
                                    InvalidInputError, InspectionError)
except ImportError:
    from .manufacturingUtils import (NDE_METHODS, MINIMUM_HIT_MISS_TARGETS,
                                     MINIMUM_SIGNAL_TARGETS, UNFLAWED_SITE_RATIO,
                                     logOddsPod, podSize,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, InspectionError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The margin demanded between the reliably detectable size and the critical flaw size. A ratio of
# one means the inspection just barely rules out failure, with nothing left for the flaw to grow in
# service between inspections.
DEFAULT_DETECTION_MARGIN = 2.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- InspectionCapability -- #
# ------------------------------------------------------------------------------------------------ #

class InspectionCapability:

    '''

    Probability of detection against flaw size, the sizes the standard names, the demonstration a
    capability claim needs, and whether the inspection establishes anything at all.

    '''

    def __init__(self):

        self.method            = ''
        self.a50               = np.nan
        self.sigma             = np.nan
        self.criticalFlawSize  = np.nan
        self.detectionMargin   = np.nan
        self.demonstrationTargets = np.nan
        self.responseType      = ''

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `method` selects a representative capability from NDE_METHODS. `a50` and `sigma` override
        it with a demonstrated curve, which is what a real programme has.

        `criticalFlawSize` comes from a damage tolerance calculation, which aerospaceMaterials owns.
        It is what turns a detection curve into a verdict.

        `responseType` is 'hitMiss' or 'signal', which sets the minimum demonstration size the
        standard asks for.

        '''

        requiredParams = {'method': str}

        optionalParams = {'a50':               (int, float),
                          'sigma':             (int, float),
                          'criticalFlawSize':  (int, float),
                          'detectionMargin':   (int, float),
                          'demonstrationTargets': (int, float),
                          'responseType':      str}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.responseType:
            self.responseType = 'hitMiss'

        if not np.isfinite(self.detectionMargin):
            self.detectionMargin = DEFAULT_DETECTION_MARGIN

        self._validateInputs()

        if not np.isfinite(self.a50):
            self.a50 = NDE_METHODS[self.method]['a50']

        if not np.isfinite(self.sigma):
            self.sigma = NDE_METHODS[self.method]['sigma']

    # -------------------------------------------------------------------------------------------- #

    def detectionCurve(self, sizes: list = None) -> dict:

        '''

        Probability of detection against flaw size, and the two sizes the standard names.

        '''

        a50 = self.a50
        a90 = podSize(0.90, a50, self.sigma)

        if sizes is None:
            sizes = list(np.geomspace(a50 / 5.0, a90 * 4.0, 8))

        curve = [{'flawSize':    float(size),
                  'probability': float(logOddsPod(size, a50, self.sigma))}
                 for size in sizes]

        return {'method':     self.method,
                'a50':        a50,
                'a90':        a90,
                'a10':        podSize(0.10, a50, self.sigma),
                'sigma':      self.sigma,
                'a90OverA50': a90 / a50,
                'nineToTheSigma': 9.0 ** self.sigma,
                'curve':      curve}

    # -------------------------------------------------------------------------------------------- #

    def demonstrationSize(self, targets: float = None) -> dict:

        '''

        The demonstration a capability claim needs, per MIL-HDBK-1823A section 4.5.2.2.

        Sixty targets for a binary hit or miss response, forty for a quantitative one, and at least
        three times as many unflawed sites as flawed ones so a false positive rate can be estimated.

        **These are minimums rather than targets.** The handbook states that 120 binary
        opportunities give a significantly more precise a50 and therefore a smaller a90/95, which
        is the point worth carrying: a bigger demonstration produces a better number for the same
        inspection.

        '''

        count = targets if targets is not None else self.demonstrationTargets

        minimum = (MINIMUM_HIT_MISS_TARGETS if self.responseType == 'hitMiss'
                   else MINIMUM_SIGNAL_TARGETS)

        result = {'responseType':     self.responseType,
                  'minimumTargets':   minimum,
                  'unflawedSites':    minimum * UNFLAWED_SITE_RATIO,
                  'totalSites':       minimum * (1 + UNFLAWED_SITE_RATIO),
                  'preciseTargets':   2 * MINIMUM_HIT_MISS_TARGETS}

        if np.isfinite(count):

            result['targets'] = float(count)
            result['meetsMinimum'] = count >= minimum

            if count < minimum:
                raise InspectionError(
                    f'A demonstration of {count:.0f} targets is below the {minimum} the standard '
                    f'asks for a {self.responseType} response. A detection curve fitted to fewer '
                    f'is a curve with confidence bounds too wide to design against, and a90/95 is '
                    f'a confidence bound.',
                    context = {'targets':      count,
                               'minimum':      minimum,
                               'responseType': self.responseType})

        return result

    # -------------------------------------------------------------------------------------------- #

    def checkAgainstCriticalFlaw(self) -> dict:

        '''

        Whether the inspection establishes anything, given the critical flaw size.

        Raises where the reliably detectable size exceeds the critical size, because an inspection
        that cannot rule out a flaw large enough to fail the part has not established that the part
        is safe. **That is a design conclusion rather than an inspection finding**, and reporting it
        as a margin invites somebody to accept the margin.

        '''

        if not np.isfinite(self.criticalFlawSize):
            raise InspectionError(
                'A critical flaw size is needed to say whether the inspection establishes '
                'anything. It comes from a damage tolerance calculation, which aerospaceMaterials '
                'owns, and there is no sensible default for it.')

        curve = self.detectionCurve()
        a90 = curve['a90']

        required = a90 * self.detectionMargin
        margin = self.criticalFlawSize / required

        probabilityAtCritical = float(logOddsPod(self.criticalFlawSize, self.a50, self.sigma))
        missedAtCritical = 1.0 - probabilityAtCritical

        result = {'method':               self.method,
                  'a90':                  a90,
                  'criticalFlawSize':     self.criticalFlawSize,
                  'detectionMargin':      self.detectionMargin,
                  'requiredCriticalSize': required,
                  'margin':               margin,
                  'probabilityAtCritical': probabilityAtCritical,
                  'missedAtCritical':     missedAtCritical}

        if self.criticalFlawSize <= a90:
            raise InspectionError(
                f'The critical flaw size of {self.criticalFlawSize * 1000.0:.3f} mm is at or below '
                f'the {a90 * 1000.0:.3f} mm this inspection finds nine times in ten, so it misses '
                f'{missedAtCritical * 100.0:.0f} per cent of flaws large enough to fail the part. '
                f'**The inspection establishes nothing.** The part has to be proof tested, life '
                f'limited, or made from something with a larger critical flaw.',
                context = {'method':           self.method,
                           'a90':              a90,
                           'criticalFlawSize': self.criticalFlawSize,
                           'missedAtCritical': missedAtCritical})

        return result

    # -------------------------------------------------------------------------------------------- #

    def compareMethods(self, methods: list = None) -> dict:

        '''

        Every inspection method against the same critical flaw size.

        **Cost and capability are correlated and not proportional**, and the ranking by a90 is not
        the ranking by usefulness: a method that reaches inside the part is worth more than a more
        sensitive one that only sees a surface, if the flaw is inside.

        '''

        if methods is None:
            methods = list(NDE_METHODS)

        originalMethod = self.method
        originalA50 = self.a50
        originalSigma = self.sigma

        results = []

        try:
            for method in methods:

                entry = NDE_METHODS[method]

                self.method = method
                self.a50 = entry['a50']
                self.sigma = entry['sigma']

                curve = self.detectionCurve()

                record = {'method':        method,
                          'a50':           curve['a50'],
                          'a90':           curve['a90'],
                          'relativeCost':  entry['relativeCost'],
                          'finds':         entry['finds'],
                          'misses':        entry['misses']}

                if np.isfinite(self.criticalFlawSize):
                    record['establishesSomething'] = self.criticalFlawSize > curve['a90']
                    record['probabilityAtCritical'] = float(
                        logOddsPod(self.criticalFlawSize, self.a50, self.sigma))

                results.append(record)

        finally:
            self.method = originalMethod
            self.a50 = originalA50
            self.sigma = originalSigma

        results.sort(key = lambda entry: entry['a90'])

        capable = [entry for entry in results if entry.get('establishesSomething')]

        return {'results':        results,
                'best':           results[0]['method'],
                'cheapestCapable': (min(capable, key = lambda entry: entry['relativeCost'])['method']
                                    if capable else None),
                'a90Spread':      results[-1]['a90'] / results[0]['a90'],
                'costSpread':     (max(entry['relativeCost'] for entry in results)
                                   / min(entry['relativeCost'] for entry in results))}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The curve, the sizes, the demonstration and the critical flaw check.
        '''

        curve = self.detectionCurve()
        demonstration = self.demonstrationSize(targets = None)

        lines = []

        lines.append(formatReportTable(
            [[f'{entry["flawSize"] * 1000.0:.3f}', f'{entry["probability"] * 100.0:.1f}%']
             for entry in curve['curve']],
            ['flaw size [mm]', 'probability of detection'],
            title = f'DETECTION CURVE, {self.method.upper()}'))

        lines.append('')
        lines.append(f'a50 {curve["a50"] * 1000.0:.3f} mm, a90 {curve["a90"] * 1000.0:.3f} mm, '
                     f'a ratio of {curve["a90OverA50"]:.2f} which is 9 to the power sigma.')
        lines.append(f'A {self.responseType} demonstration needs at least '
                     f'{demonstration["minimumTargets"]} targets and '
                     f'{demonstration["unflawedSites"]} unflawed sites.')

        if np.isfinite(self.criticalFlawSize):

            lines.append('')

            try:
                check = self.checkAgainstCriticalFlaw()
                lines.append(f'Critical flaw {check["criticalFlawSize"] * 1000.0:.3f} mm against a '
                             f'required {check["requiredCriticalSize"] * 1000.0:.3f} mm, a margin '
                             f'of {check["margin"]:.2f}.')
                lines.append(f'At the critical size the inspection finds '
                             f'{check["probabilityAtCritical"] * 100.0:.1f} per cent.')
            except InspectionError as error:
                lines.append('CRITICAL FLAW CHECK FAILED')
                lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'inspectionCapability.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if self.method not in NDE_METHODS:
            raise InvalidInputError(
                f'{self.method} is not an inspection method in the table. Available: '
                f'{sorted(NDE_METHODS)}.')

        if self.responseType not in ('hitMiss', 'signal'):
            raise InvalidInputError("Response type must be 'hitMiss' or 'signal'. The standard "
                                    'asks for different demonstration sizes for each.')

        if np.isfinite(self.a50) and self.a50 <= 0.0:
            raise InvalidInputError('a50 must be positive.')

        if np.isfinite(self.sigma) and self.sigma <= 0.0:
            raise InvalidInputError('sigma must be positive. It sets how steeply the curve rises '
                                    'and a zero would be a perfect inspection with a threshold.')

        if np.isfinite(self.criticalFlawSize) and self.criticalFlawSize <= 0.0:
            raise InvalidInputError('Critical flaw size must be positive.')

        if self.detectionMargin < 1.0:
            raise InvalidInputError(
                'A detection margin below one means the reliably detectable size exceeds the '
                'critical size, which is the failure this class exists to catch rather than a '
                'setting.')
