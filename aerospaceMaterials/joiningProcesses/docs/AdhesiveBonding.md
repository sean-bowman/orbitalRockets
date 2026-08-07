[Home](../README.md) > Adhesive Bonding

# Adhesive Bonding

## Contents

- [Overview](#overview)
- [Why the load distribution is the whole problem](#why-the-load-distribution-is-the-whole-problem)
- [Shear lag](#shear-lag)
- [Joint configurations](#joint-configurations)
- [Surface preparation](#surface-preparation)
- [Environment](#environment)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Adhesive bonding distributes load over an area rather than concentrating it at a hole, which is why it can outperform fastening in fatigue. It is also the joining method most sensitive to process control and the hardest to inspect.

---

## Why the load distribution is the whole problem

**An adhesive joint does not load uniformly.** The shear stress in the bondline peaks at the ends of the overlap and drops to nearly nothing in the middle.

| Consequence | Detail |
|---|---|
| **Beyond a certain overlap, more length adds nothing** | The middle carries no load anyway |
| **The ends govern** | Failure initiates there |
| Peel at the ends | Because the adherends bend |
| Stiffness matters | A stiffer adherend spreads the load further |

**Doubling the overlap does not double the strength**, which is the counter-intuitive result that governs joint design. Beyond about 30 times the adhesive thickness, additional overlap contributes very little.

---

## Shear lag

The Volkersen shear lag model gives the distribution:

```
tau(x) = tau_avg * (w L / 2) * cosh(w x) / sinh(w L / 2)
w = sqrt(G_a / (t_a E t))
```

| Symbol | Meaning |
|---|---|
| `G_a` | Adhesive shear modulus |
| `t_a` | Bondline thickness |
| `E`, `t` | Adherend modulus and thickness |
| `L` | Overlap length |

**The peak to average ratio grows with overlap**, so a long joint has a very high peak stress at its ends and a very low average.

**A more compliant adhesive spreads the load better**, which is why a toughened adhesive with a lower modulus can carry more than a stiff brittle one of higher nominal strength.

**A thicker bondline also spreads it**, which is one of the few places where more adhesive helps. The usual bondline is 0.1 to 0.25 mm, controlled by scrim cloth or glass beads.

**Goland and Reissner extends the model** to include the bending moment from the eccentric load path in a single lap joint, which produces the peel stress that usually initiates failure.

---

## Joint configurations

| Joint | Peel | Efficiency |
|---|---|---|
| **Single lap** | **High.** Eccentric load path | Poor |
| **Double lap** | Low. Balanced | **Good** |
| **Scarf** | **Very low.** Aligned load path | **Best** |
| Stepped lap | Low | Very good, and it is machinable |
| Butt | -- | Useless |

**The single lap joint is the worst configuration and the most common one.** The load path is eccentric, so the joint bends under load, which peels the ends apart. It is used because it is the easiest to make.

**Double lap removes the eccentricity** and it roughly doubles the capability for the same bond area.

**Scarf joints are the best and the hardest to make.** A shallow taper aligns the load path through the bond, eliminating both the eccentricity and the stress concentration. Composite repair uses scarf and stepped lap joints for exactly this reason.

**Adhesive joints must not be loaded in peel or cleavage**, and where the geometry cannot avoid it, a fastener at the end of the overlap arrests the peel.

---

## Surface preparation

**The dominant variable in bond durability, and it is a process rather than a material.**

| Adherend | Preparation |
|---|---|
| **Aluminium** | Degrease, etch (FPL or P2), **anodise (PAA or CAA)**, prime |
| Titanium | Degrease, etch, **sol-gel or plasma** |
| Steel | Degrease, grit blast, prime |
| **Composite** | **Peel ply removal**, or abrade and solvent wipe |

**Phosphoric acid anodise is the aerospace aluminium standard** because it produces a microporous oxide that the primer mechanically keys into, and the resulting bond is durable in hot wet service where a simple etch is not.

**The difference between preparations shows up in durability, not in initial strength.** A poorly prepared bond can test perfectly on delivery and fail after two years of humidity exposure, because the failure is progressive hydration of the oxide at the interface.

**Peel ply is the composite answer** and it is not without traps: some peel plies leave a release agent transfer that prevents bonding, and the qualification of a specific peel ply with a specific adhesive is a real requirement.

**Time between preparation and bonding is controlled**, typically a few hours, because surfaces re-contaminate.

---

## Environment

| Factor | Effect |
|---|---|
| **Moisture** | **The dominant degradation.** Plasticises the adhesive, attacks the interface |
| **Temperature** | Above `Tg` the adhesive loses most of its stiffness and strength |
| **Hot-wet combined** | **The design condition.** Worse than either alone |
| UV | Degrades exposed bondlines |
| Thermal cycling | Fatigues the bondline, especially with dissimilar adherends |

**Hot-wet is the design condition** for a structural adhesive and the allowables are quoted for it. A room temperature dry strength is not a design number.

**`Tg` falls when the adhesive absorbs moisture**, typically by 20 to 40 degC, so a saturated adhesive has a lower service temperature than a dry one. That interaction is why the hot-wet condition is worse than either factor separately.

**Sealing the bondline edges** limits moisture ingress, since diffusion is from the exposed edge inward.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The ends of the overlap carry the load | The middle does not |
| Overlap beyond ~30x the bondline adds little | |
| Double lap or scarf, not single lap | Eccentricity |
| **Never load in peel or cleavage** | A fastener arrests it if unavoidable |
| Bondline 0.1 to 0.25 mm | Controlled by scrim |
| **Phosphoric acid anodise for aluminium** | Durability, not initial strength |
| Hot-wet is the design condition | Not room temperature dry |
| Control the time from preparation to bond | |

---

## Failure modes

**Single lap joint at double lap allowables.** Peel at the ends.

**Overlap lengthened to gain strength.** The middle carries nothing.

**Joint loaded in peel.** Very low capability.

**Simple etch instead of anodise.** Passes on delivery, fails in service.

**Peel ply not qualified with the adhesive.** Release agent transfer.

**Room temperature dry allowables used.** Hot-wet is much lower.

**Bondline edges unsealed.** Moisture ingress.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM D1002** | Lap shear strength of adhesives, metal to metal |
| ASTM D3165 | Strength in shear of adhesives in laminated assemblies |
| ASTM D3762 | Adhesive bonded surface durability, wedge test |
| **ASTM D2651** | Preparation of metal surfaces for adhesive bonding |
| ASTM D3933 | Preparation of aluminium surfaces, phosphoric acid anodise |
| **MIL-HDBK-17 / CMH-17** | Composite materials handbook, bonded joints |
| ASTM D5573 | Classifying failure modes in adhesive bonded joints |

---

## References

1. Volkersen, O., "Die Nietkraftverteilung in zugbeanspruchten Nietverbindungen", *Luftfahrtforschung*, Vol. 15, 1938.
2. Hart-Smith, L. J., *Adhesive-Bonded Single-Lap Joints*, NASA CR-112236, 1973.
3. CMH-17, *Composite Materials Handbook*, Volume 3.
