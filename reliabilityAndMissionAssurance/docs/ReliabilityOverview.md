[Home](../README.md) > Reliability Overview

# Reliability Overview

## Contents

- [Overview](#overview)
- [What this domain found](#what-this-domain-found)
- [Two directions of analysis](#two-directions-of-analysis)
- [What is computed and what is not](#what-is-computed-and-what-is-not)
- [Document index](#document-index)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

Reliability engineering is what turns a collection of good hardware into a vehicle that works. It covers the analytical methods, the design responses, and the programmatic systems that make them stick.

**It is deliberately unglamorous and it is where most launch failures are actually decided.**

---

## What this domain found

**The two FMECA rankings disagree, and the disagreement is the finding.** A risk priority number multiplies detection in alongside severity and occurrence, which pushes a rare and detectable catastrophe below a common and hidden nuisance. On the worked table two catastrophic modes are buried by the detection column. **Criticality, which is severity times occurrence without detection, is the ranking that finds them.** See [FMECA](FMECA.md).

**The single point failures carry the whole fault tree.** Five of them account for essentially all of the top event probability, and the two carefully redundant pairs contribute a thousandth of it. **That is what a fault tree is for**: a probability can be got from a spreadsheet, and a list of the combinations that on their own lose the mission cannot. See [FaultTreeAnalysis](FaultTreeAnalysis.md).

**The importance ranking is not the probability ranking.** An event in a single point cut set has an importance near one whatever its probability. The redundant avionics units sit three orders of magnitude below a single valve on importance and an order of magnitude above it on probability.

**A third of the reliability budget has nothing behind it.** The rollup closes and two subsystems carrying 35 per cent of the allowed unreliability are supported by an allocation and an assumption. **A reliability number without a stated basis is a wish**, and the basis audit is what says which ones are. See [ReliabilityAllocation](ReliabilityAllocation.md).

**And separating two units beats adding a third by a factor of six.** Common cause is 93 per cent of a dual redundant set's failure probability at a ten per cent beta, and it does not fall at all when units are added. **Redundancy that shares a failure cause is not redundancy**, and the arithmetic says so numerically rather than as an aphorism. See [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md).

**On the worked case the dual set fails its requirement on common cause alone.** The ideal arithmetic clears it and the real one does not, which is exactly the error the beta factor exists to catch, and the fix is a layout and sourcing decision with no hardware added.

---

## Two directions of analysis

Every reliability programme runs both, and they find different things.

**A FMECA works up from the parts.** It is exhaustive rather than clever, and what it finds that nothing else does is the failure mode nobody thought about. Its weakness is that it is one component at a time and it cannot see a combination.

**A fault tree works down from the failure.** It sees combinations, which is the whole point, and its output is the minimal cut sets rather than the number. Its weakness is that it only contains the failures somebody put in it.

**Neither replaces the other and a programme that runs one is missing what the other finds.**

---

## What is computed and what is not

| Built | Why nothing else does it |
|---|---|
| `FMECA` | The ranking disagreement, and the action check |
| `FaultTree` | Cut sets, which is the only way single point failures are found |
| `ReliabilityBudget` | Series rollup with a basis audit |
| `RedundancyAnalysis` | Common cause, which every other domain here assumes away |

| Not built | Why not |
|---|---|
| Component failure rate prediction | A handbook prediction has a documented history of being optimistic |
| Quality, configuration management, problem reporting | Process, and documented as such |
| Human error probability | Very large uncertainty; the design responses are documented instead |
| The FTS reliability case | [rangeSafetyAndFTS](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md) owns it |
| Derating curves | Component specific, and they belong with the components |
| Bayesian updating | Needs a prior this repository has no basis for |

---

## Document index

| Document | Covers |
|---|---|
| [FMECA](FMECA.md) | The table, both rankings, and why the disagreement matters |
| [FaultTreeAnalysis](FaultTreeAnalysis.md) | Cut sets, importance, common cause, quantification |
| [ReliabilityAllocation](ReliabilityAllocation.md) | Series rollup, allocation, the basis audit, item count |
| [RedundancyAndFaultTolerance](RedundancyAndFaultTolerance.md) | Beta factors, coverage, fail-operational and fail-safe |
| [SinglePointFailures](SinglePointFailures.md) | Identification, acceptance rationale, tracking |
| [DeratingAndMargins](DeratingAndMargins.md) | Derating policy, and where margin actually protects |
| [QualityAndProcessControl](QualityAndProcessControl.md) | Inspection, first article, SPC, escapes |
| [ConfigurationManagement](ConfigurationManagement.md) | Baselines, change control, as-built traceability |
| [ProblemReporting](ProblemReporting.md) | Nonconformance, MRB, corrective action, trending |
| [HumanFactors](HumanFactors.md) | Procedure design, error-proofing, the failure mode that is a person |
| [StandardsIndex](StandardsIndex.md) | What governs this, and why the list is thin |
| [ValidationReferences](ValidationReferences.md) | No external anchor, and why the conclusions survive it |

---

## Design rules of thumb

- **A reliability number without a stated basis is a wish.** Say where it came from.
- **Redundancy that shares a failure cause is not redundancy.**
- **Most failures are not random.** They are design escapes, process escapes, or human error.
- **The FMECA is only useful if somebody acts on it.** An unactioned finding is worse than none.
- **Single point failures should be listed, argued and accepted deliberately**, never discovered.
- **Read an ordinal product as a sort, not a measurement.**

---

## Failure modes

**A FMECA ranked only by risk priority number.** It buries the detectable catastrophes.

**A fault tree run for its number.** The cut sets are the output.

**A reliability budget with no basis column.** A list of numbers rather than a budget.

**A redundancy gain computed without common cause.** Off by the ratio of two terms.

**A third unit added to a common cause dominated set.** It buys single digits.

**An unactioned finding.** A real hazard converted into a document.

---

## References

- [FlightTerminationSystems](../../rangeSafetyAndFTS/docs/FlightTerminationSystems.md), for the reliability case this domain does not own
- [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), for what a reliability claim is built on
- [ValidationReferences](ValidationReferences.md)
