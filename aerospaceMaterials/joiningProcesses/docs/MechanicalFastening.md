[Home](../README.md) > Mechanical Fastening

# Mechanical Fastening

## Contents

- [Overview](#overview)
- [Fastener types](#fastener-types)
- [Hole quality](#hole-quality)
- [Preload](#preload)
- [Galvanic compatibility](#galvanic-compatibility)
- [Fastener materials](#fastener-materials)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Mechanical fastening is the only joining method that is reversible, and that alone justifies it for a great deal of structure. Its cost is a hole at every fastener, and holes are the fatigue critical features of the structure.

---

## Fastener types

| Type | Removable | Installation | Use |
|---|---|---|---|
| **Solid rivet** | No | Both sides access | Traditional airframe |
| **Blind rivet** | No | **One side** | Where access is single sided |
| **Lockbolt / Hi-Lok** | No | Controlled preload | **Primary structure** |
| **Bolt and nut** | **Yes** | Torque | Removable joints, fittings |
| Threaded insert | Yes | Into soft material | Aluminium and composite |
| Interference fit pin | No | Pressed | **Fatigue critical** |

**Hi-Lok and lockbolt fasteners are the primary structure answer** because their installation produces a repeatable preload independent of operator technique, which torqued fasteners do not.

**Interference fit fasteners improve fatigue life substantially** by putting the hole bore in compression, in the same way cold expansion does. They require a tighter hole tolerance and a controlled installation force.

---

## Hole quality

**The dominant variable in joint fatigue life, larger than the fastener choice.**

| Requirement | Reason |
|---|---|
| **Size and fit class** | Interference or clearance, per the joint design |
| **Perpendicularity** | An angled hole bends the fastener |
| **Surface finish** | The initiation site |
| **No burrs** | Clamp-up and initiation |
| **Edge distance 2D minimum** | Bearing and tear-out |
| Fastener pitch 4D minimum | Net section |

**A drilled hole is IT10 to IT12** and a fastener hole usually needs better, so drilling is followed by reaming. See [machiningProcesses HoleMaking.md](../../machiningProcesses/docs/HoleMaking.md).

**Cold expansion gives 3 to 10x fatigue life** and it is the standard treatment for fatigue critical holes. The hole is expanded with a mandrel, then reamed to size.

**Interlaminar burrs in a stack are the hard case** because they cannot be removed without disassembly. The traditional answer is drill, disassemble, deburr, reassemble; the modern one is one-shot drilling with parameters developed for the stack.

---

## Preload

**A bolted joint carries load by friction and by clamp-up, and preload is what provides both.**

```
F_preload = T / (K * d)
```

**`K` is the nut factor** and it is between 0.15 and 0.25 depending on the lubrication, the plating and the thread condition.

**Torque control has a scatter of plus or minus 25 to 35 percent** on the resulting preload, because `K` varies with everything. That is a very large uncertainty on a parameter the joint depends on.

| Method | Preload scatter |
|---|---|
| **Torque** | **+/- 25 to 35 %** |
| Torque plus angle | +/- 15 % |
| **Bolt stretch measurement** | **+/- 5 %** |
| **Ultrasonic bolt measurement** | +/- 5 % |
| Load indicating washers | +/- 10 % |

**Critical joints use stretch or ultrasonic measurement** and the reason is the scatter, not the accuracy of the torque wrench.

**Preload relaxation happens** through embedment of the surface asperities in the first hours and through creep and thermal cycling thereafter. Aluminium joints relax more than steel ones.

**A preloaded bolt through thick plate loads it in short transverse tension**, sustained, which is the stress corrosion loading condition. See [wroughtMaterials GrainDirection.md](../../wroughtMaterials/docs/GrainDirection.md).

---

## Galvanic compatibility

**Every fastened joint is a galvanic couple**, because the fastener and the structure are rarely the same alloy.

| Limit | Environment |
|---|---|
| **0.15 V** | Marine, coastal, and any chloride exposure |
| **0.25 V** | General |
| 0.50 V | Dry, controlled indoor |

| Couple | dE | Verdict |
|---|---|---|
| **Ti fastener in 6061** | **1.05 V** | **Rejected** |
| **316L fastener in 6061** | 0.75 V | Rejected |
| A286 in 6061 | ~0.70 V | Rejected without isolation |
| 316L to IN625 | 0.20 V | **Fails the marine limit** |
| 2024 to 7075 | ~0.05 V | Acceptable |

**Titanium and stainless fasteners in aluminium structure exceed every limit** and they are used constantly, with isolation: wet installation with sealant, cadmium or aluminium coated fasteners, or an isolating washer.

**The area ratio matters as much as the potential.** A small cathode on a large anode is tolerable; a large cathode on a small anode is severe. A steel fastener in an aluminium plate is the favourable ratio; an aluminium fastener in a steel plate is not.

---

## Fastener materials

| Material | Strength | Use |
|---|---|---|
| **A286** | 1000 MPa | **The aerospace standard.** Non-magnetic, to 700 degC |
| **Ti-6Al-4V** | 1100 MPa | Light. **Not in oxidiser systems** |
| **Alloy steel (4340, H-11)** | 1250 to 1800 MPa | Highest strength. **Hydrogen susceptible, needs plating** |
| Inconel 718 | 1250 MPa | High temperature, corrosion |
| 2024, 7075 aluminium | 400 MPa | Rivets, in aluminium structure |
| Monel | 500 MPa | Oxygen systems |

**A286 is the aerospace fastener default** and its combination is hard to beat: high strength, non-magnetic, corrosion resistant, good to 700 degC and not notably hydrogen susceptible.

**High strength steel fasteners need cadmium or an equivalent plating**, and plating introduces hydrogen, which requires a post-plate bake within 4 hours per ASTM B850. Missing the bake is a known failure mode with a service history.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Hole quality dominates joint fatigue | More than fastener choice |
| Edge distance 2D, pitch 4D | Minimums |
| Cold expansion | 3 to 10x fatigue life |
| Torque preload scatter | +/- 25 to 35 % |
| Stretch or ultrasonic for critical joints | +/- 5 % |
| Galvanic limit 0.25 V, 0.15 V marine | |
| Small cathode on large anode is tolerable | The reverse is not |
| A286 as the default fastener | |
| Post-plate bake within 4 hours | ASTM B850 |

---

## Failure modes

**Preload assumed accurate from torque.** +/- 30 %.

**Titanium fastener in aluminium without isolation.** 1.05 V.

**Small anodic area against a large cathode.** Rapid attack.

**Interlaminar burr left in a stack.** Clamp-up prevented.

**High strength plated fastener not baked.** Hydrogen embrittlement.

**Bolt preload in thick 7075-T6.** Sustained ST tension and SCC.

**Edge distance below 2D.** Tear-out.

---

## Standards

| Standard | Scope |
|---|---|
| **NASM 33540** | Fastener hole preparation |
| **NASA-STD-5020** | Requirements for threaded fastening systems |
| **ASTM B850** | Post-coating hydrogen embrittlement relief baking |
| ASTM F519 | Mechanical hydrogen embrittlement testing of plating processes |
| **MMPDS** | Joint allowables |
| MIL-STD-889 | Dissimilar metals |
| NAS / MS / AN series | Fastener specifications |
| ASTM F606 | Testing the mechanical properties of fasteners |

---

## References

1. NASA-STD-5020B, *Requirements for Threaded Fastening Systems in Spaceflight Hardware*.
2. Bickford, J. H., *An Introduction to the Design and Behavior of Bolted Joints*, 4th ed., CRC Press, 2007.
3. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
