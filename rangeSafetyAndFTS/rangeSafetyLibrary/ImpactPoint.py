
# -- ImpactPoint -- #

'''

Where the vehicle would land if thrust stopped now, and how fast that place is running away.

The instantaneous impact point is the whole of trajectory-based range safety. The state vector
defines a Keplerian orbit; follow it forward to where it crosses the Earth's surface and that is
where the debris goes if the vehicle fails or is terminated in the next instant.

Two properties of it decide how a launch is protected, and neither is obvious.

**The impact point accelerates.** Downrange distance grows roughly as the square of speed at a
fixed flight path angle, so the impact point moves slowly early in the ascent and then extremely
quickly. A destruct line drawn where the impact point crosses it in ten seconds early in the flight
is crossed in one second later, and **the useful reaction time is set by the fastest part of the
ascent rather than the average.**

**And then it ceases to exist.** At orbital insertion the free-flight perigee rises above the
surface, the trajectory no longer intersects the Earth, and there is no impact point at all. That
is not a numerical failure and the class raises rather than returning a large number: **it is the
moment the flight termination system stops having a job**, and it is the natural end of the range
safety flight phase.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from rangeSafetyUtils import (EARTH_RADIUS, EARTH_MU, EARTH_ROTATION_RATE,
                                  freeFlightRangeAngle,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, ImpactPointError)
except ImportError:
    from .rangeSafetyUtils import (EARTH_RADIUS, EARTH_MU, EARTH_ROTATION_RATE,
                                   freeFlightRangeAngle,
                                   applyInputs, formatReportTable, createErrorContext,
                                   InvalidInputError, ImpactPointError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The time step used to differentiate the impact point numerically along a supplied ascent state
# history. Small enough that the drift rate is a derivative rather than a difference.
DRIFT_STEP = 1.0    # [s]

# ------------------------------------------------------------------------------------------------ #
# -- ImpactPoint -- #
# ------------------------------------------------------------------------------------------------ #

class ImpactPoint:

    '''

    Instantaneous impact point from a state, its drift rate along an ascent, and when it crosses a
    destruct line.

    '''

    def __init__(self):

        self.altitude        = np.nan
        self.speed           = np.nan
        self.flightPathAngle = np.nan
        self.states          = []
        self.destructRange   = np.nan
        self.reactionTime    = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `altitude` in metres above the surface, `speed` inertial in m/s, and `flightPathAngle`
        above the local horizontal in degrees. Those three are a state.

        `states` is a list of dictionaries with `time`, `altitude`, `speed` and `flightPathAngle`,
        which turns a single impact point into a drift history.

        `destructRange` is the downrange distance at which a destruct line sits, and `reactionTime`
        is how long the decision and the termination take. Together they say how much warning the
        line actually gives.

        '''

        requiredParams = {'altitude': (int, float),
                          'speed':    (int, float)}

        optionalParams = {'flightPathAngle': (int, float),
                          'states':          list,
                          'destructRange':   (int, float),
                          'reactionTime':    (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.flightPathAngle):
            self.flightPathAngle = 0.0

        if self.states is None or isinstance(self.states, float):
            self.states = []

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateImpactPoint(self, altitude: float = None, speed: float = None,
                             flightPathAngle: float = None) -> dict:

        '''

        The impact point for one state, with the Earth rotation correction applied to where it
        lands rather than as a term in the trajectory.

        '''

        height = altitude if altitude is not None else self.altitude
        velocity = speed if speed is not None else self.speed
        angle = flightPathAngle if flightPathAngle is not None else self.flightPathAngle

        solution = freeFlightRangeAngle(EARTH_RADIUS + height, velocity, angle)

        downrange = solution['rangeAngle'] * EARTH_RADIUS

        # The ground turns underneath the free-flight arc. At the equator that is about 465 m/s,
        # so a five minute flight moves the impact point 140 km west of where a non-rotating Earth
        # would put it. It is a correction rather than a detail.
        rotationOffset = (EARTH_ROTATION_RATE * solution['timeOfFlight'] * EARTH_RADIUS
                          if np.isfinite(solution['timeOfFlight']) else np.nan)

        return {'altitude':        height,
                'speed':           velocity,
                'flightPathAngle': angle,
                'downrange':       downrange,
                'rangeAngle':      solution['rangeAngle'],
                'timeOfFlight':    solution['timeOfFlight'],
                'rotationOffset':  rotationOffset,
                'eccentricity':    solution['eccentricity'],
                'perigeeAltitude': solution['perigeeAltitude']}

    # -------------------------------------------------------------------------------------------- #

    def driftRate(self, altitude: float = None, speed: float = None,
                  flightPathAngle: float = None, acceleration: float = None) -> dict:

        '''

        How fast the impact point is moving downrange, per second of flight.

        Differentiated numerically against speed, because the speed term dominates: at a fixed
        flight path angle the downrange distance grows roughly as the square of speed, so the drift
        rate grows roughly linearly with it and the impact point accelerates through the ascent.

        '''

        height = altitude if altitude is not None else self.altitude
        velocity = speed if speed is not None else self.speed
        angle = flightPathAngle if flightPathAngle is not None else self.flightPathAngle
        thrust = acceleration if acceleration is not None else 20.0

        here = self.calculateImpactPoint(height, velocity, angle)
        later = self.calculateImpactPoint(height + velocity * np.sin(np.radians(angle)) * DRIFT_STEP,
                                          velocity + thrust * DRIFT_STEP,
                                          angle)

        rate = (later['downrange'] - here['downrange']) / DRIFT_STEP

        return {'downrange':    here['downrange'],
                'driftRate':    rate,
                'acceleration': thrust,
                'speed':        velocity,
                'secondsPerHundredKilometres': 1.0e5 / rate if rate > 0.0 else np.inf}

    # -------------------------------------------------------------------------------------------- #

    def traceAscent(self) -> dict:

        '''

        The impact point through an ascent, up to the point where it stops existing.

        The table is the argument: the impact point crawls early and sprints late, and the row
        where it disappears is orbital insertion.

        '''

        if not self.states:
            raise ImpactPointError('A state history is needed to trace an ascent.')

        trace = []
        insertion = None

        for state in self.states:

            entry = {'time':            float(state['time']),
                     'altitude':        float(state['altitude']),
                     'speed':           float(state['speed']),
                     'flightPathAngle': float(state.get('flightPathAngle', 0.0))}

            try:
                point = self.calculateImpactPoint(entry['altitude'], entry['speed'],
                                                  entry['flightPathAngle'])
                entry['downrange'] = point['downrange']
                entry['timeOfFlight'] = point['timeOfFlight']
                entry['hasImpactPoint'] = True

            except ImpactPointError:
                entry['downrange'] = np.nan
                entry['timeOfFlight'] = np.nan
                entry['hasImpactPoint'] = False
                if insertion is None:
                    insertion = entry['time']

            trace.append(entry)

        withPoint = [entry for entry in trace if entry['hasImpactPoint']]

        if len(withPoint) < 2:
            raise ImpactPointError('At least two states with an impact point are needed to trace '
                                   'a drift.')

        for index in range(1, len(withPoint)):
            span = withPoint[index]['time'] - withPoint[index - 1]['time']
            withPoint[index]['driftRate'] = (
                (withPoint[index]['downrange'] - withPoint[index - 1]['downrange']) / span)

        withPoint[0]['driftRate'] = withPoint[1]['driftRate']

        rates = [entry['driftRate'] for entry in withPoint]

        return {'trace':          trace,
                'withImpactPoint': withPoint,
                'insertionTime':  insertion,
                'firstDriftRate': rates[0],
                'lastDriftRate':  rates[-1],
                'driftAcceleration': rates[-1] / rates[0] if rates[0] > 0.0 else np.inf,
                'finalDownrange': withPoint[-1]['downrange']}

    # -------------------------------------------------------------------------------------------- #

    def checkDestructLine(self) -> dict:

        '''

        How much warning a destruct line gives, and whether it is enough.

        The line is crossed by the impact point rather than by the vehicle, and the time from the
        line being approached to being crossed is the whole of the decision budget. **Because the
        impact point accelerates, that budget shrinks through the flight**, and a line sized on an
        early drift rate is sized on the wrong number.

        '''

        if not np.isfinite(self.destructRange):
            raise ImpactPointError('A destruct range is needed to check a destruct line.')

        trace = self.traceAscent()

        crossing = next((entry for entry in trace['withImpactPoint']
                         if entry['downrange'] >= self.destructRange), None)

        if crossing is None:
            return {'destructRange': self.destructRange,
                    'crossed':       False,
                    'finalDownrange': trace['finalDownrange'],
                    'note':          'the impact point never reaches the line before insertion'}

        # The warning is how long the impact point takes to cross the line at the drift rate there.
        # A hundred kilometre approach corridor is a conventional way to express it.
        warning = 1.0e5 / crossing['driftRate'] if crossing['driftRate'] > 0.0 else np.inf

        result = {'destructRange':  self.destructRange,
                  'crossed':        True,
                  'crossingTime':   crossing['time'],
                  'driftRateAtLine': crossing['driftRate'],
                  'warningTime':    warning,
                  'firstDriftRate': trace['firstDriftRate'],
                  'driftAcceleration': trace['driftAcceleration']}

        if np.isfinite(self.reactionTime):

            result['reactionTime'] = self.reactionTime
            result['margin'] = warning / self.reactionTime

            if warning < self.reactionTime:
                raise ImpactPointError(
                    f'The impact point crosses the last hundred kilometres to the destruct line in '
                    f'{warning:.1f} s against a reaction time of {self.reactionTime:.1f} s. The '
                    f'line gives no usable warning at this point in the flight, because the impact '
                    f'point drift has grown by {trace["driftAcceleration"]:.0f} times since '
                    f'liftoff.',
                    context = {'warningTime':  warning,
                               'reactionTime': self.reactionTime,
                               'driftRate':    crossing['driftRate']})

        return result

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The impact point now, and the ascent trace if a state history was supplied.
        '''

        lines = []

        try:
            point = self.calculateImpactPoint()
            lines.append(formatReportTable(
                [[f'{point["altitude"] / 1000.0:.0f}',
                  f'{point["speed"]:,.0f}',
                  f'{point["flightPathAngle"]:.1f}',
                  f'{point["downrange"] / 1000.0:,.0f}',
                  f'{point["timeOfFlight"]:.0f}']],
                ['altitude [km]', 'speed [m/s]', 'gamma [deg]', 'downrange [km]', 'flight [s]'],
                title = 'INSTANTANEOUS IMPACT POINT'))

        except ImpactPointError as error:
            lines.append('NO IMPACT POINT')
            lines.append(str(error))

        if self.states:

            lines.append('')

            trace = self.traceAscent()

            lines.append(formatReportTable(
                [[f'{entry["time"]:.0f}',
                  f'{entry["altitude"] / 1000.0:.0f}',
                  f'{entry["speed"]:,.0f}',
                  f'{entry["downrange"] / 1000.0:,.0f}' if entry['hasImpactPoint'] else 'none',
                  f'{entry.get("driftRate", 0.0) / 1000.0:.1f}' if entry['hasImpactPoint'] else '']
                 for entry in trace['trace']],
                ['t [s]', 'alt [km]', 'speed [m/s]', 'IIP [km]', 'drift [km/s]'],
                title = 'IMPACT POINT THROUGH THE ASCENT'))

            lines.append('')
            lines.append(f'Drift grows by {trace["driftAcceleration"]:.0f} times across the ascent.')

            if trace['insertionTime'] is not None:
                lines.append(f'The impact point ceases to exist at t+{trace["insertionTime"]:.0f} s.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'impactPoint.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not np.isfinite(self.altitude) or self.altitude < 0.0:
            raise InvalidInputError('Altitude cannot be negative.')

        if not np.isfinite(self.speed) or self.speed < 0.0:
            raise InvalidInputError('Speed cannot be negative.')

        if abs(self.flightPathAngle) >= 90.0:
            raise InvalidInputError('A flight path angle at or beyond ninety degrees is vertical, '
                                    'which the horizontal-referenced convention cannot express.')

        for state in self.states:
            for key in ('time', 'altitude', 'speed'):
                if key not in state:
                    raise InvalidInputError(f'Every state needs a {key}.')

        if np.isfinite(self.destructRange) and self.destructRange <= 0.0:
            raise InvalidInputError('Destruct range must be positive.')

        if np.isfinite(self.reactionTime) and self.reactionTime <= 0.0:
            raise InvalidInputError('Reaction time must be positive.')
