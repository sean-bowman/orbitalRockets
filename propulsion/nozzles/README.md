# nozzles

**Nozzle Performance and Area Ratio Selection**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this sub-domain is written yet. See [../../fluidSystems/](../../fluidSystems/) for a completed domain.

---

## What This Is

The performance half of nozzle work: what area ratio to choose, what thrust coefficient it gives, where the flow separates, and what altitude compensation would be worth if anyone flew it.

**Contour generation is not here.** The NOVA suite generates method-of-characteristics contours and cooling channel geometry and exports CAD-ready output, and this sub-domain points there rather than reimplementing it. Two implementations of the same method with nothing enforcing agreement between them is worse than one.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/NozzlePerformance.md` | Thrust coefficient, ideal and real, and the loss mechanisms | planned |
| `docs/AreaRatioSelection.md` | The altitude trade, optimum expansion, and what a booster nozzle is really sized by | planned |
| `docs/FlowSeparation.md` | Summerfield and Schmucker criteria, side loads, and the start transient | planned |
| `docs/AltitudeCompensation.md` | Aerospike, dual bell, extendible. What each buys and why they are rare | planned |
| `docs/NozzleContourInterface.md` | What NOVA generates, what this domain supplies it, and where the boundary is | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `NozzlePerformance` | Cf ideal and delivered, area ratio, altitude performance, separation check | planned |
| `AreaRatioTrade` | Optimum area ratio against a trajectory, and the mass and performance exchange | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `nozzleUtils.py`.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| NOVA | The contour generation suite. This domain supplies the requirements and consumes the geometry |
| [../combustionDevices/](../combustionDevices/) | The chamber and nozzle are one pressure vessel and one cooling circuit |
| [../../aerospaceStructures/](../../aerospaceStructures/) | Side loads during the start transient are a real structural case |

---

Sean Bowman
