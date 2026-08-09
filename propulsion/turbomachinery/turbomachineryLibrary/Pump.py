
# -- Pump -- #

'''

Head, specific speed, impeller sizing, staging and power.

A rocket pump is an ordinary centrifugal pump asked to do something extreme, and nearly everything
difficult about it follows from one ratio: the head is enormous and the flow is not.

That puts the specific speed far below where pump efficiency peaks, which is why rocket pump
efficiencies look poor next to industrial practice and why they are not going to improve. It also
puts the required tip speed high, which is a materials problem rather than a hydraulic one, and it
is what forces multiple stages on a hydrogen pump.

The class computes specific speed first and reports the geometry it implies, because that decides
what kind of machine is being built before any dimension exists.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from turbomachineryUtils import (HEAD_COEFFICIENT, PUMP_GEOMETRY, BEARING_DN_LIMIT,
                                     GRAVITY, specificSpeed, toUsSpecificSpeed,
                                     headFromPressureRise, tipSpeedFromHead,
                                     geometryForSpecificSpeed,
                                     applyInputs, formatReportTable, createErrorContext,
                                     InvalidInputError, PumpError)
except ImportError:
    from .turbomachineryUtils import (HEAD_COEFFICIENT, PUMP_GEOMETRY, BEARING_DN_LIMIT,
                                      GRAVITY, specificSpeed, toUsSpecificSpeed,
                                      headFromPressureRise, tipSpeedFromHead,
                                      geometryForSpecificSpeed,
                                      applyInputs, formatReportTable, createErrorContext,
                                      InvalidInputError, PumpError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Impeller tip speed limits by material. The impeller is a rotating disc carrying its own centrifugal
# load, so the limit is a hoop stress problem and it scales with the square of tip speed.
#
# This is the ceiling that turns a large head into multiple stages, and it is the reason a hydrogen
# pump is a different machine from a kerosene one rather than a bigger one.
IMPELLER_TIP_SPEED_LIMIT = {
    'aluminium':   {'limit': 350.0, 'note': 'light and cheap, and it runs out of strength early'},
    'titanium':    {'limit': 550.0, 'note': 'the usual choice where LOX compatibility allows it'},
    'Inconel 718': {'limit': 600.0, 'note': 'the high end, and heavy'},
    'Monel K-500': {'limit': 450.0, 'note': 'LOX compatible, which is frequently what decides it'},
}    # [m/s]

# Pump hydraulic efficiency against dimensionless specific speed. Efficiency peaks near 1.0 and
# falls away below it, which is exactly where rocket pumps are forced to operate.
#
# The falloff coefficient is chosen so the model lands in the 60 to 75 per cent band that rocket
# pumps actually achieve at the dimensionless specific speeds they actually run, roughly 0.2 to 0.4.
# At 0.26 it gives 64 per cent, which is the low end of that band.
#
# That is a fit to a known operating range rather than to data, and it is registered as unvalidated.
# A model fitted to the range it will be used in is honest as a ranking tool and is not a prediction.
PEAK_EFFICIENCY = 0.85    # [-]
PEAK_EFFICIENCY_SPECIFIC_SPEED = 1.00    # [-]
EFFICIENCY_FALLOFF = 0.15    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- Pump -- #
# ------------------------------------------------------------------------------------------------ #

class Pump:

    '''

    Head, specific speed, impeller geometry, staging and shaft power for a rocket propellant pump.

    '''

    def __init__(self):

        self.propellant      = ''
        self.density         = np.nan
        self.massFlow        = np.nan
        self.pressureRise    = np.nan
        self.shaftSpeed      = np.nan
        self.headCoefficient = np.nan
        self.impellerMaterial = ''
        self.stages          = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `shaftSpeed` is in rpm, which is how turbomachinery is universally quoted, and is converted
        internally.

        `stages` defaults to whatever the tip speed limit requires rather than to one, because a
        single stage is frequently not available and defaulting to it hides the constraint.

        '''

        requiredParams = {'density':      (int, float),
                          'massFlow':     (int, float),
                          'pressureRise': (int, float),
                          'shaftSpeed':   (int, float)}

        optionalParams = {'propellant':       str,
                          'headCoefficient':  (int, float),
                          'impellerMaterial': str,
                          'stages':           (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.headCoefficient):
            self.headCoefficient = HEAD_COEFFICIENT['typical']

        if not self.impellerMaterial:
            self.impellerMaterial = 'titanium'

        if self.impellerMaterial not in IMPELLER_TIP_SPEED_LIMIT:
            raise PumpError(
                f'Unknown impeller material \'{self.impellerMaterial}\'. '
                f'Known: {sorted(IMPELLER_TIP_SPEED_LIMIT)}.',
                context = createErrorContext(component = 'Pump'))

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def angularSpeed(self) -> float:

        '''
        Shaft speed in rad/s from the rpm input.
        '''

        return self.shaftSpeed * 2.0 * np.pi / 60.0

    def volumetricFlow(self) -> float:

        '''
        Volumetric flow in m^3/s.
        '''

        return self.massFlow / self.density

    def totalHead(self) -> float:

        '''
        Total head the pump has to produce, in metres.
        '''

        return headFromPressureRise(self.pressureRise, self.density)

    # -------------------------------------------------------------------------------------------- #

    def calculateSpecificSpeed(self) -> dict:

        '''

        Dimensionless specific speed, the geometry it implies, and the US customary equivalent.

        This is the first number to compute. It is a shape parameter: two pumps with the same
        specific speed have geometrically similar impellers regardless of size, fluid or speed, so
        it decides what kind of machine is being built before any dimension exists.

        Where the head is large the specific speed can be computed per stage, because staging is
        precisely the lever that moves it back into a sensible range.

        '''

        findings = []

        head  = self.totalHead()
        flow  = self.volumetricFlow()
        speed = self.angularSpeed()

        stages = int(self.stages) if np.isfinite(self.stages) else 1

        perStageHead = head / stages

        overall  = specificSpeed(speed, flow, head)
        perStage = specificSpeed(speed, flow, perStageHead)

        geometry = geometryForSpecificSpeed(perStage)

        findings.append(
            f'Head {head:.0f} m at {flow * 1000.0:.2f} litres per second and '
            f'{self.shaftSpeed:.0f} rpm.')

        findings.append(
            f'Dimensionless specific speed {perStage:.3f} per stage, '
            f'{toUsSpecificSpeed(perStage):.0f} in US customary units, which is a '
            f'{geometry["geometry"]} machine: {geometry["note"]}.')

        if not geometry['inRange']:
            findings.append(
                'Outside the usual range, which on a rocket pump is normal rather than alarming. '
                'The head is large and the flow is not, and that is what a rocket pump is.')

        if stages > 1:
            findings.append(
                f'Over {stages} stages the per-stage specific speed is {perStage:.3f} against '
                f'{overall:.3f} for the whole machine. Staging is the lever that moves specific '
                f'speed, and it is why a hydrogen pump has several stages and a kerosene pump has '
                f'one.')

        self.findings = findings

        return {'specificSpeed':      perStage,
                'overallSpecificSpeed': overall,
                'usSpecificSpeed':    toUsSpecificSpeed(perStage),
                'geometry':           geometry['geometry'],
                'inRange':            geometry['inRange'],
                'head':               head,
                'perStageHead':       perStageHead,
                'stages':             stages,
                'volumetricFlow':     flow,
                'findings':           findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeImpeller(self) -> dict:

        '''

        Tip speed, impeller diameter and the number of stages the material limit requires.

        The chain is short and it ends in a materials constraint:

            U = sqrt(g H / psi)        tip speed from head
            D = 2 U / omega            diameter from tip speed and shaft speed

        The tip speed limit is a hoop stress limit on a rotating disc, so it scales with the square
        of speed and it is not negotiable by hydraulic means. **When the required tip speed exceeds
        it, the answer is more stages**, and that is the calculation this method exists to do.

        '''

        findings = []

        head  = self.totalHead()
        speed = self.angularSpeed()

        material = IMPELLER_TIP_SPEED_LIMIT[self.impellerMaterial]
        limit    = material['limit']

        singleStageTipSpeed = tipSpeedFromHead(head, self.headCoefficient)

        # each stage produces head in proportion to the square of its tip speed, so the stages
        # required scale with the square of the tip speed overrun
        requiredStages = int(np.ceil((singleStageTipSpeed / limit) ** 2)) if \
            singleStageTipSpeed > limit else 1

        stages = int(self.stages) if np.isfinite(self.stages) else requiredStages

        perStageHead = head / stages
        tipSpeed     = tipSpeedFromHead(perStageHead, self.headCoefficient)
        diameter     = 2.0 * tipSpeed / speed

        withinLimit = tipSpeed <= limit

        findings.append(
            f'A single stage would need {singleStageTipSpeed:.0f} m/s tip speed against a '
            f'{limit:.0f} m/s limit for {self.impellerMaterial}.')

        if requiredStages > 1:
            findings.append(
                f'That needs {requiredStages} stages. Head goes as the square of tip speed, so the '
                f'stage count goes as the square of the overrun, and a pump that is fifty per cent '
                f'over needs three stages rather than two.')

        findings.append(
            f'{stages} stage(s) at {perStageHead:.0f} m each gives {tipSpeed:.0f} m/s and a '
            f'{diameter * 1000.0:.1f} mm impeller.')

        if not withinLimit:
            findings.append(
                f'The tip speed of {tipSpeed:.0f} m/s exceeds the {limit:.0f} m/s limit. This is a '
                f'rotating disc carrying its own centrifugal load and the limit is a hoop stress '
                f'one, so no hydraulic change avoids it.')

        # the bearing DN limit bounds shaft speed independently, on bore diameter rather than tip
        bearingBore  = 0.35 * diameter * 1000.0
        dnNumber     = bearingBore * self.shaftSpeed

        findings.append(
            f'A bearing bore of roughly {bearingBore:.0f} mm at {self.shaftSpeed:.0f} rpm is a DN '
            f'of {dnNumber / 1.0e6:.2f} million against a {BEARING_DN_LIMIT / 1.0e6:.1f} million '
            f'limit. DN bounds shaft speed from above independently of cavitation, and on a large '
            f'pump it is frequently the binding one.')

        self.findings = findings

        return {'tipSpeed':            tipSpeed,
                'singleStageTipSpeed': singleStageTipSpeed,
                'diameter':            diameter,
                'stages':              stages,
                'requiredStages':      requiredStages,
                'perStageHead':        perStageHead,
                'tipSpeedLimit':       limit,
                'withinLimit':         bool(withinLimit),
                'bearingBore':         bearingBore,
                'dnNumber':            dnNumber,
                'dnWithinLimit':       bool(dnNumber <= BEARING_DN_LIMIT),
                'findings':            findings}

    # -------------------------------------------------------------------------------------------- #

    def calculatePower(self) -> dict:

        '''

        Hydraulic power, efficiency and the shaft power the turbine has to supply.

            P_hydraulic = rho g Q H
            P_shaft     = P_hydraulic / eta

        The efficiency model is a fall-off from a peak near a specific speed of one, which is a
        curve fit to the general shape of published pump charts. **It is a ranking tool rather than
        a prediction and it is registered as unvalidated.** What it captures correctly is the
        direction: a rocket pump operates well below the specific speed where efficiency peaks, and
        it pays for that.

        '''

        findings = []

        similarity = self.calculateSpecificSpeed()

        head = similarity['head']
        flow = similarity['volumetricFlow']

        hydraulic = self.density * GRAVITY * flow * head

        ratio      = similarity['specificSpeed'] / PEAK_EFFICIENCY_SPECIFIC_SPEED
        efficiency = PEAK_EFFICIENCY * np.exp(-EFFICIENCY_FALLOFF * np.log(ratio) ** 2)

        shaft = hydraulic / efficiency

        findings.append(
            f'Hydraulic power {hydraulic / 1.0e6:.3f} MW at {efficiency:.1%} efficiency needs '
            f'{shaft / 1.0e6:.3f} MW at the shaft.')

        findings.append(
            f'The efficiency model peaks at {PEAK_EFFICIENCY:.0%} near a specific speed of '
            f'{PEAK_EFFICIENCY_SPECIFIC_SPEED:.1f}, and this pump runs at '
            f'{similarity["specificSpeed"]:.3f}. That is the penalty for high head and low flow, '
            f'and it is structural rather than a sign of a poor design.')

        findings.append(
            'The efficiency correlation is a curve fit to the shape of published pump charts and '
            'is registered as unvalidated. It ranks; it does not predict.')

        self.findings = findings

        return {'hydraulicPower': hydraulic,
                'shaftPower':     shaft,
                'efficiency':     efficiency,
                'head':           head,
                'volumetricFlow': flow,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full pump report.
        '''

        similarity = self.calculateSpecificSpeed()
        impeller   = self.sizeImpeller()
        power      = self.calculatePower()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  PUMP: {self.propellant if self.propellant else "propellant"}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Mass flow',        f'{self.massFlow:.2f}',                      'kg/s'],
             ['Density',          f'{self.density:.1f}',                       'kg/m^3'],
             ['Pressure rise',    f'{self.pressureRise / 1.0e6:.2f}',          'MPa'],
             ['Head',             f'{similarity["head"]:.0f}',                 'm'],
             ['Shaft speed',      f'{self.shaftSpeed:.0f}',                    'rpm'],
             ['Specific speed',   f'{similarity["specificSpeed"]:.3f}',        ''],
             ['  US customary',   f'{similarity["usSpecificSpeed"]:.0f}',      ''],
             ['Geometry',         similarity['geometry'],                      ''],
             ['Stages',           f'{impeller["stages"]}',                     ''],
             ['Tip speed',        f'{impeller["tipSpeed"]:.0f}',               'm/s'],
             ['Impeller diameter', f'{impeller["diameter"] * 1000.0:.1f}',     'mm'],
             ['Efficiency',       f'{power["efficiency"]:.1%}',                ''],
             ['Shaft power',      f'{power["shaftPower"] / 1.0e6:.3f}',        'MW'],
             ['Bearing DN',       f'{impeller["dnNumber"] / 1.0e6:.2f}',       'million']],
            ['Quantity', 'Value', 'Unit'], title = 'Pump'))

        lines.append('')
        for finding in (similarity['findings'] + impeller['findings'] + power['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            label = (self.propellant if self.propellant else 'pump').replace('/', '_')
            with open(os.path.join(outputDir, f'pump_{label}.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('density', self.density), ('mass flow', self.massFlow),
                            ('pressure rise', self.pressureRise),
                            ('shaft speed', self.shaftSpeed)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(component = 'Pump'))

        if not 0.0 < self.headCoefficient <= 1.0:
            raise PumpError(
                f'The head coefficient must lie in (0, 1], got {self.headCoefficient}. It is '
                f'g H over the square of tip speed, and a value above one is an impeller '
                f'producing more head than its tip speed contains.',
                context = createErrorContext(component = 'Pump'))

        if np.isfinite(self.stages) and self.stages < 1:
            raise PumpError(f'The stage count must be at least one, got {self.stages}.',
                            context = createErrorContext(component = 'Pump'))
