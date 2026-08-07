# formingProcesses

**Sheet and Tube Forming**

> **Status: complete.** 12 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

Bending, spinning, flow forming, hydroforming, superplastic forming, deep drawing and stretch forming. Forming is how most thin-walled launch vehicle structure is made, and it is the route with the best buy-to-fly of any conventional process.

The engineering is genuinely computable: minimum bend radius follows from ductility, springback has a closed form, the forming limit diagram bounds the strain, and work hardening raises the strength of the formed section in a way a designer can take credit for if the analysis supports it.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`FormingProcess`](formingProcessesLibrary/FormingProcess.py) | Bend radius, springback, forming limits and work hardening |

**`FormingProcess`** -- Minimum bend radius from reduction of area, with the grain direction factor; closed-form springback and the tool compensation; bend allowance and the migrating k-factor; forming limit diagram with the plane strain minimum; Hollomon work hardening reporting both the strength gained and the ductility spent; hydroform pressure.

Shared helpers come from [`formingUtils`](formingProcessesLibrary/formingUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/), so a class here can query an alloy and apply a knockdown without repeating the import.

The module is named `formingUtils.py` rather than `utils.py` deliberately. Every library in this repository ends up on a flat `sys.path` when pytest collects them in one process, so a second `utils.py` would shadow the first and whichever was imported earliest would win.

---

## Topic coverage

- [ ] Process selection: bending, spinning, flow forming, hydroforming, superplastic, deep draw
- [ ] Minimum bend radius from reduction of area, and the grain direction effect
- [ ] Springback: the closed form, and compensation strategies
- [ ] Bend allowance and the k-factor
- [ ] Forming limit diagram: major and minor strain, and where the safe region ends
- [ ] Work hardening: the strength gained and the ductility spent
- [ ] Flow forming: wall thickness control, mandrel design, and the cold work benefit
- [ ] Hydroforming: pressure requirement, and where it beats matched die
- [ ] Superplastic forming: strain rate sensitivity, and the alloys that support it
- [ ] Interstage annealing: when accumulated strain forces it
- [ ] Springback compensation and tooling iteration

---

## Where this sub-domain sits

| Connects to | Interaction |
|---|---|
| [aerospaceMaterials](../) | The parent domain. Allowables, material data, and the knockdown chain |
| [ProcessRouteSelection.md](../docs/ProcessRouteSelection.md) | This process as one row in the route trade |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | The cross-cutting view: make-buy, tooling, assembly, rate |

---

Sean Bowman
