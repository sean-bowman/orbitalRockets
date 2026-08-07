[Home](../../README.md) > Cryogenic Systems

# Cryogenic Systems

## Contents

- [Overview](#overview)
- [Cryogen properties](#cryogen-properties)
- [Chilldown](#chilldown)
- [Two-phase flow](#two-phase-flow)
- [Geysering](#geysering)
- [Thermal contraction](#thermal-contraction)
- [Cavitation and NPSH](#cavitation-and-npsh)
- [Materials at cryogenic temperature](#materials-at-cryogenic-temperature)
- [Stratification and self-pressurization](#stratification-and-self-pressurization)
- [Hazards](#hazards)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A cryogenic fluid system is an ordinary fluid system with four additional problems, and all four come from the same source: the fluid is at its boiling point, so anything that adds heat produces vapor.

1. **Chilldown.** The hardware starts warm. Getting it cold consumes propellant, takes time, and produces the most violent transients the system will ever see.
2. **Two-phase flow.** Once the system is cold it is still boiling somewhere. Two-phase flow has different pressure drop, different heat transfer and different dynamics from single phase, and it can choke at velocities that would be unremarkable in a liquid.
3. **Thermal contraction.** Everything shrinks, by an amount that is small as a percentage and large as a displacement, and things shrink by different amounts.
4. **Heat leak.** Every joule that reaches the propellant becomes vapor. That is boil-off, tank pressure rise, and in a feed line it is a bubble at the pump inlet.

---

## Cryogen properties

At one atmosphere:

| Fluid | T_boil [K] | rho_liquid [kg/m^3] | h_fg [kJ/kg] | h_fg x rho [MJ/m^3] | rho_vapor/rho_liquid |
|---|---|---|---|---|---|
| **LH2** | 20.3 | 71 | 446 | **31.6** | 1/53 |
| LHe | 4.2 | 125 | 21 | 2.6 | 1/7.4 |
| **LN2** | 77.4 | 807 | 199 | 161 | 1/175 |
| **LOX** | 90.2 | 1141 | 213 | 243 | 1/256 |
| LAr | 87.3 | 1394 | 161 | 224 | 1/243 |
| **LCH4** | 111.7 | 423 | 511 | 216 | 1/236 |

**Read the volumetric latent heat column.** Hydrogen has by far the highest latent heat per unit mass, which sounds favorable until you note its density. Per unit **volume** it is 31.6 MJ/m^3 against 243 for LOX, so for the same heat leak per unit tank volume a hydrogen tank boils off roughly **eight times as fast**. That, plus the much larger tank volume per unit mass, is why hydrogen insulation is such a disproportionate part of a hydrolox vehicle.

**The density ratio column** matters for two-phase flow: a small mass fraction of vapor occupies an enormous volume fraction. One percent quality in LOX is 72 percent void fraction.

---

## Chilldown

The hardware starts at ambient and has to reach cryogenic temperature before liquid can flow through it. That transition is the most demanding thing the system does.

**Three heat transfer regimes**, in the order they occur:

1. **Film boiling.** The wall is far above the liquid saturation temperature, a stable vapor film separates the liquid from the wall, and the heat transfer coefficient is **very low** (tens of W/m^2-K). Most of the chilldown time is spent here.
2. **Transition boiling.** The film becomes unstable and intermittently collapses. Heat transfer rises steeply and erratically.
3. **Nucleate boiling.** Liquid wets the wall and boils at discrete sites. Heat transfer is **very high** (thousands to tens of thousands of W/m^2-K). The wall temperature drops rapidly to saturation.

The **Leidenfrost point** is the wall superheat at which the film collapses, and it is where the chilldown suddenly accelerates. Everything before it is slow and everything after is fast.

**Chilldown mass** is what the process costs:

```
m_chilldown = (m_hardware * cp_hardware * dT) / h_fg
```

For a stainless line, `cp` falls dramatically at cryogenic temperature (from 500 J/kg-K at 293 K to about 200 J/kg-K at 77 K), so an integral is more honest than a mean value. A rough result: chilling 1 kg of stainless from 293 K to 90 K with LOX consumes roughly 0.4 kg of LOX. On a vehicle with a large plumbing mass, chilldown propellant is a real line item.

**Chilldown transients** are covered in [WaterHammer.md](WaterHammer.md). The line contains alternating slugs of liquid and vapor, each slug is accelerated by the expanding vapor behind it, and each arrival at a bend or a closed valve is a water hammer event. It happens thousands of times over a chilldown, so it is a fatigue exposure as well as a peak-load one.

**Chilldown practice:**

- **Slowly.** A restricted flow (a chilldown orifice, or the main valve cracked open) limits the slug velocities.
- **From the bottom up** where the geometry allows, so vapor escapes upward against the incoming liquid rather than being trapped.
- **With a vent open** at the high point, so the generated vapor has somewhere to go.
- **Instrumented.** Wall thermocouples along the line tell you when it is actually cold, which is usually later than expected.

---

## Two-phase flow

**Pressure drop** in two-phase flow is much higher than the equivalent single-phase liquid flow, because the vapor occupies most of the volume and the mixture velocity is correspondingly higher.

The **Lockhart-Martinelli** correlation is the standard treatment: compute the pressure drop for each phase flowing alone, form the Martinelli parameter, and apply a two-phase multiplier:

```
X^2  = (dP/dz)_liquid / (dP/dz)_vapor
phi_l^2 = 1 + C/X + 1/X^2                (C = 20 for turbulent-turbulent)
(dP/dz)_two-phase = phi_l^2 * (dP/dz)_liquid
```

Two-phase multipliers of 5 to 50 are ordinary. **A line sized on single-phase liquid pressure drop will not pass its flow during chilldown**, which is the reason chilldown is done at reduced flow.

**Flow regimes** in a horizontal line, in order of increasing vapor fraction: bubbly, plug, slug, annular, mist. **Slug flow is the dangerous one**, because a liquid slug moving at the vapor velocity carries enormous momentum and delivers it to the first bend it reaches.

**Choking.** Two-phase flow chokes at velocities far below the single-phase sound speed, because the mixture sound speed is much lower than either phase alone. A homogeneous mixture at 50 percent void fraction can have a sound speed below 20 m/s. That is why a two-phase line chokes at flow rates that would be unremarkable in liquid.

**The `Line` class in this library models single-phase flow only.** For a genuinely two-phase problem it will under-predict the pressure drop, and it says so. Use it for the cold, single-phase steady state and treat chilldown separately.

---

## Geysering

A vertical line filled with cryogenic liquid and open at the top can undergo a violent, periodic expulsion of its contents. The mechanism:

1. Heat leak into the vertical run generates vapor at the bottom
2. The vapor bubble rises, and as it rises the static head above it falls
3. Lower pressure means lower saturation temperature, so the liquid around the bubble flashes
4. That accelerates the bubble, which lowers the head further, which flashes more liquid
5. The entire column is expelled upward in seconds
6. Cold liquid rushes back down and slams into the closed bottom of the line

**Step 6 is the damage.** The refill impact is a water hammer event with the full column velocity and it has broken hardware.

Geysering is a known hazard on **long vertical cryogenic downcomers**, which is exactly the geometry of a launch vehicle LOX feed line running from a tank at the top of the vehicle to an engine at the bottom. It was identified on early Atlas and Titan vehicles and it is designed against explicitly.

**Mitigations:**

- **Recirculation.** Continuously circulate liquid through the line so the heat leak is carried away rather than accumulating. The standard solution on a launch vehicle.
- **Helium bubbling.** Inject helium at the bottom of the line to promote circulation and prevent the formation of a single large bubble.
- **Insulation.** Reduce the heat leak that drives it.
- **Avoid the geometry.** Short vertical runs, or a sloped run that lets vapor escape continuously.

---

## Thermal contraction

Integrated linear contraction from 293 K:

| Material | to 111 K (LCH4) | to 90 K (LOX) | to 77 K (LN2) | to 20 K (LH2) |
|---|---|---|---|---|
| 304/316 stainless | 0.26 % | 0.28 % | 0.30 % | 0.31 % |
| **6061 aluminum** | **0.35 %** | **0.38 %** | **0.41 %** | **0.42 %** |
| Copper | 0.28 % | 0.30 % | 0.32 % | 0.33 % |
| **Ti-6Al-4V** | **0.15 %** | **0.16 %** | **0.17 %** | **0.17 %** |
| Invar 36 | 0.04 % | 0.04 % | 0.04 % | 0.04 % |
| G-10 fiberglass (normal) | 0.20 % | 0.21 % | 0.24 % | 0.25 % |
| **PTFE** | **1.7 %** | **1.8 %** | **1.9 %** | **2.1 %** |
| Most elastomers | 1 to 2 % | (glassy below Tg) | | |

**A 3 m stainless LN2 line shrinks 9 mm.** A 3 m aluminum LH2 line shrinks 13 mm. If both ends are rigidly anchored, that displacement goes into the line as compressive stress and buckling, or into the anchors as load.

**Differential contraction is the subtler problem.** Aluminum against stainless is a 0.11 percent mismatch to 77 K, which on a 100 mm flange is 0.11 mm. That is a bolt preload change, a seal compression change, and a clearance change all at once. PTFE against stainless is a 1.6 percent mismatch, which is why plain PTFE seals fail cold.

**Accommodation, in order of preference:**

1. **Routing flexibility.** An offset or an expansion loop that absorbs growth by bending. Free and reliable.
2. **Bellows expansion joint.** Compact and effective, but it is a pressure boundary with a fatigue life and it must be restrained against pressure thrust.
3. **Flex hose.** Absorbs motion in any direction, at a large pressure drop cost.
4. **Sliding supports.** Axial freedom with lateral restraint.

**Design the gland for the cold condition, not the ambient one.** See [Seals.md](Seals.md).

---

## Cavitation and NPSH

A cryogen sits at its boiling point, so any pressure drop takes it below saturation and it flashes.

**Net positive suction head** is the margin above vapor pressure at a pump inlet:

```
NPSH_available = (P_inlet - P_vapor) / (rho * g) + V^2/(2g)
```

and it must exceed the pump's required NPSH with margin.

**Two properties of cryogens make this easier than it looks**, and it is worth knowing why:

- **Thermodynamic suppression head.** When a cryogen cavitates, the vapor that forms takes latent heat from the surrounding liquid, which cools it, which lowers the local vapor pressure, which suppresses further cavitation. The effect is strong in cryogens (because `h_fg` is small relative to the sensible heat) and negligible in water. A cryogenic pump can operate at an NPSH that would destroy a water pump.
- **Low vapor density.** A small mass of vapor makes a large volume, so the cavity is large but the collapse energy is modest.

**Suction line design** is still the critical part: keep the velocity low (3 m/s), keep the line short, minimize fittings, and avoid any local high point where vapor can collect.

---

## Materials at cryogenic temperature

| Material | Behaviour at cryogenic temperature |
|---|---|
| **304L, 316L austenitic stainless** | Fully ductile to 4 K. Yield strength roughly 2.5x the room temperature value. The default |
| **321, 347 stabilized** | Same, preferred where welds see elevated temperature in another part of the cycle |
| **6061-T6, 2219 aluminum** | Fully ductile, strength rises. Standard tank material. Low density, high conductivity (which is bad for heat leak) |
| **Ti-6Al-4V ELI** | Fully ductile in the extra-low-interstitial grade. Excellent strength to weight. **Never in LOX or GOX** |
| Inconel 718, 625 | Fully ductile, high strength |
| Monel 400 | Fully ductile |
| **Carbon steel, ferritic and martensitic steels** | **BRITTLE.** Ductile-to-brittle transition well above cryogenic temperature. Never use them |
| **9 % nickel steel** | The exception: usable to 77 K, standard for large LNG storage tanks |
| G-10 fiberglass | Low conductivity, good strength. The standard support strut material |
| PTFE, PCTFE | Usable to 4 K but contract heavily and cold flow |
| Elastomers | Glassy below Tg. Not seals at cryogenic temperature |

**The body-centred cubic problem.** Ferritic and martensitic steels have a ductile-to-brittle transition temperature because their BCC lattice loses its slip systems as temperature falls. Austenitic stainless and aluminum are face-centred cubic and have no transition; they stay ductile to absolute zero. **This is the single most important materials fact in cryogenic design** and it is why the alloy list above is so short.

---

## Stratification and self-pressurization

A cryogenic tank sitting with heat leaking in does not warm uniformly. The warm liquid near the wall rises, forms a warm layer at the top, and the ullage sees the temperature of that layer rather than the bulk temperature.

**Consequences:**

- The tank self-pressurizes faster than a uniform-temperature calculation predicts, because the saturation pressure is set by the warm surface layer
- The propellant delivered late in a burn is warmer than the bulk, which changes its density and its cavitation margin
- Venting removes vapor at the surface temperature, which is the least useful place to remove it from

**Mitigations:** mixing (a small pump circulating the bulk), thermodynamic vent systems (which expand a small liquid bleed through a J-T valve and use the resulting cold flow to cool the bulk before venting it), and simply accepting a higher tank pressure.

**A locked-up cryogenic tank does not boil off; it self-pressurizes.** The heat leak goes into raising the ullage pressure rather than vaporizing liquid at constant pressure, and the pressure rise is much faster than the boil-off calculation suggests. **Every cryogenic tank needs relief protection**, and the relief has to be sized for the credible heat input including a fire case.

---

## Hazards

**Cold burns.** Contact with cryogenic liquid or with uninsulated cold metal causes tissue damage indistinguishable from a thermal burn. Loose gloves that can be shed quickly, face shield, closed shoes, no cuffs or pockets that can trap spilled liquid.

**Asphyxiation.** One litre of LN2 becomes 700 litres of gas. A modest spill in a confined space displaces the oxygen and there is no warning: nitrogen is odourless and the body does not sense oxygen deficiency. **Oxygen monitors are mandatory** in any enclosed space where cryogens are handled, and 19.5 percent is the action level.

**Oxygen enrichment.** Air condensing on any surface below 90 K is oxygen enriched. See [Insulation.md](Insulation.md). Liquid air dripping onto asphalt or any organic material creates an impact-sensitive explosive.

**Trapped liquid.** Cryogenic liquid trapped between two closed valves warms and expands. The liquid-to-gas expansion ratio is several hundred to one and the resulting pressure is limited only by the burst pressure of the containment. **Every isolatable cryogenic volume must have a relief path.** This is the most common cryogenic system design error and it is a direct route to a burst line.

**Embrittlement of the wrong material.** A carbon steel fitting in a cryogenic line fails without warning and without deformation.

**Ice.** Formed on any cold surface, it adds mass, breaks off in sheets, and blocks vents and relief paths. A frozen vent line converts a vented tank into a locked-up one.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Every isolatable volume gets a relief path | Absolute | Trapped cryogen expands several hundred to one |
| Chilldown velocity | <= 3 m/s two-phase | Slug velocities exceed the mean |
| Chilldown direction | Bottom up where possible | Vapor escapes upward |
| Two-phase pressure drop multiplier | 5 to 50x single phase | A line sized on liquid will not pass chilldown flow |
| Suction line velocity | <= 3 m/s | NPSH protection |
| Vertical downcomer | Recirculate or bubble helium | Geysering |
| Contraction, stainless to 77 K | 0.30 % | 9 mm on a 3 m line |
| Materials | FCC only: austenitic stainless, aluminum, nickel alloys, Ti (not in LOX) | BCC steels go brittle |
| Titanium in oxygen | **Never** | Impact sensitive, it burns |
| Insulation surface temperature | > 90 K | Liquid air condensation |
| Oxygen monitors | Mandatory in enclosed spaces | Asphyxiation with no warning |
| Design seals for the cold condition | Always | Differential contraction removes squeeze |
| Instrument wall temperature, not fluid temperature | For chilldown | The wall is what you are waiting for |

---

## Failure modes

**Trapped liquid bursting a line.** The most common cryogenic design error.

**Chilldown water hammer.** Repeated slug impacts damaging bends, instrumentation and supports.

**Geysering.** Column expulsion and refill impact in a vertical downcomer.

**Thermal contraction overload.** A rigidly anchored line buckles or tears out its anchors.

**Cold leak from an elastomer seal.** The seal passed every ambient leak check and leaks the moment it goes cold.

**Vacuum jacket failure.** Boil-off rises by up to two orders of magnitude with no external sign. See [Insulation.md](Insulation.md).

**Brittle fracture of the wrong alloy.** No deformation, no warning.

**Frozen vent or relief line.** Moisture in the vent path freezes and blocks it, converting a vented tank into a locked-up one.

**Pump cavitation from a warm suction line.** Insufficient chilldown, or heat leak into an uninsulated suction run.

**Ice shedding.** On a launch vehicle, a debris hazard to whatever is downstream.

**Stratification-driven overpressure.** The tank pressure rises faster than the uniform-temperature calculation predicted.

---

## Operations

**Chill down slowly and instrument it.** Wall thermocouples along the line. The line is cold when the wall is cold, not when liquid appears at the outlet.

**Verify every relief path before loading.** Including the ones protecting isolatable segments.

**Purge with dry gas before chilling.** Any moisture in the line becomes ice, and ice blocks small passages and relief paths.

**Monitor oxygen concentration** in any enclosed space.

**Never approach an unvented cryogenic system.** A locked-up tank is a pressure vessel with an internal energy source.

**Warm up before opening.** A joint broken cold will freeze moisture into the sealing surfaces, and the hardware is at a temperature that causes injury on contact.

**Check for ice on vents and reliefs** before every operation.

**Do not stand under a cryogenic line.** Liquid air drips, and so does the cryogen if the line fails.

---

## Standards

| Standard | Scope |
|---|---|
| CGA P-12 | Safe handling of cryogenic liquids |
| CGA H-3 | Cryogenic hydrogen storage |
| **NASA-STD-8719.17** | Ground-based pressure vessels and pressurized systems |
| NASA/SP-2016-6105 | Systems engineering handbook (referenced for verification practice) |
| ASME B31.3 Chapter VIII | Piping for category M fluid service |
| ASME BPVC Section VIII Div. 1 | Pressure vessels, including low temperature requirements |
| ISO 21010 | Cryogenic vessels, gas/materials compatibility |
| ISO 21014 | Cryogenic vessels, cryogenic insulation performance |
| ASTM E1595 | Evaluating the ignition sensitivity of materials to gaseous fluid impact |
| **NASA-STD-6001** | Flammability, offgassing and compatibility, includes oxygen system guidance |
| ASTM G88 | Designing systems for oxygen service |
| ASTM G93 | Cleaning methods and cleanliness levels for oxygen service |
| NFPA 55 | Compressed gases and cryogenic fluids code |

---

## Tool interface

Cryogenic problems use the same classes as everything else, with the cryogenic-specific checks built into them:

```python
from Line import Line
from Insulation import Insulation
from WaterHammer import WaterHammer
from Seal import Seal

# LOX line: the velocity limit is an ignition limit, not a guideline
line = Line()
line.setInputs({'fluid': 'Oxygen', 'massFlow': 5.0, 'length': 8.0,
                'inletPressure': 4.0e5, 'inletTemperature': 90.2,
                'service': 'lox', 'material': '316L'})   # 7.6 m/s limit applied
line.sizeDiameter()

# Insulation: the liquid air check is automatic
insulation = Insulation()
insulation.setInputs({'material': 'polyurethane foam', 'innerDiameter': 0.0508,
                      'length': 8.0, 'innerTemperature': 90.2,
                      'ambientTemperature': 293.15, 'fluid': 'Oxygen'})
insulation.sizeThickness(targetSurfaceTemperature = 275.0)
insulation.calculateBoilOff(tankVolume = 1.0)
print(insulation.condensationRisk)     # flags 'LIQUID AIR' below 90 K

# Seals: the glass transition check raises rather than warns
seal = Seal()
seal.setInputs({'material': 'pctfe', 'crossSectionDiameter': 0.00178,
                'minimumTemperature': 90.0, 'fluid': 'LOX',
                'designPressure': 4.0e5})
seal.checkCompatibility()    # FKM at 90 K would raise CompatibilityError
```

`utils.materialProperties(material, temperature)` applies the cryogenic strength gain automatically: 316L at 77 K returns 408 MPa yield against 170 MPa at 293 K.

---

## References

1. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
2. Barron, R. F., *Cryogenic Heat Transfer*, 2nd ed., CRC Press, 2016.
3. Timmerhaus, K. D. and Flynn, T. M., *Cryogenic Process Engineering*, Plenum Press, 1989.
4. Lockhart, R. W. and Martinelli, R. C., "Proposed Correlation of Data for Isothermal Two-Phase, Two-Component Flow in Pipes", *Chemical Engineering Progress*, Vol. 45, 1949.
5. Murphy, D. W., "Geysering in Vertical Tubes", *Advances in Cryogenic Engineering*, Vol. 10, 1965.
6. NIST Cryogenic Material Properties Database, cryogenics.nist.gov.
7. Brennen, C. E., *Cavitation and Bubble Dynamics*, Oxford University Press, 1995.
8. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
