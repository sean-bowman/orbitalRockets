
# -- Turbine -- #

'''

Spouting velocity, blade speed ratio, efficiency and the flow a given power demands.

A rocket turbine is a turbine that does not get to choose its own shaft speed. The pump sets the
speed, and the turbine is bolted to the same shaft and has to make do.

That single fact explains nearly everything that looks wrong about rocket turbines next to
industrial practice. They run at blade speed ratios well below the optimum, their efficiencies are
in the sixties rather than the nineties, and they are almost always partial admission impulse
machines rather than full admission reaction ones.

**None of that is poor design. It is what a turbine looks like when the shaft speed is somebody
else's decision**, and the compromise is usually correct because the pump is the harder machine.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from turbomachineryUtils import (BLADE_SPEED_RATIO_OPTIMUM, TURBINE_INLET_LIMITS,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, TurbineError)
except ImportError:
    from .turbomachineryUtils import (BLADE_SPEED_RATIO_OPTIMUM, TURBINE_INLET_LIMITS,
                                      applyInputs, formatReportTable, createErrorContext,
                                      InvalidInputError, TurbineError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Nozzle angle measured from the plane of rotation. A shallow angle puts more of the gas velocity
# into the direction of blade motion, which is what the blade can extract, so shallow is efficient
# and hard to manufacture.
NOZZLE_ANGLE = 20.0    # [degrees]

# Losses beyond the blade velocity triangle: leakage past the blade tips, disc friction, partial
# admission scavenging, and the exit kinetic energy that leaves with the gas. The velocity triangle
# gives an ideal utilisation and this multiplier turns it into something a real machine reaches.
#
# It is an estimate and it is registered as unvalidated.
MECHANICAL_LOSS_FACTOR = 0.85    # [-]

# Blade tip speed limit, a rotating disc hoop stress problem exactly as on the pump impeller, and
# tighter because the blade is hot.
BLADE_TIP_SPEED_LIMIT = 450.0    # [m/s]

# ------------------------------------------------------------------------------------------------ #
# -- Turbine -- #
# ------------------------------------------------------------------------------------------------ #

class Turbine:

    '''

    Blade speed ratio, efficiency, and the driving gas flow a required shaft power demands.

    '''

    def __init__(self):

        self.requiredPower   = np.nan
        self.inletTemperature = np.nan
        self.pressureRatio   = np.nan
        self.shaftSpeed      = np.nan
        self.meanDiameter    = np.nan
        self.specificHeat    = np.nan
        self.gamma           = np.nan
        self.stageType       = ''
        self.bladeMaterial   = ''

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `pressureRatio` is inlet over exit, so it is greater than one.

        `meanDiameter` is the pitch diameter of the blade row. It is an input rather than an output
        because on a rocket turbopump it is usually constrained by the pump it is bolted to, which
        is the whole point of this class.

        '''

        requiredParams = {'requiredPower':    (int, float),
                          'inletTemperature': (int, float),
                          'pressureRatio':    (int, float),
                          'shaftSpeed':       (int, float),
                          'meanDiameter':     (int, float)}

        optionalParams = {'specificHeat':  (int, float),
                          'gamma':         (int, float),
                          'stageType':     str,
                          'bladeMaterial': str}

        applyInputs(self, inputs, requiredParams, optionalParams)

        # a fuel-rich gas generator exhaust, which is what most rocket turbines run on
        if not np.isfinite(self.specificHeat):
            self.specificHeat = 2500.0
        if not np.isfinite(self.gamma):
            self.gamma = 1.25

        if not self.stageType:
            self.stageType = 'impulse'

        if self.stageType not in BLADE_SPEED_RATIO_OPTIMUM:
            raise TurbineError(
                f'Unknown stage type \'{self.stageType}\'. '
                f'Known: {sorted(BLADE_SPEED_RATIO_OPTIMUM)}.',
                context = createErrorContext(component = 'Turbine'))

        if not self.bladeMaterial:
            self.bladeMaterial = 'uncooled superalloy'

        if self.bladeMaterial not in TURBINE_INLET_LIMITS:
            raise TurbineError(
                f'Unknown blade material \'{self.bladeMaterial}\'. '
                f'Known: {sorted(TURBINE_INLET_LIMITS)}.',
                context = createErrorContext(component = 'Turbine'))

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def bladeSpeed(self) -> float:

        '''
        Mean blade speed, U = omega D / 2.
        '''

        return self.shaftSpeed * 2.0 * np.pi / 60.0 * self.meanDiameter / 2.0

    def calculateSpoutingVelocity(self) -> dict:

        '''

        The isentropic spouting velocity, the speed the gas would reach expanding through the full
        pressure ratio with no work extracted.

            C0 = sqrt( 2 cp T_in (1 - PR^(-(gamma-1)/gamma)) )

        It is the yardstick the blade speed is measured against, and it is set entirely by the gas
        and the pressure ratio rather than by anything mechanical.

        '''

        exponent = (self.gamma - 1.0) / self.gamma

        availableDrop = (self.specificHeat * self.inletTemperature
                         * (1.0 - self.pressureRatio ** (-exponent)))

        velocity = np.sqrt(2.0 * availableDrop)

        return {'spoutingVelocity': velocity,
                'availableWork':    availableDrop,
                'temperatureDrop':  availableDrop / self.specificHeat}

    # -------------------------------------------------------------------------------------------- #

    def calculateEfficiency(self) -> dict:

        '''

        Blade speed ratio and the efficiency it produces.

        For a single stage impulse turbine with equiangular blading, the classical utilisation is

            eta_u = 4 (U/C0) (cos alpha - U/C0)

        which peaks at `U/C0 = cos(alpha)/2` with a value of `cos^2(alpha)`. At a 20 degree nozzle
        angle that is an optimum ratio of 0.470 and a peak utilisation of 0.883.

        **A rocket turbine is normally well below that optimum**, because the shaft speed is the
        pump's decision and the blade diameter is bounded by the machine it fits in. The efficiency
        penalty is the price of a single shaft, and a single shaft is usually worth it.

        '''

        findings = []

        spouting = self.calculateSpoutingVelocity()

        blade = self.bladeSpeed()
        ratio = blade / spouting['spoutingVelocity']

        nozzleAngle = np.radians(NOZZLE_ANGLE)
        cosine      = np.cos(nozzleAngle)

        optimumRatio = cosine / 2.0
        peak         = cosine ** 2

        utilisation = max(4.0 * ratio * (cosine - ratio), 0.0)

        efficiency = utilisation * MECHANICAL_LOSS_FACTOR

        findings.append(
            f'Spouting velocity {spouting["spoutingVelocity"]:.0f} m/s against a blade speed of '
            f'{blade:.0f} m/s, a ratio of {ratio:.3f}.')

        findings.append(
            f'The optimum for a {self.stageType} stage at a {NOZZLE_ANGLE:.0f} degree nozzle angle '
            f'is {optimumRatio:.3f}, where utilisation peaks at {peak:.3f}.')

        if ratio < optimumRatio * 0.8:
            findings.append(
                f'Running at {ratio:.3f} against an optimum of {optimumRatio:.3f} is well below '
                f'the peak, which is the normal rocket condition. The shaft speed belongs to the '
                f'pump and the turbine accepts what it is given.')
        elif ratio > cosine:
            findings.append(
                f'A blade speed ratio above {cosine:.3f} extracts no work at all: the blade is '
                f'moving as fast as the useful component of the gas. This is a geometry error '
                f'rather than an inefficiency.')

        findings.append(
            f'Utilisation {utilisation:.3f} times a {MECHANICAL_LOSS_FACTOR:.2f} mechanical loss '
            f'factor gives {efficiency:.1%}. That factor covers tip leakage, disc friction, partial '
            f'admission scavenging and exit kinetic energy, and it is an estimate registered as '
            f'unvalidated.')

        self.findings = findings

        return {'bladeSpeedRatio': ratio,
                'optimumRatio':    optimumRatio,
                'utilisation':     utilisation,
                'peakUtilisation': peak,
                'efficiency':      efficiency,
                'bladeSpeed':      blade,
                'spoutingVelocity': spouting['spoutingVelocity'],
                'belowOptimum':    bool(ratio < optimumRatio),
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeFlow(self) -> dict:

        '''

        The driving gas flow the required shaft power demands.

            mdot = P / (eta cp T_in (1 - PR^(-(gamma-1)/gamma)))

        On an open cycle this flow is thrown overboard through a low expansion nozzle, so it is a
        direct specific impulse loss to the vehicle. On a closed cycle it goes to the main chamber
        and the loss does not appear.

        **That difference is the whole distinction between a gas generator and a staged combustion
        engine**, and it is why this number matters beyond the turbopump.

        '''

        findings = []

        efficiency = self.calculateEfficiency()
        spouting   = self.calculateSpoutingVelocity()

        specificWork = efficiency['efficiency'] * spouting['availableWork']

        if specificWork <= 0.0:
            raise TurbineError(
                'The turbine extracts no work at this blade speed ratio, so no flow delivers the '
                'required power. The blade speed is at or above the useful gas velocity component.',
                context = createErrorContext(component = 'Turbine'))

        flow = self.requiredPower / specificWork

        findings.append(
            f'{self.requiredPower / 1.0e6:.3f} MW at {efficiency["efficiency"]:.1%} needs '
            f'{flow:.3f} kg/s of driving gas.')

        findings.append(
            f'The gas drops {spouting["temperatureDrop"]:.0f} K across the stage, from '
            f'{self.inletTemperature:.0f} K to {self.inletTemperature - spouting["temperatureDrop"]:.0f} K.')

        findings.append(
            'On an open cycle that flow is dumped overboard at a low expansion ratio and is a '
            'direct impulse loss. On a closed cycle it goes to the main chamber and costs nothing. '
            'That is the difference between a gas generator and a staged combustion engine.')

        self.findings = findings

        return {'drivingFlow':     flow,
                'specificWork':    specificWork,
                'efficiency':      efficiency['efficiency'],
                'temperatureDrop': spouting['temperatureDrop'],
                'exitTemperature': self.inletTemperature - spouting['temperatureDrop'],
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def checkLimits(self) -> dict:

        '''
        Inlet temperature against the blade material, and tip speed against the disc stress limit.
        '''

        findings = []

        material = TURBINE_INLET_LIMITS[self.bladeMaterial]

        temperatureOk = self.inletTemperature <= material['limit']

        blade      = self.bladeSpeed()
        tipSpeedOk = blade <= BLADE_TIP_SPEED_LIMIT

        findings.append(
            f'Inlet {self.inletTemperature:.0f} K against a {material["limit"]:.0f} K limit for '
            f'{self.bladeMaterial}: {material["note"]}.')

        if not temperatureOk:
            findings.append(
                f'The inlet is {self.inletTemperature - material["limit"]:.0f} K over the limit. '
                f'A rocket turbine runs uncooled because the run time is short, so the limit is a '
                f'creep and rupture one over that run time rather than a melting point.')

        findings.append(
            f'Blade speed {blade:.0f} m/s against a {BLADE_TIP_SPEED_LIMIT:.0f} m/s limit. The '
            f'blade is a rotating mass on a hot disc, so this is tighter than the pump impeller '
            f'limit despite the smaller loads.')

        self.findings = findings

        return {'inletTemperature': self.inletTemperature,
                'temperatureLimit': material['limit'],
                'temperatureOk':    bool(temperatureOk),
                'bladeSpeed':       blade,
                'tipSpeedLimit':    BLADE_TIP_SPEED_LIMIT,
                'tipSpeedOk':       bool(tipSpeedOk),
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full turbine report.
        '''

        efficiency = self.calculateEfficiency()
        flow       = self.sizeFlow()
        limits     = self.checkLimits()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  TURBINE: {self.stageType}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Required power',    f'{self.requiredPower / 1.0e6:.3f}',          'MW'],
             ['Inlet temperature', f'{self.inletTemperature:.0f}',               'K'],
             ['Pressure ratio',    f'{self.pressureRatio:.2f}',                  ''],
             ['Shaft speed',       f'{self.shaftSpeed:.0f}',                     'rpm'],
             ['Mean diameter',     f'{self.meanDiameter * 1000.0:.1f}',          'mm'],
             ['Blade speed',       f'{efficiency["bladeSpeed"]:.0f}',            'm/s'],
             ['Spouting velocity', f'{efficiency["spoutingVelocity"]:.0f}',      'm/s'],
             ['Blade speed ratio', f'{efficiency["bladeSpeedRatio"]:.3f}',       ''],
             ['  optimum',         f'{efficiency["optimumRatio"]:.3f}',          ''],
             ['Efficiency',        f'{efficiency["efficiency"]:.1%}',            ''],
             ['Driving flow',      f'{flow["drivingFlow"]:.3f}',                 'kg/s'],
             ['Exit temperature',  f'{flow["exitTemperature"]:.0f}',             'K'],
             ['Temperature ok',    str(limits['temperatureOk']),                 ''],
             ['Tip speed ok',      str(limits['tipSpeedOk']),                    '']],
            ['Quantity', 'Value', 'Unit'], title = 'Turbine'))

        lines.append('')
        for finding in (efficiency['findings'] + flow['findings'] + limits['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, f'turbine_{self.stageType.replace(" ", "_")}.txt'),
                      'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('required power', self.requiredPower),
                            ('inlet temperature', self.inletTemperature),
                            ('shaft speed', self.shaftSpeed),
                            ('mean diameter', self.meanDiameter)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(component = 'Turbine'))

        if self.pressureRatio <= 1.0:
            raise TurbineError(
                f'The pressure ratio must exceed one, got {self.pressureRatio}. It is inlet over '
                f'exit, and a ratio of one is a turbine with no pressure drop to work with.',
                context = createErrorContext(component = 'Turbine'))

        if self.gamma <= 1.0:
            raise TurbineError(
                f'The ratio of specific heats must exceed one, got {self.gamma}.',
                context = createErrorContext(component = 'Turbine'))
