[Home](../README.md) > Cryogenic Insulation

# Cryogenic Insulation

## Contents

- [Overview](#overview)
- [What this document adds](#what-this-document-adds)
- [MLI is a radiation problem wearing a conduction costume](#mli-is-a-radiation-problem-wearing-a-conduction-costume)
- [Penetrations, and why the parallel path wins](#penetrations-and-why-the-parallel-path-wins)
- [The ground to flight transition](#the-ground-to-flight-transition)
- [Properties at cryogenic temperature](#properties-at-cryogenic-temperature)
- [Insulation in a nodal network](#insulation-in-a-nodal-network)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

**The system view of cryogenic insulation already exists in [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/Insulation.md).** That document owns the material table, the thickness sizing, boiloff, condensation and liquid air, the critical radius result, and the natural convection correlations for a cold surface in air. The `Insulation` class there is the tool for sizing.

This document does not repeat any of it. It covers the four things a thermal analyst needs that a sizing calculation does not give: why multilayer insulation behaves the way it does, why penetrations dominate a real installation, what happens across the ground to flight transition, and how an insulated surface enters a nodal network.

---

## What this document adds

The sizing question is "how thick". The analysis questions are different and they are the ones that produce surprises.

A tank sized for a 2 per cent per day boiloff and built exactly to drawing routinely comes in worse, and the reason is never the insulation material. It is the supports, the penetrations, the seams, and the fact that the installed performance of MLI is a workmanship property rather than a material property.

---

## MLI is a radiation problem wearing a conduction costume

Multilayer insulation is quoted as an effective conductivity, 5e-05 W/m K for a 20 layer blanket, because that is the convenient way to put it in a resistance chain. The number is real and the mechanism it implies is not.

MLI does not conduct badly. It stops radiation. Each layer is a low emissivity surface, and radiation between two low emissivity surfaces carries the `(1/eps_1 + 1/eps_2 - 1)` denominator from [RadiationHeatTransfer](RadiationHeatTransfer.md). Stacking `N` layers divides the radiative exchange by roughly `N + 1`, because each gap is an independent exchange in series.

Three consequences follow, and none of them are visible in an effective conductivity.

**Compression destroys it.** Layers touching each other conduct directly, and solid conduction bypasses the entire radiative resistance. A blanket compressed under a strap or a bolt is locally not insulation. This is why MLI is installed loose and why layer density is specified.

**Vacuum is not optional.** Residual gas conducts between the layers, and gas conduction in the free molecular regime is proportional to pressure. Above roughly 1e-3 torr the performance degrades; above roughly 1 torr it is gone entirely and the blanket is worse than foam because it has no solid structure to resist convection.

**Layer count has diminishing returns.** Sixty layers give 2e-05 W/m K against 5e-05 for twenty, a factor of 2.5 for three times the layers. Above about forty layers the layer to layer solid conduction starts to dominate and adding more stops helping.

**The practical number is two to five times worse than the quoted one.** A real blanket has seams, edges, penetrations and supports. An installation that achieves twice the quoted conductivity is good. Designing to the quoted value and discovering the factor at test is a common and expensive sequence.

---

## Penetrations, and why the parallel path wins

Insulation is a high resistance in parallel with everything that goes through it, and parallel resistances are dominated by the smallest.

Consider a tank with 12 square metres of 20 layer blanket, 25 mm thick, at the quoted 5e-05 W/m K. That is `L / (k A)` = 0.025 / (5e-05 x 12) = 41.7 K/W for the whole tank.

Now add the supports. A 10 mm diameter strut, 100 mm long, in 316L at 16.2 W/m K, is 0.1 / (16.2 x 7.85e-05) = 79 K/W. One strut is comparable to the entire blanket. **Six of them, which is an ordinary number, come to 13.2 K/W in parallel and carry 3.2 times the heat the blanket does.**

The blanket is no longer the insulation system. The struts are.

This arithmetic is why cryogenic supports are made of G10 or titanium rather than steel, why they are made long and thin, and why they are heat stationed to an intermediate temperature where possible. It is also why a boiloff prediction based on blanket area alone is not a prediction.

The list of parallel paths on a real tank is longer than it looks: fill and drain lines, vent lines, instrumentation leads, level sensors, structural supports, and every seam in the blanket itself. **Counting them is more valuable than refining the blanket conductivity.**

---

## The ground to flight transition

A launch vehicle's insulation has to work in two completely different environments, and the transition between them is fast.

**On the pad** the outer surface is in air at ambient. The mechanisms are natural convection and radiation on the outside, conduction through the insulation, and the cold wall inside. If the outer surface falls below the dewpoint it condenses water; below 90 K it condenses liquid air, which is an oxygen enriched liquid running down the outside of the vehicle. [fluidSystems](../../fluidSystems/fluidSystemsLibrary/docs/Insulation.md) owns that check.

**In flight** the external convection disappears within the first minute or two, the external radiation environment changes completely, and aerodynamic heating starts adding to the outer surface rather than removing from it. **The sign of the external heat flux reverses.**

Two things follow that a steady state calculation cannot show.

The insulation that was sized to keep heat out on the pad is now also keeping aerodynamic heat out, which is usually helpful. But the thermal mass that was being cooled by ambient air is now not, and any component that relied on convective cooling on the pad has lost it. **Ground cooling that vanishes at liftoff is a classic soakback initiator**, and it is the same failure pattern as [the worked example](../codeInterface.py): the analysis is run for the pad, and for ascent, and neither run covers the interval where the cooling has stopped and the heating has not.

---

## Properties at cryogenic temperature

Every material property in this domain is temperature dependent, and at cryogenic temperatures the dependence is strong enough to change answers.

**Specific heat falls steeply.** Below roughly 100 K, the Debye model gives `c ~ T^3` for many solids. Aluminium at 20 K has a specific heat around 5 per cent of its room temperature value. **A cryogenic component has far less thermal mass than its mass suggests**, so it responds faster and its transient is shorter than a room temperature calculation predicts.

**Conductivity of pure metals rises then falls**, with a peak that can be several times the room temperature value. Alloys are much flatter, because impurity scattering dominates. This is why high purity copper and aluminium are used for cryogenic thermal straps and why 6061 is not a good substitute for 1100.

**Insulation conductivity falls with temperature**, so a blanket spanning 20 K to 300 K does not have a single conductivity. Using the mean temperature value is the standard approximation and it is typically good to 10 to 20 per cent.

The materials domain owns the property data. See [aerospaceMaterials](../../aerospaceMaterials/docs/CryogenicMaterials.md).

---

## Insulation in a nodal network

An insulated wall is a conduction resistance in series with the surface resistances on both sides, and the useful discipline is to write all three down before deciding which matters.

For a well insulated cryogenic tank the insulation dominates completely and the surface terms can be neglected. For a thinly insulated line in a high velocity airstream, they cannot. The test is the resistance fraction, which is what `resistanceSensitivity()` reports.

**The failure to avoid is modelling the blanket carefully and the penetrations not at all**, because the penetrations are in parallel and the parallel path wins.

---

## Design rules of thumb

- **Count the penetrations before refining the blanket.** One steel strut can exceed the whole blanket.
- **Design MLI to two to five times its quoted conductivity.** Installed performance is a workmanship property.
- **Never compress MLI.** A strap across a blanket is a short circuit.
- **Stop adding layers above about forty.** Solid conduction takes over.
- **Use mean temperature properties across a large gradient**, and accept 10 to 20 per cent.
- **Check the pad case and the flight case and the transition between them.** Convective cooling that disappears at liftoff is a soakback initiator.
- **Remember that cryogenic thermal mass is small.** Specific heat falls as `T^3` in the Debye regime.

---

## Failure modes

**Quoted MLI conductivity used as a design value.** Optimistic by a factor of two to five.

**Penetrations omitted.** The dominant heat path left out of the model entirely.

**MLI compressed under a fastener or strap.** Locally zero insulation, and it does not show on a drawing.

**Vacuum lost.** Above about 1 torr an MLI blanket is worse than foam.

**Room temperature specific heat used for a cryogenic transient.** Overstates thermal mass by more than an order of magnitude at 20 K, so the predicted transient is far too slow.

**The transition interval not analysed.** Pad and flight both closed, the interval between them never run.

---

## Worked numbers

| Case | Value |
|---|---|
| MLI, 20 layer, quoted effective conductivity | 5e-05 W/m K |
| MLI, 60 layer, quoted effective conductivity | 2e-05 W/m K |
| Realistic installed penalty | 2x to 5x |
| Vacuum threshold for good performance | 1e-3 torr |
| Vacuum threshold for lost performance | 1 torr |
| Liquid air condensation threshold | 90 K |
| Blanket, 20 layer, 25 mm, 12 m^2 | 41.7 K/W |
| 316L strut, 10 mm diameter, 100 mm long | 79 K/W |
| Six such struts in parallel | 13.2 K/W |
| 6061 aluminium, same strut geometry | 7.6 K/W |
| G10 at 0.6 W/m K, same strut geometry | 2120 K/W |

**Six steel struts carry 3.2 times the heat of the blanket they pass through.** The aluminium strut is ten times worse again, which is why cryogenic supports are not made of aluminium either. G10 is 27 times better than steel in the same geometry, and that is the reason it is the standard choice.

---

## Standards

| Standard | What it gives you |
|---|---|
| ASTM C740 | Evacuated reflective insulation in cryogenic service |
| ASTM C1774 | Thermal performance testing of cryogenic insulation systems |
| ASTM C177 | Guarded hot plate conductivity |
| ASTM C518 | Heat flow meter conductivity |
| NASA-STD-6001 | Flammability and offgassing, which constrains blanket materials |
| CGA H-3 | Cryogenic hydrogen storage |

---

## Tool interface

Sizing is done with the [fluidSystems Insulation class](../../fluidSystems/fluidSystemsLibrary/docs/Insulation.md). This domain takes the resulting resistance into a network.

```python
from thermalUtils import conductionResistance
from ThermalNetwork import ThermalNetwork

blanket = conductionResistance(0.025, 5.0e-05, 12.0)
strut   = conductionResistance(0.100, 16.2, 7.85e-05)

print(f'blanket {blanket:.1f} K/W, one strut {strut:.1f} K/W')

network = ThermalNetwork()
network.setInputs({'timeStep': 10.0, 'endTime': 20000.0})
network.addNodeFromMass('tank wall', mass = 180.0, specificHeat = 900.0, temperature = 90.0)
network.addNode('ambient', temperature = 293.15, boundary = True)
network.addResistance('tank wall', 'ambient', blanket, note = 'blanket')
network.addResistance('tank wall', 'ambient', strut,   note = 'one support strut')
```

---

## References

- Barron, *Cryogenic Heat Transfer*
- Gilmore, *Spacecraft Thermal Control Handbook*, volume I, chapter 5
- NASA-HDBK-2001, multilayer insulation
- Fesmire, *Standardization in cryogenic insulation systems testing and performance data*
- Timmerhaus and Flynn, *Cryogenic Process Engineering*
