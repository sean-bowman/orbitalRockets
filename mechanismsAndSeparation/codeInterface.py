
# -- mechanismsAndSeparation worked example -- #

'''

One stage separation, from the band that holds the joint to the panel that deploys afterwards.

Every device in this example operates exactly once. That single fact reorganises the engineering:
there is no run-in, no trend to watch, no second attempt, and every margin has to be demonstrated
on articles that are not the one that flies.

Four results are worth taking away and three of them are about the same thing.

**The joint that looks comfortable at installation is not the joint that flies.** Preload relaxes
by about eleven per cent over nine months of storage, and the margin has to be carried against the
relaxed value.

**Neither a stronger spring nor more springs fixes tipoff.** A stronger spring raises the tipoff
rate and the separation velocity in the same proportion, so the rotation accumulated while clearing
does not move at all. And the deterministic worst case is flat in spring count: half the springs
high and half low produce the same net moment whether there are four or forty. Only the statistical
case improves, as one over the root of the count. Matching the springs in opposing pairs is the one
thing that attacks the bound.

**Latch impact energy goes as the square of the arrival rate**, so a deployment spring chosen with
generous margin arrives violently and the latch pays quadratically for the comfort.

And underneath all of it: **test evidence is what buys margin.** The same actuator goes from a
margin of 0.21 to 0.62 without a single design change, because NASA-STD-5017B retires uncertainty
by measurement rather than by analysis.

Run:
    python mechanismsAndSeparation/codeInterface.py

Author: Sean Bowman
Date:   09/08/2026

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

sys.path.insert(0, os.path.join(HERE, 'mechanismsAndSeparationLibrary'))

from mechanismUtils import (TORQUE_MARGIN_FACTORS, REQUIRED_TORQUE_MARGIN,
                            MarginError, SeparationError, InitiationError,
                            MechanismsAndSeparationError)
from ClampBand import ClampBand
from PyrotechnicInitiator import PyrotechnicInitiator
from SeparationSystem import SeparationSystem
from DeploymentKinematics import DeploymentKinematics
from MechanismActuator import MechanismActuator

ASSET = os.path.join(HERE, 'mechanismsAndSeparationLibrary', 'assets', 'stageSeparationExample.json')

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Helpers -- #
# ------------------------------------------------------------------------------------------------ #

def buildBand(case: dict, storageMonths: float = None) -> ClampBand:

    interface = case['interface']

    band = ClampBand()
    band.setInputs({'bandTension':     interface['bandTension'],
                    'interfaceRadius': interface['radius'],
                    'wedgeAngle':      interface['wedgeAngle'],
                    'bandArea':        interface['bandArea'],
                    'flightLoad':      interface['flightLoad'],
                    'storageMonths':   (storageMonths if storageMonths is not None
                                        else interface['storageMonths'])})

    return band

def buildSeparation(case: dict) -> SeparationSystem:

    entry = case['separation']

    system = SeparationSystem()
    system.setInputs({'springCount':     entry['springCount'],
                      'springStiffness': entry['springStiffness'],
                      'springStroke':    entry['springStroke'],
                      'springRadius':    entry['springRadius'],
                      'separatingMass':  entry['separatingMass'],
                      'remainingMass':   entry['remainingMass'],
                      'inertia':         entry['inertia'],
                      'clearanceLength': entry['clearanceLength'],
                      'radialGap':       entry['radialGap']})

    return system

def buildDeployable(case: dict) -> DeploymentKinematics:

    entry = case['deployable']

    panel = DeploymentKinematics()
    panel.setInputs({'springTorque':    entry['springTorque'],
                     'springRate':      entry['springRate'],
                     'inertia':         entry['inertia'],
                     'travel':          np.radians(entry['travelDegrees']),
                     'resistingTorque': entry['resistingTorque']})

    return panel

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the joint that flies is not the joint that was installed -- #
# ------------------------------------------------------------------------------------------------ #

def reportClampBand(case: dict) -> dict:

    banner('1. THE JOINT THAT FLIES IS NOT THE JOINT THAT WAS INSTALLED')

    band = buildBand(case)

    preload    = band.calculatePreload()
    relaxation = band.calculateRelaxation()

    print(f'  A {band.bandTension / 1000.0:.0f} kN band on a '
          f'{band.wedgeAngle:.0f} degree wedge.')
    print()
    print(f'    {"quantity":24s} {"value":>12s}')
    print(f'    {"band tension":24s} {band.bandTension / 1000.0:9.1f} kN')
    print(f'    {"wedge amplification":24s} {preload["amplification"]:12.1f}')
    print(f'    {"ideal preload":24s} {preload["idealPreload"] / 1000.0:9.1f} kN')
    print(f'    {"wedge efficiency":24s} {preload["wedgeEfficiency"]:12.2f}')
    print(f'    {"delivered preload":24s} {preload["deliveredPreload"] / 1000.0:9.1f} kN')

    print()
    print('  The wedge is the whole device. A band a person can tension by hand produces a preload')
    print(f'  {preload["amplification"]:.0f} times larger, and friction on the wedge faces gives '
          f'back about a third of it.')

    print()
    print(f'    {"storage":>10s} {"retained [kN]":>15s} {"loss":>8s} {"margin":>9s}')

    trace = {}

    for months in (0.0, 3.0, 9.0, 24.0):

        trial = buildBand(case, storageMonths = months)

        entry = trial.calculateRelaxation()

        try:
            margin = trial.checkJoint()['margin']
            verdict = f'{margin:+8.1%}'
        except MarginError:
            margin = None
            verdict = '  REFUSED'

        trace[months] = {'retained': entry['retainedPreload'], 'margin': margin}

        print(f'    {months:9.0f}m {entry["retainedPreload"] / 1000.0:15.1f} '
              f'{entry["totalLoss"]:8.1%} {verdict:>9s}')

    print()
    for finding in relaxation['findings']:
        print(f'  - {finding}')

    print()
    print('  **The losses compound rather than adding**, and none of them is visible on the')
    print('  vehicle. A band installed to a comfortable margin and flown a year later is a')
    print('  different joint, and the only way to know is to have carried the relaxation in the')
    print('  margin from the start.')

    return {'band': band, 'preload': preload, 'relaxation': relaxation, 'trace': trace}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the two currents -- #
# ------------------------------------------------------------------------------------------------ #

def reportInitiator(case: dict) -> dict:

    banner('2. THE TWO CURRENTS THAT DEFINE HANDLING AN INITIATOR')

    entry = case['initiator']

    initiator = PyrotechnicInitiator()
    initiator.setInputs({'initiatorType':     entry['type'],
                         'firingVoltage':     entry['firingVoltage'],
                         'harnessResistance': entry['harnessResistance'],
                         'parallelCount':     entry['parallelCount'],
                         'strayCurrent':      entry['strayCurrent']})

    allFire = initiator.checkAllFire()
    noFire  = initiator.checkNoFire()

    print('  All-fire, the current that has to arrive:')
    print()
    for finding in allFire['findings']:
        print(f'    - {finding}')

    print()
    print('  No-fire, the current that must never arrive:')
    print()
    for finding in noFire['findings']:
        print(f'    - {finding}')

    print()
    print('  The gap between one amp and five amps is the entire design space, and it is narrower')
    print('  than it looks. Everything the vehicle does about bonding, shielding, twisted shielded')
    print('  pairs, shorting plugs and safe-and-arm devices exists to keep the left-hand number')
    print('  below the right-hand one.')

    comparison = initiator.compareInitiators()

    print()
    print(f'    {"initiator":14s} {"no-fire [A]":>13s}   fires on this circuit')
    for name, result in comparison['results'].items():
        print(f'    {name:14s} {result["noFireCurrent"]:13.2f}   '
              f'{"yes" if result["firesOnThisCircuit"] else "no"}')

    print()
    print('  **The initiator choice is an electromagnetic compatibility decision as much as an')
    print('  ordnance one.** A low energy device fires from a smaller circuit, which is real mass')
    print('  and battery, and it drops the no-fire threshold five times, which tightens every')
    print('  bonding and shielding requirement on the vehicle.')

    return {'initiator': initiator, 'allFire': allFire, 'noFire': noFire,
            'comparison': comparison}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: tipoff is a mismatch problem -- #
# ------------------------------------------------------------------------------------------------ #

def reportSeparation(case: dict) -> dict:

    banner('3. TIPOFF COMES FROM THE MISMATCH, NOT FROM THE STRENGTH')

    system = buildSeparation(case)

    velocity  = system.calculateVelocity()
    tipoff    = system.calculateTipoff()
    recontact = system.checkRecontact()

    print(f'    {"quantity":26s} {"value":>12s}')
    print(f'    {"total stored energy":26s} {velocity["totalEnergy"]:9.1f} J')
    print(f'    {"relative velocity":26s} {velocity["relativeVelocity"]:9.3f} m/s')
    print(f'    {"separating body":26s} {velocity["separatingVelocity"]:9.3f} m/s')
    print(f'    {"remaining body":26s} {velocity["remainingVelocity"]:9.3f} m/s')
    print(f'    {"tipoff rate":26s} {tipoff["rateDegrees"]:9.3f} deg/s')
    print(f'    {"rotation while clearing":26s} {recontact["rotationDegrees"]:9.3f} deg')
    print(f'    {"lateral excursion":26s} {recontact["excursion"] * 1000.0:9.2f} mm')
    print(f'    {"radial gap":26s} {recontact["radialGap"] * 1000.0:9.2f} mm')
    print(f'    {"clearance factor":26s} {recontact["clearanceFactor"]:12.1f}')

    print()
    for finding in tipoff['findings']:
        print(f'  - {finding}')

    counts = system.compareSpringCounts(case['separation']['springCountsTried'])

    print()
    print('  Now hold the total energy constant and change how many springs it is spread across:')
    print()
    print(f'    {"springs":>9s} {"stiffness [N/m]":>17s} {"velocity [m/s]":>16s} '
          f'{"worst [deg/s]":>15s} {"statistical":>13s}')

    for count, result in counts['results'].items():
        print(f'    {count:9d} {result["stiffness"]:17.0f} {result["velocity"]:16.3f} '
              f'{result["tipoff"]:15.4f} {result["statistical"]:13.4f}')

    print()
    print('  **The worst case is flat in spring count and only the statistical case improves.**')
    print('  That is not what this comparison was written expecting. Half the springs at the top')
    print('  of tolerance and half at the bottom produce the same net moment whether there are')
    print('  four of them or forty, so the bound does not move. The root-sum-square case falls as')
    print('  one over the root of the count, from 0.198 to 0.081 degrees per second.')
    print()
    print('  So adding springs buys a better expected tipoff and no better bound. A programme that')
    print('  needs the bound has to **match the springs in opposing pairs** rather than multiply')
    print('  them, and springs from one production lot are correlated anyway, which is exactly the')
    print('  case where the statistical argument is weakest.')

    return {'system': system, 'velocity': velocity, 'tipoff': tipoff,
            'recontact': recontact, 'counts': counts}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the latch pays quadratically -- #
# ------------------------------------------------------------------------------------------------ #

def reportDeployment(case: dict) -> dict:

    banner('4. THE LATCH PAYS QUADRATICALLY FOR THE SPRING')

    panel = buildDeployable(case)

    impact = panel.latchImpact()

    print(f'  The panel deploys {case["deployable"]["travelDegrees"]:.0f} degrees in '
          f'{impact["deploymentTime"]:.2f} s and arrives at')
    print(f'  {np.degrees(impact["arrivalRate"]):.1f} degrees per second, carrying '
          f'{impact["impactEnergy"]:.2f} J into the latch.')

    limit = case['deployable']['latchEnergyLimit']

    damper = panel.sizeDamper(energyLimit = limit)

    print()
    print(f'  Holding the latch to {limit:.1f} J needs a damper of '
          f'{damper["required"]:.2f} N m s per radian,')
    print(f'  which is a {damper["energyReduction"]:.0%} reduction in impact energy.')

    panel.dampingCoefficient = damper['required']

    damped = panel.latchImpact()

    print(f'  The deployment then takes {damped["deploymentTime"]:.2f} s rather than '
          f'{impact["deploymentTime"]:.2f}.')

    print()
    for finding in damped['findings']:
        print(f'  - {finding}')

    print()
    print('  And the torsion spring arrives weakest, because it unwinds as it deploys. A spring')
    print('  sized on its stowed torque rather than its torque at the end of travel is the usual')
    print('  cause of a deployable that stops halfway:')

    stalling = DeploymentKinematics()
    stalling.setInputs({'springTorque':    2.0,
                        'springRate':      2.0,
                        'inertia':         case['deployable']['inertia'],
                        'travel':          np.radians(case['deployable']['travelDegrees']),
                        'resistingTorque': 1.2})

    try:
        stalling.deploy()
        print('    the stall check did not fire, which is a defect')
    except MechanismsAndSeparationError as error:
        detail = [line for line in str(error).splitlines()
                  if line.startswith('The deployable stalls')]
        print(f'    MechanismsAndSeparationError: {detail[0][:88]}')

    return {'panel': panel, 'undamped': impact, 'damper': damper, 'damped': damped}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: test evidence is what buys margin -- #
# ------------------------------------------------------------------------------------------------ #

def reportMargins(case: dict) -> dict:

    banner('5. TEST EVIDENCE IS WHAT BUYS MARGIN')

    entry = case['actuator']

    actuator = MechanismActuator()
    actuator.setInputs({'availableTorque': entry['availableTorque'],
                        'fixedTorques':    entry['fixedTorques'],
                        'variableTorques': entry['variableTorques']})

    comparison = actuator.compareDataSources()

    print('  NASA-STD-5017B equation 4-1, the same hardware at every level of evidence:')
    print()
    print(f'    {"data source":28s} {"FSv":>6s} {"FSf":>6s} {"margin":>9s}   passes')

    for name, result in comparison['results'].items():
        print(f'    {name:28s} {result["factors"]["variable"]:6.2f} '
              f'{result["factors"]["fixed"]:6.2f} {result["margin"]:+9.3f}   '
              f'{"yes" if result["margin"] >= REQUIRED_TORQUE_MARGIN else "no"}')

    print()
    print('  Not one design change between the top row and the bottom. The factors fall from 3.00')
    print('  to 2.00 on variable torques because the uncertainty they cover has been retired by')
    print('  measurement, and the standard is explicit that the analysis factors are not a')
    print('  no-test option: verifying margin by test is required regardless.')

    print()
    print(f'  **The requirement is a margin at or above {REQUIRED_TORQUE_MARGIN:.0f}, not one.** '
          f'The reserve lives inside those')
    print('  factors rather than on top of the result. A search summary of this same standard')
    print('  reported the threshold as 1.0, and reading the standard rather than a summary of it')
    print('  is the reason this library carries the factors as data with the source attached.')

    return {'actuator': actuator, 'comparison': comparison}

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(band: dict, separation: dict, deployment: dict, margins: dict) -> None:

    banner('SUMMARY: WHAT A SINGLE-SHOT DEVICE ACTUALLY DEPENDS ON')

    print()
    print(f'    {"question":44s} {"answer":>16s}')
    print(f'    {"preload lost to nine months of storage":44s} '
          f'{band["relaxation"]["totalLoss"]:15.1%}')
    print(f'    {"tipoff, deterministic worst case":44s} '
          f'{separation["tipoff"]["rateDegrees"]:11.3f} deg/s')
    print(f'    {"tipoff, statistical at 4 springs":44s} '
          f'{separation["counts"]["results"][4]["statistical"]:11.4f} deg/s')
    print(f'    {"tipoff, statistical at 12 springs":44s} '
          f'{separation["counts"]["results"][12]["statistical"]:11.4f} deg/s')
    print(f'    {"latch energy undamped":44s} '
          f'{deployment["undamped"]["impactEnergy"]:14.2f} J')
    print(f'    {"latch energy damped":44s} '
          f'{deployment["damped"]["impactEnergy"]:14.2f} J')
    print(f'    {"actuator margin from analysis":44s} '
          f'{margins["comparison"]["results"]["theory or analysis"]["margin"]:+16.3f}')
    print(f'    {"actuator margin from flight-article test":44s} '
          f'{margins["comparison"]["results"]["acceptance test, extremes"]["margin"]:+16.3f}')

    print()
    print('  Three of those eight are bought with test evidence rather than design, and a fourth,')
    print('  the storage relaxation, is bought with schedule discipline. That is the shape of this')
    print('  domain: **the hardware is simple and the confidence is expensive.**')
    print()
    print('  What this domain does not compute, and says so rather than approximating:')
    print()
    print('    The shock. Pyroshock prediction is test-derived and an analytic shock response')
    print('    spectrum would carry more authority than it earns. What is computed is the released')
    print('    energy, which compares designs against each other and against a measured signature.')
    print()
    print('    Tribology. Vacuum lubrication, cold welding and dry film life are material and')
    print('    process questions rather than mechanism arithmetic, and they are documented rather')
    print('    than modelled.')
    print()
    print('    Deployment in one g. The offload rig is usually the hardest part of testing a')
    print('    deployable and none of it is here.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    band       = reportClampBand(case)
    reportInitiator(case)
    separation = reportSeparation(case)
    deployment = reportDeployment(case)
    margins    = reportMargins(case)

    summarise(band, separation, deployment, margins)

if __name__ == '__main__':
    main()
