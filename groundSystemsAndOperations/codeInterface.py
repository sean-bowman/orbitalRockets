
# -- groundSystemsAndOperations worked example -- #

'''

One vehicle, one pad, one launch campaign: how far away everything has to be, what the tanking
costs, what sets the countdown, and what the odds of getting off the ground actually are.

Four results, and each one is a case of the small thing setting the answer.

**A small hydrogen stage is not a small siting problem.** The standard's hydrogen rule is the larger
of a sublinear term and a flat fourteen per cent, and below 84,635 kg the sublinear term governs, so
the effective fraction rises as the load falls. A 38 t stage comes out at 18.3 per cent rather than
14, and a 4 t one at 38.

The same reading also finds that the standard's bracketed metric coefficient is not the conversion of
its English one.

**A launch attempt draws more propellant than the vehicle carries**, and on the hydrogen stage the
chill-down alone is a third of the flight load. A scrub after tanking costs most of a load and the
next attempt pays the chill-down again.

**The countdown is set by one chain and the turnaround by one driver.** Shortening anything else
buys nothing, which is the most commonly ignored fact in launch operations planning.

**Six launch commit criteria at nine tenths each are not nine tenths.** They multiply, and the
combined probability is far below the worst one alone. **Attempts beat criteria**, which makes
turnaround a launch probability requirement rather than a convenience.

Run:
    python groundSystemsAndOperations/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'groundSystemsLibrary'))

from groundUtils import (HYDROGEN_METRIC_COEFFICIENT_EXACT,
                         HYDROGEN_METRIC_COEFFICIENT_PUBLISHED,
                         SitingError, LoadingError, TimelineError)
from HazardSiting import HazardSiting
from PropellantLoading import PropellantLoading
from CountdownTimeline import CountdownTimeline
from LaunchAvailability import LaunchAvailability

ASSET = os.path.join(HERE, 'groundSystemsLibrary', 'assets', 'padCampaignExample.json')

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

def buildSiting(case: dict, withUpperStage: bool = True) -> HazardSiting:

    vehicle = case['vehicle']
    pad = case['pad']

    inputs = {'combination':    vehicle['firstStage']['combination'],
              'propellantMass': vehicle['firstStage']['propellantMass'],
              'setting':        pad['setting'],
              'facilities':     pad['facilities']}

    if withUpperStage:
        inputs['additionalLoads'] = {
            vehicle['secondStage']['combination']: vehicle['secondStage']['propellantMass']}

    siting = HazardSiting()
    siting.setInputs(inputs)

    return siting

def buildLoading(case: dict) -> PropellantLoading:

    entry = case['loading']

    loading = PropellantLoading()
    loading.setInputs({'flightLoad':      entry['flightLoad'],
                       'transferRate':    entry['transferRate'],
                       'chilldownMass':   entry['chilldownMass'],
                       'boilOffRate':     entry['boilOffRate'],
                       'holdDuration':    entry['holdDuration'],
                       'storageCapacity': entry['storageCapacity'],
                       'detankRecovery':  entry['detankRecovery']})

    return loading

def buildTimeline(case: dict) -> CountdownTimeline:

    entry = case['countdown']

    timeline = CountdownTimeline()
    timeline.setInputs({'tasks':             entry['tasks'],
                        'windowDuration':    entry['windowDuration'],
                        'turnaroundDrivers': entry['turnaroundDrivers']})

    return timeline

def buildAvailability(case: dict, attempts: int) -> LaunchAvailability:

    entry = case['availability']

    availability = LaunchAvailability()
    availability.setInputs({'constraints': entry['constraints'],
                            'attempts':    attempts,
                            'correlation': entry['correlation']})

    return availability

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: siting -- #
# ------------------------------------------------------------------------------------------------ #

def reportSiting(case: dict) -> dict:

    siting = buildSiting(case)

    equivalent = siting.calculateEquivalent()
    distances = siting.calculateDistances()
    check = siting.checkFacilities()
    crossover = siting.hydrogenCrossover()

    rows = [[entry['combination'],
             f'{entry["propellantMass"]:,.0f}',
             f'{entry["equivalentMass"]:,.0f}',
             f'{entry["effectiveFraction"] * 100.0:.1f}%',
             entry['governing']] for entry in equivalent['contributions']]

    print()
    print(f'    {"stage":<16}{"propellant [kg]":>18}{"TNT equiv [kg]":>18}'
          f'{"fraction":>12}   governing rule')

    for row in rows:
        print(f'    {row[0]:<16}{row[1]:>18}{row[2]:>18}{row[3]:>12}   {row[4]}')

    hydrogen = equivalent['contributions'][1]
    kerosene = equivalent['contributions'][0]

    flatReading = hydrogen['propellantMass'] * 0.14

    print()
    print(f'  The upper stage is {hydrogen["propellantMass"] / kerosene["propellantMass"] * 100.0:.0f}% '
          f'of the first stage by mass and contributes almost the same fraction of')
    print(f'  its own mass to the equivalent: {hydrogen["effectiveFraction"] * 100.0:.1f}% against '
          f'{kerosene["effectiveFraction"] * 100.0:.1f}%. **Read as a flat fourteen per cent it '
          f'would have')
    print(f'  been {flatReading:,.0f} kg**, and the standard gives '
          f'{hydrogen["equivalentMass"]:,.0f}, which is '
          f'{hydrogen["equivalentMass"] / flatReading:.0%} of that.')
    print()
    print(f'  The reason is the shape of the rule. Below {crossover["crossoverMass"]:,.0f} kg the '
          f'sublinear term governs and the')
    print('  effective fraction rises without limit as the load falls.')
    print()

    print('    load [kg]      effective fraction   governing rule')
    for sample in crossover['samples']:
        print(f'    {sample["propellantMass"]:>12,.0f}   {sample["effectiveFraction"] * 100.0:>16.1f}%   '
              f'{sample["governing"]}')

    print()
    print('  - **A small hydrogen stage is disproportionately hazardous per kilogram.** That is the '
          'reverse of the intuition that a small vehicle is a small siting problem.')
    print()

    published = HYDROGEN_METRIC_COEFFICIENT_PUBLISHED
    exact = HYDROGEN_METRIC_COEFFICIENT_EXACT

    print(f'  One thing found by reading the standard rather than a summary of it. The rule is '
          f'printed as')
    print(f'  8 W**(2/3) with W in pounds, and alongside it in brackets as {published} Q**(2/3) '
          f'with Q in')
    print(f'  kilograms. **Those are not the same rule.** Converting the English form exactly gives '
          f'{exact:.3f},')
    print(f'  and the two differ by a factor of {exact / published:.2f} with the published metric '
          f'form the smaller.')
    print(f'  On this stage that is {hydrogen["equivalentMass"]:,.0f} kg against '
          f'{published * hydrogen["propellantMass"] ** (2.0 / 3.0):,.0f}, and a shorter siting '
          f'distance from the latter.')
    print('  This library computes in the English form and converts, which is the conservative')
    print('  reading and the one that reproduces the numbers the standard is built on.')
    print()

    print('    criterion                       K      psi   distance [m]')
    for ring in distances['rings']:
        print(f'    {ring["criterion"]:<28}{ring["kFactor"]:>6.2f}{ring["overpressure"]:>9.1f}'
              f'{ring["distance"]:>15,.0f}')

    ratio = (distances['rings'][-1]['distance'] / distances['rings'][0]['distance'])
    kRatio = distances['rings'][-1]['kFactor'] / distances['rings'][0]['kFactor']

    print()
    print(f'  The rings span a factor of {ratio:.1f}, which is the K ratio of {kRatio:.1f} exactly: '
          f'the propellant sets')
    print('  the scale and K sets the ring. **Cube root scaling runs the wrong way for fixing a')
    print('  shortfall.** Eight times the propellant is twice the distance, so halving a distance')
    print('  needs the load cut by a factor of eight, and no vehicle offloads that much.')
    print()

    print('    facility                 criterion              required [m]   actual [m]   ratio')
    for entry in check['facilities']:
        print(f'    {entry["name"]:<24}{entry["criterion"]:<22}{entry["required"]:>13,.0f}'
              f'{entry["actual"]:>13,.0f}{entry["ratio"]:>8.2f}')

    print()
    print(f'  - The binding facility is the {check["binding"]["name"]} at '
          f'{check["binding"]["ratio"]:.2f} times its required distance.')
    print('  - **The binding one is not the closest one.** It is the one whose criterion is '
          'strictest relative to where it sits, which is a different question and the one the '
          'layout has to answer.')

    return {'equivalent': equivalent,
            'distances':  distances,
            'check':      check,
            'crossover':  crossover,
            'siting':     siting}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: loading -- #
# ------------------------------------------------------------------------------------------------ #

def reportLoading(case: dict) -> dict:

    loading = buildLoading(case)

    sequence = loading.calculatePhases()
    demand = loading.calculateGroundDemand()
    scrub = loading.scrubCost()
    sensitivity = loading.holdSensitivity()

    print()
    print('    phase        mass [kg]   rate [kg/s]   duration [min]   share of time')
    for entry in sequence['phases']:
        share = entry['duration'] / sequence['totalTime']
        print(f'    {entry["phase"]:<12}{entry["mass"]:>9,.0f}{entry["rate"]:>14.2f}'
              f'{entry["duration"] / 60.0:>17.1f}{share * 100.0:>16.0f}%')

    print()
    print(f'  Tanking takes {sequence["totalTime"] / 60.0:.0f} minutes, and the phase that '
          f'dominates it is {sequence["longestPhase"]["phase"]} at '
          f'{sequence["longestShare"] * 100.0:.0f}%.')
    print('  **Not the fast fill, which is the phase everybody pictures.** Chill-down runs at a')
    print('  fraction of the transfer rate by necessity, because the point of it is to boil.')
    print()

    print('    item                      mass [kg]   share')
    for entry in demand['breakdown']:
        print(f'    {entry["item"]:<25}{entry["mass"]:>10,.0f}{entry["share"] * 100.0:>8.1f}%')

    chilldownShare = case['loading']['chilldownMass'] / case['loading']['flightLoad']

    print()
    print(f'  - One attempt draws {demand["demandRatio"]:.2f} times the flight load from storage.')
    print(f'  - **The chill-down alone is {chilldownShare * 100.0:.0f}% of the flight load**, '
          f'because hydrogen has a small latent heat and a large vapour specific heat, so the metal '
          f'it cools costs a great deal of it.')
    print(f'  - The chill-down mass is computed by ChillDown in propulsion/ignitionAndStart and '
          f'taken here rather than recomputed. Two implementations of one enthalpy balance '
          f'eventually disagree.')
    print()

    print('    hold [min]   ground demand [kg]   demand / flight load')
    for entry in sensitivity['sweep']:
        print(f'    {entry["holdDuration"] / 60.0:>10.0f}{entry["totalDemand"]:>21,.0f}'
              f'{entry["demandRatio"]:>23.2f}')

    print()
    print(f'  - Two hours of hold adds {sensitivity["span"]:,.0f} kg, '
          f'{sensitivity["spanShare"] * 100.0:.0f}% of the flight load. **A hold is a mass as well '
          f'as a schedule**, and the slope is the boil-off rate, which makes it linear and easy to '
          f'lose track of.')
    print()

    print(f'  - A scrub after tanking loses {scrub["lostOnScrub"]:,.0f} kg, '
          f'{scrub["lostFraction"]:.2f} flight loads, even with '
          f'{scrub["detankRecovery"] * 100.0:.0f}% recovered on the detank.')
    print(f'  - Storage of {case["loading"]["storageCapacity"]:,.0f} kg supports '
          f'{scrub["attemptsAffordable"]} attempts. **The campaign is propellant limited before it '
          f'is schedule limited**, and that is a resupply contract rather than an engineering '
          f'change.')

    return {'sequence':    sequence,
            'demand':      demand,
            'scrub':       scrub,
            'sensitivity': sensitivity,
            'loading':     loading}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: countdown -- #
# ------------------------------------------------------------------------------------------------ #

def reportCountdown(case: dict) -> dict:

    timeline = buildTimeline(case)

    path = timeline.calculateCriticalPath()
    hold = case['countdown']['hold']
    recycle = timeline.calculateRecycle(hold['holdAt'], hold['backUpTo'], hold['holdDuration'])
    turnaround = timeline.calculateTurnaround()
    attempts = timeline.attemptsPerCampaign(case['countdown']['campaignDuration'])

    print()
    print('    task                          duration [min]   starts [min]   float [min]   critical')
    for entry in path['tasks']:
        print(f'    {entry["name"]:<30}{entry["duration"] / 60.0:>15.0f}'
              f'{entry["earliestStart"] / 60.0:>15.0f}{entry["float"] / 60.0:>14.0f}'
              f'{"   yes" if entry["critical"] else "":>11}')

    print()
    print(f'  The count is {path["totalDuration"] / 60.0:.0f} minutes against a serial sum of '
          f'{path["serialSum"] / 60.0:.0f}, a parallel gain of {path["parallelGain"]:.2f}.')
    print(f'  Critical path: {" -> ".join(path["criticalPath"])}.')
    print()

    if path['nearCritical']:
        print(f'  - Near critical, with under {5}% of the count in float: '
              f'{", ".join(path["nearCritical"])}.')
        print('  - **Those are the tasks that become the schedule on a bad day**, and they are the '
              'ones worth watching rather than the ones already known to be critical.')
    else:
        print('  - Nothing sits near critical, so the float is genuine rather than nominal.')

    print()
    print(f'  - A hold at T-{hold["holdAt"]:.0f} s that backs up to T-{hold["backUpTo"]:.0f} s '
          f'costs {recycle["recycle"] / 60.0:.0f} minutes, not the '
          f'{hold["holdDuration"] / 60.0:.0f} of the hold itself.')
    print(f'  - **The recycle is {recycle["multiplier"]:.1f} times the hold.** The re-run of '
          f'everything between the hold and the recycle point is the larger part, and it is what '
          f'decides whether a hold is affordable inside the window.')
    print(f'  - Against a {case["countdown"]["windowDuration"] / 60.0:.0f} minute window it '
          f'{"fits" if recycle["fitsWindow"] else "does not fit"}, with '
          f'{recycle["windowMargin"] / 60.0:.0f} minutes to spare.')
    print()

    print('    turnaround driver                duration [h]')
    for entry in turnaround['ranked']:
        print(f'    {entry["driver"]:<33}{entry["duration"] / 3600.0:>10.0f}')

    print()
    print(f'  - Turnaround is {turnaround["turnaround"] / 3600.0:.0f} h, set entirely by '
          f'{turnaround["governing"]}.')
    print(f'  - Fixing it buys {turnaround["gainIfFixed"] / 3600.0:.0f} h and no more, because the '
          f'next driver is waiting at {turnaround["nextLargest"] / 3600.0:.0f} h. **The drivers run '
          f'in parallel, so the turnaround is the largest and not the sum** of '
          f'{turnaround["sumOfDrivers"] / 3600.0:.0f} h.')
    print(f'  - A {case["countdown"]["campaignDuration"] / 86400.0:.0f} day campaign therefore gets '
          f'{attempts["attempts"]} attempts, which is the input the launch probability needs.')

    return {'path':       path,
            'recycle':    recycle,
            'turnaround': turnaround,
            'attempts':   attempts,
            'timeline':   timeline}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: availability -- #
# ------------------------------------------------------------------------------------------------ #

def reportAvailability(case: dict, attempts: int) -> dict:

    availability = buildAvailability(case, attempts)

    perAttempt = availability.calculatePerAttempt()
    campaign = availability.calculateCampaign()
    levers = availability.compareLevers()
    sweep = availability.attemptSweep()
    attribution = availability.scrubAttribution()

    # The lever comparison saturates once the campaign is nearly certain, so it is swept over
    # attempt count rather than quoted at one. Where it discriminates is where there are few
    # attempts, which is where a programme actually lives.
    ladder = [buildAvailability(case, count).compareLevers()
              for count in (1, 2, 3, 4, campaign['attempts'])]

    print()
    print('    criterion                  violated   go alone   costs the launch')
    for entry in perAttempt['constraints']:
        print(f'    {entry["constraint"]:<27}{entry["violationRate"] * 100.0:>7.0f}%'
              f'{entry["goProbability"] * 100.0:>11.0f}%{entry["costsUs"] * 100.0:>18.1f}%')

    print()
    print(f'  {perAttempt["count"]} criteria, none worse than '
          f'{(1.0 - perAttempt["worst"]["violationRate"]) * 100.0:.0f}% on its own, give '
          f'{perAttempt["perAttempt"] * 100.0:.1f}% together.')
    print(f'  **The combined penalty against the worst one alone is '
          f'{perAttempt["combinedPenalty"] * 100.0:.0f} points**, and it is invisible when '
          f'criteria are reviewed one at a time, which is how they are usually reviewed.')
    print()

    print('    attempts   cumulative   marginal gain')
    for entry in sweep['sweep'][:6]:
        print(f'    {entry["attempts"]:>8}{entry["cumulative"] * 100.0:>13.1f}%'
              f'{entry["marginal"] * 100.0:>16.1f}%')

    print()
    print(f'  - {sweep["thresholds"][0.90]} attempts reach 90%, {sweep["thresholds"][0.95]} reach '
          f'95%, {sweep["thresholds"][0.99]} reach 99%.')
    print()

    print(f'    attempts   baseline   fix the worst criterion   one more attempt   ratio')
    for entry in ladder:
        print(f'    {entry["attempts"]:>8}{entry["baseline"] * 100.0:>11.1f}%'
              f'{entry["constraintGain"] * 100.0:>24.1f}%'
              f'{entry["attemptGain"] * 100.0:>18.1f}%{entry["ratio"]:>8.1f}')

    print()
    print(f'  - The criterion fixed is {levers["worstConstraint"]}, by '
          f'{levers["improvement"] * 100.0:.0f} points, which is a large change to a launch '
          f'commit criterion.')
    print(f'  - **Attempts beat criteria at every attempt count**, and by the most where there are '
          f'fewest: a factor of {ladder[0]["ratio"]:.1f} on a single attempt campaign, falling to '
          f'{ladder[-1]["ratio"]:.1f} by {campaign["attempts"]}.')
    print('  - That makes turnaround a launch probability requirement rather than an operational')
    print('    convenience, which is the link back to the countdown.')
    print('  - It also says when to stop arguing about criteria. **Once a campaign has enough')
    print('    attempts the criteria stop mattering**, and the binding constraint moves to')
    print('    propellant resupply.')
    print()

    print(f'  - Over {campaign["attempts"]} attempts the campaign reaches '
          f'{campaign["independent"] * 100.0:.1f}% if the attempts are independent and '
          f'{campaign["correlated"] * 100.0:.1f}% at a day to day correlation of '
          f'{campaign["correlation"]:.1f}.')
    print(f'  - **Independence is the optimistic assumption**, and the '
          f'{campaign["gap"] * 100.0:.1f} point gap is the honest uncertainty in the answer. A '
          f'front over the range violates the same criteria tomorrow, and after a scrub the '
          f'conditional go probability falls to '
          f'{campaign["conditionalAfterScrub"] * 100.0:.0f}%.')
    print()

    print(f'  - {attribution["expectedScrubs"]:.1f} scrubs are expected across the campaign, of '
          f'which {attribution["byCause"][0]["scrubs"]:.1f} are weather.')
    print(f'  - Roughly half of scrubs on the Eastern Range across three decades were weather, '
          f'which is the one number in this stage with a published record behind it.')

    return {'perAttempt':  perAttempt,
            'campaign':    campaign,
            'levers':      levers,
            'sweep':       sweep,
            'attribution': attribution,
            'availability': availability}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the boundaries -- #
# ------------------------------------------------------------------------------------------------ #

def reportBoundaries(case: dict) -> None:

    print()
    print('  Ground systems is a fluid system with different constraints, so most of what a pad')
    print('  needs computing is already computed. This domain builds only what nothing else does.')
    print()

    print('  Built, because nothing else computes them:')
    print()
    print('    Explosive siting. No other domain converts a propellant load into a distance, and')
    print('    it is the only part of this domain with a standard behind it that was read in full.')
    print('    Ground propellant demand. fluidSystems computes boil-off and propulsion computes')
    print('    chill-down; nothing adds them up across a launch attempt.')
    print('    Countdown critical path and recycle. Nothing else has a schedule in it.')
    print('    Launch probability from launch commit criteria.')
    print()

    print('  Not built, and each for a stated reason:')
    print()
    print('    **GSE fluid analysis.** A ground half system is lines, valves, orifices, regulators')
    print('    and reliefs, and fluidSystems computes all of it. A second implementation sized for')
    print('    heavier walls and lower cost would be the same equations with different inputs.')
    print()
    print('    **Chill-down mass.** ChillDown in propulsion/ignitionAndStart does the enthalpy')
    print('    balance, including the factor of nine spread between its bounds for hydrogen. This')
    print('    domain consumes that number and does not reproduce it.')
    print()
    print('    **Boil-off from insulation.** Insulation in fluidSystems computes the heat leak and')
    print('    the vented rate. This domain takes the rate and integrates it over an operation.')
    print()
    print('    **Umbilical retract dynamics.** A spring and a mass, which is what')
    print('    mechanismsAndSeparation is for. The pressure area force at a disconnect is a')
    print('    Fitting calculation in fluidSystems.')
    print()
    print('    **Acoustic suppression and deluge sizing.** environmentsAndLoads owns the acoustic')
    print('    environment and the water flow is a fluidSystems problem. The pad decision is how')
    print('    much water and where, and that is a facility design rather than a calculation.')
    print()
    print('    **Debris footprint and instantaneous impact point.** rangeSafetyAndFTS.')
    print()
    print('    **Weather forecasting.** Not an engineering calculation at all. This domain takes')
    print('    violation rates as inputs and computes what they do to a campaign.')

# ------------------------------------------------------------------------------------------------ #
# -- Main -- #
# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    banner('1. THE HYDROGEN RULE IS SUBLINEAR, SO THE SMALL STAGE PAYS MORE PER KILOGRAM')
    reportSiting(case)

    banner('2. A LAUNCH ATTEMPT COSTS MORE PROPELLANT THAN THE VEHICLE CARRIES')
    reportLoading(case)

    banner('3. ONE CHAIN SETS THE COUNT AND ONE DRIVER SETS THE TURNAROUND')
    countdown = reportCountdown(case)

    banner('4. SIX CRITERIA AT NINE TENTHS EACH ARE NOT NINE TENTHS')
    reportAvailability(case, countdown['attempts']['attempts'])

    banner('5. WHAT THIS DOMAIN DOES NOT COMPUTE')
    reportBoundaries(case)

    banner('SUMMARY: EIGHT THINGS WORTH KNOWING BEFORE PLANNING A LAUNCH CAMPAIGN')

    reportSummary(case)
    print()

def reportSummary(case: dict) -> None:

    '''
    The five headline numbers, recomputed rather than carried, so the summary cannot drift from
    the stages above it.
    '''

    siting = buildSiting(case)
    loading = buildLoading(case)
    timeline = buildTimeline(case)

    equivalent = siting.calculateEquivalent()
    hydrogen = equivalent['contributions'][1]
    scrub = loading.scrubCost()
    turnaround = timeline.calculateTurnaround()
    attempts = timeline.attemptsPerCampaign(case['countdown']['campaignDuration'])
    availability = buildAvailability(case, attempts['attempts'])
    perAttempt = availability.calculatePerAttempt()
    campaign = availability.calculateCampaign()

    sequence = loading.calculatePhases()

    rows = [
        ('hydrogen effective fraction, 38 t stage',
         f'{hydrogen["effectiveFraction"] * 100.0:.1f}% against a flat 14%'),
        ('where the hydrogen rule changes over', '84,635 kg'),
        ('inhabited building distance',
         f'{siting.calculateDistances(["inhabitedBuilding"])["rings"][0]["distance"]:,.0f} m'),
        ('tanking time, and what dominates it',
         f'{sequence["totalTime"] / 60.0:.0f} min, {sequence["longestShare"] * 100.0:.0f}% chill-down'),
        ('propellant lost on a scrub', f'{scrub["lostFraction"]:.2f} flight loads'),
        ('attempts the schedule allows against storage',
         f'{attempts["attempts"]} against {scrub["attemptsAffordable"]}'),
        ('turnaround, and what sets it',
         f'{turnaround["turnaround"] / 3600.0:.0f} h, {turnaround["governing"]}'),
        ('go probability per attempt, six criteria',
         f'{perAttempt["perAttempt"] * 100.0:.1f}%'),
        ('campaign, independent against correlated',
         f'{campaign["independent"] * 100.0:.1f}% against '
         f'{campaign["correlated"] * 100.0:.1f}%'),
    ]

    print()
    for label, value in rows:
        print(f'    {label:<45}{value:>32}')

    print()
    print(f'  **The schedule allows {attempts["attempts"]} attempts and the storage supports '
          f'{scrub["attemptsAffordable"]}.** The binding constraint on this')
    print('  campaign is a tank of liquid hydrogen, not a countdown and not the weather.')
    print()
    print('  The connecting theme is that a launch campaign is limited by things that are counted')
    print('  rather than designed: the number of attempts, the number of criteria, the number of')
    print('  loads in the storage tank. **Every one of them multiplies, and none of them is the')
    print('  subject of a design review.**')

if __name__ == '__main__':
    main()
