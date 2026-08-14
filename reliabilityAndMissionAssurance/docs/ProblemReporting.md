[Home](../README.md) > Problem Reporting

# Problem Reporting

## Contents

- [Overview](#overview)
- [The flow](#the-flow)
- [Disposition](#disposition)
- [Root cause](#root-cause)
- [Corrective action](#corrective-action)
- [Trending](#trending)
- [The reporting culture](#the-reporting-culture)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

What happens when something is wrong. It is the feedback loop of the whole quality system, and it is where a programme either learns or does not.

---

## The flow

**A nonconformance is raised** when hardware does not meet its drawing, its specification or its procedure. Anyone should be able to raise one and raising one should be cheap.

**A material review board dispositions it**: use as is, rework, repair, or scrap.

**A root cause is established**, for the ones that warrant it.

**A corrective action is taken and verified**, and the verification is the part that gets skipped.

**And the nonconformance is closed**, with the record kept.

**The failure mode of the flow is that it becomes a route to a signature rather than a route to a fix.** A programme where every nonconformance is dispositioned use-as-is and closed within a day has a working process and no learning.

---

## Disposition

Four outcomes, and the first is the one that needs the most scrutiny.

**Use as is** accepts the hardware as it is, which means accepting that the requirement it missed was not needed. **That is a statement about the requirement**, and if it is used often the requirement was wrong and should be changed rather than waived repeatedly. **A recurring use-as-is is a requirement problem in disguise.**

**Rework** returns the hardware to the drawing, using an approved process. It is the clean outcome.

**Repair** returns it to a usable state without meeting the drawing, which creates a permanent deviation and a [configuration](ConfigurationManagement.md) item.

**Scrap** removes it. Expensive and unambiguous.

**The disposition is a technical decision and it is made under schedule pressure by people who want the hardware**, which is why the board is a board rather than a person.

---

## Root cause

The step most often truncated.

**A cause that is a person is not a root cause.** "Operator error" ends the investigation exactly where it should start: why was the error possible, why was it not caught, and what about the design or the procedure permitted it. See [HumanFactors](HumanFactors.md).

**A cause that is a component is usually not one either.** "The valve failed" invites a valve replacement, and the useful questions are why that valve, why now, and what else shares the cause.

**And the shared cause is the point.** A finding that stops at one component misses the [common cause](RedundancyAndFaultTolerance.md): the lot, the process setting, the environment, the drawing. **The single most valuable question in a root cause investigation is what else was made the same way.**

**Not everything warrants a full investigation**, and pretending otherwise produces investigations nobody finishes. The judgement about which ones do is itself worth making explicitly rather than by default.

---

## Corrective action

Two halves, and the second is what makes it corrective.

**Fix the hardware**, which the disposition already covers.

**Fix the cause**, which is what stops the next one. **A corrective action that only addresses the article in front of you is a repair with a form attached.**

**And verify it.** An action closed without evidence that it worked is an assumption recorded as a fact, which is the same failure as an unactioned [FMECA](FMECA.md) finding wearing different clothes.

**The verification is usually the recurrence rate**, which means it takes time and the action cannot honestly be closed on the day it is taken. Programmes close them anyway, and that is where the trending below stops working.

---

## Trending

The part that finds what individual investigations cannot.

**A single nonconformance is an event. A pattern of them is information**, and the pattern is invisible from inside any one of them.

**Trend by cause, by process, by supplier and by article**, and the useful signals are the ones that are individually unremarkable: three different components from one supplier, four unrelated defects on one shift, a nonconformance rate rising slowly on a process nobody has changed.

**That is the same idea as a [control chart](QualityAndProcessControl.md)** applied to findings rather than to parameters, and it has the same requirement: somebody has to read it.

**And it only works if the records are consistent.** A nonconformance system where the cause field is free text is a system that cannot be trended, which is a design decision made when the form was written.

---

## The reporting culture

The thing that decides whether any of the above happens.

**Raising a nonconformance has to be cheap and safe.** A system where raising one is slow, or where the person who raises one is treated as the person who caused it, produces a low nonconformance rate and no information at all.

**A low nonconformance rate is not obviously good.** It means either the process is excellent or the reporting is suppressed, and those look identical on a chart. **The discriminator is whether the ones that are raised are trivial or serious**: a healthy system reports plenty of small things.

**And the first flight of a programme is where this is tested**, because that is where the schedule pressure is highest and the incentive to absorb a problem is strongest.

---

## Design rules of thumb

- **Make raising a nonconformance cheap and safe.**
- **Treat a recurring use-as-is as a requirement problem.**
- **Never stop a root cause at a person or a component.**
- **Ask what else was made the same way.** That is the common cause question.
- **Verify corrective actions before closing them.**
- **Design the form so the records can be trended.**
- **Be suspicious of a low nonconformance rate.**

---

## Failure modes

**A nonconformance route that ends in a signature.** Process without learning.

**Recurring use-as-is dispositions.** A wrong requirement being waived repeatedly.

**Operator error recorded as a root cause.** The investigation stopped at the start.

**A corrective action closed on the day it was taken.** No verification is possible yet.

**Free text cause fields.** Untrendable by construction.

**A low nonconformance rate reported as a success.** It may be suppression.

---

## References

- [QualityAndProcessControl](QualityAndProcessControl.md), for the escapes this responds to
- [ConfigurationManagement](ConfigurationManagement.md), for what a repair creates
- [HumanFactors](HumanFactors.md), for why a person is not a root cause
- [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md), for the common cause question
