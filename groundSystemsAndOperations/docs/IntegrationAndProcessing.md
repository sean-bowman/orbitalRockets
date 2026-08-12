[Home](../README.md) > Integration and Processing

# Integration and Processing

## Contents

- [Overview](#overview)
- [The flow](#the-flow)
- [Horizontal against vertical](#horizontal-against-vertical)
- [Transport](#transport)
- [Erection and mate](#erection-and-mate)
- [What integration catches](#what-integration-catches)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Everything that happens to a vehicle between arriving at the site and standing on the pad. It is where the schedule actually goes, and the design decisions in it are mostly about where work is done rather than how.

---

## The flow

The shape is common even where the details differ.

**Receive and inspect.** Transport damage is real and it is found here or in flight.

**Stage integration.** Structures joined, systems connected, harnesses routed and tested.

**Vehicle integration.** Stages mated, interfaces verified end to end.

**Payload integration**, usually last and usually at a different cleanliness level.

**Transport to the pad.**

**Erection and mate to the launch mount.**

**Pad testing**, which is the first time the vehicle and the ground system exist together.

**And the count.**

**Everything that can be verified before the vehicle arrives at the pad should be**, because pad time is the most expensive time on the programme and the most constrained.

---

## Horizontal against vertical

The decision that shapes the whole facility.

**Horizontal integration** works at ground level. No high bay, no crane of consequence, better access, cheaper buildings, and a transporter-erector that does the lifting once. The vehicle has to take a load case it will never see again, and every joint has to be checked in an orientation it will not fly in.

**Vertical integration** builds in the flight orientation. No extra load case, gravity loads are the flight ones, and payload access is natural for anything that needs it upright. It needs a tall building, a big crane and work at height, all of which are expensive and slow.

**The trade is facility cost against vehicle structure and access**, and cadence pushes it: horizontal integration is faster to repeat, which is why high-cadence programmes tend that way and why heavy vehicles with sensitive payloads tend the other.

---

## Transport

**A vehicle on a road is a structure in a load case nobody flies.** Vibration, shock over joints, cornering, braking, and a support arrangement completely unlike the flight one.

**It is instrumented**, because an unmeasured transport is an unbounded one, and the record is what closes the question of whether anything was overloaded.

**Environmental control travels with it** on anything sensitive: temperature, humidity, cleanliness.

**And the route is a design constraint**, which is not a joke. Bridge clearances and turning radii have set stage diameters on real programmes, and the constraint is upstream of almost everything in [vehicleArchitecture](../../vehicleArchitecture/).

---

## Erection and mate

**Erection is the largest single handling operation on the programme**, and it is the one where a vehicle is most likely to be damaged by the ground.

**Wind limits during erection are usually tighter than launch limits**, because the vehicle is being handled rather than restrained. That is a schedule constraint that surprises people, and it is a launch commit criterion for the erection day rather than for launch day.

**Mate to the mount has to be repeatable and reversible**, because a demate is what a scrub with a vehicle problem needs.

---

## What integration catches

The findings that repeat, which is the useful list.

**Interfaces that two teams specified differently.** The classic, and the reason integration exists as a phase.

**Harness routing that fits on paper and not in the vehicle.** See [electricalPower](../../electricalPower/docs/HarnessDesign.md), which argues that harness mass is counted rather than fractioned for the same reason.

**Access that was assumed and is not there.** A component reachable in CAD and not with a person attached to the hand.

**Cleanliness violations**, which are found late and cost the most to fix late.

**And the things transport did.** Which is why receipt inspection is a real step rather than a formality.

---

## Design rules of thumb

- **Verify everything possible before the pad.** Pad time is the constrained resource.
- **Pick horizontal or vertical from cadence and payload**, not from tradition.
- **Instrument transport.** An unmeasured transport is unbounded.
- **Check the route before fixing the diameter.**
- **Expect erection wind limits to be tighter than launch limits.**
- **Make the mate reversible.** A demate is what a scrub needs.

---

## Failure modes

**Work deferred to the pad.** The most expensive place to do it.

**Transport uninstrumented.** No way to close the overload question.

**A stage diameter fixed before the route survey.** Bridges do not move.

**Erection scheduled without wind limits.** Tighter than launch, and forgotten.

**A mate designed one way.** A scrub needs it to come apart.

---

## References

- [HarnessDesign](../../electricalPower/docs/HarnessDesign.md), for what routing costs
- [vehicleArchitecture](../../vehicleArchitecture/), for where the diameter constraint lands
- [environmentsAndLoads](../../environmentsAndLoads/), for the transport load case
- [manufacturingAndAssembly](../../manufacturingAndAssembly/), for what happens upstream of receipt
