
# -- SeparationSystem -- #

'''

Separation velocity, tipoff rate and whether the two halves actually clear each other.

The separation velocity is the easy number and it is not the one that fails. **Tipoff is.** A set of
springs pushing on a stage produces an angular rate whenever they are not identical, and they are
never identical: spring rate tolerance, friction variation, and a centre of gravity that is not
where the drawing says it is all put a moment into a body that has just lost its structural
connection.

The result that matters is the recontact check. A stage with a healthy separation velocity and a
tipoff rate that rotates it into the interstage before it clears has separated successfully and
then hit itself.

**NASA-STD-5017B is explicit that torque margin does not apply here** where a specific rather than
a minimum separation velocity is required. That is worth knowing before applying a mechanism margin
to a separation system, and it is why this class computes velocities and clearances rather than
margins.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from mechanismUtils import (springEnergy, separationVelocity,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, SeparationError)
except ImportError:
    from .mechanismUtils import (springEnergy, separationVelocity,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, SeparationError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Spring rate tolerance as a fraction of nominal. A commercial compression spring is typically
# supplied to about ten per cent on rate; a selected and matched set is better.
#
# This is the number tipoff is most sensitive to and it is registered as unvalidated.
SPRING_RATE_TOLERANCE = 0.10    # [-]

# Clearance required at the moment the two bodies part company, as a multiple of the computed
# lateral excursion. Two is a convention rather than a standard.
CLEARANCE_FACTOR = 2.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- SeparationSystem -- #
# ------------------------------------------------------------------------------------------------ #

class SeparationSystem:

    '''

    Spring-driven separation: velocity, tipoff rate and the recontact check.

    '''

    def __init__(self):

        self.springCount     = np.nan
        self.springStiffness = np.nan
        self.springStroke    = np.nan
        self.springRadius    = np.nan
        self.separatingMass  = np.nan
        self.remainingMass   = np.nan
        self.inertia         = np.nan
        self.clearanceLength = np.nan
        self.radialGap       = np.nan
        self.rateTolerance   = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `springRadius` is the bolt circle the springs sit on, which is the moment arm for tipoff.

        `clearanceLength` is how far the separating body has to travel before it is clear of the
        body it left, and `radialGap` is how much lateral room it has while doing so.

        `inertia` is the transverse moment of inertia of the separating body about its own centre
        of gravity, and it is required rather than defaulted. An earlier version estimated it from
        the bolt circle radius, which is the wrong length entirely: a stage's transverse inertia is
        dominated by its length, and a bolt-circle estimate understates it by an order of magnitude
        and therefore overstates the tipoff rate by the same factor.

        '''

        requiredParams = {'springCount':     (int, float),
                          'springStiffness': (int, float),
                          'springStroke':    (int, float),
                          'springRadius':    (int, float),
                          'separatingMass':  (int, float),
                          'remainingMass':   (int, float),
                          'inertia':         (int, float)}

        optionalParams = {'clearanceLength': (int, float),
                          'radialGap':       (int, float),
                          'rateTolerance':   (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.rateTolerance):
            self.rateTolerance = SPRING_RATE_TOLERANCE

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateVelocity(self) -> dict:

        '''

        Total stored energy and the relative separation velocity it produces.

        '''

        perSpring = springEnergy(self.springStiffness, self.springStroke)

        total = self.springCount * perSpring

        relative = separationVelocity(total, self.separatingMass, self.remainingMass)

        # the velocity splits in inverse proportion to mass
        separating = relative * self.remainingMass / (self.separatingMass + self.remainingMass)
        remaining  = relative * self.separatingMass / (self.separatingMass + self.remainingMass)

        return {'energyPerSpring':  perSpring,
                'totalEnergy':      total,
                'relativeVelocity': relative,
                'separatingVelocity': separating,
                'remainingVelocity':  remaining,
                'massRatio':        self.separatingMass / self.remainingMass}

    # -------------------------------------------------------------------------------------------- #

    def calculateTipoff(self) -> dict:

        '''

        Angular rate imparted by spring force mismatch.

        The springs act over the same stroke, so a spring that is stiffer than its neighbours
        delivers more impulse. With the springs on a bolt circle, an imbalance produces a net
        moment about a transverse axis, and the body leaves rotating.

        Two cases are computed and the difference between them is the useful part.

        **The deterministic worst case** puts the springs on one side of the bolt circle at the top
        of tolerance and those on the other at the bottom. That imbalance is *independent of how
        many springs there are*: half of them at plus ten per cent and half at minus ten per cent
        produce the same net moment whether there are four springs or forty.

        **The statistical case** treats the rate errors as independent random draws and combines
        them by root sum of squares, which falls as one over the square root of the count.

        So more springs help only if the tolerances are random rather than adversarially arranged.
        That is a real design question rather than a modelling detail: springs from one production
        lot are correlated, and a set that has been measured and matched in opposing pairs is
        deliberately arranged to cancel. **A separation system with many springs and no matching
        requirement has bought the statistical case and specified the worst one.**

        '''

        findings = []

        velocity = self.calculateVelocity()

        # the total impulse delivered to the separating body, shared equally at nominal rate. An
        # earlier version computed each spring's impulse as though it alone acted on the whole
        # mass, which overstated it by the square root of the spring count.
        totalImpulse = self.separatingMass * velocity['separatingVelocity']

        perSpring = totalImpulse / self.springCount

        # impulse scales with the square root of energy at fixed stroke, and energy scales with
        # stiffness, so a spring at the top of tolerance delivers sqrt(1 + tol) times nominal
        highImpulse = np.sqrt(1.0 + self.rateTolerance)
        lowImpulse  = np.sqrt(1.0 - self.rateTolerance)

        # worst case: half the springs at the top of tolerance on one side of the bolt circle and
        # half at the bottom on the other
        halfCount = self.springCount / 2.0

        momentImpulse = (halfCount * perSpring * (highImpulse - lowImpulse) * self.springRadius)

        rate = momentImpulse / self.inertia

        # the statistical case: independent rate errors combined by root sum of squares. Each
        # spring contributes its own deviation about the mean at its own moment arm, and the arms
        # around a bolt circle contribute a factor of one over root two in the transverse plane.
        perSpringDeviation = perSpring * 0.5 * (highImpulse - lowImpulse)

        statisticalImpulse = (perSpringDeviation * np.sqrt(self.springCount)
                              * self.springRadius / np.sqrt(2.0))

        statisticalRate = statisticalImpulse / self.inertia

        findings.append(
            f'A spring rate tolerance of {self.rateTolerance:.0%} gives '
            f'{np.degrees(rate):.3f} degrees per second in the deterministic worst case and '
            f'{np.degrees(statisticalRate):.3f} treating the errors as independent.')

        findings.append(
            'Tipoff comes from the mismatch, not from the average. Both the velocity and the '
            'tipoff rate scale with the square root of spring stiffness, so a stronger spring '
            'raises both in the same proportion and **the rotation accumulated while clearing does '
            'not move at all**. A stronger spring buys separation velocity and no recontact '
            'margin, which is the opposite of the intuition.')

        findings.append(
            '**The worst case does not improve with spring count and the statistical case does.** '
            'Half the springs high and half low produce the same net moment however many there '
            'are, so adding springs buys a better expected outcome and no better bound. Matching '
            'the springs in opposing pairs is what attacks the bound.')

        self.findings = findings

        return {'rate':                    rate,
                'rateDegrees':             float(np.degrees(rate)),
                'statisticalRate':         statisticalRate,
                'statisticalRateDegrees':  float(np.degrees(statisticalRate)),
                'momentImpulse':           momentImpulse,
                'inertia':                 self.inertia,
                'rateTolerance':           self.rateTolerance,
                'findings':                findings}

    # -------------------------------------------------------------------------------------------- #

    def checkRecontact(self) -> dict:

        '''

        Whether the separating body clears before the tipoff rotation closes the gap.

        The body translates at the separation velocity and rotates at the tipoff rate. The lateral
        excursion at the far end of the clearance length is what has to stay inside the radial gap.

        **This is refused rather than reported when it fails**, because a separation that
        recontacts is a lost mission and not a degraded one.

        '''

        if not np.isfinite(self.clearanceLength) or not np.isfinite(self.radialGap):
            raise InvalidInputError(
                'A clearance length and a radial gap are needed to check recontact. Without them '
                'the separation velocity and tipoff rate are numbers rather than a verdict.',
                context = createErrorContext(component = 'SeparationSystem'))

        findings = []

        velocity = self.calculateVelocity()
        tipoff   = self.calculateTipoff()

        clearTime = self.clearanceLength / velocity['relativeVelocity']

        rotation = tipoff['rate'] * clearTime

        # lateral excursion of the trailing edge, which is the part still inside the interface
        excursion = self.clearanceLength * np.sin(rotation)

        required = CLEARANCE_FACTOR * excursion

        findings.append(
            f'The body takes {clearTime * 1000.0:.0f} ms to travel {self.clearanceLength * 1000.0:.0f} mm '
            f'at {velocity["relativeVelocity"]:.2f} m/s.')

        findings.append(
            f'In that time it rotates {np.degrees(rotation):.3f} degrees, giving a lateral '
            f'excursion of {excursion * 1000.0:.1f} mm against a radial gap of '
            f'{self.radialGap * 1000.0:.1f} mm.')

        if excursion >= self.radialGap:
            raise SeparationError(
                f'The separating body rotates {np.degrees(rotation):.3f} degrees while clearing, '
                f'giving a lateral excursion of {excursion * 1000.0:.1f} mm against a radial gap '
                f'of {self.radialGap * 1000.0:.1f} mm. **It recontacts.** That is a lost mission '
                f'rather than a degraded separation, so it is refused rather than reported with a '
                f'negative margin. Raise the separation velocity, tighten the spring matching, or '
                f'open the gap.',
                context = createErrorContext(component = 'SeparationSystem'))

        clears = bool(required <= self.radialGap)

        if clears:
            findings.append(
                f'It clears with a factor of {self.radialGap / excursion:.1f} on the excursion.')
        else:
            findings.append(
                f'It clears, and only by a factor of {self.radialGap / excursion:.1f} against a '
                f'convention of {CLEARANCE_FACTOR:.0f}. That is not a failure and it is not a '
                f'design anybody should be comfortable with.')

        self.findings = findings

        return {'clearTime':      clearTime,
                'rotation':       rotation,
                'rotationDegrees': float(np.degrees(rotation)),
                'excursion':      excursion,
                'radialGap':      self.radialGap,
                'clearanceFactor': self.radialGap / excursion,
                'meetsConvention': clears,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def compareSpringCounts(self, counts: list = None) -> dict:

        '''

        Separation velocity and tipoff across spring counts, holding the total energy constant.

        The result is not the one this method was written expecting. **The deterministic worst
        case is flat in spring count** and only the statistical case improves, as one over the root
        of the count.

        So adding springs buys a better expected tipoff and no better bound, and a programme that
        needs the bound has to match the springs rather than multiply them.

        '''

        if counts is None:
            counts = [2, 4, 6, 8, 12]

        original = (self.springCount, self.springStiffness)

        totalEnergy = self.springCount * springEnergy(self.springStiffness, self.springStroke)

        results = {}

        try:
            for count in counts:

                if count < 2:
                    continue

                self.springCount     = count
                self.springStiffness = (2.0 * totalEnergy
                                        / (count * self.springStroke ** 2))

                tipoff = self.calculateTipoff()

                results[count] = {
                    'stiffness':   self.springStiffness,
                    'velocity':    self.calculateVelocity()['relativeVelocity'],
                    'tipoff':      tipoff['rateDegrees'],
                    'statistical': tipoff['statisticalRateDegrees']}

        finally:
            self.springCount, self.springStiffness = original

        best = min(results, key = lambda count: results[count]['statistical'])

        worstCaseSpread = (max(entry['tipoff'] for entry in results.values())
                           - min(entry['tipoff'] for entry in results.values()))

        return {'results':           results,
                'lowestStatistical': best,
                'worstCaseIsFlat':   bool(worstCaseSpread < 1.0e-9),
                'totalEnergy':       totalEnergy}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full separation report.
        '''

        velocity = self.calculateVelocity()
        tipoff   = self.calculateTipoff()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  SEPARATION SYSTEM: {self.springCount:.0f} springs, '
                     f'{self.separatingMass:.0f} kg separating from {self.remainingMass:.0f} kg')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Energy per spring',    f'{velocity["energyPerSpring"]:.1f}',        'J'],
             ['Total energy',         f'{velocity["totalEnergy"]:.1f}',            'J'],
             ['Relative velocity',    f'{velocity["relativeVelocity"]:.3f}',       'm/s'],
             ['Separating body',      f'{velocity["separatingVelocity"]:.3f}',     'm/s'],
             ['Remaining body',       f'{velocity["remainingVelocity"]:.3f}',      'm/s'],
             ['Tipoff rate',          f'{tipoff["rateDegrees"]:.3f}',              'deg/s']],
            ['Quantity', 'Value', 'Unit'], title = 'Separation'))

        lines.append('')
        for finding in tipoff['findings']:
            lines.append(f'    - {finding}')

        if np.isfinite(self.clearanceLength) and np.isfinite(self.radialGap):

            recontact = self.checkRecontact()

            lines.append('')
            for finding in recontact['findings']:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'separation_system.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.springCount < 2:
            raise SeparationError(
                f'A separation system needs at least two springs, got {self.springCount}. One '
                f'spring is a moment about the centre of gravity rather than a separation system, '
                f'and the tipoff calculation here assumes a symmetric set.',
                context = createErrorContext(component = 'SeparationSystem'))

        for name, value in (('spring stiffness', self.springStiffness),
                            ('spring stroke',    self.springStroke),
                            ('spring radius',    self.springRadius),
                            ('separating mass',  self.separatingMass),
                            ('remaining mass',   self.remainingMass),
                            ('inertia',          self.inertia)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'SeparationSystem'))

        if not 0.0 <= self.rateTolerance < 1.0:
            raise InvalidInputError(
                f'The spring rate tolerance must lie in [0, 1), got {self.rateTolerance}. At one '
                f'a spring can have zero rate, which is not a tolerance but a failure.',
                context = createErrorContext(component = 'SeparationSystem'))

        if np.isfinite(self.radialGap) and self.radialGap <= 0.0:
            raise InvalidInputError(
                f'The radial gap must be positive, got {self.radialGap}.',
                context = createErrorContext(component = 'SeparationSystem'))
