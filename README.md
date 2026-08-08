# orbitalRockets

**Orbital-Class Launch Vehicle Engineering -- Reference and Toolset**

A working reference for the engineering of an orbital-class launch vehicle, organized by domain. Each domain pairs comprehensive technical documentation with a Python library that sizes and analyzes real hardware.

The intent is a resource that grows over time. Fluid systems is complete and serves as the template, and aerospace materials follows it with ten process sub-domains of its own. The remaining domains are scaffolded with their topic coverage defined and are filled in progressively.

---

## What This Is

Two things that are meant to be used together, in every domain.

**Technical reference documentation.** The physics, the design procedures, the rules of thumb that experienced engineers carry in their heads, the failure modes that actually occur, and the governing standards. Written to be designed from, not skimmed.

**A working toolset.** Class-per-component Python libraries that size hardware and analyze it. Every class pulls real material and fluid properties, applies the correlations documented alongside it, and reports the findings that matter rather than only the numbers.

## Design Ethos

- All internal quantities are mass-base SI. Imperial appears only at boundaries, through named conversion constants.
- Real property data: REFPROP where installed, CoolProp otherwise, correlation tables where neither models the substance.
- One class per component, one file per class, one interface everywhere: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`.
- Documentation and code are cross-linked in both directions. Every class docstring names its theory document; every document has a tool interface section.
- Errors are typed and carry context. A failed calculation says what went wrong and what the physical limit was.
- The tools report findings, not only results. A calculation that produces a number and a warning is more useful than one that produces a number.
- Shared foundations live in [common/](common/) rather than being duplicated per domain.

---

## Domains

Six of sixteen are complete. [BUILDOUT.md](BUILDOUT.md) is the master checklist: what is built, what is not, the build order, and the depth each remaining domain is planned to.

| Domain | Status | Covers |
|---|---|---|
| [fluidSystems](fluidSystems/) | **Complete** | Valves, lines, orifices, fittings, seals, leaks, welds, insulation, water hammer, hydrazine, catalyst beds, monopropellant thrusters, pressurization |
| [fluidSystems/fluidSystemsTesting](fluidSystems/fluidSystemsTesting/) | **Complete** | Test campaigns from concept through development, qualification and flight acceptance |
| [propulsion](propulsion/) | Scaffolded | Liquid bipropellant engines: combustion devices, turbomachinery, engine cycles, nozzle performance, ignition and transients, hot fire test |
| [aerospaceStructures](aerospaceStructures/) | **Complete** | Shell buckling, sandwich panels, bolted and bonded joints, modal analysis, load paths, tanks |
| [aerospaceMaterials](aerospaceMaterials/) | **Complete** | Alloy selection, allowables, fracture, corrosion, plus ten process sub-domains covering additive, casting, wrought, forming, machining, joining and post-processing |
| [thermalManagement](thermalManagement/) | **Complete** | Thermal protection systems, thermal control, radiators, heat pipes, aeroheating |
| [environmentsAndLoads](environmentsAndLoads/) | **Complete** | Random vibration, acoustics, shock, aerodynamic loads, load cases, coupled loads analysis |
| [vehicleArchitecture](vehicleArchitecture/) | Scaffolded | Staging, sizing, mass fractions, propellant selection, trade studies, mass properties |
| [mechanismsAndSeparation](mechanismsAndSeparation/) | Scaffolded | Pyrotechnics, separation systems, springs, latches, actuators, deployment |
| [electricalPower](electricalPower/) | Scaffolded | Batteries, power distribution, harnessing, grounding and bonding, EMI |
| [recoveryAndReusability](recoveryAndReusability/) | Scaffolded | Entry, descent and landing, refurbishment, life tracking, economics |
| [reliabilityAndMissionAssurance](reliabilityAndMissionAssurance/) | Scaffolded | FMECA, fault trees, reliability allocation, redundancy, quality systems |
| [avionicsAndGNC](avionicsAndGNC/) | Scaffolded | Flight computers, sensors, guidance, navigation, control, telemetry |
| [groundSystemsAndOperations](groundSystemsAndOperations/) | Scaffolded | Pads, umbilicals, propellant handling, countdown, launch operations |
| [manufacturingAndAssembly](manufacturingAndAssembly/) | Scaffolded | Welding, composites, machining, tooling, inspection and NDE, supply chain |
| [rangeSafetyAndFTS](rangeSafetyAndFTS/) | Scaffolded | Flight termination, trajectory limits, autonomous FTS, debris analysis |

Propulsion is covered here, as a hub with six sub-domains, and it is deliberately liquid bipropellant. Nozzle contour generation remains in the separate NOVA suite: this repository covers nozzle performance and area ratio selection, which are the decisions, and points at NOVA for the geometry. Reimplementing a method-of-characteristics generator here would create a second implementation with nothing enforcing agreement between them.

---

## The common package

[common/](common/) holds what more than one domain needs, so it is defined once rather than copied fifteen times.

| Module | Provides |
|---|---|
| [units.py](common/units.py) | Every unit conversion constant, US Standard Atmosphere 1976 |
| [fluidProperties.py](common/fluidProperties.py) | `fluidProps` and its REFPROP / CoolProp / correlation backends, species molar mass, leak rate and SCFM conversions |
| [materials.py](common/materials.py) | Alloy properties with a cryogenic strength correction, surface roughness by process |
| [structures.py](common/structures.py) | Thin wall relations general enough for more than one domain |
| [solvers.py](common/solvers.py) | `secantSolve` and `solveForUnknown` |
| [reporting.py](common/reporting.py) | `applyInputs` (the `setInputs` implementation) and `formatReportTable` |
| [errors.py](common/errors.py) | `EngineeringError` base and the generic error types |

**The test for whether something belongs in `common`:** name the second domain that needs it. If you cannot, it belongs to the one domain that does.

Each domain's `utils.py` locates the package by walking up from its own file until it finds `common/`, then re-exports what it needs. That keeps the namespace flat inside a domain, works from any nesting depth, and matches the `sys.path` approach NOVA and propulsionDesign already use.

```python
# Inside any domain library, this just works
from utils import fluidProps, materialProperties, PA_PER_PSIA, formatReportTable
```

---

## Installation

Targets **Python 3.10** on Windows.

```bash
pip install -r dependencies.txt
```

Fluid properties dispatch to REFPROP first and fall back to CoolProp. **CoolProp alone is sufficient** to run everything here; REFPROP adds accuracy and mixture support.

## Testing

From the repository root, across every domain:

```bash
python -m pytest -v
```

Or within a single domain:

```bash
cd fluidSystems && python -m pytest tests/ -v
```

Tests are organized in three tiers throughout: pure constants and conversions with no backend, validation against published references, and self-consistency identities and round trips. Every test carries a docstring explaining what defect it exists to catch.

## Worked examples

Each completed domain has a `codeInterface.py` driver that runs a realistic case end to end:

```bash
python fluidSystems/codeInterface.py                       # 100 N hydrazine feed system, chamber to bottle
python fluidSystems/fluidSystemsTesting/codeInterface.py   # the qualification campaign for that system
```

---

## Repository structure

```
orbitalRockets/
├── README.md
├── dependencies.txt
├── pytest.ini
├── common/                        shared foundation, seven modules
└── <domain>/
    ├── README.md                  what it covers, document index with status
    ├── codeInterface.py           worked example driver
    ├── docs/                      reference documentation
    ├── <domain>Library/           one class per component
    └── tests/                     tiered pytest suite
```

---

## License

[MIT](LICENSE). Copyright (c) 2026 Sean Bowman.

This is reference and analysis material. The MIT warranty disclaimer applies in full: nothing here substitutes for qualified engineering judgment, an independent check, or the governing standard for a given application.

---

Sean Bowman
