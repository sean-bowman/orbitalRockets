
# -- PowderLot Class Definition -- #

'''

Powder flowability, oxygen pickup across reuse cycles, and the blend-back mass balance that decides
when a lot has to be retired.

Powder is a controlled material, not a consumable. Its condition changes every time it goes through
the machine, and the two things that change are the ones that matter most:

    Morphology     Each build spatters, partially sinters and satellites the particles that were
                   not consumed. The distribution coarsens, the shape degrades, and the powder
                   stops spreading evenly. A recoater that lays a non-uniform layer produces
                   porosity that no parameter set fixes.

    Chemistry      Oxygen and nitrogen pick up on every exposure, particularly on titanium and
                   aluminium. Interstitial oxygen strengthens and embrittles, so a lot that has
                   drifted from 0.13 to 0.20 percent has quietly turned ELI titanium into grade 5
                   and lost a third of its fracture toughness.

Reuse is economically necessary. A build consumes a few percent of the powder in the chamber and
the rest is recovered, so virgin-only operation is unaffordable on any alloy worth printing. What
makes it safe is a written reuse policy with a blend-back ratio, a retirement criterion, and
oxygen testing on a schedule rather than on suspicion.

See Also:
---------
LpbfProcess       : The process window that powder condition shifts
LpbfQualification : Where the powder specification sits in the qualification structure

Theory: docs/PowderAndFeedstock.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from lpbfUtils import (applyInputs, formatReportTable, InvalidInputError,
                           ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .lpbfUtils import (applyInputs, formatReportTable, InvalidInputError,
                            ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Flowability from the Hausner ratio, which is tapped density over apparent density. A perfectly
# free-flowing spherical powder packs almost as well loose as tapped, so the ratio approaches one.
# Irregular or cohesive powder needs tapping to settle, so the ratio rises.
#
# The recoater does not tap. It spreads loose powder in a fraction of a second, so a powder that
# only packs well when tapped spreads badly, and the layer is locally thin.

HAUSNER_CLASSIFICATION = [
    (1.00, 1.11, 'excellent',  'Free flowing. Spreads uniformly at any recoat speed.'),
    (1.11, 1.18, 'good',       'Acceptable for production. The normal condition for virgin gas '
                               'atomised powder.'),
    (1.18, 1.25, 'fair',       'Spreads acceptably at reduced recoat speed. Watch the layer '
                               'uniformity.'),
    (1.25, 1.34, 'passable',   'Marginal. Expect layer defects and reduced density.'),
    (1.34, 1.45, 'poor',       'Will not spread reliably. Retire or reblend heavily.'),
    (1.45, 9.99, 'very poor',  'Cohesive. Not usable in a powder bed process.')
]

# Oxygen limits by alloy, as mass percent. The ELI limit is the one that matters most, because it
# is the whole difference between grade 23 and grade 5 and it is only 0.07 percent wide.

OXYGEN_LIMITS = {
    'TI-6AL-4V':     {'virgin': 0.13, 'limit': 0.20,
                      'note': 'Above 0.20 the powder no longer meets grade 5. Interstitial oxygen '
                              'strengthens and embrittles at the same time.'},
    'TI-6AL-4V ELI': {'virgin': 0.10, 'limit': 0.13,
                      'note': 'A 0.03 percent window. Drift past it and the powder is grade 5, '
                              'and a third of the fracture toughness has gone with no visible '
                              'change and no test that was scheduled to catch it.'},
    'INCONEL 718':   {'virgin': 0.020, 'limit': 0.050,
                      'note': 'Nickel alloys are far more tolerant. Oxide inclusions rather than '
                              'interstitial embrittlement are the concern.'},
    'INCONEL 625':   {'virgin': 0.020, 'limit': 0.050, 'note': 'As 718.'},
    '316L':          {'virgin': 0.025, 'limit': 0.060,
                      'note': 'Tolerant. Oxygen shows up as inclusions and a small ductility loss.'},
    'ALSI10MG':      {'virgin': 0.030, 'limit': 0.080,
                      'note': 'Aluminium powder oxidises readily and the oxide film interferes with '
                              'melting. Moisture pickup is the bigger problem: it produces hydrogen '
                              'porosity.'},
    'GRCOP-42':      {'virgin': 0.030, 'limit': 0.070,
                      'note': 'Copper oxide reduces the conductivity that is the whole point of '
                              'the alloy.'}
}

# Particle size distribution limits. A powder bed process needs a narrow distribution: fines below
# about 10 um are cohesive and they also present an explosion and inhalation hazard, while coarse
# particles above the layer thickness cannot be spread at all.

PSD_LIMITS = {
    'd10Minimum':      15.0e-6,   # [m], below this the fines fraction is cohesive and hazardous
    'd90Maximum':      53.0e-6,   # [m], the standard 15-45 um cut, plus tolerance
    'spanMaximum':     1.5,       # [-], (d90 - d10) / d50
    'layerRatioLimit': 0.80       # [-], d90 must sit below this fraction of the layer thickness
}

# Reuse policy defaults. Oxygen pickup per cycle is alloy and machine specific; these are typical
# for a well controlled inert chamber and they are the parameter to measure rather than assume.

DEFAULT_OXYGEN_PICKUP_PER_CYCLE = 0.004   # [mass %] per build, titanium in a controlled chamber
DEFAULT_RECOVERY_FRACTION       = 0.95    # [-], powder recovered from a build
SIEVE_MESH_STANDARD             = 63.0e-6  # [m], the standard reclaim sieve

# ------------------------------------------------------------------------------------------------ #

class PowderLot:

    '''

    Track a powder lot's flowability, chemistry and reuse history.

    Primary Input Properties:
    -------------------------
    material : str
        Key into OXYGEN_LIMITS
    apparentDensity / tappedDensity : float
        [kg/m^3], for the Hausner ratio
    particleD10 / D50 / D90 : float
        [m]
    virginOxygen : float
        [mass %] as received
    reuseCycles : int
        Builds this lot has been through

    Key Output Properties:
    ----------------------
    hausnerRatio : float
        Tapped over apparent density [-]
    flowability : str
        Classification from HAUSNER_CLASSIFICATION
    currentOxygen : float
        [mass %] after the accumulated reuse
    remainingCycles : int
        Before the oxygen limit is reached

    Public Methods:
    ---------------
    setInputs(inputs)                    Load a configuration dictionary
    calculateFlowability()               Hausner ratio, Carr index and the classification
    checkParticleSize(layerThickness)    PSD against the process limits
    projectOxygenPickup()                Accumulated oxygen and the cycles remaining
    calculateBlendBack(targetOxygen)     Virgin fraction needed to hold a target
    assessLot()                          The overall disposition
    generateReport(outputDir)            Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Identity -- #

        self.material          = 'TI-6AL-4V'   # [case insensitive string]
        self.lotIdentifier     = ''            # [case sensitive string]

        # -- Physical Condition -- #

        self.apparentDensity   = 2500.0    # [kg/m^3], loose poured
        self.tappedDensity     = 2800.0    # [kg/m^3]
        self.particleD10       = 18.0e-6   # [m]
        self.particleD50       = 32.0e-6   # [m]
        self.particleD90       = 48.0e-6   # [m]

        # -- Chemistry and History -- #

        self.virginOxygen      = np.nan    # [mass %], None takes the table value
        self.measuredOxygen    = np.nan    # [mass %], overrides the projection when measured
        self.reuseCycles       = 0         # [-]
        self.oxygenPickupPerCycle = np.nan  # [mass %] per build
        self.recoveryFraction  = DEFAULT_RECOVERY_FRACTION   # [-]

        # -- Results -- #

        self.hausnerRatio      = np.nan    # [-]
        self.carrIndex         = np.nan    # [%]
        self.flowability       = ''        # [case sensitive string]
        self.currentOxygen     = np.nan    # [mass %]
        self.remainingCycles   = np.nan    # [-]
        self.powderNotes       = []        # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material.

        '''

        requiredParams = {
            'material': 'Material not provided.'
        }

        optionalParams = ['lotIdentifier', 'apparentDensity', 'tappedDensity', 'particleD10',
                          'particleD50', 'particleD90', 'virginOxygen', 'measuredOxygen',
                          'reuseCycles', 'oxygenPickupPerCycle', 'recoveryFraction']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        if np.isnan(self.virginOxygen):
            self.virginOxygen = OXYGEN_LIMITS[self.material]['virgin']

        if np.isnan(self.oxygenPickupPerCycle):
            self.oxygenPickupPerCycle = DEFAULT_OXYGEN_PICKUP_PER_CYCLE
            self.powderNotes.append(
                f'Oxygen pickup per cycle was not supplied, so the default of '
                f'{DEFAULT_OXYGEN_PICKUP_PER_CYCLE:.4f} mass percent was used. This is machine and '
                f'chamber specific and it should be measured rather than assumed: a leaking chamber '
                f'picks up several times this.')

    def calculateFlowability(self) -> dict:

        '''

        Hausner ratio and Carr index, and what they mean for the recoater.

            HR = rho_tapped / rho_apparent
            CI = 100 (rho_tapped - rho_apparent) / rho_tapped

        They are the same measurement expressed two ways. A free flowing spherical powder packs
        almost as well loose as tapped, so HR approaches 1.0.

        THE RECOATER DOES NOT TAP. It spreads loose powder in a fraction of a second, so a powder
        that only packs well when tapped spreads badly. The layer comes out locally thin, the melt
        pool has less material than the parameter set assumes, and the result is porosity that looks
        like a parameter problem and is not.

        '''

        self.hausnerRatio = self.tappedDensity / self.apparentDensity
        self.carrIndex    = 100.0 * (self.tappedDensity - self.apparentDensity) / self.tappedDensity

        description = 'unclassified'
        note        = ''

        for lower, upper, classification, text in HAUSNER_CLASSIFICATION:
            if lower <= self.hausnerRatio < upper:
                self.flowability = classification
                description      = classification
                note             = text
                break

        result = {'hausnerRatio': self.hausnerRatio, 'carrIndex': self.carrIndex,
                  'flowability': description, 'note': note,
                  'apparentDensity': self.apparentDensity, 'tappedDensity': self.tappedDensity}

        if self.hausnerRatio >= 1.25:
            self.powderNotes.append(
                f'Hausner ratio {self.hausnerRatio:.3f} classifies as \'{description}\'. The '
                f'recoater spreads loose powder without tapping it, so this lot will lay a '
                f'non-uniform layer and produce porosity that no parameter change will fix.')

        return result

    def checkParticleSize(self, layerThickness: float = 40.0e-6) -> dict:

        '''

        Particle size distribution against the process limits.

        Two hard bounds and one distribution shape check:

            d10 too low     Fines below about 10 um are cohesive, so they degrade flow, and they
                            are also the inhalation and explosion hazard. Titanium and aluminium
                            fines are genuinely dangerous.

            d90 too high    A particle larger than the layer cannot be spread. It is dragged by the
                            recoater, scoring the layer and often crashing the build.

            span too wide   (d90 - d10) / d50. A wide distribution segregates during handling, so
                            the powder that reaches the bed is not the powder that was tested.

        The d90 against layer thickness check is the one that catches reused powder, because the
        distribution coarsens with every cycle as fines are consumed preferentially.

        '''

        span = (self.particleD90 - self.particleD10) / self.particleD50
        layerRatio = self.particleD90 / layerThickness

        issues = []

        if self.particleD10 < PSD_LIMITS['d10Minimum']:
            issues.append(
                f'd10 of {self.particleD10 * 1.0e6:.1f} um is below the '
                f'{PSD_LIMITS["d10Minimum"] * 1.0e6:.0f} um minimum. The fines fraction degrades '
                f'flow and, for titanium and aluminium, presents a real explosion and inhalation '
                f'hazard.')

        if self.particleD90 > PSD_LIMITS['d90Maximum']:
            issues.append(
                f'd90 of {self.particleD90 * 1.0e6:.1f} um exceeds the '
                f'{PSD_LIMITS["d90Maximum"] * 1.0e6:.0f} um maximum. Sieve the lot.')

        if layerRatio > PSD_LIMITS['layerRatioLimit']:
            issues.append(
                f'd90 is {layerRatio * 100.0:.0f} percent of the '
                f'{layerThickness * 1.0e6:.0f} um layer thickness, against a '
                f'{PSD_LIMITS["layerRatioLimit"] * 100.0:.0f} percent limit. Coarse particles will '
                f'be dragged by the recoater, scoring the layer and risking a build crash.')

        if span > PSD_LIMITS['spanMaximum']:
            issues.append(
                f'Distribution span of {span:.2f} exceeds {PSD_LIMITS["spanMaximum"]:.1f}. A wide '
                f'distribution segregates during handling, so the powder reaching the bed is not '
                f'the powder that was tested.')

        self.powderNotes.extend(issues)

        return {'d10': self.particleD10, 'd50': self.particleD50, 'd90': self.particleD90,
                'span': span, 'layerThickness': layerThickness, 'layerRatio': layerRatio,
                'sieveMesh': SIEVE_MESH_STANDARD,
                'issues': issues, 'acceptable': not issues}

    def projectOxygenPickup(self) -> dict:

        '''

        Accumulated oxygen from the reuse history, and the cycles remaining before the limit.

            oxygen(n) = virgin + n * pickupPerCycle

        Linear accumulation is the simple model and it is adequate, because the pickup per cycle is
        dominated by handling exposure rather than by anything that saturates.

        A MEASURED VALUE ALWAYS OVERRIDES THE PROJECTION. The projection is for planning the
        retirement point; the measurement is what dispositions the lot. Oxygen is measured by inert
        gas fusion and it is neither expensive nor slow, and a titanium powder programme that does
        not measure it on a schedule is guessing about a property that decides fracture toughness.

        '''

        limits = OXYGEN_LIMITS[self.material]

        projected = self.virginOxygen + self.reuseCycles * self.oxygenPickupPerCycle

        if not np.isnan(self.measuredOxygen):
            self.currentOxygen = self.measuredOxygen
            source = 'measured'
            if abs(self.measuredOxygen - projected) > 2.0 * self.oxygenPickupPerCycle:
                self.powderNotes.append(
                    f'The measured oxygen of {self.measuredOxygen:.4f} percent differs from the '
                    f'projected {projected:.4f} by more than two cycles worth of pickup. Either the '
                    f'pickup rate is wrong for this machine or the lot history is not what the '
                    f'records say.')
        else:
            self.currentOxygen = projected
            source = 'projected'

        headroom = limits['limit'] - self.currentOxygen
        self.remainingCycles = max(0, int(np.floor(headroom / self.oxygenPickupPerCycle)))

        result = {'material': self.material, 'virginOxygen': self.virginOxygen,
                  'currentOxygen': self.currentOxygen, 'source': source,
                  'projectedOxygen': projected,
                  'limit': limits['limit'], 'headroom': headroom,
                  'reuseCycles': self.reuseCycles,
                  'remainingCycles': self.remainingCycles,
                  'pickupPerCycle': self.oxygenPickupPerCycle,
                  'note': limits['note']}

        if self.currentOxygen >= limits['limit']:
            raise ProcessInfeasibleError(
                message = f'{self.material} powder at {self.currentOxygen:.4f} percent oxygen has '
                          f'reached the {limits["limit"]:.4f} percent limit after '
                          f'{self.reuseCycles} cycles. {limits["note"]} Retire the lot or blend it '
                          f'back with virgin powder.'
            )

        if self.remainingCycles <= 2:
            self.powderNotes.append(
                f'Only {self.remainingCycles} reuse cycles remain before the oxygen limit. Plan the '
                f'blend-back or the retirement now rather than discovering it mid-build.')

        return result

    def calculateBlendBack(self, targetOxygen: float = None) -> dict:

        '''

        Virgin powder fraction needed to bring a used lot back to a target oxygen level.

        A simple mass balance on the oxygen:

            target = f * virgin + (1 - f) * used
            f = (used - target) / (used - virgin)

        Blending back is what makes reuse sustainable indefinitely rather than for a fixed number of
        cycles. A steady state exists where the oxygen added per build equals the oxygen removed by
        the virgin fraction, and running at that ratio means the lot never has to be retired for
        chemistry.

        THE BLEND HAS TO BE HOMOGENEOUS AND IT HAS TO BE RECORDED. Two half-blended lots behave like
        two lots, and a blend that is not in the lot record breaks the traceability chain back to
        the powder certificate.

        '''

        if np.isnan(self.currentOxygen):
            self.projectOxygenPickup()

        limits = OXYGEN_LIMITS[self.material]

        if targetOxygen is None:
            # Default to the midpoint between virgin and the limit, which gives useful headroom
            targetOxygen = 0.5 * (self.virginOxygen + limits['limit'])

        if targetOxygen <= self.virginOxygen:
            raise InvalidInputError(
                message       = f'A target of {targetOxygen:.4f} percent is at or below the virgin '
                                f'level of {self.virginOxygen:.4f}. No blend reaches it.',
                parameterName = 'targetOxygen', value = targetOxygen,
                validRange    = f'Between {self.virginOxygen:.4f} and {limits["limit"]:.4f}'
            )

        if self.currentOxygen <= targetOxygen:
            return {'virginFraction': 0.0, 'targetOxygen': targetOxygen,
                    'currentOxygen': self.currentOxygen,
                    'note': 'The lot is already at or below the target. No blend needed.'}

        virginFraction = ((self.currentOxygen - targetOxygen) /
                          (self.currentOxygen - self.virginOxygen))

        # The steady state: the virgin fraction at which pickup and dilution balance exactly.
        steadyStateFraction = self.oxygenPickupPerCycle / max(
            targetOxygen - self.virginOxygen, 1.0e-9)
        steadyStateFraction = float(np.clip(steadyStateFraction, 0.0, 1.0))

        return {'currentOxygen': self.currentOxygen, 'targetOxygen': targetOxygen,
                'virginOxygen': self.virginOxygen,
                'virginFraction': virginFraction,
                'usedFraction': 1.0 - virginFraction,
                'steadyStateVirginFraction': steadyStateFraction,
                'note': f'Blending {virginFraction * 100.0:.0f} percent virgin brings this lot to '
                        f'{targetOxygen:.4f} percent. Running at '
                        f'{steadyStateFraction * 100.0:.0f} percent virgin on every build holds it '
                        f'there indefinitely, so the lot never retires on chemistry. The blend has '
                        f'to be homogeneous and it has to be in the lot record.'}

    def assessLot(self, layerThickness: float = 40.0e-6) -> dict:

        '''

        Overall disposition: use, sieve, blend or retire.

        '''

        flow    = self.calculateFlowability()
        psd     = self.checkParticleSize(layerThickness)

        try:
            oxygen = self.projectOxygenPickup()
            oxygenAcceptable = True
        except ProcessInfeasibleError as error:
            oxygen = {'currentOxygen': self.currentOxygen,
                      'limit': OXYGEN_LIMITS[self.material]['limit'],
                      'error': str(error)}
            oxygenAcceptable = False

        actions = []

        if not oxygenAcceptable:
            actions.append('RETIRE or blend back. The oxygen limit has been reached.')
        elif oxygen.get('remainingCycles', 0) <= 2:
            actions.append('Plan a blend-back. Fewer than three cycles of oxygen headroom remain.')

        if not psd['acceptable']:
            if self.particleD90 > PSD_LIMITS['d90Maximum']:
                actions.append('Sieve the lot to remove the coarse fraction.')
            else:
                actions.append('Review the particle size distribution before the next build.')

        if self.hausnerRatio >= 1.25:
            actions.append('Flowability is marginal. Reduce the recoat speed or blend with virgin.')

        disposition = 'RETIRE' if not oxygenAcceptable else \
                      ('CONDITIONAL' if actions else 'USE')

        return {'lotIdentifier': self.lotIdentifier, 'material': self.material,
                'reuseCycles': self.reuseCycles,
                'flowability': flow, 'particleSize': psd, 'oxygen': oxygen,
                'disposition': disposition,
                'actions': actions or ['No action required.']}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        if np.isnan(self.hausnerRatio):
            self.calculateFlowability()

        limits = OXYGEN_LIMITS[self.material]

        try:
            self.projectOxygenPickup()
            oxygenLine = (f'{self.currentOxygen:.4f} % against a {limits["limit"]:.4f} % limit, '
                          f'{self.remainingCycles} cycles remaining')
        except ProcessInfeasibleError:
            oxygenLine = (f'{self.currentOxygen:.4f} % -- AT OR ABOVE the '
                          f'{limits["limit"]:.4f} % limit')

        rows = [
            ['Material',            f'{self.material}'],
            ['Lot',                 f'{self.lotIdentifier or "unidentified"}'],
            ['Reuse cycles',        f'{self.reuseCycles}'],
            ['Apparent density',    f'{self.apparentDensity:.0f} kg/m^3'],
            ['Tapped density',      f'{self.tappedDensity:.0f} kg/m^3'],
            ['Hausner ratio',       f'{self.hausnerRatio:.3f} ({self.flowability})'],
            ['Carr index',          f'{self.carrIndex:.1f} %'],
            ['d10 / d50 / d90',     f'{self.particleD10 * 1.0e6:.1f} / '
                                    f'{self.particleD50 * 1.0e6:.1f} / '
                                    f'{self.particleD90 * 1.0e6:.1f} um'],
            ['Span',                f'{(self.particleD90 - self.particleD10) / self.particleD50:.2f}'],
            ['Virgin oxygen',       f'{self.virginOxygen:.4f} %'],
            ['Current oxygen',      oxygenLine]
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'POWDER LOT')

        report += f'\n\nALLOY NOTE\n{"-" * 60}\n{limits["note"]}\n'

        for note in self.powderNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'powderLot.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = ' '.join(self.material.strip().upper().split())

        if key not in OXYGEN_LIMITS:
            raise InvalidInputError(
                message       = f'No powder chemistry limits for \'{self.material}\'.',
                parameterName = 'material', value = self.material,
                validRange    = str(sorted(OXYGEN_LIMITS.keys()))
            )

        self.material = key

        if self.tappedDensity < self.apparentDensity:
            raise InvalidInputError(
                message       = f'Tapped density {self.tappedDensity:.0f} is below apparent density '
                                f'{self.apparentDensity:.0f}. Tapping settles powder, so the tapped '
                                f'value is always the higher of the two and these are transposed.',
                parameterName = 'tappedDensity', value = self.tappedDensity,
                validRange    = f'At least the apparent density, {self.apparentDensity:.0f} kg/m^3'
            )

        if not self.particleD10 < self.particleD50 < self.particleD90:
            raise InvalidInputError(
                message       = 'The particle size distribution must satisfy d10 < d50 < d90.',
                parameterName = 'particleD10/D50/D90',
                value         = (self.particleD10, self.particleD50, self.particleD90),
                validRange    = 'Strictly increasing'
            )

        if self.reuseCycles < 0:
            raise InvalidInputError(
                message       = 'Reuse cycles cannot be negative.',
                parameterName = 'reuseCycles', value = self.reuseCycles,
                validRange    = 'Zero or more'
            )
