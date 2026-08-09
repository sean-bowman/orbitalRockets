
# -- propulsionTesting worked example -- #

'''

What a hot fire can establish, and what it cannot, on the hub's 100 kN booster.

The measured channels reduce to a c* efficiency of 0.96, which is what the propulsion hub assumed.
The question this example asks is not what the number is but whether the test could have told the
difference had it been something else, and the answer separates into two.

    Validating the design, a four per cent effect, is resolvable at a ratio of 2.7, which is
    below the working floor of three and close enough to the edge to be argued about.
    Ranking two injectors a point apart is not resolvable at all, and the class refuses it.

Most development campaigns want the second and are funded on the strength of the first.

The example also contains one arithmetic trap worth more than the rest of it. Specific impulse
computed as c* times Cf and given the two uncertainties combined in root sum of squares comes out
1.6 times too uncertain, because chamber pressure and throat area appear in both and cancel. A
generic uncertainty budget cannot see that, and this repository owns one that would get it wrong.

Run:
    python propulsion/propulsionTesting/codeInterface.py

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
ROOT = os.path.dirname(os.path.dirname(HERE))

sys.path.insert(0, os.path.join(HERE, 'propulsionTestingLibrary'))

from propulsionTestUtils import (INSTRUMENT_UNCERTAINTY, INSTABILITY_FLUX_MULTIPLIER,
                                 rootSumSquare, TestDesignError)
from PerformanceReduction import PerformanceReduction
from HotFireTest import HotFireTest, DISCRIMINATION_RATIO_FLOOR

ASSET = os.path.join(HERE, 'propulsionTestingLibrary', 'assets', 'hotFireCampaignExample.json')

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

def buildReduction(case: dict, uncertainties: dict = None) -> PerformanceReduction:

    measured = case['measured']

    inputs = {'chamberPressure': measured['chamberPressure'],
              'throatArea':      np.pi / 4.0 * measured['throatDiameter'] ** 2,
              'massFlow':        measured['massFlow'],
              'thrust':          measured['thrust']}

    if uncertainties is not None:
        inputs['uncertainties'] = dict(uncertainties)

    reduction = PerformanceReduction()
    reduction.setInputs(inputs)

    return reduction

def buildTest(case: dict) -> HotFireTest:

    test = case['test']

    hotFire = HotFireTest()
    hotFire.setInputs({'objective':       test['objective'],
                       'chamberPressure': case['measured']['chamberPressure'],
                       'chamberDiameter': test['chamberDiameter'],
                       'residenceTime':   test['residenceTime'],
                       'duration':        test['duration'],
                       'sampleRate':      test['sampleRate']})

    return hotFire

# ------------------------------------------------------------------------------------------------ #
# -- Stage 1: the reduction -- #
# ------------------------------------------------------------------------------------------------ #

def reportReduction(case: dict) -> dict:

    banner('1. THE REDUCTION, AND WHAT IT IS WORTH')

    reduction = buildReduction(case)

    reduced     = reduction.reduce()
    uncertainty = reduction.calculateUncertainty()

    print(f'    {"parameter":26s} {"value":>10s} {"uncertainty":>13s}')
    print(f'    {"characteristic velocity":26s} '
          f'{reduced["characteristicVelocity"]:10.1f} '
          f'{uncertainty["characteristicVelocity"]:13.2%}')
    print(f'    {"thrust coefficient":26s} {reduced["thrustCoefficient"]:10.4f} '
          f'{uncertainty["thrustCoefficient"]:13.2%}')
    print(f'    {"specific impulse":26s} {reduced["specificImpulse"]:10.2f} '
          f'{uncertainty["specificImpulse"]:13.2%}')

    print()
    print('  Three numbers from four channels, and the algebra is the easy part.')
    print()
    print(f'    {"channel":20s} {"relative":>10s} {"share of c* variance":>22s}')
    for name, share in uncertainty['cstarShares'].items():
        print(f'    {name:20s} {uncertainty["contributors"][name]:10.2%} {share:22.0%}')

    print()
    print('  No single channel dominates, which is the case where a budget is worth building')
    print('  rather than guessing. The throat area and the mass flow carry equal weight and')
    print('  improving either one alone leaves the other in place.')
    print()
    print('  The throat area deserves a second look, because it is the only entry in that list')
    print('  that nobody calls a measurement. It comes from a cold diameter checked once, doubled')
    print('  because area goes as diameter squared, and it does not include the throat eroding')
    print('  during the firing, which is not measured at all.')

    return {'reduction': reduction, 'reduced': reduced, 'uncertainty': uncertainty}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 2: the trap -- #
# ------------------------------------------------------------------------------------------------ #

def reportCorrelation(case: dict) -> dict:

    banner('2. THE ARITHMETIC TRAP, WHICH IS WORTH MORE THAN THE REST OF THIS EXAMPLE')

    reduction = buildReduction(case)

    reduced     = reduction.reduce()
    uncertainty = reduction.calculateUncertainty()

    print('  c*  = Pc At / mdot')
    print('  Cf  = F / (Pc At)')
    print()
    print('  Chamber pressure and throat area appear in both, inverted, so the two results are')
    print('  anti-correlated. Their product is exactly F / mdot: the shared terms cancel.')
    print()
    print(f'    {"route to specific impulse":34s} {"value [s]":>11s} {"uncertainty":>13s}')
    print(f'    {"F / (mdot g), direct":34s} {reduced["specificImpulse"]:11.2f} '
          f'{uncertainty["specificImpulse"]:13.2%}')
    naiveLabel = 'c* Cf / g, uncertainties combined'

    print(f'    {naiveLabel:34s} {reduced["productCheck"]:11.2f} '
          f'{uncertainty["naiveSpecificImpulse"]:13.2%}')

    print()
    print(f'  **Same number, {uncertainty["inflationFactor"]:.2f} times the uncertainty.** The '
          f'values agree to the last digit')
    print('  because they are algebraically identical. The uncertainties do not, because the')
    print('  second route counts the chamber pressure and the throat area twice each.')
    print()
    print('  This is not a subtle case. It is the default thing to do when the reduction produces')
    print('  c* and Cf and somebody wants an Isp, and a generic uncertainty budget will do it')
    print('  wrong every time, because its interface takes independent contributors and these are')
    print('  not independent.')
    print()
    print('  This repository owns such a budget class, in fluidSystemsTesting. It is a good class')
    print('  and it would get this wrong, which is why the reduction lives here instead of being')
    print('  assembled from it.')

    return uncertainty

# ------------------------------------------------------------------------------------------------ #
# -- Stage 3: what the test can establish -- #
# ------------------------------------------------------------------------------------------------ #

def reportDiscrimination(case: dict) -> dict:

    banner('3. WHAT THIS TEST CAN ESTABLISH, AND WHAT IT CANNOT')

    reduction = buildReduction(case)

    comparison = reduction.compareEfficiency(case['ideal']['characteristicVelocity'],
                                             case['ideal']['thrustCoefficient'])

    uncertainty = reduction.calculateUncertainty()

    print(f'  c* efficiency {comparison["cstarEfficiency"]:.4f}, against the hub\'s assumed 0.96.')
    print(f'  The shortfall from ideal is {comparison["cstarShortfall"]:.2%} and the measurement '
          f'carries {uncertainty["characteristicVelocity"]:.2%}.')
    print()

    hotFire = buildTest(case)

    results = {}

    print(f'    {"acceptance criterion":34s} {"band":>7s} {"ratio":>7s}   verdict')

    for name, band in ((key, value) for key, value in case['acceptance'].items()
                       if not key.startswith('_')):

        label = {'validation': 'validate the design, 4 per cent',
                 'ranking':    'rank two injectors, 1 per cent'}.get(name, name)

        try:
            check = hotFire.checkDiscrimination(
                band, uncertainty = uncertainty['characteristicVelocity'])

            results[name] = check

            verdict = ('decides comfortably' if check['comfortable']
                       else 'decides, and it will be argued about')

            print(f'    {label:34s} {band:7.1%} {check["ratio"]:7.1f}   {verdict}')

        except TestDesignError as error:
            results[name] = None
            print(f'    {label:34s} {band:7.1%} {"":>7s}   REFUSED')
            detail = [line for line in str(error).splitlines()
                      if line.startswith('The acceptance band')]
            print(f'      {detail[0][:90]}')

    print()
    print('  That split is the result. **A four per cent effect is resolvable, if only just, and a')
    print('  one per cent effect is not resolvable at all.** The test can confirm that the')
    print('  injector performs roughly as designed. It cannot tell whether a modification took the')
    print('  efficiency from 0.96 to 0.97, and at a ratio below three even the four per cent')
    print('  verdict is close enough to the edge to be argued about.')
    print()
    print('  Most development campaigns want the second and are funded on the strength of the')
    print('  first, and the gap between those two sentences is where a lot of test money goes.')

    return {'comparison': comparison, 'results': results}

# ------------------------------------------------------------------------------------------------ #
# -- Stage 4: what it would take -- #
# ------------------------------------------------------------------------------------------------ #

def reportImprovement(case: dict) -> dict:

    banner('4. WHAT IT WOULD TAKE TO RANK TWO INJECTORS')

    baseline = buildReduction(case).calculateUncertainty()

    improvement = {key: value for key, value in case['improvement'].items()
                   if not key.startswith('_')}

    print(f'    {"instrumentation":34s} {"u(c*)":>8s} {"ratio at 1 per cent":>20s}')

    print(f'    {"as tested":34s} {baseline["characteristicVelocity"]:8.2%} '
          f'{0.01 / baseline["characteristicVelocity"]:20.1f}')

    results = {'as tested': baseline['characteristicVelocity']}

    for channel, value in improvement.items():

        trial = buildReduction(case, {channel: value}).calculateUncertainty()

        results[channel] = trial['characteristicVelocity']

        print(f'    {"improve " + channel:34s} {trial["characteristicVelocity"]:8.2%} '
              f'{0.01 / trial["characteristicVelocity"]:20.1f}')

    both = buildReduction(case, improvement).calculateUncertainty()

    results['both'] = both['characteristicVelocity']

    print(f'    {"improve both":34s} {both["characteristicVelocity"]:8.2%} '
          f'{0.01 / both["characteristicVelocity"]:20.1f}')

    print()
    print('  Improving one channel barely moves the answer, because the other is still there and')
    print('  they were carrying equal weight. Improving both moves it a long way.')
    print()
    print(f'  Even then the ratio at a one per cent band is '
          f'{0.01 / both["characteristicVelocity"]:.1f}, against a working floor of '
          f'{DISCRIMINATION_RATIO_FLOOR:.0f}.')
    print('  **Ranking two injectors a point apart needs a better test than instrumentation alone')
    print('  will buy.** The usual answer is not a better measurement but a different comparison:')
    print('  fire both injectors on the same hardware, back to back, on the same day, and compare')
    print('  them to each other rather than each to an absolute. The shared errors cancel, which')
    print('  is the same cancellation stage 2 was about, used deliberately this time.')

    return results

# ------------------------------------------------------------------------------------------------ #
# -- Stage 5: the other two objectives -- #
# ------------------------------------------------------------------------------------------------ #

def reportInstrumentation(case: dict) -> dict:

    banner('5. THE SAME FIRING, ASKED TO ANSWER TWO OTHER QUESTIONS')

    hotFire = buildTest(case)

    sampling = hotFire.checkSampleRate()
    duration = hotFire.checkDuration()

    print(f'    {"quantity":30s} {"value":>12s}')
    print(f'    {"first tangential mode":30s} {sampling["frequency"] / 1000.0:9.2f} kHz')
    print(f'    {"rate to detect it":30s} {sampling["nyquistRate"] / 1000.0:9.1f} kHz')
    print(f'    {"rate to resolve it":30s} {sampling["resolutionRate"] / 1000.0:9.0f} kHz')
    print(f'    {"rate as tested":30s} {sampling["sampleRate"] / 1000.0:9.1f} kHz')

    print()
    print('  A performance data system rate, asked to support a stability objective, and it is')
    print('  below Nyquist for the mode that matters.')
    print()
    print('  That is worse than not measuring. Below Nyquist the mode does not vanish, it aliases')
    print('  down into the performance band and appears as a low frequency oscillation that is not')
    print('  there. A test set up this way can produce a chug investigation into a 1T mode.')

    print()
    print(f'    {"chamber settles in":30s} {duration["chamberSettling"] * 1000.0:9.0f} ms')
    print(f'    {"wall settles in":30s} {duration["wallSettling"]:9.1f} s')
    print(f'    {"burn duration":30s} {duration["duration"]:9.1f} s')
    print(f'    {"usable thermal window":30s} {duration["usableThermalWindow"]:9.1f} s')

    print()
    print('  Three orders of magnitude between the two settling times. A two second burn would')
    print('  give a valid performance number and an invalid wall temperature, and the wall')
    print('  temperature is usually what the short test was run to get.')

    stability = hotFire.checkStabilityRating(
        case['stability']['pulseFraction'] * case['measured']['chamberPressure'])

    print()
    for finding in stability['findings']:
        print(f'  - {finding}')

    return {'sampling': sampling, 'duration': duration, 'stability': stability}

# ------------------------------------------------------------------------------------------------ #
# -- Summary -- #
# ------------------------------------------------------------------------------------------------ #

def summarise(stage1: dict, stage3: dict, stage4: dict, stage5: dict) -> None:

    banner('SUMMARY: WHAT THIS FIRING ESTABLISHED')

    uncertainty = stage1['uncertainty']

    print()
    print(f'    {"question":50s} answer')
    print(f'    {"does the injector perform roughly as designed":50s} yes, and only just')
    print(f'    {"is this injector a point better than that one":50s} '
          f'no, and no instrument fixes it')
    print(f'    {"what is the specific impulse":50s} '
          f'{stage1["reduced"]["specificImpulse"]:.1f} s, '
          f'plus or minus {uncertainty["specificImpulse"]:.1%}')
    print(f'    {"is the engine dynamically stable":50s} '
          f'not from this data system')
    print(f'    {"what is the steady wall temperature":50s} '
          f'yes, after {stage5["duration"]["wallSettling"]:.0f} s of the burn')

    print()
    print('  Three of those five are limited by decisions made before the firing: the throat')
    print('  measurement, the sample rate, and the burn duration. None is limited by the engine.')
    print()
    print(f'  And the trap: specific impulse from c* times Cf, with the two uncertainties combined')
    print(f'  as independent, comes out {uncertainty["inflationFactor"]:.2f} times too uncertain. '
          f'The same cancellation, used')
    print('  deliberately, is what makes a back-to-back comparison worth more than a better')
    print('  instrument.')
    print()
    print('  What this sub-domain cannot do is tell you what a firing sounded like, what the')
    print('  hardware looked like afterwards, or which channel to distrust on the day. That is')
    print('  the tacit half of test engineering and it is not written down here.')
    print()
    print('=' * 96)

# ------------------------------------------------------------------------------------------------ #

def main() -> None:

    case = loadCase()

    stage1 = reportReduction(case)

    reportCorrelation(case)

    stage3 = reportDiscrimination(case)
    stage4 = reportImprovement(case)
    stage5 = reportInstrumentation(case)

    summarise(stage1, stage3, stage4, stage5)

if __name__ == '__main__':
    main()
