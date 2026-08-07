# additiveOther

**Non-LPBF Additive Processes**

> **Status: complete.** 10 documents. This sub-domain is deliberately documentation only, and the overview says why. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

Directed energy deposition, wire arc additive, electron beam powder bed, binder jetting and cold spray. Each of these exists because laser powder bed fusion runs out somewhere: build volume, deposition rate, feedstock cost, or the ability to repair an existing part rather than make a new one.

This sub-domain is deliberately documentation only. Each process reduces to one or two equations that belong in the [ProcessComparison](../aerospaceMaterialsLibrary/ProcessComparison.py) route table rather than in a class of its own, and building five thin classes would add surface area without adding capability.

---

## Library

**Docs only.** No class is planned, and the reason is in the description above: building one would add surface area without adding capability.

---

## Topic coverage

- [ ] Process comparison: deposition rate, resolution, build volume, feedstock cost
- [ ] DED: powder and wire fed, melt pool control, and repair applications
- [ ] Wire arc additive: deposition rate, bead geometry, thermal management, large preforms
- [ ] Electron beam powder bed: vacuum, preheat, and why residual stress is lower than LPBF
- [ ] Binder jetting: green density, sintering shrinkage, and the dimensional consequence
- [ ] Cold spray: critical velocity, solid state deposition, repair and dimensional restoration
- [ ] Feedstock: wire versus powder, cost, handling and reuse
- [ ] Where each process wins, and the build volume and rate limits that decide it
- [ ] Qualification: what changes relative to the LPBF standards

---

## Where this sub-domain sits

| Connects to | Interaction |
|---|---|
| [aerospaceMaterials](../) | The parent domain. Allowables, material data, and the knockdown chain |
| [ProcessRouteSelection.md](../docs/ProcessRouteSelection.md) | This process as one row in the route trade |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | The cross-cutting view: make-buy, tooling, assembly, rate |

---

Sean Bowman
