
# -- Fitting Class Definition -- #

'''

Fitting and connector selection, pressure loss, and installation torque.

Every fitting is a leak path. That is the governing fact, and it should drive the design: the
cheapest and most reliable joint is the one that is not there. Welded and brazed joints are used
wherever a joint is permanent, and mechanical fittings are used only where the system genuinely has
to come apart.

Where a mechanical joint is needed, the selection is a trade among five things:

    pressure and temperature capability
    leak tightness class achievable and repeatable
    reusability, the number of make and break cycles before the sealing surface is spent
    cleanliness compatibility, whether the joint can be cleaned and stay clean
    mass and envelope

This class covers the standard aerospace fitting families, computes the pressure loss each adds to
a line, and estimates installation torque from the preload required to seat the joint.

A note on torque. Torque is a proxy for preload, and it is a poor one: the fraction of applied
torque that becomes preload rather than friction depends on thread lubrication, plating, surface
finish and how many times the joint has been made up. The nut factor spread on a dry stainless
joint is easily 2 to 1. Where preload actually matters, control it by turns-past-finger-tight
(the FFFT method), by bolt stretch measurement, or by using a fitting family whose design is
preload-insensitive.

See Also:
---------
Seal   : The sealing element inside the fitting
Leak   : What the fitting leaks and how it is measured
Weld   : The permanent alternative to a fitting
Line   : Where the fitting pressure losses accumulate

Theory: docs/FittingsAndConnectors.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                       M_PER_IN, NM_PER_INLBF, PA_PER_PSIA,
                       InvalidInputError, CompatibilityError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable, materialProperties,
                        M_PER_IN, NM_PER_INLBF, PA_PER_PSIA,
                        InvalidInputError, CompatibilityError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Fitting family data.
#
#   lossCoefficient      K for a union of this type in a straight run
#   pressureRating       typical working pressure for small bore in 316L [Pa]. Falls with size.
#   maximumTemperature   practical upper service temperature [K]
#   minimumTemperature   practical lower service temperature [K]
#   reuseCycles          make and break cycles before the sealing surface must be renewed
#   leakClass            typical achievable helium leak rate [scc/s]
#   nutFactor            torque coefficient K in T = K * F * d, dry stainless unless noted
#   sealingElement       what actually does the sealing
#
# The leakClass column is the one people skip and should not. A flare fitting and a metal gasket
# face seal are three orders of magnitude apart in achievable leak rate, and no amount of torque
# closes that gap.
FITTING_TYPES = {
    'an flare': {
        'lossCoefficient': 0.20, 'pressureRating': 20.7e6, 'maximumTemperature': 700.0,
        'minimumTemperature': 20.0, 'reuseCycles': 25, 'leakClass': 1.0e-4, 'nutFactor': 0.20,
        'sealingElement': 'metal to metal, 37 degree flare',
        'standard': 'AS4395 / MS33656 / AN818',
        'notes': 'The aerospace workhorse. Reusable, inspectable, cryogenic capable. Requires a properly '
                 'formed flare; a cracked or eccentric flare is the most common leak source in any system.'
    },
    'flareless': {
        'lossCoefficient': 0.25, 'pressureRating': 20.7e6, 'maximumTemperature': 550.0,
        'minimumTemperature': 77.0, 'reuseCycles': 10, 'leakClass': 1.0e-4, 'nutFactor': 0.20,
        'sealingElement': 'bite-type ferrule into the tube OD',
        'standard': 'MS21902 / AS5852',
        'notes': 'No flaring operation required. The ferrule permanently deforms the tube, so the tube end '
                 'is consumed on first assembly and the joint is only reusable onto its own ferrule.'
    },
    'compression': {
        'lossCoefficient': 0.25, 'pressureRating': 40.0e6, 'maximumTemperature': 800.0,
        'minimumTemperature': 4.0, 'reuseCycles': 25, 'leakClass': 1.0e-6, 'nutFactor': 0.18,
        'sealingElement': 'two-ferrule swaging onto the tube OD',
        'standard': 'Swagelok, Parker CPI, Gyrolok (proprietary, not interchangeable)',
        'notes': 'Excellent leak tightness and very high pressure capability. Ferrules from one manufacturer '
                 'do not interchange with another manufacturer\'s bodies; mixing them is a known failure mode.'
    },
    'vcr': {
        'lossCoefficient': 0.15, 'pressureRating': 34.5e6, 'maximumTemperature': 920.0,
        'minimumTemperature': 4.0, 'reuseCycles': 100, 'leakClass': 4.0e-9, 'nutFactor': 0.18,
        'sealingElement': 'replaceable metal gasket between two beads',
        'standard': 'Swagelok VCR and equivalents',
        'notes': 'The best readily available leak tightness in a demountable joint. The gasket is consumed '
                 'each make-up, which is a feature: the sealing surface is renewed every time. Ultra high '
                 'purity and high vacuum standard.'
    },
    'vco': {
        'lossCoefficient': 0.18, 'pressureRating': 20.7e6, 'maximumTemperature': 500.0,
        'minimumTemperature': 220.0, 'reuseCycles': 50, 'leakClass': 1.0e-7, 'nutFactor': 0.18,
        'sealingElement': 'o-ring face seal',
        'standard': 'Swagelok VCO and equivalents',
        'notes': 'Elastomer face seal version of VCR. Easier and cheaper, but limited by the elastomer '
                 'temperature range and permeation.'
    },
    'sae boss': {
        'lossCoefficient': 0.30, 'pressureRating': 34.5e6, 'maximumTemperature': 450.0,
        'minimumTemperature': 220.0, 'reuseCycles': 25, 'leakClass': 1.0e-6, 'nutFactor': 0.20,
        'sealingElement': 'o-ring against a machined boss face',
        'standard': 'SAE J1926 / MS16142 / AS5202',
        'notes': 'Straight thread with an o-ring, not a tapered pipe thread. The thread carries the load and '
                 'the o-ring does the sealing, which is why it is repeatable where NPT is not.'
    },
    'npt': {
        'lossCoefficient': 0.35, 'pressureRating': 10.0e6, 'maximumTemperature': 550.0,
        'minimumTemperature': 220.0, 'reuseCycles': 3, 'leakClass': 1.0e-3, 'nutFactor': 0.25,
        'sealingElement': 'thread interference plus sealant',
        'standard': 'ASME B1.20.1',
        'notes': 'Tapered pipe thread. Seals by galling the threads together plus tape or paste. Not '
                 'repeatable, not clean, generates thread debris, and the sealant is a contamination source. '
                 'Acceptable on a ground test stand and nowhere else.'
    },
    'grayloc': {
        'lossCoefficient': 0.10, 'pressureRating': 100.0e6, 'maximumTemperature': 900.0,
        'minimumTemperature': 20.0, 'reuseCycles': 100, 'leakClass': 1.0e-8, 'nutFactor': 0.16,
        'sealingElement': 'metal seal ring, pressure energized',
        'standard': 'Grayloc, Destec, Techlok (proprietary)',
        'notes': 'Pressure-energized metal seal: higher internal pressure increases the sealing force. Compact '
                 'and very high pressure. The clamp hub design makes it the standard for large bore high '
                 'pressure test stand plumbing.'
    },
    'conflat': {
        'lossCoefficient': 0.12, 'pressureRating': 1.0e6, 'maximumTemperature': 720.0,
        'minimumTemperature': 4.0, 'reuseCycles': 100, 'leakClass': 1.0e-10, 'nutFactor': 0.18,
        'sealingElement': 'knife edge into a soft copper gasket',
        'standard': 'ISO 3669 / ASTM F1836',
        'notes': 'Ultra high vacuum standard. Best achievable leak rate of any demountable joint, but low '
                 'internal pressure capability and a consumed copper gasket every make-up.'
    },
    'raised face flange': {
        'lossCoefficient': 0.08, 'pressureRating': 10.0e6, 'maximumTemperature': 800.0,
        'minimumTemperature': 220.0, 'reuseCycles': 50, 'leakClass': 1.0e-4, 'nutFactor': 0.20,
        'sealingElement': 'compressed gasket between raised faces',
        'standard': 'ASME B16.5',
        'notes': 'Large bore, ground systems. Bolt preload uniformity is everything; torque in a star pattern '
                 'in at least three passes.'
    },
    'quick disconnect': {
        'lossCoefficient': 2.00, 'pressureRating': 20.7e6, 'maximumTemperature': 400.0,
        'minimumTemperature': 20.0, 'reuseCycles': 500, 'leakClass': 1.0e-4, 'nutFactor': np.nan,
        'sealingElement': 'poppet seals plus an interface seal',
        'standard': 'various; MIL-C-25427 and vendor specific',
        'notes': 'High pressure loss and a much worse leak class than a made-up joint, in exchange for '
                 'operability. Every ground umbilical interface. Verify the disconnect force at pressure: a QD '
                 'that will not separate under pressure is a launch hold.'
    }
}

# AN/MS 37 degree flare fitting installation torque, in-lbf, for aluminum and steel tube by dash
# size. From MS33566 / AC 43.13-1B practice. Dash size is tube OD in sixteenths of an inch.
#
# These are the values to use, not a calculated preload. Flare fittings are torque-specified by the
# standard because the flare geometry sets the sealing stress and the torque is calibrated to it.
AN_FLARE_TORQUE_INLBF = {
    -2:  (20,   30),     # 1/8 in tube:  (minimum, maximum)
    -3:  (30,   40),     # 3/16 in
    -4:  (40,   65),     # 1/4 in
    -5:  (60,   80),     # 5/16 in
    -6:  (75,  125),     # 3/8 in
    -8:  (150, 250),     # 1/2 in
    -10: (200, 350),     # 5/8 in
    -12: (300, 500),     # 3/4 in
    -16: (500, 700),     # 1 in
    -20: (700, 900),     # 1-1/4 in
    -24: (800, 1000)     # 1-1/2 in
}

# Fluid compatibility exclusions that are hard stops, not preferences. Each of these has destroyed
# hardware. The class raises CompatibilityError rather than warning.
INCOMPATIBLE_COMBINATIONS = {
    ('TI-6AL-4V', 'OXYGEN'):   'Titanium is impact sensitive in oxygen and will burn. Never use titanium in LOX or GOX.',
    ('TI-6AL-4V', 'LOX'):      'Titanium is impact sensitive in oxygen and will burn. Never use titanium in LOX or GOX.',
    ('TI-6AL-4V', 'GOX'):      'Titanium is impact sensitive in oxygen and will burn. Never use titanium in LOX or GOX.',
    ('TI-6AL-4V', 'N2O4'):     'Titanium stress corrosion cracks in nitrogen tetroxide unless the NTO is nitric oxide inhibited, and even then it is not recommended.',
    ('6061-T6',  'N2O4'):      'Aluminum corrodes rapidly in nitrogen tetroxide above about 60 degC.',
    ('MONEL 400', 'N2H4'):     'Copper-bearing alloys catalyze hydrazine decomposition. Monel is copper bearing.'
}

class Fitting:

    '''

    Selection, pressure loss and installation torque for a mechanical joint.

    Primary Input Properties:
    -------------------------
    fittingType : str
        Key into FITTING_TYPES
    tubeOuterDiameter : float
        Tube OD [m]. Sets the dash size and the torque lookup.
    tubeInnerDiameter : float
        Tube ID [m]. Sets the reference area for the loss coefficient.
    quantity : int
        Number of fittings of this type in the run
    designPressure : float
        Maximum expected operating pressure [Pa]
    designTemperature : float
        Service temperature [K]
    fluid : str
        Service fluid, for the compatibility check
    material : str
        Fitting body material, key into materialProperties
    massFlow : float
        Mass flow rate [kg/s], for the pressure loss calculation
    density : float
        Fluid density [kg/m^3]. Computed from fluid, pressure and temperature if not given.

    Key Output Properties:
    ----------------------
    totalLossCoefficient : float
        Summed K for all fittings of this type [-]
    pressureLoss : float
        Total pressure loss through the fittings [Pa]
    torqueRange : tuple
        (minimum, maximum) installation torque [N-m]
    pressureMargin : float
        Rating divided by design pressure [-]
    leakRateEstimate : float
        Expected total helium leak rate from all joints [scc/s]

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    checkCompatibility()           Material, fluid and temperature screening
    calculatePressureLoss()        Loss through the fittings
    calculateTorque()              Installation torque range
    compareTypes(candidates)       Side by side selection table
    generateReport(outputDir)      Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Joint Definition -- #

        self.fittingType         = 'an flare'  # key into FITTING_TYPES
        self.tubeOuterDiameter   = np.nan      # [m]
        self.tubeInnerDiameter   = np.nan      # [m]
        self.quantity            = 1           # [-], number of this fitting in the run
        self.material            = '316L'      # key into materialProperties

        # -- Service Conditions -- #

        self.fluid               = ''          # [case sensitive string]
        self.designPressure      = np.nan      # [Pa, absolute]
        self.designTemperature   = 293.15      # [K]
        self.massFlow            = np.nan      # [kg/s]
        self.density             = np.nan      # [kg/m^3], overrides the property lookup

        # -- Results -- #

        self.dashSize            = np.nan      # [-], tube OD in sixteenths of an inch
        self.totalLossCoefficient = np.nan     # [-]
        self.pressureLoss        = np.nan      # [Pa]
        self.velocity            = np.nan      # [m/s]
        self.torqueRange         = (np.nan, np.nan)  # [N-m]
        self.pressureMargin      = np.nan      # [-]
        self.leakRateEstimate    = np.nan      # [scc/s helium]
        self.compatibilityNotes  = []          # [list of str], service-specific cautions
        self.generalNotes        = []          # [list of str], apply regardless of fitting family

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fittingType, tubeOuterDiameter.

        '''

        requiredParams = {
            'fittingType':       'Fitting type not provided.',
            'tubeOuterDiameter': 'Tube outer diameter not provided.'
        }

        optionalParams = ['tubeInnerDiameter', 'quantity', 'material', 'fluid', 'designPressure',
                          'designTemperature', 'massFlow', 'density']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        # Dash size is tube OD in sixteenths of an inch, the universal aerospace fitting size unit
        self.dashSize = int(round(self.tubeOuterDiameter / M_PER_IN * 16.0))

    def checkCompatibility(self) -> list:

        '''

        Screen the joint against the service conditions.

        Four checks, in order of how badly they end when missed:

        1. Material and fluid compatibility, from the hard-stop exclusion list. Raises.
        2. Temperature range of the fitting family. Raises if outside.
        3. Pressure rating against design pressure. Raises if the margin is below 1.0, warns below 1.5.
        4. Leak class against a hazardous fluid. Warns.

        Returns the list of advisory notes; hard failures raise CompatibilityError.

        '''

        self.compatibilityNotes = []
        fittingData             = FITTING_TYPES[self.fittingType.strip().lower()]

        # -- 1. Material and fluid -- #
        if self.fluid:
            key = (self.material.strip().upper(), self.fluid.strip().upper())
            if key in INCOMPATIBLE_COMBINATIONS:
                raise CompatibilityError(
                    message  = INCOMPATIBLE_COMBINATIONS[key],
                    material = self.material,
                    fluid    = self.fluid
                )

        # -- 2. Temperature -- #
        if self.designTemperature > fittingData['maximumTemperature']:
            raise CompatibilityError(
                message = (f'{self.fittingType} is rated to {fittingData["maximumTemperature"]:.0f} K and the '
                           f'service temperature is {self.designTemperature:.0f} K. The sealing element '
                           f'({fittingData["sealingElement"]}) will not survive.'),
                context = createErrorContext(component = 'Fitting', fluid = self.fluid,
                                             temperature = self.designTemperature),
                material = self.material, fluid = self.fluid
            )

        if self.designTemperature < fittingData['minimumTemperature']:
            raise CompatibilityError(
                message = (f'{self.fittingType} is rated down to {fittingData["minimumTemperature"]:.0f} K and the '
                           f'service temperature is {self.designTemperature:.0f} K. Elastomer seals go glassy and '
                           f'lose all compliance below their glass transition; metal seals are usually the only option.'),
                context = createErrorContext(component = 'Fitting', fluid = self.fluid,
                                             temperature = self.designTemperature),
                material = self.material, fluid = self.fluid
            )

        # -- 3. Pressure -- #
        if not np.isnan(self.designPressure):

            # Small bore fittings carry their full rating; capability falls with size roughly as 1/d.
            # The reference size for the tabulated rating is 1/4 inch tube.
            sizeDerate          = min(1.0, (0.25 * M_PER_IN) / self.tubeOuterDiameter)
            deratedRating       = fittingData['pressureRating'] * sizeDerate
            self.pressureMargin = deratedRating / self.designPressure

            if self.pressureMargin < 1.0:
                raise CompatibilityError(
                    message = (f'{self.fittingType} at {self.tubeOuterDiameter / M_PER_IN:.3f} in OD is rated to '
                               f'{deratedRating / 1.0e6:.2f} MPa and the design pressure is '
                               f'{self.designPressure / 1.0e6:.2f} MPa.'),
                    context  = createErrorContext(component = 'Fitting', fluid = self.fluid,
                                                  upstreamPressure = self.designPressure,
                                                  rating = deratedRating),
                    material = self.material, fluid = self.fluid
                )

            if self.pressureMargin < 1.5:
                self.compatibilityNotes.append(
                    f'Pressure margin is only {self.pressureMargin:.2f}. Fitting ratings are working pressures '
                    f'with the manufacturer\'s own factor already applied, so this is tighter than it looks.')

        # -- 4. Leak class against hazard -- #
        hazardousFluids = ('N2H4', 'HYDRAZINE', 'MMH', 'N2O4', 'NTO', 'HYDROGEN', 'H2')
        if self.fluid.strip().upper() in hazardousFluids and fittingData['leakClass'] > 1.0e-5:
            self.compatibilityNotes.append(
                f'{self.fittingType} achieves about {fittingData["leakClass"]:.1e} scc/s He per joint, which is loose '
                f'for {self.fluid} service. Consider VCR or a welded joint.')

        # -- 5. Galling -- #
        # Kept in a separate list because it applies to every stainless joint regardless of fitting
        # family. Folding it into compatibilityNotes would flag every candidate in compareTypes and
        # make the status column useless.
        self.generalNotes = []
        if 'STAINLESS' in self.material.upper() or self.material.strip().upper() in ('304L', '316L', '321'):
            self.generalNotes.append(
                'Austenitic stainless threads gall against themselves. Use silver-plated nuts, a dissimilar '
                'hardness pair, or an approved anti-seize compatible with the service fluid.')

        return self.compatibilityNotes

    def calculatePressureLoss(self) -> float:

        '''

        Pressure loss through the fittings, referenced to the tube inner diameter.

            dP = K_total * rho * V^2 / 2

        Fittings are individually small and collectively large. A run with a dozen unions and a
        quick disconnect can easily carry more loss than the straight tube it connects, and it is
        the term most often left out of a first-pass pressure budget.

        '''

        if np.isnan(self.tubeInnerDiameter) or np.isnan(self.massFlow):
            raise InvalidInputError(
                message       = 'calculatePressureLoss needs the tube inner diameter and the mass flow rate.',
                parameterName = 'tubeInnerDiameter/massFlow',
                value         = (self.tubeInnerDiameter, self.massFlow),
                validRange    = 'Both positive real'
            )

        density = self.density
        if np.isnan(density):
            if not self.fluid or np.isnan(self.designPressure):
                raise InvalidInputError(
                    message       = 'calculatePressureLoss needs either an explicit density or a fluid with pressure and temperature.',
                    parameterName = 'density', value = density, validRange = 'Positive real'
                )
            density = float(fluidProps(self.fluid, 'TP', 'D', self.designTemperature, self.designPressure))

        flowArea      = np.pi * self.tubeInnerDiameter**2 / 4.0
        self.velocity = self.massFlow / (density * flowArea)

        fittingData               = FITTING_TYPES[self.fittingType.strip().lower()]
        self.totalLossCoefficient = fittingData['lossCoefficient'] * self.quantity
        self.pressureLoss         = self.totalLossCoefficient * density * self.velocity**2 / 2.0

        # Aggregate leak rate. Joints are statistically independent, so total leakage is the sum.
        self.leakRateEstimate = fittingData['leakClass'] * self.quantity

        return self.pressureLoss

    def calculateTorque(self) -> tuple:

        '''

        Installation torque range.

        For AN/MS 37 degree flare fittings the torque comes from the MS33566 table, because the
        standard specifies torque directly: the flare geometry sets the sealing stress and the
        tabulated torque is calibrated to produce it. Do not compute a preload for these; use the
        table.

        For everything else, torque is estimated from the required seating preload and a nut factor:

            T = K * F * d

        This is an estimate and should be treated as one. The nut factor spread on a dry stainless
        joint is easily 2 to 1 depending on lubrication, plating and make-up history, which means
        the preload spread is the same. Where preload actually matters, use turns-past-finger-tight
        or the manufacturer's specified procedure instead.

        Compression fittings in particular are NOT torque specified: they are specified by turns
        past finger tight (typically 1-1/4 turns on initial make-up, and much less on remake). A
        torque wrench on a Swagelok fitting is the wrong tool.

        '''

        fittingKey  = self.fittingType.strip().lower()
        fittingData = FITTING_TYPES[fittingKey]

        # -- AN/MS flare: use the standard table -- #
        if fittingKey == 'an flare':
            dashKey = -abs(self.dashSize)
            if dashKey in AN_FLARE_TORQUE_INLBF:
                minimumInLbf, maximumInLbf = AN_FLARE_TORQUE_INLBF[dashKey]
                self.torqueRange = (minimumInLbf * NM_PER_INLBF, maximumInLbf * NM_PER_INLBF)
                return self.torqueRange
            print(f'Warning: no MS33566 torque entry for dash size {self.dashSize}. Falling back to the preload estimate.')

        # -- Compression fittings are not torque specified -- #
        if fittingKey == 'compression':
            self.torqueRange = (np.nan, np.nan)
            print('Compression fittings are specified by turns past finger tight (typically 1-1/4 turns on '
                  'initial make-up), not by torque. No torque value is returned.')
            return self.torqueRange

        nutFactor = fittingData['nutFactor']
        if np.isnan(nutFactor):
            self.torqueRange = (np.nan, np.nan)
            return self.torqueRange

        # Required preload: enough to hold the pressure end load plus a seating margin. A factor of
        # 2 on the pressure end load is the conventional gasket seating allowance.
        if np.isnan(self.designPressure):
            raise InvalidInputError(
                message       = 'calculateTorque needs a design pressure to estimate the required preload.',
                parameterName = 'designPressure', value = self.designPressure, validRange = 'Positive real'
            )

        sealingDiameter = self.tubeOuterDiameter
        pressureEndLoad = self.designPressure * np.pi * sealingDiameter**2 / 4.0
        requiredPreload = 2.0 * pressureEndLoad

        # Thread pitch diameter is approximately the tube OD plus one thread size for a typical
        # aerospace fitting nut, which is where the torque acts.
        threadDiameter = sealingDiameter * 1.4

        nominalTorque    = nutFactor * requiredPreload * threadDiameter
        self.torqueRange = (0.8 * nominalTorque, 1.2 * nominalTorque)

        return self.torqueRange

    def compareTypes(self, candidates: list = None) -> str:

        '''

        Side by side selection table for the candidate fitting families at the current service
        conditions, with the ones that fail a compatibility check marked.

        This is the call that actually answers 'which fitting should I use here'. The individual
        numbers are all in the FITTING_TYPES table; what this does is put them next to each other
        with the service conditions applied so the trade is visible in one place.

        '''

        if candidates is None:
            candidates = list(FITTING_TYPES.keys())

        savedType = self.fittingType
        rows      = []

        for candidate in candidates:

            fittingData = FITTING_TYPES[candidate]
            self.fittingType = candidate

            status = 'OK'
            try:
                self.checkCompatibility()
            except CompatibilityError as error:
                status = 'FAIL'
            else:
                if self.compatibilityNotes:
                    status = 'CAUTION'

            sizeDerate    = min(1.0, (0.25 * M_PER_IN) / self.tubeOuterDiameter) if not np.isnan(self.tubeOuterDiameter) else 1.0
            deratedRating = fittingData['pressureRating'] * sizeDerate

            rows.append([
                candidate,
                f'{deratedRating / 1.0e6:.1f}',
                f'{fittingData["minimumTemperature"]:.0f}-{fittingData["maximumTemperature"]:.0f}',
                f'{fittingData["leakClass"]:.0e}',
                f'{fittingData["reuseCycles"]:d}',
                f'{fittingData["lossCoefficient"]:.2f}',
                status
            ])

        self.fittingType = savedType

        return formatReportTable(rows,
                                 ['Type', 'Rating [MPa]', 'Temp [K]', 'Leak [scc/s]', 'Reuse', 'K', 'Status'],
                                 title = f'FITTING SELECTION COMPARISON  (fluid = {self.fluid or "unspecified"}, '
                                         f'P = {self.designPressure / 1.0e6 if not np.isnan(self.designPressure) else 0:.2f} MPa, '
                                         f'T = {self.designTemperature:.0f} K)')

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        fittingData = FITTING_TYPES[self.fittingType.strip().lower()]

        rows = [
            ['Fitting type',        f'{self.fittingType}'],
            ['Standard',            f'{fittingData["standard"]}'],
            ['Sealing element',     f'{fittingData["sealingElement"]}'],
            ['Tube OD',             f'{self.tubeOuterDiameter * 1.0e3:.3f} mm ({self.tubeOuterDiameter / M_PER_IN:.4g} in)'],
            ['Dash size',           f'-{self.dashSize:d}'],
            ['Quantity',            f'{self.quantity:d}'],
            ['Body material',       f'{self.material}'],
            ['Service fluid',       f'{self.fluid if self.fluid else "unspecified"}'],
            ['Design pressure',     f'{self.designPressure / 1.0e6:.3f} MPa' if not np.isnan(self.designPressure) else 'unspecified'],
            ['Design temperature',  f'{self.designTemperature:.1f} K'],
            ['Pressure margin',     f'{self.pressureMargin:.2f}' if not np.isnan(self.pressureMargin) else 'not evaluated'],
            ['Reuse cycles',        f'{fittingData["reuseCycles"]:d}'],
            ['Leak class per joint', f'{fittingData["leakClass"]:.1e} scc/s He']
        ]

        if not np.isnan(self.pressureLoss):
            rows.append(['Total K',          f'{self.totalLossCoefficient:.3f}'])
            rows.append(['Velocity',         f'{self.velocity:.3f} m/s'])
            rows.append(['Pressure loss',    f'{self.pressureLoss / 1.0e3:.4f} kPa'])
            rows.append(['Aggregate leak',   f'{self.leakRateEstimate:.2e} scc/s He'])

        if not np.isnan(self.torqueRange[0]):
            rows.append(['Installation torque',
                         f'{self.torqueRange[0]:.2f} to {self.torqueRange[1]:.2f} N-m '
                         f'({self.torqueRange[0] / NM_PER_INLBF:.0f} to {self.torqueRange[1] / NM_PER_INLBF:.0f} in-lbf)'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'FITTING REPORT')

        report += f'\n\nNOTES\n{"-" * 60}\n{fittingData["notes"]}\n'

        for note in self.compatibilityNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'fittingReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.fittingType.strip().lower() not in FITTING_TYPES:
            raise InvalidInputError(
                message       = f'Unknown fitting type \'{self.fittingType}\'.',
                parameterName = 'fittingType', value = self.fittingType,
                validRange    = str(sorted(FITTING_TYPES.keys()))
            )

        if self.tubeOuterDiameter <= 0.0:
            raise InvalidInputError(
                message       = 'Tube outer diameter must be positive.',
                parameterName = 'tubeOuterDiameter', value = self.tubeOuterDiameter,
                validRange    = 'Greater than 0 m'
            )

        if not np.isnan(self.tubeInnerDiameter) and self.tubeInnerDiameter >= self.tubeOuterDiameter:
            raise InvalidInputError(
                message       = 'Tube inner diameter must be smaller than the outer diameter.',
                parameterName = 'tubeInnerDiameter', value = self.tubeInnerDiameter,
                validRange    = f'Less than {self.tubeOuterDiameter:.6g} m'
            )
