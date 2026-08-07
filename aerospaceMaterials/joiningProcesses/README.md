# joiningProcesses

**Brazing, Bonding and Mechanical Joining**

> **Status: complete.** 11 documents. This sub-domain is deliberately documentation only, and the overview says why. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

The joining processes other than fusion welding. Welding is already covered by [fluidSystems Weld.py](../../fluidSystems/fluidSystemsLibrary/Weld.py), which does joint efficiency, HAZ knockdown, WRC-1992 ferrite number and inspection selection, and duplicating it here would create exactly the drift this repository works to avoid.

This sub-domain is documentation only for a second reason as well: the analysis that would justify a library, adhesive shear lag and bolted joint bearing, is a structures problem and belongs in [aerospaceStructures](../../aerospaceStructures/). What is genuinely a materials question is the braze alloy melt range against the base metal solution temperature, and that is a table.

---

## Library

**Docs only.** No class is planned, and the reason is in the description above: building one would add surface area without adding capability.

---

## Topic coverage

- [ ] Process selection: braze, adhesive, mechanical, diffusion bond, and where each belongs
- [ ] Brazing: capillary gap, lap length, filler selection, and the flux question
- [ ] Braze alloy melt ranges against base metal solution and aging temperatures
- [ ] Diffusion bonding: time, temperature, pressure, and surface preparation
- [ ] Adhesive bonding: surface preparation, cure, and why the surface prep is most of it
- [ ] Adhesive joint design: lap length, taper, and peel avoidance
- [ ] Mechanical joining: fastener material selection, galvanic pairs, and preload
- [ ] Fastener materials: A286, titanium, Inconel, and why not aluminium against carbon
- [ ] Inspection: what finds a disbond and what does not
- [ ] Where welding is covered: fluidSystems Welds.md and Weld.py

---

## Where this sub-domain sits

| Connects to | Interaction |
|---|---|
| [aerospaceMaterials](../) | The parent domain. Allowables, material data, and the knockdown chain |
| [ProcessRouteSelection.md](../docs/ProcessRouteSelection.md) | This process as one row in the route trade |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | The cross-cutting view: make-buy, tooling, assembly, rate |

---

Sean Bowman
