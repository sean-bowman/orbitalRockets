[Home](../README.md) > Hydrogen Bakeout

# Hydrogen Bakeout

## Contents

- [Overview](#overview)
- [The trigger](#the-trigger)
- [The cycle](#the-cycle)
- [Why the four hour window](#why-the-four-hour-window)
- [The temperature ceiling](#the-temperature-ceiling)
- [Verification](#verification)
- [Designing the requirement away](#designing-the-requirement-away)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Any process that puts atomic hydrogen into a high strength steel requires a bake to drive it back out. The requirement is triggered by the tensile strength, not by the service, and it is one of the few places in materials engineering where a procedural step is genuinely the difference between a working part and a fracture.

The mechanism is in [aerospaceMaterials HydrogenEmbrittlement](../../docs/HydrogenEmbrittlement.md). This document is the process.

---

## The trigger

**Ultimate tensile strength at or above 1000 MPa**, per ASTM F1940 and AMS 2759/9.

**Not the service, the strength.** A part that never sees hydrogen propellant still gets hydrogen charged into it by electroplating, and above the threshold that is enough to crack it.

| Process | Charges hydrogen |
|---|---|
| **Electroplating** | Yes. The commonest source |
| **Acid pickling and etching** | Yes, before plating |
| **Cathodic alkaline cleaning** | Yes |
| Electroless nickel | Yes, less |
| Anodising | No, the part is the anode |
| IVD aluminium | **No** |
| Mechanical plating | No |

**Anodising does not charge hydrogen** because the part is the anode: oxygen is evolved at the part and hydrogen at the cathode. That is a genuinely useful asymmetry.

---

## The cycle

| Parameter | Requirement |
|---|---|
| **Temperature** | 190 degC nominal, 175 to 205 typical |
| **Time** | 23 hours minimum |
| **Start** | Within 4 hours of plating |
| Atmosphere | Air is acceptable |
| Higher strength | Longer, up to 24+ hours |

**Longer for higher strength.** A 1400 MPa part needs a longer bake than a 1050 MPa one at the same temperature, because the trap density is higher and the hydrogen is more strongly bound.

**The bake drives hydrogen out by diffusion**, so it scales with section thickness as well. A thick part needs longer, and the specification usually states a minimum rather than an exact figure for that reason.

---

## Why the four hour window

**Hydrogen does not sit still after plating.** It diffuses through the lattice to traps: grain boundaries, inclusions, dislocations, and any existing crack tip.

**At a crack tip under residual stress, it accumulates and initiates a crack.**

| Time after plating | What is happening |
|---|---|
| 0 to 4 h | Hydrogen still mobile and distributed. A bake removes it |
| 4 to 24 h | Accumulating at traps. Cracks may be initiating |
| Days | Delayed fracture, in a part that tested fine |

**A bake started late removes the hydrogen from a part that has already cracked.** The hydrogen is gone, the crack is not, and nothing in the process records shows a problem.

**This is why the window is a hard requirement rather than good practice**, and why plating and baking are usually scheduled as one operation rather than two.

---

## The temperature ceiling

**The bake temperature is bounded above by the tempering temperature of the steel.**

Baking above the temper softens the part. A low tempered high strength steel, tempered at say 200 degC to reach 1900 MPa, has almost no window: the bake temperature and the temper temperature are the same number.

| Steel condition | Temper | Bake window |
|---|---|---|
| 4340 at 1790 MPa | ~230 degC | Narrow |
| 300M at 1965 MPa | ~300 degC | Adequate |
| A high strength part tempered at 190 degC | 190 degC | **None** |

**Where there is no window, the answer is a process that does not charge hydrogen**, not a compromise bake.

---

## Verification

**The bake cannot be verified on the part.** There is no test that says a specific part has acceptable hydrogen content without destroying it.

**What is verified is the process**, per ASTM F519:

| Element | Detail |
|---|---|
| **Notched bar specimens** | Plated alongside production parts |
| **Sustained load** | 75 percent of the notched fracture strength |
| **200 hours** | Held, and they must not fail |
| Frequency | Per plating lot, or per shift |

**F519 qualifies the plating process, not the part.** A specimen that survives says the process as run that day did not embrittle it, and that is the strongest available statement.

**Furnace records are the other half.** Temperature, time and the start time relative to plating, recorded and retained.

---

## Designing the requirement away

**The best answer to the bake requirement is not to trigger it.**

| Approach | Effect |
|---|---|
| **Keep ultimate strength below 1000 MPa** | Below the trigger entirely |
| **Specify IVD aluminium rather than cadmium** | No hydrogen charging |
| Mechanical plating | No hydrogen |
| Thermal spray | No hydrogen |
| A corrosion resistant alloy instead of a coating | No plating at all |

**IVD aluminium is the standard cadmium replacement on high strength steel** and it was adopted for the environmental reasons and kept for the hydrogen ones.

**A design that needs 1400 MPa and a sacrificial coating is a design that has to be managed carefully.** One that can meet its requirement at 950 MPa has removed a whole class of failure.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Trigger | 1000 MPa ultimate |
| Bake | 23 h minimum at 190 degC |
| Start within | 4 hours |
| Longer for higher strength and thicker section | |
| Ceiling | The tempering temperature |
| Anodising does not charge hydrogen | The part is the anode |
| Verify by ASTM F519 | It qualifies the process, not the part |
| Design the trigger away | Below 1000 MPa, or IVD aluminium |

---

## Failure modes

**Bake started late.** The crack initiated during the delay.

**Bake above the tempering temperature.** The part is soft.

**Bake omitted because the part does not see hydrogen service.** The trigger is strength.

**Acid pickling not counted as a hydrogen source.** It is one.

**F519 specimens not run with the lot.** The process was never verified.

**A 1400 MPa part with no bake window.** The process choice was wrong.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F1940** | Process control verification to prevent hydrogen embrittlement |
| **ASTM F519** | Mechanical hydrogen embrittlement evaluation of plating processes |
| **AMS 2759/9** | Hydrogen embrittlement relief baking of steel parts |
| ASTM F1624 | Threshold for hydrogen stress cracking by incremental step loading |
| SAE AMS-QQ-P-416 | Cadmium plating, including the bake requirement |
| MIL-DTL-83488 | IVD aluminium |
| AMS 2750 | Pyrometry, for the furnace |

---

## Tool interface

```python
from SurfaceTreatment import (SurfaceTreatment, HYDROGEN_BAKE_THRESHOLD,
                              HYDROGEN_BAKE_TIME, HYDROGEN_BAKE_TEMPERATURE)

print(HYDROGEN_BAKE_THRESHOLD / 1e6, 'MPa trigger')
print(HYDROGEN_BAKE_TIME / 3600.0, 'h at', HYDROGEN_BAKE_TEMPERATURE - 273.15, 'degC')

treatment = SurfaceTreatment()
treatment.setInputs({'material': '4340', 'condition': 'qt-260', 'alloyFamily': 'stainless'})
print(treatment.checkPlatingBake('cadmium')['bakeRequired'])         # True
print(treatment.checkPlatingBake('ivd aluminium')['bakeRequired'])   # False
```

---

## References

1. ASTM F1940-07a, *Standard Test Method for Process Control Verification to Prevent Hydrogen Embrittlement*.
2. ASTM F519-18, *Mechanical Hydrogen Embrittlement Evaluation of Plating/Coating Processes*.
3. AMS 2759/9, *Hydrogen Embrittlement Relief Baking of Steel Parts*.
