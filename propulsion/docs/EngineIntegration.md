[Home](../README.md) > Engine Integration

# Engine Integration

## Contents

- [Overview](#overview)
- [The interfaces, and who owns each side](#the-interfaces-and-who-owns-each-side)
- [The fuel is also the coolant](#the-fuel-is-also-the-coolant)
- [The pressure budget](#the-pressure-budget)
- [Gimbal](#gimbal)
- [Heat soak](#heat-soak)
- [The engine as an environment source](#the-engine-as-an-environment-source)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An engine is never a component in isolation, and most of the difficulty in integrating one comes from the fact that its interfaces are owned by different disciplines who each see one side.

This document is about those handovers, using the [worked example](../codeInterface.py) engine as the case: 100 kN sea level, LOX/RP-1, 10 MPa chamber, area ratio 20.35.

---

## The interfaces, and who owns each side

| Interface | This domain provides | The other side provides |
|---|---|---|
| [fluidSystems](../../fluidSystems/README.md) | Flow rates, inlet pressure requirement, inlet conditions | Delivered pressure, NPSH, transients, water hammer |
| [thermalManagement](../../thermalManagement/README.md) | Wall heat load, gas-side area, wall limit | Coolant capability, wall temperature, soakback |
| [aerospaceStructures](../../aerospaceStructures/README.md) | Thrust, gimbal loads, engine mass, exit envelope | Thrust structure stiffness, mount compliance, modes |
| [aerospaceMaterials](../../aerospaceMaterials/README.md) | Wall temperature and flux, cycle count | Liner alloy, allowables at temperature, life |
| [environmentsAndLoads](../../environmentsAndLoads/README.md) | Vibration and acoustic source levels | The environment specification everything else qualifies to |

**The failures live in the handovers rather than on either side**, which is the same pattern the [thermalManagement worked example](../../thermalManagement/codeInterface.py) demonstrates for soakback.

---

## The fuel is also the coolant

The single most consequential coupling on a regeneratively cooled engine, and it is easy to write two correct analyses either side of it that do not close.

The worked example engine burns 10.34 kg/s of RP-1. That same 10.34 kg/s is the entire coolant supply for a 2.72 MW wall heat load. **There is no independent coolant budget.**

Three consequences follow.

**The cooling circuit sets a floor on fuel flow**, which is a floor on mixture ratio from below. An engine cannot be run leaner than its cooling allows, regardless of what the performance optimum says.

**Throttling reduces coolant flow at the same time as heat load**, and the two do not fall together. Coolant flow falls linearly with chamber pressure; heat flux falls more slowly, roughly with `Pc^0.8`. **Wall temperature can rise on throttle-down**, which is counterintuitive and is why the cooling case is checked at the throttle floor rather than at full thrust.

**The coolant pressure drop is part of the feed pressure**, so the cooling circuit and the pump discharge pressure are the same conversation. A cooling channel redesign that improves wall temperature by raising velocity has just raised the pump discharge requirement, and the pump is owned by someone else.

---

## The pressure budget

The engine inlet pressure requirement is the chamber pressure plus everything consumed between the inlet and the chamber.

| Consumer | Typical share of `Pc` |
|---|---|
| Injector pressure drop | 15 to 20 % |
| Cooling circuit | 10 to 25 % |
| Valves and lines | 3 to 8 % |
| Total margin over chamber | 30 to 50 % |

The worked example uses 25 per cent, which gives 12.5 MPa at the inlet for a 10 MPa chamber. **That is an assumption in this domain and a hard requirement in [fluidSystems](../../fluidSystems/README.md)**, and the two have to be the same number.

It is worth being explicit about the direction of the dependency. The injector drop is chosen for stability, the cooling drop falls out of the channel design, and the sum lands on the pump as a discharge pressure requirement. **Nobody chooses the inlet pressure; it is an outcome.** A programme that specifies it early and holds it will find the injector or the cooling giving way instead.

---

## Gimbal

Thrust vector control by gimballing the whole engine is the usual arrangement, and it makes the engine a moving part with plumbing attached.

**Flexible lines are the hard part.** A gimballed engine needs its propellant feed to accommodate the motion, and a flex line or bellows at 12.5 MPa carrying cryogenic oxygen is a demanding component. The alternative is to place the gimbal downstream of the pumps and gimbal only the chamber, which trades plumbing difficulty for a different set of interfaces.

**The gimbal introduces a side load into the thrust structure** proportional to thrust and the sine of the deflection. At 100 kN and 5 degrees that is 8.7 kN lateral, which the mount and the thrust structure both have to carry.

**Actuator authority is set by the worst case hinge moment**, which includes the flex line stiffness, the seal friction and any aerodynamic load on a nozzle extension. Flex line stiffness is frequently the largest term and it is the one least well known early.

**Nozzle separation produces an unsteady side load** that is not in any of the above and can exceed all of them. That is the structural reason separation is a hard limit rather than a performance penalty, and it is why the throttle range and the gimbal design are connected through the nozzle.

---

## Heat soak

The engine is hot and the things around it are not, and the heat has somewhere to go after shutdown.

**Soakback after shutdown is the case that catches people.** During operation the regenerative circuit removes the wall heat and carries it into the chamber. At shutdown the coolant flow stops and the heat that is already in the metal has nowhere to go except into the structure, the valves and whatever else is bolted on. **The peak temperature at those interfaces is after the burn, not during it**, and the mechanism is exactly the one in [ThermalModelling](../../thermalManagement/docs/ThermalModelling.md).

For a restartable engine this is a hard constraint rather than a nuisance: residual propellant in a hot line boils, and a valve that has soaked to a high temperature may not seal or may not open.

**Base heating** is the other direction. The exhaust plume radiates and recirculates into the base of the vehicle, and on a multi-engine cluster the plumes interact and the base region is hotter than any single engine would produce. That is a plume analysis rather than an engine analysis, and it belongs with the vehicle.

---

## The engine as an environment source

The engine is the dominant source of the vibration and acoustic environment the whole vehicle qualifies to. See [environmentsAndLoads](../../environmentsAndLoads/README.md).

**Combustion noise** is broadband and it is worst at low frequency. It couples into the structure through the thrust mount.

**The plume is the acoustic source at liftoff**, and it is the design case for the acoustic environment of everything on the vehicle. It depends on the exhaust velocity and the mass flow, and it is reduced by water deluge rather than by anything the engine does.

**Pump-induced vibration** is narrowband at shaft order and blade passing frequency, and it is the one that damages avionics because it is persistent and tonal rather than transient.

**Combustion instability**, if it occurs, is a different category entirely. A high frequency instability produces pressure oscillations that can destroy an engine in milliseconds, and it is a threshold rather than a margin. See [combustionDevices](../combustionDevices/README.md).

---

## Design rules of thumb

- **Treat the fuel flow and the coolant flow as one number**, because they are.
- **Check the cooling case at the throttle floor**, not at full thrust.
- **Let the inlet pressure be an outcome**, not a specification.
- **Budget the pressure drops explicitly** and agree the total with the feed system owner in writing.
- **Size the actuator on flex line stiffness**, and measure it rather than estimating it.
- **Analyse soakback for any restartable engine**, and run the transient past shutdown.
- **Give the plume its own analysis.** It is a vehicle problem, not an engine problem.

---

## Failure modes

**The coolant budget written independently of the fuel budget.** They are the same propellant and the analyses will not close.

**Cooling checked only at full thrust.** Wall temperature can be worse at the throttle floor.

**Inlet pressure fixed early.** Something downstream gives way, usually the injector drop, and stability goes with it.

**Flex line stiffness estimated.** It is often the largest term in the hinge moment and it is measurable.

**Soakback ignored on a restartable engine.** Valves that have soaked may not seal, and residual propellant in a hot line boils.

**Base heating treated as an engine problem.** On a cluster the plumes interact and no single-engine analysis sees it.

**Separation side load left out of the gimbal load case.** It can exceed the steady gimbal load and it is unsteady.

---

## Worked numbers

The worked example engine, 100 kN sea level, LOX/RP-1 at 10 MPa, area ratio 20.35.

| To | Quantity | Value |
|---|---|---|
| fluidSystems | Oxidiser flow | 26.47 kg/s |
| fluidSystems | Fuel flow | 10.34 kg/s |
| fluidSystems | Inlet pressure at 1.25 margin | 12.50 MPa |
| fluidSystems | Oxidiser tank volume | 3.60 m^3 |
| fluidSystems | Fuel tank volume | 1.98 m^3 |
| thermalManagement | Wall heat load | 2.72 MW |
| thermalManagement | Gas-side wall area | 5 958 cm^2 |
| thermalManagement | Nozzle share of that area | 66 % |
| thermalManagement | Coolant supply | 10.34 kg/s, the fuel flow |
| aerospaceStructures | Thrust | 100.0 kN |
| aerospaceStructures | Design load at 1.25 | 125.0 kN |
| aerospaceStructures | Side load at 5 degrees gimbal | 8.7 kN |
| aerospaceStructures | Engine mass | 102.0 kg |
| aerospaceStructures | Exit diameter | 408.5 mm |
| aerospaceMaterials | Liner | GRCop-42 at an 800 K wall limit |

**2.72 MW through a wall about a millimetre thick, cooled by 10.34 kg/s of the fuel that is about to be burnt.** That combination is why the liner is a copper alloy rather than a superalloy, and why it is additively manufactured.

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8120 | Liquid rocket engine nozzles, including the side load discussion |
| NASA SP-8087 | Fluid-cooled combustion chambers |
| NASA SP-8048 | Liquid rocket engine turbopump bearings |
| MIL-STD-1540 | Test requirements, including the environments the engine sources |
| NASA-STD-5001 | Structural design and test factors of safety |
| AIAA S-080 | Metallic pressure vessels |
| ECSS-E-ST-35C | Propulsion general requirements, the European parent document |

---

## Tool interface

The interface quantities are outputs of the sizing rather than a separate calculation.

```python
from EngineSizing import EngineSizing

sizing = EngineSizing()
sizing.setInputs({'combination':     'LOX/RP-1',
                  'thrust':          100000.0,
                  'chamberPressure': 10.0e6,
                  'areaRatio':       20.35})

throat  = sizing.sizeThroat()
chamber = sizing.sizeChamber()

print(throat['oxidiserFlow'], throat['fuelFlow'])
print(chamber['wallHeatLoad'], chamber['availableWallArea'])
print(sizing.estimateMass()['mass'])
```

The [worked example](../codeInterface.py) prints the full handover set, which is the form it is useful in.

---

## References

- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- NASA SP-8120, *Liquid rocket engine nozzles*
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
- Sutton, *History of Liquid Propellant Rocket Engines*
- ECSS-E-ST-35C, *Propulsion general requirements*
