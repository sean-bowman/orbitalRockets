
# -- Top-Level Code Interface for the fluidSystems Library -- #

'''

End-to-end worked example: a GHe-pressurized hydrazine monopropellant feed system, 100 N class.

The script walks the whole chain in reverse flow order, because that is how a pressure budget is
actually built: start at the chamber, add every loss going upstream, and arrive at the required tank
pressure. Then size the pressurization system to deliver it, and finally check the transients, the
joints and the leak budget against the result.

    NOZZLE  <-  CATALYST BED  <-  INJECTOR  <-  THRUSTER VALVE  <-  TRIM ORIFICE  <-
    FEED LINE  <-  FILTER  <-  PROPELLANT TANK  <-  CHECK VALVE  <-  REGULATOR  <-  He BOTTLE

Run it with:

    python codeInterface.py

Configuration comes from fluidSystemsLibrary/assets/hydrazineMonopropExample.json. A field left
null means 'not specified'; a literal 0.0 means 'specified as zero', which is not the same thing.

Author: Sean Bowman
Date:   08/04/2026

'''

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fluidSystemsLibrary'))

import numpy as np

from utils import formatReportTable, PA_PER_PSIA, N_PER_LBF
from Orifice import Orifice
from Valve import Valve
from Line import Line
from Fitting import Fitting
from Seal import Seal
from LeakPath import LeakPath
from Weld import Weld
from Insulation import Insulation
from WaterHammer import WaterHammer
from CatalystBed import CatalystBed
from MonopropThruster import MonopropThruster
from Pressurization import Pressurization
from Regulator import Regulator
from CheckValve import CheckValve
from Filter import Filter

os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------------------------------------------------ #
# -- Configuration -- #
# ------------------------------------------------------------------------------------------------ #

configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'fluidSystemsLibrary', 'assets', 'hydrazineMonopropExample.json')

with open(configPath, 'r') as fileHandle:
    config = json.load(fileHandle)

print('=' * 110)
print(f'  fluidSystems worked example: {config["caseName"]}')
print('=' * 110)

stations = []   # (station name, pressure [Pa], note) accumulated going upstream

# ------------------------------------------------------------------------------------------------ #
# -- 1. Catalyst bed and thruster -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[1/9] Catalyst bed and thruster')

bedConfig      = config['catalystBed']
thrusterConfig = config['thruster']

chamberPressure = thrusterConfig['chamberPressure']

# The bed is sized from the thruster mass flow, but the mass flow comes from the thruster, which
# needs c* from the bed. Seed with the propellant table, then re-solve once the bed is sized.
thruster = MonopropThruster()
thruster.setInputs({key: value for key, value in thrusterConfig.items() if value is not None})
thruster.calculatePerformance()

bed = CatalystBed()
bed.setInputs({**bedConfig, 'massFlow': thruster.massFlow, 'chamberPressure': chamberPressure})
bed.calculateDecomposition()
bed.sizeBed()
bed.calculatePressureDrop()
bed.checkColdStart()

# Re-solve the thruster with the real bed chemistry
thruster.catalystBed = bed
thruster.massFlow    = np.nan
thruster.thrust      = thrusterConfig['thrust']
thruster.calculatePerformance()

# The bed geometry depends on the mass flow, so one more pass closes the loop
bed.massFlow = thruster.massFlow
bed.sizeBed()
bed.calculatePressureDrop()

stations.append(('Nozzle throat (chamber)', chamberPressure, f'{thruster.thrust:.1f} N, Isp {thruster.vacuumSpecificImpulse:.1f} s'))

bedInletPressure = chamberPressure + bed.pressureDrop
stations.append(('Catalyst bed inlet', bedInletPressure,
                 f'bed dP {bed.pressureDrop / 1.0e3:.1f} kPa ({bed.pressureDrop / chamberPressure * 100.0:.1f} % of Pc)'))

