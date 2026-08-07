# aerospaceMaterials

**Materials Selection, Allowables and Processing for Launch Vehicles**

Materials is where a design stops being a drawing and becomes something that can be bought, made and trusted. This domain covers the alloys actually used on launch vehicles, how their design allowables are established, how processing changes them, and the failure mechanisms that belong to the material rather than to the design.

It carries ten process sub-domains, because the route a part is made by sets its allowable and that frequently matters more than the choice of alloy.

---

## Design Ethos

- A handbook value is not a design allowable. A-basis and B-basis mean something specific and the gap is about 9 percent at n = 30.
- Processing changes properties more than alloy selection does. The same alloy in two conditions is two materials.
- Every material is compatible with something and catastrophic with something else. There is no universally good choice.
- Lead time and supply chain are material properties in every practical sense.
- The failure mode you did not design for is usually a materials mechanism: SCC, embrittlement, sensitization, creep.
- Every number carries its source, and an author estimate can never be mistaken for an MMPDS tolerance limit.

---

## Worked example

[`codeInterface.py`](codeInterface.py) sizes the GHe pressurant bottle inherited from the [fluidSystems worked example](../fluidSystems/codeInterface.py), which produced a 30 MPa, 3.23 L bottle holding 0.1394 kg of helium and stopped there because sizing a pressure vessel is a materials problem.

```bash
python codeInterface.py
```

| Inherited from the fluid analysis | Value | What it drives |
|---|---|---|
| Bottle pressure | 30 MPa | Membrane stress |
| Bottle volume | 3.23 L | 183.4 mm sphere |
| Thruster valve bore | 4.76 mm | The LPBF manifold channel |

### What it produces

| Quantity | Value |
|---|---|
| Selected material | Ti-6Al-4V annealed |
| A-basis ultimate from 30 specimens | 869.4 MPa (k = 3.064) |
| Design ultimate after the girth weld | 825.9 MPa |
| **Governing wall criterion** | **No yield during the 1.5x proof test** |
| Wall thickness | 2.623 mm, D/t = 70 |
| Bottle mass | 1.228 kg |
| Critical flaw depth | 5.19 mm |
| Leak before burst | Satisfied, ratio 1.98 |
| Crack growth life | 2873 cycles against 500 required |
| Cheapest route | Investment cast |
| Boss to bracket galvanic couple | 0.75 V against a 0.15 V limit, rejected |

### The findings, which are the point

1. **The proof test governs the wall, not burst.** Burst at FS 1.5 gives 2.50 mm and yield at MEOP gives 2.19 mm, but keeping the bottle below yield during its own 1.5x proof test needs 2.62 mm. Sized on burst alone, every flight article would be damaged by the test meant to qualify it.
2. **Titanium wins on strength to weight and is prohibited in the oxidiser version.** Change the fluid to LOX and it is rejected outright, not downgraded, because it is impact sensitive in oxygen and burns.
3. **The single load path costs 4.1 percent of the allowable.** A pressure vessel wall cannot redistribute load, so it requires A-basis rather than B. Part of that gap is the material and part is simply how much testing was done.
4. **Leak before burst is satisfied, and the STA condition would lose it.** Solution treating and aging raises the yield strength and cuts the critical flaw to 2.22 mm, below the wall. The stronger heat treatment makes the vessel less safe, which no strength table shows.
5. **The 316L feed line pits at ambient.** PREN 26.1 gives a critical pitting temperature of -6 degC, so at a coastal site 316L is below its own threshold at every service temperature.

---

## Library

| Class | Computes |
|---|---|
| [`MaterialDatabase`](aerospaceMaterialsLibrary/MaterialDatabase.py) | Property query across alloy, condition, temperature, orientation and basis, with provenance |
| [`Allowables`](aerospaceMaterialsLibrary/Allowables.py) | A and B basis tolerance limits, three independent k-factor routes, the knockdown chain |
| [`MaterialSelector`](aerospaceMaterialsLibrary/MaterialSelector.py) | Ashby index ranking with a per-candidate rejection audit trail |
| [`DamageTolerance`](aerospaceMaterialsLibrary/DamageTolerance.py) | Critical flaw, leak before burst, proof as inspection, Paris crack growth |
| [`CorrosionAssessment`](aerospaceMaterialsLibrary/CorrosionAssessment.py) | Galvanic penetration rate, PREN and CPT, SCC margin, hydrogen bake trigger |
| [`HeatTreatment`](aerospaceMaterialsLibrary/HeatTreatment.py) | Staley quench factor, aging equivalence, sensitization, distortion, HIP |
| [`ProcessComparison`](aerospaceMaterialsLibrary/ProcessComparison.py) | Route trade: buy-to-fly, allowable knockdown, mass, cost index, lead time |

The data lives in [`materialData.py`](aerospaceMaterialsLibrary/materialData.py): **31 alloys, 41 material-condition records**, with temperature dependence stored as ratio-to-room-temperature curves and a source key on every property block.

**Zero drift with the shared package.** The nine alloys carried by [`common/materials.py`](../common/materials.py) are imported and merged at load rather than re-typed, so 316L's yield strength is written down in exactly one place in the repository. A test asserts equality to 1e-12.

