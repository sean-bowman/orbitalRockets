[Home](../README.md) > Stability Rating

# Stability Rating

## Contents

- [Overview](#overview)
- [Why it is a survival requirement](#why-it-is-a-survival-requirement)
- [Bombs and pulse guns](#bombs-and-pulse-guns)
- [How hard the perturbation has to be](#how-hard-the-perturbation-has-to-be)
- [The chamber size that decides the device](#the-chamber-size-that-decides-the-device)
- [What the data system has to be able to see](#what-the-data-system-has-to-be-able-to-see)
- [The damp criterion, which this repository does not carry](#the-damp-criterion-which-this-repository-does-not-carry)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A dynamic stability rating test artificially perturbs the combustion and observes whether it recovers. It is the standard way a combustion stability requirement is verified, and it has been since the guidelines were first written in 1971.

[combustionDevices](../../combustionDevices/docs/CombustionStability.md) owns the stability model: the acoustic modes, the baffle and cavity design, the stiffness criterion. This document owns whether a test could demonstrate any of it.

---

## Why it is a survival requirement

Stability is not a performance parameter. Under high frequency instability the oscillatory chamber pressure amplitude can reach values whose peak to peak exceeds the mean chamber pressure, and the consequence is thermal rather than acoustic.

**The heat flux near the injector face can increase by a factor of 5 to 10, and it can double at the throat.**

No cooling design in this repository survives that. [combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) computes a circuit that does not close with comfortable margin at nominal flux; at five times nominal there is no circuit. That is why a stability rating is a hardware survival demonstration rather than a performance measurement, and why it is verified rather than analysed.

---

## Bombs and pulse guns

Two devices are used, and neither is off the shelf.

A **nondirectional bomb** is an explosive charge placed in the chamber. Bombs were used most on the large engines of the Apollo era: Atlas, H-1 and F-1 all used them, and the Gemini stability improvement programme was built around them. They are manufactured to rigorous specifications and their transport and handling requirements are demanding, and both of those have got worse rather than better.

A **pulse gun** is a breech holding an explosive charge, a burst disk, and a barrel firing into the chamber. The charge builds pressure behind the disk, the disk breaks, and a shock wave exits the barrel and perturbs the combustion. Simpler materials, far less restrictive handling and shipping, and consequently the direction the field has moved.

**The choice is usually procurement and handling rather than physics**, up to the chamber size limit below.

---

## How hard the perturbation has to be

Hard enough that what follows is a dynamic response rather than noise.

The NASA MSFC pulse gun development programme fired 44 tests into a chamber pressurised to 2300 psig with gaseous nitrogen. Its best configuration, a 0.40 inch breech with 15 to 16 grains of powder and a 24,000 psid burst disk, produced **zero-to-peak overpressures of 37 to 58 per cent of the mean chamber pressure**, and the paper states that this is adequate for typical combustion stability rating.

This repository takes the bottom of that band, **37 per cent**, as the minimum worth calling a perturbation. Below it the chamber has been tapped rather than perturbed, and a chamber that recovers from a tap has demonstrated nothing.

That figure is a floor taken from one programme rather than a specification, and it is registered as such.

---

## The chamber size that decides the device

The same source states that for large combustion chambers, **probably exceeding about 12 inches in diameter, a pulse gun may be unable to produce an adequate response**, necessitating a bomb. High chamber pressure may also reduce pulse gun effectiveness, though that is less well established, and adequate responses have been obtained in preburners above several thousand psia in smaller chambers.

The reference booster's chamber is 143 mm, well inside the pulse gun range. **That is an operational result rather than a technical one and it is worth having early**, because it decides whether the programme needs an explosives supply chain.

---

## What the data system has to be able to see

A stability rating is a statement about **amplitude and decay**, not about presence. Detecting that an oscillation happened is not a rating.

On the reference chamber the first tangential mode is at 4.09 kHz. Nyquist is 8.2 kHz and resolving amplitude and decay takes about **41 kHz**.

A performance data system at 5 kHz is below Nyquist. It does not miss the mode; it **aliases it into the performance band**, where it appears as a low frequency oscillation that is not there. See [Instrumentation](Instrumentation.md).

**A stability rating recorded at a performance sample rate has recorded nothing, and may have recorded something misleading.**

---

## The damp criterion, which this repository does not carry

The published guidelines specify how quickly the perturbation must decay for the engine to be rated stable, in terms of a recovery to within some band of chamber pressure within some time.

**This repository does not carry that criterion, because it has not read the source.** The CPIA combustion stability guidelines were first published in 1971 and the current revision was, as of 2021, nearly 25 years old and being updated. Those documents are not openly available and the criterion has not been verified against them.

Stating a damp time here from memory would put an unsourced number into a repository whose whole validation apparatus exists to prevent exactly that. It is recorded as a gap in [ValidationReferences](ValidationReferences.md) instead, with what it would take to close it.

What the tool does check is the perturbation magnitude and the device viability, both of which are sourced.

---

## Worked numbers

The reference booster, 143 mm chamber at 10 MPa.

| Quantity | Value |
|---|---|
| Pulse overpressure modelled | 45 % of chamber pressure |
| Reference minimum | 37 % |
| Verdict | Adequate |
| Chamber diameter | 143 mm |
| Pulse gun limit | about 305 mm |
| Verdict | Pulse gun viable |
| First tangential mode | 4.09 kHz |
| Rate to resolve it | 41 kHz |
| Heat flux multiplier at the injector face under instability | **5 to 10x** |

---

## Design rules of thumb

- **Perturb at 37 per cent of chamber pressure or more.** Below that it is a tap.
- **Check the chamber diameter before assuming a pulse gun.** Above about 12 inches it may not be enough.
- **Ten samples per cycle on the mode**, or the rating is not a rating.
- **Treat stability as a survival requirement.** The flux multiplier, not the noise, is the reason.
- **Do not quote a damp criterion you have not read.** Cite the guideline and get it.

---

## Failure modes

**A perturbation too small to be one.** The chamber recovers and nothing has been demonstrated.

**A pulse gun in a chamber too large for it.** Same outcome, arrived at by a different route, and it looks like a pass.

**A stability rating at a performance sample rate.** Below Nyquist, and aliasing makes it worse than a missing channel.

**Subscale stability taken as full scale stability.** Acoustics scale with diameter; element behaviour does not. See [CampaignStructure](CampaignStructure.md).

**Stability treated as a performance parameter.** It is a hardware survival requirement, and the 5 to 10 times flux multiplier is why.

---

## Tool interface

```python
from HotFireTest import HotFireTest

test = HotFireTest()
test.setInputs({'objective':       'Demonstrate dynamic stability against a pulse',
                'chamberPressure': 10.0e6,
                'chamberDiameter': 0.1433,
                'duration':        10.0,
                'sampleRate':      50000.0})

rating   = test.checkStabilityRating(pulseOverpressure = 4.5e6)
sampling = test.checkSampleRate()
```

`checkStabilityRating()` reports the perturbation adequacy and the device viability. It does not report a pass or a fail, because the damp criterion that would decide one is not carried.

---

## References

- Osborne, Hulka, McCay, Casiano and Dumbacher, *Development and Testing of Pulse Guns for Combustion Instability Testing*, AIAA Propulsion and Energy Forum 2021, NASA MSFC
- CPIA combustion stability guidelines, first published 1971, current revision as cited in the above and not read here
- [combustionDevices CombustionStability](../../combustionDevices/docs/CombustionStability.md), which owns the model this document tests
- Harrje and Reardon, *Liquid Propellant Rocket Combustion Instability*, NASA SP-194
