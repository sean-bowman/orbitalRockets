
# -- Material Property Database [aerospaceMaterials] -- #

'''

The alloy database: property values, design allowables, temperature dependence and source
traceability for the materials used on launch vehicle hardware.

This is data, not logic. The query logic lives in MaterialDatabase.py, which is what the rest of the
repository should import.

Three things about the structure are deliberate:

    alloy -> condition -> property     The same alloy in two conditions is two materials. 6061-T6 and
                                       6061 as-welded do not share a yield strength and pretending
                                       otherwise is how aluminium weldments get undersized.

    ratio curves, not tables           Temperature dependence is stored as a ratio to the room
                                       temperature value. One curve then corrects the typical value,
                                       the A-basis and the B-basis consistently. Absolute tables
                                       would need three copies that could disagree with each other.

    sources beside the values          A parallel dotted-path map rather than wrapping every number
                                       in {'value': ..., 'source': ...}. Keeps the data readable and
                                       keeps np.interp usable on a curve. Traceability is enforced by
                                       a test that walks every leaf, not by the structure.

The nine alloys that orbitalRockets/common/materials.py already carries are NOT re-typed here. Their
room-temperature scalars are imported and merged at module load, so there is exactly one place in the
repository where 316L's yield strength is written down. What is typed below for those nine is only
what common does not have: extra conditions, allowables, temperature curves, fracture and fatigue
data, and sources.

WARNING ON USE: a typical value is not a design allowable. Where an 'allowables' block is absent, no
A-basis or B-basis exists in this database for that condition, and the honest answer to 'what is the
design value' is that it has to be established. The Allowables class exists for exactly that.

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import materialProperties
except ImportError:
    from .utils import materialProperties

# ------------------------------------------------------------------------------------------------ #
# -- Source Registry -- #
# ------------------------------------------------------------------------------------------------ #

# Every numeric property in MATERIAL_DATABASE carries a key into this registry. The basisClass field
# is the one that matters: it is the difference between a number you can put in a stress report and a
# number that is somebody's recollection.
#
#   statistical    A computed tolerance limit from a real sample. MMPDS A-basis and B-basis.
#   spec minimum   A specification guaranteed minimum. Conservative, but not a statistical basis.
#   typical        A handbook central value. Roughly the mean. NOT a design value.
#   estimate       Author estimate. Preliminary trade only. Do not cite.

SOURCES = {
    'MMPDS-STATISTICAL': {
        'document': 'MMPDS-18', 'year': 2023, 'basisClass': 'statistical', 'confidence': 'high',
        'note': 'Computed A-basis or B-basis tolerance limit. Orientation and product form specific.'
    },
    'MMPDS-TYPICAL': {
        'document': 'MMPDS-18', 'year': 2023, 'basisClass': 'typical', 'confidence': 'high',
        'note': 'Handbook typical value. Approximately the sample mean, not a design allowable.'
    },
    'MMPDS-CURVE': {
        'document': 'MMPDS-18', 'year': 2023, 'basisClass': 'typical', 'confidence': 'high',
        'note': 'Percent-of-room-temperature curve. MMPDS publishes these as ratios, which is why '
                'this database stores them that way.'
    },
    'AMS-SPEC': {
        'document': 'SAE AMS material specification', 'basisClass': 'spec minimum', 'confidence': 'high',
        'note': 'Specification guaranteed minimum. Every lot meets it; the population mean is higher.'
    },
    'ASTM-SPEC': {
        'document': 'ASTM material specification', 'basisClass': 'spec minimum', 'confidence': 'high',
        'note': 'Specification guaranteed minimum.'
    },
    'ASME-II-D': {
        'document': 'ASME BPVC Section II Part D', 'basisClass': 'spec minimum', 'confidence': 'high',
        'note': 'Code allowable stress and elevated temperature property tables.'
    },
    'COMMON-SEED': {
        'document': 'orbitalRockets/common/materials.py', 'basisClass': 'typical', 'confidence': 'medium',
        'note': 'Merged at import from the shared lookup so the two cannot drift. Handbook typical '
                'values for preliminary sizing.'
    },
    'NIST-CRYO': {
        'document': 'NIST Cryogenic Material Properties Database', 'basisClass': 'typical',
        'confidence': 'high', 'note': 'Low temperature property fits, 4 K to 300 K.'
    },
    'DAMAGE-TOLERANT-HANDBOOK': {
        'document': 'Damage Tolerant Design Handbook, CINDAS/USAF', 'basisClass': 'typical',
        'confidence': 'medium', 'note': 'Fracture toughness and da/dN data. Scatter is wide; these '
                'are central values and a design use needs the lower bound.'
    },
    'NASA-SP-8040': {
        'document': 'NASA SP-8040, Fracture Control of Metallic Pressure Vessels',
        'basisClass': 'typical', 'confidence': 'medium', 'note': 'K_ISCC and sustained load data.'
    },
    'MIL-STD-889': {
        'document': 'MIL-STD-889C, Dissimilar Metals', 'basisClass': 'spec minimum',
        'confidence': 'high', 'note': 'Anodic index for galvanic couple screening.'
    },
    'NASA-GRCOP': {
        'document': 'NASA/TM GRCop-42 and GRCop-84 property reports', 'basisClass': 'typical',
        'confidence': 'medium', 'note': 'Additively manufactured copper alloy properties. The '
                'database is still maturing and lot to lot scatter is significant.'
    },
    'CMH-17': {
        'document': 'CMH-17, Composite Materials Handbook', 'basisClass': 'statistical',
        'confidence': 'high', 'note': 'Composite lamina allowables. Layup and cure specific.'
    },
    'ESTIMATE-2026Q1': {
        'document': 'Author estimate', 'basisClass': 'estimate', 'confidence': 'low',
        'note': 'NOT TRACEABLE. Preliminary trade only. Do not cite in a stress report.'
    }
}

# ------------------------------------------------------------------------------------------------ #
# -- Aliases -- #
# ------------------------------------------------------------------------------------------------ #

# Normalization is strip().upper() with internal whitespace collapsed, matching the behaviour of
# common/materials.py so its nine keys pass through unchanged. Everything else resolves through here.

MATERIAL_ALIASES = {
    'TI6AL4V': 'TI-6AL-4V',     'TI-64': 'TI-6AL-4V',        'GRADE 5': 'TI-6AL-4V',
    'R56400': 'TI-6AL-4V',      'TI-6-4': 'TI-6AL-4V',
    'TI6AL4V ELI': 'TI-6AL-4V ELI',  'GRADE 23': 'TI-6AL-4V ELI',  'R56407': 'TI-6AL-4V ELI',
    'IN718': 'INCONEL 718',     'ALLOY 718': 'INCONEL 718',  'N07718': 'INCONEL 718',
    'IN625': 'INCONEL 625',     'ALLOY 625': 'INCONEL 625',  'N06625': 'INCONEL 625',
    'MONEL': 'MONEL 400',       'N04400': 'MONEL 400',       'K500': 'MONEL K-500',
    'N05500': 'MONEL K-500',
    'SS304L': '304L',           'S30403': '304L',            '304 L': '304L',
    'SS316L': '316L',           'S31603': '316L',            '316 L': '316L',
    'SS321': '321',             'S32100': '321',             'S34700': '347',
    '17-4': '17-4PH',           '17-4 PH': '17-4PH',         'S17400': '17-4PH',
    '15-5': '15-5PH',           '15-5 PH': '15-5PH',         'S15500': '15-5PH',
    'A-286': 'A286',            'S66286': 'A286',
    'AL2219': '2219',           '2219-T87': '2219',          'AL 2219': '2219',
    'AL2195': '2195',           '2195-T8': '2195',           'AL-LI': '2195',
    'AL2024': '2024',           '2024-T3': '2024',
    'AL6061': '6061',           '6061-T6': '6061',           'AL 6061': '6061',
    'AL7075': '7075',           '7075-T73': '7075',          '7075-T6': '7075',
    'AL7050': '7050',           '7050-T7451': '7050',
    'ALSI10MG': 'ALSI10MG',
    'GRCOP42': 'GRCOP-42',      'GRCOP 42': 'GRCOP-42',
    'NARLOY Z': 'NARLOY-Z',
    'CUCRZR': 'C18150',         'C18200': 'C18150',
    'AISI 4340': '4340',        'SAE 4340': '4340',
    'CP TI': 'CP TI GRADE 2',   'GRADE 2': 'CP TI GRADE 2',  'R50400': 'CP TI GRADE 2',
    'TI3AL2.5V': 'TI-3AL-2.5V', 'GRADE 9': 'TI-3AL-2.5V'
}

# ------------------------------------------------------------------------------------------------ #
# -- Shared Curve Shapes -- #
# ------------------------------------------------------------------------------------------------ #

# Temperature grids reused across families, so a curve is a set of ratios against a named grid rather
# than a pair of arrays repeated forty times.

CRYO_TO_HOT_GRID  = np.array([20.0, 77.0, 200.0, 293.15, 400.0, 500.0, 600.0, 700.0])
CRYO_TO_WARM_GRID = np.array([20.0, 77.0, 200.0, 293.15, 350.0, 400.0, 450.0])
HOT_GRID          = np.array([293.15, 400.0, 600.0, 800.0, 1000.0, 1100.0, 1200.0])

# ------------------------------------------------------------------------------------------------ #
# -- The Database -- #
# ------------------------------------------------------------------------------------------------ #

MATERIAL_DATABASE = {}

# -- Aluminium Alloys -- #
#
# The launch vehicle structural default. Low density, cheap, easy to machine, and every one of them
# has a catch: 2219 is weldable but not strong, 7075 is strong but neither weldable nor SCC resistant,
# 2195 is both but costs a fortune and needs a qualified supply chain.

MATERIAL_DATABASE['2219'] = {
    'commonName': '2219-T87 (Al-Cu)', 'family': 'aluminium 2xxx', 'uns': 'A92219',
    'crystalStructure': 'fcc', 'density': 2840.0, 'poissonRatio': 0.33,
    'meltingRange': (816.0, 911.0), 'anodicIndex': 0.90, 'relativeCost': 1.4,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 14, 'plate': 18, 'bar': 12, 'forging': 30, 'extrusion': 16},
    'specifications': ['AMS 4031 (sheet)', 'AMS 4143 (forging)', 'AMS-QQ-A-250/30 (plate)'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'RP-1', 'GHE', 'GN2', 'WATER'],
    'notes': 'The cryogenic tank alloy. Weldable, tough at LH2 temperature, and LOX compatible, which '
             'is the combination almost nothing else offers. The Shuttle external tank was 2219 '
             'before it was 2195. Strength is modest: it buys you weldability.',
    'conditions': {
        't87': {
            'description': 'Solution treated, cold worked 7 percent, artificially aged',
            'forms': ['sheet', 'plate', 'bar', 'extrusion'], 'thicknessRange': (0.0005, 0.150),
            'typical': {'yieldStrength': 393.0e6, 'ultimateStrength': 476.0e6, 'elongation': 0.10,
                        'reductionOfArea': 0.20, 'elasticModulus': 73.1e9, 'shearModulus': 27.0e9,
                        'bearingUltimate': 855.0e6, 'hardness': 130.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 345.0e6, 'LT': 338.0e6, 'ST': 331.0e6},
                      'ultimateStrength': {'L': 427.0e6, 'LT': 427.0e6, 'ST': 414.0e6}},
                'B': {'yieldStrength': {'L': 359.0e6, 'LT': 352.0e6, 'ST': 345.0e6},
                      'ultimateStrength': {'L': 441.0e6, 'LT': 441.0e6, 'ST': 427.0e6}}},
            'thermal': {'thermalConductivity': 120.0, 'specificHeat': 864.0,
                        'thermalExpansion': 22.3e-6, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 36.0e6, 'T-L': 31.0e6},
                         'parisCoefficient': 1.6e-11, 'parisExponent': 3.2,
                         'thresholdRange': 2.9e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 780.0e6, 'basquinExponent': -0.105,
                        'enduranceStress': 105.0e6, 'runoutCycles': 5.0e8, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'salt fog': 275.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.97},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.34, 1.28, 1.09, 1.00, 0.93, 0.82, 0.62]),
                'ultimateRatio':     np.array([1.48, 1.40, 1.13, 1.00, 0.91, 0.78, 0.57]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.97, 0.94, 0.90]),
                'conductivityRatio': np.array([0.30, 0.55, 0.90, 1.00, 1.03, 1.06, 1.08]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.15, 1.12, 1.04, 1.00, 0.98, 0.95, 0.90]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'MMPDS-TYPICAL', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        },
        'as-welded': {
            'description': 'GTAW or FSW, as-welded, no post-weld heat treatment',
            'forms': ['plate', 'sheet'], 'thicknessRange': (0.001, 0.050),
            'typical': {'yieldStrength': 165.0e6, 'ultimateStrength': 250.0e6, 'elongation': 0.04,
                        'elasticModulus': 73.1e9},
            'thermal': {'thermalConductivity': 120.0, 'specificHeat': 864.0,
                        'thermalExpansion': 22.3e-6},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.30, 1.25, 1.08, 1.00, 0.92, 0.80, 0.60]),
                'ultimateRatio':     np.array([1.42, 1.36, 1.12, 1.00, 0.90, 0.76, 0.55]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.97, 0.94, 0.90]),
                'conductivityRatio': np.array([0.30, 0.55, 0.90, 1.00, 1.03, 1.06, 1.08]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'thermal': 'MMPDS-TYPICAL',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['2195'] = {
    'commonName': '2195-T8 (Al-Li)', 'family': 'aluminium-lithium', 'uns': 'A92195',
    'crystalStructure': 'fcc', 'density': 2710.0, 'poissonRatio': 0.33,
    'meltingRange': (843.0, 916.0), 'anodicIndex': 0.90, 'relativeCost': 4.5,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'plate': 32, 'sheet': 30, 'forging': 44, 'extrusion': 34},
    'specifications': ['AMS 4472 (plate)'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'RP-1', 'GHE', 'GN2'],
    'notes': 'Lithium lowers density and raises modulus at the same time, which is why it replaced '
             '2219 on the Shuttle super lightweight tank for a 3400 kg saving. The catch is supply '
             'chain: few mills, long lead times, and anisotropy that punishes a designer who ignores '
             'short transverse properties.',
    'conditions': {
        't8': {
            'description': 'Solution treated, cold worked, artificially aged',
            'forms': ['plate', 'sheet', 'extrusion'], 'thicknessRange': (0.002, 0.100),
            'typical': {'yieldStrength': 545.0e6, 'ultimateStrength': 580.0e6, 'elongation': 0.08,
                        'reductionOfArea': 0.16, 'elasticModulus': 76.5e9, 'shearModulus': 28.5e9,
                        'bearingUltimate': 985.0e6, 'hardness': 165.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 496.0e6, 'LT': 462.0e6, 'ST': 434.0e6},
                      'ultimateStrength': {'L': 531.0e6, 'LT': 510.0e6, 'ST': 476.0e6}},
                'B': {'yieldStrength': {'L': 517.0e6, 'LT': 483.0e6, 'ST': 455.0e6},
                      'ultimateStrength': {'L': 552.0e6, 'LT': 531.0e6, 'ST': 496.0e6}}},
            'thermal': {'thermalConductivity': 84.0, 'specificHeat': 900.0,
                        'thermalExpansion': 21.6e-6, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 33.0e6, 'T-L': 27.0e6},
                         'parisCoefficient': 2.1e-11, 'parisExponent': 3.3,
                         'thresholdRange': 2.4e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 920.0e6, 'basquinExponent': -0.098,
                        'enduranceStress': 145.0e6, 'runoutCycles': 5.0e8, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'salt fog': 240.0e6},
                              'sccRating': {'L': 'high', 'LT': 'moderate', 'ST': 'low'},
                              'hydrogenRatio': 0.95},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.30, 1.25, 1.08, 1.00, 0.94, 0.85, 0.68]),
                'ultimateRatio':     np.array([1.40, 1.34, 1.11, 1.00, 0.92, 0.81, 0.63]),
                'modulusRatio':      np.array([1.11, 1.09, 1.04, 1.00, 0.97, 0.94, 0.90]),
                'conductivityRatio': np.array([0.32, 0.58, 0.91, 1.00, 1.03, 1.06, 1.09]),
                'expansionRatio':    np.array([0.42, 0.56, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.18, 1.14, 1.05, 1.00, 0.97, 0.94, 0.89]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['2024'] = {
    'commonName': '2024-T3 (Al-Cu-Mg)', 'family': 'aluminium 2xxx', 'uns': 'A92024',
    'crystalStructure': 'fcc', 'density': 2780.0, 'poissonRatio': 0.33,
    'meltingRange': (775.0, 911.0), 'anodicIndex': 0.85, 'relativeCost': 1.1,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 6, 'plate': 8, 'bar': 6, 'extrusion': 10},
    'specifications': ['AMS 4037 (sheet and plate)', 'AMS 4120 (bar)'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY', 'SEAWATER UNCLAD'],
    'compatible': ['RP-1', 'GHE', 'GN2', 'HYDRAULIC OIL'],
    'notes': 'The airframe workhorse and a poor launch vehicle choice. Excellent damage tolerance and '
             'fatigue life, but it is not weldable, it corrodes readily unless clad, and its LOX '
             'compatibility is not established. Present here as the comparison baseline everyone '
             'reaches for, not as a recommendation.',
    'conditions': {
        't3': {
            'description': 'Solution treated, cold worked, naturally aged',
            'forms': ['sheet', 'plate'], 'thicknessRange': (0.0003, 0.025),
            'typical': {'yieldStrength': 345.0e6, 'ultimateStrength': 483.0e6, 'elongation': 0.18,
                        'reductionOfArea': 0.30, 'elasticModulus': 73.1e9, 'shearModulus': 27.6e9,
                        'bearingUltimate': 890.0e6, 'hardness': 120.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 290.0e6, 'LT': 269.0e6, 'ST': None},
                      'ultimateStrength': {'L': 434.0e6, 'LT': 427.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 303.0e6, 'LT': 283.0e6, 'ST': None},
                      'ultimateStrength': {'L': 448.0e6, 'LT': 441.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 121.0, 'specificHeat': 875.0,
                        'thermalExpansion': 23.2e-6, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 37.0e6, 'T-L': 32.0e6},
                         'parisCoefficient': 1.4e-11, 'parisExponent': 3.1,
                         'thresholdRange': 2.9e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 900.0e6, 'basquinExponent': -0.108,
                        'enduranceStress': 138.0e6, 'runoutCycles': 5.0e8, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'salt fog': 100.0e6},
                              'sccRating': {'L': 'high', 'LT': 'moderate', 'ST': 'low'},
                              'hydrogenRatio': 0.96},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.28, 1.23, 1.07, 1.00, 0.94, 0.84, 0.63]),
                'ultimateRatio':     np.array([1.38, 1.33, 1.11, 1.00, 0.91, 0.78, 0.56]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.97, 0.94, 0.90]),
                'conductivityRatio': np.array([0.31, 0.56, 0.90, 1.00, 1.03, 1.06, 1.08]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.14, 1.11, 1.04, 1.00, 0.98, 0.95, 0.90]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'MMPDS-TYPICAL', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['6061'] = {
    'commonName': '6061 (Al-Mg-Si)', 'family': 'aluminium 6xxx', 'uns': 'A96061',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (855.0, 925.0), 'anodicIndex': 0.90, 'relativeCost': 0.6,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 3, 'plate': 4, 'bar': 2, 'forging': 16, 'extrusion': 4, 'tube': 3},
    'specifications': ['AMS 4027 (sheet and plate)', 'AMS 4117 (bar)', 'AMS 4173 (extrusion)'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'RP-1', 'N2H4', 'GHE', 'GN2', 'WATER'],
    'notes': None,   # seeded from common
    'conditions': {
        't6': {
            'description': 'Solution treated and artificially aged',
            'forms': ['sheet', 'plate', 'bar', 'extrusion', 'tube'], 'thicknessRange': (0.0005, 0.200),
            'typical': {'elongation': 0.12, 'reductionOfArea': 0.35, 'shearModulus': 26.0e9,
                        'bearingUltimate': 600.0e6, 'hardness': 95.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 241.0e6, 'LT': 241.0e6, 'ST': 234.0e6},
                      'ultimateStrength': {'L': 290.0e6, 'LT': 290.0e6, 'ST': 283.0e6}},
                'B': {'yieldStrength': {'L': 252.0e6, 'LT': 252.0e6, 'ST': 245.0e6},
                      'ultimateStrength': {'L': 303.0e6, 'LT': 303.0e6, 'ST': 296.0e6}}},
            'thermal': {'specificHeat': 896.0, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 29.0e6, 'T-L': 26.0e6},
                         'parisCoefficient': 1.9e-11, 'parisExponent': 3.2,
                         'thresholdRange': 3.2e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 520.0e6, 'basquinExponent': -0.102,
                        'enduranceStress': 96.5e6, 'runoutCycles': 5.0e8, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'salt fog': 200.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.98},
            'quenchFactor': {'k1': -0.00501, 'k2': 2.2e-19, 'k3': 5190.0, 'k4': 850.0, 'k5': 180200.0},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.25, 1.21, 1.06, 1.00, 0.93, 0.79, 0.53]),
                'ultimateRatio':     np.array([1.42, 1.35, 1.11, 1.00, 0.89, 0.72, 0.46]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.97, 0.93, 0.89]),
                'conductivityRatio': np.array([0.55, 0.72, 0.94, 1.00, 1.02, 1.04, 1.06]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.12, 1.09, 1.03, 1.00, 0.98, 0.95, 0.91]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'COMMON-SEED', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'MMPDS-TYPICAL', 'environmental': 'NASA-SP-8040',
                        'quenchFactor': 'ESTIMATE-2026Q1', 'temperatureCurves': 'MMPDS-CURVE'}
        },
        'as-welded': {
            # The single most important row in this file for anyone welding aluminium. 6061-T6 loses
            # roughly 40 percent of its yield in the heat affected zone and does not recover without a
            # full solution treat and age. Weld.HAZ_KNOCKDOWN in fluidSystems carries the same factor
            # and a test asserts the two agree.
            'description': 'GTAW with 4043 or 5356 filler, as-welded, no post-weld heat treatment',
            'forms': ['sheet', 'plate', 'tube'], 'thicknessRange': (0.001, 0.050),
            'typical': {'yieldStrength': 138.0e6, 'ultimateStrength': 186.0e6, 'elongation': 0.06,
                        'elasticModulus': 68.9e9},
            'thermal': {'thermalConductivity': 167.0, 'specificHeat': 896.0,
                        'thermalExpansion': 23.6e-6},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.22, 1.18, 1.05, 1.00, 0.92, 0.77, 0.50]),
                'ultimateRatio':     np.array([1.38, 1.31, 1.10, 1.00, 0.88, 0.70, 0.44]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.97, 0.93, 0.89]),
                'conductivityRatio': np.array([0.55, 0.72, 0.94, 1.00, 1.02, 1.04, 1.06]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'thermal': 'COMMON-SEED',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['7075'] = {
    'commonName': '7075 (Al-Zn-Mg-Cu)', 'family': 'aluminium 7xxx', 'uns': 'A97075',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (750.0, 908.0), 'anodicIndex': 0.85, 'relativeCost': 0.9,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'plate': 5, 'bar': 4, 'forging': 20, 'extrusion': 6},
    'specifications': ['AMS 4078 (plate T7351)', 'AMS 4147 (forging T73)'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY', 'SUSTAINED ST TENSION IN MARINE AIR'],
    'compatible': ['RP-1', 'GHE', 'GN2', 'HYDRAULIC OIL'],
    'notes': None,   # seeded from common
    'conditions': {
        't73': {
            'description': 'Solution treated and overaged for stress corrosion resistance',
            'forms': ['plate', 'bar', 'forging', 'extrusion'], 'thicknessRange': (0.003, 0.150),
            'typical': {'elongation': 0.11, 'reductionOfArea': 0.25, 'shearModulus': 26.9e9,
                        'bearingUltimate': 945.0e6, 'hardness': 145.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 386.0e6, 'LT': 372.0e6, 'ST': 359.0e6},
                      'ultimateStrength': {'L': 462.0e6, 'LT': 455.0e6, 'ST': 441.0e6}},
                'B': {'yieldStrength': {'L': 400.0e6, 'LT': 386.0e6, 'ST': 372.0e6},
                      'ultimateStrength': {'L': 476.0e6, 'LT': 469.0e6, 'ST': 455.0e6}}},
            'thermal': {'specificHeat': 960.0, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 31.0e6, 'T-L': 25.0e6},
                         'parisCoefficient': 2.3e-11, 'parisExponent': 3.4,
                         'thresholdRange': 2.5e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 850.0e6, 'basquinExponent': -0.106,
                        'enduranceStress': 159.0e6, 'runoutCycles': 5.0e8, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            # T73 exists to raise this number. T6 in the same alloy has an ST threshold near 50 MPa,
            # which is why 7075-T6 fittings crack in service and 7075-T73 fittings do not.
            'environmental': {'sccThreshold': {'salt fog': 240.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'moderate'},
                              'hydrogenRatio': 0.92},
            'quenchFactor': {'k1': -0.00501, 'k2': 4.1e-13, 'k3': 1050.0, 'k4': 750.0, 'k5': 132400.0},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.22, 1.18, 1.06, 1.00, 0.91, 0.76, 0.48]),
                'ultimateRatio':     np.array([1.30, 1.26, 1.09, 1.00, 0.88, 0.71, 0.43]),
                'modulusRatio':      np.array([1.11, 1.09, 1.04, 1.00, 0.96, 0.92, 0.88]),
                'conductivityRatio': np.array([0.52, 0.70, 0.93, 1.00, 1.03, 1.05, 1.07]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.10, 1.08, 1.03, 1.00, 0.98, 0.95, 0.91]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'COMMON-SEED', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'MMPDS-TYPICAL', 'environmental': 'NASA-SP-8040',
                        'quenchFactor': 'ESTIMATE-2026Q1', 'temperatureCurves': 'MMPDS-CURVE'}
        },
        't6': {
            'description': 'Solution treated and peak aged. Higher strength, poor SCC resistance.',
            'forms': ['plate', 'bar', 'extrusion'], 'thicknessRange': (0.001, 0.100),
            'typical': {'yieldStrength': 503.0e6, 'ultimateStrength': 572.0e6, 'elongation': 0.09,
                        'reductionOfArea': 0.20, 'elasticModulus': 71.7e9, 'shearModulus': 26.9e9,
                        'bearingUltimate': 1050.0e6, 'hardness': 175.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 462.0e6, 'LT': 448.0e6, 'ST': 434.0e6},
                      'ultimateStrength': {'L': 524.0e6, 'LT': 517.0e6, 'ST': 496.0e6}},
                'B': {'yieldStrength': {'L': 476.0e6, 'LT': 462.0e6, 'ST': 448.0e6},
                      'ultimateStrength': {'L': 538.0e6, 'LT': 531.0e6, 'ST': 510.0e6}}},
            'thermal': {'thermalConductivity': 130.0, 'specificHeat': 960.0,
                        'thermalExpansion': 23.6e-6, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 26.0e6, 'T-L': 21.0e6},
                         'parisCoefficient': 2.8e-11, 'parisExponent': 3.5,
                         'thresholdRange': 2.2e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            # This is the row that ends careers. A sustained short transverse tensile stress of
            # 50 MPa in 7075-T6 will crack in marine air. CorrosionAssessment raises on it.
            'environmental': {'sccThreshold': {'salt fog': 50.0e6},
                              'sccRating': {'L': 'high', 'LT': 'moderate', 'ST': 'very low'},
                              'hydrogenRatio': 0.88},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.20, 1.16, 1.05, 1.00, 0.88, 0.70, 0.40]),
                'ultimateRatio':     np.array([1.26, 1.22, 1.08, 1.00, 0.85, 0.65, 0.36]),
                'modulusRatio':      np.array([1.11, 1.09, 1.04, 1.00, 0.96, 0.92, 0.88]),
                'conductivityRatio': np.array([0.52, 0.70, 0.93, 1.00, 1.03, 1.05, 1.07]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.08, 1.06, 1.02, 1.00, 0.98, 0.95, 0.91]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'environmental': 'NASA-SP-8040', 'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['7050'] = {
    'commonName': '7050-T7451', 'family': 'aluminium 7xxx', 'uns': 'A97050',
    'crystalStructure': 'fcc', 'density': 2830.0, 'poissonRatio': 0.33,
    'meltingRange': (761.0, 902.0), 'anodicIndex': 0.85, 'relativeCost': 1.2,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'plate': 8, 'forging': 24, 'extrusion': 10},
    'specifications': ['AMS 4050 (plate)', 'AMS 4333 (forging)'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY'],
    'compatible': ['RP-1', 'GHE', 'GN2'],
    'notes': 'The thick-section 7xxx alloy. Higher copper and zirconium give it far better '
             'hardenability than 7075, so a 150 mm plate develops properties through the thickness '
             'that 7075 cannot. The alloy of choice for large machined fittings and bulkheads.',
    'conditions': {
        't7451': {
            'description': 'Solution treated, stress relieved by stretching, overaged',
            'forms': ['plate', 'forging'], 'thicknessRange': (0.006, 0.150),
            'typical': {'yieldStrength': 455.0e6, 'ultimateStrength': 524.0e6, 'elongation': 0.11,
                        'reductionOfArea': 0.26, 'elasticModulus': 71.0e9, 'shearModulus': 26.9e9,
                        'bearingUltimate': 965.0e6, 'hardness': 150.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 421.0e6, 'LT': 407.0e6, 'ST': 393.0e6},
                      'ultimateStrength': {'L': 490.0e6, 'LT': 483.0e6, 'ST': 469.0e6}},
                'B': {'yieldStrength': {'L': 434.0e6, 'LT': 421.0e6, 'ST': 407.0e6},
                      'ultimateStrength': {'L': 503.0e6, 'LT': 496.0e6, 'ST': 483.0e6}}},
            'thermal': {'thermalConductivity': 157.0, 'specificHeat': 860.0,
                        'thermalExpansion': 23.5e-6, 'emissivity': 0.09},
            'fracture': {'planeStrainToughness': {'L-T': 35.0e6, 'T-L': 29.0e6},
                         'parisCoefficient': 2.0e-11, 'parisExponent': 3.3,
                         'thresholdRange': 2.7e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 830.0e6, 'basquinExponent': -0.104,
                        'enduranceStress': 152.0e6, 'runoutCycles': 5.0e8, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'salt fog': 240.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'moderate'},
                              'hydrogenRatio': 0.93},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.22, 1.18, 1.06, 1.00, 0.91, 0.76, 0.48]),
                'ultimateRatio':     np.array([1.30, 1.26, 1.09, 1.00, 0.88, 0.71, 0.43]),
                'modulusRatio':      np.array([1.11, 1.09, 1.04, 1.00, 0.96, 0.92, 0.88]),
                'conductivityRatio': np.array([0.53, 0.71, 0.93, 1.00, 1.03, 1.05, 1.07]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'toughnessRatio':    np.array([1.11, 1.08, 1.03, 1.00, 0.98, 0.95, 0.91]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['ALSI10MG'] = {
    'commonName': 'AlSi10Mg (LPBF)', 'family': 'aluminium casting alloy, additive',
    'uns': None, 'crystalStructure': 'fcc', 'density': 2670.0, 'poissonRatio': 0.33,
    'meltingRange': (830.0, 869.0), 'anodicIndex': 0.90, 'relativeCost': 6.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'lpbfPowder': 4, 'lpbfPart': 6},
    'specifications': ['ASTM F3318'],
    'incompatible': ['N2O4 ABOVE 333 K', 'MERCURY'],
    'compatible': ['RP-1', 'GHE', 'GN2', 'WATER'],
    'notes': 'The default additive aluminium. Fine cellular silicon network from the rapid '
             'solidification gives as-built properties above cast and near 6061-T6, but stress relief '
             'coarsens it and costs strength. Anisotropy is real: Z direction properties run 5 to 15 '
             'percent below XY.',
    'conditions': {
        'lpbf as-built': {
            'description': 'As-built, no thermal post-processing. Highly stressed.',
            'forms': ['lpbf'], 'thicknessRange': (0.0004, 0.100),
            'typical': {'yieldStrength': 250.0e6, 'ultimateStrength': 420.0e6, 'elongation': 0.06,
                        'elasticModulus': 70.0e9, 'shearModulus': 26.0e9, 'hardness': 120.0},
            'thermal': {'thermalConductivity': 120.0, 'specificHeat': 910.0,
                        'thermalExpansion': 21.0e-6, 'emissivity': 0.20},
            'fracture': {'planeStrainToughness': {'L-T': 22.0e6}, 'parisCoefficient': 4.0e-11,
                         'parisExponent': 3.6, 'thresholdRange': 1.8e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 420.0e6, 'basquinExponent': -0.130,
                        'enduranceStress': 55.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'as-built, Ra 12 um'},
            'anisotropy': {'zYieldRatio': 0.93, 'zUltimateRatio': 0.88, 'zElongationRatio': 0.70},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.24, 1.20, 1.06, 1.00, 0.90, 0.72, 0.42]),
                'ultimateRatio':     np.array([1.34, 1.29, 1.09, 1.00, 0.86, 0.66, 0.38]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.96, 0.92, 0.88]),
                'conductivityRatio': np.array([0.50, 0.69, 0.93, 1.00, 1.03, 1.06, 1.08]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'thermal': 'ESTIMATE-2026Q1',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'anisotropy': 'ESTIMATE-2026Q1', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        },
        'lpbf stress relieved': {
            'description': 'Stress relief 300 C / 2 h. Silicon network coarsens; strength drops.',
            'forms': ['lpbf'], 'thicknessRange': (0.0004, 0.100),
            'typical': {'yieldStrength': 200.0e6, 'ultimateStrength': 320.0e6, 'elongation': 0.10,
                        'elasticModulus': 70.0e9, 'hardness': 95.0},
            'thermal': {'thermalConductivity': 140.0, 'specificHeat': 910.0,
                        'thermalExpansion': 21.0e-6, 'emissivity': 0.20},
            'fatigue': {'basquinCoefficient': 340.0e6, 'basquinExponent': -0.120,
                        'enduranceStress': 60.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'machined'},
            'anisotropy': {'zYieldRatio': 0.96, 'zUltimateRatio': 0.94, 'zElongationRatio': 0.85},
            'temperatureCurves': {
                'temperature': CRYO_TO_WARM_GRID,
                'yieldRatio':        np.array([1.22, 1.18, 1.05, 1.00, 0.91, 0.75, 0.45]),
                'ultimateRatio':     np.array([1.32, 1.27, 1.08, 1.00, 0.87, 0.68, 0.40]),
                'modulusRatio':      np.array([1.12, 1.10, 1.04, 1.00, 0.96, 0.92, 0.88]),
                'conductivityRatio': np.array([0.52, 0.71, 0.94, 1.00, 1.02, 1.05, 1.07]),
                'expansionRatio':    np.array([0.42, 0.55, 0.86, 1.00, 1.04, 1.08, 1.12]),
                'validRange': (20.0, 450.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'thermal': 'ESTIMATE-2026Q1',
                        'fatigue': 'ESTIMATE-2026Q1', 'anisotropy': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

# -- Stainless Steels -- #
#
# The austenitic grades are the fluid system default and the reason is the face-centred cubic lattice:
# no ductile-to-brittle transition, so they stay tough to 4 K. They pay for it in density and in a
# yield strength that is embarrassing next to aluminium. The precipitation hardening grades trade the
# toughness back for strength and are not cryogenic materials.
#
# The chemistry fields feed CorrosionAssessment.calculatePittingResistance. PREN is the number that
# explains why 316L survives a launch site and 304L does not.

MATERIAL_DATABASE['304L'] = {
    'commonName': '304L austenitic stainless', 'family': 'stainless austenitic', 'uns': 'S30403',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (1673.0, 1727.0), 'anodicIndex': 0.50, 'relativeCost': 0.85,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 3, 'plate': 4, 'bar': 3, 'tube': 4, 'forging': 16},
    'specifications': ['ASTM A240 (sheet and plate)', 'ASTM A276 (bar)', 'ASTM A269 (tube)'],
    'chemistry': {'chromium': 18.5, 'nickel': 9.0, 'molybdenum': 0.0, 'nitrogen': 0.05,
                  'tungsten': 0.0, 'carbon': 0.025},
    'incompatible': ['CHLORIDES ABOVE 333 K UNDER TENSION', 'CONCENTRATED H2O2 UNPASSIVATED'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'GHE', 'GN2'],
    'notes': None,   # seeded from common
    'conditions': {
        'annealed': {
            'description': 'Solution annealed 1040 C, water quenched',
            'forms': ['sheet', 'plate', 'bar', 'tube', 'forging'], 'thicknessRange': (0.0002, 0.150),
            'typical': {'elongation': 0.50, 'reductionOfArea': 0.65, 'shearModulus': 77.0e9,
                        'bearingUltimate': 855.0e6, 'hardness': 150.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 170.0e6}, 'ultimateStrength': {'L': 485.0e6}}},
            'thermal': {'specificHeat': 500.0, 'emissivity': 0.28},
            'fracture': {'planeStrainToughness': {'L-T': 200.0e6},
                         'parisCoefficient': 3.0e-12, 'parisExponent': 3.2,
                         'thresholdRange': 6.0e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1050.0e6, 'basquinExponent': -0.110,
                        'enduranceStress': 240.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'boiling MgCl2': 40.0e6, 'marine air': 200.0e6},
                              'sccRating': {'L': 'moderate', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.90, 'pren': 19.3},
            'sensitization': {'carbonContent': 0.025, 'noseTemperature': 948.0,
                              'noseTimeSeconds': 18000.0},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                # The austenitic strength gain on cooling is real and large, and it is driven by
                # strain-induced martensite formation as much as by lattice friction.
                'yieldRatio':        np.array([2.60, 2.50, 1.55, 1.00, 0.83, 0.76, 0.71, 0.67]),
                'ultimateRatio':     np.array([3.10, 2.90, 1.62, 1.00, 0.87, 0.82, 0.78, 0.72]),
                'modulusRatio':      np.array([1.09, 1.07, 1.03, 1.00, 0.96, 0.92, 0.88, 0.84]),
                'conductivityRatio': np.array([0.12, 0.49, 0.79, 1.00, 1.16, 1.30, 1.43, 1.55]),
                'expansionRatio':    np.array([0.48, 0.60, 0.88, 1.00, 1.05, 1.09, 1.13, 1.17]),
                'toughnessRatio':    np.array([0.85, 0.88, 0.96, 1.00, 1.00, 0.99, 0.97, 0.95]),
                'validRange': (4.0, 700.0)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'ASTM-SPEC', 'thermal': 'COMMON-SEED',
                        'fracture': 'DAMAGE-TOLERANT-HANDBOOK', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'NASA-SP-8040', 'sensitization': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'NIST-CRYO'}
        }
    }
}

MATERIAL_DATABASE['316L'] = {
    'commonName': '316L austenitic stainless', 'family': 'stainless austenitic', 'uns': 'S31603',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (1648.0, 1663.0), 'anodicIndex': 0.50, 'relativeCost': 1.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 3, 'plate': 4, 'bar': 3, 'tube': 4, 'forging': 16, 'lpbfPowder': 4},
    'specifications': ['ASTM A240', 'ASTM A276', 'ASTM A269 (tube)', 'ASTM F3184 (LPBF)'],
    'chemistry': {'chromium': 17.0, 'nickel': 12.0, 'molybdenum': 2.5, 'nitrogen': 0.05,
                  'tungsten': 0.0, 'carbon': 0.025},
    'incompatible': ['CHLORIDES ABOVE 333 K UNDER TENSION'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'H2O2', 'GHE', 'GN2'],
    'notes': None,   # seeded from common
    'conditions': {
        'annealed': {
            'description': 'Solution annealed 1040 C, water quenched',
            'forms': ['sheet', 'plate', 'bar', 'tube', 'forging'], 'thicknessRange': (0.0002, 0.150),
            'typical': {'elongation': 0.50, 'reductionOfArea': 0.65, 'shearModulus': 77.0e9,
                        'bearingUltimate': 855.0e6, 'hardness': 150.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 170.0e6}, 'ultimateStrength': {'L': 485.0e6}}},
            'thermal': {'specificHeat': 500.0, 'emissivity': 0.28},
            'fracture': {'planeStrainToughness': {'L-T': 220.0e6},
                         'parisCoefficient': 2.8e-12, 'parisExponent': 3.2,
                         'thresholdRange': 6.5e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1080.0e6, 'basquinExponent': -0.110,
                        'enduranceStress': 250.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            # PREN 25.4 gives a critical pitting temperature near minus 8 C. 316L pits at ambient in a
            # chloride environment, which is exactly what a coastal launch site is.
            'environmental': {'sccThreshold': {'boiling MgCl2': 55.0e6, 'marine air': 240.0e6},
                              'sccRating': {'L': 'moderate', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.92, 'pren': 26.1},
            'sensitization': {'carbonContent': 0.025, 'noseTemperature': 948.0,
                              'noseTimeSeconds': 21600.0},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([2.50, 2.40, 1.52, 1.00, 0.84, 0.77, 0.72, 0.68]),
                'ultimateRatio':     np.array([3.00, 2.80, 1.60, 1.00, 0.88, 0.83, 0.79, 0.74]),
                'modulusRatio':      np.array([1.09, 1.07, 1.03, 1.00, 0.96, 0.92, 0.88, 0.84]),
                'conductivityRatio': np.array([0.12, 0.49, 0.79, 1.00, 1.16, 1.30, 1.43, 1.55]),
                'expansionRatio':    np.array([0.48, 0.60, 0.88, 1.00, 1.05, 1.09, 1.13, 1.17]),
                'toughnessRatio':    np.array([0.86, 0.89, 0.96, 1.00, 1.00, 0.99, 0.97, 0.95]),
                'validRange': (4.0, 700.0)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'ASTM-SPEC', 'thermal': 'COMMON-SEED',
                        'fracture': 'DAMAGE-TOLERANT-HANDBOOK', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'NASA-SP-8040', 'sensitization': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'NIST-CRYO'}
        },
        'lpbf as-built': {
            'description': 'LPBF as-built. Finer cellular structure than wrought; higher yield.',
            'forms': ['lpbf'], 'thicknessRange': (0.0004, 0.100),
            'typical': {'yieldStrength': 480.0e6, 'ultimateStrength': 620.0e6, 'elongation': 0.40,
                        'elasticModulus': 190.0e9, 'shearModulus': 74.0e9, 'hardness': 220.0},
            'thermal': {'thermalConductivity': 15.0, 'specificHeat': 500.0,
                        'thermalExpansion': 16.0e-6, 'emissivity': 0.45},
            'fatigue': {'basquinCoefficient': 950.0e6, 'basquinExponent': -0.135,
                        'enduranceStress': 180.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'as-built, Ra 12 um'},
            'anisotropy': {'zYieldRatio': 0.90, 'zUltimateRatio': 0.93, 'zElongationRatio': 0.80},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.90, 1.85, 1.35, 1.00, 0.86, 0.80, 0.75, 0.70]),
                'ultimateRatio':     np.array([2.30, 2.20, 1.45, 1.00, 0.89, 0.84, 0.80, 0.75]),
                'modulusRatio':      np.array([1.09, 1.07, 1.03, 1.00, 0.96, 0.92, 0.88, 0.84]),
                'conductivityRatio': np.array([0.12, 0.49, 0.79, 1.00, 1.16, 1.30, 1.43, 1.55]),
                'expansionRatio':    np.array([0.48, 0.60, 0.88, 1.00, 1.05, 1.09, 1.13, 1.17]),
                'validRange': (20.0, 700.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'thermal': 'ESTIMATE-2026Q1',
                        'fatigue': 'ESTIMATE-2026Q1', 'anisotropy': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

MATERIAL_DATABASE['321'] = {
    'commonName': '321 titanium-stabilised stainless', 'family': 'stainless austenitic',
    'uns': 'S32100', 'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,
    'meltingRange': (1671.0, 1727.0), 'anodicIndex': 0.50, 'relativeCost': 1.3,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 6, 'plate': 8, 'bar': 6, 'tube': 8},
    'specifications': ['ASTM A240', 'AMS 5510 (sheet)', 'AMS 5570 (tube)'],
    'chemistry': {'chromium': 17.5, 'nickel': 10.0, 'molybdenum': 0.0, 'nitrogen': 0.03,
                  'tungsten': 0.0, 'carbon': 0.05},
    'incompatible': ['CHLORIDES ABOVE 333 K UNDER TENSION'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'GHE', 'GN2'],
    'notes': None,   # seeded from common
    'conditions': {
        'annealed': {
            'description': 'Solution annealed. Titanium ties up carbon as TiC.',
            'forms': ['sheet', 'plate', 'bar', 'tube'], 'thicknessRange': (0.0002, 0.100),
            'typical': {'elongation': 0.45, 'reductionOfArea': 0.60, 'shearModulus': 77.0e9,
                        'bearingUltimate': 900.0e6, 'hardness': 160.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 205.0e6}, 'ultimateStrength': {'L': 515.0e6}}},
            'thermal': {'specificHeat': 500.0, 'emissivity': 0.28},
            'fracture': {'planeStrainToughness': {'L-T': 190.0e6}, 'parisCoefficient': 3.2e-12,
                         'parisExponent': 3.2, 'thresholdRange': 6.0e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1100.0e6, 'basquinExponent': -0.108,
                        'enduranceStress': 260.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'boiling MgCl2': 50.0e6, 'marine air': 220.0e6},
                              'sccRating': {'L': 'moderate', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.91, 'pren': 18.0},
            # The whole point of 321. Stabilisation pushes the sensitization nose out by orders of
            # magnitude, which is why it is the alloy for welded hot gas lines.
            'sensitization': {'carbonContent': 0.05, 'noseTemperature': 973.0,
                              'noseTimeSeconds': 360000.0},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([2.40, 2.30, 1.50, 1.00, 0.86, 0.80, 0.76, 0.73]),
                'ultimateRatio':     np.array([2.85, 2.70, 1.57, 1.00, 0.90, 0.86, 0.83, 0.79]),
                'modulusRatio':      np.array([1.09, 1.07, 1.03, 1.00, 0.96, 0.92, 0.89, 0.85]),
                'conductivityRatio': np.array([0.12, 0.49, 0.79, 1.00, 1.16, 1.30, 1.43, 1.55]),
                'expansionRatio':    np.array([0.48, 0.60, 0.88, 1.00, 1.05, 1.09, 1.13, 1.17]),
                'toughnessRatio':    np.array([0.86, 0.89, 0.96, 1.00, 1.00, 0.99, 0.98, 0.96]),
                'validRange': (4.0, 700.0)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'ASTM-SPEC', 'thermal': 'COMMON-SEED',
                        'fracture': 'DAMAGE-TOLERANT-HANDBOOK', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'NASA-SP-8040', 'sensitization': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'NIST-CRYO'}
        }
    }
}

MATERIAL_DATABASE['347'] = {
    'commonName': '347 niobium-stabilised stainless', 'family': 'stainless austenitic',
    'uns': 'S34700', 'crystalStructure': 'fcc', 'density': 8000.0, 'poissonRatio': 0.29,
    'meltingRange': (1671.0, 1727.0), 'anodicIndex': 0.50, 'relativeCost': 1.4,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 8, 'plate': 10, 'bar': 8, 'tube': 10},
    'specifications': ['ASTM A240', 'AMS 5512 (sheet)', 'AMS 5646 (bar)'],
    'chemistry': {'chromium': 17.5, 'nickel': 10.5, 'molybdenum': 0.0, 'nitrogen': 0.03,
                  'tungsten': 0.0, 'carbon': 0.05},
    'incompatible': ['CHLORIDES ABOVE 333 K UNDER TENSION'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'GHE', 'GN2'],
    'notes': 'Niobium stabilised rather than titanium stabilised. Preferred over 321 where the part '
             'is welded and then sees a stress relief, because niobium carbide is more stable than '
             'titanium carbide through a second thermal cycle. Common in regenerative chamber liners '
             'and hot gas manifolds.',
    'conditions': {
        'annealed': {
            'description': 'Solution annealed 1050 C',
            'forms': ['sheet', 'plate', 'bar', 'tube'], 'thicknessRange': (0.0002, 0.100),
            'typical': {'yieldStrength': 205.0e6, 'ultimateStrength': 515.0e6, 'elongation': 0.45,
                        'reductionOfArea': 0.60, 'elasticModulus': 193.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 900.0e6, 'hardness': 160.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 205.0e6}, 'ultimateStrength': {'L': 515.0e6}}},
            'thermal': {'thermalConductivity': 16.1, 'specificHeat': 500.0,
                        'thermalExpansion': 16.6e-6, 'emissivity': 0.28},
            'fracture': {'planeStrainToughness': {'L-T': 190.0e6}, 'parisCoefficient': 3.2e-12,
                         'parisExponent': 3.2, 'thresholdRange': 6.0e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1100.0e6, 'basquinExponent': -0.108,
                        'enduranceStress': 260.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'boiling MgCl2': 50.0e6, 'marine air': 220.0e6},
                              'sccRating': {'L': 'moderate', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.91, 'pren': 18.0},
            'sensitization': {'carbonContent': 0.05, 'noseTemperature': 973.0,
                              'noseTimeSeconds': 540000.0},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([2.40, 2.30, 1.50, 1.00, 0.87, 0.82, 0.78, 0.75]),
                'ultimateRatio':     np.array([2.85, 2.70, 1.57, 1.00, 0.91, 0.87, 0.84, 0.81]),
                'modulusRatio':      np.array([1.09, 1.07, 1.03, 1.00, 0.96, 0.92, 0.89, 0.85]),
                'conductivityRatio': np.array([0.12, 0.49, 0.79, 1.00, 1.16, 1.30, 1.43, 1.55]),
                'expansionRatio':    np.array([0.48, 0.60, 0.88, 1.00, 1.05, 1.09, 1.13, 1.17]),
                'toughnessRatio':    np.array([0.86, 0.89, 0.96, 1.00, 1.00, 0.99, 0.98, 0.96]),
                'validRange': (4.0, 700.0)},
            'sources': {'typical': 'ASME-II-D', 'allowables': 'ASTM-SPEC', 'thermal': 'ASME-II-D',
                        'fracture': 'DAMAGE-TOLERANT-HANDBOOK', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'NASA-SP-8040', 'sensitization': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'NIST-CRYO'}
        }
    }
}

MATERIAL_DATABASE['17-4PH'] = {
    'commonName': '17-4PH precipitation hardening stainless', 'family': 'stainless martensitic PH',
    'uns': 'S17400', 'crystalStructure': 'bcc martensite', 'density': 7800.0, 'poissonRatio': 0.272,
    'meltingRange': (1673.0, 1713.0), 'anodicIndex': 0.35, 'relativeCost': 1.6,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 6, 'plate': 10, 'forging': 20, 'lpbfPowder': 5},
    'specifications': ['AMS 5643 (bar)', 'AMS 5604 (plate)', 'ASTM A564'],
    'chemistry': {'chromium': 16.0, 'nickel': 4.0, 'molybdenum': 0.0, 'nitrogen': 0.03,
                  'tungsten': 0.0, 'carbon': 0.05, 'copper': 3.5},
    'incompatible': ['LH2', 'GH2', 'CHLORIDES UNDER SUSTAINED TENSION', 'CRYOGENIC SERVICE'],
    'compatible': ['N2H4', 'MMH', 'RP-1', 'GHE', 'GN2', 'WATER'],
    'notes': 'Martensitic, so it is body-centred cubic and it has a ductile-to-brittle transition. It '
             'is not a cryogenic material regardless of the word stainless in the name. H900 is the '
             'strongest and the most hydrogen and SCC susceptible; H1025 and above trade strength for '
             'toughness and are what should actually be specified. Note the 3.5 percent copper: it is '
             'bound as precipitates in a passivated matrix and 17-4PH is used in hydrazine service, '
             'unlike the copper-base alloys, but some programmes restrict it and it is worth checking '
             'before assuming.',
    'conditions': {
        'h900': {
            'description': 'Solution treated, aged 482 C / 1 h. Peak strength, worst toughness.',
            'forms': ['bar', 'plate', 'forging'], 'thicknessRange': (0.003, 0.200),
            'typical': {'yieldStrength': 1170.0e6, 'ultimateStrength': 1310.0e6, 'elongation': 0.10,
                        'reductionOfArea': 0.40, 'elasticModulus': 196.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 2140.0e6, 'hardness': 420.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 1103.0e6, 'LT': 1103.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1241.0e6, 'LT': 1241.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 1138.0e6, 'LT': 1138.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1276.0e6, 'LT': 1276.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 17.9, 'specificHeat': 460.0,
                        'thermalExpansion': 10.8e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 50.0e6, 'T-L': 45.0e6},
                         'parisCoefficient': 6.0e-12, 'parisExponent': 3.0,
                         'thresholdRange': 4.5e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 2100.0e6, 'basquinExponent': -0.090,
                        'enduranceStress': 590.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            # H900 is severely hydrogen susceptible. Any plating operation on it needs a bake per
            # ASTM F1940, and CorrosionAssessment triggers on the tensile strength.
            'environmental': {'sccThreshold': {'marine air': 200.0e6, 'chlorides': 120.0e6},
                              'sccRating': {'L': 'low', 'LT': 'low', 'ST': 'very low'},
                              'hydrogenRatio': 0.35, 'pren': 16.5},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.20, 1.18, 1.07, 1.00, 0.94, 0.90, 0.84, 0.75]),
                'ultimateRatio':     np.array([1.25, 1.22, 1.08, 1.00, 0.95, 0.91, 0.85, 0.76]),
                'modulusRatio':      np.array([1.08, 1.06, 1.03, 1.00, 0.96, 0.93, 0.89, 0.84]),
                'conductivityRatio': np.array([0.20, 0.55, 0.83, 1.00, 1.12, 1.22, 1.32, 1.41]),
                'expansionRatio':    np.array([0.50, 0.62, 0.89, 1.00, 1.04, 1.08, 1.12, 1.16]),
                # The BCC penalty. Toughness collapses below the transition and no amount of
                # heat treatment recovers it.
                'toughnessRatio':    np.array([0.18, 0.25, 0.68, 1.00, 1.08, 1.14, 1.18, 1.20]),
                'validRange': (77.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        },
        'h1025': {
            'description': 'Solution treated, aged 552 C / 4 h. The condition to actually specify.',
            'forms': ['bar', 'plate', 'forging'], 'thicknessRange': (0.003, 0.200),
            'typical': {'yieldStrength': 1070.0e6, 'ultimateStrength': 1140.0e6, 'elongation': 0.12,
                        'reductionOfArea': 0.45, 'elasticModulus': 196.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 1900.0e6, 'hardness': 352.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 1000.0e6, 'LT': 1000.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1069.0e6, 'LT': 1069.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 1034.0e6, 'LT': 1034.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1103.0e6, 'LT': 1103.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 17.9, 'specificHeat': 460.0,
                        'thermalExpansion': 10.8e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 80.0e6, 'T-L': 72.0e6},
                         'parisCoefficient': 5.0e-12, 'parisExponent': 3.0,
                         'thresholdRange': 5.5e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1900.0e6, 'basquinExponent': -0.088,
                        'enduranceStress': 550.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'marine air': 620.0e6, 'chlorides': 480.0e6},
                              'sccRating': {'L': 'high', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.62, 'pren': 16.5},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.18, 1.16, 1.06, 1.00, 0.95, 0.91, 0.86, 0.78]),
                'ultimateRatio':     np.array([1.22, 1.20, 1.07, 1.00, 0.96, 0.92, 0.87, 0.79]),
                'modulusRatio':      np.array([1.08, 1.06, 1.03, 1.00, 0.96, 0.93, 0.89, 0.84]),
                'conductivityRatio': np.array([0.20, 0.55, 0.83, 1.00, 1.12, 1.22, 1.32, 1.41]),
                'expansionRatio':    np.array([0.50, 0.62, 0.89, 1.00, 1.04, 1.08, 1.12, 1.16]),
                'toughnessRatio':    np.array([0.25, 0.34, 0.74, 1.00, 1.07, 1.12, 1.16, 1.18]),
                'validRange': (77.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['15-5PH'] = {
    'commonName': '15-5PH precipitation hardening stainless', 'family': 'stainless martensitic PH',
    'uns': 'S15500', 'crystalStructure': 'bcc martensite', 'density': 7800.0, 'poissonRatio': 0.272,
    'meltingRange': (1673.0, 1713.0), 'anodicIndex': 0.35, 'relativeCost': 1.8,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 8, 'plate': 12, 'forging': 22},
    'specifications': ['AMS 5659 (bar and forging)'],
    'chemistry': {'chromium': 15.0, 'nickel': 4.5, 'molybdenum': 0.0, 'nitrogen': 0.03,
                  'tungsten': 0.0, 'carbon': 0.05, 'copper': 3.5},
    'incompatible': ['LH2', 'GH2', 'CRYOGENIC SERVICE'],
    'compatible': ['N2H4', 'MMH', 'RP-1', 'GHE', 'GN2'],
    'notes': 'Essentially 17-4PH with the delta ferrite removed by rebalancing the chemistry, which '
             'gives markedly better transverse and short transverse toughness. Where a 17-4PH forging '
             'would be loaded across the grain, this is the alloy.',
    'conditions': {
        'h1025': {
            'description': 'Solution treated, aged 552 C / 4 h',
            'forms': ['bar', 'plate', 'forging'], 'thicknessRange': (0.003, 0.250),
            'typical': {'yieldStrength': 1069.0e6, 'ultimateStrength': 1138.0e6, 'elongation': 0.14,
                        'reductionOfArea': 0.50, 'elasticModulus': 196.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 1930.0e6, 'hardness': 352.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 1000.0e6, 'LT': 993.0e6, 'ST': 979.0e6},
                      'ultimateStrength': {'L': 1069.0e6, 'LT': 1062.0e6, 'ST': 1048.0e6}},
                'B': {'yieldStrength': {'L': 1034.0e6, 'LT': 1027.0e6, 'ST': 1014.0e6},
                      'ultimateStrength': {'L': 1103.0e6, 'LT': 1096.0e6, 'ST': 1083.0e6}}},
            'thermal': {'thermalConductivity': 17.8, 'specificHeat': 460.0,
                        'thermalExpansion': 10.8e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 92.0e6, 'T-L': 85.0e6},
                         'parisCoefficient': 4.8e-12, 'parisExponent': 3.0,
                         'thresholdRange': 5.8e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1880.0e6, 'basquinExponent': -0.088,
                        'enduranceStress': 545.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'marine air': 660.0e6, 'chlorides': 520.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'moderate'},
                              'hydrogenRatio': 0.64, 'pren': 15.5},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.18, 1.16, 1.06, 1.00, 0.95, 0.91, 0.86, 0.78]),
                'ultimateRatio':     np.array([1.22, 1.20, 1.07, 1.00, 0.96, 0.92, 0.87, 0.79]),
                'modulusRatio':      np.array([1.08, 1.06, 1.03, 1.00, 0.96, 0.93, 0.89, 0.84]),
                'conductivityRatio': np.array([0.20, 0.55, 0.83, 1.00, 1.12, 1.22, 1.32, 1.41]),
                'expansionRatio':    np.array([0.50, 0.62, 0.89, 1.00, 1.04, 1.08, 1.12, 1.16]),
                'toughnessRatio':    np.array([0.28, 0.37, 0.76, 1.00, 1.07, 1.12, 1.16, 1.18]),
                'validRange': (77.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['A286'] = {
    'commonName': 'A286 iron-nickel superalloy', 'family': 'stainless austenitic PH',
    'uns': 'S66286', 'crystalStructure': 'fcc', 'density': 7940.0, 'poissonRatio': 0.31,
    'meltingRange': (1644.0, 1700.0), 'anodicIndex': 0.35, 'relativeCost': 3.2,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 12, 'fastener': 8, 'forging': 26},
    'specifications': ['AMS 5731 (bar)', 'AMS 5737 (bar, solution treated and aged)'],
    'chemistry': {'chromium': 14.75, 'nickel': 25.5, 'molybdenum': 1.25, 'nitrogen': 0.03,
                  'tungsten': 0.0, 'carbon': 0.05, 'titanium': 2.1},
    'incompatible': ['CONCENTRATED H2O2'],
    'compatible': ['LOX', 'GOX', 'LH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'GHE', 'GN2'],
    'notes': 'The aerospace fastener alloy. Austenitic and precipitation hardened at the same time, so '
             'it keeps FCC toughness down to cryogenic temperature while reaching 900 MPa yield. '
             'A286 bolts are the default where a fastener sees both cryogenic temperature and real '
             'preload, and they are non-magnetic.',
    'conditions': {
        'sta': {
            'description': 'Solution treated 980 C, aged 718 C / 16 h',
            'forms': ['bar', 'fastener', 'forging'], 'thicknessRange': (0.003, 0.150),
            'typical': {'yieldStrength': 655.0e6, 'ultimateStrength': 1000.0e6, 'elongation': 0.25,
                        'reductionOfArea': 0.40, 'elasticModulus': 201.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 1650.0e6, 'hardness': 300.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 586.0e6, 'LT': 586.0e6, 'ST': None},
                      'ultimateStrength': {'L': 896.0e6, 'LT': 896.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 620.0e6, 'LT': 620.0e6, 'ST': None},
                      'ultimateStrength': {'L': 931.0e6, 'LT': 931.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 12.6, 'specificHeat': 460.0,
                        'thermalExpansion': 16.9e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 130.0e6, 'T-L': 120.0e6},
                         'parisCoefficient': 3.5e-12, 'parisExponent': 3.1,
                         'thresholdRange': 6.5e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1700.0e6, 'basquinExponent': -0.095,
                        'enduranceStress': 450.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'marine air': 550.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.85, 'pren': 19.4},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.42, 1.38, 1.14, 1.00, 0.96, 0.94, 0.92, 0.89]),
                'ultimateRatio':     np.array([1.52, 1.46, 1.17, 1.00, 0.97, 0.95, 0.93, 0.90]),
                'modulusRatio':      np.array([1.10, 1.08, 1.03, 1.00, 0.97, 0.94, 0.90, 0.86]),
                'conductivityRatio': np.array([0.15, 0.50, 0.80, 1.00, 1.15, 1.28, 1.40, 1.52]),
                'expansionRatio':    np.array([0.50, 0.62, 0.88, 1.00, 1.04, 1.08, 1.12, 1.16]),
                'toughnessRatio':    np.array([0.88, 0.91, 0.97, 1.00, 1.00, 0.99, 0.98, 0.96]),
                'validRange': (20.0, 900.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

# -- Nickel Alloys and Superalloys -- #
#
# Where temperature or corrosion rules out everything else. Face-centred cubic, so they stay tough at
# cryogenic temperature as well, which makes 718 unusual: it is one of very few alloys that is both a
# hot section material and a cryogenic pressure vessel material.
#
# The dividing line is the strengthening mechanism. Solid solution alloys (625, Hastelloy X) are
# weldable as-is. Precipitation hardened alloys (718, K-500) need a post-weld solution and age to
# recover joint properties, and a weld left as-welded is a soft spot.
#
# Nickel alloys carry a separate 'cryogenicCurves' block. Their published data runs from room
# temperature upward because that is the service range people care about, so the hot curve grid and
# the cryogenic grid do not join. MaterialDatabase selects between them on the query temperature.

MATERIAL_DATABASE['INCONEL 718'] = {
    'commonName': 'Inconel 718', 'family': 'nickel precipitation hardening', 'uns': 'N07718',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (1533.0, 1609.0), 'anodicIndex': 0.30, 'relativeCost': 6.5,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 16, 'plate': 20, 'bar': 14, 'forging': 32, 'lpbfPowder': 6},
    'specifications': ['AMS 5662 (bar STA)', 'AMS 5596 (sheet)', 'ASTM F3055 (LPBF)'],
    'chemistry': {'chromium': 19.0, 'nickel': 52.5, 'molybdenum': 3.05, 'nitrogen': 0.0,
                  'tungsten': 0.0, 'carbon': 0.04, 'niobium': 5.13},
    'incompatible': [],
    'compatible': ['LOX', 'GOX', 'LH2', 'GH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'GHE', 'GN2'],
    'notes': None,   # seeded from common
    'conditions': {
        'sta': {
            'description': 'Solution treated 954 C, double aged 718 C / 621 C per AMS 5662',
            'forms': ['bar', 'plate', 'sheet', 'forging'], 'thicknessRange': (0.0005, 0.200),
            'typical': {'elongation': 0.12, 'reductionOfArea': 0.20, 'shearModulus': 77.2e9,
                        'bearingUltimate': 2210.0e6, 'hardness': 400.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 993.0e6, 'LT': 979.0e6, 'ST': 965.0e6},
                      'ultimateStrength': {'L': 1234.0e6, 'LT': 1221.0e6, 'ST': 1200.0e6}},
                'B': {'yieldStrength': {'L': 1027.0e6, 'LT': 1014.0e6, 'ST': 1000.0e6},
                      'ultimateStrength': {'L': 1269.0e6, 'LT': 1255.0e6, 'ST': 1234.0e6}}},
            'thermal': {'specificHeat': 435.0, 'emissivity': 0.35},
            'fracture': {'planeStrainToughness': {'L-T': 96.0e6, 'T-L': 88.0e6},
                         'parisCoefficient': 4.0e-12, 'parisExponent': 3.1,
                         'thresholdRange': 8.0e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 2300.0e6, 'basquinExponent': -0.085,
                        'enduranceStress': 620.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            # Better than steel in hydrogen but not immune, and the notched ratio falls as the aging
            # treatment is pushed for strength. The highest strength condition is the worst.
            'environmental': {'sccThreshold': {'marine air': 800.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.55, 'pren': 29.1},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.96, 0.92, 0.88, 0.72, 0.50, 0.26]),
                'ultimateRatio':     np.array([1.00, 0.97, 0.95, 0.93, 0.75, 0.48, 0.24]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.83, 0.74, 0.68, 0.61]),
                'conductivityRatio': np.array([1.00, 1.20, 1.58, 1.95, 2.32, 2.50, 2.68]),
                'expansionRatio':    np.array([1.00, 1.03, 1.09, 1.15, 1.22, 1.26, 1.30]),
                'toughnessRatio':    np.array([1.00, 1.02, 1.04, 1.02, 0.92, 0.80, 0.65]),
                'validRange': (293.15, 1200.0)},
            'cryogenicCurves': {
                'temperature':       np.array([20.0, 77.0, 200.0, 293.15]),
                'yieldRatio':        np.array([1.18, 1.15, 1.06, 1.00]),
                'ultimateRatio':     np.array([1.25, 1.21, 1.08, 1.00]),
                'modulusRatio':      np.array([1.07, 1.06, 1.02, 1.00]),
                'conductivityRatio': np.array([0.13, 0.45, 0.78, 1.00]),
                'expansionRatio':    np.array([0.52, 0.63, 0.89, 1.00]),
                'toughnessRatio':    np.array([0.82, 0.86, 0.95, 1.00]),
                'validRange': (20.0, 293.15)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'COMMON-SEED', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE', 'cryogenicCurves': 'NIST-CRYO'}
        },
        'as-welded': {
            'description': 'GTAW or EBW, as-welded, no post-weld solution and age. A soft spot.',
            'forms': ['sheet', 'plate', 'tube'], 'thicknessRange': (0.001, 0.050),
            'typical': {'yieldStrength': 724.0e6, 'ultimateStrength': 957.0e6, 'elongation': 0.15,
                        'elasticModulus': 200.0e9},
            'thermal': {'thermalConductivity': 11.4, 'specificHeat': 435.0,
                        'thermalExpansion': 13.0e-6},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.96, 0.92, 0.87, 0.70, 0.48, 0.25]),
                'ultimateRatio':     np.array([1.00, 0.97, 0.94, 0.91, 0.73, 0.46, 0.23]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.83, 0.74, 0.68, 0.61]),
                'conductivityRatio': np.array([1.00, 1.20, 1.58, 1.95, 2.32, 2.50, 2.68]),
                'expansionRatio':    np.array([1.00, 1.03, 1.09, 1.15, 1.22, 1.26, 1.30]),
                'validRange': (293.15, 1200.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'thermal': 'COMMON-SEED',
                        'temperatureCurves': 'MMPDS-CURVE'}
        },
        'lpbf hip + sta': {
            'description': 'LPBF, HIP 1163 C / 100 MPa, solution treated and double aged',
            'forms': ['lpbf'], 'thicknessRange': (0.0005, 0.150),
            'typical': {'yieldStrength': 1050.0e6, 'ultimateStrength': 1250.0e6, 'elongation': 0.15,
                        'elasticModulus': 197.0e9, 'shearModulus': 76.0e9, 'hardness': 395.0},
            'thermal': {'thermalConductivity': 11.4, 'specificHeat': 435.0,
                        'thermalExpansion': 13.0e-6, 'emissivity': 0.50},
            'fracture': {'planeStrainToughness': {'L-T': 85.0e6}, 'parisCoefficient': 5.0e-12,
                         'parisExponent': 3.2, 'thresholdRange': 6.5e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 2050.0e6, 'basquinExponent': -0.092,
                        'enduranceStress': 480.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'machined'},
            # HIP closes the porosity that dominates as-built fatigue, which is why the Z knockdown
            # after HIP is 5 percent rather than the 25 percent it would be as-built.
            'anisotropy': {'zYieldRatio': 0.95, 'zUltimateRatio': 0.94, 'zElongationRatio': 0.85},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.96, 0.92, 0.88, 0.72, 0.50, 0.26]),
                'ultimateRatio':     np.array([1.00, 0.97, 0.95, 0.93, 0.75, 0.48, 0.24]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.83, 0.74, 0.68, 0.61]),
                'conductivityRatio': np.array([1.00, 1.20, 1.58, 1.95, 2.32, 2.50, 2.68]),
                'expansionRatio':    np.array([1.00, 1.03, 1.09, 1.15, 1.22, 1.26, 1.30]),
                'validRange': (293.15, 1200.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'thermal': 'COMMON-SEED',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'anisotropy': 'ESTIMATE-2026Q1', 'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['INCONEL 625'] = {
    'commonName': 'Inconel 625', 'family': 'nickel solid solution', 'uns': 'N06625',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (1563.0, 1623.0), 'anodicIndex': 0.30, 'relativeCost': 7.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 14, 'plate': 18, 'bar': 12, 'tube': 16, 'lpbfPowder': 6},
    'specifications': ['AMS 5599 (sheet)', 'AMS 5666 (bar)', 'ASTM B443', 'ASTM F3056 (LPBF)'],
    'chemistry': {'chromium': 21.5, 'nickel': 61.0, 'molybdenum': 9.0, 'nitrogen': 0.0,
                  'tungsten': 0.0, 'carbon': 0.05, 'niobium': 3.65},
    'incompatible': [],
    'compatible': ['LOX', 'GOX', 'LH2', 'GH2', 'LN2', 'N2H4', 'MMH', 'N2O4', 'RP-1', 'H2O2',
                   'GHE', 'GN2', 'SEAWATER'],
    'notes': None,   # seeded from common
    'conditions': {
        'annealed': {
            'description': 'Solution annealed 1093 C. Weldable with no post-weld heat treatment.',
            'forms': ['sheet', 'plate', 'bar', 'tube', 'bellows'], 'thicknessRange': (0.0001, 0.150),
            'typical': {'elongation': 0.45, 'reductionOfArea': 0.55, 'shearModulus': 79.0e9,
                        'bearingUltimate': 1450.0e6, 'hardness': 190.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 414.0e6}, 'ultimateStrength': {'L': 827.0e6}}},
            'thermal': {'specificHeat': 410.0, 'emissivity': 0.35},
            'fracture': {'planeStrainToughness': {'L-T': 130.0e6}, 'parisCoefficient': 3.0e-12,
                         'parisExponent': 3.1, 'thresholdRange': 8.5e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1600.0e6, 'basquinExponent': -0.100,
                        'enduranceStress': 400.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            # PREN above 50, which is why 625 is the alloy for a splash zone and why bellows at a
            # coastal launch site are made from it rather than from 316L.
            'environmental': {'sccThreshold': {'marine air': 700.0e6, 'chlorides': 600.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.80, 'pren': 51.2},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.91, 0.83, 0.80, 0.76, 0.63, 0.40]),
                'ultimateRatio':     np.array([1.00, 0.96, 0.94, 0.92, 0.79, 0.60, 0.36]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.84, 0.76, 0.71, 0.65]),
                'conductivityRatio': np.array([1.00, 1.22, 1.65, 2.08, 2.50, 2.71, 2.92]),
                'expansionRatio':    np.array([1.00, 1.03, 1.09, 1.14, 1.20, 1.24, 1.28]),
                'toughnessRatio':    np.array([1.00, 1.02, 1.03, 1.01, 0.95, 0.87, 0.75]),
                'validRange': (293.15, 1200.0)},
            'cryogenicCurves': {
                'temperature':       np.array([20.0, 77.0, 200.0, 293.15]),
                'yieldRatio':        np.array([1.24, 1.20, 1.08, 1.00]),
                'ultimateRatio':     np.array([1.30, 1.26, 1.10, 1.00]),
                'modulusRatio':      np.array([1.08, 1.06, 1.02, 1.00]),
                'conductivityRatio': np.array([0.14, 0.44, 0.77, 1.00]),
                'expansionRatio':    np.array([0.53, 0.64, 0.89, 1.00]),
                'toughnessRatio':    np.array([0.90, 0.93, 0.98, 1.00]),
                'validRange': (20.0, 293.15)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'ASTM-SPEC', 'thermal': 'COMMON-SEED',
                        'fracture': 'DAMAGE-TOLERANT-HANDBOOK', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'NASA-SP-8040', 'temperatureCurves': 'ASME-II-D',
                        'cryogenicCurves': 'NIST-CRYO'}
        }
    }
}

MATERIAL_DATABASE['MONEL 400'] = {
    'commonName': 'Monel 400 (Ni-Cu)', 'family': 'nickel-copper', 'uns': 'N04400',
    'crystalStructure': 'fcc', 'density': np.nan, 'poissonRatio': np.nan,   # seeded from common
    'meltingRange': (1573.0, 1623.0), 'anodicIndex': 0.30, 'relativeCost': 5.5,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 16, 'plate': 20, 'bar': 14, 'tube': 18},
    'specifications': ['ASTM B127 (sheet and plate)', 'ASTM B164 (bar)', 'AMS 4544'],
    'chemistry': {'chromium': 0.0, 'nickel': 66.0, 'molybdenum': 0.0, 'nitrogen': 0.0,
                  'tungsten': 0.0, 'carbon': 0.15, 'copper': 32.0},
    # The copper content is the whole story: outstanding in fluorine and peroxide, catastrophic in
    # hydrazine, where copper catalyses decomposition. See fluidSystems MaterialsCompatibility.md.
    'incompatible': ['N2H4', 'MMH', 'AEROZINE-50', 'AMMONIA', 'ACETYLENE'],
    'compatible': ['GF2', 'HF', 'H2O2', 'SEAWATER', 'GHE', 'GN2', 'LN2', 'LOX'],
    'notes': None,   # seeded from common
    'conditions': {
        'annealed': {
            'description': 'Annealed 870 C',
            'forms': ['sheet', 'plate', 'bar', 'tube'], 'thicknessRange': (0.0005, 0.100),
            'typical': {'elongation': 0.40, 'reductionOfArea': 0.60, 'shearModulus': 66.0e9,
                        'bearingUltimate': 960.0e6, 'hardness': 130.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 240.0e6}, 'ultimateStrength': {'L': 550.0e6}}},
            'thermal': {'specificHeat': 427.0, 'emissivity': 0.35},
            'fracture': {'planeStrainToughness': {'L-T': 150.0e6}, 'parisCoefficient': 3.5e-12,
                         'parisExponent': 3.1, 'thresholdRange': 7.0e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1050.0e6, 'basquinExponent': -0.105,
                        'enduranceStress': 250.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'marine air': 400.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.88, 'pren': 0.0},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.92, 0.87, 0.82, 0.62, 0.44, 0.28]),
                'ultimateRatio':     np.array([1.00, 0.95, 0.90, 0.82, 0.58, 0.40, 0.24]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.83, 0.74, 0.68, 0.62]),
                'conductivityRatio': np.array([1.00, 1.18, 1.52, 1.86, 2.20, 2.37, 2.54]),
                'expansionRatio':    np.array([1.00, 1.03, 1.09, 1.14, 1.20, 1.23, 1.26]),
                'validRange': (293.15, 900.0)},
            'cryogenicCurves': {
                'temperature':       np.array([20.0, 77.0, 200.0, 293.15]),
                'yieldRatio':        np.array([1.55, 1.50, 1.16, 1.00]),
                'ultimateRatio':     np.array([1.62, 1.55, 1.19, 1.00]),
                'modulusRatio':      np.array([1.09, 1.07, 1.03, 1.00]),
                'conductivityRatio': np.array([0.16, 0.47, 0.79, 1.00]),
                'expansionRatio':    np.array([0.51, 0.63, 0.89, 1.00]),
                'toughnessRatio':    np.array([0.92, 0.95, 0.99, 1.00]),
                'validRange': (20.0, 293.15)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'ASTM-SPEC', 'thermal': 'COMMON-SEED',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'NASA-SP-8040', 'temperatureCurves': 'ASME-II-D',
                        'cryogenicCurves': 'NIST-CRYO'}
        }
    }
}

MATERIAL_DATABASE['MONEL K-500'] = {
    'commonName': 'Monel K-500 (age hardened Ni-Cu)',
    'family': 'nickel-copper precipitation hardening', 'uns': 'N05500', 'crystalStructure': 'fcc',
    'density': 8440.0, 'poissonRatio': 0.32, 'meltingRange': (1588.0, 1623.0),
    'anodicIndex': 0.30, 'relativeCost': 8.0, 'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 20, 'forging': 34},
    'specifications': ['AMS 4676 (bar)', 'ASTM B865'],
    'chemistry': {'chromium': 0.0, 'nickel': 65.0, 'molybdenum': 0.0, 'nitrogen': 0.0,
                  'tungsten': 0.0, 'carbon': 0.13, 'copper': 30.0, 'aluminium': 2.8},
    'incompatible': ['N2H4', 'MMH', 'AEROZINE-50', 'AMMONIA'],
    'compatible': ['GF2', 'HF', 'H2O2', 'SEAWATER', 'GHE', 'GN2', 'LOX'],
    'notes': 'Aluminium and titanium additions make Monel age hardenable, roughly tripling the yield '
             'strength while keeping the fluorine and peroxide compatibility. Valve stems and '
             'fasteners in fluorine and peroxide service. Same copper prohibition as Monel 400.',
    'conditions': {
        'aged': {
            'description': 'Solution treated 982 C, age hardened 593 C / 16 h',
            'forms': ['bar', 'forging'], 'thicknessRange': (0.003, 0.150),
            'typical': {'yieldStrength': 690.0e6, 'ultimateStrength': 1100.0e6, 'elongation': 0.20,
                        'reductionOfArea': 0.35, 'elasticModulus': 179.0e9, 'shearModulus': 66.0e9,
                        'bearingUltimate': 1850.0e6, 'hardness': 300.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 690.0e6}, 'ultimateStrength': {'L': 965.0e6}}},
            'thermal': {'thermalConductivity': 17.5, 'specificHeat': 419.0,
                        'thermalExpansion': 13.7e-6, 'emissivity': 0.35},
            'fracture': {'planeStrainToughness': {'L-T': 110.0e6}, 'parisCoefficient': 4.0e-12,
                         'parisExponent': 3.1, 'thresholdRange': 6.5e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1750.0e6, 'basquinExponent': -0.095,
                        'enduranceStress': 415.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'marine air': 480.0e6},
                              'sccRating': {'L': 'high', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.72, 'pren': 0.0},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.95, 0.90, 0.84, 0.60, 0.40, 0.22]),
                'ultimateRatio':     np.array([1.00, 0.96, 0.92, 0.85, 0.58, 0.36, 0.19]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.83, 0.74, 0.68, 0.62]),
                'conductivityRatio': np.array([1.00, 1.19, 1.55, 1.90, 2.25, 2.42, 2.60]),
                'expansionRatio':    np.array([1.00, 1.03, 1.09, 1.14, 1.20, 1.23, 1.26]),
                'validRange': (293.15, 900.0)},
            'sources': {'typical': 'ASTM-SPEC', 'allowables': 'ASTM-SPEC', 'thermal': 'ASTM-SPEC',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'ESTIMATE-2026Q1', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

MATERIAL_DATABASE['HAYNES 230'] = {
    'commonName': 'Haynes 230', 'family': 'nickel solid solution, high temperature', 'uns': 'N06230',
    'crystalStructure': 'fcc', 'density': 8970.0, 'poissonRatio': 0.31,
    'meltingRange': (1574.0, 1655.0), 'anodicIndex': 0.30, 'relativeCost': 14.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 26, 'plate': 30, 'bar': 24},
    'specifications': ['AMS 5878 (sheet)', 'AMS 5891 (bar)'],
    'chemistry': {'chromium': 22.0, 'nickel': 57.0, 'molybdenum': 2.0, 'nitrogen': 0.0,
                  'tungsten': 14.0, 'carbon': 0.10},
    'incompatible': [],
    'compatible': ['HOT GAS', 'GHE', 'GN2', 'COMBUSTION PRODUCTS'],
    'notes': 'Tungsten solid solution strengthened for genuinely high temperature service, with useful '
             'strength beyond 1200 K where 625 has essentially none. Gas generator ducting, turbine '
             'inlet hardware, hot gas manifolds. Expensive and long lead.',
    'conditions': {
        'annealed': {
            'description': 'Solution annealed 1232 C',
            'forms': ['sheet', 'plate', 'bar', 'tube'], 'thicknessRange': (0.0005, 0.075),
            'typical': {'yieldStrength': 390.0e6, 'ultimateStrength': 860.0e6, 'elongation': 0.47,
                        'reductionOfArea': 0.50, 'elasticModulus': 211.0e9, 'shearModulus': 81.0e9,
                        'bearingUltimate': 1400.0e6, 'hardness': 210.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 310.0e6}, 'ultimateStrength': {'L': 760.0e6}}},
            'thermal': {'thermalConductivity': 8.9, 'specificHeat': 397.0,
                        'thermalExpansion': 12.3e-6, 'emissivity': 0.40},
            'fatigue': {'basquinCoefficient': 1500.0e6, 'basquinExponent': -0.102,
                        'enduranceStress': 350.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.85, 'pren': 51.7},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.88, 0.78, 0.74, 0.72, 0.66, 0.50]),
                'ultimateRatio':     np.array([1.00, 0.94, 0.89, 0.85, 0.72, 0.58, 0.40]),
                'modulusRatio':      np.array([1.00, 0.96, 0.91, 0.85, 0.78, 0.74, 0.69]),
                'conductivityRatio': np.array([1.00, 1.28, 1.83, 2.38, 2.92, 3.20, 3.47]),
                'expansionRatio':    np.array([1.00, 1.04, 1.11, 1.17, 1.24, 1.28, 1.32]),
                'validRange': (293.15, 1250.0)},
            'sources': {'typical': 'AMS-SPEC', 'allowables': 'AMS-SPEC', 'thermal': 'AMS-SPEC',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

MATERIAL_DATABASE['HASTELLOY X'] = {
    'commonName': 'Hastelloy X', 'family': 'nickel solid solution, high temperature', 'uns': 'N06002',
    'crystalStructure': 'fcc', 'density': 8220.0, 'poissonRatio': 0.32,
    'meltingRange': (1533.0, 1628.0), 'anodicIndex': 0.30, 'relativeCost': 11.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 22, 'plate': 26, 'bar': 20},
    'specifications': ['AMS 5536 (sheet)', 'AMS 5754 (bar)'],
    'chemistry': {'chromium': 22.0, 'nickel': 47.0, 'molybdenum': 9.0, 'nitrogen': 0.0,
                  'tungsten': 0.6, 'carbon': 0.10, 'iron': 18.5},
    'incompatible': [],
    'compatible': ['HOT GAS', 'GHE', 'GN2', 'COMBUSTION PRODUCTS'],
    'notes': 'The classic combustor sheet alloy. Excellent oxidation resistance and formability at the '
             'cost of lower strength than 230. Where a hot section part has to be formed and welded '
             'rather than machined, this is usually the choice.',
    'conditions': {
        'annealed': {
            'description': 'Solution annealed 1177 C',
            'forms': ['sheet', 'plate', 'bar'], 'thicknessRange': (0.0003, 0.050),
            'typical': {'yieldStrength': 360.0e6, 'ultimateStrength': 785.0e6, 'elongation': 0.43,
                        'reductionOfArea': 0.50, 'elasticModulus': 205.0e9, 'shearModulus': 78.0e9,
                        'bearingUltimate': 1300.0e6, 'hardness': 195.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 276.0e6}, 'ultimateStrength': {'L': 690.0e6}}},
            'thermal': {'thermalConductivity': 9.1, 'specificHeat': 486.0,
                        'thermalExpansion': 13.9e-6, 'emissivity': 0.40},
            'fatigue': {'basquinCoefficient': 1400.0e6, 'basquinExponent': -0.104,
                        'enduranceStress': 320.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.85, 'pren': 52.7},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.86, 0.75, 0.70, 0.64, 0.55, 0.38]),
                'ultimateRatio':     np.array([1.00, 0.93, 0.87, 0.80, 0.62, 0.46, 0.28]),
                'modulusRatio':      np.array([1.00, 0.96, 0.90, 0.84, 0.76, 0.71, 0.66]),
                'conductivityRatio': np.array([1.00, 1.27, 1.80, 2.33, 2.86, 3.13, 3.40]),
                'expansionRatio':    np.array([1.00, 1.04, 1.10, 1.16, 1.22, 1.26, 1.30]),
                'validRange': (293.15, 1200.0)},
            'sources': {'typical': 'AMS-SPEC', 'allowables': 'AMS-SPEC', 'thermal': 'AMS-SPEC',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

# -- Titanium Alloys -- #
#
# The best strength to weight available in a metal, and the reason it is not used everywhere is the
# incompatible list. Titanium in oxygen is impact sensitive and it burns. That is not a caution, it is
# a prohibition, and it is enforced in code by MaterialDatabase.checkCompatibility.
#
# The second catch is thermal conductivity: 6.7 W/m-K is fifteen times worse than aluminium, so a
# titanium part in a thermal path is a thermal problem.

MATERIAL_DATABASE['TI-6AL-4V'] = {
    'commonName': 'Ti-6Al-4V (grade 5)', 'family': 'titanium alpha-beta', 'uns': 'R56400',
    'crystalStructure': 'hcp alpha + bcc beta', 'density': np.nan, 'poissonRatio': np.nan,
    'meltingRange': (1877.0, 1933.0), 'betaTransus': 1268.0, 'anodicIndex': 0.15,
    'relativeCost': 8.5, 'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 12, 'plate': 16, 'bar': 10, 'forging': 30, 'lpbfPowder': 8},
    'specifications': ['AMS 4911 (sheet)', 'AMS 4928 (bar)', 'AMS 4930 (ELI)', 'AMS 4999 (LPBF)'],
    'chemistry': {'aluminium': 6.0, 'vanadium': 4.0, 'oxygen': 0.20, 'iron': 0.25},
    # The hard prohibition. Impact sensitive in oxygen, SCC in uninhibited N2O4 and in methanol.
    'incompatible': ['LOX', 'GOX', 'N2O4', 'MON-1', 'IRFNA', 'RFNA', 'METHANOL', 'DRY CHLORINE',
                     'CADMIUM', 'MERCURY'],
    'compatible': ['N2H4', 'MMH', 'GHE', 'GN2', 'LN2', 'LH2', 'GH2 LIMITED', 'RP-1', 'WATER'],
    'notes': None,   # seeded from common
    'conditions': {
        'annealed': {
            'description': 'Mill annealed 705 C / 2 h / air cool',
            'forms': ['sheet', 'plate', 'bar', 'forging'], 'thicknessRange': (0.0005, 0.100),
            'typical': {'elongation': 0.10, 'reductionOfArea': 0.25, 'shearModulus': 44.0e9,
                        'bearingUltimate': 1620.0e6, 'hardness': 334.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 828.0e6, 'LT': 828.0e6, 'ST': None},
                      'ultimateStrength': {'L': 897.0e6, 'LT': 897.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 862.0e6, 'LT': 862.0e6, 'ST': None},
                      'ultimateStrength': {'L': 924.0e6, 'LT': 924.0e6, 'ST': None}},
                'S': {'yieldStrength': {'L': 828.0e6}, 'ultimateStrength': {'L': 895.0e6}}},
            'thermal': {'specificHeat': 526.0, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 75.0e6, 'T-L': 68.0e6},
                         'parisCoefficient': 5.0e-12, 'parisExponent': 3.3,
                         'thresholdRange': 4.0e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1740.0e6, 'basquinExponent': -0.083,
                        'enduranceStress': 500.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished, Ra 0.2 um'},
            # The methanol number is the one people do not expect. Eight MPa is nothing, and methanol
            # is a common cleaning solvent, which is how titanium hardware gets cracked in the shop.
            'environmental': {'sccThreshold': {'salt fog': 55.0e6, 'MON-1': 40.0e6,
                                               'uninhibited N2O4': 12.0e6, 'methanol': 8.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.75},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.55, 1.48, 1.18, 1.00, 0.86, 0.78, 0.71, 0.62]),
                'ultimateRatio':     np.array([1.50, 1.44, 1.16, 1.00, 0.88, 0.81, 0.75, 0.67]),
                'modulusRatio':      np.array([1.10, 1.09, 1.04, 1.00, 0.95, 0.91, 0.87, 0.82]),
                'conductivityRatio': np.array([0.28, 0.37, 0.79, 1.00, 1.18, 1.33, 1.48, 1.63]),
                'expansionRatio':    np.array([0.55, 0.62, 0.87, 1.00, 1.06, 1.10, 1.14, 1.18]),
                'toughnessRatio':    np.array([0.72, 0.75, 0.92, 1.00, 1.05, 1.08, 1.10, 1.10]),
                'validRange': (20.0, 700.0)},
            'sources': {'typical': 'COMMON-SEED', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'COMMON-SEED', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'MMPDS-TYPICAL', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        },
        'sta': {
            'description': 'Solution treated 954 C, water quenched, aged 538 C / 4 h',
            'forms': ['bar', 'forging'], 'thicknessRange': (0.003, 0.050),
            'typical': {'yieldStrength': 1035.0e6, 'ultimateStrength': 1103.0e6, 'elongation': 0.08,
                        'reductionOfArea': 0.20, 'elasticModulus': 113.8e9, 'shearModulus': 44.0e9,
                        'bearingUltimate': 1860.0e6, 'hardness': 365.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 965.0e6, 'LT': 965.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1034.0e6, 'LT': 1034.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 1000.0e6, 'LT': 1000.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1069.0e6, 'LT': 1069.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 6.6, 'specificHeat': 526.0,
                        'thermalExpansion': 8.6e-6, 'emissivity': 0.30},
            # STA buys 17 percent yield and gives back 35 percent of the toughness. On a fracture
            # critical pressure vessel that is usually the wrong trade, which is why annealed is the
            # standard bottle condition.
            'fracture': {'planeStrainToughness': {'L-T': 49.0e6, 'T-L': 44.0e6},
                         'parisCoefficient': 7.0e-12, 'parisExponent': 3.4,
                         'thresholdRange': 3.2e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1980.0e6, 'basquinExponent': -0.080,
                        'enduranceStress': 580.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished, Ra 0.2 um'},
            'environmental': {'sccThreshold': {'salt fog': 40.0e6, 'MON-1': 30.0e6,
                                               'uninhibited N2O4': 9.0e6, 'methanol': 6.0e6},
                              'sccRating': {'L': 'moderate', 'LT': 'moderate', 'ST': 'moderate'},
                              'hydrogenRatio': 0.68},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.48, 1.42, 1.16, 1.00, 0.87, 0.79, 0.72, 0.63]),
                'ultimateRatio':     np.array([1.44, 1.38, 1.14, 1.00, 0.89, 0.82, 0.76, 0.68]),
                'modulusRatio':      np.array([1.10, 1.09, 1.04, 1.00, 0.95, 0.91, 0.87, 0.82]),
                'conductivityRatio': np.array([0.28, 0.37, 0.79, 1.00, 1.18, 1.33, 1.48, 1.63]),
                'expansionRatio':    np.array([0.55, 0.62, 0.87, 1.00, 1.06, 1.10, 1.14, 1.18]),
                'toughnessRatio':    np.array([0.70, 0.73, 0.91, 1.00, 1.05, 1.08, 1.10, 1.10]),
                'validRange': (20.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        },
        'lpbf hip + annealed': {
            'description': 'LPBF, HIP 920 C / 100 MPa, stress relieved and annealed',
            'forms': ['lpbf'], 'thicknessRange': (0.0005, 0.100),
            'typical': {'yieldStrength': 910.0e6, 'ultimateStrength': 1000.0e6, 'elongation': 0.14,
                        'elasticModulus': 112.0e9, 'shearModulus': 43.0e9, 'hardness': 340.0},
            'thermal': {'thermalConductivity': 6.7, 'specificHeat': 526.0,
                        'thermalExpansion': 8.6e-6, 'emissivity': 0.55},
            'fracture': {'planeStrainToughness': {'L-T': 60.0e6}, 'parisCoefficient': 6.5e-12,
                         'parisExponent': 3.4, 'thresholdRange': 3.4e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1450.0e6, 'basquinExponent': -0.095,
                        'enduranceStress': 380.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'machined'},
            'anisotropy': {'zYieldRatio': 0.96, 'zUltimateRatio': 0.95, 'zElongationRatio': 0.85},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.52, 1.46, 1.17, 1.00, 0.86, 0.78, 0.71, 0.62]),
                'ultimateRatio':     np.array([1.48, 1.42, 1.15, 1.00, 0.88, 0.81, 0.75, 0.67]),
                'modulusRatio':      np.array([1.10, 1.09, 1.04, 1.00, 0.95, 0.91, 0.87, 0.82]),
                'conductivityRatio': np.array([0.28, 0.37, 0.79, 1.00, 1.18, 1.33, 1.48, 1.63]),
                'expansionRatio':    np.array([0.55, 0.62, 0.87, 1.00, 1.06, 1.10, 1.14, 1.18]),
                'validRange': (20.0, 700.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'thermal': 'COMMON-SEED',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'anisotropy': 'ESTIMATE-2026Q1', 'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['TI-6AL-4V ELI'] = {
    'commonName': 'Ti-6Al-4V ELI (grade 23)', 'family': 'titanium alpha-beta', 'uns': 'R56407',
    'crystalStructure': 'hcp alpha + bcc beta', 'density': 4430.0, 'poissonRatio': 0.342,
    'meltingRange': (1877.0, 1933.0), 'betaTransus': 1243.0, 'anodicIndex': 0.15,
    'relativeCost': 11.0, 'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 18, 'plate': 22, 'bar': 16, 'forging': 36},
    'specifications': ['AMS 4930 (bar)', 'AMS 4907 (sheet)', 'ASTM F136'],
    'chemistry': {'aluminium': 6.0, 'vanadium': 4.0, 'oxygen': 0.13, 'iron': 0.25},
    'incompatible': ['LOX', 'GOX', 'N2O4', 'MON-1', 'IRFNA', 'RFNA', 'METHANOL', 'DRY CHLORINE',
                     'CADMIUM', 'MERCURY'],
    'compatible': ['N2H4', 'MMH', 'GHE', 'GN2', 'LN2', 'LH2', 'RP-1', 'WATER'],
    'notes': 'Extra low interstitial: oxygen held to 0.13 percent instead of 0.20. Costs about 8 '
             'percent of the yield strength and buys roughly 35 percent more fracture toughness and '
             'usable cryogenic ductility. The grade for cryogenic pressure vessels and anything '
             'fracture critical. Same absolute oxygen prohibition as grade 5.',
    'conditions': {
        'annealed': {
            'description': 'Mill annealed 705 C / 2 h',
            'forms': ['sheet', 'plate', 'bar', 'forging'], 'thicknessRange': (0.0005, 0.100),
            'typical': {'yieldStrength': 795.0e6, 'ultimateStrength': 860.0e6, 'elongation': 0.15,
                        'reductionOfArea': 0.35, 'elasticModulus': 113.8e9, 'shearModulus': 44.0e9,
                        'bearingUltimate': 1480.0e6, 'hardness': 310.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 759.0e6, 'LT': 759.0e6, 'ST': None},
                      'ultimateStrength': {'L': 828.0e6, 'LT': 828.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 786.0e6, 'LT': 786.0e6, 'ST': None},
                      'ultimateStrength': {'L': 855.0e6, 'LT': 855.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 6.7, 'specificHeat': 526.0,
                        'thermalExpansion': 8.6e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 100.0e6, 'T-L': 92.0e6},
                         'parisCoefficient': 4.2e-12, 'parisExponent': 3.2,
                         'thresholdRange': 4.8e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1580.0e6, 'basquinExponent': -0.085,
                        'enduranceStress': 450.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished, Ra 0.2 um'},
            'environmental': {'sccThreshold': {'salt fog': 70.0e6, 'MON-1': 50.0e6,
                                               'uninhibited N2O4': 15.0e6, 'methanol': 10.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.80},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.58, 1.50, 1.19, 1.00, 0.86, 0.78, 0.71, 0.62]),
                'ultimateRatio':     np.array([1.53, 1.46, 1.17, 1.00, 0.88, 0.81, 0.75, 0.67]),
                'modulusRatio':      np.array([1.10, 1.09, 1.04, 1.00, 0.95, 0.91, 0.87, 0.82]),
                'conductivityRatio': np.array([0.28, 0.37, 0.79, 1.00, 1.18, 1.33, 1.48, 1.63]),
                'expansionRatio':    np.array([0.55, 0.62, 0.87, 1.00, 1.06, 1.10, 1.14, 1.18]),
                # ELI keeps far more of its toughness cold. That is the entire reason it exists.
                'toughnessRatio':    np.array([0.84, 0.86, 0.96, 1.00, 1.04, 1.07, 1.09, 1.09]),
                'validRange': (20.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['CP TI GRADE 2'] = {
    'commonName': 'Commercially pure titanium grade 2', 'family': 'titanium alpha', 'uns': 'R50400',
    'crystalStructure': 'hcp', 'density': 4510.0, 'poissonRatio': 0.34,
    'meltingRange': (1913.0, 1941.0), 'betaTransus': 1188.0, 'anodicIndex': 0.15,
    'relativeCost': 4.0, 'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'sheet': 8, 'plate': 10, 'bar': 8, 'tube': 12},
    'specifications': ['AMS 4902 (sheet)', 'ASTM B265', 'ASTM B338 (tube)'],
    'chemistry': {'oxygen': 0.25, 'iron': 0.30},
    'incompatible': ['LOX', 'GOX', 'N2O4', 'IRFNA', 'RFNA', 'METHANOL', 'DRY CHLORINE'],
    'compatible': ['N2H4', 'MMH', 'GHE', 'GN2', 'LN2', 'RP-1', 'SEAWATER', 'WATER'],
    'notes': 'Weldable, formable and outstandingly corrosion resistant, at half the strength of 6-4. '
             'Where the requirement is corrosion rather than strength, this is the cheaper and easier '
             'titanium. Still absolutely prohibited in oxidiser service.',
    'conditions': {
        'annealed': {
            'description': 'Annealed 705 C',
            'forms': ['sheet', 'plate', 'bar', 'tube'], 'thicknessRange': (0.0003, 0.075),
            'typical': {'yieldStrength': 275.0e6, 'ultimateStrength': 345.0e6, 'elongation': 0.20,
                        'reductionOfArea': 0.40, 'elasticModulus': 105.0e9, 'shearModulus': 45.0e9,
                        'bearingUltimate': 620.0e6, 'hardness': 160.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 275.0e6}, 'ultimateStrength': {'L': 345.0e6}}},
            'thermal': {'thermalConductivity': 16.4, 'specificHeat': 523.0,
                        'thermalExpansion': 8.6e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 110.0e6}, 'parisCoefficient': 4.0e-12,
                         'parisExponent': 3.2, 'thresholdRange': 5.0e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 620.0e6, 'basquinExponent': -0.090,
                        'enduranceStress': 175.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            'environmental': {'sccThreshold': {'salt fog': 200.0e6, 'methanol': 30.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.85},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([2.10, 1.95, 1.32, 1.00, 0.78, 0.66, 0.55, 0.44]),
                'ultimateRatio':     np.array([2.00, 1.88, 1.29, 1.00, 0.80, 0.69, 0.58, 0.47]),
                'modulusRatio':      np.array([1.11, 1.10, 1.05, 1.00, 0.94, 0.89, 0.84, 0.79]),
                'conductivityRatio': np.array([0.35, 0.48, 0.82, 1.00, 1.12, 1.22, 1.32, 1.42]),
                'expansionRatio':    np.array([0.55, 0.62, 0.87, 1.00, 1.06, 1.10, 1.14, 1.18]),
                'toughnessRatio':    np.array([0.78, 0.82, 0.94, 1.00, 1.04, 1.06, 1.08, 1.08]),
                'validRange': (20.0, 600.0)},
            'sources': {'typical': 'ASTM-SPEC', 'allowables': 'ASTM-SPEC', 'thermal': 'ASTM-SPEC',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'ESTIMATE-2026Q1', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

MATERIAL_DATABASE['TI-3AL-2.5V'] = {
    'commonName': 'Ti-3Al-2.5V (grade 9)', 'family': 'titanium near-alpha', 'uns': 'R56320',
    'crystalStructure': 'hcp alpha + bcc beta', 'density': 4480.0, 'poissonRatio': 0.30,
    'meltingRange': (1893.0, 1933.0), 'betaTransus': 1208.0, 'anodicIndex': 0.15,
    'relativeCost': 9.0, 'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'tube': 20, 'bar': 16},
    'specifications': ['AMS 4944 (tube, cold worked stress relieved)', 'AMS 4945 (tube)'],
    'chemistry': {'aluminium': 3.0, 'vanadium': 2.5, 'oxygen': 0.12, 'iron': 0.25},
    'incompatible': ['LOX', 'GOX', 'N2O4', 'IRFNA', 'RFNA', 'METHANOL', 'DRY CHLORINE'],
    'compatible': ['N2H4', 'MMH', 'GHE', 'GN2', 'LN2', 'RP-1', 'HYDRAULIC OIL'],
    'notes': 'The titanium tubing alloy, and essentially the only one. Formable enough to be drawn and '
             'bent cold, unlike 6-4, at 40 percent the density of a stainless line. Standard for '
             'aircraft hydraulic lines and used for spacecraft propellant lines where the mass saving '
             'over 316L justifies the cost and the fuel-side-only restriction.',
    'conditions': {
        'cwsr': {
            'description': 'Cold worked and stress relieved, the standard tubing condition',
            'forms': ['tube'], 'thicknessRange': (0.0003, 0.005),
            'typical': {'yieldStrength': 586.0e6, 'ultimateStrength': 621.0e6, 'elongation': 0.15,
                        'reductionOfArea': 0.30, 'elasticModulus': 107.0e9, 'shearModulus': 41.0e9,
                        'bearingUltimate': 1050.0e6, 'hardness': 260.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 586.0e6}, 'ultimateStrength': {'L': 621.0e6}}},
            'thermal': {'thermalConductivity': 7.6, 'specificHeat': 544.0,
                        'thermalExpansion': 9.4e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 70.0e6}, 'parisCoefficient': 5.0e-12,
                         'parisExponent': 3.3, 'thresholdRange': 4.2e6, 'stressRatio': 0.1,
                         'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 1150.0e6, 'basquinExponent': -0.085,
                        'enduranceStress': 330.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'as-drawn tube ID'},
            'environmental': {'sccThreshold': {'salt fog': 120.0e6, 'methanol': 15.0e6},
                              'sccRating': {'L': 'high', 'LT': 'high', 'ST': 'high'},
                              'hydrogenRatio': 0.78},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.62, 1.54, 1.20, 1.00, 0.85, 0.76, 0.68, 0.58]),
                'ultimateRatio':     np.array([1.56, 1.49, 1.18, 1.00, 0.87, 0.79, 0.72, 0.63]),
                'modulusRatio':      np.array([1.10, 1.09, 1.04, 1.00, 0.95, 0.91, 0.86, 0.81]),
                'conductivityRatio': np.array([0.30, 0.40, 0.80, 1.00, 1.16, 1.30, 1.44, 1.58]),
                'expansionRatio':    np.array([0.55, 0.62, 0.87, 1.00, 1.06, 1.10, 1.14, 1.18]),
                'toughnessRatio':    np.array([0.75, 0.79, 0.93, 1.00, 1.04, 1.07, 1.09, 1.09]),
                'validRange': (20.0, 600.0)},
            'sources': {'typical': 'AMS-SPEC', 'allowables': 'AMS-SPEC', 'thermal': 'AMS-SPEC',
                        'fracture': 'ESTIMATE-2026Q1', 'fatigue': 'ESTIMATE-2026Q1',
                        'environmental': 'ESTIMATE-2026Q1', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

# -- Copper Alloys -- #
#
# Chamber liners, and essentially nothing else on a launch vehicle. The figure of merit is not
# strength, it is the combination k*sigma/(E*alpha): a liner fails by thermal strain ratcheting, so
# conductivity and strength both help and modulus and expansion both hurt.
#
# All of them are catastrophic in hydrazine. Copper catalyses decomposition.

MATERIAL_DATABASE['GRCOP-42'] = {
    'commonName': 'GRCop-42 (Cu-8Cr-4Nb)', 'family': 'copper dispersion strengthened', 'uns': None,
    'crystalStructure': 'fcc', 'density': 8756.0, 'poissonRatio': 0.33,
    'meltingRange': (1340.0, 1356.0), 'anodicIndex': 0.35, 'relativeCost': 22.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'lpbfPowder': 14, 'lpbfPart': 18},
    'specifications': ['NASA process specification, no public AMS as of 2026'],
    'chemistry': {'chromium': 8.0, 'niobium': 4.0, 'copper': 88.0},
    'incompatible': ['N2H4', 'MMH', 'AEROZINE-50', 'ACETYLENE', 'AMMONIA'],
    'compatible': ['LOX', 'GOX', 'LH2', 'GH2', 'RP-1', 'CH4', 'GHE', 'GN2'],
    'notes': 'The NASA additive chamber liner alloy. Cr2Nb precipitates pin the grain boundaries so it '
             'keeps useful strength and creep resistance to 1000 K while retaining most of copper\'s '
             'conductivity. Designed for LPBF from the start, which is why it appears in additive '
             'chambers and nowhere else. Absolutely prohibited in hydrazine.',
    'conditions': {
        'lpbf hip': {
            'description': 'LPBF, HIP 1050 C / 100 MPa',
            'forms': ['lpbf'], 'thicknessRange': (0.0005, 0.050),
            'typical': {'yieldStrength': 190.0e6, 'ultimateStrength': 290.0e6, 'elongation': 0.25,
                        'reductionOfArea': 0.35, 'elasticModulus': 125.0e9, 'shearModulus': 47.0e9,
                        'bearingUltimate': 490.0e6, 'hardness': 95.0},
            # The number that justifies the alloy. Two orders of magnitude above Inconel.
            'thermal': {'thermalConductivity': 320.0, 'specificHeat': 390.0,
                        'thermalExpansion': 17.5e-6, 'emissivity': 0.30},
            'fatigue': {'basquinCoefficient': 420.0e6, 'basquinExponent': -0.105,
                        'enduranceStress': 95.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'machined'},
            'anisotropy': {'zYieldRatio': 0.95, 'zUltimateRatio': 0.96, 'zElongationRatio': 0.88},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.92, 0.80, 0.68, 0.48, 0.34, 0.20]),
                'ultimateRatio':     np.array([1.00, 0.93, 0.82, 0.70, 0.50, 0.35, 0.21]),
                'modulusRatio':      np.array([1.00, 0.96, 0.89, 0.81, 0.72, 0.66, 0.60]),
                'conductivityRatio': np.array([1.00, 0.98, 0.94, 0.90, 0.86, 0.84, 0.82]),
                'expansionRatio':    np.array([1.00, 1.03, 1.08, 1.13, 1.19, 1.22, 1.25]),
                'validRange': (293.15, 1100.0)},
            'sources': {'typical': 'NASA-GRCOP', 'thermal': 'NASA-GRCOP', 'fatigue': 'ESTIMATE-2026Q1',
                        'anisotropy': 'ESTIMATE-2026Q1', 'temperatureCurves': 'NASA-GRCOP'}
        }
    }
}

MATERIAL_DATABASE['NARLOY-Z'] = {
    'commonName': 'NARloy-Z (Cu-3Ag-0.5Zr)', 'family': 'copper precipitation strengthened',
    'uns': None, 'crystalStructure': 'fcc', 'density': 9130.0, 'poissonRatio': 0.34,
    'meltingRange': (1320.0, 1356.0), 'anodicIndex': 0.35, 'relativeCost': 18.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'plate': 30, 'forging': 44},
    'specifications': ['Rocketdyne proprietary, no public AMS'],
    'chemistry': {'silver': 3.0, 'zirconium': 0.5, 'copper': 96.5},
    'incompatible': ['N2H4', 'MMH', 'AEROZINE-50', 'ACETYLENE', 'AMMONIA'],
    'compatible': ['LOX', 'GOX', 'LH2', 'GH2', 'RP-1', 'CH4', 'GHE', 'GN2'],
    'notes': 'The SSME main combustion chamber liner alloy, and the reference every newer copper alloy '
             'is measured against. Higher conductivity than GRCop-42 and lower elevated temperature '
             'strength, so it is the better choice for a wrought liner and the worse one for an '
             'additive part running hot.',
    'conditions': {
        'aged': {
            'description': 'Solution treated and aged',
            'forms': ['plate', 'forging'], 'thicknessRange': (0.003, 0.075),
            'typical': {'yieldStrength': 165.0e6, 'ultimateStrength': 315.0e6, 'elongation': 0.28,
                        'reductionOfArea': 0.40, 'elasticModulus': 124.0e9, 'shearModulus': 46.0e9,
                        'bearingUltimate': 530.0e6, 'hardness': 90.0},
            'thermal': {'thermalConductivity': 345.0, 'specificHeat': 385.0,
                        'thermalExpansion': 18.0e-6, 'emissivity': 0.30},
            'fatigue': {'basquinCoefficient': 450.0e6, 'basquinExponent': -0.110,
                        'enduranceStress': 90.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'machined'},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.88, 0.72, 0.55, 0.32, 0.20, 0.10]),
                'ultimateRatio':     np.array([1.00, 0.90, 0.74, 0.57, 0.34, 0.21, 0.11]),
                'modulusRatio':      np.array([1.00, 0.96, 0.88, 0.80, 0.70, 0.64, 0.58]),
                'conductivityRatio': np.array([1.00, 0.98, 0.95, 0.91, 0.87, 0.85, 0.83]),
                'expansionRatio':    np.array([1.00, 1.03, 1.08, 1.13, 1.19, 1.22, 1.25]),
                'validRange': (293.15, 1000.0)},
            'sources': {'typical': 'NASA-GRCOP', 'thermal': 'NASA-GRCOP', 'fatigue': 'ESTIMATE-2026Q1',
                        'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

MATERIAL_DATABASE['C18150'] = {
    'commonName': 'C18150 CuCrZr', 'family': 'copper precipitation hardening', 'uns': 'C18150',
    'crystalStructure': 'fcc', 'density': 8900.0, 'poissonRatio': 0.33,
    'meltingRange': (1348.0, 1356.0), 'anodicIndex': 0.35, 'relativeCost': 6.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 10, 'plate': 14},
    'specifications': ['ASTM B441', 'UNS C18150'],
    'chemistry': {'chromium': 0.8, 'zirconium': 0.08, 'copper': 99.0},
    'incompatible': ['N2H4', 'MMH', 'AEROZINE-50', 'ACETYLENE', 'AMMONIA'],
    'compatible': ['LOX', 'GOX', 'LH2', 'GH2', 'RP-1', 'CH4', 'GHE', 'GN2', 'WATER'],
    'notes': 'The commercially available copper alloy, at a fraction of the cost and lead time of the '
             'purpose-built liner alloys. Lower elevated temperature capability, but for a heat '
             'exchanger, an electrode, or a development chamber that does not need to survive many '
             'cycles, it is the sensible choice.',
    'conditions': {
        'aged': {
            'description': 'Solution treated 980 C, cold worked, aged 450 C',
            'forms': ['bar', 'plate'], 'thicknessRange': (0.003, 0.100),
            'typical': {'yieldStrength': 350.0e6, 'ultimateStrength': 450.0e6, 'elongation': 0.18,
                        'reductionOfArea': 0.45, 'elasticModulus': 128.0e9, 'shearModulus': 48.0e9,
                        'bearingUltimate': 760.0e6, 'hardness': 140.0},
            'allowables': {
                'S': {'yieldStrength': {'L': 310.0e6}, 'ultimateStrength': {'L': 415.0e6}}},
            'thermal': {'thermalConductivity': 320.0, 'specificHeat': 385.0,
                        'thermalExpansion': 17.0e-6, 'emissivity': 0.30},
            'fatigue': {'basquinCoefficient': 640.0e6, 'basquinExponent': -0.108,
                        'enduranceStress': 130.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'machined'},
            'temperatureCurves': {
                'temperature': HOT_GRID,
                'yieldRatio':        np.array([1.00, 0.90, 0.72, 0.48, 0.20, 0.12, 0.06]),
                'ultimateRatio':     np.array([1.00, 0.91, 0.74, 0.50, 0.22, 0.13, 0.07]),
                'modulusRatio':      np.array([1.00, 0.96, 0.88, 0.80, 0.70, 0.64, 0.58]),
                'conductivityRatio': np.array([1.00, 0.98, 0.95, 0.91, 0.87, 0.85, 0.83]),
                'expansionRatio':    np.array([1.00, 1.03, 1.08, 1.13, 1.19, 1.22, 1.25]),
                'validRange': (293.15, 900.0)},
            'sources': {'typical': 'ASTM-SPEC', 'allowables': 'ASTM-SPEC', 'thermal': 'ASTM-SPEC',
                        'fatigue': 'ESTIMATE-2026Q1', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

# -- Low Alloy Steels -- #
#
# High strength at low cost, and two disqualifying properties: body-centred cubic, so they go brittle
# cold, and severely hydrogen embrittlement susceptible above about 1000 MPa ultimate. Present for
# solid rocket motor cases, landing gear and pyrotechnic hardware, and as the cautionary example in
# the hydrogen document.

MATERIAL_DATABASE['4340'] = {
    'commonName': 'AISI 4340 (quenched and tempered)', 'family': 'low alloy steel', 'uns': 'G43400',
    'crystalStructure': 'bcc martensite', 'density': 7850.0, 'poissonRatio': 0.29,
    'meltingRange': (1700.0, 1755.0), 'anodicIndex': 0.85, 'relativeCost': 0.4,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 4, 'plate': 6, 'forging': 18},
    'specifications': ['AMS 6414 (bar)', 'AMS 6415 (bar)', 'SAE J404'],
    'chemistry': {'chromium': 0.80, 'nickel': 1.80, 'molybdenum': 0.25, 'carbon': 0.40},
    'incompatible': ['LH2', 'GH2', 'H2S', 'LN2 STRUCTURAL', 'CRYOGENIC SERVICE', 'N2H4'],
    'compatible': ['RP-1', 'GN2', 'GHE', 'HYDRAULIC OIL'],
    'notes': 'The classic high strength structural steel: 1790 MPa ultimate for the price of mild '
             'steel. Two things disqualify it from most launch vehicle use. It is BCC, so it is '
             'brittle at cryogenic temperature. And above 1000 MPa ultimate it is severely hydrogen '
             'embrittlement susceptible, so any plating operation demands a bake per ASTM F1940 and '
             'any hydrogen exposure at all is disqualifying.',
    'conditions': {
        'qt-260': {
            'description': 'Quenched and tempered to 260 ksi (1793 MPa) ultimate',
            'forms': ['bar', 'plate', 'forging'], 'thicknessRange': (0.003, 0.150),
            'typical': {'yieldStrength': 1520.0e6, 'ultimateStrength': 1793.0e6, 'elongation': 0.10,
                        'reductionOfArea': 0.35, 'elasticModulus': 200.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 2760.0e6, 'hardness': 520.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 1448.0e6, 'LT': 1448.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1724.0e6, 'LT': 1724.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 1483.0e6, 'LT': 1483.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1758.0e6, 'LT': 1758.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 44.5, 'specificHeat': 475.0,
                        'thermalExpansion': 12.3e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 50.0e6, 'T-L': 45.0e6},
                         'parisCoefficient': 6.9e-12, 'parisExponent': 3.0,
                         'thresholdRange': 3.0e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 3100.0e6, 'basquinExponent': -0.090,
                        'enduranceStress': 760.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'polished'},
            # 0.18 is catastrophic. A notched bar in hydrogen retains 18 percent of its air strength.
            'environmental': {'sccThreshold': {'marine air': 170.0e6, 'H2S': 50.0e6},
                              'sccRating': {'L': 'very low', 'LT': 'very low', 'ST': 'very low'},
                              'hydrogenRatio': 0.18, 'pren': 0.8},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.22, 1.20, 1.08, 1.00, 0.95, 0.92, 0.86, 0.76]),
                'ultimateRatio':     np.array([1.28, 1.25, 1.09, 1.00, 0.96, 0.93, 0.87, 0.77]),
                'modulusRatio':      np.array([1.08, 1.06, 1.03, 1.00, 0.96, 0.93, 0.89, 0.84]),
                'conductivityRatio': np.array([0.28, 0.62, 0.88, 1.00, 1.02, 1.00, 0.96, 0.90]),
                'expansionRatio':    np.array([0.45, 0.58, 0.87, 1.00, 1.05, 1.09, 1.13, 1.17]),
                # The BCC collapse. Toughness at 77 K is a tenth of the room temperature value and
                # this is why a 4340 part is never a cryogenic part.
                'toughnessRatio':    np.array([0.08, 0.12, 0.55, 1.00, 1.10, 1.16, 1.20, 1.22]),
                'validRange': (77.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

MATERIAL_DATABASE['300M'] = {
    'commonName': '300M (modified 4340)', 'family': 'low alloy steel', 'uns': 'K44220',
    'crystalStructure': 'bcc martensite', 'density': 7870.0, 'poissonRatio': 0.29,
    'meltingRange': (1700.0, 1755.0), 'anodicIndex': 0.85, 'relativeCost': 0.9,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'bar': 10, 'forging': 26},
    'specifications': ['AMS 6417 (bar)', 'AMS 6419'],
    'chemistry': {'chromium': 0.80, 'nickel': 1.80, 'molybdenum': 0.40, 'carbon': 0.42,
                  'silicon': 1.60, 'vanadium': 0.08},
    'incompatible': ['LH2', 'GH2', 'H2S', 'CRYOGENIC SERVICE', 'N2H4'],
    'compatible': ['RP-1', 'GN2', 'GHE', 'HYDRAULIC OIL'],
    'notes': 'Silicon-modified 4340 with higher hardenability and higher tempering temperature, giving '
             '1970 MPa ultimate in heavy sections. The landing gear and solid motor case alloy. Every '
             'hydrogen and cryogenic caveat that applies to 4340 applies here more strongly.',
    'conditions': {
        'qt-280': {
            'description': 'Quenched and tempered to 280 ksi (1931 MPa) ultimate',
            'forms': ['bar', 'forging'], 'thicknessRange': (0.006, 0.250),
            'typical': {'yieldStrength': 1690.0e6, 'ultimateStrength': 1965.0e6, 'elongation': 0.08,
                        'reductionOfArea': 0.30, 'elasticModulus': 200.0e9, 'shearModulus': 77.0e9,
                        'bearingUltimate': 2960.0e6, 'hardness': 555.0},
            'allowables': {
                'A': {'yieldStrength': {'L': 1586.0e6, 'LT': 1586.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1862.0e6, 'LT': 1862.0e6, 'ST': None}},
                'B': {'yieldStrength': {'L': 1620.0e6, 'LT': 1620.0e6, 'ST': None},
                      'ultimateStrength': {'L': 1896.0e6, 'LT': 1896.0e6, 'ST': None}}},
            'thermal': {'thermalConductivity': 42.0, 'specificHeat': 475.0,
                        'thermalExpansion': 12.6e-6, 'emissivity': 0.30},
            'fracture': {'planeStrainToughness': {'L-T': 60.0e6, 'T-L': 54.0e6},
                         'parisCoefficient': 7.5e-12, 'parisExponent': 3.0,
                         'thresholdRange': 2.8e6, 'stressRatio': 0.1, 'environment': 'lab air, 296 K'},
            'fatigue': {'basquinCoefficient': 3400.0e6, 'basquinExponent': -0.090,
                        'enduranceStress': 830.0e6, 'runoutCycles': 1.0e7, 'stressRatio': -1.0,
                        'surfaceCondition': 'shot peened'},
            'environmental': {'sccThreshold': {'marine air': 140.0e6, 'H2S': 40.0e6},
                              'sccRating': {'L': 'very low', 'LT': 'very low', 'ST': 'very low'},
                              'hydrogenRatio': 0.15, 'pren': 0.8},
            'temperatureCurves': {
                'temperature': CRYO_TO_HOT_GRID,
                'yieldRatio':        np.array([1.20, 1.18, 1.07, 1.00, 0.95, 0.92, 0.87, 0.78]),
                'ultimateRatio':     np.array([1.26, 1.23, 1.08, 1.00, 0.96, 0.93, 0.88, 0.79]),
                'modulusRatio':      np.array([1.08, 1.06, 1.03, 1.00, 0.96, 0.93, 0.89, 0.84]),
                'conductivityRatio': np.array([0.28, 0.62, 0.88, 1.00, 1.02, 1.00, 0.96, 0.90]),
                'expansionRatio':    np.array([0.45, 0.58, 0.87, 1.00, 1.05, 1.09, 1.13, 1.17]),
                'toughnessRatio':    np.array([0.07, 0.11, 0.53, 1.00, 1.10, 1.16, 1.20, 1.22]),
                'validRange': (77.0, 700.0)},
            'sources': {'typical': 'MMPDS-TYPICAL', 'allowables': 'MMPDS-STATISTICAL',
                        'thermal': 'MMPDS-TYPICAL', 'fracture': 'DAMAGE-TOLERANT-HANDBOOK',
                        'fatigue': 'ESTIMATE-2026Q1', 'environmental': 'NASA-SP-8040',
                        'temperatureCurves': 'MMPDS-CURVE'}
        }
    }
}

# -- Composites -- #
#
# Orthotropic, so a single yield strength is meaningless and the fields below are the longitudinal
# lamina values. A real composite analysis needs laminate theory and the full stiffness matrix, which
# is aerospaceStructures territory. What is here supports a material selection trade and a COPV
# overwrap sizing, and no more than that.

MATERIAL_DATABASE['IM7/8552'] = {
    'commonName': 'IM7/8552 carbon-epoxy unidirectional', 'family': 'composite lamina', 'uns': None,
    'crystalStructure': 'n/a', 'density': 1570.0, 'poissonRatio': 0.32,
    'meltingRange': None, 'glassTransition': 473.0, 'anodicIndex': 0.00, 'relativeCost': 12.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'prepreg': 12},
    'specifications': ['NCAMP NMS 128 (qualification)'],
    # Carbon is strongly cathodic. A carbon laminate bolted to aluminium is a galvanic couple with a
    # 0.9 V difference and an unfavourable area ratio, and it will destroy the aluminium.
    'incompatible': ['DIRECT ALUMINIUM CONTACT', 'LOX', 'GOX', 'N2O4'],
    'compatible': ['GHE', 'GN2', 'RP-1', 'DRY AIR'],
    'notes': 'The aerospace structural prepreg reference. Autoclave cured 177 C. Numbers below are '
             'unidirectional lamina properties in the fibre direction: transverse strength is roughly '
             '2 percent of longitudinal, which is the whole reason laminates exist. Isolate from '
             'aluminium with glass ply or a sealant.',
    'conditions': {
        'autoclave cured': {
            'description': 'Autoclave cured 177 C / 585 kPa, 60 percent fibre volume',
            'forms': ['prepreg tape', 'prepreg fabric'], 'thicknessRange': (0.000125, 0.050),
            'typical': {'yieldStrength': 2720.0e6, 'ultimateStrength': 2720.0e6, 'elongation': 0.016,
                        'elasticModulus': 161.0e9, 'shearModulus': 5.2e9,
                        'transverseStrength': 64.0e6, 'transverseModulus': 11.4e9,
                        'compressiveStrength': 1690.0e6, 'interlaminarShear': 128.0e6},
            'allowables': {
                'A': {'ultimateStrength': {'L': 2280.0e6}},
                'B': {'ultimateStrength': {'L': 2450.0e6}}},
            'thermal': {'thermalConductivity': 5.4, 'specificHeat': 1130.0,
                        'thermalExpansion': -0.4e-6, 'emissivity': 0.85},
            'environmental': {'sccRating': {'L': 'n/a'}, 'hydrogenRatio': 1.00,
                              'moistureKnockdown': 0.85},
            'temperatureCurves': {
                'temperature': np.array([20.0, 77.0, 200.0, 293.15, 350.0, 400.0, 440.0]),
                'yieldRatio':        np.array([1.05, 1.04, 1.02, 1.00, 0.95, 0.85, 0.62]),
                'ultimateRatio':     np.array([1.05, 1.04, 1.02, 1.00, 0.95, 0.85, 0.62]),
                'modulusRatio':      np.array([1.02, 1.02, 1.01, 1.00, 0.98, 0.94, 0.80]),
                'conductivityRatio': np.array([0.30, 0.50, 0.85, 1.00, 1.06, 1.11, 1.15]),
                'expansionRatio':    np.array([0.60, 0.70, 0.90, 1.00, 1.05, 1.10, 1.14]),
                'validRange': (20.0, 440.0)},
            'sources': {'typical': 'CMH-17', 'allowables': 'CMH-17', 'thermal': 'CMH-17',
                        'environmental': 'CMH-17', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

MATERIAL_DATABASE['T1000G'] = {
    'commonName': 'T1000G carbon-epoxy filament wound overwrap', 'family': 'composite lamina',
    'uns': None, 'crystalStructure': 'n/a', 'density': 1600.0, 'poissonRatio': 0.30,
    'meltingRange': None, 'glassTransition': 400.0, 'anodicIndex': 0.00, 'relativeCost': 20.0,
    'costBasisDate': '2026-Q1',
    'leadTimeWeeks': {'towpreg': 16},
    'specifications': ['Vendor qualification, no public AMS'],
    'incompatible': ['DIRECT ALUMINIUM CONTACT', 'LOX', 'GOX', 'N2O4', 'SUSTAINED UV'],
    'compatible': ['GHE', 'GN2', 'DRY AIR'],
    'notes': 'COPV overwrap fibre. The strength number is impressive and misleading: a COPV is not '
             'sized on ultimate, it is sized on stress rupture, because a composite under sustained '
             'load fails after a time that depends on the stress ratio. AIAA S-081 exists for this '
             'reason and the design stress ratio is typically held below 0.5.',
    'conditions': {
        'filament wound': {
            'description': 'Wet or towpreg filament wound, cured 121 C, 65 percent fibre volume',
            'forms': ['towpreg', 'wet winding'], 'thicknessRange': (0.0005, 0.040),
            'typical': {'yieldStrength': 3040.0e6, 'ultimateStrength': 3040.0e6, 'elongation': 0.019,
                        'elasticModulus': 165.0e9, 'shearModulus': 5.0e9,
                        'transverseStrength': 50.0e6, 'transverseModulus': 9.0e9,
                        'interlaminarShear': 75.0e6},
            'allowables': {
                'A': {'ultimateStrength': {'L': 2430.0e6}},
                'B': {'ultimateStrength': {'L': 2620.0e6}}},
            'thermal': {'thermalConductivity': 4.5, 'specificHeat': 1100.0,
                        'thermalExpansion': -0.5e-6, 'emissivity': 0.85},
            # The number that actually sizes a COPV. Above this stress ratio the vessel has a finite
            # and calculable life under sustained pressure.
            'stressRupture': {'designStressRatio': 0.50, 'thousandHourRatio': 0.72,
                              'lifeExponent': 0.045},
            'environmental': {'hydrogenRatio': 1.00, 'moistureKnockdown': 0.88},
            'temperatureCurves': {
                'temperature': np.array([20.0, 77.0, 200.0, 293.15, 350.0, 380.0]),
                'yieldRatio':        np.array([1.06, 1.05, 1.02, 1.00, 0.92, 0.78]),
                'ultimateRatio':     np.array([1.06, 1.05, 1.02, 1.00, 0.92, 0.78]),
                'modulusRatio':      np.array([1.02, 1.02, 1.01, 1.00, 0.97, 0.90]),
                'conductivityRatio': np.array([0.30, 0.50, 0.85, 1.00, 1.06, 1.09]),
                'expansionRatio':    np.array([0.60, 0.70, 0.90, 1.00, 1.05, 1.08]),
                'validRange': (20.0, 380.0)},
            'sources': {'typical': 'ESTIMATE-2026Q1', 'allowables': 'ESTIMATE-2026Q1',
                        'thermal': 'ESTIMATE-2026Q1', 'stressRupture': 'ESTIMATE-2026Q1',
                        'environmental': 'ESTIMATE-2026Q1', 'temperatureCurves': 'ESTIMATE-2026Q1'}
        }
    }
}

# ------------------------------------------------------------------------------------------------ #
# -- Common Package Seed Merge -- #
# ------------------------------------------------------------------------------------------------ #

# The nine alloys carried by orbitalRockets/common/materials.py are merged in here rather than
# re-typed, so 316L's yield strength is written down in exactly one place in the repository.
#
# The direction matters. This module depends on common, not the reverse: common has to stay importable
# on its own, and every domain that only needs a preliminary property lookup should keep paying only
# for that. What this file adds on top is the extra conditions, the allowables, the curves and the
# fracture and fatigue data that no other domain needs.
#
# testSeedAgreement asserts that queryMaterial and materialProperties return identical values on the
# seeded properties, so an edit to either file that breaks the agreement fails a test rather than
# silently producing two different answers to the same question.

SEEDED_FROM_COMMON = {
    '304L':        ('304L',        'annealed'),
    '316L':        ('316L',        'annealed'),
    '321':         ('321',         'annealed'),
    '6061':        ('6061-T6',     't6'),
    '7075':        ('7075-T73',    't73'),
    'INCONEL 718': ('INCONEL 718', 'sta'),
    'INCONEL 625': ('INCONEL 625', 'annealed'),
    'TI-6AL-4V':   ('TI-6AL-4V',   'annealed'),
    'MONEL 400':   ('MONEL 400',   'annealed')
}

# Alloy-level properties that come from common. These sit on the alloy record, not the condition,
# because they do not change with heat treatment to any degree worth modelling.
SEEDED_ALLOY_PROPERTIES = ('density', 'poissonRatio')

# Condition-level mechanical properties from common.
SEEDED_TYPICAL_PROPERTIES = ('yieldStrength', 'ultimateStrength', 'elasticModulus')

# Condition-level thermal properties from common.
SEEDED_THERMAL_PROPERTIES = ('thermalConductivity', 'thermalExpansion')

def _mergeCommonSeed() -> None:

    '''

    Overlay the room-temperature scalars from common/materials.py onto the seeded conditions.

    Runs once at import. Values already present in this file are NOT overwritten, so a condition can
    deliberately carry its own number where the two genuinely differ, but for the seeded conditions
    every field listed above is left as np.nan or absent above and filled here.

    '''

    for databaseKey, (commonKey, conditionKey) in SEEDED_FROM_COMMON.items():

        commonEntry = materialProperties(commonKey, 293.15)
        alloyRecord = MATERIAL_DATABASE[databaseKey]

        # -- Alloy level -- #

        for name in SEEDED_ALLOY_PROPERTIES:
            current = alloyRecord.get(name, np.nan)
            if current is None or (isinstance(current, float) and np.isnan(current)):
                alloyRecord[name] = commonEntry[name]

        if alloyRecord.get('notes') is None:
            alloyRecord['notes'] = commonEntry['notes']

        # -- Condition level -- #

        conditionRecord = alloyRecord['conditions'][conditionKey]

        typicalBlock = conditionRecord.setdefault('typical', {})
        for name in SEEDED_TYPICAL_PROPERTIES:
            if name not in typicalBlock:
                typicalBlock[name] = commonEntry[name]

        thermalBlock = conditionRecord.setdefault('thermal', {})
        for name in SEEDED_THERMAL_PROPERTIES:
            if name not in thermalBlock:
                thermalBlock[name] = commonEntry[name]

        # The cryogenic factor common uses for its linear correction, carried through so
        # testCryogenicModelReconciliation can compare the two models directly.
        conditionRecord['commonCryogenicYieldFactor'] = commonEntry['cryogenicYieldFactor']

_mergeCommonSeed()
