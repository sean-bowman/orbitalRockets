
# -- ModalEstimate Class Definition -- #

'''

First bending, axial and shell modes for beams, cylinders and panels, against a stiffness
requirement.

A launch vehicle has a minimum frequency requirement before it has a strength requirement. The
launch provider states it: the payload and its adapter must have a first lateral mode above some
value, typically 8 to 25 Hz, and a first axial mode above another, typically 15 to 45 Hz. The
purpose is to keep the payload's modes clear of the vehicle's control bandwidth and of the dominant
structural modes, so the coupled loads analysis does not find a resonance.

Meeting a frequency requirement is a stiffness problem, not a strength one, and the two size
structure in different directions:

    frequency   f = (beta^2 / 2 pi) sqrt(E I / (m L^4))
    strength    sigma = M c / I

Frequency goes as the square root of stiffness over mass, so doubling the frequency needs four
times the stiffness at the same mass. A structure sized by strength and then found to be too soft
usually has to grow substantially, which is why the frequency check belongs early.

This class is a preliminary estimate and it says so. Closed-form beam and shell modes are accurate
to perhaps 10 to 20 percent for a uniform structure with idealised boundary conditions, and a real
vehicle is neither uniform nor idealised. The value is in sizing before there is a finite element
model, and in sanity checking one afterwards.

Shell modes are the trap. A thin cylinder's lowest mode is usually not the beam bending mode at
all: it is a shell mode with circumferential waves, and it can sit far below the beam mode. A
structure checked only as a beam can be well above the requirement on paper and below it in test.

See Also:
---------
CylindricalShell : The same shell, checked for stability rather than frequency
BeamColumn       : Section properties, shared with the beam mode calculation

Theory: docs/DynamicsAndModes.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                 InvalidInputError, GeometryError, createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                  InvalidInputError, GeometryError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# beta L values for the first bending mode of a uniform beam, by boundary condition. The frequency
# goes as beta^2, so the boundary assumption moves the answer by a large factor.
BEAM_MODE_FACTORS = {
    'cantilever':        {'betaL': 1.87510, 'note': 'fixed-free. The payload on an adapter'},
    'simply supported':  {'betaL': np.pi,   'note': 'pinned both ends'},
    'fixed-fixed':       {'betaL': 4.73004, 'note': 'clamped both ends'},
    'fixed-pinned':      {'betaL': 3.92660, 'note': ''},
    'free-free':         {'betaL': 4.73004, 'note': 'a vehicle in flight, first elastic mode'},
}

# Axial (longitudinal) mode factors: f = (n / 4L) sqrt(E / rho) for a fixed-free rod, and
# (n / 2L) for fixed-fixed or free-free.
AXIAL_MODE_FACTORS = {
    'cantilever':   0.25,   # [-], quarter wave
    'fixed-fixed':  0.50,   # [-], half wave
    'free-free':    0.50,   # [-],
}

# Typical launch vehicle stiffness requirements, for the report to compare against. These vary by
# provider and are here as representative values, not as a specification.
TYPICAL_REQUIREMENTS = {
    'small launcher':  {'lateral': 8.0,  'axial': 20.0},
    'medium launcher': {'lateral': 10.0, 'axial': 25.0},
    'large launcher':  {'lateral': 15.0, 'axial': 35.0},
    'rideshare':       {'lateral': 25.0, 'axial': 45.0},
}

# Below this the closed-form estimate should not be trusted without a finite element check.
ESTIMATE_ACCURACY = 0.20    # [-], plus or minus, for a uniform idealised structure

# ------------------------------------------------------------------------------------------------ #
# -- ModalEstimate -- #
# ------------------------------------------------------------------------------------------------ #

class ModalEstimate:

    '''

    Preliminary modal frequency estimates.

    Usage:
    ------
        modes = ModalEstimate()
        modes.setInputs({'material': '2219-T87', 'condition': 't87', 'radius': 1.0,
                         'thickness': 0.004, 'length': 6.0, 'boundaryCondition': 'cantilever',
                         'tipMass': 500.0, 'requiredLateral': 10.0})
        result = modes.screenAgainstRequirement()

    '''

    def __init__(self):

        # -- Geometry -- #

        self.radius            = np.nan  # [m], for a cylinder
        self.thickness         = np.nan  # [m]
        self.length            = np.nan  # [m]
        self.area              = np.nan  # [m^2], overrides the cylinder calculation
        self.secondMoment      = np.nan  # [m^4], overrides

        # -- Material -- #

        self.material          = '2219-T87'
        self.condition         = None    # [-]
        self.basis             = 'typical'  # [-]
        self.temperature       = 293.15  # [K]
        self.modulus           = np.nan  # [Pa]
        self.density           = np.nan  # [kg/m^3]
        self.poisson           = 0.33    # [-]

        # -- Configuration -- #

        self.boundaryCondition = 'cantilever'  # key into BEAM_MODE_FACTORS
        self.tipMass           = 0.0     # [kg], concentrated mass at the free end
        self.distributedMass   = 0.0     # [kg], non-structural mass, spread along the length

        # -- Requirement -- #

        self.requiredLateral   = np.nan  # [Hz]
        self.requiredAxial     = np.nan  # [Hz]

        # -- Results -- #

        self.findings          = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: length.

        '''

        requiredParams = {'length': (int, float)}

        optionalParams = {'radius':            (int, float),
                          'thickness':         (int, float),
                          'area':              (int, float),
                          'secondMoment':      (int, float),
                          'material':          str,
                          'condition':         str,
                          'basis':             str,
                          'temperature':       (int, float),
                          'modulus':           (int, float),
                          'density':           (int, float),
                          'poisson':           (int, float),
                          'boundaryCondition': str,
                          'tipMass':           (int, float),
                          'distributedMass':   (int, float),
                          'requiredLateral':   (int, float),
                          'requiredAxial':     (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        properties = structuralAllowables(self.material, self.condition,
                                          temperature = self.temperature, basis = self.basis)

        if not np.isfinite(self.modulus):
            self.modulus = properties['elasticModulus']
        if not np.isfinite(self.density):
            self.density = properties['density']

    # -------------------------------------------------------------------------------------------- #

    def calculateSectionProperties(self) -> dict:

        '''

        Area, second moment and mass per unit length for a thin cylinder, or the supplied values.

        '''

        self._validateInputs()

        if np.isfinite(self.area) and np.isfinite(self.secondMoment):
            area, second = self.area, self.secondMoment
        else:
            area   = 2.0 * np.pi * self.radius * self.thickness
            second = np.pi * self.radius ** 3 * self.thickness

        structuralMass = area * self.length * self.density
        totalMass      = structuralMass + self.distributedMass
        massPerLength  = totalMass / self.length

        return {'area':            area,
                'secondMoment':    second,
                'structuralMass':  structuralMass,
                'totalMass':       totalMass,
                'massPerLength':   massPerLength,
                'bendingStiffness': self.modulus * second}

    # -------------------------------------------------------------------------------------------- #

    def calculateBendingMode(self) -> dict:

        '''

        First lateral bending mode.

            f = (betaL)^2 / (2 pi L^2) sqrt(E I / m')

        A tip mass is handled by Dunkerley's approximation, which combines the distributed-mass and
        point-mass frequencies as reciprocal squares. It is conservative, meaning it underestimates
        the frequency, which is the right direction for a requirement check.

        '''

        self._validateInputs()

        if self.boundaryCondition not in BEAM_MODE_FACTORS:
            raise InvalidInputError(
                f'Unknown boundary condition \'{self.boundaryCondition}\'. '
                f'Known: {sorted(BEAM_MODE_FACTORS)}.',
                context = createErrorContext(component = 'ModalEstimate'))

        section = self.calculateSectionProperties()
        betaL   = BEAM_MODE_FACTORS[self.boundaryCondition]['betaL']

        stiffness     = section['bendingStiffness']
        massPerLength = section['massPerLength']

        distributedFrequency = (betaL ** 2 / (2.0 * np.pi * self.length ** 2)
                                * np.sqrt(stiffness / massPerLength))

        frequency = distributedFrequency
        tipContribution = 0.0

        if self.tipMass > 0.0:
            # cantilever point-mass frequency, sqrt(3EI / m L^3) / 2 pi
            pointFrequency = (1.0 / (2.0 * np.pi)
                              * np.sqrt(3.0 * stiffness / (self.tipMass * self.length ** 3)))
            # Dunkerley: 1/f^2 = sum of 1/f_i^2
            frequency = 1.0 / np.sqrt(1.0 / distributedFrequency ** 2
                                      + 1.0 / pointFrequency ** 2)
            tipContribution = 1.0 - frequency / distributedFrequency

        return {'frequency':            frequency,
                'distributedFrequency': distributedFrequency,
                'betaL':                betaL,
                'boundaryCondition':    self.boundaryCondition,
                'tipMassReduction':     tipContribution,
                'lowerBound':           frequency * (1.0 - ESTIMATE_ACCURACY),
                'upperBound':           frequency * (1.0 + ESTIMATE_ACCURACY)}

    # -------------------------------------------------------------------------------------------- #

    def calculateAxialMode(self) -> dict:

        '''

        First longitudinal mode, treating the structure as a rod.

            f = k / L sqrt(E / rho)

        The wave speed sqrt(E/rho) is a material property, about 5100 m/s in aluminium, so the
        axial mode of a given length is nearly material independent among the common alloys.

        '''

        self._validateInputs()

        key = (self.boundaryCondition if self.boundaryCondition in AXIAL_MODE_FACTORS
               else 'cantilever')
        factor = AXIAL_MODE_FACTORS[key]

        waveSpeed = np.sqrt(self.modulus / self.density)
        frequency = factor * waveSpeed / self.length

        section = self.calculateSectionProperties()

        if self.tipMass > 0.0:
            # spring-mass with the rod's axial stiffness, Rayleigh corrected by a third of the rod
            axialStiffness = self.modulus * section['area'] / self.length
            effectiveMass  = self.tipMass + section['structuralMass'] / 3.0
            frequency = np.sqrt(axialStiffness / effectiveMass) / (2.0 * np.pi)

        return {'frequency':   frequency,
                'waveSpeed':   waveSpeed,
                'factor':      factor,
                'lowerBound':  frequency * (1.0 - ESTIMATE_ACCURACY),
                'upperBound':  frequency * (1.0 + ESTIMATE_ACCURACY)}

    # -------------------------------------------------------------------------------------------- #

    def calculateShellModes(self, maximumWaves: int = 8) -> dict:

        '''

        Shell modes with circumferential waves, which are frequently the lowest modes of a thin
        cylinder and are missed entirely by a beam idealisation.

        Uses the Rayleigh inextensional approximation for a ring, which captures the characteristic
        n(n^2 - 1)/sqrt(n^2 + 1) dependence. The n = 2 ovalling mode is usually the lowest.

        '''

        self._validateInputs()

        if not (np.isfinite(self.radius) and np.isfinite(self.thickness)):
            return {'applicable': False,
                    'reason': 'Shell modes need a cylinder radius and thickness.'}

        # ring bending parameter
        coefficient = (self.thickness / (self.radius ** 2)
                       * np.sqrt(self.modulus
                                 / (12.0 * self.density * (1.0 - self.poisson ** 2))))

        frequencies = {}
        for waves in range(2, maximumWaves + 1):
            frequencies[waves] = (coefficient / (2.0 * np.pi)
                                  * waves * (waves ** 2 - 1.0)
                                  / np.sqrt(waves ** 2 + 1.0))

        lowestWaves = min(frequencies, key = frequencies.get)

        beam = self.calculateBendingMode()['frequency']

        return {'applicable':      True,
                'frequencies':     frequencies,
                'lowestMode':      frequencies[lowestWaves],
                'lowestWaveCount': lowestWaves,
                'beamMode':        beam,
                'shellBelowBeam':  bool(frequencies[lowestWaves] < beam),
                'ratioToBeam':     frequencies[lowestWaves] / beam if beam > 0.0 else np.inf}

    # -------------------------------------------------------------------------------------------- #

    def screenAgainstRequirement(self) -> dict:

        '''

        Every mode against the stated requirement, with the governing one identified.

        '''

        self._validateInputs()

        bending = self.calculateBendingMode()
        axial   = self.calculateAxialMode()
        shell   = self.calculateShellModes()

        self.findings = []

        modes = {'lateral bending': bending['frequency'],
                 'axial':           axial['frequency']}
        if shell['applicable']:
            modes[f'shell n={shell["lowestWaveCount"]}'] = shell['lowestMode']

        lowest = min(modes, key = modes.get)

        self.findings.append(
            f'The lowest predicted mode is {lowest} at {modes[lowest]:.2f} Hz.')

        if shell['applicable'] and shell['shellBelowBeam']:
            self.findings.append(
                f'The shell ovalling mode at {shell["lowestMode"]:.2f} Hz is below the beam '
                f'bending mode at {shell["beamMode"]:.2f} Hz. A beam idealisation would report '
                f'this structure as {shell["beamMode"] / shell["lowestMode"]:.1f}x stiffer than '
                f'it is.')

        margins = {}
        if np.isfinite(self.requiredLateral):

            # The lateral requirement is on the lowest lateral mode, not on the beam mode. A shell
            # ovalling mode is a lateral mode and it is frequently the lowest one, so checking the
            # beam mode alone reports a structure as compliant when its true first mode is not.
            lowestLateral = bending['frequency']
            lateralSource = 'lateral bending'

            if shell['applicable'] and shell['lowestMode'] < lowestLateral:
                lowestLateral = shell['lowestMode']
                lateralSource = f'shell n={shell["lowestWaveCount"]}'

            margins['lateral'] = lowestLateral / self.requiredLateral - 1.0

            if lateralSource != 'lateral bending':
                self.findings.append(
                    f'The lateral requirement is assessed against {lateralSource} at '
                    f'{lowestLateral:.2f} Hz, not the beam mode. Checking the beam mode alone '
                    f'would report a margin of '
                    f'{bending["frequency"] / self.requiredLateral - 1.0:+.3f} instead of '
                    f'{margins["lateral"]:+.3f}.')

            if bending['lowerBound'] < self.requiredLateral:
                self.findings.append(
                    f'The lateral mode estimate is {bending["frequency"]:.2f} Hz against a '
                    f'{self.requiredLateral:.1f} Hz requirement, and the +/-'
                    f'{ESTIMATE_ACCURACY * 100.0:.0f} % band reaches '
                    f'{bending["lowerBound"]:.2f} Hz. This needs a finite element check, not a '
                    f'closed form.')

        if np.isfinite(self.requiredAxial):
            margins['axial'] = axial['frequency'] / self.requiredAxial - 1.0

        if self.tipMass > 0.0 and bending['tipMassReduction'] > 0.3:
            self.findings.append(
                f'The tip mass drops the bending frequency by '
                f'{bending["tipMassReduction"] * 100.0:.0f} %. The structure is mass dominated at '
                f'the free end, so stiffening the root buys less than it appears to.')

        self.findings.append(
            f'These are closed-form estimates, accurate to roughly +/-'
            f'{ESTIMATE_ACCURACY * 100.0:.0f} % for a uniform idealised structure. They size '
            f'before a model exists; they do not replace one.')

        return {'modes':          modes,
                'lowestMode':     lowest,
                'lowestFrequency': modes[lowest],
                'margins':        margins,
                'acceptable':     bool(all(value >= 0.0 for value in margins.values()))
                                  if margins else None,
                'findings':       self.findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the modal estimates.
        '''

        screen = self.screenAgainstRequirement()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  MODAL ESTIMATE: {self.material}, L = {self.length:.2f} m, '
                     f'{self.boundaryCondition}')
        lines.append('=' * 96)
        lines.append('')

        rows = [[name, f'{frequency:.2f}',
                 'LOWEST' if name == screen['lowestMode'] else '']
                for name, frequency in sorted(screen['modes'].items(),
                                              key = lambda item: item[1])]
        lines.append(formatReportTable(rows, ['Mode', 'Frequency [Hz]', ''],
                                       title = 'Predicted modes'))

        if screen['margins']:
            marginRows = [[name, f'{value:+.3f}', 'PASS' if value >= 0.0 else 'FAIL']
                          for name, value in screen['margins'].items()]
            lines.append('')
            lines.append(formatReportTable(marginRows, ['Requirement', 'Margin', ''],
                                           title = 'Against requirement'))

        if self.findings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in self.findings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'modalEstimate.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check enough geometry is present to define a section.
        '''

        context = createErrorContext(component = 'ModalEstimate')

        if not np.isfinite(self.length) or self.length <= 0.0:
            raise InvalidInputError('Length must be positive.', context = context)

        hasCylinder = np.isfinite(self.radius) and np.isfinite(self.thickness)
        hasSection  = np.isfinite(self.area) and np.isfinite(self.secondMoment)

        if not (hasCylinder or hasSection):
            raise InvalidInputError(
                'Provide either radius and thickness, or area and secondMoment.',
                context = context)

        if hasCylinder and self.thickness >= self.radius:
            raise GeometryError(
                f'Thickness {self.thickness:.4f} m is not less than the radius. This is not a '
                f'thin cylinder.', context = context)
