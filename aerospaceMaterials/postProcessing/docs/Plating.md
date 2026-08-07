[Home](../README.md) > Plating

# Plating

## Contents

- [Overview](#overview)
- [The processes](#the-processes)
- [What each is for](#what-each-is-for)
- [The hydrogen problem](#the-hydrogen-problem)
- [Adhesion](#adhesion)
- [Thickness and throwing power](#thickness-and-throwing-power)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Plating puts a different metal on the surface for corrosion, wear, conductivity or anti-galling. On a high strength steel it also puts hydrogen inside, and that is the dominant consideration.

---

## The processes

| Process | Mechanism | Hydrogen |
|---|---|---|
| **Electroplating** | Current through an electrolyte | **Yes** |
| **Electroless nickel** | Autocatalytic chemical reduction | **Yes**, less |
| **Ion vapour deposited aluminium** | Physical vapour deposition | **No** |
| Mechanical plating | Peening a powder onto the surface | No |
| Thermal spray | See [ThermalSpray.md](ThermalSpray.md) | No |

**The hydrogen column is the one that decides the process on a high strength part.**

---

## What each is for

| Coating | Purpose | Notes |
|---|---|---|
| **Cadmium** | Sacrificial corrosion protection on steel | Being designed out. Toxic and it charges hydrogen |
| **IVD aluminium** | The cadmium replacement | No hydrogen, and it is qualified on major programmes |
| Zinc, zinc-nickel | Sacrificial corrosion | Cheaper than cadmium |
| **Hard chrome** | Wear and hardness | Cracks. Severe fatigue debit. Hexavalent chromium |
| **Electroless nickel** | Uniform corrosion and wear | Uniform thickness in blind holes, which is its advantage |
| **Silver** | Anti-galling on threaded stainless | **Prohibited near hydrazine** |
| Gold | Contact resistance, corrosion | Electronics and connectors |
| Copper | An underlayer, and for brazing | |

**Silver on stainless fasteners is standard anti-galling practice** and it is prohibited anywhere near hydrazine, because silver catalyses decomposition. That combination catches people out because both facts are individually well known.

---

## The hydrogen problem

**Electroplating puts atomic hydrogen into the substrate.** The cathodic reaction at the part surface produces hydrogen, and some of it diffuses into the metal instead of evolving as gas.

**Above about 1000 MPa ultimate tensile strength that is enough to cause delayed brittle fracture**, hours to days after loading, in a part that tested perfectly.

| Requirement | Value |
|---|---|
| **Trigger** | 1000 MPa ultimate |
| **Bake** | 23 hours minimum at 190 degC |
| **Start within** | 4 hours of plating |

**The four hour window matters as much as the bake.** Hydrogen diffuses to traps and cracks initiate during that time, so a bake started late removes the hydrogen from a part that has already cracked.

**IVD aluminium removes the requirement rather than managing it**, which is why it replaced cadmium on high strength steel. See [HydrogenBakeout.md](HydrogenBakeout.md).

**Acid pickling before plating charges hydrogen too**, so the whole process sequence matters and not only the plating step.

---

## Adhesion

**Plating adhesion is entirely a surface preparation problem.**

| Step | Purpose |
|---|---|
| Degrease | Remove oil |
| Alkaline clean | Remove residue |
| **Acid activate** | Remove the oxide and expose bare metal |
| Strike | A thin high-current layer to establish adhesion |
| Plate | The bulk deposit |

**Aluminium needs a zincate.** Its oxide reforms in seconds, so a zinc immersion layer is deposited to displace the oxide and hold the surface until plating starts. A double zincate is standard.

**Adhesion failures are almost always cleaning failures**, and they show up as blistering or peeling either immediately or after a thermal cycle. A bend test or a thermal shock test on a coupon is the standard check.

---

## Thickness and throwing power

**Electroplated thickness is not uniform.** Current density is highest at edges and corners and lowest in recesses, so the deposit is thickest where the part projects and thinnest where it does not.

| Feature | Deposit |
|---|---|
| Edge or corner | Thick, sometimes a nodule |
| Flat face | Nominal |
| Recess | Thin |
| **Blind hole** | **Very thin or absent** |

**Throwing power** is the term for how well a process covers recesses, and it varies by electrolyte. It is never good enough to plate the inside of a small blind hole.

**Electroless nickel has no current** and therefore no current distribution problem. Its deposit is uniform everywhere the solution reaches, including blind holes and internal passages. **That uniformity is its main advantage** and it is why it is specified for complex internal geometry.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Bake trigger | 1000 MPa ultimate |
| Bake | 23 h at 190 degC, within 4 h |
| IVD aluminium | No hydrogen at all |
| Silver near hydrazine | Prohibited |
| Hard chrome | Cracks, severe fatigue debit, peen first |
| Electroless nickel | Uniform in blind holes |
| Electroplate in a recess | Thin or absent |
| Adhesion is a cleaning problem | Aluminium needs a zincate |
| Plating thickness | In the tolerance stack |

---

## Failure modes

**No bake, or a late bake, on a high strength part.** Delayed fracture days later.

**Silver plated fasteners in a hydrazine system.** Catalytic decomposition.

**Hard chrome on a fatigue critical part without peening.** The cracks propagate.

**Blind hole expected to be plated.** It is not.

**Adhesion failure from poor cleaning.** Blisters after a thermal cycle.

**Plating thickness not in the tolerance stack.** The part does not assemble.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F1940** | Process control to prevent hydrogen embrittlement |
| **AMS 2759/9** | Hydrogen embrittlement relief baking |
| SAE AMS-QQ-P-416 | Cadmium plating |
| **MIL-DTL-83488** | Aluminium coating, ion vapour deposited |
| AMS 2404 | Electroless nickel plating |
| AMS 2406 | Hard chromium plating |
| AMS 2410 | Silver plating |
| ASTM B571 | Adhesion of metallic coatings |

---

## Tool interface

```python
from SurfaceTreatment import SurfaceTreatment, PLATING_PROCESSES

for process in ('cadmium', 'ivd aluminium', 'electroless nickel'):
    treatment = SurfaceTreatment()
    treatment.setInputs({'material': '4340', 'condition': 'qt-260',
                         'alloyFamily': 'stainless'})
    result = treatment.checkPlatingBake(process)
    print(f'{process:20s} charges H2: {result["chargesHydrogen"]}, '
          f'bake required: {result["bakeRequired"]}')
```

---

## References

1. ASTM F1940-07a, *Process Control Verification to Prevent Hydrogen Embrittlement*.
2. MIL-DTL-83488D, *Coating, Aluminum, High Purity*.
3. Davis, J. R. (ed.), *Surface Engineering for Corrosion and Wear Resistance*, ASM, 2001.
