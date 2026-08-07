# machiningProcesses

**Machining and Electro-Machining**

> **Status: complete.** 12 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

Milling, turning, mirror milling, deep hole drilling, EDM and ECM. Almost every launch vehicle part is machined at some point, and the constraints that actually bite are not cutting speed but chatter, thin wall deflection and distortion.

The distortion link is the one worth building: a quenched plate carries self-equilibrating residual stress, and machining it asymmetrically releases an unbalanced moment that bows the part. That calculation lives in [HeatTreatment](../aerospaceMaterialsLibrary/HeatTreatment.py) and this sub-domain consumes it.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`MachiningProcess`](machiningProcessesLibrary/MachiningProcess.py) | Cutting force, tool life, chatter stability and distortion |

**`MachiningProcess`** -- Cutting force and spindle power from the specific cutting energy; Taylor tool life and the speed sensitivity; chatter stability lobes and the spindle speeds that permit a deeper cut; thin wall deflection as a cantilever plate, and the spring passes it needs; distortion released by asymmetric removal, consuming the HeatTreatment residual stress; surface integrity and the fatigue factor.

Shared helpers come from [`machiningUtils`](machiningProcessesLibrary/machiningUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/), so a class here can query an alloy and apply a knockdown without repeating the import.

The module is named `machiningUtils.py` rather than `utils.py` deliberately. Every library in this repository ends up on a flat `sys.path` when pytest collects them in one process, so a second `utils.py` would shadow the first and whichever was imported earliest would win.

---

## Topic coverage

- [ ] Material removal rate, cutting force from specific cutting energy, spindle power
- [ ] Taylor tool life, and the speed against life trade
- [ ] Chatter: stability lobes, and why they set the achievable depth of cut
- [ ] Thin wall deflection under cutting force, and the multi-pass strategy
- [ ] Distortion from residual stress release, and the link to heat treatment
- [ ] Machinability by alloy: why titanium and nickel are hard and aluminium is not
- [ ] Mirror milling and large panel machining
- [ ] Deep hole drilling: gun drilling, BTA, and straightness
- [ ] EDM: wire and sinker, the recast layer, and when it must be removed
- [ ] ECM and electrochemical machining: no recast, no residual stress
- [ ] Surface integrity: residual stress, white layer, and the fatigue consequence

---

## Where this sub-domain sits

| Connects to | Interaction |
|---|---|
| [aerospaceMaterials](../) | The parent domain. Allowables, material data, and the knockdown chain |
| [ProcessRouteSelection.md](../docs/ProcessRouteSelection.md) | This process as one row in the route trade |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | The cross-cutting view: make-buy, tooling, assembly, rate |

---

Sean Bowman
