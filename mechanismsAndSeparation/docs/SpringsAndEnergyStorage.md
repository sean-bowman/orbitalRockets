[Home](../README.md) > Springs and Energy Storage

# Springs and Energy Storage

## Contents

- [Overview](#overview)
- [The energy budget](#the-energy-budget)
- [The momentum split](#the-momentum-split)
- [Tolerance is the design variable](#tolerance-is-the-design-variable)
- [Matching against multiplying](#matching-against-multiplying)
- [Spring redundancy](#spring-redundancy)
- [Storage effects](#storage-effects)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

A separation spring is the simplest device in this domain and it drives the two results that are hardest to fix. This document is about what the energy buys and what the tolerance costs.

---

## The energy budget

```
E = 0.5 k x^2   per spring
```

Everything downstream is that number times the count. A separation system has an energy budget the way a stage has a delta-V budget, and it is spent on velocity, on overcoming whatever resists separation, and on nothing else useful.

**Resistances to subtract before the velocity is computed**: connector separation force, umbilical drag, residual friction in the guide pins, and any part of the joint that has not fully released. None of those is modelled in this library and all of them are real, so the computed velocity is an upper bound.

---

## The momentum split

Momentum is conserved, so the energy divides in inverse proportion to mass:

```
v_rel = sqrt(2 E (1/m1 + 1/m2))
```

The lighter body takes most of the velocity **and most of the energy**. On the reference case a 1800 kg upper stage leaves at 0.370 m/s and a 6000 kg lower stage at 0.111 m/s, and the upper stage carries 77 per cent of the energy.

That is why a separation system on a small upper stage is easier than the same requirement on a large one: the mass ratio is doing the work.

---

## Tolerance is the design variable

The energy sets the velocity. **The tolerance sets the tipoff**, and tipoff is what causes recontact.

A commercial compression spring is typically supplied to about ten per cent on rate. On the reference case that gives 0.396 degrees per second in the deterministic worst case and 0.140 statistically at four springs.

Tightening the tolerance to two per cent cuts the tipoff by a factor of five, and it costs a selection process rather than a redesign. **Tolerance is the cheapest lever in the whole separation system** and it is the one least often specified.

---

## Matching against multiplying

Two ways to attack tipoff and only one of them works on the bound.

**Multiplying the springs** improves the statistical case as one over the root of the count and leaves the deterministic worst case exactly where it was, because half high and half low produces the same net moment however many there are.

**Matching the springs** attacks the bound directly. Measure the rates, pair the high ones against the high ones across the bolt circle, and the imbalance cancels by construction rather than by chance.

The statistical argument is also weakest exactly where it is most often invoked: **springs from a single production lot are correlated**, not independent. A set bought together and installed without measurement has bought the statistical case on paper and specified the worst one in reality.

---

## Spring redundancy

NASA-STD-5017B draws a distinction here that is easy to miss.

**Redundant springs in parallel** with one failed get safety factors of 1.0 in the margin equation, which is a large relief and is deliberate: showing a positive margin after a spring failure would otherwise force an excessive margin before it.

**A single spring designed to tolerate partial failure**, such as a broken coil in a guided helical spring that still functions with reduced performance, does **not** get those factors. The standard is explicit, and the reasoning is that the mass penalty of the second case is much smaller than adding a genuinely redundant spring, so the relief is not warranted.

Reading that wrong is a factor of three on the variable torque factor in the wrong direction.

---

## Storage effects

A compression spring held at working deflection for months relaxes, in the same way a bolt does. The load at deflection falls, so the energy falls, so the separation velocity falls.

This library does not model spring relaxation, and it does model [preload relaxation](SeparationSystems.md) in the clamp band, which is the same physics in a different component. That inconsistency is deliberate rather than accidental: the clamp band relaxation has a clear failure mode and a preload to compare against, and a separation spring's relaxation shows up as a slightly lower velocity, which the recontact margin already covers.

**It is still worth measuring** rather than assuming, and it is a documented gap rather than a modelled effect.

---

## Worked numbers

| Quantity | Value |
|---|---|
| Spring stiffness | 8000 N/m |
| Stroke | 100 mm |
| Energy per spring | 40 J |
| Springs | 4 |
| Total energy | 160 J |
| Relative velocity | 0.481 m/s |
| Energy to the lighter body | 77 % |
| Tipoff at 10 % tolerance, worst case | 0.396 deg/s |
| Tipoff at 2 % tolerance, worst case | 0.079 deg/s |

---

## Design rules of thumb

- **Specify the rate tolerance**, and treat it as a design variable rather than a supplier detail.
- **Match in opposing pairs** if the bound matters, which it usually does.
- **Subtract the resistances** before believing the velocity. Connectors and umbilicals are real.
- **Do not claim one-spring-out relief** for a single spring with a tolerant design.
- **Measure the springs after storage** if the stack has sat.

---

## Failure modes

**Rate tolerance unspecified.** The cheapest lever in the system, left on the table.

**Spring count treated as a bound improvement.** It improves the expectation only.

**Lot correlation ignored.** Undermines the statistical case that justified the count.

**One-spring-out factors misapplied.** A factor of three in the wrong direction.

**Separation resistances not subtracted.** The computed velocity is an upper bound.

---

## References

- NASA-STD-5017B, table 1 and appendix A section A.2.5 on spring redundancy
- [SeparationSystems](SeparationSystems.md), where the energy becomes a velocity and a tipoff
- Conley, *Space Vehicle Mechanisms: Elements of Successful Design*
