[Home](../README.md) > Binder Jetting

# Binder Jetting

## Contents

- [Overview](#overview)
- [The process](#the-process)
- [Sintering shrinkage](#sintering-shrinkage)
- [Density](#density)
- [What it achieves](#what-it-achieves)
- [Sand moulds](#sand-moulds)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A print head deposits binder onto a powder bed, layer by layer, producing a fragile green part that is then debound and sintered. Nothing melts during printing, so there is no thermal stress, no supports and no build direction anisotropy from solidification.

The shrinkage during sintering is the whole engineering problem.

---

## The process

| Step | Detail |
|---|---|
| **1. Print** | Binder jetted onto a powder bed. Fast, and it scales with print head width |
| **2. Cure** | The binder is cured, giving green strength |
| **3. Depowder** | Loose powder removed. **No supports to cut off** |
| **4. Debind** | The binder is burned or dissolved out |
| **5. Sinter** | **Furnace, near the melting point. The part shrinks 15 to 20 %** |
| 6. Infiltrate or HIP | Optional, to raise the density |

**Printing is fast and it does not scale with part complexity**, because the print head sweeps the whole layer regardless of what is in it. A build plate full of parts prints in the same time as one part.

**No supports and no thermal stress** means the green part can be nested densely in three dimensions, which is a genuine throughput advantage over every fusion process.

**The green part is very fragile**, roughly the strength of a compressed chalk, and handling it is a real process concern.

---

## Sintering shrinkage

**15 to 20 percent linear, and it is the dominant design problem.**

| Consequence | Detail |
|---|---|
| **The printed part is 20 % oversize** | Scaled from the finished geometry |
| **Shrinkage must be uniform** | Or the part distorts |
| **Non-uniform sections shrink differently** | Thick and thin sections disagree |
| **Gravity acts during sintering** | The part is soft at temperature |
| Setters and supports | Ceramic setters support the part in the furnace |

**Uniform section thickness matters more here than in any other additive process**, because a part with a thick boss on a thin wall shrinks at different rates and warps.

**Gravity distortion during sintering** is a real and unfamiliar failure mode. The part is at 80 to 90 percent of its melting point for hours, with very little strength, and an unsupported overhang sags. Ceramic setters shaped to the part support it.

**Shrinkage is anisotropic in practice** because the powder bed density varies slightly with direction and because gravity acts vertically. Compensation is a calibrated scaling factor per axis, developed for a specific machine, material and geometry family.

---

## Density

| Route | Density |
|---|---|
| **As sintered** | **95 to 99 %** |
| Sintered plus HIP | 99.5 % or better |
| **Infiltrated** | Full, with a second material |

**As-sintered porosity is the property limitation.** A 97 percent dense part has 3 percent porosity distributed through it, and that porosity reduces the fatigue properties far more than it reduces the static strength.

**HIP closes the internal porosity** and it does not close surface connected porosity, which in a sintered part can be a substantial fraction of the total. That is a more significant limitation here than in a fusion process.

**Bronze infiltration of steel parts** produces a full density composite at lower cost than HIP, and the resulting material is neither the steel nor the bronze in its properties. It is a real material with its own allowables and it is not a substitute for a wrought steel.

**For aerospace structure, HIP is required**, and the resulting properties approach but do not equal wrought.

---

## What it achieves

| Property | Value |
|---|---|
| **Tolerance** | IT11, after shrinkage compensation |
| Surface | 6 to 15 um Ra |
| Build volume | Up to 500 mm |
| Minimum wall | 1 to 2 mm |
| **Rate** | **High.** Printing does not scale with complexity |
| **Cost** | **Low at volume** |
| Materials | Stainless, tool steel, Inconel, tungsten, ceramics |

**Its case is volume production of small to medium parts** at moderate property requirements, where the printing throughput and the low machine cost dominate.

**It is not a structural aerospace process** in the way LPBF has become, and the reason is the density and the dimensional control rather than any single disqualifying property.

---

## Sand moulds

**The application that has changed casting**, and it is worth knowing even in a metal additive context.

**Binder jetting sand produces a casting mould directly from CAD**, with no pattern and no core box.

| Consequence | Detail |
|---|---|
| **No pattern cost** | The main tooling cost of sand casting removed |
| **Complex cores** | Printed as one piece, in geometries no core box makes |
| **Lead time** | Weeks rather than months |
| Dimensional control | Better than a conventional sand mould |

**That makes a one-off sand casting economically viable**, which it was not, and it puts sand casting back into competition with additive for large simple one-off parts. See [castingProcesses SandCasting.md](../../castingProcesses/docs/SandCasting.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Shrinkage 15 to 20 % linear | Print oversize |
| **Uniform section thickness** | Or it warps |
| Support against gravity during sintering | Ceramic setters |
| As-sintered density 95 to 99 % | |
| HIP for aerospace structure | And it misses surface porosity |
| No supports, no thermal stress | Dense 3D nesting |
| Printing does not scale with complexity | The throughput case |
| Binder jet sand for casting moulds | No pattern |

---

## Failure modes

**Non-uniform sections.** Differential shrinkage and warping.

**Unsupported overhang during sintering.** Gravity sag.

**As-sintered density assumed full.** 3 to 5 % porosity.

**HIP expected to close surface connected porosity.** It does not.

**Infiltrated part treated as the base metal.** It is a different material.

**Green part handling damage.** It has almost no strength.

**Isotropic shrinkage assumed.** It is anisotropic in practice.

---

## Standards

| Standard | Scope |
|---|---|
| **ISO/ASTM 52900** | Additive manufacturing terminology |
| NASA-STD-6030 | Additive manufacturing requirements for spaceflight |
| **MPIF standards** | Powder metallurgy, sintered density and properties |
| ASTM B962 | Density of sintered powder metallurgy parts |
| ASTM B925 | Preparing metallographic specimens of PM materials |
| ASTM A1080 | Hot isostatic pressing |

---

## References

1. Gibson, I., Rosen, D. and Stucker, B., *Additive Manufacturing Technologies*, 3rd ed., Springer, 2021.
2. Mostafaei, A. et al., "Binder Jet 3D Printing: Process Parameters, Materials, Properties and Challenges", *Progress in Materials Science*, Vol. 119, 2021.
3. German, R. M., *Sintering: From Empirical Observations to Scientific Principles*, Butterworth-Heinemann, 2014.
