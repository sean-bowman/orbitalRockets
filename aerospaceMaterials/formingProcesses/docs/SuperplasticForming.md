[Home](../README.md) > Superplastic Forming

# Superplastic Forming

## Contents

- [Overview](#overview)
- [What superplasticity requires](#what-superplasticity-requires)
- [The strain rate sensitivity](#the-strain-rate-sensitivity)
- [The process](#the-process)
- [SPF/DB](#spfdb)
- [Why it is slow](#why-it-is-slow)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Some alloys, in a specific microstructural condition and within a narrow temperature and strain rate window, elongate several hundred percent without necking. Superplastic forming exploits that to make shapes no conventional process can reach.

It is slow, it is expensive, and for complex titanium structure it is often the only option.

---

## What superplasticity requires

**All three conditions simultaneously.**

| Condition | Requirement |
|---|---|
| **Fine grain size** | **Below 10 um**, and stable at temperature |
| **Temperature** | Above roughly 0.5 of the melting point in kelvin |
| **Strain rate** | **10^-4 to 10^-3 per second.** Very slow |

**The fine grain requirement is the hard one.** The mechanism is grain boundary sliding, which needs many small grains, and the grains have to resist coarsening for the hours the forming takes at temperature.

| Alloy | Temperature | Notes |
|---|---|---|
| **Ti-6Al-4V** | 900 to 925 degC | **The main aerospace application** |
| Al 5083 SPF | 500 to 520 degC | A specially processed grade |
| Al 2004 (Supral) | 460 degC | Zirconium stabilised |
| Al 7475 SPF | 515 degC | High strength |

**The alloy has to be bought as a superplastic grade.** Standard 5083 is not superplastic; SPF 5083 has been thermomechanically processed to a fine stable grain structure and it costs more.

---

## The strain rate sensitivity

**The parameter that explains everything about the process.**

```
sigma = K * (deps/dt)^m
```

**`m` is the strain rate sensitivity**, and superplastic behaviour needs `m` above about 0.3, with the best alloys reaching 0.5 to 0.8.

**High `m` resists necking**, and the mechanism is direct: where a neck starts to form, the local strain rate rises, so the local flow stress rises, so the neck stops growing and the deformation moves elsewhere.

| m | Behaviour |
|---|---|
| ~0 | Conventional. Necking runs away |
| 0.1 to 0.2 | Conventional hot working |
| **0.3 to 0.8** | **Superplastic. Necking is self-arresting** |
| 1.0 | Newtonian viscous, like glass |

**At `m` = 1 the material behaves like a viscous liquid**, and superplastic alloys approach that. Elongations of 500 to 1000 percent are routine and 2000 percent has been demonstrated.

**`m` collapses outside the strain rate window**, which is why the rate has to be controlled so tightly, and why the process cannot simply be run faster.

---

## The process

| Step | Detail |
|---|---|
| **1. Load** | The blank is clamped over a single-sided die in a heated press |
| **2. Heat** | To the forming temperature, and soak |
| **3. Pressurise** | Argon gas pressure, ramped to hold the target strain rate |
| **4. Form** | Hours. The sheet blows into the die cavity |
| **5. Cool and unload** | |

**The pressure profile is the control variable.** The strain rate depends on the pressure and the current geometry, so holding a constant strain rate requires a pressure that changes continuously through the cycle. That profile is computed, not guessed.

**Tooling is single sided**, like hydroforming, and it has to survive hundreds of hours at 900 degC. Ceramic and superalloy dies are used and they are expensive.

**Thinning is severe and uneven.** The last region to contact the die has been stretching the whole time and it ends up thinnest, often at a corner. Predicting the thickness distribution is a required part of the design.

---

## SPF/DB

**Superplastic forming combined with diffusion bonding, in one heated cycle.**

Titanium diffusion bonds readily at the superplastic forming temperature, so sheets can be selectively bonded where they touch and then blown apart where they are not.

| Structure | Result |
|---|---|
| **Two sheet** | A hollow shell with integral bonded edges |
| **Three sheet** | A sandwich with an integral formed core |
| **Four sheet** | A truss core sandwich |

**It produces integrally stiffened hollow titanium structure with no fasteners and no welds**, and nothing else does. Fan blades, engine nacelle structure and hot leading edges are the applications.

**The part count reduction is dramatic.** A fabricated equivalent might be dozens of pieces with hundreds of fasteners; the SPF/DB part is one.

**Bond line quality is the qualification problem.** A diffusion bond is a solid state joint with no fusion, and inspecting it is difficult: ultrasonic works where the geometry allows and a weak bond can look like a good one.

---

## Why it is slow

**The strain rate window is the reason and it is not negotiable.**

At 10^-3 per second, a 200 percent elongation takes

```
t = ln(3) / 1e-3 = 1100 s
```

roughly twenty minutes at the fastest usable rate. At 10^-4 it is three hours, and real parts with a soak and a controlled ramp run four to eight hours.

**One part per shift is a normal rate**, and that sets the economics entirely: SPF is for low volume, high value, geometrically impossible parts.

**Running faster loses the superplasticity.** Above the window `m` falls, necking is no longer self-arresting, and the part splits. The rate limit is physical rather than a machine limitation.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Grain size below 10 um | And stable at temperature |
| Strain rate 10^-4 to 10^-3 /s | Non-negotiable |
| `m` above 0.3 | The necking resistance |
| Ti-6Al-4V at 900 to 925 degC | The main application |
| Buy the superplastic grade | Standard alloy is not superplastic |
| Compute the pressure profile | It holds the strain rate |
| Predict the thinning | The last corner is thinnest |
| Cycle time | 4 to 8 hours |

---

## Failure modes

**Standard grade used instead of SPF grade.** Not superplastic.

**Strain rate too high.** `m` falls, and the part splits.

**Constant pressure instead of a profile.** The strain rate wanders out of the window.

**Thinning not predicted.** A corner ends up below minimum gauge.

**Grain coarsening during the long soak.** Superplasticity lost partway through.

**SPF/DB bond line assumed sound.** It is difficult to inspect and a weak bond looks like a good one.

**Rate expectations set from conventional forming.** One part per shift.

---

## Standards

| Standard | Scope |
|---|---|
| AMS 4911 | Ti-6Al-4V sheet, strip and plate, annealed |
| AMS 2801 | Heat treatment of titanium alloy parts |
| AMS 2750 | Pyrometry |
| ASTM E2448 | Determining the superplastic properties of metallic sheet |
| ASTM E8 / E8M | Tension testing |

---

## References

1. Ridley, N. (ed.), *Superplasticity: 60 Years After Pearson*, Institute of Materials, 1995.
2. Barnes, A. J., "Superplastic Forming 40 Years and Still Growing", *Journal of Materials Engineering and Performance*, Vol. 16, 2007.
3. ASM Handbook Volume 14B, *Metalworking: Sheet Forming*.
