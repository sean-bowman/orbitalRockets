
# -- Inducer -- #

'''

Suction specific speed, cavitation margin, and the tank pressure a pump demands.

This class exists because of a chain that ends somewhere unexpected. A pump cavitates if its inlet
pressure is too near the vapour pressure. Avoiding that needs net positive suction head. NPSH comes
from tank pressure. Tank pressure needs a thicker tank and a heavier pressurisation system.

**So the shaft speed of the turbopump sets a fraction of the vehicle's dry mass**, through a path
with four links in it and no single owner. That is the most consequential coupling in this
sub-domain and it is the reason inducers exist at all: an inducer is a device for buying back shaft
speed that would otherwise have to be paid for in tank pressure.

The class computes the chain in both directions. Given a shaft speed it reports the tank pressure
required; given a tank pressure it reports the shaft speed available.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from turbomachineryUtils import (SUCTION_SPECIFIC_SPEED, GRAVITY,
                                     suctionSpecificSpeed, toUsSpecificSpeed,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, CavitationError)
except ImportError:
    from .turbomachineryUtils import (SUCTION_SPECIFIC_SPEED, GRAVITY,
                                      suctionSpecificSpeed, toUsSpecificSpeed,
                                      applyInputs, formatReportTable, createErrorContext,
                                      InvalidInputError, CavitationError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The margin held between available and required NPSH. Cavitation is not a graceful degradation:
# the pump loses head, the flow becomes unsteady, and the collapsing bubbles erode the blade. A
# margin below about 1.2 is not a design.
NPSH_MARGIN = 1.5    # [-]

# Cryogenic propellants get help that storables do not. Vaporising a little cryogen at the blade
# cools the surrounding liquid, which lowers its vapour pressure, which suppresses further
# vaporisation. The effect is real and it is why a LOX pump tolerates a lower NPSH than the same
# pump on water.
#
# Represented here as a multiplier on the tolerable suction specific speed. It is an approximation
# of a genuinely complicated effect and it is registered as unvalidated.
THERMODYNAMIC_SUPPRESSION = {
    'LOX':      1.30,
    'LH2':      2.00,
    'LCH4':     1.40,
    'RP-1':     1.00,
    'N2O4':     1.00,
    'MMH':      1.00,
    'ethanol':  1.00,
    'water':    1.00,
}    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- Inducer -- #
# ------------------------------------------------------------------------------------------------ #

class Inducer:

    '''

    Cavitation margin, suction specific speed, and the tank pressure a given shaft speed requires.

    '''

    def __init__(self):

        self.propellant     = ''
        self.density        = np.nan
        self.massFlow       = np.nan
        self.shaftSpeed     = np.nan
        self.tankPressure   = np.nan
        self.vapourPressure = np.nan
        self.staticHead     = np.nan
        self.lineLoss       = np.nan
        self.inducerType    = ''

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `staticHead` is the liquid column above the pump inlet, positive when the tank is above the
        pump, which on a launch vehicle it usually is. `lineLoss` is the feed line pressure drop.

        '''

        requiredParams = {'density':        (int, float),
                          'massFlow':       (int, float),
                          'shaftSpeed':     (int, float),
                          'vapourPressure': (int, float)}

        optionalParams = {'propellant':   str,
                          'tankPressure': (int, float),
                          'staticHead':   (int, float),
                          'lineLoss':     (int, float),
                          'inducerType':  str}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.inducerType:
            self.inducerType = 'inducer'

        if self.inducerType not in SUCTION_SPECIFIC_SPEED:
            raise CavitationError(
                f'Unknown inducer type \'{self.inducerType}\'. '
                f'Known: {sorted(SUCTION_SPECIFIC_SPEED)}.',
                context = createErrorContext(component = 'Inducer'))

        for name, default in (('staticHead', 0.0), ('lineLoss', 0.0)):
            if not np.isfinite(getattr(self, name)):
                setattr(self, name, default)

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def angularSpeed(self) -> float:

        return self.shaftSpeed * 2.0 * np.pi / 60.0

    def volumetricFlow(self) -> float:

        return self.massFlow / self.density

    def suppressionFactor(self) -> float:

        '''
        The thermodynamic suppression multiplier for this propellant, defaulting to none.
        '''

        return THERMODYNAMIC_SUPPRESSION.get(self.propellant, 1.00)

    def tolerableSuctionSpecificSpeed(self) -> float:

        '''
        The suction specific speed this inducer type can deliver on this propellant.
        '''

        return SUCTION_SPECIFIC_SPEED[self.inducerType]['limit'] * self.suppressionFactor()

    # -------------------------------------------------------------------------------------------- #

    def calculateAvailableNpsh(self) -> dict:

        '''

        Net positive suction head available at the pump inlet.

            NPSH_a = (P_tank - P_vapour) / (rho g) + static head - line loss

        Everything the vehicle can offer the pump. It is a property of the tank, the plumbing and
        the propellant, and the pump has no influence on it whatever.

        '''

        findings = []

        if not np.isfinite(self.tankPressure):
            raise CavitationError(
                'No tank pressure was supplied, so the available NPSH cannot be computed. Use '
                'requiredTankPressure to work the chain in the other direction.',
                context = createErrorContext(component = 'Inducer'))

        pressureHead = (self.tankPressure - self.vapourPressure) / (self.density * GRAVITY)

        available = pressureHead + self.staticHead - self.lineLoss

        findings.append(
            f'Available NPSH {available:.1f} m, from {pressureHead:.1f} m of tank pressure over '
            f'vapour, {self.staticHead:.1f} m of static column and {self.lineLoss:.1f} m of line '
            f'loss.')

        if available <= 0.0:
            findings.append(
                'A non-positive NPSH means the pump inlet is at or below the vapour pressure. That '
                'is not a small cavitation margin, it is vapour at the inlet and the pump will not '
                'pump.')

        self.findings = findings

        return {'available':    available,
                'pressureHead': pressureHead,
                'staticHead':   self.staticHead,
                'lineLoss':     self.lineLoss,
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateRequiredNpsh(self) -> dict:

        '''

        The NPSH this shaft speed requires, from the suction specific speed the inducer can deliver.

        Rearranging the suction specific speed group:

            NPSH_r = (omega sqrt(Q) / Nss)^(4/3) / g

        The four-thirds power is what makes shaft speed so expensive. **A ten per cent increase in
        shaft speed needs a fourteen per cent increase in NPSH**, and NPSH is bought with tank
        pressure.

        '''

        findings = []

        speed     = self.angularSpeed()
        flow      = self.volumetricFlow()
        tolerable = self.tolerableSuctionSpecificSpeed()

        required = (speed * np.sqrt(flow) / tolerable) ** (4.0 / 3.0) / GRAVITY

        withMargin = required * NPSH_MARGIN

        findings.append(
            f'At {self.shaftSpeed:.0f} rpm and a tolerable suction specific speed of '
            f'{tolerable:.1f}, the pump requires {required:.1f} m NPSH, or {withMargin:.1f} m with '
            f'a {NPSH_MARGIN:.1f} margin.')

        if self.suppressionFactor() > 1.0:
            findings.append(
                f'{self.propellant} gets a thermodynamic suppression factor of '
                f'{self.suppressionFactor():.2f}: vaporising a little cryogen at the blade cools '
                f'the surrounding liquid and lowers its vapour pressure, which suppresses further '
                f'vaporisation. A storable propellant gets none of that.')

        findings.append(
            'NPSH required goes as shaft speed to the four thirds, so speed is expensive. A ten '
            'per cent faster shaft needs fourteen per cent more suction head.')

        self.findings = findings

        return {'required':     required,
                'withMargin':   withMargin,
                'margin':       NPSH_MARGIN,
                'tolerable':    tolerable,
                'suppression':  self.suppressionFactor(),
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def checkMargin(self) -> dict:

        '''
        Whether the available NPSH covers the required NPSH with margin.
        '''

        findings = []

        available = self.calculateAvailableNpsh()['available']
        required  = self.calculateRequiredNpsh()

        ratio = available / required['required'] if required['required'] > 0.0 else np.inf

        adequate = ratio >= NPSH_MARGIN

        actual = suctionSpecificSpeed(self.angularSpeed(), self.volumetricFlow(),
                                      available) if available > 0.0 else np.inf

        findings.append(
            f'Available {available:.1f} m against {required["required"]:.1f} m required, a ratio '
            f'of {ratio:.2f} against a {NPSH_MARGIN:.1f} requirement.')

        findings.append(
            f'The actual suction specific speed is {actual:.1f}, '
            f'{toUsSpecificSpeed(actual):.0f} in US customary units, against a tolerable '
            f'{required["tolerable"]:.1f}.')

        if not adequate:
            findings.append(
                'The margin is inadequate. The levers are a higher tank pressure, a lower shaft '
                'speed, a better inducer, or a boost pump, and they cost respectively tank mass, '
                'turbopump mass, development, and a second machine.')

        self.findings = findings

        return {'available':   available,
                'required':    required['required'],
                'ratio':       ratio,
                'adequate':    bool(adequate),
                'actualSuctionSpecificSpeed': actual,
                'findings':    findings}

    # -------------------------------------------------------------------------------------------- #

    def requiredTankPressure(self) -> dict:

        '''

        The tank pressure this shaft speed demands, which is where the chain ends up.

        Working backwards from the required NPSH through the static head and line loss to the tank.
        This is the number that leaves the propulsion domain and lands in
        [aerospaceStructures](../../../aerospaceStructures/README.md) as a tank wall thickness, and
        in [fluidSystems](../../../fluidSystems/README.md) as a pressurisation requirement.

        **It is the reason shaft speed is a vehicle-level decision rather than a turbopump one.**

        '''

        findings = []

        required = self.calculateRequiredNpsh()['withMargin']

        neededHead = required - self.staticHead + self.lineLoss

        pressure = self.vapourPressure + neededHead * self.density * GRAVITY

        findings.append(
            f'{required:.1f} m of NPSH with margin, less {self.staticHead:.1f} m of static column '
            f'and plus {self.lineLoss:.1f} m of line loss, needs {neededHead:.1f} m at the tank.')

        findings.append(
            f'That is a tank pressure of {pressure / 1000.0:.0f} kPa, against a vapour pressure of '
            f'{self.vapourPressure / 1000.0:.0f} kPa.')

        findings.append(
            'This number leaves the propulsion domain. It sizes the tank wall and the '
            'pressurisation system, so the turbopump shaft speed is buying or spending vehicle dry '
            'mass through a chain with four links and no single owner.')

        self.findings = findings

        return {'tankPressure':  pressure,
                'neededHead':    neededHead,
                'requiredNpsh':  required,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def maximumShaftSpeed(self, availableNpsh: float = None) -> dict:

        '''

        The fastest shaft this suction condition allows.

            omega_max = Nss (g NPSH)^0.75 / sqrt(Q)

        The other direction of the same relation, and the one that matters when the tank pressure
        is already fixed by something else.

        '''

        findings = []

        available = (self.calculateAvailableNpsh()['available']
                     if availableNpsh is None else float(availableNpsh))

        if available <= 0.0:
            raise CavitationError(
                f'The available NPSH is {available:.1f} m, which is not positive. No shaft speed '
                f'works at a pump inlet below the vapour pressure.',
                context = createErrorContext(component = 'Inducer'))

        usable    = available / NPSH_MARGIN
        tolerable = self.tolerableSuctionSpecificSpeed()

        speed = tolerable * (GRAVITY * usable) ** 0.75 / np.sqrt(self.volumetricFlow())

        rpm = speed * 60.0 / (2.0 * np.pi)

        findings.append(
            f'{available:.1f} m available, {usable:.1f} m after margin, allows {rpm:.0f} rpm at a '
            f'suction specific speed of {tolerable:.1f}.')

        comparison = {}
        for name, entry in SUCTION_SPECIFIC_SPEED.items():
            limit = entry['limit'] * self.suppressionFactor()
            comparison[name] = {
                'suctionSpecificSpeed': limit,
                'maximumRpm': limit * (GRAVITY * usable) ** 0.75
                              / np.sqrt(self.volumetricFlow()) * 60.0 / (2.0 * np.pi),
                'note': entry['note']}

        findings.append(
            f'Without an inducer the same suction condition allows only '
            f'{comparison["no inducer"]["maximumRpm"]:.0f} rpm. The inducer is buying a factor of '
            f'{comparison["inducer"]["maximumRpm"] / comparison["no inducer"]["maximumRpm"]:.1f} '
            f'in shaft speed, which is the entire reason it is fitted.')

        self.findings = findings

        return {'maximumRpm':     rpm,
                'availableNpsh':  available,
                'usableNpsh':     usable,
                'comparison':     comparison,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full cavitation report.
        '''

        required = self.calculateRequiredNpsh()
        tank     = self.requiredTankPressure()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  INDUCER AND CAVITATION: '
                     f'{self.propellant if self.propellant else "propellant"}')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Mass flow',        f'{self.massFlow:.2f}',                    'kg/s'],
                ['Density',          f'{self.density:.1f}',                     'kg/m^3'],
                ['Shaft speed',      f'{self.shaftSpeed:.0f}',                  'rpm'],
                ['Vapour pressure',  f'{self.vapourPressure / 1000.0:.0f}',     'kPa'],
                ['Inducer type',     self.inducerType,                          ''],
                ['Suppression',      f'{self.suppressionFactor():.2f}',         ''],
                ['Tolerable Nss',    f'{required["tolerable"]:.1f}',            ''],
                ['NPSH required',    f'{required["required"]:.1f}',             'm'],
                ['  with margin',    f'{required["withMargin"]:.1f}',           'm'],
                ['Tank pressure required', f'{tank["tankPressure"] / 1000.0:.0f}', 'kPa']]

        if np.isfinite(self.tankPressure):
            margin = self.checkMargin()
            rows.append(['NPSH available', f'{margin["available"]:.1f}', 'm'])
            rows.append(['Margin ratio',   f'{margin["ratio"]:.2f}',    ''])
            rows.append(['Adequate',       str(margin['adequate']),     ''])

        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Cavitation'))

        lines.append('')
        for finding in (required['findings'] + tank['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            label = (self.propellant if self.propellant else 'inducer').replace('/', '_')
            with open(os.path.join(outputDir, f'inducer_{label}.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('density', self.density), ('mass flow', self.massFlow),
                            ('shaft speed', self.shaftSpeed)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(component = 'Inducer'))

        if self.vapourPressure < 0.0:
            raise InvalidInputError(
                f'The vapour pressure cannot be negative, got {self.vapourPressure}.',
                context = createErrorContext(component = 'Inducer'))

        if np.isfinite(self.tankPressure) and self.tankPressure <= self.vapourPressure:
            raise CavitationError(
                f'The tank pressure {self.tankPressure / 1000.0:.1f} kPa is at or below the vapour '
                f'pressure {self.vapourPressure / 1000.0:.1f} kPa. The tank contains vapour, not '
                f'liquid, and there is nothing for the pump to draw.',
                context = createErrorContext(component = 'Inducer'))
