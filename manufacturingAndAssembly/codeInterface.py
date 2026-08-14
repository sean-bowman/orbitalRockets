
# -- manufacturingAndAssembly worked example -- #

'''

One tank barrel section: whether it goes together, whether anybody can tell it is sound, and what it
costs at rate.

Four results, and each is a case of an assumption that is usually made and rarely checked.

**A three sigma statistical tolerance stack is no saving at all below about nine contributors.** The
worst case is a hard bound and the statistical stack at k sigma exceeds it whenever k is above the
square root of the contributor count. On a six contributor stack the statistical method is worse
than the arithmetic one, which is the reverse of why it is used.

**One dimension holds half the stack.** Tightening it moves the whole assembly and tightening any of
the others moves nothing, because a contributor enters the statistical stack as its square.

**An inspection that cannot find a flaw smaller than the critical one establishes nothing.** At full
wall the penetrant inspection is comfortable. Take the same weld to a thinner wall, where the
critical flaw is 1.3 mm, and it fails: the inspection misses 13 per cent of the flaws large enough
to burst the tank, so the part is not inspectable and has to be proof tested or life limited
instead. **And the cheapest method that clears the size requirement cannot be used on the material
at all**, which is what the table's "what it misses" column exists to catch.

**Capacity is the slowest station and not the sum.** Fixing it buys the gap to the next station and
no more, which is the same arithmetic as a turnaround driver and is ignored just as often. And a
programme of twenty units has barely started down its learning curve: the twentieth unit still costs
half the first, and the cumulative average, which is the number the programme is judged on, is
higher still.

Run:
    python manufacturingAndAssembly/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'manufacturingLibrary'))

from manufacturingUtils import (NDE_METHODS, LEARNING_RATES, PROCESS_TOLERANCES,
                                MINIMUM_HIT_MISS_TARGETS, MINIMUM_SIGNAL_TARGETS,
                                logOddsPod,
                                ToleranceError, RateError, InspectionError)
from ToleranceStack import ToleranceStack
from InspectionCapability import InspectionCapability
from ProductionRate import ProductionRate

ASSET = os.path.join(HERE, 'manufacturingLibrary', 'assets', 'tankBarrelExample.json')

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

def buildStack(case: dict, improved: bool = False) -> ToleranceStack:

    entry = case['toleranceStack']

    contributors = [dict(item) for item in entry['contributors']]

    if improved:
        for item in contributors:
            if item['name'] == entry['improvedContributor']:
                item['tolerance'] = entry['improvedTolerance']

    stack = ToleranceStack()
    stack.setInputs({'contributors': contributors,
                     'nominalGap':   entry['nominalGap'],
                     'minimumGap':   entry['minimumGap'],
                     'maximumGap':   entry['maximumGap'],
                     'sigmaLevel':   entry['sigmaLevel']})

    return stack

def buildInspection(case: dict, thinWall: bool = False) -> InspectionCapability:

    entry = case['inspection']

    inspection = InspectionCapability()
    inspection.setInputs({'method':           entry['method'],
                          'responseType':     entry['responseType'],
                          'demonstrationTargets': entry['demonstrationTargets'],
                          'criticalFlawSize': (entry['thinWallCriticalFlawSize'] if thinWall
                                               else entry['criticalFlawSize']),
                          'detectionMargin':  entry['detectionMargin']})

    return inspection

def buildProduction(case: dict, improved: bool = False) -> ProductionRate:

    entry = case['production']

    stations = dict(entry['stations'])

    if improved:
        stations[entry['improvedStation']] = entry['improvedCycleTime']

    production = ProductionRate()
    production.setInputs({'firstUnitCost': entry['firstUnitCost'],
                          'processClass':  entry['processClass'],
                          'annualDemand':  entry['annualDemand'],
                          'shifts':        entry['shifts'],
                          'stations':      stations})

    return production

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the stack -- #
# ------------------------------------------------------------------------------------------------ #

def reportStack(case: dict) -> dict:

    stack = buildStack(case)
    result = stack.calculateStack()

    print()
    print('    contributor                     tolerance [mm]   worst case   statistical')
    for entry in result['contributors']:
        print(f'    {entry["name"]:<32}{entry["tolerance"] * 1000.0:>13.3f}'
              f'{entry["worstCaseShare"] * 100.0:>13.0f}%{entry["statisticalShare"] * 100.0:>13.0f}%')

    print()
    print(f'  Worst case {result["worstCase"] * 1000.0:.3f} mm against a statistical '
          f'{result["statistical"] * 1000.0:.3f} mm over {result["count"]} contributors.')
    print()

    print(f'  - **{result["dominant"]} holds {result["dominantShare"] * 100.0:.0f} per cent of the '
          f'statistical stack** on '
          f'{result["contributors"][0]["worstCaseShare"] * 100.0:.0f} per cent of the worst case.')
    print('  - A contributor enters the worst case linearly and the statistical stack as its')
    print('    square, so **the two rankings are different and the statistical one is far more')
    print('    concentrated.** Tightening the dominant dimension moves the assembly; tightening')
    print('    any of the others moves almost nothing.')
    print()

    print(f'  - The two stacks differ by {result["ratio"]:.2f}, against '
          f'{result["equalContributorRatio"]:.2f} for {result["count"]} EQUAL contributors.')
    print(f'  - **Unequal contributors erode the benefit of the statistical method**, by '
          f'{result["unequalPenalty"]:.2f} here, because one loose dimension dominates the '
          f'quadrature sum and the sum stops behaving like root n.')
    print()

    print(f'  - The worst case is a hard bound, so a k sigma statistical stack exceeds it whenever '
          f'k is above {result["sigmaCrossover"]:.2f}.')
    print(f'  - At the {stack.sigmaLevel:.0f} sigma this case quotes, **the statistical method '
          f'{"helps" if result["statisticalHelps"] else "does not help at all"}**: '
          f'{stack.sigmaLevel:.0f} sigma of a '
          f'{result["statistical"] * 1000.0:.3f} mm standard deviation is '
          f'{result["statistical"] * stack.sigmaLevel * 1000.0:.3f} mm, which is more than the '
          f'{result["worstCase"] * 1000.0:.3f} mm arithmetic sum.')
    print('  - For equal contributors the crossover is exactly the square root of the count, so')
    print('    **three sigma needs more than nine contributors before it saves anything.** That is')
    print('    a one line check and it is almost never made.')
    print()

    crossover = []
    for count in (2, 4, 6, 9, 10, 16, 25):
        trial = ToleranceStack()
        trial.setInputs({'nominalGap': 0.004, 'sigmaLevel': 3.0,
                         'contributors': [{'name': f'c{index}', 'tolerance': 3.0e-4}
                                          for index in range(count)]})
        entry = trial.calculateStack()
        crossover.append((count, entry['sigmaCrossover'], entry['statisticalHelps']))

    print('    equal contributors   crossover sigma   does 3 sigma help')
    for count, sigma, helps in crossover:
        print(f'    {count:>18}{sigma:>18.2f}{"   yes" if helps else "   no":>20}')

    print()

    for method in ('worstCase', 'statistical'):
        try:
            check = stack.checkGap(method)
            capped = ' (capped at the worst case)' if check['cappedAtWorstCase'] else ''
            print(f'  - {method}: gap runs {check["smallestGap"] * 1000.0:.3f} to '
                  f'{check["largestGap"] * 1000.0:.3f} mm{capped}, '
                  f'{"shim to " + format(check["shimRequired"] * 1000.0, ".3f") + " mm" if check.get("needsShim") else "no shim"}.')
        except ToleranceError as error:
            print(f'  - {method}: **REFUSED.** {str(error).splitlines()[4]}')

    improved = buildStack(case, improved = True)
    improvedResult = improved.calculateStack()

    print()
    print(f'  - Tightening {case["toleranceStack"]["improvedContributor"]} from '
          f'{case["toleranceStack"]["contributors"][0]["tolerance"] * 1000.0:.2f} to '
          f'{case["toleranceStack"]["improvedTolerance"] * 1000.0:.2f} mm cuts the worst case to '
          f'{improvedResult["worstCase"] * 1000.0:.3f} mm and the statistical to '
          f'{improvedResult["statistical"] * 1000.0:.3f}.')
    print(f'  - The dominant contributor becomes {improvedResult["dominant"]} at '
          f'{improvedResult["dominantShare"] * 100.0:.0f} per cent. **The problem moves rather '
          f'than going away**, which is the same shape as a bottleneck and a life limit.')

    rejects = stack.rejectFraction()

    print()
    print(f'  - At {rejects["sigmaLevel"]:.0f} sigma, {rejects["partsPerMillion"]:.0f} assemblies '
          f'per million fall outside the stack: one in {rejects["assembliesPerReject"]:.0f}.')
    print('  - **That is the number to argue about**, not the tail probability. One in 370 sounds')
    print('    like nothing until it is multiplied by the number of stacks in a vehicle, and every')
    print('    one of them is a rework rather than a scrap.')

    return {'result':   result,
            'improved': improvedResult,
            'rejects':  rejects,
            'stack':    stack}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the inspection -- #
# ------------------------------------------------------------------------------------------------ #

def reportInspection(case: dict) -> dict:

    inspection = buildInspection(case)

    curve = inspection.detectionCurve()
    demonstration = inspection.demonstrationSize()
    check = inspection.checkAgainstCriticalFlaw()
    methods = inspection.compareMethods()

    print()
    print('    flaw size [mm]   probability of detection')
    for entry in curve['curve']:
        print(f'    {entry["flawSize"] * 1000.0:>14.3f}{entry["probability"] * 100.0:>27.1f}%')

    print()
    print(f'  - a50 is {curve["a50"] * 1000.0:.3f} mm and a90 is {curve["a90"] * 1000.0:.3f}, a '
          f'ratio of {curve["a90OverA50"]:.2f}.')
    print(f'  - **That ratio is 9 to the power sigma and nothing else**, so the shape of the curve '
          f'is one number. A steep inspection has a small sigma and a narrow band between finding '
          f'half and finding nine tenths.')
    print()

    print(f'  - The demonstration behind a claim needs at least '
          f'{demonstration["minimumTargets"]} targets for a {inspection.responseType} response and '
          f'{demonstration["unflawedSites"]} unflawed sites for a false positive rate.')
    print(f'  - This case used {demonstration["targets"]:.0f}. **a90/95 is a confidence bound, so '
          f'it depends on the demonstration size as well as on the inspection**: the handbook notes '
          f'that {demonstration["preciseTargets"]} opportunities give a significantly smaller '
          f'a90/95 for the same technique.')
    print('  - The uncomfortable reading of that is that **the flaw size a programme designs to is')
    print('    partly a statement about how many specimens somebody paid for.**')
    print()

    print(f'  - At full wall the critical flaw is '
          f'{check["criticalFlawSize"] * 1000.0:.3f} mm against an a90 of '
          f'{check["a90"] * 1000.0:.3f}, and the inspection finds '
          f'{check["probabilityAtCritical"] * 100.0:.1f} per cent of flaws that size.')
    print(f'  - With a factor of {check["detectionMargin"]:.0f} between the reliably detectable '
          f'size and the critical one, the requirement is '
          f'{check["requiredCriticalSize"] * 1000.0:.3f} mm and the margin is '
          f'{check["margin"]:.2f}. It clears.')
    print('  - **The factor exists because the flaw grows between inspections.** A margin of one')
    print('    means the inspection just barely rules out failure today and says nothing about')
    print('    the interval before the next one.')
    print()

    thin = buildInspection(case, thinWall = True)

    try:
        thin.checkAgainstCriticalFlaw()
        thinRefused = False
        thinMessage = ''
    except InspectionError as error:
        thinRefused = True
        thinMessage = str(error).splitlines()[4]

    missedAtThin = 1.0 - float(logOddsPod(case['inspection']['thinWallCriticalFlawSize'],
                                          thin.a50, thin.sigma))

    print(f'  - Take the same weld to a thinner wall, where the critical flaw is '
          f'{case["inspection"]["thinWallCriticalFlawSize"] * 1000.0:.3f} mm, and the case is '
          f'{"REFUSED" if thinRefused else "accepted"}.')
    print(f'  - The inspection misses {missedAtThin * 100.0:.0f} per cent of flaws large enough to '
          f'burst the tank. **It establishes nothing.**')
    print('  - That is a design conclusion rather than an inspection finding: the part has to be')
    print('    proof tested, life limited, or made from something with a larger critical flaw.')
    print('  - **It is also the conclusion that gets discovered late**, because the inspection')
    print('    procedure is written after the wall thickness is fixed.')
    print()

    print('    method                a50 [mm]   a90 [mm]   cost   establishes something')
    for entry in methods['results']:
        verdict = 'yes' if entry.get('establishesSomething') else 'NO'
        print(f'    {entry["method"]:<21}{entry["a50"] * 1000.0:>10.3f}{entry["a90"] * 1000.0:>11.3f}'
              f'{entry["relativeCost"]:>7.0f}{verdict:>24}')

    cheapest = methods['cheapestCapable']

    print()
    print(f'  - a90 spans {methods["a90Spread"]:.0f} times across the list and cost spans '
          f'{methods["costSpread"]:.0f}. **Capability and cost are correlated and not '
          f'proportional.**')
    print(f'  - The most sensitive method is {methods["best"]} at '
          f'{NDE_METHODS[methods["best"]]["relativeCost"]:.0f} times a walkaround, and the '
          f'cheapest one that clears is {cheapest} at '
          f'{NDE_METHODS[cheapest]["relativeCost"]:.0f}.')
    print()
    print(f'  - **And {cheapest} cannot be used on this part at all.** It misses '
          f'{NDE_METHODS[cheapest]["misses"]}, and the barrel is 2219 aluminium.')
    print(f'  - That is the point the table exists to make. **A ranking by a90 is not a ranking by '
          f'usefulness**, and the column that decides the answer is the one saying what each '
          f'method misses rather than the one saying what it finds.')
    print(f'  - The applicable answer here is {methods["results"][3]["method"]} at '
          f'{NDE_METHODS[methods["results"][3]["method"]]["relativeCost"]:.0f}, which finds '
          f'{NDE_METHODS[methods["results"][3]["method"]]["finds"]}.')

    return {'curve':         curve,
            'demonstration': demonstration,
            'check':         check,
            'methods':       methods,
            'thinRefused':   thinRefused,
            'missedAtThin':  missedAtThin,
            'inspection':    inspection}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the rate -- #
# ------------------------------------------------------------------------------------------------ #

def reportRate(case: dict) -> dict:

    production = buildProduction(case)

    doublings = production.doublingSweep()
    cumulative = production.cumulativeCost(case['production']['runLength'])
    classes = production.compareProcessClasses(case['production']['runLength'])
    takt = production.calculateTakt()
    shifts = production.shiftSensitivity()

    print()
    print('    unit   unit cost   of the first   saving from the previous doubling')
    for entry in doublings['sweep']:
        print(f'    {entry["unit"]:>6}{entry["unitCost"]:>12.3f}'
              f'{entry["fractionOfFirst"] * 100.0:>14.0f}%{entry["savingFromPrevious"]:>36.3f}')

    print()
    print(f'  - At a {production.learningRate:.2f} learning rate the exponent is '
          f'{doublings["exponent"]:.3f}, and by unit {doublings["sweep"][-1]["unit"]} the cost is '
          f'{doublings["atLastDoubling"] * 100.0:.0f} per cent of the first.')
    print(f'  - **Every doubling saves the same fraction and a smaller absolute amount**, so '
          f'{doublings["shareInFirstFour"] * 100.0:.0f} per cent of the whole saving arrives in '
          f'the first four units.')
    print()

    print(f'  - Over a run of {cumulative["units"]} the last unit costs '
          f'{cumulative["lastUnitCost"]:.3f} and the cumulative average is '
          f'{cumulative["cumulativeAverage"]:.3f}, a factor of '
          f'{cumulative["averageOverLast"]:.2f}.')
    print('  - **The average is the number a programme is judged on and it lags the unit cost**,')
    print('    because it still carries every expensive early unit. A cost estimate quoting the')
    print('    learned-out figure is quoting a number the programme will not reach for years.')
    print()

    print('    process class      learning rate   last unit   cumulative average')
    for entry in classes['results']:
        print(f'    {entry["processClass"]:<18}{entry["learningRate"]:>15.2f}'
              f'{entry["lastUnitCost"]:>12.3f}{entry["cumulativeAverage"]:>21.3f}')

    print()
    print(f'  - Across the process classes the last unit spans {classes["spread"]:.2f} times.')
    print('  - **The more labour a process carries, the more there is to learn.** A process that')
    print('    is mostly a material purchase barely learns at all, which means a vehicle built')
    print('    from bought hardware has a flatter curve than one built from labour, whatever the')
    print('    programme plan assumes.')
    print()

    print('    station                             cycle [h]   utilisation   bottleneck')
    for entry in takt['stations']:
        print(f'    {entry["station"]:<36}{entry["cycleTime"]:>10.1f}'
              f'{entry["utilisation"] * 100.0:>14.0f}%{"   yes" if entry["isBottleneck"] else "":>13}')

    print()
    print(f'  - Takt time is {takt["taktTime"]:.1f} h for {takt["annualDemand"]:.0f} units a year '
          f'on {takt["shifts"]:.0f} shift, and the line makes {takt["capacity"]:.0f}.')
    print(f'  - **Capacity is the {takt["bottleneck"]} station and not the '
          f'{takt["sumOfCycleTimes"]:.0f} h sum**, because the stations run in parallel on '
          f'different units. Anything spent on the other four buys nothing at all.')
    print(f'  - Fixing it buys {takt["gainIfFixed"]:.1f} h and no more, because '
          f'{takt["stations"][1]["station"]} is waiting at '
          f'{takt["nextStationTime"]:.1f} h. **The bottleneck moves rather than going away.**')

    improved = buildProduction(case, improved = True)
    improvedTakt = improved.calculateTakt()

    print()
    print(f'  - Cutting it to {case["production"]["improvedCycleTime"]:.0f} h moves the bottleneck '
          f'to {improvedTakt["bottleneck"]} and raises capacity from {takt["capacity"]:.0f} to '
          f'{improvedTakt["capacity"]:.0f}.')
    print()

    print('    shifts   capacity   meets demand')
    for entry in shifts['results']:
        print(f'    {entry["shifts"]:>8.0f}{entry["capacity"]:>11.0f}'
              f'{"   yes" if entry["meetsDemand"] else "   no":>15}')

    print()
    print(f'  - {shifts["shiftsRequired"]:.0f} shift meets the demand here, and shifts are worth '
          f'checking before a machine is bought: **a second shift doubles capacity for the cost of '
          f'people and a second machine doubles it for the cost of a machine and people.**')

    return {'doublings':  doublings,
            'cumulative': cumulative,
            'classes':    classes,
            'takt':       takt,
            'improved':   improvedTakt,
            'shifts':     shifts,
            'production': production}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the boundaries -- #
# ------------------------------------------------------------------------------------------------ #

def reportBoundaries(case: dict) -> None:

    print()
    print('  The process physics of this domain lives somewhere else, and deliberately.')
    print('  aerospaceMaterials carries ten process sub-domains: additiveLPBF, additiveOther,')
    print('  spinCasting, castingProcesses, wroughtMaterials, formingProcesses, machiningProcesses,')
    print('  joiningProcesses, postProcessing and extrusionHoning. What stays here is the')
    print('  cross-cutting view.')
    print()

    print('  Built, because nothing else computes them:')
    print()
    print('    Tolerance stackup. No other domain assembles anything.')
    print('    Inspection capability against a critical flaw size. aerospaceMaterials computes the')
    print('    critical flaw and nothing asks whether it can be found.')
    print('    Learning curve and line rate. vehicleArchitecture names both as gaps in its own')
    print('    cost document and does not fill them.')
    print()

    print('  Not built, and each for a stated reason:')
    print()
    print('    **Machining, forming, casting and joining physics.** Taylor tool life, chatter')
    print('    lobes, springback, forming limit diagrams, solidification and weld knockdowns are')
    print('    all in the aerospaceMaterials sub-domains. A second implementation here would be')
    print('    the same equations with a different import path.')
    print()
    print('    **Weld joint efficiency and HAZ knockdown.** Weld in fluidSystems owns them, and')
    print('    joiningProcesses is docs-only in aerospaceMaterials for exactly that reason.')
    print()
    print('    **Buy-to-fly and process route comparison.** ProcessComparison in')
    print('    aerospaceMaterials already compares routes on buy-to-fly, allowable knockdown,')
    print('    mass, cost index and lead time.')
    print()
    print('    **Critical flaw size.** DamageTolerance in aerospaceMaterials computes it. This')
    print('    domain consumes it and asks whether the inspection can see it.')
    print()
    print('    **Cost estimating relationships.** A cost model per subsystem is a real piece of')
    print('    work and vehicleArchitecture says so in CostAndProducibility. The learning curve')
    print('    here takes a first unit cost as an input rather than predicting one.')
    print()
    print('    **Supplier qualification and counterfeit control.** A process and a governance')
    print('    problem, documented rather than modelled.')

# ------------------------------------------------------------------------------------------------ #
# -- Main -- #
# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    banner('1. A THREE SIGMA STACK IS NO SAVING BELOW NINE CONTRIBUTORS')
    reportStack(case)

    banner('2. AN INSPECTION THAT CANNOT SEE THE CRITICAL FLAW ESTABLISHES NOTHING')
    reportInspection(case)

    banner('3. CAPACITY IS THE SLOWEST STATION AND NOT THE SUM')
    reportRate(case)

    banner('4. WHAT THIS DOMAIN DOES NOT COMPUTE')
    reportBoundaries(case)

    banner('SUMMARY: WHAT TO CARRY OUT OF THIS DOMAIN')
    reportSummary(case)
    print()

def reportSummary(case: dict) -> None:

    '''
    Recomputed rather than carried, so the summary cannot drift from the stages above it.
    '''

    stack = buildStack(case).calculateStack()
    inspection = buildInspection(case)
    curve = inspection.detectionCurve()
    methods = inspection.compareMethods()
    production = buildProduction(case)
    takt = production.calculateTakt()
    cumulative = production.cumulativeCost(case['production']['runLength'])

    rows = [
        ('worst case against statistical stack',
         f'{stack["worstCase"] * 1000.0:.3f} against {stack["statistical"] * 1000.0:.3f} mm'),
        ('sigma at which the statistical stack helps', f'below {stack["sigmaCrossover"]:.2f}'),
        ('dominant contributor share', f'{stack["dominantShare"]:.0%} of the statistical stack'),
        ('a90 over a50, which is 9 to the sigma', f'{curve["a90OverA50"]:.2f}'),
        ('methods that establish anything here',
         f'{sum(1 for e in methods["results"] if e.get("establishesSomething"))} of '
         f'{len(methods["results"])}'),
        ('cheapest capable and applicable method',
         f'{methods["cheapestCapable"]} on size, {methods["results"][3]["method"]} in fact'),
        ('line capacity against demand',
         f'{takt["capacity"]:.0f} against {takt["annualDemand"]:.0f} a year'),
        ('gain from fixing the bottleneck', f'{takt["gainIfFixed"]:.0f} h, then it moves'),
        ('unit 20 against the cumulative average',
         f'{cumulative["lastUnitCost"]:.2f} against {cumulative["cumulativeAverage"]:.2f}'),
    ]

    print()
    for label, value in rows:
        print(f'    {label:<45}{value:>32}')

    print()
    print('  The connecting theme is that manufacturing is full of quantities that are governed by')
    print('  one term and estimated as though they were governed by all of them. One dimension')
    print('  holds the stack, one station holds the rate, one flaw size decides whether an')
    print('  inspection means anything. **In every case the gain from fixing the governing term is')
    print('  the gap to the next one, and in every case it is easier to improve the wrong thing.**')

if __name__ == '__main__':
    main()
