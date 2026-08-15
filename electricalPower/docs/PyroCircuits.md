[Home](../README.md) > Pyro Circuits

# Pyro Circuits

## Contents

- [Overview](#overview)
- [Where this lives](#where-this-lives)
- [What this domain supplies](#what-this-domain-supplies)
- [What that domain decides](#what-that-domain-decides)
- [The electrical requirements it imposes back](#the-electrical-requirements-it-imposes-back)
- [Design rules of thumb](#design-rules-of-thumb)
- [References](#references)

---

## Overview

The firing circuit is an electrical circuit and it is not modelled here. This document explains where it is modelled and why the boundary is drawn there.

---

## Where this lives

`PyroCircuit` was planned for this library and **deliberately not built**.

`PyrotechnicInitiator` in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/Pyrotechnics.md) already computes the firing current through the harness, the no-fire margin against stray energy, the parallel-device arithmetic that catches a circuit sized for one initiator and flown with two, and the trade between a sensitive device and a robust one.

Two implementations of the same circuit with nothing enforcing agreement between them is the failure this repository has avoided in five other places, and the boundary is drawn the same way here.

The general rule: an argument against duplicating a neighbouring tool is not an argument against every calculation in its subject. What matters is whether the two would compute the *same quantity*, and here they would.

---

## What this domain supplies

Three things the firing circuit calculation consumes, and all three are outputs of classes in this library.

**The bus voltage at the worst credible moment**, which is a cold battery at the end of a long countdown rather than a nameplate value. That comes from [Battery](BatteriesAndStorage.md) and the discharge behaviour it models.

**The harness resistance**, which is usually the dominant term in the firing loop and is computed exactly from the [AWG definition](HarnessDesign.md). On the reference circuit it is 0.9 ohm against a 1.05 ohm bridgewire, so it is comparable to the device itself.

**The credible stray current**, which comes from the [electromagnetic environment](EMIAndEMC.md) rather than from a circuit calculation, and which this domain documents and does not compute.

---

## What that domain decides

Whether the device fires, and whether it can be fired by accident.

The arithmetic and the results are in [mechanismsAndSeparation Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md). Briefly: an NSI has a 1 A and 1 W no-fire and about a 5 A all-fire, the reference circuit delivers 9.49 A per device with two in parallel, and the stray margin is a factor of 6.7 on current and 42 on power.

---

## The electrical requirements it imposes back

This is the part worth having in this domain, because the ordnance requirement drives electrical design that has nothing to do with firing anything.

**The tightest EMC requirement on the vehicle usually comes from the initiators.** One amp is a small number, and guaranteeing the harness never delivers it against radio frequency pickup, lightning transients, static discharge and a misconnected test set drives the bonding, the shielding, the twisted shielded pairs and the shorting plugs. See [EMIAndEMC](EMIAndEMC.md).

**Ordnance circuits use mechanical interruption, not solid state switching.** A transistor never fully opens, and leakage current into a bridgewire is exactly the thing a safe and arm device exists to make impossible. That is a switching decision made in this domain for a reason that originates in another.

**The pyro bus sizes nothing in the energy budget.** On the reference stage it is 120 W for milliseconds, which is 0.0 per cent of the mission energy. It is on the load list because it has to be, and the number that matters about it is a current rather than an energy.

**The firing circuit resistance is a harness requirement with a hard limit**, unlike most loads where a few per cent of voltage drop is a performance question. Here it decides whether the device fires at all.

---

## Design rules of thumb

- **Take the firing calculation from mechanisms**, and supply it the bus voltage and harness resistance.
- **Size the firing harness on the all-fire current**, which is a hard limit rather than a performance one.
- **Use mechanical interruption.** A solid state switch leaks.
- **Let the initiator sensitivity set the EMC requirement**, because it does.
- **Do not put the pyro bus in the energy budget as a driver.** It is a current, not an energy.

---

## References

- [mechanismsAndSeparation Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md), which owns the calculation
- [HarnessDesign](HarnessDesign.md), for the resistance it consumes
- [EMIAndEMC](EMIAndEMC.md), for the stray energy environment
- MIL-STD-1576, *Electroexplosive Subsystem Safety Requirements*, not read in either domain
