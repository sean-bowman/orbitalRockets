[Home](../README.md) > Post-Processing

# Post-Processing

## Contents

- [Overview](#overview)
- [The sequence, and why the order is fixed](#the-sequence-and-why-the-order-is-fixed)
- [Stress relief](#stress-relief)
- [Removal from the plate](#removal-from-the-plate)
- [HIP](#hip)
- [Heat treatment after HIP](#heat-treatment-after-hip)
- [Machining datums](#machining-datums)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The build is a fraction of the process. What follows is longer, costs more, and is where most additive parts are lost.

The order is not a preference. Several steps only work if the ones before them have happened.

---

## The sequence, and why the order is fixed

| Step | Why it must be here |
|---|---|
| **1. Stress relieve, on the plate** | The plate is the only thing holding the part in shape |
| **2. Remove from the plate** | After the stress is gone, not before |
| **3. Remove supports** | Access is easiest before HIP hardens everything |
| **4. Depowder and verify** | Last chance before a closed passage is sealed by nothing |
| **5. HIP** | Closes porosity. It is a thermal cycle at pressure |
| **6. Solution and age** | Because HIP dissolved the strengthening phase |
| **7. Machine datums, then features** | The as-built surface is not a datum |
| **8. Surface finish** | Peening last, because electropolish would remove it |
| **9. Inspect** | CT before anything is closed out |

**Steps 1 and 2 cannot swap.** A part cut off the plate before stress relief distorts, and relieving it afterwards relieves a part that is already the wrong shape.

**Steps 5 and 6 cannot swap or be separated.** A part HIPed above the gamma prime solvus and not re-treated is soft, and none of the allowables in any database apply to it.

**Step 8 must follow any electrochemical process.** Electropolishing after peening removes the compressive layer the peening created. See [postProcessing](../../postProcessing/).

---

## Stress relief

Covered in [ResidualStressAndSupports.md](ResidualStressAndSupports.md). The short version: **on the plate, always, before anything else.**

---

## Removal from the plate

| Method | Notes |
|---|---|
| **Wire EDM** | Clean, accurate, leaves a recast layer that has to be removed |
| Bandsaw | Fast, cheap, rough, and it heats the part |
| Milling | Where the plate interface becomes a datum |

**The recast layer from EDM is a real defect.** It is resolidified material with a different microstructure, often micro-cracked, and it is a fatigue initiation site. On a fatigue critical part it has to be removed by machining or etching.

---

## HIP

Hot isostatic pressing: high temperature and high pressure argon simultaneously, closing internal porosity by creep.

| Alloy | Temperature | Pressure | Time | Must follow |
|---|---|---|---|---|
| **Inconel 718** | 1163 degC | 100 MPa | 4 h | **Solution and age** |
| Inconel 625 | 1120 degC | 100 MPa | 4 h | Nothing |
| **Ti-6Al-4V** | 920 degC | 100 MPa | 2 h | Below the beta transus |
| AlSi10Mg | 520 degC | 100 MPa | 2 h | Coarsens the silicon network |
| 316L | 1120 degC | 100 MPa | 4 h | Solution anneal |

**What HIP does and does not do:**

| Defect | Result |
|---|---|
| Keyhole porosity | Closes and bonds. Recovered |
| **Lack of fusion** | Closes geometrically; oxidised surfaces often do not bond |
| **Entrapped argon** | Compressed, not removed. Re-expands on later heat treatment |
| Surface connected porosity | **Not closed at all**, because the pressure gets inside it |

**Surface connected porosity is the exception people miss.** HIP works by pressure differential across the pore wall. A pore open to the surface has argon on both sides and no differential, so it does not close.

**The titanium cycle sits below the beta transus deliberately.** Above it the alpha morphology coarsens into a lamellar structure and the fatigue strength falls substantially. The [`HeatTreatment`](../../aerospaceMaterialsLibrary/HeatTreatment.py) class flags a cycle that crosses it.

---

## Heat treatment after HIP

**The 718 case is the one that catches programmes.** The HIP temperature of 1163 degC is above the gamma prime and gamma double prime solvus, so the cycle dissolves the precipitates that give the alloy its strength. A part removed from HIP is in the solution annealed condition at roughly 400 MPa yield rather than 1034.

**It must then be solution treated and double aged per AMS 5662.** A part that skipped that step is soft, it looks identical, and no dimensional or visual inspection finds it. A hardness check does, and that is why hardness is on the lot acceptance list.

---

## Machining datums

**An as-built surface is not a datum.** At 20 um Ra with a build-direction taper and stair stepping, it cannot locate anything repeatably.

**The fix is to design datums in.** Machined pads, bosses or a retained portion of the build plate interface, present in the model specifically so the part can be located for machining.

| Practice | Reason |
|---|---|
| Design machining datums into the part | An as-built surface cannot locate |
| Retain the plate interface as a datum where possible | It is flat and it was flat during the build |
| Datum first, features second | Everything else references it |
| Allow stock on every machined surface | Distortion moves the part |

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Stress relieve on the plate, first | Non-negotiable |
| Depowder and verify before HIP | A sealed passage cannot be cleared later |
| HIP above a solvus needs a re-treat | Or the part is soft |
| HIP does not close surface connected porosity | No pressure differential |
| Ti HIP below the beta transus | 920 degC, and above it the fatigue falls |
| Remove the EDM recast layer | It is micro-cracked |
| Design machining datums in | An as-built surface is not one |
| Peen last | Electropolish would remove the layer |

---

## Failure modes

**Cut off the plate before stress relief.** The part distorts and cannot be recovered.

**HIPed and not re-solutioned.** Soft, looks identical, only a hardness check finds it.

**HIP expected to close surface connected porosity.** It does not.

**Titanium HIPed above the beta transus.** Lamellar alpha and a large fatigue debit.

**EDM recast layer left on.** Fatigue initiation site.

**No machining datum.** The part cannot be located repeatably.

**Peening followed by electropolishing.** The compressive layer is removed.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3301** | Post-processing methods for metal additive parts |
| ASTM A1080 | Hot isostatic pressing of steel and stainless |
| AMS 5662 | Inconel 718 solution treated and aged |
| AMS 2801 | Heat treatment of titanium alloy parts |
| AMS 2750 | Pyrometry |
| NASA-STD-6030 | Additive manufacturing requirements |

---

## Tool interface

```python
from HeatTreatment import HeatTreatment      # aerospaceMaterials parent library

treatment = HeatTreatment()
treatment.setInputs({'material': 'Inconel 718', 'condition': 'lpbf hip + sta'})
cycle = treatment.calculateHipCycle()
print(cycle['requiresPostHeatTreatment'], cycle['note'])
```

---

## References

1. ASTM F3301-18, *Standard for Additive Manufacturing -- Post Processing Methods*.
2. Tammas-Williams, S. et al., "The Effectiveness of Hot Isostatic Pressing for Closing Porosity in Titanium Parts", *Metallurgical and Materials Transactions A*, Vol. 47, 2016.
3. Gradl, P. R. et al., "Metal Additive Manufacturing in Aerospace: A Review", *Materials and Design*, Vol. 209, 2021.
