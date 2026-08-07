
# -- Top-Level Code Interface for the aerospaceMaterials Library -- #

'''

Worked example: material selection, allowables and process route for the GHe pressurant bottle of
the 100 N hydrazine monopropellant system.

The bottle is taken directly from the fluidSystems worked example. That analysis produced a 30 MPa,
3.23 L bottle holding 0.1394 kg of helium and stopped there, because sizing the pressure vessel is a
materials and structures problem rather than a fluid one. This picks it up.

The bottle is the right part for this domain because pressure genuinely governs its wall. The 2.24
MPa propellant tank comes out at minimum gauge and makes the whole allowables argument look
academic; the bottle does not.

    fluidSystems                          aerospaceMaterials
    ------------                          ------------------
    pressurant mass       0.1394 kg  -->  bottle volume 3.23 L
    bottle pressure         30 MPa   -->  membrane stress
    thruster valve bore   4.76 mm    -->  LPBF manifold channel

The traversal:

    1. Database query with sources        what is actually known about each candidate
    2. Selection                          Ashby index, screened and ranked
    3. Allowables                         the ladder from typical to design value
    4. Wall sizing                        three criteria, and which one governs
    5. Damage tolerance                   critical flaw, leak before burst, proof as inspection
    6. Heat treatment and surface         the STA trade, and quench distortion on the bracket
    7. Process route                      buy-to-fly, knockdown, mass, cost, lead time
    8. Corrosion                          the boss to bracket couple, and the feed line

Run:
    python codeInterface.py

Configuration is loaded from aerospaceMaterialsLibrary/assets/heliumBottleMaterialsExample.json.

Author: Sean Bowman
Date:   08/07/2026

'''

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'aerospaceMaterialsLibrary'))

import numpy as np

from utils import formatReportTable, roughnessTable, PA_PER_PSIA
from MaterialDatabase import MaterialDatabase, queryMaterial, getProvenance
from Allowables import Allowables, STANDARD_KNOCKDOWNS
from MaterialSelector import MaterialSelector
from DamageTolerance import DamageTolerance
from CorrosionAssessment import CorrosionAssessment
from HeatTreatment import HeatTreatment
from ProcessComparison import ProcessComparison

os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------------------------------------------------ #
# -- Configuration -- #
# ------------------------------------------------------------------------------------------------ #

configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'aerospaceMaterialsLibrary', 'assets',
                          'heliumBottleMaterialsExample.json')

with open(configPath, 'r') as fileHandle:
    config = json.load(fileHandle)

inherited = config['inherited']
vessel    = config['vessel']

print('=' * 110)
print(f'  aerospaceMaterials worked example: {config["caseName"]}')
print(f'  Inherited from fluidSystems case: {config["linkedCase"]}')
print('=' * 110)

# -- Geometry from the inherited volume -- #

bottleVolume   = inherited['bottleVolume']
bottlePressure = inherited['bottlePressure']

bottleDiameter = (6.0 * bottleVolume / np.pi) ** (1.0 / 3.0)
bottleRadius   = bottleDiameter / 2.0

print(f'\n  Bottle: {bottleVolume * 1000.0:.2f} L sphere at '
      f'{bottlePressure / 1.0e6:.1f} MPa ({bottlePressure / PA_PER_PSIA:.0f} psia)')
print(f'          {bottleDiameter * 1000.0:.1f} mm diameter, holding '
      f'{inherited["pressurantMass"]:.4f} kg He')

ladder = []     # (step, factor, value, basis) accumulated through the allowables chain

# ------------------------------------------------------------------------------------------------ #
# -- 1. Database query with sources -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[1/8] Material database')

candidateRows = []

