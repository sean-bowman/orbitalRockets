[Home](../README.md) > Materials Overview

# Materials Overview

## Contents

- [Overview](#overview)
- [The one distinction that matters most](#the-one-distinction-that-matters-most)
- [The selection process](#the-selection-process)
- [The knockdown chain](#the-knockdown-chain)
- [Alloy families at a glance](#alloy-families-at-a-glance)
- [The prohibitions](#the-prohibitions)
- [Where the data comes from](#where-the-data-comes-from)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [Document index](#document-index)
- [References](#references)

---

## Overview

Materials is where a design stops being a drawing and becomes something that can be bought, made and trusted. This domain covers the alloys actually used on launch vehicles, how their design allowables are established, how processing changes them, and the failure mechanisms that belong to the material rather than to the design.

The domain is organised around a single question: given a requirement, what number can you put in a stress report, and what is the evidence behind it?

---

## The one distinction that matters most

**A handbook value is not a design allowable.** They are different quantities and the gap between them is not small.

| Quantity | What it is | Where it comes from |
|---|---|---|
| **Typical** | Approximately the population mean | A handbook table |
| **S-basis** | A specification guaranteed minimum | The material specification |
| **B-basis** | 90 percent of the population exceeds it, at 95 percent confidence | A computed tolerance limit |
| **A-basis** | 99 percent of the population exceeds it, at 95 percent confidence | A computed tolerance limit |

For a typical 3 percent coefficient of variation and a sample of thirty, the A-basis sits about 9 percent below the typical value. On a mass-critical pressure vessel that is a real amount of wall.

**Which basis applies is set by the load path, not by preference.** A single load path, where failure of one element causes loss of structural integrity, requires A-basis. Redundant structure that can redistribute load permits B-basis. A pressure vessel wall is single load path by definition.

Full treatment in [AllowablesAndStatistics.md](AllowablesAndStatistics.md).

---

## The selection process

Six steps, in this order, because each one can eliminate candidates that the later steps would waste effort on.

**1. Screen on compatibility first.** It is a pass or fail with no negotiation, and it is the cheapest screen to run. Titanium in an oxidiser system is not a caution; it is a prohibition.

**2. Screen on temperature.** Both ends. A material validated to 200 K is not qualified for 77 K regardless of what a linear extrapolation suggests.

**3. Rank on the material index, not on strength.** Minimum mass for a given load is achieved by maximising a combination that depends on the loading mode. A tie in tension maximises `sigma/rho`; a plate in bending maximises `sigma^(1/2)/rho`. Those give different orderings, and titanium can win the first and lose the second.

**4. Establish the allowable.** Either the database has one or the [`Allowables`](../aerospaceMaterialsLibrary/Allowables.py) class computes one from sample data. A typical value carried into a stress report is the most common materials error there is.

**5. Apply the process knockdowns.** Weld, casting factor, build direction, quench. They compound multiplicatively and they frequently matter more than the choice between two candidate alloys.

**6. Choose the process route.** The same alloy through two routes is two materials. See [ProcessRouteSelection.md](ProcessRouteSelection.md).

---

## The knockdown chain

The path from a handbook number to a design value, with every step recorded.

```
typical value          the population mean, from a handbook
    |
    v  k-factor from the sample size and the required basis
A or B basis           a computed lower tolerance limit
    |
    v  temperature ratio curve
at service temperature
    |
    v  process knockdowns, compounding multiplicatively
        weld            0.55 for as-welded 6061, 0.95 for electron beam
        casting factor  1.0 qualified, 0.75 partial, 0.50 default
        build direction 0.90 for additive Z with HIP
        quench          0.85 for a thick slow-quenched section
    |
    v
design value           the number that goes in the stress report
```

**A design value that arrives with no audit trail cannot be defended and cannot be revisited** when one of its assumptions changes. The [`Allowables`](../aerospaceMaterialsLibrary/Allowables.py) class records every step.

---

## Alloy families at a glance

| Family | Strength | Density | Where it belongs | The catch |
|---|---|---|---|---|
| **Aluminium 2xxx** | Moderate | 2840 | Cryogenic tanks, weldable structure | 2219 buys weldability with strength |
| **Aluminium-lithium** | High | 2710 | Lightweight cryogenic tanks | Cost and a thin supply chain |
| **Aluminium 6xxx** | Low | 2700 | General structure, brackets, lines | Loses 45 % of yield in the weld |
| **Aluminium 7xxx** | High | 2810 | Machined fittings, bulkheads | Not weldable; SCC in short transverse |
| **Stainless austenitic** | Low | 8000 | Fluid systems, cryogenic everything | Heavy, and it pits in chlorides |
| **Stainless PH** | Very high | 7800 | Fasteners, valve bodies, shafts | BCC, so brittle cold; hydrogen susceptible |
| **Nickel** | High | 8200-8900 | Hot sections, corrosive service | Expensive and long lead |
| **Titanium** | Very high | 4430 | Pressure vessels, fuel-side hardware | **Prohibited in oxygen.** Poor conductor |
| **Copper** | Low | 8800-9100 | Chamber liners only | Prohibited in hydrazine |
| **Low alloy steel** | Extreme | 7850 | Motor cases, landing gear | BCC and severely hydrogen susceptible |
| **Composite** | Extreme specific | 1570 | COPV overwrap, panels, fairings | Orthotropic, and sized by stress rupture |

Each has its own document, linked from the index below.

---

## The prohibitions

These are not cautions to be weighed against mass. They are hard stops, and every one of them has a fire, a rupture or a fatality behind it.

| Combination | Mechanism |
|---|---|
| **Titanium in LOX, GOX, N2O4 or nitric acid** | Impact sensitive. It ignites and burns in oxygen |
| **Copper-base alloys in hydrazine** | Copper catalyses decomposition. Unbounded pressure rise |
| **High strength steel above 1000 MPa in hydrogen** | Embrittlement. Notched strength falls to 18 percent |
| **Ferritic or martensitic steel at cryogenic temperature** | Ductile to brittle transition. Sudden failure with no deformation |
| **Sustained short transverse tension in 7075-T6 in marine air** | SCC at 50 MPa, a stress nobody thinks twice about |
| **Carbon composite in direct contact with aluminium** | A 0.9 V galvanic couple with an unfavourable area ratio |

The fluid side of this is covered in depth by [fluidSystems MaterialsCompatibility.md](../../fluidSystems/fluidSystemsLibrary/docs/MaterialsCompatibility.md), which carries the full compatibility matrices. This domain covers the mechanisms and the quantification.

---

## Where the data comes from

Every property in the database carries a source, and every source declares a **basis class**. That field is the difference between a number that can go in a stress report and a number that is somebody's recollection.

| Basis class | Meaning | Usable for |
|---|---|---|
| `statistical` | A computed tolerance limit from a real sample | Design |
| `spec minimum` | A specification guaranteed value | Design, conservatively |
| `typical` | A handbook central value | Preliminary sizing only |
| `estimate` | Author estimate | **Trade studies only. Not traceable.** |

A test walks every numeric leaf in the database and asserts it resolves to a source, so an untraceable number cannot be added silently.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| A handbook value is not an allowable | The gap is around 9 % at n = 30 |
| Single load path requires A-basis | A pressure vessel wall is single load path |
| Screen compatibility before anything else | It is free and it is absolute |
| Rank on the material index, not strength | The index depends on the loading mode |
| Processing changes properties more than alloy choice | A 2.0 casting factor halves the allowable |
| The same alloy in two conditions is two materials | 6061-T6 and 6061 as-welded do not share a yield |
| Short transverse is where SCC lives | And it is the direction least often checked |
| Lead time is a material property | 2195 plate is 32 weeks; 6061 is 4 |
| Never quote absolute cost | Ratios indexed to 316L, with a basis date |
| Clamp, do not extrapolate, outside a validated range | An extrapolated number will be used as though validated |

---

## Failure modes

**A typical value used as an allowable.** The single most common materials error, and it produces a margin that does not exist.

**The wrong basis for the load path.** B-basis on a single load path structure.

**Process knockdowns forgotten.** An aluminium weldment sized on parent metal properties is undersized by 45 percent.

**A prohibited combination that passed because nobody checked.** Titanium in an oxidiser line.

**Short transverse properties assumed equal to longitudinal.** They are the lowest, and on thick 7xxx product they are where SCC initiates.

**A material validated at one temperature used at another.** Extrapolating a strength curve past its data.

**Cost or lead time discovered after the design is frozen.** Both are material properties and both belong in the trade.

**A stronger heat treatment making the part less safe.** STA titanium buys yield strength and gives back fracture toughness, which on a fracture critical vessel is the wrong trade.

---

## Worked example

[`codeInterface.py`](../codeInterface.py) sizes the GHe pressurant bottle inherited from the [fluidSystems worked example](../../fluidSystems/codeInterface.py): 30 MPa, 3.23 L, 0.1394 kg of helium.

| Quantity | Value |
|---|---|
| Bottle | 183.4 mm sphere, Ti-6Al-4V annealed |
| A-basis ultimate from 30 specimens | 869.4 MPa (k = 3.064) |
| Design ultimate after the girth weld | 825.9 MPa |
| **Governing wall criterion** | **No yield during the 1.5x proof test** |
| Wall | 2.623 mm, D/t = 70 |
| Bottle mass | 1.228 kg to hold 0.1394 kg of helium |
| Critical flaw depth | 5.19 mm against a 2.62 mm wall |
| Leak before burst | Satisfied |
| Crack growth life | 2873 cycles against 500 required |

**The proof test governs the wall, not burst.** Burst at FS 1.5 gives 2.50 mm and yield at MEOP gives 2.19 mm; keeping the bottle below yield during its own 1.5x proof test needs 2.62 mm. Sized on burst alone, every flight article would be damaged by the test meant to qualify it.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS** | Metallic materials properties development and standardization. The allowables source |
| **CMH-17** | Composite materials handbook |
| AMS specifications | Aerospace material specifications, per alloy and product form |
| ASTM material specifications | Composition, product form and testing |
| **NASA-STD-6016** | Standard materials and processes requirements for spacecraft |
| NASA-STD-6001 | Flammability, offgassing and compatibility |
| **AIAA S-080 / S-081** | Metallic and composite pressure vessel verification |
| MIL-STD-889 | Dissimilar metals |
| NASA-STD-5001 | Structural design and test factors of safety |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial, MaterialDatabase

properties = queryMaterial('Ti-6Al-4V', 'annealed', 293.15, orientation = 'L', basis = 'A')
print(properties['ultimateStrength'] / 1.0e6)      # 897.0 MPa, A-basis
print(properties['basisAvailable'])                 # True

database = MaterialDatabase()
database.setInputs({'material': '316L', 'condition': 'annealed', 'temperature': 77.0})
print(database.generateReport())
database.checkCompatibility('LOX')                  # raises on a prohibited combination
```

---

## Document index

| Document | Covers |
|---|---|
| [AllowablesAndStatistics.md](AllowablesAndStatistics.md) | A and B basis, k-factors, sample size, knockdowns |
| [AluminumAlloys.md](AluminumAlloys.md) | 2xxx, 6xxx, 7xxx, Al-Li, tempers, weldability |
| [SteelsAndStainless.md](SteelsAndStainless.md) | Austenitic, PH, low alloy, sensitization |
| [NickelAndSuperalloys.md](NickelAndSuperalloys.md) | 625, 718, Monel, Haynes, hot section use |
| [TitaniumAlloys.md](TitaniumAlloys.md) | Ti-6Al-4V and ELI, the oxygen prohibition |
| [CopperAlloys.md](CopperAlloys.md) | GRCop, NARloy-Z, chamber liners |
| [CompositesAndLaminates.md](CompositesAndLaminates.md) | Laminates, COPV overwrap, stress rupture |
| [PolymersAndElastomers.md](PolymersAndElastomers.md) | Glass transition, permeation, outgassing |
| [CryogenicMaterials.md](CryogenicMaterials.md) | Property curves and the DBTT data |
| [CorrosionAndSCC.md](CorrosionAndSCC.md) | Galvanic rates, PREN, SCC thresholds |
| [HydrogenEmbrittlement.md](HydrogenEmbrittlement.md) | Mechanisms, susceptibility, bake-out |
| [FractureAndDamageTolerance.md](FractureAndDamageTolerance.md) | Critical flaw, leak before burst, crack growth |
| [HeatTreatment.md](HeatTreatment.md) | Quench factor, aging, sensitization, distortion |
| [ProcessRouteSelection.md](ProcessRouteSelection.md) | Buy-to-fly, knockdowns, the ten sub-domains |
| [MaterialQualification.md](MaterialQualification.md) | Qualifying a material or process, equivalency |
| [SupplyChainAndLeadTime.md](SupplyChainAndLeadTime.md) | Mill forms, lead times, traceability, counterfeit |
| [StandardsIndex.md](StandardsIndex.md) | Annotated index of the governing standards |

---

## References

1. MMPDS-18, *Metallic Materials Properties Development and Standardization*, 2023.
2. Ashby, M. F., *Materials Selection in Mechanical Design*, 5th ed., Butterworth-Heinemann, 2016.
3. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
4. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
5. Polmear, I. et al., *Light Alloys: Metallurgy of the Light Metals*, 5th ed., Butterworth-Heinemann, 2017.
