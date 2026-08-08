[Home](../README.md) > Standards Index

# Standards Index

## Contents

- [Overview](#overview)
- [Design factors and loads](#design-factors-and-loads)
- [Stability and buckling](#stability-and-buckling)
- [Pressure vessels](#pressure-vessels)
- [Joints and fasteners](#joints-and-fasteners)
- [Fracture and NDE](#fracture-and-nde)
- [Dynamics and test](#dynamics-and-test)
- [Materials and allowables](#materials-and-allowables)
- [How they fit together](#how-they-fit-together)
- [References](#references)

---

## Overview

An annotated index of the standards this domain works to, with what each one is actually for. The list is deliberately short: these are the documents a launch vehicle structures engineer opens, not everything that exists.

---

## Design factors and loads

| Standard | What it gives you |
|---|---|
| **NASA-STD-5001** | **The factor ladder.** Yield 1.10, ultimate 1.40 by test; 1.60 and 2.00 by analysis. Also the casting factors |
| NASA-STD-5002 | Load analyses of spacecraft and payloads. Coupled loads analysis requirements |
| ECSS-E-ST-32 | The European equivalent of 5001, structural general requirements |
| SMC-S-016 | Test requirements for launch, upper stage and space vehicles |

**NASA-STD-5001 is the document everything else hangs from.** If you read one, read that.

---

## Stability and buckling

| Standard | What it gives you |
|---|---|
| **NASA SP-8007** | **Cylinders.** The knockdown curve this domain implements |
| **NASA SP-8019** | **Cones.** The analogous treatment for truncated cones |
| NASA SP-8032 | Doubly curved shells, domes |
| NASA SP-8068 | Buckling strength of structural plates |
| ECSS-E-HB-32-24 | European buckling handbook, more recent and more comprehensive |

**The SP-8000 series dates from 1965 to 1975 and is still the working basis**, which says something about how little the empirical picture has moved. The modern work is in relaxing the knockdowns for shells whose imperfections have been measured.

---

## Pressure vessels

| Standard | What it gives you |
|---|---|
| **AIAA S-080** | **Metallic pressure vessels and pressurized structures.** The factors and the qualification |
| **AIAA S-081** | Composite overwrapped pressure vessels. Stress rupture is the difference |
| MIL-STD-1522 | Pressurized systems safety, older but still cited |
| ASME BPVC Section VIII | Terrestrial pressure vessels. Different philosophy, occasionally invoked |

**S-080 and S-081 differ substantially** and the reason is stress rupture: a composite overwrap held at load for a long time fails in a way metal does not, so the COPV standard carries a time-at-pressure requirement that the metallic one has no equivalent of.

---

## Joints and fasteners

| Standard | What it gives you |
|---|---|
| **NASA-STD-5020** | **Threaded fastening systems.** Preload bounds, separation, the analysis method |
| VDI 2230 | The most complete bolted joint calculation method available |
| NASM 33540 | Fastener hole preparation |
| **AWS D17.1** | Fusion welding for aerospace |
| AWS D17.3 | Friction stir welding for aerospace |
| ASTM B850 | Post-plating hydrogen embrittlement bake |

**NASA-STD-5020 requires the analysis at both preload bounds**, which is the requirement most often missed and the reason this domain's `BoltedJoint` reports both.

---

## Fracture and NDE

| Standard | What it gives you |
|---|---|
| **NASA-STD-5019** | **Fracture control.** Classification, and what each class requires |
| **NASA-STD-5009** | NDE for fracture critical components. The flaw sizes |
| ASTM E399 / E1820 | Fracture toughness measurement |
| ASTM E647 | Fatigue crack growth rate measurement |
| ASTM E1417 / E1742 | Penetrant and radiographic examination |
| ASTM E2700 | Phased array ultrasonic |

**5019 and 5009 are used together.** 5019 says whether a part is fracture critical; 5009 says what flaw size the inspection can be credited with, which is the input the analysis needs.

---

## Dynamics and test

| Standard | What it gives you |
|---|---|
| NASA-STD-7001 | Payload vibroacoustic test criteria |
| NASA-HDBK-7005 | Dynamic environmental criteria |
| **NASA SP-8055** | POGO prevention |
| ECSS-E-ST-32-11 | Modal survey assessment. Correlation criteria |
| MIL-STD-810 | Environmental test methods, widely referenced |

---

## Materials and allowables

| Standard | What it gives you |
|---|---|
| **MMPDS** | **Metallic allowables.** A-basis and B-basis, by form, thickness and orientation |
| CMH-17 | Composite materials handbook |
| NASA-STD-6016 | Materials and processes requirements for spacecraft |
| MIL-HDBK-5 | The predecessor to MMPDS, still cited in older documents |

**MMPDS is the source this domain's allowables come from**, through the [aerospaceMaterials](../../aerospaceMaterials/) database rather than directly.

---

## How they fit together

A structural analysis of a launch vehicle tank touches most of the list in a definite order:

| Step | Standard |
|---|---|
| **1. Establish factors** | NASA-STD-5001 |
| **2. Define load cases** | NASA-STD-5002, the vehicle user guide |
| **3. Get allowables** | MMPDS, through NASA-STD-6016 |
| **4. Size for pressure** | AIAA S-080 |
| **5. Check stability** | NASA SP-8007 |
| **6. Design the joints** | NASA-STD-5020, AWS D17.1 |
| **7. Fracture control** | NASA-STD-5019, NASA-STD-5009 |
| **8. Verify dynamics** | NASA-STD-5002, ECSS-E-ST-32-11 |
| 9. Test | SMC-S-016, NASA-STD-7001 |

**The order matters.** Factors before loads, loads before allowables, allowables before sizing, and fracture control decided early enough that the NDE capability it needs can actually be provided.

---

## References

1. NASA-STD-5001B, *Structural Design and Test Factors of Safety for Spaceflight Hardware*.
2. NASA SP-8007, *Buckling of Thin-Walled Circular Cylinders*, revised 1968.
3. AIAA S-080A, *Space Systems: Metallic Pressure Vessels, Pressurized Structures, and Pressure Components*.