for name, condition in config['candidates']:

    properties = queryMaterial(name, condition, vessel['serviceTemperature'], basis = 'A')
    provenance = getProvenance(name, condition, 'allowables')

    ultimate = properties.get('ultimateStrength')
    yieldStr = properties.get('yieldStrength')

    candidateRows.append([
        f'{properties["material"]} {condition}',
        f'{properties["density"]:.0f}',
        f'{yieldStr / 1.0e6:.0f}' if yieldStr is not None else 'none',
        f'{ultimate / 1.0e6:.0f}' if ultimate is not None else 'none',
        f'{(ultimate / properties["density"]) / 1000.0:.0f}' if ultimate is not None else '-',
        provenance['basisClass'],
        f'{properties["relativeCost"]:.1f}'])

print(formatReportTable(
    candidateRows,
    ['Material', 'rho [kg/m3]', 'Fty_A [MPa]', 'Ftu_A [MPa]', 'Ftu/rho [kNm/kg]', 'Basis', 'Cost'],
    title = 'CANDIDATES AT A-BASIS, 293 K'))

print('      The Basis column is the point. A statistical entry is an MMPDS tolerance limit; a')
print('      spec minimum is a guaranteed value that is not a computed allowable at all.')

# ------------------------------------------------------------------------------------------------ #
# -- 2. Selection -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[2/8] Selection')

selector = MaterialSelector()
selector.setInputs({
    'requirements': {'serviceTemperature': vessel['serviceTemperature'],
                     'minimumTemperature': vessel['minimumTemperature'],
                     'maximumTemperature': vessel['maximumTemperature'],
                     'fluids': vessel['fluids'],
                     'environment': vessel['environment'],
                     'orientation': 'L',
                     'requireStatisticalBasis': True,
                     'minimumUltimateStrength': 250.0e6},
    'candidates': config['candidates'],
    'loadingMode': 'pressure vessel',
    'basis': 'A',
    'strengthProperty': 'ultimateStrength'})

selector.rank()

# Two different orderings, and the difference between them is the trade. The Ashby index alone
# answers 'which is lightest'; the weighted score folds in cost, lead time and how well established
# the allowable is.
byIndex = sorted(selector.ranking, key = lambda entry: entry['index'], reverse = True)

print('      By material index (lightest first), and by weighted score:')
for index, entry in enumerate(byIndex, start = 1):
    print(f'      {index}. {entry["label"]:24s} index {entry["index"] / 1000.0:7.1f} kNm/kg, '
          f'{entry["relativeMass"]:.2f}x mass, {entry["relativeCost"]:.1f}x cost, '
          f'score {entry["score"]:.3f}')

winner      = byIndex[0]
scoreWinner = selector.ranking[0]

print(f'\n      Lightest: {winner["label"]} at {winner["index"] / 1000.0:.0f} kNm/kg')
print(f'      Best weighted score: {scoreWinner["label"]}, because the index is only half the')
print(f'      weight and {scoreWinner["label"].split()[0]} is {winner["relativeCost"] / scoreWinner["relativeCost"]:.0f}x cheaper with a shorter lead time.')

# -- The same trade in an oxidiser system, which is where it inverts -- #

oxidiserSelector = MaterialSelector()
oxidiserSelector.setInputs({
    'requirements': {'serviceTemperature': 90.0, 'fluids': ['LOX'],
                     'environment': vessel['environment'],
                     'requireStatisticalBasis': True},
    'candidates': config['candidates'],
    'loadingMode': 'pressure vessel', 'basis': 'A'})
oxidiserResult  = oxidiserSelector.screen()
oxidiserRanking = oxidiserSelector.rank()

titaniumRejections = [label for label in oxidiserResult['rejected'] if 'TI-6AL-4V' in label.upper()]
oxidiserWinner     = oxidiserRanking[0]['label'] if oxidiserRanking else 'none of these candidates'

print(f'\n      Same bottle in a LOX system: titanium is rejected outright in all '
      f'{len(titaniumRejections)} conditions,')
print(f'      not downgraded, and the answer becomes {oxidiserWinner}.')

# ------------------------------------------------------------------------------------------------ #
# -- 3. Allowables -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[3/8] Allowables')

