
# -- Filter Class Definition -- #

'''

Filter sizing: rating selection, clean pressure drop, element area and dirt holding capacity.

A filter exists to protect something specific. The design starts by identifying what that is, and
almost always it is the smallest flow passage downstream: an injector orifice, a valve seat, a
regulator poppet, or a catalyst bed.

The governing rule is simple and it is the one thing to remember:

    absolute rating  <=  smallest downstream passage / 10

A particle larger than about a third of a passage will lodge in it. Filtering to a tenth gives margin
for particle agglomeration, for the fact that a nominally spherical rating says nothing about a
fibre, and for the fact that filters degrade.

Two ratings are quoted and they are not the same thing:

**Nominal rating** is a marketing number. It means the filter removes "most" particles above that
size, with no agreed definition of "most". It is not a specification and it should not appear in a
requirement.

**Absolute rating** is defined by the beta ratio: the ratio of upstream to downstream particle count
above a given size. A beta of 1000 at 10 micron means 999 of every 1000 particles above 10 micron are
captured, which is 99.9 percent efficiency. **Specify absolute ratings with a beta value.**

See Also:
---------
Orifice     : The thing the filter is usually protecting
Valve       : The seat that a single particle destroys
CatalystBed : The bed that particulate abrades
Line        : Where the filter pressure drop appears in the budget

Theory: docs/FlowControlDevices.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, formatReportTable, M_PER_MICRON,
                       PA_PER_PSIA, InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, formatReportTable, M_PER_MICRON,
                        PA_PER_PSIA, InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Filter element types.
#
#   permeability        clean flow permeability [m^2], for the Darcy pressure drop
#   thickness           element wall thickness [m]
#   dirtCapacity        dirt holding capacity per unit area [kg/m^2] before the clean dP doubles
#   maximumTemperature  service limit [K]
#   cleanable           whether the element can be back-flushed or ultrasonically cleaned
#
# The area-per-unit-envelope difference between a flat screen and a pleated element is the whole
# reason pleated elements exist: a pleated element packs five to twenty times the filtration area
# into the same envelope, which is five to twenty times the dirt capacity and a fraction of the
# clean pressure drop.
FILTER_TYPES = {
    'woven wire mesh': {
        'permeability': 2.0e-10, 'thickness': 0.20e-3, 'dirtCapacity': 0.010,
        'maximumTemperature': 800.0, 'cleanable': True, 'areaFactor': 1.0,
        'description': 'Single layer woven stainless wire cloth.',
        'notes': 'Cheap, cleanable, and it has a well-defined largest opening, which is what makes it a true '
                 'absolute filter. Low dirt capacity because all the capture is on one surface. The standard '
                 'for a last-chance screen immediately upstream of an injector.'
    },
    'sintered wire mesh': {
        'permeability': 8.0e-11, 'thickness': 0.60e-3, 'dirtCapacity': 0.045,
        'maximumTemperature': 850.0, 'cleanable': True, 'areaFactor': 1.0,
        'description': 'Multiple wire cloth layers diffusion bonded into a rigid sheet.',
        'notes': 'Depth filtration in a structurally rigid element. High collapse strength, cleanable, and it '
                 'holds far more dirt than single-layer mesh. The aerospace workhorse.'
    },
    'sintered powder': {
        'permeability': 1.5e-11, 'thickness': 1.60e-3, 'dirtCapacity': 0.080,
        'maximumTemperature': 850.0, 'cleanable': False, 'areaFactor': 1.0,
        'description': 'Sintered metal powder, typically 316L.',
        'notes': 'Very fine ratings available, down to sub-micron. High dirt capacity, high clean pressure drop, '
                 'and not reliably cleanable because the tortuous pore structure holds contamination. Used where '
                 'the rating requirement is finer than mesh can reach.'
    },
    'pleated mesh': {
        'permeability': 8.0e-11, 'thickness': 0.60e-3, 'dirtCapacity': 0.045,
        'maximumTemperature': 850.0, 'cleanable': True, 'areaFactor': 8.0,
        'description': 'Sintered mesh pleated into a cylindrical cartridge.',
        'notes': 'The same medium as sintered mesh with eight times the area in the same envelope. Eight times '
                 'the dirt capacity and roughly one eighth the clean pressure drop. The pleats can collapse '
                 'under reverse flow, so a reverse flow case must be checked.'
    },
    'etched disc': {
        'permeability': 3.0e-10, 'thickness': 0.10e-3, 'dirtCapacity': 0.005,
        'maximumTemperature': 800.0, 'cleanable': True, 'areaFactor': 1.0,
        'description': 'Photochemically etched thin metal disc with precisely defined holes.',
        'notes': 'The most precisely defined pore size of any element, because the holes are made rather than '
                 'woven. Very low dirt capacity. Used as a last-chance filter in a critical passage.'
    }
}

# Beta ratio to efficiency. Beta is the ratio of upstream to downstream particle count above the
# rated size.
#
#   efficiency = 1 - 1/beta
#
# A filter is called "absolute" at beta 1000 in aerospace practice, and beta 75 in much of the
# industrial world, which is a source of specification confusion. State the beta value.
BETA_RATIOS = {
    2:     0.500,
    10:    0.900,
    75:    0.9867,
    100:   0.990,
    200:   0.995,
    1000:  0.999,
    5000:  0.9998
}

# The protection rule: absolute rating relative to the smallest downstream passage.
PROTECTION_RATIO_MINIMUM     = 3.0    # a particle above 1/3 of a passage will lodge
PROTECTION_RATIO_RECOMMENDED = 10.0   # the design target

class Filter:

    '''

    Filter rating selection, element sizing and pressure drop.

    Primary Input Properties:
    -------------------------
    fluid : str
        Species name passed through to fluidProps
    filterType : str
        Key into FILTER_TYPES
    absoluteRating : float
        Absolute particle rating [m]. Leave unset to size from the protected passage.
    protectedPassage : float
        Smallest downstream flow passage diameter [m]
    massFlow : float
        Design mass flow rate [kg/s]
    upstreamPressure : float
        Static pressure upstream [Pa, absolute]
    temperature : float
        Fluid temperature [K]
    allowableCleanPressureDrop : float
        Design clean pressure drop budget [Pa]
    filtrationArea : float
        Element filtration area [m^2]. Leave unset to size from the dP budget.
    betaRatio : int
        Beta ratio at the absolute rating [-]
    contaminationLoading : float
        Expected contamination in the fluid [kg/m^3]. For the life estimate.

    Key Output Properties:
    ----------------------
    filtrationArea : float
        Required element area [m^2]
    cleanPressureDrop : float
        Pressure drop with a clean element [Pa]
    dirtCapacity : float
        Contamination the element holds before the dP doubles [kg]
    protectionRatio : float
        Protected passage diameter over absolute rating [-]
    efficiency : float
        Capture efficiency at the rated size [-]
    serviceLife : float
        Time or throughput to the dirt capacity [s] or [m^3]

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    selectRating()                Absolute rating from the protected passage
    sizeElement()                 Filtration area for the clean dP budget
    calculatePressureDrop()       Clean and loaded pressure drop
    calculateLife(...)            Service life from the contamination loading
    generateReport(outputDir)     Formatted results table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Fluid and Duty -- #

        self.fluid                      = ''      # [case sensitive string]
        self.massFlow                   = np.nan  # [kg/s]
        self.upstreamPressure           = np.nan  # [Pa, absolute]
        self.temperature                = 293.15  # [K]

        # -- Filter Definition -- #

        self.filterType                 = 'sintered wire mesh'  # key into FILTER_TYPES
        self.absoluteRating             = np.nan  # [m]
        self.betaRatio                  = 1000    # [-]
        self.filtrationArea             = np.nan  # [m^2]

        # -- Sizing Targets -- #

        self.protectedPassage           = np.nan  # [m], smallest downstream passage
        self.allowableCleanPressureDrop = np.nan  # [Pa]
        self.contaminationLoading       = np.nan  # [kg/m^3] in the fluid

        # -- Results -- #

        self.density                    = np.nan  # [kg/m^3]
        self.viscosity                  = np.nan  # [Pa-s]
        self.cleanPressureDrop          = np.nan  # [Pa]
        self.faceVelocity               = np.nan  # [m/s]
        self.dirtCapacity               = np.nan  # [kg]
        self.protectionRatio            = np.nan  # [-]
        self.efficiency                 = np.nan  # [-]
        self.serviceLife                = np.nan  # [s]
        self.envelopeArea               = np.nan  # [m^2], before the pleat area factor
        self.designNotes                = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: fluid, massFlow, upstreamPressure.

        '''

        requiredParams = {
            'fluid':            'Filter fluid species not provided.',
            'massFlow':         'Filter mass flow rate not provided.',
            'upstreamPressure': 'Filter upstream pressure not provided.'
        }

        optionalParams = ['temperature', 'filterType', 'absoluteRating', 'betaRatio',
                          'filtrationArea', 'protectedPassage', 'allowableCleanPressureDrop',
                          'contaminationLoading']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

        self.density   = float(fluidProps(self.fluid, 'TP', 'D',   self.temperature, self.upstreamPressure))
        self.viscosity = float(fluidProps(self.fluid, 'TP', 'VIS', self.temperature, self.upstreamPressure))

    def selectRating(self) -> dict:

        '''

        Absolute rating from the smallest downstream passage.

        The rule:

            absolute rating  <=  protected passage / 10

        A particle larger than about a third of a passage will lodge in it, so a ratio of 3 is the
        hard minimum. A ratio of 10 is the design target, and the margin buys:

        - Tolerance for particle agglomeration; several small particles can bridge a passage
        - Tolerance for non-spherical particles; a fibre passes a rating test and then lodges
        - Tolerance for filter degradation over life
        - Tolerance for the fact that no filter is perfect at any size

        The rating is then rounded down to a standard available size. Standard absolute ratings in
        stainless media are 1, 2, 5, 7, 10, 15, 20, 25, 40, 60, 100 micron.

        **Do not over-filter.** A finer filter than necessary costs pressure drop, costs dirt
        capacity (because it plugs sooner), and costs money, without protecting anything additional.
        The passage being protected sets the requirement.

        '''

        if np.isnan(self.protectedPassage):
            raise InvalidInputError(
                message       = 'selectRating needs the smallest downstream passage diameter.',
                parameterName = 'protectedPassage', value = self.protectedPassage,
                validRange    = 'Positive real'
            )

        targetRating = self.protectedPassage / PROTECTION_RATIO_RECOMMENDED

        standardRatings = np.array([1, 2, 5, 7, 10, 15, 20, 25, 40, 60, 100]) * M_PER_MICRON
        available       = standardRatings[standardRatings <= targetRating]

        if available.size == 0:
            self.absoluteRating = standardRatings[0]
            self.designNotes.append(
                f'A {self.protectedPassage * 1.0e6:.1f} micron passage needs a '
                f'{targetRating * 1.0e6:.2f} micron filter to meet the 10:1 rule, which is finer than the 1 micron '
                f'finest standard rating. Either accept a lower protection ratio or enlarge the passage.')
        else:
            self.absoluteRating = float(available[-1])

        self.protectionRatio = self.protectedPassage / self.absoluteRating
        self.efficiency      = BETA_RATIOS.get(self.betaRatio, 1.0 - 1.0 / self.betaRatio)

        if self.protectionRatio < PROTECTION_RATIO_MINIMUM:
            self.designNotes.append(
                f'Protection ratio is only {self.protectionRatio:.1f}. A particle above one third of the passage '
                f'diameter will lodge, so a ratio below {PROTECTION_RATIO_MINIMUM:.0f} does not protect the passage '
                f'at all.')
        elif self.protectionRatio < PROTECTION_RATIO_RECOMMENDED:
            self.designNotes.append(
                f'Protection ratio is {self.protectionRatio:.1f}, below the recommended {PROTECTION_RATIO_RECOMMENDED:.0f}. '
                f'Acceptable, with no margin for agglomeration, fibres or filter degradation.')

        return {
            'absoluteRating':  self.absoluteRating,
            'protectedPassage': self.protectedPassage,
            'protectionRatio': self.protectionRatio,
            'betaRatio':       self.betaRatio,
            'efficiency':      self.efficiency
        }

    def sizeElement(self, requiredLife: float = None, cleanFraction: float = 1.0 / 3.0) -> dict:

        '''

        Filtration area from the binding constraint: clean pressure drop, or service life.

        The clean element behaves as a porous medium and follows Darcy's law:

            dP = mu * v * t / k

        with `v` the face velocity (volumetric flow over filtration area), `t` the medium thickness
        and `k` the permeability. Rearranged for area:

            A = mu * Q * t / (k * dP)

        **Size on the clean pressure drop and then check the loaded case.** A filter that just meets
        its budget clean will exceed it as soon as it starts collecting anything, and the whole
        point of the filter is that it collects things. `cleanFraction` defaults to one third of the
        allowable, so the element can double its dP twice before the budget is spent.

        **The pressure drop constraint is usually NOT the binding one.** A clean metal filter element
        has a very low resistance, so sizing on dP alone produces a tiny element with a face velocity
        of metres per second and a dirt capacity measured in milligrams. It meets its pressure budget
        on day one and plugs almost immediately.

        What actually sizes a filter is **dirt capacity**, and therefore life:

            A = (contamination loading * volumetric flow * required life) / (dirt capacity per area)

        Pass `requiredLife` in seconds and the larger of the two areas wins, which is the same
        binding-constraint pattern used by `Line.sizeDiameter`. Without it, only the pressure drop
        constraint is applied and the class warns if the resulting face velocity is impractically
        high.

        The pleat area factor is applied to the envelope: a pleated element packs eight times the
        filtration area into the same envelope, which is eight times the dirt capacity and one eighth
        of the clean pressure drop for the same package size.

        '''

        if np.isnan(self.allowableCleanPressureDrop):
            raise InvalidInputError(
                message       = 'sizeElement needs a clean pressure drop budget.',
                parameterName = 'allowableCleanPressureDrop', value = self.allowableCleanPressureDrop,
                validRange    = 'Positive real'
            )

        filterData     = FILTER_TYPES[self.filterType.strip().lower()]
        volumetricFlow = self.massFlow / self.density

        # -- Pressure drop constraint -- #
        pressureArea = (self.viscosity * volumetricFlow * filterData['thickness'] /
                        (filterData['permeability'] * self.allowableCleanPressureDrop * cleanFraction))

        # -- Life constraint -- #
        lifeArea = 0.0
        if requiredLife is not None:
            if np.isnan(self.contaminationLoading):
                raise InvalidInputError(
                    message       = 'Sizing on life needs the contamination loading in the fluid [kg/m^3].',
                    parameterName = 'contaminationLoading', value = self.contaminationLoading,
                    validRange    = 'Positive real'
                )
            lifeArea = (self.contaminationLoading * volumetricFlow * requiredLife /
                        filterData['dirtCapacity'])

        self.filtrationArea = max(pressureArea, lifeArea)
        self.envelopeArea   = self.filtrationArea / filterData['areaFactor']

        self.calculatePressureDrop()

        # Dirt capacity, in mass of contamination held before the clean dP doubles
        self.dirtCapacity = self.filtrationArea * filterData['dirtCapacity']

        # Face velocity sanity check. A metal filter element run above roughly 50 mm/s in a liquid is
        # being asked to work as a restriction rather than as a filter: the residence time in the
        # medium is too short for reliable capture and the dirt capacity is negligible.
        if self.faceVelocity > 0.05 and requiredLife is None:
            self.designNotes.append(
                f'Face velocity is {self.faceVelocity * 1.0e3:.1f} mm/s, which is high for a metal filter element. '
                f'The element was sized on pressure drop alone and its dirt capacity is only '
                f'{self.filtrationArea * filterData["dirtCapacity"] * 1.0e3:.4f} g. Pass requiredLife to sizeElement '
                f'so the life constraint is applied, or use a pleated element.')

        return {
            'filtrationArea':      self.filtrationArea,
            'envelopeArea':        self.envelopeArea,
            'pressureLimitedArea': pressureArea,
            'lifeLimitedArea':     lifeArea,
            'bindingConstraint':   'life' if lifeArea > pressureArea else 'pressure drop',
            'faceVelocity':        self.faceVelocity,
            'cleanPressureDrop':   self.cleanPressureDrop,
            'dirtCapacity':        self.dirtCapacity
        }

    def calculatePressureDrop(self, loadingFraction: float = 0.0) -> float:

        '''

        Clean and loaded pressure drop.

            dP = mu * v * t / k * (1 + loading effect)

        The loading effect is modelled as a simple linear rise to double the clean dP at full dirt
        capacity, which is the conventional definition of "spent" for a filter element.

        `loadingFraction` is the collected contamination as a fraction of the dirt capacity: 0 for a
        clean element, 1 for a fully loaded one.

        In reality the dP rise is not linear; it is slow at first as particles bridge the pores, then
        very steep as the cake forms. The linear model is deliberately optimistic in the middle and
        it should not be used to predict the end of life precisely. Instrument the filter with a
        differential pressure gauge and change it on measured dP, not on hours.

        '''

        if np.isnan(self.filtrationArea):
            raise InvalidInputError(
                message       = 'calculatePressureDrop needs a filtration area. Set filtrationArea, or call sizeElement().',
                parameterName = 'filtrationArea', value = self.filtrationArea, validRange = 'Positive real'
            )

        filterData     = FILTER_TYPES[self.filterType.strip().lower()]
        volumetricFlow = self.massFlow / self.density

        self.faceVelocity      = volumetricFlow / self.filtrationArea
        self.cleanPressureDrop = (self.viscosity * self.faceVelocity * filterData['thickness'] /
                                  filterData['permeability'])

        return self.cleanPressureDrop * (1.0 + loadingFraction)

    def calculateLife(self, operatingTime: float = None) -> dict:

        '''

        Service life from the contamination loading in the fluid.

            life = dirt capacity / (contamination loading * volumetric flow)

        The contamination loading is the mass of particulate per unit volume of fluid. For a
        propellant to MIL-PRF-26536 monopropellant grade the particulate limit is 1 mg/L, which is
        1e-3 kg/m^3. For an unfiltered ground system it can be orders of magnitude higher, and for a
        newly built system the first flush carries far more than steady-state operation.

        **The first flush dominates.** A newly assembled system sheds its own construction debris:
        weld spatter, machining chips, thread debris, blast media, and whatever came off the inside
        of the tubing. That is why systems are flushed with a temporary coarse filter before the
        flight filter is installed, and why the flight filter is often installed at the last possible
        assembly step.

        '''

        if np.isnan(self.dirtCapacity):
            raise InvalidInputError(
                message       = 'calculateLife needs the dirt capacity. Call sizeElement() first.',
                parameterName = 'dirtCapacity', value = self.dirtCapacity, validRange = 'Positive real'
            )

        if np.isnan(self.contaminationLoading):
            raise InvalidInputError(
                message       = 'calculateLife needs the contamination loading in the fluid [kg/m^3].',
                parameterName = 'contaminationLoading', value = self.contaminationLoading,
                validRange    = 'Positive real'
            )

        volumetricFlow   = self.massFlow / self.density
        contaminationRate = self.contaminationLoading * volumetricFlow   # kg/s

        self.serviceLife = self.dirtCapacity / contaminationRate

        result = {
            'dirtCapacity':        self.dirtCapacity,
            'contaminationRate':   contaminationRate,
            'serviceLifeSeconds':  self.serviceLife,
            'serviceLifeHours':    self.serviceLife / 3600.0,
            'throughputVolume':    volumetricFlow * self.serviceLife,
            'throughputMass':      self.massFlow * self.serviceLife
        }

        if operatingTime is not None:
            loading = operatingTime / self.serviceLife
            result['loadingFraction']    = loading
            result['pressureDropAtTime'] = self.calculatePressureDrop(min(loading, 1.0))
            result['adequate']           = loading < 1.0
            if loading >= 1.0:
                self.designNotes.append(
                    f'The element reaches its dirt capacity in {self.serviceLife / 3600.0:.2f} hours, against a '
                    f'{operatingTime / 3600.0:.2f} hour requirement. Increase the filtration area, use a pleated '
                    f'element, or add a coarser prefilter upstream.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        filterData = FILTER_TYPES[self.filterType.strip().lower()]

        rows = [
            ['Fluid',                 f'{self.fluid}'],
            ['Filter type',           f'{self.filterType}'],
            ['Mass flow',             f'{self.massFlow:.6f} kg/s'],
            ['Density',               f'{self.density:.4f} kg/m^3'],
            ['Viscosity',             f'{self.viscosity:.5e} Pa-s'],
            ['Absolute rating',       f'{self.absoluteRating * 1.0e6:.2f} micron' if not np.isnan(self.absoluteRating) else 'not selected'],
            ['Beta ratio',            f'{self.betaRatio}'],
            ['Efficiency at rating',  f'{self.efficiency * 100.0:.3f} %' if not np.isnan(self.efficiency) else 'not evaluated'],
            ['Protected passage',     f'{self.protectedPassage * 1.0e6:.1f} micron' if not np.isnan(self.protectedPassage) else 'not specified'],
            ['Protection ratio',      f'{self.protectionRatio:.2f}' if not np.isnan(self.protectionRatio) else 'not evaluated'],
            ['Filtration area',       f'{self.filtrationArea * 1.0e4:.4f} cm^2' if not np.isnan(self.filtrationArea) else 'not sized'],
            ['Envelope area',         f'{self.envelopeArea * 1.0e4:.4f} cm^2' if not np.isnan(self.envelopeArea) else 'not sized'],
            ['Pleat area factor',     f'{filterData["areaFactor"]:.1f}'],
            ['Face velocity',         f'{self.faceVelocity * 1.0e3:.4f} mm/s' if not np.isnan(self.faceVelocity) else 'not evaluated'],
            ['Clean pressure drop',   f'{self.cleanPressureDrop / 1.0e3:.4f} kPa' if not np.isnan(self.cleanPressureDrop) else 'not evaluated'],
            ['Dirt capacity',         f'{self.dirtCapacity * 1.0e3:.4f} g' if not np.isnan(self.dirtCapacity) else 'not evaluated'],
            ['Cleanable',             f'{filterData["cleanable"]}'],
            ['Maximum temperature',   f'{filterData["maximumTemperature"]:.0f} K']
        ]

        if not np.isnan(self.serviceLife):
            rows.append(['Service life', f'{self.serviceLife / 3600.0:.3f} hours'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'FILTER REPORT')

        report += f'\n\nELEMENT NOTES\n{"-" * 60}\n{filterData["description"]}\n{filterData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'filterReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.filterType.strip().lower() not in FILTER_TYPES:
            raise InvalidInputError(
                message       = f'Unknown filter type \'{self.filterType}\'.',
                parameterName = 'filterType', value = self.filterType,
                validRange    = str(sorted(FILTER_TYPES.keys()))
            )

        if self.massFlow <= 0.0:
            raise InvalidInputError(
                message       = 'Filter mass flow must be positive.',
                parameterName = 'massFlow', value = self.massFlow, validRange = 'Greater than 0 kg/s'
            )

        if self.betaRatio < 2:
            raise InvalidInputError(
                message       = 'Beta ratio must be at least 2 (50 percent efficiency).',
                parameterName = 'betaRatio', value = self.betaRatio, validRange = '2 or greater'
            )
