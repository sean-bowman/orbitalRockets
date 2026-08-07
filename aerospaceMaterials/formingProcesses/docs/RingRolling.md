[Home](../README.md) > Ring Rolling

# Ring Rolling

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [Circumferential grain flow](#circumferential-grain-flow)
- [What it makes](#what-it-makes)
- [Achievable geometry](#achievable-geometry)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A pierced billet is rolled between a driven roll and a mandrel, growing in diameter as its wall reduces. The result is a seamless ring with grain flow running all the way round it, which is the specific thing ring rolling is for.

---

## The process

| Step | Detail |
|---|---|
| **1. Upset** | The billet is upset to a pancake |
| **2. Pierce** | A hole is punched through the centre |
| **3. Ring roll** | The pierced preform is rolled between a main roll and a mandrel |
| **4. Size** | Axial rolls control the height |
| 5. Heat treat, machine, inspect | |

**The wall reduces and the diameter grows**, conserving volume. A ring can be grown to several times its preform diameter in a single heating.

**Axial rolls control the height** at the same time, which is what keeps the ring from spreading into a cone.

**Profiled rings are possible** with shaped rolls, giving an as-rolled cross section closer to the finished part and a better buy-to-fly. That needs tooling and quantity.

---

## Circumferential grain flow

**The whole point, and it is a geometric consequence of the process.**

The material is worked continuously in the circumferential direction as the ring grows, so the grain and the inclusion stringers run all the way round with no discontinuity.

| Route | Circumferential grain flow | Joint |
|---|---|---|
| **Ring rolled** | **Continuous** | **None** |
| Rolled and welded plate | Interrupted at the weld | A weld |
| Machined from plate | Straight through, cut everywhere | None |
| Cast | None | None |

**A ring loaded in hoop tension is loaded along its grain flow**, which is the best available orientation, and there is no weld to be the weak point.

**That combination is why ring rolling is the default for a highly loaded ring**: engine cases, flanges, bearing races, and tank barrel-to-dome joint rings.

**A rolled and welded ring has a weld across the hoop load path**, carrying a joint efficiency knockdown and a fatigue-critical feature at the highest stress location. See [joiningProcesses](../../joiningProcesses/).

---

## What it makes

| Application | Why ring rolling |
|---|---|
| **Engine cases** | Hoop loaded, seamless, high integrity |
| **Flanges** | Grain flow round the bolt circle |
| **Bearing races** | Circumferential flow, hardenable |
| **Tank joint rings** | Hoop loaded, no weld |
| Gear blanks | Flow round the teeth after machining |

**The buy-to-fly is around 3 : 1** for a machined-from-ring part, which is worse than a forging and much better than machining from plate.

**Profiled rolling improves that** by getting closer to the finished section, and it is worth doing at quantity.

---

## Achievable geometry

| Property | Range |
|---|---|
| Outside diameter | 200 mm to 10 m |
| Height | 50 mm to 2 m |
| Wall | 20 mm upward |
| Tolerance | IT12 to IT14 as rolled |
| Minimum wall to diameter | Roughly 1 : 100 |

**Very thin rings are the limitation.** Below about 1 percent wall to diameter the ring buckles during rolling rather than growing.

**The diameter range is enormous** and it extends well beyond what any other seamless process reaches. A 10 m ring is routine for a ring roller and impossible for anything else.

**As-rolled tolerance is coarse** and every functional surface is machined, so the allowance is substantial. Profiled rings reduce it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Continuous circumferential grain flow | The reason to use it |
| No weld in the hoop load path | The other reason |
| Buy-to-fly | ~3 : 1 |
| Diameter range | 200 mm to 10 m |
| Minimum wall to diameter | ~1 : 100 |
| As-rolled tolerance | IT12 to IT14 |
| Profiled rolling at quantity | Better buy-to-fly, more tooling |
| The default for a highly loaded ring | Against rolled and welded |

---

## Failure modes

**Wall to diameter below 1 : 100.** The ring buckles during rolling.

**Rolled and welded substituted for cost.** A weld across the hoop load path.

**As-rolled tolerance assumed usable.** Every surface is machined.

**Profiled tooling ordered for a low quantity.** It does not amortise.

**Preform volume wrong.** The finished ring is the wrong section.

**Grain flow assumed without a macro-etch requirement.** Unverified.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM A788 | Steel forgings, general requirements |
| **AMS 2154 / MIL-STD-2154** | Ultrasonic inspection of wrought metal products |
| AMS 4928 | Ti-6Al-4V bars, forgings and rings |
| AMS 5662 | IN718 bars, forgings and rings |
| ASTM B247 | Aluminium alloy die and hand forgings and rolled rings |
| ASTM E381 | Macroetch testing, for grain flow |

---

## References

1. ASM Handbook Volume 14A, *Metalworking: Bulk Forming*.
2. Allwood, J. M. et al., "The Development of Ring Rolling Technology", *Steel Research International*, Vol. 76, 2005.
3. Altan, T., Ngaile, G. and Shen, G., *Cold and Hot Forging: Fundamentals and Applications*, ASM International, 2005.
