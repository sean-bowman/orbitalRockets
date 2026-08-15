
# -- recoveryAndReusability worked example -- #

'''

One booster, five questions: what the entry does to it, what recovery costs, what the touchdown
demands, how many flights are left in it, and whether any of that pays.

Five results, and each is a case of the obvious quantity not being the one that decides.

**Peak deceleration does not depend on the vehicle.** Allen and Eggers showed in 1958 that the
maximum g of a ballistic entry is set by the entry velocity, the flight path angle and the
atmospheric scale height, and by nothing about the body. The ballistic coefficient moves where the
peak happens and not how large it is. What it does move is the heating.

**Reserve propellant costs nearly five times the payload that recovery hardware does**, even
though the hardware is the part that gets designed, weighed and argued about. And the penalty as a
fraction of payload rises as the mission gets harder, which is why boosters are expended on the
hardest missions of a reusable fleet.

**Stroke is the cheap variable at touchdown.** The load factor is inversely proportional to it, so
the reusable absorber, which is less efficient than a crushable one, is bought back with travel
rather than with structure.

**The limiting life item is not the one that looks worst after a flight**, and extending it moves
the limit to the next one rather than removing it.

**And most of the benefit of reuse arrives in the first three flights.** Two thirds of it, here.
The argument for a very high flight count is about refurbishment cost rather than about
amortisation, and a three per cent recovery loss rate removes a quarter of the planned flights.

Run:
    python recoveryAndReusability/codeInterface.py

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

sys.path.insert(0, os.path.join(HERE, 'recoveryAndReusabilityLibrary'))

from recoveryUtils import (RECOVERY_MODES, LIFE_LIMITED_ITEMS, INSPECTION_LEVELS,
                           EntryError, LandingError, LifeError, EconomicsError, RecoveryError)
from EntryTrajectory import EntryTrajectory
from RecoveryBudget import RecoveryBudget
from LandingLoads import LandingLoads
from LifeTracking import LifeTracking
from ReuseEconomics import ReuseEconomics

sys.path.insert(0, os.path.join(ROOT, 'vehicleArchitecture', 'vehicleArchitectureLibrary'))

from StagedVehicle import StagedVehicle

sys.path.insert(0, ROOT)

from validation.referenceCases import LAUNCH_VEHICLES

ASSET = os.path.join(HERE, 'recoveryAndReusabilityLibrary', 'assets', 'boosterReuseExample.json')

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Builders -- #
# ------------------------------------------------------------------------------------------------ #

def buildEntry(case: dict, key: str = 'entry') -> EntryTrajectory:

    entry = case[key]

    trajectory = EntryTrajectory()
    trajectory.setInputs({'entryVelocity':   entry['entryVelocity'],
                          'flightPathAngle': entry['flightPathAngle'],
                          'mass':            entry['mass'],
                          'dragCoefficient': entry['dragCoefficient'],
                          'referenceArea':   entry['referenceArea'],
                          'noseRadius':      entry['noseRadius']})

    return trajectory

def buildExchangeRatios() -> dict:

    '''
    The two exchange ratios, computed from the vehicle rather than assumed.

    This is the whole reason the domain boundary is where it is. Payload lost per kilogram is a
    rocket equation result on a specific stack, so it is StagedVehicle that produces it and this
    domain that consumes it. Both stages come from the validation register, so a change to the
    published Falcon 9 masses reaches the recovery penalty without anybody reconciling two sets of
    numbers.
    '''

    reference = LAUNCH_VEHICLES['Falcon 9 Block 5']

    vehicle = StagedVehicle()
    vehicle.setInputs({
        'stages': [{'specificImpulse':       282.0,
                    'structuralCoefficient': reference['stageOneDryMass']
                                             / reference['stageOneGrossMass'],
                    'propellantMass':        reference['stageOneGrossMass']
                                             - reference['stageOneDryMass']},
                   {'specificImpulse':       348.0,
                    'structuralCoefficient': reference['stageTwoDryMass']
                                             / reference['stageTwoGrossMass'],
                    'propellantMass':        reference['stageTwoGrossMass']
                                             - reference['stageTwoDryMass']}],
        'payloadMass': reference['payloadToLeoExpended']})

    return vehicle.exchangeRatios()

def buildBudget(case: dict, mode: str = None, ratios: dict = None) -> RecoveryBudget:

    vehicle = case['vehicle']
    recovery = case['recovery']

    ratios = ratios if ratios else buildExchangeRatios()

    budget = RecoveryBudget()
    budget.setInputs({'stageDryMass':    vehicle['stageDryMass'],
                      'stagePropellant': vehicle['stagePropellant'],
                      'baselinePayload': vehicle['baselinePayload'],
                      'mode':            mode if mode else recovery['mode'],
                      'hardwareItems':   recovery['hardwareItems'],
                      'dryMassExchangeRatio': ratios['dryMassExchangeRatio'],
                      'reserveExchangeRatio': ratios['reserveExchangeRatio']})

    return budget

def buildLanding(case: dict, droneship: bool = False) -> LandingLoads:

    entry = case['landing']

    loads = LandingLoads()
    loads.setInputs({'landedMass':      entry['landedMass'],
                     'sinkRate':        entry['sinkRate'],
                     'horizontalRate':  (entry['droneshipHorizontalRate'] if droneship
                                         else entry['horizontalRate']),
                     'stroke':          entry['stroke'],
                     'absorber':        entry['absorber'],
                     'legCount':        entry['legCount'],
                     'footprintRadius': entry['footprintRadius'],
                     'centreOfGravity': entry['centreOfGravity'],
                     'groundSlope':     (entry['droneshipSlope'] if droneship
                                         else entry['groundSlope']),
                     'limitLoadFactor': entry['limitLoadFactor']})

    return loads

def buildLife(case: dict, flightsFlown: float = None) -> LifeTracking:

    entry = case['life']

    life = LifeTracking()
    life.setInputs({'flightsFlown':  flightsFlown if flightsFlown is not None
                                     else entry['flightsFlown'],
                    'certifiedLife': entry['certifiedLife']})

    return life

def buildEconomics(case: dict, payloadPenalty: float) -> ReuseEconomics:

    entry = case['economics']

    economics = ReuseEconomics()
    economics.setInputs({'refurbishmentCost':  entry['refurbishmentCost'],
                         'recoveryCost':       entry['recoveryCost'],
                         'expendableElements': entry['expendableElements'],
                         'recoverySuccess':    entry['recoverySuccess'],
                         'flightsPerArticle':  entry['flightsPerArticle'],
                         'payloadPenalty':     payloadPenalty})

    return economics

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: entry -- #
# ------------------------------------------------------------------------------------------------ #

def reportEntry(case: dict) -> dict:

    trajectory = buildEntry(case)

    deceleration = trajectory.calculatePeakDeceleration()
    heating = trajectory.calculatePeakHeating()
    beta = trajectory.compareBallisticCoefficients()
    corridor = trajectory.compareFlightPathAngles()

    orbital = buildEntry(case, 'orbitalComparison')
    orbitalDeceleration = orbital.calculatePeakDeceleration()
    orbitalHeating = orbital.calculatePeakHeating()

    print()
    print('    quantity                     booster return        from orbit')
    print(f'    {"entry velocity [m/s]":<28}{case["entry"]["entryVelocity"]:>15,.0f}'
          f'{case["orbitalComparison"]["entryVelocity"]:>18,.0f}')
    print(f'    {"peak deceleration [g]":<28}{deceleration["peakLoadFactor"]:>15.1f}'
          f'{orbitalDeceleration["peakLoadFactor"]:>18.1f}')
    print(f'    {"peak heat flux [W/cm2]":<28}{heating["peakHeatFluxWattPerCm2"]:>15.0f}'
          f'{orbitalHeating["peakHeatFluxWattPerCm2"]:>18.0f}')
    print(f'    {"heat load [J/cm2]":<28}{heating["heatLoadJoulePerCm2"]:>15,.0f}'
          f'{orbitalHeating["heatLoadJoulePerCm2"]:>18,.0f}')

    fluxRatio = orbitalHeating['peakHeatFluxWattPerCm2'] / heating['peakHeatFluxWattPerCm2']
    velocityRatio = (case['orbitalComparison']['entryVelocity']
                     / case['entry']['entryVelocity'])

    print()
    print(f'  A booster returns from a lofted suborbital trajectory rather than from orbit, so its')
    print(f'  entry velocity is {1.0 / velocityRatio * 100.0:.0f}% of an orbital one and its peak '
          f'heat flux is {1.0 / fluxRatio * 100.0:.0f}% of it,')
    print(f'  a factor of {fluxRatio:.0f}. **Peak flux goes as the cube of entry velocity** at a '
          f'fixed corridor, which')
    print(f'  alone would give {velocityRatio ** 3:.0f}; the booster also enters far more steeply, '
          f'which raises its own flux and')
    print(f'  brings the ratio back to {fluxRatio:.0f}. The total heat load differs by '
          f'{orbitalHeating["heatLoadJoulePerCm2"] / heating["heatLoadJoulePerCm2"]:.0f} times.')
    print()
    print('  That exponent is why a booster needs paint and a capsule needs a heat shield, and it')
    print('  is the whole reason first stage reuse arrived long before upper stage reuse.')
    print()

    print('    mass factor   beta [kg/m2]   peak g   peak flux [W/cm2]   heat load [J/cm2]')
    for entry in beta['results']:
        print(f'    {entry["factor"]:>11.2f}{entry["ballisticCoefficient"]:>15,.0f}'
              f'{entry["peakLoadFactor"]:>9.1f}{entry["peakHeatFlux"]:>20.0f}'
              f'{entry["heatLoad"]:>20,.0f}')

    print()
    print(f'  - **Peak deceleration is identical down that column**, across a factor of '
          f'{beta["results"][-1]["ballisticCoefficient"] / beta["results"][0]["ballisticCoefficient"]:.0f} '
          f'in ballistic coefficient.')
    print(f'  - a_max = V_e^2 sin(gamma) / (2 e H). **The vehicle is not in the equation.** Only '
          f'the entry state and the atmosphere are.')
    print(f'  - The heat flux moves by {beta["heatFluxSpread"]:.1f} times over the same range, '
          f'because it goes as the square root of the ballistic coefficient.')
    print(f'  - So a heavier body pulls the same g, lower down and later, and heats up far more '
          f'doing it. **The intuition that a heavy entry is a high-g entry is simply wrong.**')
    print()

    print('    flight path angle [deg]   peak g   peak flux [W/cm2]   heat load [J/cm2]')
    for entry in corridor['results']:
        print(f'    {entry["flightPathAngle"]:>23.0f}{entry["peakLoadFactor"]:>9.1f}'
              f'{entry["peakHeatFlux"]:>20.0f}{entry["heatLoad"]:>20,.0f}')

    print()
    print(f'  - Steepening the entry raises the peak flux by {corridor["fluxRatio"]:.1f} times and '
          f'cuts the total load to {corridor["loadRatio"]:.2f} of it.')
    print('  - **The two move in opposite directions**, so there is no best flight path angle,')
    print('    only a choice. Peak rate selects the thermal protection material and total load')
    print('    sets its thickness, so the corridor decides which of those two problems you have.')
    print()

    print(f'  - Peak heating happens at {heating["atAltitude"] / 1000.0:.1f} km and peak '
          f'deceleration at {deceleration["atAltitude"] / 1000.0:.1f}, a separation of '
          f'{heating["altitudeSeparation"] / 1000.0:.1f} km.')
    print(f'  - **The separation is the invariant, not the ratio.** It is H ln(3) for every entry '
          f'of every vehicle, because the two peak densities differ by exactly a factor of three.')
    print(f'  - Heating peaks at {heating["velocityFraction"]:.3f} of the entry velocity and '
          f'deceleration at {deceleration["velocityFraction"]:.3f}. **Both fractions are pure '
          f'numbers** and neither depends on anything about the vehicle or the planet.')
    print('  - The structure and the thermal protection are therefore not designed by the same')
    print('    instant of the entry, which is easy to assume and wrong.')

    return {'deceleration':  deceleration,
            'heating':       heating,
            'beta':          beta,
            'corridor':      corridor,
            'orbital':       {'deceleration': orbitalDeceleration, 'heating': orbitalHeating},
            'fluxRatio':     fluxRatio,
            'trajectory':    trajectory}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: what recovery costs -- #
# ------------------------------------------------------------------------------------------------ #

def reportBudget(case: dict) -> dict:

    ratios = buildExchangeRatios()

    budget = buildBudget(case, ratios = ratios)
    vehicle = case['vehicle']

    print()
    print('  The two exchange ratios, from vehicleArchitecture rather than assumed here.')
    print()
    print(f'    payload lost per kg of stage dry mass  {ratios["dryMassExchangeRatio"]:8.4f}')
    print(f'    payload lost per kg of reserve         {ratios["reserveExchangeRatio"]:8.4f}')
    print(f'    first stage mass ratio                 {ratios["firstStageMassRatio"]:8.4f}')
    print(f'    measured ratio of the two              {ratios["measuredRatio"]:8.4f}')
    print(f'    closed form 1 - 1/R                    {ratios["closedFormRatio"]:8.4f}')
    print()
    print(f'  - **The reserve is the more expensive of the two, by a factor of '
          f'{1.0 / ratios["measuredRatio"]:.2f}**, and this domain had')
    print('    that the other way round until the two libraries were wired together.')
    print('  - The reason is not the intuitive one. Both are aboard for the whole ascent burn: a')
    print('    recovery reserve is spent after separation, not during the climb. What separates')
    print('    them is that added dry mass raises the first stage initial mass and its burnout mass')
    print('    together, while reserved propellant is already aboard and raises the burnout mass')
    print('    alone.')
    print('  - **So the ratio of the two costs is 1 - 1/R exactly**, which is below one on every')
    print('    vehicle that flies. The ordering is not a property of this stage and there is no')
    print('    vehicle for which it reverses.')

    hardware = budget.calculateHardwareMass()
    reserve = budget.calculateReserve()
    penalty = budget.calculatePenalty()
    modes = budget.compareModes()

    # Swept across the two published missions rather than across arbitrary factors, so the
    # modelled penalty can be set against the published one at both ends.
    sensitivity = budget.missionSensitivity([vehicle['baselinePayload'],
                                             vehicle['publishedGtoExpended']])

    publishedPenalty = vehicle['baselinePayload'] - vehicle['publishedReusablePayload']
    implied = budget.impliedReserveFraction(publishedPenalty)

    print()
    print('    item                              mass [kg]   share')
    for entry in hardware['items']:
        print(f'    {entry["item"]:<33}{entry["mass"]:>10,.0f}{entry["share"] * 100.0:>8.0f}%')

    print()
    print(f'  Recovery hardware {hardware["totalMass"]:,.0f} kg counted, '
          f'{hardware["dryFraction"] * 100.0:.0f}% of the stage dry mass, against a reserve of '
          f'{reserve["reserveMass"]:,.0f} kg.')
    print()

    print('    cause                 mass [kg]   payload cost [kg]   share')
    for entry in penalty['contributions']:
        print(f'    {entry["cause"]:<21}{entry["mass"]:>10,.0f}{entry["payloadCost"]:>20,.0f}'
              f'{entry["share"] * 100.0:>8.0f}%')

    ratio = (penalty['contributions'][1]['payloadCost']
             / penalty['contributions'][0]['payloadCost'])

    print()
    print(f'  - **Reserve propellant costs {ratio:.1f} times the payload that the recovery '
          f'hardware does**, even though the hardware is the part that gets designed, weighed and '
          f'argued about.')
    print(f'  - The reserve is {reserve["reserveMass"] / hardware["totalMass"]:.0f} times the '
          f'hardware by mass **and it also costs more per kilogram**, so the two effects compound '
          f'rather than partly cancel. The mass ranking and the payload ranking agree here and '
          f'they do not have to.')
    print()

    print('    mode                       hardware [kg]   reserve [kg]   penalty   payload [kg]')
    for entry in modes['results']:
        print(f'    {entry["mode"]:<26}{entry["hardwareMass"]:>15,.0f}'
              f'{entry["reserveMass"]:>15,.0f}{entry["penaltyFraction"] * 100.0:>10.1f}%'
              f'{entry["recoverablePayload"]:>15,.0f}')

    print()
    print(f'  - Returning to the launch site costs '
          f'{modes["results"][-1]["penaltyFraction"] / modes["results"][-2]["penaltyFraction"]:.1f} '
          f'times what a downrange landing does, because it has to cancel and reverse the '
          f'downrange velocity.')
    print('  - **That ordering holds for any values**, which is why it is worth stating separately')
    print('    from the numbers.')
    print()

    publishedGto = vehicle['publishedGtoExpended'] - vehicle['publishedGtoReusable']

    print('    mission   expendable [kg]   penalty [kg]   modelled   published')
    print(f'    {"low orbit":<9}{vehicle["baselinePayload"]:>17,.0f}'
          f'{sensitivity["results"][0]["penaltyMass"]:>15,.0f}'
          f'{sensitivity["results"][0]["penaltyFraction"] * 100.0:>11.1f}%'
          f'{publishedPenalty / vehicle["baselinePayload"] * 100.0:>12.1f}%')
    print(f'    {"transfer":<9}{vehicle["publishedGtoExpended"]:>17,.0f}'
          f'{sensitivity["results"][1]["penaltyMass"]:>15,.0f}'
          f'{sensitivity["results"][1]["penaltyFraction"] * 100.0:>11.1f}%'
          f'{publishedGto / vehicle["publishedGtoExpended"] * 100.0:>12.1f}%')

    print()
    print(f'  - **The penalty in kilograms does not move** and the penalty as a fraction spans '
          f'{sensitivity["fractionSpread"]:.1f} times between the two missions.')
    print('  - That direction is right and it is the whole reason boosters are expended on the')
    print('    hardest missions of an otherwise reusable fleet: the recovery cost is fixed and the')
    print('    payload it eats into is not. **It is a performance decision rather than an')
    print('    operational one.**')
    print()
    print('  - **The magnitude is wrong at the transfer orbit end and the direction of the error')
    print('    is informative.** The model over-predicts at low orbit and over-predicts far more')
    print('    at transfer orbit. The exchange ratios are no longer the suspect: they are computed')
    print('    from the stack and the transfer orbit stack is a different one, flown to a different')
    print('    staging velocity with a different reserve.')
    print()

    print(f'  The published Falcon 9 penalty is {publishedPenalty:,.0f} kg, '
          f'{publishedPenalty / vehicle["baselinePayload"] * 100.0:.1f}% to low orbit, against '
          f'{penalty["payloadPenalty"]:,.0f} kg')
    print(f'  from this budget, {penalty["penaltyFraction"] * 100.0:.1f}%. The budget over-predicts '
          f'by {penalty["payloadPenalty"] / publishedPenalty - 1.0:.0%}.')
    print()
    print('  With both exchange ratios fixed by the vehicle, the budget has one free quantity left')
    print('  and it is the one this domain owns. Inverting the published penalty rather than tuning')
    print('  to it:')
    print()
    print(f'    counted hardware share of the penalty  {implied["hardwareShare"] * 100.0:8.1f}%')
    print(f'    implied reserve                        {implied["impliedReserveMass"]:8,.0f} kg')
    print(f'    implied fraction of the load           {implied["impliedFraction"] * 100.0:8.2f}%')
    print(f'    assumed fraction for this mode         {implied["assumedFraction"] * 100.0:8.2f}%')
    print()
    print(f'  - **The stage holds back about {implied["impliedFraction"] * 100.0:.0f} per cent of '
          f'its propellant load, not the '
          f'{implied["assumedFraction"] * 100.0:.0f} assumed.** The counted')
    print(f'    hardware is only {implied["hardwareShare"] * 100.0:.0f} per cent of the bill, so '
          f'the reserve is what a recovery budget is')
    print('    mostly a statement about, and it is the part nobody weighs.')
    print()
    print(f'  - **That inverted number survives being turned back into what it describes.** Through '
          f'the rocket')
    print(f'    equation on a landed mass of {implied["landedMass"]:,.0f} kg it buys '
          f'{implied["impliedDeltaV"]:,.0f} m/s, which is an entry burn and a')
    print(f'    landing burn without boost-back. The '
          f'{implied["assumedFraction"] * 100.0:.0f} per cent assumption needs '
          f'{implied["assumedDeltaV"]:,.0f} m/s, which')
    print('    is more descent than that profile flies.')
    print()
    print('  **Tuning the exchange ratios until the budget reproduced the published penalty and')
    print('  then reporting the agreement would be calibration, not validation.** Computing them')
    print('  from the vehicle and inverting the one quantity left says what the stage must be')
    print('  doing, and the delta-V check is what says whether the answer is a descent profile or')
    print('  an artefact of the arithmetic.')

    return {'hardware':     hardware,
            'reserve':      reserve,
            'penalty':      penalty,
            'modes':        modes,
            'sensitivity':  sensitivity,
            'implied':      implied,
            'published':    publishedPenalty,
            'budget':       budget}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: touchdown -- #
# ------------------------------------------------------------------------------------------------ #

def reportLanding(case: dict) -> dict:

    loads = buildLanding(case)

    touchdown = loads.calculateLoadFactor()
    absorbers = loads.compareAbsorbers()
    tipover = loads.calculateTipover()
    stroke = loads.requiredStroke(case['landing']['limitLoadFactor'])

    print()
    print(f'  Touchdown at {case["landing"]["sinkRate"]:.1f} m/s onto '
          f'{case["landing"]["stroke"] * 1000.0:.0f} mm of {touchdown["absorber"]} gives '
          f'{touchdown["loadFactor"]:.2f} g,')
    print(f'  {touchdown["forcePerLeg"] / 1000.0:,.0f} kN per leg, against a structural limit of '
          f'{case["landing"]["limitLoadFactor"]:.1f} g. Margin {touchdown["margin"]:.0%}.')
    print()

    print('    absorber              efficiency   load factor   reusable   stroke for parity [mm]')
    for entry in absorbers['results']:
        print(f'    {entry["absorber"]:<21}{entry["efficiency"]:>11.2f}'
              f'{entry["loadFactor"]:>14.2f}{"   yes" if entry["reusable"] else "":>11}'
              f'{entry["strokeForBaseline"] * 1000.0:>24.0f}')

    print()
    print(f'  - The reusable absorbers are the inefficient ones. **A crushable core has a flat '
          f'force-stroke curve and a damper does not**, because a damper force follows the '
          f'velocity and falls as the vehicle stops.')
    print(f'  - The chosen damper needs '
          f'{absorbers["results"][2]["strokeForBaseline"] / absorbers["results"][0]["strokeForBaseline"]:.1f} '
          f'times the stroke of honeycomb for the same load factor.')
    print('  - **That is the right trade for a vehicle designed to fly many times**, because')
    print('    stroke is cheap and replacing a crushed core after every landing is not.')
    print()

    print(f'  - The load factor is inversely proportional to stroke, so reaching the '
          f'{case["landing"]["limitLoadFactor"]:.1f} g limit needs only')
    print(f'    {stroke["requiredStroke"] * 1000.0:.0f} mm against the '
          f'{stroke["availableStroke"] * 1000.0:.0f} available. **Stroke is the cheap variable '
          f'and structure is the dear one**, and')
    print('    a leg design that trades the other way has the conversation backwards.')
    print()

    print(f'  - Tipover: a static angle of {tipover["staticAngle"]:.1f} degrees from a '
          f'{case["landing"]["footprintRadius"]:.0f} m footprint and an '
          f'{case["landing"]["centreOfGravity"]:.0f} m centre of gravity,')
    print(f'    less {tipover["groundSlope"]:.1f} for slope and {tipover["horizontalAngle"]:.1f} '
          f'for a {case["landing"]["horizontalRate"]:.1f} m/s horizontal rate, leaving '
          f'{tipover["margin"]:.1f}.')

    droneship = buildLanding(case, droneship = True)

    try:
        droneshipTipover = droneship.calculateTipover()
        droneshipRefused = False
        droneshipMargin = droneshipTipover['margin']
    except LandingError:
        droneshipRefused = True
        droneshipMargin = np.nan

    print(f'  - On a moving deck the slope is {case["landing"]["droneshipSlope"]:.0f} degrees and '
          f'the horizontal rate {case["landing"]["droneshipHorizontalRate"]:.1f} m/s. That case '
          f'{"is REFUSED" if droneshipRefused else f"leaves {droneshipMargin:.1f} degrees"}.')
    print('  - **The slope and the horizontal rate add rather than trading against each other**,')
    print('    which is why a droneship landing is a harder problem than a pad landing by more')
    print('    than either term alone suggests.')

    return {'touchdown':  touchdown,
            'absorbers':  absorbers,
            'tipover':    tipover,
            'stroke':     stroke,
            'droneshipRefused': droneshipRefused,
            'droneshipMargin':  droneshipMargin,
            'loads':      loads}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: life -- #
# ------------------------------------------------------------------------------------------------ #

def reportLife(case: dict) -> dict:

    life = buildLife(case)

    accumulation = life.calculateAccumulation()
    severity = life.severitySensitivity()
    fleet = life.fleetLeaderLead(case['life']['fleetFlights'])
    certification = life.certifiedAgainstDemonstrated()
    ladder = life.inspectionLadder()

    print()
    print('    item                  allowable   consumed   remaining   driver')
    for entry in accumulation['items']:
        print(f'    {entry["item"]:<21}{entry["allowableFlights"]:>11.0f}'
              f'{entry["consumed"] * 100.0:>10.0f}%{entry["remainingFlights"]:>12.1f}   '
              f'{entry["driver"]}')

    print()
    print(f'  - After {case["life"]["flightsFlown"]:.0f} flights the article is limited by the '
          f'{accumulation["limitingItem"]}, at '
          f'{accumulation["remainingFlights"]:.0f} flights remaining.')
    print(f'  - Extending it moves the limit to the {accumulation["nextItem"]}, worth '
          f'{accumulation["gainIfExtended"]:.0f} flights and no more. **Life limits behave like '
          f'turnaround drivers**: one of them governs and fixing it buys the gap to the next.')
    print('  - **The limiting item is not the one that looks worst after a flight.** Thermal')
    print('    protection comes back visibly damaged and has more life left than a turbopump that')
    print('    comes back looking untouched. Appearance and damage rate are unrelated.')
    print()

    print('    severity factor   limiting item        allowable   remaining')
    for entry in severity['results']:
        remaining = 'past limit' if entry['pastLimit'] else f'{entry["remainingFlights"]:.1f}'
        print(f'    {entry["severityFactor"]:>15.1f}   {entry["limitingItem"]:<20}'
              f'{entry["totalLife"]:>11.1f}{remaining:>12}')

    print()
    print(f'  - The article runs out of life at a severity factor of '
          f'{severity["exhaustsAtSeverity"]:.2f}, so flying it twice as hard as nominal would '
          f'have retired it before this flight.')
    print('  - **The damage already consumed does not shrink**, so a harsher environment costs')
    print('    more than proportionally, and the more flights are already on the article the')
    print('    worse the leverage gets.')
    print('  - **That number only exists if the environment was measured.** A tracker fed nominal')
    print('    flights returns a nominal answer no matter what actually happened, which makes life')
    print('    tracking a telemetry requirement before it is a structures one.')
    print()

    print(f'  - The fleet leader has {fleet["leaderFlights"]:.0f} flights against '
          f'{fleet["followerFlights"]:.0f} for the next article, a lead of '
          f'{fleet["leadInFlights"]:.0f}.')
    print('  - **The lead is the warning.** A fleet flown evenly reaches its life limit on every')
    print('    article at once, and the first indication is a failure rather than a finding.')
    print()

    print(f'  - Demonstrated life {certification["demonstratedLife"]:.0f} flights on the limiting '
          f'item; with a scatter factor of {certification["scatterFactor"]:.0f} that supports a '
          f'certified life of {certification["impliedCertified"]:.1f}.')
    print(f'  - The case states {certification["statedCertified"]:.0f}, which implies a scatter '
          f'factor of {certification["impliedScatter"]:.2f}: **certifying past the demonstrated '
          f'life rather than short of it.**')
    print('  - That is a real and common position rather than an error, and it is held by')
    print('    inspection rather than by analysis, which is what the ladder below is for.')
    print()

    print('    inspection level     relative cost   catches')
    for entry in ladder['levels']:
        print(f'    {entry["level"]:<20}{entry["relativeCost"]:>14.0f}   {entry["catches"]}')

    print()
    print(f'  - **Cost rises faster than coverage**, over a spread of {ladder["costSpread"]:.0f} '
          f'times, and the most thorough level ends the article as a flight article.')
    print('  - So the question is never "inspect more". It is "inspect what, and what will be')
    print('    decided on the answer", and an inspection with no disposition attached to its')
    print('    outcome is a cost with no product.')

    return {'accumulation':  accumulation,
            'severity':      severity,
            'fleet':         fleet,
            'certification': certification,
            'ladder':        ladder,
            'life':          life}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: economics -- #
# ------------------------------------------------------------------------------------------------ #

def reportEconomics(case: dict, payloadPenalty: float) -> dict:

    economics = buildEconomics(case, payloadPenalty)

    effective = economics.effectiveFlights()
    cost = economics.costPerFlight()
    sweep = economics.flightCountSweep()
    breakEven = economics.breakEven()
    perKilogram = economics.costPerKilogram()
    refurbishment = economics.refurbishmentSensitivity()

    print()
    print('    flights   cost per flight   amortised share   marginal saving')
    for entry in sweep['sweep']:
        print(f'    {entry["flights"]:>7}{entry["costPerFlight"]:>18.3f}'
              f'{entry["amortisedShare"] * 100.0:>18.0f}%{entry["marginalSaving"]:>18.3f}')

    print()
    print(f'  - **{sweep["shareOfBenefitInThree"]:.0%} of the benefit arrives by the third '
          f'flight.** Going from one flight to two halves the amortised unit cost; going from '
          f'twenty to forty saves {sweep["sweep"][-1]["marginalSaving"]:.3f} unit costs.')
    print(f'  - The cost floor is {sweep["floorCost"]:.3f} unit costs and nothing about flight '
          f'count touches it. **Once the count is high the refurbishment cost is the whole game**,')
    print('    and a programme optimising flight count then is optimising the term that has')
    print('    already stopped mattering.')
    print()

    print('    refurbishment cost   break-even flights   cost per flight')
    for entry in refurbishment['results']:
        breakEvenText = ('never' if not np.isfinite(entry['breakEvenFlights'])
                         else f'{entry["breakEvenFlights"]:.1f}')
        print(f'    {entry["refurbishmentCost"]:>18.2f}{breakEvenText:>21}'
              f'{entry["costPerFlight"]:>18.3f}')

    print()
    print(f'  - Break-even at {breakEven["breakEvenFlights"]:.1f} flights at the case '
          f'refurbishment cost, and it moves fast: n = 1 / (1 - refurbishment - recovery).')
    print('  - **If refurbishment and recovery together exceed one unit cost there is no')
    print('    break-even at any flight count**, and the class refuses rather than reporting a')
    print('    large number. A stage that costs as much to refurbish as to build is not worth')
    print('    recovering, and no amount of flying fixes that.')
    print()

    print(f'  - At {effective["recoverySuccess"]:.0%} recovery success, '
          f'{effective["planned"]:.0f} planned flights become '
          f'{effective["expected"]:.1f} expected: a shortfall of {effective["shortfall"]:.0%}.')
    print('  - **A three per cent loss rate removes a quarter of the flights**, because the')
    print('    losses compound over the fleet life rather than applying once. Recovery')
    print(f'    reliability is worth more than it looks, and this campaign is limited by '
          f'{effective["limitedBy"]}.')
    print()

    print(f'  - Cost per flight falls {perKilogram["flightSaving"]:.0%} against expending. Cost '
          f'per kilogram falls {perKilogram["kilogramSaving"]:.0%}, because the reusable flight '
          f'carries {payloadPenalty:.0%} less.')
    print('  - **The payload penalty is a cost and it is the one most often left out.** Which of')
    print('    those two numbers a customer cares about depends entirely on whether their payload')
    print('    fits inside the reduced capacity, and for most of them it does.')

    return {'effective':      effective,
            'cost':           cost,
            'sweep':          sweep,
            'breakEven':      breakEven,
            'perKilogram':    perKilogram,
            'refurbishment':  refurbishment,
            'economics':      economics}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 6: precedent, and the boundaries -- #
# ------------------------------------------------------------------------------------------------ #

def reportPrecedent(case: dict) -> None:

    entry = case['precedent']

    print()
    print('    programme             design turnaround   achieved turnaround   flight leader')
    print(f'    {"Space Shuttle orbiter":<21}{entry["shuttleDesignTurnaroundDays"]:>18.0f} d'
          f'{entry["shuttleShortestTurnaroundDays"]:>21.0f} d'
          f'{entry["shuttleFlightLeader"]:>15.0f}')
    print(f'    {"Falcon 9 booster":<21}{"":>18}  '
          f'{entry["falconShortestTurnaroundDays"]:>21.1f} d'
          f'{entry["falconFlightLeader"]:>15.0f}')

    ratio = entry['shuttleShortestTurnaroundDays'] / entry['shuttleDesignTurnaroundDays']

    print()
    print(f'  - The Shuttle was designed for a two week turnaround and its best ever was 54 days, '
          f'a factor of {ratio:.1f}.')
    print(f'  - **A Falcon 9 booster has turned around in {entry["falconShortestTurnaroundDays"]:.1f} '
          f'days, which is shorter than the Shuttle DESIGN goal**, and its flight leader has '
          f'{entry["falconFlightLeader"]:.0f} flights against a stated qualification target of '
          f'{entry["falconQualificationGoal"]:.0f}.')
    print('  - The difference is not landing technology. **It is that the Shuttle had to be')
    print('    inspected in ways the design made expensive**, and that is the point the domain')
    print('    opens with: reuse is an inspection problem before it is a landing problem.')
    print()

    print('  What this domain does not compute, and why:')
    print()
    print('    **Aeroheating into a structure.** environmentsAndLoads computes the aeroheating')
    print('    environment and thermalManagement sizes the ablative and radiative protection that')
    print('    survives it. This domain computes the entry that produces the flux and hands it over.')
    print()
    print('    **Fatigue and crack growth.** aerospaceMaterials owns Paris law integration, the')
    print('    damage tolerance calculation and the material data behind both. LifeTracking counts')
    print('    flights against a damage per flight; it does not derive that damage from a stress.')
    print()
    print('    **Parachute sizing.** A drag area and a deployment transient, which is a fluid and')
    print('    structural problem rather than a recovery one, and the propulsive case is the one')
    print('    this domain was built around.')
    print()
    print('    **Guidance to the landing point.** avionicsAndGNC declined to build guidance for')
    print('    stated reasons and the same reasons apply here.')
    print()
    print('    **Refurbishment scheduling and cost breakdown.** A programme management problem.')
    print('    ReuseEconomics takes the refurbishment cost as a fraction and shows what it does.')
    print()
    print('    **Sea state and droneship dynamics.** LandingLoads takes a deck slope and a')
    print('    horizontal rate as inputs and shows what they cost the tipover margin. It does not')
    print('    model the ship, and the sea state that produces those two numbers is a naval')
    print('    architecture problem rather than a launch vehicle one.')

# ------------------------------------------------------------------------------------------------ #
# -- Main -- #
# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    banner('1. PEAK DECELERATION DOES NOT DEPEND ON THE VEHICLE')
    reportEntry(case)

    banner('2. THE RESERVE COSTS MORE PAYLOAD THAN THE HARDWARE')
    budget = reportBudget(case)

    banner('3. STROKE IS THE CHEAP VARIABLE AT TOUCHDOWN')
    reportLanding(case)

    banner('4. THE LIMITING ITEM IS NOT THE ONE THAT LOOKS WORST')
    reportLife(case)

    banner('5. MOST OF THE BENEFIT ARRIVES IN THE FIRST THREE FLIGHTS')

    # The PUBLISHED penalty rather than the modelled one, because a measured number is available
    # and using the model's own output here would compound its over-prediction into the economics.
    vehicle = case['vehicle']
    publishedPenalty = ((vehicle['baselinePayload'] - vehicle['publishedReusablePayload'])
                        / vehicle['baselinePayload'])

    reportEconomics(case, publishedPenalty)

    banner('6. PRECEDENT, AND WHAT THIS DOMAIN DOES NOT COMPUTE')
    reportPrecedent(case)

    banner('SUMMARY: WHAT TO CARRY OUT OF THIS DOMAIN')
    reportSummary(case)
    print()

def reportSummary(case: dict) -> None:

    '''
    Recomputed rather than carried, so the summary cannot drift from the stages above it.
    '''

    trajectory = buildEntry(case)
    budget = buildBudget(case)
    loads = buildLanding(case)
    life = buildLife(case)

    deceleration = trajectory.calculatePeakDeceleration()
    beta = trajectory.compareBallisticCoefficients()
    penalty = budget.calculatePenalty()
    touchdown = loads.calculateLoadFactor()
    accumulation = life.calculateAccumulation()

    vehicle = case['vehicle']
    publishedPenalty = ((vehicle['baselinePayload'] - vehicle['publishedReusablePayload'])
                        / vehicle['baselinePayload'])

    economics = buildEconomics(case, publishedPenalty)
    sweep = economics.flightCountSweep()
    effective = economics.effectiveFlights()
    perKilogram = economics.costPerKilogram()

    rows = [
        ('peak deceleration, over 16x in beta',
         f'{deceleration["peakLoadFactor"]:.1f} g, unchanged'),
        ('peak heat flux over the same range',
         f'{beta["heatFluxSpread"]:.1f}x'),
        ('reserve against hardware, in payload',
         f'{penalty["contributions"][1]["payloadCost"] / penalty["contributions"][0]["payloadCost"]:.1f}x'),
        ('recovery penalty, low orbit',
         f'{penalty["penaltyFraction"]:.1%} modelled, {publishedPenalty:.1%} published'),
        ('touchdown load factor',
         f'{touchdown["loadFactor"]:.2f} g on {loads.stroke * 1000.0:.0f} mm'),
        ('what limits the article',
         f'{accumulation["limitingItem"]}, {accumulation["remainingFlights"]:.0f} left'),
        ('benefit of reuse by the third flight',
         f'{sweep["shareOfBenefitInThree"]:.0%}'),
        ('planned against expected flights',
         f'{effective["planned"]:.0f} against {effective["expected"]:.1f}'),
        ('cost per flight against per kilogram',
         f'{perKilogram["flightSaving"]:.0%} against {perKilogram["kilogramSaving"]:.0%}'),
    ]

    print()
    for label, value in rows:
        print(f'    {label:<42}{value:>35}')

    print()
    print('  The connecting theme is that reuse is decided by the quantities nobody photographs.')
    print('  The landing is the visible part and the cheapest to get right. **The reserve')
    print('  propellant, the refurbishment cost, the inspection that establishes condition, and')
    print('  the one item that limits the life are what decide whether any of it pays.**')

if __name__ == '__main__':
    main()
