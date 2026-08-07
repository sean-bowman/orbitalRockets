
# -- Material Property Lookup [orbitalRockets common] -- #

'''

Structural and thermal property lookup for the alloys used across aerospace vehicle hardware,
plus surface roughness by material and manufacturing process.

Room-temperature values with a linear cryogenic correction where one is meaningful. These are
typical handbook values for preliminary sizing, NOT design allowables. Use MMPDS or the material
specification for anything that flies.

This module is the seed for the aerospaceMaterials domain, which extends it with A-basis and
B-basis allowables, temperature-dependent curves, and fatigue and fracture data.

Author: Sean Bowman
Date:   08/06/2026

'''

import numpy as np

#--------------------------------------------------------------------------------------------------------------------------#
# -- Material and Surface Data -- #
#--------------------------------------------------------------------------------------------------------------------------#

def materialProperties(material: str, temperature: float = 293.15) -> dict:

    '''

    Structural and thermal property lookup for the alloys that show up in aerospace fluid systems.

    Room-temperature values with a linear cryogenic correction where one is meaningful. These are
    typical handbook values for preliminary sizing, NOT design allowables. Use MMPDS or the material
    specification for anything that flies.

    Returned dictionary keys, all mass-base SI:
        'density'              [kg/m^3]
        'yieldStrength'        [Pa]   0.2 % offset at the requested temperature
        'ultimateStrength'     [Pa]
        'elasticModulus'       [Pa]
        'poissonRatio'         [-]
        'thermalConductivity'  [W/m-K]
        'thermalExpansion'     [1/K]  mean CTE from 293 K to the requested temperature
        'allowableStress'      [Pa]   ASME B31.3 style, min(2/3 yield, 1/3.5 ultimate)
        'notes'                [str]  the thing that will bite you with this alloy

    '''

    materialTable = {
        '304L': {
            'density': 8000.0, 'yieldStrength': 170.0e6, 'ultimateStrength': 485.0e6,
            'elasticModulus': 193.0e9, 'poissonRatio': 0.29, 'thermalConductivity': 16.2,
            'thermalExpansion': 17.3e-6, 'cryogenicYieldFactor': 2.5,
            'notes': 'Austenitic, fully ductile to LH2 temperature, non-magnetic until cold worked. Low carbon variant resists sensitization during welding.'
        },
        '316L': {
            'density': 8000.0, 'yieldStrength': 170.0e6, 'ultimateStrength': 485.0e6,
            'elasticModulus': 193.0e9, 'poissonRatio': 0.29, 'thermalConductivity': 16.3,
            'thermalExpansion': 16.0e-6, 'cryogenicYieldFactor': 2.4,
            'notes': 'The default aerospace fluid system alloy. Molybdenum adds pitting resistance. Compatible with hydrazine, LOX and cryogens. Galls badly against itself in threaded joints without plating.'
        },
        '321': {
            'density': 8000.0, 'yieldStrength': 205.0e6, 'ultimateStrength': 515.0e6,
            'elasticModulus': 193.0e9, 'poissonRatio': 0.29, 'thermalConductivity': 16.1,
            'thermalExpansion': 16.6e-6, 'cryogenicYieldFactor': 2.3,
            'notes': 'Titanium stabilized against sensitization. Preferred where welds see 800-1500 F service, common in hot gas and gas generator lines.'
        },
        '6061-T6': {
            'density': 2700.0, 'yieldStrength': 276.0e6, 'ultimateStrength': 310.0e6,
            'elasticModulus': 68.9e9, 'poissonRatio': 0.33, 'thermalConductivity': 167.0,
            'thermalExpansion': 23.6e-6, 'cryogenicYieldFactor': 1.25,
            'notes': 'Loses roughly 40 percent of its yield strength in the weld heat affected zone and does not recover without a full solution treat and age. Never size an aluminum weldment on parent metal properties.'
        },
        '7075-T73': {
            'density': 2810.0, 'yieldStrength': 435.0e6, 'ultimateStrength': 505.0e6,
            'elasticModulus': 71.7e9, 'poissonRatio': 0.33, 'thermalConductivity': 155.0,
            'thermalExpansion': 23.4e-6, 'cryogenicYieldFactor': 1.2,
            'notes': 'High strength but not weldable and susceptible to stress corrosion cracking in the short transverse direction. Fittings and manifold bodies only.'
        },
        'INCONEL 718': {
            'density': 8190.0, 'yieldStrength': 1034.0e6, 'ultimateStrength': 1276.0e6,
            'elasticModulus': 200.0e9, 'poissonRatio': 0.29, 'thermalConductivity': 11.4,
            'thermalExpansion': 13.0e-6, 'cryogenicYieldFactor': 1.15,
            'notes': 'Precipitation hardened, requires post-weld solution and age to recover joint properties. Resistant to hydrogen embrittlement relative to other superalloys but not immune.'
        },
        'INCONEL 625': {
            'density': 8440.0, 'yieldStrength': 414.0e6, 'ultimateStrength': 827.0e6,
            'elasticModulus': 207.0e9, 'poissonRatio': 0.31, 'thermalConductivity': 9.8,
            'thermalExpansion': 12.8e-6, 'cryogenicYieldFactor': 1.2,
            'notes': 'Solid solution strengthened, weldable without post-weld heat treatment. Common for hot gas ducting and bellows.'
        },
        'TI-6AL-4V': {
            'density': 4430.0, 'yieldStrength': 880.0e6, 'ultimateStrength': 950.0e6,
            'elasticModulus': 113.8e9, 'poissonRatio': 0.342, 'thermalConductivity': 6.7,
            'thermalExpansion': 8.6e-6, 'cryogenicYieldFactor': 1.4,
            'notes': 'Outstanding strength to weight for pressure vessels. Absolutely incompatible with LOX, GOX, red fuming nitric acid and N2O4: it is impact sensitive and will burn. Never use in an oxidizer system.'
        },
        'MONEL 400': {
            'density': 8800.0, 'yieldStrength': 240.0e6, 'ultimateStrength': 550.0e6,
            'elasticModulus': 179.0e9, 'poissonRatio': 0.32, 'thermalConductivity': 21.8,
            'thermalExpansion': 13.9e-6, 'cryogenicYieldFactor': 1.5,
            'notes': 'Nickel-copper, one of the few alloys usable in gaseous fluorine and high concentration hydrogen peroxide service. Expensive and hard to machine.'
        }
    }

    key = material.strip().upper()
    if key not in materialTable:
        raise KeyError(f'materialProperties has no entry for \'{material}\'. Available: {sorted(materialTable.keys())}')

    entry = dict(materialTable[key])

    # Cryogenic strength correction. Austenitic stainless and nickel alloys gain substantial strength
    # on cooling; the factor is applied linearly between room temperature and 77 K and held constant
    # below that. This is a preliminary-sizing approximation, not a design allowable.
    if temperature < 293.15:
        fraction              = min(1.0, (293.15 - temperature) / (293.15 - 77.0))
        strengthFactor        = 1.0 + fraction * (entry['cryogenicYieldFactor'] - 1.0)
        entry['yieldStrength']    *= strengthFactor
        entry['ultimateStrength'] *= strengthFactor

    # ASME B31.3 style basic allowable stress. The governing criterion below the creep range is the
    # lesser of two thirds of yield and one third of ultimate (B31.3 uses 1/3 UTS; the 3.5 divisor
    # here is the more conservative Section VIII Division 1 basis, kept because flight hardware
    # rarely gets to use the thinner of the two).
    entry['allowableStress'] = min(2.0 / 3.0 * entry['yieldStrength'], entry['ultimateStrength'] / 3.5)
    entry['temperature']     = temperature

    return entry

