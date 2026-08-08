
# -- environmentsAndLoads worked example -- #

'''

Deriving a component environment from flight data, and comparing it against the generic
specification the same hardware is currently qualified to.

fluidSystems/fluidSystemsTesting/codeInterface.py qualifies the 100 N hydrazine feed system
against the key 'launch vehicle component'. That is a generic environment: a reasonable shape at a
plausible level, chosen rather than derived. It is what almost every programme uses before it has
flight data, and it is entirely defensible as long as everyone knows that is what it is.

This example derives the environment instead, from six flights of accelerometer data in the
correct zone, and reports the difference. The difference is the point. A derived environment can
come out above or below the generic one, and which way it goes decides whether the programme has
been over-testing or under-testing without knowing it.

The chain, with every step visible:

    1. flight measurements        six flights, one zone, one band
    2. statistical limit          mean + k sigma on the decibel values, at a stated basis
    3. maximum predicted          the MPE, applied to the measured spectral shape
    4. zone adjustment            which dominates everything else
    5. acceptance and qualification   the margin ladder
    6. cross-checks               acoustic, shock, thermal, load factors

Run:
    python environmentsAndLoads/codeInterface.py

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
                                'environmentsAndLoadsLibrary'))

from environmentsUtils import overallRms, ratioToDecibel, decibelToRatio
from RandomVibrationSpec import RandomVibrationSpec
from ShockSpectrum import ShockSpectrum
from AcousticSpec import AcousticSpec
from ThermalEnvironment import ThermalEnvironment
from LoadFactorSet import LoadFactorSet

ASSET = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'environmentsAndLoadsLibrary', 'assets',
                     'componentEnvironmentExample.json')

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
# -- Stage 1: what is currently assumed -- #
# ------------------------------------------------------------------------------------------------ #

def reportGeneric(case: dict) -> dict:

    banner('1. THE GENERIC SPECIFICATION CURRENTLY IN USE')

    inherited = case['inherited']
    generic   = [(frequency, density)
                 for frequency, density in inherited['genericVibrationSpectrum']]

    grms = overallRms(generic)

    print(f'  Linked case      : {case["linkedCase"]}')
    print(f'  Environment key  : \'{inherited["genericVibrationKey"]}\'')
    print(f'  Overall level    : {grms:.2f} Grms')
    print(f'  Flight duration  : {inherited["flightDuration"]:.0f} s')
    print()
    print('  This is a generic environment. It was chosen from a table, not derived from')
    print('  measurements of this vehicle in this zone. That is the normal state of affairs')
    print('  before flight data exists, and it is defensible as long as it is labelled.')

    return {'spectrum': generic, 'grms': grms}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the derivation -- #
# ------------------------------------------------------------------------------------------------ #

def deriveEnvironment(case: dict) -> dict:

    banner('2. DERIVING THE ENVIRONMENT FROM FLIGHT DATA')

    flight = case['flightData']
    shape  = [(frequency, density) for frequency, density in case['derivedShape']['breakpoints']]

    spec = RandomVibrationSpec()
    spec.setInputs({'breakpoints':         shape,
                    'flightMeasurements':  flight['measurements'],
                    'statisticalBasis':    flight['statisticalBasis'],
                    'zone':                flight['zone'],
                    'qualificationMargin': case['margins']['qualificationMarginRandom'],
                    'acceptanceDuration':  case['margins']['acceptanceDuration'],
                    'durationFactor':      case['margins']['durationFactor'],
                    'fatigueExponent':     case['margins']['fatigueExponent']})

    statistics = spec.deriveMaximumPredicted()

    print(f'  {statistics["sampleCount"]} flights, band '
          f'{flight["band"][0]:.0f} to {flight["band"][1]:.0f} Hz, zone \'{flight["zone"]}\'')
    print()
    print(f'    sample mean          {10.0 ** (statistics["meanDecibels"] / 10.0):.4f} g^2/Hz')
    print(f'    standard deviation   {statistics["standardDeviation"]:.2f} dB')
    print(f'    basis                {statistics["basis"]}, k = '
          f'{statistics["toleranceFactor"]:.3f}')
    print(f'    maximum predicted    {statistics["limitValue"]:.4f} g^2/Hz '
          f'({statistics["marginOverMean"]:+.2f} dB over the mean)')
    print()
    for finding in statistics['findings']:
        print(f'    - {finding}')

    # The shape comes from the measurements and the level comes from the statistics, so the shape
    # has to be normalised onto the derived maximum predicted value in the band it was measured
    # over. Reporting the statistics and then plotting the unscaled shape would be a derivation
    # that never reached the spectrum.
    bandLevel = np.interp(np.mean(flight['band']),
                          [frequency for frequency, _ in shape],
                          [density for _, density in shape])

    normalisation = ratioToDecibel(statistics['limitValue'] / bandLevel, quantity = 'power')

    spec.setInputs({'breakpoints': [(frequency, density * statistics['limitValue'] / bandLevel)
                                    for frequency, density in shape]})

    overall = spec.calculateOverallLevel()

    print()
    print(f'  Normalising the measured shape onto the derived level:')
    print(f'    shape level in band  {bandLevel:.4f} g^2/Hz')
    print(f'    derived level        {statistics["limitValue"]:.4f} g^2/Hz')
    print(f'    normalisation        {normalisation:+.2f} dB')
    print()
    print(f'  Derived environment: {overall["grms"]:.2f} Grms')
    print()
    print('  band [Hz]        slope [dB/oct]   energy [%]')
    for segment in overall['segments']:
        print(f'    {segment["lowerFrequency"]:6.0f} - {segment["upperFrequency"]:6.0f}   '
              f'{segment["slope"]:+8.2f}      {segment["energyFraction"] * 100.0:6.1f}')

    return {'spec': spec, 'statistics': statistics, 'overall': overall}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: the comparison that matters -- #
# ------------------------------------------------------------------------------------------------ #

def compareToGeneric(generic: dict, derived: dict) -> None:

    banner('3. DERIVED AGAINST GENERIC')

    derivedGrms = derived['overall']['grms']
    genericGrms = generic['grms']

    ratio    = derivedGrms / genericGrms
    decibels = ratioToDecibel(ratio ** 2, quantity = 'power')

    print(f'    generic   {genericGrms:6.2f} Grms')
    print(f'    derived   {derivedGrms:6.2f} Grms')
    print(f'    ratio     {ratio:6.2f}x   ({decibels:+.2f} dB)')
    print()

    if ratio > 1.05:
        print(f'  The derived environment is {decibels:+.1f} dB above the generic one, so this')
        print('  hardware has been qualified to less than it will actually see. That is the')
        print('  expensive discovery, and it is only findable by doing the derivation.')
    elif ratio < 0.95:
        print(f'  The derived environment is {decibels:.1f} dB below the generic one, so this')
        print('  hardware has been over-tested. That is not a safety problem and it is a real')
        print('  cost: heavier hardware, longer tests, and parts screened out for no reason.')
    else:
        print('  The two agree within 5 percent, which means the generic table was well chosen')
        print('  for this application. That is worth knowing and it was not knowable in advance.')

    print()
    print('  Either way the derived number carries something the generic one never can: a stated')
    print('  percentile, a stated confidence, and a sample it can be traced back to.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: the margin ladder -- #
# ------------------------------------------------------------------------------------------------ #

def marginLadder(derived: dict) -> None:

    banner('4. THE MARGIN LADDER, FLIGHT TO QUALIFICATION')

    spec   = derived['spec']
    levels = spec.deriveTestLevels()

    print('    step                        Grms     duration [s/axis]')
    print(f'    maximum predicted        {levels["acceptanceGrms"]:6.2f}          '
          f'{levels["acceptanceDuration"]:5.0f}')
    print(f'    acceptance               {levels["acceptanceGrms"]:6.2f}          '
          f'{levels["acceptanceDuration"]:5.0f}')
    print(f'    qualification            {levels["qualificationGrms"]:6.2f}          '
          f'{levels["qualificationDuration"]:5.0f}')
    print()
    for finding in levels['findings']:
        print(f'    - {finding}')

    print()
    print('  Compressing the qualification run:')
    print()
    print('    target [s]   offset [dB]   level [Grms]')
    for target in (60.0, 30.0, 10.0, 4.0):
        scaled = spec.scaleForDuration(target)
        print(f'      {target:6.0f}      {scaled["offsetDecibels"]:+8.2f}      '
              f'{scaled["scaledGrms"]:8.2f}')

    aggressive = spec.scaleForDuration(4.0)
    print()
    for finding in aggressive['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: zone dominates -- #
# ------------------------------------------------------------------------------------------------ #

def zoneSensitivity(derived: dict) -> None:

    banner('5. ZONE DEFINITION DOMINATES EVERYTHING ELSE')

    spec = derived['spec']

    print('    zone                   factor   offset [dB]   Grms')
    for zone in ('engine compartment', 'aft skirt', 'tank barrel',
                 'forward skirt', 'payload bay', 'isolated payload'):
        result = spec.applyZone(zone)
        print(f'    {zone:22s} {result["factor"]:5.1f}      '
              f'{result["offsetDecibels"]:+6.1f}     {result["grms"]:6.2f}')

    print()
    print('  The spread from engine compartment to isolated payload is 20x in density, which is')
    print('  13 dB. Every margin policy argument in this domain is worth 3 to 6 dB. Drawing the')
    print('  zone boundary in the wrong place costs more than every other decision combined,')
    print('  and it is done early, on a layout drawing, by someone who may not be thinking')
    print('  about vibration at all.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 6: independent cross-checks -- #
# ------------------------------------------------------------------------------------------------ #

def crossChecks(case: dict, derived: dict) -> None:

    banner('6. INDEPENDENT CROSS-CHECKS')

    # -- acoustic -- #

    acoustic = AcousticSpec()
    acoustic.setInputs({'referenceEnvironment': case['acoustic']['referenceEnvironment'],
                        'surfaceMass': case['acoustic']['respondingPanelSurfaceMass']})

    overall  = acoustic.calculateOverallLevel()
    response = acoustic.estimateVibrationResponse()

    print(f'  Acoustic: {overall["overallLevel"]:.1f} dB OASPL in the '
          f'{case["acoustic"]["referenceEnvironment"]}')
    print(f'    estimated panel response  {response["estimatedGrms"]:.1f} Grms')
    print(f'    derived vibration         {derived["overall"]["grms"]:.1f} Grms')
    print()

    ratio = response['estimatedGrms'] / derived['overall']['grms']
    if 0.3 < ratio < 3.0:
        print('    The acoustic estimate and the measured environment agree to within a factor')
        print('    of three, which is as well as a vibroacoustic correlation does. The zone is')
        print('    acoustically driven, so an acoustic change would move the vibration.')
    else:
        print(f'    These differ by {ratio:.1f}x. Either the zone is structure-borne rather than')
        print('    acoustically driven, or one of the two is wrong.')

    # -- shock -- #

    print()
    shock = ShockSpectrum()
    shock.setInputs({'source':    case['shock']['source'],
                     'distance':  case['shock']['distance'],
                     'jointPath': case['shock']['jointPath']})

    attenuation = shock.calculateAttenuation()
    levels      = shock.deriveTestLevels()

    print(f'  Shock: {case["shock"]["source"]} at {case["shock"]["distance"]:.2f} m behind '
          f'{len(case["shock"]["jointPath"])} joints')
    print(f'    source                    {shock.peakSrs:6.0f} g')
    print(f'    total attenuation         {attenuation["totalAttenuation"]:+6.1f} dB')
    print(f'    at the component          {levels["maximumPredictedPeak"]:6.0f} g')
    print(f'    qualification (+6 dB)     {levels["qualificationPeak"]:6.0f} g')

    # -- thermal -- #

    print()
    thermal = ThermalEnvironment()
    thermal.setInputs({'surfaceFinish':       case['thermal']['surfaceFinish'],
                       'altitude':            case['thermal']['altitude'],
                       'radiatingArea':       case['thermal']['radiatingArea'],
                       'internalDissipation': case['thermal']['internalDissipation'],
                       'missionYears':        case['thermal']['missionYears']})

    cases  = thermal.calculateOnOrbitCases()
    cycles = thermal.calculateThermalCycles()

    print(f'  Thermal: {case["thermal"]["surfaceFinish"]} at '
          f'{case["thermal"]["altitude"] / 1000.0:.0f} km')
    print(f'    hot case                  {cases["hotTemperature"] - 273.15:+6.1f} degC')
    print(f'    cold case                 {cases["coldTemperature"] - 273.15:+6.1f} degC')
    print(f'    swing                     {cases["swing"]:6.1f} K')
    print(f'    cycles in one year        {cycles["cycles"]:6.0f}')
    print()
    print(f'    The fluidSystems test campaign assumes '
          f'{case["inherited"]["flightThermalCycles"]} thermal cycles for this hardware. On orbit '
          f'it sees')
    print(f'    {cycles["cycles"]:.0f}. Those are different questions: the campaign number is the '
          f'ascent')
    print('    profile, this one is the orbital life, and hardware that flies needs both.')

# ------------------------------------------------------------------------------------------------ #
# -- Stage 7: what the structures domain consumes -- #
# ------------------------------------------------------------------------------------------------ #

def loadFactors(case: dict) -> None:

    banner('7. THE LOAD FACTORS aerospaceStructures CONSUMES')

    factors = LoadFactorSet()
    factors.setInputs({'mass': case['inherited']['componentMass'],
                       'description': 'feed system component'})
    factors.addStandardEvents()

    result = factors.identifyGoverning()

    print('    event              axial [g]  lateral [g]  combined [g]  dynamic [%]')
    for name, event in factors.events.items():
        combined = result['combined'][name]
        marker = '  <- GOVERNS' if name == result['governingByCombined'] else ''
        print(f'    {name:18s} {event["axial"]:7.2f}    {event["lateral"]:8.2f}     '
              f'{combined["combined"]:8.2f}      {combined["dynamicShare"] * 100.0:5.0f}{marker}')

    print()
    for finding in result['findings']:
        print(f'    - {finding}')

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(generic: dict, derived: dict) -> None:

    banner('SUMMARY: WHAT THE DERIVATION BOUGHT')

    derivedGrms = derived['overall']['grms']
    genericGrms = generic['grms']
    decibels    = ratioToDecibel((derivedGrms / genericGrms) ** 2, quantity = 'power')

    statistics = derived['statistics']

    print()
    print(f'    generic specification    {genericGrms:6.2f} Grms   no basis, no traceability')
    print(f'    derived specification    {derivedGrms:6.2f} Grms   '
          f'{statistics["basis"]} from {statistics["sampleCount"]} flights')
    print(f'    difference               {decibels:+6.2f} dB')
    print()
    print('  The generic number is not wrong. It is unaccountable. It cannot be defended when a')
    print('  test level looks expensive, it cannot be relaxed when it looks conservative, and it')
    print('  cannot be updated when more flights fly, because there is nothing to update.')
    print()
    print('  The derived number can be argued with, which is the whole point. Every element of it')
    print('  is visible: the sample, the percentile, the confidence, the zone, the shape, and')
    print('  each decibel of margin with the reason it was added.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    generic = reportGeneric(case)
    derived = deriveEnvironment(case)

    compareToGeneric(generic, derived)
    marginLadder(derived)
    zoneSensitivity(derived)
    crossChecks(case, derived)
    loadFactors(case)
    summarise(generic, derived)

if __name__ == '__main__':
    main()
