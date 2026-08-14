[Home](../README.md) > Autonomous FTS

# Autonomous FTS

## Contents

- [Overview](#overview)
- [What changes and what does not](#what-changes-and-what-does-not)
- [The architecture](#the-architecture)
- [Rule sets](#rule-sets)
- [Verification](#verification)
- [What it buys](#what-it-buys)
- [What it costs](#what-it-costs)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

An autonomous flight termination system moves the decision onboard. **It does not remove the requirement to justify it**, and understanding exactly what it changes is the whole of this document.

---

## What changes and what does not

**What changes** is who decides and how fast. A command system needs a ground station tracking the vehicle, a person or an algorithm evaluating limits, a transmitter, and a link that survives the vehicle's attitude and plume. An autonomous system has the state vector already and evaluates the rules onboard in milliseconds.

**What does not change** is the reliability requirement, the risk criteria, or the burden of showing that the rules are correct. **14 CFR 450.145 applies to an autonomous system exactly as it applies to a command system**, and the 0.999 at 95 per cent confidence still cannot be demonstrated by test.

**What gets harder** is the verification, and that is the trade. The reliability of a radio link is an engineering question with decades of practice behind it. **The correctness of a rule set is a software assurance question**, and this repository has already said what that costs: see [SoftwareAssurance](../../avionicsAndGNC/docs/SoftwareAssurance.md), where the point is that software fails by design and never at random, so three copies of it vote unanimously for the wrong answer.

---

## The architecture

**Redundant navigation**, usually GPS and inertial, because the rules are evaluated on a state vector and a wrong state vector is a wrong decision. See [SensorsAndNavigation](../../avionicsAndGNC/docs/SensorsAndNavigation.md).

**Redundant processors** running the rule set, with a voting scheme.

**The same ordnance train** as a command system, and the same [safe and arm](FlightTerminationSystems.md).

**And no ground segment at all** in the flight path, which is the operational point.

**The processors are the new failure mode.** They are subject to the [common mode problem](../../avionicsAndGNC/docs/FlightComputers.md) that identical redundancy cannot address, and a rule set error is present in every copy simultaneously.

---

## Rule sets

The rules are geodetic and state-based conditions evaluated continuously, and they replace what a ground operator would have judged.

**Boundary conditions.** The impact point outside a permitted region, expressed as a polygon rather than a line.

**State conditions.** Velocity, attitude rate or acceleration outside envelopes that indicate loss of control.

**Health conditions.** Loss of navigation, loss of processor agreement, or a self-test failure.

**And time conditions.** A gate not reached by a given time, which catches the underperforming vehicle.

**The rules are mission specific and they are data rather than code**, which is deliberate: a mission change should be a data change with its own verification rather than a software change with a full requalification. **That distinction is only real if the data is verified to the same standard as the code**, which is where programmes get into trouble.

---

## Verification

The hard part, and it is a different hard part from a command system.

**The rules have to be correct**, which means they terminate the vehicle in every case the risk analysis assumed they would and in no case they did not. That is a claim about coverage of a state space, and the state space is large.

**Simulation is the primary evidence**, run across dispersions and failure injections. **It has the limitation every simulation has**: it contains what somebody modelled, and the flight contains everything. See [AvionicsTesting](../../avionicsAndGNC/docs/AvionicsTesting.md).

**Hardware in the loop closes some of it**, by running the real processors on the real rules against a simulated vehicle.

**And the end-to-end test still applies**: the ordnance path has to be proven on the flight article regardless of what decides to fire it.

**What cannot be verified is the case nobody thought of**, which is the same limitation a command system has with a ground operator and is at least visible there.

---

## What it buys

**Reaction time**, which matters because the [impact point accelerates](TrajectoryLimitsAndIIP.md). An onboard decision in milliseconds against a ground loop in seconds is worth hundreds of kilometres of destruct line margin late in the ascent.

**Operational independence.** No downrange tracking assets, no ships, no ground station chain along the azimuth. That is the cost argument and it is a large one.

**And consistency.** A rule set decides the same way every time, which a person under pressure does not.

---

## What it costs

**A software assurance programme** for something in the highest consequence class on the vehicle.

**A navigation solution good enough to decide on**, with its own redundancy and its own failure modes.

**And the loss of a human judgement that could have handled a case the rules did not anticipate.** That cuts both ways: the operator who would have caught the unanticipated case is also the operator who might have hesitated, and the regulation does not express a preference.

---

## Design rules of thumb

- **Treat the rule set as flight software**, at the highest assurance level.
- **Verify mission data to the standard the code is verified to.**
- **Expect the verification burden to move rather than shrink.**
- **Give the navigation solution its own redundancy.** A wrong state is a wrong decision.
- **Keep the end-to-end ordnance test.** Autonomy does not touch it.
- **Buy autonomy for reaction time and independence**, not because it looks simpler.

---

## Failure modes

**Autonomy assumed to reduce the requirement.** It does not; 450.145 applies unchanged.

**Mission data changed without verification.** A rule set error is in every copy at once.

**A rule set verified only in simulation.** It contains what somebody modelled.

**Navigation single string behind redundant processors.** A wrong state decides wrongly, twice.

**The end-to-end test dropped.** The ordnance path is unproven whatever decides to fire it.

---

## References

- [SoftwareAssurance](../../avionicsAndGNC/docs/SoftwareAssurance.md), for what verifying a rule set costs
- [FlightComputers](../../avionicsAndGNC/docs/FlightComputers.md), for the common mode problem
- [TrajectoryLimitsAndIIP](TrajectoryLimitsAndIIP.md), for why reaction time is worth so much
- 14 CFR 450.145, which applies to autonomous and command systems alike
