[Home](../README.md) > Anodising and Conversion Coating

# Anodising and Conversion Coating

## Contents

- [Overview](#overview)
- [Anodising](#anodising)
- [The fatigue debit](#the-fatigue-debit)
- [Conversion coating](#conversion-coating)
- [The chromate problem](#the-chromate-problem)
- [Titanium anodising](#titanium-anodising)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Aluminium's corrosion resistance comes from a natural oxide a few nanometres thick. Anodising grows that oxide deliberately to micrometres; conversion coating replaces it with a chemically formed film.

Both protect. Anodising carries a fatigue debit that is frequently overlooked.

---

## Anodising

The part is the anode in an acid electrolyte. Oxygen is evolved at the surface and it oxidises the aluminium in place, growing a porous oxide layer.

| Type | Electrolyte | Thickness | Use |
|---|---|---|---|
| **Type I** | Chromic acid | 2 to 5 um | Thin, and the least fatigue debit. Where fatigue matters |
| **Type II** | Sulphuric acid | 5 to 25 um | The general purpose coating. Dyeable |
| **Type III** | Sulphuric, chilled | 25 to 100 um | Hard anodise. Wear resistance |

**The coating grows both outward and inward.** Roughly half the thickness is above the original surface and half below it, so a 50 um hard anodise adds 25 um to a dimension and consumes 25 um of the part.

**That has to be in the tolerance stack**, and on a close-fitting part it is often the whole tolerance.

**Sealing is a separate step and it is essential.** As formed, the oxide is porous. Sealing in hot water or a nickel acetate solution hydrates the oxide and closes the pores. An unsealed anodise is a poor corrosion coating and it will absorb whatever it is exposed to.

---

## The fatigue debit

**The anodic layer is a brittle ceramic bonded to a ductile substrate.** It cracks under strain, and those cracks are stress concentrations at the surface, which is exactly where fatigue cracks start.

| Coating | Typical fatigue knockdown |
|---|---|
| Type I chromic, thin | 5 to 15 % |
| **Type II sulphuric** | **15 to 30 %** |
| **Type III hard anodise** | **30 to 60 %** |

**The debit scales with thickness**, which is why hard anodise is the worst. A 100 um coating cracks at a lower strain and the cracks are deeper.

**Shot peening before anodising offsets it**, and it is standard practice on fatigue critical anodised parts. The compressive layer keeps the substrate surface in compression so the coating cracks do not propagate.

**Type I exists for this reason.** Chromic acid anodising produces a thinner, less brittle coating specifically where fatigue governs, and it is why it survives in aerospace despite the chromium.

---

## Conversion coating

A chemical rather than electrochemical process. The surface reacts with the solution to form a thin conversion film, typically under 1 um.

| Property | Anodising | Conversion coating |
|---|---|---|
| Thickness | 2 to 100 um | < 1 um |
| **Fatigue debit** | Real | **Negligible** |
| **Electrically conductive** | No | **Yes** |
| Corrosion protection | Better | Adequate |
| Paint adhesion | Good | Excellent, and it is the main use |
| Dimensional effect | Real | Negligible |

**Electrical conductivity is the discriminator.** An anodised surface is an insulator, so an anodised part cannot be a ground path or a bonding surface. Conversion coating conducts, which is why every grounding and bonding surface on an aluminium structure is conversion coated rather than anodised.

**Negligible fatigue debit is the other reason**, and together they make conversion coating the default for a structural part that will be painted.

---

## The chromate problem

**Hexavalent chromium is a carcinogen and it is being regulated out.**

Traditional conversion coatings (Alodine, Iridite) and Type I anodising both use hexavalent chromium. Both work extremely well and both are on a regulatory path towards elimination.

| Replacement | Status |
|---|---|
| Trivalent chromium conversion | Mature, qualified, slightly worse corrosion performance |
| Non-chrome conversion | Available, variable performance |
| Boric-sulphuric anodise | The Type I replacement. Qualified on major programmes |
| Thin film sulphuric | Another Type I replacement |

**Design out the hexavalent processes rather than seek exemptions.** An exemption is a temporary permission with an expiry date attached to a programme that may outlive it. See [aerospaceMaterials SupplyChainAndLeadTime](../../docs/SupplyChainAndLeadTime.md).

---

## Titanium anodising

Different mechanism, different purpose.

| Purpose | Notes |
|---|---|
| **Anti-galling** | The primary reason. Titanium galls severely against itself |
| Identification | The oxide colour varies with voltage, so parts can be colour coded |
| Adhesive bonding preparation | A specific process, and it is not the same as decorative anodising |
| Fretting resistance | Some benefit |

**Titanium anodising is not a corrosion coating**, because titanium does not need one. It is a surface engineering treatment for friction and galling.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Coating grows half in, half out | Put it in the tolerance stack |
| Type II fatigue debit | 15 to 30 % |
| Type III fatigue debit | 30 to 60 % |
| Peen before anodising | Offsets the debit |
| Anodise is an insulator | Conversion coat any bonding surface |
| Conversion coating fatigue debit | Negligible |
| Sealing is essential | An unsealed anodise is porous |
| Design out hexavalent chromium | Not an exemption |

---

## Failure modes

**Hard anodise on a fatigue critical part.** A 30 to 60 percent debit nobody accounted for.

**Anodised bonding surface.** No ground path.

**Anodise thickness not in the tolerance stack.** The part does not fit.

**Unsealed anodise.** Porous, and it absorbs contamination.

**Hexavalent chromium exemption relied on.** It expires.

**Titanium anodise expected to prevent corrosion.** It is a galling treatment.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-A-8625** | Anodic coatings for aluminium and aluminium alloys |
| MIL-DTL-5541 | Chemical conversion coatings on aluminium |
| **AMS 2470 / 2471 / 2472** | Chromic, sulphuric and hard anodising |
| AMS 2488 | Anodic treatment of titanium, hard coating |
| ASTM B580 | Anodic oxide coatings on aluminium |
| ASTM D3933 | Preparation of aluminium for adhesive bonding |

---

## References

1. MIL-A-8625F, *Anodic Coatings for Aluminum and Aluminum Alloys*.
2. Wernick, S., Pinner, R. and Sheasby, P. G., *The Surface Treatment and Finishing of Aluminium and its Alloys*, 5th ed., ASM, 1987.
3. Cree, A. M. and Weidmann, G. W., "Effect of Anodised Coatings on Fatigue Crack Growth Rates in Aluminium Alloy", *Surface Engineering*, Vol. 13, 1997.
