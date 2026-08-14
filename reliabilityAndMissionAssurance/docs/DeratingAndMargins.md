[Home](../README.md) > Derating and Margins

# Derating and Margins

## Contents

- [Overview](#overview)
- [What derating does](#what-derating-does)
- [Where margin protects](#where-margin-protects)
- [Where it does not](#where-it-does-not)
- [A derating policy](#a-derating-policy)
- [Margin stacking](#margin-stacking)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Margin is the usual answer to uncertainty and it is a good one within limits. This document is about the limits.

---

## What derating does

**Derating is operating a component below its rated capability**, and it works by moving the component away from the part of its failure distribution that is steep.

A capacitor at half its rated voltage, a resistor at half its rated power, a bolt at half its proof load: in each case a small change in the applied stress no longer produces a large change in the failure probability, and the component's life is dominated by something other than the applied stress.

**The mechanism is the shape of the distribution rather than the margin itself**, which is why derating is worth so much at first and so little after: the first factor of two moves the component off the steep part and the second moves it along a flat one.

**The derating curves themselves are component specific** and they live with the components: [electricalPower](../../electricalPower/) for electronics, [aerospaceMaterials](../../aerospaceMaterials/docs/AllowablesAndStatistics.md) for structural allowables. This domain does not reproduce them.

---

## Where margin protects

Three cases, and they are the ones worth spending on.

**Against a distribution.** Where the applied load and the capability both vary, margin buys separation between two distributions and the benefit is real and computable. That is the structural case and [aerospaceStructures](../../aerospaceStructures/) owns it.

**Against a known unknown.** A load that has not been measured yet, an environment that will be characterised later, a property that has a scatter factor on it. Margin here is a placeholder for information, and **it should shrink as the information arrives.**

**And against degradation.** A component that wears, corrodes or fatigues starts with margin and spends it, and the margin is what buys the life. See [LifeTrackingAndLimits](../../recoveryAndReusability/docs/LifeTrackingAndLimits.md).

---

## Where it does not

The cases where margin is spent and buys nothing, and they are the ones that cause failures.

**Against a design error.** A component sized against the wrong load case has margin against a load it will not see. **Margin does not protect against being wrong about what the problem is**, and most launch failures are design escapes rather than overstressed parts.

**Against a process escape.** A weld with a defect in it has whatever strength the defect leaves, and the margin computed on the drawing is not there. That is a [manufacturing](../../manufacturingAndAssembly/docs/ProcessQualification.md) and [inspection](../../manufacturingAndAssembly/docs/InspectionAndNDE.md) problem, not a margin one.

**Against a single point failure.** A valve with a large margin on its actuator still fails if the actuator fails, and the margin says nothing about the failure rate. See [SinglePointFailures](SinglePointFailures.md).

**And against a common cause.** Two units with generous margin, sharing a power feed, fail together at the feed. Margin is per-component and common cause is not. See [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md).

**Three of those four are the dominant failure classes on a launch vehicle**, which is the uncomfortable conclusion: **most failures are not random and margin defends mainly against the random ones.**

---

## A derating policy

What one contains, and why it should be written once rather than argued per component.

**A table of derating factors by component class and by parameter**: voltage, current, power, temperature, and for structure the stress ratio.

**A statement of what the ratings are relative to**, which is where policies quietly differ: rated at what temperature, in what environment, for what life.

**An exceptions process**, because there will be exceptions and an unwritten process produces undocumented ones.

**And a review point**, because a policy applied at the component level and never rolled up produces a system with unknown total margin.

**The value of the policy is consistency rather than the numbers.** A programme where every component is derated by a documented rule is a programme where the margin is knowable; one where each is argued separately is not.

---

## Margin stacking

The problem a policy creates and nobody owns.

**Margin applied at every level multiplies.** A load case with margin, a component derated against it, a structure with a factor of safety, and a qualification tested above that: the total can be several times what anybody intended, and **nobody has the whole number** because each factor was applied by a different person for a defensible reason.

**The consequences are real.** Mass that buys nothing, a design that fails a requirement it would otherwise meet, and a qualification test that overtests a component into a failure mode it will never see in flight.

**The fix is a margin accounting**, kept the way a [mass budget](../../vehicleArchitecture/docs/MassChain.md) is kept: one place where every factor is written down, with what it protects against.

**And the same discipline as the [basis audit](ReliabilityAllocation.md)**: a factor with no stated reason is a factor nobody can remove later.

---

## Design rules of thumb

- **Derate to move off the steep part of the distribution**, and stop.
- **Write the policy once.** Consistency is worth more than the values.
- **Make margin against a known unknown shrink** as the information arrives.
- **Do not expect margin to protect against a design or process escape.**
- **Keep a margin accounting.** Factors multiply and nobody holds the total.
- **State what each factor protects against.** Otherwise it is permanent.

---

## Failure modes

**Margin as a substitute for understanding the load case.** It defends against the wrong thing.

**Margin used against a single point failure.** It says nothing about the rate.

**Margin per component against a common cause.** Common cause is not per component.

**Factors applied at four levels and never rolled up.** Mass for nothing.

**A qualification level derived from stacked margins.** Overtesting into an irrelevant failure mode.

**A factor with no stated reason.** Permanent by default.

---

## References

- [aerospaceStructures](../../aerospaceStructures/), for the structural margin case
- [AllowablesAndStatistics](../../aerospaceMaterials/docs/AllowablesAndStatistics.md), for what an allowable already contains
- [ProcessQualification](../../manufacturingAndAssembly/docs/ProcessQualification.md), for the escapes margin does not cover
- [MassChain](../../vehicleArchitecture/docs/MassChain.md), for what stacked margin costs
