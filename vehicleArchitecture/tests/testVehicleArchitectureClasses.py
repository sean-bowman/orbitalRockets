# -- Tests for the vehicleArchitecture classes -- #

'''

Tiered tests for the four vehicle-level classes.

Tier 1 covers the contract. Two refusals matter here: a sizing loop that diverges, and a stage
whose structure outweighs the propellant it would need. Both are open designs, and returning the
last iterate of a diverging loop would look exactly like a converged answer.

Tier 2 validates against closed forms and against a real vehicle. The Falcon 9 check is the only
external anchor in this domain and it validates the bookkeeping rather than any model.

Tier 3 covers the results the domain exists to produce: the staging optimum is flat, the loss
budget does not choose thrust to weight, payload elasticity scales inversely with payload fraction,
and one bar of feed pressure is worth several hundred kilograms of liftoff mass.

Author: Sean Bowman
Date:   09/08/2026

'''

import os
import sys

import numpy as np
import pytest

DOMAIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT   = os.path.dirname(DOMAIN)

sys.path.insert(0, os.path.join(DOMAIN, 'vehicleArchitectureLibrary'))
sys.path.insert(0, ROOT)

from vehicleUtils import (STANDARD_GRAVITY, MASS_GROWTH_ALLOWANCE, STRUCTURAL_COEFFICIENT_BAND,
                          LEO_ORBITAL_VELOCITY, exhaustVelocity, deltaV, structuralCoefficient,
                          massGrowthAllowance,
                          InvalidInputError, VehicleArchitectureError,
                          ClosureError, StagingError)
from StagedVehicle import StagedVehicle
from MassBudget import MassBudget, DEFAULT_MARGIN_POLICY
from AscentTrajectory import (AscentTrajectory, REFERENCE_THRUST_TO_WEIGHT,
                              REFERENCE_GRAVITY_LOSS, REFERENCE_DRAG_LOSS)
from SizingLoop import SizingLoop, NON_TANK_DRY_FRACTION

from validation.referenceCases import LAUNCH_VEHICLES, UNVALIDATED

# Falcon 9 Block 5, published stage masses.
FALCON_ONE_DRY,   FALCON_ONE_GROSS   = 22200.0, 433100.0
FALCON_TWO_DRY,   FALCON_TWO_GROSS   = 4000.0,  111500.0
FALCON_PAYLOAD_LEO = 22800.0

def buildVehicle(**overrides) -> StagedVehicle:

    inputs = {'stages': [{'specificImpulse': 297.0,
                          'structuralCoefficient': FALCON_ONE_DRY / FALCON_ONE_GROSS},
                         {'specificImpulse': 348.0,
                          'structuralCoefficient': FALCON_TWO_DRY / FALCON_TWO_GROSS}],
              'payloadMass':  FALCON_PAYLOAD_LEO,
              'targetDeltaV': 9252.0}
    inputs.update(overrides)

    vehicle = StagedVehicle()
    vehicle.setInputs(inputs)

    return vehicle

def buildBudget(**overrides) -> MassBudget:

    inputs = {'items': [{'name': 'tanks',    'mass': 1200.0, 'maturity': 'calculated',
                         'station': 8.0},
                        {'name': 'engines',  'mass': 900.0,  'maturity': 'preliminary',
                         'station': 1.0},
                        {'name': 'avionics', 'mass': 120.0,  'maturity': 'estimated',
                         'station': 14.0}],
              'allocatedMass':  3000.0,
              'programmePhase': 'preliminary'}
    inputs.update(overrides)

    budget = MassBudget()
    budget.setInputs(inputs)

    return budget

def buildAscent(**overrides) -> AscentTrajectory:

    inputs = {'thrustToWeight': 1.35}
    inputs.update(overrides)

    ascent = AscentTrajectory()
    ascent.setInputs(inputs)

    return ascent

def buildLoop(**overrides) -> SizingLoop:

    inputs = {'payloadMass':  1500.0,
              'targetDeltaV': 9300.0,
              'stages': [{'specificImpulse': 297.0, 'deltaVFraction': 0.45},
                         {'specificImpulse': 340.0, 'deltaVFraction': 0.55}],
              'tankRadius':   0.9,
              'tankPressure': 0.35e6}
    inputs.update(overrides)

    loop = SizingLoop()
    loop.setInputs(inputs)

    return loop