print(f'      c* = {bed.characteristicVelocity:.1f} m/s, Tc = {bed.chamberTemperature:.0f} K, '
      f'mdot = {thruster.massFlow:.5f} kg/s')
print(f'      bed {bed.bedDiameter * 1.0e3:.2f} mm dia x {bed.bedLength * 1.0e3:.2f} mm, '
      f'{bed.catalystMass * 1.0e3:.1f} g catalyst, dP {bed.pressureDrop / 1.0e3:.1f} kPa')
print(f'      throat {thruster.throatDiameter * 1.0e3:.3f} mm, exit {thruster.exitDiameter * 1.0e3:.2f} mm, '
      f'ignition delay {bed.ignitionDelay * 1.0e3:.2f} ms')

# ------------------------------------------------------------------------------------------------ #
# -- 2. Injector -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[2/9] Injector')

injectorConfig       = config['injector']
injectorPressureDrop = thrusterConfig['injectorPressureDrop'] * chamberPressure
injectorInletPressure = bedInletPressure + injectorPressureDrop

injector = Orifice()
injector.setInputs({'fluid': 'N2H4',
                    'upstreamPressure':    injectorInletPressure,
                    'downstreamPressure':  bedInletPressure,
                    'upstreamTemperature': bedConfig['inletTemperature'],
                    'massFlow':            thruster.massFlow,
                    **injectorConfig})
injector.sizeDiameter()

stations.append(('Injector inlet', injectorInletPressure,
                 f'{injector.numberOfOrifices} x {injector.diameter * 1.0e3:.4f} mm, '
                 f'Cd {injector.dischargeCoefficient:.3f}'))

print(f'      {injector.numberOfOrifices} elements at {injector.diameter * 1.0e3:.4f} mm, '
      f'Cd {injector.dischargeCoefficient:.4f}, Re {injector.reynolds:.3g}')
print(f'      injector dP {injectorPressureDrop / 1.0e3:.1f} kPa, cavitation: {injector.cavitationStatus}')

# ------------------------------------------------------------------------------------------------ #
# -- 3. Thruster valve -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[3/9] Thruster valve')

valveConfig        = config['thrusterValve']
valveOutletPressure = injectorInletPressure
valveInletPressure  = valveOutletPressure + valveConfig['allowablePressureDrop']

thrusterValve = Valve()
thrusterValve.setInputs({'fluid': 'N2H4',
                         'upstreamPressure':    valveInletPressure,
                         'downstreamPressure':  valveOutletPressure,
                         'upstreamTemperature': bedConfig['inletTemperature'],
                         'massFlow':            thruster.massFlow,
                         'valveType':           valveConfig['valveType'],
                         'nominalSize':         valveConfig['nominalSize'],
                         'seatMaterial':        valveConfig['seatMaterial']})
thrusterValve.sizeFlowCoefficient()
thrusterValve.calculateActuationLoad()

stations.append(('Thruster valve inlet', valveInletPressure,
                 f'Cv {thrusterValve.requiredFlowCoefficient:.4f}, '
                 f'actuation {thrusterValve.actuationForce:.0f} N'))

print(f'      required Cv {thrusterValve.requiredFlowCoefficient:.4f}, choked: {thrusterValve.isChoked}, '
      f'cavitation: {thrusterValve.cavitationStatus}')
print(f'      seat load {thrusterValve.seatLoad:.1f} N, unbalance {thrusterValve.unbalanceForce:.1f} N, '
      f'actuation {thrusterValve.actuationForce:.1f} N')

# ------------------------------------------------------------------------------------------------ #
# -- 4. Trim orifice -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[4/9] Trim orifice')

trimConfig          = config['trimOrifice']
trimOutletPressure  = valveInletPressure
trimInletPressure   = trimOutletPressure + trimConfig['allowablePressureDrop']

trimOrifice = Orifice()
trimOrifice.setInputs({'fluid': 'N2H4',
                       'upstreamPressure':    trimInletPressure,
                       'downstreamPressure':  trimOutletPressure,
                       'upstreamTemperature': bedConfig['inletTemperature'],
                       'massFlow':            thruster.massFlow,
                       'orificeType':         trimConfig['orificeType']})
