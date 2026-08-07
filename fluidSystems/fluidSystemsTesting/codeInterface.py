
# -- Top-Level Code Interface for the fluidSystemsTesting Library -- #

'''

End-to-end worked example: the qualification and acceptance campaign for the thruster valve from the
fluidSystems design example.

This deliberately continues the design-side worked example rather than inventing a fresh case. The
same 100 N hydrazine feed system, the same hardware, and critically the same two numbers that the
design analysis produced:

    2.4249 MPa   the peak pressure including the water hammer surge, which is the MEOP
    1.04e-05 scc/s   the hazard-derived system leak allowable, from the hydrazine exposure limit

Those two numbers are the entire bridge between the two directories. The design library computed
them; this library turns them into a test campaign. If either changes on the design side, everything
here moves with it, which is exactly the coupling a real programme has and usually manages badly.

Run it with:

    python codeInterface.py

Author: Sean Bowman
Date:   08/06/2026

'''

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fluidSystemsTestingLibrary'))

import numpy as np

from campaignUtils import formatReportTable, PA_PER_PSIA
from TestCampaign import TestCampaign
from PressureTest import PressureTest
from LeakTest import LeakTest
from EnvironmentalTest import EnvironmentalTest
from LifeTest import LifeTest
from UncertaintyBudget import UncertaintyBudget
from SampleSize import SampleSize

os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------------------------------------------------ #
# -- Inputs, inherited from the fluidSystems design example -- #
# ------------------------------------------------------------------------------------------------ #

# These come straight out of `fluidSystems/codeInterface.py`. Changing the design changes the
# campaign, and that traceability is the point.
MAXIMUM_EXPECTED_OPERATING_PRESSURE = 2.4249e6    # Pa, the surge peak, not the steady pressure
SYSTEM_LEAK_ALLOWABLE               = 1.042e-5    # scc/s He, derived from the hydrazine TLV
FEED_LINE_OUTER_DIAMETER            = 0.00953     # m, 0.375 in tube
FEED_LINE_WALL_THICKNESS            = 0.00165     # m, 0.065 in wall
VALVE_INTERNAL_VOLUME               = 0.00002     # m^3, 20 cc
SYSTEM_JOINT_COUNT                  = 12          # joints in the feed system
EXPECTED_ACTUATION_CYCLES           = 5000        # over the mission
MISSION_TEMPERATURE_RANGE           = (253.15, 333.15)   # K

print('=' * 110)
print('  fluidSystemsTesting worked example: qualification and acceptance of the thruster valve')
print('  Inherited from the fluidSystems design example: MEOP {:.4f} MPa, leak allowable {:.2e} scc/s'.format(
    MAXIMUM_EXPECTED_OPERATING_PRESSURE / 1.0e6, SYSTEM_LEAK_ALLOWABLE))
print('=' * 110)

# ------------------------------------------------------------------------------------------------ #
# -- 1. Campaign matrix -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[1/6] Test campaign matrix')

campaign = TestCampaign()
campaign.setInputs({
    'articleName':   'Thruster isolation valve, 100 N hydrazine monopropellant system',
    'articleType':   'valve',
    'hardwareClass': 'component',
    'fluidHazard':   'toxic',
    'isCryogenic':   False,
    'isSpaceflight': True,
    'tailoring':     {'thermal vacuum': 'Valve is internal to a pressurized bay; thermal vacuum is '
                                        'covered at the propulsion module assembly level'}
})
matrix = campaign.buildMatrix()

print(f'      qualification: {len(matrix["qualificationSequence"])} tests, '
      f'{len(matrix["destructiveTests"])} destructive')
print(f'      acceptance:    {len(matrix["acceptanceSequence"])} tests, every flight article')
print(f'      tailored out:  {len(matrix["tailoredOut"])} with stated reasons')

# ------------------------------------------------------------------------------------------------ #
# -- 2. Pressure testing -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[2/6] Proof and burst')

