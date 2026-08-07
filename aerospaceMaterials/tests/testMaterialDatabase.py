
# -- Tests for the material database -- #

'''

Tiered tests for materialData.py and MaterialDatabase.py.

Tier 1 covers structural integrity of the database itself: every record well formed, every property
traceable to a source, every alias resolving. These catch a typo the moment it is introduced.
Tier 2 validates against published values and against the other tables in the repository that carry
the same physical facts, so the copies cannot drift apart.
Tier 3 covers self-consistency: the temperature curves, the clamping behaviour, and the invariants
that have to hold no matter which alloy is asked about.

The drift tests are the important ones. Three tables in this repository carry overlapping material
facts and nothing but a test stops them diverging.

Author: Sean Bowman
Date:   08/06/2026

'''

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'aerospaceMaterialsLibrary'))

from materialData import (MATERIAL_DATABASE, MATERIAL_ALIASES, SOURCES, SEEDED_FROM_COMMON,
                          SEEDED_TYPICAL_PROPERTIES, SEEDED_THERMAL_PROPERTIES,
                          SEEDED_ALLOY_PROPERTIES)
from MaterialDatabase import (MaterialDatabase, queryMaterial, resolveMaterialKey, getProvenance,
                              listMaterials, BASIS_ORDER, ORIENTATIONS)
from utils import materialProperties, roughnessTable, InvalidInputError, CompatibilityError

# ---------------------------------------------------------------------------------------------- #
# -- Tier 1: database structural integrity -- #
# ---------------------------------------------------------------------------------------------- #

def testEveryAlloyHasRequiredFields():

    '''
    Every alloy record must carry the identity fields the selector and the corrosion classes read.
    A missing anodicIndex surfaces as a TypeError deep inside a galvanic calculation otherwise.
    '''

    required = ('commonName', 'family', 'crystalStructure', 'density', 'poissonRatio',
                'anodicIndex', 'relativeCost', 'costBasisDate', 'incompatible', 'compatible',
                'conditions')

    for key, record in MATERIAL_DATABASE.items():
        for field in required:
            assert field in record, f'{key} is missing the required alloy field \'{field}\''
        assert record['conditions'], f'{key} has no conditions defined'

def testEveryConditionHasTypicalStrength():

    '''
    A condition with no yield or ultimate strength cannot be used for anything. Catches a record
    where the seed merge was expected to fill a value and the seed mapping was never added.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            typical = condition.get('typical', {})
            for name in ('yieldStrength', 'ultimateStrength', 'elasticModulus'):
                assert name in typical, \
                    f'{key} / {conditionKey} has no {name}. If it was meant to come from ' \
                    f'common/materials.py, add it to SEEDED_FROM_COMMON.'
                assert typical[name] > 0.0, f'{key} / {conditionKey} has a non-positive {name}'

def testEveryPropertyBlockHasASource():

    '''
    Traceability is enforced here rather than by the data structure. Every property block in every
    condition must name a source key, and every source key must resolve in SOURCES.
    '''

    tracked = ('typical', 'allowables', 'thermal', 'fracture', 'fatigue', 'environmental',
               'temperatureCurves', 'anisotropy', 'quenchFactor', 'stressRupture', 'sensitization')

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            sources = condition.get('sources', {})
            for block in tracked:
                if block not in condition:
                    continue
                assert block in sources, \
                    f'{key} / {conditionKey} has a \'{block}\' block with no source entry. ' \
                    f'An untraceable number is not usable in a stress report.'
                assert sources[block] in SOURCES, \
                    f'{key} / {conditionKey} block \'{block}\' names source ' \
                    f'\'{sources[block]}\' which is not in SOURCES'

def testEverySourceDeclaresABasisClass():

    '''
    basisClass is what separates an MMPDS tolerance limit from somebody's recollection. A source
    without one would silently read as trustworthy.
    '''

    valid = {'statistical', 'spec minimum', 'typical', 'estimate'}

    for key, record in SOURCES.items():
        assert 'basisClass' in record, f'SOURCES[{key}] has no basisClass'
        assert record['basisClass'] in valid, \
            f'SOURCES[{key}] has basisClass \'{record["basisClass"]}\', expected one of {valid}'
        assert 'document' in record, f'SOURCES[{key}] has no document'

def testEveryAliasResolves():

    '''
    An alias pointing at a key that does not exist is a silent trap: it only fails when somebody
    happens to use that spelling.
    '''

    for alias, target in MATERIAL_ALIASES.items():
        assert target in MATERIAL_DATABASE, \
            f'Alias \'{alias}\' points at \'{target}\' which is not in MATERIAL_DATABASE'

def testTemperatureCurvesAreWellFormed():

    '''
    Every ratio array must be the same length as its temperature grid, and every grid must be
    monotonically increasing or np.interp returns silent nonsense.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            for blockName in ('temperatureCurves', 'cryogenicCurves'):
                block = condition.get(blockName)
                if block is None:
                    continue
                grid = block['temperature']
                assert np.all(np.diff(grid) > 0.0), \
                    f'{key} / {conditionKey} / {blockName} temperature grid is not increasing. ' \
                    f'np.interp will return silent nonsense.'
                for curveName, values in block.items():
                    if not curveName.endswith('Ratio'):
                        continue
                    assert len(values) == len(grid), \
                        f'{key} / {conditionKey} / {blockName} curve \'{curveName}\' has ' \
                        f'{len(values)} points against a {len(grid)} point grid'
                    assert np.all(values > 0.0), \
                        f'{key} / {conditionKey} / {blockName} curve \'{curveName}\' has a ' \
                        f'non-positive ratio'

