[Home](README.md) > Buildout

# Buildout Checklist

The master list of what is built and what is not, kept current as the repository is populated.

**Last updated:** 08 August 2026, at commit `d2129c4`.
**Repository totals:** 294 markdown documents, 621 passing tests, 6 domains complete of 16, propulsion hub done.

---

## Contents

- [How a domain is built](#how-a-domain-is-built)
- [Depth policy](#depth-policy)
- [Build order](#build-order)
- [Complete](#complete)
- [In progress](#in-progress)
- [Scaffolded, not started](#scaffolded-not-started)
- [Bare, not scaffolded](#bare-not-scaffolded)
- [Repository wide verification](#repository-wide-verification)

---

## How a domain is built

Four stages, in this order. Library before documents, so that every number a document cites has already been produced by running code.

| Stage | Content | Done when |
|---|---|---|
| **1** | Component classes and a tiered test suite | Tests pass, uniquely named helper module in place |
| **2** | `codeInterface.py` worked example, driven by a JSON asset | Runs end to end, numbers verified, example tests written |
| **3** | Documents, written against stage 2 numbers | Every numeric claim produced by code, every snippet executes |
| **4** | Verification, README status, commit, push | Links resolve, no dashes, snippets run, full suite green |
| **5** | Validation against published hardware | At least one external reference case, or an entry in the unvalidated register saying why not |

### Three naming rules, all from the same cause

A flat `sys.path` resolves identically named modules in different domains to one entry in `sys.modules`. The first one imported wins and the rest silently receive it. This has bitten the repository three times in three different places, so all three rules are written down here rather than rediscovered.

**The library helper module must be uniquely named**: `structuresUtils`, `environmentsUtils`, `thermalUtils`, `propulsionUtils`, never `utils`. Sharing the name works by accident for the shared re-exported foundation and fails for anything only one domain defines.

**Test file basenames must be unique across the whole repository.** `propulsion/tests/testWorkedExample.py` and `thermalManagement/tests/testWorkedExample.py` cannot coexist: pytest imports test modules by basename and raises an import file mismatch. Name them for the domain, as `testPropulsionWorkedExample.py`.

**`codeInterface.py` must be loaded by explicit path, never by `import codeInterface`.** Every domain has one at its root and they cannot be renamed without breaking the documented `python <domain>/codeInterface.py` entry point, so the fix belongs at the import rather than the file. Load it with `importlib.util.spec_from_file_location` under a domain-unique module name.

That last one is the dangerous member of the family, because it fails silently rather than loudly: a second domain's example tests pass while asserting against the first domain's module. Both worked-example test files carry a `testTheExampleLoadedIsThisDomainsOwn` guard, and every new domain should copy it.

### Stage 5 exists because stage 4 does not catch a wrong model

Stages 1 to 4 check that the code does what it was written to do. They do not check whether what it
was written to do is right, and 666 passing tests did not catch a placeholder heat flux that was
wrong by a factor of three and had a document written against its conclusion.

Every domain must therefore compare at least one result against something published for real
hardware, or record in [validation/referenceCases.py](validation/referenceCases.py) why it cannot.
The methodology, and the rule that no reference may be adjusted to make a test pass, are in
[validation/README.md](validation/README.md).

**The hard part is not finding a reference, it is establishing that it is the same quantity.** The
propulsion library models a thrust chamber; a published engine specific impulse is a whole-engine
figure that includes the cycle. RS-25 is closed cycle and validates the library to 1.7 per cent.
F-1 is open cycle and disagrees by 8.1 per cent, and is kept in the reference set precisely because
it marks the boundary of what the library covers.

---

## Depth policy

Depth scales to how much computable engineering a domain carries. A class that wraps a lookup table is a class not to build, and the reasoning behind each docs-only decision gets written down rather than assumed.

| Depth | What it means | Applies to |
|---|---|---|
| **Full** | Classes, worked example, 12 to 15 documents | Domains with real computable physics |
| **Light** | Fewer classes, 8 to 10 documents, worked example only if it earns one | Domains that are mostly process and judgement |
| **Docs only** | No library. The reasoning for why is written into the overview | Sub-domains whose content is database axes or lives elsewhere |

Three `aerospaceMaterials` sub-domains are deliberately docs only: `wroughtMaterials` because product form and temper are database axes, `joiningProcesses` because `Weld.py` already owns it, and `additiveOther` because each process is one equation belonging in `ProcessComparison`.

---

## Build order

Dependency driven. Propulsion first because it is the repository's stated identity and every domain it consumes is already complete. Reliability last because FMECA needs hardware to analyse.

1. `propulsion` and its six sub-domains
2. `vehicleArchitecture`
3. `mechanismsAndSeparation`
4. `electricalPower`
5. `avionicsAndGNC`
6. `groundSystemsAndOperations`
7. `recoveryAndReusability`
8. `manufacturingAndAssembly`
9. `rangeSafetyAndFTS`
10. `reliabilityAndMissionAssurance`

---

## Complete

| Domain | Depth | Docs | Classes | Stage 5 validation |
|---|---|---|---|---|
| [fluidSystems](fluidSystems/) | Full | 24 | 17 | **outstanding** |
| [fluidSystems/fluidSystemsTesting](fluidSystems/fluidSystemsTesting/) | Full | 17 | 8 | **outstanding** |
| [aerospaceMaterials](aerospaceMaterials/) | Full | 18 | 8 | partial, against MMPDS through `common/materials.py` |
| [aerospaceStructures](aerospaceStructures/) | Full | 15 | 9 | **outstanding** |
| [environmentsAndLoads](environmentsAndLoads/) | Full | 13 | 6 | **outstanding** |
| [thermalManagement](thermalManagement/) | Full | 12 | 6 | **outstanding** |

**The six completed domains predate stage 5 and none of them is validated against published
hardware.** That is the largest single piece of outstanding work in the repository and it is not
optional: a domain that has only been checked against itself has not been checked. The retrofit
order is below.

### aerospaceMaterials sub-domains

| Sub-domain | Depth | Docs | Classes |
|---|---|---|---|
| [additiveLPBF](aerospaceMaterials/additiveLPBF/) | Full | 15 | 4 |
| [additiveOther](aerospaceMaterials/additiveOther/) | Docs only | 10 | 0 |
| [castingProcesses](aerospaceMaterials/castingProcesses/) | Full | 11 | 2 |
| [extrusionHoning](aerospaceMaterials/extrusionHoning/) | Full | 9 | 2 |
| [formingProcesses](aerospaceMaterials/formingProcesses/) | Full | 12 | 2 |
| [joiningProcesses](aerospaceMaterials/joiningProcesses/) | Docs only | 11 | 0 |
| [machiningProcesses](aerospaceMaterials/machiningProcesses/) | Full | 12 | 2 |
| [postProcessing](aerospaceMaterials/postProcessing/) | Full | 14 | 2 |
| [spinCasting](aerospaceMaterials/spinCasting/) | Full | 14 | 2 |
| [wroughtMaterials](aerospaceMaterials/wroughtMaterials/) | Docs only | 14 | 0 |

---

## In progress

| Domain | Depth | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---|---|---|---|---|
| [propulsion](propulsion/) hub | Full | **done** | **done** | **done** | **done**, and **validated** against RS-25 |

### propulsion sub-domains

| Sub-domain | Depth | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---|---|---|---|---|
| [combustionDevices](propulsion/combustionDevices/) | Full | **done** | not started | not started | not started |
| [turbomachinery](propulsion/turbomachinery/) | Full | not started | not started | not started | not started |
| [engineCycles](propulsion/engineCycles/) | Full | not started | not started | not started | not started |
| [nozzles](propulsion/nozzles/) | Full | not started | not started | not started | not started |
| [ignitionAndStart](propulsion/ignitionAndStart/) | Full | not started | not started | not started | not started |
| [propulsionTesting](propulsion/propulsionTesting/) | Light | not started | not started | not started | not started |

**Nozzle contour generation stays out of this repository.** The NOVA suite generates method of characteristics contours and cooling channel geometry. The `nozzles` sub-domain covers performance, area ratio selection and the altitude compensation trades: the decisions, not the geometry generation. Reimplementing a contour generator here would create a second implementation with nothing enforcing agreement between them.

---

## Scaffolded, not started

These have a `utils.py` bootstrap stub, an empty `docs/`, an empty `tests/`, and are listed in `pytest.ini`.

| Domain | Planned depth | Why that depth |
|---|---|---|
| [vehicleArchitecture](vehicleArchitecture/) | Full | Tsiolkovsky, staging optimisation, mass fractions and propellant selection are all computable, and the domain closes the loop back to propulsion |
| [mechanismsAndSeparation](mechanismsAndSeparation/) | Full | Spring energy, separation dynamics, pyrotechnic shock and latch kinematics are real mechanics |
| [electricalPower](electricalPower/) | Full | Battery sizing, harness voltage drop, load profiles and grounding topology all compute |
| [recoveryAndReusability](recoveryAndReusability/) | Full | Entry ballistic coefficient, parachute sizing, propulsive landing budgets, and life tracking against the fatigue work already in structures |
| [reliabilityAndMissionAssurance](reliabilityAndMissionAssurance/) | Light | FMECA and fault trees are process. The computable part is reliability allocation, redundancy arithmetic and confidence from test counts, which is a small library |

---

## Bare, not scaffolded

README and `objectives.md` only. No `docs/`, no `tests/`, no library, and not yet in `pytest.ini`. Scaffolding is part of the build.

| Domain | Planned depth | Why that depth |
|---|---|---|
| [avionicsAndGNC](avionicsAndGNC/) | Full | Sensor error budgets, navigation drift, control authority and link budgets are quantitative |
| [groundSystemsAndOperations](groundSystemsAndOperations/) | Light | Mostly procedure and facility design. The computable part is propellant loading, chilldown and countdown timeline arithmetic |
| [manufacturingAndAssembly](manufacturingAndAssembly/) | Light | The process physics already lives in the ten `aerospaceMaterials` sub-domains. What is left is assembly sequence, tooling and inspection planning |
| [rangeSafetyAndFTS](rangeSafetyAndFTS/) | Light | Debris footprint and instantaneous impact point compute. The rest is regulation, and the standards index carries most of the value |

---

## Validation retrofit, outstanding

Six domains were completed before stage 5 existed. Each needs at least one comparison against
published hardware, in this order, chosen by how much downstream work depends on the domain being
right.

| Order | Domain | Candidate reference |
|---|---|---|
| 1 | [aerospaceStructures](aerospaceStructures/) | NASA SP-8007 shell buckling test correlation data, which is the basis of the knockdown factor already implemented |
| 2 | [thermalManagement](thermalManagement/) | A published spacecraft thermal balance case, or the Stefan-Boltzmann equilibrium of a known coated surface |
| 3 | [fluidSystems](fluidSystems/) | Crane TP-410 worked examples for line pressure drop, and REFPROP as ground truth for properties |
| 4 | [environmentsAndLoads](environmentsAndLoads/) | A published qualification specification, GEVS or a launch vehicle user guide, against a derived level |
| 5 | [aerospaceMaterials](aerospaceMaterials/) | Extend the existing MMPDS seed agreement into a real allowables comparison with published k-factors |
| 6 | [fluidSystems/fluidSystemsTesting](fluidSystems/fluidSystemsTesting/) | Lowest priority: the domain is process rather than physics and has less to get numerically wrong |

**aerospaceStructures is first** because shell buckling knockdowns are the single most consequential
empirical factor in the repository, they are used by more than one domain, and SP-8007 carries the
scatter data the knockdown was fitted to.

---

## Repository wide verification

Run before every commit that touches documents.

| Check | What it catches |
|---|---|
| Full test suite | Everything the tests cover |
| Markdown link walk | Broken links, including into other domains |
| Escape check | Links pointing outside the repository |
| Dash check | Em and en dashes, which are not house style |
| Snippet execution | Every documented python fence, run in a subprocess |
| Worked example run | That the example still produces the numbers its documents cite |
| Cross-domain drift tests | Tables duplicated across domains, read with `ast` rather than imported |
| Validation against published hardware | A model that is wrong in a way internal consistency cannot see |

**Every numeric claim in a document has to be produced by running code.** That rule has caught more errors than every other check combined, including twenty seven broken snippets in `aerospaceMaterials` that only failed when executed.

---

Sean Bowman
