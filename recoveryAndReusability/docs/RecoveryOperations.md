[Home](../README.md) > Recovery Operations

# Recovery Operations

## Contents

- [Overview](#overview)
- [Safing](#safing)
- [Downrange recovery](#downrange-recovery)
- [Transport back](#transport-back)
- [The operation nobody budgets](#the-operation-nobody-budgets)
- [Recovery reliability](#recovery-reliability)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Everything between touchdown and the stage arriving at the refurbishment facility. It is a fixed cost per flight, it is invisible in a vehicle design review, and on a downrange recovery it is a fleet of ships.

---

## Safing

The first thing that happens to a landed stage, and it is a hazardous operation on hardware that has just been through a flight.

**Residual propellant** is the immediate problem. A stage lands with what is left of the reserve, and it has to be vented, drained or made inert before anybody approaches. On a cryogenic stage that is a boil-off and a purge; on a hypergolic one it is a [toxic operation](../../groundSystemsAndOperations/docs/HazardousOperations.md) with breathing apparatus.

**Stored pressure.** Every pressurant bottle on the stage is still at pressure, and a composite overwrapped vessel that has been through an entry and a landing is one whose condition is not yet established.

**Unfired ordnance**, if any remains. Separation charges that did not fire are more dangerous than ones that did.

**And the approach itself**, on a vehicle that has just landed on legs whose lock state is not confirmed and which may be on a slope.

**Safing is a written procedure with hold points**, and it is the first thing that has to be designed for a reusable vehicle rather than assumed.

---

## Downrange recovery

A downrange landing puts the stage on a ship, which is a different operational problem from a landing at the launch site.

**The ship has to be on station**, which means it left days earlier and it has weather constraints of its own. A recovery ship's sea state limit is a launch commit criterion, and it is one that is easy to forget when writing the criteria list.

**The stage has to be secured to the deck** before the ship moves, on a vessel that is itself moving.

**And the transit back takes days.** That is a fixed contribution to turnaround, and on a fleet flying frequently it is a fleet-of-ships problem rather than a one-ship problem.

**A return to the launch site removes all of that** at the cost of roughly double the reserve propellant. See [RecoveryHardware](RecoveryHardware.md). **The trade is a fixed operational cost against a per-flight performance cost**, and which wins depends on how often the vehicle flies.

---

## Transport back

**A landed stage is a structure in a load case it was not designed for**, exactly as a new one is on the way out. See [IntegrationAndProcessing](../../groundSystemsAndOperations/docs/IntegrationAndProcessing.md).

**And it is a structure whose condition is unknown**, which is the difference. Transporting a new stage risks damaging a known article; transporting a flown one risks confusing the inspection that follows, because damage found later cannot be attributed between the flight and the road.

**Instrument the transport**, for that reason as much as for the loads.

---

## The operation nobody budgets

Recovery operations are a fixed cost per flight and they do not appear anywhere in a vehicle mass or performance budget. That makes them easy to leave out of a reuse case entirely.

They are in [ReuseEconomics](ReuseEconomics.md) as a recurring term alongside refurbishment, and **the two together are what set the break-even flight count**: `n = 1 / (1 - refurbishment - recovery)`. A recovery operation costing a tenth of a stage moves the break-even as surely as a refurbishment costing the same.

**The failure mode is a reuse case that counts the stage and forgets the ships.**

---

## Recovery reliability

Recovery does not always succeed, and the arithmetic of that is worse than it looks.

A stage recovered with probability `p` flies a geometric number of times before it is lost, so twenty planned flights at 97 per cent recovery become **15.2 expected: a shortfall of 24 per cent from a 3 per cent loss rate.**

**The losses compound over the fleet life rather than applying once**, which is why recovery reliability is worth far more than its rate suggests, and why the early flights of a recovery programme are worth flying conservatively even at a performance cost.

It also means the effective flight count is an expectation rather than a plan, and a fleet sized on the plan is a fleet that shrinks.

---

## Design rules of thumb

- **Design safing before the first landing**, not after it.
- **Put the recovery ship sea state in the launch commit criteria.**
- **Count the transit in the turnaround.** It is days and it is fixed.
- **Instrument the transport back**, so found damage can be attributed.
- **Put recovery operations in the break-even**, not just refurbishment.
- **Treat recovery reliability as worth several times its rate.**

---

## Failure modes

**A reuse case that counts the stage and forgets the ships.** The break-even moves.

**A launch commit criteria list with no recovery ship constraint.** The ship becomes the surprise.

**Unattributable damage after transport.** Instrument it or lose the inspection.

**An effective flight count taken from the plan.** Losses compound.

**Safing improvised on the pad after the first landing.** The worst conditions available for a procedure.

---

## References

- [HazardousOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md), for the safing conventions
- [IntegrationAndProcessing](../../groundSystemsAndOperations/docs/IntegrationAndProcessing.md), for the transport load case
- [ReuseEconomics](ReuseEconomics.md), for where the recovery cost lands