sampleSpecification = config['allowablesSample']
generator = np.random.default_rng(sampleSpecification['seed'])
sample    = generator.normal(sampleSpecification['meanStrength'],
                             sampleSpecification['standardDeviation'],
                             sampleSpecification['specimens'])

allowables = Allowables()
allowables.setInputs({'sampleData': sample, 'propertyName': 'ultimateStrength',
                      'loadPath': vessel['loadPath'],
                      'knockdowns': {'EB girth weld': vessel['girthWeldProcess']}})

basisValues = allowables.calculateBasisValue()
selection   = allowables.selectDesignValue()
chain       = allowables.applyKnockdowns()

print(f'      {allowables.sampleSize} specimens, mean {allowables.mean / 1.0e6:.1f} MPa, '
      f'CV {allowables.coefficientOfVariation * 100.0:.2f} %')
print(f'      k_A = {basisValues["A"]["kFactor"]:.3f}, k_B = {basisValues["B"]["kFactor"]:.3f}')
print(f'      A-basis {basisValues["A"]["value"] / 1.0e6:.1f} MPa, '
      f'B-basis {basisValues["B"]["value"] / 1.0e6:.1f} MPa')
print(f'      Single load path requires A-basis, which costs '
      f'{selection["costOfSingleLoadPath"] * 100.0:.1f} % against B')
print(f'      Design value after the girth weld knockdown: '
      f'{allowables.designValue / 1.0e6:.1f} MPa')

sampleSizeStudy = allowables.calculateRequiredSampleSize(0.92)
if sampleSizeStudy['achievable']:
    print(f'      Reaching a 0.92 basis ratio would need n = '
          f'{sampleSizeStudy["requiredSampleSize"]}, against the '
          f'{allowables.sampleSize} tested')

designUltimate = allowables.designValue

# The yield allowable follows the same chain, from the database A-basis rather than a sample
yieldProperties = queryMaterial('Ti-6Al-4V', 'annealed', vessel['serviceTemperature'], basis = 'A')
weldFactor      = STANDARD_KNOCKDOWNS[vessel['girthWeldProcess']]['factor']
designYield     = yieldProperties['yieldStrength'] * weldFactor

print(f'      Design yield, A-basis with the same weld knockdown: '
      f'{designYield / 1.0e6:.1f} MPa')

# ------------------------------------------------------------------------------------------------ #
# -- 4. Wall sizing, and the binding constraint -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[4/8] Wall sizing')

# Sphere membrane: sigma = P R / (2 t), so t = P R / (2 sigma)

criteria = {
    'Burst, FS 1.5 on ultimate':
        vessel['burstFactorOnUltimate'] * bottlePressure * bottleRadius / (2.0 * designUltimate),
    'Yield at MEOP, FS 1.25':
        vessel['yieldFactorAtMeop'] * bottlePressure * bottleRadius / (2.0 * designYield),
    'No yield during 1.5x proof':
        vessel['proofFactor'] * bottlePressure * bottleRadius / (2.0 * designYield)
}

governingCriterion = max(criteria, key = criteria.get)
wallThickness      = criteria[governingCriterion]

sizingRows = [[name, f'{value * 1000.0:.3f}',
               'GOVERNS' if name == governingCriterion else '']
              for name, value in criteria.items()]

print(formatReportTable(sizingRows, ['Criterion', 'Wall [mm]', ''],
                        title = 'WALL THICKNESS, THREE CRITERIA'))

titaniumProperties = queryMaterial('Ti-6Al-4V', 'annealed', vessel['serviceTemperature'])
bottleMass = np.pi * bottleDiameter ** 2 * wallThickness * titaniumProperties['density']

operatingStress = bottlePressure * bottleRadius / (2.0 * wallThickness)
proofStress     = vessel['proofFactor'] * operatingStress

print(f'      Wall {wallThickness * 1000.0:.3f} mm, D/t = {bottleDiameter / wallThickness:.0f}, '
      f'mass {bottleMass:.3f} kg')
print(f'      Membrane stress {operatingStress / 1.0e6:.1f} MPa at MEOP, '
      f'{proofStress / 1.0e6:.1f} MPa at proof')
