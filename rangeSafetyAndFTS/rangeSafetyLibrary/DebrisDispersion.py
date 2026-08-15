
# -- DebrisDispersion -- #

'''

Where the pieces land after a destruct, and how far apart.

A public risk analysis needs the probability that debris reaches each populated region. That number
is usually assumed, and it is the weakest input in the calculation because everything else is
multiplied by it. This class computes it instead, by propagating a fragment catalogue from the
break-up point to the ground.

**The ballistic coefficient is the whole model.** `m / (Cd A)` decides how much of its downrange
velocity a fragment keeps, how long it falls, and therefore how far the wind carries it. A launch
vehicle's catalogue spans three orders of magnitude in it, from an insulation panel to a turbopump,
and **that spread is what makes a debris footprint tens of kilometres long rather than a point.**

Two results come out of it that a single average fragment cannot produce.

**The far end of the footprint is set by the heaviest fragments and the near end by the lightest**,
and they are far apart. Dense fragments carry their downrange velocity almost to the ground; light
ones stop in the upper air and fall nearly vertically from wherever they stopped.

**Wind matters for the light end and not for the heavy end**, because drift is the wind speed times
the fall time and the fall time differs by an order of magnitude across the catalogue. A wind that
moves a turbopump a few hundred metres moves an insulation panel tens of kilometres.

Author: Sean Bowman
Date:   08/14/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import math
import os

import numpy as np

try:
    from rangeSafetyUtils import (DEBRIS_CATALOGUE, DESTRUCT_IMPARTED_VELOCITY, CASUALTY_AREA,
                                  GRAVITY, ballisticCoefficient, terminalVelocity,
                                  atmosphericDensity, ATMOSPHERIC_SCALE_HEIGHT,
                                  applyInputs, formatReportTable,
                                  createErrorContext, InvalidInputError, RiskError)
except ImportError:
    from .rangeSafetyUtils import (DEBRIS_CATALOGUE, DESTRUCT_IMPARTED_VELOCITY, CASUALTY_AREA,
                                   GRAVITY, ballisticCoefficient, terminalVelocity,
                                   atmosphericDensity, ATMOSPHERIC_SCALE_HEIGHT,
                                   applyInputs, formatReportTable,
                                   createErrorContext, InvalidInputError, RiskError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The integration step is set from what is actually changing rather than fixed, because a fixed
# step is either wrong for an insulation panel entering thick air or unaffordable for the same
# panel spending forty minutes at terminal velocity afterwards.
#
# Two criteria, and the tighter one wins. The velocity must not change by much in one step, which
# binds while a fragment is decelerating and relaxes to nothing once it reaches terminal velocity.
# And the altitude must not change by much of a scale height, which is what keeps the density from
# stepping over its own variation.
# Halving both moves the furthest impact by under a metre and the most wind-drifted one by 34 m in
# 57 km, which is a test rather than a claim.
STEP_VELOCITY_FRACTION = 0.01             # [-] of the current speed, per step
STEP_SCALE_HEIGHT_FRACTION = 0.01         # [-] of the atmospheric scale height, per step
MINIMUM_STEP = 0.01                       # [s]
MAXIMUM_STEP = 4.0                        # [s]

# Ceiling on the fall time, so that a fragment which somehow fails to descend stops the integration
# rather than running forever. An insulation panel from 40 km takes about 45 minutes.
MAXIMUM_FALL_TIME = 7200.0        # [s]

# One-sigma fraction of the imparted speed that lands in the cross-range direction. The destruct
# throws fragments in every direction and only the cross-range component widens the footprint.
CROSS_RANGE_VELOCITY_FRACTION = 0.577     # [-], the standard deviation of a uniform direction

# One-sigma uncertainty on the mean wind between the last balloon and the flight. Representative,
# and it is the term that spreads the light end of the catalogue: drift is the wind times the fall
# time, so an error in the wind is an error in the impact point multiplied by three quarters of an
# hour for an insulation panel and by three minutes for a turbopump.
DEFAULT_WIND_UNCERTAINTY = 3.0            # [m/s]

# Fraction of the catalogue the defined regions must account for. A dispersed class has tails that
# run to infinity, so exact coverage is not achievable; three nines separates a tail from a hole.
UNASSIGNED_FRAGMENT_TOLERANCE = 0.999     # [-]

# ------------------------------------------------------------------------------------------------ #
# -- DebrisDispersion -- #
# ------------------------------------------------------------------------------------------------ #

class DebrisDispersion:

    '''

    Fragment catalogue, ballistic propagation to the ground, footprint and impact probabilities.

    '''

    def __init__(self):

        self.breakupAltitude       = np.nan   # [m]
        self.breakupSpeed          = np.nan   # [m/s]
        self.breakupFlightPathAngle = np.nan  # [deg] above the local horizontal
        self.breakupDownrange      = np.nan   # [m] from the launch point

        self.catalogue             = None     # dict of fragment classes
        self.impartedVelocity      = np.nan   # [m/s]

        self.windSpeed             = np.nan   # [m/s], positive downrange
        self.windUncertainty       = np.nan   # [m/s], one sigma on the mean wind
        self.windAltitudeLimit     = np.nan   # [m], above which the wind is taken as zero

        self._propagation          = None
        self.findings              = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load the break-up state and the fragment catalogue.

        `breakupDownrange` is where the vehicle was when the destruct command took effect, which is
        the instantaneous impact point calculation in `ImpactPoint`, not the vehicle's ground track.
        Every impact distance this class reports is measured from the same launch point.

        `catalogue` defaults to `DEBRIS_CATALOGUE`. A programme's own catalogue is the right input
        and this one is representative.

        `windSpeed` is a mean downrange wind. It is deliberately a single number: a real dispersion
        uses a measured wind profile, and carrying one here would imply the rest of the model is
        good enough to deserve it.

        '''

        requiredParams = {'breakupAltitude':        (int, float),
                          'breakupSpeed':           (int, float),
                          'breakupFlightPathAngle': (int, float)}

        optionalParams = {'breakupDownrange':   (int, float),
                          'catalogue':          dict,
                          'impartedVelocity':   (int, float),
                          'windSpeed':          (int, float),
                          'windUncertainty':    (int, float),
                          'windAltitudeLimit':  (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.catalogue is None or not isinstance(self.catalogue, dict) or not self.catalogue:
            self.catalogue = DEBRIS_CATALOGUE

        if not np.isfinite(self.impartedVelocity):
            self.impartedVelocity = DESTRUCT_IMPARTED_VELOCITY

        if not np.isfinite(self.breakupDownrange):
            self.breakupDownrange = 0.0

        if not np.isfinite(self.windSpeed):
            self.windSpeed = 0.0

        if not np.isfinite(self.windUncertainty):
            self.windUncertainty = DEFAULT_WIND_UNCERTAINTY

        if not np.isfinite(self.windAltitudeLimit):
            self.windAltitudeLimit = 12000.0

        self._propagation = None

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def ballisticCoefficients(self) -> dict:

        '''

        The catalogue sorted by ballistic coefficient, with the terminal velocity each implies.

        Reported before anything is propagated, because the ordering here is the ordering of every
        result that follows and it costs one division per class.

        '''

        entries = []

        for name, entry in self.catalogue.items():

            ballistic = ballisticCoefficient(entry['mass'], entry['dragArea'])

            entries.append({'class':      name,
                            'count':      float(entry['count']),
                            'mass':       float(entry['mass']),
                            'dragArea':   float(entry['dragArea']),
                            'ballistic':  ballistic,
                            'terminal':   terminalVelocity(ballistic),
                            'casualtyClass': entry.get('casualtyClass', 'medium')})

        entries.sort(key = lambda item: item['ballistic'])

        span = entries[-1]['ballistic'] / entries[0]['ballistic']

        return {'fragments':    entries,
                'lightest':     entries[0]['class'],
                'heaviest':     entries[-1]['class'],
                'ballisticSpan': span,
                'totalCount':   sum(item['count'] for item in entries),
                'totalMass':    sum(item['count'] * item['mass'] for item in entries)}

    # -------------------------------------------------------------------------------------------- #

    def propagate(self) -> dict:

        '''

        Fall every fragment class from the break-up point to the ground.

        A two dimensional point mass with drag in an exponential atmosphere, integrated with a
        fixed step. The fragment starts with the vehicle's velocity at break-up, so a dense
        fragment keeps most of the downrange component and a light one loses it in the first few
        kilometres of fall.

        Wind is applied below `windAltitudeLimit` as a horizontal velocity the air carries, so the
        drag acts on the velocity relative to the air rather than to the ground. That is the whole
        of the wind model and it is the reason light fragments drift and heavy ones do not.

        '''

        if self._propagation is not None:
            return self._propagation

        results = []

        for entry in self.ballisticCoefficients()['fragments']:

            trace = self._fall(entry['ballistic'])

            # Downrange spread about the mean impact point, from two independent causes.
            #
            # The destruct throws the fragment isotropically, so the same displacement that widens
            # the footprint cross-range spreads it downrange. And the mean wind is not known
            # exactly, so its error is multiplied by the fall time.
            #
            # **The two are dominant at opposite ends of the catalogue.** A turbopump keeps its
            # throw and falls too fast for the wind to matter; an insulation panel loses its throw
            # in seconds and then spends three quarters of an hour in a wind nobody measured.
            throwSpread = trace['crossRange']
            windSpread  = self.windUncertainty * trace['time']

            results.append({**entry,
                            'fallTime':       trace['time'],
                            'impactRange':    self.breakupDownrange + trace['downrange'],
                            'glideRange':     trace['downrange'],
                            'impactSpeed':    trace['speed'],
                            'crossRange':     trace['crossRange'],
                            'throwSpread':    throwSpread,
                            'windSpread':     windSpread,
                            'spread':         float(np.hypot(throwSpread, windSpread)),
                            'spreadCause':    'wind' if windSpread > throwSpread else 'destruct',
                            'windDrift':      trace['windDrift']})

        nearest  = min(results, key = lambda item: item['impactRange'])
        furthest = max(results, key = lambda item: item['impactRange'])

        length = furthest['impactRange'] - nearest['impactRange']

        # The cross-range half width, integrated rather than taken as the imparted speed times the
        # fall time. The two are nothing alike: a fragment thrown sideways decelerates under the
        # same drag that makes it fall slowly, so the throw is spent in the first few seconds.
        halfWidth = max(item['crossRange'] for item in results)

        findings = []

        findings.append(
            f'The catalogue spans {self.ballisticCoefficients()["ballisticSpan"]:.0f} to one in '
            f'ballistic coefficient, and the impacts span '
            f'{length / 1000.0:.1f} km along the trajectory.')

        byBallistic = [item['class'] for item in
                       sorted(results, key = lambda item: item['ballistic'])]
        byImpact    = [item['class'] for item in
                       sorted(results, key = lambda item: item['impactRange'])]

        orderingHolds = byBallistic == byImpact

        findings.append(
            f'**The far end of the footprint belongs to {furthest["class"]} and the near end to '
            f'{nearest["class"]}.** Dense fragments keep their downrange velocity almost to the '
            f'ground; light ones stop in the upper air and fall from where they stopped.')

        if orderingHolds:
            findings.append(
                'The impacts fall in ballistic coefficient order, which is what happens in still '
                'air: nothing but the fragment decides where it lands.')
        else:
            findings.append(
                f'**The impacts are NOT in ballistic coefficient order.** In still air they would '
                f'be, and the wind breaks it: {byBallistic[0]} is the lightest fragment in the '
                f'catalogue and it lands past {byImpact[0]}, because it falls slowly enough for '
                f'the wind to carry it further than its own trajectory took it. **A footprint is '
                f'therefore not a property of the vehicle alone**, and the order of the pieces on '
                f'the ground changes with the weather.')

        drifts = [abs(item['windDrift']) for item in results]

        driftRatio = max(drifts) / max(min(drifts), 1.0)

        lightest = min(results, key = lambda item: item['ballistic'])
        heaviest = max(results, key = lambda item: item['ballistic'])

        findings.append(
            f'The wind moves {lightest["class"]} by '
            f'{abs(lightest["windDrift"]) / 1000.0:.1f} km and {heaviest["class"]} by '
            f'{abs(heaviest["windDrift"]):.0f} m, a factor of {driftRatio:.0f}. **Drift is the '
            f'wind speed times the fall time and the fall times differ by an order of magnitude**, '
            f'so a wind that is negligible for the heavy end sets the position of the light end.')

        windDominated = [item['class'] for item in results if item['spreadCause'] == 'wind']
        throwDominated = [item['class'] for item in results if item['spreadCause'] == 'destruct']

        findings.append(
            f'**The scatter about each impact point comes from a different cause at each end of '
            f'the catalogue.** The wind not being known exactly spreads '
            f'{len(windDominated)} of {len(results)} classes and the destruct throw spreads '
            f'{len(throwDominated)}. A fragment that falls slowly loses its throw in seconds and '
            f'then spends the rest of the descent in a wind nobody measured; a fragment that falls '
            f'fast does the opposite.')

        self.findings = findings

        self._propagation = {'fragments':      results,
                             'orderingHolds':  bool(orderingHolds),
                             'nearest':        nearest['class'],
                             'furthest':       furthest['class'],
                             'nearestRange':   nearest['impactRange'],
                             'furthestRange':  furthest['impactRange'],
                             'footprintLength': length,
                             'halfWidth':      halfWidth,
                             'longestFall':    max(item['fallTime'] for item in results),
                             'findings':       findings}

        return self._propagation

    # -------------------------------------------------------------------------------------------- #

    def footprint(self) -> dict:

        '''

        The debris footprint as an area, and what fraction of the catalogue is in it.

        Reported as a rectangle rather than an ellipse. An ellipse implies a distribution this
        model does not have: four fragment classes give four impact points, not a density, and
        drawing a smooth contour through four points would look like a Monte Carlo result without
        being one.

        '''

        propagation = self.propagate()

        length = propagation['footprintLength']
        width  = 2.0 * propagation['halfWidth']

        area = length * width

        density = propagation['fragments']

        return {'length':       length,
                'width':        width,
                'area':         area,
                'nearestRange': propagation['nearestRange'],
                'furthestRange': propagation['furthestRange'],
                'fragmentCount': sum(item['count'] for item in density),
                'aspectRatio':  length / width if width > 0.0 else np.inf}

    # -------------------------------------------------------------------------------------------- #

    def impactProbabilities(self, regions: list) -> dict:

        '''

        Fraction of the catalogue landing in each downrange band, which is what a risk analysis
        needs and usually assumes.

        `regions` is a list of dictionaries with `name`, `start` and `end` in metres downrange from
        the launch point, and optionally `crossRange` and `crossWidth` for a region that sits
        beside the trajectory rather than under it.

        **The cross-range term is what a launch azimuth actually buys.** A footprint is a few
        kilometres wide and tens long, so a town ten kilometres off the ground track takes a
        fraction of the debris that the same town directly downrange would take. A region given no
        cross-range extent is taken as spanning the whole width, which is the conservative reading
        and the right default.

        **This raises where the bands do not cover the footprint.** A risk analysis missing the
        region a fragment lands in is not conservative, it is incomplete, and reporting a total
        below one lets the shortfall pass as rounding.

        '''

        if not regions:
            raise RiskError(
                'Impact probabilities need regions to fall into. A footprint with no regions '
                'defined over it produces no risk number, which is not the same as no risk.',
                context = createErrorContext(component = 'DebrisDispersion'))

        propagation = self.propagate()

        totalCount = sum(item['count'] for item in propagation['fragments'])

        entries = []

        for region in regions:

            start, end = float(region['start']), float(region['end'])

            if end <= start:
                raise InvalidInputError(
                    f'Region \'{region["name"]}\' runs from {start:.0f} to {end:.0f} m, which is '
                    f'empty or reversed.',
                    context = createErrorContext(component = 'DebrisDispersion'))

            count = 0.0
            area  = 0.0
            inside = []

            offset    = float(region.get('crossRange', 0.0))
            halfExtent = (0.5 * float(region['crossWidth'])
                          if region.get('crossWidth') else None)

            for item in propagation['fragments']:

                fraction = self._fractionInBand(item, start, end)

                if halfExtent is not None:
                    fraction *= self._fractionAcross(item, offset - halfExtent,
                                                     offset + halfExtent)

                if fraction <= 0.0:
                    continue

                inside.append(item['class'])

                count += item['count'] * fraction
                area  += (item['count'] * fraction
                          * CASUALTY_AREA[item['casualtyClass']]['area'])

            entries.append({'name':              region['name'],
                            'start':             start,
                            'end':               end,
                            'classes':           inside,
                            'count':             count,
                            'impactProbability': count / totalCount,
                            'casualtyArea':      area})

        assigned = sum(entry['count'] for entry in entries)

        # A dispersed class has tails, so exact coverage is not achievable and near coverage is.
        # The threshold is what separates a tail from a hole in the analysis.
        #
        # Coverage is checked downrange only. A region narrower than the footprint is deliberately
        # not covering all of it, and the debris that misses it lands somewhere the analysis has
        # already accounted for in the band containing it.
        if assigned < UNASSIGNED_FRAGMENT_TOLERANCE * totalCount and not any(
                region.get('crossWidth') for region in regions):

            missing = [item['class'] for item in propagation['fragments']
                       if sum(self._fractionInBand(item, entry['start'], entry['end'])
                              for entry in entries) < UNASSIGNED_FRAGMENT_TOLERANCE]

            raise RiskError(
                f'{totalCount - assigned:.0f} of {totalCount:.0f} fragments land outside every '
                f'region defined, and the classes least covered are {sorted(set(missing))}. A risk '
                f'analysis that does not cover where the debris lands is incomplete rather than '
                f'conservative, and a probability total below one would let the shortfall pass as '
                f'rounding.',
                context = {'footprint': (propagation['nearestRange'],
                                         propagation['furthestRange']),
                           'regions':   [(entry['start'], entry['end']) for entry in entries]})

        totalArea = sum(entry['casualtyArea'] for entry in entries)

        for entry in entries:
            entry['areaShare'] = entry['casualtyArea'] / totalArea if totalArea > 0.0 else 0.0

        byCount = max(entries, key = lambda entry: entry['count'])
        byArea  = max(entries, key = lambda entry: entry['casualtyArea'])

        return {'regions':          entries,
                'totalCount':       totalCount,
                'totalCasualtyArea': totalArea,
                'mostFragments':    byCount['name'],
                'mostCasualtyArea': byArea['name'],
                'rankingAgrees':    byCount['name'] == byArea['name']}

    # -------------------------------------------------------------------------------------------- #

    def windSensitivity(self, speeds: list = None) -> dict:

        '''

        The footprint against wind speed, which is the input a launch day decision turns on.

        A wind limit is usually justified by loads on the vehicle. This says what it does to the
        debris footprint, which is a different and sometimes larger effect.

        '''

        if speeds is None:
            speeds = [0.0, 5.0, 10.0, 20.0, 30.0]

        original = self.windSpeed

        results = []

        try:
            for speed in speeds:

                self.windSpeed = speed
                self._propagation = None

                propagation = self.propagate()

                results.append({'windSpeed':       speed,
                                'nearestRange':    propagation['nearestRange'],
                                'furthestRange':   propagation['furthestRange'],
                                'footprintLength': propagation['footprintLength']})
        finally:
            self.windSpeed = original
            self._propagation = None

        nearest = [entry['nearestRange'] for entry in results]

        return {'results':        results,
                'nearestMoved':   max(nearest) - min(nearest),
                'lengthMoved':    (max(entry['footprintLength'] for entry in results)
                                   - min(entry['footprintLength'] for entry in results)),
                'nearEndDominates': bool(max(nearest) - min(nearest)
                                         > 0.5 * (max(entry['footprintLength']
                                                      for entry in results)
                                                  - min(entry['footprintLength']
                                                        for entry in results)))}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The catalogue, where each class lands, and the footprint it adds up to.
        '''

        propagation = self.propagate()
        extent      = self.footprint()

        lines = []

        lines.append(formatReportTable(
            [[item['class'],
              f'{item["count"]:.0f}',
              f'{item["ballistic"]:.1f}',
              f'{item["terminal"]:.1f}',
              f'{item["fallTime"]:.0f}',
              f'{item["impactRange"] / 1000.0:.1f}',
              f'{item["windDrift"] / 1000.0:.2f}']
             for item in propagation['fragments']],
            ['class', 'count', 'beta [kg/m2]', 'v_t [m/s]', 'fall [s]', 'impact [km]',
             'drift [km]'],
            title = 'DEBRIS CATALOGUE AND IMPACTS'))

        lines.append('')
        lines.append(f'Footprint {extent["length"] / 1000.0:.1f} km long by '
                     f'{extent["width"] / 1000.0:.1f} km wide, from '
                     f'{extent["nearestRange"] / 1000.0:.1f} to '
                     f'{extent["furthestRange"] / 1000.0:.1f} km downrange.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'debrisDispersion.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _fractionAcross(self, fragment: dict, start: float, end: float) -> float:

        '''

        Fraction of a fragment class landing between two cross-range offsets.

        The spread is the same as the downrange one, and that is not an approximation. A mean wind
        moves the whole footprint sideways rather than widening it, but the UNCERTAINTY in that
        wind is a vector: its cross-range component is as large as its downrange component, and it
        acts over the same fall time.

        **The consequence is that light debris disperses cross-range by kilometres and heavy
        debris by hundreds of metres**, which is the opposite ordering to the destruct throw and is
        what actually sets how far off the ground track a town has to be.

        '''

        spread = fragment['spread']

        if spread <= 0.0:
            return 1.0 if start <= 0.0 < end else 0.0

        def cumulative(value: float) -> float:
            return 0.5 * (1.0 + math.erf(value / (spread * math.sqrt(2.0))))

        return cumulative(end) - cumulative(start)

    # -------------------------------------------------------------------------------------------- #

    def _fractionInBand(self, fragment: dict, start: float, end: float) -> float:

        '''

        Fraction of a fragment class landing between two downrange distances.

        Each class is taken as normally distributed about its computed impact point, with the
        standard deviation from the destruct throw and the wind uncertainty. **That is a
        distribution over one cause of scatter and not over all of them**: it says nothing about
        where inside a class the individual fragments differ, or about break-up time uncertainty,
        both of which a real analysis carries.

        '''

        spread = fragment['spread']

        if spread <= 0.0:
            return 1.0 if start <= fragment['impactRange'] < end else 0.0

        # The normal CDF from the error function, so this needs nothing beyond numpy.
        def cumulative(value: float) -> float:
            return 0.5 * (1.0 + math.erf((value - fragment['impactRange'])
                                         / (spread * math.sqrt(2.0))))

        return cumulative(end) - cumulative(start)

    # -------------------------------------------------------------------------------------------- #

    def _fall(self, ballistic: float) -> dict:

        '''

        Integrate one fragment from the break-up state to the ground.

        Fixed step fourth order Runge-Kutta on the two dimensional state. The drag acts on the
        velocity relative to the air, which is what makes the wind term do anything at all.

        '''

        angle = np.radians(self.breakupFlightPathAngle)

        # Six states: downrange, altitude, the two in-plane velocities, and the cross-range pair
        # the destruct charge starts moving. The cross-range component decays under the same drag
        # as everything else, which is the reason it is integrated rather than estimated.
        state = np.array([0.0,
                          self.breakupAltitude,
                          self.breakupSpeed * np.cos(angle),
                          self.breakupSpeed * np.sin(angle),
                          0.0,
                          self.impartedVelocity * CROSS_RANGE_VELOCITY_FRACTION])

        # The same fragment with no wind, so the drift is the difference between the two rather
        # than an estimate from the fall time.
        still = state.copy()

        time     = 0.0
        previous = state

        while state[1] > 0.0 and time < MAXIMUM_FALL_TIME:

            step = self._stepSize(state, ballistic)

            previous = state

            state = self._step(state, ballistic, self.windSpeed, step)
            still = self._step(still, ballistic, 0.0, step)

            time += step

        # Linear interpolation back to the ground, so the impact point does not depend on where the
        # last step happened to land.
        if previous[1] != state[1]:
            fraction = previous[1] / (previous[1] - state[1])
            impact   = previous + fraction * (state - previous)
        else:
            impact = state

        return {'time':       time,
                'downrange':  float(impact[0]),
                'speed':      float(np.hypot(impact[2], impact[3])),
                'crossRange': float(abs(impact[4])),
                'windDrift':  float(impact[0] - still[0])}

    def _stepSize(self, state: np.ndarray, ballistic: float) -> float:

        '''
        The tighter of two limits: a fraction of the time for the speed to change appreciably, and
        a fraction of the time to fall through a scale height.

        The first binds while a fragment is decelerating and relaxes once it reaches terminal
        velocity, where the net acceleration is near zero and nothing is changing. Using the drag
        time constant instead would keep the step small for the entire forty minute descent of a
        panel that has already stopped accelerating.
        '''

        speed = float(np.hypot(state[2], state[3]))

        rates = self._derivative(state, ballistic, self.windSpeed)

        acceleration = float(np.hypot(rates[2], rates[3]))

        velocityStep = (STEP_VELOCITY_FRACTION * max(speed, 1.0) / acceleration
                        if acceleration > 0.0 else MAXIMUM_STEP)

        vertical = abs(float(state[3]))

        altitudeStep = (STEP_SCALE_HEIGHT_FRACTION * ATMOSPHERIC_SCALE_HEIGHT / vertical
                        if vertical > 0.0 else MAXIMUM_STEP)

        return float(np.clip(min(velocityStep, altitudeStep), MINIMUM_STEP, MAXIMUM_STEP))

    def _step(self, state: np.ndarray, ballistic: float, wind: float,
              step: float) -> np.ndarray:

        '''
        One fourth order Runge-Kutta step.
        '''

        first  = self._derivative(state, ballistic, wind)
        second = self._derivative(state + 0.5 * step * first, ballistic, wind)
        third  = self._derivative(state + 0.5 * step * second, ballistic, wind)
        fourth = self._derivative(state + step * third, ballistic, wind)

        return state + (step / 6.0) * (first + 2.0 * second + 2.0 * third + fourth)

    def _derivative(self, state: np.ndarray, ballistic: float, wind: float) -> np.ndarray:

        '''
        Rates for the point mass. Drag decelerates along the velocity relative to the air, gravity
        acts on the vertical component alone, and the cross-range component sees the same drag.
        '''

        altitude = state[1]

        # The wind is a boundary layer feature and is taken as zero above its limit rather than
        # extended to the break-up altitude, where it would be a different wind entirely.
        localWind = wind if altitude <= self.windAltitudeLimit else 0.0

        relative = np.array([state[2] - localWind, state[3], state[5]])

        speed = float(np.linalg.norm(relative))

        density = atmosphericDensity(altitude)

        # rho v^2 / (2 beta) along the relative velocity
        deceleration = density * speed / (2.0 * ballistic)

        return np.array([state[2],
                         state[3],
                         -deceleration * relative[0],
                         -deceleration * relative[1] - GRAVITY,
                         state[5],
                         -deceleration * relative[2]])

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong footprint rather than an error.
        '''

        if not np.isfinite(self.breakupAltitude) or self.breakupAltitude <= 0.0:
            raise InvalidInputError(
                f'A break-up altitude of {self.breakupAltitude} m gives nothing to fall from.',
                context = createErrorContext(component = 'DebrisDispersion'))

        if not np.isfinite(self.breakupSpeed) or self.breakupSpeed < 0.0:
            raise InvalidInputError(
                f'A break-up speed of {self.breakupSpeed} m/s is not a state.',
                context = createErrorContext(component = 'DebrisDispersion'))

        if abs(self.breakupFlightPathAngle) > 90.0:
            raise InvalidInputError(
                f'A flight path angle of {self.breakupFlightPathAngle} degrees is outside the '
                f'range this class measures from the local horizontal.',
                context = createErrorContext(component = 'DebrisDispersion'))

        for name, entry in self.catalogue.items():

            for field in ('count', 'mass', 'dragArea'):
                if field not in entry:
                    raise InvalidInputError(
                        f'Fragment class \'{name}\' has no {field}. A catalogue entry needs a '
                        f'count, a mass and a drag area, because the ballistic coefficient is the '
                        f'whole model.',
                        context = createErrorContext(component = 'DebrisDispersion'))

            if entry['count'] <= 0.0:
                raise InvalidInputError(
                    f'Fragment class \'{name}\' has a count of {entry["count"]}. A class with no '
                    f'fragments in it should be left out rather than counted as zero.',
                    context = createErrorContext(component = 'DebrisDispersion'))

            casualty = entry.get('casualtyClass', 'medium')

            if casualty not in CASUALTY_AREA:
                raise InvalidInputError(
                    f'Fragment class \'{name}\' maps to casualty class \'{casualty}\', which is '
                    f'not one of {sorted(CASUALTY_AREA)}.',
                    context = createErrorContext(component = 'DebrisDispersion'))

        if self.impartedVelocity < 0.0:
            raise InvalidInputError(
                f'An imparted velocity of {self.impartedVelocity} m/s is not a destruct event.',
                context = createErrorContext(component = 'DebrisDispersion'))
