
# -- PyrotechnicInitiator -- #

'''

Bridgewire initiators, and the two currents that define everything about handling one.

**No-fire** is the current the device must survive without firing. The NASA Standard Initiator
convention is one amp and one watt applied for five minutes, and the entire ordnance safety
practice of a vehicle is built around keeping stray energy below it: bonding, shielding, twisted
shielded pairs, shorting plugs, safe and arm devices, and the rule that nobody transmits near a
loaded vehicle.

**All-fire** is the current at which the device fires reliably. The firing circuit has to deliver it
with margin through the harness resistance, the bridgewire resistance and whatever the battery has
left at the end of a cold countdown.

The gap between them is the whole design space, and **it is narrower than it looks**: a five to one
ratio in current is only twenty-five to one in power, and a fault that puts a few volts across a
one ohm bridgewire is already most of the way to no-fire.

This class computes both sides of that gap and refuses a circuit that fails either.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from mechanismUtils import (INITIATOR_TYPES, NO_FIRE_MARGIN, ALL_FIRE_MARGIN,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, InitiationError)
except ImportError:
    from .mechanismUtils import (INITIATOR_TYPES, NO_FIRE_MARGIN, ALL_FIRE_MARGIN,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, InitiationError)

# ------------------------------------------------------------------------------------------------ #
# -- PyrotechnicInitiator -- #
# ------------------------------------------------------------------------------------------------ #

class PyrotechnicInitiator:

    '''

    Firing circuit adequacy and stray energy safety for a bridgewire initiator.

    '''

    def __init__(self):

        self.initiatorType    = ''
        self.firingVoltage    = np.nan
        self.harnessResistance = np.nan
        self.switchResistance = np.nan
        self.parallelCount    = np.nan
        self.strayCurrent     = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `firingVoltage` is the voltage at the initiator bus at the worst credible moment, which is
        a cold battery at the end of a long countdown rather than a nameplate value.

        `parallelCount` is how many initiators the circuit fires at once, because they share the
        current and a circuit sized for one will not fire two.

        '''

        requiredParams = {'initiatorType':     str,
                          'firingVoltage':     (int, float),
                          'harnessResistance': (int, float)}

        optionalParams = {'switchResistance': (int, float),
                          'parallelCount':    (int, float),
                          'strayCurrent':     (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.switchResistance):
            self.switchResistance = 0.05

        if not np.isfinite(self.parallelCount):
            self.parallelCount = 1.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def device(self) -> dict:

        return INITIATOR_TYPES[self.initiatorType]

    # -------------------------------------------------------------------------------------------- #

    def calculateFiringCurrent(self) -> dict:

        '''

        The current the circuit actually delivers, through everything in series.

        Initiators fired in parallel share the source, so the bridgewire resistance seen by the
        supply falls but the current per device falls too once the harness resistance is
        significant. That is the case a circuit sized on one device gets wrong.

        '''

        device = self.device()

        bridgewire = device['bridgewireResistance']

        # parallel bridgewires present a lower resistance to the supply
        effectiveBridgewire = bridgewire / self.parallelCount

        total = self.harnessResistance + self.switchResistance + effectiveBridgewire

        busCurrent = self.firingVoltage / total

        perDevice = busCurrent / self.parallelCount

        return {'bridgewireResistance': bridgewire,
                'effectiveBridgewire':  effectiveBridgewire,
                'totalResistance':      total,
                'busCurrent':           busCurrent,
                'currentPerDevice':     perDevice,
                'powerPerDevice':       perDevice ** 2 * bridgewire,
                'allFireCurrent':       device['allFireCurrent'],
                'allFireRatio':         perDevice / device['allFireCurrent']}

    # -------------------------------------------------------------------------------------------- #

    def checkAllFire(self) -> dict:

        '''

        Whether the circuit fires the device, with margin.

        Refused rather than reported when it does not, because a firing circuit that does not fire
        is a mission that ends where the ordnance was supposed to work.

        '''

        findings = []

        firing = self.calculateFiringCurrent()

        required = ALL_FIRE_MARGIN * firing['allFireCurrent']

        findings.append(
            f'The circuit delivers {firing["currentPerDevice"]:.2f} A per device through '
            f'{firing["totalResistance"]:.2f} ohm, against an all-fire current of '
            f'{firing["allFireCurrent"]:.2f} A.')

        if self.parallelCount > 1:
            findings.append(
                f'{self.parallelCount:.0f} devices in parallel share the bus, so the per-device '
                f'current is {firing["currentPerDevice"]:.2f} A against a bus current of '
                f'{firing["busCurrent"]:.2f} A. A circuit sized for one device does not fire '
                f'several.')

        if firing['currentPerDevice'] < required:
            raise InitiationError(
                f'The circuit delivers {firing["currentPerDevice"]:.2f} A per device against an '
                f'all-fire current of {firing["allFireCurrent"]:.2f} A, which needs '
                f'{required:.2f} A at the {ALL_FIRE_MARGIN:.1f} margin convention. **A firing '
                f'circuit that does not fire is a mission that ends where the ordnance was '
                f'supposed to work**, so this is refused. The total circuit resistance is '
                f'{firing["totalResistance"]:.2f} ohm, of which {self.harnessResistance:.2f} is '
                f'harness: that is usually the term to attack.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))

        findings.append(
            f'That is {firing["allFireRatio"]:.1f} times all-fire, against a convention of '
            f'{ALL_FIRE_MARGIN:.1f}.')

        self.findings = findings

        return {**firing,
                'requiredCurrent': required,
                'fires':           True,
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def checkNoFire(self) -> dict:

        '''

        Whether a credible stray current stays safely below the no-fire threshold.

        The convention applied is a factor of two on current, which is a factor of four on power.
        That sounds generous and it is not: stray energy comes from radio frequency pickup on a
        harness that acts as an antenna, from lightning-induced transients, from static discharge
        and from a test set connected wrongly, and the margin is against all of them at once.

        '''

        if not np.isfinite(self.strayCurrent):
            raise InvalidInputError(
                'A credible stray current is needed to check no-fire. It comes from an '
                'electromagnetic environment analysis of the vehicle, and assuming zero is the '
                'assumption that makes the check pointless.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))

        findings = []

        device = self.device()

        noFireCurrent = device['noFireCurrent']

        allowed = noFireCurrent / NO_FIRE_MARGIN

        strayPower = self.strayCurrent ** 2 * device['bridgewireResistance']

        allowedPower = device['noFirePower'] / (NO_FIRE_MARGIN ** 2)

        findings.append(
            f'A stray current of {self.strayCurrent:.3f} A puts {strayPower * 1000.0:.1f} mW into '
            f'the bridgewire, against a no-fire rating of {noFireCurrent:.2f} A and '
            f'{device["noFirePower"]:.2f} W.')

        safe = bool(self.strayCurrent <= allowed and strayPower <= allowedPower)

        if not safe:
            raise InitiationError(
                f'A credible stray current of {self.strayCurrent:.3f} A is above the '
                f'{allowed:.3f} A this repository treats as safe, which is the {noFireCurrent:.2f} '
                f'A no-fire rating with a factor of {NO_FIRE_MARGIN:.0f}. **An initiator that can '
                f'be fired by the vehicle\'s own electromagnetic environment is a hazard rather '
                f'than a device**, so this is refused. The fix is bonding, shielding and shorting '
                f'rather than a less sensitive initiator, because a less sensitive initiator needs '
                f'a bigger firing circuit.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))

        findings.append(
            f'That is a factor of {noFireCurrent / self.strayCurrent:.1f} on current and '
            f'{device["noFirePower"] / strayPower:.0f} on power, because power goes as the square.')

        self.findings = findings

        return {'strayCurrent':   self.strayCurrent,
                'strayPower':     strayPower,
                'noFireCurrent':  noFireCurrent,
                'noFirePower':    device['noFirePower'],
                'allowedCurrent': allowed,
                'currentFactor':  noFireCurrent / self.strayCurrent,
                'safe':           safe,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def compareInitiators(self) -> dict:

        '''

        The trade between a sensitive initiator and a robust one, which runs both ways at once.

        A low energy initiator fires from a smaller circuit, which is a real mass and battery
        saving. It also has a no-fire threshold five times lower, which tightens every bonding,
        shielding and grounding requirement on the vehicle. **The initiator choice is an
        electromagnetic compatibility decision as much as an ordnance one.**

        '''

        original = self.initiatorType

        results = {}

        try:
            for name in INITIATOR_TYPES:

                self.initiatorType = name

                firing = self.calculateFiringCurrent()

                results[name] = {
                    'allFireRatio':  firing['allFireRatio'],
                    'noFireCurrent': INITIATOR_TYPES[name]['noFireCurrent'],
                    'firesOnThisCircuit': bool(firing['currentPerDevice']
                                               >= ALL_FIRE_MARGIN
                                               * INITIATOR_TYPES[name]['allFireCurrent'])}

        finally:
            self.initiatorType = original

        return {'results': results}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full initiator report.
        '''

        firing = self.calculateFiringCurrent()

        device = self.device()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  PYROTECHNIC INITIATOR: {self.initiatorType}, '
                     f'{self.parallelCount:.0f} in parallel at {self.firingVoltage:.1f} V')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Harness resistance',   f'{self.harnessResistance:.3f}',            'ohm'],
             ['Switch resistance',    f'{self.switchResistance:.3f}',             'ohm'],
             ['Bridgewire',           f'{firing["bridgewireResistance"]:.3f}',    'ohm'],
             ['Total resistance',     f'{firing["totalResistance"]:.3f}',         'ohm'],
             ['Bus current',          f'{firing["busCurrent"]:.2f}',              'A'],
             ['Current per device',   f'{firing["currentPerDevice"]:.2f}',        'A'],
             ['All-fire current',     f'{device["allFireCurrent"]:.2f}',          'A'],
             ['Ratio to all-fire',    f'{firing["allFireRatio"]:.2f}',            ''],
             ['No-fire current',      f'{device["noFireCurrent"]:.2f}',           'A'],
             ['No-fire power',        f'{device["noFirePower"]:.2f}',             'W']],
            ['Quantity', 'Value', 'Unit'], title = 'Firing circuit'))

        lines.append('')
        lines.append(f'    - {device["note"]}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'pyrotechnic_initiator.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.initiatorType not in INITIATOR_TYPES:
            raise InvalidInputError(
                f'Unknown initiator type \'{self.initiatorType}\'. Known types are '
                f'{sorted(INITIATOR_TYPES)}.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))

        if self.firingVoltage <= 0.0:
            raise InvalidInputError(
                f'The firing voltage must be positive, got {self.firingVoltage}.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))

        for name, value in (('harness resistance', self.harnessResistance),
                            ('switch resistance',  self.switchResistance)):
            if value < 0.0:
                raise InvalidInputError(
                    f'The {name} cannot be negative, got {value}.',
                    context = createErrorContext(component = 'PyrotechnicInitiator'))

        if self.parallelCount < 1:
            raise InvalidInputError(
                f'At least one initiator has to be fired, got {self.parallelCount}.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))

        if np.isfinite(self.strayCurrent) and self.strayCurrent < 0.0:
            raise InvalidInputError(
                f'The stray current cannot be negative, got {self.strayCurrent}.',
                context = createErrorContext(component = 'PyrotechnicInitiator'))
