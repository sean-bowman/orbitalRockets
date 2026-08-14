[Home](../README.md) > Hazard Areas and Clearing

# Hazard Areas and Clearing

## Contents

- [Overview](#overview)
- [The three hazard areas](#the-three-hazard-areas)
- [Ships](#ships)
- [Aircraft](#aircraft)
- [Clearing and re-entry](#clearing-and-re-entry)
- [Where the ground calculation lives](#where-the-ground-calculation-lives)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Everything that has to be empty, and for how long. It is the operational face of the [risk analysis](PublicRiskAnalysis.md) and it is what a range actually enforces on the day.

---

## The three hazard areas

**The ground hazard area** around the pad, sized by explosive equivalence and Hopkinson-Cranz scaling. That calculation lives in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md) and is not repeated here.

**The launch hazard area** downrange, covering where debris from an early failure would land. It is a sea and air exclusion rather than a land one on most sites, because that is what a coastal launch has downrange.

**And the impact hazard areas** for planned events: a spent stage, a fairing, a jettisoned interstage. **Those are not failures**, they are scheduled arrivals of hardware at known places, and they are cleared like any other.

**The third is the one that surprises people.** A nominal launch drops several objects in the ocean by design, and every one of them has a cleared area and a notice attached.

---

## Ships

The exclusion nobody can enforce directly.

**A ship in a hazard area is a hazard area with a ship in it**, and the range has no authority to move it. The tools are a published notice to mariners, surveillance on the day, and a hold if something is inside.

**A shipping lane is not empty ocean** and the [risk analysis](PublicRiskAnalysis.md) treats it as a low but non-zero population density. In the worked case the downrange ocean carries 82 per cent of the debris and 1 per cent of the risk, and that 1 per cent is ships.

**The practical consequence is that a hold for a ship is a routine launch commit criterion**, and it belongs in the [countdown](../../groundSystemsAndOperations/docs/LaunchOperations.md) rather than in the safety analysis.

---

## Aircraft

Treated separately by the regulation, and the criterion is different in kind.

**14 CFR 450.101 excludes people in aircraft from the collective casualty expectation** and instead requires that the aircraft hazard areas keep the **probability of impact with debris capable of causing a casualty below 1e-6.**

**That is a probability of impact rather than a probability of casualty**, which is a stricter and simpler test: an aircraft struck by debris is assumed to be lost rather than assessed for casualties.

**The mechanism is airspace closure**, coordinated with the air navigation service provider, and it is a real cost: a closure across a busy airspace displaces traffic and there is a limit to how often and how long it can be done.

**That is one of the reasons launch cadence is an airspace question as well as a range question**, and it is a constraint that grows rather than shrinks as launch rate rises.

---

## Clearing and re-entry

The operational half.

**Clearing takes real time and it is on the critical path.** Nothing hazardous starts until the account of people closes, which is why the pad clear is the first task in the worked [countdown](../../groundSystemsAndOperations/docs/LaunchOperations.md).

**Re-entry after a scrub is the harder direction**, with a loaded and pressurised vehicle and possibly armed ordnance. It has its own criteria and they should be written before the scrub rather than during it. See [HazardousOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md).

**And a terminated or failed vehicle creates an unplanned hazard area** wherever it came down, which has to be established, secured and worked with the same conventions as the pad: unfired ordnance, residual propellant, stored pressure. See [DestructMechanisms](DestructMechanisms.md).

---

## Where the ground calculation lives

Stated so the boundary is explicit.

**Quantity-distance siting, explosive equivalence and blast overpressure are all in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md)**, read from DESR 6055.09 and asserted against the register there. The ground hazard areas in this domain are that calculation applied to the same vehicle.

**What this domain adds is the flight half**: where the debris goes once the vehicle has left, which is [TrajectoryLimitsAndIIP](TrajectoryLimitsAndIIP.md) and [DebrisAndBlast](DebrisAndBlast.md).

---

## Design rules of thumb

- **Clear the planned impact areas too.** A nominal launch drops hardware by design.
- **Put the ship surveillance hold in the launch commit criteria.**
- **Treat aircraft as a probability of impact**, not a probability of casualty.
- **Budget clearing time on the critical path.** It is real and it is first.
- **Write the re-entry criteria before the scrub.**
- **Plan for an unplanned hazard area** wherever a failed vehicle lands.

---

## Failure modes

**Planned impact areas forgotten.** Nominal hardware arrives in cleared water.

**A shipping lane treated as empty ocean.** It is a low but non-zero density.

**Aircraft assessed for casualties.** The regulation uses impact probability.

**Airspace closure assumed available.** It is a finite and shrinking resource at rate.

**Re-entry improvised after a scrub.** The worst conditions for a decision.

---

## References

- [HazardZonesAndSiting](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md), which owns the ground calculation
- [HazardousOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md), for clearing and re-entry
- [PublicRiskAnalysis](PublicRiskAnalysis.md), which sizes the areas
- 14 CFR 450.101, for the aircraft criterion
