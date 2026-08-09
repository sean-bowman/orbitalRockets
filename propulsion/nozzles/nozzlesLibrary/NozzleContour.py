
# -- NozzleContour -- #

'''

A conceptual-fidelity bell contour by Rao's parabolic approximation.

**This is not a method of characteristics solution and it does not pretend to be.** The NOVA suite
generates axisymmetric method of characteristics isentropic contours and the cooling channel
geometry that follows them, and nothing here approaches that fidelity.

What this class is for is the stage before that. A conceptual design needs a wall angle, a length
and a surface area before anyone runs a characteristics solution, and those three quantities feed
the loss decomposition, the cooling area and the mass estimate. Rao's approximation gives them from
an area ratio and a length fraction, in closed form, and it is the standard conceptual-design method
for exactly this reason.

The two fidelities do not overlap and they answer different questions. This one answers "roughly
what shape and how much area"; NOVA answers "what are the coordinates".

**It also removed a lookup table that was wrong.** An earlier version of this sub-domain carried
tabulated exit angles, with an 80 per cent bell fixed at 8 degrees regardless of area ratio. Rao
gives 11.5 degrees at an area ratio of 20, and the difference doubles the divergence loss. See
`exitAngle`.

Author: Sean Bowman
Date:   09/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from nozzleUtils import (divergenceEfficiency, applyInputs, formatReportTable,
                             createErrorContext, InvalidInputError, ContourError)
except ImportError:
    from .nozzleUtils import (divergenceEfficiency, applyInputs, formatReportTable,
                              createErrorContext, InvalidInputError, ContourError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Rao's wall angles for an 80 per cent bell, fitted against area ratio in logarithm.
#
#     theta_n = 24.317 + 2.623 ln(eps)      the initial wall angle just downstream of the throat
#     theta_e = 19.433 - 2.623 ln(eps)      the exit wall angle
#
# The fit reproduces the published Rao values to within 0.4 degrees between area ratios of 10 and
# 100, which is the range a launch vehicle nozzle occupies. It is a fit to published design data
# rather than a derivation, and it is registered as such.
#
# The two angles move in opposite directions with area ratio, which is the geometric heart of a bell:
# a larger expansion turns the flow harder at the throat and has further to turn it back by the exit.
RAO_INITIAL_INTERCEPT = 24.317    # [degrees]
RAO_INITIAL_SLOPE     = 2.623     # [degrees]
RAO_EXIT_INTERCEPT    = 19.433    # [degrees]
RAO_EXIT_SLOPE        = -2.623    # [degrees]

# Reference length fraction the fit was taken at. A shorter bell turns the flow harder at the throat
# and leaves at a steeper angle, and both effects scale roughly with the inverse of the length.
RAO_REFERENCE_LENGTH_FRACTION = 0.80    # [-]

# The throat downstream arc radius, as a multiple of throat radius. Rao's construction uses 0.382,
# and it sets where the parabola begins.
THROAT_ARC_RADIUS_RATIO = 0.382    # [-]

# The conical half angle a bell length is quoted against.
REFERENCE_CONE_HALF_ANGLE = 15.0    # [degrees]

# Points used to integrate the contour for length and surface area.
INTEGRATION_POINTS = 200    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- NozzleContour -- #
# ------------------------------------------------------------------------------------------------ #

class NozzleContour:

    '''

    Wall angles, length and surface area for a Rao parabolic bell at conceptual fidelity.

    '''

    def __init__(self):

        self.throatRadius   = np.nan
        self.areaRatio      = np.nan
        self.lengthFraction = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `lengthFraction` is the bell length as a fraction of a 15 degree cone of the same area
        ratio, which is how bells are universally quoted.

        '''

        requiredParams = {'throatRadius': (int, float),
                          'areaRatio':    (int, float)}

        optionalParams = {'lengthFraction': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.lengthFraction):
            self.lengthFraction = RAO_REFERENCE_LENGTH_FRACTION

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def exitRadius(self) -> float:

        return self.throatRadius * np.sqrt(self.areaRatio)

    def conicalLength(self) -> float:

        '''
        The length of a 15 degree cone of the same area ratio, which the bell length is quoted
        against.
        '''

        return ((self.exitRadius() - self.throatRadius)
                / np.tan(np.radians(REFERENCE_CONE_HALF_ANGLE)))

    def length(self) -> float:

        return self.lengthFraction * self.conicalLength()

    # -------------------------------------------------------------------------------------------- #

    def wallAngles(self) -> dict:

        '''

        The initial and exit wall angles from Rao's approximation.

        The length correction is the part worth explaining. The published fit is for an 80 per cent
        bell. A shorter bell has to turn the flow harder at the throat and cannot turn it as far
        back by the exit, so both angles rise, and they rise roughly with the inverse of the length
        fraction.

        A 60 per cent bell therefore leaves at a steeper angle than an 80 per cent one, which is
        precisely the divergence loss that a shorter nozzle trades against its lower wall friction.

        '''

        logRatio = np.log(self.areaRatio)

        initial = RAO_INITIAL_INTERCEPT + RAO_INITIAL_SLOPE * logRatio
        exit_   = RAO_EXIT_INTERCEPT + RAO_EXIT_SLOPE * logRatio

        correction = RAO_REFERENCE_LENGTH_FRACTION / self.lengthFraction

        initial *= correction
        exit_   *= correction

        # The correction multiplies both angles, so it cannot reverse their order: the exit angle is
        # below the initial angle for every area ratio above one. A guard on that ordering would
        # never fire, and a guard that never fires is worse than none because it reads as a handled
        # failure mode. The reachable failure is the initial angle itself running away.
        if initial >= 90.0:
            raise ContourError(
                f'The initial wall angle comes out at {initial:.1f} degrees, which turns the wall '
                f'past radial and is not a nozzle. An area ratio of {self.areaRatio:.1f} at a '
                f'length fraction of {self.lengthFraction:.2f} is far outside the range Rao\'s fit '
                f'covers, and the correction has extrapolated it into nonsense rather than merely '
                f'losing accuracy.',
                context = createErrorContext(component = 'NozzleContour'))

        return {'initialAngle':   initial,
                'exitAngle':      exit_,
                'turning':        initial - exit_,
                'lengthCorrection': correction}

    # -------------------------------------------------------------------------------------------- #

    def exitAngle(self) -> float:

        '''

        The exit wall angle, which is the number the divergence loss is computed from.

        This is the method that replaced a lookup table. The table gave an 80 per cent bell an exit
        angle of 8 degrees regardless of area ratio, and Rao gives 11.5 at an area ratio of 20.
        The divergence efficiency at 8 degrees is 0.9951 and at the angle Rao gives it is 0.9899,
        so the table understated the divergence loss by a factor of two.

        '''

        return self.wallAngles()['exitAngle']

    # -------------------------------------------------------------------------------------------- #

    def coordinates(self) -> dict:

        '''

        The contour, as a throat arc followed by a parabola.

        Rao's construction is a circular arc from the throat through the initial wall angle, then a
        parabola from there to the exit meeting the exit angle. The parabola is fitted to the two
        end points and the two slopes, which determines it uniquely.

        These coordinates are for area and length, not for manufacture. A contour for manufacture
        comes from NOVA.

        '''

        angles = self.wallAngles()

        throatRadius = self.throatRadius
        exitRadius   = self.exitRadius()

        arcRadius = THROAT_ARC_RADIUS_RATIO * throatRadius

        initial = np.radians(angles['initialAngle'])
        exit_   = np.radians(angles['exitAngle'])

        # the arc runs from the throat to the initial wall angle
        arcAngles = np.linspace(0.0, initial, INTEGRATION_POINTS // 4)

        arcAxial  = arcRadius * np.sin(arcAngles)
        arcRadial = throatRadius + arcRadius * (1.0 - np.cos(arcAngles))

        startAxial  = float(arcAxial[-1])
        startRadial = float(arcRadial[-1])

        totalLength = self.length()

        if totalLength <= startAxial:
            raise ContourError(
                f'The bell length {totalLength * 1000.0:.1f} mm is shorter than the throat arc '
                f'alone at {startAxial * 1000.0:.1f} mm. The length fraction is too small for this '
                f'area ratio.',
                context = createErrorContext(component = 'NozzleContour'))

        # a parabola in axial distance, fitted to both end points and both slopes
        span = totalLength - startAxial

        axial = np.linspace(startAxial, totalLength, INTEGRATION_POINTS)

        fraction = (axial - startAxial) / span

        startSlope = np.tan(initial)
        endSlope   = np.tan(exit_)

        # radius from a quadratic whose slope goes linearly from startSlope to endSlope
        radial = (startRadial
                  + span * (startSlope * fraction
                            + 0.5 * (endSlope - startSlope) * fraction ** 2))

        # scale so the exit radius comes out exactly right, which the two-slope fit does not
        # guarantee for an arbitrary length fraction
        scale = (exitRadius - startRadial) / (radial[-1] - startRadial)

        radial = startRadial + (radial - startRadial) * scale

        # the parabola starts where the arc ends, so its first point is the arc's last one and is
        # dropped; leaving it in puts a zero length segment at the junction, which is harmless in
        # the area integral and not harmless to anything that differentiates the contour
        return {'axial':  np.concatenate([arcAxial, axial[1:]]),
                'radial': np.concatenate([arcRadial, radial[1:]]),
                'arcEndAxial':  startAxial,
                'arcEndRadial': startRadial,
                'exitRadius':   exitRadius,
                'length':       totalLength}

    # -------------------------------------------------------------------------------------------- #

    def surfaceArea(self) -> dict:

        '''

        Wetted area by integrating the contour, and the cone frustum approximation it replaces.

        The frustum approximation treats the bell as a straight cone from throat to exit. A real
        bell bulges outward, so it has more area than the cone, and the difference matters because
        that area carries the cooling load. See combustionDevices, which used the frustum.

        '''

        findings = []

        contour = self.coordinates()

        axial  = contour['axial']
        radial = contour['radial']

        segments = np.sqrt(np.diff(axial) ** 2 + np.diff(radial) ** 2)
        meanRadii = 0.5 * (radial[:-1] + radial[1:])

        area = float(np.sum(2.0 * np.pi * meanRadii * segments))

        exitRadius = self.exitRadius()
        length     = self.length()

        frustum = (np.pi * (self.throatRadius + exitRadius)
                   * np.sqrt(length ** 2 + (exitRadius - self.throatRadius) ** 2))

        findings.append(
            f'Integrated wetted area {area * 1.0e4:.0f} cm^2 against a cone frustum estimate of '
            f'{frustum * 1.0e4:.0f} cm^2, a ratio of {area / frustum:.3f}.')

        findings.append(
            'A bell bulges outward from the straight line between throat and exit, so it has more '
            'wetted area than a frustum. That area carries the cooling load, which is where the '
            'difference is felt.')

        self.findings = findings

        return {'area':          area,
                'frustumArea':   frustum,
                'ratio':         area / frustum,
                'length':        length,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full contour report.
        '''

        angles = self.wallAngles()
        area   = self.surfaceArea()

        divergence = divergenceEfficiency(angles['exitAngle'])

        lines = []
        lines.append('=' * 96)
        lines.append(f'  NOZZLE CONTOUR: Rao parabolic, area ratio {self.areaRatio:.2f}, '
                     f'{self.lengthFraction:.0%} bell')
        lines.append('=' * 96)
        lines.append('')
        lines.append('  Conceptual fidelity. A contour for manufacture comes from the NOVA suite.')
        lines.append('')

        lines.append(formatReportTable(
            [['Throat radius',      f'{self.throatRadius * 1000.0:.1f}',        'mm'],
             ['Exit radius',        f'{self.exitRadius() * 1000.0:.1f}',        'mm'],
             ['Cone length',        f'{self.conicalLength() * 1000.0:.1f}',     'mm'],
             ['Bell length',        f'{self.length() * 1000.0:.1f}',            'mm'],
             ['Initial wall angle', f'{angles["initialAngle"]:.1f}',            'degrees'],
             ['Exit wall angle',    f'{angles["exitAngle"]:.1f}',               'degrees'],
             ['Turning',            f'{angles["turning"]:.1f}',                 'degrees'],
             ['Divergence efficiency', f'{divergence:.4f}',                     ''],
             ['Wetted area',        f'{area["area"] * 1.0e4:.0f}',              'cm^2'],
             ['Frustum estimate',   f'{area["frustumArea"] * 1.0e4:.0f}',       'cm^2'],
             ['Ratio',              f'{area["ratio"]:.3f}',                     '']],
            ['Quantity', 'Value', 'Unit'], title = 'Contour'))

        lines.append('')
        for finding in area['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'nozzle_contour.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if self.throatRadius <= 0.0:
            raise InvalidInputError(
                f'The throat radius must be positive, got {self.throatRadius}.',
                context = createErrorContext(component = 'NozzleContour'))

        if self.areaRatio <= 1.0:
            raise InvalidInputError(
                f'The area ratio must exceed one, got {self.areaRatio}.',
                context = createErrorContext(component = 'NozzleContour'))

        if not 0.3 <= self.lengthFraction <= 1.2:
            raise ContourError(
                f'The length fraction must lie between 0.3 and 1.2, got {self.lengthFraction}. '
                f'Rao\'s approximation is fitted over roughly 0.6 to 1.0 and extrapolating far '
                f'outside that produces wall angles that are not physical.',
                context = createErrorContext(component = 'NozzleContour'))
