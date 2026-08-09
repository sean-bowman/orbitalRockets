[Home](../README.md) > Instrumentation

# Instrumentation

## Contents

- [Overview](#overview)
- [The four channels a reduction needs](#the-four-channels-a-reduction-needs)
- [What makes each one hard](#what-makes-each-one-hard)
- [Sample rate, and the three thresholds](#sample-rate-and-the-three-thresholds)
- [Aliasing is worse than not measuring](#aliasing-is-worse-than-not-measuring)
- [Filtering, and what it removes](#filtering-and-what-it-removes)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Instrumentation decides what a firing can establish, and the decisions are all made before anyone lights anything. A channel that was not recorded, was recorded too slowly, or was filtered before it was stored, cannot be recovered afterwards.

---

## The four channels a reduction needs

Chamber pressure, thrust, propellant mass flow, and the throat area. The last is not usually called instrumentation and it carries as much uncertainty as any of the others; see [DataReduction](DataReduction.md).

| Channel | Representative | What sets it |
|---|---|---|
| Chamber pressure | 0.50 % | The tap, more often than the transducer |
| Thrust | 0.75 % | The load path, not the load cell |
| Mass flow | 1.00 % | Per propellant, and the total is the RSS of two |
| Throat area | 1.00 % | A cold diameter, doubled, with no erosion term |

These are representative of good practice rather than of any installation. **A real budget comes from the calibration certificates**, and they are registered as unvalidated in this repository for that reason.

---

## What makes each one hard

**Chamber pressure.** The transducer is usually better than the number above. What degrades it is the tap: a short passage that fills with combustion products, an unpurged line that reads a standing wave, or a location inside a recirculation zone reading something that is not the chamber. The transducer is calibrated and the tap is not.

**Thrust.** The load cell is the best instrument in the set. The load path is not. Every line crossing from ground to engine carries a fraction of the thrust, and that fraction changes with pressure and temperature. It is a **bias rather than a scatter**, which means repeating the test does not find it, and the only ways to catch it are an in-situ calibration with the plumbing pressurised and a deliberate variation in line pressure.

**Mass flow.** Two meters, one per propellant, and the total is the root sum of squares of the two. Cryogenic service degrades a turbine meter through density uncertainty; two-phase flow degrades it through both density and the meter's own response, which is what makes flow measurement during a chill-in transient effectively unavailable. See [ignitionAndStart](../../ignitionAndStart/docs/ChillInAndConditioning.md).

**Throat area.** Covered in [DataReduction](DataReduction.md). It is a cold, single measurement of a hot, changing dimension.

---

## Sample rate, and the three thresholds

The frequency that matters is the first tangential acoustic mode, because it is the one that destroys engines. [combustionDevices](../../combustionDevices/docs/CombustionStability.md) owns the stability model; this sub-domain owns whether the data system could have seen it.

```
f_1T = 1.8412 * a / (pi * D)
```

On a 143 mm chamber with a representative speed of sound of 1000 m/s that is **4.09 kHz**, and there are three thresholds against it.

| Threshold | Rate | Answers |
|---|---|---|
| Nyquist, 2x | 8.2 kHz | Is the frequency representable at all |
| Detection, practical | above Nyquist with margin | Did an instability happen |
| **Resolution, 10x** | **41 kHz** | How large was it and how fast did it damp |

**Ten samples per cycle is the working rule for a stability rating**, because a rating is a statement about amplitude and decay rather than about presence. Nyquist is a theoretical floor and it is not a usable engineering criterion for a transient waveform.

---

## Aliasing is worse than not measuring

A typical performance data system runs at a few kilohertz. On the reference chamber that is **below Nyquist for the 1T mode**.

Below Nyquist the mode does not vanish. It aliases down into the performance band and appears as a low frequency oscillation that is not there.

**A test set up this way can produce a chug investigation into a 1T mode.** That is not a missing measurement, it is a wrong one, and it costs more than the missing one would have.

The fix is an anti-alias filter ahead of the sampler on every channel that is not being sampled fast enough to see what is there. That is a hardware decision made at build time, and it is the reason it is worth asking what frequencies exist before choosing a data system rather than after.

---

## Filtering, and what it removes

Filtering applied before storage is irreversible, and there is rarely a good reason for it now that storage is cheap.

Two distinct things get called filtering. **Anti-alias filtering** is necessary and belongs in hardware ahead of the sampler. **Smoothing** is analysis and belongs after storage, where it can be undone.

Storing only the smoothed channel is how a test loses the evidence for the thing that went wrong, and it is not recoverable afterwards.

---

## Worked numbers

The reference booster, 143 mm chamber.

| Quantity | Value |
|---|---|
| First tangential mode | 4.09 kHz |
| Rate to detect | 8.2 kHz |
| Rate to resolve amplitude and decay | 41 kHz |
| Typical performance data system | 5 kHz |
| Verdict | **Below Nyquist. Aliases into the performance band** |

---

## Design rules of thumb

- **Compute the acoustic modes before choosing a data system rate**, not after.
- **Ten samples per cycle for a stability rating.** Nyquist detects; it does not resolve.
- **Anti-alias in hardware, smooth in software.** One is necessary and irreversible, the other is analysis.
- **Store raw.** Storage is cheaper than a repeat test.
- **Calibrate thrust in situ with the plumbing pressurised.** The load path is a bias and repeating the test will not find it.
- **Purge the pressure taps.** The tap is usually worse than the transducer.

---

## Failure modes

**A performance data system asked to support a stability objective.** Below Nyquist, and it aliases rather than misses.

**Thrust calibrated with the lines depressurised.** A bias that survives every repeat.

**An unpurged chamber pressure tap.** Reads a standing wave or a plugged passage.

**Filtering before storage.** Irreversible, and it removes the evidence for the anomaly.

**Flow measurement trusted through a transient.** Two-phase flow degrades both the density and the meter response.

**The throat area left out of the instrumentation list.** It is tied for the largest uncertainty in the c* budget.

---

## Tool interface

```python
from HotFireTest import HotFireTest

test = HotFireTest()
test.setInputs({'objective':       'Establish c* efficiency at the design point',
                'chamberPressure': 10.0e6,
                'chamberDiameter': 0.1433,
                'residenceTime':   0.00147,
                'duration':        10.0,
                'sampleRate':      5000.0})

sampling = test.checkSampleRate()

print(test.generateReport())
```

`checkSampleRate()` returns `detects` and `resolves` separately, and both are `None` when no sample rate was supplied, because asserting nothing is better than asserting a default.

---

## References

- [combustionDevices CombustionStability](../../combustionDevices/docs/CombustionStability.md), for the acoustic mode model this document samples against
- Osborne, Hulka, McCay, Casiano and Dumbacher, *Development and Testing of Pulse Guns for Combustion Instability Testing*, AIAA Propulsion and Energy Forum 2021
- ISA-37 series, transducer specification and terminology
- Sutton and Biblarz, *Rocket Propulsion Elements*, the testing chapter
