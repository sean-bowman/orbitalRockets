
# -- BoltedJoint Class Definition -- #

'''

Preloaded bolted joints: the joint stiffness diagram, separation, bolt tension, and the bearing and
shear-out checks on the members.

A preloaded joint is the one structural element where more applied load does not mean much more
bolt load, right up until it does. That is the whole reason to preload. The bolt and the clamped
members form two springs in parallel: applied tension splits between them by their relative
stiffness, and because the members are far stiffer than the bolt, most of the applied load goes
into unloading the members rather than into stretching the bolt.

    load factor    Phi = k_bolt / (k_bolt + k_member)
    bolt tension   F_bolt = F_preload + Phi * P
    separation at  P_sep = F_preload / (1 - Phi)

Phi is typically 0.1 to 0.3, so a joint carrying 10 kN of applied tension may see only 2 kN of
additional bolt tension. Then the members separate, Phi effectively becomes 1.0, and the bolt takes
everything. The joint's behaviour changes discontinuously at that point, which is why separation is
checked as its own requirement rather than being folded into a stress margin.

Preload itself is the least controlled quantity in the joint. Torque control has a scatter of plus
or minus 25 to 35 percent because the nut factor depends on the thread and bearing friction, and
those depend on plating, lubrication, and how many times the fastener has been used. NASA-STD-5020
requires the analysis to be run at both the maximum and the minimum preload, because the two bound
different failure modes: maximum preload governs bolt yield, minimum preload governs separation and
slip.

Three member failure modes matter and none of them involve the bolt:

    bearing      the hole elongates under the bolt shank
    shear-out    the material between the hole and the free edge tears out
    net section  the reduced section through the hole fails in tension

Edge distance is what separates a joint that fails by bearing, which is progressive and visible,
from one that fails by shear-out, which is sudden.

See Also:
---------
PressureVessel : The Y-ring joint this analyses
BeamColumn     : Bolted end fittings set the effective length factor

Theory: docs/BoltedJoints.md

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
                                 marginOfSafety, InvalidInputError, GeometryError,
                                 createErrorContext)
except ImportError:
    from .structuresUtils import (applyInputs, formatReportTable, structuralAllowables,
                                  marginOfSafety, InvalidInputError, GeometryError,
                                  createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Nut factor K in T = K F d. The spread across these is the reason torque control is imprecise.
NUT_FACTORS = {
    'dry':               {'value': 0.20, 'note': 'as-received steel on steel'},
    'lubricated':        {'value': 0.15, 'note': 'oiled or waxed'},
    'cadmium plated':    {'value': 0.16, 'note': ''},
    'solid film lube':   {'value': 0.12, 'note': 'the most repeatable common option'},
    'anti-seize':        {'value': 0.13, 'note': 'variable, depends heavily on application'},
}

# Preload scatter by control method, as a fraction. NASA-STD-5020 requires the analysis at both
# bounds, because maximum preload governs bolt yield and minimum governs separation and slip.
PRELOAD_SCATTER = {
    'torque':            0.30,   # [-], plus or minus
    'torque plus angle': 0.15,   # [-]
    'bolt stretch':      0.05,   # [-]
    'ultrasonic':        0.05,   # [-]
    'load indicating':   0.10,   # [-]
}

# Preload as a fraction of the bolt's tensile yield. 65 % is the common aerospace target.
PRELOAD_FRACTION_DEFAULT = 0.65    # [-]

# Short-term embedment relaxation of the preload, from asperities bedding in.
EMBEDMENT_LOSS = 0.05    # [-], fraction of preload lost in the first hours

# NASA-STD-5020 separation factor of safety. Separation is a discontinuity in joint behaviour, so
# it carries its own factor rather than being folded into a stress margin.
SEPARATION_FACTOR_DEFAULT = 1.20    # [-]

# The pressure cone starts at the head or washer bearing face, which is wider than the shank.
HEAD_BEARING_RATIO   = 1.50    # [-], bearing face diameter over bolt diameter
HOLE_CLEARANCE_RATIO = 1.10    # [-], clearance hole diameter over bolt diameter

# Minimum edge distance in bolt diameters, below which shear-out replaces bearing as the mode.
MINIMUM_EDGE_DISTANCE_RATIO = 2.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- BoltedJoint -- #
# ------------------------------------------------------------------------------------------------ #

class BoltedJoint:

    '''

    Preloaded bolted joint analysis.

    Usage:
    ------
        joint = BoltedJoint()
        joint.setInputs({'boltDiameter': 0.00635, 'boltMaterial': 'A286',
                         'memberMaterial': '2219-T87', 'memberCondition': 't87',
                         'gripLength': 0.012, 'memberThickness': 0.006,
                         'edgeDistance': 0.0127, 'appliedTension': 4.0e3})
        result = joint.calculateJointDiagram()

    '''

    def __init__(self):

        # -- Bolt -- #

        self.boltDiameter     = np.nan  # [m], nominal
        self.boltMaterial     = 'A286'
        self.boltCondition    = None    # [-]
        self.boltModulus      = 200.0e9 # [Pa], A286
        self.boltYield        = 590.0e6 # [Pa], A286
        self.tensileAreaRatio = 0.75    # [-], stress area over nominal area, typical UNJF

        # -- Members -- #

        self.memberMaterial   = '2219-T87'
        self.memberCondition  = None    # [-]
        self.basis            = 'typical'  # [-]
        self.temperature      = 293.15  # [K]
        self.memberModulus    = np.nan  # [Pa]
        self.memberYield      = np.nan  # [Pa]
        self.memberUltimate   = np.nan  # [Pa]
        self.gripLength       = np.nan  # [m], total clamped thickness
        self.memberThickness  = np.nan  # [m], the thinner member, for bearing
        self.edgeDistance     = np.nan  # [m], hole centre to free edge
        self.pitch            = np.nan  # [m], hole centre to hole centre

        # -- Preload -- #

        self.preloadFraction  = PRELOAD_FRACTION_DEFAULT  # [-]
        self.preloadMethod    = 'torque'   # key into PRELOAD_SCATTER
        self.nutFactorKey     = 'lubricated'  # key into NUT_FACTORS
        self.includeEmbedment = True    # [-]

        # -- Applied Loading -- #

        self.appliedTension   = 0.0     # [N], per bolt, along the bolt axis
        self.appliedShear     = 0.0     # [N], per bolt, transverse

        # -- Factors -- #

        self.factorOfSafety   = 1.4     # [-]
        self.separationFactor = SEPARATION_FACTOR_DEFAULT  # [-]

        # -- Results -- #

        self.findings         = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: boltDiameter, gripLength.

        '''

        requiredParams = {'boltDiameter': (int, float),
                          'gripLength':   (int, float)}

        optionalParams = {'boltMaterial':     str,
                          'boltCondition':    str,
                          'boltModulus':      (int, float),
                          'boltYield':        (int, float),
                          'tensileAreaRatio': (int, float),
                          'memberMaterial':   str,
                          'memberCondition':  str,
                          'basis':            str,
                          'temperature':      (int, float),
                          'memberModulus':    (int, float),
                          'memberYield':      (int, float),
                          'memberUltimate':   (int, float),
                          'memberThickness':  (int, float),
                          'edgeDistance':     (int, float),
                          'pitch':            (int, float),
                          'preloadFraction':  (int, float),
                          'preloadMethod':    str,
                          'nutFactorKey':     str,
                          'includeEmbedment': bool,
                          'appliedTension':   (int, float),
                          'appliedShear':     (int, float),
                          'factorOfSafety':   (int, float),
                          'separationFactor': (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        properties = structuralAllowables(self.memberMaterial, self.memberCondition,
                                          temperature = self.temperature, basis = self.basis)

        if not np.isfinite(self.memberModulus):
            self.memberModulus = properties['elasticModulus']
        if not np.isfinite(self.memberYield):
            self.memberYield = properties['yieldStrength']
        if not np.isfinite(self.memberUltimate):
            self.memberUltimate = properties['ultimateStrength']

    # -------------------------------------------------------------------------------------------- #

    @property
    def nominalArea(self) -> float:

        '''
        Nominal shank area.
        '''

        return np.pi * self.boltDiameter ** 2 / 4.0

    @property
    def tensileStressArea(self) -> float:

        '''
        The thread stress area, which is what carries the tension. Smaller than the shank.
        '''

        return self.tensileAreaRatio * self.nominalArea

    # -------------------------------------------------------------------------------------------- #

    def calculateStiffnesses(self) -> dict:

        '''

        Bolt and member stiffness, and the load factor Phi that splits applied load between them.

        The member stiffness uses the standard 30 degree pressure cone, which is why the clamped
        material behaves as a frustum rather than a cylinder. The result is that members are
        typically three to ten times stiffer than the bolt.

        '''

        self._validateInputs()

        boltStiffness = self.boltModulus * self.tensileStressArea / self.gripLength

        # Rotscher pressure cone, integrated along its length rather than approximated by the area
        # at mid-grip. The closed form is Shigley's, for one frustum of height l:
        #
        #     k = pi E d tan(a) / ln( ((2 l tan(a) + D - d)(D + d)) / ((2 l tan(a) + D + d)(D - d)) )
        #
        # A symmetric joint is two such frusta in series, each of half the grip.
        #
        # The mid-grip equivalent-area shortcut is wrong in a way that is easy to miss: the cone
        # area grows as the square of the grip while the stiffness divides by the grip, so that
        # form makes member stiffness *rise* with grip length. A longer spring must be softer.
        #
        # The cone starts at the head or washer bearing face, not at the shank, because the clamp
        # load is introduced over the head footprint. Starting it at the bolt diameter understates
        # member stiffness by roughly 1.7x and pushes the load factor out of the 0.1 to 0.3 band
        # that real preloaded joints occupy.
        coneAngle       = np.radians(30.0)
        bearingDiameter = HEAD_BEARING_RATIO * self.boltDiameter
        holeDiameter    = HOLE_CLEARANCE_RATIO * self.boltDiameter
        frustumHeight   = self.gripLength / 2.0

        growth    = 2.0 * frustumHeight * np.tan(coneAngle)
        numerator = (growth + bearingDiameter - holeDiameter) * (bearingDiameter + holeDiameter)
        denominator = (growth + bearingDiameter + holeDiameter) * (bearingDiameter - holeDiameter)

        if denominator <= 0.0 or numerator / denominator <= 1.0:
            raise GeometryError(
                'The pressure cone geometry is degenerate: the clearance hole is at or beyond the '
                'head bearing diameter, so there is no material to clamp.',
                context = createErrorContext(component = 'BoltedJoint'))

        frustumStiffness = (np.pi * self.memberModulus * self.boltDiameter * np.tan(coneAngle)
                            / np.log(numerator / denominator))

        # two frusta in series
        memberStiffness = frustumStiffness / 2.0

        # reported for continuity with the simpler form
        equivalentArea = memberStiffness * self.gripLength / self.memberModulus

        loadFactor = boltStiffness / (boltStiffness + memberStiffness)

        return {'boltStiffness':    boltStiffness,
                'memberStiffness':  memberStiffness,
                'stiffnessRatio':   memberStiffness / boltStiffness,
                'loadFactor':       loadFactor,
                'equivalentArea':   equivalentArea,
                'tensileStressArea': self.tensileStressArea}

    # -------------------------------------------------------------------------------------------- #

    def calculatePreload(self) -> dict:

        '''

        Nominal, maximum and minimum preload, with the scatter of the chosen control method.

        Both bounds matter and they bound different failure modes, which is why NASA-STD-5020
        requires the analysis at each.

        '''

        self._validateInputs()

        if self.preloadMethod not in PRELOAD_SCATTER:
            raise InvalidInputError(
                f'Unknown preload method \'{self.preloadMethod}\'. '
                f'Known: {sorted(PRELOAD_SCATTER)}.',
                context = createErrorContext(component = 'BoltedJoint'))

        if self.nutFactorKey not in NUT_FACTORS:
            raise InvalidInputError(
                f'Unknown nut factor \'{self.nutFactorKey}\'. Known: {sorted(NUT_FACTORS)}.',
                context = createErrorContext(component = 'BoltedJoint'))

        nominal = self.preloadFraction * self.boltYield * self.tensileStressArea

        if self.includeEmbedment:
            nominal *= (1.0 - EMBEDMENT_LOSS)

        scatter = PRELOAD_SCATTER[self.preloadMethod]
        nutFactor = NUT_FACTORS[self.nutFactorKey]['value']

        torque = nutFactor * nominal * self.boltDiameter

        return {'nominalPreload':  nominal,
                'maximumPreload':  nominal * (1.0 + scatter),
                'minimumPreload':  nominal * (1.0 - scatter),
                'scatter':         scatter,
                'preloadMethod':   self.preloadMethod,
                'nutFactor':       nutFactor,
                'installationTorque': torque,
                'embedmentApplied': self.includeEmbedment,
                'preloadStress':   nominal / self.tensileStressArea}

    # -------------------------------------------------------------------------------------------- #

    def calculateJointDiagram(self) -> dict:

        '''

        Bolt tension under applied load, the separation load, and the margins at both preload
        bounds.

        This is the class's central calculation and the reason preloaded joints behave the way they
        do: applied tension mostly unloads the members rather than loading the bolt.

        '''

        self._validateInputs()

        stiffness = self.calculateStiffnesses()
        preload   = self.calculatePreload()

        loadFactor = stiffness['loadFactor']
        applied    = self.appliedTension

        # maximum preload governs bolt yield
        boltTensionMax = preload['maximumPreload'] + loadFactor * applied * self.factorOfSafety
        boltStressMax  = boltTensionMax / self.tensileStressArea

        # minimum preload governs separation
        separationLoad = (preload['minimumPreload'] / (1.0 - loadFactor)
                          if loadFactor < 1.0 else np.inf)

        self.findings = []

        boltShare = loadFactor * applied
        self.findings.append(
            f'The load factor is {loadFactor:.3f}, so of {applied / 1000.0:.2f} kN applied only '
            f'{boltShare / 1000.0:.2f} kN reaches the bolt. The rest unloads the members.')

        if separationLoad < applied * self.separationFactor:
            self.findings.append(
                f'The joint separates at {separationLoad / 1000.0:.2f} kN, below the applied load '
                f'times the separation factor. Past separation the load factor becomes 1.0 and the '
                f'bolt takes everything, so the joint behaviour changes discontinuously.')

        if self.preloadMethod == 'torque':
            self.findings.append(
                f'Torque control carries {preload["scatter"] * 100.0:.0f} % preload scatter. '
                f'Maximum preload governs bolt yield and minimum governs separation, so both '
                f'bounds are analysed.')

        return {'loadFactor':        loadFactor,
                'boltTensionMaximum': boltTensionMax,
                'boltStressMaximum': boltStressMax,
                'boltShareOfApplied': boltShare,
                'memberShareOfApplied': (1.0 - loadFactor) * applied,
                'separationLoad':    separationLoad,
                'separationMargin':  marginOfSafety(separationLoad, applied,
                                                    self.separationFactor),
                'yieldMargin':       marginOfSafety(self.boltYield, boltStressMax, 1.0),
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateMemberChecks(self) -> dict:

        '''

        Bearing, shear-out and net section on the clamped members.

        None of these involve the bolt's strength. They are the reason edge distance and pitch are
        specified, and edge distance is what decides whether the joint fails progressively by
        bearing or suddenly by shear-out.

        '''

        self._validateInputs()

        if not np.isfinite(self.memberThickness):
            raise InvalidInputError('Member checks need memberThickness.',
                                    context = createErrorContext(component = 'BoltedJoint'))

        shear = abs(self.appliedShear)

        bearingArea   = self.boltDiameter * self.memberThickness
        bearingStress = shear / bearingArea if bearingArea > 0.0 else np.nan
        # bearing allowable is conventionally 1.5x ultimate, since the hole is confined
        bearingAllowable = 1.5 * self.memberUltimate

        results = {'bearingStress':    bearingStress,
                   'bearingAllowable': bearingAllowable,
                   'bearingMargin':    marginOfSafety(bearingAllowable, bearingStress,
                                                      self.factorOfSafety)}

        if np.isfinite(self.edgeDistance):
            edgeRatio = self.edgeDistance / self.boltDiameter
            # two shear planes from the hole to the edge
            shearOutArea = 2.0 * (self.edgeDistance - self.boltDiameter / 2.0) * self.memberThickness
            shearOutStress = shear / shearOutArea if shearOutArea > 0.0 else np.inf
            shearAllowable = 0.577 * self.memberUltimate    # von Mises shear

            results.update({'edgeDistanceRatio': edgeRatio,
                            'shearOutStress':    shearOutStress,
                            'shearOutAllowable': shearAllowable,
                            'shearOutMargin':    marginOfSafety(shearAllowable, shearOutStress,
                                                                self.factorOfSafety),
                            'edgeDistanceAdequate': bool(edgeRatio >= MINIMUM_EDGE_DISTANCE_RATIO)})

        if np.isfinite(self.pitch):
            netWidth      = self.pitch - self.boltDiameter
            netArea       = netWidth * self.memberThickness
            netStress     = shear / netArea if netArea > 0.0 else np.inf
            results.update({'netSectionStress': netStress,
                            'netSectionMargin': marginOfSafety(self.memberUltimate, netStress,
                                                               self.factorOfSafety)})

        return results

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the joint.
        '''

        stiffness = self.calculateStiffnesses()
        preload   = self.calculatePreload()
        diagram   = self.calculateJointDiagram()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  BOLTED JOINT: {self.boltMaterial} bolt '
                     f'{self.boltDiameter * 1000.0:.2f} mm into {self.memberMaterial}')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Bolt stiffness',   f'{stiffness["boltStiffness"] / 1.0e6:.1f}', 'MN/m'],
                ['Member stiffness', f'{stiffness["memberStiffness"] / 1.0e6:.1f}', 'MN/m'],
                ['Stiffness ratio',  f'{stiffness["stiffnessRatio"]:.2f}', '-'],
                ['Load factor Phi',  f'{stiffness["loadFactor"]:.4f}', '-']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'],
                                       title = 'Joint stiffness'))
        lines.append('')

        preloadRows = [['Nominal preload', f'{preload["nominalPreload"] / 1000.0:.2f}', 'kN'],
                       ['Maximum',         f'{preload["maximumPreload"] / 1000.0:.2f}', 'kN'],
                       ['Minimum',         f'{preload["minimumPreload"] / 1000.0:.2f}', 'kN'],
                       ['Install torque',  f'{preload["installationTorque"]:.2f}', 'N*m'],
                       ['Separation load', f'{diagram["separationLoad"] / 1000.0:.2f}', 'kN'],
                       ['Separation margin', f'{diagram["separationMargin"]:+.3f}', '-'],
                       ['Bolt yield margin', f'{diagram["yieldMargin"]:+.3f}', '-']]
        lines.append(formatReportTable(preloadRows, ['Quantity', 'Value', 'Unit'],
                                       title = f'Preload, {self.preloadMethod} control'))

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
            with open(os.path.join(outputDir, 'boltedJoint.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the joint geometry is physical.
        '''

        context = createErrorContext(component = 'BoltedJoint')

        if not np.isfinite(self.boltDiameter) or self.boltDiameter <= 0.0:
            raise InvalidInputError('Bolt diameter must be positive.', context = context)

        if not np.isfinite(self.gripLength) or self.gripLength <= 0.0:
            raise InvalidInputError('Grip length must be positive.', context = context)

        if not 0.0 < self.preloadFraction < 1.0:
            raise InvalidInputError(
                f'Preload fraction must be in (0, 1), got {self.preloadFraction}.',
                context = context)

        if np.isfinite(self.edgeDistance) and self.edgeDistance <= self.boltDiameter / 2.0:
            raise GeometryError(
                f'Edge distance {self.edgeDistance * 1000.0:.2f} mm is inside the hole radius. '
                f'There is no material to shear out.', context = context)

        if np.isfinite(self.pitch) and self.pitch <= self.boltDiameter:
            raise GeometryError(
                f'Pitch {self.pitch * 1000.0:.2f} mm is not greater than the bolt diameter. The '
                f'holes overlap.', context = context)
