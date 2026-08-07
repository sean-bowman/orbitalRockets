[Home](../README.md) > Hydroforming

# Hydroforming

## Contents

- [Overview](#overview)
- [Sheet hydroforming](#sheet-hydroforming)
- [Tube hydroforming](#tube-hydroforming)
- [Pressure sizing](#pressure-sizing)
- [Where it wins](#where-it-wins)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Hydroforming replaces one half of a matched tool set with fluid pressure. That halves the tooling cost and it changes the friction and thinning behaviour in a way that improves the achievable shape.

---

## Sheet hydroforming

**A rubber diaphragm backed by hydraulic pressure presses the sheet against a single rigid form block.**

| Property | Value |
|---|---|
| Minimum r/t | 2.0 |
| **Tolerance** | **+/- 0.2 mm** |
| Tooling | **Medium. One block, not a matched pair** |
| Rate | Medium |

**The tooling saving is the primary attraction.** A matched die set for a deep drawn part is two precision tools; a hydroform needs one, and the diaphragm adapts to whatever shape it is pressed against.

**The pressure is uniform over the whole surface**, which is the mechanical difference from a rigid punch. A rigid punch contacts first at the high points and generates friction there; uniform pressure does not, so the strain distributes more evenly and the part thins less at the critical points.

**More even thinning means a deeper shape from the same material**, and that is the second attraction.

**The limitation is depth and pressure.** Deep shapes need very high pressure, and the press has to contain it over the full blank area, so press force grows with the blank area times the pressure.

---

## Tube hydroforming

**A tube is placed in a die, sealed at both ends, and pressurised internally while the ends are pushed inward.**

| Element | Role |
|---|---|
| **Internal pressure** | Expands the tube against the die |
| **Axial feed** | Pushes material in to replace what the expansion thins |
| Die | Defines the final shape |

**The axial feed is what makes it work.** Pressure alone thins the tube until it bursts. Feeding material in from the ends replaces the thinned material and allows a much larger expansion.

**The pressure and feed have to be coordinated** through the cycle, and that coordination is the process's difficulty. Too much pressure early bursts the tube; too much feed early buckles it.

**It makes complex tubular parts in one piece** that would otherwise be several pieces welded, which is its main application: structural frame members, manifolds and exhaust components.

---

## Pressure sizing

For sheet hydroforming against a form block, the pressure needed to make the sheet conform to a radius `r` follows from thin shell equilibrium:

```
p = 2 * sigma_flow * t / r
```

**Small radii need high pressure**, and the inverse dependence is strong. A 2 mm sheet of a 400 MPa flow stress material needs

| Form radius | Pressure |
|---|---|
| 50 mm | 32 MPa |
| 20 mm | 80 MPa |
| **5 mm** | **320 MPa** |

**That is why hydroformed parts have generous radii.** The sharp corner that a rigid punch would form at moderate force needs an impractical pressure from a diaphragm.

**Typical machine capability is 50 to 100 MPa**, with specialised presses to 400 MPa. Sizing the pressure early tells you immediately whether the shape is hydroformable.

**The press force is pressure times blank area**, so a large panel at high pressure needs an enormous press. A 1 m by 1 m blank at 80 MPa needs 80 MN, which is a very large machine.

---

## Where it wins

| Condition | Why |
|---|---|
| **Complex shallow shapes** | Uniform pressure distributes the strain |
| **Low to medium volume** | One tool instead of two |
| **Tight tolerance** | +/- 0.2 mm, better than stretch or draw |
| Generous radii | Which the pressure limit requires anyway |
| Tubular structures in one piece | Tube hydroforming |

**It loses on deep shapes and sharp radii**, both for the same reason: the pressure required.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `p = 2 sigma_flow t / r` | Sizes the pressure |
| Machine capability | 50 to 100 MPa typical |
| Press force | Pressure times blank area |
| Generous radii | Sharp corners need impractical pressure |
| Tolerance | +/- 0.2 mm |
| Tooling | One block, not a matched pair |
| Tube forming needs coordinated feed | Pressure alone bursts it |

---

## Failure modes

**Sharp radius specified.** The pressure needed is beyond the machine.

**Press force sized on pressure alone.** It is pressure times area.

**Tube hydroformed without axial feed.** It thins and bursts.

**Axial feed too high early.** The tube buckles.

**Diaphragm life ignored.** It is a consumable, and it fails on sharp features.

---

## Worked numbers

From [`FormingProcess.calculateHydroformPressure`](../formingProcessesLibrary/FormingProcess.py), 2 mm 6061-O:

| Form radius | Required pressure | Within a 100 MPa machine |
|---|---|---|
| 50 mm | ~16 MPa | yes |
| 20 mm | ~40 MPa | yes |
| **5 mm** | **~160 MPa** | **no** |

---

## Standards

| Standard | Scope |
|---|---|
| ASTM E2218 | Determining forming limit curves |
| ASTM E646 | Tensile strain hardening exponents |
| ASTM E517 | Plastic strain ratio r |
| SAE ARP1917 | Sheet metal forming terminology |

---

## Tool interface

```python
from FormingProcess import FormingProcess

for radius in (0.050, 0.020, 0.005):
    forming = FormingProcess()
    forming.setInputs({'material': '6061', 'condition': 't6', 'process': 'hydroform',
                       'thickness': 0.002, 'bendRadius': radius})
    result = forming.calculateHydroformPressure()
    for key in sorted(result):
        print(f'  r={radius*1000:5.1f} mm  {key}: {result[key]}')
```

---

## References

1. Hosford, W. F. and Caddell, R. M., *Metal Forming: Mechanics and Metallurgy*, 4th ed., Cambridge, 2011.
2. Koc, M. (ed.), *Hydroforming for Advanced Manufacturing*, Woodhead, 2008.
3. ASM Handbook Volume 14B, *Metalworking: Sheet Forming*.