trimOrifice.sizeDiameter()

stations.append(('Trim orifice inlet', trimInletPressure,
                 f'{trimOrifice.diameter * 1.0e3:.4f} mm bore'))

print(f'      {trimOrifice.diameter * 1.0e3:.4f} mm bore, Cd {trimOrifice.dischargeCoefficient:.4f}, '
      f'velocity {trimOrifice.velocity:.2f} m/s')

# ------------------------------------------------------------------------------------------------ #
# -- 5. Feed line and fittings -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[5/9] Feed line')

lineConfig        = config['feedLine']
lineOutletPressure = trimInletPressure

feedLine = Line()
feedLine.setInputs({'fluid': 'N2H4',
                    'massFlow':         thruster.massFlow,
                    'inletTemperature': bedConfig['inletTemperature'],
                    'inletPressure':    lineOutletPressure + lineConfig['allowablePressureDrop'],
                    'designPressure':   4.0e6,
                    **{key: value for key, value in lineConfig.items() if key != 'allowablePressureDrop'},
                    'allowablePressureDrop': lineConfig['allowablePressureDrop']})
feedLine.sizeDiameter()
feedLine.selectStandardTube()
feedLine.calculateWallThickness()
feedLine.calculateMass()

lineInletPressure = lineOutletPressure + feedLine.pressureDrop

stations.append(('Feed line inlet', lineInletPressure,
                 f'{feedLine.selectedTube}, {feedLine.velocity:.2f} m/s'))

print(f'      {feedLine.selectedTube}, ID {feedLine.innerDiameter * 1.0e3:.3f} mm, '
      f'velocity {feedLine.velocity:.3f} m/s')
print(f'      dP {feedLine.pressureDrop / 1.0e3:.2f} kPa (friction {feedLine.frictionPressureDrop / 1.0e3:.2f}, '
      f'minor {feedLine.minorPressureDrop / 1.0e3:.2f}), mass {feedLine.dryMass:.3f} kg')
print(f'      wall margin {feedLine.wallThickness["margin"] * 100.0:+.0f} %, '
      f'hoop stress {feedLine.wallThickness["hoopStress"] / 1.0e6:.2f} MPa')

# -- Fittings on the run -- #
unions = Fitting()
unions.setInputs({'fittingType': 'an flare', 'tubeOuterDiameter': feedLine.outerDiameter,
                  'tubeInnerDiameter': feedLine.innerDiameter, 'quantity': 2,
                  'fluid': 'N2H4', 'designPressure': 4.0e6,
                  'designTemperature': bedConfig['inletTemperature'],
                  'massFlow': thruster.massFlow, 'material': feedLine.material})
unions.checkCompatibility()
unions.calculatePressureLoss()
unions.calculateTorque()

print(f'      2 x AN flare unions: torque {unions.torqueRange[0]:.1f} to {unions.torqueRange[1]:.1f} N-m, '
      f'aggregate leak {unions.leakRateEstimate:.1e} scc/s He')

# ------------------------------------------------------------------------------------------------ #
# -- 6. Filter -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[6/9] Filter')

filterConfig       = config['filter']
filterOutletPressure = lineInletPressure

propellantFilter = Filter()
propellantFilter.setInputs({'fluid': 'N2H4',
                            'massFlow':          thruster.massFlow,
                            'upstreamPressure':  filterOutletPressure + filterConfig['allowableCleanPressureDrop'],
                            'temperature':       bedConfig['inletTemperature'],
                            'protectedPassage':  injector.diameter,
                            'filterType':        filterConfig['filterType'],
                            'betaRatio':         filterConfig['betaRatio'],
                            'allowableCleanPressureDrop': filterConfig['allowableCleanPressureDrop'],
                            'contaminationLoading':       filterConfig['contaminationLoading']})
