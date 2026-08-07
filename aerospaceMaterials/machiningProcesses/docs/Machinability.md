[Home](../README.md) > Machinability

# Machinability

## Contents

- [Overview](#overview)
- [The index](#the-index)
- [Why titanium is difficult](#why-titanium-is-difficult)
- [Why nickel superalloys are worse](#why-nickel-superalloys-are-worse)
- [Why aluminium is easy](#why-aluminium-is-easy)
- [The cost consequence](#the-cost-consequence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Machinability is not a single property. It bundles tool life, cutting force, surface finish and chip control into one index, and the index is useful precisely because those things correlate.

Understanding why an alloy sits where it does is more useful than the number, because it says what to change.

---

## The index

**Indexed to free machining steel at 100.**

| Material | Index | Taylor C | k_s [J/mm^3] | Thermal conductivity [W/m/K] |
|---|---|---|---|---|
| **6061-T6** | **190** | 800 | 0.7 | **167** |
| 2219-T87 | 130 | 600 | 0.8 | 120 |
| 7075-T73 | 120 | 550 | 0.8 | 155 |
| 4340 | 55 | 200 | 2.8 | 44 |
| 316L | 45 | 150 | 3.0 | **15** |
| 17-4PH H1025 | 40 | 140 | 3.2 | 18 |
| **TI-6AL-4V** | **22** | 75 | 3.5 | **6.7** |
| **INCONEL 718** | **12** | **40** | **4.5** | **11** |

**The correlation with thermal conductivity is strong and it is not a coincidence.** The alloys at the bottom of the table are the ones that cannot get heat away from the cutting edge.

---

## Why titanium is difficult

**Four properties combine, and each one alone would be manageable.**

| Property | Value | Consequence |
|---|---|---|
| **Low thermal conductivity** | 6.7 W/m/K | The heat stays at the cutting edge |
| **Chemical reactivity** | High | It reacts with tool materials at temperature |
| **Low modulus** | 114 GPa | The workpiece deflects, and it springs back into the tool |
| **Work hardening in the cut** | Moderate | The next pass meets a hardened layer |

**Low thermal conductivity is the dominant one.** In steel, roughly 75 percent of the cutting heat leaves in the chip; in titanium the chip is thin and the conductivity is low, so a much larger fraction goes into the tool. Cutting edge temperatures reach 1100 degC at modest speeds.

**Chemical reactivity finishes the tool off.** At those temperatures titanium reacts with the cobalt binder in carbide and dissolves it, so the tool fails by diffusion rather than by abrasion. Coated carbide helps and ceramic tools, which work well in nickel, are unusable in titanium for exactly this reason.

**The low modulus causes chatter and spring-back.** The workpiece deflects under the cutting force and springs back behind the tool, rubbing on the flank and adding heat where it is least wanted.

**The controls are low speed and high pressure coolant**: 40 to 75 m/min with coolant at 70 bar or more directed into the cutting zone. High pressure coolant is not a refinement in titanium machining, it is the enabling technology.

---

## Why nickel superalloys are worse

**Everything titanium has, plus strength retained at temperature.**

| Property | Consequence |
|---|---|
| **Strength retained to 700 degC** | The material does not soften where it is being cut |
| **Low thermal conductivity** | 11 W/m/K |
| **Severe work hardening** | The cut leaves a layer harder than the base |
| **Abrasive carbides in the microstructure** | Direct tool wear |
| Notch sensitivity at the depth of cut line | The characteristic failure |

**Retained hot strength is the distinguishing property.** Most metals soften as the cutting zone heats, which reduces the force; Inconel 718 does not, so the force stays high while the temperature climbs.

**Work hardening in the cut is severe** and the layer left by one pass is significantly harder than the base material. The next pass cuts that layer, hardens it further at its edge, and the notch forms at the depth of cut line where the tool sits in the previous pass's hardened boundary.

**Varying the depth of cut between passes is the standard countermeasure** and it is worth a substantial fraction of the tool life.

**Ceramic and CBN tools work here** where they do not in titanium, because nickel does not attack them chemically the way titanium does. Whisker reinforced ceramics run at several times the carbide speed in Inconel.

---

## Why aluminium is easy

| Property | Value | Consequence |
|---|---|---|
| **High thermal conductivity** | 167 W/m/K | The heat leaves in the chip and the workpiece |
| **Low strength** | 276 MPa | Low force and low specific energy |
| **Low melting point** | 660 degC | Its cutting zone never gets hot |
| Non-reactive with carbide | | No diffusion wear |

**Aluminium machining is limited by the machine, not by the material.** Speeds of 800 m/min and above are routine, spindle speeds of 20,000 to 40,000 rpm are used, and the constraint is spindle power and chip evacuation.

**Built-up edge is the one aluminium problem** and it is worst at low speed with the softer alloys. Uncoated polished carbide with a high positive rake, run fast, avoids it. Diamond coated and PCD tooling is used where the alloy is silicon bearing and abrasive.

**AlSi10Mg and other cast or additive aluminium alloys are more abrasive** than wrought aluminium because of the silicon, and they wear tools noticeably faster.

---

## The cost consequence

**A 16x machinability spread is a 16x difference in machining time**, roughly, and machining time is the dominant cost for a machined aerospace part.

| Material | Relative removal rate | Relative machining cost |
|---|---|---|
| 6061-T6 | 1.00 | 1.0 |
| 316L | ~0.24 | ~4 |
| TI-6AL-4V | ~0.12 | ~8 |
| **INCONEL 718** | **~0.06** | **~16** |

**That is why buy-to-fly matters most on the difficult alloys.** A 10 : 1 buy-to-fly on Inconel is not just ten times the material cost, it is a very large machining bill for the nine parts in ten that become chips.

**It is also why near net shape routes compete hardest in titanium and nickel.** Additive, forging and casting all become attractive at Inconel machining rates in a way they are not at aluminium rates.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Machinability tracks thermal conductivity | Not strength alone |
| Titanium: low speed, high pressure coolant | 40 to 75 m/min, 70 bar |
| No ceramic tools in titanium | Chemical attack |
| Ceramic and CBN work in nickel | And run several times faster |
| Vary the depth of cut in nickel | Spreads the notch |
| Aluminium is machine limited | Not material limited |
| Built-up edge in aluminium | Go faster, polished positive rake |
| 16x spread means 16x cost | Near net shape competes hardest at the bottom |

---

## Failure modes

**Ceramic tooling used in titanium.** Rapid chemical attack.

**Flood coolant at low pressure in titanium.** It does not reach the cutting zone.

**Constant depth of cut in nickel.** Notching at the same line every pass.

**Aluminium speeds applied to titanium.** The tool fails in seconds.

**Machining cost estimated per unit volume without the machinability index.** Off by up to 16x.

**Wrought aluminium tooling used on AlSi10Mg.** Faster wear from the silicon.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO 3685** | Tool life testing with single point turning tools |
| ISO 8688 | Tool life testing in milling |
| ISO 513 | Classification of hard cutting materials |
| ASTM E618 | Evaluating machining performance of ferrous metals |
| SAE ARP4915 | Aerospace machining practices |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'machiningProcessesLibrary')

from MachiningProcess import MACHINABILITY

for material in MACHINABILITY:
    data = MACHINABILITY[material]
    print(f'{material:16s} rating {data["machinabilityRating"]:5.0f}  '
          f'n {data["taylorExponent"]:.2f}  C {data["taylorConstant"]:5.0f} m/min  '
          f'k_s {data["specificEnergy"]/1.0e9:.1f} J/mm^3')
```

---

## References

1. Ezugwu, E. O. and Wang, Z. M., "Titanium Alloys and their Machinability", *Journal of Materials Processing Technology*, Vol. 68, 1997.
2. Ulutan, D. and Ozel, T., "Machining Induced Surface Integrity in Titanium and Nickel Alloys", *International Journal of Machine Tools and Manufacture*, Vol. 51, 2011.
3. ASM Handbook Volume 16, *Machining*.
