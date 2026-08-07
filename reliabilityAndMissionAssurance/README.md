# reliabilityAndMissionAssurance

**Reliability, Fault Tolerance and Mission Assurance**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

Reliability engineering is what turns a collection of good hardware into a vehicle that works. This domain covers the analytical methods (FMECA, fault trees, reliability allocation), the design responses (redundancy, fault tolerance, derating), and the programmatic systems (quality, configuration control, problem reporting) that make them stick.

It is deliberately unglamorous and it is where most launch failures are actually decided.

Reference documentation with a focused class library for the calculations that genuinely need one.

## Design Ethos

- A reliability number without a stated basis is a wish. Say where it came from.
- Redundancy that shares a failure cause is not redundancy.
- Most failures are not random. They are design escapes, process escapes, or human error.
- The FMECA is only useful if somebody acts on it. An unactioned finding is worse than none.
- Single-point failures should be listed, argued and accepted deliberately, never discovered.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/ReliabilityOverview.md` | Hub: the reliability process, terminology, document index | planned |
| `docs/FMECA.md` | Failure modes and effects, criticality, severity and detectability, actioning | planned |
| `docs/FaultTreeAnalysis.md` | Top-down analysis, cut sets, common cause, quantification | planned |
| `docs/ReliabilityAllocation.md` | Budgeting reliability across subsystems, prediction methods and their limits | planned |
| `docs/RedundancyAndFaultTolerance.md` | Redundancy types, common cause, fail-operational and fail-safe, voting | planned |
| `docs/DeratingAndMargins.md` | Derating policy, margin philosophy, where margin actually protects | planned |
| `docs/SinglePointFailures.md` | Identification, acceptance rationale, mitigation, tracking | planned |
| `docs/QualityAndProcessControl.md` | Inspection, first article, statistical process control, escapes | planned |
| `docs/ConfigurationManagement.md` | Baselines, change control, as-designed versus as-built, traceability | planned |
| `docs/ProblemReporting.md` | Nonconformance, MRB, corrective action, closure, trending | planned |
| `docs/HumanFactors.md` | Procedure design, error-proofing, the failure mode that is a person | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing reliability and quality standards | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `FMECA` | Failure mode table, RPN or criticality ranking, filtering and reporting | planned |
| `FaultTree` | Tree construction, minimal cut sets, probability rollup, common cause | planned |
| `ReliabilityBudget` | Allocation across subsystems, series and parallel rollup, margin tracking | planned |
| `RedundancyAnalysis` | Configuration reliability, common cause beta factor, coverage | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/) | Test evidence is what a reliability claim is built on |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Single-shot non-redundant devices dominate the fault tree |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | FTS reliability is the most stringent requirement on the vehicle |
| [fluidSystems](../fluidSystems/) | Leak paths, single valves and trapped volumes are the recurring findings |

---

Sean Bowman
