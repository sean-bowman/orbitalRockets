[Home](../README.md) > Manufacturing Overview

# Manufacturing Overview

## Contents

- [Overview](#overview)
- [What this domain found](#what-this-domain-found)
- [Where the process physics lives](#where-the-process-physics-lives)
- [What is computed and what is not](#what-is-computed-and-what-is-not)
- [Document index](#document-index)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

How a design becomes hardware, at rate, repeatably. This domain covers the processes used to make launch vehicle structure, the tooling that holds it, the joining methods, and the inspection that establishes whether any of it worked.

**The process physics is not here and that is deliberate.** It lives in the ten process sub-domains under [aerospaceMaterials](../../aerospaceMaterials/). What stays here is the cross-cutting view: what a stack of tolerances does, what an inspection establishes, and what rate does to cost.

---

## What this domain found

**A three sigma statistical tolerance stack is no saving at all below about nine contributors.** The worst case is a hard bound, and a statistical stack at k sigma exceeds it whenever k is above the sum of tolerances divided by their quadrature sum, which for equal contributors is exactly the square root of the count. **On a six contributor stack the statistical method is worse than the arithmetic one**, which is the reverse of why it is used, and the check is one line. See [AssemblyAndIntegration](AssemblyAndIntegration.md).

**One dimension holds half the stack.** A contributor enters the worst case linearly and the statistical stack as its square, so the statistical ranking is far more concentrated. Tightening the dominant dimension moves the assembly and tightening any of the others moves almost nothing. And tightening it moves the problem to the next contributor rather than removing it.

**An inspection that cannot find a flaw smaller than the critical one establishes nothing.** At full wall a penetrant inspection of the worked tank is comfortable. Take the same weld to a thinner wall, where the critical flaw is 1.3 mm, and it misses 13 per cent of the flaws large enough to burst the tank. **That is a design conclusion rather than an inspection finding**, and it is the one discovered late, because the inspection procedure is written after the wall thickness is fixed. See [InspectionAndNDE](InspectionAndNDE.md).

**The cheapest method that clears the size requirement cannot be used on the material.** Magnetic particle clears at a third the cost of the alternatives and does nothing on an aluminium tank. **A ranking by detectable flaw size is not a ranking by usefulness**, and the column that decides the answer is the one saying what each method misses.

**Capacity is the slowest station and not the sum.** A five station line with 268 hours of total cycle time makes 27 units a year because one station takes 75 of them. Fixing it buys the gap to the next station and no more, which is the same arithmetic as a [turnaround driver](../../groundSystemsAndOperations/docs/LaunchOperations.md) and a [life limit](../../recoveryAndReusability/docs/LifeTrackingAndLimits.md). See [RateAndLearning](RateAndLearning.md).

**And a programme of twenty units has barely started down its learning curve.** At an 85 per cent rate the twentieth unit still costs half the first, and the cumulative average, which is the number a programme is judged on, is a quarter higher again. A cost estimate quoting the learned-out figure is quoting a number the programme will not reach.

---

## Where the process physics lives

Ten sub-domains under [aerospaceMaterials](../../aerospaceMaterials/), and they carry the equations.

| Sub-domain | Carries |
|---|---|
| [additiveLPBF](../../aerospaceMaterials/additiveLPBF/) | Laser powder bed process, qualification, powder lots |
| [additiveOther](../../aerospaceMaterials/additiveOther/) | DED, WAAM, EB-PBF, binder jet, cold spray |
| [castingProcesses](../../aerospaceMaterials/castingProcesses/) | Solidification, feeding, tolerance and allowance |
| [spinCasting](../../aerospaceMaterials/spinCasting/) | Centrifugal casting and inclusion migration |
| [wroughtMaterials](../../aerospaceMaterials/wroughtMaterials/) | Product form, temper and orientation |
| [formingProcesses](../../aerospaceMaterials/formingProcesses/) | Bend radius, springback, forming limits |
| [machiningProcesses](../../aerospaceMaterials/machiningProcesses/) | Tool life, chatter lobes, thin wall deflection |
| [joiningProcesses](../../aerospaceMaterials/joiningProcesses/) | Joining routes, pointing at Weld in fluidSystems |
| [postProcessing](../../aerospaceMaterials/postProcessing/) | Shot peen, plating, alpha case removal |
| [extrusionHoning](../../aerospaceMaterials/extrusionHoning/) | Abrasive flow machining |

**This domain does not duplicate any of them.** A second implementation of Taylor tool life or springback here would be the same equations with a different import path, and two of them drift.

---

## What is computed and what is not

| Built | Why nothing else does it |
|---|---|
| `ToleranceStack` | No other domain assembles anything |
| `InspectionCapability` | aerospaceMaterials computes the critical flaw; nothing asks whether it can be found |
| `ProductionRate` | vehicleArchitecture names the learning curve as a gap in its own cost document |

| Not built | Where it lives |
|---|---|
| Machining, forming, casting, joining physics | The ten sub-domains above |
| Weld joint efficiency and HAZ knockdown | [Weld](../../fluidSystems/fluidSystemsLibrary/docs/Welds.md) in fluidSystems |
| Buy-to-fly and route comparison | `ProcessComparison` in [aerospaceMaterials](../../aerospaceMaterials/docs/ProcessRouteSelection.md) |
| Critical flaw size | `DamageTolerance` in [aerospaceMaterials](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md) |
| Cost estimating relationships | Named as a gap in [vehicleArchitecture](../../vehicleArchitecture/docs/CostAndProducibility.md) |
| Supplier qualification and counterfeit control | A governance problem, documented rather than modelled |

---

## Document index

| Document | Covers |
|---|---|
| [MachiningAndFabrication](MachiningAndFabrication.md) | What machining costs, what it can hold, and when it is the wrong answer |
| [FormingAndSpinning](FormingAndSpinning.md) | Forming routes for a tank, springback, and why domes are spun |
| [WeldingAndJoining](WeldingAndJoining.md) | Process selection, distortion, and where the joint efficiency lives |
| [CompositesManufacturing](CompositesManufacturing.md) | Layup, cure, tooling, and the defect that inspection is for |
| [ToolingAndFixturing](ToolingAndFixturing.md) | Tooling as a design constraint, accuracy, thermal effects, lead time |
| [AssemblyAndIntegration](AssemblyAndIntegration.md) | Tolerance stacks, the crossover, shimming, sequence and access |
| [InspectionAndNDE](InspectionAndNDE.md) | Probability of detection, a90 and a90/95, what each method misses |
| [ProcessQualification](ProcessQualification.md) | Qualifying a process, coupons, first article, production control |
| [SupplyChainAndMakeBuy](SupplyChainAndMakeBuy.md) | Make-buy, supplier qualification, lead time, obsolescence |
| [RateAndLearning](RateAndLearning.md) | Wright's curve, the bottleneck, shifts, and what rate does to a design |
| [StandardsIndex](StandardsIndex.md) | One standard read, and the rest indexed |
| [ValidationReferences](ValidationReferences.md) | The anchor, one distinction it settled, three gaps |

---

## Design rules of thumb

- **Design for manufacture is a design activity, not a manufacturing complaint.**
- **Tooling cost and lead time are design decisions** made by someone who was not thinking about tooling.
- **A process is not qualified until a coupon made the same way has been destroyed.**
- **Inspection finds what it is looking for.** Decide what you are looking for before choosing the method.
- **Rate changes everything.** A process that works for one article may not work for fifty.
- **Check the crossover before using a statistical stack.** It is one line and it is usually skipped.

---

## Failure modes

**A three sigma statistical stack on six contributors.** Worse than the arithmetic sum it replaced.

**Every dimension tightened equally.** One of them holds half the stack and the rest hold nothing.

**An inspection specified after the wall thickness.** It may not be able to see the critical flaw.

**An inspection method chosen by sensitivity.** The one that clears may not work on the material.

**Capacity estimated as the sum of cycle times.** It is the slowest station.

**A learned-out unit cost quoted for a twenty unit programme.** It will not be reached.

---

## References

- MIL-HDBK-1823A, *Nondestructive Evaluation System Reliability Assessment*
- [aerospaceMaterials](../../aerospaceMaterials/), which carries the process physics in ten sub-domains
- [CostAndProducibility](../../vehicleArchitecture/docs/CostAndProducibility.md), which names the gaps this domain fills
- [ValidationReferences](ValidationReferences.md)
