
# -- ClampBand -- #

'''

Marman band preload, what it loses in storage, and the energy it releases when it lets go.

A clamp band is a tension band around a pair of V-section flanges. The wedge turns a modest band
tension into a large axial preload, and that amplification is the whole reason a light band holds a
stage on: at a fifteen degree wedge it is about twenty-three to one.

Three things are worth computing and the second is the one that fails.

**The preload**, which has to exceed the flight loads with margin or the joint gaps and the
interface fails in a way no static analysis predicted.

**What is left of it after storage.** Preload relaxes: embedment flattens surface asperities within
hours, and creep continues for months. A band installed to a comfortable margin and flown a year
later is a different joint, and this is the failure mode the domain ethos names explicitly.

**The energy released at separation**, which is the shock source. Everything nearby pays for a fast
release, and the shock is the price of not having a slow one.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from mechanismUtils import (clampBandPreload, PRELOAD_RELAXATION, TYPICAL_WEDGE_ANGLE,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, MarginError)
except ImportError:
    from .mechanismUtils import (clampBandPreload, PRELOAD_RELAXATION, TYPICAL_WEDGE_ANGLE,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, MarginError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Required ratio of retained preload to the maximum flight separating load. Below this the joint
# can gap, and a gapping joint under vibration is a fretting and fatigue problem rather than a
# static one.
#
# A factor of 1.2 on preload against limit load is common practice and it is a convention.
PRELOAD_MARGIN = 1.2    # [-]

# Friction coefficient between the band and the flange wedge faces. It opposes the band tightening
# and it opposes the band releasing, so it appears twice with opposite signs.
BAND_FRICTION = 0.15    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- ClampBand -- #
# ------------------------------------------------------------------------------------------------ #

class ClampBand:

    '''

    Preload, relaxation over storage, release margin and the released strain energy.

    '''

    def __init__(self):

        self.bandTension    = np.nan
        self.wedgeAngle     = np.nan
        self.interfaceRadius = np.nan
        self.bandArea       = np.nan
        self.bandModulus    = np.nan
        self.flightLoad     = np.nan
        self.storageMonths  = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `bandTension` is the tension installed in the band, which is what a torque wrench on the
        tensioning bolt actually sets. `flightLoad` is the maximum axial load trying to separate
        the joint in flight.

        '''

        requiredParams = {'bandTension':     (int, float),
                          'interfaceRadius': (int, float)}

        optionalParams = {'wedgeAngle':    (int, float),
                          'bandArea':      (int, float),
                          'bandModulus':   (int, float),
                          'flightLoad':    (int, float),
                          'storageMonths': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.wedgeAngle):
            self.wedgeAngle = TYPICAL_WEDGE_ANGLE

        if not np.isfinite(self.bandModulus):
            self.bandModulus = 200.0e9

        if not np.isfinite(self.storageMonths):
            self.storageMonths = 0.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculatePreload(self) -> dict:

        '''

        Axial preload from the band tension, and the wedge amplification that produces it.

        '''

        ideal = clampBandPreload(self.bandTension, self.wedgeAngle)

        # friction on the wedge faces opposes the band tightening, so less of the tension reaches
        # the joint than the frictionless wedge relation suggests
        wedge = np.radians(self.wedgeAngle)

        efficiency = ((np.tan(wedge) )
                      / (np.tan(wedge) + BAND_FRICTION))

        delivered = ideal * efficiency

        return {'bandTension':   self.bandTension,
                'wedgeAngle':    self.wedgeAngle,
                'idealPreload':  ideal,
                'amplification': ideal / self.bandTension,
                'wedgeEfficiency': efficiency,
                'deliveredPreload': delivered}

    # -------------------------------------------------------------------------------------------- #

    def calculateRelaxation(self) -> dict:

        '''

        What is left of the preload after embedment and storage, and whether the joint still holds.

        Embedment happens within hours of installation as surface asperities flatten under the
        contact pressure. Short-term relaxation continues over weeks. Storage relaxation continues
        for as long as the vehicle sits, and it is the term nobody plans for because it depends on
        a schedule rather than on a design.

        **This is the failure mode the domain ethos names**, and the reason is that all three losses
        are small and they compound.

        '''

        findings = []

        preload = self.calculatePreload()

        installed = preload['deliveredPreload']

        losses = {'embedment': PRELOAD_RELAXATION['embedment'],
                  'shortTerm': PRELOAD_RELAXATION['shortTerm']}

        if self.storageMonths > 0.0:
            # storage relaxation is treated as accruing over the first year and then flattening,
            # which is the shape of a creep curve and is a model rather than a measurement
            losses['storage'] = (PRELOAD_RELAXATION['storage']
                                 * min(self.storageMonths / 12.0, 1.0))

        retained = installed

        for fraction in losses.values():
            retained *= (1.0 - fraction)

        totalLoss = 1.0 - retained / installed

        findings.append(
            f'Installed preload {installed / 1000.0:.1f} kN, retained '
            f'{retained / 1000.0:.1f} kN after {totalLoss:.1%} total relaxation.')

        detail = ', '.join(f'{name} {fraction:.1%}' for name, fraction in losses.items())

        findings.append(f'The losses compound rather than adding: {detail}.')

        if self.storageMonths > 0.0:
            findings.append(
                f'{self.storageMonths:.0f} months of storage contributes '
                f'{losses.get("storage", 0.0):.1%} of that, and it is the term that depends on a '
                f'schedule rather than on a design.')

        self.findings = findings

        return {'installedPreload': installed,
                'retainedPreload':  retained,
                'losses':           losses,
                'totalLoss':        totalLoss,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def checkJoint(self) -> dict:

        '''

        Whether the retained preload still holds the joint closed against the flight load.

        Refused rather than reported when it does not, because a clamp band that gaps in flight is
        not a joint with a negative margin, it is a stage coming apart at the wrong moment.

        '''

        if not np.isfinite(self.flightLoad):
            raise InvalidInputError(
                'A flight load is needed to check the joint. Without it the preload is a number '
                'rather than a margin.',
                context = createErrorContext(component = 'ClampBand'))

        relaxation = self.calculateRelaxation()

        retained = relaxation['retainedPreload']

        margin = retained / (PRELOAD_MARGIN * self.flightLoad) - 1.0

        if margin < 0.0:
            raise MarginError(
                f'The retained preload of {retained / 1000.0:.1f} kN does not hold the joint '
                f'against a flight load of {self.flightLoad / 1000.0:.1f} kN with the required '
                f'factor of {PRELOAD_MARGIN:.1f}. The margin is {margin:+.2%}. **A clamp band that '
                f'gaps in flight is a stage coming apart**, so this is refused rather than '
                f'reported. Note that this is after {relaxation["totalLoss"]:.1%} relaxation: the '
                f'installed joint may have looked comfortable.',
                context = createErrorContext(component = 'ClampBand'))

        return {'retainedPreload': retained,
                'flightLoad':      self.flightLoad,
                'requiredPreload': PRELOAD_MARGIN * self.flightLoad,
                'margin':          margin,
                'holds':           True}

    # -------------------------------------------------------------------------------------------- #

    def calculateReleaseEnergy(self) -> dict:

        '''

        The strain energy stored in the band, which is what gets released as shock.

        A tensioned band is a spring. Cutting it releases its stored energy in microseconds, and
        that energy going into the structure is the shock source. The magnitude of the resulting
        shock response spectrum is not computed here and cannot be: **pyroshock prediction is a
        test-derived discipline** and any analytic number would carry more authority than it earns.

        What is computed is the energy, which is the right quantity to compare between designs and
        to compare against a device with a measured shock signature.

        '''

        if not np.isfinite(self.bandArea):
            raise InvalidInputError(
                'A band cross-sectional area is needed to compute stored energy, because the '
                'energy depends on how much the band stretched to reach its tension.',
                context = createErrorContext(component = 'ClampBand'))

        findings = []

        length = 2.0 * np.pi * self.interfaceRadius

        stiffness = self.bandArea * self.bandModulus / length

        stretch = self.bandTension / stiffness

        energy = 0.5 * self.bandTension * stretch

        stress = self.bandTension / self.bandArea

        findings.append(
            f'The band is {length:.2f} m long and stretches {stretch * 1000.0:.2f} mm to reach '
            f'{self.bandTension / 1000.0:.1f} kN, storing {energy:.1f} J.')

        findings.append(
            f'Band stress is {stress / 1.0e6:.0f} MPa, which is what decides whether the band '
            f'survives its own tension.')

        findings.append(
            '**The shock this produces is not computed and cannot be.** Pyroshock prediction is a '
            'test-derived discipline and an analytic shock response spectrum would carry more '
            'authority than it earns. The energy is the right quantity to compare designs against '
            'each other and against a device with a measured signature.')

        self.findings = findings

        return {'bandLength':  length,
                'bandStiffness': stiffness,
                'stretch':     stretch,
                'storedEnergy': energy,
                'bandStress':  stress,
                'findings':    findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full clamp band report.
        '''

        preload    = self.calculatePreload()
        relaxation = self.calculateRelaxation()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  CLAMP BAND: {self.interfaceRadius * 2000.0:.0f} mm interface, '
                     f'{self.bandTension / 1000.0:.1f} kN band tension')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Band tension',      f'{self.bandTension / 1000.0:.2f}',                'kN'],
                ['Wedge half angle',  f'{self.wedgeAngle:.1f}',                          'deg'],
                ['Wedge amplification', f'{preload["amplification"]:.1f}',               'x'],
                ['Ideal preload',     f'{preload["idealPreload"] / 1000.0:.1f}',         'kN'],
                ['Wedge efficiency',  f'{preload["wedgeEfficiency"]:.2f}',               ''],
                ['Delivered preload', f'{preload["deliveredPreload"] / 1000.0:.1f}',     'kN'],
                ['Retained preload',  f'{relaxation["retainedPreload"] / 1000.0:.1f}',   'kN'],
                ['Total relaxation',  f'{relaxation["totalLoss"]:.1%}',                  '']]

        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Preload'))

        lines.append('')
        for finding in relaxation['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'clamp_band.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('band tension',     self.bandTension),
                            ('interface radius', self.interfaceRadius)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'ClampBand'))

        if not 0.0 < self.wedgeAngle < 90.0:
            raise InvalidInputError(
                f'The wedge half angle must lie in (0, 90) degrees, got {self.wedgeAngle}.',
                context = createErrorContext(component = 'ClampBand'))

        if np.isfinite(self.bandArea) and self.bandArea <= 0.0:
            raise InvalidInputError(
                f'The band area must be positive, got {self.bandArea}.',
                context = createErrorContext(component = 'ClampBand'))

        if self.storageMonths < 0.0:
            raise InvalidInputError(
                f'The storage duration cannot be negative, got {self.storageMonths}.',
                context = createErrorContext(component = 'ClampBand'))

        if np.isfinite(self.flightLoad) and self.flightLoad < 0.0:
            raise InvalidInputError(
                f'The flight load cannot be negative, got {self.flightLoad}.',
                context = createErrorContext(component = 'ClampBand'))
