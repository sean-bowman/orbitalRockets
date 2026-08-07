[Home](../README.md) > Product Forms

# Product Forms

## Contents

- [Overview](#overview)
- [The forms](#the-forms)
- [Plate and sheet](#plate-and-sheet)
- [Extrusion](#extrusion)
- [Bar and forging](#bar-and-forging)
- [Tube](#tube)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

The product form determines the grain structure, the achievable properties, the available sizes and the lead time. It is a specification element, not a purchasing detail.

---

## The forms

| Form | Definition | Grain structure | Lead time |
|---|---|---|---|
| **Sheet** | Below 6 mm | Strongly directional, fine | 4 to 8 wk |
| **Plate** | 6 mm and above | Directional, coarser with thickness | 8 to 16 wk |
| **Extrusion** | Constant section, pushed through a die | **Strongly L directional** | 12 to 20 wk |
| **Bar** | Rolled or drawn round, square, hex | L directional | 4 to 12 wk |
| **Forging** | Worked to shape | **Follows the contour** | 20 to 30 wk |
| **Tube** | Seamless or welded | Circumferential and axial | 8 to 16 wk |

**Lead time varies by a factor of five across the forms** and it is often the deciding factor on a development programme.

---

## Plate and sheet

**The 6 mm boundary is a convention** and it matters because the properties differ.

| | Sheet | Plate |
|---|---|---|
| Thickness | < 6 mm | >= 6 mm |
| Quench rate | Fast | **Slower, and it falls with thickness** |
| Properties | Higher | Lower, and falling with thickness |
| ST direction | Not meaningful | **Meaningful and dangerous** |
| Typical use | Skins, webs | Machined structure, bulkheads |

**Sheet has no meaningful short transverse direction** because it is too thin for a through-thickness load path to develop. That removes an entire class of problem, which is one reason sheet metal structure is simpler to analyse.

**Plate properties fall with thickness** because the quench rate falls, and the MMPDS tables are stratified by thickness for this reason. A 100 mm plate is a different material from a 12 mm plate of the same alloy and temper. See [ThicknessEffects.md](ThicknessEffects.md).

---

## Extrusion

**Metal is pushed through a shaped die, producing a constant cross section.**

| Property | Detail |
|---|---|
| **Grain structure** | **Very strongly aligned with the extrusion axis** |
| **L properties** | Excellent |
| **Transverse properties** | Noticeably lower |
| Section complexity | High. Hollow sections, integral flanges, tee and hat sections |
| Tooling | A die per section. Moderate cost, 12 to 20 week lead |

**Extrusions are the right answer for a long constant section member**, and a launch vehicle uses them for stringers, longerons, ring segments and rails.

**The anisotropy is stronger than in plate** because the deformation is more severe and entirely in one direction. Design around the L direction and treat the transverse properties as substantially reduced.

**Integral features come free.** An extruded stringer with an integral flange and a fastener land replaces a built-up assembly, and that is much of the reason extrusions dominate aircraft structure.

**Peripheral coarse grain is the defect to know about.** The surface layer of an extrusion can recrystallise to a very coarse grain during or after extrusion, with substantially lower properties, and it is either machined off or controlled by the extrusion practice.

---

## Bar and forging

| | Bar | Forging |
|---|---|---|
| Grain flow | Along the axis | **Follows the part contour** |
| Properties | Good L, lower radial | Best available |
| Cost | Low | High, plus tooling |
| Lead time | 4 to 12 wk | 20 to 30 wk |
| Buy-to-fly for a machined part | Poor | Good |

**The radial direction of bar is short transverse**, which is easy to forget. A fitting machined from a large diameter bar with a radial load path is loaded in ST.

**Forging is the only route where the grain flow can be designed**, and that is its whole advantage. See [formingProcesses Forging.md](../../formingProcesses/docs/Forging.md).

---

## Tube

| Type | Detail |
|---|---|
| **Seamless** | Extruded or pierced and drawn. **No weld** |
| **Welded** | Rolled from strip and seam welded |
| Welded and drawn | Welded then cold drawn, improving the weld |

**Seamless is specified for pressure and fatigue critical service** because there is no longitudinal weld in the hoop load path. It costs more and it has fewer size options.

**Welded tube is entirely adequate for many applications** and it is much cheaper, with better dimensional control and a wider size range.

**The distinction has to be on the specification.** ASTM A269 covers both seamless and welded stainless tube, and a call-out that does not state which has not specified the important thing. See [fluidSystems](../../../fluidSystems/).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Sheet below 6 mm, plate above | And they behave differently |
| Sheet has no meaningful ST | Plate does |
| Plate properties fall with thickness | Use the right MMPDS stratum |
| Extrusions are very strongly L directional | Design around it |
| Bar radial direction is ST | Easy to forget |
| Forging grain flow follows the contour | Its whole advantage |
| Specify seamless or welded for tube | It is not a detail |
| Lead time varies 5x across the forms | Often the deciding factor |

---

## Failure modes

**Plate allowables used at a thickness outside the stratum.** Optimistic.

**Extrusion loaded transversely at L allowables.** Substantially overstated.

**Fitting machined from bar with a radial load.** ST loading, unrecognised.

**Peripheral coarse grain not machined off an extrusion.** Low properties at the surface.

**Welded tube supplied where seamless was assumed.** A weld in the hoop load path.

**Forging lead time discovered late.** 30 weeks.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM B209** | Aluminium sheet and plate |
| ASTM B211 | Aluminium bar, rod and wire |
| **ASTM B221** | Aluminium extruded bar, rod, wire, profiles and tube |
| ASTM B247 | Aluminium die and hand forgings and rolled rings |
| ASTM A240 | Stainless plate, sheet and strip |
| ASTM A276 | Stainless bar and shapes |
| **ASTM A269 / A213** | Stainless tube, seamless and welded |
| MMPDS | Allowables by form and thickness |

---

## References

1. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
2. Campbell, F. C., *Manufacturing Technology for Aerospace Structural Materials*, Elsevier, 2006.
3. ASM Handbook Volume 14A, *Metalworking: Bulk Forming*.
