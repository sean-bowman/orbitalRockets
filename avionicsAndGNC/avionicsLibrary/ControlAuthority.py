
# -- ControlAuthority -- #

'''

Whether the thrust vector control can hold the vehicle, and which disturbance decides.

A launch vehicle is aerodynamically unstable. The centre of pressure sits ahead of the centre of
gravity, so any angle of attack produces a moment that increases the angle of attack, and the
control system is the only thing preventing a tumble. **That is a continuous requirement rather
than a peak one**, and it is why a control failure at max dynamic pressure is immediate rather than
gradual.

Three disturbances compete to size the gimbal and the ordering is not the obvious one.

**Thrust misalignment and centre of gravity offset** produce a moment proportional to thrust, so
they are present the whole burn and largest when the thrust is largest.

**Aerodynamic instability** produces a moment proportional to dynamic pressure and angle of attack,
so it peaks at max-Q and vanishes outside the atmosphere.

**Wind** appears as angle of attack, so it acts through the same term as the instability and is
usually how the instability becomes a sizing case rather than a stability one.

The gimbal angle is one half of the answer. **The actuator rate is the other and it is the one that
is usually short**, because a slow actuator is a phase lag and phase lag is what turns a stable loop
unstable.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from avionicsUtils import (TVC_ARRANGEMENTS, GAIN_MARGIN_REQUIREMENT,
                               PHASE_MARGIN_REQUIREMENT,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, ControlAuthorityError)
except ImportError:
    from .avionicsUtils import (TVC_ARRANGEMENTS, GAIN_MARGIN_REQUIREMENT,
                                PHASE_MARGIN_REQUIREMENT,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, ControlAuthorityError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Fraction of the available gimbal angle that may be spent holding steady disturbances, leaving the
# rest for control. A vehicle trimmed at its stop cannot manoeuvre.
#
# A third is a convention rather than a standard.
TRIM_ALLOWANCE = 0.33    # [-]

# Thrust misalignment as an angle, from engine mounting tolerance and thrust vector uncertainty
# within the engine itself. Representative and registered as unvalidated.
THRUST_MISALIGNMENT = 0.25    # [degrees]

# Lateral centre of gravity offset from the thrust axis, as a fraction of vehicle diameter.
CG_OFFSET_FRACTION = 0.005    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- ControlAuthority -- #
# ------------------------------------------------------------------------------------------------ #

class ControlAuthority:

    '''

    Disturbance moments, the gimbal angle they demand, and the actuator rate the loop needs.

    '''

    def __init__(self):

        self.thrust        = np.nan
        self.gimbalArm     = np.nan
        self.arrangement   = ''
        self.dynamicPressure = np.nan
        self.referenceArea = np.nan
        self.staticMargin  = np.nan
        self.vehicleLength = np.nan
        self.vehicleDiameter = np.nan
        self.windAngleOfAttack = np.nan
        self.normalForceSlope  = np.nan
        self.inertia       = np.nan
        self.bendingFrequency = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `gimbalArm` is the distance from the gimbal plane to the centre of gravity, which is the
        moment arm the thrust acts through.

        `staticMargin` is the distance from the centre of gravity to the centre of pressure as a
        fraction of vehicle length, **negative when the vehicle is unstable**, which a launch
        vehicle is.

        '''

        requiredParams = {'thrust':      (int, float),
                          'gimbalArm':   (int, float),
                          'arrangement': str}

        optionalParams = {'dynamicPressure':   (int, float),
                          'referenceArea':     (int, float),
                          'staticMargin':      (int, float),
                          'vehicleLength':     (int, float),
                          'vehicleDiameter':   (int, float),
                          'windAngleOfAttack': (int, float),
                          'normalForceSlope':  (int, float),
                          'inertia':           (int, float),
                          'bendingFrequency':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.normalForceSlope):
            self.normalForceSlope = 2.0

        if not np.isfinite(self.windAngleOfAttack):
            self.windAngleOfAttack = 0.0

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def availableMoment(self, angle: float = None) -> float:

        '''

        Control moment from a gimbal deflection.

            M = F sin(delta) L

        The small angle approximation is not used, because a gimbal at its stop is not a small
        angle and that is exactly the case being checked.

        '''

        if angle is None:
            angle = TVC_ARRANGEMENTS[self.arrangement]['maximumAngle']

        return self.thrust * np.sin(np.radians(angle)) * self.gimbalArm

    # -------------------------------------------------------------------------------------------- #

    def calculateDisturbances(self) -> dict:

        '''

        The three disturbance moments, and which one governs.

        '''

        findings = []

        # thrust misalignment: an angular error in the thrust vector acting through the arm
        misalignment = (self.thrust * np.sin(np.radians(THRUST_MISALIGNMENT)) * self.gimbalArm)

        # centre of gravity offset: thrust along the axis, applied at a lateral offset
        offset = np.nan
        if np.isfinite(self.vehicleDiameter):
            offset = self.thrust * CG_OFFSET_FRACTION * self.vehicleDiameter

        # aerodynamic: unstable vehicle at angle of attack
        aerodynamic = np.nan
        if all(np.isfinite(value) for value in (self.dynamicPressure, self.referenceArea,
                                                self.staticMargin, self.vehicleLength)):

            totalAngle = self.windAngleOfAttack

            normalForce = (self.dynamicPressure * self.referenceArea * self.normalForceSlope
                           * np.radians(totalAngle))

            aerodynamic = abs(normalForce * self.staticMargin * self.vehicleLength)

        terms = {'thrust misalignment': misalignment}

        if np.isfinite(offset):
            terms['centre of gravity offset'] = offset

        if np.isfinite(aerodynamic):
            terms['aerodynamic at angle of attack'] = aerodynamic

        # steady disturbances add rather than combining in quadrature, because they can align
        total = sum(terms.values())

        governing = max(terms, key = terms.get)

        findings.append(
            f'The disturbance moments total {total / 1000.0:.1f} kN m, governed by {governing} at '
            f'{terms[governing] / total:.0%}.')

        if np.isfinite(aerodynamic) and governing != 'aerodynamic at angle of attack':
            findings.append(
                'The aerodynamic term is not the largest, which is the usual case away from max '
                'dynamic pressure and with modest wind. **Thrust misalignment is present the whole '
                'burn and largest when the thrust is largest**, so it sizes the gimbal on most '
                'vehicles even though the aerodynamic case gets the attention.')

        self.findings = findings

        return {'terms':     terms,
                'total':     total,
                'governing': governing,
                'shares':    {name: value / total for name, value in terms.items()},
                'findings':  findings}

    # -------------------------------------------------------------------------------------------- #

    def checkAuthority(self) -> dict:

        '''

        Whether the gimbal can hold the disturbances and still have authority left to manoeuvre.

        The trim allowance is the point. A vehicle that needs its full gimbal range to hold steady
        disturbances is trimmed at its stop and cannot respond to anything, so it is not a marginal
        vehicle, it is an uncontrolled one.

        '''

        findings = []

        arrangement = TVC_ARRANGEMENTS[self.arrangement]

        maximum = arrangement['maximumAngle']

        if maximum <= 0.0:
            raise ControlAuthorityError(
                f"The '{self.arrangement}' arrangement has no gimbal, so its control authority "
                f'comes entirely from reaction control and is not computed here. That is adequate '
                f'in vacuum and nowhere near adequate in atmosphere, which is why it appears on '
                f'upper stages and not on boosters.',
                context = createErrorContext(component = 'ControlAuthority'))

        disturbances = self.calculateDisturbances()

        available = self.availableMoment(maximum)

        # the gimbal angle needed to trim the steady disturbances
        argument = disturbances['total'] / (self.thrust * self.gimbalArm)

        if abs(argument) >= 1.0:
            raise ControlAuthorityError(
                f'The disturbance moment of {disturbances["total"] / 1000.0:.1f} kN m exceeds what '
                f'the thrust can produce at any gimbal angle, {self.thrust * self.gimbalArm / 1000.0:.1f} '
                f'kN m at ninety degrees. **This vehicle cannot be controlled by thrust vectoring '
                f'at all**, and the answer is a longer moment arm, a smaller disturbance or a '
                f'different control effector.',
                context = createErrorContext(component = 'ControlAuthority'))

        trimAngle = float(np.degrees(np.arcsin(argument)))

        allowed = TRIM_ALLOWANCE * maximum

        remaining = maximum - trimAngle

        findings.append(
            f'Trimming the disturbances takes {trimAngle:.2f} degrees of the {maximum:.1f} '
            f'available, leaving {remaining:.2f} for control.')

        if trimAngle > allowed:
            raise ControlAuthorityError(
                f'Trimming the steady disturbances takes {trimAngle:.2f} degrees against a '
                f'{allowed:.2f} degree allowance, which is {TRIM_ALLOWANCE:.0%} of the '
                f'{maximum:.1f} degree range. **A vehicle trimmed near its stop cannot '
                f'manoeuvre**, so this is refused rather than reported as a small margin. The '
                f'governing disturbance is {disturbances["governing"]}.',
                context = createErrorContext(component = 'ControlAuthority'))

        findings.append(
            f'That is inside the {TRIM_ALLOWANCE:.0%} trim allowance, so there is authority left '
            f'to respond with.')

        self.findings = findings

        return {'maximumAngle':     maximum,
                'availableMoment':  available,
                'disturbanceMoment': disturbances['total'],
                'trimAngle':        trimAngle,
                'allowedTrim':      allowed,
                'remainingAngle':   remaining,
                'governing':        disturbances['governing'],
                'authorityRatio':   available / disturbances['total'],
                'adequate':         True,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def requiredActuatorRate(self, controlFrequency: float) -> dict:

        '''

        The gimbal rate the control loop needs, and why it is usually the binding requirement.

        A control loop closing at a given frequency needs the actuator to move at that frequency
        without adding significant phase lag. For a sinusoidal command of amplitude `A` at
        frequency `f`, the peak rate is `2 pi f A`, and an actuator slower than that rate-limits,
        which is a nonlinearity the linear stability margins do not cover.

        **Rate limiting is how a loop with good margins on paper goes unstable in flight.**

        '''

        if controlFrequency <= 0.0:
            raise InvalidInputError(
                f'The control frequency must be positive, got {controlFrequency}.',
                context = createErrorContext(component = 'ControlAuthority'))

        findings = []

        authority = self.checkAuthority()

        amplitude = np.radians(authority['remainingAngle'])

        peakRate = float(np.degrees(2.0 * np.pi * controlFrequency * amplitude))

        findings.append(
            f'Commanding the full remaining {authority["remainingAngle"]:.2f} degrees at '
            f'{controlFrequency:.1f} Hz needs {peakRate:.0f} degrees per second of gimbal rate.')

        findings.append(
            '**An actuator slower than that rate-limits**, which is a nonlinearity the gain and '
            'phase margins do not cover. A loop with good margins on paper goes unstable in flight '
            'through exactly this.')

        if np.isfinite(self.bendingFrequency):

            separation = self.bendingFrequency / controlFrequency

            findings.append(
                f'The first bending mode is at {self.bendingFrequency:.1f} Hz, a separation of '
                f'{separation:.1f} from the control frequency.')

            if separation < 5.0:
                findings.append(
                    'That is close. **Structural flex inside the control bandwidth couples the '
                    'loop to the airframe**, and the fix is a notch filter, which costs phase '
                    'margin at the control frequency, which is the thing the separation was '
                    'protecting. See aerospaceStructures for the mode itself.')

        self.findings = findings

        return {'controlFrequency': controlFrequency,
                'commandAmplitude': authority['remainingAngle'],
                'requiredRate':     peakRate,
                'bendingFrequency': self.bendingFrequency,
                'bendingSeparation': (self.bendingFrequency / controlFrequency
                                      if np.isfinite(self.bendingFrequency) else np.nan),
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def compareArrangements(self) -> dict:

        '''

        The same vehicle on each thrust vector control arrangement.

        '''

        original = self.arrangement

        results = {}

        try:
            for name in TVC_ARRANGEMENTS:

                self.arrangement = name

                try:
                    authority = self.checkAuthority()
                    results[name] = {'maximumAngle': authority['maximumAngle'],
                                     'trimAngle':    authority['trimAngle'],
                                     'remaining':    authority['remainingAngle'],
                                     'adequate':     True}
                except ControlAuthorityError:
                    results[name] = {'maximumAngle': TVC_ARRANGEMENTS[name]['maximumAngle'],
                                     'adequate':     False}

        finally:
            self.arrangement = original

        viable = [name for name, entry in results.items() if entry['adequate']]

        return {'results': results, 'viable': viable}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full control authority report.
        '''

        disturbances = self.calculateDisturbances()
        authority    = self.checkAuthority()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  CONTROL AUTHORITY: {self.arrangement}, {self.thrust / 1000.0:.0f} kN '
                     f'through {self.gimbalArm:.1f} m')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [[name, f'{value / 1000.0:.1f}', f'{disturbances["shares"][name]:.0%}']
             for name, value in sorted(disturbances['terms'].items(), key = lambda item: -item[1])],
            ['Disturbance', 'Moment [kN m]', 'Share'], title = 'Disturbances'))

        lines.append('')
        lines.append(formatReportTable(
            [['Gimbal range',        f'{authority["maximumAngle"]:.1f}',            'deg'],
             ['Trim required',       f'{authority["trimAngle"]:.2f}',               'deg'],
             ['Trim allowance',      f'{authority["allowedTrim"]:.2f}',             'deg'],
             ['Remaining for control', f'{authority["remainingAngle"]:.2f}',        'deg'],
             ['Authority ratio',     f'{authority["authorityRatio"]:.1f}',          ''],
             ['Governing disturbance', f'{authority["governing"]}',                 '']],
            ['Quantity', 'Value', 'Unit'], title = 'Authority'))

        lines.append('')
        for finding in disturbances['findings'] + authority['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'control_authority.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.arrangement not in TVC_ARRANGEMENTS:
            raise InvalidInputError(
                f"Unknown arrangement '{self.arrangement}'. Known arrangements are "
                f'{sorted(TVC_ARRANGEMENTS)}.',
                context = createErrorContext(component = 'ControlAuthority'))

        for name, value in (('thrust', self.thrust), ('gimbal arm', self.gimbalArm)):
            if value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'ControlAuthority'))

        if np.isfinite(self.staticMargin) and self.staticMargin > 0.0:
            raise ControlAuthorityError(
                f'The static margin is {self.staticMargin:+.3f}, which is positive and therefore '
                f'statically stable. A launch vehicle is unstable, with the centre of pressure '
                f'ahead of the centre of gravity, and a positive value here is almost always a '
                f'sign convention error. Supply a negative static margin, or remove it if the '
                f'aerodynamic term is not being computed.',
                context = createErrorContext(component = 'ControlAuthority'))

        for name, value in (('dynamic pressure', self.dynamicPressure),
                            ('reference area',   self.referenceArea),
                            ('vehicle length',   self.vehicleLength),
                            ('vehicle diameter', self.vehicleDiameter),
                            ('inertia',          self.inertia),
                            ('bending frequency', self.bendingFrequency)):
            if np.isfinite(value) and value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'ControlAuthority'))

        if self.windAngleOfAttack < 0.0:
            raise InvalidInputError(
                f'The wind angle of attack is a magnitude, got {self.windAngleOfAttack}.',
                context = createErrorContext(component = 'ControlAuthority'))
