[Home](../README.md) > Chamber Structures

# Chamber Structures

## Contents

- [Overview](#overview)
- [The liner and jacket are one structure](#the-liner-and-jacket-are-one-structure)
- [Thermal strain dominates](#thermal-strain-dominates)
- [Doghouse failure](#doghouse-failure)
- [Low cycle fatigue](#low-cycle-fatigue)
- [Material selection](#material-selection)
- [Additive manufacture](#additive-manufacture)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A regeneratively cooled chamber is a pressure vessel with a large temperature gradient through its wall and a set of channels machined into the middle of it. Each of those three facts is manageable; together they produce a structure whose governing load case is not pressure.

**The chamber fails by thermal strain and low cycle fatigue, not by burst.** A chamber sized only as a pressure vessel will be adequately strong and will not last.

---

## The liner and jacket are one structure

The inner liner carries the hot gas and the coolant channels. The outer jacket closes the channels and carries most of the hoop load. They are bonded, brazed or grown together, and they act as one.

The load split is not obvious. **The liner is hot, soft and thin; the jacket is cool, stiff and thicker**, so the jacket takes a disproportionate share of the pressure load, and the liner takes a disproportionate share of the thermal load. Analysing either alone gets both wrong.

The coolant pressure is **higher than the chamber pressure**, because the coolant has to reach the injector and get through it. So the liner is loaded inward by the coolant, not outward by the chamber gas, over most of its area. That reverses the sign of the pressure stress relative to what a first sketch suggests.

For the [worked example](../codeInterface.py), chamber pressure is 10 MPa and the coolant side runs at 12.5 MPa at the inlet. The liner sees a 2.5 MPa inward differential plus a 163 K gradient through 1 mm.

---

## Thermal strain dominates

The hot face is at 800 K and the cold face at 637 K, through a millimetre of copper alloy. The hot face wants to expand relative to the cold face and cannot, because they are the same piece of metal.

The restrained thermal strain is:

```
eps = alpha dT
```

For GRCop-42 at roughly 17e-6 per kelvin and a 163 K gradient, that is **0.28 per cent**. The yield strain of the alloy at temperature is of the same order.

**So the liner yields on the first firing, in compression, on the hot face.** That is not a failure and it is not avoidable; it is the design condition. On shutdown the wall cools, the compressive plastic strain is locked in, and the hot face goes into tension. The next firing reverses it again.

**That is a low cycle fatigue problem with roughly one cycle per firing**, and it is why a chamber's life is quoted in firings rather than in seconds.

---

## Doghouse failure

The characteristic failure mode of a regeneratively cooled liner, and it is worth knowing by name because the mechanism is not obvious.

The channel land between two coolant passages is the hottest and most restrained part of the liner. Over repeated cycles the accumulated plastic strain thins and bulges the land into the coolant channel, which reduces the flow area, which raises the local wall temperature, which accelerates the thinning.

The bulged cross-section looks like a doghouse in section, which is where the name comes from. **The end state is a crack through the land into the coolant channel**, at which point coolant enters the chamber. On a fuel-cooled chamber that is a fuel-rich streak and a survivable anomaly. On anything oxidiser-cooled it is not.

Three things drive it: the temperature gradient, the number of cycles, and the ratio of land width to channel width. It is the reason liner life is a design requirement rather than an outcome.

---

## Low cycle fatigue

Life is set by strain range rather than by stress amplitude, which is the defining characteristic of the low cycle regime. The Coffin-Manson relation applies:

```
N_f ~ (plastic strain range)^-c
```

with `c` around 0.5 to 0.6 for the copper alloys.

**The practical consequence is that life is extremely sensitive to wall temperature**, because the strain range follows the gradient. A wall running 100 K hotter than design does not lose ten per cent of its life; it loses a large fraction of it.

That sensitivity is why the wall temperature limits in the cooling class are life limits rather than melting limits. GRCop-42 at 800 K is nowhere near melting. It is at the temperature above which the cycle count falls away quickly.

See [aerospaceMaterials](../../../aerospaceMaterials/docs/FractureAndDamageTolerance.md) for the fatigue machinery and [aerospaceStructures](../../../aerospaceStructures/README.md) for the general structural treatment.

---

## Material selection

The liner requirement is unusual: **high thermal conductivity first, strength at temperature second.** That ordering is the opposite of most structural choices and it follows directly from the wall drop.

| Material | `k` [W/m K] | Wall drop at 52.1 MW/m^2 through 1 mm |
|---|---|---|
| GRCop-42 | 320 | 163 K |
| NARloy-Z | 320 | 163 K |
| C18150 | 320 | 163 K |
| Inconel 718 | 25 | 2085 K |

**A superalloy liner at this flux is not a wall.** The copper alloys are chosen despite poor strength at temperature because nothing else keeps the gradient survivable.

The copper alloys differ from each other mainly in how they hold strength and how they behave over cycles. GRCop-42 is the modern choice: it is dispersion strengthened, it holds up over cycles better than the older alloys, and it is printable.

The jacket is a different problem and is usually a nickel alloy or stainless, chosen for strength because it is cool.

---

## Additive manufacture

The chamber is one of the strongest cases for metal additive manufacture in the whole vehicle, and the reason is geometric rather than economic.

Coolant channels are internal, they vary in cross-section along the chamber, and the traditional route is to machine slots into a liner and then close them with an electrodeposited or brazed jacket. That is a long process with a difficult joint that is loaded exactly where it is hardest to inspect.

**Printing the liner with the channels closed removes the joint.** That is the point, and the cost and lead time benefits are secondary to it.

The constraints that come with it belong to [aerospaceMaterials](../../../aerospaceMaterials/additiveLPBF/README.md): the channels are self-supporting horizontal features with a downskin roughness that is worse than a machined surface, and that roughness enters the coolant pressure drop and the heat transfer. See [extrusionHoning](../../../aerospaceMaterials/extrusionHoning/README.md) for what can be done about it.

---

## Design rules of thumb

- **Analyse the liner and jacket together.** Neither is right alone.
- **Remember the coolant pressure exceeds the chamber pressure.** The liner is loaded inward.
- **Size for thermal strain and cycles, not for burst.** The pressure case is rarely governing.
- **Treat the wall temperature limit as a life limit**, because it is.
- **Choose the liner on conductivity first.** An order of magnitude in `k` is an order of magnitude in gradient.
- **Watch the land to channel width ratio.** It drives the doghouse mode.
- **Print the liner if the channels are complex.** The joint you avoid is the one you cannot inspect.

---

## Failure modes

**Doghouse.** Progressive land thinning into the coolant channel over cycles, ending in a crack. The characteristic regenerative liner failure.

**Chamber sized as a pressure vessel only.** Strong enough and short lived.

**Wall temperature limit treated as a melting limit.** It is a life limit and it is hundreds of kelvin below melting.

**Superalloy liner at high flux.** Two thousand kelvin through a millimetre.

**Jacket analysed without the liner.** The load split is not what either alone suggests.

**Printed channel roughness ignored.** It enters both the pressure drop and the heat transfer, in opposite directions.

---

## Worked numbers

The [worked example](../codeInterface.py) chamber liner.

| Quantity | Value |
|---|---|
| Chamber pressure | 10.0 MPa |
| Coolant inlet pressure | 12.5 MPa |
| Liner differential, inward | 2.5 MPa |
| Peak flux | 52.1 MW/m^2 |
| Wall thickness | 1.0 mm |
| Wall drop, GRCop-42 | 163 K |
| Hot face | 800 K |
| Cold face | 637 K |
| Restrained thermal strain at 17e-6 per K | 0.28 % |
| Same wall in Inconel 718 | 2085 K drop |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA-STD-5012** | **Strength and life assessment for rocket engines.** The structural counterpart to everything here |
| NASA SP-8087 | Fluid-cooled combustion chambers |
| AIAA S-080 | Metallic pressure vessels |
| NASA-STD-6030 | Additive manufacturing requirements for spaceflight hardware |
| MMPDS | Allowables, though not for the copper alloys, which are programme specific |

---

## Tool interface

The wall thermal state comes from the cooling class; the structural assessment belongs to [aerospaceStructures](../../../aerospaceStructures/README.md).

```python
from RegenerativeCooling import RegenerativeCooling

cooling = RegenerativeCooling()
cooling.setInputs({'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6,
                   'throatDiameter': 0.0906, 'coolantFlow': 10.34,
                   'wallMaterial': 'GRCop-42', 'wallThickness': 0.001})

wall = cooling.calculateWallTemperature()

print(wall['wallDrop'], wall['coolantSideTemperature'])

for name, entry in wall['comparison'].items():
    print(f'{name:14s} {entry["wallDrop"]:7.0f} K')
```

---

## References

- NASA-STD-5012, *Strength and life assessment requirements for liquid fueled space propulsion system engines*
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
- Quentmeyer, *Experimental fatigue life investigation of cylindrical thrust chambers*
- Ellis, *GRCop-84: a high temperature copper alloy for high heat flux applications*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