def testRatioCurvesAreUnityAtRoomTemperature():

    '''
    The curves are ratios to the room temperature value, so they must pass through 1.0 at 293.15 K.
    A curve that does not means the stored typical value and the curve disagree about what the room
    temperature value is, and every corrected property is then wrong by that offset.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            for blockName in ('temperatureCurves', 'cryogenicCurves'):
                block = condition.get(blockName)
                if block is None:
                    continue
                grid = block['temperature']
                if not (grid[0] <= 293.15 <= grid[-1]):
                    continue
                for curveName, values in block.items():
                    if not curveName.endswith('Ratio'):
                        continue
                    atRoom = float(np.interp(293.15, grid, values))
                    assert atRoom == pytest.approx(1.0, abs = 0.01), \
                        f'{key} / {conditionKey} / {blockName} curve \'{curveName}\' is ' \
                        f'{atRoom:.3f} at 293.15 K, not 1.0. The curve and the stored typical ' \
                        f'value disagree about the room temperature reference.'

def testUnknownMaterialRaises():

    '''
    An unknown material must raise with the available keys listed, not return a default.
    '''

    with pytest.raises(InvalidInputError):
        resolveMaterialKey('unobtainium')

    with pytest.raises(InvalidInputError):
        queryMaterial('316L', 'a condition that does not exist')

# ---------------------------------------------------------------------------------------------- #
# -- Tier 2: drift against the other tables in the repository -- #
# ---------------------------------------------------------------------------------------------- #

def testSeedAgreementWithCommon():

    '''
    THE drift test. The nine alloys carried by common/materials.py are merged into this database at
    import rather than re-typed, so both must return identical numbers. If this fails, somebody has
    added a duplicate value to one file and the repository now has two answers to the question
    'what is 316L's yield strength'.
    '''

    for databaseKey, (commonKey, conditionKey) in SEEDED_FROM_COMMON.items():

        queried = queryMaterial(databaseKey, conditionKey, 293.15)
        common  = materialProperties(commonKey, 293.15)

        for name in SEEDED_ALLOY_PROPERTIES + SEEDED_TYPICAL_PROPERTIES + SEEDED_THERMAL_PROPERTIES:
            assert queried[name] == pytest.approx(common[name], rel = 1e-12), \
                f'{databaseKey} / {conditionKey} disagrees with common/materials.py on {name}: ' \
                f'{queried[name]} versus {common[name]}. The seed merge has been bypassed by a ' \
                f'value typed directly into materialData.py.'

def testAllowableStressMatchesCommon():

    '''
    The B31.3 style basic allowable is computed in both places from the same formula. Catches a
    divergence in the 2/3 yield versus ultimate/3.5 criterion.
    '''

    for databaseKey, (commonKey, conditionKey) in SEEDED_FROM_COMMON.items():
        queried = queryMaterial(databaseKey, conditionKey, 293.15)
        common  = materialProperties(commonKey, 293.15)
        assert queried['allowableStress'] == pytest.approx(common['allowableStress'], rel = 1e-12), \
            f'{databaseKey} basic allowable disagrees with common/materials.py'

def testCryogenicModelReconciliation():

    '''
    common/materials.py uses a crude one-sided linear cryogenic correction; this database uses a real
    ratio curve. They will not agree exactly and they are not required to. What they must not do is
    disagree by more than 20 percent at 77 K, because that would mean the crude model is not merely
    crude but wrong, and every preliminary sizing done with it is misleading.

    Austenitic stainless is excluded from the tight bound: its strain-induced martensite gain is
    strongly product-form dependent and the two sources genuinely differ on it.
    '''

    for databaseKey, (commonKey, conditionKey) in SEEDED_FROM_COMMON.items():

        record = MATERIAL_DATABASE[databaseKey]['conditions'][conditionKey]
        block  = record.get('cryogenicCurves') or record.get('temperatureCurves')

        if block is None or block['temperature'][0] > 77.0:
            continue

        curveRatio  = float(np.interp(77.0, block['temperature'], block['yieldRatio']))
        commonRatio = record['commonCryogenicYieldFactor']

        tolerance = 0.35 if 'austenitic' in MATERIAL_DATABASE[databaseKey]['family'] else 0.20

        assert abs(curveRatio - commonRatio) / commonRatio < tolerance, \
            f'{databaseKey} cryogenic strength gain at 77 K: curve says {curveRatio:.2f}x, ' \
            f'common/materials.py says {commonRatio:.2f}x. The crude model is allowed to be ' \
            f'crude but not wrong. One of the two needs correcting.'

def testAsWeldedAluminiumMatchesWeldKnockdown():

    '''
    The 6061-T6 heat affected zone knockdown is carried in two places: as an 'as-welded' condition
    here, and as HAZ_KNOCKDOWN in fluidSystems Weld.py. Both encode the same physical fact, that
    6061-T6 loses roughly 40 percent of its yield in the weld and does not recover without a full
    solution treat and age.

    Weld.py is left alone deliberately: it is working code with passing tests. This test is what
    stops the two drifting.
    '''

    # Weld.py is read and parsed rather than imported. Both libraries have a module named utils on a
    # flat sys.path, so importing Weld here would resolve its 'from utils import ...' against this
    # domain's utils and fail. Parsing the literal has no import side effects and cannot be broken by
    # path ordering, which makes it the more robust choice for a cross-domain consistency check.
    import ast

    weldPath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), 'fluidSystems', 'fluidSystemsLibrary', 'Weld.py')

    if not os.path.exists(weldPath):
        pytest.skip('fluidSystems Weld.py not present; nothing to reconcile against')

    with open(weldPath, 'r', encoding = 'utf-8') as fileHandle:
        tree = ast.parse(fileHandle.read())

    knockdownTable = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == 'HAZ_KNOCKDOWN':
                knockdownTable = ast.literal_eval(node.value)

    if knockdownTable is None:
        pytest.skip('Weld.HAZ_KNOCKDOWN not present; nothing to reconcile against')

    parent   = queryMaterial('6061', 't6',        293.15)['yieldStrength']
    asWelded = queryMaterial('6061', 'as-welded', 293.15)['yieldStrength']
    ratio    = asWelded / parent

    entry = None
    for key, value in knockdownTable.items():
        if '6061' in key.upper():
            entry = value
            break

    if entry is None:
        pytest.skip('No 6061 entry in Weld.HAZ_KNOCKDOWN')

    expected = entry['yield'] if isinstance(entry, dict) else entry

    assert ratio == pytest.approx(expected, rel = 0.15), \
        f'6061 as-welded yield ratio is {ratio:.3f} in materialData.py but Weld.HAZ_KNOCKDOWN ' \
        f'says {expected:.3f}. The same physical fact is written down twice and the copies have ' \
        f'drifted.'

def testTitaniumYieldAgainstMmpds():

    '''
    Validated against MMPDS: Ti-6Al-4V annealed sheet has an A-basis ultimate of 897 MPa (130 ksi)
    and an A-basis yield of 828 MPa (120 ksi). Catches a unit error or a transposed digit in the
    allowables block of the most safety critical alloy in the database.
    '''

    result = queryMaterial('Ti-6Al-4V', 'annealed', 293.15, basis = 'A')

    assert result['ultimateStrength'] == pytest.approx(897.0e6, rel = 0.01), \
        f'Ti-6Al-4V A-basis ultimate should be about 897 MPa, got ' \
        f'{result["ultimateStrength"] / 1.0e6:.1f} MPa'
    assert result['yieldStrength'] == pytest.approx(828.0e6, rel = 0.01)
    assert result['basisAvailable'] is True

def testAusteniticStainlessGainsStrengthWhenCold():

    '''
    Validated against the NIST cryogenic database: 316L roughly doubles its yield strength between
    room temperature and 77 K. This is the single most useful fact about austenitic stainless in
    cryogenic service and a sign error in the curve would invert it.
    '''

    room = queryMaterial('316L', 'annealed', 293.15)['yieldStrength']
    cold = queryMaterial('316L', 'annealed', 77.0)['yieldStrength']

    assert cold > room, 'Austenitic stainless must gain strength on cooling, not lose it'
    assert cold / room == pytest.approx(2.4, rel = 0.15), \
        f'316L should gain roughly 2.4x yield at 77 K, got {cold / room:.2f}x'

def testMartensiticSteelLosesToughnessWhenCold():

    '''
    The body-centred cubic problem, quantified. 4340 keeps most of its strength at 77 K and loses
    almost all of its fracture toughness, which is why a high strength steel is never a cryogenic
    material regardless of what its strength table says.

    This is the test that would catch somebody copying an FCC toughness curve onto a BCC alloy.
    '''

    database = MaterialDatabase()

    database.setInputs({'material': '4340', 'condition': 'qt-260', 'temperature': 293.15})
    roomToughness = database.getFractureData()['planeStrainToughness']['L-T']

    database = MaterialDatabase()
    database.setInputs({'material': '4340', 'condition': 'qt-260', 'temperature': 77.0})
    coldToughness = database.getFractureData()['planeStrainToughness']['L-T']

    roomYield = queryMaterial('4340', 'qt-260', 293.15)['yieldStrength']
    coldYield = queryMaterial('4340', 'qt-260', 77.0)['yieldStrength']

    assert coldToughness / roomToughness < 0.25, \
        f'4340 should lose most of its toughness at 77 K, retained ' \
        f'{coldToughness / roomToughness:.2f}'
    assert coldYield / roomYield > 1.0, \
        'and it should keep its strength, which is exactly what makes it dangerous'

def testElectronBeamLithiumAlloyIsLighterAndStiffer():

    '''
    Validated against the Al-Li literature: 2195 is roughly 4 percent less dense and 5 percent
    stiffer than 2219, which together are why the Shuttle super lightweight tank saved 3400 kg.
    Both effects have to be present; a density error alone would look like a win.
    '''

    conventional = queryMaterial('2219', 't87', 293.15)
    lithium      = queryMaterial('2195', 't8',  293.15)

    assert lithium['density'] < conventional['density'], 'Al-Li must be less dense'
    assert lithium['elasticModulus'] > conventional['elasticModulus'], 'and stiffer'
    assert lithium['density'] / conventional['density'] == pytest.approx(0.954, rel = 0.02)

def testCopperLinerConductivityDominatesNickel():

    '''
    Validated against published GRCop-42 data: thermal conductivity around 320 W/m-K against 11.4
    for Inconel 718. That factor of 28 is the entire reason a regeneratively cooled chamber has a
    copper liner, and a unit error here would make the trade look marginal.
    '''

    copper = queryMaterial('GRCop-42', 'lpbf hip', 293.15)['thermalConductivity']
    nickel = queryMaterial('Inconel 718', 'sta',   293.15)['thermalConductivity']

    assert copper / nickel > 20.0, \
        f'GRCop-42 should conduct more than 20x better than Inconel 718, got {copper / nickel:.1f}x'

def testAdditiveRoughnessMatchesCommonTable():

    '''
    The LPBF roughness entries live in common/materials.py and both additiveLPBF and extrusionHoning
    will want to quote them. Asserting the improvement ratio here fixes the number that the extrusion
    honing class has to reproduce, so the two cannot drift.
    '''

    asBuilt      = roughnessTable('lpbf as-built')
    afterHoning  = roughnessTable('lpbf abrasive flow')
    drawnTube    = roughnessTable('drawn tube')

    assert asBuilt / afterHoning == pytest.approx(4.0, rel = 0.01), \
        'Abrasive flow machining should improve LPBF internal roughness by a factor of 4'
    assert asBuilt / drawnTube > 10.0, \
        'As-built LPBF must be more than an order of magnitude rougher than drawn tube, which is ' \
        'the claim that makes additive manifold pressure drop a real problem'

# ---------------------------------------------------------------------------------------------- #
# -- Tier 3: self-consistency and query behaviour -- #
# ---------------------------------------------------------------------------------------------- #

def testTemperatureClampingIsRecordedNotSilent():

    '''
    Outside the validated range the query clamps rather than extrapolating, and it must say so. A
    silent clamp is worse than an extrapolation because it looks like a valid answer.
    '''

    result = queryMaterial('7075', 't73', 900.0)

    assert result['extrapolated'], \
        'Querying 7075 at 900 K is far outside its validated range and must be flagged'
    assert any('CLAMPED' in note for note in result['databaseNotes']), \
        'The clamp must appear in databaseNotes, not just in the extrapolated list'

def testClampedValueEqualsRangeEndpoint():

    '''
    A clamped property must equal the value at the range endpoint exactly. If it does not, the
    clamp is being applied to the wrong quantity.
    '''

    atLimit   = queryMaterial('7075', 't73', 450.0)['yieldStrength']
    beyond    = queryMaterial('7075', 't73', 900.0)['yieldStrength']

    assert beyond == pytest.approx(atLimit, rel = 1e-12), \
        'A clamped query must return the endpoint value, not an extrapolated one'

def testAllowableDoesNotFallBackToTypical():

    '''
    The most dangerous possible behaviour would be returning a typical value when an A-basis was
    asked for. 316L has no A-basis in this database, only a specification minimum, so the query
    must say so rather than quietly handing back the typical number.
    '''

    result = queryMaterial('316L', 'annealed', 293.15, basis = 'A')

    assert result['basisAvailable'] is False, \
        '316L has no A-basis in this database and the query must not claim otherwise'
    assert any('No A-basis' in note for note in result['databaseNotes']), \
        'The absence of an allowable has to be stated, not inferred from a flag'

def testShortTransverseAbsenceIsReported():

    '''
    Ti-6Al-4V sheet has no short transverse allowable, because sheet has no meaningful short
    transverse direction. Asking for one must return None with an explanation rather than silently
    substituting the longitudinal value, which would be unconservative.
    '''

    result = queryMaterial('Ti-6Al-4V', 'annealed', 293.15, orientation = 'ST', basis = 'A')

    assert result['yieldStrength'] is None
    assert any('short transverse' in note.lower() for note in result['databaseNotes'])

def testShortTransverseIsNeverStrongerThanLongitudinal():

    '''
    A universal invariant of wrought product. Grain flow runs longitudinally, so ST properties are
    always the weakest. A record violating this has transposed its orientations.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            for basis, block in condition.get('allowables', {}).items():
                for name, oriented in block.items():
                    longitudinal    = oriented.get('L')
                    shortTransverse = oriented.get('ST')
                    if longitudinal is None or shortTransverse is None:
                        continue
                    assert shortTransverse <= longitudinal, \
                        f'{key} / {conditionKey} / {basis} / {name}: short transverse ' \
                        f'({shortTransverse / 1.0e6:.0f} MPa) exceeds longitudinal ' \
                        f'({longitudinal / 1.0e6:.0f} MPa). The orientations are transposed.'

