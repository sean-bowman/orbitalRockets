[Home](../README.md) > Defects

# Casting Defects

## Contents

- [Overview](#overview)
- [The catalogue](#the-catalogue)
- [Shrinkage against gas porosity](#shrinkage-against-gas-porosity)
- [Bifilms](#bifilms)
- [Cold shut and misrun](#cold-shut-and-misrun)
- [Hot tearing](#hot-tearing)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Casting defects are what the casting factor exists to cover. Every one of them is preventable in principle and stochastic in practice, and that combination is why castings carry a knockdown.

---

## The catalogue

| Defect | Appearance | Cause | Fix |
|---|---|---|---|
| **Shrinkage porosity** | Angular, interdendritic, at hot spots | Inadequate feeding | Riser, chill, redesign |
| **Gas porosity** | Rounded, dispersed or clustered | Dissolved gas rejected on freezing | Degas the melt |
| **Bifilms** | Planar, crack-like, often invisible | Turbulent fill folding the oxide film | Unpressurised gating, filters |
| **Cold shut** | A seam where two fronts met | Low superheat, slow fill | More superheat, faster fill |
| **Misrun** | An incomplete casting | The metal froze before filling | More superheat, thicker section |
| **Hot tear** | Irregular crack, oxidised faces | Restrained contraction while semi-solid | Compliance, better feeding |
| Inclusions | Sand, slag, refractory | Mould erosion, dirty melt | Filters, better gating |
| Core shift | Wall thin on one side | Core not located | Better core prints, chaplets |
| Veining | Metal fins on the surface | Mould surface cracking | Mould additives |

---

## Shrinkage against gas porosity

**Distinguishing them is the first diagnostic step, and the shape tells you.**

| | Shrinkage | Gas |
|---|---|---|
| **Shape** | Angular, jagged, interdendritic | **Rounded** |
| **Location** | Hot spots, last to freeze | Dispersed, or under the cope surface |
| **Distribution** | Localised | Often widespread |
| **Fix** | Feeding: riser, chill | Melt: degassing |

**Rounded means gas** because a gas bubble is pressurised and takes a spherical form. **Angular means shrinkage** because the void is what is left between dendrite arms when there is no liquid to fill it.

**Getting this wrong wastes a great deal of effort.** Adding riser volume to fix gas porosity does nothing, and degassing to fix shrinkage does nothing either.

---

## Bifilms

**Campbell's argument, and it changed how quality castings are gated.**

Liquid aluminium and most other alloys carry a solid oxide film on their surface. In a turbulent fill, the surface folds over on itself, and the two dry oxide faces come into contact.

**They do not bond**, because both faces are oxide. The result is a double film with an unbonded interface: a crack, folded into the bulk of the metal, with essentially zero thickness.

| Property | Consequence |
|---|---|
| **Effectively zero thickness** | **Invisible to radiography** |
| Planar | The worst possible defect geometry for fatigue |
| Can unfurl under stress | Becomes a visible crack later |
| Distributed by the flow | Anywhere the turbulent metal went |

**Bifilms explain why casting properties scatter so much more than wrought.** They are a population of pre-existing cracks of unknown size and location, and the fatigue life of a casting is often the fatigue life of its worst bifilm.

**Prevention is the only control**, because inspection does not find them.

| Measure | Effect |
|---|---|
| **Unpressurised gating, 1 : 2 : 4** | Slow, non-turbulent fill |
| **Tapered sprue** | No aspiration |
| **Ceramic foam filters** | Catch films and reduce turbulence |
| **Bottom gating** | Fill upward, no free fall |
| Ingate velocity below 0.5 m/s | The critical velocity for surface folding |

**The 0.5 m/s critical ingate velocity is the practical rule** that comes out of the bifilm argument, and it is worth knowing even if nothing else from it is used.

---

## Cold shut and misrun

**Both are failures to fill, and they differ in degree.**

| Defect | Detail |
|---|---|
| **Cold shut** | Two fronts met and did not fuse. A seam, and the casting is complete |
| **Misrun** | The metal froze before reaching the end. The casting is incomplete |

| Cause | Fix |
|---|---|
| Insufficient superheat | More |
| Section below the process minimum | Thicken it |
| Slow fill | Larger gates |
| Cold mould | Preheat |

**A cold shut is more dangerous than a misrun** because a misrun is obviously scrap and a cold shut can pass a visual inspection while being a full-section crack.

---

## Hot tearing

An irregular crack formed while the casting is still partly liquid, with oxidised fracture faces that distinguish it from a cold crack.

**The mechanism is restrained contraction in the semi-solid state.** Between the coherency point and full solidification the material has almost no strength and no ductility, and any strain imposed on it tears the remaining liquid films apart.

| Contributor | Effect |
|---|---|
| **A rigid mould or core** | The casting cannot contract |
| **Wide freezing range** | Longer time in the vulnerable state |
| **Sharp fillets** | Strain concentration |
| Poor feeding | No liquid to heal the tear |
| Hot spots | The last liquid, and the weakest point |

**The fixes are compliance and feeding.** A collapsible core, a mould that yields, and generous fillets all reduce the imposed strain; better feeding lets the liquid heal the tear as it forms.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Rounded means gas, angular means shrinkage | The first diagnostic |
| Bifilms are invisible to radiography | Prevention only |
| Ingate velocity | Below 0.5 m/s |
| Unpressurised gating and a tapered sprue | The two basic controls |
| Cold shut is more dangerous than a misrun | It passes inspection |
| Hot tears need compliance and feeding | Not just feeding |
| Generous fillets | Strain and hot spots both |

---

## Failure modes

**Gas porosity treated by adding riser volume.** No effect.

**Shrinkage treated by degassing.** No effect.

**Turbulent fill accepted because radiography was clean.** Bifilms do not show.

**Cold shut passed on visual inspection.** A full section crack.

**Rigid core in a wide freezing range alloy.** Hot tearing.

**Sharp internal corners.** Hot spots and strain concentration together.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E446 / E186 / E280** | Reference radiographs for steel castings, by thickness |
| ASTM E505 | Reference radiographs for aluminium and magnesium die castings |
| ASTM E155 | Reference radiographs for aluminium and magnesium castings |
| ASTM E1417 | Liquid penetrant testing |
| ASTM A802 | Steel castings, surface acceptance standards |
| AMS 2175 | Castings, classification and inspection |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. Campbell, J., *Castings Practice: The Ten Rules of Castings*, Butterworth-Heinemann, 2004.
3. ASM Handbook Volume 15, *Casting*.
