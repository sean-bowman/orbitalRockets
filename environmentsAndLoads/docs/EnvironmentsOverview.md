[Home](../README.md) > Environments Overview

# Environments Overview

## Contents

- [Overview](#overview)
- [The derivation chain](#the-derivation-chain)
- [The environments](#the-environments)
- [Where each one comes from](#where-each-one-comes-from)
- [What dominates the answer](#what-dominates-the-answer)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Every qualification level, every factor of safety and every design margin in this repository traces back to an environment definition. This domain is upstream of nearly everything else, and getting the environment wrong means every downstream qualification is answering the wrong question correctly.

The organising question is not what the environments are. It is where a given number came from, and whether it can be defended.

---

## The derivation chain

**Every environment specification climbs the same ladder, and each rung has a distinct reason.**

| Step | What it is | Who it protects |
|---|---|---|
| **Flight measurements** | Several flights, several channels, one zone | Nobody yet. This is evidence |
| **Statistical limit** | Mean plus k sigma, at a stated percentile and confidence | Against sampling |
| **Maximum predicted (MPE)** | What the hardware will actually see | The design |
| **Acceptance level** | = MPE. **Demonstrates no margin at all** | Against workmanship |
| **Qualification level** | MPE + 3 dB, for twice the duration | The design margin |

**Acceptance equals the MPE and therefore demonstrates nothing about margin.** It is a workmanship screen on flight hardware: it finds the unit that was built wrong. Qualification is a different question asked of a different article, and neither substitutes for the other.

**The 3 dB is not arbitrary.** It is a factor of two in power spectral density, which is roughly one standard deviation of the lot-to-lot and unit-to-unit variability seen in practice. Shock gets 6 dB because its scatter is larger.

**Two things are lost from that chain constantly.** The statistics are done on decibel values, because environments are log-normally distributed far more often than normally. And the percentile and confidence are part of the specification: P95/50 and P95/90 are different numbers, and quoting a level without its basis is quoting half a number.

---

## The environments

| Environment | Character | Damages |
|---|---|---|
| **Random vibration** | Broadband, minutes, statistical | Fatigue at mounts and leads |
| **Acoustic** | Broadband pressure field, seconds | Large light panels, and everything on them |
| **Shock** | Milliseconds, thousands of g | **Relays, crystals, solder, brittle parts** |
| **Sine and transient** | Low frequency, coupled | Primary structure |
| **Quasi-static** | Steady plus dynamic amplification | Primary structure |
| **Thermal** | Slow, deterministic, cyclic | Anything with an expansion mismatch |
| **Pressure** | Ascent profile, venting | Sealed compartments |
| Natural | Wind, humidity, salt fog, radiation | Everything, slowly |

**Shock is the odd one out.** It breaks small stiff things and leaves the structure it passed through unharmed, which is why a structural analysis of a shock event usually misses the point entirely.

---

## Where each one comes from

| Environment | Physical source |
|---|---|
| **Random vibration** | Mostly the **acoustic field**, plus engine and structure-borne paths |
| **Acoustic** | Engine exhaust at liftoff, aerodynamic at transonic |
| **Shock** | Pyrotechnic separation devices, and there are more of them than expected |
| **Transient** | Liftoff release, engine ignition and shutdown, staging, gust |
| **Quasi-static** | Trajectory acceleration plus the dynamic amplification of the transients |
| **Thermal** | Aeroheating on ascent, radiation balance on orbit |

**Most random vibration is acoustically induced**, which is why the two documents belong together and why an acoustic change moves the vibration environment. A zone whose vibration is structure-borne behaves differently and the two can be told apart by comparing a vibroacoustic estimate against the measurement.

---

## What dominates the answer

**Not the margin policy. Zone definition.**

| Decision | Worth |
|---|---|
| **Zone boundary** | **13 dB**, engine compartment to isolated payload |
| Statistical basis | 1 to 3 dB, P95/50 against P95/90 |
| Qualification margin | 3 dB random, 6 dB shock |
| Duration compression | 0 to 3 dB, depending on the factor |

**The zone is worth more than every other decision combined**, and it is settled early, on a layout drawing, frequently by someone not thinking about vibration at all. Arguing about a 3 dB margin policy while the zone boundary is unexamined is arguing about the wrong thing.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Acceptance = MPE, and demonstrates no margin | It screens workmanship |
| Qualification = MPE + 3 dB for 2x duration | 6 dB for shock |
| Do the statistics in decibels | Environments are log-normal |
| State the percentile and confidence | Or the level is half a number |
| Zone definition dominates | 13 dB against 3 dB for policy |
| Most vibration is acoustically induced | An acoustic change moves it |
| Shock breaks small stiff things | Not structure |
| Grms is a summary, not a specification | The shape decides the damage |

---

## Failure modes

**A generic environment used without labelling it as chosen rather than derived.**

**Statistics taken on linear values.** Environments are log-normally distributed.

**A level quoted with no percentile or confidence.** It cannot be compared or defended.

**Acceptance treated as demonstrating margin.** It equals the MPE.

**Zone boundaries drawn without a vibration argument.** The largest single lever, unexamined.

**Grms matched between two different spectra.** They damage hardware differently.

**A structural analysis run on a shock event.** Shock does not break structure.

---

## Worked numbers

From [`codeInterface.py`](../codeInterface.py), deriving the environment for hardware currently qualified against a generic key:

| Quantity | Value |
|---|---|
| Generic specification | 8.13 Grms, no basis |
| **Derived specification** | **9.25 Grms, P95/50 from 6 flights** |
| **Difference** | **+1.12 dB** |
| Standard deviation of the sample | 1.01 dB |
| Statistical margin over the mean | +1.67 dB |
| Shape normalisation onto the derived level | +1.00 dB |

**The hardware has been qualified to less than it will see**, and that is only findable by doing the derivation.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-HDBK-7005** | Dynamic environmental criteria. The derivation reference |
| **NASA-STD-7001** | Payload vibroacoustic test criteria |
| NASA-STD-7002 | Payload test requirements |
| **GSFC-STD-7000** | The GEVS general environmental verification specification |
| MIL-STD-1540 | Test requirements for launch, upper stage and space vehicles |
| MIL-STD-810 | Environmental engineering considerations and laboratory tests |
| ECSS-E-ST-10-03 | Testing |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from RandomVibrationSpec import RandomVibrationSpec

spec = RandomVibrationSpec()
spec.setInputs({'referenceSpectrum': 'GEVS qualification',
                'flightMeasurements': [0.042, 0.061, 0.038, 0.071, 0.049, 0.055]})

print(f'{spec.calculateOverallLevel()["grms"]:.2f} Grms')

statistics = spec.deriveMaximumPredicted()
print(f'{statistics["basis"]}: {statistics["limitValue"]:.4f} g^2/Hz, '
      f'{statistics["marginOverMean"]:+.2f} dB over the mean')
```

---

## Document index

| Document | Covers |
|---|---|
| [EnvironmentDerivation.md](EnvironmentDerivation.md) | Flight data to specification, and every margin added |
| [RandomVibration.md](RandomVibration.md) | PSD, Grms, zones, Miner scaling, test levels |
| [AcousticEnvironment.md](AcousticEnvironment.md) | SPL, octave bands, vibroacoustic response |
| [ShockEnvironment.md](ShockEnvironment.md) | Pyroshock, SRS, attenuation, test methods |
| [SineAndTransientVibration.md](SineAndTransientVibration.md) | Low frequency transients, sine equivalent |
| [StaticAndQuasiStaticLoads.md](StaticAndQuasiStaticLoads.md) | Load factors by event, combination |
| [AerodynamicLoads.md](AerodynamicLoads.md) | Max-Q, angle of attack, buffet, gust |
| [ThermalEnvironments.md](ThermalEnvironments.md) | Aeroheating, on-orbit cases, cycling |
| [PressureEnvironments.md](PressureEnvironments.md) | Ascent profile, venting, compartments |
| [NaturalEnvironments.md](NaturalEnvironments.md) | Wind, humidity, salt fog, radiation |
| [LoadCyclesAndCLA.md](LoadCyclesAndCLA.md) | The loads cycle, coupled loads analysis |
| [StandardsIndex.md](StandardsIndex.md) | Annotated index of the governing standards |

---

## References

1. NASA-HDBK-7005, *Dynamic Environmental Criteria*, 2001.
2. GSFC-STD-7000B, *General Environmental Verification Standard (GEVS)*.
3. Himelblau, H. et al., *Handbook for Dynamic Data Acquisition and Analysis*, IES-RP-DTE012.
