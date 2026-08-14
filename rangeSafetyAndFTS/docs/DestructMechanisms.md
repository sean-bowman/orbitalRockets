[Home](../README.md) > Destruct Mechanisms

# Destruct Mechanisms

## Contents

- [Overview](#overview)
- [What termination is for](#what-termination-is-for)
- [Linear shaped charge](#linear-shaped-charge)
- [Thrust termination](#thrust-termination)
- [What termination achieves](#what-termination-achieves)
- [What it does not](#what-it-does-not)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Terminating a launch vehicle is not blowing it up. It is a specific action with a specific objective, and understanding the objective explains the hardware.

---

## What termination is for

**To stop the vehicle adding energy in the wrong direction**, and to do it in a way that puts the debris where the [risk analysis](PublicRiskAnalysis.md) said it would go.

That is the whole objective. It is not to destroy the vehicle, not to consume the propellant, and not to make the debris small.

**A vehicle that has been terminated is a ballistic object**, and everything after termination is [where the pieces land](TrajectoryLimitsAndIIP.md).

---

## Linear shaped charge

The usual mechanism on a liquid vehicle.

A linear shaped charge runs along the tankage and, when initiated, cuts the tank open along its length. **The objective is to spill the propellant and end the thrust**, not to fragment the vehicle.

Two consequences follow and both matter to the risk analysis.

**The propellants mix and may deflagrate rather than detonate.** That is why the [TNT equivalence](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md) tables exist and why they are far below one hundred per cent for most combinations: an aboveground unconfined spill is a poor explosive.

**And the vehicle breaks up into large pieces rather than small ones.** A cut tank produces structure sections, engines and an upper stage, not a cloud. **That is better for the risk analysis than fragmentation would be**, because large pieces have a higher ballistic coefficient, fall closer to the impact point and disperse less. See [DebrisAndBlast](DebrisAndBlast.md).

---

## Thrust termination

The alternative on a solid motor, where there is no propellant to spill.

A solid motor cannot be shut down, so termination means **destroying the pressure vessel's ability to sustain chamber pressure**: cutting the case open, or blowing the nozzle or the forward closure off, so the motor vents rather than thrusts.

**It does not stop the burn.** The propellant continues to burn at a much lower pressure, and the motor becomes a large object producing a small and unpredictable thrust.

**That is why solid motors are a harder range safety problem** than liquids: the termination is less complete, the residual behaviour is less predictable, and there is no equivalent of simply spilling the propellant.

---

## What termination achieves

Stated positively, because the list is short and specific.

**It ends the thrust**, which stops the impact point running further downrange.

**It puts the break-up at a known time**, which is what makes the debris footprint computable at all.

**And it does both fast enough to matter**, which is the reaction time budget in [TrajectoryLimitsAndIIP](TrajectoryLimitsAndIIP.md).

---

## What it does not

The list that matters more.

**It does not eliminate the debris.** Everything that was on the vehicle still comes down, and the risk analysis is about where.

**It does not prevent a ground impact.** Terminating over a populated area terminates over a populated area.

**It does not act instantly**, and the delay between the decision and the end of thrust is a real term in the destruct line margin.

**And it does not make the vehicle safe to approach.** A terminated vehicle on the ground is unfired ordnance, residual propellant and stored pressure. See [HazardAreasAndClearing](HazardAreasAndClearing.md) and the safing conventions in [groundSystemsAndOperations](../../groundSystemsAndOperations/docs/HazardousOperations.md).

---

## Design rules of thumb

- **Terminate to end thrust, not to destroy the vehicle.**
- **Prefer large pieces to small ones.** They disperse less.
- **Expect a solid motor termination to be incomplete.** It vents rather than stops.
- **Count the delay from decision to thrust end** in the destruct line margin.
- **Plan the ground safing of a terminated vehicle** before it is needed.

---

## Failure modes

**Termination equated with destruction.** The objective is thrust, not fragments.

**Fragmentation assumed to be safer.** Small pieces disperse further.

**A solid motor assumed to stop.** It vents and keeps burning.

**Termination delay omitted from the destruct margin.** It is a real distance.

**A terminated vehicle approached as wreckage.** It is unfired ordnance.

---

## References

- [Pyrotechnics](../../mechanismsAndSeparation/docs/Pyrotechnics.md), for the initiation train
- [HazardZonesAndSiting](../../groundSystemsAndOperations/docs/HazardZonesAndSiting.md), for the explosive equivalence of a spill
- [DebrisAndBlast](DebrisAndBlast.md)
