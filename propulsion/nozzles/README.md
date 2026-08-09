# nozzles

**Nozzle Performance and Area Ratio Selection**

> **Status: complete.** Two classes, six documents and 40 tests, with a worked example that ranks the levers available to a nozzle designer and finds the ordering nearly the reverse of the attention each receives. Two of the four planned classes were deliberately not built.

---

## What This Is

The performance half of nozzle work: what area ratio to choose, what thrust coefficient it gives, where the flow separates, and what altitude compensation would be worth if anyone flew it.

**Contour generation is not here.** The NOVA suite generates method-of-characteristics contours and cooling channel geometry and exports CAD-ready output, and this sub-domain points there rather than reimplementing it. Two implementations of the same method with nothing enforcing agreement between them is worse than one.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [NozzlePerformance.md](docs/NozzlePerformance.md) | The three loss mechanisms, and where the loss actually is | **written** |
| [AreaRatioSelection.md](docs/AreaRatioSelection.md) | What the hub owns, how flat the optimum is, and what really sets a booster | **written** |
| [FlowSeparation.md](docs/FlowSeparation.md) | Summerfield against Schmucker, side loads, and the fully separated start | **written** |
| [AltitudeCompensation.md](docs/AltitudeCompensation.md) | The size of the prize, where it sits, and why nobody has captured it | **written** |
| [NozzleContourInterface.md](docs/NozzleContourInterface.md) | What NOVA generates, what this domain supplies, and where the boundary is | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The external sources the tools are checked against, and the one thing they cannot check | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `NozzleLosses` | Divergence, boundary layer and kinetic losses, and both separation criteria | **written** |
| `AltitudeCompensation` | The ideal compensation bound, and what each arrangement recovers | **written** |
| `NozzlePerformance` | Cf, altitude performance, separation check | **not built** |
| `AreaRatioTrade` | Optimum area ratio against a trajectory | **not built** |

**Two planned classes were deliberately not built.** `NozzlePerformance` and `AreaRatioTrade` would both duplicate the [propulsion hub](../README.md), which already owns the thrust coefficient and whose worked example is built entirely on the area ratio trade. The hub's implementation is validated against RS-25; a second one here would be a second thing to keep in agreement with nothing enforcing it.

That is the same reasoning that keeps contour generation in NOVA, and the same one that left three [aerospaceMaterials](../../aerospaceMaterials/) sub-domains documentation-only.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `nozzleUtils.py`.

---


## Worked example

`codeInterface.py` ranks the levers available to a nozzle designer.

| Lever | Worth | Status |
|---|---|---|
| Altitude compensation, ideal | **14.51 s** | Unreachable |
| Altitude compensation, aerospike | **10.16 s** | Never flown operationally |
| Bell instead of a cone | 4.29 s | Done on every flying engine |
| A fuller bell | 0.29 s | Costs the length back |
| Schmucker instead of Summerfield | 0.45 s | Despite a 36 per cent change in area ratio |

The ordering is nearly the reverse of the attention each receives. Most of the compensation prize sits at altitude, not at sea level: the gap is 6.2 s at sea level and 39.6 s at 55 km.

```bash
python propulsion/nozzles/codeInterface.py
```

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| NOVA | The contour generation suite. This domain supplies the requirements and consumes the geometry |
| [../combustionDevices/](../combustionDevices/) | The chamber and nozzle are one pressure vessel and one cooling circuit |
| [../../aerospaceStructures/](../../aerospaceStructures/) | Side loads during the start transient are a real structural case |

---

Sean Bowman
