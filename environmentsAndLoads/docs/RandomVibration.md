[Home](../README.md) > Random Vibration

# Random Vibration

## Contents

- [Overview](#overview)
- [PSD and Grms](#psd-and-grms)
- [Why Grms is not a specification](#why-grms-is-not-a-specification)
- [Reading a breakpoint table](#reading-a-breakpoint-table)
- [Where the energy comes from](#where-the-energy-comes-from)
- [Duration scaling](#duration-scaling)
- [Test levels](#test-levels)
- [Notching and force limiting](#notching-and-force-limiting)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Random vibration is the environment most hardware is qualified against and the one whose specification is most often taken as given. It is defined by a power spectral density, summarised by a single number that hides most of what matters, and scaled in time by an assumption almost nobody states.

---

## PSD and Grms

**The acceleration spectral density has units of g^2/Hz**, which is a mean square per unit bandwidth. Integrating it over frequency gives a mean square acceleration, and its square root is Grms:

```
Grms = sqrt( integral of W(f) df )
```

**A breakpoint table is straight lines on a log-log plot**, so within a segment the density follows a power law and the integral has a closed form:

```
W(f) = W1 (f / f1)^n,    n = ln(W2/W1) / ln(f2/f1)
```

**The exponent `n = -1` case is singular** and degenerates to a logarithm. That corresponds to a slope of exactly -3.01 dB per octave, which is not a contrived value: it is the slope of many real specifications, so the singular branch is exercised in practice rather than being a theoretical nicety.

---

## Why Grms is not a specification

**Two spectra with identical Grms damage hardware completely differently**, because the damage depends on where the energy sits relative to the hardware's resonances.

**A component with its first mode at 200 Hz cares enormously about energy at 200 Hz and very little about energy at 1500 Hz.** Both spectra can have the same area.

**Grms is useful for three things**: comparing like shapes, sizing a shaker, and sanity-checking a derivation. It is not useful for deciding whether hardware survives, and a specification that quotes only Grms has not specified the environment.

**The energy distribution is the useful output.** For the GEVS spectrum, 60 percent of the energy is between 50 and 800 Hz and only 1.3 percent is below 50 Hz. Hardware with no resonance in the dominant band sees far less than the Grms suggests.

---

## Reading a breakpoint table

| Slope | Meaning |
|---|---|
| **0 dB/oct** | Flat. Constant energy per unit bandwidth |
| **+3 dB/oct** | Constant energy per octave below |
| **+6 dB/oct** | The common low frequency roll-on |
| **-3.01 dB/oct** | The singular case for integration |
| **-6 dB/oct** | The common high frequency roll-off |

**Slope in dB per octave is `10 log10(W2/W1) / log2(f2/f1)`**, and it is how every specification is written because it makes the plot straight.

**GEVS is +6, flat, -6**, which is the archetype: roll on from 20 Hz, a broad flat plateau where the acoustic energy is, and roll off above 800 Hz.

---

## Where the energy comes from

| Source | Character |
|---|---|
| **Acoustic** | The dominant source for most zones. Liftoff and transonic |
| **Engine** | Structure-borne from the thrust structure. Narrowband components |
| **Aerodynamic** | Boundary layer and separated flow. Transonic |
| Machinery | Pumps and turbines, narrowband |

**Most random vibration is acoustically induced**, which is why an acoustic estimate is a useful independent check on a measured environment. If the two agree within a factor of three, the zone is acoustically driven and an acoustic change will move the vibration. If they do not, the path is structure-borne and it will not.

**Zone dominates the level.** Engine compartment to isolated payload is a factor of 20 in density, which is 13 dB. See [EnvironmentDerivation.md](EnvironmentDerivation.md).

---

## Duration scaling

**Miner's rule converts between test duration and level, and it is the most heavily leaned-on assumption in environmental testing.**

```
W2 / W1 = (T1 / T2)^(1/b)
```

with `b = 4` the conventional fatigue exponent for aluminium.

| Compression | Offset |
|---|---|
| 2x | +0.75 dB |
| 4x | +1.51 dB |
| **10x** | **+2.51 dB** |
| 15x | +2.94 dB |

**It presumes three things and states none of them**: that the damage mechanism is high cycle fatigue with a single S-N exponent, that damage accumulates linearly, and that the failure mode does not change with level.

**The third is where it breaks.** A test compressed by a large factor is run at a level high enough to excite a failure mode flight never would: a part rattles into a stop, a connector unseats, a bracket yields. The test then fails for a reason that has nothing to do with the mission.

**The exponent is an assumption, not a measurement.** Using `b = 6` instead of `b = 4` changes a 10x compression from +2.51 dB to +1.67 dB, and both are defensible in the literature.

---

## Test levels

| Level | Value | Purpose |
|---|---|---|
| **Acceptance** | = MPE, 60 s/axis | **Screens workmanship** |
| **Qualification** | MPE + 3 dB, 120 s/axis | **Demonstrates design margin** |
| Protoflight | MPE + 3 dB, 60 s/axis | A compromise, on flight hardware |

**Protoflight is the pragmatic middle**: qualification level for acceptance duration, run on the article that flies. It saves a dedicated qualification unit and it consumes some of the flight article's life, which is the trade.

**+3 dB is a factor of two in density and only 1.41 in Grms.** A decibel margin on a power quantity is a square root in the amplitude everyone quotes, and confusing the two is a factor-of-two error in either direction.

---

## Notching and force limiting

**Notching reduces the input at frequencies where the shaker drives the article harder than flight would.**

**The physical basis is impedance.** In flight, an article is mounted on a finite-impedance structure that unloads at the article's resonances. On a shaker it is mounted on a very high impedance fixture that does not, so the article sees a much larger input right where it responds most.

| Method | Basis |
|---|---|
| **Force limiting** | Measure the interface force, limit it to the flight prediction |
| **Response limiting** | Limit a measured response to the flight prediction |
| Manual notching | Reduce the input at named frequencies. Needs justification |

**Force limiting is the defensible form** because it is measured rather than assumed, and NASA-HDBK-7004 covers it. Unjustified notching is the difference between testing hardware and negotiating with a specification.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `Grms = sqrt(area under the PSD)` | |
| Grms is a summary, not a specification | The shape decides the damage |
| Slope in dB/oct is `10 log10(W2/W1) / log2(f2/f1)` | |
| -3.01 dB/oct is the singular integration case | And it is a real slope |
| Most vibration is acoustically induced | Cross-check against an acoustic estimate |
| Miner exponent `b = 4` | An assumption, not a measurement |
| +3 dB is 2x in density, 1.41x in Grms | |
| Force limiting is the defensible notch | Measured, not assumed |

---

## Failure modes

**Grms matched between differently shaped spectra.** They damage differently.

**A specification quoting only Grms.** The environment is not specified.

**dB applied as an amplitude quantity to a PSD.** A factor of two.

**Large duration compression without a failure mode argument.** The test excites something flight would not.

**The Miner exponent left unstated.** The scaling is sensitive to it.

**Notching without force or response limiting.** Unsupported relief.

**Zone assumed homogeneous with 8 dB of scatter.** It is two zones.

---

## Worked numbers

From [`RandomVibrationSpec`](../environmentsAndLoadsLibrary/RandomVibrationSpec.py) on the GEVS qualification spectrum:

| Band | Slope | Energy |
|---|---|---|
| 20 to 50 Hz | +5.97 dB/oct | 1.3 % |
| **50 to 800 Hz** | 0.00 dB/oct | **60.1 %** |
| 800 to 2000 Hz | -5.97 dB/oct | 38.7 % |

**Grms 14.14 against the published 14.1**, which validates the whole log-log integration chain against an external number.

| Zone | Grms |
|---|---|
| Engine compartment | 28.27 |
| Tank barrel | 14.14 |
| **Isolated payload** | **6.32** |

---

## Standards

| Standard | Scope |
|---|---|
| **GSFC-STD-7000** | GEVS, the reference general specification |
| **NASA-HDBK-7005** | Dynamic environmental criteria |
| **NASA-HDBK-7004** | Force limited vibration testing |
| MIL-STD-1540 | Test requirements and margin policy |
| MIL-STD-810 Method 514 | Vibration test methods |
| ECSS-E-ST-10-03 | Testing |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from RandomVibrationSpec import RandomVibrationSpec

spec = RandomVibrationSpec()
spec.setInputs({'referenceSpectrum': 'GEVS qualification'})

overall = spec.calculateOverallLevel()
print(f'{overall["grms"]:.2f} Grms')
for segment in overall['segments']:
    print(f'  {segment["lowerFrequency"]:6.0f} - {segment["upperFrequency"]:6.0f} Hz  '
          f'{segment["slope"]:+6.2f} dB/oct  {segment["energyFraction"] * 100.0:5.1f} %')

for target in (60.0, 10.0, 4.0):
    scaled = spec.scaleForDuration(target)
    print(f'{target:5.0f} s  {scaled["offsetDecibels"]:+.2f} dB  {scaled["scaledGrms"]:.2f} Grms')
```

---

## References

1. GSFC-STD-7000B, *General Environmental Verification Standard*.
2. NASA-HDBK-7005, *Dynamic Environmental Criteria*, 2001.
3. Scharton, T. D., *Force Limited Vibration Testing Monograph*, NASA RP-1403, 1997.