def testAbasisIsNeverAboveBbasis():

    '''
    A-basis is a 99 percent exceedance and B-basis is 90 percent, so A is always the lower number.
    Inverting them is an easy and dangerous transposition.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            allowables = condition.get('allowables', {})
            if 'A' not in allowables or 'B' not in allowables:
                continue
            for name in allowables['A']:
                for orientation in ORIENTATIONS:
                    aValue = allowables['A'][name].get(orientation)
                    bValue = allowables['B'].get(name, {}).get(orientation)
                    if aValue is None or bValue is None:
                        continue
                    assert aValue <= bValue, \
                        f'{key} / {conditionKey} / {name} / {orientation}: A-basis ' \
                        f'({aValue / 1.0e6:.0f}) exceeds B-basis ({bValue / 1.0e6:.0f}). ' \
                        f'They are transposed.'

def testAllowablesNeverExceedTypical():

    '''
    An allowable is a lower tolerance limit on the population, so it cannot exceed the typical
    value. A record that violates this has mixed a specification minimum from one product form with
    a typical value from another.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            typical = condition.get('typical', {})
            for basis, block in condition.get('allowables', {}).items():
                for name, oriented in block.items():
                    if name not in typical:
                        continue
                    value = oriented.get('L')
                    if value is None:
                        continue
                    assert value <= typical[name] * 1.02, \
                        f'{key} / {conditionKey} / {basis} / {name}: allowable ' \
                        f'{value / 1.0e6:.0f} MPa exceeds the typical value ' \
                        f'{typical[name] / 1.0e6:.0f} MPa'