print(f'      A {bottleMass:.2f} kg bottle to hold {inherited["pressurantMass"]:.4f} kg of helium.')

# What the wall would have been on the burst criterion alone
burstOnlyWall = criteria['Burst, FS 1.5 on ultimate']
burstOnlyProofStress = vessel['proofFactor'] * bottlePressure * bottleRadius / (2.0 * burstOnlyWall)

print(f'\n      Sizing on burst alone gives {burstOnlyWall * 1000.0:.3f} mm, at which the proof')
print(f'      test would develop {burstOnlyProofStress / 1.0e6:.0f} MPa against a design yield of')
print(f'      {designYield / 1.0e6:.0f} MPa. The bottle would yield during its own acceptance test.')

# ------------------------------------------------------------------------------------------------ #
# -- 5. Damage tolerance -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[5/8] Damage tolerance')

damage = DamageTolerance()
damage.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                  'temperature': vessel['serviceTemperature'],
                  'operatingStress': operatingStress, 'proofStress': proofStress,
                  'wallThickness': wallThickness, 'designCycles': vessel['designCycles'],
                  'inspectionMethod': 'penetrant, standard',
                  'geometryCase': 'surface flaw, semi-elliptical'})

criticalFlaw = damage.calculateCriticalFlaw()
leakResult   = damage.checkLeakBeforeBurst()
proofResult  = damage.calculateProofScreening()
growthResult = damage.calculateCrackGrowth()

print(f'      K_Ic {damage.fractureToughness / 1.0e6:.0f} MPa-sqrt(m)')
print(f'      Critical flaw at MEOP    {damage.criticalFlawSize * 1000.0:.2f} mm')
print(f'      Wall thickness           {wallThickness * 1000.0:.2f} mm')
print(f'      Leak before burst        {"YES" if damage.leakBeforeBurst else "NO"} '
      f'(ratio {leakResult["ratio"]:.2f})')
print(f'      Proof screens flaws to   {damage.proofFlawSize * 1000.0:.2f} mm')
print(f'      Penetrant credited with  {proofResult["ndeFlawSize"] * 1000.0:.2f} mm '
      f'(governs: {proofResult["governedBy"]})')
print(f'      Cycles to failure        {growthResult["cyclesToFailure"]:.0f} against '
      f'{vessel["designCycles"]} required, margin {growthResult["lifeMargin"]:.1f}x')

# The STA trade, quantified
staDamage = DamageTolerance()
staDamage.setInputs({'material': 'Ti-6Al-4V', 'condition': 'sta',
                     'operatingStress': operatingStress, 'wallThickness': wallThickness})
staDamage.calculateCriticalFlaw()

print(f'\n      The STA trade: STA raises A-basis yield from '
      f'{queryMaterial("Ti-6Al-4V", "annealed", 293.15, basis = "A")["yieldStrength"] / 1.0e6:.0f} '
      f'to {queryMaterial("Ti-6Al-4V", "sta", 293.15, basis = "A")["yieldStrength"] / 1.0e6:.0f} MPa')
print(f'      and drops the critical flaw from {damage.criticalFlawSize * 1000.0:.2f} to '
      f'{staDamage.criticalFlawSize * 1000.0:.2f} mm, which loses leak before burst.')

# ------------------------------------------------------------------------------------------------ #
# -- 6. Heat treatment and distortion -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[6/8] Heat treatment')

bracket = config['bracket']

treatment = HeatTreatment()
treatment.setInputs({'material': bracket['material'], 'condition': bracket['condition'],
                     'sectionThickness': 0.025, 'partLength': 0.300, 'partWidth': 0.150,
                     'solutionTemperature': 803.0, 'quenchant': 'agitated water',
                     'agingTemperature': 433.0, 'agingTime': 28800.0,
                     'machinedFraction': 0.50})

treatment.modelCoolingCurve()
quench     = treatment.calculateQuenchFactor()
distortion = treatment.calculateDistortion()

