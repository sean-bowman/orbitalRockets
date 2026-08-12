[Home](README.md) > Buildout

# Buildout Checklist

The master list of what is built and what is not, kept current as the repository is populated.

**Last updated:** 10 August 2026, at commit `10a8c5e`.
**Repository totals:** 405 markdown documents, 1299 passing tests, 12 domains complete of 16. Ten areas validated at hardware level and five at standard level.

---

## Contents

- [How a domain is built](#how-a-domain-is-built)
- [Depth policy](#depth-policy)
- [Build order](#build-order)
- [Complete](#complete)
- [In progress](#in-progress)
- [propulsion, complete](#propulsion-complete)
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

1. ~~`propulsion` and its six sub-domains~~ **done**
2. ~~`vehicleArchitecture`~~ **done**
3. ~~`mechanismsAndSeparation`~~ **done**
4. ~~`electricalPower`~~ **done**
5. ~~`avionicsAndGNC`~~ **done**
6. ~~`groundSystemsAndOperations`~~ **done**
7. `recoveryAndReusability`
8. `manufacturingAndAssembly`
9. `rangeSafetyAndFTS`
10. `reliabilityAndMissionAssurance`

---

## Complete

| Domain | Depth | Docs | Classes | Stage 5 validation |
|---|---|---|---|---|
| [fluidSystems](fluidSystems/) | Full | 25 | 17 | **hardware**, IAPWS-95 water density |
| [fluidSystems/fluidSystemsTesting](fluidSystems/fluidSystemsTesting/) | Full | 17 | 8 | internal, outstanding |
| [aerospaceMaterials](aerospaceMaterials/) | Full | 18 | 8 | internal, against MMPDS through `common/materials.py`, outstanding |
| [aerospaceStructures](aerospaceStructures/) | Full | 16 | 9 | standard, SP-8007 knockdown |
| [environmentsAndLoads](environmentsAndLoads/) | Full | 14 | 6 | **hardware**, GEVS 14.1 Grms |
| [thermalManagement](thermalManagement/) | Full | 13 | 6 | **hardware**, Stefan-Boltzmann and solar constant |
| [vehicleArchitecture](vehicleArchitecture/) | Full | 14 | 4 | **hardware**, Falcon 9 Block 5 stage masses |
| [mechanismsAndSeparation](mechanismsAndSeparation/) | Full | 12 | 5 | **standard**, NASA-STD-5017B read in full |
| [electricalPower](electricalPower/) | Full | 12 | 4 | **standard**, the AWG definition, exact to four figures |
| [avionicsAndGNC](avionicsAndGNC/) | Full | 12 | 3 | internal, no external anchor, outstanding |
| [groundSystemsAndOperations](groundSystemsAndOperations/) | Light | 13 | 4 | **standard**, DESR 6055.09 read in full |

**Four reach hardware level and three reach standard level.** Each carries a
`docs/ValidationReferences.md` bibliography recording what it was checked against, at what level,
and what remains unchecked.

Three remain internal. aerospaceMaterials is seeded from an MMPDS-derived table and tested against
it, and fluidSystemsTesting is a process domain rather than a physics one. **avionicsAndGNC is the
weakest-anchored domain in the repository**, with no hardware source and no standard read, and it is
also the domain whose conclusions depend least on its numbers: the results follow from integration
orders and sums rather than from values. All three are listed as outstanding rather than closed.

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

Nothing. The next domain in the build order is [recoveryAndReusability](recoveryAndReusability/), which is scaffolded and planned to full depth.

### A naming rule the scaffold does not follow

Every unbuilt domain still ships a library helper called `utils.py`, which violates the first of the three naming rules above. `vehicleArchitecture` renamed its to `vehicleUtils.py` on build-out and the remaining nine should do the same as they are built. The two legacy domains that still import from `utils`, `aerospaceMaterials` and `fluidSystems`, predate the rule and are left alone rather than churned.

---

## propulsion, complete

| Domain | Depth | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---|---|---|---|---|
| [propulsion](propulsion/) hub | Full | **done** | **done** | **done** | **done**, and **validated** against RS-25 |

### propulsion sub-domains

| Sub-domain | Depth | Stage 1 | Stage 2 | Stage 3 | Stage 4 |
|---|---|---|---|---|---|
| [combustionDevices](propulsion/combustionDevices/) | Full | **done** | **done** | **done** | **done**, bounded only |
| [turbomachinery](propulsion/turbomachinery/) | Full | **done** | **done** | **done** | **done**, **hardware validated** |
| [engineCycles](propulsion/engineCycles/) | Full | **done** | **done** | **done** | **done**, **hardware validated** |
| [nozzles](propulsion/nozzles/) | Full | **done** | **done** | **done** | **done**, bounded |
| [ignitionAndStart](propulsion/ignitionAndStart/) | Full | **done** | **done** | **done** | **done**, one hardware source and four gaps |
| [propulsionTesting](propulsion/propulsionTesting/) | Light | **done** | **done** | **done** | **done**, one hardware source and three gaps |

**Nozzle contour generation for manufacture stays out of this repository, and the boundary is fidelity rather than subject.** The NOVA suite generates method of characteristics contours and cooling channel geometry, and reimplementing that here would create a second implementation with nothing enforcing agreement between them.

**That argument was stretched too far once and it cost a published finding.** It was read as "compute no geometry at all", which left the divergence loss depending on a lookup table of exit angles. The table gave an 80 per cent bell 8 degrees regardless of area ratio; Rao's approximation gives 11.5 at an area ratio of 20. Correcting it doubled the divergence loss and inverted the sub-domain's conclusion about where the largest loss is. `NozzleContour` now computes the angle in closed form at conceptual fidelity, which does not overlap a characteristics solution.

**The general rule this produced, carried forward to every remaining domain:** an argument against duplicating an external tool is not an argument against every calculation in that tool's subject. Check what the neighbouring tool actually computes before declining to compute anything nearby, and never let a lookup table stand in for an equation that exists in closed form.

---

## Scaffolded, not started

These have a `utils.py` bootstrap stub, an empty `docs/`, an empty `tests/`, and are listed in `pytest.ini`.

| Domain | Planned depth | Why that depth |
|---|---|---|
| [recoveryAndReusability](recoveryAndReusability/) | Full | Entry ballistic coefficient, parachute sizing, propulsive landing budgets, and life tracking against the fatigue work already in structures |
| [reliabilityAndMissionAssurance](reliabilityAndMissionAssurance/) | Light | FMECA and fault trees are process. The computable part is reliability allocation, redundancy arithmetic and confidence from test counts, which is a small library |

---

## Bare, not scaffolded

README and `objectives.md` only. No `docs/`, no `tests/`, no library, and not yet in `pytest.ini`. Scaffolding is part of the build.

| Domain | Planned depth | Why that depth |
|---|---|---|
| [manufacturingAndAssembly](manufacturingAndAssembly/) | Light | The process physics already lives in the ten `aerospaceMaterials` sub-domains. What is left is assembly sequence, tooling and inspection planning |
| [rangeSafetyAndFTS](rangeSafetyAndFTS/) | Light | Debris footprint and instantaneous impact point compute. The rest is regulation, and the standards index carries most of the value |

---

## Validation retrofit, outstanding

Six domains were completed before stage 5 existed. Each needs at least one comparison against
published hardware, in this order, chosen by how much downstream work depends on the domain being
right.

| Domain | Done | Level reached | What still limits it |
|---|---|---|---|
| [aerospaceStructures](aerospaceStructures/) | yes | Standard | The SP-8007 curve itself is unvalidated. Reproducing it proves the implementation and nothing about the correlation |
| [thermalManagement](thermalManagement/) | yes | Hardware | Only the radiation path. Conduction and the contact conductance table remain unchecked |
| [fluidSystems](fluidSystems/) | yes | Hardware | Properties only. Line pressure drop against Crane TP-410 worked examples is still outstanding |
| [environmentsAndLoads](environmentsAndLoads/) | yes | Hardware | Random vibration only. Acoustics and shock remain unchecked |
| [aerospaceMaterials](aerospaceMaterials/) | no | Internal | Needs a real allowables comparison with published k-factors |
| [fluidSystems/fluidSystemsTesting](fluidSystems/fluidSystemsTesting/) | no | Internal | Process domain, lowest priority |

**The most consequential unvalidated number in the repository is the SP-8007 shell buckling
knockdown.** It converts a classical stress that overpredicts by four and a half into a design value,
more than one domain depends on it, and reproducing the published curve to 1e-4 says nothing about
whether the curve is right. Closing that needs the shell buckling test databases compiled since
1968.

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
