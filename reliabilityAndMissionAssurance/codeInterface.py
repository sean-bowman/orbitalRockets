
# -- reliabilityAndMissionAssurance worked example -- #

'''

One two stage vehicle: what can fail, what that costs, where the budget goes, and whether the
redundancy on it is redundancy.

Four results, and each is a case of the analysis pointing somewhere other than where the effort
goes.

**The two rankings in a FMECA disagree, and the disagreement is the finding.** A risk priority
number multiplies detection in, which pushes a rare and detectable catastrophe below a common and
hidden nuisance. Criticality does not, and it is the ranking that finds the modes a launch vehicle
cannot afford to sort to the bottom.

**The single point failures carry the whole fault tree.** Five of them account for essentially all
of the top event probability, and the two carefully redundant pairs contribute a thousandth of it.
**A fault tree is run to find the cut sets of order one**, and a tree that produces a number without
producing that list has been run for the wrong reason.

**A third of the reliability budget has nothing behind it.** The rollup closes, and two subsystems
carrying 35 per cent of the allowed unreliability are supported by an allocation and an assumption.
**A reliability number without a stated basis is a wish**, and the audit is what says which ones are.

**And adding a redundant unit buys seven per cent where separating the ones you have buys
forty-five.** Common cause is 93 per cent of a dual redundant set's failure probability at a ten per
cent beta, and no amount of duplication touches it. **Redundancy that shares a failure cause is not
redundancy.**

Run:
    python reliabilityAndMissionAssurance/codeInterface.py

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

sys.path.insert(0, os.path.join(HERE, 'reliabilityAndMissionAssuranceLibrary'))

from reliabilityUtils import (BETA_FACTORS, SEVERITY_CLASSES, DETECTION_CLASSES, FAILURE_RATES,
                              seriesReliability, zeroFailureDemonstration,
                              FmecaError, FaultTreeError, AllocationError, RedundancyError)
from FMECA import FMECA
from FaultTree import FaultTree
from ReliabilityBudget import ReliabilityBudget
from RedundancyAnalysis import RedundancyAnalysis

ASSET = os.path.join(HERE, 'reliabilityAndMissionAssuranceLibrary', 'assets',
                     'vehicleReliabilityExample.json')

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

def buildFmeca(case: dict, actionAll: bool = False) -> FMECA:

    entry = case['fmeca']

    actioned = ([mode['mode'] for mode in entry['modes']] if actionAll
                else entry['actioned'])

    analysis = FMECA()
    analysis.setInputs({'modes': entry['modes'], 'actioned': actioned})

    return analysis

def buildFaultTree(case: dict) -> FaultTree:

    entry = case['faultTree']

    tree = FaultTree()
    tree.setInputs({'topEvent':    entry['topEvent'],
                    'gates':       entry['gates'],
                    'basicEvents': entry['basicEvents']})

    return tree

def buildBudget(case: dict) -> ReliabilityBudget:

    entry = case['budget']

    budget = ReliabilityBudget()
    budget.setInputs({'target':          entry['target'],
                      'itemReliability': entry['itemReliability'],
                      'subsystems':      entry['subsystems']})

    return budget

def buildRedundancy(case: dict, sharing: str = None) -> RedundancyAnalysis:

    entry = case['redundancy']

    analysis = RedundancyAnalysis()
    analysis.setInputs({'elementReliability':  entry['elementReliability'],
                        'units':               entry['units'],
                        'sharing':             sharing if sharing else entry['sharing'],
                        'coverage':            entry['coverage'],
                        'requiredReliability': entry['requiredReliability']})

    return analysis

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the FMECA -- #
# ------------------------------------------------------------------------------------------------ #

def reportFmeca(case: dict) -> dict:

    analysis = buildFmeca(case)

    table = analysis.calculateTable()
    disagreement = analysis.rankingDisagreement()
    review = analysis.mandatoryReview()

    print()
    print('    item                    mode                     severity       detection      crit   RPN')
    for entry in table['byCriticality']:
        print(f'    {entry["item"]:<23}{entry["mode"]:<25}{entry["severity"]:<15}'
              f'{entry["detection"]:<15}{entry["criticality"]:>4}{entry["riskPriority"]:>6}')

    print()
    print(f'  - Top by criticality is **{table["topByCriticality"]}**; top by risk priority is '
          f'**{table["topByRiskPriority"]}**. The rankings '
          f'{"agree" if table["rankingsAgree"] else "DISAGREE"}.')
    print('  - A risk priority number is severity times occurrence times detection, and all three')
    print('    are ordinal ranks. **Multiplying ordinals produces something that sorts and does not')
    print('    measure**: an RPN of 80 is not twice an RPN of 40.')
    print()

    print('    mode                     severity       by criticality   by RPN   moved')
    for entry in disagreement['entries']:
        print(f'    {entry["mode"]:<25}{entry["severity"]:<15}{entry["criticalityRank"]:>15}'
              f'{entry["priorityRank"]:>9}{entry["movement"]:>8}')

    print()
    if disagreement['anyBuried']:
        print(f'  - **Buried by the detection column: {", ".join(disagreement["buried"])}.**')
        print('  - A catastrophic mode that is detectable sorts below a less severe one that is')
        print('    not, which is exactly backwards for a launch vehicle where the catastrophic')
        print('    modes are the whole point.')
    print(f'  - **Criticality is severity times occurrence without detection**, and it is the '
          f'ranking that finds them.')
    print()

    print(f'  - {review["count"]} of {table["count"]} modes sit at or above '
          f'{review["threshold"]} severity, which is '
          f'{review["share"] * 100.0:.0f} per cent of the table.')
    print('  - **Those are reviewed because they are severe**, regardless of how either ordinal')
    print('    product ranks them. That filter uses no arithmetic at all and it is the one that')
    print('    cannot be gamed.')
    print()

    try:
        analysis.checkActions()
        actionsClear = True
        message = ''
    except FmecaError as error:
        actionsClear = False
        message = str(error).splitlines()[4]

    if actionsClear:
        print('  - Every mandatory review mode has an action against it.')
    else:
        print(f'  - **REFUSED.** {message}')
        print('  - **The FMECA is only useful if somebody acts on it.** An unactioned finding is')
        print('    worse than none, because it converts a real hazard into a document saying the')
        print('    hazard was considered.')

    complete = buildFmeca(case, actionAll = True)
    complete.checkActions()

    print()
    print('  - With every mode actioned the check passes, which is the point: the class is not')
    print('    measuring the design, it is measuring whether the analysis was finished.')

    return {'table': table, 'disagreement': disagreement, 'review': review,
            'actionsClear': actionsClear, 'analysis': analysis}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the fault tree -- #
# ------------------------------------------------------------------------------------------------ #

def reportFaultTree(case: dict) -> dict:

    tree = buildFaultTree(case)

    analysis = tree.analyseCutSets()
    importance = tree.importance()

    print()
    print('    cut set                     order   probability   share   ')
    for entry in analysis['cutSets']:
        marker = '  SINGLE POINT' if entry['isSinglePoint'] else ''
        print(f'    {" + ".join(entry["events"]):<28}{entry["order"]:>5}'
              f'{entry["probability"]:>14.3e}{entry["share"] * 100.0:>8.1f}%{marker}')

    print()
    print(f'  - The top event is {analysis["exactProbability"]:.3e} exactly, against '
          f'{analysis["rareEventSum"]:.3e} from the rare event sum: an overstatement of '
          f'{analysis["rareEventError"] * 100.0:.2f} per cent.')
    print('  - **The rare event approximation is optimistic in the safe direction**, because')
    print('    summing cut set probabilities double counts the overlaps. Computing both makes the')
    print('    error visible rather than assumed.')
    print()

    print(f'  - **{analysis["singlePointCount"]} single point failures carry '
          f'{analysis["singlePointShare"] * 100.0:.0f} per cent of the top event probability.**')
    print('  - The two carefully redundant pairs, the avionics and the initiators, contribute')
    print('    between them a thousandth of it.')
    print('  - **That is what a fault tree is for.** A probability can be got from a spreadsheet;')
    print('    a list of the combinations that on their own lose the mission cannot.')
    print()

    print('    basic event        probability   importance   removing it buys')
    for entry in importance['results']:
        print(f'    {entry["event"]:<18}{entry["probability"]:>13.2e}'
              f'{entry["importance"]:>13.3e}{entry["reductionShare"] * 100.0:>19.1f}%')

    print()
    print(f'  - The most important event is {importance["mostImportant"]} and the most probable is '
          f'{importance["mostProbable"]}: the rankings '
          f'{"agree here" if importance["rankingsAgree"] else "disagree"}.')
    print('  - **The importance measure is not the probability.** An event in a single point cut')
    print('    set has an importance near one whatever its probability, and an event behind an AND')
    print('    gate has an importance of roughly its partner probability. The redundant avionics')
    print('    units sit three orders of magnitude below the single valve on importance and one')
    print('    order ABOVE it on probability.')
    print()

    accepted = case['faultTree']['acceptedSinglePoints']

    try:
        tree.checkSinglePoints(accepted)
        singlePointsClear = True
        message = ''
    except FaultTreeError as error:
        singlePointsClear = False
        message = str(error).splitlines()[4]

    if singlePointsClear:
        print('  - Every single point failure is on the accepted list.')
    else:
        print(f'  - **REFUSED.** {message}')
        print('  - **A single point failure is a decision, not a finding.** They should be listed,')
        print('    argued and accepted deliberately, and an undiscovered one has had the decision')
        print('    made by default.')

    return {'analysis': analysis, 'importance': importance,
            'singlePointsClear': singlePointsClear, 'tree': tree}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the budget -- #
# ------------------------------------------------------------------------------------------------ #

def reportBudget(case: dict) -> dict:

    budget = buildBudget(case)

    rollup = budget.calculateRollup()
    audit = budget.basisAudit()
    allocation = budget.allocate()
    items = budget.itemCountEffect()
    demonstration = budget.demonstrationCost()

    print()
    print('    subsystem        reliability   failure    share   basis')
    for entry in rollup['subsystems']:
        print(f'    {entry["name"]:<17}{entry["reliability"]:>11.5f}{entry["failure"]:>11.2e}'
              f'{entry["share"] * 100.0:>8.0f}%   {entry["basis"]}')

    print()
    print(f'  - The rollup reaches {rollup["systemReliability"]:.5f} against a target of '
          f'{rollup["target"]:.3f}, a margin of {rollup["margin"]:.2f}.')
    print(f'  - **{rollup["dominant"]} is {rollup["dominantShare"] * 100.0:.0f} per cent of the '
          f'allowed unreliability**, so it is the only subsystem where an improvement moves the '
          f'vehicle.')
    print(f'  - The budget is kept in failure probability rather than reliability, because failure '
          f'probabilities are nearly additive: the sum is '
          f'{rollup["sumOfFailures"]:.3e} against an exact '
          f'{rollup["systemFailure"]:.3e}, an error of '
          f'{rollup["additiveError"] * 100.0:.2f} per cent.')
    print()

    print('    basis          share of the failure budget   means')
    for entry in audit['byBasis']:
        print(f'    {entry["basis"]:<15}{entry["share"] * 100.0:>21.0f}%   {entry["means"]}')

    print()
    print(f'  - **{audit["evidencedShare"] * 100.0:.0f} per cent of the failure budget has '
          f'evidence behind it and {audit["assumedShare"] * 100.0:.0f} per cent does not.**')
    print(f'  - The weakest entry is {audit["weakest"]}, and it is carrying a real share of the '
          f'vehicle target on a number somebody wrote down.')
    print('  - **A reliability number without a stated basis is a wish.** The basis column costs')
    print('    nothing to keep and it is the difference between a budget and a list of numbers.')
    print()

    print('    items    system reliability')
    for entry in items['sweep']:
        print(f'    {entry["items"]:>5}{entry["reliability"]:>22.4f}')

    print()
    print(f'  - At {items["itemReliability"]:.5f} per item, reliability halves at '
          f'{items["halvingCount"]:,.0f} items.')
    print('  - **Item count is a reliability parameter.** A design with twice the parts at the same')
    print('    per-part reliability has roughly twice the failure probability, which makes part')
    print('    count reduction a reliability decision before it is a mass or cost one.')
    print()

    print(f'  - Demonstrating the {demonstration["target"]:.2f} target by flight alone, with no '
          f'failures, would take {demonstration["flights"]:.0f} flights at '
          f'{demonstration["confidence"]:.0%} confidence.')
    print(f'  - Each additional nine costs {demonstration["perNine"]:.0f} times that. **So a '
          f'vehicle reliability is argued from its parts rather than demonstrated as a whole**, '
          f'which is why the basis audit above matters more than the number.')

    return {'rollup': rollup, 'audit': audit, 'allocation': allocation,
            'items': items, 'demonstration': demonstration, 'budget': budget}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: redundancy -- #
# ------------------------------------------------------------------------------------------------ #

def reportRedundancy(case: dict) -> dict:

    analysis = buildRedundancy(case)

    units = analysis.unitSweep()
    betas = analysis.betaSweep()
    levers = analysis.compareLevers()

    print()
    print('    units   Q with common cause   Q ideal      common cause   this unit buys')
    for entry in units['sweep']:
        print(f'    {entry["units"]:>5}{entry["systemFailure"]:>22.3e}'
              f'{entry["idealFailure"]:>13.3e}{entry["commonCauseShare"] * 100.0:>15.0f}%'
              f'{entry["marginalGain"] * 100.0:>17.0f}%')

    print()
    print(f'  - At a beta of {analysis.beta:.2f} the second unit buys '
          f'{units["firstUnitGain"] * 100.0:.0f} per cent and the fifth buys '
          f'{units["lastUnitGain"] * 100.0:.0f}.')
    print(f'  - **Common cause is {units["sweep"][1]["commonCauseShare"] * 100.0:.0f} per cent of '
          f'a dual redundant set failure probability**, and it does not fall when units are added: '
          f'the ideal arithmetic and the real one diverge by '
          f'{units["idealDivergence"]:,.0f} times by five units.')
    print('  - **Q = ((1 - beta) q)^n + beta q.** The first term falls as the nth power and the')
    print('    second does not fall at all, so above a couple of units the second term is simply')
    print('    the answer.')
    print()

    print('    sharing                  beta   Q            common cause   what it means')
    for entry in betas['results']:
        print(f'    {entry["sharing"]:<24}{entry["beta"]:>5.2f}{entry["systemFailure"]:>13.3e}'
              f'{entry["commonCauseShare"] * 100.0:>15.0f}%   {entry["note"]}')

    print()
    print(f'  - Across the sharing classes the failure probability spans {betas["spread"]:.0f} '
          f'times at a fixed unit count.')
    print('  - **That is the lever that works.** Separating the units physically and thermally,')
    print('    sourcing them from different lots, and where the consequence justifies it using')
    print('    different designs, are the only things that move the term that dominates.')
    print()

    print(f'  - Adding a third unit buys {levers["unitGain"] * 100.0:.0f} per cent. Moving from '
          f'{levers["currentSharing"]} to {levers["betterSharing"]} buys '
          f'{levers["betaGain"] * 100.0:.0f}, a factor of {levers["ratio"]:.1f}.')
    print('  - **Redundancy that shares a failure cause is not redundancy**, and the arithmetic')
    print('    says so numerically rather than as an aphorism.')
    print()

    try:
        analysis.checkRequirement()
        clears = True
        message = ''
    except RedundancyError as error:
        clears = False
        message = str(error).splitlines()[4]

    if clears:
        check = analysis.checkRequirement()
        print(f'  - Against a required {check["requiredReliability"]:.4f} the set reaches '
              f'{check["systemReliability"]:.6f}, a margin of {check["margin"]:.2f}.')
    else:
        print(f'  - **REFUSED.** {message}')

    ladder = []

    for sharing in ('identicalDifferentLot', 'sameDesignSeparated', 'diverseDesign',
                    'diverseAndSeparated'):

        trial = buildRedundancy(case, sharing = sharing)

        try:
            trial.checkRequirement()
            clearsHere = True
        except RedundancyError:
            clearsHere = False

        ladder.append({'sharing': sharing,
                       'beta':    trial.beta,
                       'reliability': trial.calculateConfiguration()['systemReliability'],
                       'clears':  clearsHere})

    print('    sharing                  beta   system R    clears the requirement')
    for entry in ladder:
        print(f'    {entry["sharing"]:<24}{entry["beta"]:>5.2f}{entry["reliability"]:>12.6f}'
              f'{"   yes" if entry["clears"] else "   no":>26}')

    firstClearing = next((entry['sharing'] for entry in ladder if entry['clears']), None)

    print()
    print(f'  - Separation alone does not close it. **{firstClearing} does**, and no hardware was')
    print('    added anywhere on that ladder: every row is the same two units at the same element')
    print('    reliability, differing only in how much they share.')
    print('  - **The improvement is a layout decision and a sourcing decision**, which is what')
    print('    makes it the cheapest reliability available and the one most often left on the')
    print('    table.')

    return {'units': units, 'betas': betas, 'levers': levers,
            'clears': clears, 'sharingLadder': ladder,
            'firstClearing': firstClearing, 'analysis': analysis}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the boundaries -- #
# ------------------------------------------------------------------------------------------------ #

def reportBoundaries(case: dict) -> None:

    print()
    print('  Reliability engineering is mostly process, and the process parts are documented')
    print('  rather than modelled. Four things are computed here because they are arithmetic that')
    print('  gets done wrong.')
    print()

    print('  Built, because nothing else computes them:')
    print()
    print('    FMECA ranking, and the disagreement between criticality and risk priority.')
    print('    Fault tree cut sets, which is the only way single point failures are found.')
    print('    Series rollup and allocation with a basis audit.')
    print('    Common cause redundancy, which every other domain in this repository assumes away.')
    print()

    print('  Not built, and each for a stated reason:')
    print()
    print('    **Component failure rate prediction.** A parts count prediction from a handbook is')
    print('    a number with a well documented history of being optimistic, and generating one')
    print('    here would give it more authority than it earns. The rates in this library are')
    print('    representative and registered as unvalidated.')
    print()
    print('    **Quality systems, configuration management and problem reporting.** Process, and')
    print('    documented as such. They are where most escapes actually come from and none of')
    print('    them is a calculation.')
    print()
    print('    **Human error probability.** Quantified human reliability analysis exists and its')
    print('    numbers carry very large uncertainty. HumanFactors documents the design responses')
    print('    rather than putting a probability on a person.')
    print()
    print('    **The FTS reliability case.** rangeSafetyAndFTS owns it, including the zero-failure')
    print('    demonstration arithmetic, and this domain supplies the common cause model its')
    print('    redundancy arithmetic leaves out.')
    print()
    print('    **Derating curves.** Component specific and they belong with the components:')
    print('    electricalPower for electronics, aerospaceMaterials for allowables.')
    print()
    print('    **Bayesian updating of a reliability estimate.** Real, useful, and it needs a prior')
    print('    this repository has no basis for.')

# ------------------------------------------------------------------------------------------------ #
# -- Main -- #
# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    banner('1. THE TWO FMECA RANKINGS DISAGREE, AND THAT IS THE FINDING')
    reportFmeca(case)

    banner('2. THE SINGLE POINT FAILURES CARRY THE WHOLE FAULT TREE')
    reportFaultTree(case)

    banner('3. A THIRD OF THE BUDGET HAS NOTHING BEHIND IT')
    reportBudget(case)

    banner('4. SEPARATING THE UNITS BEATS ADDING ONE')
    reportRedundancy(case)

    banner('5. WHAT THIS DOMAIN DOES NOT COMPUTE')
    reportBoundaries(case)

    banner('SUMMARY: WHAT TO CARRY OUT OF THIS DOMAIN')
    reportSummary(case)
    print()

def reportSummary(case: dict) -> None:

    '''
    Recomputed rather than carried, so the summary cannot drift from the stages above it.
    '''

    fmeca = buildFmeca(case)
    table = fmeca.calculateTable()
    disagreement = fmeca.rankingDisagreement()

    tree = buildFaultTree(case)
    cutSets = tree.analyseCutSets()

    budget = buildBudget(case)
    rollup = budget.calculateRollup()
    audit = budget.basisAudit()
    demonstration = budget.demonstrationCost()

    redundancy = buildRedundancy(case)
    units = redundancy.unitSweep()
    levers = redundancy.compareLevers()

    rows = [
        ('FMECA rankings agree', 'no' if not table['rankingsAgree'] else 'yes'),
        ('modes buried by the detection column', f'{len(disagreement["buried"])}'),
        ('single point failures in the tree', f'{cutSets["singlePointCount"]}'),
        ('share of the top event they carry', f'{cutSets["singlePointShare"]:.0%}'),
        ('rare event overstatement', f'{cutSets["rareEventError"]:.2%}'),
        ('dominant subsystem, and its share',
         f'{rollup["dominant"]}, {rollup["dominantShare"]:.0%}'),
        ('failure budget with evidence behind it', f'{audit["evidencedShare"]:.0%}'),
        ('flights to demonstrate the target', f'{demonstration["flights"]:.0f}'),
        ('common cause share of a dual set',
         f'{units["sweep"][1]["commonCauseShare"]:.0%}'),
        ('a third unit against separating the two',
         f'{levers["unitGain"]:.0%} against {levers["betaGain"]:.0%}'),
    ]

    print()
    for label, value in rows:
        print(f'    {label:<45}{value:>32}')

    print()
    print('  The connecting theme is that reliability engineering keeps producing numbers whose')
    print('  form matters more than their value. An ordinal product sorts and does not measure. A')
    print('  cut set of order one is categorically different from one of order two. A failure')
    print('  probability with no basis is not a number at all. And a redundancy gain that ignores')
    print('  common cause is off by the ratio of two terms rather than by a percentage.')
    print()
    print('  **In every case the arithmetic is easy and the discipline is in reading it honestly.**')

if __name__ == '__main__':
    main()