def roughnessTable(surface: str = 'drawn tube') -> float:

    '''

    Absolute surface roughness [m] by material and manufacturing process.

    Roughness only matters through eps/D, so it matters enormously in small-bore tubing and barely
    at all in a large duct. A 0.0015 mm drawn-tube roughness in a 6 mm ID line is eps/D = 2.5e-4,
    which is squarely in the roughness-dependent part of the Moody diagram.

    The additive entries are the ones people get wrong: as-built LPBF internal surfaces are one to
    two orders of magnitude rougher than drawn tube, and downskin surfaces are worse than upskin.
    An additively manufactured manifold sized on drawn-tube roughness will under-predict its
    pressure drop by a large factor.

    '''

    roughnessValues = {
        'drawn tube':        1.5e-6,    # drawn stainless, copper, aluminum tubing
        'commercial steel':  45.0e-6,   # welded and seamless steel pipe
        'stainless pipe':    15.0e-6,   # commercial stainless pipe
        'galvanized':        150.0e-6,
        'cast iron':         260.0e-6,
        'concrete':          1000.0e-6,
        'glass':             0.0,       # hydraulically smooth
        'flexhose':          300.0e-6,  # convoluted metal hose, dominated by the convolutions
        'braided flexhose':  500.0e-6,
        'lpbf as-built':     20.0e-6,   # laser powder bed fusion, upskin, well developed parameters
        'lpbf downskin':     40.0e-6,   # overhanging surfaces, partially sintered powder adhesion
        'lpbf abrasive flow': 5.0e-6,   # after abrasive flow machining of internal passages
        'ded as-built':      100.0e-6   # directed energy deposition
    }

    key = surface.strip().lower()
    if key not in roughnessValues:
        raise KeyError(f'roughnessTable has no entry for \'{surface}\'. Available: {sorted(roughnessValues.keys())}')

    return roughnessValues[key]
