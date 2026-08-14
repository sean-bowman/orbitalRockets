# manufacturingAndAssembly

**Manufacturing, Joining, Tooling and Inspection**

> **Status: complete.** Three classes, twelve documents and 66 tests. The process physics lives in the ten `aerospaceMaterials` sub-domains; what is here is the cross-cutting view.

---

## What This Is

How a design becomes hardware, at rate, repeatably. This domain covers the processes used to make launch vehicle structure, the tooling that holds it, the joining methods, and the inspection that establishes whether any of it worked.

**The process physics is not here and that is deliberate.** Tool life, chatter, springback, forming limits, solidification and weld knockdowns all live in the ten process sub-domains under [aerospaceMaterials](../aerospaceMaterials/). What stays here is what a stack of tolerances does, what an inspection establishes, and what rate does to cost.

---

## The four results

**A three sigma statistical tolerance stack is no saving at all below about nine contributors.** The worst case is a hard bound, so a statistical stack at k sigma exceeds it whenever k is above the sum of tolerances over their quadrature sum, which for equal contributors is **exactly the square root of the count**. On the worked six contributor stack the statistical method produces 3.38 mm against a 2.35 mm arithmetic sum, which cannot physically occur. The check is one line and it is almost never made.

**One dimension holds half the stack.** A contributor enters the worst case linearly and the statistical stack as its square, so the statistical ranking is far more concentrated: barrel roundness is 34 per cent of the worst case and 50 of the statistical. Tightening it moves the assembly and tightening the others moves almost nothing, and **fixing it makes weld shrinkage the new dominant contributor at 50 per cent.** The problem moves rather than going away.

**An inspection that cannot find a flaw smaller than the critical one establishes nothing.** At full wall the penetrant inspection of the tank weld clears with a margin of 1.38. Take the same weld to a thinner wall, where the critical flaw is 1.3 mm, and it misses 13 per cent of the flaws large enough to burst the tank. **That is a design conclusion rather than an inspection finding**, and it is discovered late because the inspection procedure is written after the wall thickness is fixed.

**And the cheapest method that clears the size requirement cannot be used on the material.** Magnetic particle clears at a third the cost of the alternatives and does nothing on an aluminium tank. **A ranking by detectable flaw size is not a ranking by usefulness**, and the column that decides the answer is the one saying what each method misses.

**Capacity is the slowest station and not the sum.** A five station line with 268 hours of total cycle time makes 27 units a year because one station takes 75 of them, and fixing it buys 15 hours and no more. That is the same arithmetic as a [turnaround driver](../groundSystemsAndOperations/) and a [life limit](../recoveryAndReusability/), appearing in this repository for the third time. And a programme of twenty units has barely learned: the twentieth unit still costs half the first and the cumulative average, which is what a programme is judged on, is a quarter higher again.

---

## Design Ethos

- Design for manufacture is a design activity, not a manufacturing complaint.
- Tooling cost and lead time are design decisions made by someone who was not thinking about tooling.
- A process is not qualified until a coupon made the same way has been destroyed.
- Inspection finds what it is looking for. Decide what you are looking for before choosing the method.
- Rate changes everything. A process that works for one article may not work for fifty.
- Check the crossover before using a statistical stack. It is one line.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [ManufacturingOverview.md](docs/ManufacturingOverview.md) | Hub: what the domain found, where the process physics lives, document index | **written** |
| [AssemblyAndIntegration.md](docs/AssemblyAndIntegration.md) | Two stacks, the crossover, the dominant contributor, shimming, sequence | **written** |
| [InspectionAndNDE.md](docs/InspectionAndNDE.md) | Probability of detection, a50 and a90 and a90/95, what each method misses | **written** |
| [RateAndLearning.md](docs/RateAndLearning.md) | Wright's curve, unit against average, the bottleneck, shifts before machines | **written** |
| [MachiningAndFabrication.md](docs/MachiningAndFabrication.md) | Where the cost is, buy-to-fly, thin walls, what machining can hold | **written** |
| [FormingAndSpinning.md](docs/FormingAndSpinning.md) | Spun against gored domes, springback, forming limits, rolling a barrel | **written** |
| [WeldingAndJoining.md](docs/WeldingAndJoining.md) | Process selection, friction stir, distortion, qualification, alternatives | **written** |
| [CompositesManufacturing.md](docs/CompositesManufacturing.md) | Part and process as one decision, layup, cure, tooling, defects | **written** |
| [ToolingAndFixturing.md](docs/ToolingAndFixturing.md) | Tooling as a design decision, lead time, accuracy, thermal, rate | **written** |
| [ProcessQualification.md](docs/ProcessQualification.md) | What qualification establishes, coupons, first article, what counts as a change | **written** |
| [SupplyChainAndMakeBuy.md](docs/SupplyChainAndMakeBuy.md) | Make-buy axes, supplier qualification, lead time, obsolescence, counterfeit | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | One standard read, and why the rest live with the processes | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The anchor covering the model and not the numbers, and three gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `ToleranceStack` | Worst case and statistical stacks, the crossover, the dominant contributor, shims, rejects | **written** |
| `InspectionCapability` | Detection curve, a50 and a90, demonstration size, the critical flaw check, method comparison | **written** |
| `ProductionRate` | Wright's curve, cumulative average, process class comparison, takt, bottleneck, shifts | **written** |