# ------------------------------------------------------------------------------------------------ #
# -- Tier 1: the contract -- #
# ------------------------------------------------------------------------------------------------ #

def testTheSpecificErrorsSubclassTheDomainBase():

    assert issubclass(ClosureError, VehicleArchitectureError)
    assert issubclass(StagingError, VehicleArchitectureError)

def testAMassRatioBelowOneIsRejected():

    with pytest.raises(StagingError, match = 'at least one'):
        deltaV(3000.0, 0.9)

def testAStageHeavierThanItsGrossMassIsRefused():

    '''
    A dry mass at or above the gross mass means the stage carries no propellant. That is a
    bookkeeping error or a design that has already failed, and neither is a heavy stage.
    '''

    with pytest.raises(ClosureError, match = 'no propellant'):
        structuralCoefficient(1000.0, 900.0)

def testAStructuralCoefficientOutsideTheUnitIntervalIsRefused():

    with pytest.raises(ClosureError, match = r'\(0, 1\)'):
        buildVehicle(stages = [{'specificImpulse': 300.0, 'structuralCoefficient': 1.2}])

def testAStageMissingItsDefiningParametersIsRejected():

    with pytest.raises(StagingError, match = 'no structuralCoefficient'):
        buildVehicle(stages = [{'specificImpulse': 300.0}])

def testAVehicleThatCannotReachItsTargetIsRefusedWithTheCeiling():

    '''
    A stage cannot exceed a mass ratio of one over its structural coefficient however much
    propellant it carries, so there is a hard delta-V ceiling. The message reports it, because
    knowing the target is unreachable is more useful than knowing the solve failed.
    '''

    with pytest.raises(StagingError, match = 'unbounded propellant'):
        buildVehicle(stages = [{'specificImpulse': 250.0, 'structuralCoefficient': 0.30},
                               {'specificImpulse': 250.0, 'structuralCoefficient': 0.30}],
                     targetDeltaV = 12000.0).optimiseStaging()

def testAnUndefinedVehicleCannotReportPerformance():

    with pytest.raises(StagingError, match = 'no propellant mass'):
        buildVehicle().calculatePerformance()

def testAnUnknownMaturityIsRejected():

    with pytest.raises(InvalidInputError, match = 'Unknown design maturity'):
        massGrowthAllowance(100.0, 'hopeful')

def testADuplicateLineItemIsRejected():

    '''
    Duplicated names are how an item gets counted twice or dropped in a rollup, and neither shows
    up as an error later.
    '''

    with pytest.raises(InvalidInputError, match = 'Duplicate line item'):
        buildBudget(items = [{'name': 'tanks', 'mass': 100.0, 'maturity': 'calculated'},
                             {'name': 'tanks', 'mass': 200.0, 'maturity': 'calculated'}])

def testALineItemWithoutAMaturityIsRejected():

    with pytest.raises(InvalidInputError, match = 'no maturity'):
        buildBudget(items = [{'name': 'tanks', 'mass': 100.0}])

def testACentreOfGravityNeedsEveryStation():

    with pytest.raises(InvalidInputError, match = 'needs a station'):
        buildBudget(items = [{'name': 'a', 'mass': 10.0, 'maturity': 'actual', 'station': 1.0},
                             {'name': 'b', 'mass': 10.0, 'maturity': 'actual'}]
                    ).calculateCentreOfGravity()

def testAVehicleThatCannotLeaveThePadIsRefused():

    with pytest.raises(VehicleArchitectureError, match = 'does not leave the pad'):
        buildAscent(thrustToWeight = 0.95)

def testASizingLoopRefusesAnAssertedStructuralCoefficient():

    '''
    Computing the coefficient is what this class is for, so accepting one would let a caller assert
    the answer the loop exists to find.
    '''

    with pytest.raises(InvalidInputError, match = 'given a structural coefficient'):
        buildLoop(stages = [{'specificImpulse': 297.0, 'deltaVFraction': 1.0,
                             'structuralCoefficient': 0.05}])

def testDeltaVFractionsMustSumToOne():

    with pytest.raises(InvalidInputError, match = 'sum to'):
        buildLoop(stages = [{'specificImpulse': 297.0, 'deltaVFraction': 0.45},
                            {'specificImpulse': 340.0, 'deltaVFraction': 0.45}])

