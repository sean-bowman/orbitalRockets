# combustionDevices

**Injectors, Chambers, Stability and Cooling**

> **Status: complete.** Three classes, eight documents and 58 tests, with a worked example that takes the hub's chamber and finds it cannot be regeneratively cooled by its own fuel. Validated to bounding level only: the peak throat flux sits inside a measured literature band, and the integrated heat load has no external anchor.

---

## What This Is

The hot end of the engine, and the part with the most ways to fail. An injector that mixes badly loses c* efficiency; one that mixes too well next to the wall burns through it; one that couples with an acoustic mode destroys the engine in milliseconds.

Chamber sizing is where the textbook and the practice diverge, though not in the direction usually claimed. `L*` sets a minimum volume for combustion to complete and chambers are usually built near it. Cooling does not size the chamber: it decides whether the design is feasible at all, and when it fails the answer is film cooling or a lower chamber pressure rather than a longer chamber. Lengthening a chamber adds heat load with the area. See [ChamberSizing](docs/ChamberSizing.md), which computes it.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [InjectorDesign.md](docs/InjectorDesign.md) | Element types, orifice sizing, the forced momentum ratio, the outer row | **written** |
| [ChamberSizing.md](docs/ChamberSizing.md) | L*, why residence time cancels, contraction ratio, what cooling really constrains | **written** |
| [CombustionStability.md](docs/CombustionStability.md) | Acoustic modes, chug, baffles and cavities, why there is no margin | **written** |
| [RegenerativeCooling.md](docs/RegenerativeCooling.md) | Bartz, the capability check, the chamber pressure ceiling, coolant choice | **written** |
| [AlternativeCooling.md](docs/AlternativeCooling.md) | Film, ablative, radiation, transpiration, and what each one costs | **written** |
| [CombustionEfficiency.md](docs/CombustionEfficiency.md) | What c* efficiency contains, how it is measured, what engines achieve | **written** |
| [ChamberStructures.md](docs/ChamberStructures.md) | Liner and jacket, thermal strain, doghouse failure, low cycle fatigue | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The external sources the tools are checked against, and what is not checked | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `Injector` | Orifice sizing, momentum ratio, stiffness, the outer row trade | **written** |
| `CombustionStability` | Acoustic modes, chug criterion, baffle and cavity tuning | **written** |
| `RegenerativeCooling` | Bartz heat load, coolant capability, wall temperature, channels | **written** |

## Worked example

`codeInterface.py` takes the 100 kN chamber the [propulsion hub](../codeInterface.py) sizes and computes its heat load properly.

| Quantity | Value |
|---|---|
| Hub placeholder heat load | 2.72 MW |
| Bartz heat load | 8.13 MW |
| Coolant outlet, regenerative only | 664 K |
| RP-1 coking limit | 575 K, **unvalidated** |
| Film fraction that closes the circuit | 8 %, costing 2.4 to 4.0 % of c* |

The engine cannot be regeneratively cooled by its own fuel. That is not a defect in the hub, which labelled its placeholder, nor in the engine, which is an ordinary size at an ordinary chamber pressure. It is what a small high pressure hydrocarbon engine does.

```bash
python propulsion/combustionDevices/codeInterface.py
```


---|---|---|
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
