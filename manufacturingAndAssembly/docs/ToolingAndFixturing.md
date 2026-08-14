[Home](../README.md) > Tooling and Fixturing

# Tooling and Fixturing

## Contents

- [Overview](#overview)
- [Tooling is a design decision](#tooling-is-a-design-decision)
- [Cost and lead time](#cost-and-lead-time)
- [Accuracy](#accuracy)
- [Thermal effects](#thermal-effects)
- [Fixturing against distortion](#fixturing-against-distortion)
- [Tooling at rate](#tooling-at-rate)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

**Tooling cost and lead time are design decisions made by someone who was not thinking about tooling.** That is the domain ethos and this is the document behind it.

---

## Tooling is a design decision

A tool exists because a design demanded a shape, a tolerance or an operation. **Every one of those demands was made by a designer, usually without a tooling number attached**, and by the time the number exists the design is fixed.

Three specific cases where a small design change removes a large tool.

**A shape that needs a die.** A gentle change to a radius or a draft angle can move a part from a die-formed process to a brake-formed one.

**A tolerance that needs a fixture.** A [tolerance stack](AssemblyAndIntegration.md) that closes without a locating fixture removes a tool, a setup and a contributor at once.

**And a feature reachable from one side.** Two-sided access doubles the tooling and adds a datum transfer.

**None of those is visible from the drawing**, which is why the tooling conversation has to happen before the drawing is released rather than after.

---

## Cost and lead time

**Lead time is usually the constraint rather than cost**, and it is the one that surprises programmes.

A large form tool or an autoclave tool is months, and those months sit in series with everything downstream: no tool, no first article, no [qualification](ProcessQualification.md), no production. **Tooling lead time is on the critical path of a programme far more often than any part is.**

**The cost is a non-recurring number amortised over the production run**, which means the right tool for one article and the right tool for fifty are different tools. A soft tool that makes ten parts and a hard tool that makes a thousand are both correct answers to different questions, and choosing the hard tool for a ten-part programme is a common and expensive error.

**And a tool is itself a manufactured article** with its own tolerance, inspection and qualification, which is easy to forget when it appears in a schedule as a single line.

---

## Accuracy

**A tool cannot be more accurate than the machine that made it**, and the part cannot be more accurate than the tool.

That chain is why tooling accuracy usually has to be a factor better than part accuracy, conventionally four to ten times, and why an accurate part on a large scale is expensive: the tool has to be measured on the same [laser tracker](InspectionAndNDE.md) as the part, in the same conditions, and tied to the same coordinate frame.

**Tool wear moves the answer slowly**, which is worse than moving it quickly because nothing triggers. A tool that is checked on a schedule catches it; a tool checked when somebody suspects something does not.

---

## Thermal effects

The error source that is invisible because everything looks fine.

**A shop is not at a controlled temperature and a launch vehicle sized article is large.** A 3.7 m aluminium barrel moves about 0.08 mm per degree, so a five degree difference between the morning and the afternoon is a real fraction of the assembly tolerance.

**Tool and part expand differently** unless they are the same material, and on a composite tool that difference is the whole tooling material decision. See [CompositesManufacturing](CompositesManufacturing.md).

**And a measurement is taken at a temperature.** A dimension recorded without a temperature is a dimension with an unknown error in it, which is why the convention is to report at 20 C and correct.

**Thermal growth is the fifth largest contributor in the worked stack**, at three per cent, which sounds negligible until you notice it costs nothing to remove by measuring at a controlled temperature.

---

## Fixturing against distortion

A fixture that holds a part during welding reacts the shrinkage, which sounds like a fix and is a trade.

**Restraining distortion converts it into residual stress.** The part comes out of the fixture straighter and with more stress in it, and that stress reappears the next time material is removed. See [MachiningAndFabrication](MachiningAndFabrication.md) and [WeldingAndJoining](WeldingAndJoining.md).

**So a fixture is the third choice**, after minimising heat input and balancing the welding sequence, and it should be understood as a decision to move the problem downstream rather than to solve it.

---

## Tooling at rate

**A tool adequate for one article is a bottleneck for fifty.**

A single tool means a single station, and the [line capacity](RateAndLearning.md) is the slowest station. A second tool is capacity, and it costs a second non-recurring number plus a second qualification plus the ongoing question of whether parts from the two tools are interchangeable.

**Two tools that are not identical produce two populations**, and a [tolerance stack](AssemblyAndIntegration.md) built on one of them is wrong about the other. That is a real failure mode and it is why multi-tool programmes measure tool-to-tool variation as a first-class quantity.

---

## Design rules of thumb

- **Have the tooling conversation before the drawing is released.**
- **Cost lead time, not just money.** It is usually the constraint.
- **Match the tool to the run length.** A hard tool for ten parts is waste.
- **Make the tool a factor better than the part**, and measure it the same way.
- **Check tools on a schedule.** Wear moves the answer slowly.
- **Control the measurement temperature.** It costs nothing.
- **Treat a fixture as moving distortion, not removing it.**

---

## Failure modes

**A tool number that arrives after the design freezes.** Nothing can be changed.

**A hard tool for a short run.** Non-recurring cost with nothing to amortise over.

**Tool lead time discovered in the schedule review.** It is in series with everything.

**A tool at part accuracy.** The part will be worse.

**An uncontrolled measurement temperature.** A free error left in.

**Two nominally identical tools, never compared.** Two populations and one stack.

---

## References

- [AssemblyAndIntegration](AssemblyAndIntegration.md), which owns the tolerance stack
- [RateAndLearning](RateAndLearning.md), for tooling as a bottleneck
- [CompositesManufacturing](CompositesManufacturing.md), for the expansion match
- [InspectionAndNDE](InspectionAndNDE.md), for how a tool is measured
