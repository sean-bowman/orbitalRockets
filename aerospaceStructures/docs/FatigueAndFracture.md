[Home](../README.md) > Fatigue and Fracture

# Fatigue and Fracture

## Contents

- [Overview](#overview)
- [Fatigue against fracture](#fatigue-against-fracture)
- [Where fatigue actually happens](#where-fatigue-actually-happens)
- [Fracture control](#fracture-control)
- [Leak before burst](#leak-before-burst)
- [Proof test as NDE](#proof-test-as-nde)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The mechanics live in [aerospaceMaterials FractureAndDamageTolerance](../../aerospaceMaterials/docs/FractureAndDamageTolerance.md). This document is about where the structure is actually vulnerable and what the fracture control process requires.

---

## Fatigue against fracture

| | Fatigue | Fracture |
|---|---|---|
| **Question** | How many cycles to initiate a crack? | Given a crack, will it grow or break? |
| **Method** | S-N, strain-life, Miner's rule | `K = Y sigma sqrt(pi a)`, Paris law |
| **Governs** | Long-life structure, many cycles | **Pressure vessels, single-flight hardware** |
| Input | Stress spectrum, surface condition | Initial flaw size, toughness, NDE capability |

**Launch vehicle primary structure sees very few cycles.** A stage flies once, or a handful of times for a reusable one. The governing consideration is therefore usually fracture, not fatigue: given a flaw that inspection could have missed, does it survive the mission?

**Reusable structure inverts this.** A booster designed for tens of flights accumulates real cycle counts and fatigue re-enters as a design driver, along with inspection intervals between flights.

---

## Where fatigue actually happens

**Not in the middle of a panel.** Fatigue is a local phenomenon and it starts at a discontinuity.

| Location | Why |
|---|---|
| **Fastener holes** | Stress concentration plus surface damage from drilling |
| **Weld toes** | Geometric notch plus residual tension plus HAZ |
| **Fillet runouts** | Section change |
| **Weld land runouts** | Stiffness discontinuity |
| **Y-ring** | Discontinuity bending at a weld |
| Machining marks | Especially with tensile residual stress |

**Hole quality dominates joint fatigue life more than fastener choice does**, and cold expansion is worth 3 to 10x. See [aerospaceMaterials HoleMaking](../../aerospaceMaterials/machiningProcesses/docs/HoleMaking.md).

**Weld toe geometry dominates weld fatigue life**, and grinding the toe smooth is a recognised improvement technique worth a factor of two or more.

**Surface residual stress from machining swings the fatigue life by a factor of two**, between a sharp tool with flood coolant and a worn tool running dry. That is larger than most design decisions and it is invisible on a drawing that specifies only Ra.

---

## Fracture control

**NASA-STD-5019 defines the process**, and the classification decides how much work follows.

| Classification | Requirement |
|---|---|
| **Non-fracture-critical** | Contained, low released energy, or fail-safe |
| **Fracture critical** | Full damage tolerance analysis, NDE, traceability |
| Low risk | A defined exception with its own criteria |

**A part is fracture critical if its failure is catastrophic and it is not fail-safe.** Pressure vessels, single load path primary structure and rotating machinery usually are.

**The analysis needs an initial flaw size**, and it comes from the NDE method's demonstrated capability, not from what was found. The standard flaw sizes assume the largest crack the inspection could have missed with 90 percent probability at 95 percent confidence.

**Single load path is what makes it critical.** In the [aerospaceMaterials](../../aerospaceMaterials/) helium bottle example, going to a single load path cost 4.1 percent in mass through the fracture requirements it triggered.

---

## Leak before burst

**A pressure vessel design goal: the through-crack that leaks should be shorter than the crack that would burst it.**

**Then a defect announces itself as a leak rather than as a rupture**, which is a fundamentally different failure consequence.

**The condition depends on toughness against strength**, roughly as `K_Ic^2 / sigma`. A stronger, less tough condition of the same alloy can lose it, and in the materials worked example the Ti-6Al-4V STA condition lost leak-before-burst that the annealed condition satisfied.

**That is a real design constraint on heat treatment selection**, and it is the kind of coupling that a strength-only trade misses entirely.

---

## Proof test as NDE

**Surviving a proof load demonstrates that no flaw larger than the critical size at the proof stress is present.**

**That bounds the initial flaw size for the damage tolerance analysis**, which is a legitimate and widely used technique. It is quantitative, not a general reassurance.

**It has two costs.** The proof test can grow a subcritical flaw, so it is applied with a subsequent inspection or a demonstrated no-growth condition. And it consumes life: the proof cycle is one of the cycles the vessel is designed for.

**Proof is also frequently the sizing case**, as the worked example shows: the proof test governs the tank wall at 22.592 mm against 21.904 mm for burst. A vessel sized on burst alone yields during its own acceptance test.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Fracture governs single-flight structure | Fatigue governs reusable |
| Fatigue starts at discontinuities | Holes, weld toes, runouts |
| Cold expansion | 3 to 10x hole fatigue life |
| Grind the weld toe | 2x or more |
| Machining surface condition | 2x swing, invisible on the drawing |
| Initial flaw from NDE capability | Not from what was found |
| Design for leak before burst | And check it survives the heat treatment choice |
| Proof test bounds the flaw size | And consumes a cycle |

---

## Failure modes

**Fatigue checked in the panel, not at the holes.** It initiates at the discontinuity.

**Initial flaw taken as what inspection found.** It must be what inspection could have missed.

**Leak before burst lost to a strength-driven heat treatment change.** A strength-only trade misses it.

**Proof test treated as evidence of margin.** It bounds a flaw size, nothing more.

**Proof cycle omitted from the life count.** It is one of them.

**Reusable structure analysed as single flight.** Fatigue re-enters as a driver.

**Surface finish specified as Ra only on a fatigue critical surface.** Nothing is controlled.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5019** | Fracture control requirements for spaceflight hardware |
| **NASA-STD-5009** | NDE requirements for fracture critical components |
| NASA-STD-5001 | Structural design and test factors |
| ASTM E399 / E1820 | Fracture toughness |
| ASTM E647 | Fatigue crack growth rates |
| ASTM E466 | Force controlled constant amplitude fatigue |
| AIAA S-080 | Metallic pressure vessels |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterials/aerospaceMaterialsLibrary')

from DamageTolerance import DamageTolerance

analysis = DamageTolerance()
analysis.setInputs({'material': 'TI-6AL-4V', 'condition': 'annealed',
                    'operatingStress': 400.0e6, 'wallThickness': 0.0026,
                    'geometryCase': 'surface flaw, semi-elliptical', 'inspectionMethod': 'penetrant, standard'})

critical = analysis.calculateCriticalFlaw()
print(f'critical flaw {critical["criticalFlawSize"] * 1000.0:.3f} mm')

leak = analysis.checkLeakBeforeBurst()
print(f'leak before burst: {leak["leakBeforeBurst"]}, ratio {leak["ratio"]:.2f}')
```

---

## References

1. NASA-STD-5019A, *Fracture Control Requirements for Spaceflight Hardware*.
2. Anderson, T. L., *Fracture Mechanics: Fundamentals and Applications*, 4th ed., CRC Press, 2017.
3. NASGRO, *Fatigue Crack Growth Computer Program*, NASA JSC and SwRI.
