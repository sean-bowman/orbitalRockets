# aerospaceStructures

**Launch Vehicle Structural Design and Analysis**

> **Status: in progress.** Two of eight classes are built and tested (34 tests). The remaining six classes and all fifteen documents are planned. See [../fluidSystems/](../fluidSystems/) for a completed domain.

---

## What This Is

Launch vehicle structure is a buckling problem wearing a stress problem's clothes. Almost nothing on a vehicle fails by exceeding its material strength; it fails by buckling, by fatigue at a joint, or by a load path nobody drew. This domain covers the forms that actually appear on a vehicle -- thin monocoque shells, pressurized tanks, sandwich panels, thrust structures, and the joints between them -- and the analysis each one needs.

It is the domain most tightly coupled to fluid systems, because a propellant tank is simultaneously a pressure vessel, a primary structure and a fluid container, and the three requirements do not agree with each other.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../fluidSystems/) template.

## Design Ethos

- Buckling governs, not strength. A stress check that passes proves very little on a thin shell.
- Knockdown factors are empirical and enormous. A theoretical buckling load is a starting point, not an answer.
- Every load case is a combination. The governing case is rarely the largest single load.
- Joints are where structures fail. Analyze them with the same effort as the members they connect.
- Mass is the objective function. A structure that is adequate and heavy has failed at its job.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/StructuresOverview.md` | Hub: load paths, the analysis sequence, conventions, document index | planned |
| `docs/LoadsAndLoadCases.md` | Load sources, combination, factors of safety, limit and ultimate, load case matrices | planned |
| `docs/ShellBuckling.md` | Cylindrical and conical shells, knockdown factors, NASA SP-8007, stiffened shells | planned |
| `docs/PressureVesselsAndTanks.md` | Membrane theory, domes, Y-rings, common bulkheads, autofrettage, COPVs | planned |
| `docs/SandwichPanels.md` | Honeycomb and foam cores, facesheet wrinkling, core shear, intracell buckling | planned |
| `docs/StiffenedStructures.md` | Isogrid, orthogrid, skin-stringer, ring frames, crippling | planned |
| `docs/BoltedJoints.md` | Preload, separation, joint diagrams, bearing and shear-out, NASA-STD-5020 | planned |
| `docs/BondedAndCompositeJoints.md` | Adhesive joints, composite laminates, failure criteria, damage tolerance | planned |
| `docs/WeldedStructures.md` | Weld joint efficiency, HAZ derating, friction stir, weld land design | planned |
| `docs/ThrustStructures.md` | Thrust takeout, gimbal loads, engine mounts, interstage and skirt design | planned |
| `docs/DynamicsAndModes.md` | Modal analysis, frequency requirements, POGO, slosh, coupled loads analysis | planned |
| `docs/FatigueAndFracture.md` | S-N and crack growth, fracture control, NASA-STD-5019, damage tolerance | planned |
| `docs/StabilityAndCollapse.md` | External pressure, vacuum jacket collapse, general instability | planned |
| `docs/MassPropertiesAndOptimization.md` | Mass estimating relationships, sizing loops, structural efficiency | planned |
| `docs/StandardsIndex.md` | Annotated index of the governing structural standards | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `CylindricalShell` | Buckling under axial, bending, external pressure, torsion and combined load, with SP-8007 knockdowns and pressure stabilization | **built** |
| `PressureVessel` | Membrane stresses, dome geometry, wall thickness, proof and burst, mass | **built** |
| `SandwichPanel` | Facesheet wrinkling, core shear, dimpling, panel bending and buckling | planned |
| `StiffenedPanel` | Isogrid and skin-stringer smeared properties, crippling, panel and general instability | planned |
| `BoltedJoint` | Preload, joint stiffness diagram, separation margin, bearing and shear-out | planned |
| `BeamColumn` | Euler and Johnson columns, combined axial and bending, effective length | planned |
| `ModalEstimate` | First bending and axial modes for shells, beams and panels | planned |
| `LoadCase` | Load combination, limit and ultimate factors, governing case identification | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `utils.py`, and the structure-specific helpers live in `structuresUtils.py`.

Allowables come from the [aerospaceMaterials](../aerospaceMaterials/) database through `structuralAllowables()`, which carries the full alloy roster and the A and B basis values. It falls back to the nine-alloy seed table in `common` when that domain is absent, and always reports which source answered.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | A propellant tank is a pressure vessel, a primary structure and a fluid container at once |
| [aerospaceMaterials](../aerospaceMaterials/) | Allowables, knockdown factors and joint efficiencies all come from the material |
| [environmentsAndLoads](../environmentsAndLoads/) | Supplies the load cases this domain sizes against |
| [thermalManagement](../thermalManagement/) | Thermal gradients are a load case; thermal growth is a displacement constraint |

---

Sean Bowman
