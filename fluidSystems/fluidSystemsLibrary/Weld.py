
# -- Weld Class Definition -- #

'''

Weld joint design, strength derating, and inspection requirement.

A weld is the best joint in a fluid system: it has the lowest leak rate, the lowest pressure drop,
the lowest mass and the fewest failure modes of any option available. It is also permanent, which
means every welded joint is a commitment, and it means the design has to be right the first time
because there is no adjustment after the fact.

The three questions this class answers:

1. **How much strength is left?** A weld is not parent metal. The joint efficiency factor E accounts
   for the fabrication process and inspection level, and the heat affected zone knockdown accounts
   for what the thermal cycle did to the base material. For 6061-T6 aluminum those two together
   remove more than half the strength, and a design that used parent metal properties is wrong by a
   factor of two.

2. **Will it crack?** Austenitic stainless welds solidify with a ferrite content that depends on the
   composition, and too little ferrite causes hot cracking during solidification while too much
   embrittles the joint at cryogenic temperature. The WRC-1992 diagram predicts it from the chromium
   and nickel equivalents.

3. **What inspection is required?** Set by the pressure class, the fluid hazard and the governing
   code, not by preference.

The class does not attempt to model the weld thermally or metallurgically in any detail. It captures
the design decisions that a fluid system engineer actually makes and the derating factors that get
forgotten.

See Also:
---------
Fitting : The demountable alternative
Line    : The pressure design the weld has to survive
Leak    : Why a welded joint is preferred where leak rate matters

Theory: docs/Welds.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (applyInputs, formatReportTable, materialProperties, b31_3WallThickness,
                       hoopStressCalculator, InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (applyInputs, formatReportTable, materialProperties, b31_3WallThickness,
                        hoopStressCalculator, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Weld joint types and the quality factor each can achieve.
#
#   jointEfficiency   ASME B31.3 quality factor E for the joint, at the stated inspection level
#   inspectable       whether the joint can be volumetrically inspected (radiography or UT)
#   stressConcentration  geometric stress concentration factor at the toe, for fatigue assessment
#
# The critical distinction is between joints that can be volumetrically inspected and joints that
# cannot. A full penetration butt weld with a backing purge can be radiographed and can carry E = 1.0.
# A socket weld or a fillet weld cannot be volumetrically inspected at all, so it carries a permanent
# efficiency penalty and a fatigue penalty regardless of how well it was made.
WELD_JOINT_TYPES = {
    'butt full penetration': {
        'jointEfficiency': 1.00, 'inspectable': True, 'stressConcentration': 1.2,
        'description': 'Full penetration groove weld between two aligned members. The reference joint.',
        'notes': 'Requires a back purge on stainless and nickel alloys or the root oxidizes ("sugars"), which '
                 'produces a rough, particle-shedding internal surface and a crack initiation site. The purge '
                 'is not optional on a fluid system weld.'
    },
    'butt full penetration no rt': {
        'jointEfficiency': 0.85, 'inspectable': False, 'stressConcentration': 1.2,
        'description': 'Full penetration groove weld with visual inspection only.',
        'notes': 'Same joint, no volumetric inspection, and B31.3 charges 15 percent of the allowable stress '
                 'for the privilege. On a mass-critical vehicle it is almost always cheaper to pay for the '
                 'radiography than to carry the wall.'
    },
    'socket': {
        'jointEfficiency': 0.80, 'inspectable': False, 'stressConcentration': 2.1,
        'description': 'Tube inserted into a socket and fillet welded at the outside.',
        'notes': 'Fast and forgiving to fit up, and it leaves an unwelded annular crevice at the root. That '
                 'crevice traps fluid, cannot be cleaned, cannot be inspected, and is a crack initiation site '
                 'under thermal cycling. Do not use it in a fatigue or cleanliness critical system.'
    },
    'fillet': {
        'jointEfficiency': 0.60, 'inspectable': False, 'stressConcentration': 2.5,
        'description': 'Fillet weld at a lap or corner joint.',
        'notes': 'Structural attachments only. Not a pressure boundary joint on flight hardware.'
    },
    'tube to fitting': {
        'jointEfficiency': 1.00, 'inspectable': True, 'stressConcentration': 1.3,
        'description': 'Autogenous orbital weld between a tube and a weld-prep fitting.',
        'notes': 'The workhorse of a clean fluid system. Machine welded, highly repeatable, and the weld prep '
                 'geometry is designed so the joint is inspectable. Requires precise tube end preparation and '
                 'square, burr-free cuts.'
    },
    'sleeve': {
        'jointEfficiency': 0.85, 'inspectable': False, 'stressConcentration': 1.8,
        'description': 'External sleeve over a butted tube joint, welded at both ends.',
        'notes': 'A field repair joint. Accommodates poor fit-up but leaves an internal crevice.'
    },
    'electron beam': {
        'jointEfficiency': 1.00, 'inspectable': True, 'stressConcentration': 1.1,
        'description': 'Vacuum electron beam weld.',
        'notes': 'Very narrow heat affected zone, deep penetration in a single pass, minimal distortion. The '
                 'small HAZ is the real advantage: it minimizes the strength knockdown in precipitation '
                 'hardened alloys. Requires a vacuum chamber that fits the part.'
    },
    'friction stir': {
        'jointEfficiency': 0.95, 'inspectable': True, 'stressConcentration': 1.2,
        'description': 'Solid state joint made by a rotating tool.',
        'notes': 'No melting, so no solidification cracking and much less strength loss in aluminum than fusion '
                 'welding. Standard for large aluminum tank barrels. Requires heavy backing support and leaves '
                 'an exit hole that must be designed out.'
    }
}

# Heat affected zone strength knockdown factors, applied to the parent metal yield strength.
#
# This is the number that gets forgotten, and 6061-T6 is where it hurts. A precipitation hardened
# aluminum alloy loses its temper in the HAZ and does not recover without a full solution treat and
# age of the whole assembly, which is usually impossible after welding. The as-welded HAZ properties
# are the design properties.
HAZ_KNOCKDOWN = {
    '6061-T6':      {'yield': 0.55, 'ultimate': 0.65, 'recoverable': False,
                     'note': 'Loses temper in the HAZ. As-welded design allowable is roughly the O temper. '
                             'Post-weld solution treat and age recovers it but distorts the part.'},
    '7075-T73':     {'yield': 0.40, 'ultimate': 0.50, 'recoverable': False,
                     'note': 'Not considered weldable. Severe hot cracking susceptibility and no strength '
                             'recovery. Machine from solid or use a different alloy.'},
    '304L':         {'yield': 1.00, 'ultimate': 1.00, 'recoverable': True,
                     'note': 'Solid solution alloy, no strength to lose. The low carbon grade resists '
                             'sensitization during the weld thermal cycle.'},
    '316L':         {'yield': 1.00, 'ultimate': 1.00, 'recoverable': True,
                     'note': 'Solid solution alloy. Weld metal is typically slightly stronger than parent due '
                             'to the cast structure and the ferrite content.'},
    '321':          {'yield': 1.00, 'ultimate': 1.00, 'recoverable': True,
                     'note': 'Titanium stabilized against sensitization; preferred where the weld sees 700 to '
                             '1100 K service.'},
    'INCONEL 718':  {'yield': 0.55, 'ultimate': 0.70, 'recoverable': True,
                     'note': 'Precipitation hardened. Weld in the solution annealed condition and age the '
                             'assembly afterward to recover full properties. Welding in the aged condition '
                             'risks strain age cracking.'},
    'INCONEL 625':  {'yield': 1.00, 'ultimate': 1.00, 'recoverable': True,
                     'note': 'Solid solution strengthened and weldable with no post-weld heat treatment.'},
    'TI-6AL-4V':    {'yield': 0.90, 'ultimate': 0.95, 'recoverable': True,
                     'note': 'Weldable with full inert shielding of the weld, the HAZ and the back side. Any '
                             'oxygen or nitrogen pickup embrittles the joint irreversibly. Discoloration other '
                             'than light straw is a reject.'},
    'MONEL 400':    {'yield': 1.00, 'ultimate': 1.00, 'recoverable': True,
                     'note': 'Readily weldable.'}
}

# WRC-1992 constitution diagram coefficients for predicting the ferrite number of an austenitic
# stainless weld from its composition.
#
#   Cr_eq = Cr + Mo + 0.7*Nb
#   Ni_eq = Ni + 35*C + 20*N + 0.25*Cu
#
# Ferrite Number is then read from the diagram. The linear fit used here is a working approximation
# to the diagram over the range that matters for 300-series filler metals.
FERRITE_TARGET_MINIMUM = 3.0    # below this, solidification (hot) cracking risk rises sharply
FERRITE_TARGET_MAXIMUM = 10.0   # above this, cryogenic toughness and corrosion resistance suffer

# Inspection level required by pressure class and fluid hazard.
INSPECTION_LEVELS = {
    'visual':                {'coverage': 1.00, 'detectableFlaw': 1.0e-3,
                              'description': 'Visual examination of the completed weld, per AWS D17.1.'},
    'penetrant':             {'coverage': 1.00, 'detectableFlaw': 2.0e-4,
                              'description': 'Liquid penetrant examination. Surface breaking flaws only.'},
    'radiography':           {'coverage': 1.00, 'detectableFlaw': 5.0e-4,
                              'description': 'Volumetric X-ray or gamma examination. Good for volumetric flaws '
                                             '(porosity, inclusions), poor for tight planar cracks aligned '
                                             'with the beam.'},
    'ultrasonic':            {'coverage': 1.00, 'detectableFlaw': 2.0e-4,
                              'description': 'Volumetric ultrasonic examination. Good for planar flaws, which '
                                             'is exactly what radiography misses. Requires a trained operator '
                                             'and a calibration block.'},
    'radiography and penetrant': {'coverage': 1.00, 'detectableFlaw': 2.0e-4,
                              'description': 'Combined volumetric and surface examination. The standard for '
                                             'flight pressure boundary welds.'}
}

class Weld:

    '''

    Weld joint design, derating and inspection requirement.

    Primary Input Properties:
    -------------------------
    jointType : str
        Key into WELD_JOINT_TYPES
    material : str
        Parent material, key into materialProperties and HAZ_KNOCKDOWN
    outerDiameter : float
        Tube or pipe outer diameter at the joint [m]
    wallThickness : float
        Parent wall thickness [m]
    designPressure : float
        Maximum expected operating pressure [Pa, gauge]
    designTemperature : float
        Service temperature [K]
    fluidHazard : str
        'inert', 'flammable', 'toxic' or 'oxidizer'. Drives the inspection requirement.
    postWeldHeatTreat : bool
        Whether the assembly will be post-weld heat treated
    chromium / nickel / molybdenum / carbon / niobium / nitrogen / copper : float
        Weld metal composition in weight percent, for the ferrite prediction

    Key Output Properties:
    ----------------------
    jointEfficiency : float
        Effective E for the joint [-]
    hazYieldStrength / hazUltimateStrength : float
        Derated heat affected zone strength [Pa]
    allowableStress : float
        Design allowable at the weld [Pa]
    allowablePressure : float
        Maximum pressure the joint can carry at the given wall [Pa]
    pressureMargin : float
        allowablePressure / designPressure [-]
    ferriteNumber : float
        Predicted WRC-1992 ferrite number [-]
    requiredInspection : str
        Key into INSPECTION_LEVELS

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    calculateDerating()            Joint efficiency and HAZ knockdown
    calculateAllowablePressure()   Pressure capability of the derated joint
    calculateFerriteNumber()       WRC-1992 ferrite prediction for austenitic stainless
    selectInspection()             Required inspection level from pressure and hazard
    generateReport(outputDir)      Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Joint Definition -- #

        self.jointType           = 'tube to fitting'  # key into WELD_JOINT_TYPES
        self.material            = '316L'             # parent material
        self.outerDiameter       = np.nan  # [m]
        self.wallThickness       = np.nan  # [m]
        self.postWeldHeatTreat   = False   # [-]

        # -- Service Conditions -- #

        self.designPressure      = np.nan  # [Pa, gauge]
        self.designTemperature   = 293.15  # [K]
        self.fluidHazard         = 'inert' # 'inert' / 'flammable' / 'toxic' / 'oxidizer'
        self.pressureCycles      = 0       # [-], expected pressure cycles over life

        # -- Weld Metal Composition [weight percent] -- #
        # Defaults are nominal ER316L filler.
        self.chromium            = 18.5    # [wt %]
        self.nickel              = 12.0    # [wt %]
        self.molybdenum          = 2.5     # [wt %]
        self.carbon              = 0.02    # [wt %]
        self.niobium             = 0.0     # [wt %]
        self.nitrogen            = 0.05    # [wt %]
        self.copper              = 0.2     # [wt %]

        # -- Results -- #

        self.jointEfficiency     = np.nan  # [-]
        self.hazYieldStrength    = np.nan  # [Pa]
        self.hazUltimateStrength = np.nan  # [Pa]
        self.parentAllowable     = np.nan  # [Pa]
        self.allowableStress     = np.nan  # [Pa]
        self.allowablePressure   = np.nan  # [Pa]
        self.actualHoopStress    = np.nan  # [Pa]
        self.pressureMargin      = np.nan  # [-]
        self.requiredWallThickness = np.nan  # [m]
        self.chromiumEquivalent  = np.nan  # [wt %]
        self.nickelEquivalent    = np.nan  # [wt %]
        self.ferriteNumber       = np.nan  # [-]
        self.requiredInspection  = ''      # key into INSPECTION_LEVELS
        self.designNotes         = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: jointType, material, outerDiameter, wallThickness.

        '''

        requiredParams = {
            'jointType':     'Weld joint type not provided.',
            'material':      'Parent material not provided.',
            'outerDiameter': 'Joint outer diameter not provided.',
            'wallThickness': 'Parent wall thickness not provided.'
        }

        optionalParams = ['designPressure', 'designTemperature', 'fluidHazard', 'postWeldHeatTreat',
                          'pressureCycles', 'chromium', 'nickel', 'molybdenum', 'carbon',
                          'niobium', 'nitrogen', 'copper']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateDerating(self) -> dict:

        '''

        Joint efficiency and heat affected zone strength knockdown.

        Two independent derating mechanisms, and both apply:

        **Joint efficiency E.** A code factor that accounts for the fabrication process and the
        inspection level. It is not a material property; it is a statement about how confident the
        code is that the joint has no undetected flaws. A radiographed full penetration butt weld
        gets E = 1.0. The same weld without radiography gets 0.85. A socket weld gets 0.80 and
        cannot be improved by inspection, because it cannot be volumetrically inspected at all.

        **HAZ knockdown.** What the weld thermal cycle did to the base metal. Zero for solid solution
        alloys (304L, 316L, 625) because there is no precipitation structure to destroy. Severe for
        precipitation hardened alloys: 6061-T6 keeps about 55 percent of its yield strength, and it
        does not come back without a full solution treat and age of the whole assembly.

        The two multiply. A 6061-T6 socket weld carries 0.80 x 0.55 = 44 percent of the parent metal
        allowable, and a design that used parent metal properties is wrong by a factor of 2.3.

        '''

        jointData    = WELD_JOINT_TYPES[self.jointType.strip().lower()]
        materialKey  = self.material.strip().upper()

        self.jointEfficiency = jointData['jointEfficiency']

        parentProperties     = materialProperties(self.material, self.designTemperature)
        self.parentAllowable = parentProperties['allowableStress']

        knockdown = HAZ_KNOCKDOWN.get(materialKey)
        if knockdown is None:
            self.designNotes.append(
                f'No HAZ knockdown data for {self.material}. Assuming no strength loss, which is optimistic for '
                f'any precipitation hardened alloy. Verify against the material specification.')
            yieldFactor, ultimateFactor = 1.0, 1.0
        else:
            yieldFactor    = knockdown['yield']
            ultimateFactor = knockdown['ultimate']

            # Post-weld heat treatment recovers the knockdown where the alloy allows it
            if self.postWeldHeatTreat and knockdown['recoverable']:
                yieldFactor, ultimateFactor = 1.0, 1.0
                self.designNotes.append(
                    f'Post-weld heat treatment assumed to fully recover {self.material} HAZ properties. This is only '
                    f'true if the entire assembly sees the correct thermal cycle; a local stress relief does not '
                    f'restore precipitation strength.')
            elif self.postWeldHeatTreat and not knockdown['recoverable']:
                self.designNotes.append(
                    f'{self.material} HAZ properties are NOT recoverable by post-weld heat treatment in a practical '
                    f'assembly. The knockdown stands.')

            self.designNotes.append(knockdown['note'])

        self.hazYieldStrength    = parentProperties['yieldStrength']    * yieldFactor
        self.hazUltimateStrength = parentProperties['ultimateStrength'] * ultimateFactor

        # Design allowable at the weld: the code allowable basis applied to the derated properties,
        # then multiplied by the joint efficiency.
        hazAllowable         = min(2.0 / 3.0 * self.hazYieldStrength, self.hazUltimateStrength / 3.5)
        self.allowableStress = hazAllowable * self.jointEfficiency

        return {
            'jointEfficiency':     self.jointEfficiency,
            'hazYieldFactor':      yieldFactor,
            'hazUltimateFactor':   ultimateFactor,
            'parentAllowable':     self.parentAllowable,
            'allowableStress':     self.allowableStress,
            'totalDerating':       self.allowableStress / self.parentAllowable
        }

    def calculateAllowablePressure(self) -> float:

        '''

        Maximum pressure the derated joint can carry at the given wall thickness, and the wall
        thickness that would be required at the design pressure.

        Uses the B31.3 straight-pipe relation with the weld allowable stress substituted for the
        parent allowable, which is the correct treatment: the weld is the governing section.

        '''

        if np.isnan(self.allowableStress):
            self.calculateDerating()

        innerDiameter = self.outerDiameter - 2.0 * self.wallThickness

        # Invert the B31.3 relation for pressure at the actual wall
        #   t = P*D / (2*(S*E + P*Y))    ->    P = 2*S*E*t / (D - 2*Y*t)
        coefficientY           = 0.4
        self.allowablePressure = (2.0 * self.allowableStress * self.wallThickness /
                                  (self.outerDiameter - 2.0 * coefficientY * self.wallThickness))

        if not np.isnan(self.designPressure):
            self.pressureMargin    = self.allowablePressure / self.designPressure
            self.actualHoopStress  = hoopStressCalculator(self.designPressure, innerDiameter,
                                                          thickness = self.wallThickness)
            thicknessResult        = b31_3WallThickness(self.designPressure, self.outerDiameter,
                                                        self.allowableStress / self.jointEfficiency,
                                                        jointEfficiency = self.jointEfficiency,
                                                        millTolerance   = 0.0)
            self.requiredWallThickness = thicknessResult['pressureDesignThickness']

            if self.pressureMargin < 1.0:
                self.designNotes.append(
                    f'The weld cannot carry the design pressure at this wall thickness. Required wall is '
                    f'{self.requiredWallThickness * 1.0e3:.4f} mm against an actual {self.wallThickness * 1.0e3:.4f} mm.')

        # Fatigue advisory. A joint with a stress concentration and a meaningful cycle count needs a
        # fatigue assessment that this class does not perform.
        jointData = WELD_JOINT_TYPES[self.jointType.strip().lower()]
        if self.pressureCycles > 1000 and jointData['stressConcentration'] > 1.5:
            self.designNotes.append(
                f'{self.pressureCycles} pressure cycles on a joint with a stress concentration factor of '
                f'{jointData["stressConcentration"]:.1f} needs a fatigue assessment. This class checks static '
                f'strength only. Weld toe cracking is a fatigue failure, not a strength failure.')

        return self.allowablePressure

    def calculateFerriteNumber(self) -> dict:

        '''

        WRC-1992 ferrite number prediction for an austenitic stainless weld.

        Austenitic stainless weld metal solidifies with some fraction of delta ferrite in an
        austenite matrix, and the amount matters in both directions:

        **Too little ferrite (below FN 3)** and the weld is susceptible to solidification cracking.
        Fully austenitic solidification concentrates sulfur and phosphorus in the last liquid to
        freeze, which forms low-melting films along the grain boundaries and tears under the
        contraction strain. This is why filler metals are deliberately over-alloyed in chromium
        relative to the base metal.

        **Too much ferrite (above FN 10)** and the weld loses cryogenic toughness, because ferrite
        has a ductile-to-brittle transition and austenite does not. It also becomes vulnerable to
        sigma phase embrittlement if the joint sees elevated temperature service.

        For cryogenic service, target FN 3 to 8. For hot gas service, target the low end to reduce
        sigma phase risk.

            Cr_eq = Cr + Mo + 0.7*Nb
            Ni_eq = Ni + 35*C + 20*N + 0.25*Cu

        The ferrite number is then read from the WRC-1992 diagram. The relation used here is a linear
        working fit valid over the 300-series filler range and should be treated as indicative;
        measure the actual ferrite number with a Feritscope on a procedure qualification coupon.

        '''

        self.chromiumEquivalent = self.chromium + self.molybdenum + 0.7 * self.niobium
        self.nickelEquivalent   = self.nickel + 35.0 * self.carbon + 20.0 * self.nitrogen + 0.25 * self.copper

        # Working linear fit to the WRC-1992 diagram over the 300-series range. Ferrite rises with
        # the chromium equivalent and falls with the nickel equivalent, with the zero-ferrite
        # boundary running roughly along Ni_eq = 0.75*Cr_eq - 0.25.
        self.ferriteNumber = max(0.0, 3.34 * (self.chromiumEquivalent - 1.30 * self.nickelEquivalent - 1.55))

        if self.ferriteNumber < FERRITE_TARGET_MINIMUM:
            self.designNotes.append(
                f'Predicted ferrite number {self.ferriteNumber:.1f} is below the {FERRITE_TARGET_MINIMUM:.0f} FN '
                f'minimum. Solidification cracking risk. Use a filler with a higher chromium equivalent '
                f'(ER308L rather than ER316L, or ER309L for dissimilar joints).')
        elif self.ferriteNumber > FERRITE_TARGET_MAXIMUM:
            self.designNotes.append(
                f'Predicted ferrite number {self.ferriteNumber:.1f} exceeds the {FERRITE_TARGET_MAXIMUM:.0f} FN '
                f'maximum. Reduced cryogenic toughness and sigma phase risk at elevated temperature.')

        if self.designTemperature < 150.0 and self.ferriteNumber > 8.0:
            self.designNotes.append(
                f'Cryogenic service at {self.designTemperature:.0f} K with FN {self.ferriteNumber:.1f}. Ferrite has a '
                f'ductile to brittle transition and austenite does not; target FN 3 to 8 for cryogenic welds.')

        return {
            'chromiumEquivalent': self.chromiumEquivalent,
            'nickelEquivalent':   self.nickelEquivalent,
            'ferriteNumber':      self.ferriteNumber
        }

    def selectInspection(self) -> str:

        '''

        Required inspection level from pressure class, fluid hazard and joint inspectability.

        The logic follows normal aerospace fluid system practice rather than a single code clause:

        - Any pressure boundary weld gets at least visual plus penetrant.
        - A hazardous fluid (toxic, flammable or oxidizer) pressure boundary gets volumetric
          inspection.
        - A high pressure joint (above 10 MPa) gets volumetric inspection.
        - A joint that cannot be volumetrically inspected in a service that requires it is flagged,
          because the answer there is to change the joint design, not to change the inspection plan.

        Radiography and ultrasonic examination find different flaws. Radiography is good at
        volumetric defects (porosity, slag, incomplete fill) and poor at tight planar cracks aligned
        with the beam. Ultrasonic is the reverse. Where the consequence of a missed crack is severe,
        specify both, or specify radiography plus penetrant so surface-breaking cracks are caught by
        the penetrant.

        '''

        jointData = WELD_JOINT_TYPES[self.jointType.strip().lower()]

        hazardous       = self.fluidHazard.strip().lower() in ('toxic', 'flammable', 'oxidizer')
        highPressure    = (not np.isnan(self.designPressure)) and self.designPressure > 10.0e6
        volumetricNeeded = hazardous or highPressure

        if volumetricNeeded:
            if jointData['inspectable']:
                self.requiredInspection = 'radiography and penetrant'
            else:
                self.requiredInspection = 'penetrant'
                self.designNotes.append(
                    f'A {self.jointType} joint cannot be volumetrically inspected, and this service '
                    f'({self.fluidHazard}'
                    f'{", " + format(self.designPressure / 1.0e6, ".1f") + " MPa" if not np.isnan(self.designPressure) else ""}) '
                    f'requires it. Change the joint to a full penetration butt or tube-to-fitting weld.')
        else:
            self.requiredInspection = 'penetrant'

        if self.fluidHazard.strip().lower() == 'oxidizer':
            self.designNotes.append(
                'Oxidizer service: the weld root must be smooth and free of oxide. A sugared or spattered root '
                'sheds particles into the flow, and a particle in a high velocity oxygen stream is an ignition '
                'source. Verify the internal surface by borescope, not only by radiography.')

        return self.requiredInspection

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        jointData = WELD_JOINT_TYPES[self.jointType.strip().lower()]

        rows = [
            ['Joint type',           f'{self.jointType}'],
            ['Description',          f'{jointData["description"]}'],
            ['Parent material',      f'{self.material}'],
            ['Outer diameter',       f'{self.outerDiameter * 1.0e3:.4f} mm'],
            ['Wall thickness',       f'{self.wallThickness * 1.0e3:.4f} mm'],
            ['Design temperature',   f'{self.designTemperature:.1f} K'],
            ['Fluid hazard class',   f'{self.fluidHazard}'],
            ['Post-weld heat treat', f'{self.postWeldHeatTreat}'],
            ['Joint efficiency E',   f'{self.jointEfficiency:.3f}'],
            ['Stress concentration', f'{jointData["stressConcentration"]:.2f}'],
            ['Parent allowable',     f'{self.parentAllowable / 1.0e6:.2f} MPa'],
            ['HAZ yield',            f'{self.hazYieldStrength / 1.0e6:.2f} MPa'],
            ['HAZ ultimate',         f'{self.hazUltimateStrength / 1.0e6:.2f} MPa'],
            ['Weld allowable stress', f'{self.allowableStress / 1.0e6:.2f} MPa'],
            ['Total derating',       f'{self.allowableStress / self.parentAllowable:.3f}']
        ]

        if not np.isnan(self.allowablePressure):
            rows.append(['Allowable pressure',   f'{self.allowablePressure / 1.0e6:.3f} MPa'])
        if not np.isnan(self.designPressure):
            rows.append(['Design pressure',      f'{self.designPressure / 1.0e6:.3f} MPa'])
            rows.append(['Pressure margin',      f'{self.pressureMargin:.3f}'])
            rows.append(['Hoop stress at MEOP',  f'{self.actualHoopStress / 1.0e6:.2f} MPa'])
            rows.append(['Required wall',        f'{self.requiredWallThickness * 1.0e3:.4f} mm'])

        if not np.isnan(self.ferriteNumber):
            rows.append(['Chromium equivalent',  f'{self.chromiumEquivalent:.2f} wt %'])
            rows.append(['Nickel equivalent',    f'{self.nickelEquivalent:.2f} wt %'])
            rows.append(['Predicted ferrite FN', f'{self.ferriteNumber:.1f}'])

        if self.requiredInspection:
            rows.append(['Required inspection',  f'{self.requiredInspection}'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'WELD JOINT REPORT')

        report += f'\n\nJOINT NOTES\n{"-" * 60}\n{jointData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'weldReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.jointType.strip().lower() not in WELD_JOINT_TYPES:
            raise InvalidInputError(
                message       = f'Unknown weld joint type \'{self.jointType}\'.',
                parameterName = 'jointType', value = self.jointType,
                validRange    = str(sorted(WELD_JOINT_TYPES.keys()))
            )

        if self.wallThickness <= 0.0 or self.outerDiameter <= 0.0:
            raise InvalidInputError(
                message       = 'Joint outer diameter and wall thickness must be positive.',
                parameterName = 'outerDiameter/wallThickness',
                value         = (self.outerDiameter, self.wallThickness),
                validRange    = 'Both greater than 0 m'
            )

        if 2.0 * self.wallThickness >= self.outerDiameter:
            raise InvalidInputError(
                message       = 'Wall thickness is at least half the outer diameter, which leaves no bore.',
                parameterName = 'wallThickness', value = self.wallThickness,
                validRange    = f'Less than {self.outerDiameter / 2.0:.6g} m'
            )
