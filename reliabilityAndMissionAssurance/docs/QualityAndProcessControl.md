[Home](../README.md) > Quality and Process Control

# Quality and Process Control

## Contents

- [Overview](#overview)
- [Most failures are escapes](#most-failures-are-escapes)
- [The three escape types](#the-three-escape-types)
- [Statistical process control](#statistical-process-control)
- [Inspection is not quality](#inspection-is-not-quality)
- [What a quality system is for](#what-a-quality-system-is-for)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

**Most failures are not random. They are design escapes, process escapes, or human error.** That sentence is the domain ethos and this document is about the middle one.

---

## Most failures are escapes

The uncomfortable framing that reorients a reliability programme.

**A random failure is a good part failing.** It happens, and it is what a failure rate describes and what [derating](DeratingAndMargins.md) and [redundancy](RedundancyAndFaultTolerance.md) defend against.

**An escape is a bad part passing.** A component that was never going to work, released into the vehicle because nothing caught it, and no failure rate describes it because it is not a rate at all: it is a specific thing that went wrong once.

**The defences are completely different.** Redundancy defends against random failures and does very little against escapes, because an escape frequently affects both units: a bad lot, a bad process setting, a misread drawing. **That is a common cause with a name.**

**And the arithmetic of a reliability budget describes only the random half**, which is the honest limitation of everything in [ReliabilityAllocation](ReliabilityAllocation.md).

---

## The three escape types

**A design escape** is a requirement that was wrong, a load case that was missed, an interface that two teams specified differently. It is present in every article, it is invisible to inspection because the part matches the drawing, and it is found by review, by analysis and by test. **It is the class that dominates first flights.**

**A process escape** is a part that does not match its drawing or its process specification: a weld with a defect, a torque never applied, a coating out of spec. It affects some articles rather than all, and it is what inspection and process control exist for.

**A human error** is an action taken wrongly: a connector on the wrong pin, a step skipped, a value transposed. See [HumanFactors](HumanFactors.md), where the point is that it is a design failure rather than a person failure.

**The proportions shift through a programme.** Design escapes dominate early, process escapes dominate at rate, and human error is constant and always present.

---

## Statistical process control

The instrument that catches a process escape before it becomes a part.

**A control chart fires on a trend, not on a limit.** That is the whole idea and it is what separates it from inspection: a process drifting toward its tolerance is still producing conforming parts, and the chart says so before the first nonconforming one appears.

**Which parameters to chart is the design question.** Charting everything produces noise that nobody reads; charting the parameters that actually move the outcome produces a signal. **The choice comes from the process qualification**, where the sensitivity was established. See [ProcessQualification](../../manufacturingAndAssembly/docs/ProcessQualification.md).

**Charting an output rather than a parameter is the common error.** A dimension is an outcome and by the time it moves the process already has. The parameter that produced it moved first.

**And a chart nobody reads is worse than none**, for the same reason an unactioned [FMECA](FMECA.md) finding is: it converts a real signal into a record that the signal was collected.

---

## Inspection is not quality

The distinction that costs programmes the most.

**Inspection sorts good parts from bad ones.** It does not make good parts, it does not reduce the escape rate, and it is limited by what the technique can reach and detect. See [InspectionAndNDE](../../manufacturingAndAssembly/docs/InspectionAndNDE.md), where the probability of detection curve makes the limit explicit: **there is no flaw size an inspection is guaranteed to find.**

**Process control makes good parts.** It is upstream, it is cheaper, and it addresses the cause rather than the symptom.

**A programme that responds to an escape by adding an inspection has treated the symptom.** The inspection catches some fraction of the next occurrence and the process still produces them. **The correct response is to find why the process produced it**, which is [ProblemReporting](ProblemReporting.md).

**Inspection is still necessary**, because process control is imperfect and some escapes have no upstream signal. The failure is treating it as sufficient.

---

## What a quality system is for

Stripped of the certification language, three things.

**To make what was intended repeatable.** A qualified process, a controlled configuration, a recorded execution.

**To make a deviation visible.** A nonconformance raised rather than absorbed, a trend charted rather than averaged out.

**And to make the record survive the programme.** Which lot, which operator, which parameters, which disposition. **A part with no traceable record is an unqualified part** whatever its paperwork says, and that record is what an investigation runs on years later.

**None of those is a calculation**, which is why this domain documents them rather than modelling them, and why a quality system that is audited for compliance rather than used for those three things has become the paperwork it is accused of being.

---

## Design rules of thumb

- **Separate random failures from escapes.** Different defences entirely.
- **Expect design escapes early and process escapes at rate.**
- **Chart parameters, not outputs.** The output moves last.
- **Choose what to chart from the process qualification.**
- **Respond to an escape upstream**, not with another inspection.
- **Keep the record.** It is what an investigation runs on.

---

## Failure modes

**A reliability programme that only addresses random failures.** It covers the smaller half.

**Redundancy relied on against escapes.** A bad lot affects both units.

**An output charted instead of a parameter.** The signal arrives late.

**An inspection added in response to an escape.** The symptom, not the cause.

**A control chart nobody reads.** A record that the signal was collected.

**A traceability record that stops at a distributor.** It establishes the distributor.

---

## References

- [ProcessQualification](../../manufacturingAndAssembly/docs/ProcessQualification.md), which is where the parameters come from
- [InspectionAndNDE](../../manufacturingAndAssembly/docs/InspectionAndNDE.md), for what inspection can establish
- [ProblemReporting](ProblemReporting.md), for what happens after an escape
- AS9100, aerospace quality management, not read
