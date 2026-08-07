# castingProcesses

**Investment, Sand and Die Casting**

> **Status: complete.** 11 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

The casting routes other than centrifugal, which has its own sub-domain. Investment casting is the dominant aerospace casting route and it produces complex geometry in one piece with an excellent as-cast surface.

The engineering content that justifies a library is the casting factor. Per NASA-STD-5001 the allowable knockdown falls from 2.0 to 1.0 with a qualified process, full volumetric NDE and three sample lots, and that factor is the entire allowable. Qualifying the process is frequently cheaper than the mass the default factor costs.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`CastingProcess`](castingProcessesLibrary/CastingProcess.py) | Solidification, riser sizing, and the casting factor that sets the allowable |

**`CastingProcess`** -- Casting modulus and Chvorinov time; riser sizing by the modulus method checked against the shrinkage volume, with the binding condition reported; the NASA-STD-5001 casting factor ladder and the mass penalty it carries; ISO 8062 tolerance to machining stock, and pattern shrinkage.

Shared helpers come from [`castingUtils`](castingProcessesLibrary/castingUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/), so a class here can query an alloy and apply a knockdown without repeating the import.

The module is named `castingUtils.py` rather than `utils.py` deliberately. Every library in this repository ends up on a flat `sys.path` when pytest collects them in one process, so a second `utils.py` would shadow the first and whichever was imported earliest would win.

---

## Topic coverage

- [ ] Process comparison: investment, sand, die, and where each belongs
- [ ] Investment casting: pattern, shell, burnout, pour, and the achievable geometry
- [ ] Solidification: Chvorinov, modulus, and directional solidification
- [ ] Riser sizing by the modulus method, and gating ratios
- [ ] Minimum section from fluidity, and the wall thickness limit
- [ ] Casting factor selection per NASA-STD-5001 and 6016
- [ ] Defects: porosity, shrinkage, cold shut, inclusion, hot tear
- [ ] Inspection: RT, penetrant, and what each finds
- [ ] Tolerance grade and machining allowance per ISO 8062
- [ ] Qualification: three sample lots, and what full volumetric NDE means

---

## Where this sub-domain sits

| Connects to | Interaction |
|---|---|
| [aerospaceMaterials](../) | The parent domain. Allowables, material data, and the knockdown chain |
| [ProcessRouteSelection.md](../docs/ProcessRouteSelection.md) | This process as one row in the route trade |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | The cross-cutting view: make-buy, tooling, assembly, rate |

---

Sean Bowman
