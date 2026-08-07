[Home](../README.md) > Environmental Testing

# Environmental Testing

## Contents

- [Overview](#overview)
- [Random vibration](#random-vibration)
- [Miner's rule and duration scaling](#miners-rule-and-duration-scaling)
- [Acoustic testing](#acoustic-testing)
- [Shock](#shock)
- [Thermal cycling and thermal vacuum](#thermal-cycling-and-thermal-vacuum)
- [Fixturing and control](#fixturing-and-control)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Environmental testing is where fluid system hardware actually fails, and it fails at the fittings and the supports rather than in the middle of a component. The purpose is to demonstrate the design survives the flight environment with margin, and to catch the workmanship escapes that no inspection finds.

Every level applied should be traceable to a flight environment through a stated margin policy. A test level nobody can trace is a test level nobody can defend when it turns out to be expensive.

---

## Random vibration

**The specification is a PSD**, given as breakpoints on a log-log plot in g^2/Hz against Hz.

**Grms is the square root of the area under it**, integrated segment by segment treating each segment as a straight line on log-log axes:

```
m    = ln(S2/S1) / ln(f2/f1)
area = (f2*S2 - f1*S1) / (m + 1)      for m != -1
area = S1 * f1 * ln(f2/f1)            for m == -1
```

**Treating the breakpoints as linear on linear axes is the obvious mistake** and it overestimates the area under a rolloff. The [`EnvironmentalTest`](../fluidSystemsTestingLibrary/EnvironmentalTest.py) class does it properly, including the degenerate slope = -1 case which integrates to a logarithm.

**Levels:**

| Level | PSD | Duration |
|---|---|---|
| Acceptance | Flight | 60 s per axis |
| **Qualification** | **Flight +3 dB** | **120 s per axis** |

+3 dB is a factor of two in PSD and therefore sqrt(2) in Grms.

**Three axes**, each tested separately. The article is tested in the flight mounting configuration, because mounting stiffness changes the response and a component qualified on a rigid fixture has not been qualified as installed.

---

## Miner's rule and duration scaling

The relationship that makes level and duration interchangeable.

Under Miner's rule with fatigue exponent `m`, equal damage requires `S1^m * t1 = S2^m * t2`. Stress amplitude scales as the square root of PSD, so

```
(PSD2 / PSD1) = (t1 / t2)^(2/m)
```

With the standard `m = 4`, this is a square-root relationship: **halving the duration needs a factor of sqrt(2) in PSD, which is 1.5 dB.**

**This is why +3 dB and 2x duration are not the same margin counted twice.** A factor of two in PSD raises stress by sqrt(2), and sqrt(2)^4 = 4, so the 3 dB alone is equivalent to 4x the exposure time. The 2x duration is additional margin on top.

**Compressing a test has a limit.** Raising the level to fit the schedule eventually excites failure modes the article would never see in flight: a resonance that only responds at high amplitude, a nonlinearity, a joint that slips. **The conventional limit is about 6 dB**, and the class flags anything beyond it as not defensible.

| Compression | Level increase needed | Defensible |
|---|---|---|
| 120 s -> 60 s | +1.5 dB | Yes |
| 120 s -> 30 s | +3.0 dB | Yes |
| 120 s -> 12 s | +5.0 dB | Marginal |
| 120 s -> 2 s | +8.9 dB | **No** |

**The exponent is the assumption everything rests on.** Four is standard and it comes from a typical S-N slope; a material with a different slope needs a different number, and if the exponent is wrong every scaled level is wrong with it.

---

## Acoustic testing

For large, lightweight structures the acoustic environment couples in better through the surface than through the mounting points, and a shaker cannot reproduce it. A reverberant chamber or a direct field acoustic test applies the environment as sound pressure.

**Relevant when** the article has a high area-to-mass ratio: panels, fairings, blankets, large ducts. **Not relevant** for a compact valve, where shaker testing at the mount is representative.

Levels are specified as octave-band SPL, with qualification at +3 dB over acceptance.

---

## Shock

**Specified as a shock response spectrum**, the peak response of a set of single-degree-of-freedom oscillators to the transient.

| Level | Value |
|---|---|
| Qualification | 1.4x flight SRS |
| Applications | 3 per axis |

**There is no duration concept and no Miner scaling.** Shock is a single transient and the damage model is peak response rather than accumulated cycles. The three applications cover shock machine variability, not damage accumulation, which is why the count does not scale with anything.

**Test methods** in rough order of fidelity: actual pyrotechnic device on a representative structure, resonant plate, shaker-generated transient. The last is convenient and reproduces the SRS but not the wave content, which matters for high-frequency response.

---

## Thermal cycling and thermal vacuum

| Level | Range | Cycles |
|---|---|---|
| Acceptance | Flight range | 4 |
| **Qualification** | **Flight range +/- 10 K** | **8** |

**Margin is applied in both temperature and cycles** because the mechanisms differ: temperature extremes find material limits and tolerance stack-ups, cycles find fatigue and differential contraction.

**Dwell at each extreme** long enough for the article to reach thermal equilibrium, verified by instrumentation rather than assumed from a time constant.

**Thermal vacuum** adds the vacuum environment: outgassing, the loss of convective heat transfer, and any function that depends on ambient pressure. It is a qualification-level test.

**Leak test at temperature, not only after return to ambient.** Differential contraction is the failure mechanism for a cryogenic seal and it does not exist at room temperature.

---

## Fixturing and control

**The fixture is part of the test.** A fixture with a resonance in the test band puts energy where the specification did not intend it, and a fixture that is too compliant under-tests. Fixture design targets a first mode well above the test band, typically above 2 kHz for a component.

**Control accelerometer placement** determines what is actually being controlled. Single-point control at a stiff location can under-test the article; multi-point averaging is more representative and is standard for anything non-trivial.

**Notching** reduces the input at a resonance to avoid over-testing beyond the flight response. It is legitimate when the flight response is known and the notch is justified by a force limit or a measured flight level. It is not legitimate as a way to make an article survive.

**Instrument response, not just input.** Response accelerometers on the article are what tell you whether the article saw what the specification intended.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Grms integration | Log-log segment-wise, not linear |
| Qualification random | +3 dB, 2x duration, per axis |
| Miner exponent | 4, standard |
| Level-duration trade | `(PSD ratio) = (time ratio)^(2/m)` |
| Compression limit | ~6 dB |
| Shock qualification | 1.4x flight SRS, 3 per axis |
| Thermal qualification | Flight range +/- 10 K, 2x cycles |
| Fixture first mode | Well above the test band |
| Test in the flight mounting configuration | Mounting stiffness changes the response |
| Leak test after each exposure | Identifies which one caused a failure |
| Instrument article response | Not just the control input |

---

## Failure modes

**Fixture resonance in the test band.** The article is tested at a level nobody specified.

**Single-point control under-testing.** The control point is stiff and the article sees less than intended.

**Notching used to pass rather than to avoid over-test.** The article survives a test it should have failed.

**Test level compressed too far.** A failure mode is excited that flight would never produce.

**Component qualified alone, failed in the assembly.** Different mounting stiffness.

**Leak test only at the end of the environmental sequence.** The article failed and nobody knows which exposure did it.

**Thermal dwell too short.** The article never reached the extreme it was supposed to be tested at.

**Ambient leak test on cryogenic hardware.** The mechanism is not exercised.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), a launch vehicle component environment:

| Quantity | Value |
|---|---|
| Flight PSD | 0.01 g^2/Hz at 20 Hz, 0.08 from 80 to 500 Hz, 0.005 at 2000 Hz |
| **Acceptance** | **8.13 Grms, 60 s per axis** |
| **Qualification** | **11.48 Grms, 120 s per axis** |
| Grms ratio | sqrt(2), as +3 dB requires |
| Shock, qualification | 2100 g peak SRS, 3 per axis |
| Thermal, flight | 253.2 to 333.1 K, 4 cycles |
| **Thermal, qualification** | **243.2 to 343.1 K, 8 cycles** |
| Compressing 120 s to 30 s | +3.0 dB, defensible |
| Compressing 120 s to 2 s | +8.9 dB, **not defensible** |

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-1540** | Test requirements for launch, upper stage and space vehicles |
| **MIL-STD-810** | Environmental engineering considerations and laboratory tests |
| NASA-STD-7001 | Payload vibroacoustic test criteria |
| NASA-STD-7002 | Payload test requirements |
| NASA-HDBK-7005 | Dynamic environmental criteria |
| ECSS-E-ST-10-03 | Space engineering: testing |
| IEST-RP-DTE012 | Handbook for dynamic data acquisition and analysis |

---

## Tool interface

```python
from EnvironmentalTest import EnvironmentalTest

test = EnvironmentalTest()
test.setInputs({'flightPowerSpectralDensity': [(20.0, 0.01), (80.0, 0.08),
                                               (500.0, 0.08), (2000.0, 0.005)],
                'flightDuration': 60.0,
                'shockEnvironmentKey': 'separation',
                'flightTemperatureRange': (253.15, 333.15), 'flightThermalCycles': 4})

test.calculateRandomVibration()      # Grms, qualification PSD, durations
test.calculateShock()                # qualification SRS
test.calculateThermal()              # range and cycles
test.scaleDurationToLevel(30.0)      # Miner: level needed to compress the test
test.scaleLevelToDuration(3.0)       # Miner: duration equivalent to a level
print(test.generateReport())
```

Lookup tables: `EnvironmentalTest.GENERIC_VIBRATION_ENVIRONMENTS`, `GENERIC_SHOCK_ENVIRONMENTS`.

---

## References

1. MIL-STD-1540E, *Test Requirements for Launch, Upper-Stage, and Space Vehicles*.
2. MIL-STD-810H, *Environmental Engineering Considerations and Laboratory Tests*.
3. NASA-STD-7001B, *Payload Vibroacoustic Test Criteria*.
4. Steinberg, D. S., *Vibration Analysis for Electronic Equipment*, 3rd ed., Wiley, 2000.
5. Miner, M. A., "Cumulative Damage in Fatigue", *Journal of Applied Mechanics*, Vol. 12, 1945.
