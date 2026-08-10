[Home](../README.md) > Electrical Testing

# Electrical Testing

## Contents

- [Overview](#overview)
- [Continuity](#continuity)
- [Insulation resistance](#insulation-resistance)
- [Hipot](#hipot)
- [The order matters](#the-order-matters)
- [Functional and EMC](#functional-and-emc)
- [What testing does not catch](#what-testing-does-not-catch)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Harness testing is cheap, fast and catches a class of defect that is otherwise found during integration at a hundred times the cost. It is also routinely done in the wrong order.

---

## Continuity

Every conductor connects the two things it should and nothing else. Two halves, and the second is the one that gets skipped.

**Continuity**: pin A to pin B has a low resistance. Catches an open, a mis-crimp, a broken conductor.

**Isolation**: pin A to every other pin has a high resistance. Catches a short, a whisker, a mis-wire into the adjacent contact.

A harness tested only for continuity passes with two conductors swapped, provided each one connects to something.

**Measure the resistance rather than checking for a beep.** A crimp that is making contact through a small area has continuity and will fail on vibration, and the only warning is a resistance a few tens of milliohms higher than its neighbours. **The comparison across identical conductors is what finds it**, not the absolute value.

---

## Insulation resistance

A DC voltage, typically a few hundred volts, applied between a conductor and everything else, measuring leakage.

It catches damaged insulation, contamination and moisture ingress, and it catches them before they become a short.

**It is a trend measurement more than a pass or fail.** A harness whose insulation resistance has fallen by an order of magnitude between two tests has something wrong with it even if both readings pass, and the value is meaningless without the humidity and temperature at which it was taken.

---

## Hipot

A high potential, well above the working voltage, applied to prove the insulation withstands it.

Two things about it are worth knowing.

**It is a proof test and it is potentially damaging.** Hipot stresses the insulation, and repeated hipot testing degrades what it is testing. That argues for doing it once, at acceptance, at the specified voltage and no higher.

**It interacts with altitude.** The [Paschen](PowerDistribution.md) minimum means insulation adequate at sea level and in vacuum can break down at intermediate pressure, so a hipot at ambient does not qualify a harness for ascent. Testing at altitude is the real qualification and it is rarely done.

---

## The order matters

Continuity, then insulation resistance, then hipot, then functional.

**Continuity first** because a hipot on a mis-wired harness applies high voltage to something that was not meant to see it.

**Insulation resistance before hipot** because it is non-destructive and it finds the gross defects that would make the hipot a damaging event rather than a proof.

**Hipot before functional** because a hipot after installation risks the connected equipment, and disconnecting to hipot re-introduces the mating errors continuity was checking for.

Getting that order wrong is how a test programme damages the article it is qualifying.

---

## Functional and EMC

**Functional test** exercises the harness with the real loads. It catches interactions that a bench test does not: shared impedance coupling, inrush interactions, and grounding problems that only appear with the real return paths.

**EMC test** is covered in [EMIAndEMC](EMIAndEMC.md), including what it does and does not catch. The short version: it catches an emitter above the limit and a filter that was designed and not fitted, and it does not catch a configuration that was not tested.

---

## What testing does not catch

**An intermittent.** A crimp that opens under vibration and closes at rest passes every static test. The resistance comparison above is the only static hint, and vibration testing with continuity monitoring is the real answer.

**A defect introduced after test.** Every mate and de-mate is an opportunity, which is an argument for testing as late as possible and for minimising [connector count](HarnessDesign.md).

**A routing error.** A harness can be electrically perfect and routed against a sharp edge or through a hot zone, and no electrical test sees it. That is an inspection.

**A configuration not tested.** True of functional and EMC testing both.

---

## Design rules of thumb

- **Test isolation as well as continuity.** Continuity alone passes a swap.
- **Record resistances and compare across conductors.** The outlier is the bad crimp.
- **Treat insulation resistance as a trend.** One reading means little.
- **Hipot once, at acceptance, at the specified voltage.**
- **Keep the order.** Continuity, insulation, hipot, functional.
- **Test as late as practical.** Every mate afterwards is an opportunity.

---

## Failure modes

**Continuity checked and isolation not.** A swapped pair passes.

**A beep test instead of a resistance measurement.** The marginal crimp passes.

**Hipot before continuity.** High voltage applied to the wrong conductor.

**Repeated hipot.** Degrades the insulation it is proving.

**Hipot at ambient taken as qualification for ascent.** The Paschen range is not covered.

**An intermittent that passes every static test.** Needs vibration with continuity monitoring.

---

## References

- SAE AS50881, *Wiring Aerospace Vehicle*, for installation and test requirements, not read here
- [EMIAndEMC](EMIAndEMC.md)
- [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), for the campaign philosophy this follows
