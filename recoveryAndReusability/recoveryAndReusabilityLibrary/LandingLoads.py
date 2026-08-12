
# -- LandingLoads -- #

'''

Touchdown, which is an energy problem dressed as a load problem.

The vehicle arrives with kinetic energy and the legs have to absorb it over a stroke. The load
factor is what that costs:

    n = v**2 / (2 * g * s * eta) + 1

with `s` the usable stroke and `eta` the efficiency of the absorber, the fraction of the
force-stroke rectangle it actually fills. **The load factor is inversely proportional to the
stroke**, which is the whole design conversation: doubling the stroke halves the load, and stroke is
cheap in mass compared with the structure that reacts the load.

**A crushable core is a one-shot absorber and a damper is not**, which is the difference between a
capsule and a reusable booster. The crushable core is lighter, has a flatter force-stroke curve and
an efficiency near 0.8; the damper is heavier and can be flown again without replacement. On a
vehicle designed for many flights that difference is the whole trade, and it is decided by flight
count rather than by mass.

**Tipover is the other failure and it is a geometry problem.** The vehicle tips if its centre of
gravity passes outside the leg footprint, and the margin is the angle from the centre of gravity to
the tipping edge. Horizontal velocity, ground slope and a leg that fails to lock all eat into it,
and they add rather than trading against each other.

Both failures are refused rather than reported. A vehicle that exceeds its structural load factor or
tips over is not a vehicle with a small negative margin.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from recoveryUtils import (GRAVITY,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, LandingError)
except ImportError:
    from .recoveryUtils import (GRAVITY,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, LandingError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Absorber efficiency: the fraction of the force-stroke rectangle the device actually fills. A
# crushable honeycomb is close to ideal because its force is nearly constant through the crush; a
# hydraulic damper is not, because its force follows the velocity and falls as the vehicle stops.
ABSORBER_EFFICIENCY = {
    'crushableHoneycomb': {'efficiency': 0.80, 'reusable': False,
                           'note': 'flat force-stroke curve, replaced after every landing'},
    'crushableAluminium': {'efficiency': 0.70, 'reusable': False,
                           'note': 'cheaper and less uniform than honeycomb'},
    'hydraulicDamper':    {'efficiency': 0.55, 'reusable': True,
                           'note': 'force falls as the vehicle slows, so the rectangle is poorly filled'},
    'pneumaticStrut':     {'efficiency': 0.45, 'reusable': True,
                           'note': 'springs back, which is a rebound problem as well as an efficiency one'},
}

# A tipover margin below this is treated as no margin at all. The vehicle is on uneven ground, in
# wind, with a residual horizontal rate, and none of that is in the static calculation.
MINIMUM_TIPOVER_MARGIN = 1.0    # [deg]

# ------------------------------------------------------------------------------------------------ #
# -- LandingLoads -- #
# ------------------------------------------------------------------------------------------------ #

class LandingLoads:

    '''

    Touchdown load factor from sink rate and stroke, absorber comparison, and tipover margin.

    '''

    def __init__(self):

        self.landedMass       = np.nan
        self.sinkRate         = np.nan
        self.horizontalRate   = np.nan
        self.stroke           = np.nan
        self.absorber         = ''
        self.legCount         = np.nan
        self.footprintRadius  = np.nan
        self.centreOfGravity  = np.nan
        self.groundSlope      = np.nan
        self.limitLoadFactor  = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `sinkRate` is the vertical velocity at contact [m/s] and `stroke` the usable absorber
        travel [m]. `absorber` is a key of ABSORBER_EFFICIENCY.

        `footprintRadius` is the distance from the vehicle axis to a leg foot [m] and
        `centreOfGravity` is the height of the centre of gravity above the feet [m]. Those two set
        the tipover geometry and nothing else does.

        `limitLoadFactor` is what the structure is designed to, which turns a load calculation into
        a verdict.

        '''

        requiredParams = {'landedMass': (int, float),
                          'sinkRate':   (int, float),
                          'stroke':     (int, float)}

        optionalParams = {'absorber':        str,
                          'legCount':        (int, float),
                          'horizontalRate':  (int, float),
                          'footprintRadius': (int, float),
                          'centreOfGravity': (int, float),
                          'groundSlope':     (int, float),
                          'limitLoadFactor': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not self.absorber:
            self.absorber = 'crushableHoneycomb'

        if not np.isfinite(self.legCount):
            self.legCount = 4

        for attribute in ('horizontalRate', 'groundSlope'):
            if not np.isfinite(getattr(self, attribute)):
                setattr(self, attribute, 0.0)

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateLoadFactor(self, absorber: str = None, stroke: float = None) -> dict:

        '''

        Touchdown load factor from the energy balance.

        The kinetic energy at contact is absorbed over the stroke at a force the absorber can
        sustain. The plus one is the vehicle's own weight, which the legs carry after the motion
        stops and which a purely kinetic form leaves out.

        '''

        name = absorber if absorber else self.absorber
        travel = stroke if stroke is not None else self.stroke

        efficiency = ABSORBER_EFFICIENCY[name]['efficiency']

        loadFactor = self.sinkRate ** 2 / (2.0 * GRAVITY * travel * efficiency) + 1.0

        force = loadFactor * self.landedMass * GRAVITY
        energy = 0.5 * self.landedMass * self.sinkRate ** 2

        result = {'absorber':      name,
                  'efficiency':    efficiency,
                  'stroke':        travel,
                  'loadFactor':    loadFactor,
                  'totalForce':    force,
                  'forcePerLeg':   force / self.legCount,
                  'kineticEnergy': energy,
                  'energyPerLeg':  energy / self.legCount,
                  'reusable':      ABSORBER_EFFICIENCY[name]['reusable']}

        if np.isfinite(self.limitLoadFactor):

            result['limitLoadFactor'] = self.limitLoadFactor
            result['margin'] = self.limitLoadFactor / loadFactor - 1.0

            if loadFactor > self.limitLoadFactor:
                raise LandingError(
                    f'Touchdown at {self.sinkRate:.1f} m/s over {travel * 1000.0:.0f} mm of '
                    f'{name} gives {loadFactor:.1f} g against a structural limit of '
                    f'{self.limitLoadFactor:.1f}. The stroke is the cheap variable here: the load '
                    f'factor is inversely proportional to it.',
                    context = {'sinkRate':        self.sinkRate,
                               'stroke':          travel,
                               'absorber':        name,
                               'loadFactor':      loadFactor,
                               'limitLoadFactor': self.limitLoadFactor})

        return result

    # -------------------------------------------------------------------------------------------- #

    def requiredStroke(self, targetLoadFactor: float, absorber: str = None) -> dict:

        '''

        Invert the load factor for the stroke a target needs.

        This is the form a leg is actually designed in: the structure sets the load factor and the
        leg has to deliver the stroke that produces it.

        '''

        name = absorber if absorber else self.absorber
        efficiency = ABSORBER_EFFICIENCY[name]['efficiency']

        if targetLoadFactor <= 1.0:
            raise LandingError('A target load factor at or below one is a vehicle that never '
                               'stops. The plus one is its own weight.')

        stroke = self.sinkRate ** 2 / (2.0 * GRAVITY * (targetLoadFactor - 1.0) * efficiency)

        return {'targetLoadFactor': targetLoadFactor,
                'absorber':         name,
                'requiredStroke':   stroke,
                'availableStroke':  self.stroke,
                'sufficient':       self.stroke >= stroke}

    # -------------------------------------------------------------------------------------------- #

    def compareAbsorbers(self) -> dict:

        '''

        Every absorber at the same stroke and sink rate.

        The reusable ones are less efficient, so they need more stroke for the same load factor.
        That is the cost of not replacing the absorber after every landing, and on a vehicle
        designed for many flights it is worth paying.

        '''

        results = []

        for name in ABSORBER_EFFICIENCY:

            # The limit check is deliberately bypassed here, because the point of the comparison is
            # to show which options fail it.
            efficiency = ABSORBER_EFFICIENCY[name]['efficiency']
            loadFactor = self.sinkRate ** 2 / (2.0 * GRAVITY * self.stroke * efficiency) + 1.0

            results.append({'absorber':     name,
                            'efficiency':   efficiency,
                            'loadFactor':   loadFactor,
                            'reusable':     ABSORBER_EFFICIENCY[name]['reusable'],
                            'strokeForBaseline': (self.stroke
                                                  * ABSORBER_EFFICIENCY['crushableHoneycomb']['efficiency']
                                                  / efficiency)})

        results.sort(key = lambda entry: entry['loadFactor'])

        reusable = [entry for entry in results if entry['reusable']]
        singleUse = [entry for entry in results if not entry['reusable']]

        return {'results':      results,
                'bestOverall':  results[0]['absorber'],
                'bestReusable': reusable[0]['absorber'] if reusable else None,
                'reuseCost':    (reusable[0]['loadFactor'] / singleUse[0]['loadFactor']
                                 if reusable and singleUse else np.nan)}

    # -------------------------------------------------------------------------------------------- #

    def calculateTipover(self) -> dict:

        '''

        Static tipover margin, and what the flight conditions take out of it.

        The vehicle tips if the resultant of its weight and its horizontal momentum falls outside
        the leg footprint. The static angle is atan(footprint / cg height); the ground slope
        subtracts from it directly, and the horizontal rate subtracts an equivalent angle through
        the energy it has to be absorbed over.

        '''

        if not (np.isfinite(self.footprintRadius) and np.isfinite(self.centreOfGravity)):
            raise LandingError('Tipover needs both the footprint radius and the centre of gravity '
                               'height. Neither has a sensible default: they are the whole '
                               'calculation.')

        staticAngle = np.degrees(np.arctan2(self.footprintRadius, self.centreOfGravity))

        # The horizontal rate has to be arrested by the leg friction and structure, and while it is
        # the vehicle rotates. The equivalent angle is the rotation the horizontal kinetic energy
        # would produce against the potential energy of lifting the centre of gravity to the tip.
        raised = np.sqrt(self.footprintRadius ** 2 + self.centreOfGravity ** 2) - self.centreOfGravity
        tipEnergy = self.landedMass * GRAVITY * raised
        horizontalEnergy = 0.5 * self.landedMass * self.horizontalRate ** 2

        energyRatio = horizontalEnergy / tipEnergy if tipEnergy > 0.0 else np.inf
        horizontalAngle = staticAngle * min(1.0, energyRatio)

        margin = staticAngle - self.groundSlope - horizontalAngle

        result = {'staticAngle':      staticAngle,
                  'groundSlope':      self.groundSlope,
                  'horizontalAngle':  horizontalAngle,
                  'energyRatio':      energyRatio,
                  'margin':           margin,
                  'tipEnergy':        tipEnergy,
                  'horizontalEnergy': horizontalEnergy}

        if margin <= MINIMUM_TIPOVER_MARGIN:
            raise LandingError(
                f'Tipover margin is {margin:.1f} degrees against a static angle of '
                f'{staticAngle:.1f}, after {self.groundSlope:.1f} for slope and '
                f'{horizontalAngle:.1f} for a horizontal rate of {self.horizontalRate:.1f} m/s. '
                f'A vehicle that tips over is lost rather than degraded, so this is raised rather '
                f'than reported.',
                context = {'footprintRadius': self.footprintRadius,
                           'centreOfGravity': self.centreOfGravity,
                           'horizontalRate':  self.horizontalRate,
                           'groundSlope':     self.groundSlope})

        return result

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        The load factor, the absorber comparison, and the tipover margin if the geometry is given.
        '''

        loads = self.calculateLoadFactor()
        comparison = self.compareAbsorbers()

        lines = []

        lines.append(formatReportTable(
            [[f'{self.sinkRate:.1f}',
              f'{self.stroke * 1000.0:.0f}',
              f'{loads["efficiency"]:.2f}',
              f'{loads["loadFactor"]:.1f}',
              f'{loads["forcePerLeg"] / 1000.0:,.0f}']],
            ['sink [m/s]', 'stroke [mm]', 'efficiency', 'load factor', 'force per leg [kN]'],
            title = f'TOUCHDOWN, {self.absorber.upper()}'))

        lines.append('')

        lines.append(formatReportTable(
            [[entry['absorber'],
              f'{entry["efficiency"]:.2f}',
              f'{entry["loadFactor"]:.1f}',
              'yes' if entry['reusable'] else '',
              f'{entry["strokeForBaseline"] * 1000.0:.0f}'] for entry in comparison['results']],
            ['absorber', 'efficiency', 'load factor', 'reusable', 'stroke for baseline [mm]'],
            title = 'ABSORBERS'))

        if np.isfinite(self.footprintRadius) and np.isfinite(self.centreOfGravity):

            lines.append('')

            try:
                tipover = self.calculateTipover()
                lines.append(f'Tipover margin {tipover["margin"]:.1f} deg from a static '
                             f'{tipover["staticAngle"]:.1f}, after slope and horizontal rate.')
            except LandingError as error:
                lines.append('TIPOVER CHECK FAILED')
                lines.append(str(error))

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'landingLoads.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if self.absorber not in ABSORBER_EFFICIENCY:
            raise InvalidInputError(
                f'{self.absorber} is not an absorber type. Available: '
                f'{sorted(ABSORBER_EFFICIENCY)}.')

        if not np.isfinite(self.landedMass) or self.landedMass <= 0.0:
            raise InvalidInputError('Landed mass must be positive.')

        if not np.isfinite(self.sinkRate) or self.sinkRate <= 0.0:
            raise InvalidInputError('Sink rate must be positive. A vehicle that arrives with zero '
                                    'vertical velocity has already landed.')

        if not np.isfinite(self.stroke) or self.stroke <= 0.0:
            raise InvalidInputError('Stroke must be positive.')

        if int(self.legCount) < 3:
            raise InvalidInputError('Fewer than three legs is not a stable footprint.')

        if self.horizontalRate < 0.0:
            raise InvalidInputError('Horizontal rate is a magnitude and cannot be negative.')

        if not 0.0 <= self.groundSlope < 90.0:
            raise InvalidInputError('Ground slope must lie between zero and ninety degrees.')
