[Home](../README.md) > Power Overview

# Power Overview

## Contents

- [Overview](#overview)
- [What the domain found](#what-the-domain-found)
- [The architecture decisions](#the-architecture-decisions)
- [Document index](#document-index)
- [What this domain does not own](#what-this-domain-does-not-own)
- [Design rules of thumb](#design-rules-of-thumb)
- [References](#references)

---

## Overview

The electrical system touches every other subsystem, which means most of its inputs are somebody else's outputs. A heater duty cycle is a thermal design. A bus voltage is an architecture decision. A firing circuit belongs to mechanisms.

That is the shape of the domain and it is worth stating first, because it explains why so much of the work here is bookkeeping and boundary-drawing rather than analysis.

---

## What the domain found

Four results, each the opposite of the obvious one.

**The load that dominates is not the one anybody worries about.** The propellant heaters get the attention and avionics consumes twice their energy, because a 35 W load at full duty beats a 42 W load that cycles. Duty cycle multiplies and power does not.

**The heater is still the number worth checking, for a different reason.** Sweeping its duty cycle across a plausible range moves the mission energy by 44 per cent, on a load that is 24 per cent of it. **That swing is larger than the energy margin**, and it comes from an input this domain does not own. The ranking by energy and the ranking by uncertainty are different lists.

**Voltage drop chooses the wire gauge, not current.** Ampacity says 20 AWG and voltage drop says 14: six gauge steps and four times the copper. A harness sized on current would leave the load at 25.1 V on a 28 V bus. See [HarnessDesign](HarnessDesign.md).

**The nameplate battery is 1.85 times the energy delivered**, before any margin, because depth of discharge and cold multiply. Neither is a margin: they are the difference between what the label says and what the battery does.

---

## The architecture decisions

Three, and they are all made early and expensive to change late.

**Bus voltage.** Current falls with voltage and the allowed drop rises with it, so **copper falls roughly with the square of bus voltage**. On the reference harness a 12 V bus does not close at all, 28 V needs 14 AWG, and 100 V needs 24. That is the cleanest argument for a higher bus and it is why anything with a long harness runs above 28 V.

**Grounding topology.** Single point against multipoint has no scalar answer and it is settled before the harness is drawn. See [GroundingAndBonding](GroundingAndBonding.md).

**Distribution topology.** Centralised switching against distributed, which trades harness mass against box count and fault isolation. See [PowerDistribution](PowerDistribution.md).

---

## Document index

| Document | Covers |
|---|---|
| [BatteriesAndStorage](BatteriesAndStorage.md) | Chemistries, the two derations, rate against energy, safety |
| [PowerDistribution](PowerDistribution.md) | Buses, switching, protection, load shedding |
| [HarnessDesign](HarnessDesign.md) | Gauge from voltage drop, derating, mass counted rather than fractioned |
| [GroundingAndBonding](GroundingAndBonding.md) | Single point against multipoint, structure as return |
| [EMIAndEMC](EMIAndEMC.md) | Emissions and susceptibility, MIL-STD-461, and what is not modelled |
| [PyroCircuits](PyroCircuits.md) | Where the firing circuit lives, and why it is not here |
| [ValveAndActuatorDrive](ValveAndActuatorDrive.md) | Inrush, peak and hold, flyback, the hot coil |
| [PowerQuality](PowerQuality.md) | Transients, ripple, undervoltage, brownout |
| [ElectricalTesting](ElectricalTesting.md) | Continuity, insulation resistance, hipot, EMC test |
| [StandardsIndex](StandardsIndex.md) | The standards, and the ones not read |
| [ValidationReferences](ValidationReferences.md) | One exact anchor and three gaps |

---

## What this domain does not own

**The firing circuit.** `PyroCircuit` was planned for this library and deliberately not built, because `PyrotechnicInitiator` in [mechanismsAndSeparation](../../mechanismsAndSeparation/) already computes the firing current, the no-fire margin and the parallel-device arithmetic. This domain supplies the bus voltage and the harness resistance; that one decides whether the device fires. See [PyroCircuits](PyroCircuits.md).

**Grounding topology and EMI magnitudes.** Documented and not modelled. Single point against multipoint is a topology decision with no scalar answer, and emissions and susceptibility are measured against MIL-STD-461 rather than computed.

**Fault current and protection coordination.** Fusing and current limiting need a source impedance model this domain does not carry.

**Battery thermal runaway.** A safety analysis rather than an energy one, and it belongs with [thermalManagement](../../thermalManagement/) and [reliabilityAndMissionAssurance](../../reliabilityAndMissionAssurance/).

---

## Design rules of thumb

- **Size the wire on voltage drop**, then check ampacity, not the other way round.
- **Count the harness.** A fraction of dry mass never converges.
- **Size the battery cold.** The pad is the design case, not the flight.
- **Rank by uncertainty as well as by energy.** They are different lists.
- **Raise the bus if the harness is long.** Copper falls with the square of voltage.

---

## References

- [ValidationReferences](ValidationReferences.md), for the AWG anchor
- MIL-STD-461, *Requirements for the Control of Electromagnetic Interference*
- SAE AS50881, *Wiring Aerospace Vehicle*
- [fluidSystems](../../fluidSystems/), where the heater and valve loads come from