def testADivergingSizingLoopIsRefusedRatherThanReturned():

    '''
    The refusal that matters most in this domain. A diverging loop's last iterate looks exactly
    like a converged answer, so returning it would hand somebody an open design that reads as
    closed.
    '''

    with pytest.raises(ClosureError, match = 'does not close|diverging|did not converge'):
        buildLoop(tankPressure = 40.0e6, payloadMass = 20000.0).close()

def testATankTooFatForItsPropellantIsRefused():

    with pytest.raises(ClosureError, match = 'too fat'):
        buildLoop(tankRadius = 3.0).sizeTank(500.0)

# ------------------------------------------------------------------------------------------------ #
# -- Tier 2: closed forms and the reference vehicle -- #
# ------------------------------------------------------------------------------------------------ #

def testTsiolkovskyMatchesItsDefinition():

    assert deltaV(3000.0, np.e) == pytest.approx(3000.0)
    assert deltaV(3000.0, 1.0) == pytest.approx(0.0)

def testExhaustVelocityIsSpecificImpulseTimesStandardGravity():

    assert exhaustVelocity(300.0) == pytest.approx(300.0 * STANDARD_GRAVITY)

def testTheStructuralCoefficientIsAgainstGrossMassNotPropellant():

    '''
    Some sources define it against propellant mass and the two differ by enough to change a design.
    This repository uses gross mass throughout and the reference cases are read the same way.
    '''

    assert structuralCoefficient(FALCON_ONE_DRY, FALCON_ONE_GROSS) == pytest.approx(
        FALCON_ONE_DRY / FALCON_ONE_GROSS)

    assert structuralCoefficient(FALCON_ONE_DRY, FALCON_ONE_GROSS) == pytest.approx(
        0.0513, abs = 0.0005)

def testTheFalconNineStageMassesReproduceALowEarthOrbitDeltaV():

    '''
    The one external anchor this domain has. Published stage masses and engine performance, put
    through the rocket equation, have to land near the delta-V a low Earth orbit mission needs.

    It validates the bookkeeping rather than any model, and the bookkeeping is what usually goes
    wrong: each stage lifts everything above it.
    '''

    vehicle = StagedVehicle()
    vehicle.setInputs({
        'stages': [{'specificImpulse': 297.0,
                    'structuralCoefficient': FALCON_ONE_DRY / FALCON_ONE_GROSS,
                    'propellantMass': FALCON_ONE_GROSS - FALCON_ONE_DRY},
                   {'specificImpulse': 348.0,
                    'structuralCoefficient': FALCON_TWO_DRY / FALCON_TWO_GROSS,
                    'propellantMass': FALCON_TWO_GROSS - FALCON_TWO_DRY}],
        'payloadMass': FALCON_PAYLOAD_LEO})

    performance = vehicle.calculatePerformance()

    assert performance['totalDeltaV'] == pytest.approx(9300.0, rel = 0.03)

    assert performance['liftoffMass'] == pytest.approx(
        FALCON_ONE_GROSS + FALCON_TWO_GROSS + FALCON_PAYLOAD_LEO)

def testTheReferenceVehicleMatchesTheRegisteredEntry():

    reference = LAUNCH_VEHICLES['Falcon 9 Block 5']

    assert reference['level'] == 'hardware'

    assert reference['stageOneDryMass']   == FALCON_ONE_DRY
    assert reference['stageOneGrossMass'] == FALCON_ONE_GROSS
    assert reference['payloadToLeoExpended'] == FALCON_PAYLOAD_LEO

def testTheReferenceCoefficientsSitInsideTheLibraryBands():

    lower, upper = STRUCTURAL_COEFFICIENT_BAND['kerolox booster']

    assert lower <= FALCON_ONE_DRY / FALCON_ONE_GROSS <= upper

    lower, upper = STRUCTURAL_COEFFICIENT_BAND['kerolox upper']

    assert lower <= FALCON_TWO_DRY / FALCON_TWO_GROSS <= upper

def testTheOptimalSplitSumsToTheTarget():

    '''
    Regression guard on a defect that shipped and was caught by this assertion. An earlier bisection
    ran the wrong way and its bracket search overshot the admissible boundary, so the optimiser
    returned a corner solution whose split did not sum to the target at all.
    '''

    vehicle = buildVehicle()

    result = vehicle.optimiseStaging()

    assert sum(result['deltaVSplit']) == pytest.approx(vehicle.targetDeltaV, rel = 1.0e-6)

