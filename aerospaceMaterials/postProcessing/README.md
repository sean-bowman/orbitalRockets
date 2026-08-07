# postProcessing

**Surface and Post-Processing**

> **Status: complete.** 14 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

Everything done after the part exists that changes its properties or its surface: shot and laser peening, chemical milling, electropolishing, anodising and conversion coating, plating, thermal spray, and vibratory finishing.

Hot isostatic pressing is deliberately not here. It is a thermal cycle at pressure and it belongs with solution treatment and aging in [HeatTreatment](../aerospaceMaterialsLibrary/HeatTreatment.py), where it interacts with them directly.

The calculations that justify a library are the compressive layer from peening and the fatigue improvement it buys, Faraday stock removal for the electrochemical processes, and the titanium alpha case removal depth, which is a required specification rather than an optional refinement.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`SurfaceTreatment`](postProcessingLibrary/SurfaceTreatment.py) | Peening, chemical and electrochemical removal, plating and thermal spray |

**`SurfaceTreatment`** -- Almen intensity to compressive layer depth and fatigue improvement factor, with exponential coverage saturation; Faraday and etch rate stock removal from both surfaces; titanium alpha case depth and the removal it requires; the ASTM F1940 plating bake trigger; thermal spray residual stress from CTE mismatch.

Shared helpers come from [`surfaceUtils`](postProcessingLibrary/surfaceUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/), so a class here can query an alloy and apply a knockdown without repeating the import.

The module is named `surfaceUtils.py` rather than `utils.py` deliberately. Every library in this repository ends up on a flat `sys.path` when pytest collects them in one process, so a second `utils.py` would shadow the first and whichever was imported earliest would win.

---

## Topic coverage

- [ ] Shot peening: Almen intensity, coverage, compressive layer depth and the fatigue benefit
- [ ] Laser shock peening: deeper layer, no surface roughening, and the cost
- [ ] Chemical milling: Faraday removal, both surfaces, and the dimensional consequence
- [ ] Titanium alpha case removal: depth, and why it is a required specification
- [ ] Electropolishing: stock removal, Ra improvement, and the achievable floor
- [ ] Anodising and conversion coating: thickness, corrosion protection, fatigue debit
- [ ] Plating: nickel, cadmium, silver, gold, and the hydrogen embrittlement bake trigger
- [ ] IVD aluminium as the cadmium replacement
- [ ] Thermal spray: HVOF, plasma, cold spray, bond coat, and residual stress from CTE mismatch
- [ ] Vibratory and tumble finishing: edge break, Ra, and the limits on internal features
- [ ] Laser polishing and its place against abrasive methods
- [ ] Passivation, and where it overlaps the fluidSystems treatment
- [ ] Verification: how each process is inspected and what the acceptance is

---

## Where this sub-domain sits

| Connects to | Interaction |
|---|---|
| [aerospaceMaterials](../) | The parent domain. Allowables, material data, and the knockdown chain |
| [ProcessRouteSelection.md](../docs/ProcessRouteSelection.md) | This process as one row in the route trade |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | The cross-cutting view: make-buy, tooling, assembly, rate |

---

Sean Bowman
