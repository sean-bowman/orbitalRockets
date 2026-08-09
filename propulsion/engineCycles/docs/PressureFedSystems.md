[Home](../README.md) > Pressure Fed Systems

# Pressure Fed Systems

## Contents

- [Overview](#overview)
- [The tank is the pump](#the-tank-is-the-pump)
- [What it costs](#what-it-costs)
- [Where it is the right answer](#where-it-is-the-right-answer)
- [The pressurisation system](#the-pressurisation-system)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

No turbomachinery. The tank is pressurised above the chamber and the propellant flows because of it.

It is the simplest possible feed system, it removes the hardest component in the engine, and it puts the cost somewhere that scales badly.

---

## The tank is the pump

The tank has to deliver what a pump would have delivered: chamber pressure plus the injector, the cooling jacket and the plumbing. For a 10 MPa chamber that is **14.0 MPa at the tank.**

A pumped stage runs its tanks at **150 to 300 kPa**, enough to keep the pump from cavitating. See [CavitationAndNPSH](../../turbomachinery/docs/CavitationAndNPSH.md).

**So the tank pressure is roughly fifty times higher**, and tank wall mass is proportional to pressure times volume.

---

## What it costs

For the [worked example](../codeInterface.py) engine's propellant volumes, 3.60 m^3 of oxidiser and 1.98 m^3 of fuel:

| Configuration | Tank pressure | Tank mass |
|---|---|---|
| Pumped | 150 to 300 kPa | 46 kg |
| Pressure fed | 14.0 MPa | **2219 kg** |

**Forty eight times the tank mass**, against an engine that would have weighed about a hundred kilograms.

That number is computed with a thin wall pressure vessel model that is an assumption rather than data, and it is registered as unvalidated. **The conclusion does not depend on its accuracy**, because the ratio comes from the pressure ratio rather than from the model: a factor of fifty in pressure is a factor of fifty in wall mass whatever the constant.

**This is the clearest elimination in cycle selection.** It needs no trade study.

---

## Where it is the right answer

It is not a bad cycle. It is a cycle with a scaling law that rules it out above a certain size, and below that size it is frequently the best choice available.

**Reaction control and attitude control.** Small propellant quantities, many restarts, and a requirement to be simple and reliable rather than efficient. Nearly all of it is pressure fed, and the [fluidSystems](../../../fluidSystems/README.md) worked example is exactly this case.

**Small upper stages and kick stages.** Where the propellant load is small enough that the tank penalty is affordable and the development cost of a turbopump is not.

**Anything that has to sit for years and then work.** A turbopump is a rotating machine with bearings and seals; a pressurised tank is not.

**Low chamber pressure designs.** The penalty scales with chamber pressure, so a 2 MPa pressure fed engine is a very different proposition from a 10 MPa one. That is why pressure fed engines run at low chamber pressure, and why they accept the performance that comes with it.

---

## The pressurisation system

The tank pressure has to come from somewhere and the arrangement is its own design problem, owned by [fluidSystems](../../../fluidSystems/fluidSystemsLibrary/docs/PressurizationAndBlowdown.md).

**Stored gas** is a high pressure bottle of helium, a regulator, and the plumbing. The bottle is itself a pressure vessel and its mass is not negligible, so the real penalty is larger than the tank mass alone.

**Blowdown** starts with ullage gas already in the tank and lets the pressure fall as the propellant is consumed. It removes the regulator and the bottle, and the chamber pressure falls through the burn, which is a performance loss and a mixture ratio problem.

**Autogenous** pressurisation uses the propellant's own vapour, heated. It removes the helium and it couples the pressurisation to the engine.

Helium is the usual choice and it is expensive in mass terms: it needs a heavy bottle and it has to be warm at the point of use or it condenses the propellant vapour and loses pressure.

---

## Design rules of thumb

- **Use it below a few tonnes of propellant** and not above.
- **Keep the chamber pressure low.** The penalty scales with it directly.
- **Count the pressurant bottle**, not just the propellant tanks.
- **Prefer it wherever restart count and storage life dominate.**
- **Consider blowdown if the mixture ratio drift is tolerable**, and check that it is.
- **Do not run a trade study to eliminate it on a booster.** The ratio is a factor of fifty.

---

## Failure modes

**Proposed for a booster.** The tank is a pressure vessel and it is an order of magnitude heavier.

**The pressurant bottle omitted from the mass estimate.** It is a high pressure vessel of its own.

**Blowdown adopted without checking the mixture ratio drift.** Both circuits do not fall together.

**Cold helium into a cryogenic tank.** It condenses vapour and the pressure collapses.

**The tank sized at chamber pressure.** It has to deliver chamber pressure plus the injector, the jacket and the lines.

---

## Worked numbers

The [worked example](../codeInterface.py) engine's propellant volumes at a 10 MPa chamber.

| Quantity | Value |
|---|---|
| Required tank pressure | 14.0 MPa |
| Pumped stage tank pressure, for comparison | 150 to 300 kPa |
| Pressure fed tank mass | 2219 kg |
| Pumped tank mass | 46 kg |
| Ratio | 48 x |
| Engine mass that would have been saved | about 100 kg |

---

## Standards

| Standard | What it gives you |
|---|---|
| **AIAA S-080** | **Metallic pressure vessels**, which is what a pressure fed tank is |
| AIAA S-081 | Composite overwrapped pressure vessels |
| NASA-STD-5019 | Fracture control, which a pressure vessel needs |
| NASA SP-8007 | Buckling of thin walled cylinders, for the unpressurised case |

---

## Tool interface

```python
from EngineCycle import EngineCycle

cycle = EngineCycle()
cycle.setInputs({'cycle': 'pressure fed', 'chamberPressure': 10.0e6})

ladder = cycle.calculatePressureLadder()
print(ladder['dischargePressure'])
```

The class refuses a turbine flow fraction on this cycle, because there is no turbine and the number would be meaningless rather than small.

---

## References

- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 6
- AIAA S-080, *Metallic pressure vessels*
- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
