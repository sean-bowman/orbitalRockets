[Home](../README.md) > Process Qualification

# Process Qualification

## Contents

- [Overview](#overview)
- [What qualification establishes](#what-qualification-establishes)
- [Coupons](#coupons)
- [First article inspection](#first-article-inspection)
- [Production control](#production-control)
- [What counts as a change](#what-counts-as-a-change)
- [Where the sub-domains carry it](#where-the-sub-domains-carry-it)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

**A process is not qualified until a coupon made the same way has been destroyed.** That is the domain ethos, and it means something specific: the evidence is destructive, it is on material made by the actual process, and there is no substitute for it.

---

## What qualification establishes

Three separate things that get collapsed into one word.

**That the process produces the properties the design assumed.** Established by destructive testing of coupons.

**That the process produces them repeatably.** Established by testing enough coupons, from enough lots, to see the scatter. See [AllowablesAndStatistics](../../aerospaceMaterials/docs/AllowablesAndStatistics.md), where the sample size question is worked properly.

**And that a specific article was made by that process.** Established by the production control record rather than by any test, and it is the one most often weak.

**The third is where qualification actually fails.** A qualified process and an unqualified execution of it produce an article with a certificate and unknown properties.

---

## Coupons

**Made the same way** is the whole requirement and it is more demanding than it sounds.

Same material lot, same process parameters, same thickness, same orientation, same post-processing, and where possible the same run. A coupon machined from a different plate and heat treated in a different furnace load establishes something about the process in general and very little about the article.

**Witness coupons made alongside the article** are the strong version, and they cost material and furnace space. **They are the only evidence that ties a specific article to a specific test.**

**On additive that becomes acute**, because the properties depend on build location, orientation and thermal history within the build. [additiveLPBF](../../aerospaceMaterials/additiveLPBF/) works that through in detail and it is the sub-domain with the most demanding coupon strategy in the repository.

---

## First article inspection

The full dimensional and process verification of the first part off a tool or a process, and it is a different thing from a qualification.

**Qualification says the process can make the part.** First article says this tool, this programme and this setup did.

**It is repeated after any change that could affect the result**, which is a longer list than people expect and is the subject of the next section.

**And it is the moment a design's manufacturability is actually established.** A first article that needs three deviations is a design that was not makeable, and the deviations are the record of it.

---

## Production control

What holds the process between qualification and the last article.

**Parameter recording.** The actual machine settings for the actual run, kept.

**Statistical process control** on the parameters that matter, so a drift is visible before it becomes a nonconformance. The point of a control chart is that it fires on a trend rather than on a limit.

**Periodic requalification coupons**, because a process drifts in ways parameter recording does not capture: a consumable ages, a fixture wears, an operator leaves.

**And configuration control**, so that what was made is knowable afterwards. **A part with no traceable process record is a part with no qualification**, whatever the process qualification says.

---

## What counts as a change

The list that decides how often a programme requalifies, and the entries that surprise people are the ones not on the drawing.

**Material lot**, on anything where lot-to-lot variation is real, which is most composites and some metals.

**Consumable lot**, including filler wire, adhesive, prepreg and powder.

**Machine**, even a nominally identical one. See the two-tool problem in [ToolingAndFixturing](ToolingAndFixturing.md).

**Operator**, on a manual process, which is the honest reason automation is pursued as much as rate is.

**Parameters outside the qualified range**, and those ranges are narrower than people assume: a thickness change or a position change can each fall outside a [welding](WeldingAndJoining.md) procedure.

**And a supplier**, which is the largest of them and is [SupplyChainAndMakeBuy](SupplyChainAndMakeBuy.md).

---

## Where the sub-domains carry it

This document is the cross-cutting view. The process-specific qualification content sits with the process.

| Sub-domain | Carries |
|---|---|
| [additiveLPBF](../../aerospaceMaterials/additiveLPBF/) | The most detailed qualification treatment here: powder lots, build location, witness coupons |
| [spinCasting](../../aerospaceMaterials/spinCasting/) | Casting qualification and inspection |
| [castingProcesses](../../aerospaceMaterials/castingProcesses/) | Tolerance, allowance and first article |
| [extrusionHoning](../../aerospaceMaterials/extrusionHoning/) | Process qualification for abrasive flow |
| [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/) | The campaign philosophy this reflects |

---

## Design rules of thumb

- **Make witness coupons alongside the article.** They are the only tie between test and part.
- **Establish what counts as a change before the first change happens.**
- **Chart the parameters that matter**, so drift fires before nonconformance does.
- **Requalify periodically.** Processes drift in ways parameters do not show.
- **Read the first article deviations as a design finding**, not a shop problem.
- **Keep the record.** A part without one is unqualified whatever the process is.

---

## Failure modes

**Coupons from a different lot or furnace load.** Evidence about the process, not the part.

**A qualified process, an unqualified execution.** A certificate and unknown properties.

**A parameter change assumed inside the range.** The ranges are narrow.

**A new machine assumed identical.** Two populations.

**First article deviations treated as shop problems.** They are design findings.

**No traceable record.** No qualification, whatever the paperwork says.

---

## References

- [AllowablesAndStatistics](../../aerospaceMaterials/docs/AllowablesAndStatistics.md), for the sample size question
- [additiveLPBF](../../aerospaceMaterials/additiveLPBF/), for the most demanding coupon strategy here
- [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), for the campaign philosophy
- [InspectionAndNDE](InspectionAndNDE.md)
