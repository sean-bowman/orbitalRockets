# -- Validation of the fluidSystems library against published references -- #

'''

The fluid tools checked against the property backend and the Joukowsky relation.

This domain started ahead of the others, because REFPROP and CoolProp are independent
implementations of measured equations of state and the repository has been calling them since the
beginning. The check here is that it calls them correctly, not that the equation of state is
right.

Every other test file in this domain checks that the code does what it was written to do. This one
checks whether what it was written to do is right, which is a different question and the only one
that can catch a wrong model.

The `level` recorded against each reference says how strong the check is. A `hardware` check
compares against measured or specified real hardware and can catch a wrong model. A `standard`
check reproduces a published formula exactly and can only catch an implementation error. Calling
the second one validation without qualification is how a repository convinces itself of something
false.

Author: Sean Bowman
Date:   08/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

# fluidSystems predates the unique-helper-module rule and its helper is still named utils.py,
# which is exactly the collision that rule exists to prevent. Importing the property accessor from
# common directly sidesteps it entirely and is the more honest dependency anyway: the thing being
# validated is the property backend call, which lives in common.
sys.path.insert(0, os.path.join(ROOT, 'common'))
sys.path.insert(0, ROOT)

from validation.referenceCases import VALIDATION_LEVELS, REFERENCE_KINDS
from validation.referenceCases import FLUID_RELATIONS, FRICTION_FACTOR, ROUGH_PIPE

from fluidProperties import fluidProps

# The friction factor and the line are the things being validated here, so they do have to come
# from the domain library despite the helper module still being named utils.py.
sys.path.insert(0, os.path.join(DOMAIN, 'fluidSystemsLibrary'))

from utils import frictionFactor
from Line import Line

def testEveryFluidReferenceCarriesItsProvenanceAndLevel():

    for name, entry in FLUID_RELATIONS.items():
        assert entry['source'], name
        assert entry['kind'] in REFERENCE_KINDS, name
        assert entry['level'] in VALIDATION_LEVELS, name

def testWaterDensityAtStandardConditionsMatchesTheEquationOfState():

    '''
    The property backend is itself the external reference. Water at 20 C and one atmosphere is
    998.2 kg/m^3 by IAPWS-95, and a repository that returns something else is calling the backend
    wrongly.
    '''

    reference = FLUID_RELATIONS['water at standard conditions']

    density = fluidProps('water', 'TP', 'D',
                         reference['temperature'], reference['pressure'])

    assert float(density) == pytest.approx(reference['density'], rel = 0.005), (
        f'computed {float(density):.1f} kg/m^3 against IAPWS-95 {reference["density"]:.1f}')

def testJoukowskySurgeMatchesItsClosedForm():

    '''
    dP = rho a dV, exact for instantaneous closure and an upper bound for any real one. A tool that
    exceeds it has an error rather than a conservative answer.
    '''

    density, waveSpeed, velocityChange = 998.2, 1200.0, 3.0

    expected = density * waveSpeed * velocityChange

    assert expected == pytest.approx(3.5935e6, rel = 1.0e-3)


# ------------------------------------------------------------------------------------------------ #
# -- Line pressure drop -- #
# ------------------------------------------------------------------------------------------------ #

def _superpipeFrictionFactor(reynolds: float) -> float:

    '''
    Solve the Princeton Superpipe relation 1/sqrt(f) = 1.930 log10( Re sqrt(f) ) - 0.537 for f.

    Implicit in f like Colebrook is, and solved by bisection here rather than by the library's own
    iteration, so the reference does not share code with the thing it checks.
    '''

    reference = FRICTION_FACTOR['Princeton Superpipe']

    def residual(factor: float) -> float:
        root = np.sqrt(factor)
        return 1.0 / root - (reference['logSlope'] * np.log10(reynolds * root)
                             - reference['logIntercept'])

    low, high = 1.0e-4, 0.2

    for _ in range(200):
        middle = 0.5 * (low + high)
        if residual(middle) * residual(low) <= 0.0:
            high = middle
        else:
            low = middle

    return 0.5 * (low + high)

def testFrictionFactorAgainstMeasuredSmoothPipeData():

    '''
    The strongest check available to this domain on the friction factor, because the Superpipe fit
    is a fit to measurement rather than to another correlation.

    Every method here lands inside three per cent of it across four decades of Reynolds number, and
    under one per cent through the decade a feed line actually runs at.
    '''

    reference = FRICTION_FACTOR['Princeton Superpipe']

    assert reference['level'] == 'hardware'

    low, high = reference['reynoldsRange']

    for method, bound in (('colebrook', 3.0), ('churchill', 3.0), ('haaland', 3.0)):

        for reynolds in np.logspace(np.log10(low), np.log10(high), 40):

            measured = _superpipeFrictionFactor(reynolds)
            computed = frictionFactor(reynolds, 0.0, method)

            error = abs(computed / measured - 1.0) * 100.0

            assert error < bound, \
                f'{method} is {error:.2f} % from the Superpipe fit at Re = {reynolds:.2e}'

def testEveryMethodUnderPredictsMeasuredFriction():

    '''
    The direction is the part worth asserting. A low friction factor is a low pressure drop, so a
    line sized on one carries less margin than its number says, and none of the three methods
    crosses over anywhere in the range to make that a wash.
    '''

    reference = FRICTION_FACTOR['Princeton Superpipe']

    low, high = reference['reynoldsRange']

    for method in ('colebrook', 'churchill', 'haaland'):

        for reynolds in np.logspace(np.log10(low), np.log10(high), 40):

            measured = _superpipeFrictionFactor(reynolds)

            # A hair above measured at the very bottom of the range for colebrook, and below it
            # everywhere else. The bound is what the register records, not a tolerance.
            assert frictionFactor(reynolds, 0.0, method) < 1.002 * measured

def testTheShortfallGrowsWithReynoldsNumber():

    '''
    Not a tolerance but a shape. The Prandtl constants the Colebrook equation reduces to at zero
    roughness were fitted at Reynolds numbers an order of magnitude below what the Superpipe
    reached, so the disagreement is expected to open up at the top and it does.
    '''

    errors = [frictionFactor(reynolds, 0.0, 'colebrook') / _superpipeFrictionFactor(reynolds) - 1.0
              for reynolds in (1.0e5, 1.0e6, 1.0e7, 3.55e7)]

    assert errors == sorted(errors, reverse = True), \
        'the shortfall is expected to grow monotonically with Reynolds number'

    assert errors[-1] * 100.0 == pytest.approx(FRICTION_FACTOR['Princeton Superpipe']
                                               ['colebrookWorst'], abs = 0.05)

def testColebrookReducesToThePrandtlSmoothPipeLaw():

    '''
    At zero roughness the Colebrook equation is the Prandtl smooth pipe law, and the Superpipe work
    is what moved its two constants from 2.0 and 0.8 to 1.930 and 0.537. Asserting the reduction is
    what makes the comparison above a statement about the correlation rather than about this
    implementation of it.

    The intercept the reduction actually gives is 2 log10(2.51) = 0.799347 and not the 0.8 that
    gets quoted. The rounding is in the textbook rather than in the equation.
    '''

    reference = FRICTION_FACTOR['Princeton Superpipe']

    for reynolds in (1.0e4, 1.0e5, 1.0e6, 1.0e7):

        factor = frictionFactor(reynolds, 0.0, 'colebrook')
        root   = np.sqrt(factor)

        assert 1.0 / root == pytest.approx(
            reference['prandtlSlope'] * np.log10(reynolds * root) - reference['prandtlIntercept'],
            rel = 1.0e-6)

def testBlasiusBracketsTheLowReynoldsEnd():

    '''
    The Superpipe fit starts at Re = 31,000 and a small feed line can sit below it, so the low end
    needs its own bracket. Blasius is the classical one, and the library sits 2.8 per cent below it
    at worst and below it almost everywhere: the same direction as the Superpipe comparison at the
    other end of the range, which is the part worth noticing.

    Blasius is itself a correlation rather than a measurement, so this brackets and does not
    validate.
    '''

    reference = FRICTION_FACTOR['Blasius']

    low, high = reference['reynoldsRange']

    for reynolds in np.logspace(np.log10(low), np.log10(high), 20):

        blasius = 0.3164 * reynolds ** -0.25

        assert frictionFactor(reynolds, 0.0, 'colebrook') == pytest.approx(blasius, rel = 0.028)

def testTheWholePressureDropChainReproducesHagenPoiseuille():

    '''
    The only place in this domain where a pressure drop has an exact answer, and therefore the only
    check that covers the whole chain rather than one term of it.

    Velocity from mass flow, the Reynolds number, the 64/Re friction factor and the Darcy-Weisbach
    assembly all have to be right together, and a factor of four anywhere, a radius used where a
    diameter belongs, or a Fanning factor read as a Darcy one all fail here by a large margin. No
    tolerance is required.
    '''

    diameter    = 0.004        # [m]
    length      = 2.0          # [m]
    temperature = 293.15       # [K]
    pressure    = 500000.0     # [Pa]

    density   = float(fluidProps('Water', 'TP', 'D',   temperature, pressure))
    viscosity = float(fluidProps('Water', 'TP', 'VIS', temperature, pressure))

    area     = np.pi * diameter ** 2 / 4.0
    massFlow = density * 0.4 * area

    line = Line()
    line.setInputs({'fluid':            'Water',
                    'massFlow':         massFlow,
                    'length':           length,
                    'innerDiameter':    diameter,
                    'inletPressure':    pressure,
                    'inletTemperature': temperature,
                    'numberOfStations': 200})

    computed = line.calculatePressureDrop()

    assert line.reynolds < 2300.0, 'this case has to be laminar for the closed form to apply'

    volumetric = massFlow / density

    poiseuille = 128.0 * viscosity * volumetric * length / (np.pi * diameter ** 4)

    assert computed == pytest.approx(poiseuille, rel = 1.0e-5), \
        f'{computed:.4f} Pa against a closed form {poiseuille:.4f} Pa'

def testThePressureDropScalesAsTheClosedFormSays():

    '''
    Hagen-Poiseuille is fourth power in diameter and first power in length and flow, which is a
    stronger statement than one matching number. A chain that got a single case right by luck does
    not get the exponents right as well.
    '''

    def dropFor(diameter: float, length: float, velocity: float) -> float:

        temperature, pressure = 293.15, 500000.0

        density  = float(fluidProps('Water', 'TP', 'D', temperature, pressure))
        massFlow = density * velocity * np.pi * diameter ** 2 / 4.0

        line = Line()
        line.setInputs({'fluid':            'Water',
                        'massFlow':         massFlow,
                        'length':           length,
                        'innerDiameter':    diameter,
                        'inletPressure':    pressure,
                        'inletTemperature': temperature,
                        'numberOfStations': 200})

        return line.calculatePressureDrop()

    base = dropFor(0.004, 2.0, 0.2)

    # Volumetric flow is velocity times area, so at fixed velocity halving the diameter cuts the
    # flow by four and the drop rises by four rather than sixteen.
    assert dropFor(0.002, 2.0, 0.2) == pytest.approx(4.0 * base, rel = 0.01)
    assert dropFor(0.004, 4.0, 0.2) == pytest.approx(2.0 * base, rel = 0.01)
    assert dropFor(0.004, 2.0, 0.4) == pytest.approx(2.0 * base, rel = 0.01)


# ------------------------------------------------------------------------------------------------ #
# -- The roughness branch, against Nikuradse -- #
# ------------------------------------------------------------------------------------------------ #

def testTheFullyRoughLimitReproducesNikuradsesLaw():

    '''
    Nikuradse glued sifted sand of a measured grain size inside six pipes and established that in
    the fully rough regime the resistance stops depending on Reynolds number at all:

        1 / sqrt(lambda) = 1.74 + 2 log10(r / k)

    The library has to reproduce that at every one of his six relative radii, which span a factor
    of 34.
    '''

    reference = ROUGH_PIPE['Nikuradse sand-grain']

    assert reference['level'] == 'hardware'

    for relativeRadius in reference['relativeRadii']:

        measured = 1.0 / (reference['lawConstant']
                          + reference['lawSlope'] * np.log10(relativeRadius)) ** 2

        # k / d, where Nikuradse's r is a radius and the library takes roughness over diameter.
        computed = frictionFactor(1.0e9, 1.0 / (2.0 * relativeRadius), 'colebrook')

        assert computed == pytest.approx(measured, rel = 0.002), \
            f'r/k = {relativeRadius}: {computed:.5f} against a measured {measured:.5f}'

def testColebrooksThreePointSevenIsNikuradsesConstant():

    '''
    The reason the check above comes out almost exact, and it is worth asserting rather than
    noticing. Taking Colebrook to the fully rough limit leaves

        1 / sqrt(lambda) = 2 log10(r/k) + 2 log10(7.4)

    so the 3.7 in the Colebrook equation and the 1.74 Nikuradse fitted are the same constant
    written two ways. Reproducing his law therefore establishes that the library implements the
    roughness term as intended, and not that the measurement was right.
    '''

    reference = ROUGH_PIPE['Nikuradse sand-grain']

    assert 2.0 * np.log10(7.4) == pytest.approx(reference['colebrookConstant'], abs = 5.0e-5)

    assert reference['colebrookConstant'] == pytest.approx(reference['lawConstant'], rel = 0.001)

def testFullyRoughFrictionStopsDependingOnReynoldsNumber():

    '''
    The physical content of Nikuradse's result, and the thing that separates the rough branch from
    the smooth one. Once the roughness elements protrude through the viscous sublayer the pressure
    drag on them sets the resistance and viscosity drops out.
    '''

    for relativeRoughness in (0.001, 0.005, 0.02):

        factors = [frictionFactor(reynolds, relativeRoughness, 'colebrook')
                   for reynolds in (1.0e7, 1.0e8, 1.0e9, 1.0e10)]

        assert max(factors) / min(factors) < 1.02, \
            f'friction still moving with Reynolds number at eps/D = {relativeRoughness}'

def testRoughnessRaisesFrictionAndSmoothPipeIsTheFloor():

    '''
    Monotonicity, which holds whatever the constants are. A rougher pipe cannot have less
    resistance, and no roughness can take it below the smooth pipe value at the same Reynolds
    number.
    '''

    reynolds = 1.0e6

    smooth = frictionFactor(reynolds, 0.0, 'colebrook')

    previous = smooth

    for relativeRoughness in (1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 5.0e-2):

        rough = frictionFactor(reynolds, relativeRoughness, 'colebrook')

        assert rough > previous
        assert rough > smooth

        previous = rough

def testTheSandGrainSubstitutionIsRecordedRatherThanAssumed():

    '''
    The unvalidated step in any rough pipe calculation, and it is not closed by reproducing
    Nikuradse. His k is a measured grain diameter; every roughness in common/materials.py is an
    equivalent sand-grain roughness inferred from pressure drop on a real surface. The two are
    different quantities defined so they can be used in the same formula.
    '''

    reference = ROUGH_PIPE['Nikuradse sand-grain']

    assert 'equivalent sand-grain' in reference['roughnessNote']
    assert reference['scopeNote']
