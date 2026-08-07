
# -- Pressurization Class Definition -- #

'''

Pressurant sizing for regulated and blowdown propellant feed systems.

Every pressure-fed system has to answer one question: how much pressurant, in how big a bottle, at
what pressure. The answer determines a surprising fraction of the dry mass of a small spacecraft,
because a composite overwrapped pressure vessel at 30 MPa is heavy and the gas inside it is not.

Two architectures:

**Regulated.** A high pressure bottle feeds a regulator which holds the propellant tank at constant
pressure. Thrust is constant over the whole burn, the propellant tank is sized for the regulated
pressure only, and the cost is a regulator (a single point failure with a well-documented failure
mode), a high pressure bottle, isolation valves, and relief protection downstream of the regulator.

**Blowdown.** The propellant tank is charged with pressurant once, at the start, and the pressure
falls as propellant is consumed. No regulator, no separate bottle, no isolation valves. The cost is
that thrust falls with pressure -- a 4:1 blowdown delivers its last impulse at a quarter of the
initial thrust -- and that the propellant tank has to be sized for the initial pressure and has to
be large enough to hold the initial ullage as well as the propellant.

For a small satellite the blowdown system wins on almost every axis except performance, which is why
it is the default. For anything with a demanding thrust or mixture ratio requirement, the regulated
system wins.

The class computes both, using real gas properties from the property backend rather than the ideal
gas law, because helium at 30 MPa has a compressibility factor around 1.18 and treating it as ideal
under-predicts the stored mass by nearly 20 percent.

See Also:
---------
Regulator        : The regulator itself, its droop and its failure modes
MonopropThruster : The thrust decay a blowdown system produces
Line             : The feed line the pressurant travels through

Theory: docs/PressurizationAndBlowdown.md

Author: Sean Bowman
Date:   08/04/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                       R_UNIVERSAL, speciesMolarMass, PA_PER_PSIA,
                       InvalidInputError, createErrorContext)
except ImportError:
    from .utils import (fluidProps, applyInputs, secantSolve, formatReportTable,
                        R_UNIVERSAL, speciesMolarMass, PA_PER_PSIA,
                        InvalidInputError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Pressurant gas selection data.
#
# The molar mass column is the whole story for a regulated system: pressurant mass scales directly
# with molar mass at a given pressure and volume, so helium costs one seventh the mass of nitrogen
# for the same job. That is why every mass-critical system uses helium despite its cost, its
# permeability and its tendency to leak through anything.
PRESSURANT_GASES = {
    'helium': {
        'species': 'Helium', 'molarMass': 4.002602e-3,
        'notes': 'One seventh the mass of nitrogen for the same pressure-volume, which is decisive for flight '
                 'mass. Leaks through everything, permeates elastomers faster than any other gas, and is '
                 'expensive. Low solubility in most propellants, which matters because dissolved pressurant '
                 'comes out of solution in the feed line and in the injector.'
    },
    'nitrogen': {
        'species': 'Nitrogen', 'molarMass': 28.01348e-3,
        'notes': 'Seven times the mass of helium for the same job, which rules it out for most flight systems. '
                 'Cheap, available everywhere, and the standard for ground systems and for test stands. '
                 'Dissolves appreciably in hydrazine and in hydrocarbons, which can cause feed system gassing. '
                 'Liquefies at 77 K, so it cannot pressurize a cryogenic tank colder than that.'
    },
    'argon': {
        'species': 'Argon', 'molarMass': 39.948e-3,
        'notes': 'Heavier still. Used where chemical inertness with an exotic propellant matters more than mass.'
    }
}

# Ullage collapse factor: the ratio of actual pressurant required to the ideal adiabatic requirement.
#
# The ideal calculation assumes the ullage gas neither gains nor loses heat. In reality it loses heat
# to the tank wall and to the cold propellant surface, its temperature falls, its density rises, and
# more mass is needed to hold the same pressure. That is ullage collapse, and it is the single
# largest correction in pressurant sizing.
#
# The factor depends on how much wall area the ullage sees, how cold the propellant is, and how long
# the expulsion takes. A slow expulsion into a cold cryogenic tank is the worst case.
COLLAPSE_FACTORS = {
    'storable, fast expulsion':    1.10,   # minutes, ambient propellant
    'storable, slow expulsion':    1.25,   # hours, ambient propellant
    'storable, spacecraft duty':   1.15,   # long duration, many small expulsions, near equilibrium
    'cryogenic, fast expulsion':   1.35,   # the gas is cooled hard by the propellant surface
    'cryogenic, slow expulsion':   1.60,   # worst case
    'ideal':                       1.00    # no heat transfer, for comparison only
}

# Bottle expansion process. A bottle discharging quickly cools substantially, which reduces the mass
# that can be extracted before the bottle pressure falls to the regulator lockup point.
BOTTLE_PROCESSES = {
    'isothermal': 'Bottle stays at ambient temperature throughout. Correct for a slow discharge with '
                  'good thermal contact, and the optimistic bound.',
    'adiabatic':  'Bottle receives no heat during discharge and cools as it empties. Correct for a fast '
                  'discharge, and the conservative bound. The residual mass left in the bottle is '
                  'significantly higher.'
}

class Pressurization:

    '''

    Pressurant mass and bottle sizing for regulated and blowdown feed systems.

    Primary Input Properties:
    -------------------------
    architecture : str
        'regulated' or 'blowdown'
    pressurant : str
        Key into PRESSURANT_GASES
    propellantVolume : float
        Volume of propellant to be expelled [m^3]
    tankPressure : float
        Regulated tank pressure, or initial tank pressure for a blowdown [Pa]
    finalTankPressure : float
        Final tank pressure for a blowdown [Pa]. Alternatively set blowdownRatio.
    blowdownRatio : float
        Initial over final tank pressure [-]
    tankTemperature : float
        Propellant tank temperature [K]
    bottlePressure : float
        Initial pressurant bottle pressure [Pa]. Regulated architecture only.
    bottleTemperature : float
        Bottle temperature [K]
    regulatorLockupPressure : float
        Minimum bottle pressure at which the regulator still works [Pa]
    collapseFactorKey : str
        Key into COLLAPSE_FACTORS
    bottleProcess : str
        'isothermal' or 'adiabatic'
    polytropicExponent : float
        Ullage expansion exponent for the blowdown, 1.0 isothermal to gamma adiabatic

    Key Output Properties:
    ----------------------
    pressurantMass : float
        Total pressurant mass required [kg]
    bottleVolume : float
        Required bottle internal volume [m^3]
    initialUllageVolume : float
        Blowdown initial ullage [m^3]
    totalTankVolume : float
        Blowdown tank volume including ullage [m^3]
    residualMass : float
        Pressurant left in the bottle at lockup [kg]
    usableMassFraction : float
        Fraction of the loaded pressurant that is usable [-]

    Public Methods:
    ---------------
    setInputs(inputs)              Load a configuration dictionary
    calculateRegulated()           Pressurant mass and bottle sizing for a regulated system
    calculateBlowdown()            Ullage volume and pressurant mass for a blowdown system
    comparePressurants()           Side by side gas selection table
    generateReport(outputDir)      Formatted results table

    Typical Workflow:
    -----------------
    >>> system = Pressurization()
    >>> system.setInputs({'architecture': 'blowdown', 'pressurant': 'helium',
    ...                   'propellantVolume': 0.030, 'tankPressure': 2.4e6,
    ...                   'blowdownRatio': 4.0, 'tankTemperature': 293.15})
    >>> system.calculateBlowdown()
    >>> print(system.generateReport())

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Architecture -- #

        self.architecture             = 'blowdown'  # 'regulated' or 'blowdown'
        self.pressurant               = 'helium'    # key into PRESSURANT_GASES

        # -- Propellant Tank -- #

        self.propellantVolume         = np.nan  # [m^3], volume to be expelled
        self.tankPressure             = np.nan  # [Pa], regulated pressure or initial blowdown pressure
        self.finalTankPressure        = np.nan  # [Pa], blowdown only
        self.blowdownRatio            = np.nan  # [-], alternative to finalTankPressure
        self.tankTemperature          = 293.15  # [K]

        # -- Pressurant Bottle -- #

        self.bottlePressure           = np.nan  # [Pa], regulated only
        self.bottleTemperature        = 293.15  # [K]
        self.regulatorLockupPressure  = np.nan  # [Pa], minimum usable bottle pressure

        # -- Model Selection -- #

        self.collapseFactorKey        = 'storable, spacecraft duty'  # key into COLLAPSE_FACTORS
        self.collapseFactor           = np.nan  # [-], overrides the lookup
        self.bottleProcess            = 'isothermal'  # 'isothermal' or 'adiabatic'

        # Ullage expansion exponent for a blowdown. 1.0 is isothermal (slow expulsion, gas in
        # equilibrium with the tank wall) and gamma is adiabatic (fast expulsion). Spacecraft duty
        # cycles are close to isothermal because the expulsion happens over months.
        self.polytropicExponent       = 1.0     # [-]

        # -- Results -- #

        self.pressurantMass           = np.nan  # [kg], total loaded
        self.usablePressurantMass     = np.nan  # [kg]
        self.residualMass             = np.nan  # [kg], left at lockup
        self.usableMassFraction       = np.nan  # [-]
        self.bottleVolume             = np.nan  # [m^3]
        self.initialUllageVolume      = np.nan  # [m^3], blowdown
        self.finalUllageVolume        = np.nan  # [m^3], blowdown
        self.totalTankVolume          = np.nan  # [m^3], blowdown
        self.ullageFraction           = np.nan  # [-], blowdown initial ullage over tank volume
        self.bottleDensityInitial     = np.nan  # [kg/m^3]
        self.bottleDensityFinal       = np.nan  # [kg/m^3]
        self.bottleFinalTemperature   = np.nan  # [K]
        self.tankGasDensity           = np.nan  # [kg/m^3]
        self.compressibilityFactor    = np.nan  # [-], bottle initial
        self.designNotes              = []      # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: propellantVolume, tankPressure.

        '''

        requiredParams = {
            'propellantVolume': 'Propellant volume to be expelled not provided.',
            'tankPressure':     'Tank pressure not provided.'
        }

        optionalParams = ['architecture', 'pressurant', 'finalTankPressure', 'blowdownRatio',
                          'tankTemperature', 'bottlePressure', 'bottleTemperature',
                          'regulatorLockupPressure', 'collapseFactorKey', 'collapseFactor',
                          'bottleProcess', 'polytropicExponent']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def calculateRegulated(self) -> dict:

        '''

        Pressurant mass and bottle sizing for a regulated system.

        **Ullage requirement.** The tank ullage must be filled with gas at the regulated pressure as
        the propellant leaves. With ideal gas and an adiabatic tank, the energy balance on the ullage
        gives the perhaps surprising result that the final ullage temperature equals the supply
        temperature, so the ideal requirement is simply

            m_ullage = rho(P_tank, T_supply) * V_propellant

        **Collapse factor.** In reality the ullage gas loses heat to the tank wall and to the cold
        propellant surface, its temperature falls, its density rises, and more mass is needed to hold
        the same pressure. That is ullage collapse, and it is the largest correction in the whole
        calculation: 10 percent for a fast storable expulsion, up to 60 percent for a slow cryogenic
        one.

        **Bottle sizing.** The bottle must hold the ullage requirement plus a residual, because the
        regulator stops working when the bottle pressure falls to its lockup point. The usable mass
        is the difference between the loaded density and the density at lockup:

            V_bottle = m_required / ( rho(P_initial, T_initial) - rho(P_lockup, T_final) )

        For an isothermal discharge `T_final = T_initial`. For an adiabatic discharge the bottle
        cools as it empties:

            T_final = T_initial * (P_lockup / P_initial)^((gamma-1)/gamma)

        and the residual density is higher, so more gas is left behind. The isothermal case is the
        optimistic bound and the adiabatic case the conservative one; a real bottle is between them
        and closer to isothermal for a slow spacecraft expulsion.

        **Real gas properties are used throughout.** Helium at 30 MPa and 293 K has a
        compressibility factor of about 1.18, so the ideal gas law under-predicts the stored mass by
        nearly 20 percent. That error goes directly into the bottle volume and therefore into the
        vehicle dry mass.

        '''

        gasData = PRESSURANT_GASES[self.pressurant.strip().lower()]
        species = gasData['species']

        if np.isnan(self.bottlePressure):
            raise InvalidInputError(
                message       = 'A regulated system needs an initial bottle pressure.',
                parameterName = 'bottlePressure', value = self.bottlePressure, validRange = 'Positive real'
            )

        lockupPressure = self.regulatorLockupPressure
        if np.isnan(lockupPressure):
            # A regulator needs a working differential to function. A common rule is that the bottle
            # must stay at least 10 to 20 percent above the regulated pressure, and 1.2x is a
            # reasonable default.
            lockupPressure = 1.2 * self.tankPressure
            self.regulatorLockupPressure = lockupPressure
            self.designNotes.append(
                f'Regulator lockup pressure not specified; assumed {lockupPressure / 1.0e6:.3f} MPa, which is 1.2 '
                f'times the regulated pressure. A real regulator has a stated minimum inlet pressure and it '
                f'should be used instead.')

        # -- Ullage requirement -- #
        collapseFactor = self._collapseFactor()

        self.tankGasDensity   = float(fluidProps(species, 'TP', 'D', self.tankTemperature, self.tankPressure))
        idealUllageMass       = self.tankGasDensity * self.propellantVolume
        self.usablePressurantMass = idealUllageMass * collapseFactor

        # -- Bottle sizing -- #
        self.bottleDensityInitial = float(fluidProps(species, 'TP', 'D', self.bottleTemperature, self.bottlePressure))

        if self.bottleProcess.strip().lower() == 'adiabatic':
            gamma = float(fluidProps(species, 'TP', 'Cp/Cv', self.bottleTemperature, self.bottlePressure))
            self.bottleFinalTemperature = self.bottleTemperature * (lockupPressure / self.bottlePressure)**((gamma - 1.0) / gamma)
        else:
            self.bottleFinalTemperature = self.bottleTemperature

        self.bottleDensityFinal = float(fluidProps(species, 'TP', 'D', self.bottleFinalTemperature, lockupPressure))

        usableDensity = self.bottleDensityInitial - self.bottleDensityFinal
        if usableDensity <= 0.0:
            raise InvalidInputError(
                message       = ('The bottle lockup density exceeds the initial density, so no gas can be extracted. '
                                 'Check that the bottle pressure is above the lockup pressure.'),
                parameterName = 'bottlePressure', value = self.bottlePressure,
                validRange    = f'Greater than {lockupPressure:.6g} Pa'
            )

        self.bottleVolume       = self.usablePressurantMass / usableDensity
        self.pressurantMass     = self.bottleDensityInitial * self.bottleVolume
        self.residualMass       = self.bottleDensityFinal * self.bottleVolume
        self.usableMassFraction = self.usablePressurantMass / self.pressurantMass

        # Compressibility factor, for visibility
        specificGasConstant        = R_UNIVERSAL / gasData['molarMass']
        idealDensity               = self.bottlePressure / (specificGasConstant * self.bottleTemperature)
        self.compressibilityFactor = idealDensity / self.bottleDensityInitial

        if abs(self.compressibilityFactor - 1.0) > 0.05:
            self.designNotes.append(
                f'{species} at {self.bottlePressure / 1.0e6:.1f} MPa has a compressibility factor of '
                f'{self.compressibilityFactor:.3f}. An ideal gas calculation would be wrong by '
                f'{abs(self.compressibilityFactor - 1.0) * 100.0:.1f} percent on stored mass, and that error goes '
                f'straight into the bottle volume.')

        if self.usableMassFraction < 0.6:
            self.designNotes.append(
                f'Only {self.usableMassFraction * 100.0:.1f} percent of the loaded pressurant is usable; the rest is '
                f'residual at regulator lockup. Raising the bottle pressure or lowering the regulated pressure both '
                f'improve this.')

        return {
            'pressurantMass':       self.pressurantMass,
            'usablePressurantMass': self.usablePressurantMass,
            'residualMass':         self.residualMass,
            'usableMassFraction':   self.usableMassFraction,
            'bottleVolume':         self.bottleVolume,
            'collapseFactor':       collapseFactor,
            'compressibilityFactor': self.compressibilityFactor
        }

    def calculateBlowdown(self) -> dict:

        '''

        Ullage volume and pressurant mass for a blowdown system.

        The ullage gas expands polytropically as the propellant leaves:

            P_initial * V_initial^n = P_final * V_final^n
            V_final = V_initial + V_propellant

        so for a blowdown ratio `B = P_initial / P_final`:

            V_initial = V_propellant / ( B^(1/n) - 1 )

        For an isothermal expansion (`n = 1`) and a 4:1 blowdown, the initial ullage is one third of
        the propellant volume, so the tank must be 33 percent larger than the propellant it holds.
        That is the real cost of a blowdown system and it is often larger than the mass of the
        regulator and bottle it replaces.

        | Blowdown ratio | Initial ullage / propellant volume | Tank oversizing |
        |---|---|---|
        | 2:1 | 100 % | 2.0x |
        | 3:1 | 50 % | 1.5x |
        | **4:1** | **33 %** | **1.33x** |
        | 5:1 | 25 % | 1.25x |
        | 10:1 | 11 % | 1.11x |

        A higher blowdown ratio needs less ullage but delivers a wider thrust range, and beyond about
        4:1 the low-end thrust becomes impractical. That trade is why 4:1 is close to universal.

        `n = 1.0` is isothermal, correct for a slow spacecraft expulsion over months where the gas
        stays in equilibrium with the tank wall. `n = gamma` is adiabatic, correct for a fast
        expulsion, and it requires MORE initial ullage for the same blowdown ratio because the gas
        cools as it expands and loses pressure faster.

        '''

        gasData = PRESSURANT_GASES[self.pressurant.strip().lower()]
        species = gasData['species']

        # Resolve the blowdown ratio
        blowdownRatio = self.blowdownRatio
        if np.isnan(blowdownRatio):
            if np.isnan(self.finalTankPressure):
                raise InvalidInputError(
                    message       = 'A blowdown system needs either a blowdownRatio or a finalTankPressure.',
                    parameterName = 'blowdownRatio', value = blowdownRatio, validRange = 'Greater than 1'
                )
            blowdownRatio      = self.tankPressure / self.finalTankPressure
            self.blowdownRatio = blowdownRatio
        else:
            self.finalTankPressure = self.tankPressure / blowdownRatio

        exponent = self.polytropicExponent

        # -- Ullage volumes -- #
        self.initialUllageVolume = self.propellantVolume / (blowdownRatio**(1.0 / exponent) - 1.0)
        self.finalUllageVolume   = self.initialUllageVolume + self.propellantVolume
        self.totalTankVolume     = self.finalUllageVolume
        self.ullageFraction      = self.initialUllageVolume / self.totalTankVolume

        # -- Pressurant mass -- #
        # Real gas density at the initial charge condition. No collapse factor is applied here,
        # because the pressurant is loaded once and allowed to equilibrate before the mission
        # begins; there is no transient expulsion to cool it.
        self.tankGasDensity  = float(fluidProps(species, 'TP', 'D', self.tankTemperature, self.tankPressure))
        self.pressurantMass  = self.tankGasDensity * self.initialUllageVolume

        # All of it is usable in the sense that none is stranded in a bottle, but none of it is
        # recoverable either: the gas ends up spread through the tank at the final pressure.
        self.usablePressurantMass = self.pressurantMass
        self.residualMass         = 0.0
        self.usableMassFraction   = 1.0
        self.bottleVolume         = 0.0

        specificGasConstant        = R_UNIVERSAL / gasData['molarMass']
        idealDensity               = self.tankPressure / (specificGasConstant * self.tankTemperature)
        self.compressibilityFactor = idealDensity / self.tankGasDensity

        if blowdownRatio > 5.0:
            self.designNotes.append(
                f'Blowdown ratio {blowdownRatio:.2f} means the final thrust is {1.0 / blowdownRatio * 100.0:.1f} '
                f'percent of the initial. The attitude control system has to be stable across that range and the '
                f'minimum impulse bit changes by the same factor.')

        if blowdownRatio < 2.0:
            self.designNotes.append(
                f'Blowdown ratio {blowdownRatio:.2f} requires an initial ullage of '
                f'{self.initialUllageVolume / self.propellantVolume * 100.0:.0f} percent of the propellant volume. '
                f'At that point a regulated system is almost certainly lighter.')

        return {
            'blowdownRatio':       blowdownRatio,
            'initialUllageVolume': self.initialUllageVolume,
            'totalTankVolume':     self.totalTankVolume,
            'ullageFraction':      self.ullageFraction,
            'pressurantMass':      self.pressurantMass,
            'finalTankPressure':   self.finalTankPressure,
            'tankOversizing':      self.totalTankVolume / self.propellantVolume
        }

    def comparePressurants(self) -> str:

        '''

        Side by side pressurant gas comparison at the current conditions.

        The mass column is the decision. Helium is one seventh the mass of nitrogen for the same
        pressure-volume, which for a flight system is decisive and for a ground system is irrelevant.

        '''

        savedPressurant = self.pressurant
        rows = []

        for key, data in PRESSURANT_GASES.items():

            self.pressurant = key

            try:
                if self.architecture.strip().lower() == 'regulated':
                    result = self.calculateRegulated()
                    massValue   = result['pressurantMass']
                    volumeValue = result['bottleVolume'] * 1.0e3
                else:
                    result = self.calculateBlowdown()
                    massValue   = result['pressurantMass']
                    volumeValue = result['initialUllageVolume'] * 1.0e3
            except Exception:
                continue

            rows.append([
                data['species'],
                f'{data["molarMass"] * 1.0e3:.3f}',
                f'{massValue:.4f}',
                f'{volumeValue:.3f}',
                f'{self.compressibilityFactor:.4f}'
            ])

        self.pressurant = savedPressurant
        if self.architecture.strip().lower() == 'regulated':
            self.calculateRegulated()
        else:
            self.calculateBlowdown()

        volumeHeader = 'Bottle [L]' if self.architecture.strip().lower() == 'regulated' else 'Ullage [L]'

        return formatReportTable(rows,
                                 ['Gas', 'MW [g/mol]', 'Mass [kg]', volumeHeader, 'Z'],
                                 title = f'PRESSURANT COMPARISON  ({self.architecture}, '
                                         f'{self.propellantVolume * 1.0e3:.1f} L propellant, '
                                         f'{self.tankPressure / 1.0e6:.2f} MPa tank)')

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table.

        '''

        gasData = PRESSURANT_GASES[self.pressurant.strip().lower()]

        rows = [
            ['Architecture',          f'{self.architecture}'],
            ['Pressurant',            f'{gasData["species"]}'],
            ['Propellant volume',     f'{self.propellantVolume * 1.0e3:.3f} L'],
            ['Tank pressure',         f'{self.tankPressure / 1.0e6:.4f} MPa ({self.tankPressure / PA_PER_PSIA:.1f} psia)'],
            ['Tank temperature',      f'{self.tankTemperature:.2f} K'],
            ['Tank gas density',      f'{self.tankGasDensity:.4f} kg/m^3'],
            ['Compressibility Z',     f'{self.compressibilityFactor:.4f}'],
            ['Pressurant mass',       f'{self.pressurantMass:.5f} kg']
        ]

        if self.architecture.strip().lower() == 'regulated':
            rows.extend([
                ['Bottle pressure',        f'{self.bottlePressure / 1.0e6:.4f} MPa'],
                ['Bottle temperature',     f'{self.bottleTemperature:.2f} K'],
                ['Bottle process',         f'{self.bottleProcess}'],
                ['Bottle final temperature', f'{self.bottleFinalTemperature:.2f} K'],
                ['Regulator lockup',       f'{self.regulatorLockupPressure / 1.0e6:.4f} MPa'],
                ['Bottle initial density', f'{self.bottleDensityInitial:.3f} kg/m^3'],
                ['Bottle final density',   f'{self.bottleDensityFinal:.3f} kg/m^3'],
                ['Collapse factor',        f'{self._collapseFactor():.3f}'],
                ['Usable pressurant',      f'{self.usablePressurantMass:.5f} kg'],
                ['Residual at lockup',     f'{self.residualMass:.5f} kg'],
                ['Usable mass fraction',   f'{self.usableMassFraction * 100.0:.2f} %'],
                ['Bottle volume',          f'{self.bottleVolume * 1.0e3:.3f} L']
            ])
        else:
            rows.extend([
                ['Blowdown ratio',         f'{self.blowdownRatio:.3f}'],
                ['Final tank pressure',    f'{self.finalTankPressure / 1.0e6:.4f} MPa'],
                ['Polytropic exponent',    f'{self.polytropicExponent:.3f}'],
                ['Initial ullage volume',  f'{self.initialUllageVolume * 1.0e3:.3f} L'],
                ['Total tank volume',      f'{self.totalTankVolume * 1.0e3:.3f} L'],
                ['Initial ullage fraction', f'{self.ullageFraction * 100.0:.2f} %'],
                ['Tank oversizing',        f'{self.totalTankVolume / self.propellantVolume:.3f}x propellant volume']
            ])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'PRESSURIZATION REPORT')

        report += f'\n\nPRESSURANT NOTES\n{"-" * 60}\n{gasData["notes"]}\n'

        for note in self.designNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'pressurizationReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.architecture.strip().lower() not in ('regulated', 'blowdown'):
            raise InvalidInputError(
                message       = f'Unknown architecture \'{self.architecture}\'.',
                parameterName = 'architecture', value = self.architecture,
                validRange    = 'regulated or blowdown'
            )

        if self.pressurant.strip().lower() not in PRESSURANT_GASES:
            raise InvalidInputError(
                message       = f'Unknown pressurant \'{self.pressurant}\'.',
                parameterName = 'pressurant', value = self.pressurant,
                validRange    = str(sorted(PRESSURANT_GASES.keys()))
            )

        if self.propellantVolume <= 0.0:
            raise InvalidInputError(
                message       = 'Propellant volume must be positive.',
                parameterName = 'propellantVolume', value = self.propellantVolume,
                validRange    = 'Greater than 0 m^3'
            )

        if self.tankPressure <= 0.0:
            raise InvalidInputError(
                message       = 'Tank pressure must be absolute and positive.',
                parameterName = 'tankPressure', value = self.tankPressure,
                validRange    = 'Greater than 0 Pa absolute'
            )

        if not np.isnan(self.blowdownRatio) and self.blowdownRatio <= 1.0:
            raise InvalidInputError(
                message       = 'Blowdown ratio must be greater than 1.',
                parameterName = 'blowdownRatio', value = self.blowdownRatio, validRange = 'Greater than 1'
            )

        # Nitrogen cannot pressurize a tank colder than its own condensation point at that pressure
        if self.pressurant.strip().lower() == 'nitrogen' and self.tankTemperature < 130.0:
            self.designNotes.append(
                f'Nitrogen pressurant at a {self.tankTemperature:.1f} K tank temperature will condense. Use helium '
                f'for any cryogenic tank colder than about 130 K.')

    def _collapseFactor(self) -> float:

        '''

        Ullage collapse factor, from the explicit override or the duty-cycle lookup.

        '''

        if not np.isnan(self.collapseFactor):
            return self.collapseFactor

        factor = COLLAPSE_FACTORS.get(self.collapseFactorKey.strip().lower())
        if factor is None:
            raise InvalidInputError(
                message       = f'Unknown collapse factor key \'{self.collapseFactorKey}\'.',
                parameterName = 'collapseFactorKey', value = self.collapseFactorKey,
                validRange    = str(sorted(COLLAPSE_FACTORS.keys()))
            )

        return factor
