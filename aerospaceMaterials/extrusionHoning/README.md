# extrusionHoning

**Abrasive Flow Machining for Internal Passages**

> **Status: complete.** 9 documents, with the classes below built and tested. See [../../fluidSystems/](../../fluidSystems/) for the domain this one is modelled on.

---

## What This Is

Abrasive flow machining, or extrusion honing, forces an abrasive-laden viscoelastic media through a workpiece to finish internal passages that no tool can reach. It is the practical answer to the as-built surface roughness of additively manufactured flow passages, and to deburring and radiusing cross-drilled intersections.

It earns its own directory because it is the process that makes additive fluid hardware usable, and because the parameters that control it are not obvious.

Reference documentation with a focused class library for the calculations that genuinely need one.

## Design Ethos

- Media rheology is the process variable. Everything else is secondary to picking the right media.
- Material removal follows the flow. Wherever the media accelerates, it cuts more.
- It radiuses edges whether you want it to or not. Design for that rather than fighting it.
- Uniformity requires flow control, usually fixturing that restricts the easy paths.
- Verify by flow test, not by inspection. You cannot see inside the passage you just finished.

---

## Library

Built and tested. Run `python -m pytest tests/ -v` from this directory.

| Class | Computes |
|---|---|
| [`ExtrusionHoning`](extrusionHoningLibrary/ExtrusionHoning.py) | Media rheology, wall shear, flow split and surface finish |

**`ExtrusionHoning`** -- media grade selection from the passage size; wall shear as a force balance on the media column, and the power law shear rate; radial removal, diametral growth and edge radius; exponential roughness decay to the grit-limited floor; flow split across branching passages and the restrictor sizing that balances them.

The three planned classes collapsed into one. `AbrasiveMedia` became the `MEDIA_GRADES` table, because a media grade lookup is not a class, and `SurfaceFinish` folded into `calculateSurfaceFinish` because the roughness decay is one equation rather than a separate object.

The flow split is the part worth having. For a power law fluid the conductance goes as `D^(3 + 1/n)`, and with `n` near 0.28 the diameter exponent is above six, so a ten percent diameter difference between two branches produces a seventy percent flow difference. The branch that flows more gets honed more, opens further, and takes an even larger share. The process is self-correcting within one passage and exactly the opposite across parallel ones, which is why fixturing and restrictors exist.

Shared helpers come from [`honingUtils`](extrusionHoningLibrary/honingUtils.py), which bootstraps both [`orbitalRockets/common`](../../common/) and the parent [`aerospaceMaterialsLibrary`](../aerospaceMaterialsLibrary/).

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/ExtrusionHoningOverview.md` | Hub: the process, where it applies, document index | planned |
| `docs/MediaAndRheology.md` | Carrier viscosity, abrasive type, grit size, concentration, media life | planned |
| `docs/ProcessParameters.md` | Pressure, flow rate, cycle count, temperature, and what each controls | planned |
| `docs/MaterialRemovalAndFinish.md` | Removal rate models, achievable Ra, edge radius, dimensional change | planned |
| `docs/FixturingAndFlowControl.md` | Tooling, restrictors, achieving uniform removal in complex passages | planned |
| `docs/AdditiveApplications.md` | Finishing LPBF internal passages, powder removal, what it can and cannot fix | planned |
| `docs/VerificationAndInspection.md` | Flow test, borescope, CT, replication, surface measurement inside a passage | planned |
| `docs/ProcessQualification.md` | Qualifying the process, coupons, first article, production control | planned |
| `docs/StandardsIndex.md` | Annotated index of relevant standards and vendor practice | planned |


## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceMaterials](../) | Subsurface condition and residual stress after machining; sits with additiveLPBF |
| [fluidSystems](../../fluidSystems/) | The reason it exists: as-built LPBF roughness ruins a pressure drop prediction |
| [manufacturingAndAssembly](../../manufacturingAndAssembly/) | One process among the finishing options |

---

Sean Bowman
