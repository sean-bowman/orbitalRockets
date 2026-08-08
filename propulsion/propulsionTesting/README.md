# propulsionTesting

**Hot Fire Campaigns and Test Data**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this sub-domain is written yet. See [../../fluidSystems/](../../fluidSystems/) for a completed domain.

---

## What This Is

How an engine is actually developed, which is by testing it. This sub-domain covers the campaign structure from component tests through to acceptance, what each test is meant to answer, and the instrumentation and data reduction that turn a firing into a number.

It is the propulsion counterpart to [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), and it follows the same principle: a test that cannot fail its own acceptance criterion has not tested anything.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/CampaignStructure.md` | Component, subscale, development, qualification and acceptance | planned |
| `docs/TestStands.md` | Thrust measurement, the load path, and what a stand actually measures | planned |
| `docs/Instrumentation.md` | Pressure, temperature, flow and thrust. The measurements that are hard | planned |
| `docs/DataReduction.md` | From raw channels to c*, Cf and Isp, and the uncertainty in each | planned |
| `docs/StabilityRating.md` | Bomb and pulse testing, and what a stability rating demonstrates | planned |
| `docs/AnomalyInvestigation.md` | Reading a failure from the data, and the signatures worth recognising | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `HotFireTest` | Test definition, duration, sequence and the pass criteria | planned |
| `PerformanceReduction` | c*, Cf and Isp from measured channels, with the uncertainty budget | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `propulsionTestUtils.py`.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../../fluidSystems/fluidSystemsTesting/](../../fluidSystems/fluidSystemsTesting/) | The same campaign philosophy, applied to the feed system |
| [../../environmentsAndLoads/](../../environmentsAndLoads/) | Static fire measurements are a source for the vibration environment |
| [../../reliabilityAndMissionAssurance/](../../reliabilityAndMissionAssurance/) | Test evidence is what a reliability claim rests on |

---

Sean Bowman