pressureTest = PressureTest()
pressureTest.setInputs({
    'maximumExpectedOperatingPressure': MAXIMUM_EXPECTED_OPERATING_PRESSURE,
    'hardwareClass':  'component',
    'testMedium':     'liquid',
    'testFluid':      'Water',
    'testVolume':     VALVE_INTERNAL_VOLUME,
    'testTemperature': 293.15,
    'material':       '316L',
    'outerDiameter':  FEED_LINE_OUTER_DIAMETER,
    'wallThickness':  FEED_LINE_WALL_THICKNESS
})
levels = pressureTest.calculateLevels()
energy = pressureTest.calculateStoredEnergy()
pressureTest.checkArticleCapability()

print(f'      proof {levels["proofPressure"] / 1.0e6:.4f} MPa, '
      f'burst {levels["burstPressure"] / 1.0e6:.4f} MPa, hold {levels["holdTime"]:.0f} s')
print(f'      hydrostatic stored energy {energy["storedEnergy"]:.2f} J, '
      f'yield margin at proof {pressureTest.yieldMargin:.1f}')

# The same test done pneumatically, to show why it is not
pneumatic = PressureTest()
pneumatic.setInputs({
    'maximumExpectedOperatingPressure': MAXIMUM_EXPECTED_OPERATING_PRESSURE,
    'hardwareClass': 'component', 'testMedium': 'gas', 'testFluid': 'Nitrogen',
    'testVolume': VALVE_INTERNAL_VOLUME
})
pneumatic.calculateLevels()
pneumaticEnergy = pneumatic.calculateStoredEnergy()

energyRatio = pneumaticEnergy['storedEnergy'] / energy['storedEnergy']
print(f'      the SAME test done pneumatically stores {pneumaticEnergy["storedEnergy"] / 1.0e3:.2f} kJ, '
      f'a factor of {energyRatio:.0f} more')
print(f'      unprotected personnel standoff would be '
      f'{pneumaticEnergy["safeStandoffDistance"]["personnel unprotected"]:.2f} m')

# ------------------------------------------------------------------------------------------------ #
# -- 3. Leak testing -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[3/6] Leak testing')

leakTest = LeakTest()
leakTest.setInputs({
    'allowableLeakRate': SYSTEM_LEAK_ALLOWABLE,
    'species':           'He',
    'serviceFluid':      'Nitrogen',
    'testPressure':      MAXIMUM_EXPECTED_OPERATING_PRESSURE,
    'downstreamPressure': 101325.0,
    'temperature':       293.15,
    'jointCount':        SYSTEM_JOINT_COUNT,
    'testVolume':        0.010,
    'transducerResolution': 100.0,
    'testDuration':      3600.0,
    'temperatureStability': 0.1
})
method     = leakTest.selectMethod()
allocation = leakTest.allocateAcrossJoints()
decay      = leakTest.evaluatePressureDecay()

print(f'      method: {method["selectedMethod"]} (floor {method["methodSensitivity"]:.1e} scc/s, '
      f'margin {method["detectionMargin"]:.1f}x)')
print(f'      per-joint allowable {allocation["perJointAllowable"]:.2e} scc/s across '
      f'{SYSTEM_JOINT_COUNT} joints')
print(f'      joint types that clear it: {", ".join(allocation["adequateJointTypes"])}')
print(f'      pressure decay feasible: {decay["feasible"]} '
      f'(floor {decay["overallFloorSccs"]:.2e} scc/s, limited by {decay["limitedBy"]})')

# ------------------------------------------------------------------------------------------------ #
# -- 4. Environmental testing -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[4/6] Environmental levels')

environmental = EnvironmentalTest()
environmental.setInputs({
    'flightEnvironmentKey':   'launch vehicle component',
    'flightDuration':         60.0,
    'shockEnvironmentKey':    'separation',
    'flightTemperatureRange': MISSION_TEMPERATURE_RANGE,
    'flightThermalCycles':    4
})
vibration = environmental.calculateRandomVibration()
shock     = environmental.calculateShock()
thermal   = environmental.calculateThermal()