propellantFilter.selectRating()
sizingResult = propellantFilter.sizeElement(requiredLife = filterConfig['requiredLife'])
lifeResult   = propellantFilter.calculateLife(operatingTime = filterConfig['requiredLife'])

filterInletPressure = filterOutletPressure + propellantFilter.cleanPressureDrop

stations.append(('Filter inlet (tank outlet)', filterInletPressure,
                 f'{propellantFilter.absoluteRating * 1.0e6:.0f} micron absolute, beta {propellantFilter.betaRatio}'))

print(f'      {propellantFilter.absoluteRating * 1.0e6:.0f} micron absolute protecting a '
      f'{injector.diameter * 1.0e6:.0f} micron injector bore (ratio {propellantFilter.protectionRatio:.1f})')
print(f'      binding constraint: {sizingResult["bindingConstraint"]}, '
      f'area {propellantFilter.filtrationArea * 1.0e4:.1f} cm^2, '
      f'envelope {propellantFilter.envelopeArea * 1.0e4:.2f} cm^2')
print(f'      clean dP {propellantFilter.cleanPressureDrop:.1f} Pa, '
      f'dirt capacity {propellantFilter.dirtCapacity * 1.0e3:.3f} g, '
      f'life {lifeResult["serviceLifeHours"]:.1f} h')

# ------------------------------------------------------------------------------------------------ #
# -- 7. Pressurization and pressure control -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[7/9] Pressurization and pressure control')

pressurizationConfig = config['pressurization']
regulatorConfig      = config['regulator']
missionConfig        = config['mission']

requiredTankPressure = filterInletPressure

stations.append(('Propellant tank', requiredTankPressure, 'required regulated pressure'))

pressurization = Pressurization()
pressurization.setInputs({'architecture':      pressurizationConfig['architecture'],
                          'pressurant':        pressurizationConfig['pressurant'],
                          'propellantVolume':  missionConfig['propellantVolume'],
                          'tankPressure':      requiredTankPressure,
                          'tankTemperature':   pressurizationConfig['tankTemperature'],
                          'bottlePressure':    pressurizationConfig['bottlePressure'],
                          'bottleTemperature': pressurizationConfig['bottleTemperature'],
                          'collapseFactorKey': pressurizationConfig['collapseFactorKey'],
                          'bottleProcess':     pressurizationConfig['bottleProcess']})
pressurization.calculateRegulated()

print(f'      regulated: {pressurization.pressurantMass:.4f} kg He in a '
      f'{pressurization.bottleVolume * 1.0e3:.2f} L bottle at '
      f'{pressurizationConfig["bottlePressure"] / 1.0e6:.0f} MPa (Z = {pressurization.compressibilityFactor:.3f})')
print(f'      usable {pressurization.usableMassFraction * 100.0:.1f} %, '
      f'residual {pressurization.residualMass:.4f} kg')

# The blowdown alternative, for comparison
blowdown = Pressurization()
blowdown.setInputs({'architecture': 'blowdown', 'pressurant': pressurizationConfig['pressurant'],
                    'propellantVolume': missionConfig['propellantVolume'],
                    'tankPressure': requiredTankPressure,
                    'blowdownRatio': pressurizationConfig['blowdownRatio'],
                    'tankTemperature': pressurizationConfig['tankTemperature'],
                    'polytropicExponent': pressurizationConfig['polytropicExponent']})
blowdownResult = blowdown.calculateBlowdown()

print(f'      blowdown alternative at {blowdownResult["blowdownRatio"]:.0f}:1: '
      f'{blowdown.pressurantMass:.4f} kg He, {blowdown.initialUllageVolume * 1.0e3:.1f} L ullage, '
      f'{blowdownResult["tankOversizing"]:.2f}x tank volume')