print(f'      6061-T6 bracket, 25 mm section, agitated water')
print(f'      Biot {treatment.biotNumber:.2f}, cooling {treatment.coolingRate:.0f} K/s, '
      f'quench factor {treatment.quenchFactor:.2f}')
print(f'      Retained strength {quench["retainedStrengthFraction"] * 100.0:.1f} % of the ideal quench')
print(f'      Quench residual stress {distortion["residualStress"] / 1.0e6:.0f} MPa')
print(f'      Bow if machined 50 % from one side: '
      f'{distortion["predictedBow"] * 1000.0:.3f} mm over 300 mm')

# The section thickness sensitivity, which is the design lever
print('\n      Retained strength against section thickness:')
for thickness in (0.010, 0.025, 0.050, 0.100):
    study = HeatTreatment()
    study.setInputs({'material': '7075', 'condition': 't73', 'sectionThickness': thickness,
                     'quenchant': 'agitated water'})
    study.modelCoolingCurve()
    retained = study.calculateQuenchFactor()['retainedStrengthFraction']
    print(f'          7075-T73 at {thickness * 1000.0:5.0f} mm: {retained * 100.0:5.1f} %')

# ------------------------------------------------------------------------------------------------ #
# -- 7. Process route -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[7/8] Process route')

comparison = ProcessComparison()
comparison.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                      'finishedMass': bottleMass,
                      'minimumWallThickness': wallThickness,
                      'characteristicSize': bottleDiameter,
                      'requiredTolerance': 0.30e-3,
                      'quantity': 1})

routes = comparison.compareRoutes()

routeRows = [[entry['route'], f'{entry["buyToFly"]:.1f}:1',
              f'{entry["allowableFactor"]:.2f}',
              f'{entry["effectiveMass"]:.3f}',
              f'{entry["relativeCost"]:.1f}',
              f'{entry["leadTimeWeeks"]:.0f}'] for entry in routes]

print(formatReportTable(routeRows,
                        ['Route', 'Buy-to-fly', 'Allowable', 'Eff mass [kg]', 'Rel cost',
                         'Lead wk'],
                        title = 'ROUTES FOR THE BOTTLE, CHEAPEST FIRST'))

cheapest = comparison.selectRoute('minimum cost')
fastest  = comparison.selectRoute('minimum lead time')
lightest = comparison.selectRoute('minimum mass')

print(f'      Cheapest: {cheapest["selected"]}')
print(f'      Fastest:  {fastest["selected"]}')
print(f'      Lightest: {lightest["selected"]}')

# ------------------------------------------------------------------------------------------------ #
# -- 8. Corrosion -- #
# ------------------------------------------------------------------------------------------------ #

print('\n[8/8] Corrosion')

corrosion = CorrosionAssessment()
corrosion.setInputs({'anodeMaterial': bracket['material'], 'anodeCondition': bracket['condition'],
                     'cathodeMaterial': 'Ti-6Al-4V', 'cathodeCondition': 'annealed',
                     'anodeArea': bracket['bracketArea'], 'cathodeArea': bracket['bossArea'],
                     'environment': vessel['environment'],
                     'serviceLife': vessel['serviceLifeYears'] * 3.156e7,
                     'corrosionAllowance': bracket['corrosionAllowance']})

galvanic = corrosion.calculateGalvanicCouple()

print(f'      Ti-6Al-4V boss to 6061-T6 bracket')
print(f'      Potential difference {galvanic["potentialDifference"]:.2f} V against a '
      f'{galvanic["permittedDifference"]:.2f} V limit for {vessel["environment"]}')
print(f'      Acceptable: {"YES" if galvanic["acceptable"] else "NO"}')
print(f'      Area ratio {galvanic["areaRatio"]:.2f}, penetration '
      f'{galvanic["penetrationPerYear"] * 1.0e3:.4f} mm/yr, '
      f'{galvanic["penetrationDepth"] * 1.0e3:.3f} mm over {vessel["serviceLifeYears"]:.0f} years')