def testTheOptimalSplitIsTheSameAcrossAWideRangeOfTargets():

    for target in (7000.0, 9252.0, 11000.0, 14000.0):

        vehicle = buildVehicle(targetDeltaV = target)

        assert sum(vehicle.optimiseStaging()['deltaVSplit']) == pytest.approx(target, rel = 1.0e-6)

def testSizingAndPerformanceAreInverses():

    '''
    Size a vehicle to a delta-V, then compute what the sized vehicle delivers. The two have to
    agree or one of the two mass bookkeepings is wrong.
    '''

    vehicle = buildVehicle()

    sized = vehicle.sizeToDeltaV()

    check = StagedVehicle()
    check.setInputs({
        'stages': [{'specificImpulse': vehicle.stages[index]['specificImpulse'],
                    'structuralCoefficient': vehicle.stages[index]['structuralCoefficient'],
                    'propellantMass': entry['propellantMass']}
                   for index, entry in enumerate(sized['stages'])],
        'payloadMass': vehicle.payloadMass})

    assert check.calculatePerformance()['totalDeltaV'] == pytest.approx(
        vehicle.targetDeltaV, rel = 1.0e-6)

def testTheRotationAssistIsLargestDueEastAtTheEquator():

    equator = AscentTrajectory()
    equator.setInputs({'thrustToWeight': 1.35, 'latitude': 0.0, 'launchAzimuth': 90.0})

    cape = buildAscent(latitude = 28.5, launchAzimuth = 90.0)

    polar = AscentTrajectory()
    polar.setInputs({'thrustToWeight': 1.35, 'latitude': 28.5, 'launchAzimuth': 180.0})

    assert equator.rotationAssist() > cape.rotationAssist()
    assert polar.rotationAssist() == pytest.approx(0.0, abs = 1.0e-9)

def testTheLossModelMatchesItsReferencePoint():

    losses = buildAscent(thrustToWeight = REFERENCE_THRUST_TO_WEIGHT).calculateLosses()

    assert losses['gravity'] == pytest.approx(REFERENCE_GRAVITY_LOSS)
    assert losses['drag']    == pytest.approx(REFERENCE_DRAG_LOSS)

def testTheGrowthAllowanceMatchesItsTable():

    for maturity, rate in MASS_GROWTH_ALLOWANCE.items():
        assert massGrowthAllowance(100.0, maturity) == pytest.approx(100.0 * rate)

def testAWeighedItemCarriesNoGrowth():

    assert massGrowthAllowance(500.0, 'actual') == 0.0

def testTheRollupIsTheSumOfItsLines():

    rollup = buildBudget().rollUp()

    assert rollup['estimate'] == pytest.approx(sum(line['estimate'] for line in rollup['lines']))
    assert rollup['growth']   == pytest.approx(sum(line['allowance'] for line in rollup['lines']))
    assert rollup['predicted'] == pytest.approx(rollup['estimate'] + rollup['growth'])

# ------------------------------------------------------------------------------------------------ #
# -- Tier 3: the results -- #
# ------------------------------------------------------------------------------------------------ #

def testTheStagingOptimumIsFlat():

    '''
    The first of the two results this domain exists to produce. Ten per cent either way off the
    optimal split is worth a fraction of a per cent, so the optimisation is worth doing once and it
    is not worth defending.
    '''

    flatness = buildVehicle().checkStagingFlatness()

    assert flatness['isFlat'] is True
    assert flatness['worstPenalty'] < 0.01

def testTheRealVehicleIsNotAtTheOptimumAndItBarelyMatters():

    '''
    Falcon 9 puts substantially more delta-V on its first stage than the payload optimum wants, and
    sizing it optimally would save a few per cent of liftoff mass. That gap buys engine
    commonality, booster recovery and a staging altitude, none of which the optimisation can see.
    '''

    vehicle = buildVehicle()

    optimal = vehicle.optimiseStaging()['deltaVSplit']

    actual = deltaV(exhaustVelocity(297.0),
                    (FALCON_ONE_GROSS + FALCON_TWO_GROSS + FALCON_PAYLOAD_LEO)
                    / (FALCON_TWO_GROSS + FALCON_PAYLOAD_LEO))

    assert actual > optimal[0], 'the real vehicle front-loads relative to the optimum'

    optimalMass = vehicle.sizeToDeltaV(optimal)['liftoffMass']

    published = FALCON_ONE_GROSS + FALCON_TWO_GROSS + FALCON_PAYLOAD_LEO

    assert optimalMass < published
    assert (published - optimalMass) / published < 0.06, 'and it costs only a few per cent'