def testYieldNeverExceedsUltimate():

    '''
    True for every metal in every condition. Catches a transposed pair, which is easy to introduce
    and produces a negative margin that looks like a design problem rather than a data problem.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey, condition in record['conditions'].items():
            typical = condition['typical']
            if 'transverseStrength' in typical:
                continue      # composite lamina, where the two are the same by definition
            assert typical['yieldStrength'] <= typical['ultimateStrength'], \
                f'{key} / {conditionKey}: yield exceeds ultimate. They are transposed.'

def testTitaniumInOxygenRaises():

    '''
    The hard prohibition, enforced in code rather than documented. Titanium is impact sensitive in
    oxygen and it burns. This must raise exactly the way Seal.checkCompatibility raises on Buna-N
    in hydrazine.
    '''

    database = MaterialDatabase()
    database.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed'})

    with pytest.raises(CompatibilityError):
        database.checkCompatibility('LOX')

    with pytest.raises(CompatibilityError):
        database.checkCompatibility('GOX')

def testMonelInHydrazineRaises():

    '''
    Copper catalyses hydrazine decomposition, so every copper bearing alloy is prohibited. Monel is
    the one that catches people out, because it is otherwise an excellent propulsion alloy.
    '''

    database = MaterialDatabase()
    database.setInputs({'material': 'Monel 400', 'condition': 'annealed'})

    with pytest.raises(CompatibilityError):
        database.checkCompatibility('N2H4')

def testUnknownFluidWarnsRatherThanPasses():

    '''
    Absence of a prohibition is not evidence of compatibility, and the query must say so rather
    than returning silently and letting the caller infer approval.
    '''

    database = MaterialDatabase()
    database.setInputs({'material': '316L', 'condition': 'annealed'})
    notes = database.checkCompatibility('chlorine trifluoride')

    assert any('not evidence of compatibility' in note for note in notes)

def testEveryCopperBaseAlloyProhibitsHydrazine():

    '''
    A completeness check rather than a spot check. Adding a new copper-base alloy without the
    hydrazine prohibition fails here.

    The threshold is 10 percent, and the reason it is not lower is a real distinction rather than a
    convenience. The prohibition is on copper-BASE alloys, where copper is the matrix and is
    available to catalyse decomposition at the wetted surface: Monel at 30 percent, GRCop at 88,
    NARloy at 96, CuCrZr at 99. The precipitation hardening stainless grades carry 3 to 4 percent
    copper bound as precipitates inside a passivated chromium oxide matrix, and 17-4PH is in fact
    used in hydrazine service. Setting the threshold at 3 percent would flag those and be wrong.

    17-4PH and 15-5PH carry the copper content in their chemistry block regardless, so a programme
    that does restrict them can find them.
    '''

    for key, record in MATERIAL_DATABASE.items():
        copperContent = record.get('chemistry', {}).get('copper', 0.0)
        if copperContent < 10.0:
            continue
        prohibited = ' '.join(record['incompatible']).upper()
        assert 'N2H4' in prohibited, \
            f'{key} is a copper-base alloy at {copperContent} percent copper but does not ' \
            f'prohibit hydrazine. Copper catalyses hydrazine decomposition.'

def testProvenanceResolvesAndFlagsEstimates():

    '''
    An author estimate must be identifiable as one. AlSi10Mg LPBF data is estimated in this
    database and must report itself that way.
    '''

    traceable = getProvenance('Ti-6Al-4V', 'annealed', 'allowables')
    assert traceable['basisClass'] == 'statistical'

    estimated = getProvenance('AlSi10Mg', 'lpbf as-built', 'typical')
    assert estimated['basisClass'] == 'estimate', \
        'LPBF aluminium properties are not traceable and must not present as though they were'

def testListMaterialsFiltersByFamily():

    '''
    The candidate set builder MaterialSelector depends on.
    '''

    titanium = listMaterials(family = 'titanium')
    assert len(titanium) >= 4
    assert all('TI' in key.upper() or 'CP TI' in key.upper() for key, _ in titanium)

    everything = listMaterials()
    assert len(everything) == sum(len(record['conditions'])
                                  for record in MATERIAL_DATABASE.values())

def testGetTemperatureCurveIsMonotonicForAluminium():

    '''
    Aluminium loses strength monotonically as it heats. A curve that rises somewhere in the middle
    means two breakpoints are out of order.
    '''

    database = MaterialDatabase()
    database.setInputs({'material': '6061', 'condition': 't6'})

    temperatures = np.linspace(293.15, 450.0, 25)
    values       = database.getTemperatureCurve('yieldStrength', temperatures)

    assert np.all(np.diff(values) <= 1.0e-6), \
        'Aluminium yield strength must fall monotonically with temperature above ambient'

def testReportRunsForEveryRecord():

    '''
    A smoke test across the whole database. generateReport touches nearly every field, so a record
    with a missing or wrongly typed value surfaces here rather than in a worked example.
    '''

    for key, record in MATERIAL_DATABASE.items():
        for conditionKey in record['conditions']:
            database = MaterialDatabase()
            database.setInputs({'material': key, 'condition': conditionKey})
            report = database.generateReport()
            assert 'MATERIAL DATASHEET' in report
            assert len(report) > 200, f'{key} / {conditionKey} produced a suspiciously short report'