print(f'      Corrosion allowance {bracket["corrosionAllowance"] * 1.0e3:.3f} mm, '
      f'margin {galvanic.get("allowanceMargin", float("nan")):.2f}')

# The feed line, which is 316L at a coastal site
feedLine = CorrosionAssessment()
feedLine.setInputs({'anodeMaterial': '316L', 'anodeCondition': 'annealed',
                    'environment': vessel['environment'],
                    'temperature': vessel['serviceTemperature']})
pitting = feedLine.calculatePittingResistance()

print(f'\n      316L feed line: PREN {pitting["pren"]:.1f}, critical pitting temperature '
      f'{pitting["criticalPittingCelsius"]:.0f} degC')
print(f'      Pits at the service temperature: '
      f'{"YES" if pitting["pitsAtServiceTemperature"] else "no"}')

protection = corrosion.recommendProtection()
print(f'\n      Protection, most effective first:')
for index, recommendation in enumerate(protection[:3], start = 1):
    print(f'        {index}. {recommendation[:96]}')

# ------------------------------------------------------------------------------------------------ #
# -- The allowables ladder -- #
# ------------------------------------------------------------------------------------------------ #

print()
ladderRows = [[entry['step'],
               '' if entry['factor'] is None else f'{entry["factor"]:.4f}',
               f'{entry["value"] / 1.0e6:.1f}',
               entry['basis'][:52]] for entry in allowables.knockdownChain]
ladderRows.append(['Applied stress at MEOP', '', f'{operatingStress / 1.0e6:.1f}',
                   f'membrane, {wallThickness * 1000.0:.2f} mm wall'])
ladderRows.append(['Margin of safety', '',
                   f'{designUltimate / (operatingStress * 1.5) - 1.0:+.3f}',
                   'against ultimate at FS 1.5'])

print(formatReportTable(ladderRows, ['Step', 'Factor', 'Value [MPa]', 'Basis'],
                        title = 'ALLOWABLES LADDER'))

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

print()

summaryRows = [
    ['Inherited bottle pressure',  f'{bottlePressure / 1.0e6:.1f} MPa '
                                   f'({bottlePressure / PA_PER_PSIA:.0f} psia)'],
    ['Inherited bottle volume',    f'{bottleVolume * 1000.0:.2f} L'],
    ['Bottle diameter',            f'{bottleDiameter * 1000.0:.1f} mm sphere'],
    ['Selected material',          f'Ti-6Al-4V annealed'],
    ['A-basis ultimate',           f'{basisValues["A"]["value"] / 1.0e6:.1f} MPa '
                                   f'(k = {basisValues["A"]["kFactor"]:.3f}, n = '
                                   f'{allowables.sampleSize})'],
    ['Design ultimate',            f'{designUltimate / 1.0e6:.1f} MPa after the girth weld'],
    ['Governing wall criterion',   f'{governingCriterion}'],
    ['Wall thickness',             f'{wallThickness * 1000.0:.3f} mm (D/t = '
                                   f'{bottleDiameter / wallThickness:.0f})'],
    ['Bottle mass',                f'{bottleMass:.3f} kg'],
    ['Membrane stress at MEOP',    f'{operatingStress / 1.0e6:.1f} MPa'],
    ['Critical flaw depth',        f'{damage.criticalFlawSize * 1000.0:.2f} mm'],
    ['Leak before burst',          f'{"YES" if damage.leakBeforeBurst else "NO"}'],
    ['Crack growth life',          f'{growthResult["cyclesToFailure"]:.0f} cycles, '
                                   f'{growthResult["lifeMargin"]:.1f}x margin'],
    ['Cheapest route',             f'{cheapest["selected"]}'],
    ['Fastest route',              f'{fastest["selected"]}'],
    ['Boss to bracket couple',     f'{galvanic["potentialDifference"]:.2f} V, '
                                   f'{"acceptable" if galvanic["acceptable"] else "REJECTED"}'],
    ['316L feed line PREN',        f'{pitting["pren"]:.1f}, CPT '
                                   f'{pitting["criticalPittingCelsius"]:.0f} degC']
]