```python
import sys
sys.path.insert(0, 'aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial

properties = queryMaterial('Ti-6Al-4V', 'annealed', 293.15, orientation = 'L', basis = 'A')
print(properties['ultimateStrength'] / 1.0e6)   # 897.0 MPa
print(properties['basisAvailable'])              # True, and False where no allowable exists
```

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [MaterialsOverview.md](docs/MaterialsOverview.md) | Hub: the selection process, the knockdown chain, the prohibitions | complete |
| [AllowablesAndStatistics.md](docs/AllowablesAndStatistics.md) | A and B basis, k-factors, sample size, ANOVA, knockdowns | complete |
| [AluminumAlloys.md](docs/AluminumAlloys.md) | 2xxx, 6xxx, 7xxx, Al-Li, tempers, weldability, SCC | complete |
| [SteelsAndStainless.md](docs/SteelsAndStainless.md) | Austenitic, PH, low alloy, sensitization, pitting | complete |
| [NickelAndSuperalloys.md](docs/NickelAndSuperalloys.md) | 625, 718, Monel, Haynes, hot section use, welding | complete |
| [TitaniumAlloys.md](docs/TitaniumAlloys.md) | Ti-6Al-4V and ELI, the oxygen prohibition, alpha case | complete |
| [CopperAlloys.md](docs/CopperAlloys.md) | GRCop, NARloy-Z, chamber liners, thermal ratcheting | complete |
| [CompositesAndLaminates.md](docs/CompositesAndLaminates.md) | Laminates, COPV overwrap, stress rupture, BVID | complete |
| [PolymersAndElastomers.md](docs/PolymersAndElastomers.md) | Glass transition, permeation, outgassing, compression set | complete |
| [CryogenicMaterials.md](docs/CryogenicMaterials.md) | Property curves, DBTT data, contraction, conductivity | complete |
| [CorrosionAndSCC.md](docs/CorrosionAndSCC.md) | Galvanic rates, area ratio, PREN, SCC thresholds | complete |
| [HydrogenEmbrittlement.md](docs/HydrogenEmbrittlement.md) | Mechanisms, susceptibility, the temperature peak, bake-out | complete |
| [FractureAndDamageTolerance.md](docs/FractureAndDamageTolerance.md) | Critical flaw, leak before burst, proof as NDE, crack growth | complete |
| [HeatTreatment.md](docs/HeatTreatment.md) | Quench factor, hardenability, aging, sensitization, HIP | complete |
| [ProcessRouteSelection.md](docs/ProcessRouteSelection.md) | Buy-to-fly, knockdowns, the eleven routes, the ten sub-domains | complete |
| [MaterialQualification.md](docs/MaterialQualification.md) | Material and process specs, allowables, equivalency, traceability | complete |
| [SupplyChainAndLeadTime.md](docs/SupplyChainAndLeadTime.md) | Lead times, mill forms, cost ratios, counterfeit, obsolescence | complete |
| [StandardsIndex.md](docs/StandardsIndex.md) | Annotated index of the governing materials standards | complete |

---

## Process sub-domains

The route a part is made by sets its allowable, so the process depth lives here rather than in [manufacturingAndAssembly](../manufacturingAndAssembly/), which keeps the cross-cutting view.

| Sub-domain | Library | Status |
|---|---|---|
| [additiveLPBF](additiveLPBF/) | Planned | scaffolded |
| [additiveOther](additiveOther/) | Docs only | planned |
| [spinCasting](spinCasting/) | Planned | scaffolded |
| [castingProcesses](castingProcesses/) | Planned | planned |
| [wroughtMaterials](wroughtMaterials/) | Docs only | scaffolded |
| [formingProcesses](formingProcesses/) | Planned | planned |
| [machiningProcesses](machiningProcesses/) | Planned | planned |
| [joiningProcesses](joiningProcesses/) | Docs only | planned |
| [postProcessing](postProcessing/) | Planned | planned |
| [extrusionHoning](extrusionHoning/) | Planned | scaffolded |

**Three are deliberately docs-only.** `wroughtMaterials` because product form, temper and grain direction are database axes rather than computations. `joiningProcesses` because [fluidSystems Weld.py](../fluidSystems/fluidSystemsLibrary/Weld.py) already does joint efficiency and HAZ knockdown, and duplicating it would create drift. `additiveOther` because each process is one or two equations that belong in the route table.

---

## Testing

```bash
python -m pytest tests/ -v
```

Three tiers, matching the repository convention. Tier 1 covers database structural integrity and the guards that stop the classes doing harm. Tier 2 validates against MMPDS k-factor tables, the PREN and CPT correlations, the 7075 through-hardening limit and the ASTM F1940 bake trigger. Tier 3 covers self-consistency, including a cross-check of three independent k-factor implementations against each other.

**Cross-domain drift tests** assert that this database agrees with `common/materials.py` on the nine shared alloys, that the as-welded aluminium condition matches `Weld.HAZ_KNOCKDOWN`, and that every numeric property resolves to a declared source.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [aerospaceStructures](../aerospaceStructures/) | Supplies every allowable the structural analysis consumes |
| [fluidSystems](../fluidSystems/) | Compatibility, cryogenic properties, weld knockdowns, seal materials |
| [fluidSystems/fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/) | Proof and burst levels, and the fracture control that proof testing provides |
| [manufacturingAndAssembly](../manufacturingAndAssembly/) | The cross-cutting view: process selection, make-buy, tooling, assembly, rate |

---

Sean Bowman
