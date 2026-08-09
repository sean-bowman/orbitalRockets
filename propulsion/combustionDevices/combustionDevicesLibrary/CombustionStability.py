
# -- CombustionStability -- #

'''

Chamber acoustic modes, the chug criterion, and the devices that suppress each.

The thing to hold on to about combustion instability is that it is a threshold and not a margin.
A stable engine and an unstable one differ by a design detail rather than by a factor, and there is
no continuous quantity that says how stable an engine is. That is why the rating test is a
deliberate perturbation rather than a measurement: you set off a bomb in the chamber and time how
long the oscillation takes to die, because the only meaningful question is whether a disturbance
grows or decays.

Nothing in this class predicts stability. It computes the frequencies a chamber will support, the
one necessary condition that is easy to check, and what the suppression devices are tuned to. A
class that returned a stability margin would be lying, and the absence of one is deliberate.

Three regimes, by frequency and by what they couple to:

    chug        tens to low hundreds of Hz     feed system and chamber volume
    buzz        hundreds of Hz                 longitudinal chamber acoustics
    screech     thousands of Hz                transverse chamber acoustics

Chug is a nuisance that shows up as rough running. Screech destroys engines in milliseconds.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from combustionUtils import (CHAMBER_ACOUSTIC_MODES, CHUG_STIFFNESS_FLOOR,
                                 combustionGasProperties,
                                 applyInputs, formatReportTable, createErrorContext,
                                 InvalidInputError, StabilityError)
except ImportError:
    from .combustionUtils import (CHAMBER_ACOUSTIC_MODES, CHUG_STIFFNESS_FLOOR,
                                  combustionGasProperties,
                                  applyInputs, formatReportTable, createErrorContext,
                                  InvalidInputError, StabilityError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# A baffle with N radial blades suppresses tangential modes up to order N/2, by preventing a
# coherent wave from travelling around the circumference. It does nothing at all to radial modes,
# which is why a baffled engine can still go unstable in 1R and why baffles are not a complete
# answer on their own.
BAFFLE_SUPPRESSION_ORDER = 0.5    # [-]

# Baffle blade depth as a fraction of chamber radius. Deep enough to interrupt the wave near the
# injector face where the energy is added, and no deeper, because the blades are uncooled
# obstructions in the hottest part of the chamber and they are a classic failure item.
TYPICAL_BAFFLE_DEPTH_RATIO = 0.25    # [-]

# The damping time a rating test has to demonstrate after a bomb or a pulse. Anything longer and
# the engine is not dynamically stable even if it did not destroy itself during the test.
STABILITY_DAMP_TIME = 0.040    # [s]

# Rating perturbation methods, and what each one is good for.
RATING_METHODS = {
    'bomb':          {'note': 'explosive charge in the chamber. The most severe and most standard'},
    'pulse gun':     {'note': 'external gas pulse through a port. Repeatable, less severe'},
    'directed flow': {'note': 'a jet across the injector face. Least severe, easiest to instrument'},
}

# ------------------------------------------------------------------------------------------------ #
# -- CombustionStability -- #
# ------------------------------------------------------------------------------------------------ #

class CombustionStability:

    '''

    Acoustic mode frequencies, the chug criterion, and the tuning of baffles and cavities.

    '''

    def __init__(self):

        self.combination     = ''
        self.chamberDiameter = np.nan
        self.chamberLength   = np.nan
        self.injectorStiffness = np.nan
        self.baffleBlades    = np.nan

        self.gasProperties = {}
        self.findings      = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''
        `chamberLength` is the barrel plus convergent length, which is what the longitudinal mode
        sees.
        '''

        requiredParams = {'combination':     str,
                          'chamberDiameter': (int, float),
                          'chamberLength':   (int, float)}

        optionalParams = {'injectorStiffness': (int, float),
                          'baffleBlades':      (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if not np.isfinite(self.injectorStiffness):
            self.injectorStiffness = 0.15

        if not np.isfinite(self.baffleBlades):
            self.baffleBlades = 0.0

        self._validateInputs()

        self.gasProperties = combustionGasProperties(self.combination)

    # -------------------------------------------------------------------------------------------- #

    def speedOfSound(self) -> float:

        '''

        Speed of sound in the combustion products, sqrt(gamma R Tc).

        Taken at the chamber stagnation temperature, which overstates it slightly because the gas
        in the chamber is moving, and the error is smaller than the uncertainty in the temperature.

        '''

        return float(np.sqrt(self.gasProperties['gamma']
                             * self.gasProperties['specificGasConstant']
                             * self.gasProperties['chamberTemperature']))

    # -------------------------------------------------------------------------------------------- #

    def calculateAcousticModes(self) -> dict:

        '''

        Transverse and longitudinal mode frequencies for a cylindrical chamber.

            transverse:    f = alpha a / (pi D)      alpha the Bessel eigenvalue
            longitudinal:  f = n a / (2 L)

        The first tangential mode is the one that destroys engines. It is the lowest transverse
        mode, it couples readily with the injection and atomisation process, and its pressure wave
        sweeps around the chamber circumference scrubbing the wall as it goes.

        '''

        findings = []

        sound = self.speedOfSound()

        transverse = {}
        for name, entry in CHAMBER_ACOUSTIC_MODES.items():
            transverse[name] = {
                'frequency': entry['eigenvalue'] * sound / (np.pi * self.chamberDiameter),
                'eigenvalue': entry['eigenvalue'],
                'note': entry['note']}

        longitudinal = {f'{order}L': {'frequency': order * sound / (2.0 * self.chamberLength),
                                      'order': order}
                        for order in (1, 2, 3)}

        firstTangential = transverse['1T']['frequency']

        findings.append(
            f'Speed of sound {sound:.0f} m/s at {self.gasProperties["chamberTemperature"]:.0f} K.')

        findings.append(
            f'First tangential at {firstTangential:.0f} Hz in a '
            f'{self.chamberDiameter * 1000.0:.0f} mm chamber. That is the mode that destroys '
            f'engines, and it scales as one over diameter, so a large chamber has a low and '
            f'dangerous 1T and a small chamber has a high one.')

        findings.append(
            f'First longitudinal at {longitudinal["1L"]["frequency"]:.0f} Hz. Longitudinal modes '
            f'couple with the feed system more readily and destroy engines less often.')

        self.findings = findings

        return {'speedOfSound':  sound,
                'transverse':    transverse,
                'longitudinal':  longitudinal,
                'firstTangential': firstTangential,
                'findings':      findings}

    # -------------------------------------------------------------------------------------------- #

    def checkChugCriterion(self, throttleSetting: float = 1.0) -> dict:

        '''

        The injector stiffness criterion for low frequency stability.

        This is a necessary condition and not a sufficient one. Chug is a system oscillation
        involving the feed line inertance, the chamber volume and the combustion time lag as well
        as the injector, so clearing the criterion does not prove stability. Failing it does prove
        a problem, which is what makes it worth checking.

        '''

        findings = []

        if not 0.0 < throttleSetting <= 1.0:
            raise StabilityError(
                f'The throttle setting must lie in (0, 1], got {throttleSetting}.',
                context = createErrorContext(component = 'CombustionStability'))

        stiffness = self.injectorStiffness * throttleSetting

        clears = stiffness >= CHUG_STIFFNESS_FLOOR

        findings.append(
            f'Injector stiffness {stiffness:.1%} at {throttleSetting:.0%} throttle against a '
            f'{CHUG_STIFFNESS_FLOOR:.0%} floor.')

        if clears:
            findings.append(
                'The necessary condition is met. It is not sufficient: chug involves the feed line '
                'inertance and the chamber volume, and neither is in this check.')
        else:
            findings.append(
                'The necessary condition is not met, so the feed system and the chamber are '
                'coupled strongly enough to sustain a low frequency oscillation. This one is a '
                'prediction rather than a warning.')

        self.findings = findings

        return {'stiffness':       stiffness,
                'floor':           CHUG_STIFFNESS_FLOOR,
                'clears':          clears,
                'throttleSetting': throttleSetting,
                'necessaryOnly':   True,
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeBaffles(self) -> dict:

        '''

        Which tangential modes a baffle suppresses, and how deep the blades have to be.

        A baffle with `N` radial blades prevents a coherent wave travelling around the
        circumference for tangential orders up to `N/2`. **It does nothing to radial modes.** A
        baffled engine that goes unstable in 1R is a well documented outcome and it is why baffles
        and acoustic cavities are usually fitted together rather than as alternatives.

        '''

        findings = []

        modes = self.calculateAcousticModes()

        blades = int(self.baffleBlades)

        if blades <= 0:
            findings.append('No baffle fitted, so every transverse mode is available.')
            self.findings = findings
            return {'blades': 0, 'suppressedOrder': 0, 'suppressed': [],
                    'unsuppressed': sorted(modes['transverse']),
                    'bladeDepth': 0.0, 'findings': findings}

        suppressedOrder = int(blades * BAFFLE_SUPPRESSION_ORDER)

        suppressed   = []
        unsuppressed = []

        for name in modes['transverse']:
            # tangential modes are the ones named nT; radial and mixed modes are not suppressed
            if name.endswith('T') and name[:-1].isdigit():
                order = int(name[:-1])
                (suppressed if order <= suppressedOrder else unsuppressed).append(name)
            else:
                unsuppressed.append(name)

        bladeDepth = TYPICAL_BAFFLE_DEPTH_RATIO * self.chamberDiameter / 2.0

        findings.append(
            f'{blades} blades suppress tangential modes to order {suppressedOrder}: '
            f'{", ".join(suppressed) if suppressed else "none"}.')

        findings.append(
            f'Unsuppressed: {", ".join(unsuppressed)}. Radial modes are unaffected by a baffle at '
            f'any blade count, because a radial wave does not travel around the circumference.')

        findings.append(
            f'Blade depth {bladeDepth * 1000.0:.0f} mm, a quarter of the chamber radius. Deep '
            f'enough to interrupt the wave near the injector face where the energy is added, and '
            f'no deeper, because the blades are uncooled obstructions in the hottest part of the '
            f'chamber and they are a classic failure item.')

        self.findings = findings

        return {'blades':          blades,
                'suppressedOrder': suppressedOrder,
                'suppressed':      suppressed,
                'unsuppressed':    unsuppressed,
                'bladeDepth':      bladeDepth,
                'findings':        findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeAcousticCavity(self, targetMode: str = '1T') -> dict:

        '''

        Helmholtz resonator geometry tuned to a chamber mode.

            f = (a / 2 pi) sqrt( A / (V L_eff) )

        Acoustic cavities sit in the injector face or the chamber wall near it and absorb energy at
        the frequency they are tuned to. Unlike baffles they work on radial modes as well, which is
        why the two are complements rather than alternatives.

        The tuning is temperature sensitive, because the speed of sound in the cavity depends on
        what is in it and how hot that is. A cavity tuned at the design chamber temperature is
        mistuned at start-up and during a throttle excursion, which is one reason cavities are made
        with a range of depths rather than all identical.

        '''

        findings = []

        modes = self.calculateAcousticModes()

        if targetMode not in modes['transverse']:
            raise StabilityError(
                f'Unknown mode \'{targetMode}\'. Known: {sorted(modes["transverse"])}.',
                context = createErrorContext(component = 'CombustionStability'))

        frequency = modes['transverse'][targetMode]['frequency']
        sound     = modes['speedOfSound']

        # a quarter wave cavity of this depth resonates at the target frequency
        quarterWaveDepth = sound / (4.0 * frequency)

        findings.append(
            f'A quarter wave cavity tuned to {targetMode} at {frequency:.0f} Hz is '
            f'{quarterWaveDepth * 1000.0:.1f} mm deep.')

        findings.append(
            'Cavities absorb radial modes as well as tangential ones, which baffles do not. That '
            'is why the two are fitted together rather than chosen between.')

        findings.append(
            'The tuning moves with the speed of sound in the cavity, so a cavity tuned at the '
            'design chamber temperature is mistuned at start-up and during a throttle excursion. '
            'A range of depths covers more than a single tuning does.')

        self.findings = findings

        return {'targetMode':       targetMode,
                'frequency':        frequency,
                'quarterWaveDepth': quarterWaveDepth,
                'speedOfSound':     sound,
                'findings':         findings}

    # -------------------------------------------------------------------------------------------- #

    def ratingRequirement(self) -> dict:

        '''

        What a stability rating test has to demonstrate.

        The engine is perturbed deliberately and the oscillation is timed. Anything that does not
        decay within the damp time is not dynamically stable, whatever it did in undisturbed
        operation. This is the only meaningful stability statement, and it is a test result rather
        than a calculation.

        '''

        findings = [
            f'A rating test perturbs the chamber deliberately and requires the oscillation to '
            f'decay within {STABILITY_DAMP_TIME * 1000.0:.0f} ms.',
            'Undisturbed stable operation demonstrates nothing. An engine can run smoothly for a '
            'full duration and go unstable on the next start, because the question is whether a '
            'disturbance grows and no disturbance was applied.']

        for name, entry in RATING_METHODS.items():
            findings.append(f'{name}: {entry["note"]}.')

        self.findings = findings

        return {'dampTime': STABILITY_DAMP_TIME,
                'methods':  RATING_METHODS,
                'findings': findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full stability report.
        '''

        modes   = self.calculateAcousticModes()
        chug    = self.checkChugCriterion()
        baffles = self.sizeBaffles()
        cavity  = self.sizeAcousticCavity()
        rating  = self.ratingRequirement()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  COMBUSTION STABILITY: {self.combination}')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [['Chamber diameter', f'{self.chamberDiameter * 1000.0:.1f}',   'mm'],
             ['Chamber length',   f'{self.chamberLength * 1000.0:.1f}',     'mm'],
             ['Speed of sound',   f'{modes["speedOfSound"]:.0f}',           'm/s'],
             ['Injector stiffness', f'{self.injectorStiffness:.1%}',        ''],
             ['Baffle blades',    f'{baffles["blades"]}',                   ''],
             ['Cavity depth',     f'{cavity["quarterWaveDepth"] * 1000.0:.1f}', 'mm']],
            ['Quantity', 'Value', 'Unit'], title = 'Configuration'))

        lines.append('')
        lines.append('  Acoustic modes:')
        lines.append('')
        lines.append(f'    {"mode":6s} {"frequency [Hz]":>15s}   note')
        for name, entry in modes['transverse'].items():
            lines.append(f'    {name:6s} {entry["frequency"]:15.0f}   {entry["note"]}')
        for name, entry in modes['longitudinal'].items():
            lines.append(f'    {name:6s} {entry["frequency"]:15.0f}   longitudinal')

        lines.append('')
        for finding in (modes['findings'] + chug['findings'] + baffles['findings']
                        + cavity['findings'] + rating['findings']):
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            path = os.path.join(outputDir, f'stability_{self.combination.replace("/", "_")}.txt')
            with open(path, 'w', encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        for name, value in (('chamber diameter', self.chamberDiameter),
                            ('chamber length', self.chamberLength)):
            if value <= 0.0:
                raise InvalidInputError(f'The {name} must be positive, got {value}.',
                                        context = createErrorContext(
                                            component = 'CombustionStability'))

        if not 0.0 < self.injectorStiffness < 1.0:
            raise StabilityError(
                f'The injector stiffness must lie in (0, 1), got {self.injectorStiffness}.',
                context = createErrorContext(component = 'CombustionStability'))

        if self.baffleBlades < 0:
            raise StabilityError(
                f'The baffle blade count cannot be negative, got {self.baffleBlades}.',
                context = createErrorContext(component = 'CombustionStability'))
