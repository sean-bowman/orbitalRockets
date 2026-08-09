
# -- RegenerativeCooling -- #

'''

Gas-side heat flux from Bartz, coolant side capability, wall temperature and the channel geometry.

The organising idea is that regenerative cooling is not a heat transfer problem with a margin. It
is a closure problem with three separate ways to fail, and passing one of them says nothing about
the other two.

    the wall must stay below its material limit          a conduction and film problem
    the coolant must not exceed its own limit            a bulk temperature problem
    the pressure drop must fit the available head        a plumbing problem

The second is the one that decides whether an engine can be regeneratively cooled at all, because
it does not depend on the channel design. Total heat load divided by coolant flow and specific heat
is a bulk temperature rise, and if that rise puts the coolant past its decomposition or coking limit
then no amount of channel work fixes it. That check needs the heat load and the flow and nothing
else, and it should be the first thing computed rather than the last.

For the reference engine it comes out negative, and that is the useful result rather than an
inconvenience. See `checkCoolantCapability`.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from combustionUtils import (bartzCoefficient, combustionGasProperties,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, CoolingError)
except ImportError:
    from .combustionUtils import (bartzCoefficient, combustionGasProperties,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, CoolingError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Coolant limits. The number that matters is not the boiling point, it is the temperature at which
# the fluid starts destroying itself or the passage. For hydrocarbons that is coking: the fuel
# cracks at the hot wall and lays down carbon, which insulates the wall it was cooling and starts a
# runaway. For hydrazines it is thermal decomposition, which is exothermic and considerably worse.
#
# These are bulk limits. The film temperature at the wall is higher than the bulk by the coolant
# side film drop, so a design that closes on bulk temperature can still coke at the wall.
COOLANT_LIMITS = {
    'RP-1':      {'limit': 575.0, 'specificHeat': 2100.0, 'density': 810.0,
                  'note': 'coking. The carbon layer insulates the wall it was cooling'},
    'LCH4':      {'limit': 700.0, 'specificHeat': 3500.0, 'density': 423.0,
                  'note': 'far less prone to coking than kerosene, which is much of its appeal'},
    'LH2':       {'limit': 900.0, 'specificHeat': 14300.0, 'density': 71.0,
                  'note': 'enormous specific heat and no decomposition. The ideal coolant'},
    'MMH':       {'limit': 480.0, 'specificHeat': 2900.0, 'density': 878.0,
                  'note': 'thermal decomposition, and it is exothermic'},
    'ethanol':   {'limit': 600.0, 'specificHeat': 2600.0, 'density': 789.0,
                  'note': 'well behaved, and the low boiling point wants pressure to suppress it'},
}    # [K], [J/kg K], [kg/m^3]

# Which propellant is the coolant, per combination. It is the fuel in every case here, because the
# oxidiser is the thing you least want in a hot passage, and an oxidiser leak into the jacket is
# not a leak, it is a fire.
COOLANT_BY_COMBINATION = {
    'LOX/RP-1':    'RP-1',
    'LOX/LCH4':    'LCH4',
    'LOX/LH2':     'LH2',
    'N2O4/MMH':    'MMH',
    'LOX/ethanol': 'ethanol',
}

# Throat radius of curvature as a multiple of throat radius. It appears in Bartz to the 0.1 power,
# so the answer is insensitive to it, which is convenient because it is rarely known early.
THROAT_CURVATURE_RATIO = 1.5    # [-]

# Wall material limits. The copper alloys conduct well enough to keep the gas-side face cool and
# they are the only realistic choice at high flux; the superalloys tolerate more temperature and
# conduct an order less, which puts the gas-side face hotter for the same coolant.
WALL_MATERIALS = {
    'GRCop-42':  {'limit': 800.0, 'conductivity': 320.0,
                  'note': 'the modern chamber liner. Printable, and it survives the cycles'},
    'NARloy-Z':  {'limit': 800.0, 'conductivity': 320.0,
                  'note': 'the Shuttle main engine liner. Same regime as GRCop'},
    'C18150':    {'limit': 750.0, 'conductivity': 320.0,
                  'note': 'chromium zirconium copper. Lower strength at temperature'},
    'Inconel 718': {'limit': 900.0, 'conductivity': 25.0,
                    'note': 'tolerates more and conducts far less. A film cooled wall, not a regen one'},
}    # [K], [W/m K]

# Sections the heat load is integrated over, as a fraction of the wall each one contributes. The
# integration is done properly in calculateHeatLoad; these are the labels.
INTEGRATION_STEPS = 40    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- RegenerativeCooling -- #
# ------------------------------------------------------------------------------------------------ #

class RegenerativeCooling:

    '''

    Heat load, coolant capability, wall temperature and channel sizing for a regeneratively cooled
    chamber.

    '''

    def __init__(self):

        self.combination     = ''
        self.chamberPressure = np.nan
        self.throatDiameter  = np.nan
        self.contractionRatio = np.nan
        self.areaRatio       = np.nan
        self.barrelLength    = np.nan
        self.convergentLength = np.nan
        self.divergentLength = np.nan
        self.coolantFlow     = np.nan
        self.coolantInlet    = np.nan
        self.wallMaterial    = ''
        self.wallThickness   = np.nan
        self.wallTemperature = np.nan

        self.gasProperties = {}
        self.findings      = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Geometry comes from the hub `EngineSizing`, which is the intended source. Supplying it
        directly is allowed so this class can be used on a chamber that was not sized here.

        `wallTemperature` is the gas-side wall temperature the flux is evaluated at. It is an input
        rather than an output because Bartz is implicit in it, and iterating it against a channel
        design is a different calculation from establishing whether the heat load can be carried at
        all.

        '''

        requiredParams = {'combination':     str,
                          'chamberPressure': (int, float),
                          'throatDiameter':  (int, float),
                          'coolantFlow':     (int, float)}

        optionalParams = {'contractionRatio': (int, float),
                          'areaRatio':        (int, float),
                          'barrelLength':     (int, float),
                          'convergentLength': (int, float),
                          'divergentLength':  (int, float),
                          'coolantInlet':     (int, float),
                          'wallMaterial':     str,
                          'wallThickness':    (int, float),
                          'wallTemperature':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        defaults = {'contractionRatio': 2.5, 'areaRatio': 20.0, 'coolantInlet': 290.0,
                    'wallThickness': 0.001, 'wallTemperature': 800.0}

        for name, value in defaults.items():
            if not np.isfinite(getattr(self, name)):
                setattr(self, name, value)

        if not self.wallMaterial:
            self.wallMaterial = 'GRCop-42'

        throatRadius = self.throatDiameter / 2.0

        if not np.isfinite(self.barrelLength):
            self.barrelLength = 0.40
        if not np.isfinite(self.convergentLength):
            chamberRadius = throatRadius * np.sqrt(self.contractionRatio)
            self.convergentLength = (chamberRadius - throatRadius) / np.tan(np.radians(30.0))
        if not np.isfinite(self.divergentLength):
            exitRadius = throatRadius * np.sqrt(self.areaRatio)
            self.divergentLength = 0.80 * (exitRadius - throatRadius) / np.tan(np.radians(15.0))

        self._validateInputs()

        self.gasProperties = combustionGasProperties(self.combination)

    # -------------------------------------------------------------------------------------------- #

    def calculateHeatFlux(self, areaRatioToThroat: float = 1.0) -> dict:

        '''

        Bartz heat flux at a station, given as the local area over the throat area.

        The throat is the peak by a wide margin, because the coefficient carries `(At/A)^0.9`. At a
        contraction ratio of 2.5 the barrel is already at less than half the throat flux, and the
        divergent section falls away faster still.

        '''

        return bartzCoefficient(self.throatDiameter,
                                THROAT_CURVATURE_RATIO * self.throatDiameter / 2.0,
                                self.chamberPressure,
                                self.gasProperties['characteristicVelocity'],
                                areaRatioToThroat,
                                self.wallTemperature,
                                self.gasProperties)

    # -------------------------------------------------------------------------------------------- #

    def calculateHeatLoad(self) -> dict:

        '''

        Total heat load, by integrating the Bartz flux over the actual wetted geometry.

        The three sections are integrated separately because they behave differently. The barrel is
        at constant area and constant flux. The convergent section accelerates to the throat and
        carries the peak. The divergent section has by far the most area and by far the lowest flux,
        and the product of those two is not negligible: it is a third of the total here.

        '''

        findings = []

        throatRadius = self.throatDiameter / 2.0
        throatArea   = np.pi * throatRadius ** 2

        sections = {}

        # barrel, constant area
        chamberRadius = throatRadius * np.sqrt(self.contractionRatio)
        barrelArea    = 2.0 * np.pi * chamberRadius * self.barrelLength
        barrelFlux    = self.calculateHeatFlux(self.contractionRatio)['heatFlux']

        sections['barrel'] = {'area': barrelArea, 'meanFlux': barrelFlux,
                              'load': barrelArea * barrelFlux}

        # convergent, area ratio falling from the contraction ratio to one
        sections['convergent'] = self._integrateSection(
            self.contractionRatio, 1.0, self.convergentLength, throatRadius)

        # divergent, area ratio rising from one to the expansion ratio
        sections['divergent'] = self._integrateSection(
            1.0, self.areaRatio, self.divergentLength, throatRadius)

        totalArea = sum(entry['area'] for entry in sections.values())
        totalLoad = sum(entry['load'] for entry in sections.values())

        peakFlux = self.calculateHeatFlux(1.0)['heatFlux']

        findings.append(
            f'Peak flux {peakFlux / 1.0e6:.1f} MW/m^2 at the throat, against a wall at '
            f'{self.wallTemperature:.0f} K.')

        findings.append(
            f'Total heat load {totalLoad / 1.0e6:.2f} MW over {totalArea * 1.0e4:.0f} cm^2, an '
            f'area-weighted mean of {totalLoad / totalArea / 1.0e6:.2f} MW/m^2.')

        divergentShare = sections['divergent']['load'] / totalLoad

        findings.append(
            f'The divergent section is {sections["divergent"]["area"] / totalArea:.0%} of the area '
            f'and {divergentShare:.0%} of the load. It runs at a low flux and there is a great deal '
            f'of it, and neglecting it understates the load by a third.')

        findings.append(
            'Bartz is quoted at plus or minus twenty per cent and is worse in the convergent '
            'section. These numbers carry that, and a cooling design that closes on a ten per cent '
            'margin has not closed.')

        self.findings = findings

        return {'sections':      sections,
                'totalArea':     totalArea,
                'totalLoad':     totalLoad,
                'meanFlux':      totalLoad / totalArea,
                'peakFlux':      peakFlux,
                'throatArea':    throatArea,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def checkCoolantCapability(self) -> dict:

        '''

        Whether the coolant can absorb the heat load without exceeding its own limit.

        This is the first check to run and the one most often run last. It needs the heat load, the
        coolant flow and the coolant specific heat, and nothing about the channel design at all:

            dT = Q / (mdot cp)

        If that rise puts the coolant past its coking or decomposition limit then the chamber cannot
        be regeneratively cooled by that flow, and no channel geometry changes it. The answers are
        film cooling, a larger coolant flow, a lower chamber pressure or a different coolant.

        The limit here is a bulk temperature. The film temperature at the wall is higher, so a
        design that closes on bulk can still coke at the wall, and the margin has to cover that.

        '''

        findings = []

        heat = self.calculateHeatLoad()

        coolantName = COOLANT_BY_COMBINATION.get(self.combination)

        if coolantName is None:
            raise CoolingError(
                f'No coolant is defined for \'{self.combination}\'. Known: '
                f'{sorted(COOLANT_BY_COMBINATION)}.',
                context = createErrorContext(component = 'RegenerativeCooling'))

        coolant = COOLANT_LIMITS[coolantName]

        temperatureRise = heat['totalLoad'] / (self.coolantFlow * coolant['specificHeat'])
        outlet          = self.coolantInlet + temperatureRise

        margin   = coolant['limit'] - outlet
        # cast explicitly: a numpy bool fails an `is True` identity check, and callers
        # and tests both reasonably use one
        feasible = bool(outlet <= coolant['limit'])

        # the flow that would be needed to close, and the fraction of the fuel it represents
        requiredFlow = (heat['totalLoad']
                        / (coolant['specificHeat'] * (coolant['limit'] - self.coolantInlet)))

        findings.append(
            f'{self.coolantFlow:.2f} kg/s of {coolantName} absorbing '
            f'{heat["totalLoad"] / 1.0e6:.2f} MW rises {temperatureRise:.0f} K, from '
            f'{self.coolantInlet:.0f} K to {outlet:.0f} K.')

        findings.append(
            f'The {coolantName} limit is {coolant["limit"]:.0f} K: {coolant["note"]}.')

        if feasible:
            findings.append(
                f'The circuit closes with {margin:.0f} K of margin on bulk temperature. The film '
                f'temperature at the wall is higher than the bulk, so that margin is not all '
                f'available.')
        else:
            findings.append(
                f'The circuit does not close. The outlet is {-margin:.0f} K past the limit, and '
                f'{requiredFlow:.2f} kg/s would be needed against the {self.coolantFlow:.2f} kg/s '
                f'available, a factor of {requiredFlow / self.coolantFlow:.2f}.')
            findings.append(
                'No channel geometry fixes this. The levers are film cooling to remove load from '
                'the regenerative circuit, a lower chamber pressure, a different coolant, or a '
                'larger engine, because heat load per unit coolant flow falls slowly with scale.')

        findings.append(
            f'The load is {heat["totalLoad"] / self.coolantFlow / 1000.0:.0f} kJ per kilogram of '
            f'coolant. That ratio is the honest figure of merit for a regenerative circuit, and it '
            f'is what makes small high pressure engines hard.')

        self.findings = findings

        return {'coolant':          coolantName,
                'temperatureRise':  temperatureRise,
                'outletTemperature': outlet,
                'limit':            coolant['limit'],
                'margin':           margin,
                'feasible':         feasible,
                'requiredFlow':     requiredFlow,
                'loadPerUnitFlow':  heat['totalLoad'] / self.coolantFlow,
                'heatLoad':         heat['totalLoad'],
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateWallTemperature(self, coolantBulkTemperature: float = None) -> dict:

        '''

        The temperature drop through the wall at the throat, and the coolant side coefficient the
        design requires.

        A series resistance: gas film, wall conduction, coolant film. The wall conduction term is
        why chamber liners are copper. At 320 W/m K and a millimetre thick, a 52 MW/m^2 flux drops
        163 K across the wall. The same wall in Inconel at 25 W/m K drops 2085 K, which is not a
        wall, it is a hole.

        The coolant side is reported as a required coefficient rather than assumed, because at
        these fluxes an assumed value produces nonsense in one direction or the other. Fifty
        megawatts per square metre through a film drop of a hundred kelvin needs half a million
        watts per square metre kelvin, and stating that as a requirement is honest where assuming
        thirty thousand and reporting a seventeen hundred kelvin film drop is not.

        '''

        findings = []

        material = WALL_MATERIALS.get(self.wallMaterial)

        if material is None:
            raise CoolingError(
                f'Unknown wall material \'{self.wallMaterial}\'. Known: {sorted(WALL_MATERIALS)}.',
                context = createErrorContext(component = 'RegenerativeCooling'))

        throat = self.calculateHeatFlux(1.0)

        flux = throat['heatFlux']

        wallDrop = flux * self.wallThickness / material['conductivity']

        coolantSideTemperature = self.wallTemperature - wallDrop

        # the local bulk coolant temperature at the throat, taken as the mid-circuit value unless
        # one is supplied, because the throat is roughly halfway around a counterflow circuit
        if coolantBulkTemperature is None:
            capability = self.checkCoolantCapability()
            coolantBulkTemperature = self.coolantInlet + 0.5 * capability['temperatureRise']

        filmDrop = coolantSideTemperature - coolantBulkTemperature

        requiredCoefficient = flux / filmDrop if filmDrop > 0.0 else np.inf

        findings.append(
            f'At {flux / 1.0e6:.1f} MW/m^2 through {self.wallThickness * 1000.0:.1f} mm of '
            f'{self.wallMaterial} at {material["conductivity"]:.0f} W/m K, the wall drops '
            f'{wallDrop:.0f} K.')

        if np.isfinite(requiredCoefficient):
            findings.append(
                f'The gas-side face at {self.wallTemperature:.0f} K puts the coolant-side face at '
                f'{coolantSideTemperature:.0f} K, against a bulk coolant at '
                f'{coolantBulkTemperature:.0f} K. Holding that {filmDrop:.0f} K film drop needs '
                f'{requiredCoefficient / 1000.0:.0f} kW/m^2 K on the coolant side.')

            findings.append(
                'A high velocity supercritical hydrocarbon in a millimetre-scale channel reaches '
                'roughly 50 to 200 kW/m^2 K. Anything much past that is asking the channel design '
                'for something it cannot give, and the answer is film cooling rather than a finer '
                'channel.')
        else:
            findings.append(
                f'The coolant-side face at {coolantSideTemperature:.0f} K is at or below the bulk '
                f'coolant at {coolantBulkTemperature:.0f} K, so there is no film drop available and '
                f'no coolant side coefficient closes this. The wall cannot be held at '
                f'{self.wallTemperature:.0f} K by this circuit.')

        if self.wallTemperature > material['limit']:
            findings.append(
                f'The gas-side face is {self.wallTemperature - material["limit"]:.0f} K above the '
                f'{material["limit"]:.0f} K limit for {self.wallMaterial}. That is a life problem '
                f'rather than an immediate one: copper alloys creep and the thermal cycle count '
                f'falls away quickly above the limit.')

        comparison = {}
        for name, entry in WALL_MATERIALS.items():
            comparison[name] = {'wallDrop': flux * self.wallThickness / entry['conductivity'],
                                'limit':    entry['limit'],
                                'conductivity': entry['conductivity']}

        findings.append(
            'A superalloy wall at the same thickness drops an order more temperature, which is why '
            'a high flux chamber is copper and an Inconel chamber is film cooled rather than '
            'regeneratively cooled.')

        self.findings = findings

        return {'heatFlux':               flux,
                'wallDrop':               wallDrop,
                'filmDrop':               filmDrop,
                'requiredCoefficient':    requiredCoefficient,
                'coolantBulkTemperature': coolantBulkTemperature,
                'gasSideTemperature':     self.wallTemperature,
                'coolantSideTemperature': coolantSideTemperature,
                'materialLimit':          material['limit'],
                'withinLimit':            bool(self.wallTemperature <= material['limit']),
                'comparison':             comparison,
                'findings':               findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeChannels(self, channelCount: int = 100, channelHeight: float = 0.003) -> dict:

        '''

        Channel velocity and pressure drop for a rectangular channel jacket at the throat.

        A first pass. The channel width is what is left of the circumference after the ribs, the
        velocity follows from the flow and the flow area, and the pressure drop follows from the
        velocity. The purpose is to establish whether the numbers are anywhere near sensible before
        anything is designed.

        '''

        findings = []

        coolantName = COOLANT_BY_COMBINATION[self.combination]
        coolant     = COOLANT_LIMITS[coolantName]

        if channelCount < 1:
            raise CoolingError(f'Channel count must be at least one, got {channelCount}.',
                               context = createErrorContext(component = 'RegenerativeCooling'))

        throatCircumference = np.pi * self.throatDiameter

        # half the circumference goes to ribs at the throat, which is typical for a milled jacket
        channelWidth = 0.5 * throatCircumference / channelCount
        flowArea     = channelCount * channelWidth * channelHeight

        velocity = self.coolantFlow / (coolant['density'] * flowArea)

        hydraulicDiameter = (2.0 * channelWidth * channelHeight
                             / (channelWidth + channelHeight))

        # Darcy friction factor from a smooth-wall approximation, then the channel drop over the
        # throat region only. The full circuit is longer and this is the local figure.
        reynolds = coolant['density'] * velocity * hydraulicDiameter / 1.0e-3
        friction = 0.184 / reynolds ** 0.2 if reynolds > 4000.0 else 64.0 / max(reynolds, 1.0)

        length        = self.barrelLength + self.convergentLength + self.divergentLength
        pressureDrop  = (friction * length / hydraulicDiameter
                         * 0.5 * coolant['density'] * velocity ** 2)

        findings.append(
            f'{channelCount} channels {channelWidth * 1000.0:.2f} mm wide by '
            f'{channelHeight * 1000.0:.1f} mm deep at the throat give {velocity:.1f} m/s.')

        findings.append(
            f'Pressure drop {pressureDrop / 1.0e6:.2f} MPa over {length * 1000.0:.0f} mm, which is '
            f'{pressureDrop / self.chamberPressure:.0%} of chamber pressure and comes out of the '
            f'pump discharge.')

        if velocity < 10.0:
            findings.append(
                f'{velocity:.1f} m/s is low. Coolant side heat transfer goes roughly as velocity '
                f'to the 0.8, so a slow channel is a hot wall.')
        elif velocity > 100.0:
            findings.append(
                f'{velocity:.1f} m/s is high and the pressure drop shows it. Velocity buys wall '
                f'temperature and it is paid for in pump work.')

        self.findings = findings

        return {'channelCount':      channelCount,
                'channelWidth':      channelWidth,
                'channelHeight':     channelHeight,
                'flowArea':          flowArea,
                'velocity':          velocity,
                'hydraulicDiameter': hydraulicDiameter,
                'reynolds':          reynolds,
                'pressureDrop':      pressureDrop,
                'circuitLength':     length,
                'findings':          findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full cooling report.
        '''

        heat     = self.calculateHeatLoad()
        capable  = self.checkCoolantCapability()
        wall     = self.calculateWallTemperature()
        channels = self.sizeChannels()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  REGENERATIVE COOLING: {self.combination}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Chamber pressure',  f'{self.chamberPressure / 1.0e6:.2f}',   'MPa'],
             ['Throat diameter',   f'{self.throatDiameter * 1000.0:.1f}',   'mm'],
             ['Peak flux',         f'{heat["peakFlux"] / 1.0e6:.1f}',       'MW/m^2'],
             ['Mean flux',         f'{heat["meanFlux"] / 1.0e6:.2f}',       'MW/m^2'],
             ['Total heat load',   f'{heat["totalLoad"] / 1.0e6:.2f}',      'MW'],
             ['Wetted area',       f'{heat["totalArea"] * 1.0e4:.0f}',      'cm^2']],
            ['Quantity', 'Value', 'Unit'], title = 'Heat load'))

        lines.append('')
        lines.append('  By section:')
        lines.append('')
        lines.append(f'    {"section":12s} {"area [cm2]":>12s} {"mean q [MW/m2]":>16s} '
                     f'{"load [MW]":>11s}')
        for name, entry in heat['sections'].items():
            lines.append(f'    {name:12s} {entry["area"] * 1.0e4:12.1f} '
                         f'{entry["meanFlux"] / 1.0e6:16.2f} {entry["load"] / 1.0e6:11.3f}')

        lines.append('')
        lines.append(formatReportTable(
            [['Coolant',           capable['coolant'],                         ''],
             ['Coolant flow',      f'{self.coolantFlow:.2f}',                  'kg/s'],
             ['Temperature rise',  f'{capable["temperatureRise"]:.0f}',        'K'],
             ['Outlet',            f'{capable["outletTemperature"]:.0f}',      'K'],
             ['Limit',             f'{capable["limit"]:.0f}',                  'K'],
             ['Margin',            f'{capable["margin"]:+.0f}',                'K'],
             ['Closes',            str(capable['feasible']),                   ''],
             ['Load per unit flow', f'{capable["loadPerUnitFlow"] / 1000.0:.0f}', 'kJ/kg']],
            ['Quantity', 'Value', 'Unit'], title = 'Coolant capability'))

        lines.append('')
        lines.append(formatReportTable(
            [['Wall material',     self.wallMaterial,                          ''],
             ['Wall thickness',    f'{self.wallThickness * 1000.0:.2f}',       'mm'],
             ['Wall drop',         f'{wall["wallDrop"]:.0f}',                  'K'],
             ['Gas-side face',     f'{wall["gasSideTemperature"]:.0f}',        'K'],
             ['Coolant-side face', f'{wall["coolantSideTemperature"]:.0f}',    'K'],
             ['Required coolant h', f'{wall["requiredCoefficient"] / 1000.0:.0f}', 'kW/m^2 K'],
             ['Channel velocity',  f'{channels["velocity"]:.1f}',              'm/s'],
             ['Channel drop',      f'{channels["pressureDrop"] / 1.0e6:.2f}',  'MPa']],
            ['Quantity', 'Value', 'Unit'], title = 'Wall and channels'))

        lines.append('')
        for finding in (heat['findings'] + capable['findings']
                        + wall['findings'] + channels['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            path = os.path.join(outputDir,
                                f'cooling_{self.combination.replace("/", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _integrateSection(self, startRatio: float, endRatio: float, length: float,
                          throatRadius: float) -> dict:

        '''
        Integrate the Bartz flux over a conical section, area weighted.
        '''

        totalArea = 0.0
        totalLoad = 0.0

        for index in range(INTEGRATION_STEPS):

            fraction  = (index + 0.5) / INTEGRATION_STEPS
            areaRatio = startRatio + (endRatio - startRatio) * fraction
            areaRatio = max(areaRatio, 1.0)

            radius  = np.sqrt(areaRatio) * throatRadius
            segment = 2.0 * np.pi * radius * length / INTEGRATION_STEPS

            totalArea += segment
            totalLoad += segment * self.calculateHeatFlux(areaRatio)['heatFlux']

        return {'area': totalArea, 'meanFlux': totalLoad / totalArea, 'load': totalLoad}

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('chamber pressure', self.chamberPressure),
                            ('throat diameter', self.throatDiameter),
                            ('coolant flow', self.coolantFlow),
                            ('wall thickness', self.wallThickness),
                            ('wall temperature', self.wallTemperature)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(
                                            component = 'RegenerativeCooling'))

        if self.contractionRatio <= 1.0:
            raise CoolingError(
                f'The contraction ratio must exceed one, got {self.contractionRatio}.',
                context = createErrorContext(component = 'RegenerativeCooling'))

        if self.areaRatio <= 1.0:
            raise CoolingError(f'The area ratio must exceed one, got {self.areaRatio}.',
                               context = createErrorContext(component = 'RegenerativeCooling'))

        if self.wallTemperature >= self.gasPropertiesTemperature():
            raise CoolingError(
                f'The wall temperature {self.wallTemperature:.0f} K is at or above the chamber '
                f'temperature, so there is no driving temperature difference and no heat transfer.',
                context = createErrorContext(component = 'RegenerativeCooling'))

    def gasPropertiesTemperature(self) -> float:

        '''
        Chamber temperature for the combination, read before the gas properties are cached.
        '''

        return combustionGasProperties(self.combination)['chamberTemperature']