print(f'      random: acceptance {vibration["acceptanceGrms"]:.2f} Grms for '
      f'{vibration["acceptanceDuration"]:.0f} s/axis, qualification '
      f'{vibration["qualificationGrms"]:.2f} Grms for {vibration["qualificationDuration"]:.0f} s/axis')
print(f'      shock:  {shock["peakQualification"]:.0f} g peak SRS, '
      f'{shock["applicationsPerAxis"]} applications per axis')
print(f'      thermal: {thermal["qualificationTemperatureRange"][0]:.1f} to '
      f'{thermal["qualificationTemperatureRange"][1]:.1f} K, '
      f'{thermal["qualificationThermalCycles"]} cycles')

compressed = environmental.scaleDurationToLevel(30.0)
print(f'      compressing the 120 s qual to 30 s needs +{compressed["decibelIncrease"]:.1f} dB '
      f'(defensible: {compressed["defensible"]})')

# ------------------------------------------------------------------------------------------------ #
# -- 5. Life testing -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[5/6] Life testing')

lifeTest = LifeTest()
lifeTest.setInputs({
    'articleType':       'valve',
    'expectedLife':      EXPECTED_ACTUATION_CYCLES,
    'cycleRate':         2.0,          # cycles per second on the test stand
    'availableDuration': 30.0 * 86400.0,   # 30 days
    'accelerationModel': 'none'
})
life     = lifeTest.calculateRequiredLife()
duration = lifeTest.calculateDuration()

print(f'      {life["requiredLife"]:.0f} cycles required ({life["lifeFactor"]:.0f}x the '
      f'{EXPECTED_ACTUATION_CYCLES} expected)')
print(f'      at {duration["cycleRate"]:.1f} cycles/s that is '
      f'{duration["requiredDurationDays"]:.2f} days, fits: {duration["feasible"]}')
print(f'      test condition: {life["condition"]}')

# ------------------------------------------------------------------------------------------------ #
# -- 6. Measurement uncertainty and sample size -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[6/6] Uncertainty and sample size')

budget = UncertaintyBudget()
budget.setInputs({'measurand': 'valve flow coefficient Cv', 'measurandValue': 0.348,
                  'measurandUnit': '-'})
budget.addContributor('flow meter calibration', 0.0035, 'normal k=2', evaluationType = 'B',
                      note = 'Coriolis meter, 0.5 % of reading at k=2')
budget.addContributor('pressure transducer',    0.0052, 'normal k=2', evaluationType = 'B',
                      note = '0.25 % FS on a 5 MPa range')
budget.addContributor('fluid density',          0.0021, 'rectangular', evaluationType = 'B',
                      note = 'Property data uncertainty')
budget.addContributor('temperature effect',     0.0028, 'rectangular', evaluationType = 'B',
                      note = 'Uncontrolled ambient over the test')
budget.addContributor('repeatability',          0.0019, 'normal k=1', evaluationType = 'A',
                      note = 'Standard deviation of 10 runs')
uncertainty = budget.calculate()

print(f'      Cv = {budget.measurandValue:.4f} +/- {uncertainty["expandedUncertainty"]:.4f} '
      f'(k = 2, {uncertainty["relativeExpandedUncertainty"] * 100.0:.2f} %)')
print(f'      dominant contributor: {uncertainty["dominantContributor"]} '
      f'({uncertainty["dominantShare"] * 100.0:.0f} % of the variance)')

sampleSize = SampleSize()
sampleSize.setInputs({'targetReliability': 0.99, 'confidenceLevel': 0.90, 'availableArticles': 3})
required     = sampleSize.calculateSuccessRun()
demonstrated = sampleSize.calculateDemonstrated()

print(f'      R = 0.99 at 90 % confidence needs {required["requiredSampleSize"]} units, zero failures')
print(f'      the 3 qualification articles actually demonstrate R = '
      f'{demonstrated["demonstratedReliability"]:.4f} at the same confidence')

# ------------------------------------------------------------------------------------------------ #
# -- Campaign summary -- #
# ------------------------------------------------------------------------------------------------ #

print()
print(campaign.generateReport())