print(formatReportTable(summaryRows, ['Quantity', 'Value'], title = 'MATERIALS SUMMARY'))

# ------------------------------------------------------------------------------------------------ #
# -- Findings -- #
# ------------------------------------------------------------------------------------------------ #

print()
print('=' * 110)
print('  FINDINGS')
print('=' * 110)
print()
print(f'  1. THE PROOF TEST GOVERNS THE WALL, NOT BURST. Burst at FS 1.5 gives')
print(f'     {criteria["Burst, FS 1.5 on ultimate"] * 1000.0:.2f} mm and yield at MEOP gives '
      f'{criteria["Yield at MEOP, FS 1.25"] * 1000.0:.2f} mm, but holding the bottle below yield')
print(f'     during its own 1.5x proof test needs '
      f'{criteria["No yield during 1.5x proof"] * 1000.0:.2f} mm. Sized on burst alone the bottle')
print(f'     would yield during acceptance testing, and every flight article would be damaged')
print(f'     by the test meant to qualify it.')
print()
print(f'  2. TITANIUM WINS ON STRENGTH TO WEIGHT AND IS PROHIBITED IN THE OXIDISER VERSION.')
print(f'     Ti-6Al-4V leads the ranking at '
      f'{winner["index"] / 1000.0:.0f} kNm/kg. Change the fluid to LOX and it')
print(f'     is rejected outright, not downgraded, because it is impact sensitive in oxygen')
print(f'     and burns. The same bottle then needs a different alloy and a mass penalty.')
print()
print(f'  3. THE SINGLE LOAD PATH COSTS '
      f'{selection["costOfSingleLoadPath"] * 100.0:.1f} PERCENT OF THE ALLOWABLE. A pressure')
print(f'     vessel wall cannot redistribute load, so it requires A-basis rather than B, and at')
print(f'     n = {allowables.sampleSize} that gap is worth '
      f'{(basisValues["B"]["value"] - basisValues["A"]["value"]) / 1.0e6:.0f} MPa. Part of the gap is the material')
print(f'     and part of it is simply how much testing was done.')
print()
print(f'  4. LEAK BEFORE BURST IS SATISFIED, AND THE STA CONDITION WOULD LOSE IT.')
print(f'     The critical flaw is {damage.criticalFlawSize * 1000.0:.2f} mm against a '
      f'{wallThickness * 1000.0:.2f} mm wall, so a growing crack')
print(f'     vents rather than running. Solution treating and aging raises the yield strength')
print(f'     and cuts the critical flaw to {staDamage.criticalFlawSize * 1000.0:.2f} mm, below the wall. '
      f'The stronger heat treatment')
print(f'     makes the vessel less safe, which the strength table alone does not show.')
print()
print(f'  5. THE BOSS TO BRACKET COUPLE IS REJECTED AT '
      f'{galvanic["potentialDifference"]:.2f} V AGAINST A '
      f'{galvanic["permittedDifference"]:.2f} V LIMIT.')
print(f'     Titanium against 6061-T6 at a coastal site consumes '
      f'{galvanic["penetrationDepth"] * 1.0e3:.3f} mm of bracket over')
print(f'     {vessel["serviceLifeYears"]:.0f} years against a '
      f'{bracket["corrosionAllowance"] * 1.0e3:.3f} mm allowance. The joint needs isolation, and the')
print(f'     coating goes on the cathode.')
print()
print(f'  6. THE 316L FEED LINE PITS AT AMBIENT. PREN {pitting["pren"]:.1f} gives a critical pitting')
print(f'     temperature of {pitting["criticalPittingCelsius"]:.0f} degC, so in a coastal chloride environment')
print(f'     316L is below its own threshold at every service temperature. Passivation restores')
print(f'     the film; only a higher alloy content raises the threshold.')
print()

debug = 1
