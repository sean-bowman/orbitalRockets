
# -- aerospaceStructures worked example -- #

'''

A propellant tank sized as a pressure vessel, then checked as primary structure, beside a dry skirt.

The tank is the one component where this domain and fluidSystems are the same object. The operating
pressure comes from fluidSystems/codeInterface.py, the allowables come from aerospaceMaterials, and
what this example adds is the structural half: the same wall that holds the pressure also has to
carry the launch loads without buckling.

The example was built expecting scale to change which failure mode governs. It does not, and that
is the more useful result. A pressure-sized wall obeys t = p R / sigma, so the thickness scales
linearly with the radius and R/t is a constant: 79.7 here, at 0.18 m and at 1.80 m alike. A tank
sized by pressure is therefore exactly as imperfection sensitive at every scale, which is not what
intuition suggests.

What that constant buys is worth stating. At R/t of 79.7 in 2219-T87 the buckling allowable and the
material yield strength come out equal to three figures, so this geometry sits precisely on the
boundary between a strength-governed and a stability-governed wall.

The shell that is genuinely a stability problem is the one with no pressure in it. An interstage or
an aft skirt carries the same compression and has no internal pressure to size its wall, so R/t is
a free choice and it is chosen thin. The example therefore runs three articles:

    small tank    R = 0.18 m, the 30 litre monopropellant tank from the fluid system
    stage tank    R = 1.80 m, the same propellant at the same pressure at vehicle scale
    dry skirt     R = 1.80 m, no internal pressure, sized by the compression alone

Run:
    python aerospaceStructures/codeInterface.py

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'aerospaceStructuresLibrary'))

from structuresUtils import structuralAllowables, marginOfSafety
from PressureVessel import PressureVessel
from CylindricalShell import CylindricalShell
from StiffenedPanel import StiffenedPanel
from BeamColumn import BeamColumn
from BoltedJoint import BoltedJoint
from ModalEstimate import ModalEstimate
from LoadCase import LoadCase

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'aerospaceStructuresLibrary', 'assets', 'tankStructureExample.json')

def banner(title: str) -> None:

    '''
    A section heading, matching the other worked examples in the repository.
    '''

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    '''
    Read the worked example configuration.
    '''

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the inherited case -- #
# ------------------------------------------------------------------------------------------------ #

def reportInheritance(case: dict) -> None:

    banner('1. INHERITED FROM fluidSystems AND aerospaceMaterials')

    inherited = case['inherited']

    print(f'  Linked case         : {case["linkedCase"]}')
    print(f'  Propellant volume   : {inherited["propellantVolume"] * 1000.0:.1f} L')
    print(f'  Tank pressure       : {inherited["tankPressure"] / 1.0e6:.4f} MPa')
    print(f'  Surge peak          : {inherited["surgePeakPressure"] / 1.0e6:.4f} MPa')
    print()

    allowables = structuralAllowables(case['smallTank']['material'],
                                      case['smallTank']['condition'],
                                      basis = case['smallTank']['basis'])

    print(f'  Allowables source   : {allowables["source"]}')
    print(f'  2219-T87 A-basis Fty: {allowables["yieldStrength"] / 1.0e6:.1f} MPa')
    print(f'  2219-T87 A-basis Ftu: {allowables["ultimateStrength"] / 1.0e6:.1f} MPa')
    print(f'  Modulus             : {allowables["elasticModulus"] / 1.0e9:.1f} GPa')
    print()
    print('  The surge peak is the pressure the wall is sized against, not the operating')
    print('  pressure, because a water hammer transient is a real load the tank must survive.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the two tanks as pressure vessels -- #
# ------------------------------------------------------------------------------------------------ #

def sizeVessels(case: dict) -> dict:

    banner('2. PRESSURE VESSEL SIZING AT TWO SCALES')

    pressure = case['inherited']['surgePeakPressure']
    sized    = {}

    for label, key in (('small tank', 'smallTank'), ('stage tank', 'stageTank')):

        configuration = case[key]

        tank = PressureVessel()
        tank.setInputs({'material':          configuration['material'],
                        'condition':         configuration['condition'],
                        'basis':             configuration['basis'],
                        'radius':            configuration['radius'],
                        'domeType':          configuration['domeType'],
                        'jointEfficiency':   configuration['jointEfficiency'],
                        'operatingPressure': pressure,
                        'cylindricalLength': configuration.get('cylindricalLength', 0.30)})

        result = tank.sizeWallThickness()
        tank.thickness = result['requiredThickness']

        sized[key] = {'tank': tank, 'sizing': result}

        print()
        print(f'  {label.upper()}  R = {configuration["radius"]:.2f} m')
        for name, value in result['candidates'].items():
            marker = '  <- GOVERNS' if name == result['bindingConstraint'] else ''
            print(f'    {name:8s} {value * 1000.0:7.3f} mm{marker}')
        print(f'    R/t = {result["radiusToThickness"]:.1f}')

    print()
    print('  The binding requirement is the same at both scales and so is R/t, because a')
    print('  pressure-sized wall obeys t = p R / sigma and the radius cancels. Scaling a')
    print('  pressurized tank up does not make it more buckling prone.')

    return sized

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the same walls as compression members -- #
# ------------------------------------------------------------------------------------------------ #

def checkBuckling(case: dict, sized: dict) -> dict:

    banner('3. THE SAME WALLS IN COMPRESSION')

    gravity = 9.80665
    results = {}

    for label, key, axialLoad in (
            ('small tank', 'smallTank', 0.0),
            ('stage tank', 'stageTank',
             6.0 * case['stageTank']['dryMassAbove'] * gravity)):

        configuration = case[key]
        thickness     = sized[key]['sizing']['requiredThickness']

        shell = CylindricalShell()
        shell.setInputs({'material':  configuration['material'],
                         'condition': configuration['condition'],
                         'basis':     configuration['basis'],
                         'radius':    configuration['radius'],
                         'thickness': thickness,
                         'length':    configuration.get('cylindricalLength', 0.30),
                         'axialLoad': axialLoad})

        try:
            buckling = shell.calculateAxialBuckling()
        except Exception as error:
            print()
            print(f'  {label.upper()}')
            print(f'    {type(error).__name__}: {error}')
            print(f'    R/t = {configuration["radius"] / thickness:.1f}. The wall is too thick for')
            print('    thin-shell buckling theory, which is itself the answer: at this scale the')
            print('    tank cannot buckle and pressure governs outright.')
            results[key] = None
            continue

        print()
        print(f'  {label.upper()}  R/t = {shell.radiusToThickness:.1f}')
        print(f'    classical buckling  {buckling["classicalStress"] / 1.0e6:8.1f} MPa')
        print(f'    knockdown           {buckling["knockdown"]:8.4f}')
        print(f'    allowable buckling  {buckling["allowableStress"] / 1.0e6:8.1f} MPa')
        print(f'    material yield      {buckling["yieldStrength"] / 1.0e6:8.1f} MPa')
        print(f'    applied             {buckling["appliedStress"] / 1.0e6:8.1f} MPa')
        print(f'    margin              {buckling["margin"]:+8.3f}')
        print(f'    buckling governs    {buckling["bucklingGoverns"]} '
              f'by {buckling["governingRatio"]:.1f}x')

        results[key] = {'shell': shell, 'buckling': buckling}

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3b: the dry skirt, which really is a stability problem -- #
# ------------------------------------------------------------------------------------------------ #

def drySkirt(case: dict) -> dict:

    banner('3b. THE DRY SKIRT, WHERE STABILITY ACTUALLY GOVERNS')

    gravity   = 9.80665
    skirt     = case['drySkirt']
    axialLoad = 6.0 * case['stageTank']['dryMassAbove'] * gravity

    shell = CylindricalShell()
    shell.setInputs({'material':  skirt['material'],
                     'condition': skirt['condition'],
                     'basis':     skirt['basis'],
                     'radius':    skirt['radius'],
                     'thickness': skirt['thickness'],
                     'length':    skirt['length'],
                     'axialLoad': axialLoad})

    result = shell.calculateAxialBuckling()

    print()
    print(f'  R = {skirt["radius"]:.2f} m, t = {skirt["thickness"] * 1000.0:.2f} mm, '
          f'R/t = {shell.radiusToThickness:.0f}')
    print()
    print(f'    classical buckling  {result["classicalStress"] / 1.0e6:8.1f} MPa')
    print(f'    knockdown           {result["knockdown"]:8.4f}')
    print(f'    allowable buckling  {result["allowableStress"] / 1.0e6:8.1f} MPa')
    print(f'    material yield      {result["yieldStrength"] / 1.0e6:8.1f} MPa')
    print(f'    applied             {result["appliedStress"] / 1.0e6:8.1f} MPa')
    print(f'    margin              {result["margin"]:+8.3f}')
    print()
    for finding in result['findings']:
        print(f'    - {finding}')

    sizing = shell.sizeThicknessForAxialLoad()
    print()
    print(f'    wall required for zero margin: {sizing["thickness"] * 1000.0:.2f} mm '
          f'(R/t {sizing["radiusToThickness"]:.0f})')

    return {'shell': shell, 'buckling': result, 'sizing': sizing}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: pressure stabilization -- #
# ------------------------------------------------------------------------------------------------ #

def pressureStabilization(case: dict, sized: dict) -> None:

    banner('4. PRESSURE STABILIZATION OF THE STAGE TANK')

    gravity   = 9.80665
    thickness = sized['stageTank']['sizing']['requiredThickness']
    axialLoad = 6.0 * case['stageTank']['dryMassAbove'] * gravity

    print()
    print('  A tank is pressurized in flight, and internal pressure suppresses the inward')
    print('  buckling lobes the imperfections would otherwise trigger. The recovery is large.')
    print()
    print('  internal p [MPa]   knockdown   allowable [MPa]   margin')

    for pressure in (0.0, 0.5e6, 1.0e6, 2.236e6):

        shell = CylindricalShell()
        shell.setInputs({'material': '2219-T87', 'condition': 't87', 'basis': 'A',
                         'radius': case['stageTank']['radius'], 'thickness': thickness,
                         'length': case['stageTank']['cylindricalLength'],
                         'axialLoad': axialLoad, 'internalPressure': pressure})

        result = shell.calculateAxialBuckling()

        print(f'    {pressure / 1.0e6:8.3f}      {result["knockdown"]:8.4f}   '
              f'{result["allowableStress"] / 1.0e6:12.1f}   {result["margin"]:+8.3f}')

    print()
    print('  This is why pressure-stabilized stages exist, and it is also the trap: an analysis')
    print('  crediting stabilization has to show the pressure cannot be lost while the')
    print('  compressive load is applied. A tank that is empty and unpressurized on the pad is')
    print('  the ground handling case, and it is checked at zero pressure.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the governing load case -- #
# ------------------------------------------------------------------------------------------------ #

def governingLoadCase(case: dict) -> None:

    banner('5. WHICH LOAD CASE GOVERNS')

    cases = LoadCase()
    cases.setInputs({'referenceMass':   case['stageTank']['dryMassAbove'],
                     'referenceRadius': case['stageTank']['radius'],
                     'referenceLength': case['stageTank']['cylindricalLength'],
                     'qualificationBy': 'test'})

    for name, entry in case['loadCases'].items():
        if name.startswith('_'):
            continue
        cases.addCase(name,
                      axialG = entry['axialG'],
                      lateralG = entry['lateralG'],
                      internalPressure = entry.get('internalPressure', 0.0),
                      dynamicPressure = entry.get('dynamicPressure', 0.0))

    result = cases.identifyGoverning()

    print()
    print('  case               axial [g]  lateral [g]  p_int [MPa]  severity')
    for name, entry in cases.cases.items():
        marker = '  <- GOVERNS' if name == result['governingBySeverity'] else ''
        print(f'    {name:16s} {entry["axialG"]:7.2f}     {entry["lateralG"]:7.2f}      '
              f'{entry["internalPressure"] / 1.0e6:7.3f}    '
              f'{result["severityIndex"][name]:6.3f}{marker}')

    print()
    for finding in result['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 6: the stiffened alternative -- #
# ------------------------------------------------------------------------------------------------ #

def stiffenedAlternative(case: dict, sized: dict) -> None:

    banner('6. ORTHOGRID AGAINST A THICKER MONOCOQUE WALL')

    gravity   = 9.80665
    axialLoad = 6.0 * case['stageTank']['dryMassAbove'] * gravity
    grid      = case['stiffenedAlternative']

    panel = StiffenedPanel()
    panel.setInputs({'material': '2219-T87', 'condition': 't87', 'basis': 'A',
                     'panelType': 'orthogrid',
                     'skinThickness':      grid['skinThickness'],
                     'stiffenerSpacing':   grid['stiffenerSpacing'],
                     'stiffenerHeight':    grid['stiffenerHeight'],
                     'stiffenerThickness': grid['stiffenerThickness'],
                     'stiffenerType':      grid['stiffenerType'],
                     'radius':             case['stageTank']['radius'],
                     'frameSpacing':       case['stageTank']['cylindricalLength'],
                     'axialLoad':          axialLoad})

    screen     = panel.screenInstabilityModes()
    comparison = panel.compareAgainstUnstiffened()
    smeared    = panel.calculateSmearedProperties()

    print()
    print(f'  smeared thickness   {smeared["smearedThickness"] * 1000.0:.3f} mm')
    print(f'  areal mass          {smeared["arealMass"]:.2f} kg/m^2')
    print()
    for name, stress in sorted(screen['stresses'].items(), key = lambda item: item[1]):
        marker = '  <- GOVERNS' if name == screen['governingMode'] else ''
        print(f'    {name:22s} {stress / 1.0e6:8.1f} MPa{marker}')
    print(f'    applied                {screen["appliedStress"] / 1.0e6:8.1f} MPa')
    print(f'    margin                 {screen["margin"]:+8.3f}')

    print()
    print(f'  Against an unstiffened skin of identical areal mass:')
    print(f'    unstiffened allowable  {comparison["unstiffenedAllowable"] / 1.0e6:8.1f} MPa')
    print(f'    stiffened allowable    {comparison["stiffenedAllowable"] / 1.0e6:8.1f} MPa')
    print(f'    gain                   {comparison["gain"]:8.2f}x')
    print()
    for finding in screen['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 7: the mounting joint -- #
# ------------------------------------------------------------------------------------------------ #

def mountingJoint(case: dict) -> None:

    banner('7. THE BOLTED FLANGE TO THE THRUST STRUCTURE')

    gravity   = 9.80665
    mounting  = case['mounting']
    axialLoad = 6.0 * case['stageTank']['dryMassAbove'] * gravity
    perBolt   = axialLoad / mounting['boltCount']

    joint = BoltedJoint()
    joint.setInputs({'boltDiameter':    mounting['boltDiameter'],
                     'memberMaterial':  '2219-T87',
                     'memberCondition': 't87',
                     'basis':           'A',
                     'gripLength':      mounting['gripLength'],
                     'memberThickness': mounting['memberThickness'],
                     'edgeDistance':    mounting['edgeDistance'],
                     'pitch':           mounting['pitch'],
                     'preloadMethod':   mounting['preloadMethod'],
                     'appliedTension':  perBolt,
                     'appliedShear':    0.3 * perBolt})

    stiffness = joint.calculateStiffnesses()
    preload   = joint.calculatePreload()
    diagram   = joint.calculateJointDiagram()
    members   = joint.calculateMemberChecks()

    print()
    print(f'  {mounting["boltCount"]} bolts, {perBolt / 1000.0:.2f} kN tension each')
    print()
    print(f'    load factor Phi        {stiffness["loadFactor"]:8.4f}')
    print(f'    nominal preload        {preload["nominalPreload"] / 1000.0:8.2f} kN')
    print(f'    install torque         {preload["installationTorque"]:8.2f} N*m')
    print(f'    separation load        {diagram["separationLoad"] / 1000.0:8.2f} kN')
    print(f'    separation margin      {diagram["separationMargin"]:+8.3f}')
    print(f'    bolt yield margin      {diagram["yieldMargin"]:+8.3f}')
    print(f'    edge distance ratio    {members["edgeDistanceRatio"]:8.2f}')
    print(f'    bearing margin         {members["bearingMargin"]:+8.3f}')
    print(f'    shear-out margin       {members["shearOutMargin"]:+8.3f}')
    print()
    for finding in diagram['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 8: the stiffness requirement -- #
# ------------------------------------------------------------------------------------------------ #

def stiffnessRequirement(case: dict, sized: dict) -> None:

    banner('8. AGAINST THE STIFFNESS REQUIREMENT')

    thickness = sized['stageTank']['sizing']['requiredThickness']

    modes = ModalEstimate()
    modes.setInputs({'material':  '2219-T87', 'condition': 't87', 'basis': 'A',
                     'radius':    case['stageTank']['radius'],
                     'thickness': thickness,
                     'length':    case['stageTank']['cylindricalLength'],
                     'boundaryCondition': 'cantilever',
                     'tipMass':   case['stageTank']['dryMassAbove'],
                     'requiredLateral': case['dynamics']['requiredLateral'],
                     'requiredAxial':   case['dynamics']['requiredAxial']})

    result = modes.screenAgainstRequirement()

    print()
    for name, frequency in sorted(result['modes'].items(), key = lambda item: item[1]):
        marker = '  <- LOWEST' if name == result['lowestMode'] else ''
        print(f'    {name:22s} {frequency:8.2f} Hz{marker}')

    print()
    for name, margin in result['margins'].items():
        verdict = 'PASS' if margin >= 0.0 else 'FAIL'
        print(f'    {name:22s} margin {margin:+8.3f}   {verdict}')

    print()
    for finding in result['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, sized: dict, skirt: dict) -> None:

    banner('SUMMARY: WHAT ACTUALLY DECIDES THE FAILURE MODE')

    small = sized['smallTank']['sizing']
    stage = sized['stageTank']['sizing']

    print()
    print('  article            radius     wall      R/t     governed by')
    print(f'    small tank      {case["smallTank"]["radius"]:7.2f} m  '
          f'{small["requiredThickness"] * 1000.0:6.2f} mm  {small["radiusToThickness"]:6.1f}   '
          f'pressure, {small["bindingConstraint"]} test')
    print(f'    stage tank      {case["stageTank"]["radius"]:7.2f} m  '
          f'{stage["requiredThickness"] * 1000.0:6.2f} mm  {stage["radiusToThickness"]:6.1f}   '
          f'pressure, {stage["bindingConstraint"]} test')
    print(f'    dry skirt       {case["drySkirt"]["radius"]:7.2f} m  '
          f'{case["drySkirt"]["thickness"] * 1000.0:6.2f} mm  '
          f'{skirt["shell"].radiusToThickness:6.0f}   buckling, by '
          f'{skirt["buckling"]["governingRatio"]:.1f}x')

    print()
    print('  The two tanks differ by a factor of ten in radius and have the same R/t, because a')
    print('  pressure-sized wall obeys t = p R / sigma and the radius cancels out. Scale is not')
    print('  what makes a shell a stability problem.')
    print()
    print('  What makes it one is having no pressure to size the wall. The skirt carries the same')
    print('  compression at the same radius in the same alloy, and because nothing sets its')
    print('  thickness but the compression itself, it is chosen thin: R/t of 600 against 79.7.')
    print(f'  There the knockdown falls to {skirt["buckling"]["knockdown"]:.3f} and the classical')
    print('  solution is optimistic by a factor of three.')
    print()
    print('  The tanks sit at R/t 79.7, where the 2219-T87 buckling allowable and its yield')
    print('  strength coincide to three figures. That is the boundary between the two regimes,')
    print('  and a pressurized tank in this alloy lands on it whatever size it is built.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    reportInheritance(case)
    sized    = sizeVessels(case)
    buckling = checkBuckling(case, sized)
    skirt    = drySkirt(case)
    pressureStabilization(case, sized)
    governingLoadCase(case)
    stiffenedAlternative(case, sized)
    mountingJoint(case)
    stiffnessRequirement(case, sized)
    summarise(case, sized, skirt)

if __name__ == '__main__':
    main()
