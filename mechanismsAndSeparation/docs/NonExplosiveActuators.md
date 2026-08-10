[Home](../README.md) > Non-Explosive Actuators

# Non-Explosive Actuators

## Contents

- [Overview](#overview)
- [The devices](#the-devices)
- [The trade against pyrotechnics](#the-trade-against-pyrotechnics)
- [Where they win](#where-they-win)
- [Where they do not](#where-they-do-not)
- [Why none of them is sized here](#why-none-of-them-is-sized-here)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

A non-explosive actuator releases a preloaded joint without an explosive train. The category exists almost entirely because of shock, and the trade is more one-sided than it first appears.

---

## The devices

**Shape memory alloy.** A pre-strained element is heated past its transition temperature, recovers its shape, and that motion releases a latch. No debris, low shock, resettable on the bench, and it needs sustained electrical power for seconds rather than milliseconds.

**Paraffin actuator.** A wax charge is heated and expands, driving a piston. High force, slow, resettable, and the actuation time depends on the thermal environment, which means a cold vehicle deploys later than a warm one.

**Split spool.** A preloaded spool held together by a redundant restraint, released by fusing a wire or by a shape memory element. High preload capacity in a small package, and the release is fast enough to be useful without being a shock source.

**Fuse wire and burn wire.** The simplest of all: a loaded restraint held by a wire that is melted by current. Cheap, light, and its reliability depends on a single wire and the current getting to it.

---

## The trade against pyrotechnics

| Axis | Pyrotechnic | Non-explosive |
|---|---|---|
| Shock | High, and it reaches everything nearby | Low to negligible |
| Actuation time | Milliseconds | Seconds |
| Power | A firing pulse | Sustained, seconds of watts |
| Debris and contamination | Yes, unless contained | None |
| Resettable for test | No | Usually yes |
| Handling and shipping | Restricted, expensive, licensed | Ordinary |
| Preload capacity | Very high | High, and device-limited |
| Flight heritage | Extensive | Extensive on spacecraft, less on launch vehicles |

**The two decisive rows are shock and resettability**, and they point the same way.

---

## Where they win

**Anywhere near sensitive hardware.** Optics, detectors and precision mechanisms are damaged by shock long before structure is, and eliminating the source is easier than qualifying everything nearby to survive it.

**Where the same mechanism has to be tested repeatedly.** A resettable device can be functionally tested on the flight article. A pyrotechnic cannot: the article that flies has never been fired, and every test is on a different unit. **That is a categorical difference in what the qualification evidence means.**

**Where handling dominates the programme.** Explosive devices bring licensing, storage, transport restrictions, and a set of operations that a small programme may not be able to support at all.

---

## Where they do not

**When the release has to be fast.** A stage separation with a tight sequence cannot wait seconds, and a device whose actuation time varies with temperature makes the sequence uncertain as well as slow.

**When the preload is very high.** A large clamp band is a pyrotechnic application because the energy is there and the alternatives are heavy.

**When the power is not available.** Seconds of watts at exactly the wrong moment in a power budget is a real constraint, and it is worse on a small vehicle. See [electricalPower](../../electricalPower/).

**When the thermal environment is uncontrolled.** A paraffin actuator in an unknown thermal state has an unknown actuation time.

---

## Why none of them is sized here

Every device in this category is a proprietary characteristic curve rather than a calculation.

Actuation time against temperature, release load against preload, power against ambient: all of them are manufacturer test data for a specific part number, and none follows from a governing equation the way a spring or a bridgewire does.

**So this document describes the trade and models nothing**, which is the same decision this repository made about pyroshock and about tribology. Sizing one of these from a plausible-looking correlation would produce a number with no provenance in a domain that cannot afford one.

What [MechanismActuator](ActuatorsAndDrives.md) does apply is the margin equation, which works for any driving device once its available torque or force is known from its data sheet.

---

## Design rules of thumb

- **Start non-explosive near anything sensitive.** Eliminating shock beats qualifying against it.
- **Value resettability properly.** It changes what the flight article's test evidence means.
- **Check the power profile**, not just the energy. Seconds of watts is a different ask from a pulse.
- **Check actuation time across the thermal range**, not at ambient.
- **Take the performance from the manufacturer's test data.** There is no equation for it.

---

## Failure modes

**A slow device in a fast sequence.** Seconds where the sequence allowed milliseconds.

**A thermally sensitive device in an uncontrolled environment.** The actuation time becomes a range.

**Power not budgeted.** The device draws watts for seconds at a moment already busy.

**Performance taken from a correlation rather than the data sheet.** There is no governing equation.

**Resettability assumed.** Not every device in the category resets, and some reset only on the bench.

---

## References

- NASA-STD-5017B, which applies to these devices as much as to pyrotechnics
- [Pyrotechnics](Pyrotechnics.md), for what they are replacing
- [electricalPower](../../electricalPower/), for the sustained power they need
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*
