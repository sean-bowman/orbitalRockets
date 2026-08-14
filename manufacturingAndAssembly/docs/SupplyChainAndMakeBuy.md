[Home](../README.md) > Supply Chain and Make-Buy

# Supply Chain and Make-Buy

## Contents

- [Overview](#overview)
- [The make-buy decision](#the-make-buy-decision)
- [What buying actually buys](#what-buying-actually-buys)
- [Supplier qualification](#supplier-qualification)
- [Lead time](#lead-time)
- [Obsolescence](#obsolescence)
- [Counterfeit and traceability](#counterfeit-and-traceability)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Every part is made or bought, and the decision is usually framed as cost when it is really about control, lead time and the shape of the learning curve.

---

## The make-buy decision

Four axes, and cost is the one that moves least.

**Control.** A made part can be changed on a decision and a bought one on a negotiation. On anything expected to change, which is most of a first vehicle, that difference dominates.

**Lead time.** A made part is limited by your capacity and a bought one by somebody else's queue, and their queue is invisible until it is a problem.

**Capability.** Some processes are not worth owning at any volume, and some are not available to buy at any price.

**And the learning curve.** A made part learns at the rate of its labour content; **a bought part barely learns at all**, because it is a purchase and the supplier's learning accrues to the supplier. See [RateAndLearning](RateAndLearning.md), where a raw material learning rate of 0.98 sits against 0.80 for manual assembly.

**That last one is the axis people miss**, and it means a vehicle built largely from bought hardware has a flatter cost curve than one built from labour, whatever the programme plan assumes.

---

## What buying actually buys

Worth stating plainly, because a bought part is often treated as a solved problem.

**It buys the capability and not the responsibility.** A supplier's process problem is still your flight failure, and the [qualification](ProcessQualification.md) obligation does not transfer with the purchase order.

**It buys a longer feedback loop.** A finding in your shop is a conversation; a finding at a supplier is a corrective action, a schedule and a commercial position.

**And it buys somebody else's priorities.** A supplier with a larger customer has a queue you are in rather than a queue you own.

---

## Supplier qualification

The same three questions as a [process qualification](ProcessQualification.md), asked of an organisation.

**Can they make it.** Established by a first article and by coupons made the same way, on their material and their machines. **A supplier qualification that does not include destructive testing of their output is a survey of their quality system**, which is a different and lesser thing.

**Can they make it repeatably.** Established over time and by their own production control record, which means you have to be able to read it.

**And will they tell you when something changes.** This is the one that is contractual rather than technical, and it is the one that fails. A supplier who changes a sub-tier source or a process parameter without notification has invalidated a qualification you still believe in.

---

## Lead time

**Lead time is the constraint far more often than cost**, and long lead items are a design input.

Forgings, castings, large plate, qualified fasteners, valves and anything with a bespoke process behind it run to many months. **Those months sit in series with everything downstream**, exactly as [tooling](ToolingAndFixturing.md) does.

**The design consequence is that a long lead item has to be committed before the design that uses it is finished**, which means committing to a size and an interface early and holding them. A programme that changes a forging envelope late has bought the lead time twice.

**And a single-source long lead item is a single point of schedule failure**, which is a different risk from a single point of technical failure and is managed differently.

---

## Obsolescence

The slow problem, and it is worse on a long programme than a short one.

**Electronic parts obsolete fastest**, and a flight computer qualified on a part that is no longer made is a requalification waiting to happen. See [avionicsAndGNC](../../avionicsAndGNC/).

**Materials and processes obsolete too**, more slowly and less visibly: an alloy temper that stops being rolled, a coating that is regulated out, an adhesive whose formulation changes.

**A lifetime buy is the usual answer** and it converts an obsolescence risk into a storage and shelf life problem, which is real: adhesives, prepregs and some elastomers have finite shelf lives, and a lifetime buy of a shelf-limited item is a slow write-off.

---

## Counterfeit and traceability

**Traceability is the mitigation and there is no other one.**

A counterfeit part is one whose provenance is false, and no amount of incoming inspection reliably distinguishes a good counterfeit from a genuine part. **Incoming inspection catches the bad counterfeits**, which is worth doing and is not a solution.

**So the control is the supply chain rather than the part**: buy from the manufacturer or a franchised distributor, keep the certification chain unbroken, and treat a broker purchase as an exception with its own justification and testing.

**The certification chain is what a traceability record is**, and it is only as good as its weakest link. A record that stops at a distributor is a record that establishes the distributor.

---

## Design rules of thumb

- **Decide make-buy on control and lead time, not on unit cost.**
- **Remember that a bought part barely learns.** It flattens the cost curve.
- **Destroy something a supplier made** before qualifying them.
- **Contract the notification of change.** It is the failure that survives a good qualification.
- **Commit long lead envelopes early and hold them.**
- **Check shelf life before a lifetime buy.**
- **Keep the certification chain unbroken.** It is the only counterfeit control that works.

---

## Failure modes

**Make-buy decided on unit cost.** The axes that matter are control and lead time.

**A learning curve assumed on bought hardware.** It barely learns.

**A supplier qualified by quality system survey.** Nothing was destroyed.

**A change made at a supplier without notification.** A qualification you still believe in.

**A forging envelope changed late.** The lead time is bought twice.

**A lifetime buy of a shelf-limited item.** A slow write-off.

**A broker purchase treated as routine.** The certification chain is broken.

---

## References

- [ProcessQualification](ProcessQualification.md), which this applies to an organisation
- [RateAndLearning](RateAndLearning.md), for the learning curve consequence
- [ProcessRouteSelection](../../aerospaceMaterials/docs/ProcessRouteSelection.md), which computes route lead time
- AS9100 and AS5553, quality management and counterfeit avoidance, not read