**Six things were deliberately not built**, and this domain declines more than any other because ten sub-domains already carry the physics.

**Machining, forming, casting and joining physics.** Taylor tool life, chatter lobes, springback, forming limit diagrams, solidification and weld knockdowns are all in the [aerospaceMaterials](../aerospaceMaterials/) sub-domains. A second implementation here would be the same equations with a different import path.

**Weld joint efficiency and HAZ knockdown**, which [Weld](../fluidSystems/) in fluidSystems owns. **Buy-to-fly and route comparison**, which `ProcessComparison` owns. **Critical flaw size**, which `DamageTolerance` owns and this domain consumes. **Cost estimating relationships**, which [vehicleArchitecture](../vehicleArchitecture/) names as a gap and which remains one. **Supplier qualification and counterfeit control**, which is governance rather than calculation.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `manufacturingUtils.py`.

---

## Worked example

`codeInterface.py` takes one tank barrel section from a tolerance stack through inspection capability to production rate.

| Question | Answer |
|---|---|
| Worst case against statistical stack | 2.350 against 1.127 mm |
| Sigma at which the statistical stack helps | below 2.09 |
| Dominant contributor share | 50 % of the statistical stack |
| Rejects at three sigma | 1 in 370 |
| a90 over a50, which is 9 to the sigma | 2.41 |
| Critical flaw check, full wall against thin | clears, then **refused** |
| Flaws missed at the thin wall critical size | 13 % |
| Methods that establish anything | 5 of 7 |
| Cheapest capable method, and applicable one | magnetic particle, then penetrant |
| Line capacity against demand | 27 against 24 a year |
| Gain from fixing the bottleneck | 15 h, then it moves |
| Unit 20 against the cumulative average | 0.50 against 0.62 |

```bash
python manufacturingAndAssembly/codeInterface.py
```

---

## The anchor, and what it settled

**MIL-HDBK-1823A was read** for its probability of detection model and its demonstration sizes. The anchor covers the model and not the numbers, which is an unusual split: the log-odds curve and the 60 target minimum are the standard and are exact, while the a50 and sigma values put into the model are representative and registered as unvalidated.

**Reading it settled a distinction that is routinely collapsed.** a90 is a property of the inspection: the size found nine times in ten. a90/95 is the 95 per cent confidence bound on an *estimate* of a90, so it falls as the demonstration grows for the same technique. The handbook states that a90/95 has become a de facto design criterion, and that 120 binary opportunities give a significantly smaller a90/95 than the 60 minimum. **Put together: the flaw size a programme designs to is partly a statement about how many specimens somebody paid for.**

**This is the third time in this repository that reading a standard rather than a summary changed something**, after NASA-STD-5017B in [mechanismsAndSeparation](../mechanismsAndSeparation/) and DESR 6055.09 in [groundSystemsAndOperations](../groundSystemsAndOperations/). The pattern is consistent enough to be a rule.

**ASME Y14.5 was not read**, which is the largest gap here: the stack arithmetic is right and what a tolerance zone means on a feature of size with a datum reference frame is assumed. See [ValidationReferences](docs/ValidationReferences.md).

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceMaterials](../aerospaceMaterials/) | Processing determines properties; all ten process sub-domains live there and this domain duplicates none of them |
| [aerospaceStructures](../aerospaceStructures/) | Manufacturing constraints are structural design constraints |
| [fluidSystems](../fluidSystems/) | Owns the weld analysis, and its cleanliness and inspection practice are shared directly |
| [vehicleArchitecture](../vehicleArchitecture/) | Names the learning curve and the cost estimating relationship as gaps; this domain fills the first |
| [recoveryAndReusability](../recoveryAndReusability/) | Post-flight inspection is the same capability question asked of a flown article |
| [groundSystemsAndOperations](../groundSystemsAndOperations/) | The bottleneck arithmetic here is the turnaround driver arithmetic there |

---

Sean Bowman
