
# -- EntryTrajectory -- #

'''

The entry environment in closed form, and the one result everybody expects to be wrong.

Allen and Eggers solved ballistic entry into an exponential atmosphere in 1958. Assume a constant
flight path angle, no lift, and drag balancing nothing else, and the velocity against density is

    V(rho) = V_e * exp( -rho * H / (2 * beta * sin|gamma|) )

Differentiating that gives every peak in the entry, and the peaks have a property worth stating
before any of the numbers.

**Peak deceleration is independent of the ballistic coefficient.**

    a_max = V_e**2 * sin|gamma| / (2 * e * H)

A dense slender body and a light blunt one, entering at the same speed on the same path angle, pull
the same maximum g. The heavy one does it lower down and later, and that is the whole of the
difference. **The vehicle does not appear in the equation at all**, only the entry state and the
atmosphere.

What the ballistic coefficient does change is the heating.

    q_max  ~ sqrt( beta * sin|gamma| )        peak rate rises with beta AND with steepness
    Q_total ~ sqrt( beta / sin|gamma| )       total load rises with beta and FALLS with steepness

**So flight path angle trades peak rate against total load in opposite directions**, and that is the
entry design trade: peak rate selects the thermal protection material, total load sets its
thickness. A steep entry needs a material that survives a high flux and not much of it. A shallow
one needs a lot of a cheaper material.

**And peak heating happens before peak deceleration**, at 0.846 of the entry velocity against 0.607,
roughly ten per cent higher in altitude. The structure and the thermal protection are not designed
by the same instant.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from recoveryUtils import (ATMOSPHERIC_SCALE_HEIGHT, SEA_LEVEL_DENSITY,
                               PEAK_DECELERATION_VELOCITY_FRACTION,
                               PEAK_HEATING_VELOCITY_FRACTION,
                               SUTTON_GRAVES_CONSTANT, WATT_PER_M2_TO_WATT_PER_CM2,
                               GRAVITY,
                               ballisticCoefficient, suttonGravesHeatFlux, altitudeFromDensity,
                               applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, EntryError)
except ImportError:
    from .recoveryUtils import (ATMOSPHERIC_SCALE_HEIGHT, SEA_LEVEL_DENSITY,
                                PEAK_DECELERATION_VELOCITY_FRACTION,
                                PEAK_HEATING_VELOCITY_FRACTION,
                                SUTTON_GRAVES_CONSTANT, WATT_PER_M2_TO_WATT_PER_CM2,
                                GRAVITY,
                                ballisticCoefficient, suttonGravesHeatFlux, altitudeFromDensity,
                                applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, EntryError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Below this the ballistic assumption stops meaning anything, because a nearly horizontal entry is
# a glide and the constant flight path angle the solution assumes is the first thing to go.
MINIMUM_FLIGHT_PATH_ANGLE = 1.0     # [deg]

# ------------------------------------------------------------------------------------------------ #
# -- EntryTrajectory -- #
# ------------------------------------------------------------------------------------------------ #

class EntryTrajectory:

    '''

    Allen-Eggers ballistic entry: the peaks, where they happen, and what each depends on.

    '''

    def __init__(self):

        self.entryVelocity   = np.nan
        self.flightPathAngle = np.nan
        self.mass            = np.nan
        self.dragCoefficient = np.nan
        self.referenceArea   = np.nan
        self.noseRadius      = np.nan
        self.scaleHeight     = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `entryVelocity` is the speed at the atmospheric interface [m/s] and `flightPathAngle` is
        the angle below the local horizontal [deg], positive.

        `mass`, `dragCoefficient` and `referenceArea` set the ballistic coefficient.
        `noseRadius` is the effective stagnation point radius [m], which appears only in the
        heating and not in the trajectory.

        `scaleHeight` defaults to a 7,200 m exponential fit. The solution is only as good as it,
        which is stated rather than hidden.

        '''

        requiredParams = {'entryVelocity':   (int, float),
                          'flightPathAngle': (int, float),
                          'mass':            (int, float),
                          'dragCoefficient': (int, float),
                          'referenceArea':   (int, float)}

        optionalParams = {'noseRadius':  (int, float),
                          'scaleHeight': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.scaleHeight):
            self.scaleHeight = ATMOSPHERIC_SCALE_HEIGHT

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def ballisticCoefficient(self) -> float:

        '''
        beta = m / (Cd A), the one vehicle number the trajectory depends on.
        '''

        return ballisticCoefficient(self.mass, self.dragCoefficient, self.referenceArea)

    # -------------------------------------------------------------------------------------------- #

    def calculatePeakDeceleration(self) -> dict:

        '''

        The maximum deceleration, where it happens, and the demonstration that the vehicle is not
        in the answer.

        a_max = V_e**2 sin|gamma| / (2 e H), at V = V_e / sqrt(e) and rho = beta sin|gamma| / H.

        '''

        angle = np.radians(self.flightPathAngle)
        beta = self.ballisticCoefficient()

        peak = (self.entryVelocity ** 2 * np.sin(angle)
                / (2.0 * np.e * self.scaleHeight))

        density = beta * np.sin(angle) / self.scaleHeight
        velocity = self.entryVelocity * PEAK_DECELERATION_VELOCITY_FRACTION

        return {'peakDeceleration':   peak,
                'peakLoadFactor':     peak / GRAVITY,
                'atVelocity':         velocity,
                'atDensity':          density,
                'atAltitude':         altitudeFromDensity(density),
                'ballisticCoefficient': beta,
                'velocityFraction':   PEAK_DECELERATION_VELOCITY_FRACTION}

    # -------------------------------------------------------------------------------------------- #

    def calculatePeakHeating(self) -> dict:

        '''

        The maximum stagnation point heat flux, where it happens, and the total heat load.

        Peak flux is at rho = beta sin|gamma| / (3 H) and V = V_e exp(-1/6), which is earlier and
        higher than peak deceleration. The total load comes from integrating the flux over the
        entry, which has a closed form:

            Q = k V_e**2 sqrt( pi beta H / (Rn sin|gamma|) )

        '''

        if not np.isfinite(self.noseRadius):
            raise EntryError('A nose radius is needed for the heating calculation. It does not '
                             'appear in the trajectory, only in the stagnation point flux.')

        angle = np.radians(self.flightPathAngle)
        beta = self.ballisticCoefficient()

        density = beta * np.sin(angle) / (3.0 * self.scaleHeight)
        velocity = self.entryVelocity * PEAK_HEATING_VELOCITY_FRACTION

        flux = suttonGravesHeatFlux(density, self.noseRadius, velocity)

        # The heat load integral over an exponential atmosphere. The integrand is
        # rho**(-1/2) exp(-a rho), whose integral from zero to infinity is sqrt(pi / a).
        load = (SUTTON_GRAVES_CONSTANT * self.entryVelocity ** 2
                * np.sqrt(np.pi * beta * self.scaleHeight
                          / (self.noseRadius * np.sin(angle))))

        deceleration = self.calculatePeakDeceleration()
        altitude = altitudeFromDensity(density)

        # Peak heating sits exactly H ln(3) above peak deceleration, because the two peak densities
        # differ by a factor of three and altitude is logarithmic in density.
        #
        # **The separation is the invariant, not the ratio.** Sources that quote the altitude ratio
        # as about 1.1 are quoting it for an orbital entry, where the deceleration peak is high
        # enough that 7.9 km is a tenth of it. On a booster returning from a lofted suborbital
        # trajectory the peaks are much lower and the same 7.9 km is half the altitude again.
        separation = self.scaleHeight * np.log(3.0)

        return {'peakHeatFlux':      flux,
                'peakHeatFluxWattPerCm2': flux * WATT_PER_M2_TO_WATT_PER_CM2,
                'heatLoad':          load,
                'heatLoadJoulePerCm2': load * WATT_PER_M2_TO_WATT_PER_CM2,
                'atVelocity':        velocity,
                'atDensity':         density,
                'atAltitude':        altitude,
                'velocityFraction':  PEAK_HEATING_VELOCITY_FRACTION,
                'altitudeSeparation': separation,
                'altitudeRatio':     altitude / deceleration['atAltitude'],
                'aheadOfDeceleration': bool(altitude > deceleration['atAltitude'])}

    # -------------------------------------------------------------------------------------------- #

    def compareBallisticCoefficients(self, factors: list = None) -> dict:

        '''

        The same entry state at several ballistic coefficients.

        The point of the table is what does NOT move. Peak deceleration is identical down the
        column, and everything else changes.

        '''

        if factors is None:
            factors = [0.25, 0.5, 1.0, 2.0, 4.0]

        original = self.mass
        results = []

        try:
            for factor in factors:

                self.mass = original * factor

                deceleration = self.calculatePeakDeceleration()
                heating = self.calculatePeakHeating()

                results.append({'factor':               factor,
                                'ballisticCoefficient': deceleration['ballisticCoefficient'],
                                'peakLoadFactor':       deceleration['peakLoadFactor'],
                                'decelerationAltitude': deceleration['atAltitude'],
                                'peakHeatFlux':         heating['peakHeatFluxWattPerCm2'],
                                'heatLoad':             heating['heatLoadJoulePerCm2']})
        finally:
            self.mass = original

        loadFactors = [entry['peakLoadFactor'] for entry in results]
        fluxes = [entry['peakHeatFlux'] for entry in results]

        return {'results':          results,
                'loadFactorSpread': max(loadFactors) / min(loadFactors),
                'heatFluxSpread':   max(fluxes) / min(fluxes),
                'decelerationIsInvariant': bool(np.allclose(loadFactors, loadFactors[0]))}

    # -------------------------------------------------------------------------------------------- #

    def compareFlightPathAngles(self, angles: list = None) -> dict:

        '''

        The entry corridor, and the trade it contains.

        Steeper raises the peak rate and lowers the total load. Shallower does the reverse. There
        is no angle that improves both, which is why the corridor is a choice rather than an
        optimum.

        '''

        if angles is None:
            angles = [2.0, 5.0, 10.0, 20.0, 40.0]

        original = self.flightPathAngle
        results = []

        try:
            for angle in angles:

                self.flightPathAngle = angle

                deceleration = self.calculatePeakDeceleration()
                heating = self.calculatePeakHeating()

                results.append({'flightPathAngle': angle,
                                'peakLoadFactor':  deceleration['peakLoadFactor'],
                                'peakHeatFlux':    heating['peakHeatFluxWattPerCm2'],
                                'heatLoad':        heating['heatLoadJoulePerCm2']})
        finally:
            self.flightPathAngle = original

        steepest = results[-1]
        shallowest = results[0]

        return {'results':        results,
                'fluxRatio':      steepest['peakHeatFlux'] / shallowest['peakHeatFlux'],
                'loadRatio':      steepest['heatLoad'] / shallowest['heatLoad'],
                'tradeIsOpposed': bool(steepest['peakHeatFlux'] > shallowest['peakHeatFlux']
                                       and steepest['heatLoad'] < shallowest['heatLoad'])}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''

        The peaks, and the two comparisons that carry the argument.

        '''

        deceleration = self.calculatePeakDeceleration()
        heating = self.calculatePeakHeating()

        lines = []

        lines.append(formatReportTable(
            [['peak deceleration',
              f'{deceleration["peakLoadFactor"]:.1f} g',
              f'{deceleration["atVelocity"]:,.0f}',
              f'{deceleration["atAltitude"] / 1000.0:.1f}'],
             ['peak heat flux',
              f'{heating["peakHeatFluxWattPerCm2"]:.0f} W/cm2',
              f'{heating["atVelocity"]:,.0f}',
              f'{heating["atAltitude"] / 1000.0:.1f}']],
            ['event', 'magnitude', 'at [m/s]', 'altitude [km]'],
            title = 'ENTRY PEAKS'))

        lines.append('')
        lines.append(f'Ballistic coefficient {deceleration["ballisticCoefficient"]:,.0f} kg/m2, '
                     f'total heat load {heating["heatLoadJoulePerCm2"]:,.0f} J/cm2.')
        lines.append('')

        beta = self.compareBallisticCoefficients()

        lines.append(formatReportTable(
            [[f'{entry["factor"]:.2f}',
              f'{entry["ballisticCoefficient"]:,.0f}',
              f'{entry["peakLoadFactor"]:.1f}',
              f'{entry["peakHeatFlux"]:.0f}',
              f'{entry["heatLoad"]:,.0f}'] for entry in beta['results']],
            ['mass factor', 'beta [kg/m2]', 'peak g', 'peak [W/cm2]', 'load [J/cm2]'],
            title = 'BALLISTIC COEFFICIENT'))

        lines.append('')
        lines.append('Peak deceleration does not move. The heating does.')

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'entryTrajectory.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        if not np.isfinite(self.entryVelocity) or self.entryVelocity <= 0.0:
            raise InvalidInputError('Entry velocity must be positive.')

        if not np.isfinite(self.flightPathAngle):
            raise InvalidInputError('A flight path angle is required.')

        if self.flightPathAngle >= 90.0:
            raise EntryError('A flight path angle of 90 degrees or more is a vertical entry or a '
                             'climb. The solution assumes a constant angle below the horizontal.')

        if self.flightPathAngle < MINIMUM_FLIGHT_PATH_ANGLE:
            raise EntryError(
                f'A flight path angle of {self.flightPathAngle:.2f} degrees is a glide rather than '
                f'a ballistic entry. The Allen-Eggers solution assumes the angle stays constant, '
                f'and near the horizontal it does not: lift and the curvature of the planet both '
                f'become first order.',
                context = {'flightPathAngle': self.flightPathAngle,
                           'minimum':         MINIMUM_FLIGHT_PATH_ANGLE})

        if self.mass <= 0.0 or self.dragCoefficient <= 0.0 or self.referenceArea <= 0.0:
            raise InvalidInputError('Mass, drag coefficient and reference area must be positive.')

        if np.isfinite(self.noseRadius) and self.noseRadius <= 0.0:
            raise InvalidInputError('Nose radius must be positive where it is given.')

        if self.scaleHeight <= 0.0:
            raise InvalidInputError('Scale height must be positive.')
