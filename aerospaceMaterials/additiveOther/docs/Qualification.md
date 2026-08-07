[Home](../README.md) > Qualification

# Qualification

## Contents

- [Overview](#overview)
- [Why additive qualification is hard](#why-additive-qualification-is-hard)
- [What has to be qualified](#what-has-to-be-qualified)
- [Feedstock](#feedstock)
- [Witness coupons](#witness-coupons)
- [Process specific requirements](#process-specific-requirements)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Additive manufacturing makes the material and the part in the same operation, which means the material properties are a property of the build. Qualification therefore has to cover the feedstock, the machine, the parameters, the build layout and the post-processing as one system.

The requirements below follow NASA-STD-6030, and they apply to every process in this sub-domain as well as to LPBF.

---

## Why additive qualification is hard

| Reason | Detail |
|---|---|
| **The material is made with the part** | There is no certified stock to trace to |
| **Properties depend on location in the build** | Position, orientation, thermal neighbourhood |
| **Properties depend on build direction** | Anisotropy is intrinsic |
| **Defects are stochastic** | Lack of fusion, porosity, at unknown locations |
| **Small statistical base** | Nothing like the wrought production history |
| **Machine to machine variation** | Nominally identical machines are not |

**The last one is underrated.** Two machines of the same model with the same parameters produce measurably different material, because of laser or beam calibration, gas flow, optics condition and recoater state. Machine qualification is a separate requirement from process qualification for exactly this reason.

**The small statistical base is why the knockdowns are large.** An A-basis allowable wants 100 specimens from 10 lots, and additive allowables databases are still building toward that. The knockdown is uncertainty as much as material.

---

## What has to be qualified

| Element | Detail |
|---|---|
| **Feedstock** | Chemistry, size distribution, morphology, reuse history |
| **Machine** | Calibration, beam or arc characterisation, atmosphere |
| **Parameters** | Frozen. Any change requires requalification |
| **Build layout** | Position and orientation on the plate |
| **Post-processing** | Stress relief, HIP, heat treatment, surface |
| **NDE** | CT or equivalent, with a stated capability |
| **Witness coupons** | Per build, in representative positions |

**The build layout is a qualified variable**, which surprises people. Moving a part to a different plate position changes its thermal environment and therefore its properties, so the qualified layout is part of the frozen configuration.

**Parameters are frozen and change controlled.** A parameter change that improves the build still requires requalification, and that friction is a real constraint on process improvement.

---

## Feedstock

| Property | Requirement |
|---|---|
| **Chemistry** | Within specification, including interstitials |
| **Particle size distribution** | Controlled. It affects flow and packing |
| **Morphology** | Spherical, with satellites controlled |
| **Flowability** | Hall or Carney flow |
| **Moisture** | Controlled storage |
| **Reuse** | **Tracked, with a blend ratio and a cycle limit** |

**Powder reuse is the control that matters most in practice.** Powder is recovered from each build, sieved and reused, and it changes with each cycle: oxygen picks up, the size distribution shifts as fines are consumed, and morphology degrades.

**A reuse limit and a virgin blend ratio are specified**, typically a fixed fraction of virgin powder per cycle and a maximum number of cycles, with periodic chemistry verification.

**Oxygen pickup is the usual limiting parameter for titanium**, because the ELI specification is tight and reused powder drifts upward toward it.

**Wire feedstock avoids all of this**, which is a real and underrated advantage of WAAM and wire DED. Welding wire is certified stock with a lot number, and there is no reuse.

---

## Witness coupons

**Test specimens built alongside the part, in the same build, from the same powder, with the same parameters.**

| Requirement | Detail |
|---|---|
| **Same build** | Not a separate qualification build |
| **Representative position** | Where properties are expected to be worst |
| **Representative orientation** | Including the weakest build direction |
| **Same post-processing** | Through HIP and heat treatment with the part |
| Tests | Tensile, and density, hardness, metallography as required |

**Coupons are the only per-build evidence of the material properties**, since the part itself cannot be tested.

**Position matters and it has to be chosen deliberately.** A coupon at the plate centre in a favourable thermal environment does not represent a part at the edge. The qualification establishes where the worst position is and the coupons go there.

**Orientation must include the weakest direction**, which is the build direction for almost every process in this family. A coupon built only in XY does not demonstrate the Z properties the part depends on.

---

## Process specific requirements

| Process | Additional requirement |
|---|---|
| **EB-PBF** | Sintered cake removal verification, especially internal passages |
| **DED** | Substrate condition and interface bonding |
| **WAAM** | Interpass temperature record, distortion control |
| **Binder jetting** | **Sintered density per lot**, and shrinkage calibration |
| **Cold spray** | **Adhesion testing**, per ASTM C633 |
| Repair | Substrate assessment, repair count, service life limit |

**Cold spray adhesion testing is the one that has no equivalent elsewhere**, because the deposit-to-substrate bond is the design allowable rather than the deposit's own strength.

**Binder jet density has to be verified per lot** because the sinter cycle is where the density is made, and furnace variation directly changes it.

**WAAM interpass temperature is essential** because it governs both the microstructure and the accumulated distortion, and it is easily allowed to drift on a long build.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| The material is made with the part | Qualify the whole system |
| Build layout is a qualified variable | Position and orientation |
| Machine qualification is separate | Machines differ |
| Track powder reuse | Blend ratio and cycle limit |
| Wire feedstock avoids the reuse problem | An underrated advantage |
| Witness coupons in the worst position | And the weakest orientation |
| Coupons go through the same post-processing | |
| Cold spray needs adhesion testing | The allowable is the bond |

---

## Failure modes

**Coupons from a separate qualification build.** Not representative of this build.

**Coupons in a favourable plate position.** Optimistic.

**XY coupons only.** The Z direction is unverified.

**Powder reuse untracked.** Oxygen drift, especially in titanium.

**Parameters changed without requalification.** The qualification is void.

**Build layout changed.** Different thermal environment, different properties.

**LPBF qualification data applied to another process.** Not valid.

**Cold spray qualified on cohesive strength.** Adhesion governs.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6030** | Additive manufacturing requirements for spaceflight systems |
| **NASA-STD-6033** | Additive manufacturing quality |
| **ASTM F3049** | Characterising properties of metal powders for additive |
| ASTM F2924 / F3001 | Additive Ti-6Al-4V and ELI |
| ASTM F3187 | Directed energy deposition |
| ASTM F3339 | Cold spray |
| **ASTM C633** | Adhesion or cohesion strength of thermal spray coatings |
| ISO/ASTM 52920 / 52930 | Qualification principles and installation qualification |
| ASTM E1441 | Computed tomography imaging |
| AWS D20.1 | Fabrication of metal components using additive manufacturing |

---

## References

1. NASA-STD-6030, *Additive Manufacturing Requirements for Spaceflight Systems*.
2. NASA-STD-6033, *Additive Manufacturing Quality Requirements for Spaceflight Systems*.
3. Seifi, M. et al., "Progress Towards Metal Additive Manufacturing Standardization to Support Qualification and Certification", *JOM*, Vol. 69, 2017.
