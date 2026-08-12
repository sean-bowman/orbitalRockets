[Home](../README.md) > Flight Computers

# Flight Computers

## Contents

- [Overview](#overview)
- [Redundancy is easy and management is not](#redundancy-is-easy-and-management-is-not)
- [The schemes](#the-schemes)
- [Fault containment](#fault-containment)
- [Radiation](#radiation)
- [Watchdogs](#watchdogs)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The flight computer runs the guidance, the control law and the sequence. It is one of the few components on a vehicle where the answer to a reliability requirement is genuinely to have more than one, and that answer creates a harder problem than the one it solved.

---

## Redundancy is easy and management is not

Fitting three computers is a procurement decision. **Deciding which one is right is the engineering.**

A redundant set has to detect a disagreement, identify which member is wrong, exclude it, and continue, all within a control cycle, and every one of those steps can itself fail.

The domain ethos states it: **redundancy management is harder than redundancy.**

---

## The schemes

**Dual redundant** detects a disagreement and cannot resolve it. Two computers that disagree tell you something is wrong and not which one. That is useful for a fail-safe system, where the safe action is to stop, and useless for a launch vehicle in ascent, where there is no safe stop.

**Triple modular redundancy** votes. Two agreeing outvote one disagreeing, and the system continues correctly through one failure. It is the classical answer and it costs three of everything plus a voter, and **the voter is a single point of failure** unless it too is replicated.

**Dual-dual** pairs two self-checking pairs. Each pair detects its own failure and drops out, and the other pair continues. It is cheaper than triple in some respects and it moves the detection problem inside the pair.

**Self-checking with a dissimilar backup** runs a simpler, independently developed system alongside the primary, on the argument that the two will not share a design fault. It costs a second development and it is the only scheme that addresses **common mode** failure at all.

---

## Fault containment

The reason a scheme can fail despite having enough boxes.

**A common mode failure defeats replication entirely.** Three identical computers running identical software hit the same software fault at the same instant, and voting between them produces a unanimous wrong answer. Replication protects against random failure and not against design failure.

**A shared resource is a shared failure.** Three computers on one power bus, one data bus or one clock have a single point of failure regardless of their number, and the bus is the usual one. See [DataBusesAndNetworks](DataBusesAndNetworks.md).

**Fault containment regions** are the design response: draw the boundaries first, then check that no fault crosses one. That is an architecture activity done early, and it is much harder to retrofit than to plan.

---

## Radiation

A launch vehicle spends minutes rather than years in the environment, which changes the problem relative to a spacecraft.

**Total dose is not the constraint** on an ascent. Accumulated damage needs time.

**Single event effects are.** A single particle can flip a bit, latch up a device or upset a state machine, and the probability over minutes is small and not negligible, particularly through the South Atlantic Anomaly.

The responses are error detection and correction on memory, a watchdog that recovers from an upset state, current limiting that survives a latch-up, and part selection.

**Part selection is a specialist activity and it is not modelled here.** It is named because a decision to use a commercial processor is a decision about single event rate, and that should be a decision rather than a default.

---

## Watchdogs

A watchdog resets a computer that has stopped behaving. Two things about it are worth knowing and both are about what it does not do.

**A watchdog detects a stopped computer, not a wrong one.** Software that is looping happily and computing nonsense pets the watchdog on schedule.

**A reset costs the flight time it takes.** A computer that resets and recovers in 200 ms has missed 200 ms of control on an unstable vehicle, and whether that is survivable is a control question rather than an avionics one.

So a watchdog is a last resort that turns a hang into a transient, and the transient has to be sized.

---

## Design rules of thumb

- **Decide the redundancy management before the redundancy.** It is the hard half.
- **Draw fault containment regions early.** Retrofitting them is much harder.
- **Check the shared resources.** Three computers on one bus is one computer.
- **Treat common mode separately.** Replication does not address it.
- **Size the watchdog recovery against the control loop.** A reset is a control outage.

---

## Failure modes

**Dual redundancy in a system with no safe stop.** Detects and cannot resolve.

**A voter that is not itself redundant.** A single point of failure in a redundant system.

**Three identical units running identical software.** Unanimous and wrong.

**A shared bus, power or clock.** Defeats the replication count.

**A watchdog relied on to catch wrong answers.** It catches stopped ones.

---

## References

- Wie, *Space Vehicle Dynamics and Control*
- NASA-HDBK-1002 and the NASA software engineering standards, not read here
- [DataBusesAndNetworks](DataBusesAndNetworks.md), for the shared resource
- [SoftwareAssurance](SoftwareAssurance.md), for the common mode argument
