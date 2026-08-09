[Home](../README.md) > Test Stands

# Test Stands

## Contents

- [Overview](#overview)
- [What a stand actually measures](#what-a-stand-actually-measures)
- [The load path](#the-load-path)
- [Bias against scatter](#bias-against-scatter)
- [In-situ calibration](#in-situ-calibration)
- [Stand dynamics](#stand-dynamics)
- [Altitude simulation, and what it changes](#altitude-simulation-and-what-it-changes)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

A test stand holds an engine still and measures the force it produces. Both halves are harder than they sound, and the difficulty is concentrated in one place: everything else that crosses between the engine and the ground.

This document is qualitative. The computable content in this sub-domain is in [DataReduction](DataReduction.md) and [CampaignStructure](CampaignStructure.md), and a stand model would need geometry this repository does not carry.

---

## What a stand actually measures

**A load cell measures the force in the load cell.** Whether that equals the thrust depends on what else is carrying load in parallel with it.

The engine is connected to the ground by the thrust mount and by every propellant line, purge line, instrumentation cable, drain and vent that crosses the interface. All of them have stiffness. All of them carry a share of the thrust in proportion to it.

---

## The load path

The share carried by the plumbing is not constant. A pressurised line is stiffer than an unpressurised one, a cold line is stiffer than a warm one, and a flexible joint changes its stiffness with the pressure across it.

So the fraction of thrust bypassing the load cell **changes during the firing**, and it changes between the calibration and the test if the calibration was done with the lines empty.

The mitigations are ordinary and they have to be designed in rather than added later.

**Minimise the number of crossings.** Every line is a parallel load path.

**Make the crossings soft.** Flexible joints and bellows exist for this, and their stiffness is a specified quantity that should be specified.

**Route crossings perpendicular to the thrust axis** where the geometry permits, so that their stiffness acts in a direction the load cell does not measure.

---

## Bias against scatter

This is the part worth stating carefully because it changes what a repeat test is worth.

**A load path error is a bias, not a scatter.** It is the same on every firing with the same plumbing at the same pressure. Repeating the test does not find it, averaging does not reduce it, and a beautifully repeatable set of firings can all be wrong by the same amount.

Scatter is found by repeating. **Bias is found by changing something deliberately**, and that is the only way.

---

## In-situ calibration

The calibration that catches a load path bias is done with the engine installed, the lines connected, and **the lines at flight pressure**.

A known force is applied along the thrust axis, usually by a hydraulic cylinder or a dead weight through a reversing linkage, and the load cell reading is compared against it. Doing that with the lines depressurised calibrates a different stand from the one that will be fired.

Varying the line pressure across the calibration and watching the reading move is what quantifies the sensitivity. If it does not move, the crossings are soft enough. If it does, the amount it moves is the term that belongs in the uncertainty budget and usually is not there.

---

## Stand dynamics

The stand has natural frequencies and they land in the data.

The thrust structure, the engine mass and the mount stiffness form an oscillator whose frequency is typically in the tens to low hundreds of hertz. That is well below the acoustic modes in [StabilityRating](StabilityRating.md) and well within the band a load cell records.

Two consequences.

**A stand mode can be mistaken for a chug instability**, because both are low frequency oscillations visible in thrust and sometimes in chamber pressure. Distinguishing them takes either a modal survey of the stand, done once, or the observation that a stand mode does not move with chamber pressure and a chug does.

**Thrust during a transient is not thrust.** The start and shutdown ramps in [ignitionAndStart](../../ignitionAndStart/docs/ShutdownTransient.md) excite the stand, and the load cell records the sum of the engine thrust and the stand ringing. A cutoff impulse measured from an unfiltered thrust trace includes the stand.

**Do a modal survey.** It is cheap, it is done once, and without it every low frequency feature in the data is ambiguous forever.

---

## Altitude simulation, and what it changes

A sea level stand cannot test a high area ratio nozzle, because it separates. See [nozzles](../../nozzles/docs/FlowSeparation.md), where the separation criteria bound the area ratio a sea level firing permits.

Altitude simulation, by a diffuser and ejector system or by a vacuum chamber, removes that bound and adds its own difficulties: the diffuser has to start, its starting transient interacts with the engine start, and the back pressure it achieves is a measurement in its own right that belongs in the reduction.

**An engine tested at sea level and flown in vacuum has not had its nozzle tested**, and the part of the performance that comes from the nozzle is the part the reduction attributes to Cf.

---

## Design rules of thumb

- **Count the crossings.** Each one is a parallel load path.
- **Calibrate in situ, at flight line pressure.** Anything else calibrates a different stand.
- **Vary line pressure during calibration** and put the sensitivity in the budget.
- **Do a modal survey once.** Without it, every low frequency feature is ambiguous.
- **Do not read a transient off an unfiltered thrust trace.** The stand is in it.
- **Treat load path error as bias.** Repeating will not find it.

---

## Failure modes

**Calibration with the lines depressurised.** A bias that survives every repeat.

**A stiff line crossing the load path.** The same, and it grows with feed pressure.

**A stand mode diagnosed as a chug.** Costs an injector redesign that fixes nothing.

**Cutoff impulse from a raw thrust trace.** Includes the stand ringing.

**A high area ratio nozzle tested at sea level.** It separates, and the Cf measured is not the flight Cf.

**A diffuser start transient overlapping the engine start.** Two transients, one data set, and no way to attribute what happens.

---

## References

- Sutton and Biblarz, *Rocket Propulsion Elements*, the testing chapter
- [nozzles FlowSeparation](../../nozzles/docs/FlowSeparation.md), for the sea level area ratio bound
- [ignitionAndStart ShutdownTransient](../../ignitionAndStart/docs/ShutdownTransient.md), for the transient the stand rings on
- NASA SP-8124, *Liquid rocket engine self-cooled combustion chambers*, for stand and facility discussion
