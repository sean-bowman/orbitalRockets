[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [The AWG definition](#the-awg-definition)
- [SAE AS50881](#sae-as50881)
- [MIL-STD-461 and MIL-STD-464](#mil-std-461-and-mil-std-464)
- [MIL-STD-704](#mil-std-704)
- [MIL-STD-1576](#mil-std-1576)
- [What was not read](#what-was-not-read)
- [References](#references)

---

## Overview

This domain rests on one exact definition and several standards that were not read. That is an unusual split and it is worth being explicit about, because the one exact thing happens to be the one the domain's central result depends on.

---

## The AWG definition

Not a standard document so much as a long-established definition, and it is exact:

```
d(n) = 0.127 mm * 92 ** ((36 - n) / 39)
```

36 AWG is exactly 0.005 inches and each gauge step multiplies the diameter by the 39th root of 92. Combined with the standard annealed copper resistivity of 1.724e-8 ohm m at 20 C, that makes every conductor resistance in this library computed rather than tabulated.

**It reproduces published resistance tables to four significant figures**, which is the tightest agreement anywhere in this repository.

That matters more than it sounds. The domain concludes that voltage drop rather than ampacity chooses the wire gauge on a launch vehicle harness, and voltage drop is a pure resistance calculation. **The exact half of that comparison is the half the conclusion rests on**, and the representative half, ampacity, would have to be wrong by several gauge steps to overturn it.

---

## SAE AS50881

*Wiring Aerospace Vehicle*. The governing standard for wire selection, installation, current rating, derating for bundle size and altitude, marking, routing, clamping and separation of redundant circuits.

**Not read.** It is not openly available, and its current ratings and derating factors are given as curves rather than tables in any case.

The consequence is that `SINGLE_WIRE_AMPACITY`, `BUNDLE_DERATING` and `ALTITUDE_DERATING` in this library are representative values consistent with common practice, and they are registered as unvalidated in [ValidationReferences](ValidationReferences.md).

**Obtaining it is the largest closable gap in the domain**, and the bundle derating curve is the piece worth getting first, because it is the larger of the two effects.

---

## MIL-STD-461 and MIL-STD-464

*Requirements for the Control of Electromagnetic Interference Characteristics of Subsystems and Equipment*, and *Electromagnetic Environmental Effects Requirements for Systems*.

Between them they define the emissions and susceptibility limits, the test methods, and the system-level electromagnetic requirements including bonding, grounding, lightning and static.

**Neither is read**, and [EMIAndEMC](EMIAndEMC.md) is therefore qualitative throughout. The requirement group structure it describes, CE, CS, RE and RS, is the standard's organisation; the limits are not carried.

---

## MIL-STD-704

*Aircraft Electric Power Characteristics*. Defines the steady-state and transient characteristics of an electrical power system and what utilisation equipment must tolerate.

**Not read.** [PowerQuality](PowerQuality.md) describes the four disturbance categories qualitatively and carries none of the limits.

It is worth naming because it is the document that would turn "specify behaviour, not just tolerance" from advice into a requirement.

---

## MIL-STD-1576

*Electroexplosive Subsystem Safety Requirements and Test Methods for Space Systems*.

**Not read**, in this domain or in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/StandardsIndex.md), which is where the firing circuit calculation lives. The no-fire and all-fire conventions used there come from general practice.

It is recorded in both domains as the largest gap affecting ordnance, and it is the one standard whose absence touches two domains at once.

---

## What was not read

Collected, because in this domain the list is longer than the list of what was.

| Standard | Would fix |
|---|---|
| SAE AS50881 | Ampacity and derating, currently representative |
| MIL-STD-461 | Emissions and susceptibility limits, currently absent |
| MIL-STD-464 | System-level EMC and bonding requirements |
| MIL-STD-704 | Power quality limits and required tolerance |
| MIL-STD-1576 | Initiator margins, shared with mechanisms |

**And one that has no standard to read**: the cell datasheet for the actual battery, which would replace every derating factor in [BatteriesAndStorage](BatteriesAndStorage.md) with a measured curve. That is published by every manufacturer and it is the most tractable gap of the lot.

---

## References

- The AWG definition and standard copper resistivity
- SAE AS50881, *Wiring Aerospace Vehicle*
- MIL-STD-461, MIL-STD-464, MIL-STD-704, MIL-STD-1576
- [ValidationReferences](ValidationReferences.md)