def testTheLossOptimumIsOutsideThePracticalBand():

    '''
    The second result, and it was not what this class was written expecting. Gravity loss falls
    faster with thrust to weight than drag loss rises, so the loss budget wants a thrust to weight
    nothing flies. It therefore sets a floor and not a target.
    '''

    sweep = buildAscent().optimiseThrustToWeight()

    assert sweep['optimumInsidePracticalBand'] is False
    assert sweep['optimum'] > 2.0
    assert sweep['thrustMultipleToReachOptimum'] > 1.5

def testTheAscentBudgetLandsNearARealMissionRequirement():

    budget = buildAscent().calculateBudget()

    assert 8500.0 < budget['requiredDeltaV'] < 9600.0
    assert budget['rotationAssist'] > 0.0
    assert budget['losses']['gravity'] > budget['losses']['drag']

def testPayloadElasticityScalesInverselyWithPayloadFraction():

    '''
    The correction this domain made to its own stated ethos. The claim that small upstream errors
    are large payload errors is about marginal vehicles, not about rockets: the elasticity is
    inversely proportional to the payload fraction the design already has.
    '''

    good = buildVehicle()

    marginal = buildVehicle(
        stages = [{'specificImpulse': 285.0, 'structuralCoefficient': 0.090},
                  {'specificImpulse': 320.0, 'structuralCoefficient': 0.120}])

    goodFraction     = good.sizeToDeltaV()['payloadFraction']
    marginalFraction = marginal.sizeToDeltaV()['payloadFraction']

    goodElasticity     = abs(good.payloadSensitivity()['fixedVehicle']['dryMassElasticity'])
    marginalElasticity = abs(marginal.payloadSensitivity()['fixedVehicle']['dryMassElasticity'])

    assert marginalFraction < goodFraction
    assert marginalElasticity > 2.0 * goodElasticity

    assert goodElasticity < 1.0, 'on a healthy vehicle it is well under one'

def testHigherSpecificImpulseHelpsAndHeavierStructureHurts():

    '''
    Sign checks, and they caught a real defect: with the bisection running the wrong way every
    elasticity in this set came out with the wrong sign and nothing else noticed.
    '''

    elasticities = buildVehicle().payloadSensitivity()['elasticities']

    for name, value in elasticities.items():

        if 'specificImpulse' in name:
            assert value > 0.0, name

        if 'structuralCoefficient' in name:
            assert value < 0.0, name

        if name == 'target delta-V':
            assert value < 0.0

def testTheUpperStageMattersMoreThanTheLower():

    '''
    A kilogram on the upper stage is carried the whole way and a kilogram on the lower stage is
    dropped early, so the upper stage elasticities are larger. This is the quantitative form of a
    rule everybody states qualitatively.
    '''

    elasticities = buildVehicle().payloadSensitivity()['elasticities']

    assert (abs(elasticities['stage 2 specificImpulse'])
            > abs(elasticities['stage 1 specificImpulse']))

    assert (abs(elasticities['stage 2 structuralCoefficient'])
            > abs(elasticities['stage 1 structuralCoefficient']))

def testGrowthAllowanceAndMarginAreReportedSeparately():

    '''
    The result the mass budget exists to produce. A budget that shows healthy margin because the
    growth allowance was spent on it has no margin, and keeping the two apart is the only way to
    see that.
    '''

    margin = buildBudget().checkMargin()

    assert margin['predicted'] > margin['estimate']
    assert margin['required']  > margin['predicted']

    assert margin['growth'] > 0.0
    assert margin['margin'] > 0.0

    assert margin['required'] == pytest.approx(margin['predicted'] + margin['margin'])

def testABudgetCanCloseOnEstimateAndNotOnPrediction():

    '''
    The failure mode. Comparing an estimate against an allocation is the commonest way a budget
    looks healthier than it is.
    '''

    budget = buildBudget(allocatedMass = 2300.0)

    margin = budget.checkMargin()

    assert margin['closesOnEstimate'] is True
    assert margin['closesOnPredicted'] is False

