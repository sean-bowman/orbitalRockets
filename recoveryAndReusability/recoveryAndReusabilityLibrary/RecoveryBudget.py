
# -- RecoveryBudget -- #

'''

What recovery costs, paid on every flight including the ones that do not come back.

Two things are given up to recover a stage. **Propellant that could have accelerated the payload**,
spent on boost-back, entry and landing burns. And **dry mass that the stage carries the whole way
up**: legs, fins, avionics, and the structure to react landing loads.

The dry mass is the more expensive of the two per kilogram, because a kilogram of landing leg is
carried through the entire first stage burn while a kilogram of reserve propellant is only carried
until it is used. They are not interchangeable and a budget that adds them without weighting is
missing that.

**The penalty as a fraction of payload rises as the mission gets harder.** The recovery reserve is
roughly fixed and the payload is not, so on a demanding mission the same reserve eats a larger share
of a smaller margin. That is why boosters are expended on the hardest missions of an otherwise
reusable fleet, and it is a performance decision rather than an operational one.

**The published Falcon 9 penalties are 18.9 per cent to low orbit and 33.7 per cent to transfer
orbit**, from the same source table, and this class is checked against them: a bottom-up budget that
does not land in that range is a budget with something missing.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from recoveryUtils import (RECOVERY_MODES, GRAVITY,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, RecoveryError)
except ImportError:
    from .recoveryUtils import (RECOVERY_MODES, GRAVITY,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, RecoveryError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The two exchange ratios: payload lost per kilogram of first stage dry mass, and per kilogram of
# reserve propellant.
#
# **These are properties of the vehicle rather than of the recovery system**, and the domain that
# owns them is vehicleArchitecture, whose StagedVehicle.payloadSensitivity computes the payload
# elasticity of a given vehicle directly. They are inputs here with representative defaults, in the
# same way that chill-down mass is an input to groundSystemsAndOperations rather than a calculation
# in it.
#
# Dry mass costs more per kilogram than reserve propellant, because it is carried through the whole
# first stage burn while the reserve is burned at the end of it. That ordering is structural. The
# VALUES are representative and registered as unvalidated.
DRY_MASS_EXCHANGE_RATIO = 0.30        # [kg payload per kg stage dry mass]
RESERVE_EXCHANGE_RATIO = 0.12         # [kg payload per kg reserve propellant]

# ------------------------------------------------------------------------------------------------ #
# -- RecoveryBudget -- #
# ------------------------------------------------------------------------------------------------ #

class RecoveryBudget:

    '''

    Recovery hardware mass, reserve propellant, and the payload each costs, by recovery mode.

    '''

    def __init__(self):

        self.stageDryMass     = np.nan
        self.stagePropellant  = np.nan
        self.baselinePayload  = np.nan
        self.mode             = ''
        self.hardwareItems    = {}
        self.reserveFraction  = np.nan
        self.dryMassExchangeRatio = np.nan
        self.reserveExchangeRatio = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `stageDryMass` and `stagePropellant` describe the expendable stage [kg], and
        `baselinePayload` is what it delivers without recovery hardware.

        `mode` is a key of RECOVERY_MODES. `hardwareItems` overrides the mode's dry fraction with
        a counted list, which is the better estimate once the hardware exists, and `reserveFraction`
        overrides the mode's propellant reserve.

        '''

        requiredParams = {'stageDryMass':    (int, float),
                          'stagePropellant': (int, float),
                          'baselinePayload': (int, float)}

        optionalParams = {'mode':            str,
                          'hardwareItems':   dict,
                          'reserveFraction': (int, float),
                          'dryMassExchangeRatio': (int, float),
                          'reserveExchangeRatio': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.mode:
            self.mode = 'downrangeLanding'

        if not np.isfinite(self.dryMassExchangeRatio):
            self.dryMassExchangeRatio = DRY_MASS_EXCHANGE_RATIO

        if not np.isfinite(self.reserveExchangeRatio):
            self.reserveExchangeRatio = RESERVE_EXCHANGE_RATIO

        if self.hardwareItems is None or isinstance(self.hardwareItems, float):
            self.hardwareItems = {}

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateHardwareMass(self) -> dict:

        '''

        Recovery dry mass, counted if a list was supplied and fractional if not.

        **Counting beats fractioning** for the same reason it does on a harness: a counted estimate
        converges as the design matures and a fractional one does not.

        '''

        mode = RECOVERY_MODES[self.mode]

        if self.hardwareItems:

            items = [{'item': name, 'mass': float(mass)}
                     for name, mass in self.hardwareItems.items()]
            total = sum(entry['mass'] for entry in items)
            method = 'counted'

        else:

            total = mode['hardwareDryFraction'] * self.stageDryMass
            items = [{'item': f'{self.mode} allowance', 'mass': total}]
            method = 'fractional'

        for entry in items:
            entry['share'] = entry['mass'] / total if total > 0.0 else 0.0

        return {'items':        items,
                'totalMass':    total,
                'method':       method,
                'dryFraction':  total / self.stageDryMass,
                'largest':      max(items, key = lambda entry: entry['mass']) if items else None}

    # -------------------------------------------------------------------------------------------- #

    def calculateReserve(self) -> dict:

        '''

        Reserve propellant held back for the recovery burns.

        '''

        mode = RECOVERY_MODES[self.mode]

        fraction = (self.reserveFraction if np.isfinite(self.reserveFraction)
                    else mode['reservePropellantFraction'])

        reserve = fraction * self.stagePropellant

        return {'reserveFraction':  fraction,
                'reserveMass':      reserve,
                'ascentPropellant': self.stagePropellant - reserve,
                'mode':             self.mode,
                'note':             mode['note']}

    # -------------------------------------------------------------------------------------------- #

    def calculatePenalty(self) -> dict:

        '''

        Payload given up, split between the two causes.

        The split is the useful part. Dry mass and reserve propellant do not cost the same per
        kilogram, and the ranking by mass is not the ranking by payload.

        '''

        hardware = self.calculateHardwareMass()
        reserve = self.calculateReserve()

        fromHardware = hardware['totalMass'] * self.dryMassExchangeRatio
        fromReserve = reserve['reserveMass'] * self.reserveExchangeRatio

        total = fromHardware + fromReserve
        payload = self.baselinePayload - total

        if payload <= 0.0:
            raise RecoveryError(
                f'The recovery budget removes {total:,.0f} kg from a baseline payload of '
                f'{self.baselinePayload:,.0f} kg, which leaves nothing to launch. A stage that '
                f'cannot carry a payload and recover itself is an expendable stage.',
                context = {'mode':          self.mode,
                           'hardwareMass':  hardware['totalMass'],
                           'reserveMass':   reserve['reserveMass']})

        contributions = [{'cause': 'recovery hardware', 'mass': hardware['totalMass'],
                          'payloadCost': fromHardware},
                         {'cause': 'reserve propellant', 'mass': reserve['reserveMass'],
                          'payloadCost': fromReserve}]

        for entry in contributions:
            entry['share'] = entry['payloadCost'] / total

        heaviest = max(contributions, key = lambda entry: entry['mass'])
        costliest = max(contributions, key = lambda entry: entry['payloadCost'])

        return {'contributions':   contributions,
                'payloadPenalty':  total,
                'recoverablePayload': payload,
                'penaltyFraction': total / self.baselinePayload,
                'heaviest':        heaviest['cause'],
                'costliest':       costliest['cause'],
                'rankingAgrees':   heaviest['cause'] == costliest['cause']}

    # -------------------------------------------------------------------------------------------- #

    def compareModes(self, modes: list = None) -> dict:

        '''

        Every recovery mode against the same stage.

        The ordering is the result: a return to the launch site costs more than a downrange
        landing because it has to cancel and reverse the downrange velocity, and both cost more
        than expending the stage. That holds for any values.

        '''

        if modes is None:
            modes = list(RECOVERY_MODES)

        original = self.mode
        results = []

        try:
            for mode in modes:

                self.mode = mode

                if mode == 'expended':
                    results.append({'mode': mode, 'penaltyFraction': 0.0,
                                    'recoverablePayload': self.baselinePayload,
                                    'reserveMass': 0.0, 'hardwareMass': 0.0})
                    continue

                penalty = self.calculatePenalty()

                results.append({'mode':               mode,
                                'penaltyFraction':    penalty['penaltyFraction'],
                                'recoverablePayload': penalty['recoverablePayload'],
                                'reserveMass':        penalty['contributions'][1]['mass'],
                                'hardwareMass':       penalty['contributions'][0]['mass']})
        finally:
            self.mode = original

        results.sort(key = lambda entry: entry['penaltyFraction'])

        return {'results': results,
                'cheapestRecovery': next(entry['mode'] for entry in results
                                         if entry['mode'] != 'expended'),
                'dearest': results[-1]['mode']}

    # -------------------------------------------------------------------------------------------- #

    def missionSensitivity(self, payloads: list = None) -> dict:

        '''

        The same recovery budget against several mission difficulties.

        The recovery cost is a nearly fixed number of kilograms. Expressed as a fraction of a
        payload that shrinks with mission energy, it grows, which is why the transfer orbit
        penalty is roughly twice the low orbit one on a real vehicle.

        '''

        if payloads is None:
            payloads = [self.baselinePayload * factor for factor in (1.0, 0.7, 0.5, 0.36)]

        original = self.baselinePayload
        results = []

        try:
            for payload in payloads:
                self.baselinePayload = payload
                penalty = self.calculatePenalty()
                results.append({'baselinePayload': payload,
                                'penaltyMass':     penalty['payloadPenalty'],
                                'penaltyFraction': penalty['penaltyFraction']})
        finally:
            self.baselinePayload = original

        masses = [entry['penaltyMass'] for entry in results]

        return {'results':         results,
                'penaltyMassIsFixed': bool(np.allclose(masses, masses[0])),
                'fractionSpread':  results[-1]['penaltyFraction'] / results[0]['penaltyFraction']}

    # -------------------------------------------------------------------------------------------- #

    def impliedExchangeRatios(self, publishedPenalty: float) -> dict:

        """

        Invert a published payload penalty to the exchange ratios the vehicle must actually have.

        This is the honest way to use a published penalty. **Tuning the ratios until the budget
        reproduces the penalty and then reporting the agreement is calibration**, not validation.
        Inverting it and reporting what the vehicle implies is a different claim: it says what the
        mass chain must be doing, and leaves the reader to judge whether that is plausible.

        The inversion holds the ratio between the two fixed, because one equation cannot determine
        two unknowns, and the ratio is the part that is structural.

        """

        hardware = self.calculateHardwareMass()
        reserve = self.calculateReserve()

        if publishedPenalty <= 0.0:
            raise RecoveryError('A published penalty must be a positive mass of payload given up.')

        ratio = self.dryMassExchangeRatio / self.reserveExchangeRatio

        # penalty = hardware * (ratio * b) + reserve * b, solved for b.
        denominator = hardware['totalMass'] * ratio + reserve['reserveMass']

        if denominator <= 0.0:
            raise RecoveryError('A recovery budget with no hardware and no reserve cannot explain '
                                'a payload penalty.')

        impliedReserve = publishedPenalty / denominator
        impliedDry = impliedReserve * ratio

        return {'publishedPenalty':     publishedPenalty,
                'impliedDryMassRatio':  impliedDry,
                'impliedReserveRatio':  impliedReserve,
                'assumedDryMassRatio':  self.dryMassExchangeRatio,
                'assumedReserveRatio':  self.reserveExchangeRatio,
                'dryMassAgreement':     impliedDry / self.dryMassExchangeRatio,
                'fixedRatio':           ratio}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        """
        The hardware, the reserve, and what each costs in payload.
        """

        hardware = self.calculateHardwareMass()
        reserve = self.calculateReserve()
        penalty = self.calculatePenalty()

        lines = []

        lines.append(formatReportTable(
            [[entry['item'], f'{entry["mass"]:,.0f}', f'{entry["share"] * 100.0:.0f}%']
             for entry in hardware['items']],
            ['item', 'mass [kg]', 'share'],
            title = f'RECOVERY HARDWARE, {hardware["method"].upper()}'))

        lines.append('')
        lines.append(f'Reserve propellant {reserve["reserveMass"]:,.0f} kg, '
                     f'{reserve["reserveFraction"] * 100.0:.0f}% of the load.')
        lines.append('')

        lines.append(formatReportTable(
            [[entry['cause'],
              f'{entry["mass"]:,.0f}',
              f'{entry["payloadCost"]:,.0f}',
              f'{entry["share"] * 100.0:.0f}%'] for entry in penalty['contributions']],
            ['cause', 'mass [kg]', 'payload cost [kg]', 'share'],
            title = 'PAYLOAD PENALTY'))

        lines.append('')
        lines.append(f'Penalty {penalty["penaltyFraction"] * 100.0:.1f}% of baseline, leaving '
                     f'{penalty["recoverablePayload"]:,.0f} kg.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'recoveryBudget.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if self.mode not in RECOVERY_MODES:
            raise InvalidInputError(
                f'{self.mode} is not a recovery mode. Available: {sorted(RECOVERY_MODES)}.')

        for name, value in (('stageDryMass', self.stageDryMass),
                            ('stagePropellant', self.stagePropellant),
                            ('baselinePayload', self.baselinePayload)):
            if not np.isfinite(value) or value <= 0.0:
                raise InvalidInputError(f'{name} must be a positive mass in kilograms.')

        for name, ratio in (('dryMassExchangeRatio', self.dryMassExchangeRatio),
                            ('reserveExchangeRatio', self.reserveExchangeRatio)):
            if ratio <= 0.0:
                raise InvalidInputError(f'{name} must be positive.')

        if self.dryMassExchangeRatio <= self.reserveExchangeRatio:
            raise InvalidInputError(
                'Dry mass costs more payload per kilogram than reserve propellant, because it is '
                'carried through the whole burn and the reserve is burned at the end of it. A '
                'ratio pair the other way round is a sign convention error.')

        if np.isfinite(self.reserveFraction) and not 0.0 <= self.reserveFraction < 1.0:
            raise InvalidInputError('Reserve fraction is a fraction of the propellant load below '
                                    'one. A stage that reserves all of it does not launch.')

        for name, mass in self.hardwareItems.items():
            if float(mass) <= 0.0:
                raise InvalidInputError(f'Recovery hardware item {name} has a non-positive mass.')
