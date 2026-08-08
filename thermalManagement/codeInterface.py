
# -- thermalManagement worked example -- #

'''

An ascent heat pulse followed all the way through: from the aeroheating environment, into the
thermal protection that stops it, through the structure behind, and into the avionics that peak
long after the vehicle has left the atmosphere.

The chain is the point. Three domains own consecutive links of it and none of them owns the whole
thing, which is exactly how a soakback failure gets missed:

    environmentsAndLoads    supplies the aeroheating flux and duration
    thermalManagement       sizes the protection and solves the transient
    fluidSystems            owns the avionics that end up hot

The heating lasts 140 seconds. The avionics reach their maximum roughly fifteen minutes later,
with the vehicle in vacuum and nothing heating anything. A thermal analysis that stops when the
heat pulse stops reports a number that is comfortably inside limits and misses the one that is not.

The example then runs the same avionics on orbit, where the problem inverts: the hot case wants a
larger radiator and the cold case pays for it in heater power, continuously, for the mission.

Run:
    python thermalManagement/codeInterface.py

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'thermalManagementLibrary'))

from thermalUtils import STEFAN_BOLTZMANN, thermalDiffusivity, thermalPenetrationDepth
from ThermalNetwork import ThermalNetwork
from AblativeTPS import AblativeTPS
from Radiator import Radiator
from ThermalControl import ThermalControl

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'thermalManagementLibrary', 'assets',
                     'ascentToOrbitThermalExample.json')

SUTTON_GRAVES_CONSTANT = 1.7415e-4    # [SI], the same constant environmentsAndLoads uses

def banner(title: str) -> None:

    print()
    print('=' * 96)
    print(f'  {title}')
    print('=' * 96)

def loadCase() -> dict:

    with open(ASSET, 'r', encoding = 'utf-8') as handle:
        return json.load(handle)

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the environment -- #
# ------------------------------------------------------------------------------------------------ #

def reportEnvironment(case: dict) -> dict:

    banner('1. THE AEROHEATING ENVIRONMENT, FROM environmentsAndLoads')

    inherited = case['inherited']

    flux = (SUTTON_GRAVES_CONSTANT
            * np.sqrt(inherited['ascentDensity'] / inherited['noseRadius'])
            * inherited['ascentVelocity'] ** 3)

    load = flux * inherited['pulseDuration']

    print(f'  Linked case      : {case["linkedCase"]}')
    print(f'  Velocity         : {inherited["ascentVelocity"]:.0f} m/s')
    print(f'  Density          : {inherited["ascentDensity"]:.2e} kg/m^3')
    print(f'  Nose radius      : {inherited["noseRadius"]:.2f} m')
    print()
    print(f'  Stagnation flux  : {flux / 1.0e6:.3f} MW/m^2')
    print(f'  Pulse duration   : {inherited["pulseDuration"]:.0f} s')
    print(f'  Integrated load  : {load / 1.0e6:.1f} MJ/m^2')
    print()
    print('  Heating goes as velocity cubed and the square root of density, so this peaks well')
    print('  above peak dynamic pressure. Sizing protection at max-Q is the wrong condition.')

    return {'heatFlux': flux, 'heatLoad': load,
            'duration': inherited['pulseDuration']}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the protection -- #
# ------------------------------------------------------------------------------------------------ #

def sizeProtection(case: dict, environment: dict) -> dict:

    banner('2. SIZING THE THERMAL PROTECTION')

    protection = case['protection']

    shield = AblativeTPS()
    shield.setInputs({'material':           protection['material'],
                      'peakHeatFlux':       environment['heatFlux'],
                      'heatLoad':           environment['heatLoad'],
                      'pulseDuration':      environment['duration'],
                      'backfaceLimit':      protection['backfaceLimit'],
                      'initialTemperature': protection['initialTemperature'],
                      'thicknessMargin':    protection['thicknessMargin']})

    flux   = shield.calculateNetHeatFlux()
    sizing = shield.sizeThickness()

    print(f'  Material         : {protection["material"]}')
    print(f'  Ablating         : {flux["isAblating"]}')
    print(f'  Surface          : {flux["surfaceTemperature"]:.0f} K '
          f'(equilibrium {flux["equilibriumTemperature"]:.0f} K, '
          f'ablation {flux["ablationTemperature"]:.0f} K)')
    print(f'  Net flux         : {flux["netFlux"] / 1.0e6:.3f} MW/m^2')
    print()
    print(f'  Recession        : {sizing["recessionDepth"] * 1000.0:6.2f} mm')
    print(f'  Insulation       : {sizing["insulatingDepth"] * 1000.0:6.2f} mm')
    print(f'  Total thickness  : {sizing["totalThickness"] * 1000.0:6.2f} mm')
    print(f'  Areal mass       : {sizing["arealMass"]:6.2f} kg/m^2')
    print(f'  Limited by       : {sizing["limitedBy"]}')
    print()
    for finding in sizing['findings']:
        print(f'    - {finding}')

    comparison = shield.compareMaterials()
    print()
    print('  Against the alternatives:')
    print('    material            thickness    areal mass   limited by')
    for name, entry in comparison['materials'].items():
        marker = '  <-' if name == protection['material'] else ''
        print(f'    {name:18s} {entry["thickness"] * 1000.0:7.2f} mm  '
              f'{entry["arealMass"]:8.2f} kg/m^2  {entry["limitedBy"]}{marker}')

    shieldMass = sizing['arealMass'] * protection['protectedArea']
    print()
    print(f'  Over {protection["protectedArea"]:.2f} m^2 that is {shieldMass:.2f} kg of shield.')

    return {'shield': shield, 'sizing': sizing, 'flux': flux, 'mass': shieldMass}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the transient, run too short -- #
# ------------------------------------------------------------------------------------------------ #

def buildNetwork(case: dict, endTime: float) -> ThermalNetwork:

    '''
    The thermal path from the TPS backface through the bulkhead into the avionics.
    '''

    structure = case['structure']

    network = ThermalNetwork()
    network.setInputs({'timeStep': case['transient']['timeStep'], 'endTime': endTime})

    network.addNodeFromMass('tps backface',
                            mass = 4.0, specificHeat = 1900.0,
                            temperature = case['protection']['initialTemperature'])
    network.addNodeFromMass('bulkhead',
                            mass = structure['bulkheadMass'],
                            specificHeat = structure['bulkheadSpecificHeat'],
                            temperature = case['protection']['initialTemperature'])
    network.addNodeFromMass('avionics',
                            mass = structure['avionicsMass'],
                            specificHeat = structure['avionicsSpecificHeat'],
                            temperature = case['protection']['initialTemperature'],
                            heatLoad = structure['avionicsDissipation'])
    network.addNode('sink', temperature = structure['sinkTemperature'], boundary = True)

    network.addContact('tps backface', 'bulkhead',
                       area = structure['bulkheadContactArea'],
                       jointType = structure['bulkheadJoint'])
    network.addContact('bulkhead', 'avionics',
                       area = structure['avionicsContactArea'],
                       jointType = structure['avionicsJoint'])
    network.addRadiation('bulkhead', 'sink',
                         emissivity = structure['radiatingEmissivity'],
                         area = structure['radiatingArea'])

    return network

def runTransient(case: dict, environment: dict, protection: dict) -> dict:

    banner('3. THE TRANSIENT, AND WHY THE RUN LENGTH DECIDES THE ANSWER')

    structure = case['structure']
    duration  = environment['duration']

    # the heat arriving at the TPS backface, taken as the conducted fraction of the surface load
    backfaceFlux = protection['flux']['netFlux'] * 0.05 + 4.0e4
    inputPower   = backfaceFlux * case['protection']['protectedArea']

    schedule = {'tps backface': lambda t: inputPower if t <= duration else 0.0}

    results = {}

    for label, endTime, why in (
            ('short', case['transient']['shortRun'], 'stopped when the heating stops'),
            ('long',  case['transient']['longRun'],  'run until every node turns over')):

        network = buildNetwork(case, endTime)
        result  = network.solveTransient(heatLoadSchedule = schedule)
        results[label] = {'network': network, 'result': result}

        print()
        print(f'  Run to {endTime:.0f} s, {why}. Truncated = {result["truncated"]}')
        print('    node             peak [K]   at [s]   limit [K]')
        for name, peak in result['peaks'].items():
            limit = (f'{structure["avionicsLimit"]:.1f}' if name == 'avionics' else '')
            print(f'    {name:14s} {peak["peakTemperature"]:9.1f} {peak["peakTime"]:8.0f}   '
                  f'{limit}')

        if result['truncated']:
            print(f'    still rising: {result["stillRising"]}')

    shortPeak = results['short']['result']['peaks']['avionics']
    longPeak  = results['long']['result']['peaks']['avionics']
    limit     = structure['avionicsLimit']

    print()
    print(f'  The short run reports the avionics at {shortPeak["peakTemperature"]:.1f} K and the '
          f'long run at {longPeak["peakTemperature"]:.1f} K,')
    print(f'  against a {limit:.1f} K limit.')

    if shortPeak['peakTemperature'] <= limit < longPeak['peakTemperature']:
        print()
        print('  The short run passes and the long run fails, on the same model, the same')
        print('  hardware and the same heat pulse. The only difference is when the analyst')
        print(f'  stopped integrating. The heating ended at {duration:.0f} s and the avionics '
              f'peaked at')
        print(f'  {longPeak["peakTime"]:.0f} s, in vacuum, with nothing heating anything.')
        print()
        print('  The short run also declared itself truncated, which is the only reason the')
        print('  mistake is visible at all. A solver that reports a maximum without checking')
        print('  whether the node was still rising reports this failure as a pass.')

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: soakback -- #
# ------------------------------------------------------------------------------------------------ #

def analyseSoakback(case: dict, environment: dict, transient: dict) -> None:

    banner('4. SOAKBACK')

    network = transient['long']['network']

    soakback = network.findSoakback(eventEndTime = environment['duration'])

    print('    node             during [K]   after [K]   peak at [s]   soaks back')
    for name, entry in soakback['nodes'].items():
        print(f'    {name:14s} {entry["peakDuringEvent"]:10.1f} '
              f'{entry["peakAfterEvent"]:11.1f} {entry["peakTime"]:13.0f}   '
              f'{entry["soaksBack"]}')

    print()
    for finding in soakback['findings']:
        print(f'    - {finding}')

    sensitivity = network.resistanceSensitivity()
    print()
    print('  Where the uncertainty lives:')
    for name, entry in sorted(sensitivity['shares'].items(),
                              key = lambda item: -item[1]['fraction']):
        print(f'    {name:28s} {entry["fraction"] * 100.0:5.1f} %   {entry["note"]}')
    print()
    for finding in sensitivity['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: on orbit -- #
# ------------------------------------------------------------------------------------------------ #

def onOrbit(case: dict) -> None:

    banner('5. THE SAME AVIONICS ON ORBIT')

    orbit     = case['onOrbit']
    structure = case['structure']

    radiator = Radiator()
    radiator.setInputs({'heatLoad':             structure['avionicsDissipation'],
                        'radiatingTemperature': orbit['radiatingTemperature'],
                        'sinkTemperature':      structure['sinkTemperature'],
                        'surfaceFinish':        orbit['surfaceFinish']})

    sizing = radiator.sizeArea()

    print(f'  Rejecting {structure["avionicsDissipation"]:.0f} W at '
          f'{orbit["radiatingTemperature"]:.0f} K to a {structure["sinkTemperature"]:.0f} K sink')
    print(f'    net flux         {sizing["netFlux"]:8.1f} W/m^2')
    print(f'    area             {sizing["area"]:8.3f} m^2')
    print()
    for finding in sizing['findings']:
        print(f'    - {finding}')

    comparison = radiator.compareSinks()
    print()
    print('  Against the available sinks:')
    for name, entry in comparison['sinks'].items():
        area = f'{entry["area"]:.3f} m^2' if entry['usable'] else 'unusable'
        print(f'    {name:18s} {entry["sinkTemperature"]:6.0f} K  {area}')

    print()
    control = ThermalControl()
    control.setInputs({'component':           orbit['component'],
                       'coldCaseLoss':        orbit['coldCaseLoss'],
                       'hotCaseTemperature':  orbit['radiatingTemperature'],
                       'internalDissipation': 0.0,
                       'thermalMass':         structure['avionicsMass']
                                              * structure['avionicsSpecificHeat'],
                       'missionDuration':     orbit['missionDuration'],
                       'deadband':            orbit['deadband']})

    heater = control.sizeHeater()
    duty   = control.calculateDutyCycle()
    hot    = control.checkHotCase()

    print(f'  The cold case needs {heater["requiredPower"]:.1f} W, sized to '
          f'{heater["sizedPower"]:.1f} W')
    print(f'    duty cycle       {duty["dutyCycle"] * 100.0:8.1f} %')
    if 'cycles' in duty:
        print(f'    thermostat cycles{duty["cycles"]:8.0f}')
    print(f'    hot case margin  {hot["margin"]:+8.1f} K')
    print()
    for finding in (heater['findings'] + duty.get('findings', []) + hot['findings']):
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(case: dict, environment: dict, protection: dict, transient: dict) -> None:

    banner('SUMMARY: THE CHAIN, AND WHERE IT BREAKS')

    shortPeak = transient['short']['result']['peaks']['avionics']['peakTemperature']
    longPeak  = transient['long']['result']['peaks']['avionics']['peakTemperature']
    peakTime  = transient['long']['result']['peaks']['avionics']['peakTime']
    limit     = case['structure']['avionicsLimit']

    print()
    print('    link                          owner                    value')
    print(f'    aeroheating flux              environmentsAndLoads     '
          f'{environment["heatFlux"] / 1.0e6:.3f} MW/m^2')
    print(f'    protection thickness          thermalManagement        '
          f'{protection["sizing"]["totalThickness"] * 1000.0:.2f} mm')
    print(f'    avionics peak, short run      thermalManagement        {shortPeak:.1f} K')
    print(f'    avionics peak, long run       thermalManagement        {longPeak:.1f} K')
    print(f'    avionics limit                fluidSystems             {limit:.1f} K')

    print()
    print(f'  The heating lasts {environment["duration"]:.0f} s. The avionics peak at '
          f'{peakTime:.0f} s,')
    print(f'  {peakTime / environment["duration"]:.0f} times the event duration, in vacuum, with '
          f'nothing heating anything.')
    print()
    print('  No single domain owns that. environmentsAndLoads owns the flux and stops at the')
    print('  surface. thermalManagement owns the protection and can legitimately declare success')
    print('  at the backface. fluidSystems owns the avionics and receives a temperature. The')
    print('  failure lives in the handover, which is why the chain is worth running end to end')
    print('  rather than domain by domain.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    environment = reportEnvironment(case)
    protection  = sizeProtection(case, environment)
    transient   = runTransient(case, environment, protection)

    analyseSoakback(case, environment, transient)
    onOrbit(case)
    summarise(case, environment, protection, transient)

if __name__ == '__main__':
    main()
