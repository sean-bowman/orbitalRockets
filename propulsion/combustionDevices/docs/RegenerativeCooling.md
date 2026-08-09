[Home](../README.md) > Regenerative Cooling

# Regenerative Cooling

## Contents

- [Overview](#overview)
- [Three ways to fail, and the order to check them](#three-ways-to-fail-and-the-order-to-check-them)
- [Bartz](#bartz)
- [Where the heat actually is](#where-the-heat-actually-is)
- [The coolant capability check](#the-coolant-capability-check)
- [Chamber pressure has a ceiling](#chamber-pressure-has-a-ceiling)
- [Scale does not rescue you](#scale-does-not-rescue-you)
- [The coolant decides more than the channel](#the-coolant-decides-more-than-the-channel)
- [The wall](#the-wall)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [What is not validated](#what-is-not-validated)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Regenerative cooling runs the fuel through a jacket around the chamber before burning it, so the heat that would destroy the wall goes into the propellant instead and is recovered. It is elegant, it is standard, and it has a hard limit that is easy to discover late.

**The limit is not the channel.** It is that the coolant has a finite capacity to absorb heat before it destroys itself, and that capacity is set by three numbers none of which a channel designer controls.

---

## Three ways to fail, and the order to check them

A cooling design has to close on three separate constraints, and passing one says nothing about the other two.

| Constraint | Question | Depends on |
|---|---|---|
| **Coolant capability** | Can the coolant absorb the load at all? | Heat load, flow, specific heat |
| Wall temperature | Does the wall survive? | Flux, conductivity, thickness, film coefficient |
| Pressure drop | Does the drop fit the available head? | Channel geometry, velocity, length |

**Check the first one first.** It needs three numbers, it takes one line, and it decides whether the other two are worth doing:

```
dT = Q / (mdot cp)
```

The channel does not appear in it. If that rise puts the coolant past its coking or decomposition limit, no channel geometry fixes it, and a week spent on channel optimisation was a week wasted. `checkCoolantCapability` runs before anything is sized for exactly this reason.

The order is frequently the other way round in practice, because channel design is the interesting part and capability is arithmetic.

---

## Bartz

The gas-side heat transfer coefficient:

```
h_g = (0.026 / Dt^0.2) (mu^0.2 cp / Pr^0.6) (Pc / c*)^0.8 (Dt / Rc)^0.1 (At / A)^0.9 sigma
```

`sigma` is a property variation correction accounting for the boundary layer being far colder than the free stream. It depends on wall temperature, so **the correlation is implicit in the thing it is used to find** and has to be iterated if the wall is not known.

Three exponents carry the behaviour.

**`Pc^0.8`.** Flux rises nearly linearly with chamber pressure. This is the term that puts a ceiling on how hard an engine can be run on a given coolant.

**`(At/A)^0.9`.** The throat carries the peak by a wide margin, and everything else falls away fast in both directions. At a contraction ratio of 2.5 the barrel is already at less than half the throat flux.

**`Dt^-0.2`.** A larger engine has a slightly lower flux. Only slightly, and this is the term that fails to save you at scale.

**Bartz is a 1957 correlation with real scatter, quoted at plus or minus twenty per cent and worse in the convergent section.** The literature consistently reports that the one-dimensional form **overpredicts** inner wall temperature, because it does not account for boundary layer thickness variation along the wall. A cooling design that closes on a ten per cent margin against Bartz has not closed.

---

## Where the heat actually is

For the [worked example](../codeInterface.py) chamber, 100 kN LOX/RP-1 at 10 MPa:

| Section | Area [cm^2] | Mean flux [MW/m^2] | Load [MW] |
|---|---|---|---|
| Barrel | 1841 | 23.65 | 4.355 |
| Convergent | 170 | 33.29 | 0.567 |
| Divergent | 4230 | 7.58 | 3.205 |
| **Total** | **6241** | **13.02** | **8.127** |

**The divergent section is 68 per cent of the area and 39 per cent of the load.** It runs at a low flux and there is a great deal of it, and the product is not negligible.

That matters because the divergent section is the easy one to leave out. It is downstream, its flux is low, and a chamber cooling analysis that stops at the throat understates the load by nearly forty per cent. The [propulsion hub](../../docs/EngineSizing.md) made the mirror-image error in the other direction by counting only the barrel wall for its area check.

**The convergent section is the opposite trap:** three per cent of the area and seven per cent of the load, at the highest mean flux of the three. It is small, it is hot, and it is where Bartz is least reliable.

---

## The coolant capability check

For the same chamber, with the whole fuel flow through the jacket:

| Quantity | Value |
|---|---|
| Heat load | 8.13 MW |
| Coolant flow | 10.34 kg/s, all of the fuel |
| Bulk temperature rise | 374 K |
| Outlet | 664 K |
| RP-1 coking limit | 575 K |
| Margin | -89 K |
| Flow that would close it | 13.58 kg/s |

**The circuit does not close, and there is no more fuel.** It is all already in the jacket. Closing would need 1.31 times the flow the engine burns.

The useful figure of merit is the load per unit coolant flow, here **786 kJ per kilogram**. That number is what makes a regenerative circuit hard or easy, and it is nearly independent of the things a designer normally reaches for.

---

## Chamber pressure has a ceiling

Holding thrust constant and varying chamber pressure, so the throat shrinks as pressure rises:

| `Pc` [MPa] | Throat [mm] | Peak flux [MW/m^2] | Load [MW] | Coolant rise [K] | Closes |
|---|---|---|---|---|---|
| 3 | 165.4 | 17.6 | 5.02 | 231 | Yes |
| 5 | 128.1 | 27.9 | 6.16 | 284 | Yes |
| 7 | 108.3 | 37.8 | 7.05 | 324 | No |
| 10 | 90.6 | 52.1 | 8.13 | 374 | No |
| 15 | 74.0 | 75.0 | 9.56 | 440 | No |

**There is a chamber pressure ceiling for pure regenerative cooling on a given coolant, and for RP-1 at this scale it is near 6 MPa.**

That is a hard design boundary and it is not obvious from anything upstream. The [hub](../../docs/EngineSizing.md) shows performance saturating with chamber pressure and difficulty rising; this is one of the specific difficulties, and it arrives abruptly rather than gradually.

Note that the load rises far more slowly than the flux does, because the engine is shrinking as the pressure rises. Flux nearly quadruples from 3 to 15 MPa and the load less than doubles.

---

## Scale does not rescue you

The instinctive response to a cooling problem is that a bigger engine will be easier, because heat transfer is a surface effect and propellant flow is a volume effect. **That instinct is wrong here, and the reason is worth understanding.**

At a fixed chamber pressure of 10 MPa:

| Thrust [kN] | Heat load [MW] | Load per unit coolant [kJ/kg] | Coolant rise [K] | Closes |
|---|---|---|---|---|
| 10 | 1.02 | 989 | 471 | No |
| 100 | 8.13 | 786 | 374 | No |
| 1000 | 64.55 | 624 | 297 | No |

**A hundredfold increase in thrust improves the load per unit coolant by only 37 per cent, and it still does not close.**

The reason is that both the wetted area and the propellant flow scale with the square of the throat diameter, so they cancel. The only term that helps is the `Dt^-0.2` in Bartz, which over a factor of ten in diameter is a factor of 1.6 in flux.

Scale helps a little. It does not change the answer.

---

## The coolant decides more than the channel

The same 8.13 MW load into the same 10.34 kg/s, varying only what the coolant is:

| Coolant | `cp` [J/kg K] | Rise [K] | Outlet [K] | Limit [K] | Closes |
|---|---|---|---|---|---|
| LH2 | 14 300 | 55 | 345 | 900 | Yes, easily |
| LCH4 | 3 500 | 225 | 515 | 700 | Yes |
| MMH | 2 900 | 271 | 561 | 480 | No |
| Ethanol | 2 600 | 302 | 592 | 600 | Barely |
| RP-1 | 2 100 | 374 | 664 | 575 | No |

**This table is most of the argument for LOX/methane in a reusable engine, and it is not the argument usually given.**

The usual argument is coking: methane cokes far less than kerosene, so it does not lay carbon down in the passages between flights. That is true and it is secondary. The primary effect is that **methane's specific heat is 1.7 times RP-1's and its limit is 125 K higher**, and the two together turn a circuit that fails by 89 K into one that closes with 185 K to spare.

Hydrogen is in a different category again. At 14 300 J/kg K it absorbs the same load for a 55 K rise, which is why hydrogen engines run chamber pressures that would be impossible on anything else, and why the expander cycle exists at all.

---

## The wall

A series resistance: gas film, wall conduction, coolant film.

```
dT_wall = q t / k
```

At 52.1 MW/m^2 through 1 mm:

| Material | `k` [W/m K] | Wall drop [K] |
|---|---|---|
| GRCop-42 | 320 | 163 |
| NARloy-Z | 320 | 163 |
| Inconel 718 | 25 | 2085 |

**A 2085 K drop is not a wall, it is a hole.** That single comparison is why chamber liners are copper alloys despite their poor strength at temperature, and why an Inconel chamber is film cooled rather than regeneratively cooled.

The coolant side is reported as a **required** coefficient rather than an assumed one, because at these fluxes an assumed value produces nonsense. Holding the reference wall at 800 K with a bulk coolant at 477 K needs a 160 K film drop, which at 52.1 MW/m^2 is **325 kW/m^2 K**. A high velocity supercritical hydrocarbon in a millimetre-scale channel reaches roughly 50 to 200. Anything past that is asking the channel for something it cannot give.

An early version of this library assumed 30 kW/m^2 K and reported a 1736 K film drop, which is arithmetic rather than engineering. Stating the requirement is the honest form.

---

## Design rules of thumb

- **Check coolant capability before designing a channel.** Three numbers, one line, and it decides whether the rest is worth doing.
- **Count the whole gas-side wall.** The divergent section is two thirds of the area and nearly forty per cent of the load.
- **Design against Bartz plus twenty per cent**, and expect the real wall to be cooler than predicted rather than hotter.
- **Treat chamber pressure as bounded by the coolant**, not only by the feed system.
- **Do not expect scale to fix a cooling problem.** Area and flow both scale as the square of diameter.
- **Choose the coolant before the channel.** Specific heat and decomposition limit decide more than any geometry.
- **Use a copper alloy liner at high flux.** An order of magnitude in conductivity is an order of magnitude in wall drop.
- **Report the required coolant coefficient** rather than assuming one.

---

## Failure modes

**Channel design started before capability was checked.** The most expensive way to discover that the circuit cannot close.

**Cooling analysis stopped at the throat.** Understates the load by nearly forty per cent, because the divergent section is most of the area.

**Barrel-only wall area used for a sizing check.** The mirror-image error, and the propulsion hub made it.

**Bartz treated as accurate.** Plus or minus twenty per cent, biased to overpredict, worse in the convergent section.

**A coolant coefficient assumed rather than required.** Produces either a nonsense film drop or a wall temperature that no channel achieves.

**Superalloy liner at high flux.** Two thousand kelvin through a millimetre.

**Coking limit treated as a boiling point.** It is a decomposition threshold, the wall film is hotter than the bulk, and the failure is progressive rather than sudden: carbon lays down, insulates, and the wall behind it runs hotter still.

---

## Worked numbers

The [worked example](../codeInterface.py) chamber, all produced by running the code.

| Quantity | Value |
|---|---|
| Peak throat flux | 52.1 MW/m^2 |
| Area-weighted mean flux | 13.02 MW/m^2 |
| Total heat load | 8.13 MW |
| Wetted area | 6241 cm^2 |
| Divergent share of area | 68 % |
| Divergent share of load | 39 % |
| Coolant bulk rise | 374 K |
| Coolant outlet | 664 K |
| Load per unit coolant flow | 786 kJ/kg |
| Flow needed to close | 13.58 kg/s against 10.34 available |
| Wall drop, 1 mm GRCop-42 | 163 K |
| Required coolant coefficient | 325 kW/m^2 K |

---

## What is not validated

**The integrated heat load.** The 8.13 MW is a Bartz result and has no external anchor. The peak throat flux of 52.1 MW/m^2 does sit inside a measured literature band of 18 to 54 MW/m^2, at 95 per cent of the way up it, which is consistent with the documented over-prediction. **That is a bounding check and not a validation:** the band spans a factor of three across different propellants and scales.

**The coolant limits.** The RP-1 figure of 575 K decides whether the circuit closes, and it is a widely quoted range rather than a sourced value. The real limit is a film temperature depending on residence time and surface chemistry.

Both are registered in [validation/referenceCases.py](../../../validation/referenceCases.py) with what would close them. See [ValidationReferences](ValidationReferences.md).

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8087** | **Liquid rocket engine fluid-cooled combustion chambers.** The design monograph |
| NASA SP-8124 | Self-cooled combustion chambers, for the ablative and radiation alternatives |
| Bartz 1957 | The correlation itself |
| NASA-STD-5012 | Strength and life assessment for rocket engines, which is where the thermal cycle life lives |
| ASTM D6375 | Thermal oxidation stability of hydrocarbon fuels, relevant to coking |

---

## Tool interface

```python
from RegenerativeCooling import RegenerativeCooling

cooling = RegenerativeCooling()
cooling.setInputs({'combination':      'LOX/RP-1',
                   'chamberPressure':  10.0e6,
                   'throatDiameter':   0.0906,
                   'contractionRatio': 2.5,
                   'areaRatio':        20.35,
                   'barrelLength':     0.4091,
                   'convergentLength': 0.0456,
                   'divergentLength':  0.475,
                   'coolantFlow':      10.34})

capability = cooling.checkCoolantCapability()
print(capability['feasible'], capability['temperatureRise'])

heat = cooling.calculateHeatLoad()
print(heat['totalLoad'], heat['peakFlux'])

wall = cooling.calculateWallTemperature()
print(wall['wallDrop'], wall['requiredCoefficient'])
```

Run `checkCoolantCapability` first. It is the cheapest call in the class and the only one that can tell you not to make the others.

---

## References

- Bartz, *A simple equation for rapid estimation of rocket nozzle convective heat transfer coefficients*, 1957
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*, chapter 4
- Pizzarelli et al., *Overview and analysis of the experimentally measured throat heat transfer in liquid rocket engine thrust chambers*, Acta Astronautica 184 (2021)
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 8
