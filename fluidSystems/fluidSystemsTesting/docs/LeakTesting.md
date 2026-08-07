[Home](../README.md) > Leak Testing

# Leak Testing

## Contents

- [Overview](#overview)
- [Method selection](#method-selection)
- [Where leak testing repeats](#where-leak-testing-repeats)
- [Executing a helium test](#executing-a-helium-test)
- [Pressure decay](#pressure-decay)
- [Allocating the budget across joints](#allocating-the-budget-across-joints)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The physics of leaks (flow regimes, conductance, gas scaling, equivalent hole size) is in [fluidSystemsLibrary/docs/Leaks.md](../../fluidSystemsLibrary/docs/Leaks.md). This document is about executing the test.

Leak testing repeats more than any other test in a campaign, because it is the one that detects damage caused by everything else. It is also the test most often specified at a rate nobody checked was measurable.

---

## Method selection

| Method | Floor [scc/s He] | Locates? | Quantifies? | Notes |
|---|---|---|---|---|
| Mass spec, hard vacuum | 1e-11 | Roughly | Yes | The flight hardware reference. Needs the article to hold vacuum |
| Mass spec, inside out | 1e-10 | No | Yes | Total leakage; needs a chamber that fits the article |
| Accumulation / bagging | 1e-8 | No | Yes | Slow; enclosure volume and dwell must be controlled |
| **Sniffer probe** | **1e-6** | **Yes** | Poorly | Highly operator dependent. Good for locating |
| Pressure decay | 1e-4 | No | Yes | Temperature limited. See below |
| Bubble immersion | 1e-4 | Yes | By count | Wets the article; unusable if it must stay dry |
| Bubble solution | 1e-3 | Yes | No | A contamination source |
| Ultrasonic | 1e-2 | Yes | No | Gross leaks only; useful as a first pass |

**Choose the least sensitive method that clears the requirement with a factor of ten.** A mass spectrometer will measure anything and it is slow, expensive and demands the article hold vacuum. Specifying at the exact floor of a method turns every measurement into a pass/fail argument about instrumentation.

**If no method clears the requirement, the requirement is the problem.** The [`LeakTest`](../fluidSystemsTestingLibrary/LeakTest.py) class raises rather than planning a test that cannot work.

---

## Where leak testing repeats

| Point | Why it is there |
|---|---|
| Post assembly | Baseline, before anything is done to the article |
| **Post proof** | Proof can open a marginal joint |
| Post vibration | Vibration loosens joints and damages seals |
| Post thermal cycling | Differential contraction is what breaks a cryogenic seal |
| **At temperature** | A seal that passes at ambient can fail cold |
| Post life | Wear-out shows as leakage growth before functional failure |
| Pre-flight | Final verification in the flight configuration |

**Testing after each environmental exposure rather than only at the end** costs a few extra tests and tells you which exposure caused a failure. That is the difference between a corrective action and an investigation.

**Ambient leak testing does not qualify a cryogenic joint.** Differential contraction is the failure mechanism and it does not exist at room temperature.

---

## Executing a helium test

**Bracket with a calibrated leak standard.** Measure the standard before and after. If the two disagree, the data between them is not usable. This is the single most important procedural control in leak testing.

**Background helium** rises through the day as helium is sprayed and it sets the practical floor far more often than the instrument does. Ventilate, and take a background reading before every measurement.

**Work from least likely to most likely.** A large leak saturates the spectrometer and takes minutes to clear. Finding the big one first costs you the rest of the shift.

**Spray probe control.** Helium is lighter than air and rises. Spray from the bottom up, at a controlled rate, and allow the system response time between locations. A fast traverse produces a signal that cannot be attributed to a location.

**Record everything:** method, instrument, calibration standard and date, background level, technique, dwell times, temperature. Leak data without those is not repeatable and therefore not usable as evidence.

---

## Pressure decay

```
Q = V * dP / dt          so      Q_min = V * dP_resolution / t_test
```

That is the transducer-limited floor, and it is almost never the binding one.

**The binding constraint is temperature.** For a fixed volume of gas, `dP/P = dT/T`. A drift of 0.1 K at 293 K is 3.4e-4 of the absolute pressure, which at 10 MPa is 3.4 kPa: orders of magnitude above any leak signal worth chasing.

| Case: 10 L at 2.4 MPa, 100 Pa transducer, 1 h, 0.1 K stability | Floor |
|---|---|
| Transducer limited | 2.7e-3 scc/s |
| **Temperature limited** | **2.2e-2 scc/s** |
| Binding | Temperature, by a factor of 8.2 |

**Making it work**, when it must:

1. Thermal soak for hours, and measure gas temperature rather than ambient
2. Measure and compensate: correct pressure to a reference temperature, buying one to two orders of magnitude
3. **Reference volume**: a sealed, identical, known-tight volume measured differentially, so common-mode temperature effects cancel. The standard method for sensitive decay testing
4. Minimize the volume: isolate the smallest volume containing the joint under test
5. Differential rather than absolute transducer, gaining the turndown ratio in resolution

**Pressure decay is a system integrity check, not a joint qualification test.** It earns its place where the requirement is coarse, no tracer gas is available, or the system is too large to bag or evacuate.

---

## Allocating the budget across joints

Leak rates add. A system allowable divided by the joint count gives the per-joint allowable, and comparing that against what joint families actually achieve is what turns a leak requirement into a joint selection decision.

| Joint family | Achievable [scc/s He] |
|---|---|
| Welded | 1e-9 |
| VCR metal gasket | 4e-9 |
| Compression fitting | 1e-6 |
| SAE boss o-ring | 1e-6 |
| **AN flare** | **1e-4** |
| NPT | 1e-3 |

**Do this allocation early.** It is the calculation that stops a programme discovering at leak check that its fittings were never going to work.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Method margin over its floor | 10x minimum |
| Bracket with a calibrated leak | Before and after, always |
| Background measurement | Before every measurement |
| Test order | Least likely leak location first |
| Leak test after every environment | Not only at the end |
| Cryogenic hardware | Test cold; ambient does not qualify it |
| Pressure decay | Temperature limited, not transducer limited |
| Reference volume for sensitive decay | Cancels common-mode drift |
| Allocate across joints early | Drives the joint architecture |

---

## Failure modes

**A requirement nobody checked was measurable.** Discovered at test planning or later.

**Background helium mistaken for a leak.** Every failed check should start with a background measurement.

**Permeation mistaken for a leak.** An elastomer-sealed joint has an irreducible permeation rate. If the measured rate matches the calculated permeation, the joint is not leaking.

**Virtual leaks.** A trapped volume inside the article outgasses into the evacuated system and looks exactly like a real leak. It cannot be found by external spray. Design them out.

**Ambient-only testing on cryogenic hardware.** The seal passes every check and fails cold.

**A leak found, fixed, and reappearing.** Usually a second leak masked by the first, or a joint disturbed while fixing it. Re-check the whole article after any repair.

**Calibration drift across the test.** Caught by bracketing, missed without it.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), verifying the hazard-derived system allowable:

| Quantity | Value |
|---|---|
| System allowable (from the hydrazine TLV) | 1.042e-05 scc/s He |
| Joint count | 12 |
| **Per-joint allowable** | **8.68e-07 scc/s** |
| Joint families that clear it | **Welded, VCR metal gasket only** |
| Selected method | Sniffer probe (floor 1e-6, margin 10.4x) |
| Equivalent hole diameter | 0.686 micron |
| Flow regime | Transitional |
| Pressure decay floor | 2.27e-02 scc/s, temperature limited |
| Pressure decay feasible | **No**, by three orders of magnitude |
| Scaled to nitrogen service | 6.70e-06 scc/s |

The finding matches the design-side analysis exactly: the AN flare unions used in the design example cannot meet the allowable. Both directories reach the same conclusion from opposite ends, which is the cross-check working as intended.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM E432 | Selection of a leak testing method |
| ASTM E479 | Preparation of a leak testing specification |
| ASTM E493 / E498 / E499 | Mass spectrometer: inside-out, tracer probe, detector probe |
| ASTM E515 | Bubble emission techniques |
| ASME BPVC Section V Article 10 | Leak testing |
| **MIL-STD-1330** | Cleaning and testing of shipboard oxygen, nitrogen and hydrogen systems |
| ISO 20485 | Non-destructive testing, leak testing, tracer gas method |
| ANSI/FCI 70-2 | Control valve seat leakage classification |

---

## Tool interface

```python
from LeakTest import LeakTest

test = LeakTest()
test.setInputs({'allowableLeakRate': 1.042e-5, 'species': 'He', 'serviceFluid': 'Nitrogen',
                'testPressure': 2.4249e6, 'downstreamPressure': 101325.0,
                'jointCount': 12, 'testVolume': 0.010,
                'transducerResolution': 100.0, 'testDuration': 3600.0})

test.selectMethod()             # raises TestInfeasibleError if nothing can see it
test.allocateAcrossJoints()     # per-joint allowable and which families clear it
test.evaluatePressureDecay()    # delegates to fluidSystems LeakPath
test.scaleToServiceFluid()
print(test.generateReport())
```

---

## References

1. Jousten, K. (ed.), *Handbook of Vacuum Technology*, 2nd ed., Wiley-VCH, 2016.
2. ASTM E432-91, *Standard Guide for Selection of a Leak Testing Method*.
3. Nondestructive Testing Handbook, Volume 1: *Leak Testing*, 4th ed., ASNT, 2017.
4. Marr, J. W., *Leakage Testing Handbook*, NASA CR-952, 1968.
