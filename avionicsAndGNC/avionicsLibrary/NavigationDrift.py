
# -- NavigationDrift -- #

'''

How fast an inertial navigation solution goes wrong, and which error term actually does it.

Four error sources feed the position solution and they grow at different rates, which means the one
that dominates changes with flight duration. That is the whole content of this class.

    accelerometer random walk    position grows as t^1.5
    accelerometer bias           position grows as t^2
    gyro random walk             position grows as t^2.5
    gyro bias, through tilt      position grows as t^3

**The gyro bias term is the one that dominates and it is not the one people budget.** An attitude
error tilts the accelerometer triad, so a component of gravity appears as horizontal acceleration.
That error is proportional to the attitude error, the attitude error grows linearly with gyro bias,
and integrating twice gives a cube.

On a tactical grade unit over a nine minute ascent the accelerometer bias contributes 429 m and the
gyro bias through tilt contributes 3743 m. At sixty seconds they are within a few per cent of each
other, which is why a short-flight intuition transfers badly.

**An aiding source does not reduce these errors. It stops them growing**, which is a different and
more useful thing, and it is why the aiding availability matters more than its accuracy.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from avionicsUtils import (IMU_GRADES, AIDING_SOURCES, MICRO_G, STANDARD_GRAVITY,
                               attitudeErrorFromGyroBias, attitudeErrorFromRandomWalk,
                               positionErrorFromAccelBias, positionErrorFromTilt,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, NavigationError)
except ImportError:
    from .avionicsUtils import (IMU_GRADES, AIDING_SOURCES, MICRO_G, STANDARD_GRAVITY,
                                attitudeErrorFromGyroBias, attitudeErrorFromRandomWalk,
                                positionErrorFromAccelBias, positionErrorFromTilt,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, NavigationError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Share of the combined position error at which one term is called dominant.
DOMINANCE_THRESHOLD = 0.5    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- NavigationDrift -- #
# ------------------------------------------------------------------------------------------------ #

class NavigationDrift:

    '''

    Inertial error growth by term, the dominant contributor, and what aiding bounds it to.

    '''

    def __init__(self):

        self.grade         = ''
        self.flightTime    = np.nan
        self.aiding        = ''
        self.positionRequirement = np.nan
        self.gyroBias      = np.nan
        self.accelBias     = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `grade` selects a representative IMU class. `gyroBias` and `accelBias` override the grade's
        values for a specific unit, in degrees per hour and micro g.

        `positionRequirement` is the position accuracy the mission needs at the end of the flight,
        which is what turns a drift calculation into a verdict.

        '''

        requiredParams = {'grade':      str,
                          'flightTime': (int, float)}

        optionalParams = {'aiding':              str,
                          'positionRequirement': (int, float),
                          'gyroBias':            (int, float),
                          'accelBias':           (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.aiding:
            self.aiding = 'none'

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def sensorData(self) -> dict:

        '''
        The IMU error terms, with any explicit overrides applied.
        '''

        entry = dict(IMU_GRADES[self.grade])

        if np.isfinite(self.gyroBias):
            entry['gyroBias'] = self.gyroBias

        if np.isfinite(self.accelBias):
            entry['accelBias'] = self.accelBias

        return entry

    # -------------------------------------------------------------------------------------------- #

    def calculateDrift(self, time: float = None) -> dict:

        '''

        The four position error contributions and the attitude error behind two of them.

        Terms are combined by root sum of squares, which assumes they are independent. Bias and
        random walk are; two bias terms on the same unit may not be, and that is a limitation of
        this model rather than of the physics.

        '''

        if time is None:
            time = self.flightTime

        sensor = self.sensorData()

        # attitude, which feeds the tilt term
        attitudeBias = attitudeErrorFromGyroBias(sensor['gyroBias'], time)
        attitudeWalk = attitudeErrorFromRandomWalk(sensor['gyroRandomWalk'], time)

        attitude = float(np.sqrt(attitudeBias ** 2 + attitudeWalk ** 2))

        # position, term by term
        fromAccelBias = positionErrorFromAccelBias(sensor['accelBias'], time)

        # velocity random walk integrates to a position error growing as t^1.5
        fromAccelWalk = (sensor['accelRandomWalk'] / np.sqrt(3600.0)
                         * (2.0 / 3.0) * time ** 1.5)

        fromGyroBias = positionErrorFromTilt(attitudeBias, time)

        # the walk term in attitude feeds tilt as well, growing as t^2.5
        fromGyroWalk = (0.5 * STANDARD_GRAVITY * np.radians(sensor['gyroRandomWalk'])
                        / np.sqrt(3600.0) * (4.0 / 15.0) * time ** 2.5)

        terms = {'accelerometer bias':        fromAccelBias,
                 'accelerometer random walk': fromAccelWalk,
                 'gyro bias through tilt':    fromGyroBias,
                 'gyro random walk':          fromGyroWalk}

        total = float(np.sqrt(sum(value ** 2 for value in terms.values())))

        dominant = max(terms, key = terms.get)

        return {'time':            time,
                'attitudeError':   attitude,
                'attitudeDegrees': float(np.degrees(attitude)),
                'terms':           terms,
                'shares':          {name: (value / total) ** 2
                                    for name, value in terms.items()},
                'totalPosition':   total,
                'dominant':        dominant,
                'dominantShare':   (terms[dominant] / total) ** 2}

    # -------------------------------------------------------------------------------------------- #

    def identifyCrossover(self, upper: float = None, points: int = 400) -> dict:

        '''

        Where the gyro bias term overtakes the accelerometer bias term.

        This is the useful output. Below the crossover an accelerometer specification is the thing
        to buy; above it a gyro specification is, and **the crossover is early enough that most
        launch vehicle flights are on the gyro side of it.**

        '''

        if upper is None:
            upper = max(self.flightTime, 60.0)

        findings = []

        times = np.linspace(1.0, upper, points)

        accel = np.array([positionErrorFromAccelBias(self.sensorData()['accelBias'], value)
                          for value in times])

        gyro = np.array([positionErrorFromTilt(
            attitudeErrorFromGyroBias(self.sensorData()['gyroBias'], value), value)
            for value in times])

        crossed = np.where(gyro >= accel)[0]

        crossover = float(times[crossed[0]]) if crossed.size else None

        if crossover is None:
            findings.append(
                f'The accelerometer bias term still dominates at {upper:.0f} s. This is a short '
                f'enough flight that the accelerometer specification is what to buy.')
        else:
            findings.append(
                f'The gyro bias term overtakes the accelerometer bias term at {crossover:.0f} s.')

            findings.append(
                'Below that an accelerometer specification is what to buy and above it a gyro '
                'specification is. **Most launch vehicle flights are on the gyro side of it**, and '
                'a budget written from a short-flight intuition buys the wrong sensor.')

        self.findings = findings

        return {'times':     times,
                'accelTerm': accel,
                'gyroTerm':  gyro,
                'crossover': crossover,
                'gyroDominatesAtFlightTime': bool(crossover is not None
                                                  and crossover < self.flightTime),
                'findings':  findings}

    # -------------------------------------------------------------------------------------------- #

    def checkRequirement(self) -> dict:

        '''

        Whether the solution meets its accuracy requirement at the end of the flight.

        With no aiding this is a straight comparison. With aiding the error is bounded rather than
        reduced, so the comparison is against the bound, and the availability decides whether the
        bound can be relied on.

        '''

        if not np.isfinite(self.positionRequirement):
            raise InvalidInputError(
                'A position requirement is needed to check the navigation solution. Without it the '
                'drift is a number rather than a verdict.',
                context = createErrorContext(component = 'NavigationDrift'))

        findings = []

        drift = self.calculateDrift()

        source = AIDING_SOURCES[self.aiding]

        bound = source['positionBound']

        if bound is None:
            effective = drift['totalPosition']

            findings.append(
                f'Unaided, the position error reaches {effective:.0f} m at '
                f'{self.flightTime:.0f} s, dominated by {drift["dominant"]} at '
                f'{drift["dominantShare"]:.0%}.')
        else:
            effective = min(drift['totalPosition'], bound)

            findings.append(
                f'{self.aiding} bounds the position error at {bound:.0f} m against an unaided '
                f'{drift["totalPosition"]:.0f} m at {self.flightTime:.0f} s.')

            findings.append(
                f'**The aiding does not reduce the inertial error, it stops it growing.** At '
                f'{source["availability"]:.0%} availability the unaided case is what has to be '
                f'survivable, not merely unlikely.')

        meets = bool(effective <= self.positionRequirement)

        if not meets:
            raise NavigationError(
                f'The navigation solution reaches {effective:.0f} m against a requirement of '
                f'{self.positionRequirement:.0f} m at {self.flightTime:.0f} s of flight. The '
                f'dominant term is {drift["dominant"]} at {drift["dominantShare"]:.0%} of the '
                f'variance, so that is where a better sensor buys something. **A navigation '
                f'solution that does not meet its requirement is not a degraded solution**, it is '
                f'a vehicle that does not know where it is, so this is refused rather than '
                f'reported with a negative margin.',
                context = createErrorContext(component = 'NavigationDrift'))

        findings.append(
            f'That meets the {self.positionRequirement:.0f} m requirement with a factor of '
            f'{self.positionRequirement / effective:.1f}.')

        self.findings = findings

        return {'unaidedError':   drift['totalPosition'],
                'effectiveError': effective,
                'bound':          bound,
                'availability':   source['availability'],
                'requirement':    self.positionRequirement,
                'meets':          meets,
                'dominant':       drift['dominant'],
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def compareGrades(self) -> dict:

        '''

        The same flight on every IMU grade, which is where the four orders of magnitude show.

        '''

        original = self.grade

        results = {}

        try:
            for grade in IMU_GRADES:

                self.grade = grade

                drift = self.calculateDrift()

                results[grade] = {'attitude': drift['attitudeDegrees'],
                                  'position': drift['totalPosition'],
                                  'dominant': drift['dominant']}

        finally:
            self.grade = original

        best = min(results, key = lambda name: results[name]['position'])

        spread = (max(entry['position'] for entry in results.values())
                  / min(entry['position'] for entry in results.values()))

        return {'results': results,
                'best':    best,
                'spread':  spread}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full navigation drift report.
        '''

        drift = self.calculateDrift()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  NAVIGATION DRIFT: {self.grade} grade over {self.flightTime:.0f} s, '
                     f'aiding {self.aiding}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [[name, f'{value:.1f}', f'{drift["shares"][name]:.1%}']
             for name, value in sorted(drift['terms'].items(), key = lambda item: -item[1])],
            ['Term', 'Position error [m]', 'Share of variance'], title = 'By term'))

        lines.append('')
        lines.append(formatReportTable(
            [['Attitude error',  f'{drift["attitudeDegrees"]:.4f}',   'deg'],
             ['Position error',  f'{drift["totalPosition"]:.1f}',     'm'],
             ['Dominant term',   f'{drift["dominant"]}',              ''],
             ['Its share',       f'{drift["dominantShare"]:.0%}',     '']],
            ['Quantity', 'Value', 'Unit'], title = 'Total'))

        crossover = self.identifyCrossover()

        lines.append('')
        for finding in crossover['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'navigation_drift.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.grade not in IMU_GRADES:
            raise InvalidInputError(
                f"Unknown IMU grade '{self.grade}'. Known grades are {sorted(IMU_GRADES)}.",
                context = createErrorContext(component = 'NavigationDrift'))

        if self.aiding not in AIDING_SOURCES:
            raise InvalidInputError(
                f"Unknown aiding source '{self.aiding}'. Known sources are "
                f'{sorted(AIDING_SOURCES)}.',
                context = createErrorContext(component = 'NavigationDrift'))

        if self.flightTime <= 0.0:
            raise InvalidInputError(
                f'The flight time must be positive, got {self.flightTime}.',
                context = createErrorContext(component = 'NavigationDrift'))

        for name, value in (('gyro bias', self.gyroBias), ('accelerometer bias', self.accelBias)):
            if np.isfinite(value) and value < 0.0:
                raise InvalidInputError(
                    f'The {name} cannot be negative, got {value}. A bias has a sign in reality and '
                    f'this model uses its magnitude, so supply the magnitude.',
                    context = createErrorContext(component = 'NavigationDrift'))

        if np.isfinite(self.positionRequirement) and self.positionRequirement <= 0.0:
            raise InvalidInputError(
                f'The position requirement must be positive, got {self.positionRequirement}.',
                context = createErrorContext(component = 'NavigationDrift'))