# -- Regulator, relief and burst disc -- #
regulator = Regulator()
regulator.setInputs({'fluid':               pressurizationConfig['pressurant'].capitalize(),
                     'temperature':         pressurizationConfig['tankTemperature'],
                     'regulatorType':       regulatorConfig['regulatorType'],
                     'inletPressure':       pressurizationConfig['bottlePressure'],
                     'finalInletPressure':  pressurization.regulatorLockupPressure,
                     'setPressure':         requiredTankPressure,
                     'massFlow':            0.001,
                     'reliefType':          regulatorConfig['reliefType'],
                     'burstDiscRating':     regulatorConfig['burstDiscRating'],
                     'burstDiscMaterial':   regulatorConfig['burstDiscMaterial'],
                     'burstDiscTolerance':  regulatorConfig['burstDiscTolerance'],
                     'burstDiscTemperature': regulatorConfig['burstDiscTemperature'],
                     'maximumOperatingPressure': 4.0e6,
                     'proofPressure':       4.0e6 * regulatorConfig['proofFactor']})
regulator.sizeRegulator()
regulator.sizeRelief(reliefFlow = regulatorConfig['reliefFlow'])
regulator.checkBurstDisc()
stackup = regulator.checkPressureStackup()

stations.append(('Regulator inlet (bottle)', pressurizationConfig['bottlePressure'], 'initial bottle pressure'))

print(f'      regulator band {regulator.outletPressureBand[0] / 1.0e6:.4f} to '
      f'{regulator.outletPressureBand[1] / 1.0e6:.4f} MPa '
      f'({(regulator.outletPressureBand[1] - regulator.outletPressureBand[0]) / requiredTankPressure * 100.0:.1f} % of set)')
print(f'      relief set {regulator.reliefSetPressure / 1.0e6:.4f} MPa, '
      f'area {regulator.reliefArea * 1.0e6:.3f} mm^2; '
      f'burst disc {regulator.burstDiscBand[0] / 1.0e6:.3f} to {regulator.burstDiscBand[1] / 1.0e6:.3f} MPa')
print(f'      pressure set point ladder: {"ALL PASS" if stackup["allPass"] else "VIOLATION"}')

# -- Check valve -- #
checkConfig = config['checkValve']
checkValve  = CheckValve()
checkValve.setInputs({'fluid': 'Helium',
                      'valveType':        checkConfig['valveType'],
                      'nominalSize':      checkConfig['nominalSize'],
                      'massFlow':         0.001,
                      'minimumMassFlow':  checkConfig['minimumMassFlow'],
                      'upstreamPressure': requiredTankPressure,
                      'temperature':      pressurizationConfig['tankTemperature']})
checkValve.calculatePressureDrop()
chatter = checkValve.checkChatter()
checkValve.calculateReverseLeakage()

print(f'      pressurant check valve: dP {checkValve.pressureDrop / 1.0e3:.2f} kPa, '
      f'chatter risk {chatter["chatterRisk"]}, reverse leak {checkValve.reverseLeakRate:.1e} scc/s He')

# ------------------------------------------------------------------------------------------------ #
# -- 8. Transients, joints and thermal -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[8/9] Transients, joints and thermal')

# -- Water hammer on thruster valve closure -- #
surge = WaterHammer()
surge.setInputs({'fluid': 'N2H4',
                 'pressure':      lineInletPressure,
                 'temperature':   bedConfig['inletTemperature'],
                 'velocity':      feedLine.velocity,
                 'innerDiameter': feedLine.innerDiameter,
                 'wallThickness': feedLine.wallThicknessActual,
                 'length':        feedLine.length,
                 'material':      feedLine.material,
                 'closureTime':   valveConfig['closureTime']})
surge.calculateSurge()

print(f'      water hammer: wave speed {surge.waveSpeed:.0f} m/s, pipe period '
      f'{surge.pipePeriod * 1.0e3:.2f} ms, closure {valveConfig["closureTime"] * 1.0e3:.0f} ms')
print(f'      Joukowsky {surge.joukowskySurge / 1.0e6:.3f} MPa, actual surge '
      f'{surge.actualSurge / 1.0e6:.4f} MPa, peak {surge.peakPressure / 1.0e6:.4f} MPa, '
      f'stress margin {surge.stressMargin:.1f}')

