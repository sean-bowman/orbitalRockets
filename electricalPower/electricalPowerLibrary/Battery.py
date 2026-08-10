
# -- Battery -- #

'''

Battery sizing, and the two derations that decide the answer.

The nameplate capacity is not the capacity. Two factors come off it before anything is delivered,
and both are larger than most energy budget margins.

**Depth of discharge** is a life and reliability limit rather than a physical one. A pack that has
to survive many cycles is held to half its capacity; a primary battery used once can go to ninety
per cent. That is a factor of nearly two between two batteries with the same label.

**Temperature** is the one that bites on a launch vehicle. A battery cold-soaked on the pad at
minus twenty delivers three quarters of its rated capacity, and the vehicle that sized it at twenty
degrees has lost a quarter of its energy before the count starts.

Multiply those together and a nameplate 100 W h pack that is cycled and cold delivers under 40 W h.
**The chemistry choice matters less than the two derations**, which is the opposite of how the
trade is usually presented.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from powerUtils import (BATTERY_CHEMISTRIES, DEPTH_OF_DISCHARGE,
                            TEMPERATURE_CAPACITY_FACTOR, interpolateFactor,
                            applyInputs, formatReportTable, createErrorContext,
                            InvalidInputError, PowerBudgetError)
except ImportError:
    from .powerUtils import (BATTERY_CHEMISTRIES, DEPTH_OF_DISCHARGE,
                             TEMPERATURE_CAPACITY_FACTOR, interpolateFactor,
                             applyInputs, formatReportTable, createErrorContext,
                             InvalidInputError, PowerBudgetError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Pack-level specific energy as a fraction of cell level, once the case, interconnects, management
# electronics and thermal hardware are counted. Representative, and registered as unvalidated.
PACK_FRACTION = 0.68    # [-]

# Energy margin held above the computed mission energy.
DEFAULT_ENERGY_MARGIN = 0.25    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- Battery -- #
# ------------------------------------------------------------------------------------------------ #

class Battery:

    '''

    Usable capacity after derating, pack mass, and whether the discharge rate is achievable.

    '''

    def __init__(self):

        self.chemistry     = ''
        self.busVoltage    = np.nan
        self.missionEnergy = np.nan
        self.peakPower     = np.nan
        self.temperature   = np.nan
        self.cycleClass    = ''
        self.energyMargin  = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `missionEnergy` is the energy the loads actually consume, in joules, and it comes from
        [PowerBudget](PowerBudget.py). `temperature` is the coldest the battery gets while it has
        to deliver, which is usually the pad rather than flight.

        '''

        requiredParams = {'chemistry':     str,
                          'busVoltage':    (int, float),
                          'missionEnergy': (int, float)}

        optionalParams = {'peakPower':    (int, float),
                          'temperature':  (int, float),
                          'cycleClass':   str,
                          'energyMargin': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.cycleClass:
            self.cycleClass = 'single use'

        if not np.isfinite(self.temperature):
            self.temperature = 20.0

        if not np.isfinite(self.energyMargin):
            self.energyMargin = DEFAULT_ENERGY_MARGIN

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def chemistryData(self) -> dict:

        return BATTERY_CHEMISTRIES[self.chemistry]

    # -------------------------------------------------------------------------------------------- #

    def calculateDerating(self) -> dict:

        '''

        What fraction of the nameplate capacity is actually available.

        Both factors multiply, and neither is a margin: they are the difference between what the
        label says and what the battery does. A margin sits on top of the derated number.

        '''

        depth = DEPTH_OF_DISCHARGE[self.cycleClass]

        temperature = interpolateFactor(TEMPERATURE_CAPACITY_FACTOR, self.temperature)

        usable = depth * temperature

        return {'depthOfDischarge':  depth,
                'temperatureFactor': temperature,
                'usableFraction':    usable,
                'temperature':       self.temperature,
                'cycleClass':        self.cycleClass}

    # -------------------------------------------------------------------------------------------- #

    def sizePack(self) -> dict:

        '''

        The pack the mission needs, after derating and margin.

        The chain is: mission energy, plus margin, divided by the usable fraction, gives the
        nameplate capacity required. Then the specific energy and the pack fraction give a mass.

        '''

        findings = []

        derating = self.calculateDerating()

        chemistry = self.chemistryData()

        withMargin = self.missionEnergy * (1.0 + self.energyMargin)

        nameplate = withMargin / derating['usableFraction']

        # specific energy is quoted in watt hours per kilogram
        cellSpecific = chemistry['specificEnergy'] * 3600.0    # [J/kg]

        packSpecific = cellSpecific * PACK_FRACTION

        mass = nameplate / packSpecific

        cellCount = int(np.ceil(self.busVoltage / chemistry['nominalVoltage']))

        capacityAmpHours = nameplate / (3600.0 * self.busVoltage)

        findings.append(
            f'Mission energy {self.missionEnergy / 3600.0:.1f} W h, plus '
            f'{self.energyMargin:.0%} margin, is {withMargin / 3600.0:.1f} W h to deliver.')

        findings.append(
            f'Only {derating["usableFraction"]:.0%} of the nameplate is available: '
            f'{derating["depthOfDischarge"]:.0%} depth of discharge for a {self.cycleClass} pack '
            f'and {derating["temperatureFactor"]:.0%} at {self.temperature:.0f} C.')

        findings.append(
            f'So the nameplate has to be {nameplate / 3600.0:.1f} W h, which is '
            f'{nameplate / withMargin:.2f} times the energy actually delivered.')

        findings.append(
            f'At {chemistry["specificEnergy"]:.0f} W h/kg cell level and {PACK_FRACTION:.0%} pack '
            f'fraction, that is {mass:.2f} kg in about {cellCount} cells in series.')

        self.findings = findings

        return {'missionEnergy':    self.missionEnergy,
                'withMargin':       withMargin,
                'derating':         derating,
                'nameplateEnergy':  nameplate,
                'capacityAmpHours': capacityAmpHours,
                'packMass':         mass,
                'cellsInSeries':    cellCount,
                'oversizeFactor':   nameplate / self.missionEnergy,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def checkDischargeRate(self) -> dict:

        '''

        Whether the pack can deliver the peak power, which is a separate question from the energy.

        A battery sized on energy alone can be unable to deliver the current, and the two are
        decoupled: a long low load sizes on energy and a short high load sizes on rate. **Which one
        governs decides the chemistry**, and it is the only place in this class where the chemistry
        choice actually changes the answer.

        '''

        if not np.isfinite(self.peakPower):
            raise InvalidInputError(
                'A peak power is needed to check the discharge rate. Sizing on energy alone is how '
                'a pack that cannot deliver the current gets built.',
                context = createErrorContext(component = 'Battery'))

        findings = []

        sized = self.sizePack()

        chemistry = self.chemistryData()

        # the C rate the mission demands of the pack as sized
        demandedRate = self.peakPower / (sized['nameplateEnergy'] / 3600.0)

        limit = chemistry['maximumDischargeRate']

        adequate = bool(demandedRate <= limit)

        findings.append(
            f'A peak of {self.peakPower:.0f} W from a {sized["nameplateEnergy"] / 3600.0:.1f} W h '
            f'pack is {demandedRate:.2f} C, against a limit of {limit:.1f} C for '
            f'{self.chemistry}.')

        if not adequate:

            required = self.peakPower / limit * 3600.0

            findings.append(
                f'**The rate governs rather than the energy.** The pack has to be '
                f'{required / 3600.0:.1f} W h to deliver the current, which is '
                f'{required / sized["nameplateEnergy"]:.1f} times what the energy alone needed.')

            raise PowerBudgetError(
                f'The pack sized on energy delivers {sized["nameplateEnergy"] / 3600.0:.1f} W h '
                f'and cannot supply {self.peakPower:.0f} W, which needs {demandedRate:.2f} C '
                f'against a {limit:.1f} C limit. **A battery that cannot deliver the current is '
                f'not a battery with a small negative margin**, so this is refused. Either size on '
                f'rate at {required / 3600.0:.1f} W h, or choose a chemistry that supports the '
                f'rate: {sorted(name for name, entry in BATTERY_CHEMISTRIES.items() if entry["maximumDischargeRate"] >= demandedRate)}.',
                context = createErrorContext(component = 'Battery'))

        findings.append(
            f'Energy governs, with {limit / demandedRate:.1f} times the rate capability in hand.')

        self.findings = findings

        return {'peakPower':      self.peakPower,
                'demandedRate':   demandedRate,
                'rateLimit':      limit,
                'adequate':       adequate,
                'governedBy':     'energy',
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def compareChemistries(self) -> dict:

        '''

        The same mission across chemistries, which shows how little of the answer is chemistry.

        '''

        original = self.chemistry

        results = {}

        try:
            for name in BATTERY_CHEMISTRIES:

                self.chemistry = name

                sized = self.sizePack()

                entry = {'packMass':  sized['packMass'],
                         'nameplate': sized['nameplateEnergy'],
                         'rateLimit': BATTERY_CHEMISTRIES[name]['maximumDischargeRate']}

                if np.isfinite(self.peakPower):
                    demanded = self.peakPower / (sized['nameplateEnergy'] / 3600.0)
                    entry['rateAdequate'] = bool(demanded <= entry['rateLimit'])
                    entry['demandedRate'] = demanded

                results[name] = entry

        finally:
            self.chemistry = original

        viable = {name: entry for name, entry in results.items()
                  if entry.get('rateAdequate', True)}

        lightest = min(viable, key = lambda name: viable[name]['packMass']) if viable else None

        return {'results':  results,
                'viable':   sorted(viable),
                'lightest': lightest}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full battery report.
        '''

        sized = self.sizePack()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  BATTERY: {self.chemistry}, {self.busVoltage:.0f} V bus at '
                     f'{self.temperature:.0f} C')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Mission energy',      f'{self.missionEnergy / 3600.0:.1f}',                 'W h'],
             ['Energy margin',       f'{self.energyMargin:.0%}',                           ''],
             ['Depth of discharge',  f'{sized["derating"]["depthOfDischarge"]:.0%}',       ''],
             ['Temperature factor',  f'{sized["derating"]["temperatureFactor"]:.0%}',      ''],
             ['Usable fraction',     f'{sized["derating"]["usableFraction"]:.0%}',         ''],
             ['Nameplate required',  f'{sized["nameplateEnergy"] / 3600.0:.1f}',           'W h'],
             ['Capacity',            f'{sized["capacityAmpHours"]:.2f}',                   'A h'],
             ['Oversize factor',     f'{sized["oversizeFactor"]:.2f}',                     'x'],
             ['Pack mass',           f'{sized["packMass"]:.2f}',                           'kg'],
             ['Cells in series',     f'{sized["cellsInSeries"]}',                          '']],
            ['Quantity', 'Value', 'Unit'], title = 'Sizing'))

        lines.append('')
        for finding in sized['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append(f'    - {self.chemistryData()["note"]}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'battery.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.chemistry not in BATTERY_CHEMISTRIES:
            raise InvalidInputError(
                f"Unknown chemistry '{self.chemistry}'. Known chemistries are "
                f'{sorted(BATTERY_CHEMISTRIES)}.',
                context = createErrorContext(component = 'Battery'))

        if self.cycleClass not in DEPTH_OF_DISCHARGE:
            raise InvalidInputError(
                f"Unknown cycle class '{self.cycleClass}'. Known classes are "
                f'{sorted(DEPTH_OF_DISCHARGE)}.',
                context = createErrorContext(component = 'Battery'))

        for name, value in (('bus voltage',    self.busVoltage),
                            ('mission energy', self.missionEnergy)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'Battery'))

        if self.energyMargin < 0.0:
            raise InvalidInputError(
                f'The energy margin cannot be negative, got {self.energyMargin}.',
                context = createErrorContext(component = 'Battery'))

        limit = self.chemistryData()['lowTemperatureLimit']

        if self.temperature < limit:
            raise PowerBudgetError(
                f'The battery is at {self.temperature:.0f} C and {self.chemistry} has a low '
                f'temperature limit of {limit:.0f} C. Below it the capacity model here does not '
                f'apply and the cell may not deliver at all, so this is refused rather than '
                f'extrapolated. Heat the battery or change the chemistry.',
                context = createErrorContext(component = 'Battery'))

        if np.isfinite(self.peakPower) and self.peakPower < 0.0:
            raise InvalidInputError(
                f'The peak power cannot be negative, got {self.peakPower}.',
                context = createErrorContext(component = 'Battery'))