summaryRows = [
    ['Article',                   'Thruster isolation valve, 100 N hydrazine system'],
    ['MEOP (inherited)',          f'{MAXIMUM_EXPECTED_OPERATING_PRESSURE / 1.0e6:.4f} MPa '
                                  f'({MAXIMUM_EXPECTED_OPERATING_PRESSURE / PA_PER_PSIA:.1f} psig)'],
    ['Proof pressure',            f'{pressureTest.proofPressure / 1.0e6:.4f} MPa, '
                                  f'{pressureTest.holdTime:.0f} s hold, hydrostatic'],
    ['Burst pressure',            f'{pressureTest.burstPressure / 1.0e6:.4f} MPa, destructive'],
    ['Leak allowable (inherited)', f'{SYSTEM_LEAK_ALLOWABLE:.3e} scc/s He, system'],
    ['Leak allowable per joint',  f'{leakTest.perJointAllowable:.3e} scc/s across {SYSTEM_JOINT_COUNT} joints'],
    ['Leak method',               f'{leakTest.selectedMethod}'],
    ['Random vibration, qual',    f'{environmental.qualificationGrms:.2f} Grms, '
                                  f'{environmental.qualificationDuration:.0f} s/axis'],
    ['Shock, qual',               f'{max(a for _, a in environmental.qualificationShockSpectrum):.0f} g peak SRS'],
    ['Thermal, qual',             f'{environmental.qualificationTemperatureRange[0]:.1f} to '
                                  f'{environmental.qualificationTemperatureRange[1]:.1f} K, '
                                  f'{environmental.qualificationThermalCycles} cycles'],
    ['Life, qual',                f'{lifeTest.requiredLife:.0f} cycles '
                                  f'({lifeTest.requiredDuration / 86400.0:.1f} days at 2 Hz)'],
    ['Cv measurement uncertainty', f'+/- {uncertainty["expandedUncertainty"]:.4f} '
                                   f'({uncertainty["relativeExpandedUncertainty"] * 100.0:.2f} %, k = 2)'],
    ['Qualification articles',    f'3 (1 consumed by burst)'],
    ['Demonstrated reliability',  f'R = {demonstrated["demonstratedReliability"]:.4f} at 90 % confidence']
]

print()
print(formatReportTable(summaryRows, ['Quantity', 'Value'], title = 'CAMPAIGN SUMMARY'))

# ------------------------------------------------------------------------------------------------ #
# -- The findings, which are the point -- #
# ------------------------------------------------------------------------------------------------ #

print()
print('=' * 110)
print('  FINDINGS')
print('=' * 110)
print()
print('  1. The per-joint leak allowable of {:.2e} scc/s admits only welded or VCR joints. The design'.format(
    leakTest.perJointAllowable))
print('     example used AN flare unions at 1e-4 scc/s each, so the joint architecture has to change.')
print('     Both directories reach the same conclusion from opposite ends.')
print()
print('  2. Pressure decay cannot verify this leak requirement. It is limited by {} at {:.2e} scc/s,'.format(
    decay['limitedBy'], decay['overallFloorSccs']))
print('     three orders of magnitude above the target. The campaign has to use a tracer gas method.')
print()
print('  3. A pneumatic proof test would store {:.0f} times the energy of the hydrostatic one and would'.format(
    energyRatio))
print('     require a {:.1f} m unprotected standoff. Proof with liquid.'.format(
    pneumaticEnergy['safeStandoffDistance']['personnel unprotected']))
print()
print('  4. Three qualification articles demonstrate R = {:.2f}, not the R = 0.99 the requirement asks'.format(
    demonstrated['demonstratedReliability']))
print('     for. Closing that gap needs analysis, heritage and process control, not more testing:')
print('     the demonstration alone would need {} units.'.format(required['requiredSampleSize']))
print()
print('  5. The dominant measurement uncertainty is the {} at {:.0f} % of the variance.'.format(
    uncertainty['dominantContributor'], uncertainty['dominantShare'] * 100.0))
print('     Improving anything else on the stand will not move the Cv uncertainty.')
print()

debug = 1