# -- Seal -- #
sealConfig = config['seal']
flangeSeal = Seal()
flangeSeal.setInputs({**sealConfig, 'fluid': 'N2H4',
                      'designPressure':    surge.peakPressure,
                      'designTemperature': bedConfig['inletTemperature']})
flangeSeal.checkCompatibility()
flangeSeal.sizeGland()
flangeSeal.checkExtrusion()
flangeSeal.calculatePermeation('He')

print(f'      seal: groove {flangeSeal.grooveDepth * 1.0e3:.4f} x {flangeSeal.grooveWidth * 1.0e3:.4f} mm, '
      f'squeeze {flangeSeal.squeeze * 100.0:.1f} %, fill {flangeSeal.glandFill * 100.0:.1f} %, '
      f'backup ring: {flangeSeal.backupRingRequired}')

# -- Weld -- #
weldConfig = config['weld']
joint = Weld()
joint.setInputs({**weldConfig,
                 'outerDiameter':     feedLine.outerDiameter,
                 'wallThickness':     feedLine.wallThicknessActual,
                 'designPressure':    surge.peakPressure,
                 'designTemperature': bedConfig['inletTemperature']})
joint.calculateDerating()
joint.calculateAllowablePressure()
joint.calculateFerriteNumber()
joint.selectInspection()

print(f'      weld: E {joint.jointEfficiency:.2f}, allowable {joint.allowablePressure / 1.0e6:.2f} MPa, '
      f'margin {joint.pressureMargin:.2f}, ferrite FN {joint.ferriteNumber:.1f}, '
      f'inspection: {joint.requiredInspection}')

# -- Insulation on the feed line -- #
insulationConfig = config['insulation']
lineInsulation   = Insulation()
lineInsulation.setInputs({'material':           insulationConfig['material'],
                          'geometry':           'cylindrical',
                          'innerDiameter':      feedLine.outerDiameter,
                          'length':             insulationConfig['length'],
                          'innerTemperature':   bedConfig['inletTemperature'],
                          'ambientTemperature': insulationConfig['ambientTemperature'],
                          'relativeHumidity':   insulationConfig['relativeHumidity'],
                          'windSpeed':          insulationConfig['windSpeed']})
lineInsulation.sizeThickness(targetHeatLeak = insulationConfig['targetHeatLeak'])

print(f'      insulation: {lineInsulation.thickness * 1.0e3:.2f} mm {insulationConfig["material"]} holds the '
      f'heat loss to {abs(lineInsulation.heatLeak):.2f} W')
print(f'      heater power to hold {bedConfig["inletTemperature"]:.1f} K against a '
      f'{insulationConfig["ambientTemperature"]:.0f} K environment: {abs(lineInsulation.heatLeak):.2f} W')

# ------------------------------------------------------------------------------------------------ #
# -- 9. Leak budget -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[9/9] Leak budget')

leakConfig = config['leakCheck']

leak = LeakPath()
leak.setInputs({'species':            leakConfig['species'],
                'upstreamPressure':   requiredTankPressure,
                'downstreamPressure': 101325.0,
                'temperature':        bedConfig['inletTemperature'],
                'length':             leakConfig['pathLength']})

allowable = leak.calculateAllowableFromHazard(enclosureVolume    = missionConfig['enclosureVolume'],
                                              concentrationLimit = missionConfig['hazardConcentrationLimit'],
                                              exposureTime       = 28800.0)

leak.leakRate     = allowable['allowableUnventilatedSccs']
leak.leakRateUnit = 'sccs'
leak.calculateEquivalentDiameter()
method = leak.selectDetectionMethod()

decayTest = leak.calculatePressureDecayTest(testVolume           = leakConfig['testVolume'],
                                            transducerResolution = leakConfig['transducerResolution'],
                                            testDuration         = leakConfig['testDuration'],
                                            temperatureStability = leakConfig['temperatureStability'])

