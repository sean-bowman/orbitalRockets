[Home](../README.md) > Mould Design

# Mould Design

## Contents

- [Overview](#overview)
- [Permanent against expendable](#permanent-against-expendable)
- [Coatings](#coatings)
- [Thermal management](#thermal-management)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

The mould does two jobs that conflict: it extracts heat fast enough to give a fine directional structure, and it survives being filled with molten metal several hundred times.

---

## Permanent against expendable

| Type | Material | Life | Use |
|---|---|---|---|
| **Permanent (die)** | Steel or cast iron | Hundreds to thousands | Production. Fast cooling, fine structure |
| **Expendable (sand-lined)** | Sand on a steel shell | One | Large parts, short runs, high melting alloys |
| Graphite | Graphite | Tens to hundreds | Copper alloys, and a good surface |

**Permanent moulds give the better casting.** Faster cooling means a finer structure, a shorter solidification time, and a lower capture number requirement. The limit is thermal fatigue of the mould.

**Expendable liners are for anything the die cannot survive.** A steel mould filled with molten steel at 1600 degC has a short life, so a sand or refractory lining is used and discarded.

**The tradeoff is directly visible in the solidification time.** A sand-lined mould has a Chvorinov constant roughly twice a metal mould's, so it freezes half as fast, which halves the front velocity and doubles the capture number. Slower cooling gives a coarser structure and a cleaner casting.

---

## Coatings

**Every permanent mould is coated**, and the coating does three jobs at once.

| Job | Detail |
|---|---|
| **Thermal barrier** | Slows heat extraction, controlling the structure and protecting the mould |
| **Release** | The casting has to come out |
| **Chemical barrier** | Stops the melt welding to or alloying with the mould |

| Coating | Use |
|---|---|
| Refractory wash (zircon, alumina) | The general answer |
| Graphite | Copper alloys, good release |
| Ceramic slurry | Where a thicker barrier is wanted |

**Coating thickness is a process variable, not a housekeeping detail.** It sets the effective Chvorinov constant, so it sets the solidification time, so it sets the capture number and the structure. A mould re-coated more heavily than usual produces a different casting.

**Coating thrown off at high G** is one of the failure modes that bounds the speed window. Above about 150 G the coating can detach and end up in the casting, which is an inclusion source rather than a barrier.

---

## Thermal management

| Control | Effect |
|---|---|
| **Preheat** | 150 to 300 degC typical. Reduces thermal shock and slows the initial freeze |
| **External cooling** | Water or air on the mould exterior, for production rate |
| Coating thickness | The primary structural control |
| Mould mass | A heavy mould is a bigger heat sink |

**Preheat is what stops the mould cracking.** Filling a cold steel mould with melt at 1600 degC puts the bore into severe thermal shock, and thermal fatigue cracking of the mould bore is the usual end of a mould's life.

**External cooling is a production rate measure** and it has to be uniform. Cooling one side harder than the other gives a wall that is thicker on the cooled side, because the melt freezes there first.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Permanent for production | Finer structure, faster cycle |
| Expendable liner for high melting alloys | Or the mould does not survive |
| Coating thickness is a process variable | It sets the solidification time |
| Preheat | 150 to 300 degC |
| Uniform external cooling | Or the wall is eccentric |
| Coating detaches above ~150 G | One of the limits on speed |

---

## Failure modes

**Cold mould.** Thermal shock cracking of the bore.

**Coating thickness varied.** A different casting, and nobody changed a parameter.

**Coating thrown at high speed.** Inclusions from the barrier that was meant to prevent them.

**Non-uniform external cooling.** An eccentric wall.

**Mould thermal fatigue.** Cracks print through into the casting surface.

---

## Standards

| Standard | Scope |
|---|---|
| ASTM A451 / A426 | Centrifugally cast pipe |
| ISO 8062 | Casting tolerances and machining allowances |
| ASTM A802 | Steel castings, surface acceptance standards |

---

## References

1. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
2. ASM Handbook Volume 15, *Casting*.
3. Janco, N., *Centrifugal Casting*, American Foundrymen's Society, 1988.
