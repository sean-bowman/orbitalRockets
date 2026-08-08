[Home](../README.md) > Shock Environment

# Shock Environment

## Contents

- [Overview](#overview)
- [What an SRS is and is not](#what-an-srs-is-and-is-not)
- [Sources](#sources)
- [Attenuation](#attenuation)
- [What shock actually breaks](#what-shock-actually-breaks)
- [Test methods](#test-methods)
- [Why the margin is 6 dB](#why-the-margin-is-6-db)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Shock is the environment with the worst signal-to-noise ratio in the discipline. The event lasts milliseconds, the peak accelerations are thousands of g, the measurement is difficult and frequently wrong, and the flight-to-flight scatter is large enough that the qualification margin is doubled relative to random vibration.

---

## What an SRS is and is not

**The shock response spectrum is the peak response of a family of single degree of freedom oscillators**, one per frequency, all driven by the same base transient, conventionally at Q = 10.

```
SRS(f) = max over time of the response of an oscillator at f with Q = 10
```

**It is not a Fourier spectrum** and it does not describe the event. It describes what the event would do to a simple oscillator, which is a damage-potential summary.

**It is not invertible.** Many different transients produce the same SRS, and two of them can damage real hardware differently. Matching an SRS in test does not mean reproducing the flight event.

**Q matters and is often omitted.** An SRS at Q = 10 and one at Q = 50 are different numbers for the same event. Comparing them without conversion is meaningless, and Q = 10 is the near-universal convention precisely so the comparison usually works.

---

## Sources

| Source | Peak SRS | Character |
|---|---|---|
| **Linear shaped charge** | 10000 g | The most severe. Stage separation |
| **Frangible joint** | 6000 g | Contained, cleaner |
| Explosive bolt | 3000 g | Local, and there are usually several |
| Clamp band release | 1500 g | Payload separation, distributed |
| Separation nut | 2000 g | Lower shock, heavier hardware |
| **Pin puller** | 1000 g | Low shock release device |

**Pyrotechnic devices are chosen for reliability, not for low shock**, which is why the severe ones persist. A low-shock alternative usually has more parts and a lower demonstrated reliability, and that trade is made in favour of working.

**There are more shock events than people expect.** Every separation, every deployment, every valve actuation with a pyrotechnic initiator, and they all occur at least once in a mission that has to work the first time.

---

## Attenuation

**This is what makes pyroshock survivable.**

| Mechanism | Rule |
|---|---|
| **Distance** | **-13 dB per metre**, an engineering approximation |
| **Bolted joint** | -3 dB per joint |
| Riveted joint | -3 dB per joint |
| Bonded joint | -2 dB |
| Welded joint | -1 dB |
| **Shock isolator** | **-20 dB** |

**High frequency content is dissipated over a short path**, far faster than vibration, which is why the distance rule is so steep. A component a metre away behind two bolted joints sees roughly a twelfth of the source level.

**Moving a sensitive component is cheaper than qualifying it.** That is the single most useful design response to a shock problem and it is available early and not late.

**Joints attenuate because interfaces slip.** A welded joint is continuous and dissipates little; a bolted one has a friction interface that converts energy to heat. That is why a monolithic machined structure transmits shock better than a built-up one.

---

## What shock actually breaks

**Small stiff things, and not structure.**

| Vulnerable | Why |
|---|---|
| **Relays** | Contacts chatter or transfer |
| **Crystals and oscillators** | Brittle, and resonant in the shock band |
| **Solder joints** | Especially large components on thin boards |
| **Brittle parts** | Ceramics, glass, optical elements |
| Connectors | Unseat or momentarily open |
| Fasteners | Loosen, if not locked |

**Structure is generally unharmed.** A shock event that destroys a relay leaves the bracket the relay is mounted to entirely fine, because the structure's mass and its low frequency modes do not respond to a millisecond transient.

**A structural analysis of a shock event usually misses the point.** The right question is which components sit in the shock path and whether their internal resonances fall in the amplified band.

**Relay chatter is a functional failure, not a physical one.** The relay works perfectly afterwards; it simply changed state at the wrong moment, which for a flight termination system or an ordnance circuit is not a small matter.

---

## Test methods

| Method | Fidelity | Character |
|---|---|---|
| **Pyrotechnic, flight article** | **Highest** | The actual device on the actual structure |
| **Mechanical impact** | Good above 1 kHz | Resonant plate or bar. The common choice |
| **Electrodynamic shaker** | **Poor above 2 kHz** | Synthesised transient, limited by stroke |
| Drop table | Low frequency only | Classical pulses. Not pyroshock |

**A shaker cannot reproduce pyroshock above about 2 kHz**, which is where most of the damage potential is. A shaker shock test that passes proves less than it appears to, and that limitation should be stated in the test report rather than discovered later.

**Mechanical impact is the practical answer** for most component qualification: a resonant plate struck by a projectile, tuned to match the SRS.

**Matching the SRS does not match the event.** Two tests that both meet the specification can damage hardware differently, because the SRS is a lossy summary.

---

## Why the margin is 6 dB

**Because the scatter is larger and the measurement is worse.**

| Reason | Detail |
|---|---|
| **Flight-to-flight variation** | Pyrotechnic events are not repeatable to a few percent |
| **Measurement difficulty** | Accelerometer resonance, zero shift, cable effects |
| **The SRS is lossy** | It summarises a transient that varies |
| Path variability | Joint preload and contact condition change with build |

**Six decibels is a factor of two in level**, not in energy, because an SRS is an amplitude quantity. That is a different arithmetic from random vibration's +3 dB, which is a factor of two in power spectral density and only 1.41 in Grms.

**Accelerometer zero shift is a real and common measurement artefact.** A piezoelectric accelerometer driven beyond its linear range produces a DC offset that integrates into an enormous apparent velocity change, and an SRS computed from it is wrong at low frequency. That is one reason an SRS below about 100 Hz is usually an artefact.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| SRS at Q = 10 | State it, or the number is ambiguous |
| An SRS is not invertible | Matching it does not match the event |
| Distance attenuation | -13 dB per metre |
| Bolted joint | -3 dB each |
| Isolator | -20 dB |
| Move the component rather than qualify it | The cheapest fix |
| Shock breaks relays and crystals | Not structure |
| Shaker cannot reproduce above ~2 kHz | State the limitation |
| Qualification margin | +6 dB, a factor of two in level |

---

## Failure modes

**A structural analysis run on a shock event.** Shock does not break structure.

**An SRS quoted without its Q.** Ambiguous by a large factor.

**A shaker shock test accepted as equivalent.** Not above 2 kHz.

**SRS matched and the event assumed reproduced.** Many transients share one SRS.

**An SRS below 100 Hz taken seriously.** Usually accelerometer zero shift.

**Relay chatter treated as a non-failure.** For an ordnance circuit it is a failure.

**Shock path assumed from the drawing.** Joint preload and contact vary with build.

---

## Worked numbers

From [`ShockSpectrum`](../environmentsAndLoadsLibrary/ShockSpectrum.py), a linear shaped charge at 1.2 m behind two bolted joints:

| Quantity | Value |
|---|---|
| Source peak | 10000 g |
| Distance attenuation | -15.6 dB |
| Joint attenuation | -6.0 dB |
| **Total** | **-21.6 dB** |
| **At the component** | **832 g** |
| Qualification (+6 dB) | 1660 g |

**A factor of 12 in level from a metre of structure and two joints.**

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-7003** | Pyroshock test criteria |
| NASA-HDBK-7005 | Dynamic environmental criteria |
| **MIL-STD-810 Method 517** | Pyroshock test methods |
| MIL-STD-1540 | Test requirements |
| **NASA SP-8072** | Acoustic loads generated by the propulsion system |
| ANSI S2.10 | Analysis and presentation of shock and vibration data |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from ShockSpectrum import ShockSpectrum, SHOCK_SOURCES

for distance, joints in ((0.1, []), (1.2, ['bolted', 'bolted']),
                         (2.0, ['bolted', 'bolted', 'welded'])):
    shock = ShockSpectrum()
    shock.setInputs({'source': 'linear shaped charge', 'distance': distance,
                     'jointPath': joints})
    attenuation = shock.calculateAttenuation()
    levels      = shock.deriveTestLevels()
    print(f'{distance:.1f} m, {len(joints)} joints: '
          f'{attenuation["totalAttenuation"]:+6.1f} dB -> '
          f'{levels["maximumPredictedPeak"]:6.0f} g')

print(shock.compareTestMethods()['findings'][0])
```

---

## References

1. NASA-STD-7003A, *Pyroshock Test Criteria*.
2. Himelblau, H. et al., *Guidelines for Dynamic Data Acquisition and Analysis*, NASA-HDBK-7005.
3. Kacena, W. J., McGrath, M. B. and Rader, W. P., *Aerospace Systems Pyrotechnic Shock Data*, NASA CR-116437, 1970.