print(f'      hazard-derived system allowable: {allowable["allowableUnventilatedSccs"]:.3e} scc/s He '
      f'(0.01 ppm N2H4 in {missionConfig["enclosureVolume"]:.0f} m^3 over 8 h)')
print(f'      equivalent hole {leak.equivalentDiameter * 1.0e6:.3f} micron, regime {leak.regime}')
print(f'      2 flare unions alone contribute {unions.leakRateEstimate:.1e} scc/s He: '
      f'{"WITHIN" if unions.leakRateEstimate <= allowable["allowableUnventilatedSccs"] else "EXCEEDS"} the system allowable')
print(f'      required detection method: {method}')
print(f'      pressure decay feasibility: {"adequate" if decayTest["feasible"] else "INADEQUATE"}, '
      f'limited by {decayTest["limitedBy"]} at {decayTest["overallFloorSccs"]:.2e} scc/s')

# ------------------------------------------------------------------------------------------------ #
# -- Station table -- #
# ------------------------------------------------------------------------------------------------ #

print()
rows = []
previousPressure = None
for name, pressure, note in stations:
    delta = '' if previousPressure is None else f'{(pressure - previousPressure) / 1.0e3:+.2f}'
    rows.append([name, f'{pressure / 1.0e6:.4f}', f'{pressure / PA_PER_PSIA:.1f}', delta, note])
    previousPressure = pressure

print(formatReportTable(rows,
                        ['Station (upstream order)', 'P [MPa]', 'P [psia]', 'dP [kPa]', 'Note'],
                        title = 'PRESSURE BUDGET'))

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

summaryRows = [
    ['Thrust',                      f'{thruster.thrust:.2f} N ({thruster.thrust / N_PER_LBF:.2f} lbf)'],
    ['Vacuum specific impulse',     f'{thruster.vacuumSpecificImpulse:.2f} s'],
    ['Propellant mass flow',        f'{thruster.massFlow:.5f} kg/s'],
    ['Chamber pressure',            f'{chamberPressure / 1.0e6:.4f} MPa'],
    ['Chamber temperature',         f'{bed.chamberTemperature:.1f} K'],
    ['Required tank pressure',      f'{requiredTankPressure / 1.0e6:.4f} MPa'],
    ['Total feed system dP',        f'{(requiredTankPressure - chamberPressure) / 1.0e3:.2f} kPa '
                                    f'({(requiredTankPressure - chamberPressure) / chamberPressure * 100.0:.1f} % of Pc)'],
    ['Peak pressure (surge)',       f'{surge.peakPressure / 1.0e6:.4f} MPa'],
    ['Feed line',                   f'{feedLine.selectedTube}'],
    ['Feed line mass',              f'{feedLine.dryMass:.3f} kg'],
    ['Catalyst mass',               f'{bed.catalystMass * 1.0e3:.1f} g'],
    ['Pressurant mass (regulated)', f'{pressurization.pressurantMass:.4f} kg He'],
    ['Pressurant bottle',           f'{pressurization.bottleVolume * 1.0e3:.2f} L at '
                                    f'{pressurizationConfig["bottlePressure"] / 1.0e6:.0f} MPa'],
    ['Filter element',              f'{propellantFilter.absoluteRating * 1.0e6:.0f} micron, '
                                    f'{propellantFilter.envelopeArea * 1.0e4:.1f} cm^2 envelope'],
    ['Line heater power',           f'{abs(lineInsulation.heatLeak):.2f} W'],
    ['System leak allowable',       f'{allowable["allowableUnventilatedSccs"]:.2e} scc/s He']
]

print()
print(formatReportTable(summaryRows, ['Quantity', 'Value'], title = 'SYSTEM SUMMARY'))

print('\nRun any component\'s generateReport() for the full detail, for example:')
print('    print(bed.generateReport())')
print('    print(thruster.generateReport())')
print('    print(regulator.generateReport())')
print()

debug = 1
