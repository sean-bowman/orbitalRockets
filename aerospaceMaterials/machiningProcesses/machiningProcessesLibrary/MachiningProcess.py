
# -- MachiningProcess Class Definition -- #

'''

Cutting force, tool life, chatter stability and the distortion released by asymmetric material
removal.

Almost every launch vehicle part is machined at some point, and the constraints that actually bite
are not the ones people expect. Cutting speed is a cost parameter. What limits a real aerospace part
is chatter, thin wall deflection, and distortion, and all three are geometry problems rather than
material problems.

    Chatter        Self-excited vibration between the tool and the workpiece. It is not a
                   resonance you can drive through: above a critical depth of cut the process is
                   unconditionally unstable. The stability lobe diagram says which spindle speeds
                   permit a deeper cut, and the answer is counterintuitive because faster is
                   sometimes far better.

    Thin wall      A 2 mm rib deflects away from the tool, so the cut is shallower than commanded
                   and the wall ends up thick. Then it springs back. Multiple spring passes are the
                   answer and they are what make thin walled parts slow.

    Distortion     A quenched plate carries self-equilibrating residual stress. Machine it
                   asymmetrically and the balance breaks. This is the direct link to heat
                   treatment, and it is the failure that scraps large machined parts.

See Also:
---------
HeatTreatment : Supplies the quench residual stress this class releases
MaterialDatabase : Machinability and the specific cutting energy

Theory: docs/CuttingMechanics.md, docs/ChatterAndStability.md, docs/Distortion.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from machiningUtils import (applyInputs, formatReportTable, queryMaterial,
                                InvalidInputError, ProcessInfeasibleError, createErrorContext)
except ImportError:
    from .machiningUtils import (applyInputs, formatReportTable, queryMaterial,
                                 InvalidInputError, ProcessInfeasibleError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Machinability data. Specific cutting energy is the energy to remove unit volume and it sets the
# cutting force directly. Taylor exponent and constant set the tool life.
#
# The spread is the story. Aluminium cuts at 0.7 GJ/m^3 and Inconel at 4.0, so the same removal rate
# needs six times the power and produces six times the heat. That heat has to go somewhere, and in
# titanium and nickel it goes into the tool because the workpiece does not conduct it away.

MACHINABILITY = {
    '6061':        {'specificEnergy': 0.75e9, 'taylorExponent': 0.30, 'taylorConstant': 700.0,
                    'machinabilityRating': 1.00, 'maximumSpeed': 15.0,
                    'note': 'The easiest common aerospace alloy. Limited by chip evacuation and '
                            'spindle speed rather than by anything material.'},
    '7075':        {'specificEnergy': 0.85e9, 'taylorExponent': 0.28, 'taylorConstant': 600.0,
                    'machinabilityRating': 0.90, 'maximumSpeed': 12.0,
                    'note': 'As 6061. Thick plate parts are dominated by distortion, not cutting.'},
    '2219':        {'specificEnergy': 0.90e9, 'taylorExponent': 0.28, 'taylorConstant': 550.0,
                    'machinabilityRating': 0.85, 'maximumSpeed': 10.0, 'note': 'Straightforward.'},
    '316L':        {'specificEnergy': 2.30e9, 'taylorExponent': 0.20, 'taylorConstant': 180.0,
                    'machinabilityRating': 0.35, 'maximumSpeed': 2.5,
                    'note': 'Work hardens under the tool, so a rubbing pass hardens the surface for '
                            'the next one. Take a positive depth of cut or none at all.'},
    '17-4PH':      {'specificEnergy': 2.60e9, 'taylorExponent': 0.20, 'taylorConstant': 150.0,
                    'machinabilityRating': 0.30, 'maximumSpeed': 2.0,
                    'note': 'Machine in the solution annealed condition and age afterwards where '
                            'the tolerance permits.'},
    'TI-6AL-4V':   {'specificEnergy': 2.80e9, 'taylorExponent': 0.25, 'taylorConstant': 90.0,
                    'machinabilityRating': 0.22, 'maximumSpeed': 1.0,
                    'note': 'The heat does not conduct away from the edge because the alloy is a '
                            'poor conductor, so it all goes into the tool. Flood coolant, sharp '
                            'tools, no dwell, and never let the tool rub.'},
    'INCONEL 718': {'specificEnergy': 4.00e9, 'taylorExponent': 0.15, 'taylorConstant': 40.0,
                    'machinabilityRating': 0.12, 'maximumSpeed': 0.5,
                    'note': 'Work hardens severely and abrades the tool. Ceramic or whisker '
                            'reinforced inserts at high speed, or carbide at low speed. Nothing in '
                            'between works.'},
    'INCONEL 625': {'specificEnergy': 3.80e9, 'taylorExponent': 0.15, 'taylorConstant': 45.0,
                    'machinabilityRating': 0.13, 'maximumSpeed': 0.6, 'note': 'As 718.'},
    'GRCOP-42':    {'specificEnergy': 1.20e9, 'taylorExponent': 0.25, 'taylorConstant': 300.0,
                    'machinabilityRating': 0.55, 'maximumSpeed': 5.0,
                    'note': 'Gummy. Sharp positive rake geometry and high speed to avoid a built '
                            'up edge.'}
}

# Cutting processes and their geometry.
CUTTING_PROCESSES = {
    'face mill':   {'teeth': 6, 'engagementFraction': 0.70, 'note': 'Bulk removal on a flat face.'},
    'end mill':    {'teeth': 4, 'engagementFraction': 0.25, 'note': 'Profiling and pocketing.'},
    'ball mill':   {'teeth': 2, 'engagementFraction': 0.15,
                    'note': 'Surfacing. Effective diameter varies with depth, so the surface speed '
                            'at the tip is zero and the tool rubs there.'},
    'turn':        {'teeth': 1, 'engagementFraction': 1.00, 'note': 'Continuous cut, no interruption.'},
    'drill':       {'teeth': 2, 'engagementFraction': 1.00,
                    'note': 'Chip evacuation governs above about 3 diameters deep.'}
}

# Chatter. The limiting depth of cut for unconditional stability is set by the real part of the
# frequency response function at the most flexible mode.
#
# The lobe structure is the useful part: at spindle speeds where the tooth passing frequency is a
# whole fraction of the natural frequency, the achievable depth of cut is several times the
# unconditional limit. Running IN a lobe rather than between two is often the difference between a
# 1 mm and a 5 mm depth of cut, and it costs nothing.

CHATTER_LOBE_COUNT = 6      # [-], how many lobes to evaluate

# Thin wall deflection. A wall deflects away from the tool under the radial cutting force, so the
# cut is shallow and the wall ends up thick. Spring passes remove the remainder.
THIN_WALL_TOLERANCE = 25.0e-6    # [m], the deflection below which a single pass is adequate

# Surface integrity. Machining leaves residual stress in the surface, and its sign depends on
# whether mechanical deformation or thermal expansion dominated.
SURFACE_RESIDUAL_STRESS = {
    'sharp tool, flood coolant':    {'stress': -300.0e6, 'fatigueFactor': 1.15,
                                     'note': 'Compressive. Mechanical deformation dominates and the '
                                             'surface is left in compression, which helps fatigue.'},
    'worn tool, flood coolant':     {'stress': 50.0e6, 'fatigueFactor': 0.90,
                                     'note': 'A worn tool rubs rather than cuts, and the heat pushes '
                                             'the surface into tension.'},
    'sharp tool, dry':              {'stress': 200.0e6, 'fatigueFactor': 0.80,
                                     'note': 'Thermal expansion dominates. Tensile surface stress '
                                             'and a fatigue debit.'},
    'worn tool, dry':               {'stress': 450.0e6, 'fatigueFactor': 0.60,
                                     'note': 'The worst case. Tensile surface stress plus a white '
                                             'layer, and the fatigue debit is severe.'}
}

# ------------------------------------------------------------------------------------------------ #

class MachiningProcess:

    '''

    Cutting force, tool life, chatter stability, thin wall deflection and distortion.

    Primary Input Properties:
    -------------------------
    material : str
        Key into MACHINABILITY
    process : str
        Key into CUTTING_PROCESSES
    cuttingSpeed / feedPerTooth / axialDepth / radialDepth / toolDiameter : float
        The cut [m/s], [m], [m], [m], [m]
    naturalFrequency / stiffness / dampingRatio : float
        The dominant flexible mode, for the chatter calculation

    Key Output Properties:
    ----------------------
    cuttingForce : float
        [N] tangential
    spindlePower : float
        [W]
    toolLife : float
        [s] from Taylor
    criticalDepthOfCut : float
        [m], the unconditionally stable limit

    Public Methods:
    ---------------
    setInputs(inputs)                     Load a configuration dictionary
    calculateCuttingForce()               Force, torque and spindle power
    calculateToolLife()                   Taylor, and the speed against life trade
    calculateStabilityLobes()             Chatter limit and the favourable spindle speeds
    calculateThinWallDeflection(h, t)     Deflection and the spring pass count
    calculateDistortion(stress, ...)      Released bow from asymmetric removal
    assessSurfaceIntegrity(condition)     Residual stress and the fatigue factor
    generateReport(outputDir)             Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Material and Process -- #

        self.material         = 'TI-6AL-4V'   # [case insensitive string]
        self.condition        = None          # [case insensitive string]
        self.process          = 'end mill'    # [case insensitive string]

        # -- The Cut -- #

        self.cuttingSpeed     = 0.60      # [m/s], surface speed
        self.feedPerTooth     = 0.10e-3   # [m]
        self.axialDepth       = 0.005     # [m]
        self.radialDepth      = 0.003     # [m]
        self.toolDiameter     = 0.012     # [m]

        # -- The Flexible Mode -- #

        self.naturalFrequency = 800.0     # [Hz], the dominant mode of tool or workpiece
        self.modalStiffness   = 2.0e7     # [N/m]
        self.dampingRatio     = 0.03      # [-]

        # -- Results -- #

        self.cuttingForce       = np.nan  # [N]
        self.spindlePower       = np.nan  # [W]
        self.toolLife           = np.nan  # [s]
        self.criticalDepthOfCut = np.nan  # [m]
        self.machiningNotes     = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material.

        '''

        requiredParams = {
            'material': 'Material not provided.'
        }

        optionalParams = ['condition', 'process', 'cuttingSpeed', 'feedPerTooth', 'axialDepth',
                          'radialDepth', 'toolDiameter', 'naturalFrequency', 'modalStiffness',
                          'dampingRatio']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateCuttingForce(self) -> dict:

        '''

        Cutting force, torque, spindle power and material removal rate.

            F_c = k_c A_c                  specific cutting energy times chip area
            P   = F_c v                    tangential force times surface speed
            MRR = a_e a_p f z N            radial x axial x feed x teeth x speed

        The specific cutting energy is where the alloy difference lives, and the spread is large:
        aluminium at 0.75 GJ/m^3 against Inconel at 4.0. The same removal rate therefore needs five
        times the spindle power on the nickel alloy and produces five times the heat.

        WHERE THAT HEAT GOES IS THE REAL DIFFERENCE. In aluminium it leaves in the chip and in the
        workpiece, both of which conduct well. In titanium and nickel neither conducts, so it goes
        into the tool edge, and that is why tool life on those alloys is measured in minutes.

        '''

        properties = MACHINABILITY[self.material]
        process    = CUTTING_PROCESSES[self.process]

        spindleSpeed = self.cuttingSpeed / (np.pi * self.toolDiameter)      # [rev/s]

        # Average chip area over the engagement
        chipArea = self.feedPerTooth * self.axialDepth * process['engagementFraction']

        self.cuttingForce = properties['specificEnergy'] * chipArea

        torque = self.cuttingForce * self.toolDiameter / 2.0
        self.spindlePower = self.cuttingForce * self.cuttingSpeed

        removalRate = (self.radialDepth * self.axialDepth * self.feedPerTooth *
                       process['teeth'] * spindleSpeed)

        return {'specificEnergy': properties['specificEnergy'],
                'spindleSpeed': spindleSpeed,
                'spindleSpeedRpm': spindleSpeed * 60.0,
                'chipArea': chipArea,
                'cuttingForce': self.cuttingForce,
                'torque': torque,
                'spindlePower': self.spindlePower,
                'materialRemovalRate': removalRate,
                'removalRateCubicCentimetrePerMinute': removalRate * 1.0e6 * 60.0,
                'machinabilityRating': properties['machinabilityRating']}

    def calculateToolLife(self) -> dict:

        '''

        Taylor tool life, and what a speed change costs.

            V T^n = C

        The exponent n is the sensitivity, and it is small: 0.15 for Inconel, 0.30 for aluminium. A
        small exponent means life is VERY sensitive to speed.

        At n = 0.15, a 20 percent speed increase cuts tool life by a factor of 3.4. At n = 0.30 the
        same increase costs a factor of 1.8. That is why nickel alloys are machined at speeds that
        look absurdly slow next to aluminium: the exponent punishes any deviation far harder.

        '''

        properties = MACHINABILITY[self.material]

        exponent = properties['taylorExponent']
        constant = properties['taylorConstant']

        speedMetresPerMinute = self.cuttingSpeed * 60.0

        if speedMetresPerMinute >= constant:
            self.toolLife = 0.0
            raise ProcessInfeasibleError(
                message = f'A cutting speed of {speedMetresPerMinute:.0f} m/min on {self.material} '
                          f'is at or above the Taylor constant of {constant:.0f} m/min, which is '
                          f'the speed at which tool life falls to one minute. The tool fails '
                          f'immediately.'
            )

        lifeMinutes = (constant / speedMetresPerMinute) ** (1.0 / exponent)
        self.toolLife = lifeMinutes * 60.0

        # What a 20 percent speed change costs
        fasterLife = (constant / (1.2 * speedMetresPerMinute)) ** (1.0 / exponent)
        lifeRatio  = lifeMinutes / fasterLife

        maximumSpeed = properties['maximumSpeed']

        result = {'cuttingSpeed': self.cuttingSpeed,
                  'cuttingSpeedMetresPerMinute': speedMetresPerMinute,
                  'taylorExponent': exponent, 'taylorConstant': constant,
                  'toolLife': self.toolLife, 'toolLifeMinutes': lifeMinutes,
                  'lifeRatioForTwentyPercentFaster': lifeRatio,
                  'recommendedMaximumSpeed': maximumSpeed,
                  'note': properties['note']}

        if self.cuttingSpeed > maximumSpeed:
            self.machiningNotes.append(
                f'The cutting speed of {self.cuttingSpeed:.2f} m/s exceeds the '
                f'{maximumSpeed:.2f} m/s normally recommended for {self.material}. Tool life is '
                f'{lifeMinutes:.1f} minutes at this speed.')

        if lifeMinutes < 10.0:
            self.machiningNotes.append(
                f'Tool life of {lifeMinutes:.1f} minutes means a tool change inside a single '
                f'feature on most parts. A tool change mid-feature leaves a witness mark and it is '
                f'a dimensional discontinuity, so the programme has to be written around it.')

        self.machiningNotes.append(
            f'The Taylor exponent is {exponent:.2f}, so a 20 percent speed increase cuts tool life '
            f'by a factor of {lifeRatio:.1f}. That sensitivity is why {self.material} is run at '
            f'speeds that look slow.')

        return result

    def calculateStabilityLobes(self) -> dict:

        '''

        Chatter stability limit and the spindle speeds that permit a deeper cut.

        The unconditionally stable depth of cut, below which no chatter is possible at any speed:

            a_lim = -1 / (2 K_s Re[G(omega)]_min)

        with the minimum real part of the frequency response function approximated for a single mode
        by -1 / (4 k zeta (1 + zeta)).

        THE LOBE STRUCTURE IS THE USEFUL PART AND IT IS COUNTERINTUITIVE. At spindle speeds where
        the tooth passing frequency is a whole fraction of the natural frequency, the regenerative
        phase lines up favourably and the achievable depth of cut is several times the
        unconditional limit:

            N_lobe = 60 f_n / (z * lobeNumber)          rev/min

        Running IN a lobe rather than between two is often the difference between a 1 mm and a 5 mm
        depth of cut, and it costs nothing but a spindle speed change. The lowest lobes are the
        widest and the most useful, and they sit at high spindle speed, which is why high speed
        machining of thin walls works at all.

        Chatter is NOT a resonance to be driven through. Above the stability limit the process is
        self-excited and unconditionally unstable, and the result is a scrapped part and often a
        broken tool.

        '''

        properties = MACHINABILITY[self.material]
        process    = CUTTING_PROCESSES[self.process]

        # Minimum real part of the FRF for a single degree of freedom mode
        minimumRealPart = -1.0 / (4.0 * self.modalStiffness * self.dampingRatio *
                                  (1.0 + self.dampingRatio))

        # Cutting stiffness, the force per unit chip area, taken from the specific energy
        cuttingStiffness = properties['specificEnergy'] * process['engagementFraction']

        self.criticalDepthOfCut = -1.0 / (2.0 * cuttingStiffness * minimumRealPart)

        # The lobes. Each is centred where the tooth passing frequency divides the natural frequency.
        lobes = []
        for lobeNumber in range(1, CHATTER_LOBE_COUNT + 1):
            spindleRpm = 60.0 * self.naturalFrequency / (process['teeth'] * lobeNumber)
            # Achievable depth in the middle of a lobe, relative to the unconditional limit. The
            # lowest lobes are the widest and give the largest gain.
            gain = 1.0 + 3.0 / lobeNumber
            lobes.append({'lobeNumber': lobeNumber,
                          'spindleSpeedRpm': spindleRpm,
                          'surfaceSpeed': spindleRpm / 60.0 * np.pi * self.toolDiameter,
                          'achievableDepth': self.criticalDepthOfCut * gain,
                          'gain': gain})

        currentRpm = self.cuttingSpeed / (np.pi * self.toolDiameter) * 60.0

        # Which lobe, if any, the current speed sits in
        nearest = min(lobes, key = lambda entry: abs(entry['spindleSpeedRpm'] - currentRpm))
        inLobe  = abs(nearest['spindleSpeedRpm'] - currentRpm) / nearest['spindleSpeedRpm'] < 0.10

        stable = self.axialDepth <= self.criticalDepthOfCut

        result = {'criticalDepthOfCut': self.criticalDepthOfCut,
                  'axialDepth': self.axialDepth,
                  'unconditionallyStable': stable,
                  'cuttingStiffness': cuttingStiffness,
                  'naturalFrequency': self.naturalFrequency,
                  'currentSpindleSpeedRpm': currentRpm,
                  'lobes': lobes,
                  'nearestLobe': nearest,
                  'runningInLobe': inLobe}

        if not stable:
            if inLobe:
                self.machiningNotes.append(
                    f'The {self.axialDepth * 1.0e3:.1f} mm axial depth exceeds the '
                    f'{self.criticalDepthOfCut * 1.0e3:.2f} mm unconditional limit, but the spindle '
                    f'is running inside lobe {nearest["lobeNumber"]} where '
                    f'{nearest["achievableDepth"] * 1.0e3:.2f} mm is achievable. This is stable and '
                    f'it depends on holding the spindle speed.')
            else:
                bestLobe = max(lobes, key = lambda entry: entry['achievableDepth'])
                raise ProcessInfeasibleError(
                    message = f'The {self.axialDepth * 1.0e3:.1f} mm axial depth exceeds the '
                              f'{self.criticalDepthOfCut * 1.0e3:.2f} mm unconditional stability '
                              f'limit and the spindle is not running in a stability lobe. The '
                              f'process will chatter, which is self-excited and not a resonance to '
                              f'be driven through: the part is scrapped and the tool usually '
                              f'breaks. Either reduce the depth, or move the spindle to '
                              f'{bestLobe["spindleSpeedRpm"]:.0f} rev/min where '
                              f'{bestLobe["achievableDepth"] * 1.0e3:.2f} mm is achievable.'
                )

        if not inLobe and stable:
            bestLobe = max(lobes, key = lambda entry: entry['achievableDepth'])
            self.machiningNotes.append(
                f'The spindle is not in a stability lobe. Moving it to '
                f'{bestLobe["spindleSpeedRpm"]:.0f} rev/min would raise the achievable depth of cut '
                f'from {self.criticalDepthOfCut * 1.0e3:.2f} to '
                f'{bestLobe["achievableDepth"] * 1.0e3:.2f} mm at no cost.')

        return result

    def calculateThinWallDeflection(self, wallHeight: float, wallThickness: float) -> dict:

        '''

        Deflection of a thin wall under the radial cutting force, and the spring passes it needs.

        A wall machined on one side is a cantilever loaded at the cut:

            delta = F L^3 / (3 E I)

        The wall deflects AWAY from the tool, so the cut is shallower than commanded and the wall
        is left thick. Then it springs back to nominal, carrying the error.

        The cube on the height is what makes this brutal. Doubling the wall height multiplies the
        deflection by eight, and halving the thickness multiplies it by eight again through the
        second moment of area.

        SPRING PASSES ARE THE ANSWER and they are what make thin walled parts slow. Each pass at zero
        nominal depth removes a fraction of the remaining error, and the count needed follows from
        the ratio of the deflection to the tolerance.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)

        if np.isnan(self.cuttingForce):
            self.calculateCuttingForce()

        modulus = properties['elasticModulus']

        # Radial force is roughly a third of the tangential for a positive rake tool
        radialForce = 0.35 * self.cuttingForce

        # The wall is a cantilever PLATE, not a beam of the tool's width. A load applied locally
        # spreads laterally into the surrounding material, and the effective width that resists the
        # deflection is roughly twice the cantilever height rather than the axial engagement.
        #
        # Using the axial depth as the section width is the obvious mistake and it overstates the
        # deflection by more than an order of magnitude, because it models a narrow strip
        # cantilevering alone when the whole wall is carrying the load.
        effectiveWidth = max(2.0 * wallHeight, self.axialDepth)

        secondMoment = effectiveWidth * wallThickness ** 3 / 12.0

        deflection = radialForce * wallHeight ** 3 / (3.0 * modulus * secondMoment)

        # Each spring pass removes roughly 60 percent of the remaining error
        passEfficiency = 0.60
        springPasses = 0
        remaining = deflection
        while remaining > THIN_WALL_TOLERANCE and springPasses < 12:
            remaining *= (1.0 - passEfficiency)
            springPasses += 1

        result = {'wallHeight': wallHeight, 'wallThickness': wallThickness,
                  'aspectRatio': wallHeight / wallThickness,
                  'radialForce': radialForce,
                  'effectiveWidth': effectiveWidth, 'secondMomentOfArea': secondMoment,
                  'deflection': deflection,
                  'tolerance': THIN_WALL_TOLERANCE,
                  'springPassesRequired': springPasses,
                  'residualError': remaining}

        if deflection > 0.5e-3:
            self.machiningNotes.append(
                f'A {wallThickness * 1.0e3:.1f} mm wall {wallHeight * 1.0e3:.0f} mm tall deflects '
                f'{deflection * 1.0e3:.3f} mm under the radial cutting force. Deflection goes as '
                f'the cube of the height and the inverse cube of the thickness, so this is a '
                f'geometry problem rather than a cutting parameter problem. Machine it in steps '
                f'from the top down so the unmachined material below supports the wall, or use a '
                f'support wax.')

        if springPasses >= 4:
            self.machiningNotes.append(
                f'{springPasses} spring passes are needed to bring the wall inside '
                f'{THIN_WALL_TOLERANCE * 1.0e6:.0f} um. That is most of the cycle time for this '
                f'feature and it is why thin walled parts are slow.')

        return result

    def calculateDistortion(self, residualStress: float, plateThickness: float,
                            machinedFraction: float, partLength: float,
                            partWidth: float = 0.200) -> dict:

        '''

        Bow released when a residually stressed plate is machined asymmetrically.

        THIS IS THE DIRECT LINK TO HEAT TREATMENT and it is the failure that scraps large machined
        parts. A quenched plate carries self-equilibrating residual stress: compression at both
        surfaces balanced by tension in the core, with zero net force and zero net moment, which is
        what lets it sit flat.

        Machine material off one side and the balance breaks. The remaining section carries an
        unbalanced moment and the part bows.

        The residual stress input comes from HeatTreatment.calculateDistortion, and the parabolic
        profile assumption is the same one, for the same reason: treating the removed layer as
        carrying a uniform stress overstates the released moment by roughly a factor of four,
        because that layer contains both the compressive surface and part of the tensile core.

        '''

        properties = queryMaterial(self.material, self.condition, 293.15)
        modulus = properties['elasticModulus']

        removedThickness   = plateThickness * machinedFraction
        remainingThickness = plateThickness - removedThickness

        if remainingThickness <= 0.0:
            raise InvalidInputError(
                message       = 'The machined fraction removes the whole plate.',
                parameterName = 'machinedFraction', value = machinedFraction,
                validRange    = 'Less than 1.0'
            )

        def stressProfile(position: np.ndarray) -> np.ndarray:
            '''Self-equilibrating parabolic residual stress, matching HeatTreatment.'''
            return residualStress * (3.0 * (2.0 * position / plateThickness) ** 2 - 1.0) / 2.0

        upperLimit = plateThickness / 2.0 - removedThickness
        lowerLimit = -plateThickness / 2.0

        positions = np.linspace(lowerLimit, upperLimit, 2001)
        stresses  = stressProfile(positions)

        integrate = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz

        centroid  = (lowerLimit + upperLimit) / 2.0
        netMoment = partWidth * float(integrate(stresses * (positions - centroid), positions))

        secondMoment = partWidth * remainingThickness ** 3 / 12.0

        curvature = netMoment / (modulus * secondMoment)
        bow = abs(curvature) * partLength ** 2 / 8.0

        result = {'residualStress': residualStress,
                  'plateThickness': plateThickness,
                  'removedThickness': removedThickness,
                  'remainingThickness': remainingThickness,
                  'unbalancedMoment': netMoment,
                  'curvature': curvature,
                  'predictedBow': bow,
                  'partLength': partLength}

        if bow > 0.5e-3:
            self.machiningNotes.append(
                f'Machining {machinedFraction * 100.0:.0f} percent from one side of a '
                f'{plateThickness * 1.0e3:.0f} mm plate releases a bow of {bow * 1.0e3:.2f} mm over '
                f'{partLength * 1.0e3:.0f} mm. The fixes, in order: specify a stress relieved temper '
                f'(T351 or T7451 rather than T6), machine symmetrically in alternating passes, or '
                f'rough, stress relieve and then finish in a second setup.')

        return result

    def assessSurfaceIntegrity(self, condition: str = 'sharp tool, flood coolant') -> dict:

        '''

        Surface residual stress and the fatigue factor it carries.

        The sign of the residual stress depends on which mechanism dominated:

            Mechanical deformation dominates   The surface is left in COMPRESSION, which is
                                               beneficial and worth up to 15 percent on fatigue.

            Thermal expansion dominates        The surface is left in TENSION, which is a fatigue
                                               debit and in the worst case forms a white layer of
                                               untempered martensite.

        A worn tool rubs rather than cuts, so it puts heat in instead of removing material. THE SAME
        MACHINE, THE SAME PROGRAMME AND THE SAME MATERIAL PRODUCE A 15 PERCENT FATIGUE BENEFIT OR A
        40 PERCENT PENALTY DEPENDING ON WHETHER THE TOOL WAS CHANGED ON SCHEDULE.

        '''

        if condition not in SURFACE_RESIDUAL_STRESS:
            raise InvalidInputError(
                message       = f'Unknown surface condition \'{condition}\'.',
                parameterName = 'condition', value = condition,
                validRange    = str(sorted(SURFACE_RESIDUAL_STRESS.keys()))
            )

        entry = SURFACE_RESIDUAL_STRESS[condition]

        best  = SURFACE_RESIDUAL_STRESS['sharp tool, flood coolant']
        swing = best['fatigueFactor'] / entry['fatigueFactor']

        if entry['stress'] > 0.0:
            self.machiningNotes.append(
                f'A {condition} cut leaves the surface in {entry["stress"] / 1.0e6:.0f} MPa tension '
                f'and carries a fatigue factor of {entry["fatigueFactor"]:.2f}. A sharp tool with '
                f'flood coolant would leave it in compression at a factor of '
                f'{best["fatigueFactor"]:.2f}, a swing of {swing:.2f} times on fatigue life for a '
                f'tool change.')

        return {'condition': condition,
                'surfaceResidualStress': entry['stress'],
                'fatigueFactor': entry['fatigueFactor'],
                'bestAchievable': best['fatigueFactor'],
                'swing': swing,
                'note': entry['note']}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        force = self.calculateCuttingForce()

        try:
            life = self.calculateToolLife()
            lifeLine = f'{life["toolLifeMinutes"]:.1f} min'
        except ProcessInfeasibleError:
            lifeLine = 'IMMEDIATE FAILURE at this speed'

        try:
            chatter = self.calculateStabilityLobes()
            chatterLine = (f'{self.criticalDepthOfCut * 1.0e3:.2f} mm unconditional, '
                           f'{"in" if chatter["runningInLobe"] else "not in"} a lobe')
        except ProcessInfeasibleError:
            chatterLine = f'{self.criticalDepthOfCut * 1.0e3:.2f} mm -- WILL CHATTER'

        properties = MACHINABILITY[self.material]

        rows = [
            ['Material',            f'{self.material}'],
            ['Machinability',       f'{properties["machinabilityRating"]:.2f} (6061 = 1.00)'],
            ['Process',             f'{self.process}'],
            ['Cutting speed',       f'{self.cuttingSpeed:.2f} m/s '
                                    f'({self.cuttingSpeed * 60.0:.0f} m/min)'],
            ['Spindle speed',       f'{force["spindleSpeedRpm"]:.0f} rev/min'],
            ['Specific energy',     f'{properties["specificEnergy"] / 1.0e9:.2f} GJ/m^3'],
            ['Cutting force',       f'{self.cuttingForce:.0f} N'],
            ['Spindle power',       f'{self.spindlePower / 1000.0:.2f} kW'],
            ['Removal rate',        f'{force["removalRateCubicCentimetrePerMinute"]:.1f} cm^3/min'],
            ['Taylor exponent',     f'{properties["taylorExponent"]:.2f}'],
            ['Tool life',           lifeLine],
            ['Chatter limit',       chatterLine]
        ]

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'MACHINING PROCESS')

        report += f'\n\nMATERIAL NOTE\n{"-" * 60}\n{properties["note"]}\n'

        for note in self.machiningNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'machiningProcess.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        key = ' '.join(self.material.strip().upper().split())

        if key not in MACHINABILITY:
            raise InvalidInputError(
                message       = f'No machinability data for \'{self.material}\'. Specific cutting '
                                f'energy varies by a factor of five across these alloys and it '
                                f'cannot be assumed.',
                parameterName = 'material', value = self.material,
                validRange    = str(sorted(MACHINABILITY.keys()))
            )

        self.material = key

        process = self.process.strip().lower()

        if process not in CUTTING_PROCESSES:
            raise InvalidInputError(
                message       = f'Unknown cutting process \'{self.process}\'.',
                parameterName = 'process', value = self.process,
                validRange    = str(sorted(CUTTING_PROCESSES.keys()))
            )

        self.process = process

        for name, value in (('cuttingSpeed', self.cuttingSpeed),
                            ('feedPerTooth', self.feedPerTooth),
                            ('axialDepth', self.axialDepth),
                            ('toolDiameter', self.toolDiameter),
                            ('naturalFrequency', self.naturalFrequency),
                            ('modalStiffness', self.modalStiffness)):
            if value <= 0.0:
                raise InvalidInputError(
                    message       = f'{name} must be positive.',
                    parameterName = name, value = value, validRange = 'Greater than 0'
                )

        if not 0.0 < self.dampingRatio < 1.0:
            raise InvalidInputError(
                message       = 'Damping ratio must lie between 0 and 1.',
                parameterName = 'dampingRatio', value = self.dampingRatio, validRange = '(0, 1)'
            )
