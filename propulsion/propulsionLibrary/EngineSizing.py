
# -- EngineSizing -- #

'''

From a thrust requirement to a throat, a chamber and a mass estimate.

The chain is short and each link is forced by the one before it:

    mdot = F / (Isp g0)             the propellant the thrust requires
    At   = mdot c* / Pc             the throat that chokes that flow at that pressure
    Ae   = eps At                   the exit the expansion requires
    Vc   = L* At                    the chamber volume the combustion requires
    Ac   = contraction ratio x At   the chamber cross-section

The interesting part is the last two, because a chamber volume is not a chamber.

Characteristic length sets a volume from the residence time combustion needs, and says nothing
about the shape of it. The wall has to carry the heat flux as well, and wall area is a different
function of the geometry than volume is, so the two requirements have to be checked separately.
`sizeChamber` computes both and reports the margin between them.

The cross-check counts the whole gas-side wall rather than the barrel alone, which matters more
than it sounds. On the reference case here the divergent section is 60 per cent of the wetted area,
and a cooling check run on the barrel by itself concludes the chamber is short by a factor of two
when the real margin is 1.37. Cooling does govern chamber length on plenty of real engines,
particularly small ones and high chamber pressure ones, but it has to be demonstrated rather than
assumed, and the demonstration has to include the nozzle.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from propulsionUtils import (PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH, GRAVITY,
                                 R_UNIVERSAL,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, SizingError, PropellantError)
    from EnginePerformance import EnginePerformance
except ImportError:
    from .propulsionUtils import (PROPELLANT_COMBINATIONS, CHARACTERISTIC_LENGTH, GRAVITY,
                                  R_UNIVERSAL,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, SizingError, PropellantError)
    from .EnginePerformance import EnginePerformance

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Chamber cross-section over throat area. Below about 2 the chamber is fast enough that the pressure
# drop from the injector face to the throat becomes a real performance loss; above about 5 the
# chamber is mass that is not doing anything. Large engines sit at the low end because the throat is
# already big, small engines at the high end.
DEFAULT_CONTRACTION_RATIO = 2.5    # [-]

# The convergent half angle from the chamber barrel down to the throat. The flow is subsonic and
# accelerating here, so it tolerates a steep angle without separating, and steep is short and light.
CONVERGENT_HALF_ANGLE = 30.0    # [degrees]

# Conical nozzle divergence half angle. Fifteen degrees is the classical choice and the divergence
# loss it carries is the reason bell nozzles exist.
CONICAL_HALF_ANGLE = 15.0    # [degrees]

# Bell nozzles are quoted as a percentage of the length of a 15 degree cone of the same area ratio.
# Eighty per cent is the common design point: it recovers most of the divergence loss of the cone
# for four fifths of the length, and the remaining twenty per cent buys very little.
BELL_LENGTH_FRACTION = 0.80    # [-]

# Chamber wall heat flux, used to convert a cooling load into the wall area a chamber needs. This is
# a representative peak-throat value for a regeneratively cooled hydrocarbon engine. It is a
# stand-in for a cooling analysis rather than a substitute for one, and it exists to demonstrate
# that the cooling requirement and the L* requirement are different numbers.
REFERENCE_THROAT_HEAT_FLUX = 3.0e7    # [W/m^2]

# The fraction of the propellant chemical power that reaches the chamber and nozzle walls. A few per
# cent sounds small and is an enormous absolute number: the walls of a megawatt-class chamber are
# rejecting more power than most industrial heat exchangers.
WALL_HEAT_LOAD_FRACTION = 0.02    # [-]

# The throat carries the peak flux and nowhere else comes close, so an area-averaged flux over the
# whole gas-side wall is a fraction of it. A quarter is the usual first approximation.
CHAMBER_AVERAGE_FLUX_FRACTION = 0.25    # [-]

# Thrust-to-weight for a complete liquid rocket engine, used for the mass estimate. Real engines
# span roughly 60 for a small pressure-fed thruster to over 150 for a large staged combustion
# engine. This is a scaling estimate and not a mass properties calculation.
ENGINE_THRUST_TO_WEIGHT = 100.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- EngineSizing -- #
# ------------------------------------------------------------------------------------------------ #

class EngineSizing:

    '''

    Throat, chamber and nozzle geometry from a thrust requirement, plus a mass estimate.

    '''

    def __init__(self):

        self.combination      = ''
        self.thrust           = np.nan
        self.chamberPressure  = np.nan
        self.areaRatio        = np.nan
        self.ambientPressure  = np.nan
        self.contractionRatio = np.nan
        self.characteristicLength = np.nan

        self.properties  = {}
        self.performance = None
        self.findings    = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `thrust` is in newtons at `ambientPressure`, which defaults to sea level.

        Stating the ambient the thrust is quoted at is not a formality. A 100 kN sea level engine
        and a 100 kN vacuum engine are different engines, and the difference is roughly ten per cent
        of the throat area.

        '''

        requiredParams = {'combination':     str,
                          'thrust':          (int, float),
                          'chamberPressure': (int, float),
                          'areaRatio':       (int, float)}

        optionalParams = {'ambientPressure':      (int, float),
                          'contractionRatio':     (int, float),
                          'characteristicLength': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combination not in PROPELLANT_COMBINATIONS:
            raise PropellantError(
                f'Unknown propellant combination \'{self.combination}\'. '
                f'Known: {sorted(PROPELLANT_COMBINATIONS)}.',
                context = createErrorContext(component = 'EngineSizing'))

        self.properties = dict(PROPELLANT_COMBINATIONS[self.combination])

        if not np.isfinite(self.ambientPressure):
            self.ambientPressure = 101325.0

        if not np.isfinite(self.contractionRatio):
            self.contractionRatio = DEFAULT_CONTRACTION_RATIO

        if not np.isfinite(self.characteristicLength):
            self.characteristicLength = CHARACTERISTIC_LENGTH[self.combination]['value']

        self._validateInputs()

        self.performance = EnginePerformance()
        self.performance.setInputs({'combination':     self.combination,
                                    'chamberPressure': self.chamberPressure,
                                    'areaRatio':       self.areaRatio,
                                    'ambientPressure': self.ambientPressure})

    # -------------------------------------------------------------------------------------------- #

    def sizeThroat(self) -> dict:

        '''

        Mass flow, throat area and exit area from the thrust requirement.

        The throat is where the engine is defined. Everything else in the geometry is a ratio to it.

        '''

        findings = []

        impulse = self.performance.calculateSpecificImpulse()
        cstar   = impulse['characteristicVelocity']['delivered']

        massFlow = self.thrust / (impulse['delivered'] * GRAVITY)

        throatArea = massFlow * cstar / self.chamberPressure
        exitArea   = throatArea * self.areaRatio

        throatDiameter = 2.0 * np.sqrt(throatArea / np.pi)
        exitDiameter   = 2.0 * np.sqrt(exitArea / np.pi)

        oxidiserFlow = massFlow * self.properties['mixtureRatio'] / (1.0 + self.properties['mixtureRatio'])
        fuelFlow     = massFlow / (1.0 + self.properties['mixtureRatio'])

        findings.append(
            f'{self.thrust / 1000.0:.1f} kN at {impulse["delivered"]:.1f} s needs '
            f'{massFlow:.2f} kg/s, split {oxidiserFlow:.2f} oxidiser and {fuelFlow:.2f} fuel at a '
            f'mixture ratio of {self.properties["mixtureRatio"]:.2f}.')

        findings.append(
            f'Throat diameter {throatDiameter * 1000.0:.1f} mm, exit diameter '
            f'{exitDiameter * 1000.0:.1f} mm at an area ratio of {self.areaRatio:.0f}.')

        self.findings = findings

        return {'massFlow':       massFlow,
                'oxidiserFlow':   oxidiserFlow,
                'fuelFlow':       fuelFlow,
                'throatArea':     throatArea,
                'exitArea':       exitArea,
                'throatDiameter': throatDiameter,
                'exitDiameter':   exitDiameter,
                'specificImpulse': impulse['delivered'],
                'characteristicVelocity': cstar,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeChamber(self) -> dict:

        '''

        Chamber geometry from characteristic length, cross-checked against the wall area the
        cooling load needs.

        The cross-check counts the whole gas-side wall, barrel plus convergent plus nozzle, and not
        the barrel alone. Counting only the barrel is the easy mistake and it overstates the cooling
        requirement badly: on a moderately expanded engine the divergent section is the majority of
        the wetted area, and it is regeneratively cooled on most engines that have a regenerative
        circuit at all.

        Both requirements are reported. L* gives a volume and cooling gives an area, so neither
        governs the other directly, and the honest output is the margin between what the geometry
        provides and what the heat load needs.

        '''

        findings = []

        throat = self.sizeThroat()
        nozzle = self.sizeNozzle()

        throatArea  = throat['throatArea']
        chamberArea = throatArea * self.contractionRatio

        chamberDiameter = 2.0 * np.sqrt(chamberArea / np.pi)
        throatDiameter  = throat['throatDiameter']

        chamberVolume = self.characteristicLength * throatArea

        # the convergent section is a frustum from the chamber diameter down to the throat
        convergentLength = ((chamberDiameter - throatDiameter) / 2.0
                            / np.tan(np.radians(CONVERGENT_HALF_ANGLE)))

        chamberRadius = chamberDiameter / 2.0
        throatRadius  = throatDiameter / 2.0

        convergentVolume = (np.pi * convergentLength / 3.0
                            * (chamberRadius ** 2 + throatRadius ** 2
                               + chamberRadius * throatRadius))

        barrelVolume = chamberVolume - convergentVolume

        if barrelVolume <= 0.0:
            raise SizingError(
                f'The convergent section alone is {convergentVolume * 1.0e6:.1f} cm^3, which '
                f'exceeds the {chamberVolume * 1.0e6:.1f} cm^3 the characteristic length allows. '
                f'A contraction ratio of {self.contractionRatio:.1f} is too large for an L* of '
                f'{self.characteristicLength:.2f} m, and there is no barrel left to put an '
                f'injector on.',
                context = createErrorContext(component = 'EngineSizing'))

        barrelLength = barrelVolume / chamberArea

        # residence time: the chamber volume divided by the volumetric flow through it, which needs
        # the chamber gas density rather than either propellant density
        specificGasConstant = R_UNIVERSAL * 1000.0 / self.properties['molarMass']
        chamberDensity      = self.chamberPressure / (specificGasConstant
                                                      * self.properties['chamberTemperature'])
        residenceTime       = chamberVolume * chamberDensity / throat['massFlow']

        # the cooling cross-check, over the whole gas-side wall
        jetPower     = self.thrust ** 2 / (2.0 * throat['massFlow'])
        wallHeatLoad = WALL_HEAT_LOAD_FRACTION * jetPower

        averageFlux      = REFERENCE_THROAT_HEAT_FLUX * CHAMBER_AVERAGE_FLUX_FRACTION
        requiredWallArea = wallHeatLoad / averageFlux

        barrelWallArea     = np.pi * chamberDiameter * barrelLength
        convergentWallArea = (np.pi * (chamberRadius + throatRadius)
                              * np.sqrt(convergentLength ** 2
                                        + (chamberRadius - throatRadius) ** 2))
        nozzleWallArea     = (np.pi * (throatRadius + nozzle['exitRadius'])
                              * np.sqrt(nozzle['bellLength'] ** 2
                                        + (nozzle['exitRadius'] - throatRadius) ** 2))

        availableWallArea = barrelWallArea + convergentWallArea + nozzleWallArea

        coolingMargin = availableWallArea / requiredWallArea
        governing     = 'characteristic length' if coolingMargin >= 1.0 else 'cooling'

        findings.append(
            f'Chamber diameter {chamberDiameter * 1000.0:.1f} mm at a contraction ratio of '
            f'{self.contractionRatio:.1f}, with a {barrelLength * 1000.0:.1f} mm barrel and a '
            f'{convergentLength * 1000.0:.1f} mm convergent section.')

        findings.append(
            f'An L* of {self.characteristicLength:.2f} m gives {chamberVolume * 1.0e6:.0f} cm^3 '
            f'and a residence time of {residenceTime * 1000.0:.2f} ms, against the one to five '
            f'milliseconds a liquid engine typically allows.')

        findings.append(
            f'The walls are rejecting {wallHeatLoad / 1.0e6:.2f} MW, which is '
            f'{WALL_HEAT_LOAD_FRACTION:.0%} of the {jetPower / 1.0e6:.1f} MW of jet power. That is '
            f'the load the regenerative circuit carries, and it is why the fuel side of the feed '
            f'system is sized the way it is.')

        findings.append(
            f'That load needs {requiredWallArea * 1.0e4:.0f} cm^2 of wall against the '
            f'{availableWallArea * 1.0e4:.0f} cm^2 the geometry provides, a margin of '
            f'{coolingMargin:.2f}. The nozzle is {nozzleWallArea / availableWallArea:.0%} of that '
            f'area, so a cooling check run on the barrel alone would reach a different conclusion.')

        if governing == 'cooling':
            findings.append(
                'There is not enough wall to reject the heat load at the assumed flux, so the '
                'chamber has to lengthen, run a higher flux, or use film cooling. L* is a floor '
                'here rather than the driver.')
        else:
            findings.append(
                'The geometry has enough wall area at the assumed flux, so characteristic length '
                'governs the chamber. The flux assumed here is representative rather than '
                'computed, and a real cooling analysis is what settles it.')

        self.findings = findings

        return {'chamberArea':        chamberArea,
                'chamberDiameter':    chamberDiameter,
                'chamberVolume':      chamberVolume,
                'barrelLength':       barrelLength,
                'convergentLength':   convergentLength,
                'barrelWallArea':     barrelWallArea,
                'convergentWallArea': convergentWallArea,
                'nozzleWallArea':     nozzleWallArea,
                'availableWallArea':  availableWallArea,
                'requiredWallArea':   requiredWallArea,
                'coolingMargin':      coolingMargin,
                'wallHeatLoad':       wallHeatLoad,
                'jetPower':           jetPower,
                'chamberDensity':     chamberDensity,
                'residenceTime':      residenceTime,
                'governing':          governing,
                'findings':           findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeNozzle(self) -> dict:

        '''

        Nozzle length for a conical and an eighty per cent bell, and the divergence loss of the cone.

        The bell exists because of the divergence loss. A 15 degree cone throws away the transverse
        component of its exit momentum, which is a loss of `(1 + cos alpha) / 2`, or 1.7 per cent.
        Recovering most of that for four fifths of the length is a good trade, and it is why almost
        nothing flies a cone.

        The contour itself is a method of characteristics problem and belongs in the NOVA suite.
        This is the length and the loss, which is what a sizing pass needs.

        '''

        findings = []

        throat = self.sizeThroat()

        throatRadius = throat['throatDiameter'] / 2.0
        exitRadius   = throat['exitDiameter'] / 2.0

        conicalLength = (exitRadius - throatRadius) / np.tan(np.radians(CONICAL_HALF_ANGLE))
        bellLength    = BELL_LENGTH_FRACTION * conicalLength

        divergenceEfficiency = (1.0 + np.cos(np.radians(CONICAL_HALF_ANGLE))) / 2.0

        findings.append(
            f'A {CONICAL_HALF_ANGLE:.0f} degree cone is {conicalLength * 1000.0:.0f} mm long and '
            f'an {BELL_LENGTH_FRACTION:.0%} bell is {bellLength * 1000.0:.0f} mm.')

        findings.append(
            f'The cone carries a divergence efficiency of {divergenceEfficiency:.4f}, a '
            f'{(1.0 - divergenceEfficiency) * 100.0:.1f} per cent loss, from the transverse '
            f'component of the exit momentum. The bell recovers most of it in less length, which '
            f'is the whole argument.')

        findings.append(
            'The contour that achieves it is a method of characteristics problem and is generated '
            'in the NOVA suite. This is the envelope and the loss, which is what sizing needs.')

        self.findings = findings

        return {'conicalLength':        conicalLength,
                'bellLength':           bellLength,
                'divergenceEfficiency': divergenceEfficiency,
                'exitRadius':           exitRadius,
                'throatRadius':         throatRadius,
                'findings':             findings}

    # -------------------------------------------------------------------------------------------- #

    def estimateMass(self) -> dict:

        '''

        Engine mass from a thrust-to-weight scaling, with the propellant flow rates it implies.

        A scaling estimate, and labelled as one. Engine mass is set by the cycle, the chamber
        pressure and the materials, none of which a single ratio captures. It is here because a
        vehicle sizing loop needs a number before any of those exist, and a number with its basis
        stated is better than a number without one.

        '''

        findings = []

        throat = self.sizeThroat()

        mass = self.thrust / (ENGINE_THRUST_TO_WEIGHT * GRAVITY)

        findings.append(
            f'Engine mass {mass:.1f} kg at a thrust-to-weight of {ENGINE_THRUST_TO_WEIGHT:.0f}. '
            f'That is a scaling estimate: real engines span roughly 60 for a small pressure-fed '
            f'thruster to over 150 for a large staged combustion engine, and the cycle decides '
            f'which end.')

        findings.append(
            f'At {throat["massFlow"]:.2f} kg/s the engine consumes its own mass in propellant '
            f'every {mass / throat["massFlow"]:.1f} seconds, which is the reason engine mass '
            f'matters far less than propellant mass on anything but an upper stage.')

        self.findings = findings

        return {'mass':            mass,
                'thrustToWeight':  ENGINE_THRUST_TO_WEIGHT,
                'massFlow':        throat['massFlow'],
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full sizing report.
        '''

        throat  = self.sizeThroat()
        chamber = self.sizeChamber()
        nozzle  = self.sizeNozzle()
        mass    = self.estimateMass()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ENGINE SIZING: {self.combination}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Thrust',            f'{self.thrust / 1000.0:.1f}',             'kN'],
             ['Chamber pressure',  f'{self.chamberPressure / 1.0e6:.2f}',     'MPa'],
             ['Area ratio',        f'{self.areaRatio:.1f}',                   ''],
             ['Specific impulse',  f'{throat["specificImpulse"]:.1f}',        's'],
             ['Mass flow',         f'{throat["massFlow"]:.2f}',               'kg/s'],
             ['  oxidiser',        f'{throat["oxidiserFlow"]:.2f}',           'kg/s'],
             ['  fuel',            f'{throat["fuelFlow"]:.2f}',               'kg/s']],
            ['Quantity', 'Value', 'Unit'], title = 'Requirement'))

        lines.append('')
        lines.append(formatReportTable(
            [['Throat diameter',    f'{throat["throatDiameter"] * 1000.0:.1f}',    'mm'],
             ['Exit diameter',      f'{throat["exitDiameter"] * 1000.0:.1f}',      'mm'],
             ['Chamber diameter',   f'{chamber["chamberDiameter"] * 1000.0:.1f}',  'mm'],
             ['Barrel length',      f'{chamber["barrelLength"] * 1000.0:.1f}',     'mm'],
             ['Convergent length',  f'{chamber["convergentLength"] * 1000.0:.1f}', 'mm'],
             ['Bell length',        f'{nozzle["bellLength"] * 1000.0:.0f}',        'mm'],
             ['Chamber volume',     f'{chamber["chamberVolume"] * 1.0e6:.0f}',     'cm^3'],
             ['Residence time',     f'{chamber["residenceTime"] * 1000.0:.2f}',    'ms'],
             ['Governed by',        chamber['governing'],                          ''],
             ['Cooling margin',     f'{chamber["coolingMargin"]:.2f}',             ''],
             ['Wall heat load',     f'{chamber["wallHeatLoad"] / 1.0e6:.2f}',      'MW'],
             ['Engine mass',        f'{mass["mass"]:.1f}',                         'kg']],
            ['Quantity', 'Value', 'Unit'], title = 'Geometry'))

        lines.append('')
        for finding in (throat['findings'] + chamber['findings']
                        + nozzle['findings'] + mass['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            path = os.path.join(outputDir, f'sizing_{self.combination.replace("/", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('thrust', self.thrust),
                            ('chamber pressure', self.chamberPressure),
                            ('characteristic length', self.characteristicLength)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'EngineSizing'))

        if self.areaRatio <= 1.0:
            raise InvalidInputError(
                f'The area ratio must exceed one, got {self.areaRatio}.',
                context = createErrorContext(component = 'EngineSizing'))

        if self.contractionRatio <= 1.0:
            raise SizingError(
                f'The contraction ratio must exceed one, got {self.contractionRatio}. A chamber '
                f'no larger than its own throat has no subsonic section to burn in.',
                context = createErrorContext(component = 'EngineSizing'))
