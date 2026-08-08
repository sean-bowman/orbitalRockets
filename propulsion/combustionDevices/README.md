# combustionDevices

**Injectors, Chambers, Stability and Cooling**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this sub-domain is written yet. See [../../fluidSystems/](../../fluidSystems/) for a completed domain.

---

## What This Is

The hot end of the engine, and the part with the most ways to fail. An injector that mixes badly loses c* efficiency; one that mixes too well next to the wall burns through it; one that couples with an acoustic mode destroys the engine in milliseconds.

Chamber sizing is where the textbook and the practice diverge. `L*` and residence time set a minimum volume for the combustion to complete, and on almost every real engine the chamber is larger than that minimum because the cooling jacket needs the area. Sizing a chamber on `L*` alone and then discovering the heat flux is the classic sequence.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/InjectorDesign.md` | Element types, momentum ratio, mixing, and the wall compatibility problem | planned |
| `docs/ChamberSizing.md` | L*, residence time, contraction ratio, and why cooling usually governs | planned |
| `docs/CombustionStability.md` | Acoustic modes, coupling, baffles and cavities, rating by bomb and pulse | planned |
| `docs/RegenerativeCooling.md` | Heat flux, coolant side heat transfer, channel sizing, and the failure modes | planned |
| `docs/AlternativeCooling.md` | Film, transpiration, ablative, radiation, and dump cooling | planned |
| `docs/CombustionEfficiency.md` | c* efficiency, what causes the loss, and how it is measured | planned |
| `docs/ChamberStructures.md` | The liner and jacket as a pressure vessel, thermal strain, doghouse failure | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `Injector` | Element sizing, pressure drop, momentum ratio, mixing and stability screens | planned |
| `CombustionChamber` | L*, contraction ratio, chamber volume and the residence time check | planned |
| `RegenerativeCooling` | Heat flux, wall temperature, coolant pressure drop and channel sizing | planned |
| `CombustionStability` | Acoustic mode frequencies, injector coupling parameters, damping devices | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `combustionUtils.py`.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../nozzles/](../nozzles/) | The chamber and nozzle are one pressure vessel and one thermal problem |
| [../../aerospaceMaterials/](../../aerospaceMaterials/) | GRCop liners, and the additive manufacture that makes integral channels possible |
| [../../thermalManagement/](../../thermalManagement/) | Regenerative cooling is a heat exchanger with an extreme heat flux |
| [../../fluidSystems/](../../fluidSystems/) | Injector pressure drop is the last element of the feed system |

---

Sean Bowman
