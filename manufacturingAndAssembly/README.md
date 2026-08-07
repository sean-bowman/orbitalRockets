# manufacturingAndAssembly

**Manufacturing, Joining, Tooling and Inspection**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this domain is written yet. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

How a design becomes hardware, at rate, repeatably. This domain covers the processes used to make launch vehicle structure and components, the tooling that holds them, the joining methods, and the inspection that establishes whether any of it worked.

Documentation first because the analytical content is thinner than the process content, and because the process-specific analysis lives in the sub-domains: additive LPBF, spin casting and extrusion honing each have their own directory.

Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

## Design Ethos

- Design for manufacture is a design activity, not a manufacturing complaint.
- Tooling cost and lead time are design decisions made by someone who was not thinking about tooling.
- A process is not qualified until a coupon made the same way has been destroyed.
- Inspection finds what it is looking for. Decide what you are looking for before choosing the method.
- Rate changes everything. A process that works for one article may not work for fifty.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/ManufacturingOverview.md` | Hub: process selection, the make-buy decision, document index | planned |
| `docs/MachiningAndFabrication.md` | Milling, turning, mirror milling, tolerances, fixturing, cost drivers | planned |
| `docs/FormingAndSpinning.md` | Sheet forming, spinning, hydroforming, stretch forming, springback | planned |
| `docs/WeldingAndJoining.md` | GTAW, FSW, EBW, brazing; process selection, distortion, qualification | planned |
| `docs/CompositesManufacturing.md` | Layup, AFP, cure, tooling, out-of-autoclave, defects | planned |
| `docs/AdditiveManufacturing.md` | Process overview and the link to the additiveLPBF sub-domain | planned |
| `docs/ToolingAndFixturing.md` | Tooling design, cost, lead time, accuracy, thermal effects | planned |
| `docs/AssemblyAndIntegration.md` | Assembly sequence, tolerance stackup, shimming, access, torque control | planned |
| `docs/InspectionAndNDE.md` | Dimensional, CMM, laser tracker, RT, UT, PT, CT; what each finds and misses | planned |
| `docs/ProcessQualification.md` | Qualifying a process, coupons, first article, production control | planned |
| `docs/SupplyChainAndMakeBuy.md` | Make-buy, supplier qualification, lead time, counterfeit, obsolescence | planned |
| `docs/RateAndLearning.md` | Producing at rate, learning curves, bottlenecks, capacity | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing manufacturing standards | planned |

## Library

None planned yet. Reference documentation first. A class library will follow once the documents establish what the tools actually need to compute.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceMaterials](../aerospaceMaterials/) | Processing determines properties; all ten process sub-domains live there |
| [extrusionHoning](../aerospaceMaterials/extrusionHoning/) | Abrasive flow machining, one of those sub-domains |
| [aerospaceStructures](../aerospaceStructures/) | Manufacturing constraints are structural design constraints |
| [fluidSystems](../fluidSystems/) | Welding, cleanliness and inspection practice are shared directly |

---

Sean Bowman