def testTheMarginPolicyTightensThroughTheProgramme():

    phases = list(DEFAULT_MARGIN_POLICY.values())

    assert phases == sorted(phases, reverse = True)

def testTheCentreOfGravityMovesWithGrowth():

    centre = buildBudget().calculateCentreOfGravity()

    assert centre['centreOfGravity'] != pytest.approx(centre['centreOnEstimate'])
    assert abs(centre['shiftFromGrowth']) > 0.0

def testTheSizingLoopConvergesAndTheTankDrivesTheCoefficient():

    result = buildLoop().close()

    assert result['converged'] is True
    assert result['iterations'] < 20

    for index, coefficient in enumerate(result['coefficients']):

        tank    = result['tanks'][index]['tankMass']
        nonTank = result['tanks'][index]['nonTankMass']

        assert coefficient > 0.0
        assert tank > 0.0
        assert nonTank == pytest.approx(
            NON_TANK_DRY_FRACTION * result['stages'][index]['propellantMass'])

def testTheMassChainAmplifiesATankKilogramIntoManyLiftoffKilograms():

    '''
    The number this whole domain exists to produce, and no single subsystem can see it. It runs
    from a fluid system pressure drop through a structures wall thickness into a rocket equation.
    '''

    trace = buildLoop().traceMassChain(pressureIncrement = 0.1e6)

    assert trace['wallChange'] > 0.0
    assert trace['tankMassChange'] > 0.0
    assert trace['liftoffChange'] > 0.0

    assert trace['amplification'] > 5.0, (
        'a kilogram in the first stage tank should cost several kilograms at liftoff')

def testRaisingTheTankPressureWorsensEverythingMonotonically():

    previous = None

    for pressure in (0.35e6, 0.7e6, 1.5e6, 2.5e6):

        result = buildLoop(tankPressure = pressure).close()

        current = (result['tanks'][0]['wallThickness'],
                   result['coefficients'][0],
                   result['liftoffMass'])

        if previous is not None:
            for index in range(3):
                assert current[index] > previous[index], (pressure, index)

        previous = current

def testAPressureFedVehicleIsNearlyTwiceTheLiftoffMass():

    '''
    The whole reason turbopumps exist, computed rather than asserted. The structures library
    thickens the wall and this domain reports what that costs.
    '''

    pumpFed     = buildLoop(tankPressure = 0.35e6).close()
    pressureFed = buildLoop(tankPressure = 3.5e6).close()

    assert pressureFed['liftoffMass'] / pumpFed['liftoffMass'] > 1.5

    lower, upper = STRUCTURAL_COEFFICIENT_BAND['pressure fed']

    assert pressureFed['coefficients'][0] > STRUCTURAL_COEFFICIENT_BAND['kerolox booster'][1]
    assert lower <= pressureFed['coefficients'][0] <= upper

def testTheSizingLoopUsesTheStructuresPressureVessel():

    '''
    The cross-domain coupling asserted directly. If this class ever grew its own tank model the two
    would drift, and the drift would be invisible because both would produce plausible masses.
    '''

    import PressureVessel as structuresModule

    assert 'aerospaceStructures' in os.path.abspath(structuresModule.__file__)

def testBooleanFlagsAreRealPythonBooleans():

    flags = [buildVehicle().checkStagingFlatness()['isFlat'],
             buildAscent().optimiseThrustToWeight()['optimumInsidePracticalBand'],
             buildBudget().checkMargin()['closesOnRequired'],
             buildLoop().close()['converged']]

    for flag in flags:
        assert type(flag) is bool, f'{flag!r} is {type(flag)}, not bool'

def testTheUnvalidatedRegisterNamesWhatThisDomainCannotCheck():

    for key in ('ascentLossModel', 'nonTankDryFraction', 'massGrowthAllowance'):

        entry = UNVALIDATED[key]

        assert 'vehicleArchitecture' in entry['domain']
        assert entry['consequence']
        assert entry['nextStep']

def testReportsRunForEveryClass():

    assert 'STAGED VEHICLE' in buildVehicle().generateReport()
    assert 'MASS BUDGET'    in buildBudget().generateReport()
    assert 'ASCENT BUDGET'  in buildAscent().generateReport()
    assert 'SIZING LOOP'    in buildLoop().generateReport()
