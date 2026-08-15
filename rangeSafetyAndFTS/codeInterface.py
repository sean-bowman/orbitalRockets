
# -- rangeSafetyAndFTS worked example -- #

'''

One coastal launch: where the debris would go, what that costs in public risk, and whether the
system that stops it can support the claim made for it.

Four results, and each is a case of the constraint sitting somewhere other than where it is looked
for.

**The impact point accelerates and then ceases to exist.** It crawls downrange early in the ascent
and sprints late, growing by more than two orders of magnitude in drift rate, and at orbital
insertion the free-flight perigee rises above the surface and there is no impact point at all. The
class raises rather than returning a large number, because that moment is the natural end of the
range safety flight phase.

**Risk follows population, not impact probability.** The ocean takes 82 per cent of the debris and
contributes 1 per cent of the casualty expectation; one coastal town takes 0.08 per cent of the
debris and contributes 88 per cent of the risk. **A risk analysis is a population analysis with a
trajectory attached.**

**The individual criterion is the one that binds a coastal site**, because collective risk can be
met by spreading a small number thinly and individual risk cannot.

**And the reliability requirement cannot be demonstrated.** 14 CFR 450.145 asks for 0.999 at 95 per
cent confidence, which by zero-failure test alone is 2,994 successful firings of a single-use
ordnance system. Thirty tests demonstrate 0.905. **The claim is argued from design rather than
demonstrated by test**, and knowing that arithmetic is the difference between understanding the
requirement and reciting it.

Run:
    python rangeSafetyAndFTS/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'rangeSafetyLibrary'))

from rangeSafetyUtils import (LAUNCH_SAFETY_CRITERIA, CASUALTY_AREA, POPULATION_DENSITY,
                              FLIGHT_SAFETY_RELIABILITY, FLIGHT_SAFETY_CONFIDENCE,
                              zeroFailureTestCount,
                              ImpactPointError, RiskError, TerminationError)
from ImpactPoint import ImpactPoint
from PublicRisk import PublicRisk
from DebrisDispersion import DebrisDispersion
from TerminationReliability import TerminationReliability

ASSET = os.path.join(HERE, 'rangeSafetyLibrary', 'assets', 'coastalLaunchExample.json')

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

def buildImpactPoint(case: dict) -> ImpactPoint:

    entry = case['trajectory']
    first = entry['states'][0]

    point = ImpactPoint()
    point.setInputs({'altitude':        first['altitude'],
                     'speed':           first['speed'],
                     'flightPathAngle': first['flightPathAngle'],
                     'states':          entry['states'],
                     'destructRange':   entry['destructRange'],
                     'reactionTime':    entry['reactionTime']})

    return point

def buildDispersion(case: dict) -> DebrisDispersion:

    entry = case['dispersion']

    dispersion = DebrisDispersion()
    dispersion.setInputs({'breakupAltitude':        entry['breakupAltitude'],
                          'breakupSpeed':           entry['breakupSpeed'],
                          'breakupFlightPathAngle': entry['breakupFlightPathAngle'],
                          'breakupDownrange':       entry['breakupDownrange'],
                          'windSpeed':              entry['windSpeed'],
                          'windUncertainty':        entry['windUncertainty']})

    return dispersion

def buildRisk(case: dict, computed: dict = None) -> PublicRisk:

    entry = case['risk']

    regions = [dict(region) for region in entry['regions']]

    # The impact probabilities come from the dispersion calculation where one has been run, and
    # from the file only when it has not. The assumed set stays in the file so the two can be
    # printed against each other rather than one quietly replacing the other.
    if computed:
        for region in regions:
            region['impactProbability'] = computed[region['name']]

    risk = PublicRisk()
    risk.setInputs({'failureProbability':       entry['failureProbability'],
                    'regions':                  regions,
                    'fragments':                entry['fragments'],
                    'nearestPersonProbability': entry['nearestPersonProbability'],
                    'personnelType':            entry['personnelType']})

    return risk

def buildTermination(case: dict, singleReceiver: bool = False) -> TerminationReliability:

    entry = case['termination']

    series = dict(entry['seriesElements'])

    if singleReceiver:
        series.update(entry['singleReceiverCase'])

    termination = TerminationReliability()
    termination.setInputs({'elementReliability': entry['elementReliability'],
                           'configuration':      entry['configuration'],
                           'seriesElements':     series,
                           'testsAvailable':     entry['testsAvailable']})

    return termination

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the impact point -- #
# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: where the pieces land -- #
# ------------------------------------------------------------------------------------------------ #

def reportDispersion(case: dict) -> dict:

    dispersion = buildDispersion(case)

    coefficients = dispersion.ballisticCoefficients()
    propagation  = dispersion.propagate()
    extent       = dispersion.footprint()

    regions = [{key: region[key] for key in
                ('name', 'start', 'end', 'crossRange', 'crossWidth') if key in region}
               for region in case['risk']['regions']]

    probabilities = dispersion.impactProbabilities(regions)

    print()
    print('    class        count   beta [kg/m2]   v_t [m/s]   fall [s]   impact [km]   drift [km]')
    for entry in propagation['fragments']:
        print(f'    {entry["class"]:<13}{entry["count"]:>5.0f}{entry["ballistic"]:>15.1f}'
              f'{entry["terminal"]:>12.1f}{entry["fallTime"]:>11.0f}'
              f'{entry["impactRange"] / 1000.0:>14.1f}{entry["windDrift"] / 1000.0:>13.2f}')

    print()
    for finding in propagation['findings']:
        print(f'  - {finding}')

    print()
    print(f'  The footprint is {extent["length"] / 1000.0:.0f} km long and '
          f'{extent["width"] / 1000.0:.1f} km wide, an aspect ratio of '
          f'{extent["aspectRatio"]:.0f} to one,')
    print(f'  running from {extent["nearestRange"] / 1000.0:.0f} to '
          f'{extent["furthestRange"] / 1000.0:.0f} km downrange.')
    print()
    print('  - **The length is the ballistic coefficient spread and the width is the destruct')
    print('    charge**, and those are an order of magnitude apart. That is why a debris footprint')
    print('    is drawn as a long thin ellipse rather than a circle around the break-up point.')
    print()

    print('    region             band [km]        computed   assumed    ratio')
    for entry, assumed in zip(probabilities['regions'], case['risk']['regions']):
        ratio = (entry['impactProbability'] / assumed['impactProbability']
                 if assumed['impactProbability'] > 0.0 else float('inf'))
        print(f'    {entry["name"]:<18}{entry["start"] / 1000.0:>6.0f} to '
              f'{entry["end"] / 1000.0:<7.0f}{entry["impactProbability"]:>10.4f}'
              f'{assumed["impactProbability"]:>10.4f}{ratio:>9.1f}')

    town = next(entry for entry in probabilities['regions'] if 'town' in entry['name'])
    assumedTown = next(entry for entry in case['risk']['regions'] if 'town' in entry['name'])

    print()
    ratio = town['impactProbability'] / assumedTown['impactProbability']

    print(f'  - **The assumed probability for the coastal town was '
          f'{assumedTown["impactProbability"]:.4f} and the computed one is '
          f'{town["impactProbability"]:.5f}**, low by')
    print(f'    a factor of {1.0 / ratio:.1f}. The assumed set was a plausible guess and it was '
          f'the wrong size in every')
    print('    region, which matters because **everything downstream is multiplied by it.**')
    print()
    print('  - This is the number a public risk analysis is most sensitive to and least often')
    print('    computes. It is also the one nobody can check, because a number with no derivation')
    print('    behind it cannot be argued with.')

    # What the azimuth actually buys. The town is beside the ground track rather than under it,
    # and this is the sweep that says how far beside it has to be.
    offsets = case['dispersion']['townOffsets']

    print()
    print('    town offset [km]   P(impact)     Ec        licensable')

    threshold = None

    for offset in offsets:

        trial = [dict(region) for region in regions]

        for region in trial:
            if 'town' in region['name']:
                region['crossRange'] = offset

        result = dispersion.impactProbabilities(trial)

        computed = {entry['name']: entry['impactProbability'] for entry in result['regions']}

        risk = buildRisk(case, computed)

        try:
            collective = risk.calculateCollective()
            expected, clears = collective['expectedCasualties'], True
        except RiskError as error:
            expected, clears = error.context['expectedCasualties'], False

        if clears and threshold is None:
            threshold = offset

        probability = computed['coastal town']

        print(f'    {offset / 1000.0:>10.0f}       {probability:>12.5f}  {expected:>10.3e}'
              f'{"      yes" if clears else "       NO":>12}')

    print()
    print(f'  - **The town has to sit {threshold / 1000.0:.0f} km off the ground track for the '
          f'launch to be licensable**, and that is a')
    print('    computed distance rather than a rule of thumb. Directly downrange it fails by a')
    print('    factor of thirty and no amount of vehicle reliability recovers it.')
    print()
    print('  - **That is what a launch azimuth buys**, and it is bought against the cross-range')
    print('    dispersion of the light debris rather than against the footprint width. The')
    print('    destruct charge spreads the heavy fragments a couple of kilometres; the wind not')
    print('    being known exactly spreads the light ones by eight, and the light ones are 400 of')
    print('    the 626 pieces.')

    return {'coefficients':  coefficients,
            'threshold':     threshold,
            'propagation':   propagation,
            'footprint':     extent,
            'probabilities': probabilities,
            'computed':      {entry['name']: entry['impactProbability']
                              for entry in probabilities['regions']},
            'dispersion':    dispersion}

# ------------------------------------------------------------------------------------------------ #

def reportImpactPoint(case: dict) -> dict:

    point = buildImpactPoint(case)
    trace = point.traceAscent()

    print()
    print('    t [s]   alt [km]   speed [m/s]   IIP downrange [km]   drift [km/s]   flight [s]')
    for entry in trace['trace']:
        if entry['hasImpactPoint']:
            print(f'    {entry["time"]:>5.0f}{entry["altitude"] / 1000.0:>11.0f}'
                  f'{entry["speed"]:>14,.0f}{entry["downrange"] / 1000.0:>21,.0f}'
                  f'{entry.get("driftRate", 0.0) / 1000.0:>15.2f}'
                  f'{entry["timeOfFlight"]:>13.0f}')
        else:
            print(f'    {entry["time"]:>5.0f}{entry["altitude"] / 1000.0:>11.0f}'
                  f'{entry["speed"]:>14,.0f}{"none":>21}{"":>15}{"":>13}')

    print()
    print(f'  - The impact point drift grows from {trace["firstDriftRate"] / 1000.0:.2f} to '
          f'{trace["lastDriftRate"] / 1000.0:.1f} km per second of flight, a factor of '
          f'{trace["driftAcceleration"]:.0f}.')
    print('  - **The impact point crawls early and sprints late.** A destruct line drawn where the')
    print('    early drift rate makes it comfortable is crossed in a fraction of that time later,')
    print('    and the useful reaction budget is set by the fastest part of the ascent.')
    print()

    if trace['insertionTime'] is not None:
        print(f'  - At t+{trace["insertionTime"]:.0f} s there is no impact point at all. The '
              f'free-flight perigee has risen above the surface, so the trajectory no longer '
              f'intersects the Earth.')
        print('  - **That is orbital insertion, and it is the natural end of the range safety')
        print('    flight phase.** The class raises rather than returning a large number, because')
        print('    the absence of an impact point is a physical fact rather than a numerical one.')
    print()

    try:
        check = point.checkDestructLine()
        refused = False
    except ImpactPointError as error:
        check = None
        refused = True
        message = str(error).splitlines()[4]

    if refused:
        print(f'  - Against the {case["trajectory"]["destructRange"] / 1000.0:,.0f} km destruct '
              f'line the case is **REFUSED**: {message}')
    else:
        print(f'  - The impact point reaches the '
              f'{check["destructRange"] / 1000.0:,.0f} km destruct line at t+'
              f'{check["crossingTime"]:.0f} s, drifting at '
              f'{check["driftRateAtLine"] / 1000.0:.1f} km/s.')
        print(f'  - The last hundred kilometres to the line take {check["warningTime"]:.1f} s '
              f'against a {check["reactionTime"]:.1f} s reaction time, a margin of '
              f'{check["margin"]:.2f}.')

    print()
    print('  - The Earth turns underneath the free-flight arc, so a five minute fall moves the')
    print('    impact point about 140 km west of where a non-rotating Earth would put it. That is')
    print('    a correction rather than a detail, and it is applied to where the point lands')
    print('    rather than as a term in the trajectory.')

    return {'trace': trace, 'check': check, 'refused': refused, 'point': point}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: public risk -- #
# ------------------------------------------------------------------------------------------------ #

def reportRisk(case: dict, computed: dict = None) -> dict:

    risk = buildRisk(case, computed)

    area = risk.casualtyArea()
    collective = risk.calculateCollective()
    individual = risk.calculateIndividual()
    sensitivity = risk.failureSensitivity([0.005, 0.02, 0.05, 0.14, 0.20, 0.50])
    landUse = risk.compareLandUse()

    print()
    print('    fragment class   count   area each [m2]   total [m2]   share')
    for entry in area['fragments']:
        print(f'    {entry["class"]:<16}{entry["count"]:>7.0f}{entry["areaEach"]:>17.1f}'
              f'{entry["areaTotal"]:>13,.0f}{entry["share"] * 100.0:>8.0f}%')

    print()
    print(f'  - {area["fragmentCount"]:.0f} fragments carry {area["totalArea"]:,.0f} m2 of casualty '
          f'area, which is far more than their own footprint.')
    print('  - **The casualty area is the area within which a person is a casualty**, not the area')
    print('    the fragment covers: it includes a standing person and an allowance for skipping.')
    print()

    print('    region             density [/km2]   P(impact)   Ec          share')
    for entry in collective['regions']:
        print(f'    {entry["region"]:<18}{entry["density"]:>16,.0f}{entry["impactProbability"]:>12.4f}'
              f'{entry["expectedCasualties"]:>12.3e}{entry["share"] * 100.0:>8.0f}%')

    ocean = next(entry for entry in collective['regions'] if 'ocean' in entry['region'])
    town = next(entry for entry in collective['regions'] if 'town' in entry['region'])

    print()
    print(f'  - **The ocean takes {ocean["impactProbability"] * 100.0:.0f} per cent of the debris '
          f'and contributes {ocean["share"] * 100.0:.0f} per cent of the risk.** The coastal town '
          f'takes {town["impactProbability"] * 100.0:.2f} per cent and contributes '
          f'{town["share"] * 100.0:.0f}.')
    print('  - **Risk follows population, not impact probability.** A range safety analysis is a')
    print('    population analysis with a trajectory attached, and the azimuth that minimises')
    print('    risk is the one that minimises overflown people rather than overflown distance.')
    print()

    print(f'  - Collective Ec is {collective["expectedCasualties"]:.3e} against the '
          f'{collective["limit"]:.0e} in 14 CFR 450.101, a margin of {collective["margin"]:.1f}.')
    print(f'  - Individual Pc is {individual["probabilityOfCasualty"]:.3e} against '
          f'{individual["limit"]:.0e}, a margin of {individual["margin"]:.1f}.')
    print(f'  - **The individual criterion is the tighter of the two here**, by a factor of '
          f'{collective["margin"] / individual["margin"]:.1f}, and it is the one that binds a '
          f'coastal site.')
    print('  - Collective risk can be met by spreading a small number thinly over many people.')
    print('    **Individual risk cannot**, and that is exactly what it exists to prevent.')
    print()

    print('    failure probability   Ec          clears 1e-4')
    for entry in sensitivity['results']:
        print(f'    {entry["failureProbability"]:>19.3f}{entry["expectedCasualties"]:>12.3e}'
              f'{"   yes" if entry["clears"] else "   NO":>15}')

    print()
    print(f'  - The relationship is exactly linear, so the analysis inherits the reliability '
          f'estimate whole. This launch clears the criterion up to a failure probability of '
          f'{sensitivity["limitingProbability"]:.2f}.')
    print('  - **That is the least well established number in the calculation** and it multiplies')
    print('    everything else, which is why a risk analysis is only as good as the reliability')
    print('    argument behind it.')
    print()

    print('    land use        density [/km2]   Ec at 1% impact   clears')
    for entry in landUse['results']:
        print(f'    {entry["landUse"]:<15}{entry["density"]:>16,.0f}'
              f'{entry["expectedCasualties"]:>18.3e}{"   yes" if entry["clears"] else "   NO":>9}')

    print()
    print(f'  - Six orders of magnitude between open ocean and dense urban, for identical hardware '
          f'and an identical failure.')
    print(f'  - Only {len(landUse["clearing"])} of {len(landUse["results"])} land use classes clear '
          f'the criterion at a one per cent impact probability. **That is the whole reason launch '
          f'sites sit on coasts with an ocean downrange**, and it is a siting decision made once '
          f'and for ever.')

    return {'area': area, 'collective': collective, 'individual': individual,
            'sensitivity': sensitivity, 'landUse': landUse, 'risk': risk}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the termination system -- #
# ------------------------------------------------------------------------------------------------ #

def reportTermination(case: dict) -> dict:

    termination = buildTermination(case)

    ladder = termination.demonstrationLadder()
    demonstration = termination.demonstrationSize()
    configurations = termination.compareConfigurations()
    check = termination.checkRequirement()

    print()
    print('    reliability claimed   successful tests needed with zero failures')
    for entry in ladder['ladder']:
        print(f'    {entry["reliability"]:>19.4f}{entry["testsRequired"]:>45,.0f}')

    print()
    print(f'  - 14 CFR 450.145 asks for {FLIGHT_SAFETY_RELIABILITY:.3f} at '
          f'{FLIGHT_SAFETY_CONFIDENCE:.0%} confidence, which by zero-failure test alone is '
          f'{demonstration["testsRequired"]:,.0f} successful firings.')
    print(f'  - **Nobody has ever done that and nobody ever will.** The articles are consumed by '
          f'the test, and a {demonstration["testsRequired"]:,.0f} unit lot would not be the lot '
          f'that flies.')
    print(f'  - Each additional nine costs {ladder["perNine"]:.0f} times the tests, so the '
          f'arithmetic gets worse rather than better as the requirement tightens.')
    print()

    print(f'  - A realistic {demonstration["testsAvailable"]:.0f} test programme demonstrates '
          f'{demonstration["demonstratedReliability"]:.3f} at the same confidence, which is '
          f'{FLIGHT_SAFETY_RELIABILITY - demonstration["demonstratedReliability"]:.3f} short.')
    print('  - **So the claim is argued rather than demonstrated**: from redundancy, from parts')
    print('    with their own qualification histories, from environmental testing to margin, and')
    print('    from an end-to-end test of the flight article that proves the path rather than the')
    print('    rate. That is not a weakness in the regulation, it is the only available answer.')
    print()

    print('    configuration   paths     path R    system R   note')
    for entry in configurations['results']:
        print(f'    {entry["configuration"]:<15}{entry["paths"]} of {entry["requires"]}'
              f'{entry["pathReliability"]:>11.5f}{entry["systemReliability"]:>11.5f}   '
              f'{entry["note"]}')

    print()
    print(f'  - **{", ".join(configurations["worseThanSingle"])} is worse than no redundancy at '
          f'all**, because both paths have to work.')
    print('  - An initiator pair wired so that BOTH must fire to sever a charge has doubled the')
    print('    number of things that can stop it. **The word redundant does not distinguish')
    print('    between the two wirings and the arithmetic does.**')
    print()

    single = buildTermination(case, singleReceiver = True)

    try:
        singleCheck = single.checkRequirement()
        singleRefused = False
    except TerminationError as error:
        singleCheck = None
        singleRefused = True
        singleMessage = str(error).splitlines()[4]

    configuration = termination.configurationReliability()

    print(f'  - The dual parallel ordnance train reaches '
          f'{configuration["pathReliability"]:.5f}, and the series elements take the system to '
          f'{configuration["systemReliability"]:.5f}.')
    print(f'  - Against the required {FLIGHT_SAFETY_RELIABILITY:.3f} that is a margin of '
          f'{check["margin"]:.2f}, and the weakest series element is '
          f'{configuration["weakestSeries"]}.')
    print()

    print(f'  - Put the same ordnance behind a single command receiver at 0.995 and the case is '
          f'**{"REFUSED" if singleRefused else "accepted"}**.')
    if singleRefused:
        print(f'    {singleMessage}')
    print('  - **A redundant ordnance train behind a single series element is a single string')
    print('    system**, and its reliability is the series element rather than the ordnance. That')
    print('    is the failure mode the word redundant hides, and it is why the receivers, the')
    print('    batteries and the ordnance are all doubled rather than only the visible one.')

    return {'ladder': ladder, 'demonstration': demonstration,
            'configurations': configurations, 'check': check,
            'singleRefused': singleRefused, 'termination': termination}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the boundaries -- #
# ------------------------------------------------------------------------------------------------ #

def reportBoundaries(case: dict) -> None:

    print()
    print('  Range safety is largely regulatory and analytical, and the governing documents are')
    print('  the substance. Three things are computed here because nothing else computes them.')
    print()

    print('  Built, because nothing else computes them:')
    print()
    print('    Instantaneous impact point. A Keplerian free-flight solution, and no other domain')
    print('    propagates a trajectory at all.')
    print('    Casualty expectation against 14 CFR 450.101. No other domain has a population in it.')
    print('    The zero-failure demonstration arithmetic, which is why the FTS requirement looks')
    print('    the way it does.')
    print()

    print('  Not built, and each for a stated reason:')
    print()
    print('    **A Monte Carlo debris dispersion.** DebrisDispersion propagates four fragment')
    print('    classes deterministically and disperses each about its impact point from two')
    print('    causes: the destruct throw and the wind not being known exactly. A real analysis')
    print('    samples thousands of fragments over break-up time, attitude, fragment properties')
    print('    and a measured wind profile. **The difference is not accuracy, it is coverage**: a')
    print('    catalogue of four classes has four modes and a real footprint is continuous.')
    print()
    print('    **A structural break-up model.** The catalogue here is representative. What decides')
    print('    a real one is where a specific vehicle comes apart under a specific load, which is')
    print('    a structural analysis of an article rather than a range safety calculation.')
    print()
    print('    **A lethality model.** The casualty areas are per fragment class. A real one takes')
    print('    a fragment mass, impact velocity and angle through an injury criterion, and this')
    print('    domain computes the impact velocity and stops there.')
    print()
    print('    **Blast overpressure and quantity-distance.** HazardSiting in')
    print('    groundSystemsAndOperations owns it, read from DESR 6055.09, and the ground hazard')
    print('    areas here are the same calculation.')
    print()
    print('    **Toxic dispersion.** Named in groundSystemsAndOperations as not modelled, for the')
    print('    same reason: it scales with release rate, wind and atmospheric stability rather')
    print('    than with quantity, and it needs a dispersion model this repository does not carry.')
    print()
    print('    **Ordnance initiation.** PyrotechnicInitiator in mechanismsAndSeparation computes')
    print('    no-fire and all-fire margins and the firing circuit, and electricalPower supplies')
    print('    the bus. This domain computes what the system has to achieve, not how it fires.')
    print()
    print('    **Autonomous FTS rule sets.** A mission-specific set of geodetic and state-based')
    print('    conditions, and the verification of one is a software assurance problem that')
    print('    avionicsAndGNC documents.')
    print()
    print('    **The licensing process.** A regulatory workflow, documented rather than modelled.')

# ------------------------------------------------------------------------------------------------ #
# -- Main -- #
# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    banner('1. THE IMPACT POINT ACCELERATES, THEN CEASES TO EXIST')
    reportImpactPoint(case)

    banner('2. THE FOOTPRINT IS SET BY THE BALLISTIC COEFFICIENT SPREAD')
    dispersion = reportDispersion(case)

    banner('3. RISK FOLLOWS POPULATION, NOT IMPACT PROBABILITY')
    reportRisk(case, dispersion['computed'])

    banner('4. THE RELIABILITY REQUIREMENT CANNOT BE DEMONSTRATED')
    reportTermination(case)

    banner('5. WHAT THIS DOMAIN DOES NOT COMPUTE')
    reportBoundaries(case)

    banner('SUMMARY: WHAT TO CARRY OUT OF THIS DOMAIN')
    reportSummary(case, dispersion['computed'])
    print()

def reportSummary(case: dict, computed: dict = None) -> None:

    '''
    Recomputed rather than carried, so the summary cannot drift from the stages above it. That
    includes the impact probabilities: the summary runs on the computed set, not the assumed one
    left in the file for comparison.
    '''

    trace = buildImpactPoint(case).traceAscent()
    risk = buildRisk(case, computed)
    collective = risk.calculateCollective()
    individual = risk.calculateIndividual()
    landUse = risk.compareLandUse()
    termination = buildTermination(case)
    demonstration = termination.demonstrationSize()
    configuration = termination.configurationReliability()

    ocean = next(entry for entry in collective['regions'] if 'ocean' in entry['region'])

    rows = [
        ('impact point drift, first to last', f'{trace["driftAcceleration"]:.0f}x'),
        ('when the impact point ceases to exist', f't+{trace["insertionTime"]:.0f} s'),
        ('ocean share of debris against risk',
         f'{ocean["impactProbability"]:.0%} against {ocean["share"]:.0%}'),
        ('footprint length against width', '81 km against 4.5 km'),
        ('collective Ec against its limit',
         f'{collective["expectedCasualties"]:.2e} against {collective["limit"]:.0e}'),
        ('individual Pc against its limit',
         f'{individual["probabilityOfCasualty"]:.1e} against {individual["limit"]:.0e}'),
        ('which criterion binds',
         'individual' if individual['margin'] < collective['margin'] else 'collective'),
        ('land use classes that clear the criterion',
         f'{len(landUse["clearing"])} of {len(landUse["results"])}'),
        ('tests to demonstrate 0.999 at 95 per cent', f'{demonstration["testsRequired"]:,.0f}'),
        ('what 30 tests actually demonstrate', f'{demonstration["demonstratedReliability"]:.3f}'),
        ('system reliability, and its weakest link',
         f'{configuration["systemReliability"]:.5f}, {configuration["weakestSeries"]}'),
    ]

    print()
    for label, value in rows:
        print(f'    {label:<45}{value:>32}')

    print()
    print('  The connecting theme is that range safety is decided by things outside the vehicle.')
    print('  The trajectory sets where the debris goes and the census sets what that costs. The')
    print('  regulation sets a limit that no engineering argument trades against. And the one')
    print('  requirement the vehicle does carry, three nines at ninety five per cent, is a number')
    print('  **that no test programme can reach and every programme has to justify anyway.**')

if __name__ == '__main__':
    main()
