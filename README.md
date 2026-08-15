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

**All sixteen are complete.** Each domain's README states what it carries, and its `docs/ValidationReferences.md` states what that rests on and where it runs out.

[validation/](validation/) holds the comparisons against published hardware, and the register of what has not been checked against anything external. A tool that has only been checked against itself has not been checked.

| Domain | Status | Covers |
|---|---|---|
| [fluidSystems](fluidSystems/) | **Complete** | Valves, lines, orifices, fittings, seals, leaks, welds, insulation, water hammer, hydrazine, catalyst beds, monopropellant thrusters, pressurization |
| [fluidSystems/fluidSystemsTesting](fluidSystems/fluidSystemsTesting/) | **Complete** | Test campaigns from concept through development, qualification and flight acceptance |
| [propulsion](propulsion/) | **Complete** | Liquid bipropellant engines: combustion devices, turbomachinery, engine cycles, nozzle performance, ignition and transients, hot fire test |
| [aerospaceStructures](aerospaceStructures/) | **Complete** | Shell buckling, sandwich panels, bolted and bonded joints, modal analysis, load paths, tanks |
| [aerospaceMaterials](aerospaceMaterials/) | **Complete** | Alloy selection, allowables, fracture, corrosion, plus ten process sub-domains covering additive, casting, wrought, forming, machining, joining and post-processing |
| [thermalManagement](thermalManagement/) | **Complete** | Thermal protection systems, thermal control, radiators, heat pipes, aeroheating |
| [environmentsAndLoads](environmentsAndLoads/) | **Complete** | Random vibration, acoustics, shock, aerodynamic loads, load cases, coupled loads analysis |
| [vehicleArchitecture](vehicleArchitecture/) | **Complete** | Staging, sizing, mass fractions, propellant selection, trade studies, mass properties |
| [mechanismsAndSeparation](mechanismsAndSeparation/) | **Complete** | Pyrotechnics, separation systems, springs, latches, actuators, deployment |
| [electricalPower](electricalPower/) | **Complete** | Batteries, power distribution, harnessing, grounding and bonding, EMI |
| [recoveryAndReusability](recoveryAndReusability/) | **Complete** | Entry, descent and landing, refurbishment, life tracking, economics |
| [reliabilityAndMissionAssurance](reliabilityAndMissionAssurance/) | **Complete** | FMECA, fault trees, reliability allocation, redundancy, quality systems |
| [avionicsAndGNC](avionicsAndGNC/) | **Complete** | Flight computers, sensors, guidance, navigation, control, telemetry |
| [groundSystemsAndOperations](groundSystemsAndOperations/) | **Complete** | Pads, umbilicals, propellant handling, countdown, launch operations |
| [manufacturingAndAssembly](manufacturingAndAssembly/) | **Complete** | Welding, composites, machining, tooling, inspection and NDE, supply chain |
| [rangeSafetyAndFTS](rangeSafetyAndFTS/) | **Complete** | Flight termination, trajectory limits, autonomous FTS, debris analysis |

Propulsion is covered here, as a hub with six sub-domains, and it is deliberately liquid bipropellant. Nozzle contour generation remains in the separate NOVA suite: this repository covers nozzle performance and area ratio selection, which are the decisions, and points at NOVA for the geometry. Reimplementing a method-of-characteristics generator here would create a second implementation with nothing enforcing agreement between them.

---

## The common package

[common/](common/) holds what more than one domain needs, so it is defined once rather than copied fifteen times.

| Module | Provides |
|---|---|
| [units.py](common/units.py) | Every unit conversion constant, US Standard Atmosphere 1976 |
| [fluidProperties.py](common/fluidProperties.py) | `fluidProps` and its REFPROP / CoolProp / correlation backends, species molar mass, leak rate and SCFM conversions |
| [materials.py](common/materials.py) | Alloy properties with a cryogenic strength correction, surface roughness by process |
| [cryogenicProperties.py](common/cryogenicProperties.py) | NIST cryogenic specific heat curve fits, and the enthalpy integral a chill-down needs |
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

## How a domain is built

Five stages, in this order. Library before documents, so that every number a document cites has
already been produced by running code.

| Stage | Content | Done when |
|---|---|---|
| **1** | Component classes and a tiered test suite | Tests pass, uniquely named helper module in place |
| **2** | `codeInterface.py` worked example, driven by a JSON asset | Runs end to end, numbers verified |
| **3** | Documents, written against stage 2 numbers | Every numeric claim produced by code, every snippet executes |
| **4** | Verification: links resolve, snippets run, full suite green | Nothing in the domain contradicts anything else in it |
| **5** | Validation against something published | An external reference case exists, or the register says why not |

**Stage 5 exists because stages 1 to 4 cannot catch a wrong model.** They establish that the code
does what it was written to do. They say nothing about whether what it was written to do is right,
and 666 passing tests once failed to catch a placeholder heat flux wrong by a factor of three that
had a document written against its conclusion.

**The hard part of stage 5 is not finding a reference, it is establishing that it is the same
quantity.** The propulsion library models a thrust chamber; a published engine specific impulse is a
whole-engine figure that includes the cycle. RS-25 is closed cycle and validates the library to
1.7 per cent. F-1 is open cycle and disagrees by 8.1 per cent, and stays in the reference set
precisely because it marks the boundary of what the library covers.

### Three naming rules, all from the same cause

A flat `sys.path` resolves identically named modules in different domains to one entry in
`sys.modules`. The first one imported wins and the rest silently receive it. This has bitten the
repository three times in three different places, so all three rules are written down rather than
rediscovered.

**The library helper module must be uniquely named**: `structuresUtils`, `thermalUtils`,
`rangeSafetyUtils`, never `utils`. Sharing the name works by accident for the shared re-exported
foundation and fails for anything only one domain defines. `fluidSystems` predates the rule and is
the one remaining exception.

**Test file basenames must be unique across the whole repository.**
`propulsion/tests/testWorkedExample.py` and `thermalManagement/tests/testWorkedExample.py` cannot
coexist: pytest imports test modules by basename and raises an import file mismatch. Name them for
the domain, as `testPropulsionWorkedExample.py`.

**`codeInterface.py` must be loaded by explicit path, never by `import codeInterface`.** Every
domain has one at its root and none can be renamed without breaking the documented
`python <domain>/codeInterface.py` entry point, so the fix belongs at the import rather than at the
file. Load it with `importlib.util.spec_from_file_location` under a domain-unique module name.

**The last one is the dangerous member of the family, because it fails silently rather than
loudly**: a second domain's example tests pass while asserting against the first domain's module.
Every worked-example test file carries a `testTheExampleLoadedIsThisDomainsOwn` guard.

### Depth scales to the computable content

A class that wraps a lookup table is a class not to build, and the reasoning behind each
documentation-only decision is written into the relevant overview rather than assumed. Three
`aerospaceMaterials` sub-domains are deliberately documentation only: `wroughtMaterials` because
product form and temper are database axes, `joiningProcesses` because `Weld.py` already owns it,
and `additiveOther` because each process is one equation belonging in `ProcessComparison`.

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
